"""A1 da P17 (09/10): o HiGHS, pelo appsi, aceita a escala da etapa 1 como solucao inicial da
etapa 2? Sonda minima, sem mexer em src/.

    python docs\\diagnostico\\sonda_warmstart.py <log_do_highs>

Caso P08 da bateria (12x36, 8 + 4, o menor). Etapa 1 como a ferramenta (pesos + modelo_br),
solucao carregada no modelo; etapa 2 montada com `preparar_equilibrio(..., exato=False)`
(penalidade <= valor da etapa 1); `f_max`/`f_min` recebem os valores da escala da etapa 1 (sem
isso o Pyomo os mandaria como 0 e a partida seria inviavel); resolve com `warmstart=True`, 20 s,
log do HiGHS em arquivo. Procura no log a mensagem do HiGHS sobre a solucao inicial.
"""

from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(AQUI))

import pyomo.environ as pyo  # noqa: E402

import bateria_propriedades as bp  # noqa: E402
import bateria_rodar as brd  # noqa: E402
import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import modelo  # noqa: E402


def main() -> int:
    log = Path(sys.argv[1])
    c = next(x for x in bp.TODOS if x.nome.startswith("P08"))
    inst, custo, _ = fe.pesos(fe.montar(brd.entrada(c)))
    m = ea.modelo_br(inst, custo)
    res = modelo.resolver(m, solver=modelo.SOLVER_PADRAO, tempo_limite=60, carregar=False)
    assert modelo.carregar_solucao(m, res)
    z = modelo.valor_objetivo(m)
    escala = modelo.atribuicoes(m)
    print("etapa 1: valor", z, "| provado", modelo.provou_otimo(res))
    fe.preparar_equilibrio(m, inst, z, exato=False)
    por = fe.por_categoria(inst, escala)
    for g in m.f_max:
        m.f_max[g].value = por[g]["fracao_max"]
        m.f_min[g].value = por[g]["fracao_min"]
    print("partida: criterio da etapa 2 na escala da etapa 1 =", pyo.value(m.objetivo_equilibrio.expr))
    opt = pyo.SolverFactory(modelo.SOLVER_PADRAO)
    opt.options["log_file"] = str(log)
    r2 = opt.solve(m, load_solutions=False, timelimit=20, warmstart=True)
    print("etapa 2: estado", modelo.estado(r2), "| tem solucao", modelo.tem_solucao(r2))
    texto = log.read_text(encoding="utf-8", errors="replace")
    linhas = [l for l in texto.splitlines() if "start" in l.lower() or "feasible" in l.lower()]
    print("linhas do log sobre a partida:", linhas[:6])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
