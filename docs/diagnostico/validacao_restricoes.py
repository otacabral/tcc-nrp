"""Validacao por restricao nos 4 otimos (56, 58, 197, 219) — pedido do orientador, 14/10.

Sem solver. Le as escalas salvas (`resultados/<inst>_completo.xml`) e as saidas do avaliador
oficial ja versionadas (`resultados/<inst>_completo_avaliador.txt`) e confere:

0. a grade "Schedule" impressa pelo avaliador e a escala do XML (senao a comparacao seria
   entre escalas diferentes);
1. duras = 0: avaliador (cobertura), um turno por dia contado direto no XML, `conferir_rigidas`
   e as restricoes do modelo Pyomo com x fixado na escala;
2. penalidade por tipo: avaliador x modelo (x avaliacao.py), com a diferenca;
3. o mesmo por profissional e por profissional x tipo.

A coluna "modelo" e calculada pelas expressoes do proprio modelo (`m.parcela`,
`m.pena_familia`), com x fixado e as auxiliares no menor valor admissivel — o MESMO codigo que
gera o valor da funcao objetivo. Nao e conferencia independente do modelo; a independencia
esta na coluna do avaliador. Esperado registrado antes: `resultados/validacao_restricoes_
2026-10-19/ESPERADO.md`.

    python docs\\diagnostico\\validacao_restricoes.py
"""

from __future__ import annotations

import csv
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

import pyomo.environ as pyo
from pyomo.repn import generate_standard_repn

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import modelo  # noqa: E402
from avaliacao import violacoes  # noqa: E402
from parser import ler_instancia  # noqa: E402
from solucao import conferir_rigidas, ler_xml  # noqa: E402

SAIDA = RAIZ / "resultados" / "validacao_restricoes_2026-10-19"

ALVOS = [
    ("sprint01", "instancias/sprint/sprint/sprint01.xml", 56),
    ("sprint02", "instancias/sprint/sprint/sprint02.xml", 58),
    ("long01", "instancias/long/long/long01.xml", 197),
    ("long02", "instancias/long/long/long02.xml", 219),
]

# rotulo do avaliador (inicio da linha) -> familia do modelo. Premissa deste script, escrita a
# mao a partir dos rotulos do codigo-fonte do avaliador; rotulo sem mapa faz o script falhar.
ROTULOS = [
    ("Maximum number of assignments", "max_num_assignments"),
    ("Minimum number of assignments", "min_num_assignments"),
    ("Maximum number of consecutive working days", "max_consecutive_working_days"),
    ("Minimum number of consecutive working days", "min_consecutive_working_days"),
    ("Maximum number of consecutive free days", "max_consecutive_free_days"),
    ("Minimum number of consecutive free days", "min_consecutive_free_days"),
    ("Maximum consecutive working weekends", "max_consecutive_working_weekends"),
    ("Minimum consecutive working weekends", "min_consecutive_working_weekends"),
    ("Identical shift types during weekend", "identical_shift_types_during_weekend"),
    # achados no controle de 19/10 (nao aparecem nas 4 escalas otimas); grafia do avaliador
    ("Incomplete working weekend", "complete_weekends"),
    ("Identical shifttypes during weekend", "identical_shift_types_during_weekend"),
    ("Alternative skill", "alternative_skill_category"),
    ("Two free days after a night shift", "two_free_days_after_night_shifts"),
    ("Requested day off", "day_off_requests"),
    ("Requested shift off", "shift_off_requests"),
    ("Requested shift on", "shift_on_requests"),
    ("Unwanted pattern", "unwanted_patterns"),
    ("Unwanted Pattern", "unwanted_patterns"),
]

