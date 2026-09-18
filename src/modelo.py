"""Instancia -> modelo Pyomo.

Fronteira (PLANO.md): este modulo consome apenas `Instancia`, nunca XML.

Duas rigidas (documentacao oficial, 2.2.1) e as flexiveis de Santos et al. (2016), na
codificacao por atribuicao `x[n,s,d]` decidida em 08/09.

A semantica das flexiveis nao foi inventada aqui: ela esta fixada em `src/avaliacao.py`, que
calcula a penalidade de uma escala em Python puro e foi conferido contra o avaliador oficial
em 207 escalas nas 69 instancias, par a par de profissional x restricao. Este modulo so
lineariza aquela semantica. Quando os dois divergirem, o erro esta aqui.

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

def construir(inst: Instancia, flexiveis: bool = True, habilidade_rigida: bool = False,
              noite_antes_de_fds_livre: bool = False) -> pyo.ConcreteModel:
    """Monta o modelo.

    `flexiveis=False` da o modelo minimo, so com as duas rigidas e funcao objetivo nula —
    util para conferir viabilidade e para o Experimento A, que e pergunta de viabilidade.

    `habilidade_rigida=True` restringe o dominio: profissional so cobre turno cuja habilidade
    tem. **O padrao e False**, que reproduz a formulacao de referencia — Santos et al. (2016)
    penalizam a habilidade no coeficiente da variavel de atribuicao, e o avaliador oficial nao
    trata habilidade como rigida em lugar nenhum. A versao rigida fica para a instancia
    brasileira. Ver PROPOSTAS.md, P3, **ainda nao validada**: se for recusada, inverter aqui.

    `noite_antes_de_fds_livre=True` liga a restricao que o avaliador oficial nao pontua. Fica
    desligada nas instancias do INRC, sob pena de divergir em 44 delas, e ligada na instancia
    brasileira. Ver DECISOES.md, 18/09.
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

    m.X = pyo.Set(initialize=[(n, s, d) for s in turnos for n in elegiveis[s] for d in dias],
                  dimen=3)
    m.x = pyo.Var(m.X, domain=pyo.Binary)

    # (I) cobertura, como igualdade, inclusive onde a demanda nao e declarada
    def _cobertura(m, d, s):
        termos = [m.x[n, s, d] for n in elegiveis[s]]
        if not termos:
            return pyo.Constraint.Skip
        return sum(termos) == inst.demanda_de(d, s)

    m.cobertura = pyo.Constraint(dias, turnos, rule=_cobertura)

    # (II) no maximo um turno por profissional por dia
    def _um_turno(m, n, d):
        termos = [m.x[n, s, d] for s in turnos if n in elegiveis[s]]
        return sum(termos) <= 1 if termos else pyo.Constraint.Skip

    m.um_turno_por_dia = pyo.Constraint(tuple(inst.profissionais), dias, rule=_um_turno)

    # y[n,d] = trabalha no dia d
    m.y = pyo.Var(tuple(inst.profissionais), dias, domain=pyo.Binary)

    def _liga_y(m, n, d):
        termos = [m.x[n, s, d] for s in turnos if n in elegiveis[s]]
        return m.y[n, d] == sum(termos) if termos else m.y[n, d] == 0

    m.definicao_y = pyo.Constraint(tuple(inst.profissionais), dias, rule=_liga_y)

    if flexiveis:
        _adicionar_flexiveis(m, inst, elegiveis, habilidade_rigida,
                             noite_antes_de_fds_livre)
    else:
        m.objetivo = pyo.Objective(expr=0, sense=pyo.minimize)
    return m


# ---------------------------------------------------------------------------
# Restricoes flexiveis
# ---------------------------------------------------------------------------

