"""Chama o avaliador oficial e compara com o objetivo do modelo.

O avaliador (`avaliador/evaluator.jar`) nao declara Main-Class no manifesto, entao roda por
classpath, indicando a classe principal (ver README.md):

    java -cp avaliador/evaluator.jar dds.nrp.core.evaluation.ScheduleEvaluator inst.xml sol.xml

Uso:

    python src\\validar.py instancias/sprint/sprint/sprint01.xml resultados/sprint01.xml
    python src\\validar.py <instancia> <solucao> --objetivo 56
    python src\\validar.py <instancia> <solucao> --procurar NoNightShift

Sem `-p`, o avaliador detalha as violacoes por restricao e por profissional. A saida
detalhada e sempre gravada ao lado da solucao, com sufixo `_avaliador.txt`: e o insumo do
trabalho das semanas 2-3, quando as 13 flexiveis entram uma por vez e e preciso saber qual
restricao divergiu.

Convencao do projeto: nenhum resultado numerico vale sem passar por aqui ou ser conferivel
contra a Tabela 6 de Santos et al. (2016).
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
AVALIADOR = RAIZ / "avaliador"
JAR = AVALIADOR / "evaluator.jar"
CLASSE = "dds.nrp.core.evaluation.ScheduleEvaluator"
TEMPO_LIMITE = 300  # segundos
# Heap da JVM do avaliador (DECISOES.md, "2026-10-21 — Correcao de defeito: avaliador sem
# memoria lido como sem violacao"): com o padrao (~3 GB nesta maquina) o avaliador estoura na
# instancia de 89 profissionais do caso B.
MEMORIA_JAVA = "-Xmx6g"


class AvaliadorIndisponivel(RuntimeError):
    """Java ausente, jar ausente, ou o avaliador nao rodou."""


def diagnostico() -> list[str]:
    """Confere o que o avaliador precisa. Lista vazia = pronto para rodar."""
    problemas = []
    if shutil.which("java") is None:
        problemas.append("java nao encontrado no PATH (o avaliador precisa de JDK 21+)")
    if not JAR.exists():
        problemas.append(f"avaliador ausente: {JAR.relative_to(RAIZ)} (ver README.md, Download)")
    return problemas


def _executar(argumentos: list[str]) -> str:
    problemas = diagnostico()
    if problemas:
        raise AvaliadorIndisponivel("; ".join(problemas))
    # CORRIGIDO EM 06/10 (DECISOES.md, "Correcao de defeito: src/validar.py"): o classpath
    # tinha so o evaluator.jar, sem dom4j/jaxen/jaxb-api; o curinga, como no README, leva todos.
    comando = ["java", MEMORIA_JAVA, "-cp", str(AVALIADOR / "*"), CLASSE, *argumentos]
    try:
        processo = subprocess.run(comando, capture_output=True, text=True,
                                  timeout=TEMPO_LIMITE, check=False)
    except subprocess.TimeoutExpired as erro:
        raise AvaliadorIndisponivel(f"avaliador excedeu {TEMPO_LIMITE}s") from erro
    saida = (processo.stdout or "") + (processo.stderr or "")
    # CORRIGIDO EM 21/10: o avaliador que parou (sem memoria, por exemplo) devolvia um stack
    # trace, e `_numero` lia como penalidade um numero de linha dele. Saida de quem parou nao e
    # conferencia: falha alto.
    if processo.returncode != 0 or "Exception in thread" in saida:
        primeira = next((l for l in saida.splitlines() if l.strip()), "")
        raise AvaliadorIndisponivel(f"avaliador terminou com codigo {processo.returncode}: "
                                    f"{primeira[:200]}")
    return saida


def _numero(saida: str) -> int | None:
    """Extrai a penalidade da saida do avaliador.

    Com `-p` a saida e so o numero. Sem `-p`, procura uma linha que fale em penalidade ou
    total; em ultimo caso, o ultimo inteiro da saida. Se nada servir, devolve None — e a
    saida crua fica disponivel para leitura humana, em vez de um palpite silencioso.
    """
    texto = saida.strip()
    if re.fullmatch(r"-?\d+", texto):
        return int(texto)
    for linha in reversed(texto.splitlines()):
        if re.search(r"penalt|total|cost|objective", linha, re.IGNORECASE):
            numeros = re.findall(r"-?\d+", linha)
            if numeros:
                return int(numeros[-1])
    numeros = re.findall(r"-?\d+", texto)
    return int(numeros[-1]) if numeros else None


def avaliar(instancia: Path | str, solucao: Path | str) -> tuple[int | None, str, str]:
    """Roda o avaliador nas duas formas.

    Devolve (penalidade, saida_resumida, saida_detalhada). A detalhada e gravada ao lado da
    solucao com sufixo `_avaliador.txt`.
    """
    instancia, solucao = Path(instancia), Path(solucao)
    # CORRIGIDO EM 06/10: `-p` tem de vir ANTES dos arquivos (README); depois deles o avaliador
    # responde "Syntax error". E caminhos com barra normal: com contrabarra o avaliador recusa
    # caminho absoluto ("Invalid file path").
    arquivos = [instancia.as_posix(), solucao.as_posix()]
    resumida = _executar(["-p", *arquivos])
    detalhada = _executar(arquivos)
    registro = solucao.with_name(solucao.stem + "_avaliador.txt")
    registro.write_text(detalhada, encoding="utf-8")
    return _numero(resumida), resumida.strip(), detalhada


def conferir(instancia: Path | str, solucao: Path | str,
             objetivo_interno: int | None = None, procurar: str | None = None) -> int:
    """Roda o avaliador e compara com o objetivo do modelo. Devolve o codigo de saida."""
    try:
        penalidade, resumida, detalhada = avaliar(instancia, solucao)
    except AvaliadorIndisponivel as erro:
        print(f"[FALHA] {erro}")
        return 2

    print(f"instancia : {Path(instancia).name}")
    print(f"solucao   : {Path(solucao).name}")
    print(f"avaliador : {penalidade if penalidade is not None else '(nao interpretado)'}")
    if penalidade is None:
        print("  saida crua do avaliador, para leitura:")
        print("  " + resumida.replace("\n", "\n  "))

    if objetivo_interno is not None:
        bate = penalidade == objetivo_interno
        print(f"modelo    : {objetivo_interno}")
        print(f"[{'OK   ' if bate else 'FALHA'}] "
              + ("os dois valores batem" if bate
                 else f"divergencia de {abs((penalidade or 0) - objetivo_interno)}"))
        if not bate:
            print("  a saida detalhada esta no arquivo _avaliador.txt, com as violacoes por "
                  "restricao e por profissional")
            return 1

    if procurar:
        linhas = [l for l in detalhada.splitlines() if procurar.lower() in l.lower()]
        print(f"\nocorrencias de '{procurar}' na saida detalhada: {len(linhas)}")
        for linha in linhas[:20]:
            print("  " + linha.strip())
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Roda o avaliador oficial do INRC-2010.")
    ap.add_argument("instancia", help="XML da instancia")
    ap.add_argument("solucao", help="XML da solucao")
    ap.add_argument("--objetivo", type=int, default=None,
                    help="valor calculado pelo modelo, para comparar")
    ap.add_argument("--procurar", default=None,
                    help="termo a procurar na saida detalhada, ex.: NoNightShift")
    args = ap.parse_args()
    return conferir(args.instancia, args.solucao, args.objetivo, args.procurar)


if __name__ == "__main__":
    sys.exit(main())
