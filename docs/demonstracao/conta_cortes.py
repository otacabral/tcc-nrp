"""Rodada 2 da demonstracao: corte de tecnicos esperado PELA CONTA, antes de rodar.

    python docs\\demonstracao\\conta_cortes.py

Sem solver e sem as contas da ferramenta (`ferramenta.piso`, `ferramenta.diagnosticar`): a
conta e feita aqui, a partir dos dados de `caso_clinica_medica.py`, para nao conferir a
ferramenta com a propria premissa (CLAUDE.md). Os alertas do COFEN sao a definicao do
proprio Parecer, e por isso saem de `instancia_br.alertas_cofen`.

Para cada numero de tecnicos (os primeiros da lista do caso), de 22 para baixo:

1. Horas do posto de tecnico (H_tec) contra a soma dos tetos dos tecnicos (C_tec). O teto de
   cada um e o menor entre a carga contratual nos dias disponiveis e a alternancia do 12x36
   (no maximo ceil(d / 2) plantoes de 12 h em d dias disponiveis seguidos). O que falta,
   H_tec - C_tec, so enfermeiro cobre: minimo de turnos de enfermeiro em posto de tecnico =
   ceil(falta / 12).
2. Folga dos enfermeiros: C_enf (mesmo teto) - H_enf (horas do posto de enfermeiro). Se a
   falta de tecnicos passa da folga dos enfermeiros, trava por horas.
3. Soma de dois dias seguidos do 12x36: ninguem trabalha dois dias seguidos, entao em cada
   par de dias a demanda total tem de caber nas pessoas disponiveis em pelo menos um dos
   dois dias; o mesmo para o posto de enfermeiro e os enfermeiros.
"""

from __future__ import annotations

import math
import sys
from datetime import timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "src"))

import caso_clinica_medica as caso  # noqa: E402
import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402

DIAS = [caso.INICIO + timedelta(days=k) for k in range(28)]
DUR = 12


def demanda(d):
    """(enf, tec) de cada turno no dia d, pela regra do caso."""
    if d in caso.FERIADOS:
        return caso.DEMANDA_FERIADO
    if d.weekday() >= 5:
        return caso.DEMANDA_FDS
    return caso.DEMANDA


def disponiveis(nome):
    fora = set()
    for n, a, b in caso.FERIAS:
        if n == nome:
            fora |= {a + timedelta(days=k) for k in range((b - a).days + 1)}
    return [d for d in DIAS if d not in fora]


def teto_h(nome):
    carga = 36 if nome in caso.CARGAS_36 else 44
    disp = disponiveis(nome)
    contrato = carga * len(disp) / 7
    # alternancia: em cada bloco de dias disponiveis seguidos, no maximo ceil(tamanho/2)
    plantoes, bloco = 0, 0
    for d in DIAS + [None]:
        if d is not None and d in disp:
            bloco += 1
        else:
            plantoes += math.ceil(bloco / 2)
            bloco = 0
    return min(contrato, plantoes * DUR)


def conta(n_tec):
    tecnicos = caso.TECNICOS[:n_tec]
    h_tec = sum(sum(t for _, t in demanda(d).values()) for d in DIAS) * DUR
    h_enf = sum(sum(e for e, _ in demanda(d).values()) for d in DIAS) * DUR
    c_tec = sum(teto_h(n) for n in tecnicos)
    c_enf = sum(teto_h(n) for n in caso.ENFERMEIROS)
    falta = max(0.0, h_tec - c_tec)
    folga_enf = c_enf - h_enf
    pessoas = caso.ENFERMEIROS + tecnicos
    pior_par, pior_par_enf = None, None
    for d0, d1 in zip(DIAS, DIAS[1:]):
        dem = sum(sum(x) for x in demanda(d0).values()) + sum(sum(x) for x in demanda(d1).values())
        dem_enf = sum(e for e, _ in demanda(d0).values()) + sum(e for e, _ in demanda(d1).values())
        livres = sum(1 for n in pessoas if d0 in disponiveis(n) or d1 in disponiveis(n))
        livres_enf = sum(1 for n in caso.ENFERMEIROS
                         if d0 in disponiveis(n) or d1 in disponiveis(n))
        if pior_par is None or dem - livres > pior_par[0]:
            pior_par = (dem - livres, d0, dem, livres)
        if pior_par_enf is None or dem_enf - livres_enf > pior_par_enf[0]:
            pior_par_enf = (dem_enf - livres_enf, d0, dem_enf, livres_enf)
    alertas = br.alertas_cofen(fe.montar(caso.entrada(n_tec)), caso.GRAU, caso.PACIENTES)
    trava = []
    if falta > folga_enf + 1e-9:
        trava.append("horas")
    if pior_par[0] > 0:
        trava.append("dois dias seguidos")
    if pior_par_enf[0] > 0:
        trava.append("dois dias seguidos (enfermeiros)")
    return {"n_tec": n_tec, "total": len(pessoas), "h_tec": h_tec, "c_tec": c_tec,
            "enf_em_tec_min": math.ceil(falta / DUR - 1e-9), "folga_enf_h": folga_enf,
            "par": pior_par, "alertas": len(alertas), "trava": trava}


def main() -> int:
    print("| técnicos | total | horas posto téc. | tetos dos téc. | enf. em posto téc. (mín.) "
          "| folga dos enf. | pior par de dias (demanda / disponíveis) | alertas COFEN "
          "| trava pela conta |")
    print("|---|---|---|---|---|---|---|---|---|")
    for n in range(22, 16, -1):
        c = conta(n)
        _, d0, dem, livres = c["par"]
        print(f"| {n} | {c['total']} | {c['h_tec']:.0f} h | {c['c_tec']:.0f} h | "
              f"{c['enf_em_tec_min']} | {c['folga_enf_h']:.0f} h | {d0:%d/%m}–"
              f"{d0 + timedelta(days=1):%d/%m}: {dem} / {livres} | {c['alertas']} | "
              f"{', '.join(c['trava']) or 'não'} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
