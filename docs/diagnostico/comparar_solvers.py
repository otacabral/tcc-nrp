"""HiGHS x SCIP, Fase 0 (22/10; pedido do orientador na reuniao de 22/10). So diagnostico: NAO
mexe na ferramenta (`app.py`, `ferramenta.py`, `modelo.py` intocados; o SCIP entra so aqui).

    python docs\\diagnostico\\comparar_solvers.py --identidade   # o modelo que cada um recebe
    python docs\\diagnostico\\comparar_solvers.py --warmstart    # a partida da opcao B no SCIP
    python docs\\diagnostico\\comparar_solvers.py --fumaca       # sprint01 nos dois + avaliador

Regras iguais para os dois: o mesmo modelo Pyomo (`modelo.construir`), gap relativo de parada
0,01% (1e-4; no HiGHS e o padrao, aqui fixado), 1 thread, limite de tempo igual. HiGHS pelo
appsi (o caminho da ferramenta); SCIP pela interface nova do Pyomo (`ScipDirect`, PySCIPOpt) —
a antiga (`scip_direct` do `SolverFactory`) nao aceita partida nem log no Pyomo 6.10.1.
Gap comparado com a MESMA formula nos dois: (melhor escala - melhor limite) / |melhor escala|.
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / "src")]

import pyomo.environ as pyo  # noqa: E402
from pyomo.contrib.appsi.solvers import Highs  # noqa: E402
from pyomo.contrib.solver.solvers.scip.scip_direct import ScipDirect  # noqa: E402

import modelo  # noqa: E402
from parser import ler_instancia  # noqa: E402

GAP, THREADS = 1e-4, 1
SPRINT01 = RAIZ / "instancias/sprint/sprint/sprint01.xml"
falhas = 0


def confere(ok, msg):
    global falhas
    falhas += not ok
    print(f"   {'ok   ' if ok else 'FALHA'} {msg}", flush=True)


def highs(m, tempo, partida=False):
    """HiGHS como a ferramenta o chama (appsi), com gap e threads fixados. Devolve o dicionario
    de medidas e o objeto do solver (para ler o modelo que ele recebeu)."""
    h = Highs()
    h.config.time_limit = tempo
    h.config.load_solution = False
    h.config.mip_gap = GAP
    h.highs_options = {"threads": THREADS, "mip_rel_gap": GAP}
    t0 = time.time()
    r = h.solve(m) if not partida else _highs_partida(h, m)
    seg = time.time() - t0
    ub = r.best_feasible_objective
    lb = r.best_objective_bound
    if ub is not None and r.termination_condition.name != "infeasible":
        try:
            r.solution_loader.load_vars()
        except Exception:  # noqa: BLE001
            pass
    return _medidas("HiGHS", r.termination_condition.name, ub, lb, seg,
                    r.termination_condition.name == "optimal"), h


def _highs_partida(h, m):
    h.config.warmstart = True
    return h.solve(m)


import contextlib  # noqa: E402
import os  # noqa: E402
import tempfile  # noqa: E402

import pyomo.contrib.solver.solvers.scip.scip_direct as _scip_direct  # noqa: E402

_ultimo_log = {"texto": ""}


@contextlib.contextmanager
def _log_em_arquivo(*_a, **_k):
    """Troca o `capture_output(capture_fd=True)` do `ScipDirect`. Achado de 22/10: o Pyomo le o
    log do SCIP por um pipe, numa thread do Python, enquanto o `optimize()` do PySCIPOpt segura o
    GIL. Com log grande (o sprint01 sem partida), o pipe enche, o SCIP espera a thread, a thread
    espera o GIL: o processo para com CPU zero (duas rodadas travadas). Aqui o descritor 1 vai
    para um arquivo temporario, que nao enche; o log e lido depois."""
    sys.stdout.flush()
    with tempfile.TemporaryFile() as f:
        salvo = os.dup(1)
        os.dup2(f.fileno(), 1)
        try:
            yield
        finally:
            os.dup2(salvo, 1)
            os.close(salvo)
            f.seek(0)
            _ultimo_log["texto"] = f.read().decode("utf-8", errors="replace")


_scip_direct.capture_output = _log_em_arquivo


class ScipObjetivoDireto(ScipDirect):
    """O `ScipDirect` do Pyomo 6.10.1 reescreve o objetivo como epigrafo: cria uma variavel z,
    a restricao z >= objetivo e minimiza z. E equivalente, mas NAO e o modelo que o HiGHS recebe
    (no HiGHS o objetivo vai como custo das colunas), e o epigrafo pode atrapalhar o SCIP. Aqui
    o objetivo vai direto, como custo das variaveis — o mesmo problema dos dois lados (item 4).
    So muda este metodo; o resto da interface e a do Pyomo."""

    def _set_objective(self, obj):
        if obj is None:
            self._solver_model.setObjective(0, sense="minimize")
        else:
            expr = self._expr_visitor.walk_expression(obj.expr)
            self._solver_model.setObjective(
                expr, sense="minimize" if obj.sense == pyo.minimize else "maximize")
        self._objective = obj


def scip(m, tempo, partida=False):
    s = ScipObjetivoDireto()
    t0 = time.time()
    r = s.solve(m, time_limit=tempo, rel_gap=GAP, threads=THREADS, load_solutions=False,
                raise_exception_on_nonoptimal_result=False, warmstart_discrete_vars=partida)
    seg = time.time() - t0
    ub, lb = r.incumbent_objective, r.objective_bound
    if ub is not None:
        r.solution_loader.load_vars()
    provou = r.termination_condition.name == "convergenceCriteriaSatisfied"
    d = _medidas("SCIP", f"{r.termination_condition.name} ({s._solver_model.getStatus()})",
                 ub, lb, seg, provou)
    d["log"] = _ultimo_log["texto"]
    return d, s


def _medidas(nome, estado, ub, lb, seg, provou):
    gap = None
    if ub is not None and lb is not None and not math.isinf(lb):
        gap = 0.0 if abs(ub) < 1e-9 and abs(ub - lb) < 1e-6 else abs(ub - lb) / max(abs(ub), 1e-9)
    return {"solver": nome, "estado": estado, "ub": ub, "lb": lb, "gap": gap, "tempo": seg,
            "provado": provou}


def _tamanho(m):
    nv = sum(1 for v in m.component_data_objects(pyo.Var, active=True))
    ni = sum(1 for v in m.component_data_objects(pyo.Var, active=True) if v.is_integer())
    nc = sum(1 for c in m.component_data_objects(pyo.Constraint, active=True))
    return nv, ni, nc


# --- item 4: o modelo que cada solver recebeu ---------------------------------------------------

def _canon_highs(h):
    """Linhas e colunas como o HiGHS as recebeu, com o nome da variavel do Pyomo."""
    lp = h._solver_model.getLp()
    nome = {i: v.name for v, i in ((h._vars[k][0], h._pyomo_var_to_solver_var_map[k])
                                   for k in h._pyomo_var_to_solver_var_map)}
    cols = {nome[j]: (_lim(lp.col_lower_[j]), _lim(lp.col_upper_[j]), float(lp.col_cost_[j]))
            for j in range(lp.num_col_)}
    a = lp.a_matrix_
    linhas = Counter()
    if a.format_.name == "kColwise":
        por_linha = [[] for _ in range(lp.num_row_)]
        for j in range(lp.num_col_):
            for k in range(a.start_[j], a.start_[j + 1]):
                por_linha[a.index_[k]].append((nome[j], round(a.value_[k], 9)))
    else:
        por_linha = [[(nome[a.index_[k]], round(a.value_[k], 9))
                      for k in range(a.start_[i], a.start_[i + 1])] for i in range(lp.num_row_)]
    for i, termos in enumerate(por_linha):
        linhas[_linha(termos, lp.row_lower_[i], lp.row_upper_[i])] += 1
    inteiras = {nome[j] for j in range(lp.num_col_)
                if lp.integrality_ and lp.integrality_[j].name != "kContinuous"}
    return cols, linhas, inteiras, lp.offset_


def _canon_scip(s):
    sm = s._solver_model
    nome = {sv.name: pv.name for pv, sv in s._pyomo_var_to_solver_var_map.items()}
    variaveis = sm.getVars(transformed=False)          # o problema recebido, nao o pre-processado
    sobra = [v.name for v in variaveis if v.name not in nome]
    if sobra:
        raise RuntimeError(f"o SCIP recebeu variaveis que o Pyomo nao tem: {sobra[:5]}")
    cols = {nome[v.name]: (_lim(v.getLbOriginal()), _lim(v.getUbOriginal()), float(v.getObj()))
            for v in variaveis}
    linhas = Counter()
    for c in sm.getConss(transformed=False):
        termos = [(nome[k], round(val, 9)) for k, val in sm.getValsLinear(c).items()]
        linhas[_linha(termos, sm.getLhs(c), sm.getRhs(c))] += 1
    inteiras = {nome[v.name] for v in variaveis if v.vtype() in ("BINARY", "INTEGER")}
    return cols, linhas, inteiras, sm.getObjoffset()


def _lim(x):
    return None if x is None or abs(x) >= 1e19 else round(float(x), 9)


def _linha(termos, lo, up):
    """Forma canonica de uma linha: so com limite inferior (a >= b) vira -a <= -b, porque os
    dois solvers recebem a mesma restricao, as vezes multiplicada por -1."""
    lo, up = _lim(lo), _lim(up)
    if up is None and lo is not None:
        termos, lo, up = [(n, -c) for n, c in termos], None, -lo
    return tuple(sorted(termos)), lo, up


def identidade() -> int:
    from ferramenta import modelo_etapa1, montar
    import instancia_br as br
    import ferramenta as fe
    casos = [("sprint01 (INRC)", lambda: modelo.construir(ler_instancia(str(SPRINT01)))),
             ("ferramenta, 12x36, 4 + 8, padrao", lambda: modelo_etapa1(montar(fe.Entrada(
                 turnos=fe.MODELOS[list(fe.MODELOS)[0]], grau="intermediario", n_enfermeiros=4,
                 n_tecnicos=8, demanda_turno={"D": (1, 2), "N": (1, 2)},
                 inicio=br.primeira_segunda())), None)[0])]
    for rotulo, faz in casos:
        print(f"identidade: {rotulo}")
        m = faz()
        _, h = highs(m, 1)
        _, s = scip(m, 1)
        ch, cs = _canon_highs(h), _canon_scip(s)
        nv, ni, nc = _tamanho(m)
        print(f"   Pyomo: {nv} variaveis ({ni} inteiras), {nc} restricoes")
        print(f"   HiGHS recebeu: {len(ch[0])} colunas ({len(ch[2])} inteiras), "
              f"{sum(ch[1].values())} linhas, offset {ch[3]}")
        print(f"   SCIP recebeu:  {len(cs[0])} colunas ({len(cs[2])} inteiras), "
              f"{sum(cs[1].values())} linhas, offset {cs[3]}")
        confere(ch[0] == cs[0], "colunas iguais (limites e custo, por variavel)")
        confere(ch[2] == cs[2], "as mesmas variaveis inteiras")
        confere(ch[1] == cs[1], "linhas iguais (coeficientes por variavel e limites)")
        confere(abs(ch[3] - cs[3]) < 1e-9, "a mesma constante no objetivo")
    # controle positivo: uma linha a mais so do lado do SCIP tem de aparecer como diferenca
    m = casos[0][1]()
    _, h = highs(m, 1)
    v = next(iter(m.component_data_objects(pyo.Var, active=True)))
    m.controle = pyo.Constraint(expr=v <= 7)
    _, s = scip(m, 1)
    ch, cs = _canon_highs(h), _canon_scip(s)
    confere(ch[1] != cs[1] and sum(cs[1].values()) == sum(ch[1].values()) + 1,
            "controle: uma linha a mais so no SCIP e acusada")
    print("identidade " + ("OK" if not falhas else f"com {falhas} FALHA(S)"))
    return 1 if falhas else 0


# --- item 2: a partida da opcao B -----------------------------------------------------------------

def _partida_no_log(log):
    """As linhas em que o SCIP registra a solucao de partida: a parcial (so as inteiras, como
    o Pyomo a entrega) e completada pela heuristica `completesol`, e a original e transformada
    para o problema pre-processado ("transformed 1/1 original solutions")."""
    return [l.strip() for l in log.splitlines()
            if "completesol" in l or "original solutions" in l or "partial" in l.lower()]


def warmstart() -> int:
    print("warmstart (1): sprint01, a escala otima do HiGHS como partida do SCIP")
    m = modelo.construir(ler_instancia(str(SPRINT01)))
    d, _ = highs(m, 120)
    print(f"   HiGHS: {d['estado']}, valor {d['ub']}")
    d2, _ = scip(m, 120, partida=True)
    linhas = _partida_no_log(d2["log"])
    print("   log do SCIP:", *linhas[:4], sep="\n      ")
    confere(any("completesol" in l and "5.600000e+01" in l for l in linhas),
            "o SCIP aceitou a partida: a heuristica completesol a completou com valor 56")
    print(f"   SCIP: {d2['estado']}, valor {d2['ub']}")
    d3, _ = scip(modelo.construir(ler_instancia(str(SPRINT01))), 120, partida=False)
    confere(not any("completesol" in l for l in _partida_no_log(d3["log"])),
            "controle: sem partida, o log nao tem a linha do completesol")

    print("warmstart (2): opcao B, 3 niveis em sequencia, bloco 2 parte da escala do bloco 1")
    import ferramenta as fe
    import instancia_br as br
    import prioridades as pr
    ini = br.primeira_segunda()
    p = dict(fe.prioridades_padrao(), min_turnos=(fe.DESEJAVEL, 14))
    e = fe.Entrada(turnos=fe.MODELOS[list(fe.MODELOS)[0]], grau="intermediario",
                   n_enfermeiros=1, n_tecnicos=2, demanda_turno={"D": (0, 1), "N": (0, 0)},
                   inicio=ini, pedidos=[("Téc 1", ini), ("Téc 2", ini)], prioridades=p)
    original = pr.LIMITE_FUSAO
    pr.LIMITE_FUSAO = 0
    try:
        m, inst, blocos = fe.modelo_etapa1(fe.montar(e), p)
    finally:
        pr.LIMITE_FUSAO = original
    presentes = [b for b in blocos if any(f in m.parcela for f in b.familias)]
    m.presos = pyo.ConstraintList()
    valores = []
    for i, b in enumerate(presentes):
        expr = sum(m.parcela[f] for f in b.familias if f in m.parcela)
        m.del_component(m.objetivo)
        m.objetivo = pyo.Objective(expr=expr, sense=pyo.minimize)
        d, _ = scip(m, 60, partida=bool(i))
        valores.append(round(d["ub"]))
        if i:
            linhas = _partida_no_log(d["log"])
            print(f"   bloco {i + 1} ({'+'.join(b.niveis)}), log:", *linhas[:3], sep="\n      ")
            confere(any("completesol" in l for l in linhas),
                    f"bloco {i + 1}: o SCIP aceitou a partida (completesol)")
        m.presos.add(expr <= valores[-1])
    confere(valores == [0, 1, 14], f"valores por nivel {valores} (a ferramenta com o HiGHS: "
                                   f"0, 1, 14, teste opB-b)")
    print("warmstart " + ("OK" if not falhas else f"com {falhas} FALHA(S)"))
    return 1 if falhas else 0


# --- item 6: fumaca ---------------------------------------------------------------------------

def fumaca() -> int:
    import validar
    from solucao import escrever_xml
    saida = RAIZ / "resultados" / "solvers_2026-10-22"
    saida.mkdir(parents=True, exist_ok=True)
    inst = ler_instancia(str(SPRINT01))
    linhas = ["| Solver | Variáveis | Restrições | Tempo (s) | Melhor escala | Melhor limite | "
              "Gap | Ótimo provado | Avaliador oficial |", "|---|---:|---:|---:|---:|---:|---:|---|---:|"]
    for nome, f in (("HiGHS", highs), ("SCIP", scip)):
        m = modelo.construir(inst)
        nv, _, nc = _tamanho(m)
        d, _ = f(m, 600)
        escala = modelo.atribuicoes(m)
        arq = saida / f"sprint01_{nome}.xml"
        escrever_xml(inst, escala, arq)
        valor, _, _ = validar.avaliar(SPRINT01, arq)
        print(f"   {nome}: {d['estado']} | {d['tempo']:.1f} s | escala {d['ub']} | limite "
              f"{d['lb']} | gap {d['gap']} | avaliador {valor}")
        confere(d["provado"] and round(d["ub"]) == 56, f"{nome}: otimo provado, 56 (Tabela 6)")
        confere(valor == 56, f"{nome}: avaliador oficial 56")
        linhas.append(f"| {nome} | {nv} | {nc} | {d['tempo']:.1f} | {d['ub']:g} | {d['lb']:g} | "
                      f"{d['gap']:.2%} | {'sim' if d['provado'] else 'não'} | {valor} |")
    (saida / "fumaca.md").write_text("\n".join(
        ["# Fumaça HiGHS × SCIP — sprint01 (22/10)", "",
         "i5-10210U, 1 thread, gap 0,01%, limite 600 s; HiGHS 1.15.1 (appsi), SCIP 10.0 "
         "(PySCIPOpt 6.3.0). Tempo medido numa configuração só: não é resultado.", "",
         *linhas, ""]), encoding="utf-8")
    print("fumaca " + ("OK" if not falhas else f"com {falhas} FALHA(S)"))
    return 1 if falhas else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--identidade", action="store_true")
    g.add_argument("--warmstart", action="store_true")
    g.add_argument("--fumaca", action="store_true")
    a = ap.parse_args()
    sys.exit(identidade() if a.identidade else warmstart() if a.warmstart else fumaca())
