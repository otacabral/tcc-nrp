"""Os XML do caminho dos experimentos nao mudam? Conferencia byte a byte, antes x depois.

Uso, da raiz, com a .venv ativa:

    python docs\\conferencia_xml_experimentos.py gerar <pasta>   # escreve os XML da grade
    python docs\\conferencia_xml_experimentos.py comparar <a> <b>

Para o "antes", rodar `gerar` a partir de uma copia do commit anterior (git worktree), com
`--src <copia>\\src`. A grade cobre o caminho dos experimentos e o da ferramenta por pacientes:
5 graus x 2 regimes x 2 regras x efetivos 36-44 x variacao {0; 0,5; 1}, mais as entradas por
pacientes, razao, equipe e indisponibilidade. Feita em 02/10 para a carga por contrato
(DECISOES.md, "2026-10-02 — Carga por contrato", item f), no lugar da conferencia avulsa
dos 361 XML de 29/09, que nao ficou no repositorio.
"""

from __future__ import annotations

import argparse
import filecmp
import sys
from pathlib import Path


def gerar(src: Path, pasta: Path) -> int:
    sys.path.insert(0, str(src))
    import instancia_br as br
    pasta.mkdir(parents=True, exist_ok=True)
    n = 0

    def escreve(nome, inst):
        nonlocal n
        br.escrever_xml(inst, pasta / f"{nome}.xml")
        n += 1

    for grau in br.GRAUS:
        for regime in ("8h", "12x36"):
            for regra in ("teto", "maior_resto"):
                for efetivo in range(36, 45):
                    for variacao in (0.0, 0.5, 1.0):
                        inst = br.construir(grau=grau, regime=regime, regra=regra,
                                            efetivo=efetivo, variacao=variacao)
                        escreve(f"{grau}_{regime}_{regra}_e{efetivo}_v{variacao}", inst)
    inicio = br.primeira_segunda()
    for regime in ("8h", "12x36"):
        for razao in (None, 20 / 29):
            inst = br.construir(regime=regime, pacientes={"minimo": 10, "intermediario": 12},
                                razao_fds=razao, n_enfermeiros=12, n_tecnicos=26,
                                inicio=inicio,
                                indisponibilidades=[("Enf 1", inicio, inicio)])
            escreve(f"pacientes_{regime}_{razao}", inst)
    return n


def comparar(a: Path, b: Path) -> int:
    nomes_a = sorted(p.name for p in a.glob("*.xml"))
    nomes_b = sorted(p.name for p in b.glob("*.xml"))
    if nomes_a != nomes_b:
        print(f"conjuntos diferentes: {set(nomes_a) ^ set(nomes_b)}")
        return 1
    _, diferentes, erros = filecmp.cmpfiles(a, b, nomes_a, shallow=False)
    print(f"{len(nomes_a)} XML; diferentes: {len(diferentes)}; erros: {len(erros)}")
    for nome in (diferentes + erros)[:10]:
        print(f"   {nome}")
    return 1 if diferentes or erros else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gerar")
    g.add_argument("pasta", type=Path)
    g.add_argument("--src", type=Path, default=Path(__file__).resolve().parents[1] / "src")
    c = sub.add_parser("comparar")
    c.add_argument("a", type=Path)
    c.add_argument("b", type=Path)
    a = ap.parse_args()
    if a.cmd == "gerar":
        print(f"{gerar(a.src, a.pasta)} XML em {a.pasta}")
        return 0
    return comparar(a.a, a.b)


if __name__ == "__main__":
    raise SystemExit(main())
