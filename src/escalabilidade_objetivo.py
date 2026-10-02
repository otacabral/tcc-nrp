"""Curva de escalabilidade COM OBJETIVO NAO TRIVIAL — P1 do `PROPOSTAS.md` (Etapa 4).

Roda da raiz do repositorio, com a .venv ativa:

    python src\\escalabilidade_objetivo.py                  # 36, 40, 60, 80, 120, 200
    python src\\escalabilidade_objetivo.py --n 40           # so esse
    python src\\escalabilidade_objetivo.py --tempo 900      # limite POR ETAPA, em segundos

Saida: `resultados/escalabilidade_objetivo.csv`, gravado a cada tamanho concluido.

## O que muda em relacao a `escalabilidade.py`

So o objetivo. As instancias sao AS MESMAS (`escalabilidade.construir`: 12x36, grau
intermediario, porte escolhido para o piso cair em N), e o modelo tambem (`ea.modelo_br`, as
mesmas opcoes da ferramenta). Muda:

- **pedidos de folga sinteticos**: 2 por profissional, em datas distintas sorteadas com
  `random.Random(SEMENTE + N)` — a semente esta registrada abaixo, e cada tamanho tem a sua
  sequencia, reproduzivel sozinho com `--n`;
- **o objetivo completo da ferramenta** (DECISOES.md, "Redesenho"): etapa 1 com pesos
  inteiros (`ferramenta.pesos`: enfermeiro em posto de tecnico custa 1, pedido negado custa
  W); etapa 2 com a penalidade presa no otimo, minimizando a penalidade individual maxima
  (`ferramenta.preparar_equilibrio`). Como na ferramenta, a etapa 2 so roda se a etapa 1
  provou otimalidade e a penalidade e maior que zero.

Com isso o limite inferior deixa de ser zero por construcao, e a prova de otimalidade passa
a custar alguma coisa — e isso que a P1 queria medir.

Tempo de resolucao e LIMITE OPERACIONAL, nao resultado (CLAUDE.md): registra-se com a
maquina e o solver nomeados. O que interessa e se a prova fecha.
"""

from __future__ import annotations

import argparse
import dataclasses
import platform
import random
import sys
import time
from pathlib import Path

import pyomo.environ as pyo

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


def com_pedidos(inst, n: int):
    """2 pedidos de folga por profissional, em datas distintas sorteadas. Peso 1 aqui;
    `ferramenta.pesos` troca pelo W, como faz na tela."""
    rng = random.Random(SEMENTE + n)
    pedidos = []
    for p in sorted(inst.profissionais, key=modelo._chave):
        for d in sorted(rng.sample(list(inst.dias), PEDIDOS_POR_PESSOA)):
            pedidos.append(Pedido(tipo="folga_dia", profissional=p, data=d, peso=1))
    return dataclasses.replace(inst, pedidos=tuple(pedidos))


def _resolver(m, solver: str, tempo: int):
    """Resolve e devolve (estado, resultado, parede, cpu). Nunca levanta."""
    t0, c0 = time.time(), time.process_time()
    try:
        resultado = modelo.resolver(m, solver=solver, tempo_limite=tempo, carregar=False)
    except Exception as e:  # noqa: BLE001
        return f"erro: {type(e).__name__}: {e}", None, time.time() - t0, time.process_time() - c0
    return (modelo.estado(resultado), resultado, time.time() - t0,
            time.process_time() - c0)


def _provou(estado: str) -> bool:
    return "optimal" in estado.lower()


