"""Gravacao de CSV de resultado por MESCLAGEM. Sem Pyomo, sem XML — so a biblioteca padrao.

Existe por causa de dois acidentes, os dois em 22/09, os dois no `experimento_b`:

1. rodar `--alvo long01` **apagou as linhas** das duas sprints, porque a gravacao era por
   cima. Consertado preenchendo o que faltasse e nunca descartando linha;
2. a rodada `--por-pessoa` trocou a coluna `segundos` por `segundos_parede` e `segundos_cpu`,
   e **apagou a coluna `observacao`** — onde estava o registro de que a maquina tinha ficado
   suspensa no meio do `long02`. O conserto anterior protegia linhas, nao colunas.

Perder coluna e mais silencioso que perder linha: o arquivo continua parecendo certo. Dai
este modulo ser separado e **testavel sem o solver** — `python src\\tabela.py` roda os casos
dos dois acidentes. O `experimentos.py` e o `experimento_a.py` importam daqui.

A regra, em uma frase: **o arquivo so cresce.** Linha com chave repetida e substituida; linha
com chave nova entra; coluna que existia continua existindo, mesmo que a rodada de hoje nao
saiba mais o que por nela.
"""

from __future__ import annotations

import csv
from pathlib import Path


def mesclar_csv(caminho: Path | str, novos: list[dict], chave: tuple[str, ...],
                remover=None) -> None:
    """Grava `novos` em `caminho`, preservando linhas e colunas que ja estavam la.

    `chave` sao as colunas que identificam uma linha. Ordem das colunas no arquivo final:
    as da rodada nova primeiro, na ordem em que vieram, e depois as que so existiam antes.
    Ordem das linhas: as antigas na ordem original, e as novas no fim — de modo que reescrever
    uma linha existente nao a move de lugar.

    `remover` e um teste sobre a tupla de chave, para o caso em que a rodada nova **substitui
    um bloco inteiro** em vez de linha a linha. E o que a composicao por familia precisa: ela
    descreve UMA escala, entao misturar as linhas de hoje com as de ontem daria uma escala que
    nunca existiu. Usar so quando for isso — o padrao, e o caso normal, e nao apagar nada.
    """
    caminho = Path(caminho)
    if not novos:
        return
    caminho.parent.mkdir(parents=True, exist_ok=True)

    colunas = list(novos[0])
    antigas: list[dict] = []
    if caminho.exists():
        with caminho.open(newline="", encoding="utf-8-sig") as f:
            leitor = csv.DictReader(f, delimiter=";")
            antigas = [l for l in leitor if all(l.get(c) is not None for c in chave)]
            for c in leitor.fieldnames or []:
                if c not in colunas:
                    colunas.append(c)

    acumulado: dict[tuple, dict] = {}
    for linha in antigas:
        acumulado[tuple(linha[c] for c in chave)] = {c: (linha.get(c) or "") for c in colunas}
    if remover is not None:
        for k in [k for k in acumulado if remover(k)]:
            del acumulado[k]
    for linha in novos:
        # a linha nova pode nao ter as colunas que so existiam no arquivo: completa com vazio
        acumulado[tuple(str(linha[c]) for c in chave)] = {c: linha.get(c, "") for c in colunas}

    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=colunas, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(acumulado.values())


# --- conferencia ----------------------------------------------------------------------

def _ler(caminho: Path) -> tuple[list[str], list[dict]]:
    with caminho.open(newline="", encoding="utf-8-sig") as f:
        leitor = csv.DictReader(f, delimiter=";")
        return list(leitor.fieldnames or []), list(leitor)


def main() -> int:
    """Reproduz os dois acidentes e exige que nao aconteçam mais."""
    import tempfile

    erros = []
    base = Path(tempfile.mkdtemp())

    # acidente 1: rodada com UMA instancia nao pode apagar as outras
    a = base / "a.csv"
    mesclar_csv(a, [{"instancia": "sprint01", "Z": 56}, {"instancia": "sprint02", "Z": 58}],
                ("instancia",))
    mesclar_csv(a, [{"instancia": "long01", "Z": 197}], ("instancia",))
    _, linhas = _ler(a)
    if {l["instancia"] for l in linhas} != {"sprint01", "sprint02", "long01"}:
        erros.append(f"acidente 1: linhas perdidas -> {[l['instancia'] for l in linhas]}")

    # acidente 2: rodada que TROCA o esquema nao pode apagar coluna antiga
    b = base / "b.csv"
    mesclar_csv(b, [{"instancia": "long02", "Z": 219, "segundos": 11565.3,
                     "observacao": "maquina suspensa"}], ("instancia",))
    mesclar_csv(b, [{"instancia": "sprint01", "Z": 56, "segundos_cpu": 203.7}], ("instancia",))
    colunas, linhas = _ler(b)
    if "observacao" not in colunas or "segundos" not in colunas:
        erros.append(f"acidente 2: coluna perdida -> {colunas}")
    velha = next((l for l in linhas if l["instancia"] == "long02"), {})
    if velha.get("observacao") != "maquina suspensa":
        erros.append(f"acidente 2: conteudo perdido -> {velha}")
    nova = next((l for l in linhas if l["instancia"] == "sprint01"), {})
    if nova.get("observacao") != "" or nova.get("segundos_cpu") != "203.7":
        erros.append(f"acidente 2: linha nova mal preenchida -> {nova}")

    # sobrescrever a mesma chave atualiza, nao duplica
    mesclar_csv(b, [{"instancia": "long02", "Z": 219, "segundos": 1.0,
                     "observacao": "corrigido"}], ("instancia",))
    _, linhas = _ler(b)
    if len([l for l in linhas if l["instancia"] == "long02"]) != 1:
        erros.append("chave repetida duplicou a linha")
    if next(l for l in linhas if l["instancia"] == "long02")["observacao"] != "corrigido":
        erros.append("chave repetida nao atualizou a linha")

    # chave composta, que e o caso do perfil por profissional
    c = base / "c.csv"
    mesclar_csv(c, [{"instancia": "x", "profissional": "0", "v": 1},
                    {"instancia": "x", "profissional": "1", "v": 2}],
                ("instancia", "profissional"))
    mesclar_csv(c, [{"instancia": "x", "profissional": "0", "v": 9}],
                ("instancia", "profissional"))
    _, linhas = _ler(c)
    if [l["v"] for l in linhas] != ["9", "2"]:
        erros.append(f"chave composta: {[(l['profissional'], l['v']) for l in linhas]}")

    for e in erros:
        print("FALHOU:", e)
    print("tabela.py:", "OK" if not erros else f"{len(erros)} falha(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
