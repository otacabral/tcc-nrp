"""Medicao de apoio a proposta P5: sobreposicao de turnos nas 69 instancias do INRC-2010.

NAO faz parte do pipeline. Nao e importado por nada em src/. Esta em docs/ porque e a
evidencia reproduzivel da Revisao 3 da P5, nao codigo do modelo.

Roda da raiz do repositorio, com a .venv ativa:

    python docs\\medicao_sobreposicao.py

A pergunta: o efeito medido em docs/medicao_conversao_12h.py e propriedade do long01 ou das
instancias do INRC? Nao e sobre regime de jornada — e sobre REAGREGAR TURNOS SOBREPOSTOS EM
JANELAS DISJUNTAS. Uma instancia cujos turnos particionam o dia nao tem esse residuo.

Para cada instancia mede:

- se ha par de tipos de turno que se sobrepoe parcialmente (nao identicos);
- a inflacao do teto ao reagregar o perfil horario em janelas disjuntas de 8 h e de 12 h,
  no total e na categoria de habilidade mais escassa (quando ha mais de uma habilidade);
- o corte das janelas e o inicio do turno mais cedo da instancia.

As instancias sem sobreposicao sao o grupo de controle: nelas o residuo em janelas de 8 h
tem de ser zero, porque os turnos ja SAO uma particao em blocos de 8 h.
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict

sys.path.insert(0, "src")

from parser import descobrir_instancias, ler_instancia  # noqa: E402


def intervalos(inst):
    """{id do turno: (inicio, fim)} em meias-horas desde 00:00; fim pode passar de 48."""
    out = {}
    for t in inst.turnos.values():
        ini = t.inicio.hour * 2 + t.inicio.minute // 30
        fim = t.fim.hour * 2 + t.fim.minute // 30
        if fim <= ini:
            fim += 48
        out[t.id] = (ini, fim)
    return out


def ha_sobreposicao(iv) -> bool:
    """Existe par de turnos distintos com interseccao de tempo? Turnos identicos (mesmo
    horario, habilidades diferentes) nao contam: eles nao quebram a particao."""
    ids = list(iv)
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            p, q = iv[ids[a]], iv[ids[b]]
            if p == q:
                continue
            for desloc in (0, 48, -48):
                if max(p[0], q[0] + desloc) < min(p[1], q[1] + desloc):
                    return True
    return False


def perfil(inst, habilidade=None):
    """Demanda em profissionais presentes por meia-hora absoluta do horizonte."""
    p = defaultdict(int)
    iv = intervalos(inst)
    for (dia, tid), qtd in inst.demanda.items():
        if habilidade is not None and habilidade not in inst.turnos[tid].habilidades:
            continue
        ini, fim = iv[tid]
        base = inst.indice(dia) * 48
        for k in range(ini, fim):
            p[base + k] += qtd
    return p


def inflacao_do_teto(p, corte_h, dur_h):
    """Quanto o teto por janela disjunta acrescenta as horas-profissional originais."""
    if not p:
        return None
    off, larg = int(corte_h * 2), int(dur_h * 2)
    jan = defaultdict(int)
    for k, v in p.items():
        jan[(k - off) // larg] += v
    horas = sum(p.values()) * 0.5
    teto = sum(math.ceil(v / larg) for v in jan.values()) * dur_h
    return teto / horas - 1


def main():
    def fmt(x):
        return "      - " if x is None else f"{x * 100:+7.1f}%"

    print(f"{'instancia':20s}{'turnos':>7s}{'sobrep':>8s}"
          f"{'8h tot':>9s}{'12h tot':>9s}{'8h escassa':>12s}{'12h escassa':>13s}  escassa")
    linhas = []
    for desc in descobrir_instancias()[0]:
        inst = ler_instancia(desc["caminho"], validar=False)
        iv = intervalos(inst)
        corte = min(i for i, _ in iv.values()) / 2
        t8 = inflacao_do_teto(perfil(inst), corte, 8)
        t12 = inflacao_do_teto(perfil(inst), corte, 12)
        habs = sorted({h for t in inst.turnos.values() for h in t.habilidades})
        escassa, e8, e12 = "-", None, None
        if len(habs) > 1:
            escassa = min(habs, key=lambda h: sum(perfil(inst, h).values()))
            e8 = inflacao_do_teto(perfil(inst, escassa), corte, 8)
            e12 = inflacao_do_teto(perfil(inst, escassa), corte, 12)
        linhas.append((desc["nome_literatura"], len(iv), ha_sobreposicao(iv),
                       t8, t12, e8, e12, escassa))
        l = linhas[-1]
        print(f"{l[0]:20s}{l[1]:7d}{('SIM' if l[2] else 'nao'):>8s}"
              f"{fmt(l[3])}{fmt(l[4])}{fmt(l[5])}{fmt(l[6])}  {l[7]}")

    n = len(linhas)
    com_sobrep = [l for l in linhas if l[2]]
    sem_sobrep = [l for l in linhas if not l[2]]
    com_escassa = [l for l in linhas if l[5] is not None]
    pior_em_8h = [l for l in com_escassa if l[5] > l[6]]

    print()
    print(f"{len(com_sobrep)} de {n} instancias tem turnos que se sobrepoem parcialmente.")
    print(f"Grupo de controle — as {len(sem_sobrep)} sem sobreposicao: "
          f"inflacao em janelas de 8 h = "
          f"{sorted({round(l[3] * 100, 1) for l in sem_sobrep})}, "
          f"em janelas de 12 h = {sorted({round(l[4] * 100, 1) for l in sem_sobrep})}.")
    print(f"{len(com_escassa)} de {n} tem mais de uma habilidade. Nessas, a categoria escassa "
          f"infla MAIS em 8 h que em 12 h em {len(pior_em_8h)} de {len(com_escassa)}.")


if __name__ == "__main__":
    main()
