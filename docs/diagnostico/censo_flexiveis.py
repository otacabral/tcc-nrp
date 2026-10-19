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
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import prioridades  # noqa: E402
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


def limite(inst, fam: str, n: str) -> int:
    """Desde 19/10 (2o bloco), a formula mora em `src/prioridades.py`, que a ferramenta usa
    para a regra de fusao da opcao B; fonte unica."""
    return prioridades.limite_por_profissional(inst, fam, n)


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