def _adicionar_flexiveis(m, inst: Instancia, elegiveis, habilidade_rigida,
                         com_noite_antes_de_fds) -> None:
    dias = inst.dias
    nd = len(dias)
    profissionais = tuple(inst.profissionais)
    # a funcao objetivo e montada por familia de restricao, e cada familia vira uma
    # Expression propria. Isso permite comparar o modelo com avaliacao.py restricao por
    # restricao quando os dois divergirem, e alimenta a decomposicao do Experimento B.
    parcelas: dict[str, list] = {}
    restricoes = []      # expressoes auxiliares
    folgas = {}          # nome -> (familia, coef, expressao do limite inferior)

    contador = [0]

    def somar(familia, expr):
        parcelas.setdefault(familia, []).append(expr)

    def nova_folga(familia, coef, *limites):
        """Cria UMA folga, penalizada por coef, maior ou igual a cada limite dado. Como
        coef > 0 e o problema e de minimizacao, ela assume o maior dos limites.

        Varios limites para uma folga so nao e detalhe: e a diferenca entre penalizar uma
        vez e penalizar uma vez por limite. O padrao de dia fixo (livre na sexta, trabalha
        no fim de semana) e uma violacao por semana, nao uma por dia trabalhado."""
        contador[0] += 1
        nome = f"{familia}__{contador[0]}"
        folgas[nome] = (familia, coef, list(limites))
        return nome

    # --- por profissional
    for n in profissionais:
        c = inst.contrato_de(n)
        y = [m.y[n, dias[i]] for i in range(nd)]

        # numero de atribuicoes
        r = c.max_num_assignments
        if r.ativa:
            nova_folga("max_num_assignments", r.peso, sum(y) - r.valor)
        r = c.min_num_assignments
        if r.ativa:
            nova_folga("min_num_assignments", r.peso, r.valor - sum(y))

        # dias consecutivos de trabalho: janela deslizante de tamanho limite+1
        r = c.max_consecutive_working_days
        if r.ativa and r.valor < nd:
            L = r.valor
            for i in range(nd - L):
                nova_folga("max_consecutive_working_days", r.peso, sum(y[i:i + L + 1]) - L)

        # minimo de dias consecutivos: um indicador por (inicio, tamanho de bloco curto).
        # Bloco de tamanho R comeca em t se y[t-1]=0, y[t..t+R-1]=1 e y[t+R]=0. Fora do
        # horizonte vale 0 — bloco encostado na borda conta, como em avaliacao.py.
        r = c.min_consecutive_working_days
        if r.ativa:
            for R in range(1, r.valor):
                for t in range(0, nd - R + 1):
                    antes = (1 - y[t - 1]) if t > 0 else 1
                    depois = (1 - y[t + R]) if t + R < nd else 1
                    nova_folga("min_consecutive_working_days", r.peso * (r.valor - R),
                               sum(y[t:t + R]) + antes + depois - (R + 1))

        # folgas consecutivas: mesma estrutura com (1 - y). Nas bordas o dia virtual e de
        # trabalho, o que faz bloco de folga encostado na borda contar.
        r = c.max_consecutive_free_days
        if r.ativa and r.valor < nd:
            L = r.valor
            for i in range(nd - L):
                nova_folga("max_consecutive_free_days", r.peso, sum(1 - v for v in y[i:i + L + 1]) - L)
        r = c.min_consecutive_free_days
        if r.ativa:
            for R in range(1, r.valor):
                for t in range(0, nd - R + 1):
                    antes = y[t - 1] if t > 0 else 1
                    depois = y[t + R] if t + R < nd else 1
                    nova_folga("min_consecutive_free_days", r.peso * (r.valor - R),
                               sum(1 - v for v in y[t:t + R]) + antes + depois - (R + 1))

        # --- fins de semana
        fds = inst.fins_de_semana(c.id)
        precisa_wk = (c.max_consecutive_working_weekends.ativa
                      or c.min_consecutive_working_weekends.ativa
                      or com_noite_antes_de_fds and c.no_night_shift_before_free_weekend.ativa)
        wk = {}
        if precisa_wk:
            for f in fds:
                v = pyo.Var(domain=pyo.Binary)
                m.add_component(f"wk_{n}_{f.indice}", v)
                wk[f.indice] = v
                for d in f.datas:
                    restricoes.append(v >= m.y[n, d])
                restricoes.append(v <= sum(m.y[n, d] for d in f.datas))

        r = c.max_consecutive_working_weekends
        if r.ativa and r.valor < len(fds):
            L = r.valor
            for i in range(len(fds) - L):
                nova_folga("max_consecutive_working_weekends", r.peso, sum(wk[j] for j in range(i, i + L + 1)) - L)
        r = c.min_consecutive_working_weekends
        if r.ativa:
            nw = len(fds)
            for R in range(1, r.valor):
                for t in range(0, nw - R + 1):
                    antes = (1 - wk[t - 1]) if t > 0 else 1
                    depois = (1 - wk[t + R]) if t + R < nw else 1
                    nova_folga("min_consecutive_working_weekends", r.peso * (r.valor - R),
                               sum(wk[j] for j in range(t, t + R)) + antes + depois - (R + 1))

        # fim de semana completo: penalidade = |W| x (numero de blocos) - dias trabalhados
        r = c.complete_weekends
        if r.ativa:
            for f in fds:
                tam = len(f.datas)
                inicios = []
                for k, d in enumerate(f.datas):
                    b = pyo.Var(domain=pyo.NonNegativeReals)
                    m.add_component(f"cw_{n}_{f.indice}_{k}", b)
                    anterior = m.y[n, f.datas[k - 1]] if k > 0 else 0
                    restricoes.append(b >= m.y[n, d] - anterior)
                    inicios.append(b)
                somar("complete_weekends", r.peso * (tam * sum(inicios)
                                              - sum(m.y[n, d] for d in f.datas)))

        # turnos identicos no fim de semana: por tipo de turno usado, exige-se cobrir todos
        # os dias do fim de semana
        r = c.identical_shift_types_during_weekend
        if r.ativa:
            for f in fds:
                tam = len(f.datas)
                for s in inst.turnos:
                    if n not in elegiveis[s]:
                        continue
                    usados = [m.x[n, s, d] for d in f.datas]
                    u = pyo.Var(domain=pyo.NonNegativeReals, bounds=(0, 1))
                    m.add_component(f"id_{n}_{f.indice}_{s}", u)
                    for v in usados:
                        restricoes.append(u >= v)
                    somar("identical_shift_types_during_weekend", r.peso * (tam * u - sum(usados)))

        # turno noturno antes de fim de semana livre: fora da objetivo por padrao
        r = c.no_night_shift_before_free_weekend
        if com_noite_antes_de_fds and r.ativa:
            noturnos = [s for s, t in inst.turnos.items() if t.noturno and n in elegiveis[s]]
            for f in fds:
                vespera = f.datas[0] - __import__("datetime").timedelta(days=1)
                if vespera < inst.inicio or not noturnos:
                    continue
                noite = sum(m.x[n, s, vespera] for s in noturnos)
                nova_folga("no_night_shift_before_free_weekend", r.peso, noite - wk[f.indice])

        # habilidade alternativa: coeficiente na variavel de atribuicao
        r = c.alternative_skill_category
        if r.ativa and not habilidade_rigida:
            tem = inst.profissionais[n].habilidades
            for s in inst.turnos:
                if inst.turnos[s].habilidades <= tem or n not in elegiveis[s]:
                    continue
                for d in dias:
                    somar("alternative_skill_category", r.peso * m.x[n, s, d])

        # padroes indesejados
        for pid in c.padroes_indesejados:
            padrao = inst.padroes.get(pid)
            if padrao is None or padrao.peso <= 0:
                continue
            primeira = padrao.entradas[0]
            seguintes = padrao.entradas[1:]
            if primeira.turno == "None" and primeira.dia != "Any" and all(
                    e.turno == "Any" for e in seguintes):
                # livre no dia fixo e trabalhando em pelo menos um dos seguintes
                for i, d in enumerate(dias):
                    if d.strftime("%A") != primeira.dia:
                        continue
                    limites = [m.y[n, dias[i + k]] - m.y[n, d]
                               for k in range(1, padrao.tamanho) if i + k < nd]
                    if limites:
                        nova_folga("unwanted_patterns", padrao.peso, *limites)
                continue
            for i in range(nd - padrao.tamanho + 1):
                casamento, casa = [], True
                for k, entrada in enumerate(padrao.entradas):
                    d = dias[i + k]
                    if entrada.dia != "Any" and d.strftime("%A") != entrada.dia:
                        casa = False; break
                    if entrada.turno == "None":
                        casamento.append(1 - m.y[n, d])
                    elif entrada.turno == "Any":
                        casamento.append(m.y[n, d])
                    elif n in elegiveis[entrada.turno]:
                        casamento.append(m.x[n, entrada.turno, d])
                    else:
                        casa = False; break
                if casa and casamento:
                    nova_folga("unwanted_patterns", padrao.peso, sum(casamento) - (len(casamento) - 1))

    # --- pedidos individuais
    for p in inst.pedidos:
        if p.peso <= 0:
            continue
        if p.tipo == "folga_dia":
            somar("day_off_requests", p.peso * m.y[p.profissional, p.data])
        elif p.tipo == "folga_turno" and p.profissional in elegiveis.get(p.turno, ()):
            somar("shift_off_requests", p.peso * m.x[p.profissional, p.turno, p.data])
        elif p.tipo == "trabalho_dia":
            somar("day_on_requests", p.peso * (1 - m.y[p.profissional, p.data]))
        elif p.tipo == "trabalho_turno" and p.profissional in elegiveis.get(p.turno, ()):
            somar("shift_on_requests", p.peso * (1 - m.x[p.profissional, p.turno, p.data]))

    # --- materializa folgas e restricoes
    m.folga = pyo.Var(list(folgas), domain=pyo.NonNegativeReals)
    m.limite_folga = pyo.ConstraintList()
    for nome, (familia, coef, limites) in folgas.items():
        for limite in limites:
            m.limite_folga.add(m.folga[nome] >= limite)
        somar(familia, coef * m.folga[nome])
    m.auxiliares = pyo.ConstraintList()
    for expr in restricoes:
        m.auxiliares.add(expr)

    familias = sorted(parcelas)
    m.parcela = pyo.Expression(familias, rule=lambda m, f: sum(parcelas[f]))
    m.objetivo = pyo.Objective(expr=sum(m.parcela[f] for f in familias), sense=pyo.minimize)


