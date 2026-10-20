"""3o bloco (20/10), teste 1 de cada parte que toca src/: a entrada do solver com a
classificacao PADRAO e a mesma da v1.3.0.

Esperado registrado antes: `resultados/pedidos_2026-10-20/ESPERADO.md`, item 1. Reusa os 81
casos de `identidade_opcao_b.py` (bateria P01-P18 e K1-K6, demonstracao; acrescimos 0, 1, 2).

    python docs\diagnostico\identidade_3bloco.py --gravar <pasta>            # 1a (as duas arvores)
    python docs\diagnostico\identidade_3bloco.py --gravar <pasta> --regras   # 1b (so a nova)
    python docs\diagnostico\identidade_3bloco.py --controle <pasta>          # so a nova
    python docs\diagnostico\identidade_opcao_b.py --comparar <v130> <nova>

`--regras`: os pedidos de folga de cada caso vao como linhas "Folga + dia, Essencial" da tabela
"Pedidos e regras dos profissionais" (`Entrada.regras`), em vez do caminho antigo.
"""

from __future__ import annotations

import argparse
import dataclasses
import filecmp
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import identidade_opcao_b as io_b  # noqa: E402  (ajusta o sys.path)

fe = io_b.fe


def como_regras(e):
    import prioridades as pr
    linhas = [pr.Linha(quem, d, None, pr.FOLGA, pr.ESSENCIAL) for quem, d in e.pedidos]
    return dataclasses.replace(e, pedidos=[], regras=linhas)


def gravar(pasta: Path, regras: bool) -> int:
    pasta.mkdir(parents=True, exist_ok=True)
    n = com_pedidos = 0
    for nome, e in io_b.entradas():
        com_pedidos += bool(e.pedidos)
        if regras:
            e = como_regras(e)
        horas_enf = fe._horas_enfermeiro(e)
        for acrescimo in (0, 1, 2):
            io_b.gravar_caso(pasta, f"{nome}_a{acrescimo}", fe.montar(e, acrescimo, horas_enf))
            n += 1
    print(f"{n} casos ({com_pedidos} entradas com pedidos), {3 * n} arquivos em {pasta}")
    return 0


def controle(pasta: Path) -> int:
    """Controle positivo: uma linha "Folga + turno" a mais muda o LP da etapa 1."""
    import prioridades as pr
    pasta.mkdir(parents=True, exist_ok=True)
    nome, e = next(io_b.entradas())
    inst = fe.montar(e)
    quem = next(iter(inst.profissionais.values())).nome
    turno = e.turnos[0][0]
    outra = dataclasses.replace(e, regras=[pr.Linha(quem, None, turno, pr.FOLGA)])
    io_b.gravar_caso(pasta, f"{nome}_padrao", fe.montar(e))
    io_b.gravar_caso(pasta, f"{nome}_linha", fe.montar(outra))
    igual = filecmp.cmp(pasta / f"{nome}_padrao_etapa1.lp", pasta / f"{nome}_linha_etapa1.lp",
                        shallow=False)
    print(f"controle: LP da etapa 1 com uma linha a mais {'IGUAL (falhou)' if igual else 'muda (ok)'}")
    return 1 if igual else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gravar", type=Path)
    ap.add_argument("--regras", action="store_true")
    ap.add_argument("--controle", type=Path)
    a = ap.parse_args()
    if a.controle:
        return controle(a.controle)
    return gravar(a.gravar, a.regras)


if __name__ == "__main__":
    raise SystemExit(main())
