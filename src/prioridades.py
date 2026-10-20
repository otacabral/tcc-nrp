"""Prioridades da escala — a funcao objetivo por niveis escolhidos pelo gestor (opcao B).

DECISOES.md, "2026-10-14 — Funcao objetivo por niveis escolhidos pelo gestor (opcao B)" e
"2026-10-19 — Opcao B: mecanismo, tempo e criterios expostos". Este modulo so faz contas sobre
a instancia, sem solver: o catalogo dos criterios, o maximo de violacoes de cada um, o plano de
resolucao (que niveis se fundem num bloco so), a situacao de cada criterio antes de resolver e
o resultado por criterio depois. Quem resolve e `ferramenta.resolver_com_objetivo`.

Como um nivel entra no modelo: cada familia considerada vai para o contrato (ou para os
pedidos, ou para o custo por atribuicao) com peso = coeficiente do seu nivel dentro do bloco.
A funcao objetivo de um bloco e a soma das parcelas das suas familias (`m.parcela`); o
`modelo.py` nao muda. Familia nao considerada fica como estava no contrato — com a
classificacao padrao, o contrato e o XML da instancia nao mudam.
"""

from __future__ import annotations

import dataclasses
import itertools
import math
from collections import Counter
from dataclasses import dataclass

from instancia import Flexivel

ESSENCIAL, IMPORTANTE, DESEJAVEL, NAO = ("Essencial", "Importante", "Desejável",
                                         "Não considerar")
NIVEIS = (ESSENCIAL, IMPORTANTE, DESEJAVEL, NAO)
CONSIDERADOS = (ESSENCIAL, IMPORTANTE, DESEJAVEL)   # de cima para baixo

# Regra de fusao (DECISOES.md, 19/10, item a): niveis vizinhos vao juntos, por coeficiente,
# so se o objetivo maximo do bloco fundido ficar abaixo disto — a condicao de 09/10 para o gap
# padrao do HiGHS (0,01%) provar o otimo inteiro. Lido na chamada: o teste (b) o zera para
# forcar a sequencia.
LIMITE_FUSAO = 10_000

GRUPOS = ("Pedidos e qualificação", "Sequências de trabalho e folga", "Fins de semana",
          "Noturno e carga")

# situacao, calculada antes de resolver
OK, CLT_PREVALECE, NUNCA, GARANTIDO = ("ok", "a CLT prevalece", "nunca será atendido neste "
                                       "regime", "já garantido pela CLT")

PEDIDO, CUSTO = "day_off_requests", "custo_atribuicao"

# Pedidos e regras dos profissionais (DECISOES.md, "2026-10-19 — Pedidos e regras por
# profissional"): a importancia e da LINHA. No plano de niveis, os pedidos de cada nivel sao um
# "criterio" a parte, de id REGRAS + nivel.
FOLGA, SO_TURNO = "Folga", "Só este turno"
TIPOS = (FOLGA, SO_TURNO)
REGRAS = "regras@"
NOME_REGRAS = "Pedidos e regras dos profissionais"
FAMILIAS_PEDIDO = (PEDIDO, "shift_off_requests")


@dataclass(frozen=True)
class Criterio:
    id: str
    grupo: int                   # indice em GRUPOS
    nome: str
    familia: str | None          # familia do modelo; None = linha "ja garantido pela CLT"
    ajuda: str
    limite: int | None = None    # limite padrao, quando ha parametro
    rotulo_limite: str = ""
    nivel: str = NAO             # nivel padrao
    sem_conferencia: bool = False   # sem conferencia externa possivel (i na ajuda)

    @property
    def clt(self) -> bool:
        return self.familia is None


