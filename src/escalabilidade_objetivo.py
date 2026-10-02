"""Curva de escalabilidade COM OBJETIVO NAO TRIVIAL — P1 do `PROPOSTAS.md` (Etapa 4).

Roda da raiz do repositorio, com a .venv ativa:

    python src\\escalabilidade_objetivo.py                  # 36, 40, 60, 80, 120, 200
    python src\\escalabilidade_objetivo.py --n 40           # so esse
    python src\\escalabilidade_objetivo.py --tempo 900      # limite POR ETAPA, em segundos

Saida: `resultados/escalabilidade_objetivo.csv`, gravado a cada tamanho concluido, e o log
do HiGHS de cada etapa em `resultados/escalabilidade_objetivo/highs_N<n>_etapa<k>.log`.

## O que muda em relacao a `escalabilidade.py`

So o objetivo. As instancias sao AS MESMAS (`escalabilidade.construir`: 12x36, grau
intermediario, porte escolhido para o piso cair em N), e o modelo tambem (`ea.modelo_br`, as
mesmas opcoes da ferramenta). Muda:

- **pedidos de folga sinteticos**: 2 por profissional, em datas distintas sorteadas com
  `random.Random(SEMENTE + N)` — a semente esta registrada abaixo, e cada tamanho tem a sua
  sequencia, reproduzivel sozinho com `--n`;
- **o objetivo completo da ferramenta** (DECISOES.md, "Redesenho"): etapa 1 com pesos
  inteiros (`ferramenta.pesos`: enfermeiro em posto de tecnico custa 1, pedido negado custa
  W); etapa 2 com a penalidade presa no otimo, minimizando a amplitude de carga em horas
  (`ferramenta.preparar_equilibrio`, 02/10). Como na ferramenta, a etapa 2 so roda se a
  etapa 1 provou otimalidade.

Com isso o limite inferior deixa de ser zero por construcao, e a prova de otimalidade passa
a custar alguma coisa — e isso que a P1 queria medir.

Por etapa registra-se: estado do solver, se provou otimalidade, gap ao fim, tempo de relogio
e **tempo ate a primeira escala legal** — lido do log do HiGHS (primeira linha da arvore com
solucao finita, na coluna de tempo do proprio HiGHS). Toda solucao do modelo e legal: a CLT
esta nas restricoes rigidas.

Tempo de resolucao e LIMITE OPERACIONAL, nao resultado (CLAUDE.md): registra-se com a
maquina e o solver nomeados. O que interessa e se a prova fecha.
"""

from __future__ import annotations

import argparse
import dataclasses
import math
import platform
import random
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import escalabilidade as esc  # noqa: E402
import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import modelo  # noqa: E402
import solucao  # noqa: E402
from instancia import Pedido  # noqa: E402
from tabela import mesclar_csv  # noqa: E402

SAIDA = RAIZ / "resultados" / "escalabilidade_objetivo.csv"
ESCALAS = RAIZ / "resultados" / "escalabilidade_objetivo"

SEMENTE = 20261002         # data da rodada; cada tamanho usa SEMENTE + N
PEDIDOS_POR_PESSOA = 2

# linha da arvore do HiGHS: "Src Proc. InQueue | Leaves Expl. | BestBound BestSol Gap | ...
# Time". O BestSol e o 7o campo depois da letra de origem (opcional); o tempo, o ultimo.
_LINHA_ARVORE = re.compile(
    r"^\s*[A-Za-z]?\s+\d+\s+\d+\s+\d+\s+[\d.]+%\s+(\S+)\s+(\S+)\s+.*?([\d.]+)s\s*$")


def com_pedidos(inst, n: int):
    """2 pedidos de folga por profissional, em datas distintas sorteadas. Peso 1 aqui;
    `ferramenta.pesos` troca pelo W, como faz na tela."""
    rng = random.Random(SEMENTE + n)
    pedidos = []
    for p in sorted(inst.profissionais, key=modelo._chave):
        for d in sorted(rng.sample(list(inst.dias), PEDIDOS_POR_PESSOA)):
            pedidos.append(Pedido(tipo="folga_dia", profissional=p, data=d, peso=1))
    return dataclasses.replace(inst, pedidos=tuple(pedidos))


