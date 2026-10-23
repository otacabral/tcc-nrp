"""Diagnostico da anomalia da bateria HiGHS x SCIP (22/10): no medium_late05, o HiGHS informou 7.435
como melhor solucao e a escala carregada vale 2.199 no avaliador oficial. So o HiGHS, nas
condicoes da bateria (600 s, gap 0,01%, 1 thread, appsi). Nada da ferramenta muda.

    python docs\\diagnostico\\anomalia_medium_late05.py

Compara: (1) o valor informado pelo appsi (`best_feasible_objective`) e o do proprio HiGHS
(`objective_function_value`); (2) o objetivo recalculado nas variaveis carregadas, e o produto
custo x valor das colunas; (3) a integralidade das variaveis inteiras (maior desvio de 0/1);
(4) a penalidade verdadeira da escala (avaliacao.py e avaliador oficial); (5) por familia, a soma
das folgas no modelo contra a contagem do avaliacao.py — folga maior que o excesso = folga solta.
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(AQUI)]

import pyomo.environ as pyo  # noqa: E402
from pyomo.contrib.appsi.solvers import Highs  # noqa: E402

import modelo  # noqa: E402
import validar  # noqa: E402
from avaliacao import por_restricao  # noqa: E402
from parser import ler_instancia  # noqa: E402
from solucao import escrever_xml  # noqa: E402

INST = RAIZ / "instancias/medium/medium_late_xml/medium_late05.xml"
SAIDA = RAIZ / "resultados" / "solvers_2026-10-22" / "anomalia"


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    inst = ler_instancia(str(INST))
    m = modelo.construir(inst)
    h = Highs()
    h.config.time_limit = 600
    h.config.load_solution = False
    h.config.mip_gap = 1e-4
    h.highs_options = {"threads": 1, "mip_rel_gap": 1e-4}
    t0 = time.time()
    r = h.solve(m)
    seg = time.time() - t0
    hs = h._solver_model
    info = hs.getInfo()
    out = {"tempo_s": round(seg, 1), "estado": r.termination_condition.name,
           "appsi_best_feasible_objective": r.best_feasible_objective,
           "appsi_best_objective_bound": r.best_objective_bound,
           "highs_objective_function_value": info.objective_function_value,
           "highs_mip_dual_bound": info.mip_dual_bound,
           "highs_mip_gap": info.mip_gap,
           "highs_primal_solution_status": info.primal_solution_status}
    r.solution_loader.load_vars()
    out["objetivo_recalculado_nas_variaveis_carregadas"] = pyo.value(m.objetivo)
    lp = hs.getLp()
    sol = hs.getSolution()
    out["custo_x_valor_das_colunas_highs"] = (sum(c * v for c, v in zip(lp.col_cost_, sol.col_value))
                                              + lp.offset_)
    desvio, pior = 0.0, None
    inteiras = 0
    for v in m.component_data_objects(pyo.Var, active=True):
        if v.is_integer() and v.value is not None:
            inteiras += 1
            d = abs(v.value - round(v.value))
            if d > desvio:
                desvio, pior = d, v.name
    out["inteiras"] = inteiras
    out["maior_desvio_de_integralidade"] = desvio
    out["variavel_do_maior_desvio"] = pior
    escala = modelo.atribuicoes(m)
    verdade = por_restricao(inst, escala)
    out["penalidade_avaliacao_py"] = sum(verdade.values())
    arq = SAIDA / "medium_late05_HiGHS_escala.xml"
    escrever_xml(inst, escala, arq)
    valor, resumida, _ = validar.avaliar(INST, arq)
    out["penalidade_avaliador_oficial"] = valor
    # por familia: a parcela do modelo (peso x folga, nas variaveis carregadas) x a contagem do
    # avaliacao.py na escala (custo = excesso x peso). Parcela maior = folga solta.
    out["parcelas_do_modelo"] = {f: round(pyo.value(e), 4) for f, e in m.parcela.items()}
    out["avaliacao_py_por_familia"] = dict(verdade)
    (SAIDA / "diagnostico.json").write_text(json.dumps(out, ensure_ascii=False, indent=1,
                                                       default=str), encoding="utf-8")
    for k, v in out.items():
        if k not in ("parcelas_do_modelo", "avaliacao_py_por_familia"):
            print(f"{k}: {v}")
    print("parcelas do modelo (peso x folga, por familia) x avaliacao.py:")
    for fam, valor_m in (out["parcelas_do_modelo"] or {}).items():
        print(f"   {fam:45s} modelo {valor_m:10.2f} | avaliacao.py {verdade.get(fam, 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