# Limites padrao: contrato 0 do medium_late05; fins de semana em 4 semanas, 2, sem fonte
# (DECISOES.md, 19/10, decisao de implementacao 5).
CRITERIOS = (
    Criterio("pedido_folga", 0, "Pedido de folga no dia", PEDIDO,
             "Folga pedida na tabela de pedidos. Ex.: Ana pediu folga em 20/11 e foi escalada "
             "nesse dia: 1 violação.", nivel=ESSENCIAL),
    Criterio("enf_posto_tec", 0, "Enfermeiro em posto de técnico", CUSTO,
             "Turno em que um enfermeiro cobre vaga de técnico. Ex.: faltam técnicos no sábado "
             "e um enfermeiro cobre: 1 violação.", nivel=IMPORTANTE),
    Criterio("max_dias_seguidos", 1, "Máximo de dias seguidos de trabalho", None,
             "A CLT já limita: no máximo 6 dias seguidos (art. 67); no 12×36, nenhum dia "
             "seguido (36 h de descanso). Preferência mais apertada: trabalho futuro."),
    Criterio("min_dias_seguidos", 1, "Mínimo de dias seguidos de trabalho",
             "min_consecutive_working_days",
             "Evita dia de trabalho isolado. Ex.: com mínimo 3, trabalhar só na terça, entre "
             "folgas, conta 2 violações.", 3, "dias"),
    Criterio("max_folgas_seguidas", 1, "Máximo de folgas seguidas",
             "max_consecutive_free_days",
             "Evita folgas longas demais. Ex.: com máximo 4, seis folgas seguidas contam 2 "
             "violações.", 4, "dias"),
    Criterio("min_folgas_seguidas", 1, "Mínimo de folgas seguidas",
             "min_consecutive_free_days",
             "Evita folga isolada. Ex.: com mínimo 3, uma folga isolada conta 2 violações.",
             3, "dias"),
    Criterio("seq_indesejadas", 1, "Sequências indesejadas", None,
             "As sequências proibidas pelo descanso da CLT (11 h entre turnos, 36 h depois do "
             "plantão de 12 h, folga isolada de 24 h) já são regra rígida."),
    Criterio("max_fds_seguidos", 2, "Máximo de fins de semana seguidos trabalhados",
             "max_consecutive_working_weekends",
             "Ex.: com máximo 3, quatro fins de semana seguidos trabalhados contam 1 violação.",
             3, "fins de semana"),
    Criterio("min_fds_seguidos", 2, "Mínimo de fins de semana seguidos trabalhados",
             "min_consecutive_working_weekends",
             "Evita fim de semana trabalhado isolado. Ex.: com mínimo 2, um fim de semana "
             "trabalhado entre dois livres conta 1 violação.", 2, "fins de semana"),
    Criterio("fds_4_semanas", 2, "Fins de semana trabalhados em 4 semanas",
             "max_working_weekends_in_four_weeks",
             "Ex.: com máximo 2, três fins de semana trabalhados em quatro semanas contam 1 "
             "violação.", 2, "fins de semana", sem_conferencia=True),
    Criterio("fds_completo", 2, "Fim de semana completo", "complete_weekends",
             "Trabalha os dias do fim de semana todos ou nenhum. Ex.: trabalhar só no sábado "
             "conta 1 violação."),
    Criterio("mesmo_turno_fds", 2, "Mesmo turno no fim de semana",
             "identical_shift_types_during_weekend",
             "Quem trabalha no fim de semana faz o mesmo turno em todos os dias dele. Ex.: "
             "diurno no sábado e noturno no domingo contam 2 violações."),
    Criterio("max_turnos", 3, "Máximo de turnos no período", None,
             "A CLT já limita: o teto de horas da carga contratual nos dias disponíveis. "
             "Preferência mais apertada: trabalho futuro."),
    Criterio("min_turnos", 3, "Mínimo de turnos no período", "min_num_assignments",
             "Ex.: com mínimo 10, quem fez 8 turnos conta 2 violações.", 10, "turnos"),
    Criterio("noturno_antes_fds", 3, "Noturno na véspera de fim de semana livre",
             "no_night_shift_before_free_weekend",
             "Ex.: noturno na sexta e o fim de semana livre: 1 violação.",
             sem_conferencia=True),
    Criterio("folgas_apos_noites", 3, "Duas folgas depois de noites",
             "two_free_days_after_night_shifts",
             "Depois de uma sequência de noturnos, dois dias de folga. Ex.: noturno na segunda "
             "e trabalho na quarta: 1 violação.", sem_conferencia=True),
)
POR_ID = {c.id: c for c in CRITERIOS}
CONTRATO = [c for c in CRITERIOS if c.familia not in (None, PEDIDO, CUSTO)]


def padrao() -> dict[str, tuple[str, int | None]]:
    """A classificacao padrao: a ferramenta de antes da opcao B."""
    return {c.id: (c.nivel, c.limite) for c in CRITERIOS if not c.clt}


