"""Opcao B, teste (a1): a entrada do solver com a classificacao PADRAO e a mesma da v1.2.3.

Esperado registrado antes: `resultados/opcao_b_2026-10-19/ESPERADO.md`, item (a1). Roda nas
duas arvores (a v1.2.3 num `git worktree`, e a atual), sem solver; cada uma grava, por caso, o
XML da instancia, o LP da etapa 1 e o LP da etapa 2 numa pasta. Depois, `--comparar A B`
confere byte a byte.

    python docs\\diagnostico\\identidade_opcao_b.py --gravar <pasta>
    python docs\\diagnostico\\identidade_opcao_b.py --comparar <pasta_v123> <pasta_nova>
    python docs\\diagnostico\\identidade_opcao_b.py --controle <pasta>   # so na arvore nova

Casos: bateria nivel 1 (P01-P18) e nivel 2 (K1-K6), as tres rodadas da demonstracao, cada um com
acrescimos 0, 1 e 2 (a busca do menor quadro monta essas instancias).
"""

from __future__ import annotations

import argparse
import filecmp
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "docs"), str(AQUI),
                str(RAIZ / "docs" / "demonstracao")]

import bateria_desenho as bd  # noqa: E402
import bateria_rodar as brr  # noqa: E402
import caso_clinica_medica as cc  # noqa: E402
import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402

NOMES = [f"P{k:02d}" for k in range(1, 19)] + [f"K{k}" for k in range(1, 7)]


def entradas():
    casos = {c.nome.split()[0]: c for c in bd.CASOS + bd.CONHECIDOS}
    for nome in NOMES:
        yield nome, brr.entrada(casos[nome])
    for tec in (20, 19, 18):
        yield f"demo{tec}", cc.entrada(tec)


def modelo_etapa1(inst, prioridades=None):
    """O modelo da etapa 1 como a ferramenta o monta, na arvore em que roda."""
    if hasattr(fe, "modelo_etapa1"):           # arvore nova (opcao B)
        m, inst_p, _ = fe.modelo_etapa1(inst, prioridades)
        return m, inst_p
    inst_p, custo, _ = fe.pesos(inst)          # v1.2.3
    return ea.modelo_br(inst_p, custo), inst_p


def gravar_caso(pasta: Path, rotulo: str, inst, prioridades=None) -> None:
    br.escrever_xml(inst, pasta / f"{rotulo}.xml")
    m, inst_p = modelo_etapa1(inst, prioridades)
    m.write(str(pasta / f"{rotulo}_etapa1.lp"), io_options={"symbolic_solver_labels": True})
    fe.preparar_equilibrio(m, inst_p, 0, exato=True)
    m.write(str(pasta / f"{rotulo}_etapa2.lp"), io_options={"symbolic_solver_labels": True})


def gravar(pasta: Path) -> int:
    pasta.mkdir(parents=True, exist_ok=True)
    n = 0
    for nome, e in entradas():
        horas_enf = fe._horas_enfermeiro(e)
        for acrescimo in (0, 1, 2):
            gravar_caso(pasta, f"{nome}_a{acrescimo}", fe.montar(e, acrescimo, horas_enf))
            n += 1
        print(nome, flush=True)
    print(f"{n} casos, {3 * n} arquivos em {pasta}")
    return 0


def comparar(a: Path, b: Path) -> int:
    nomes = sorted(p.name for p in a.iterdir())
    outros = sorted(p.name for p in b.iterdir())
    if nomes != outros:
        print(f"LISTAS DIFERENTES: so em A {set(nomes) - set(outros)}; "
              f"so em B {set(outros) - set(nomes)}")
        return 1
    dif = [n for n in nomes if not filecmp.cmp(a / n, b / n, shallow=False)]
    print(f"{len(nomes)} arquivos; {len(nomes) - len(dif)} identicos; {len(dif)} diferentes")
    for n in dif:
        print("   DIFERENTE:", n)
    return 1 if dif else 0


def controle(pasta: Path) -> int:
    """Controle positivo: uma suave ligada no Desejavel muda o LP da etapa 1 do P01."""
    pasta.mkdir(parents=True, exist_ok=True)
    nome, e = next(entradas())
    padrao = fe.prioridades_padrao()
    outra = dict(padrao, min_folgas_seguidas=(fe.DESEJAVEL, 3))
    gravar_caso(pasta, f"{nome}_padrao", fe.montar(e), padrao)
    gravar_caso(pasta, f"{nome}_suave", fe.montar(e), outra)
    igual = filecmp.cmp(pasta / f"{nome}_padrao_etapa1.lp", pasta / f"{nome}_suave_etapa1.lp",
                        shallow=False)
    print(f"controle: LP da etapa 1 com uma suave {'IGUAL (falhou)' if igual else 'muda (ok)'}")
    return 1 if igual else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gravar", type=Path)
    ap.add_argument("--comparar", nargs=2, type=Path)
    ap.add_argument("--controle", type=Path)
    a = ap.parse_args()
    if a.gravar:
        return gravar(a.gravar)
    if a.controle:
        return controle(a.controle)
    return comparar(*a.comparar)


if __name__ == "__main__":
    raise SystemExit(main())
