"""Censo das flexiveis nas 69 instancias do INRC-2010 e limite superior de violacoes (19/10).

So leitura dos arquivos, sem solver. Serve a dois pedidos da sessao de 19/10:

- item 3c/3d (diagnostico da opcao B): em quantas instancias cada flexivel e exercitada (ativa,
  pela regra de 15/09, em pelo menos um contrato) e um LIMITE SUPERIOR do numero de violacoes
  (unidades de excesso, peso 1, como a opcao B conta) por instancia — para medir o tamanho dos
  coeficientes se a escolha for pesos escalonados;
- item 8 (`docs/pesos_inrc.md`): os pesos de cada flexivel nas 69 instancias.

Os limites sao validos, nao justos: servem para dimensionar, nao para afirmar nada da escala.
Formula de cada um em `LIMITES` (texto) e em `limite()` (conta).

    python docs\\diagnostico\\censo_flexiveis.py
"""

from __future__ import annotations

import csv
import itertools
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

from parser import descobrir_instancias, ler_instancia  # noqa: E402

SAIDA = RAIZ / "resultados" / "censo_flexiveis_2026-10-19"

CONTRATO = ["max_num_assignments", "min_num_assignments", "max_consecutive_working_days",
            "min_consecutive_working_days", "max_consecutive_free_days",
            "min_consecutive_free_days", "max_consecutive_working_weekends",
            "min_consecutive_working_weekends", "max_working_weekends_in_four_weeks",
            "complete_weekends", "identical_shift_types_during_weekend",
            "no_night_shift_before_free_weekend", "two_free_days_after_night_shifts",
            "alternative_skill_category"]
OUTRAS = ["unwanted_patterns", "day_off_requests", "shift_off_requests", "day_on_requests",
          "shift_on_requests"]

LIMITES = {
    "max_num_assignments": "D − v por profissional",
    "min_num_assignments": "v por profissional",
    "max_consecutive_working_days": "D − v por profissional",
    "min_consecutive_working_days": "(v − 1) × ⌈D/2⌉ por profissional",
    "max_consecutive_free_days": "D − v por profissional",
    "min_consecutive_free_days": "(v − 1) × ⌈D/2⌉ por profissional",
    "max_consecutive_working_weekends": "F − v por profissional",
    "min_consecutive_working_weekends": "(v − 1) × ⌈F/2⌉ por profissional",
    "max_working_weekends_in_four_weeks": "(F − 3) × (4 − v) por profissional",
    "complete_weekends": "por fim de semana, o pior padrão de dias (enumerado)",
    "identical_shift_types_during_weekend": "por fim de semana, a pior combinação de turnos (enumerada)",
    "no_night_shift_before_free_weekend": "F por profissional (com turno noturno)",
    "two_free_days_after_night_shifts": "2 × D por profissional (frouxo)",
    "alternative_skill_category": "D por profissional sem todas as habilidades",
    "unwanted_patterns": "por padrão, as posições em que ele pode casar",
    "day_off_requests": "nº de pedidos",
    "shift_off_requests": "nº de pedidos",
    "day_on_requests": "nº de pedidos",
    "shift_on_requests": "nº de pedidos",
}


def _pior_completo(tam: int) -> int:
    """Fim de semana completo: tam x (blocos) - dias trabalhados, no pior padrao."""
    pior = 0
    for p in itertools.product((0, 1), repeat=tam):
        blocos = sum(1 for k in range(tam) if p[k] and (k == 0 or not p[k - 1]))
        pior = max(pior, tam * blocos - sum(p))
    return pior


def _pior_identico(tam: int, n_turnos: int) -> int:
    """Turnos identicos: soma, por tipo usado, de (tam - dias com aquele tipo)."""
    pior = 0
    for p in itertools.product(range(n_turnos + 1), repeat=tam):   # 0 = folga
        usados = Counter(t for t in p if t)
        pior = max(pior, sum(tam - c for c in usados.values()))
    return pior