NOME_PT = {
    "max_num_assignments": "máximo de atribuições",
    "min_num_assignments": "mínimo de atribuições",
    "max_consecutive_working_days": "máximo de dias seguidos de trabalho",
    "min_consecutive_working_days": "mínimo de dias seguidos de trabalho",
    "max_consecutive_free_days": "máximo de folgas seguidas",
    "min_consecutive_free_days": "mínimo de folgas seguidas",
    "max_consecutive_working_weekends": "máximo de fins de semana seguidos",
    "min_consecutive_working_weekends": "mínimo de fins de semana seguidos",
    "max_working_weekends_in_four_weeks": "máximo de fins de semana em 4 semanas",
    "complete_weekends": "fim de semana completo",
    "identical_shift_types_during_weekend": "turnos idênticos no fim de semana",
    "no_night_shift_before_free_weekend": "noturno antes de fim de semana livre",
    "two_free_days_after_night_shifts": "duas folgas após noites",
    "alternative_skill_category": "habilidade alternativa",
    "unwanted_patterns": "padrões indesejados",
    "day_off_requests": "pedido de folga (dia)",
    "shift_off_requests": "pedido de folga (turno)",
    "day_on_requests": "pedido de trabalho (dia)",
    "shift_on_requests": "pedido de trabalho (turno)",
}

LINHA_VIOL = re.compile(r"^\s*(.*?): excess = (-?\d+) , pos = (-?\d+), cost = (-?\d+)\s*$")


# --- avaliador ------------------------------------------------------------------------------

def ler_avaliador(caminho: Path):
    """(grade {(prof, i): turno}, custos {(prof, familia): custo}, total, linhas de erro)."""
    texto = caminho.read_text(encoding="utf-8", errors="replace").splitlines()
    grade, custos, total, erros = {}, defaultdict(int), None, []
    quem = None
    for k, linha in enumerate(texto):
        if "Hard constraints" in linha or linha.startswith("Error!"):
            erros.append(linha.strip())
        m = re.match(r"^Employee\s+(\S+)\s*\|(.*)\|\s*$", linha)
        if m:
            for i, cel in enumerate(m.group(2).split("|")):
                if cel.strip():
                    grade[(m.group(1), i)] = cel.strip()
            continue
        m = re.match(r"^\s*Employee:\s*(\S+)\s*$", linha)
        if m:
            quem = m.group(1)
            continue
        m = LINHA_VIOL.match(linha)
        if m:
            rotulo = m.group(1)
            familia = next((f for r, f in ROTULOS if rotulo.startswith(r)), None)
            if familia is None:
                raise SystemExit(f"{caminho.name}: rotulo sem mapa: {rotulo!r}")
            custos[(quem, familia)] += int(m.group(4))
            continue
        if linha.strip() == "Penalty:":
            total = int(next(t for t in texto[k + 1:] if t.strip().isdigit()).strip())
    return grade, dict(custos), total, erros


# --- escala, direto do XML ---------------------------------------------------------------------

def um_turno_por_dia_xml(caminho: Path) -> int:
    """Pares (profissional, data) com mais de uma atribuicao, contados no XML cru."""
    raiz = ET.parse(caminho).getroot()
    c = Counter((a.findtext("Employee"), a.findtext("Date")) for a in raiz.iter("Assignment"))
    return sum(1 for v in c.values() if v > 1)


# --- modelo com x fixado -----------------------------------------------------------------------

