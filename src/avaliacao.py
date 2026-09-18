"""Penalidade de uma escala, calculada em Python puro — sem Pyomo e sem Java.

Duas funcoes no projeto:

1. **Oraculo de semantica.** As 13 flexiveis sao escritas aqui primeiro e conferidas contra o
   avaliador oficial, violacao por violacao e profissional por profissional, em escalas
   quaisquer. Sem solver no meio: erro de semantica aparece isolado de erro de modelagem.
   Depois a funcao objetivo do Pyomo codifica a mesma semantica, e o teste dela passa a ser
   "o valor do modelo bate com o daqui na propria solucao do modelo".

2. **Insumo do Experimento B.** O experimento compara a distribuicao da penalidade entre
   profissionais — maxima individual, amplitude, dispersao. O modelo devolve o total; a
   decomposicao por profissional sai daqui.

Convencoes seguidas, todas da documentacao oficial (secao 2.2.3 e apendice A):
`custo = excesso x peso`, e restricao so conta se estiver ativa pela regra de 15/09
(`DECISOES.md`).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from instancia import Instancia


@dataclass(frozen=True)
class Violacao:
    profissional: str
    restricao: str   # chave interna, igual ao atributo em Contrato quando houver
    excesso: int
    peso: int
    detalhe: str = ""

    @property
    def custo(self) -> int:
        return self.excesso * self.peso


# ---------------------------------------------------------------------------
# Utilidades sobre a escala
# ---------------------------------------------------------------------------

def _por_profissional(inst: Instancia, escala) -> dict[str, dict[date, str]]:
    agenda: dict[str, dict[date, str]] = {n: {} for n in inst.profissionais}
    for (d, n, s) in escala:
        agenda[n][d] = s
    return agenda


def _blocos(marcados: list[bool]) -> list[tuple[int, int]]:
    """Blocos maximos de True. Devolve (inicio, tamanho)."""
    blocos, ini = [], None
    for i, v in enumerate(marcados):
        if v and ini is None:
            ini = i
        elif not v and ini is not None:
            blocos.append((ini, i - ini)); ini = None
    if ini is not None:
        blocos.append((ini, len(marcados) - ini))
    return blocos


# ---------------------------------------------------------------------------
# As restricoes, uma funcao cada
# ---------------------------------------------------------------------------

def _num_atribuicoes(inst, n, dias_trabalhados, contrato):
    total = len(dias_trabalhados)
    r = contrato.max_num_assignments
    if r.ativa and total > r.valor:
        yield Violacao(n, "max_num_assignments", total - r.valor, r.peso)
    r = contrato.min_num_assignments
    if r.ativa and total < r.valor:
        yield Violacao(n, "min_num_assignments", r.valor - total, r.peso)


def _dias_consecutivos(inst, n, trabalha, contrato):
    """Blocos de dias trabalhados seguidos."""
    for _, tamanho in _blocos(trabalha):
        r = contrato.max_consecutive_working_days
        if r.ativa and tamanho > r.valor:
            yield Violacao(n, "max_consecutive_working_days", tamanho - r.valor, r.peso)
        r = contrato.min_consecutive_working_days
        if r.ativa and tamanho < r.valor:
            yield Violacao(n, "min_consecutive_working_days", r.valor - tamanho, r.peso)


def _folgas_consecutivas(inst, n, trabalha, contrato):
    """Blocos de folga. Os blocos nas pontas do horizonte contam: a documentacao trata o
    intervalo como distancia entre eventos, com um evento virtual antes do inicio e outro
    depois do fim (secao 2.2.3, 'Maximum and minimum number of consecutive free days')."""
    for _, tamanho in _blocos([not t for t in trabalha]):
        r = contrato.max_consecutive_free_days
        if r.ativa and tamanho > r.valor:
            yield Violacao(n, "max_consecutive_free_days", tamanho - r.valor, r.peso)
        r = contrato.min_consecutive_free_days
        if r.ativa and 0 < tamanho < r.valor:
            yield Violacao(n, "min_consecutive_free_days", r.valor - tamanho, r.peso)


def _fins_de_semana(inst, n, agenda, contrato):
    fds = inst.fins_de_semana(contrato.id)
    trabalhados = [any(d in agenda for d in f.datas) for f in fds]

    for _, tamanho in _blocos(trabalhados):
        r = contrato.max_consecutive_working_weekends
        if r.ativa and tamanho > r.valor:
            yield Violacao(n, "max_consecutive_working_weekends", tamanho - r.valor, r.peso)
        r = contrato.min_consecutive_working_weekends
        if r.ativa and tamanho < r.valor:
            yield Violacao(n, "min_consecutive_working_weekends", r.valor - tamanho, r.peso)

    for f, trabalhou in zip(fds, trabalhados):
        if not trabalhou:
            continue
        # fim de semana completo: blocos de dias trabalhados dentro do fim de semana, cada um
        # comparado ao tamanho do fim de semana. Trabalhar em dias nao contiguos penaliza mais
        # (documentacao, secao 2.2.3, exemplo X 0 X).
        r = contrato.complete_weekends
        if r.ativa:
            dentro = [d in agenda for d in f.datas]
            for _, tamanho in _blocos(dentro):
                if tamanho < len(f.datas):
                    yield Violacao(n, "complete_weekends", len(f.datas) - tamanho, r.peso,
                                   f"fds {f.indice}")
        # turnos identicos: para cada tipo de turno usado no fim de semana, exige-se que ele
        # cubra todos os dias do fim de semana
        r = contrato.identical_shift_types_during_weekend
        if r.ativa:
            usados = defaultdict(int)
            for d in f.datas:
                if d in agenda:
                    usados[agenda[d]] += 1
            for turno, quantas in usados.items():
                if quantas < len(f.datas):
                    yield Violacao(n, "identical_shift_types_during_weekend",
                                   len(f.datas) - quantas, r.peso, f"fds {f.indice} {turno}")


def _noite_antes_de_fds_livre(inst, n, agenda, contrato):
    """NAO PONTUA. O avaliador oficial nao avalia esta restricao.

    Verificado em 2026-09-18 no codigo do `evaluator.jar`: `NO_NIGHT_FREE` e lido pelo
    parser, guardado no contrato e reescrito na saida, mas **nenhuma condicao o le**. A
    classe `ScheduleEvaluator` da numeracao instancia treze condicoes, e nao ha nenhuma para
    esta. Confirmado empiricamente: o rotulo "No night shift before free weekend" nunca
    aparece na saida detalhada, em nenhuma instancia, nem quando a restricao esta ligada com
    peso 10 e a escala tem a situacao que ela penalizaria.

    Consequencia para o modelo: implementa-la faria o valor divergir do avaliador em 44 das
    69 instancias, inclusive em `medium_late05`, que e alvo de validacao. Fica implementada
    aqui como funcao vazia, documentada, e nao entra na funcao objetivo.

    A restricao segue existindo no problema real, e vale para a instancia brasileira — onde
    nao ha avaliador para contradizer. Ver DECISOES.md.
    """
    return
    yield  # pragma: no cover - mantem a assinatura de gerador


def _folgas_apos_noites(inst, n, agenda, contrato):
    """Duas folgas depois de uma sequencia de noites. O elemento do XML e booleano, sem
    parametro: a documentacao fixa o numero em duas (secao 2.2.3, Tabela 7). Nenhuma
    instancia do INRC usa esta restricao — implementada sem conferencia externa possivel
    (DECISOES.md, escopo de 15/09)."""
    r = contrato.two_free_days_after_night_shifts
    if not r.ativa:
        return
    noturnos = {s for s, t in inst.turnos.items() if t.noturno}
    dias = inst.dias
    for i, d in enumerate(dias):
        if agenda.get(d) not in noturnos:
            continue
        if i + 1 < len(dias) and agenda.get(dias[i + 1]) in noturnos:
            continue  # ainda dentro da sequencia de noites
        for j in (i + 1, i + 2):
            if j < len(dias) and dias[j] in agenda:
                yield Violacao(n, "two_free_days_after_night_shifts", 1, r.peso)


def _habilidade(inst, n, agenda, contrato):
    r = contrato.alternative_skill_category
    if not r.ativa:
        return
    tem = inst.profissionais[n].habilidades
    for d, s in agenda.items():
        if not inst.turnos[s].habilidades <= tem:
            yield Violacao(n, "alternative_skill_category", 1, r.peso, f"{d} {s}")


def _padroes(inst, n, agenda, contrato):
    """Padroes indesejados.

    O avaliador nao faz casamento literal: cada forma de padrao vira uma numeracao com uma
    regra propria (`PatternConditionBuilder`). Nos dados do INRC existem tres formas, e duas
    regras distintas — verificado em 2026-09-18 varrendo as 69 instancias:

    | Forma | Exemplo | Ocorrencias |
    |---|---|---|
    | `ST-ST` e `ST-ST-ST`, dia Any | `L@Any-D@Any` | 311 |
    | `F-W-W`, dia fixo | `None@Friday-Any@Saturday-Any@Sunday` | 57 |

    Para as de turno especifico, `buildSTSTST_Any` numera os dias do padrao em sequencia e
    usa `max_consecutive = tamanho - 1`: penaliza uma vez cada casamento completo. Casamento
    literal reproduz isso.

    Para a de dia fixo, `buildFWW_Fixed` numera o dia fixo com 3, os dias seguintes com 4, e
    usa `max_between = 2` com evento virtual 0 antes do periodo. O resultado e mais frouxo
    que o casamento literal: penaliza quando a pessoa esta livre no dia fixo e trabalha em
    **pelo menos um** dos dias seguintes, nao nos dois. Uma vez por semana.
    """
    dias = inst.dias
    for pid in contrato.padroes_indesejados:
        padrao = inst.padroes.get(pid)
        if padrao is None or padrao.peso <= 0:
            continue
        primeira = padrao.entradas[0]
        seguintes = padrao.entradas[1:]

        if primeira.turno == "None" and primeira.dia != "Any" and all(
                e.turno == "Any" for e in seguintes):
            for i, d in enumerate(dias):
                if d.strftime("%A") != primeira.dia or i + len(seguintes) >= len(dias) + 1:
                    continue
                if d in agenda:
                    continue  # trabalhou no dia fixo: nao ha violacao
                janela = [dias[i + k] for k in range(1, padrao.tamanho) if i + k < len(dias)]
                if any(dia in agenda for dia in janela):
                    yield Violacao(n, "unwanted_patterns", 1, padrao.peso,
                                   f"padrao {pid} {d}")
            continue

        for i in range(len(dias) - padrao.tamanho + 1):
            casa = True
            for k, entrada in enumerate(padrao.entradas):
                d = dias[i + k]
                if entrada.dia != "Any" and d.strftime("%A") != entrada.dia:
                    casa = False; break
                turno = agenda.get(d)
                if entrada.turno == "None":
                    if turno is not None:
                        casa = False; break
                elif entrada.turno == "Any":
                    if turno is None:
                        casa = False; break
                elif turno != entrada.turno:
                    casa = False; break
            if casa:
                yield Violacao(n, "unwanted_patterns", 1, padrao.peso, f"padrao {pid} dia {i}")


def _pedidos(inst, n, agenda):
    for p in inst.pedidos:
        if p.profissional != n or p.peso <= 0:
            continue
        trabalhou = p.data in agenda
        if p.tipo == "folga_dia" and trabalhou:
            yield Violacao(n, "day_off_requests", 1, p.peso, str(p.data))
        elif p.tipo == "folga_turno" and agenda.get(p.data) == p.turno:
            yield Violacao(n, "shift_off_requests", 1, p.peso, str(p.data))
        elif p.tipo == "trabalho_dia" and not trabalhou:
            yield Violacao(n, "day_on_requests", 1, p.peso, str(p.data))
        elif p.tipo == "trabalho_turno" and agenda.get(p.data) != p.turno:
            yield Violacao(n, "shift_on_requests", 1, p.peso, str(p.data))


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

def violacoes(inst: Instancia, escala) -> list[Violacao]:
    """Todas as violacoes de restricao flexivel da escala."""
    agenda = _por_profissional(inst, escala)
    saida: list[Violacao] = []
    for n, dias_trabalhados in agenda.items():
        contrato = inst.contrato_de(n)
        trabalha = [d in dias_trabalhados for d in inst.dias]
        saida += list(_num_atribuicoes(inst, n, dias_trabalhados, contrato))
        saida += list(_dias_consecutivos(inst, n, trabalha, contrato))
        saida += list(_folgas_consecutivas(inst, n, trabalha, contrato))
        saida += list(_fins_de_semana(inst, n, dias_trabalhados, contrato))
        saida += list(_noite_antes_de_fds_livre(inst, n, dias_trabalhados, contrato))
        saida += list(_folgas_apos_noites(inst, n, dias_trabalhados, contrato))
        saida += list(_habilidade(inst, n, dias_trabalhados, contrato))
        saida += list(_padroes(inst, n, dias_trabalhados, contrato))
        saida += list(_pedidos(inst, n, dias_trabalhados))
    return saida


def penalidade(inst: Instancia, escala) -> int:
    return sum(v.custo for v in violacoes(inst, escala))


def por_profissional(inst: Instancia, escala) -> dict[str, int]:
    """Penalidade de cada profissional. Base do Experimento B."""
    total = {n: 0 for n in inst.profissionais}
    for v in violacoes(inst, escala):
        total[v.profissional] += v.custo
    return total


def por_restricao(inst: Instancia, escala) -> dict[str, int]:
    total: dict[str, int] = defaultdict(int)
    for v in violacoes(inst, escala):
        total[v.restricao] += v.custo
    return dict(total)
