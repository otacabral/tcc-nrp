"""Caminhos citados no NUMEROS_TCC.md que nao estao no git (10/10). So leitura.

    python docs\\diagnostico\\citados_fora_do_git.py            # lista e tamanho total
    python docs\\diagnostico\\citados_fora_do_git.py --lista     # so os caminhos (para o git add)

Regra, mecanica: o texto inteiro do `resultados/NUMEROS_TCC.md` e quebrado em palavras (por
espaco, crase, aspas, parenteses, virgula, ponto e virgula, barra vertical e asterisco; o pareamento
de crases nao serve, porque ha crase solta no arquivo); fica a palavra que existe como arquivo ou pasta a partir da raiz, ou, se for so um nome, a que
existe com esse nome numa unica pasta de `resultados/`, `docs/` ou `src/` (nome em mais de uma
pasta = ambiguo, listado a parte). Pasta citada = todos os arquivos dela. Fora: `instancias/` e
`avaliador/` (dado publico, baixado da fonte, ver README). Somam-se, por pedido do Otavio (10/10),
os `resultados/*_completo_avaliador.txt` e os `p17_*.json`, e os tres logs do HiGHS que sustentam a
condicao de otimo do cabecalho do NUMEROS (o "limite inferior registrado no log"; os nomes estao
no relatorio 09c, citado ali).
Sai so o que `git ls-files` nao tem.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
NUMEROS = RAIZ / "resultados" / "NUMEROS_TCC.md"
FORA = ("instancias/", "avaliador/")
EXTRAS = (["resultados/escalabilidade_objetivo/highs_N40_etapa1.log",
           "resultados/escalabilidade_objetivo/highs_N60_etapa1.log",
           "resultados/escalabilidade_objetivo/highs_N80_etapa1.log"]
          + sorted(p.relative_to(RAIZ).as_posix() for p in RAIZ.glob("resultados/*_completo_avaliador.txt"))
          + sorted(p.relative_to(RAIZ).as_posix() for p in RAIZ.glob("resultados/**/p17_*.json")))


def versionados() -> set[str]:
    saida = subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8").stdout
    return set(saida.splitlines())


def por_nome() -> dict[str, list[str]]:
    nomes: dict[str, list[str]] = {}
    for base in ("resultados", "docs", "src"):
        for p in (RAIZ / base).rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                nomes.setdefault(p.name, []).append(p.relative_to(RAIZ).as_posix())
    return nomes


def citados() -> tuple[set[str], list[tuple[str, list[str]]], set[str]]:
    texto = NUMEROS.read_text(encoding="utf-8")
    nomes = por_nome()
    achados, ambiguos, sumidos = set(), [], set()
    for palavra in re.split(r"[\s`\"'(),;|*]+", texto):
        p = palavra.replace("\\", "/").rstrip(".:")
        if not p or p.startswith(FORA) or p.startswith(("-", "/", ".")) or ":" in p:
            continue
        alvo = RAIZ / p
        if alvo.is_file():
            achados.add(alvo.relative_to(RAIZ).as_posix())
        elif alvo.is_dir() and "/" in p:
            achados.update(q.relative_to(RAIZ).as_posix() for q in alvo.rglob("*")
                           if q.is_file() and "__pycache__" not in q.parts)
        elif "/" not in p and p in nomes:
            if len(nomes[p]) == 1:
                achados.add(nomes[p][0])
            else:
                ambiguos.append((p, nomes[p]))
        elif re.match(r"(resultados|docs|src)/.+\.\w+$", p):
            sumidos.add(p)          # tem cara de caminho e nao existe
    return achados, ambiguos, sumidos


def main() -> int:
    achados, ambiguos, sumidos = citados()
    git = versionados()
    faltam = sorted(c for c in achados | set(EXTRAS) if c not in git and (RAIZ / c).is_file())
    inexistentes = sorted(c for c in EXTRAS if not (RAIZ / c).is_file())
    if "--lista" in sys.argv:
        print("\n".join(faltam))
        return 0
    total = 0
    for c in faltam:
        tam = (RAIZ / c).stat().st_size
        total += tam
        print(f"{tam / 1024:9.1f} KB  {c}{'   (extra)' if c in EXTRAS else ''}")
    print(f"{len(faltam)} arquivos fora do git; total {total / 1024:.1f} KB "
          f"({len(achados)} caminhos citados no NUMEROS, {len(EXTRAS)} extras)")
    for nome, onde in ambiguos:
        print(f"AMBIGUO (nome em mais de uma pasta): {nome} -> {onde}")
    for c in sorted(sumidos):
        print(f"CITADO E INEXISTENTE: {c}")
    for c in inexistentes:
        print(f"EXTRA INEXISTENTE: {c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
