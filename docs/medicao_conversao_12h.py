"""Medicao de apoio a proposta P5: discretizacao da demanda em blocos de 12 h.

NAO faz parte do pipeline. Nao e importado por nada em src/. Esta em docs/ porque e a
evidencia reproduzivel dos numeros da entrada P5 do PROPOSTAS.md, nao codigo do modelo.

Roda da raiz do repositorio, com a .venv ativa:

    python docs\\medicao_conversao_12h.py

O que mede, sobre o long01 (5.920 horas-profissional, 384 delas de enfermeiro-chefe):

1. o perfil horario exato da demanda, reagregado em janelas de 12 h, em tres pontos de corte;
2. o efeito de tres regras de arredondamento sobre o total de horas;
3. a demanda por dia da semana, que a media diaria esconde;
4. o pico de 48 h — quatro janelas consecutivas — que e o que dimensiona o efetivo sob 12x36,
   porque o descanso de 36 h deixa um profissional entrar em no maximo uma janela a cada quatro;
5. a faixa admissivel inteira desse pico, resolvendo um MILP com a demanda por janela livre
   entre piso e teto e o total do horizonte fixado. E o encaminhamento 1 da P5;
6. o proprio long01 reagregado em janelas de 8 h, que mostra que o braco de 8 h tambem e
   uma discretizacao — seus turnos D e DH cruzam a fronteira das 14:30. Sustenta a Revisao 2.

Corte de referencia: 06:30/18:30, alinhado ao inicio do turno E. Divide o horizonte em
exatamente 56 janelas, sem fatia parcial.
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

sys.path.insert(0, "src")

from parser import ler_instancia  # noqa: E402

ALVO = "instancias/long/long/long01.xml"
CORTE = 6.5
DIAS = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]


# --- perfil horario -------------------------------------------------------------------

def horas_do_turno(t) -> float:
    ini = t.inicio.hour + t.inicio.minute / 60
    fim = t.fim.hour + t.fim.minute / 60
    if fim <= ini:
        fim += 24
    return fim - ini


def perfil_horario(inst, apenas_chefe=False):
    """Demanda em profissionais presentes por meia-hora absoluta do horizonte.

    Chave: indice de meia-hora desde 00:00 do primeiro dia. Valor: quantos profissionais a
    instancia exige presentes naquele intervalo de 30 min.
    """
    perfil = defaultdict(int)
    for (dia, tid), qtd in inst.demanda.items():
        t = inst.turnos[tid]
        if apenas_chefe and "HeadNurse" not in t.habilidades:
            continue
        base = inst.indice(dia) * 48
        ini = t.inicio.hour * 2 + t.inicio.minute // 30
        for k in range(int(round(horas_do_turno(t) * 2))):
            perfil[base + ini + k] += qtd
    return perfil


def horas_profissional(perfil) -> float:
    return sum(perfil.values()) * 0.5


def converter(perfil, corte_h, arredondar):
    """Agrega o perfil em janelas de 12 h a partir de `corte_h`.

    Devolve {indice da janela: efetivo exigido}. `arredondar` recebe as horas-profissional
    da janela dividido por 12; passe `lambda x: x` para obter a demanda exata fracionaria.
    """
    off = int(corte_h * 2)
    janelas = defaultdict(int)
    for k, v in perfil.items():
        janelas[(k - off) // 24] += v
    return {j: arredondar(v / 24) for j, v in janelas.items()}


def pico_48h(janelas) -> float:
    """Maior soma de quatro janelas consecutivas. Piso do efetivo sob 12x36."""
    v = [janelas[i] for i in sorted(janelas)]
    return max(sum(v[i:i + 4]) for i in range(len(v) - 3))


def maior_resto(bruto, alvo_blocos):
    """Metodo de Hamilton: piso em toda janela, depois distribui os blocos que faltam pelas
    janelas de maior parte fracionaria."""
    piso = {j: math.floor(v) for j, v in bruto.items()}
    faltam = alvo_blocos - sum(piso.values())
    for j in sorted(bruto, key=lambda j: bruto[j] - piso[j], reverse=True)[:max(faltam, 0)]:
        piso[j] += 1
    return piso


# --- medicao 1: o total ---------------------------------------------------------------

def medicao_total(inst):
    print("1. EFEITO DAS REGRAS DE ARREDONDAMENTO SOBRE O TOTAL DE HORAS")
    print()
    for nome, so_chefe in (("todas as categorias", False), ("so o chefe", True)):
        perfil = perfil_horario(inst, apenas_chefe=so_chefe)
        h0 = horas_profissional(perfil)
        print(f"   {nome} — {h0:.0f} h = {h0 / 12:.2f} blocos de 12 h")
        for corte in (6.5, 7.0, 8.0):
            bruto = converter(perfil, corte, lambda x: x)
            teto = sum(math.ceil(v) for v in bruto.values()) * 12
            mr = sum(maior_resto(bruto, round(h0 / 12)).values()) * 12
            print(f"      corte {corte:4.1f} ({len(bruto)} janelas): "
                  f"teto {teto:6.0f} h ({teto - h0:+.0f} h, {(teto / h0 - 1) * 100:+.1f}%) | "
                  f"maior resto {mr:6.0f} h ({mr - h0:+.0f} h, {(mr / h0 - 1) * 100:+.2f}%)")
        print()


# --- medicao 2: a demanda por dia da semana -------------------------------------------

def medicao_dia_da_semana(inst):
    print("2. DEMANDA POR DIA DA SEMANA (a media diaria esconde a diferenca util/fim de semana)")
    print()
    tipos = list(inst.turnos)
    print("      " + "".join(f"{t:>7s}" for t in tipos) + f"{'total':>8s}")
    for w in range(7):
        dias = [d for d in inst.dias if d.weekday() == w]
        linha = {t: sum(inst.demanda.get((d, t), 0) for d in dias) / len(dias) for t in tipos}
        print(f"   {DIAS[w]:3s}" + "".join(f"{linha[t]:7.2f}" for t in tipos)
              + f"{sum(linha.values()):8.2f}")
    print()


# --- medicao 3: o pico de 48 h e a faixa admissivel -----------------------------------

def faixa_do_pico(bruto, alvo_blocos):
    """Menor e maior pico de 48 h atingiveis com a demanda por janela inteira entre piso e
    teto e o total do horizonte fixado em `alvo_blocos`. Encaminhamento 1 da P5."""
    idx = sorted(bruto)
    n = len(idx)
    lo = np.array([math.floor(bruto[i]) for i in idx], float)
    hi = np.array([math.ceil(bruto[i]) for i in idx], float)
    total = LinearConstraint(np.ones((1, n)), [alvo_blocos], [alvo_blocos])

    # minimo: variavel auxiliar t >= cada soma de quatro janelas consecutivas
    c = np.zeros(n + 1)
    c[-1] = 1.0
    linhas = [np.r_[np.ones(n), 0.0]]
    lb, ub = [alvo_blocos], [alvo_blocos]
    for w in range(n - 3):
        linha = np.zeros(n + 1)
        linha[w:w + 4] = 1.0
        linha[-1] = -1.0
        linhas.append(linha)
        lb.append(-np.inf)
        ub.append(0.0)
    r = milp(c=c, constraints=LinearConstraint(np.array(linhas), lb, ub),
             integrality=np.r_[np.ones(n), 1.0],
             bounds=Bounds(np.r_[lo, 0.0], np.r_[hi, np.inf]))
    minimo = r.fun

    # maximo: o maior pico e' o melhor entre maximizar cada janela de quatro em separado
    maximo = -1.0
    for w in range(n - 3):
        cc = np.zeros(n)
        cc[w:w + 4] = -1.0
        r = milp(c=cc, constraints=total, integrality=np.ones(n), bounds=Bounds(lo, hi))
        maximo = max(maximo, -r.fun)
    return minimo, maximo


def medicao_pico(inst):
    print("3. PICO DE 48 H — o que dimensiona o efetivo sob 12x36")
    print()
    for nome, so_chefe in (("todas as categorias", False), ("so o chefe", True)):
        perfil = perfil_horario(inst, apenas_chefe=so_chefe)
        h0 = horas_profissional(perfil)
        bruto = converter(perfil, CORTE, lambda x: x)
        alvo = round(h0 / 12)
        exato = pico_48h(bruto)
        teto = pico_48h({k: math.ceil(v) for k, v in bruto.items()})
        mr = pico_48h(maior_resto(bruto, alvo))
        mn, mx = faixa_do_pico(bruto, alvo)
        print(f"   {nome} — total fixado em {alvo} blocos")
        print(f"      demanda exata fracionaria  {exato:6.2f}")
        print(f"      teto                       {teto:6.0f}  ({(teto / exato - 1) * 100:+.1f}%)")
        print(f"      maior resto                {mr:6.0f}  ({(mr / exato - 1) * 100:+.1f}%)")
        print(f"      faixa admissivel inteira   [{mn:.0f}, {mx:.0f}]  "
              f"<- as duas regras caem no topo")
        print()


# --- medicao 4: o long01 submetido ao proprio procedimento ----------------------------

def medicao_simetria(inst):
    """O braco de 8 h tambem e uma discretizacao? Reagrega o perfil em janelas de 8 h,
    sem sobreposicao, e compara com a reagregacao em 12 h. Sustenta a Revisao 2 da P5."""
    print("4. O LONG01 SUBMETIDO AO PROPRIO PROCEDIMENTO (janelas de 8 h, sem sobreposicao)")
    print()
    for nome, so_chefe in (("todas as categorias", False), ("so o chefe", True)):
        perfil = perfil_horario(inst, apenas_chefe=so_chefe)
        h0 = horas_profissional(perfil)
        for dur in (8, 12):
            off = int(CORTE * 2)
            larg = int(dur * 2)
            jan = defaultdict(int)
            for k, v in perfil.items():
                jan[(k - off) // larg] += v
            bruto = {a: b / larg for a, b in jan.items()}
            frac = [v for v in bruto.values() if abs(v - round(v)) > 1e-9]
            teto = sum(math.ceil(v) for v in bruto.values()) * dur
            print(f"   {nome:20s} janelas de {dur:2d} h: {len(bruto):3d} janelas, "
                  f"{len(frac):3d} fracionarias | teto {teto:6.0f} h contra {h0:6.0f} h "
                  f"({(teto / h0 - 1) * 100:+.1f}%)")
        print()
    print("   Causa: E 06:30-14:30, L 14:30-22:30 e N 22:30-06:30 se encaixam, mas D e DH")
    print("   vao de 08:30 a 16:30 e cruzam a fronteira das 14:30. O long01 nao e uma")
    print("   particao do dia em janelas de 8 h — e um conjunto de turnos sobrepostos.")
    print()

if __name__ == "__main__":
    inst = ler_instancia(ALVO)
    print(f"{inst.id}: {inst.demanda_total} atribuicoes, "
          f"{horas_profissional(perfil_horario(inst)):.0f} horas-profissional, "
          f"{horas_profissional(perfil_horario(inst, apenas_chefe=True)):.0f} h de chefe")
    print()
    medicao_total(inst)
    medicao_dia_da_semana(inst)
    medicao_pico(inst)
    medicao_simetria(inst)
