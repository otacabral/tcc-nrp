"""Instancia -> modelo Pyomo.

Fronteira (PLANO.md): este modulo consome apenas `Instancia`, nunca XML. E o que permite a
instancia brasileira entrar sem tocar no modelo.

Estado: **modelo minimo**, so com as duas restricoes rigidas da competicao. As 13 flexiveis
entram uma por vez nas semanas 2-3, conferindo no avaliador a cada uma.

O solver e parametro da chamada, nunca do modelo (CONTEXTO_PROJETO.md, secao 8):

    m = construir(inst)
    resolver(m, solver="appsi_highs")     # padrao, sem licenca
    resolver(m, solver="appsi_gurobi")    # se a licenca academica sair
"""

from __future__ import annotations

from datetime import date

import pyomo.environ as pyo

from instancia import Instancia

SOLVER_PADRAO = "appsi_highs"


# ---------------------------------------------------------------------------
# Construcao
# ---------------------------------------------------------------------------

def construir(inst: Instancia, habilidade_rigida: bool = True) -> pyo.ConcreteModel:
    """Modelo minimo: duas rigidas, funcao objetivo nula.

    Rigidas (documentacao oficial, secao 2.2.1):
      (I) toda a demanda deve ser coberta — modelada como igualdade, seguindo Santos et al.
          (2016) e o DECISOES.md de 08/09. Turno sem demanda declarada num dia tem demanda
          zero, portanto ninguem pode trabalhar nele naquele dia;
      (II) no maximo um turno por profissional por dia.

    `habilidade_rigida` e a flag da pergunta aberta do DECISOES.md. Com True, so entram no
    modelo as atribuicoes em que o profissional tem a habilidade exigida pelo turno — a
    leitura de que categoria alternativa e proibida. Com False, qualquer profissional pode
    cobrir qualquer turno, que e a leitura de que a habilidade so gera penalidade. As duas
    versoes rodadas contra `long01` = 197 resolvem a duvida: so uma da exatamente 197.
    """
    m = pyo.ConcreteModel(name=inst.id)

    dias = inst.dias
    turnos = tuple(inst.turnos)

    if habilidade_rigida:
        elegiveis = {s: inst.habilitados(s) for s in turnos}
    else:
        todos = tuple(inst.profissionais)
        elegiveis = {s: todos for s in turnos}

    for s in turnos:
        if not elegiveis[s] and any(inst.demanda_de(d, s) > 0 for d in dias):
            raise ValueError(
                f"{inst.id}: turno {s} tem demanda mas nenhum profissional habilitado. "
                f"Exige {sorted(inst.turnos[s].habilidades)}.")

    indice = [(n, s, d) for s in turnos for n in elegiveis[s] for d in dias]
    m.X = pyo.Set(initialize=indice, dimen=3)
    m.x = pyo.Var(m.X, domain=pyo.Binary)

    # (I) cobertura, como igualdade
    def _cobertura(m, d, s):
        termos = [m.x[n, s, d] for n in elegiveis[s]]
        if not termos:
            # turno sem ninguem habilitado. Demanda positiva ja foi barrada acima; aqui so
            # resta o caso de demanda zero, em que a restricao seria 0 == 0.
            return pyo.Constraint.Skip
        return sum(termos) == inst.demanda_de(d, s)

    m.cobertura = pyo.Constraint(dias, turnos, rule=_cobertura)

    # (II) no maximo um turno por profissional por dia
    def _um_turno(m, n, d):
        termos = [m.x[n, s, d] for s in turnos if n in elegiveis[s]]
        return sum(termos) <= 1 if termos else pyo.Constraint.Skip

    m.um_turno_por_dia = pyo.Constraint(tuple(inst.profissionais), dias, rule=_um_turno)

    # Sem restricoes flexiveis ainda: qualquer escala viavel serve.
    m.objetivo = pyo.Objective(expr=0, sense=pyo.minimize)
    return m


# ---------------------------------------------------------------------------
# Resolucao
# ---------------------------------------------------------------------------

def resolver(m: pyo.ConcreteModel, solver: str = SOLVER_PADRAO,
             tempo_limite: int | None = None, log: bool = False):
    """Resolve e devolve o objeto de resultado do Pyomo.

    `tempo_limite` em segundos. A forma de passar a opcao muda entre as interfaces appsi e
    as classicas, entao tentamos as duas.
    """
    opt = pyo.SolverFactory(solver)
    if tempo_limite is not None:
        if hasattr(opt, "config") and hasattr(opt.config, "time_limit"):
            opt.config.time_limit = tempo_limite
        else:
            for chave in ("time_limit", "timelimit", "TimeLimit", "sec"):
                try:
                    opt.options[chave] = tempo_limite
                    break
                except Exception:  # noqa: BLE001 - opcao inexistente no solver
                    continue
    return opt.solve(m, tee=log)


def estado(resultado) -> str:
    """Condicao de termino, em texto, funcionando nas duas familias de interface."""
    for caminho in ("termination_condition", "solver.termination_condition"):
        alvo = resultado
        try:
            for parte in caminho.split("."):
                alvo = getattr(alvo, parte)
            return str(alvo)
        except AttributeError:
            continue
    return str(resultado)


def resolvido(resultado) -> bool:
    return "optimal" in estado(resultado).lower() or "feasible" in estado(resultado).lower()


# ---------------------------------------------------------------------------
# Extracao
# ---------------------------------------------------------------------------

def atribuicoes(m: pyo.ConcreteModel) -> tuple[tuple[date, str, str], ...]:
    """Escala como tuplas (data, profissional, turno), ordenada por data e profissional."""
    escolhidas = []
    for (n, s, d) in m.X:
        valor = pyo.value(m.x[n, s, d], exception=False)
        if valor is not None and valor > 0.5:
            escolhidas.append((d, n, s))
    return tuple(sorted(escolhidas, key=lambda a: (a[0], _chave(a[1]), a[2])))


def _chave(identificador: str):
    """Ordena IDs numericos como numeros: 2 antes de 10."""
    return (0, int(identificador)) if identificador.isdigit() else (1, identificador)


def dimensao(m: pyo.ConcreteModel) -> dict[str, int]:
    """Numero de variaveis e restricoes. Afirmacao de forca media (DECISOES.md 08/09):
    e propriedade da formulacao, nao do algoritmo."""
    return {
        "variaveis": sum(1 for _ in m.component_data_objects(pyo.Var)),
        "restricoes": sum(1 for _ in m.component_data_objects(pyo.Constraint, active=True)),
    }
