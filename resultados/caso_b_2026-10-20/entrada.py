"""Caso B — Massens (2019), quatro setores somados: rodada de porte. Entrada da ferramenta.

Fase 1 (20/10): so a entrada; a rodada e da fase 2. 89 pessoas (15 enfermeiros, 74 tecnicos),
rodizio livre, classificacao padrao, carga 44 h, mesmo inicio e horizonte do caso A, sem ferias
(cenario 1 de Massens), orcamento 60 min.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import ferramenta as fe  # noqa: E402

INICIO = date(2027, 1, 4)
ORCAMENTO = 60 * 60
TURNOS = [("M", 7, 13), ("T", 13, 19), ("N", 19, 7), ("D12", 7, 19)]
DIA_UTIL = {"M": (4, 19), "T": (4, 19), "N": (2, 17), "D12": (0, 0)}
FIM_DE_SEMANA = {"M": (0, 0), "T": (0, 0), "N": (2, 17), "D12": (2, 19)}


def entrada() -> fe.Entrada:
    return fe.Entrada(turnos=TURNOS, grau="intermediario", n_enfermeiros=15, n_tecnicos=74,
                      demanda_turno=DIA_UTIL, demanda_fds=FIM_DE_SEMANA, fim_de_semana="sab_dom",
                      inicio=INICIO, prioridades=None)
