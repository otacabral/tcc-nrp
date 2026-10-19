"""Controle positivo da validacao por restricao (19/10). Esperado registrado antes em
`resultados/validacao_restricoes_2026-10-19/ESPERADO.md` (adendo).

(c1) a conferencia consegue falhar: escala perturbada x saida do avaliador da ORIGINAL;
(c2) avaliador x modelo fora do otimo: a escala perturbada, reavaliada pelo avaliador oficial.

Perturbacao: troca que preserva cobertura e um turno por dia — num dia sorteado, ou dois
profissionais trocam de turno, ou o turno de quem trabalha passa para quem esta de folga.

    python docs\\diagnostico\\validacao_restricoes_controle.py
"""

from __future__ import annotations

import random
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from avaliacao import violacoes  # noqa: E402
from parser import ler_instancia  # noqa: E402
from solucao import conferir_rigidas, escrever_xml, ler_xml  # noqa: E402
from validar import avaliar  # noqa: E402
from validacao_restricoes import (ALVOS, SAIDA, avaliar_no_modelo,  # noqa: E402
                                  ler_avaliador, um_turno_por_dia_xml)

POR_INSTANCIA, TROCAS, SEMENTE = 5, 8, 20261019


def perturbar(inst, escala, rng):
    agenda = {(n, d): s for d, n, s in escala}
    profs, dias = list(inst.profissionais), list(inst.dias)
    feitas = 0
    while feitas < TROCAS:
        d = rng.choice(dias)
        a, b = rng.sample(profs, 2)
        sa, sb = agenda.get((a, d)), agenda.get((b, d))
        if sa == sb:
            continue
        for n, s in ((a, sb), (b, sa)):
            if s is None:
                agenda.pop((n, d), None)
            else:
                agenda[(n, d)] = s
        feitas += 1
    return tuple(sorted(((d, n, s) for (n, d), s in agenda.items()),
                        key=lambda x: (x[0], x[1], x[2])))


def comparar(inst, escala, grade, aval):
    """(grade = escala?, tipos com diferenca, celulas prof x tipo com diferenca,
    total do avaliador, objetivo do modelo, restricoes violadas)."""
    dias = list(inst.dias)
    grade_ok = grade == {(n, dias.index(d)): s for d, n, s in escala}
    violadas, obj, parcela, pena = avaliar_no_modelo(inst, escala)
    py = defaultdict(int)
    for v in violacoes(inst, escala):
        py[(v.profissional, v.restricao)] += v.custo
    familias = sorted({f for _, f in aval} | set(parcela))
    tipos = sum(1 for f in familias
                if sum(c for (_, g), c in aval.items() if g == f) != parcela.get(f, 0))
    celulas = sum(1 for n in inst.profissionais for f in familias
                  if aval.get((n, f), 0) != pena.get((n, f), 0)
                  or aval.get((n, f), 0) != py.get((n, f), 0))
    return grade_ok, tipos, celulas, sum(aval.values()), obj, violadas


def main() -> int:
    rng = random.Random(SEMENTE)
    destino = SAIDA / "controle"
    destino.mkdir(parents=True, exist_ok=True)
    linhas = ["| Instância | Escala | Mudou | c1: grade = XML | c1: tipos ≠ | c1: total original × "
              "modelo | c2: duras (aval/XML/rígidas/modelo) | c2: avaliador | c2: modelo | "
              "c2: tipos ≠ | c2: células ≠ |",
              "|---|---|---|---|---:|---|---|---:|---:|---:|---:|"]
    falhas = []
    for nome, caminho, z6 in ALVOS:
        inst = ler_instancia(RAIZ / caminho)
        _, _, escala = ler_xml(RAIZ / "resultados" / f"{nome}_completo.xml")
        grade0, aval0, total0, _ = ler_avaliador(
            RAIZ / "resultados" / f"{nome}_completo_avaliador.txt")
        for k in range(POR_INSTANCIA):
            nova = perturbar(inst, escala, rng)
            mudou = set(nova) != set(escala)
            # (c1) contra a saida da ORIGINAL: tem de acusar
            g1, t1, _, _, obj1, _ = comparar(inst, nova, grade0, aval0)
            acusou = (not g1) and (t1 > 0 or obj1 != total0)
            # (c2) reavaliada pelo avaliador oficial
            xml = destino / f"{nome}_perturbada{k + 1}.xml"
            escrever_xml(inst, nova, xml, penalidade=0)
            avaliar(RAIZ / caminho, xml)          # grava <xml>_avaliador.txt
            grade2, aval2, total2, erros = ler_avaliador(
                xml.with_name(xml.stem + "_avaliador.txt"))
            g2, t2, c2, _, obj2, vio = comparar(inst, nova, grade2, aval2)
            dup = um_turno_por_dia_xml(xml)
            rig = conferir_rigidas(inst, nova, habilidade_rigida=False)
            ok2 = (g2 and not erros and dup == 0 and not rig and not vio
                   and total2 == obj2 and total2 >= z6 and t2 == 0 and c2 == 0)
            if not (mudou and acusou and ok2):
                falhas.append(f"{nome} #{k + 1}")
            linhas.append(
                f"| {nome} | perturbada {k + 1} | {'sim' if mudou else 'não'} | "
                f"{'sim' if g1 else 'não'} | {t1} | {total0} × {obj1} | "
                f"{len(erros)}/{dup}/{len(rig)}/{len(vio)} | {total2} | {obj2} | {t2} | {c2} |")
            print(linhas[-1], flush=True)
    texto = ["# Controle positivo da validação por restrição (19/10/2026)", "",
             f"Semente {SEMENTE}; {POR_INSTANCIA} escalas por instância, {TROCAS} trocas cada. "
             "Escalas e saídas do avaliador nesta pasta.", ""] + linhas + [
             "", "TUDO OK" if not falhas else f"FALHOU: {falhas}"]
    (destino / "controle.md").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print(texto[-1])
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
