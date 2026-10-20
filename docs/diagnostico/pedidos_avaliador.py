"""3o bloco (20/10), Parte 2, testes 4 e 5: pedidos da tabela "Pedidos e regras dos
profissionais" no avaliador oficial. Esperado registrado antes: `resultados/pedidos_2026-10-20/
ESPERADO.md`, itens 4 e 5.

4. Instancia XML sintetica (formato INRC) do caso 2b, com os `DayOffRequests` /
   `ShiftOffRequests` gerados pela tabela (peso 1). Escalas: a da ferramenta e 9 perturbadas
   (troca de turno entre dois profissionais num dia sorteado: a cobertura se mantem). Por
   profissional, a penalidade dos pedidos: avaliador x modelo (expressoes do proprio modelo, x
   fixado) x `avaliacao.py`; e o total do avaliador x os descumpridos contados pela ferramenta.
   Premissa compartilhada: a traducao tabela -> pedidos (`prioridades.traduzir`) e a mesma para
   os tres; aqui se confere a PONTUACAO dos pedidos e a escrita do XML, nao a traducao (essa e
   conferida pelas contas a mao dos testes 2 e 3).
5. So leitura: `DayOnRequests` / `ShiftOnRequests` no XSD e no avaliador (nada vai a tela).

    python docs\\diagnostico\\pedidos_avaliador.py
"""

from __future__ import annotations

import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(AQUI)]

import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402
import prioridades as pr  # noqa: E402
from avaliacao import violacoes  # noqa: E402
from solucao import escrever_xml as escrever_solucao  # noqa: E402
from validar import avaliar  # noqa: E402
from validacao_restricoes import avaliar_no_modelo, ler_avaliador  # noqa: E402

SAIDA = RAIZ / "resultados" / "pedidos_2026-10-20" / "avaliador"
SEMENTE, PERTURBADAS, TROCAS = 20261020, 9, 3
T8 = [("M", 7, 8, "M"), ("T", 15, 8, "T"), ("N", 23, 8, "N")]
FAMILIAS = ("day_off_requests", "shift_off_requests")
TAG = {"folga_dia": "DayOff", "folga_turno": "ShiftOff",
       "trabalho_dia": "DayOn", "trabalho_turno": "ShiftOn"}
BLOCO = {"DayOff": "DayOffRequests", "DayOn": "DayOnRequests",
         "ShiftOff": "ShiftOffRequests", "ShiftOn": "ShiftOnRequests"}


def escrever_instancia(inst, caminho: Path) -> Path:
    """O XML da instancia (`instancia_br.escrever_xml`) mais os pedidos, peso 1, na ordem do
    esquema (DayOff, DayOn, ShiftOff, ShiftOn depois de CoverRequirements)."""
    br.escrever_xml(inst, caminho)
    arvore = etree.parse(str(caminho))
    raiz = arvore.getroot()
    for tag in ("DayOff", "DayOn", "ShiftOff", "ShiftOn"):
        itens = [p for p in inst.pedidos if TAG[p.tipo] == tag]
        if not itens:
            continue
        bloco = etree.SubElement(raiz, BLOCO[tag])
        for p in itens:
            el = etree.SubElement(bloco, tag, weight="1")
            if p.turno is not None:
                etree.SubElement(el, "ShiftTypeID").text = p.turno
            etree.SubElement(el, "EmployeeID").text = p.profissional
            etree.SubElement(el, "Date").text = p.data.isoformat()
    arvore.write(str(caminho), pretty_print=True, xml_declaration=True, encoding="utf-8")
    return caminho


def perturbar(inst, escala, rng):
    agenda = {(n, d): s for d, n, s in escala}
    profs, dias = list(inst.profissionais), list(inst.dias)
    feitas = 0
    while feitas < TROCAS:
        d = rng.choice(dias)
        a, b = rng.sample(profs, 2)
        sa, sb = agenda.get((a, d)), agenda.get((b, d))
        if sa == sb:
            continue
        for n, s in ((a, sb), (b, sa)):
            if s is None:
                agenda.pop((n, d), None)
            else:
                agenda[(n, d)] = s
        feitas += 1
    return tuple(sorted((d, n, s) for (n, d), s in agenda.items()))