def normalizar(prioridades: dict | None) -> dict[str, tuple[str, int | None]]:
    p = padrao()
    for k, (nivel, limite) in (prioridades or {}).items():
        if k not in POR_ID or POR_ID[k].clt:
            raise ValueError(f"critério desconhecido ou sem campo: {k}")
        if nivel not in NIVEIS:
            raise ValueError(f"{POR_ID[k].nome}: importância {nivel!r}")
        tem = POR_ID[k].limite is not None
        if tem and (limite is None or int(limite) < 0):
            raise ValueError(f"{POR_ID[k].nome}: limite {limite!r}")
        p[k] = (nivel, int(limite) if tem else None)
    return p


def considerados(p) -> list[Criterio]:
    return [POR_ID[k] for k, (nivel, _) in p.items() if nivel != NAO]


# --- maximo de violacoes (formulas do censo de 19/10; DECISOES.md, 19/10, item a) -------------

def _pior_completo(tam: int) -> int:
    """Fim de semana completo: tam x (blocos) - dias trabalhados, no pior padrao."""
    pior = 0
    for p in itertools.product((0, 1), repeat=tam):
        blocos = sum(1 for k in range(tam) if p[k] and (k == 0 or not p[k - 1]))
        pior = max(pior, tam * blocos - sum(p))
    return pior


def _pior_identico(tam: int, n_turnos: int) -> int:
    """Turnos identicos: soma, por tipo usado, de (tam - dias com aquele tipo)."""
    pior = 0
    for p in itertools.product(range(n_turnos + 1), repeat=tam):   # 0 = folga
        usados = Counter(t for t in p if t)
        pior = max(pior, sum(tam - c for c in usados.values()))
    return pior


FAMILIAS_CONTRATO = ["max_num_assignments", "min_num_assignments",
                     "max_consecutive_working_days", "min_consecutive_working_days",
                     "max_consecutive_free_days", "min_consecutive_free_days",
                     "max_consecutive_working_weekends", "min_consecutive_working_weekends",
                     "max_working_weekends_in_four_weeks", "complete_weekends",
                     "identical_shift_types_during_weekend",
                     "no_night_shift_before_free_weekend",
                     "two_free_days_after_night_shifts", "alternative_skill_category"]


def limite_por_profissional(inst, fam: str, n: str) -> int:
    """Limite SUPERIOR das violacoes (unidades de excesso, peso 1) da familia `fam` para o
    profissional `n`. Valido, nao justo. Fonte unica: o censo de 19/10
    (`docs/diagnostico/censo_flexiveis.py`) chama esta funcao."""
    c = inst.contrato_de(n)
    D = len(inst.dias)
    fds = inst.fins_de_semana(c.id)
    F = len(fds)
    if fam in FAMILIAS_CONTRATO:
        r = getattr(c, fam)
        if not r.ativa:
            return 0
        v = r.valor or 0
        if fam in ("max_num_assignments", "max_consecutive_working_days",
                   "max_consecutive_free_days"):
            return max(0, D - v)
        if fam == "min_num_assignments":
            return min(v, D)
        if fam in ("min_consecutive_working_days", "min_consecutive_free_days"):
            return max(0, v - 1) * math.ceil(D / 2)
        if fam == "max_consecutive_working_weekends":
            return max(0, F - v)
        if fam == "min_consecutive_working_weekends":
            return max(0, v - 1) * math.ceil(F / 2)
        if fam == "max_working_weekends_in_four_weeks":
            return max(0, F - 3) * max(0, 4 - v)
        if fam == "complete_weekends":
            return sum(_pior_completo(len(f.datas)) for f in fds)
        if fam == "identical_shift_types_during_weekend":
            return sum(_pior_identico(len(f.datas), len(inst.turnos)) for f in fds)
        if fam == "no_night_shift_before_free_weekend":
            return F if any(t.noturno for t in inst.turnos.values()) else 0
        if fam == "two_free_days_after_night_shifts":
            return 2 * D if any(t.noturno for t in inst.turnos.values()) else 0
        if fam == "alternative_skill_category":
            tem = inst.profissionais[n].habilidades
            return D if any(not t.habilidades <= tem for t in inst.turnos.values()) else 0
    if fam == "unwanted_patterns":
        total = 0
        for pid in c.padroes_indesejados:
            p = inst.padroes.get(pid)
            if p is None or p.peso <= 0:
                continue
            fixo = p.entradas[0].dia
            total += sum(1 for i, d in enumerate(inst.dias)
                         if i + p.tamanho <= D + (1 if fixo != "Any" else 0)
                         and (fixo == "Any" or d.strftime("%A") == fixo))
        return total
    tipo = {"day_off_requests": "folga_dia", "shift_off_requests": "folga_turno",
            "day_on_requests": "trabalho_dia", "shift_on_requests": "trabalho_turno"}[fam]
    return sum(1 for p in inst.pedidos if p.tipo == tipo and p.profissional == n and p.peso > 0)


