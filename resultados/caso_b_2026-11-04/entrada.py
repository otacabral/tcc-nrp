"""Caso B — Massens (2019), quatro setores somados: a entrada de 20/10 com a janela real do Anexo B
(04/11/2026).

Decisao: `DECISOES.md`, "2026-11-04 — Caso A: entrada revista ...; rodadas na v1.4.5", rodada 4:
"Caso B como antes (89, demanda da Tabela 13), so com a janela a)". Tudo o mais vem da entrada de
20/10 (`resultados/caso_b_2026-10-20/entrada.py`, que fica como esta): 89 pessoas (15 enfermeiros,
74 tecnicos), rodizio livre, classificacao padrao, carga 44 h, sem ferias, orcamento 60 min. So
muda o inicio: 29/10/2018 (segunda; 28 dias, ate 25/11/2018), no lugar de 04/01/2027 (tambem
segunda). Feriados de 02/11 e 15/11 sem ajuste de demanda, como no caso A.
"""

from __future__ import annotations

import dataclasses
import importlib.util
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "entrada_caso_b_2026_10_20", RAIZ / "resultados" / "caso_b_2026-10-20" / "entrada.py")
_antiga = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_antiga)

INICIO = date(2018, 10, 29)               # janela a): segunda; 28 dias, ate 25/11/2018
ORCAMENTO = _antiga.ORCAMENTO


def entrada():
    return dataclasses.replace(_antiga.entrada(), inicio=INICIO)