def caso_2b():
    ini = br.primeira_segunda()
    inst = br.construir(turnos=T8, demanda_turno={"M": (0, 2), "T": (0, 1), "N": (0, 1)},
                        n_enfermeiros=0, n_tecnicos=6, nomes_tecnicos=list("ABCDEF"), dias=7,
                        inicio=ini)
    L = pr.Linha
    from datetime import timedelta
    regras = [L(n, None, t, pr.SO_TURNO) for n, t in zip("ABCDEF", "MMTTNN")]
    regras += [L("A", ini + timedelta(days=1), None, pr.FOLGA),
               L("C", ini + timedelta(days=3), "T", pr.FOLGA)]
    return fe.com_regras(inst, regras)


def teste_4() -> bool:
    SAIDA.mkdir(parents=True, exist_ok=True)
    inst = caso_2b()
    tipos = Counter(p.tipo for p in inst.pedidos)
    xml_inst = escrever_instancia(inst, SAIDA / "caso2b_instancia.xml")
    xsd = br.validar_xsd(xml_inst)
    _, inst_p, escala, info = fe.resolver_com_objetivo(inst, 120)
    rng = random.Random(SEMENTE)
    escalas = [("ferramenta", escala)] + [(f"perturbada{k}", perturbar(inst, escala, rng))
                                          for k in range(1, PERTURBADAS + 1)]
    linhas = ["| Escala | Avaliador (pedidos) | Modelo (pedidos) | avaliacao.py (pedidos) | "
              "Ferramenta (descumpridos) | Profissionais com diferença |",
              "|---|---:|---:|---:|---:|---:|"]
    ok = not xsd and tipos["folga_dia"] > 0 and tipos["folga_turno"] > 0
    for rotulo, esc in escalas:
        sol = escrever_solucao(inst, esc, SAIDA / f"caso2b_{rotulo}.xml", penalidade=0)
        avaliar(xml_inst, sol)
        _, aval, _, erros = ler_avaliador(sol.with_name(sol.stem + "_avaliador.txt"))
        _, _, _, pena = avaliar_no_modelo(inst, esc)
        py = defaultdict(int)
        for v in violacoes(inst, esc):
            py[(v.profissional, v.restricao)] += v.custo
        nossos = len(pr.descumpridos(inst, esc))
        dif = sum(1 for n in inst.profissionais for f in FAMILIAS
                  if not aval.get((n, f), 0) == pena.get((n, f), 0) == py.get((n, f), 0))
        tot = [sum(c for (n, f), c in x.items() if f in FAMILIAS) for x in (aval, pena, py)]
        bate = dif == 0 and tot[0] == tot[1] == tot[2] == nossos and not any(
            "Hard" in e for e in erros)
        ok &= bate
        linhas.append(f"| {rotulo} | {tot[0]} | {tot[1]} | {tot[2]} | {nossos} | {dif} |")
        print(linhas[-1], flush=True)
    texto = ["# Teste 4 — pedidos da tabela no avaliador oficial (20/10/2026)", "",
             f"Caso 2b + \"Folga, d2\" de A + \"Folga, d4, turno T\" de C; pedidos gerados: "
             f"{tipos['folga_dia']} DayOff, {tipos['folga_turno']} ShiftOff (peso 1). XSD da "
             f"instância: {'válido' if not xsd else xsd}. Escala da ferramenta: "
             f"{info['caminho']}, provado {info['provado']}. Semente {SEMENTE}; "
             f"{PERTURBADAS} perturbadas, {TROCAS} trocas cada.", "",
             "Colunas: penalidade dos pedidos (DayOff + ShiftOff) somada nos profissionais. "
             "A coluna do modelo vem das expressões do próprio modelo (`m.pena_familia`, x "
             "fixado) — não é conferência independente do modelo. **Premissa compartilhada "
             "pelas quatro colunas:** a lista de pedidos gerada pela tradução da tabela; o teste "
             "não confere a tradução (conferida nos testes 2 e 3, à mão).", ""] + linhas + [
             "", "TUDO OK" if ok else "FALHOU"]
    (SAIDA / "teste4.md").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print(texto[-1])
    return ok


