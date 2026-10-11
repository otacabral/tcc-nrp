"""Diagnostico da etapa 2 no K5 (11/10): mais tempo (A) e quebra de simetria (B). SO TESTE.

    python docs\\diagnostico\\p17_etapa2_variantes.py A              # 1800 s
    python docs\\diagnostico\\p17_etapa2_variantes.py B              # 180 s, com ordem por horas
    python docs\\diagnostico\\p17_etapa2_variantes.py A --teste      # 60 s, so para ver rodar
    python docs\\diagnostico\\p17_etapa2_variantes.py B --teste

Decisao do Otavio (11/10): nada muda em `src/`, na ferramenta ou na v1.2.2, qualquer que seja o
resultado. Este script monta, por fora, o modelo da etapa 2 do K5 com as funcoes da ferramenta
(`ferramenta.montar`, `ferramenta.pesos`, `experimento_a.modelo_br`,
`ferramenta.preparar_equilibrio(..., exato=False)`) e o resolve com `modelo.resolver`.

PARTIDA: a escala da etapa 1 gravada em `resultados/p17_diagnostico_2026-10-10/etapa1_escala.json`
(criterio 0,4091; penalidade 21). Para a partida ser viavel no modelo inteiro, as variaveis
auxiliares da etapa 1 (folgas das restricoes flexiveis) precisam de valor coerente com ela: o
script FIXA os `x` nessa escala, resolve a etapa 1 (so sobram as auxiliares), confere que o
objetivo e 21, e solta os `x`. Depois troca o objetivo pelo da etapa 2, com penalidade <= 21,
preenche `f_max`/`f_min` com os valores da escala e resolve com `partida=True`.

A) TEMPO: o mesmo modelo da etapa 2, limite de 1800 s.
B) SIMETRIA: limite de 180 s, com restricoes de ordem dentro de cada grupo de profissionais
   IDENTICOS (mesma categoria, mesmas horas devidas, mesmas indisponibilidades, mesmos pedidos):
   horas(i) >= horas(i+1), na ordem dos ids. No K5, os 13 enfermeiros formam um grupo e os 5
   tecnicos outro (conferido pelo script). A partida e a mesma escala com as pessoas
   RENUMERADAS por horas decrescentes dentro do grupo: o criterio continua 0,4091 e a escala
   cumpre a ordem. A escala final e devolvida a numeracao original (inversa da renumeracao) e
   conferida na instancia original.

ESPERADO, registrado e commitado ANTES de rodar (decisao do Otavio, 11/10): "melhora" e "sem
melhora" sao os dois resultados validos, em A e em B. Conferencias, todas obrigatorias:
1. partida aceita pelo HiGHS com valor 0,4091 (do log);
2. havendo melhora, o criterio recontado da escala final SEM `ferramenta.indicadores` (pela
   recontagem de `p17_diagnostico_k5.recontar`, que so le a escala e os horarios da Entrada) =
   o melhor valor do log;
3. penalidade da escala final <= 21, recontada da escala (enfermeiros em posto de tecnico; o K5
   nao tem pedidos);
4. descanso (`ferramenta.cumpre`) e rigidas (`solucao.conferir_rigidas`) OK;
5. em B, a escala final, desfeita a renumeracao, e legal na instancia original (4. aplicado a
   ela) e tem o mesmo criterio recontado.
Qualquer conferencia falhando e defeito do diagnostico, nao da ferramenta, e para a rodada.

Grava em `resultados/p17_variantes_2026-10-11/<A|B>/` (ou `<A|B>_teste/`): `highs.log`,
`escala_final.json`, `resumo.json` (melhoras com tempo e valor, limites, conferencias e a
diferenca entre colegas por categoria em horas).
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "docs"))
sys.path.insert(0, str(AQUI))

import pyomo.environ as pyo  # noqa: E402

import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import modelo  # noqa: E402
import solucao  # noqa: E402
import p17_diagnostico_k5 as diag  # noqa: E402

PARTIDA = RAIZ / "resultados" / "p17_diagnostico_2026-10-10" / "etapa1_escala.json"
SAIDA = RAIZ / "resultados" / "p17_variantes_2026-10-11"
Z = 21                   # penalidade da etapa 1 nessa escala (ferramenta.json da rodada)
CRITERIO_PARTIDA = 0.40909090909
TOL = 1e-6


def ler_escala(arq: Path):
    return [(date.fromisoformat(d), n, s) for d, n, s in json.loads(arq.read_text("utf-8"))]


def grupos_identicos(inst) -> list[list[str]]:
    chave = {}
    for n, p in inst.profissionais.items():
        k = (fe.categoria(inst, n), inst.horas_devidas(n),
             tuple(sorted(str(d) for m, d in inst.indisponiveis if m == n)),
             tuple(sorted((str(q.data), q.tipo, str(q.turno)) for q in inst.pedidos if q.profissional == n)))
        chave.setdefault(k, []).append(n)
    return [sorted(g, key=int) for g in chave.values() if len(g) > 1]


def horas_por_pessoa(inst, escala) -> dict[str, float]:
    h = {n: 0.0 for n in inst.profissionais}
    for _, n, s in escala:
        h[n] += inst.turnos[s].duracao_h
    return h


def renumerar(inst, escala, grupos):
    """Dentro de cada grupo, a pessoa com mais horas vai para o primeiro id, e assim por diante.
    Devolve (escala renumerada, mapa novo -> original)."""
    h = horas_por_pessoa(inst, escala)
    ida, volta = {}, {}
    for g in grupos:
        por_horas = sorted(g, key=lambda n: (-h[n], int(n)))
        for novo, original in zip(g, por_horas):
            ida[original], volta[novo] = novo, original
    troca = lambda n, mapa: mapa.get(n, n)
    return [(d, troca(n, ida), s) for d, n, s in escala], volta


def penalidade_recontada(inst, escala) -> int:
    """Enfermeiros em posto de tecnico (o K5 nao tem pedidos): a etapa 1 da ferramenta."""
    base = {s for s, t in inst.turnos.items() if fe.br.HABILIDADE_ENF not in t.habilidades}
    return sum(1 for _, n, s in escala if fe.categoria(inst, n) == fe.ENF and s in base)


def legal(inst, escala) -> bool:
    return (fe.cumpre(inst, fe.medir(inst, escala))
            and not solucao.conferir_rigidas(inst, escala, habilidade_rigida=True))


def main() -> int:
    variante = sys.argv[1]
    teste = "--teste" in sys.argv
    tempo = 60 if teste else (1800 if variante == "A" else 180)
    saida = SAIDA / (variante + ("_teste" if teste else ""))
    saida.mkdir(parents=True, exist_ok=True)
    log = saida / "highs.log"
    if log.exists():
        log.unlink()

    e = diag.entrada()
    inst = fe.montar(e)
    inst, custo, W = fe.pesos(inst)
    escala0 = ler_escala(PARTIDA)
    grupos = grupos_identicos(inst)
    print("grupos de identicos:", [len(g) for g in grupos], flush=True)
    escala_partida, volta = (renumerar(inst, escala0, grupos) if variante == "B"
                             else (escala0, {}))

    m = ea.modelo_br(inst, custo)
    na_escala = {(n, s, d) for d, n, s in escala_partida}
    for idx in m.X:
        m.x[idx].fix(1 if idx in na_escala else 0)
    r = modelo.resolver(m, solver=modelo.SOLVER_PADRAO, tempo_limite=60, carregar=False)
    if not modelo.carregar_solucao(m, r):
        raise SystemExit("PARADO: a escala de partida nao fecha no modelo da etapa 1")
    z = modelo.valor_objetivo(m)
    if z != Z:
        raise SystemExit(f"PARADO: penalidade da partida no modelo = {z}, esperado {Z}")
    for idx in m.X:
        m.x[idx].unfix()

    fe.preparar_equilibrio(m, inst, Z, exato=False)
    cat = fe.por_categoria(inst, escala_partida)
    for g in m.f_max:
        m.f_max[g].value = cat[g]["fracao_max"]
        m.f_min[g].value = cat[g]["fracao_min"]
    if variante == "B":
        horas = {n: sum(inst.turnos[s].duracao_h * m.x[n, s, d] for (n2, s, d) in m.X if n2 == n)
                 for n in inst.profissionais}
        pares = [(g[i], g[i + 1]) for g in grupos for i in range(len(g) - 1)]
        m.ordem = pyo.Constraint(range(len(pares)),
                                 rule=lambda m, k: horas[pares[k][0]] >= horas[pares[k][1]])
        print(f"restricoes de ordem: {len(pares)}", flush=True)

    r = modelo.resolver(m, solver=modelo.SOLVER_PADRAO, tempo_limite=tempo, carregar=False,
                        partida=True, log_arquivo=str(log))
    if not modelo.carregar_solucao(m, r):
        raise SystemExit("PARADO: a etapa 2 nao devolveu escala")
    final = list(modelo.atribuicoes(m))
    final_original = [(d, volta.get(n, n), s) for d, n, s in final]

    lg = diag.ler_log(log)
    rc_partida = diag.recontar(escala_partida, e)
    rc_final = diag.recontar(final, e)
    rc_original = diag.recontar(final_original, e)
    primal = diag._num(lg["primal"])
    melhorou = primal is not None and primal < CRITERIO_PARTIDA - TOL
    conf = {
        "1 partida aceita = 0,4091": lg["partida"] is not None
                                     and abs(lg["partida"] - CRITERIO_PARTIDA) < TOL
                                     and abs(rc_partida["criterio"] - CRITERIO_PARTIDA) < TOL,
        "2 criterio recontado = melhor do log": (not melhorou)
                                                or abs(rc_final["criterio"] - primal) < TOL,
        "3 penalidade <= 21": penalidade_recontada(inst, final_original) <= Z,
        "4 descanso e rigidas": legal(inst, final),
    }
    if variante == "B":
        conf["5 desfeita a renumeracao, legal e mesmo criterio"] = (
            legal(inst, final_original)
            and abs(rc_original["criterio"] - rc_final["criterio"]) < TOL)
    if not melhorou:
        conf["sem melhora: criterio final = partida"] = abs(rc_final["criterio"]
                                                            - CRITERIO_PARTIDA) < TOL

    resumo = {
        "variante": variante, "teste": teste, "tempo_limite": tempo,
        "grupos_identicos": [len(g) for g in grupos],
        "desfecho": "MELHORA" if melhorou else "SEM MELHORA",
        "partida_log": lg["partida"], "melhoras": lg["melhoras_na_tabela"],
        "primal": lg["primal"], "dual": lg["dual"], "gap": lg["gap"], "status": lg["status"],
        "penalidade_final": penalidade_recontada(inst, final_original),
        "diferenca_h": {g: {"partida": rc_partida[g]["diferenca_h"],
                            "final": rc_original[g]["diferenca_h"]}
                        for g in ("enfermeiros", "tecnicos")},
        "criterio": {"partida": rc_partida["criterio"], "final": rc_original["criterio"]},
        "conferencias": conf,
    }
    (saida / "escala_final.json").write_text(
        json.dumps([(str(d), n, s) for d, n, s in final_original]), encoding="utf-8")
    (saida / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1,
                                                  default=str), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False, indent=1, default=str))
    ok = all(conf.values())
    print(f"{variante}{' (teste)' if teste else ''}: {resumo['desfecho']}; "
          f"{'CONFERENCIAS OK' if ok else 'CONFERENCIA FALHOU'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