def postos_base(inst, habilidade_enf: str) -> list[str]:
    return [s for s, t in inst.turnos.items() if habilidade_enf not in t.habilidades]


def maximo(inst, crit: Criterio, habilidade_enf: str) -> int:
    """Maximo de violacoes do criterio na instancia (com o contrato ja aplicado, peso 1)."""
    if crit.familia == CUSTO:
        # o mesmo maximo da `ferramenta.pesos` de antes: o total de postos de tecnico
        base = postos_base(inst, habilidade_enf)
        return sum(q for (_, s), q in inst.demanda.items() if s in base)
    if crit.familia == PEDIDO:
        return sum(1 for p in inst.pedidos if p.tipo == "folga_dia" and p.nivel is None)
    return sum(limite_por_profissional(inst, crit.familia, n) for n in inst.profissionais)


# --- aplicar a classificacao na instancia -------------------------------------------------------

def aplicar(inst, p, coef: dict[str, int], habilidade_enf: str):
    """A instancia com os criterios considerados no contrato e nos pedidos, cada um com peso =
    `coef[id]`, e o custo por atribuicao. Devolve (instancia, custo). Criterio nao considerado:
    pedidos com peso 0, sem custo, e o contrato como estava."""
    contrato = inst.contratos["0"]
    mudancas = {}
    for c in CONTRATO:
        nivel, limite = p[c.id]
        if nivel != NAO:
            mudancas[c.familia] = Flexivel(presente=True, ligada=True, peso=coef[c.id],
                                           valor=limite)
    if mudancas:
        inst = dataclasses.replace(
            inst, contratos={**inst.contratos, "0": dataclasses.replace(contrato, **mudancas)})
    inst = dataclasses.replace(
        inst, pedidos=tuple(dataclasses.replace(x, peso=peso_do_pedido(x, p, coef))
                            for x in inst.pedidos))
    custo = {}
    if p["enf_posto_tec"][0] != NAO:
        base = postos_base(inst, habilidade_enf)
        enf = [x.id for x in inst.profissionais.values() if habilidade_enf in x.habilidades]
        custo = {(n, s): coef["enf_posto_tec"] for n in enf for s in base}
    return inst, custo


@dataclass
class Bloco:
    niveis: list[str]
    coef: dict[str, int]          # id do criterio -> coeficiente
    maximo: int                   # objetivo maximo do bloco

    @property
    def familias(self) -> list[str]:
        saida = []
        for k in self.coef:
            for f in (FAMILIAS_PEDIDO if k.startswith(REGRAS) else (POR_ID[k].familia,)):
                if f not in saida:
                    saida.append(f)
        return saida