def limite(inst, fam: str, n: str) -> int:
    c = inst.contrato_de(n)
    D = len(inst.dias)
    fds = inst.fins_de_semana(c.id)
    F = len(fds)
    if fam in CONTRATO:
        r = getattr(c, fam)
        if not r.ativa:
            return 0
        v = r.valor or 0
        if fam in ("max_num_assignments", "max_consecutive_working_days",
                   "max_consecutive_free_days"):
            return max(0, D - v)
        if fam == "min_num_assignments":
            return min(v, D)
        if fam in ("min_consecutive_working_days", "min_consecutive_free_days"):
            return max(0, v - 1) * math.ceil(D / 2)
        if fam == "max_consecutive_working_weekends":
            return max(0, F - v)
        if fam == "min_consecutive_working_weekends":
            return max(0, v - 1) * math.ceil(F / 2)
        if fam == "max_working_weekends_in_four_weeks":
            return max(0, F - 3) * max(0, 4 - v)
        if fam == "complete_weekends":
            return sum(_pior_completo(len(f.datas)) for f in fds)
        if fam == "identical_shift_types_during_weekend":
            return sum(_pior_identico(len(f.datas), len(inst.turnos)) for f in fds)
        if fam == "no_night_shift_before_free_weekend":
            return F if any(t.noturno for t in inst.turnos.values()) else 0
        if fam == "two_free_days_after_night_shifts":
            return 2 * D if any(t.noturno for t in inst.turnos.values()) else 0
        if fam == "alternative_skill_category":
            tem = inst.profissionais[n].habilidades
            return D if any(not t.habilidades <= tem for t in inst.turnos.values()) else 0
    if fam == "unwanted_patterns":
        total = 0
        for pid in c.padroes_indesejados:
            p = inst.padroes.get(pid)
            if p is None or p.peso <= 0:
                continue
            fixo = p.entradas[0].dia
            total += sum(1 for i, d in enumerate(inst.dias)
                         if i + p.tamanho <= D + (1 if fixo != "Any" else 0)
                         and (fixo == "Any" or d.strftime("%A") == fixo))
        return total
    tipo = {"day_off_requests": "folga_dia", "shift_off_requests": "folga_turno",
            "day_on_requests": "trabalho_dia", "shift_on_requests": "trabalho_turno"}[fam]
    return sum(1 for p in inst.pedidos if p.tipo == tipo and p.profissional == n and p.peso > 0)


def pesos_de(inst, fam: str) -> list[int]:
    """Pesos com que a familia esta ativa na instancia (um por contrato, padrao ou pedido)."""
    if fam in CONTRATO:
        return [getattr(c, fam).peso for c in inst.contratos.values() if getattr(c, fam).ativa]
    if fam == "unwanted_patterns":
        usados = {pid for c in inst.contratos.values() for pid in c.padroes_indesejados}
        return [inst.padroes[p].peso for p in usados if p in inst.padroes
                and inst.padroes[p].peso > 0]
    tipo = {"day_off_requests": "folga_dia", "shift_off_requests": "folga_turno",
            "day_on_requests": "trabalho_dia", "shift_on_requests": "trabalho_turno"}[fam]
    return [p.peso for p in inst.pedidos if p.tipo == tipo and p.peso > 0]


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    achadas, _ = descobrir_instancias()
    familias = CONTRATO + OUTRAS
    linhas = []
    ativas = Counter()
    pesos = defaultdict(Counter)
    maior = {}
    for a in sorted(achadas, key=lambda a: (a["track"], a["lote"], a["numero"])):
        inst = ler_instancia(a["caminho"])
        nome = a["nome_literatura"]
        for fam in familias:
            ps = pesos_de(inst, fam)
            lim = sum(limite(inst, fam, n) for n in inst.profissionais)
            if ps:
                ativas[fam] += 1
                pesos[fam].update(ps)
            if fam == "no_night_shift_before_free_weekend":
                obs = "avaliador não pontua (DECISOES 18/09)"
            else:
                obs = ""
            linhas.append((nome, inst.id, len(inst.profissionais), len(inst.dias), fam,
                           len(ps), ",".join(str(p) for p in sorted(set(ps))), lim, obs))
            if lim > maior.get(fam, (0, ""))[0]:
                maior[fam] = (lim, nome)
    with open(SAIDA / "censo.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["instancia", "id_xml", "profissionais", "dias", "familia",
                    "ocorrencias_ativas", "pesos", "limite_superior_violacoes", "obs"])
        w.writerows(linhas)
    md = ["# Censo das flexíveis nas 69 instâncias do INRC-2010 (19/10/2026)", "",
          "Gerado por `python docs\\diagnostico\\censo_flexiveis.py`, sem solver. Ativa = regra "
          "de 15/09 (ligada e peso > 0) em pelo menos um contrato; pedidos e padrões, com peso "
          "> 0. Ocorrências = contratos (ou padrões, ou pedidos) em que está ativa. Limite = "
          "limite superior de violações por instância, em unidades de excesso (peso 1), somado "
          "sobre os profissionais; válido, não justo. Detalhe por instância: `censo.csv`.", "",
          "| Família | Instâncias com a família ativa (de 69) | Pesos observados (peso: ocorrências) "
          "| Limite: fórmula | Maior limite (instância) |", "|---|---:|---|---|---|"]
    for fam in familias:
        p = ", ".join(f"{k}: {v}" for k, v in sorted(pesos[fam].items())) or "—"
        lim, onde = maior.get(fam, (0, "—"))
        md.append(f"| `{fam}` | {ativas[fam]} | {p} | {LIMITES[fam]} | {lim} ({onde}) |")
    (SAIDA / "censo.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"censo gravado em {SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