# ---------------------------------------------------------------------------
# Resolucao
# ---------------------------------------------------------------------------

def resolver(m: pyo.ConcreteModel, solver: str = SOLVER_PADRAO,
             tempo_limite: int | None = None, log: bool = False):
    """Resolve e devolve o objeto de resultado do Pyomo."""
    opt = pyo.SolverFactory(solver)
    if tempo_limite is not None:
        if hasattr(opt, "config") and hasattr(opt.config, "time_limit"):
            opt.config.time_limit = tempo_limite
        else:
            for chave in ("time_limit", "timelimit", "TimeLimit", "sec"):
                try:
                    opt.options[chave] = tempo_limite
                    break
                except Exception:  # noqa: BLE001
                    continue
    return opt.solve(m, tee=log)


def estado(resultado) -> str:
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
    e = estado(resultado).lower()
    return "optimal" in e or "feasible" in e


# ---------------------------------------------------------------------------
# Extracao
# ---------------------------------------------------------------------------

def atribuicoes(m: pyo.ConcreteModel) -> tuple[tuple[date, str, str], ...]:
    escolhidas = []
    for (n, s, d) in m.X:
        valor = pyo.value(m.x[n, s, d], exception=False)
        if valor is not None and valor > 0.5:
            escolhidas.append((d, n, s))
    return tuple(sorted(escolhidas, key=lambda a: (a[0], _chave(a[1]), a[2])))


