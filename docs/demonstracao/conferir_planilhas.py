"""Confere as planilhas BAIXADAS da demonstracao, sem usar o que a tela calculou (08/10, P12).

    python docs\\demonstracao\\conferir_planilhas.py

Para cada rodada, le `<rodada>_escala.xlsx` (aba Escala), remonta a escala atribuicao por
atribuicao a partir dos codigos das celulas e passa por `solucao.conferir_rigidas`
(cobertura e um turno por dia, habilidade rigida), pelo descanso medido no relogio
(`conferencia_descanso_escala`), pelo teto de horas e pelas ferias. A instancia sai dos dados
do caso (`caso_clinica_medica.entrada`), com o quadro que a planilha mostra.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(AQUI))

import caso_clinica_medica as caso  # noqa: E402
import ferramenta as fe  # noqa: E402
import solucao  # noqa: E402

RODADAS = {"rodada1": None, "rodada2_19tec": 19, "rodada2_18tec": 18}


def instancia(e, nomes: list[str]):
    """A instancia com o quadro da planilha: a composicao da regra ou a de so enfermeiros."""
    acrescimo = len(nomes) - e.quadro
    if acrescimo == 0:
        return fe.montar(e)
    for so_enf in (False, True):
        inst = fe.montar(e, acrescimo, fe._horas_enfermeiro(e), so_enfermeiros=so_enf)
        if sorted(p.nome for p in inst.profissionais.values()) == sorted(nomes):
            return inst
    raise ValueError("nenhuma composicao tem os nomes da planilha")


def cobertura_declarada(e, inst, tab) -> list:
    """Dias e turnos em que a planilha cobre diferente da demanda DECLARADA no caso. Pega
    entrada digitada errada na tela (o feriado de 20/11 colado em 24/11 ate 08/10), que
    `conferir_rigidas` nao pega se a instancia vier do que a tela recebeu."""
    declarada = fe.montar(e)
    rot = fe.rotulos(inst)
    dif = []
    for k, d in enumerate(inst.dias):
        cont = tab[tab.columns[2 + k]].dropna().value_counts().to_dict()
        for s in inst.turnos:
            if cont.get(rot[s], 0) != declarada.demanda_de(d, s):
                dif.append((fe.rotulo_dia(d), s, declarada.demanda_de(d, s), cont.get(rot[s], 0)))
    return dif


def conferir(rodada: str, tec: int | None) -> bool:
    arq = AQUI / f"{rodada}_escala.xlsx"
    tab = pd.read_excel(arq, sheet_name="Escala", index_col=0)
    e = caso.entrada(tec)
    inst = instancia(e, list(tab.index))
    por_nome = {p.nome: n for n, p in inst.profissionais.items()}
    codigo = {v: k for k, v in fe.rotulos(inst).items()}
    escala = []
    for nome, linha in tab.iterrows():
        for k, d in enumerate(inst.dias):
            c = linha.iloc[2 + k]
            if isinstance(c, str) and c and c != "indisp.":
                escala.append((d, por_nome[nome], codigo[c]))
    rigidas = solucao.conferir_rigidas(inst, escala, habilidade_rigida=True)
    m = fe.medir(inst, escala)
    horas = {n: 0.0 for n in inst.profissionais}
    for _, n, s in escala:
        horas[n] += inst.turnos[s].duracao_h
    acima = [n for n, h in horas.items() if h > inst.horas_devidas(n) + 1e-6]
    ferias = [(d, n) for d, n, _ in escala if (n, d) in inst.indisponiveis]
    ok = not rigidas and fe.cumpre(inst, m) and not acima and not ferias
    dif = cobertura_declarada(e, inst, tab)
    ok = ok and not dif
    print(f"{rodada}: cobertura contra a demanda DECLARADA no caso: {dif or 'igual em todos os dias'}")
    print(f"{rodada}: {len(tab)} profissionais, {len(escala)} atribuicoes | rigidas "
          f"{rigidas[:2] or 'ok'} | descanso {'cumpre' if fe.cumpre(inst, m) else 'NAO CUMPRE'} "
          f"(menor folga {m['menor_folga']:.0f} h, semanal {fe.fmt_semanal(m['menor_semanal'])}, "
          f"{m['max_consec']} dias seguidos) | teto {acima or 'ok'} | ferias {ferias or 'ok'}")
    return ok


def main() -> int:
    """Sem argumento, as tres rodadas; com argumentos, so as nomeadas (o `rodar_rodada.sh`
    chama uma por vez, no fim de cada rodada)."""
    nomes = sys.argv[1:] or list(RODADAS)
    ok = all([conferir(r, RODADAS[r]) for r in nomes])
    print("planilhas da demonstracao: OK" if ok else "planilhas da demonstracao: FALHA")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
