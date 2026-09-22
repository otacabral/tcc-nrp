"""Regressao do modelo: um comando, quatro alvos, quatro conferencias cada.

Roda da raiz do repositorio, com a .venv ativa:

    python src\\regressao.py              # sprint01 e sprint02 (rapido, ~segundos)
    python src\\regressao.py --todos      # inclui long01 e long02 (minutos)
    python src\\regressao.py --todos --gravar-escalas   # e grava as escalas otimas

Existe porque o ambiente da sessao nao tem Pyomo — o PyPI esta bloqueado por politica de
rede da organizacao. Toda alteracao no `modelo.py` e escrita sem execucao e precisa desta
regressao rodada localmente antes que a proxima entre. Uma alteracao de cada vez: com duas
pendentes nao se sabe qual quebrou o que.

O que confere, por alvo:

1. **otimo provado** — o solver tem de declarar optimal, nao apenas devolver algo;
2. **valor da Tabela 6** — o objetivo bate com Santos et al. (2016);
3. **espelho semantico** — o objetivo do modelo bate com `avaliacao.py`, que por sua vez ja
   foi conferido contra o avaliador oficial par a par;
4. **decomposicao por profissional** — `sum(m.pena[n])` bate com o objetivo, e cada `pena[n]`
   bate com `avaliacao.py` profissional por profissional. E o invariante que sustenta a
   medida do Experimento B: a fatia de cada pessoa num total fixado em Z*.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pyomo.environ as pyo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import modelo  # noqa: E402
from avaliacao import penalidade, por_profissional  # noqa: E402
from parser import ler_instancia  # noqa: E402
from solucao import escrever_xml  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]

ALVOS = [
    ("sprint01", "instancias/sprint/sprint/sprint01.xml", 56),
    ("sprint02", "instancias/sprint/sprint/sprint02.xml", 58),
    ("long01", "instancias/long/long/long01.xml", 197),
    ("long02", "instancias/long/long/long02.xml", 219),
]


def conferir(nome: str, caminho: str, z_esperado: int, solver: str,
             tempo_limite: int | None, gravar_escala: bool = False) -> list[str]:
    erros = []
    inst = ler_instancia(caminho)
    t0 = time.time()
    m = modelo.construir(inst)
    res = modelo.resolver(m, solver=solver, tempo_limite=tempo_limite, carregar=False)
    seg = time.time() - t0

    if not modelo.resolvido(res):
        return [f"{nome}: solver nao provou otimalidade ({modelo.estado(res)})"]
    if not modelo.carregar_solucao(m, res):
        return [f"{nome}: solver declarou otimo mas nao entregou solucao"]

    z = modelo.valor_objetivo(m)
    escala = modelo.atribuicoes(m)
    z_aval = penalidade(inst, escala)
    pena = {n: round(pyo.value(m.pena[n])) for n in inst.profissionais}
    pena_aval = por_profissional(inst, escala)

    if z != z_esperado:
        erros.append(f"{nome}: objetivo {z}, esperado {z_esperado} (Tabela 6)")
    if z_aval != z:
        erros.append(f"{nome}: modelo {z} x avaliacao.py {z_aval}")
    if sum(pena.values()) != z:
        erros.append(f"{nome}: sum(m.pena) {sum(pena.values())} x objetivo {z}")
    divergem = [n for n in inst.profissionais if pena[n] != pena_aval.get(n, 0)]
    if divergem:
        erros.append(f"{nome}: m.pena diverge de avaliacao.py em {len(divergem)} "
                     f"profissionais, p.ex. {divergem[:3]}")

    # 5) decomposicao cruzada: a grade (profissional x familia) tem de fechar nos dois
    # sentidos. Se fechar so num, alguma parcela foi contada no profissional errado.
    grade = {(n, f): round(pyo.value(m.pena_familia[n, f]))
             for n in inst.profissionais for f in m.parcela}
    for n in inst.profissionais:
        if sum(grade[n, f] for f in m.parcela) != pena[n]:
            erros.append(f"{nome}: pena_familia nao soma pena[{n}]")
            break
    for f in m.parcela:
        if sum(grade[n, f] for n in inst.profissionais) != round(pyo.value(m.parcela[f])):
            erros.append(f"{nome}: pena_familia nao soma parcela[{f}]")
            break

    if gravar_escala and not erros:
        # `resultados/` esta no .gitignore, entao a escala otima nao viaja pelo repositorio:
        # cada maquina precisa gerar a sua. Sem isso, a conferencia do piso forcado
        # (docs/conferencia_piso_forcado.py) nao tem o que ler e nao atesta nada.
        destino = RAIZ / "resultados" / f"{nome}_completo.xml"
        escrever_xml(inst, escala, destino, penalidade=z)
        print(f"        escala gravada em {destino.relative_to(RAIZ)}")

    marca = "OK " if not erros else "FALHOU"
    print(f"   {marca} {nome:10s} Z={z:4d} (esperado {z_esperado:4d}) | "
          f"sum(pena)={sum(pena.values()):4d} | max pena={max(pena.values()):3d} | "
          f"{seg:6.1f}s")
    return erros


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--todos", action="store_true", help="inclui long01 e long02")
    ap.add_argument("--solver", default=modelo.SOLVER_PADRAO)
    ap.add_argument("--tempo", type=int, default=None, help="limite por alvo, em segundos")
    ap.add_argument("--gravar-escalas", action="store_true",
                    help="grava a escala otima de cada alvo em resultados/<alvo>_completo.xml."
                         " Necessario porque resultados/ esta no .gitignore e as escalas nao"
                         " viajam pelo repositorio; e o insumo de"
                         " docs/conferencia_piso_forcado.py")
    a = ap.parse_args()

    alvos = ALVOS if a.todos else ALVOS[:2]
    print(f"regressao do modelo, solver {a.solver}, {len(alvos)} alvos")
    erros = []
    for nome, caminho, z in alvos:
        erros += conferir(nome, caminho, z, a.solver, a.tempo, a.gravar_escalas)

    print()
    if erros:
        print("REGRESSAO REPROVOU:")
        for e in erros:
            print(f"   {e}")
        return 1
    print("regressao OK: otimo provado, Tabela 6, espelho de avaliacao.py e "
          "decomposicao por profissional")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
