"""Curva de escalabilidade do metodo exato: ate que tamanho a prova fecha?

Roda da raiz do repositorio, com a .venv ativa:

    python src\\escalabilidade.py                  # 36 (ancora), 40, 60, 80, 120, 200
    python src\\escalabilidade.py --n 40 --n 60    # so esses
    python src\\escalabilidade.py --tempo 1800     # limite por instancia, em segundos

Saida: `resultados/escalabilidade.csv`, gravado a cada instancia concluida e mesclado com o
que ja estiver la — uma queda no meio nao perde o que ja rodou.

Decide se vale implementar heuristica de warm start (decisao de 25/09, no
`VIRADA_ESCOPO_2026-09-24.md`): a heuristica so entra se existir faixa de tamanho em que a
prova nao fecha. **O que interessa e onde ela para de fechar, nao o tempo** — tempo de
resolucao e afirmacao fraca e nao vai ao texto como resultado.

## Como a demanda escala

Cada instancia tem `N` profissionais e a demanda cresce junto. A escala **nao** e proporcao
simples do porte: o porte e escolhido para que a fracao de profissional por janela seja a
MESMA do caso base (8,8095 -> teto 9, resto 0,1905). Sem isso o residuo de arredondamento
mudaria de instancia para instancia e a curva mediria duas coisas ao mesmo tempo — tamanho e
sorte de divisibilidade. Com isso, o piso de capacidade cai exatamente em `N` nos seis
tamanhos, conferido antes de resolver.

Consequencia: horas por profissional variam de 164,4 (N=36) a 167,4 (N=200), menos de 2%. E o
preco de manter o residuo fixo, e e o lado certo de pagar.

## Aviso sobre o valor objetivo, que aqui e degenerado

Na instancia brasileira, com os limites legais rigidos, **sobra pouca coisa na funcao
objetivo**: o que resta ativo no contrato e `single_assignment_per_day` (ja rigida no modelo),
`min_consecutive_working_days` = 1 e `min_consecutive_free_days` = 1, as duas satisfeitas por
qualquer bloco de trabalho. O otimo e zero, e o problema e de VIABILIDADE.

Entao, aqui, "provar otimalidade" quer dizer **decidir**: exibir escala legal ou provar que
nao existe. As colunas `valor` e `gap` sao registradas como pedido, mas vao sair 0 e 0%
sempre que o solver decidir — elas nao medem dificuldade nesta instancia. A coluna que mede e
`veredito`.

Isso nao enfraquece o experimento: encontrar a primeira escala viavel e exatamente o que o
warm start aceleraria, e e o que o `efetivo 36` ja custou 43 s de CPU no Experimento A.
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import pyomo.environ as pyo

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import instancia_br as br  # noqa: E402
import modelo  # noqa: E402
import solucao  # noqa: E402
from tabela import mesclar_csv  # noqa: E402

SAIDA = RAIZ / "resultados" / "escalabilidade.csv"
ESCALAS = RAIZ / "resultados" / "escalabilidade"

TAMANHOS = [36, 40, 60, 80, 120, 200]      # 36 e a ancora: resposta ja conhecida
HORAS_JANELA = 28 * 24                      # o perfil e horario; a janela do 12x36 tem 12 h

OTIMO, VIAVEL_SEM_PROVA, INVIAVEL, INDETERMINADO, ERRO = (
    "otimo_provado", "viavel_sem_prova", "inviavel", "indeterminado", "erro")


def porte_para(n: int) -> float:
    """Porte que mantem a fracao por janela do caso base e poe o piso exatamente em `n`.

    No caso base, 5.920 h em 28 dias dao 8,8095 profissionais por janela: teto 9, resto
    0,1905. Para `n` profissionais queremos `n/4` por janela com o mesmo resto — sao 56
    janelas de 12 h em 28 dias, e `56 * (n/4) = 14n`, que e a capacidade de `n` pessoas a
    14 plantoes cada.
    """
    fracao = br.PORTE_HORAS / HORAS_JANELA - math.floor(br.PORTE_HORAS / HORAS_JANELA)
    return HORAS_JANELA * (n / 4 - 1 + fracao)


def construir(n: int):
    return br.construir(grau="intermediario", regime="12x36", regra="teto",
                        efetivo=n, porte_horas=porte_para(n))


def piso(inst) -> int:
    """Maior dos dois limites inferiores conhecidos, os dois sem resolver nada."""
    capacidade = math.ceil(inst.demanda_total / br.MAX_ATRIBUICOES["12x36"])
    por_dia: dict = {}
    for (d, _), q in inst.demanda.items():
        por_dia[d] = por_dia.get(d, 0) + q
    dias = inst.dias
    alternancia = max(por_dia[dias[k]] + por_dia[dias[k + 1]] for k in range(len(dias) - 1))
    return max(capacidade, alternancia)


def _numero(resultado, *caminhos):
    """Le um numero do objeto de resultado, tentando varios dialetos de Pyomo."""
    for caminho in caminhos:
        alvo = resultado
        try:
            for parte in caminho.split("."):
                alvo = getattr(alvo, parte)
            if alvo is not None:
                return float(alvo)
        except (AttributeError, TypeError, ValueError):
            continue
    return None


def folga_relativa(resultado) -> str:
    """Gap entre a melhor solucao e o melhor limite, ao fim do tempo. "" se nao der para ler."""
    melhor = _numero(resultado, "best_feasible_objective",
                     "problem.upper_bound", "problem[0].upper_bound")
    limite = _numero(resultado, "best_objective_bound",
                     "problem.lower_bound", "problem[0].lower_bound")
    if melhor is None or limite is None:
        return ""
    if abs(melhor) < 1e-9:
        return "0.0%" if abs(melhor - limite) < 1e-6 else "inf"
    return f"{abs(melhor - limite) / abs(melhor):.1%}"


def rodar(n: int, solver: str, tempo: int, verboso: bool = True) -> dict:
    inst = construir(n)
    p = piso(inst)
    if p != n:
        # a instancia foi montada para o piso cair em n; se nao caiu, o resultado nao compara
        # com os outros tamanhos e e melhor falhar alto do que registrar linha enganosa
        raise RuntimeError(f"N={n}: piso deu {p}, esperado {n} — a escala de demanda quebrou")
    if verboso:
        print(f"\nN = {n:3d}: porte {porte_para(n):8.0f} h, demanda {inst.demanda_total:5d} "
              f"plantoes, piso {p}", flush=True)

    m = modelo.construir(inst, flexiveis=True, habilidade_rigida=True,
                         noite_antes_de_fds_livre=True,
                         rigidas_legais=modelo.RIGIDAS_LEGAIS_BR)
    d = modelo.dimensao(m)
    if verboso:
        print(f"         modelo: {d['variaveis']} variaveis, {d['restricoes']} restricoes",
              flush=True)

    t0, c0 = time.time(), time.process_time()
    try:
        resultado = modelo.resolver(m, solver=solver, tempo_limite=tempo, carregar=False)
    except Exception as e:  # noqa: BLE001
        print(f"         [ERRO] {type(e).__name__}: {e}")
        return {"N": n, "veredito": ERRO, "detalhe": f"{type(e).__name__}: {e}"}
    parede, cpu = time.time() - t0, time.process_time() - c0

    estado = modelo.estado(resultado).lower()
    valor, descanso, conferencia = "", "", ""
    if "infeasible" in estado:
        veredito = INVIAVEL
    elif "optimal" in estado or "feasible" in estado:
        if not modelo.carregar_solucao(m, resultado):
            veredito = ERRO
            conferencia = "solver declarou solucao e nao entregou"
        else:
            veredito = OTIMO if "optimal" in estado else VIAVEL_SEM_PROVA
            escala = modelo.atribuicoes(m)
            valor = modelo.valor_objetivo(m)
            ESCALAS.mkdir(parents=True, exist_ok=True)
            solucao.escrever_xml(inst, escala, ESCALAS / f"{inst.id}.xml", penalidade=valor)
            problemas = solucao.conferir_rigidas(inst, escala, habilidade_rigida=True)
            descanso, falhas = _conferir_descanso(inst, escala)
            conferencia = "; ".join(problemas + falhas) or "ok"
    else:
        veredito = INDETERMINADO

    if verboso:
        print(f"         {veredito:17s} valor={valor} gap={folga_relativa(resultado) or '-'} "
              f"({cpu:.0f}s de CPU)   conferencia: {conferencia or '-'}", flush=True)

    return {
        "N": n, "porte_horas": round(porte_para(n), 1),
        "demanda_plantoes": inst.demanda_total, "piso": p,
        "variaveis": d["variaveis"], "restricoes": d["restricoes"],
        "veredito": veredito, "valor": valor,
        "gap": folga_relativa(resultado), "estado_solver": modelo.estado(resultado),
        "descanso_minimo_h": descanso, "conferencia": conferencia,
        "segundos_cpu": round(cpu, 1), "segundos_parede": round(parede, 1),
        "limite_s": tempo, "solver": solver, "detalhe": "",
    }


def _conferir_descanso(inst, escala) -> tuple:
    """Descanso real na escala produzida, medido no relogio.

    O avaliador oficial nao serve para esta familia na instancia de 12x36 — ele le o padrao
    das 36 h como (noturno, folga, folga). Ver a P13 no historico. Entao a conferencia de
    descanso e esta, que le os horarios do arquivo.
    """
    from datetime import datetime, timedelta

    exigido = br.DESCANSO_EXIGIDO["12x36"]
    por_prof: dict = {}
    for (dia, n, turno) in escala:
        por_prof.setdefault(n, []).append((dia, turno))
    menor = float("inf")
    for turnos in por_prof.values():
        turnos.sort()
        marcos = []
        for dia, tid in turnos:
            t = inst.turnos[tid]
            ini = datetime.combine(dia, t.inicio)
            fim = datetime.combine(dia, t.fim) + (timedelta(days=1) if t.noturno
                                                  else timedelta())
            marcos.append((ini, fim))
        for k in range(len(marcos) - 1):
            menor = min(menor, (marcos[k + 1][0] - marcos[k][1]).total_seconds() / 3600)
    if menor == float("inf"):
        return "", []
    falhas = [] if menor >= exigido else [
        f"descanso minimo {menor:.0f} h, exigido {exigido} h"]
    return f"{menor:.0f}", falhas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", action="append", type=int, help="tamanho; pode repetir")
    ap.add_argument("--solver", default=modelo.SOLVER_PADRAO)
    ap.add_argument("--tempo", type=int, default=900,
                    help="limite por instancia, em segundos (padrao 900)")
    ap.add_argument("--quieto", action="store_true")
    a = ap.parse_args()

    tamanhos = a.n or TAMANHOS
    print(f"Curva de escalabilidade: {len(tamanhos)} instancias, solver {a.solver}, "
          f"limite {a.tempo}s cada")
    print("Grau intermediario, 12x36, arredondamento por teto. O 36 e a ancora: ja sabemos")
    print("que fecha, e serve para o script se denunciar se der outra coisa.")
    print("O objetivo e degenerado nesta instancia (otimo = 0): quem mede e `veredito`.")

    linhas = []
    for n in tamanhos:
        try:
            linha = rodar(n, a.solver, a.tempo, not a.quieto)
        except RuntimeError as e:
            print(f"   FALHOU {e}")
            return 1
        linhas.append(linha)
        mesclar_csv(SAIDA, linhas, ("N",))

    print(f"\n{'N':>5s}{'demanda':>9s}{'variaveis':>11s}{'restricoes':>12s}{'veredito':>18s}"
          f"{'valor':>7s}{'gap':>7s}{'descanso':>10s}{'conferencia':>13s}{'CPU (s)':>9s}")
    for r in linhas:
        print(f"{r['N']:5d}{r.get('demanda_plantoes', ''):>9}{r.get('variaveis', ''):>11}"
              f"{r.get('restricoes', ''):>12}{r['veredito']:>18s}{str(r.get('valor','')):>7s}"
              f"{str(r.get('gap','')):>7s}{str(r.get('descanso_minimo_h','')):>8s} h"
              f"{str(r.get('conferencia','')):>13s}{str(r.get('segundos_cpu','')):>9s}")

    fecharam = [r for r in linhas if r["veredito"] == OTIMO]
    nao = [r for r in linhas if r["veredito"] in (VIAVEL_SEM_PROVA, INDETERMINADO)]
    print(f"\nresultado: {SAIDA}")
    print(f"escalas:   {ESCALAS}")
    print(f"\nprova fechou em {len(fecharam)} de {len(linhas)}: "
          f"{[r['N'] for r in fecharam]}")
    if nao:
        print(f"NAO fechou em: {[(r['N'], r['veredito']) for r in nao]}")
        print("-> existe faixa em que a prova nao fecha; o warm start tem o que acelerar.")
    else:
        print("-> a prova fechou em todos os tamanhos testados. Pelo criterio de 25/09, o")
        print("   warm start NAO se justifica nesta faixa. Para decidir de vez, subir o N")
        print("   ate encontrar o limite, em vez de concluir que ele nao existe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