def avaliar_no_modelo(inst, escala):
    """Fixa x na escala, poe as auxiliares no menor valor admissivel e devolve
    (violadas, objetivo, parcela {familia}, pena_familia {(n, familia)})."""
    m = modelo.construir(inst)
    marcadas = {(n, s, d) for d, n, s in escala}
    for idx in m.X:
        m.x[idx].value = 1 if idx in marcadas else 0
    for n in inst.profissionais:
        for d in inst.dias:
            m.y[n, d].value = round(sum(pyo.value(m.x[n, s, d]) for s in inst.turnos
                                        if (n, s, d) in m.X))
    # wk_<n>_<f> = trabalhou no fim de semana f (determinada pelas restricoes que a ligam a y)
    for n in inst.profissionais:
        for f in inst.fins_de_semana(inst.contrato_de(n).id):
            v = m.component(f"wk_{n}_{f.indice}")
            if v is not None:
                v.value = max(pyo.value(m.y[n, d]) for d in f.datas)
    # demais auxiliares (cw_, id_, folga): coeficiente positivo no objetivo, entao a
    # minimizacao as poe no menor valor que as restricoes admitem. Cada restricao que as
    # envolve tem uma so delas.
    livres = {id(v): v for v in m.folga.values()}
    for comp in m.component_objects(pyo.Var):
        if comp.name.startswith(("cw_", "id_")):
            for v in comp.values():
                livres[id(v)] = v
    for v in livres.values():
        v.value = max(0.0, v.lb or 0.0)
    for c in list(m.limite_folga.values()) + list(m.auxiliares.values()):
        repn = generate_standard_repn(c.body)
        alvo = [(coef, v) for coef, v in zip(repn.linear_coefs, repn.linear_vars)
                if id(v) in livres]
        if len(alvo) != 1:
            continue
        a, v = alvo[0]
        resto = repn.constant + sum(coef * pyo.value(w) for coef, w in
                                    zip(repn.linear_coefs, repn.linear_vars) if w is not v)
        precisa = []
        if c.lower is not None:
            limite = pyo.value(c.lower)
            precisa.append((limite - resto) / a if a > 0 else None)
        if c.upper is not None:
            limite = pyo.value(c.upper)
            precisa.append((limite - resto) / a if a < 0 else None)
        for p in precisa:
            if p is not None and p > v.value:
                v.value = p
    violadas = []
    for c in m.component_data_objects(pyo.Constraint, active=True):
        corpo = pyo.value(c.body)
        if (c.lower is not None and corpo < pyo.value(c.lower) - 1e-6) or \
                (c.upper is not None and corpo > pyo.value(c.upper) + 1e-6):
            violadas.append(c.name)
    parcela = {f: round(pyo.value(m.parcela[f])) for f in m.parcela}
    pena = {(n, f): round(pyo.value(m.pena_familia[n, f]))
            for n in inst.profissionais for f in m.parcela}
    return violadas, round(pyo.value(m.objetivo)), parcela, pena


# --- relatorio ----------------------------------------------------------------------------------