def primeira_solucao_s(log: str) -> float | None:
    """Tempo do HiGHS na primeira linha da arvore com melhor solucao finita."""
    for linha in log.splitlines():
        achou = _LINHA_ARVORE.match(linha)
        if achou:
            try:
                melhor = float(achou.group(2))
            except ValueError:
                continue
            if math.isfinite(melhor):
                return float(achou.group(3))
    return None


def _resolver(m, solver: str, tempo: int, log: Path) -> dict:
    """Resolve com o log do HiGHS em `log` e devolve o que a P1 registra. Nunca levanta."""
    log.parent.mkdir(parents=True, exist_ok=True)
    log.unlink(missing_ok=True)
    t0 = time.time()
    try:
        resultado = modelo.resolver(m, solver=solver, tempo_limite=tempo, carregar=False,
                                    log_arquivo=str(log))
    except Exception as e:  # noqa: BLE001
        return {"estado": f"erro: {type(e).__name__}: {e}", "resultado": None,
                "relogio_s": round(time.time() - t0, 1), "otimo": False, "gap": "",
                "primeira_s": None}
    return {"estado": modelo.estado(resultado), "resultado": resultado,
            "relogio_s": round(time.time() - t0, 1),
            "otimo": modelo.provou_otimo(resultado),
            "gap": esc.folga_relativa(resultado),
            "primeira_s": primeira_solucao_s(log.read_text(encoding="utf-8", errors="replace")
                                             if log.exists() else "")}


def _registrar(linha: dict, etapa: str, r: dict) -> None:
    linha.update({f"{etapa}_estado": r["estado"], f"{etapa}_otimo": r["otimo"],
                  f"{etapa}_gap": r["gap"], f"{etapa}_relogio_s": r["relogio_s"],
                  f"{etapa}_primeira_escala_s": r["primeira_s"]})
    print(f"   ### {etapa}: {r['estado']} | provou otimo: {'sim' if r['otimo'] else 'NAO'} | "
          f"gap {r['gap'] or '-'} | relogio {r['relogio_s']} s | primeira escala legal "
          f"{r['primeira_s'] if r['primeira_s'] is not None else '-'} s (HiGHS)", flush=True)


