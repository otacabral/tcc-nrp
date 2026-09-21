"""Gerador da instancia brasileira, a partir do Parecer Normativo COFEN no 1/2024.

Fronteira: este modulo produz `Instancia` e XML no esquema oficial. Nao conhece Pyomo.
`modelo.py` consome a `Instancia` resultante sem saber que ela nao veio de arquivo.

O PRIMITIVO e o perfil assistencial horario continuo — horas de enfermagem por hora do
horizonte —, NUNCA blocos de 8 h ou de 12 h. Os dois regimes sao emitidos do mesmo perfil,
pela mesma regra de reagregacao. Montar o perfil "por turno" faria o regime daquele tamanho
nascer com residuo zero de graca, e a assimetria entre os bracos voltaria embutida no
primitivo, invisivel no resultado. Ver PROPOSTAS.md, P5 revisao 3, "Armadilha no gerador".

Parametros do Parecer (secoes 2.8 e 3.0), ja extraidos e conferidos na fonte primaria pelo
projeto de redacao em 21/09. Nao reinterpretar a norma aqui:

| Grau de dependencia | Horas / paciente / 24 h | % enfermeiros | % tecnicos |
|---|---|---|---|
| Minimo          |  4 | 33% (minimo que garanta 1 por turno) | 67% |
| Intermediario   |  6 | 33% (minimo que garanta 1 por turno) | 67% |
| Alta dependencia| 10 | 36% | 64% |
| Semi-intensivo  | 10 | 42% | 58% |
| Intensivo       | 18 | 52% | 48% |

O percentual vale para o QUADRO TOTAL em cobertura de 24 h, nao por turno. A proporcao
profissional/paciente por turno era da Resolucao 543/2017, revogada — nao usar.

Porte: 5.920 horas-profissional em 28 dias = 211,43 h/dia, o mesmo invariante da P4 e o
porte do long01. Perfil uniforme nas 24 h, porque o Parecer da horas por paciente em 24 h
sem curva horaria: 211,43 / 24 = 8,81 profissionais presentes em qualquer hora.

Quadro de referencia do Experimento A, sem IST: QP_ref = 211,43 x 7 / 42 = 35,24. A formula
do Parecer (QP = THE x DS x (1 + IST) / CHS) nao depende de regime de jornada — da o mesmo
quadro para 8 h e para 12x36 na mesma carga semanal. E justamente isso que o Experimento A
poe a prova.

Uso:

    python src\\instancia_br.py --grau intermediario --efetivo 36
    python src\\instancia_br.py --conferencia          # so as conferencias, sem emitir

Fora de escopo, declarado (item 9 da decisao de 21/09): IST de 15%, 5% de educacao
permanente, enfermeiros para atividades gerenciais e acrescimo de 10% por restricao de
atividade. Sao fatores de dimensionamento, fora do horizonte de escalonamento, e o IST e
multiplicativo igual nos dois regimes — nao altera a comparacao relativa.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from datetime import date, time, timedelta
from pathlib import Path

from lxml import etree

from instancia import (
    DIAS_SEMANA,
    Contrato,
    Flexivel,
    Instancia,
    Padrao,
    EntradaPadrao,
    Profissional,
    Turno,
)

RAIZ = Path(__file__).resolve().parents[1]
XSD_ENTRADA = RAIZ / "docs" / "scheme_input.xsd"

PORTE_HORAS = 5920.0      # invariante da P4: o porte do long01
DIAS_HORIZONTE = 28
CARGA_SEMANAL = 42.0      # h/semana nos dois regimes
CORTE = 7                 # janelas alinhadas as 07:00; o horizonte COMECA no corte

HABILIDADE_BASE = "Enfermagem"    # todo profissional tem
HABILIDADE_ENF = "Enfermeiro"     # so o enfermeiro tem


@dataclass(frozen=True)
class Grau:
    """Uma linha da tabela do Parecer."""

    nome: str
    horas_paciente_24h: float
    pct_enfermeiros: float
    piso_enfermeiro_por_janela: int   # 1 onde o Parecer exige 1 por turno; 0 caso contrario


GRAUS = {
    g.nome: g for g in (
        Grau("minimo", 4, 0.33, 1),
        Grau("intermediario", 6, 0.33, 1),
        Grau("alta", 10, 0.36, 0),
        Grau("semi_intensivo", 10, 0.42, 0),
        Grau("intensivo", 18, 0.52, 0),
    )
}

# (id, hora de inicio, duracao em horas, descricao)
REGIMES = {
    "8h": (("M", 7, 8, "Manha"), ("T", 15, 8, "Tarde"), ("N", 23, 8, "Noite")),
    "12x36": (("D", 7, 12, "Diurno"), ("N", 19, 12, "Noturno")),
}

# Maximo de plantoes em 28 dias que respeita 42 h/semana (item 4 da decisao de 21/09)
MAX_ATRIBUICOES = {"8h": 21, "12x36": 14}


# --- o primitivo ----------------------------------------------------------------------

def perfil_continuo(porte_horas: float = PORTE_HORAS,
                    dias: int = DIAS_HORIZONTE) -> dict[int, float]:
    """Profissionais presentes em cada hora do horizonte.

    A hora 0 e o CORTE do primeiro dia, nao a meia-noite: o horizonte comeca as 07:00 e
    termina as 07:00 do dia seguinte ao ultimo, de modo que as janelas de 8 h e as de 12 h
    fecham exatamente, sem fatia parcial nas pontas (P5, revisao 1).

    Derivado da necessidade assistencial em 24 h, hora a hora — nunca de blocos. O Parecer
    nao fornece curva horaria, entao a necessidade e uniforme; o que NAO se faz e declara-la
    ja repartida em turnos, que e o vicio descrito no cabecalho.
    """
    por_hora = porte_horas / dias / 24
    return {h: por_hora for h in range(dias * 24)}


def pacientes(grau: Grau, porte_horas: float = PORTE_HORAS,
              dias: int = DIAS_HORIZONTE) -> float:
    """Pacientes implicitos no porte, dado o grau. E resultado, nao parametro.

    Manter o porte fixo em todos os graus (item 5 da decisao de 21/09) significa que a
    unidade representada muda de tamanho conforme o grau: 52,9 pacientes no minimo contra
    11,7 no intensivo. O numero nunca entra no modelo — a escala so ve horas e composicao —,
    mas precisa ser declarado no texto para o leitor saber o que a instancia representa.
    """
    return porte_horas / dias / grau.horas_paciente_24h


# --- reagregacao ----------------------------------------------------------------------

def reagregar(perfil: dict[int, float], duracao: int, regra: str = "teto") -> dict[int, int]:
    """Perfil continuo -> profissionais exigidos por janela disjunta de `duracao` horas.

    `regra`: "teto" nunca subserve; "maior_resto" preserva o total do horizonte (metodo de
    Hamilton). As duas sao emitidas como instancias separadas: sao as pontas do intervalo
    que o Experimento A reporta. Ver PROPOSTAS.md, P5.
    """
    exato = janelas_exatas(perfil, duracao)
    if regra == "teto":
        return {j: math.ceil(v) for j, v in exato.items()}
    if regra == "maior_resto":
        return _maior_resto(exato)
    raise ValueError(f"regra desconhecida: {regra}")


def _maior_resto(exato: dict[int, float]) -> dict[int, int]:
    """Metodo de Hamilton, com o empate desfeito por espalhamento.

    Com perfil uniforme TODAS as janelas tem a mesma parte fracionaria, entao o maior resto
    nao tem criterio proprio para escolher quem recebe o bloco extra. Desempatar por indice
    concentraria os arredondamentos para cima no comeco do horizonte e deixaria os ultimos
    onze dias subdimensionados — artefato visivel, e indefensavel numa instancia publicada.
    O empate e desfeito espalhando os extras uniformemente (regra de Bresenham).
    """
    piso = {j: math.floor(v) for j, v in exato.items()}
    faltam = round(sum(exato.values())) - sum(piso.values())
    tiers: dict[float, list[int]] = {}
    for j, v in exato.items():
        tiers.setdefault(round(v - piso[j], 9), []).append(j)
    for frac in sorted(tiers, reverse=True):
        if faltam <= 0:
            break
        janelas = sorted(tiers[frac])
        k = min(faltam, len(janelas))
        # k janelas uniformemente espalhadas entre as len(janelas) do mesmo patamar
        escolhidas = [janelas[i] for i in range(len(janelas))
                      if ((i + 1) * k) // len(janelas) > (i * k) // len(janelas)]
        for j in escolhidas:
            piso[j] += 1
        faltam -= len(escolhidas)
    return piso


def janelas_exatas(perfil: dict[int, float], duracao: int) -> dict[int, float]:
    """Profissionais exigidos por janela, sem arredondar.

    A hora 0 do perfil ja e o corte, entao as janelas saem alinhadas e completas.
    """
    total: dict[int, float] = {}
    for h, v in perfil.items():
        j = h // duracao
        total[j] = total.get(j, 0.0) + v
    return {j: v / duracao for j, v in total.items()}


def horas(janelas: dict[int, int | float], duracao: int) -> float:
    return sum(janelas.values()) * duracao


# --- conferencias ---------------------------------------------------------------------

def conferir_perfil(perfil: dict[int, float]) -> list[str]:
    """Conferencia anti-tautologia (PLANO.md, semana 4).

    Reagrega o perfil nos DOIS tamanhos de janela. Se algum der residuo zero, o primitivo
    foi construido naquele tamanho e o braco correspondente ganharia vantagem de graca.
    E o que acontece nas 4 instancias de controle do INRC, que foram declaradas em tres
    turnos que particionam o dia.
    """
    erros = []
    for duracao in (8, 12):
        exato = janelas_exatas(perfil, duracao)
        residuo = sum(math.ceil(v) - v for v in exato.values())
        if residuo < 1e-9:
            erros.append(
                f"residuo nulo em janelas de {duracao} h: o perfil foi construido nesse "
                f"tamanho, e o regime de {duracao} h nasceria com vantagem artificial"
            )
    return erros


def conferir_porte(perfil: dict[int, float], porte_horas: float = PORTE_HORAS) -> list[str]:
    """O perfil entrega o porte declarado?"""
    entregue = sum(perfil.values())
    if abs(entregue - porte_horas) > 1e-6:
        return [f"perfil entrega {entregue:.2f} h, porte declarado {porte_horas:.2f} h"]
    return []


def conferir_par(perfil: dict[int, float], duracao: int,
                 porte_horas: float = PORTE_HORAS) -> list[str]:
    """As duas instancias de um regime saem do mesmo perfil e diferem so na regra.

    Tolerancia de um bloco por categoria: a igualdade exata e impossivel quando o porte nao
    e divisivel pela duracao da janela (5.920 / 12 = 493,33 blocos). Ver P5.
    """
    erros = []
    h_teto = horas(reagregar(perfil, duracao, regra="teto"), duracao)
    h_mr = horas(reagregar(perfil, duracao, regra="maior_resto"), duracao)
    if abs(h_mr - porte_horas) > duracao + 1e-6:
        erros.append(f"maior resto em {duracao} h entrega {h_mr:.0f} h, "
                     f"fora da tolerancia de um bloco em torno de {porte_horas:.0f} h")
    if h_teto < porte_horas - 1e-6:
        erros.append(f"teto em {duracao} h entrega {h_teto:.0f} h, abaixo do porte")
    return erros


def conferir_descanso(regime: str, descanso_clt: bool = True) -> tuple[float, list[str]]:
    """Menor intervalo entre o fim de um turno e o inicio do proximo, entre as sequencias
    que o contrato admite. Confere que as regras de descanso codificadas de fato valem.

    Enumera todos os pares (turno no dia d, turno no dia d+k) para k = 1 e 2, descarta os
    proibidos por MaxConsecutiveWorkingDays e pelos padroes indesejados, e mede o intervalo.
    O k = 2 com o dia do meio livre e o caso do descanso semanal: no regime de 8 h e ele que
    tem de dar pelo menos 24 h (CLT art. 67), aproximado por no maximo 6 dias seguidos.
    """
    turnos = {tid: (ini, ini + dur) for tid, ini, dur, _ in REGIMES[regime]}
    max_consec = 1 if regime == "12x36" else 6
    proibidos = set()
    if regime == "12x36":
        proibidos.add(("N", 2, "D"))
    elif descanso_clt:
        proibidos |= {("N", 1, "M"), ("N", 1, "T"), ("T", 1, "M")}

    menor, linhas = float("inf"), []
    for k in (1, 2):
        if k == 1 and max_consec < 2:
            linhas.append(f"   k=1: proibido por MaxConsecutiveWorkingDays = {max_consec}")
            continue
        for a, (_, fim_a) in turnos.items():
            for b, (ini_b, _) in turnos.items():
                if (a, k, b) in proibidos:
                    continue
                intervalo = (k * 24 + ini_b) - fim_a
                linhas.append(f"   {a} dia d -> {b} dia d+{k}: {intervalo:2.0f} h")
                menor = min(menor, intervalo)
    return menor, linhas


# --- montagem da Instancia ------------------------------------------------------------

def _flex(valor=None, ligada=True, peso=1) -> Flexivel:
    return Flexivel(presente=True, ligada=ligada, peso=peso, valor=valor)


def _turnos(regime: str, grau: Grau) -> dict[str, Turno]:
    """Um turno generico por janela, mais um turno de enfermeiro onde o Parecer exige 1.

    Leitura literal do Parecer (item 8 da decisao de 21/09): o percentual se aplica ao
    QUADRO, nao a cobertura da janela. Entao a composicao vive na lista de profissionais, e
    a cobertura so carrega o piso de 1 enfermeiro por janela onde a norma o preve.
    """
    turnos = {}
    for tid, inicio, duracao, desc in REGIMES[regime]:
        fim = (inicio + duracao) % 24
        turnos[tid] = Turno(id=tid, inicio=time(inicio), fim=time(fim),
                            descricao=desc, habilidades=frozenset({HABILIDADE_BASE}))
        if grau.piso_enfermeiro_por_janela:
            turnos[f"{tid}E"] = Turno(id=f"{tid}E", inicio=time(inicio), fim=time(fim),
                                      descricao=f"{desc} (enfermeiro)",
                                      habilidades=frozenset({HABILIDADE_ENF}))
    return turnos


def _contrato(regime: str, descanso_clt: bool) -> Contrato:
    """Contrato unico do regime. Os limites legais entram como flexiveis do esquema.

    ATENCAO: no formato do INRC toda restricao de contrato e flexivel. Para o Experimento A,
    o teto de 42 h/semana e o descanso precisam BINDAR, senao "minimo viavel" vira divisao.
    A rigidez e opcao do modelo (`modelo.py`), nao do arquivo — assim a instancia emitida
    continua sendo uma instancia normal do INRC, reutilizavel por terceiros. Ver P7.
    """
    padroes = ("clt_36h_N_D",) if regime == "12x36" else ()
    if regime == "8h" and descanso_clt:
        padroes = ("clt_N_M", "clt_N_T", "clt_T_M")
    return Contrato(
        id="0",
        descricao=f"regime {regime}, 42h/semana",
        weekend_definition="SaturdaySunday",
        padroes_indesejados=padroes,
        single_assignment_per_day=_flex(),
        max_num_assignments=_flex(MAX_ATRIBUICOES[regime]),
        min_num_assignments=_flex(0, ligada=False, peso=0),
        max_consecutive_working_days=_flex(1 if regime == "12x36" else 6),
        min_consecutive_working_days=_flex(1),
        max_consecutive_free_days=_flex(DIAS_HORIZONTE, ligada=False, peso=0),
        min_consecutive_free_days=_flex(1),
        max_consecutive_working_weekends=_flex(0, ligada=False, peso=0),
        min_consecutive_working_weekends=_flex(0, ligada=False, peso=0),
        max_working_weekends_in_four_weeks=_flex(0, ligada=False, peso=0),
        complete_weekends=_flex(ligada=False, peso=0),
        identical_shift_types_during_weekend=_flex(ligada=False, peso=0),
        no_night_shift_before_free_weekend=_flex(ligada=False, peso=0),
        two_free_days_after_night_shifts=_flex(ligada=False, peso=0),
        alternative_skill_category=_flex(ligada=False, peso=0),
    )


def _padroes(regime: str, descanso_clt: bool) -> dict[str, Padrao]:
    """Sequencias proibidas pelas regras de descanso.

    Janelas 07-15 (M), 15-23 (T) e 23-07 (N). Os tres pares com menos de 11 h de intervalo:

    | sequencia | fim | inicio seguinte | intervalo |
    |---|---|---|---|
    | N -> M | 07:00 | 07:00 do mesmo dia |  0 h |
    | N -> T | 07:00 | 15:00 do mesmo dia |  8 h |
    | T -> M | 23:00 | 07:00 do dia seguinte |  8 h |

    N -> N (16 h), T -> T (16 h) e M -> qualquer (>= 16 h) passam. Sem essas proibicoes o
    braco de 8 h ganha liberdade que o 12x36 nao tem (item 7 da decisao de 21/09).

    O descanso semanal de 24 h consecutivas (CLT art. 67) fica aproximado por
    MaxConsecutiveWorkingDays = 6: um dia livre a cada sete garante ao menos 24 h entre o
    fim de um turno e o inicio do proximo, em qualquer combinacao admitida acima. E
    aproximacao declarada, nao equivalencia.
    """
    if regime == "12x36":
        # As 36 h do art. 59-A nao sao garantidas por MaxConsecutiveWorkingDays = 1. O
        # plantao noturno termina as 07:00 do dia seguinte; com o dia do meio livre, o
        # plantao diurno de dois dias depois comeca as 07:00 — sao 24 h, nao 36. Unica
        # combinacao com o furo; diurno->diurno da 36 h e noturno->noturno da 60 h. P7.2.
        return {"clt_36h_N_D": Padrao(
            id="clt_36h_N_D", peso=1,
            entradas=(EntradaPadrao("N", "Any"), EntradaPadrao("None", "Any"),
                      EntradaPadrao("D", "Any")))}
    if not descanso_clt:
        return {}
    pares = (("N", "M"), ("N", "T"), ("T", "M"))
    return {
        f"clt_{a}_{b}": Padrao(id=f"clt_{a}_{b}", peso=1,
                               entradas=(EntradaPadrao(a, "Any"), EntradaPadrao(b, "Any")))
        for a, b in pares
    }


def _profissionais(efetivo: int, grau: Grau) -> tuple[dict[str, Profissional], int]:
    """Composicao no QUADRO, como o Parecer manda: n_enf >= pct x efetivo."""
    n_enf = math.ceil(grau.pct_enfermeiros * efetivo)
    profs = {}
    for i in range(efetivo):
        enfermeiro = i < n_enf
        habs = {HABILIDADE_BASE} | ({HABILIDADE_ENF} if enfermeiro else set())
        profs[str(i)] = Profissional(id=str(i), nome=f"{'ENF' if enfermeiro else 'TEC'}{i}",
                                     contrato="0", habilidades=frozenset(habs))
    return profs, n_enf


def _demanda(janelas: dict[int, int], regime: str, grau: Grau,
             inicio: date, dias: int) -> dict[tuple[date, str], int]:
    """Cobertura por (dia, turno), a partir das janelas reagregadas.

    A janela j do regime pertence ao dia `inicio + j // janelas_por_dia`. O piso de
    enfermeiro sai do total generico: 9 na janela viram 1 no turno de enfermeiro e 8 no
    generico, o que exprime "9 profissionais, ao menos 1 enfermeiro".
    """
    por_dia = 24 // REGIMES[regime][0][2]
    ids = [t[0] for t in REGIMES[regime]]
    demanda: dict[tuple[date, str], int] = {}
    for j, total in sorted(janelas.items()):
        if j < 0 or j >= dias * por_dia:
            continue
        dia = inicio + timedelta(days=j // por_dia)
        tid = ids[j % por_dia]
        piso = min(grau.piso_enfermeiro_por_janela, total)
        if piso:
            demanda[(dia, f"{tid}E")] = piso
        demanda[(dia, tid)] = total - piso
    return demanda


def construir(grau: str = "intermediario", efetivo: int = 36, regime: str = "12x36",
              regra: str = "teto", porte_horas: float = PORTE_HORAS,
              dias: int = DIAS_HORIZONTE, inicio: date | None = None,
              descanso_clt: bool = True) -> Instancia:
    """Monta a instancia brasileira. Todos os parametros sao varridos nos experimentos."""
    g = GRAUS[grau]
    inicio = inicio or primeira_segunda()
    if inicio.weekday() != 0:
        raise ValueError("o horizonte comeca numa segunda-feira, para fechar 4 fins de semana")
    perfil = perfil_continuo(porte_horas, dias)
    duracao = REGIMES[regime][0][2]
    janelas = reagregar(perfil, duracao, regra=regra)
    profs, _ = _profissionais(efetivo, g)
    return Instancia(
        id=f"br_{grau}_{regime}_{regra}_e{efetivo}",
        arquivo="",
        inicio=inicio,
        fim=inicio + timedelta(days=dias - 1),
        habilidades=(HABILIDADE_BASE, HABILIDADE_ENF),
        turnos=_turnos(regime, g),
        padroes=_padroes(regime, descanso_clt),
        contratos={"0": _contrato(regime, descanso_clt)},
        profissionais=profs,
        demanda=_demanda(janelas, regime, g, inicio, dias),
        pedidos=(),
    )


def primeira_segunda(ano: int = 2027) -> date:
    d = date(ano, 1, 1)
    return d + timedelta(days=(7 - d.weekday()) % 7)


def quadro_referencia(porte_horas: float = PORTE_HORAS, dias: int = DIAS_HORIZONTE,
                      carga_semanal: float = CARGA_SEMANAL) -> float:
    """QP_ref do Parecer, sem IST. E o denominador do Experimento A."""
    return porte_horas / dias * 7 / carga_semanal


# --- serializacao ---------------------------------------------------------------------

def _sub(pai, tag, texto=None, **attrs):
    e = etree.SubElement(pai, tag, {k: str(v) for k, v in attrs.items()})
    if texto is not None:
        e.text = str(texto)
    return e


def escrever_xml(inst: Instancia, caminho: Path | str) -> Path:
    """Serializa no esquema oficial de entrada."""
    raiz = etree.Element("SchedulingPeriod", ID=inst.id, nsmap={
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"})
    raiz.set("{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation",
             "competition.xsd")
    _sub(raiz, "StartDate", inst.inicio.isoformat())
    _sub(raiz, "EndDate", inst.fim.isoformat())
    hab = _sub(raiz, "Skills")
    for h in inst.habilidades:
        _sub(hab, "Skill", h)

    tipos = _sub(raiz, "ShiftTypes")
    for t in inst.turnos.values():
        s = _sub(tipos, "Shift", ID=t.id)
        _sub(s, "StartTime", t.inicio.strftime("%H:%M:%S"))
        _sub(s, "EndTime", t.fim.strftime("%H:%M:%S"))
        _sub(s, "Description", t.descricao)
        hs = _sub(s, "Skills")
        for h in sorted(t.habilidades):
            _sub(hs, "Skill", h)

    if inst.padroes:
        pats = _sub(raiz, "Patterns")
        for p in inst.padroes.values():
            el = _sub(pats, "Pattern", ID=p.id, weight=p.peso)
            ent = _sub(el, "PatternEntries")
            for i, e in enumerate(p.entradas):
                pe = _sub(ent, "PatternEntry", index=i)
                _sub(pe, "ShiftType", e.turno)
                _sub(pe, "Day", e.dia)

    cs = _sub(raiz, "Contracts")
    for c in inst.contratos.values():
        el = _sub(cs, "Contract", ID=c.id)
        _sub(el, "Description", c.descricao)
        _sub(el, "SingleAssignmentPerDay", "true",
             weight=c.single_assignment_per_day.peso)
        for tag, campo in (("MaxNumAssignments", c.max_num_assignments),
                           ("MinNumAssignments", c.min_num_assignments),
                           ("MaxConsecutiveWorkingDays", c.max_consecutive_working_days),
                           ("MinConsecutiveWorkingDays", c.min_consecutive_working_days),
                           ("MaxConsecutiveFreeDays", c.max_consecutive_free_days),
                           ("MinConsecutiveFreeDays", c.min_consecutive_free_days),
                           ("MaxConsecutiveWorkingWeekends",
                            c.max_consecutive_working_weekends),
                           ("MinConsecutiveWorkingWeekends",
                            c.min_consecutive_working_weekends),
                           ("MaxWorkingWeekendsInFourWeeks",
                            c.max_working_weekends_in_four_weeks)):
            _sub(el, tag, campo.valor or 0,
                 on=1 if campo.ligada else 0, weight=campo.peso)
        _sub(el, "WeekendDefinition", c.weekend_definition)
        for tag, campo in (("CompleteWeekends", c.complete_weekends),
                           ("IdenticalShiftTypesDuringWeekend",
                            c.identical_shift_types_during_weekend),
                           ("NoNightShiftBeforeFreeWeekend",
                            c.no_night_shift_before_free_weekend),
                           ("AlternativeSkillCategory", c.alternative_skill_category)):
            _sub(el, tag, "true" if campo.ligada else "false", weight=campo.peso)
        if c.padroes_indesejados:
            up = _sub(el, "UnwantedPatterns")
            for pid in c.padroes_indesejados:
                _sub(up, "Pattern", pid)

    es = _sub(raiz, "Employees")
    for p in inst.profissionais.values():
        el = _sub(es, "Employee", ID=p.id)
        _sub(el, "ContractID", p.contrato)
        _sub(el, "Name", p.nome)
        hs = _sub(el, "Skills")
        for h in sorted(p.habilidades):
            _sub(hs, "Skill", h)

    cov = _sub(raiz, "CoverRequirements")
    por_dia = {d: {t: q for (dd, t), q in inst.demanda.items() if dd == d and q > 0}
               for d in inst.dias}
    for w in range(7):
        datas = [d for d in inst.dias if d.weekday() == w]
        if not datas:
            continue
        perfis = {tuple(sorted(por_dia[d].items())) for d in datas}
        if len(perfis) == 1:
            # a demanda se repete em todas as ocorrencias deste dia da semana
            dw = _sub(cov, "DayOfWeekCover")
            _sub(dw, "Day", DIAS_SEMANA[w])
            for tid, q in sorted(por_dia[datas[0]].items()):
                c = _sub(dw, "Cover")
                _sub(c, "Shift", tid)
                _sub(c, "Preferred", q)
        else:
            # perfil nao periodico: cada data por si, que tem precedencia no esquema
            for d in datas:
                ds = _sub(cov, "DateSpecificCover")
                _sub(ds, "Date", d.isoformat())
                for tid, q in sorted(por_dia[d].items()):
                    c = _sub(ds, "Cover")
                    _sub(c, "Shift", tid)
                    _sub(c, "Preferred", q)

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    etree.ElementTree(raiz).write(str(caminho), pretty_print=True,
                                  xml_declaration=True, encoding="utf-8")
    return caminho


def validar_xsd(caminho: Path | str) -> list[str]:
    """Valida contra docs/scheme_input.xsd. Lista vazia = valido."""
    esquema = etree.XMLSchema(etree.parse(str(XSD_ENTRADA)))
    doc = etree.parse(str(caminho))
    if esquema.validate(doc):
        return []
    return [f"l{e.line}: {e.message}" for e in esquema.error_log]


# --- linha de comando -----------------------------------------------------------------

def relatorio_conferencias() -> int:
    perfil = perfil_continuo()
    print(f"porte           {sum(perfil.values()):.2f} h em {DIAS_HORIZONTE} dias "
          f"= {PORTE_HORAS / DIAS_HORIZONTE:.2f} h/dia")
    print(f"perfil uniforme {perfil[0]:.4f} profissionais presentes em qualquer hora")
    print(f"QP_ref          {quadro_referencia():.2f} profissionais "
          f"(Parecer, sem IST, {CARGA_SEMANAL:.0f} h/semana)")
    print()
    erros = conferir_porte(perfil) + conferir_perfil(perfil)
    for duracao in (8, 12):
        erros += conferir_par(perfil, duracao)
        exato = janelas_exatas(perfil, duracao)
        for regra in ("teto", "maior_resto"):
            jan = reagregar(perfil, duracao, regra=regra)
            h = horas(jan, duracao)
            blocos = sum(jan.values())
            cap = MAX_ATRIBUICOES["8h" if duracao == 8 else "12x36"]
            v = sorted(jan.values())
            print(f"janelas de {duracao:2d} h, {regra:12s}: exato {list(exato.values())[0]:.4f} "
                  f"-> {min(v)}..{max(v)} por janela | {h:.0f} h "
                  f"({(h / PORTE_HORAS - 1) * 100:+.2f}%) | {blocos} blocos | "
                  f"piso por capacidade {blocos / cap:.2f}")
        print()
    print("descanso minimo admitido pelo contrato:")
    for regime in sorted(REGIMES):
        menor, linhas = conferir_descanso(regime)
        exigido = 36 if regime == "12x36" else 11
        marca = "OK" if menor >= exigido - 1e-9 else "REPROVOU"
        print(f"   {regime:6s} menor intervalo {menor:.0f} h | exigido {exigido} h | {marca}")
        for l in linhas:
            print(f"   {l}")
        if menor < exigido:
            erros.append(f"{regime}: descanso minimo {menor:.0f} h, exigido {exigido} h")
    print()
    print("pacientes implicitos e composicao (efetivo 36):")
    for nome, g in GRAUS.items():
        print(f"   {nome:15s} {pacientes(g):5.1f} pacientes | "
              f"enfermeiros >= {g.pct_enfermeiros:.0%} = {math.ceil(g.pct_enfermeiros * 36):2d}"
              f" | piso por janela {g.piso_enfermeiro_por_janela}")
    print()
    if erros:
        print("CONFERENCIAS REPROVARAM:")
        for e in erros:
            print(f"   {e}")
        return 1
    print("conferencias OK: porte, anti-tautologia e tolerancia de um bloco")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grau", default="intermediario", choices=sorted(GRAUS))
    ap.add_argument("--efetivo", type=int, default=36)
    ap.add_argument("--regime", default="12x36", choices=sorted(REGIMES))
    ap.add_argument("--regra", default="teto", choices=("teto", "maior_resto"))
    ap.add_argument("--sem-descanso-clt", action="store_true",
                    help="desliga as sequencias proibidas pela interjornada de 11 h")
    ap.add_argument("--saida", default="instancias/br")
    ap.add_argument("--conferencia", action="store_true",
                    help="so roda as conferencias do perfil e sai")
    a = ap.parse_args()

    if a.conferencia:
        return relatorio_conferencias()

    inst = construir(grau=a.grau, efetivo=a.efetivo, regime=a.regime, regra=a.regra,
                     descanso_clt=not a.sem_descanso_clt)
    destino = Path(a.saida) / f"{inst.id}.xml"
    escrever_xml(inst, destino)
    erros = validar_xsd(destino)
    print(f"{destino}: {inst.demanda_total} atribuicoes, "
          f"{len(inst.profissionais)} profissionais, {len(inst.turnos)} turnos")
    if erros:
        print("XML INVALIDO no esquema:")
        for e in erros[:5]:
            print(f"   {e}")
        return 1
    print("XML valido no esquema oficial")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