def planejar(inst, p, habilidade_enf: str) -> list[Bloco]:
    """Os blocos de resolucao, de cima (Essencial) para baixo. Regra de fusao: de baixo para
    cima, o nivel de cima entra no bloco com coeficiente (maximo do bloco + 1) se o maximo do
    bloco fundido ficar abaixo de `LIMITE_FUSAO`; senao comeca bloco novo, com coeficiente 1."""
    unidade, _ = aplicar(inst, p, {**{c.id: 1 for c in CRITERIOS},
                                   **{REGRAS + n: 1 for n in CONSIDERADOS}}, habilidade_enf)
    regras = maximo_regras(inst)
    niveis = []
    for nivel in CONSIDERADOS:
        ids = [c.id for c in considerados(p) if p[c.id][0] == nivel]
        u = sum(maximo(unidade, POR_ID[k], habilidade_enf) for k in ids)
        if nivel in regras:          # sem linhas no nivel, nada (nivel vazio nao resolve)
            ids.append(REGRAS + nivel)
            u += regras[nivel]
        if ids:
            niveis.append((nivel, ids, u))
    blocos: list[Bloco] = []
    for nivel, ids, u in reversed(niveis):
        atual = blocos[-1] if blocos else None
        if atual is not None:
            k = atual.maximo + 1
            if k * u + atual.maximo < LIMITE_FUSAO:
                atual.niveis.insert(0, nivel)
                atual.coef = {**{i: k for i in ids}, **atual.coef}
                atual.maximo += k * u
                continue
        blocos.append(Bloco([nivel], {i: 1 for i in ids}, u))
    return list(reversed(blocos))


def coeficientes(blocos: list[Bloco]) -> dict[str, int]:
    return {k: v for b in blocos for k, v in b.coef.items()}


def descrever(blocos: list[Bloco]) -> str:
    if len(blocos) <= 1:
        return "fundido"
    return f"em sequência, {len(blocos)} blocos"


# --- situacao, antes de resolver ----------------------------------------------------------------

def situacoes(inst, p, limite_efetivo: int) -> dict[str, str]:
    """A situacao de cada criterio (DECISOES.md, 19/10, decisao de implementacao 4).
    `limite_efetivo`: maximo de dias seguidos que as regras de descanso admitem."""
    teto_turnos = inst.contratos["0"].max_num_assignments.valor
    fds = inst.fins_de_semana("0")
    dias_fds = {d for f in fds for d in f.datas}
    demanda_fds = any(q > 0 for (d, _), q in inst.demanda.items() if d in dias_fds)
    sem_dia_seguido = (limite_efetivo == 1 and demanda_fds
                       and any(len(f.datas) >= 2 for f in fds))
    saida = {}
    for c in CRITERIOS:
        if c.clt:
            saida[c.id] = GARANTIDO
            continue
        limite = p[c.id][1]
        if c.id == "min_dias_seguidos" and limite is not None and limite > limite_efetivo:
            saida[c.id] = CLT_PREVALECE
        elif (c.id == "min_turnos" and limite is not None and teto_turnos is not None
              and limite > teto_turnos):
            saida[c.id] = CLT_PREVALECE
        elif c.id in ("fds_completo", "mesmo_turno_fds") and sem_dia_seguido:
            saida[c.id] = NUNCA
        else:
            saida[c.id] = OK
    return saida


def explicar(c: Criterio, situacao: str, limite_efetivo: int, teto_turnos) -> str:
    """A frase da situacao, para a ajuda da linha."""
    if situacao == CLT_PREVALECE and c.id == "min_dias_seguidos":
        return (f"A CLT prevalece: as regras de descanso admitem no máximo {limite_efetivo} "
                f"dia(s) seguido(s); o mínimo pedido será violado sempre que alguém trabalhar.")
    if situacao == CLT_PREVALECE and c.id == "min_turnos":
        return (f"A CLT prevalece: o teto legal é {teto_turnos} turnos no período; o mínimo "
                f"pedido não pode ser cumprido.")
    if situacao == NUNCA:
        return ("Nunca será atendido neste regime: ninguém pode trabalhar dois dias seguidos, "
                "então quem trabalha no fim de semana trabalha um dia só.")
    return ""


# --- resultado por criterio, depois de resolver --------------------------------------------------

