"""Caso A — Massens (2019), Clinica Ortovascular, Anexo B (p. 70): entrada revista (04/11/2026).

Decisao: `DECISOES.md`, "2026-11-04 — Caso A: entrada revista pela leitura independente do
Anexo B; rodadas na v1.4.5" (itens a a f). Substitui, para as rodadas de 05/11, a entrada de
20/10 (`resultados/caso_a_2026-10-20/entrada.py`), que fica como esta.

    from entrada import entrada            # (com resultados/caso_a_2026-11-04 no sys.path)
    e1 = entrada("turno_fixo"); e2 = entrada("rodizio_livre")
    entrada("turno_fixo", equipe=22)       # sensibilidade da conta previa: sem o 4309
    entrada("turno_fixo", equipe=24)       # com o 6089 como tecnico (sem linha)
    entrada("turno_fixo", enf_fds=1)       # 1 enfermeiro no plantao diurno do fim de semana

a) janela real: 29/10 a 25/11/2018, 28 dias a partir de uma segunda; feriados de 02/11 e 15/11
   sem ajuste de demanda (o Anexo B nao muda nada nessas colunas);
b) ferias pela faixa cinza (p. 70): 6137 de 31/10 a 15/11; 5976 de 15/11 ao fim da janela;
c) 23: 4 enfermeiros e 19 tecnicos, o volante 4309 como tecnico de noite; a 6089 fora;
d) demanda do Anexo B: plantao diurno do fim de semana 0 enfermeiro + 5 tecnicos;
e) "So este turno" sem dia para todos com horario na escala: 33 linhas;
f) carga 44 h (padrao), grau intermediario (suposicao declarada), sem pacientes nem pedidos.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import ferramenta as fe  # noqa: E402
import prioridades as pr  # noqa: E402

INICIO = date(2018, 10, 29)               # segunda; 28 dias, ate 25/11/2018
ORCAMENTO = 60 * 60                       # segundos
TURNOS = [("M", 7, 13), ("T", 13, 19), ("N", 19, 7), ("D12", 7, 19)]

# os cartoes-ponto do Anexo B como nomes
ENF_MANHA, ENF_TARDE, ENF_NOITE = ["Enf 6118"], ["Enf 4798"], ["Enf 4969", "Enf 5993"]
ENFERMEIROS = ENF_MANHA + ENF_TARDE + ENF_NOITE
MANHA = [f"Téc {c}" for c in (5762, 6262, 5697, 6017, 6209)]
TARDE = [f"Téc {c}" for c in (6003, 6052, 6271, 6187, 6137)]
NOITE_A = [f"Téc {c}" for c in (4158, 5595, 5976, 5337)]
NOITE_B = [f"Téc {c}" for c in (4178, 5923, 4789, 3602)]
VOLANTE = "Téc 4309"                       # evidencia dividida; decisao do Otavio (item c)
INTEGRAL = "Téc 6089"                      # so na sensibilidade com 24 (sem linha)

# demanda: (enfermeiros, tecnicos) por turno
DIA_UTIL = {"M": (1, 5), "T": (1, 5), "N": (1, 4), "D12": (0, 0)}

FERIAS = [("Téc 6137", date(2018, 10, 31), date(2018, 11, 15)),
          ("Téc 5976", date(2018, 11, 15), date(2018, 11, 25))]


def tecnicos(equipe: int = 23) -> list[str]:
    if equipe not in (22, 23, 24):
        raise ValueError(equipe)
    base = MANHA + TARDE + NOITE_A + NOITE_B
    return base + ([] if equipe == 22 else [VOLANTE]) + ([INTEGRAL] if equipe == 24 else [])


def demanda_fds(enf_fds: int = 0) -> dict:
    return {"M": (0, 0), "T": (0, 0), "N": (1, 4), "D12": (enf_fds, 5)}


def regras_turno_fixo(equipe: int = 23, importancia: str = pr.ESSENCIAL) -> list:
    """As 33 linhas "So este turno", sem dia (item e). A importancia e a da rodada: Essencial na
    classificacao padrao e na 1, Desejavel na 2."""
    L, E = pr.Linha, importancia
    linhas = []
    for n in MANHA:
        linhas += [L(n, None, "M", pr.SO_TURNO, E), L(n, None, "D12", pr.SO_TURNO, E)]
    for n in TARDE:
        linhas += [L(n, None, "T", pr.SO_TURNO, E), L(n, None, "D12", pr.SO_TURNO, E)]
    noturnos = NOITE_A + NOITE_B + ([VOLANTE] if equipe != 22 else [])
    linhas += [L(n, None, "N", pr.SO_TURNO, E) for n in noturnos]
    linhas += [L(n, None, "M", pr.SO_TURNO, E) for n in ENF_MANHA]
    linhas += [L(n, None, "T", pr.SO_TURNO, E) for n in ENF_TARDE]
    linhas += [L(n, None, "N", pr.SO_TURNO, E) for n in ENF_NOITE]
    return linhas                          # o 6089 (so com 24): sem linha


def entrada(rodada: str, equipe: int = 23, enf_fds: int = 0,
            importancia: str = pr.ESSENCIAL, prioridades: dict | None = None) -> fe.Entrada:
    if rodada not in ("turno_fixo", "rodizio_livre"):
        raise ValueError(rodada)
    tec = tecnicos(equipe)
    return fe.Entrada(
        turnos=TURNOS, grau="intermediario", n_enfermeiros=len(ENFERMEIROS),
        n_tecnicos=len(tec), demanda_turno=DIA_UTIL, demanda_fds=demanda_fds(enf_fds),
        fim_de_semana="sab_dom", inicio=INICIO, nomes_enfermeiros=ENFERMEIROS,
        nomes_tecnicos=tec, indisponibilidades=FERIAS,
        regras=regras_turno_fixo(equipe, importancia) if rodada == "turno_fixo" else [],
        prioridades=prioridades)           # None = classificacao PADRAO; carga 44 h para todos