def rodar(n: int, solver: str, tempo: int) -> dict:
    inst = esc.construir(n)
    p = esc.piso(inst)
    if p != n:
        raise RuntimeError(f"N={n}: piso deu {p}, esperado {n} — a escala de demanda quebrou")
    inst, custo, W = fe.pesos(com_pedidos(inst, n))
    m = ea.modelo_br(inst, custo)
    d = modelo.dimensao(m)
    print(f"\nN = {n:3d}: {len(inst.pedidos)} pedidos, W = {W}, {d['variaveis']} variaveis, "
          f"{d['restricoes']} restricoes", flush=True)

    linha = {"N": n, "pedidos": len(inst.pedidos), "peso_pedido": W, "semente": SEMENTE + n,
             "variaveis": d["variaveis"], "restricoes": d["restricoes"], "limite_s": tempo,
             "solver": solver}

    # etapa 1: pesos inteiros
    e1, r1, parede1, cpu1 = _resolver(m, solver, tempo)
    linha.update(etapa1_estado=e1, etapa1_otimo=_provou(e1), etapa1_parede_s=round(parede1, 1),
                 etapa1_cpu_s=round(cpu1, 1), etapa1_gap=esc.folga_relativa(r1) if r1 else "")
    print(f"         etapa 1: {e1}, gap {linha['etapa1_gap'] or '-'}, "
          f"{parede1:.0f} s de parede, {cpu1:.0f} s de CPU", flush=True)
    if r1 is None or not ("optimal" in e1.lower() or "feasible" in e1.lower()) \
            or not modelo.carregar_solucao(m, r1):
        linha["etapa2_estado"] = "nao rodou (etapa 1 sem solucao)"
        return linha
    escala = modelo.atribuicoes(m)
    z = modelo.valor_objetivo(m)
    linha.update(penalidade=z, pena_max_etapa1=max(round(pyo.value(m.pena[k])) for k in m.pena))

    # etapa 2: equilibrio, so com a etapa 1 provada otima e penalidade > 0 (como na ferramenta)
    if not _provou(e1):
        linha["etapa2_estado"] = "nao rodou (etapa 1 sem prova)"
    elif z == 0:
        linha["etapa2_estado"] = "nao rodou (penalidade zero)"
    else:
        fe.preparar_equilibrio(m, z)
        e2, r2, parede2, cpu2 = _resolver(m, solver, tempo)
        linha.update(etapa2_estado=e2, etapa2_otimo=_provou(e2),
                     etapa2_parede_s=round(parede2, 1), etapa2_cpu_s=round(cpu2, 1),
                     etapa2_gap=esc.folga_relativa(r2) if r2 else "")
        print(f"         etapa 2: {e2}, gap {linha['etapa2_gap'] or '-'}, "
              f"{parede2:.0f} s de parede, {cpu2:.0f} s de CPU", flush=True)
        if r2 is not None and ("optimal" in e2.lower() or "feasible" in e2.lower()) \
                and modelo.carregar_solucao(m, r2):
            escala = modelo.atribuicoes(m)
            linha["pena_max_etapa2"] = max(round(pyo.value(m.pena[k])) for k in m.pena)

    # conferencias da escala final: rigidas e descanso medido no relogio
    ind = fe.indicadores(inst, escala)
    med = fe.medir(inst, escala)
    problemas = solucao.conferir_rigidas(inst, escala, habilidade_rigida=True)
    descanso_ok = fe.cumpre(inst, med)
    linha.update(pedidos_atendidos=ind["pedidos_atendidos"],
                 enf_em_posto_tec=ind["enf_em_posto_tec"],
                 horas_min=ind["horas_min"], horas_max=ind["horas_max"],
                 descanso_ok=descanso_ok, menor_folga_h=med["menor_folga"],
                 menor_semanal_h=med["menor_semanal"], max_consec=med["max_consec"],
                 rigidas="; ".join(problemas) or "ok")
    # a penalidade tem de bater com o que a escala mostra: pedidos negados x W + enf em tec
    recontada = (ind["pedidos_total"] - ind["pedidos_atendidos"]) * W + ind["enf_em_posto_tec"]
    linha["penalidade_recontada"] = recontada
    ESCALAS.mkdir(parents=True, exist_ok=True)
    solucao.escrever_xml(inst, escala, ESCALAS / f"{inst.id}_objetivo.xml", penalidade=z)
    print(f"         penalidade {z} (recontada {recontada}) | pedidos "
          f"{ind['pedidos_atendidos']}/{ind['pedidos_total']} | enf em posto tec "
          f"{ind['enf_em_posto_tec']} | maior individual {linha['pena_max_etapa1']} -> "
          f"{linha.get('pena_max_etapa2', '-')} | descanso {'ok' if descanso_ok else 'FALHA'} "
          f"(menor {med['menor_folga']:g} h acima do exigido, semanal {med['menor_semanal']:g} h)"
          f" | rigidas {linha['rigidas']}", flush=True)
    return linha


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", action="append", type=int, help="tamanho; pode repetir")
    ap.add_argument("--solver", default=modelo.SOLVER_PADRAO)
    ap.add_argument("--tempo", type=int, default=900, help="limite POR ETAPA (padrao 900 s)")
    a = ap.parse_args()

    print(f"Curva com objetivo nao trivial (P1). Solver {a.solver}, limite {a.tempo} s por "
          f"etapa, semente {SEMENTE} (+N).")
    print(f"Maquina: {platform.processor()} | {platform.platform()} | "
          f"Python {platform.python_version()}", flush=True)
    linhas = []
    for n in a.n or esc.TAMANHOS:
        try:
            linhas.append(rodar(n, a.solver, a.tempo))
        except RuntimeError as e:
            print(f"   FALHOU {e}")
            return 1
        mesclar_csv(SAIDA, linhas, ("N",))

    print(f"\n{'N':>5s}{'etapa 1':>22s}{'s parede':>10s}{'etapa 2':>22s}{'s parede':>10s}"
          f"{'penal.':>8s}{'pedidos':>10s}{'descanso':>10s}")
    for r in linhas:
        print(f"{r['N']:5d}{str(r.get('etapa1_estado', '')):>22s}"
              f"{str(r.get('etapa1_parede_s', '')):>10s}{str(r.get('etapa2_estado', '')):>22s}"
              f"{str(r.get('etapa2_parede_s', '')):>10s}{str(r.get('penalidade', '')):>8s}"
              f"{str(r.get('pedidos_atendidos', '')) + '/' + str(r['pedidos']):>10s}"
              f"{'ok' if r.get('descanso_ok') else 'FALHA':>10s}")
    print(f"\nresultado: {SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