def resultado(inst, escala, p, habilidade_enf: str) -> list[tuple[str, str, int, int]]:
    """(nivel, criterio, violacoes, profissionais afetados) dos criterios considerados, contados
    na escala, fora do modelo (DECISOES.md, 19/10, decisao de implementacao 6)."""
    from avaliacao import violacoes
    from solucao import noites_antes_de_fim_de_semana_livre_por_pessoa
    trabalhados = {(n, d) for d, n, _ in escala}
    por_familia: dict[str, Counter] = {}
    for v in violacoes(inst, escala):
        por_familia.setdefault(v.restricao, Counter())[v.profissional] += v.excesso
    linhas = []
    for nivel in CONSIDERADOS:
        for c in considerados(p):
            if p[c.id][0] != nivel:
                continue
            if c.familia == PEDIDO:
                quem = Counter(x.profissional for x in inst.pedidos
                               if x.tipo == "folga_dia" and x.nivel is None
                               and (x.profissional, x.data) in trabalhados)
            elif c.familia == CUSTO:
                enf = {x.id for x in inst.profissionais.values()
                       if habilidade_enf in x.habilidades}
                quem = Counter(n for _, n, s in escala if n in enf
                               and habilidade_enf not in inst.turnos[s].habilidades)
            elif c.familia == "no_night_shift_before_free_weekend":
                quem = Counter(noites_antes_de_fim_de_semana_livre_por_pessoa(inst, escala))
            else:
                quem = por_familia.get(c.familia, Counter())
            quem = +quem   # tira os zeros
            linhas.append((nivel, c.nome, sum(quem.values()), len(quem)))
        if any(x.nivel == nivel for x in inst.pedidos):
            quem = Counter(n for nv, n in descumpridos(inst, escala) if nv == nivel)
            linhas.append((nivel, NOME_REGRAS, sum(quem.values()), len(quem)))
    return linhas


# --- pedidos e regras dos profissionais (DECISOES.md, 2026-10-19; esperado em
# resultados/pedidos_2026-10-20/ESPERADO.md) ----------------------------------------------------

@dataclass(frozen=True)
class Linha:
    """Uma linha da tabela "Pedidos e regras dos profissionais". `dia` None = todos os dias;
    `turno` None = o dia todo; `importancia` None = o padrao (`importancia_padrao`)."""
    profissional: str
    dia: object | None
    turno: str | None
    tipo: str = FOLGA
    importancia: str | None = None


def importancia_padrao(linha: Linha) -> str:
    """Folga com dia e sem turno: Essencial (= a v1.3.0); as demais: Desejavel."""
    if linha.tipo == FOLGA and linha.dia is not None and linha.turno is None:
        return ESSENCIAL
    return DESEJAVEL


def _rank(nivel: str) -> int:
    return len(CONSIDERADOS) - CONSIDERADOS.index(nivel)    # Essencial = o mais alto


def traduzir(inst, linhas, habilidade_enf: str, id_de=lambda quem: quem) -> tuple:
    """As linhas da tabela como pedidos NEGATIVOS do INRC (`folga_dia`, `folga_turno`), com o
    nivel de cada um em `Pedido.nivel` e peso 1. Turnos `u` sao os da tela (o posto de tecnico);
    para enfermeiro, u vale tambem pelo posto de enfermeiro (u + "E").

    Por profissional-dia-turno, o nivel e o mais alto entre as linhas que o proibem (uma
    violacao so). "So este turno": por (profissional, dia), os turnos permitidos sao a uniao das
    linhas "So este turno" que valem no dia, no nivel mais alto entre elas. Dia com TODOS os
    turnos proibidos no mesmo nivel vira um `folga_dia` (a unidade de hoje); senao, um
    `folga_turno` por turno proibido. Levanta ValueError com mensagem legivel."""
    from instancia import Pedido
    turnos_tela = [s for s, t in inst.turnos.items() if habilidade_enf not in t.habilidades]
    dias = list(inst.dias)
    proib: dict[tuple, dict[str, str]] = {}      # (n, d) -> {u: nivel}, na ordem de entrada
    so: dict[tuple, tuple[set, str]] = {}         # (n, d) -> (permitidos, nivel)

    def marca(n, d, u, nivel):
        cel = proib.setdefault((n, d), {})
        if u not in cel or _rank(nivel) > _rank(cel[u]):
            cel[u] = nivel

    for k, l in enumerate(linhas, 1):
        quem = f"linha {k} ({l.profissional})"
        if l.tipo not in TIPOS:
            raise ValueError(f"{quem}: tipo {l.tipo!r}; use {' ou '.join(TIPOS)}")
        nivel = l.importancia or importancia_padrao(l)
        if nivel not in CONSIDERADOS:
            raise ValueError(f"{quem}: importância {nivel!r}")
        if l.dia is None and l.turno is None:
            raise ValueError(f"{quem}: informe o dia, o turno ou os dois")
        if l.tipo == SO_TURNO and l.turno is None:
            raise ValueError(f"{quem}: \"{SO_TURNO}\" precisa do turno")
        if l.turno is not None and l.turno not in turnos_tela:
            raise ValueError(f"{quem}: turno {l.turno!r} não existe; use {turnos_tela}")
        if l.dia is not None and l.dia not in dias:
            raise ValueError(f"{quem}: dia {l.dia:%d/%m/%Y} fora do período")
        try:
            n = id_de(l.profissional)
        except (ValueError, KeyError):
            n = None
        if n not in inst.profissionais:
            raise ValueError(f"{quem}: profissional inexistente")
        for d in ([l.dia] if l.dia is not None else dias):
            if l.tipo == FOLGA:
                for u in ([l.turno] if l.turno is not None else turnos_tela):
                    marca(n, d, u, nivel)
            else:
                proib.setdefault((n, d), {})       # guarda a ordem de entrada
                perm, nv = so.get((n, d), (set(), nivel))
                so[(n, d)] = (perm | {l.turno}, max(nv, nivel, key=_rank))
    for (n, d), (perm, nivel) in so.items():
        for u in turnos_tela:
            if u not in perm:
                marca(n, d, u, nivel)
    pedidos = []
    for (n, d), cel in proib.items():
        if not cel:
            continue
        enf = habilidade_enf in inst.profissionais[n].habilidades
        if set(cel) == set(turnos_tela) and len(set(cel.values())) == 1:
            pedidos.append(Pedido(tipo="folga_dia", profissional=n, data=d, peso=1,
                                  nivel=next(iter(cel.values()))))
            continue
        for u in turnos_tela:
            if u not in cel:
                continue
            for s in ((u, f"{u}E") if enf else (u,)):
                if s in inst.turnos:
                    pedidos.append(Pedido(tipo="folga_turno", profissional=n, data=d, peso=1,
                                          turno=s, nivel=cel[u]))
    return tuple(pedidos)