def valor_objetivo(m: pyo.ConcreteModel) -> int:
    return int(round(pyo.value(m.objetivo)))


def _chave(identificador: str):
    return (0, int(identificador)) if identificador.isdigit() else (1, identificador)


def dimensao(m: pyo.ConcreteModel) -> dict[str, int]:
    """Numero de variaveis e restricoes. Afirmacao de forca media (DECISOES.md 08/09)."""
    return {
        "variaveis": sum(1 for _ in m.component_data_objects(pyo.Var)),
        "restricoes": sum(1 for _ in m.component_data_objects(pyo.Constraint, active=True)),
    }


# ---------------------------------------------------------------------------
# Linha de comando
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    from pathlib import Path

    from avaliacao import penalidade
    from parser import ler_instancia
    from solucao import conferir_rigidas, escrever_xml

    raiz = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description="Resolve o modelo.")
    ap.add_argument("instancia")
    ap.add_argument("--solver", default=SOLVER_PADRAO)
    ap.add_argument("--tempo", type=int, default=None, help="limite em segundos")
    ap.add_argument("--saida", default=None)
    ap.add_argument("--minimo", action="store_true",
                    help="so as duas rigidas, sem funcao objetivo")
    ap.add_argument("--habilidade-rigida", action="store_true",
                    help="profissional so cobre turno cuja habilidade tem")
    ap.add_argument("--log", action="store_true")
    args = ap.parse_args()

    inst = ler_instancia(args.instancia)
    print(inst.resumo())

    m = construir(inst, flexiveis=not args.minimo,
                  habilidade_rigida=args.habilidade_rigida)
    d = dimensao(m)
    print(f"modelo {'minimo' if args.minimo else 'completo'}: {d['variaveis']} variaveis, "
          f"{d['restricoes']} restricoes")

    resultado = resolver(m, solver=args.solver, tempo_limite=args.tempo, log=args.log)
    print(f"solver {args.solver}: {estado(resultado)}")
    if not resolvido(resultado):
        print("[FALHA] nenhuma escala viavel obtida")
        return 1

    escala = atribuicoes(m)
    problemas = conferir_rigidas(inst, escala, habilidade_rigida=args.habilidade_rigida)
    print(f"escala com {len(escala)} atribuicoes; rigidas: "
          + ("OK" if not problemas else f"{len(problemas)} problema(s) {problemas[:3]}"))
    if problemas:
        return 1

    if not args.minimo:
        do_modelo, do_python = valor_objetivo(m), penalidade(inst, escala)
        bate = do_modelo == do_python
        print(f"objetivo do modelo: {do_modelo} | avaliacao.py: {do_python} | "
              + ("OK" if bate else "DIVERGEM"))
        if not bate:
            return 1

    destino = Path(args.saida) if args.saida else (
        raiz / "resultados" / f"{inst.id}{'_minimo' if args.minimo else ''}.xml")
    escrever_xml(inst, escala, destino,
                 penalidade=0 if args.minimo else valor_objetivo(m), validar=True)
    print(f"solucao escrita e validada: {destino}")
    print(f"proximo passo: python src\\validar.py {args.instancia} {destino}"
          + ("" if args.minimo else f" --objetivo {valor_objetivo(m)}"))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
