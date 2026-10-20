"""Caso A — Massens (2019), Clinica Ortovascular, Anexo B (p. 70): entrada da ferramenta.

Fase 1 (20/10): so a entrada; as rodadas sao da fase 2 (depois da suite e da tag v1.4.0).
Fonte de cada campo: `D:\TCC\escrita\fontes\FICHA_CASO_REALISTA.md` e o pedido da Orientacao
de 20/10. Leituras adotadas: `resultados/relatorio_2026-10-20b.md`.

    from entrada import entrada            # (com resultados/caso_a_2026-10-20 no sys.path)
    e1 = entrada("turno_fixo"); e2 = entrada("rodizio_livre")
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import ferramenta as fe  # noqa: E402
import prioridades as pr  # noqa: E402

INICIO = date(2027, 1, 4)                 # segunda; 28 dias, ate 31/01/2027, sem feriado
ORCAMENTO = 60 * 60                       # segundos
TURNOS = [("M", 7, 13), ("T", 13, 19), ("N", 19, 7), ("D12", 7, 19)]

# 4 enfermeiros: as linhas do Anexo B
ENFERMEIROS = ["Enf 6118", "Enf 4798", "Enf 4969", "Enf 5993"]
# 20 tecnicos: as equipes (os ids das linhas nao foram passados; nomes provisorios por equipe —
# trocar pelo id do Anexo B nao muda o modelo), o volante noturno 4309 e o integral 6089
MANHA = [f"Manhã {i}" for i in range(1, 6)]
TARDE = [f"Tarde {i}" for i in range(1, 6)]
NOITE_A = [f"Noite A {i}" for i in range(1, 5)]
NOITE_B = [f"Noite B {i}" for i in range(1, 5)]
VOLANTE, INTEGRAL = "Téc 4309", "Téc 6089"
TECNICOS = MANHA + TARDE + NOITE_A + NOITE_B + [VOLANTE, INTEGRAL]

# demanda: (enfermeiros, tecnicos) por turno
DIA_UTIL = {"M": (1, 5), "T": (1, 5), "N": (1, 4), "D12": (0, 0)}
FIM_DE_SEMANA = {"M": (0, 0), "T": (0, 0), "N": (1, 4), "D12": (1, 5)}

# ferias (ficha: 1 tecnico da tarde a partir do dia 5; 1 da noite a partir do dia 15; duracao de
# 15 dias, a do cenario 2 de Massens para tarde e noite A — suposicao declarada)
FERIAS = [(TARDE[0], date(2027, 1, 5), date(2027, 1, 19)),
          (NOITE_A[0], date(2027, 1, 15), date(2027, 1, 29))]


def regras_turno_fixo() -> list:
    """Rodada 1: "So este turno", Essencial. Manha e tarde tambem fazem o D12 do fim de semana."""
    L, E = pr.Linha, pr.ESSENCIAL
    linhas = []
    for n in MANHA:
        linhas += [L(n, None, "M", pr.SO_TURNO, E), L(n, None, "D12", pr.SO_TURNO, E)]
    for n in TARDE:
        linhas += [L(n, None, "T", pr.SO_TURNO, E), L(n, None, "D12", pr.SO_TURNO, E)]
    for n in NOITE_A + NOITE_B + [VOLANTE]:
        linhas.append(L(n, None, "N", pr.SO_TURNO, E))
    return linhas                          # o integral 6089: sem linha


def entrada(rodada: str) -> fe.Entrada:
    if rodada not in ("turno_fixo", "rodizio_livre"):
        raise ValueError(rodada)
    return fe.Entrada(
        turnos=TURNOS, grau="intermediario", n_enfermeiros=len(ENFERMEIROS),
        n_tecnicos=len(TECNICOS), demanda_turno=DIA_UTIL, demanda_fds=FIM_DE_SEMANA,
        fim_de_semana="sab_dom", inicio=INICIO, nomes_enfermeiros=ENFERMEIROS,
        nomes_tecnicos=TECNICOS, indisponibilidades=FERIAS,
        regras=regras_turno_fixo() if rodada == "turno_fixo" else [],
        prioridades=None)                  # classificacao PADRAO; carga 44 h para todos