def peso_do_pedido(x, p, coef: dict) -> int:
    """Peso de um pedido: o coeficiente do seu nivel no bloco; 0 se o nivel nao e considerado.
    Pedido sem nivel (caminho antigo): o nivel do criterio "pedido_folga"."""
    if x.nivel is None:
        return coef.get("pedido_folga", 0) if p["pedido_folga"][0] != NAO else 0
    return coef.get(REGRAS + x.nivel, 0) if x.nivel in CONSIDERADOS else 0


def maximo_regras(inst) -> dict[str, int]:
    """Maximo de violacoes dos pedidos da tabela, por nivel: os `folga_dia` do nivel mais os
    pares (profissional, dia) com algum `folga_turno` do nivel (um turno por dia)."""
    saida: dict[str, set] = {}
    for x in inst.pedidos:
        if x.nivel is not None:
            saida.setdefault(x.nivel, set()).add((x.tipo == "folga_dia", x.profissional, x.data))
    return {nv: len(v) for nv, v in saida.items()}


def tem_regras(inst) -> bool:
    return any(x.nivel is not None for x in inst.pedidos)


def expressao_pedidos(m, inst, niveis, p):
    """A parte dos pedidos no objetivo de um bloco em sequencia: so os pedidos dos `niveis` do
    bloco, com o peso ja aplicado (`aplicar`)."""
    termos = []
    for x in inst.pedidos:
        nivel = x.nivel if x.nivel is not None else p["pedido_folga"][0]
        if x.peso <= 0 or nivel not in niveis:
            continue
        if x.tipo == "folga_dia":
            termos.append(x.peso * m.y[x.profissional, x.data])
        elif x.tipo == "folga_turno" and (x.profissional, x.turno, x.data) in m.X:
            termos.append(x.peso * m.x[x.profissional, x.turno, x.data])
    return sum(termos)


def descumpridos(inst, escala) -> list[tuple[str, str]]:
    """(nivel, profissional) de cada pedido da tabela descumprido na escala — uma entrada por
    profissional-dia-turno (ou profissional-dia, no `folga_dia`)."""
    feito = {(n, d): s for d, n, s in escala}
    saida = []
    for x in inst.pedidos:
        if x.nivel is None:
            continue
        s = feito.get((x.profissional, x.data))
        if s is not None and (x.tipo == "folga_dia" or s == x.turno):
            saida.append((x.nivel, x.profissional))
    return saida