def rodar(n: int, solver: str, tempo: int) -> dict:
    inst = esc.construir(n)
    p = esc.piso(inst)
    if p != n:
        raise RuntimeError(f"N={n}: piso deu {p}, esperado {n} — a escala de demanda quebrou")
    inst, custo, W = fe.pesos(com_pedidos(inst, n))
    m = ea.modelo_br(inst, custo)
    d = modelo.dimensao(m)
    print(f"\n### N = {n:3d}: {len(inst.pedidos)} pedidos, W = {W}, {d['variaveis']} "
          f"variaveis, {d['restricoes']} restricoes", flush=True)

    linha = {"N": n, "pedidos": len(inst.pedidos), "peso_pedido": W, "semente": SEMENTE + n,
             "variaveis": d["variaveis"], "restricoes": d["restricoes"], "limite_s": tempo,
             "solver": solver}

    # etapa 1: pesos inteiros
    r1 = _resolver(m, solver, tempo, ESCALAS / f"highs_N{n}_etapa1.log")
    _registrar(linha, "etapa1", r1)
    if r1["resultado"] is None or not modelo.tem_solucao(r1["resultado"]) \
            or not modelo.carregar_solucao(m, r1["resultado"]):
        linha["etapa2_estado"] = "nao rodou (etapa 1 sem escala)"
        print("   ### sem escala na etapa 1", flush=True)
        return linha
    escala = modelo.atribuicoes(m)
    z = modelo.valor_objetivo(m)
    linha.update(penalidade=z, amplitude_etapa1=fe.amplitude(inst, escala))

    # etapa 2: equilibrio de horas, so com a etapa 1 provada otima (como na ferramenta)
    if not r1["otimo"]:
        linha["etapa2_estado"] = "nao rodou (etapa 1 sem prova)"
    else:
        fe.preparar_equilibrio(m, inst, z)
        r2 = _resolver(m, solver, tempo, ESCALAS / f"highs_N{n}_etapa2.log")
        _registrar(linha, "etapa2", r2)
        if r2["resultado"] is not None and modelo.tem_solucao(r2["resultado"]) \
                and modelo.carregar_solucao(m, r2["resultado"]):
            escala = modelo.atribuicoes(m)
            linha["amplitude_etapa2"] = fe.amplitude(inst, escala)

    # conferencias da escala final: rigidas e descanso medido no relogio
    ind = fe.indicadores(inst, escala)
    med = fe.medir(inst, escala)
    problemas = solucao.conferir_rigidas(inst, escala, habilidade_rigida=True)
    descanso_ok = fe.cumpre(inst, med)
    linha.update(pedidos_atendidos=ind["pedidos_atendidos"],
                 enf_em_posto_tec=ind["enf_em_posto_tec"], negados_max=ind["negados_max"],
                 horas_min=ind["horas_min"], horas_max=ind["horas_max"],
                 descanso_ok=descanso_ok, menor_folga_h=med["menor_folga"],
                 menor_semanal_h=med["menor_semanal"], max_consec=med["max_consec"],
                 rigidas="; ".join(problemas) or "ok")
    # a penalidade tem de bater com o que a escala mostra: pedidos negados x W + enf em tec
    recontada = (ind["pedidos_total"] - ind["pedidos_atendidos"]) * W + ind["enf_em_posto_tec"]
    linha["penalidade_recontada"] = recontada
    ESCALAS.mkdir(parents=True, exist_ok=True)
    solucao.escrever_xml(inst, escala, ESCALAS / f"{inst.id}_objetivo.xml", penalidade=z)
    print(f"   ### penalidade {z} (recontada {recontada}) | pedidos "
          f"{ind['pedidos_atendidos']}/{ind['pedidos_total']} | enf em posto tec "
          f"{ind['enf_em_posto_tec']} | amplitude da fracao {linha['amplitude_etapa1']:.1%}"
          f" -> {linha.get('amplitude_etapa2', '-')} | carga {ind['horas_min']:g}-"
          f"{ind['horas_max']:g} h | descanso {'ok' if descanso_ok else 'FALHA'} (folga minima "
          f"{med['menor_folga']:g} h acima do exigido, semanal {med['menor_semanal']:g} h) | "
          f"rigidas {linha['rigidas']}", flush=True)
    return linha


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", action="append", type=int, help="tamanho; pode repetir")
    ap.add_argument("--solver", default=modelo.SOLVER_PADRAO)
    ap.add_argument("--tempo", type=int, default=900, help="limite POR ETAPA (padrao 900 s)")
    a = ap.parse_args()

    print(f"### Curva com objetivo nao trivial (P1). Solver {a.solver}, limite {a.tempo} s por "
          f"etapa, semente {SEMENTE} (+N).")
    print(f"### Maquina: {platform.processor()} | {platform.platform()} | "
          f"Python {platform.python_version()}", flush=True)
    linhas = []
    for n in a.n or esc.TAMANHOS:
        try:
            linhas.append(rodar(n, a.solver, a.tempo))
        except RuntimeError as e:
            print(f"   FALHOU {e}")
            return 1
        mesclar_csv(SAIDA, linhas, ("N",))

    print("\n### resumo")
    for r in linhas:
        print(f"### N={r['N']:3d} | etapa 1 {r.get('etapa1_estado')} gap "
              f"{r.get('etapa1_gap') or '-'} {r.get('etapa1_relogio_s')} s (1a escala "
              f"{r.get('etapa1_primeira_escala_s')} s) | etapa 2 {r.get('etapa2_estado')} gap "
              f"{r.get('etapa2_gap') or '-'} {r.get('etapa2_relogio_s', '-')} s | penalidade "
              f"{r.get('penalidade', '-')} | descanso "
              f"{'ok' if r.get('descanso_ok') else 'FALHA/sem escala'}")
    print(f"\nresultado: {SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