def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    md = ["# Validação por restrição nos 4 ótimos — resultado (19/10/2026)", "",
          "Gerado por `python docs\\diagnostico\\validacao_restricoes.py`, sem solver. "
          "Esperado registrado antes: `ESPERADO.md` (nesta pasta).", ""]
    resumo, falhas = [], []
    linhas_tipo, linhas_prof = [], []
    for nome, caminho, z6 in ALVOS:
        inst = ler_instancia(RAIZ / caminho)
        xml = RAIZ / "resultados" / f"{nome}_completo.xml"
        _, _, escala = ler_xml(xml)
        grade, aval, total_aval, erros = ler_avaliador(
            RAIZ / "resultados" / f"{nome}_completo_avaliador.txt")

        # 0) a grade do avaliador e esta escala
        dias = list(inst.dias)
        da_escala = {(n, dias.index(d)): s for d, n, s in escala}
        grade_ok = grade == da_escala

        # 1) duras
        dup = um_turno_por_dia_xml(xml)
        rig = conferir_rigidas(inst, escala, habilidade_rigida=False)
        violadas, obj, parcela, pena = avaliar_no_modelo(inst, escala)

        # 2) por tipo (inclui avaliacao.py)
        py = defaultdict(int)
        for v in violacoes(inst, escala):
            py[(v.profissional, v.restricao)] += v.custo
        familias = sorted({f for _, f in aval} | set(parcela) | {f for _, f in py})
        tab = []
        for f in familias:
            a = sum(c for (_, g), c in aval.items() if g == f)
            mo = parcela.get(f, 0)
            p = sum(c for (_, g), c in py.items() if g == f)
            tab.append((f, a, mo, p))
            linhas_tipo.append((nome, f, NOME_PT.get(f, f), a, mo, a - mo, p))
        soma_a, soma_m = sum(t[1] for t in tab), sum(t[2] for t in tab)
        dif_tipo = sum(1 for t in tab if t[1] != t[2] or t[1] != t[3])

        # 3) por profissional e por profissional x tipo
        profs = sorted(inst.profissionais, key=lambda n: (len(n), n))
        dif_prof = dif_cel = 0
        for n in profs:
            a = sum(c for (q, _), c in aval.items() if q == n)
            mo = sum(c for (q, _), c in pena.items() if q == n)
            p = sum(c for (q, _), c in py.items() if q == n)
            dif_prof += (a != mo) or (a != p)
            linhas_prof.append((nome, n, a, mo, a - mo, p))
            for f in familias:
                if aval.get((n, f), 0) != pena.get((n, f), 0) or \
                        aval.get((n, f), 0) != py.get((n, f), 0):
                    dif_cel += 1

        ok = (grade_ok and not erros and dup == 0 and not rig and not violadas
              and soma_a == soma_m == total_aval == obj == z6 and dif_tipo == 0
              and dif_prof == 0 and dif_cel == 0)
        if not ok:
            falhas.append(nome)
        resumo.append((nome, z6, total_aval, soma_a, soma_m, obj, grade_ok, len(erros), dup,
                       len(rig), len(violadas), dif_tipo, dif_prof, dif_cel, ok))

        md += [f"## {nome} (Tabela 6 = {z6})", "",
               f"- grade do avaliador = escala do XML: {'sim' if grade_ok else 'NÃO'}",
               f"- duras: avaliador {len(erros)} linha(s) de erro; um turno por dia no XML "
               f"{dup}; `conferir_rigidas` {len(rig)}; restrições do modelo violadas com x "
               f"fixado {len(violadas)}" + (f" ({violadas[:3]})" if violadas else ""),
               f"- profissionais: {len(profs)}; com diferença avaliador × modelo: {dif_prof}; "
               f"células profissional × tipo com diferença: {dif_cel}", "",
               "| Tipo de restrição | Família no modelo | Avaliador | Modelo | Diferença | "
               "avaliacao.py |", "|---|---|---:|---:|---:|---:|"]
        md += [f"| {NOME_PT.get(f, f)} | `{f}` | {a} | {mo} | {a - mo} | {p} |"
               for f, a, mo, p in tab]
        md += [f"| **Total** | | **{soma_a}** | **{soma_m}** | **{soma_a - soma_m}** | "
               f"**{sum(t[3] for t in tab)}** |", ""]

    sep = "|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---|"
    tabela_resumo = [
        "## Resumo", "",
        "| Instância | Tabela 6 | Penalty do avaliador | Soma por tipo (avaliador) | "
        "Soma por tipo (modelo) | Objetivo do modelo (x fixado) | Grade = XML | "
        "Duras: avaliador / XML / conferir_rigidas / modelo | Tipos com diferença | "
        "Profissionais com diferença | Células prof × tipo com diferença | OK |", sep]
    for (nome, z6, ta, sa, sm, obj, g, e, dup, rig, vio, dt, dp, dc, ok) in resumo:
        tabela_resumo.append(
            f"| {nome} | {z6} | {ta} | {sa} | {sm} | {obj} | {'sim' if g else 'NÃO'} | "
            f"{e} / {dup} / {rig} / {vio} | {dt} | {dp} | {dc} | {'OK' if ok else 'FALHOU'} |")
    md[4:4] = tabela_resumo + [""]
    md += ["## Por profissional", "",
           "Arquivo `por_profissional.csv` (instância, profissional, avaliador, modelo, "
           "diferença, avaliacao.py). Por tipo: `por_tipo.csv`.", ""]
    (SAIDA / "tabela.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    with open(SAIDA / "por_tipo.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["instancia", "familia", "tipo", "avaliador", "modelo", "diferenca",
                    "avaliacao_py"])
        w.writerows(linhas_tipo)
    with open(SAIDA / "por_profissional.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["instancia", "profissional", "avaliador", "modelo", "diferenca",
                    "avaliacao_py"])
        w.writerows(linhas_prof)
    for linha in resumo:
        print(linha)
    print("TUDO OK" if not falhas else f"FALHOU: {falhas}")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