def teste_5() -> bool:
    """DayOn em d1 e ShiftOn M em d2, 1 tecnico; escala: T no d2."""
    from datetime import timedelta
    from instancia import Pedido
    import dataclasses
    SAIDA.mkdir(parents=True, exist_ok=True)
    ini = br.primeira_segunda()
    d2 = ini + timedelta(days=1)
    zero = {"M": (0, 0), "T": (0, 0), "N": (0, 0)}
    inst = br.construir(turnos=T8, demanda_turno=zero, demanda_data={(d2, "T", "tec"): 1},
                        n_enfermeiros=0, n_tecnicos=1, dias=7, inicio=ini)
    n = next(iter(inst.profissionais))
    inst = dataclasses.replace(inst, pedidos=(
        Pedido(tipo="trabalho_dia", profissional=n, data=ini, peso=1),
        Pedido(tipo="trabalho_turno", profissional=n, data=d2, peso=1, turno="M")))
    xml_inst = escrever_instancia(inst, SAIDA / "teste5_instancia.xml")
    # `escrever_xml` deixa um DayOfWeekCover vazio para o dia da semana sem demanda em nenhum
    # turno, e o XSD exige ao menos um Cover (achado deste teste, 20/10). So aqui, tiro os vazios
    arvore = etree.parse(str(xml_inst))
    for el in arvore.getroot().iter("DayOfWeekCover"):
        if el.find("Cover") is None:
            el.getparent().remove(el)
    arvore.write(str(xml_inst), pretty_print=True, xml_declaration=True, encoding="utf-8")
    xsd = br.validar_xsd(xml_inst)
    sol = escrever_solucao(inst, ((d2, n, "T"),), SAIDA / "teste5_solucao.xml", penalidade=0)
    avaliar(xml_inst, sol)
    texto = sol.with_name(sol.stem + "_avaliador.txt").read_text(encoding="utf-8",
                                                                errors="replace")
    pedidos = [l.strip() for l in texto.splitlines() if re.search(r"Requested", l)]
    custo = sum(int(m.group(1)) for l in pedidos if (m := re.search(r"cost = (\d+)", l)))
    print("XSD:", "válido" if not xsd else xsd)
    for l in pedidos:
        print("  ", l)
    print(f"teste 5: custo dos pedidos no avaliador = {custo} (esperado 2)")
    ok = not xsd and custo == 2 and len(pedidos) == 2
    texto = ["# Teste 5 — DayOnRequests / ShiftOnRequests no avaliador (20/10/2026, só leitura)",
             "", f"XSD da instância: {'válido' if not xsd else xsd}.",
             "Instância: 1 técnico, 7 dias, M/T/N; DayOn em d1 e ShiftOn M em d2, peso 1. "
             "Escala: T no d2.", "",
             f"Linhas do avaliador com \"Requested\": {pedidos or 'nenhuma'}.",
             f"Custo dos pedidos no avaliador: **{custo}** (esperado registrado antes: 2).", "",
             "Resultado: " + ("como o esperado." if ok else
                              "DIFERENTE do esperado — o avaliador não pontua DayOn/ShiftOn "
                              "(causa no código-fonte do jar: ver o relatório 2026-10-20).")]
    (SAIDA / "teste5.md").write_text("\n".join(texto) + "\n", encoding="utf-8")
    return ok


def main() -> int:
    """Codigo de saida = o do teste 4. O 5 e so leitura: o resultado e informado, seja qual for
    (esperado 2; se der outro valor, e achado sobre o avaliador, nao falha da ferramenta)."""
    ok4 = teste_4()
    ok5 = teste_5()
    print(f"teste 4: {'TUDO OK' if ok4 else 'FALHOU'}; teste 5 (só leitura): "
          f"{'como o esperado' if ok5 else 'DIFERENTE do esperado (2)'}")
    return 0 if ok4 else 1


if __name__ == "__main__":
    raise SystemExit(main())
