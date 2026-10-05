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
    python src\\instancia_br.py --pacientes intermediario=30 --enfermeiros 13 --tecnicos 25 \\
        --razao-fds 0.7                               # as entradas da ferramenta

Fora de escopo, declarado (item 9 da decisao de 21/09): IST de 15%, 5% de educacao
permanente, enfermeiros para atividades gerenciais e acrescimo de 10% por restricao de
atividade. Sao fatores de dimensionamento, fora do horizonte de escalonamento, e o IST e
multiplicativo igual nos dois regimes — nao altera a comparacao relativa.
"""

from __future__ import annotations

import argparse
import dataclasses
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
    Pedido,
    Profissional,
    Turno,
)

RAIZ = Path(__file__).resolve().parents[1]
XSD_ENTRADA = RAIZ / "docs" / "scheme_input.xsd"

PORTE_HORAS = 5920.0      # invariante da P4: o porte do long01
DIAS_HORIZONTE = 28
CARGA_SEMANAL = 42.0      # h/semana nos dois regimes — caminho dos experimentos e do QP
# Caminho de turnos configurados (DECISOES.md, "2026-10-02 — Carga por contrato"): cada
# profissional tem a sua carga contratual. Padrao 44 h, o limite da CF (art. 7o, XIII).
CARGA_CONTRATUAL_PADRAO = 44.0
CARGAS_CONTRATUAIS = (30.0, 36.0, 40.0, 44.0)
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

# Maximo de dias seguidos de trabalho, por regime: a alternancia do 12x36 e o descanso semanal
# (art. 67, aproximado por 6 dias) no de 8 h. FONTE UNICA para o contrato, para o gerador de
# regras de descanso e para a conferencia das sequencias.
MAX_CONSECUTIVOS = {"8h": 6, "12x36": 1}

# Regras de descanso da CLT, em horas. FONTE UNICA: o gerador de pares proibidos, a conferencia
# das sequencias e a medicao na escala pronta saem daqui.
INTERJORNADA = 11      # art. 66
POS_TURNO_LONGO = 36   # art. 59-A: doze horas seguidas por trinta e seis de descanso
TURNO_LONGO = 12       # a partir de quantas horas de turno vale o descanso de 36 h


def descanso_exigido(duracao_h: float) -> int:
    """Descanso minimo depois de um turno desta duracao. Escrever 36 h para turno de 8 h
    reprova escala legal — foi o que a conferencia fez em 23/09."""
    return POS_TURNO_LONGO if duracao_h >= TURNO_LONGO else INTERJORNADA


# Descanso minimo por regime, derivado da regra acima (nao e segunda lista).
DESCANSO_EXIGIDO = {r: descanso_exigido(REGIMES[r][0][2]) for r in REGIMES}


# --- o primitivo ----------------------------------------------------------------------

# Forma da variacao entre dias, MEDIDA no long01 em 23/09: 29 atribuicoes em cada dia util e
# 20 em cada dia de fim de semana, 20 x 29 + 8 x 20 = 740 exatamente. Nao e amplitude
# arbitraria — e a mesma logica de "calibrado ao porte" que ja governa o nivel, estendida do
# nivel para a FORMA. Decisao do projeto de redacao, 23/09.
FORMA_LONG01 = {"util": 29, "fim_de_semana": 20}


def fatores_por_dia(dias: int, inicio: date, variacao: float) -> list[float]:
    """Multiplicador de cada dia do horizonte. Media ponderada exatamente 1.

    `variacao` interpola entre o perfil plano e a forma do `long01`: 0 e plano, 1 e a forma
    medida inteira, valores no meio sao a mesma forma atenuada. A media dar 1 e o que mantem
    o NIVEL em 211,4 h/dia enquanto so a forma muda — sem isso a varredura mudaria duas
    coisas ao mesmo tempo e nao mediria nenhuma.
    """
    du = sum(1 for d in range(dias) if (inicio + timedelta(days=d)).weekday() < 5)
    df = dias - du
    media = (du * FORMA_LONG01["util"] + df * FORMA_LONG01["fim_de_semana"]) / dias
    alvo = {True: FORMA_LONG01["util"] / media, False: FORMA_LONG01["fim_de_semana"] / media}
    return [1 + variacao * (alvo[(inicio + timedelta(days=d)).weekday() < 5] - 1)
            for d in range(dias)]


def fatores_por_razao(dias: int, inicio: date, razao_fds: float) -> list[float]:
    """Multiplicador de cada dia, dada a razao demanda do fim de semana / demanda do dia util.

    E a entrada da ferramenta (DECISOES.md, 29/09): `razao_fds` vai de 0 a 1 — 1 e demanda
    igual em todos os dias, 0 e fim de semana sem demanda. Media ponderada exatamente 1, pela
    mesma razao de `fatores_por_dia`: o total de horas e preservado e so a forma muda.

    `razao_fds = 20/29` e a forma do `long01`, a mesma que `fatores_por_dia` com
    `variacao = 1`. Valores intermediarios NAO coincidem com `variacao` intermediaria: aqui a
    razao e o parametro, la e a interpolacao entre plano e `long01`. `variacao` fica porque
    e com ela que as rodadas do Experimento A foram feitas e se reproduzem.
    """
    if not 0 <= razao_fds <= 1:
        raise ValueError(f"razao fim de semana / dia util fora de [0, 1]: {razao_fds}")
    du = sum(1 for d in range(dias) if (inicio + timedelta(days=d)).weekday() < 5)
    df = dias - du
    util = dias / (du + razao_fds * df)
    return [util if (inicio + timedelta(days=d)).weekday() < 5 else razao_fds * util
            for d in range(dias)]


def perfil_continuo(porte_horas: float = PORTE_HORAS, dias: int = DIAS_HORIZONTE,
                    variacao: float = 0.0, inicio: date | None = None,
                    razao_fds: float | None = None) -> dict[int, float]:
    """Profissionais presentes em cada hora do horizonte.

    A hora 0 e o CORTE do primeiro dia, nao a meia-noite: o horizonte comeca as 07:00 e
    termina as 07:00 do dia seguinte ao ultimo, de modo que as janelas de 8 h e as de 12 h
    fecham exatamente, sem fatia parcial nas pontas (P5, revisao 1).

    Derivado da necessidade assistencial em 24 h, hora a hora — nunca de blocos. O Parecer
    nao fornece curva horaria, entao DENTRO do dia a necessidade e uniforme; o que NAO se faz
    e declara-la ja repartida em turnos, que e o vicio descrito no cabecalho.

    `variacao` faz a necessidade variar ENTRE dias, mantendo o total. Existe porque com
    demanda plana nenhuma restricao de escalonamento tinha como apertar: a alternancia do
    12x36 preenche janelas alternadas exatamente, a composicao fecha sozinha se a proporcao e
    igual em toda janela, e o piso de um enfermeiro por turno fica longe do limite. O
    Experimento A com `variacao=0` mede aritmetica de capacidade, nao rigidez de regime.
    Decisao do projeto de redacao, 23/09.

    `razao_fds` e a outra forma de dizer a mesma coisa, que e a da ferramenta: ver
    `fatores_por_razao`. As duas nao podem vir juntas.
    """
    if razao_fds is not None and variacao:
        raise ValueError("variacao e razao_fds sao duas formas da mesma entrada; use uma so")
    por_hora = porte_horas / dias / 24
    if razao_fds is not None and razao_fds != 1:
        fatores = fatores_por_razao(dias, inicio or primeira_segunda(), razao_fds)
        return {h: por_hora * fatores[h // 24] for h in range(dias * 24)}
    if not variacao:
        return {h: por_hora for h in range(dias * 24)}
    fatores = fatores_por_dia(dias, inicio or primeira_segunda(), variacao)
    return {h: por_hora * fatores[h // 24] for h in range(dias * 24)}


def pacientes(grau: Grau, porte_horas: float = PORTE_HORAS,
              dias: int = DIAS_HORIZONTE) -> float:
    """Pacientes implicitos no porte, dado o grau. E resultado, nao parametro.

    Manter o porte fixo em todos os graus (item 5 da decisao de 21/09) significa que a
    unidade representada muda de tamanho conforme o grau: 52,9 pacientes no minimo contra
    11,7 no intensivo. O numero nunca entra no modelo — a escala so ve horas e composicao —,
    mas precisa ser declarado no texto para o leitor saber o que a instancia representa.
    """
    return porte_horas / dias / grau.horas_paciente_24h


# --- entrada por pacientes e quadro de pessoal ------------------------------------------

IST = 0.15   # indice de seguranca tecnica do Parecer: cobre ausencias que a escala nao modela


def horas_por_dia(pacientes_por_grau: dict[str, float]) -> float:
    """Horas de enfermagem por dia = soma de pacientes x horas por paciente do grau.

    E a entrada da ferramenta (DECISOES.md, 29/09). O caminho por `PORTE_HORAS` continua
    existindo, porque e por ele que os experimentos se reproduzem.
    """
    desconhecidos = set(pacientes_por_grau) - set(GRAUS)
    if desconhecidos:
        raise ValueError(f"grau desconhecido: {sorted(desconhecidos)}; use {sorted(GRAUS)}")
    if any(p < 0 for p in pacientes_por_grau.values()):
        raise ValueError("numero de pacientes negativo")
    total = sum(p * GRAUS[g].horas_paciente_24h for g, p in pacientes_por_grau.items())
    if total <= 0:
        raise ValueError("nenhum paciente informado")
    return total


def grau_de_maior_carga(pacientes_por_grau: dict[str, float]) -> str:
    """O grau que governa a composicao quando a unidade mistura graus (Parecer).

    Regra (DECISOES.md, "2026-09-29 — Ajustes da Etapa 2"): vale o MAIOR PERCENTUAL DE
    ENFERMEIROS entre os graus presentes. Equivale a "maior carga" do Parecer; no empate de
    horas entre alta dependencia e semi-intensivo (10 h cada), vale o semi-intensivo, 42%.
    Conservador por construcao. Entre graus de mesmo percentual (minimo e intermediario,
    33%), desempata a ordem da tabela — sem efeito, porque os dois pedem a mesma composicao.
    """
    ordem = list(GRAUS)
    presentes = [g for g, p in pacientes_por_grau.items() if p > 0]
    if not presentes:
        raise ValueError("nenhum paciente informado")
    return max(presentes, key=lambda g: (GRAUS[g].pct_enfermeiros, ordem.index(g)))


def quadro_pessoal(horas_dia: float, carga_semanal: float = CARGA_SEMANAL,
                   ist: float = IST) -> tuple[float, float]:
    """QP do Parecer em duas parcelas: (nucleo assistencial, quadro completo).

    nucleo = horas por dia x 7 / CHS; completo = nucleo x (1 + IST). A escala e comparada
    ao NUCLEO, porque o IST cobre ferias e ausencias que a escala de 28 dias nao modela.
    """
    nucleo = horas_dia * 7 / carga_semanal
    return nucleo, nucleo * (1 + ist)


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


def conferir_amarracao(inst: Instancia) -> list[str]:
    """Tudo o que a instancia declara esta de fato amarrado ao contrato e aos turnos?

    Nasceu de dois erros em sequencia, no mesmo dia, ambos por lista duplicada:

    1. os padroes da CLT nomeavam so os turnos-base e deixavam as variantes de enfermeiro sem
       regra de descanso — o solver marcou `NE` as 23:00 e `M` as 07:00, zero hora de
       intervalo;
    2. corrigido o gerador de padroes, o resultado nao mudou NADA, porque o contrato apontava
       para os tres ids antigos. Padrao que o contrato nao referencia nao e imposto pelo
       modelo nem cobrado pelo avaliador: existe no arquivo e nao vale nada.

    As conferencias que existiam nao tinham como pegar nenhum dos dois, porque enumeravam as
    mesmas listas. Esta aqui confere a AMARRACAO — se o que esta escrito chega a valer —, que
    e uma pergunta diferente de "o valor esta certo".
    """
    erros = []
    c = inst.contratos["0"]
    emitidos, referenciados = set(inst.padroes), set(c.padroes_indesejados)
    if emitidos - referenciados:
        erros.append(f"padroes emitidos que o contrato NAO referencia, logo inertes: "
                     f"{sorted(emitidos - referenciados)}")
    if referenciados - emitidos:
        erros.append(f"contrato referencia padrao inexistente: "
                     f"{sorted(referenciados - emitidos)}")
    nos_padroes = {e.turno for p in inst.padroes.values() for e in p.entradas} - {"None", "Any"}
    if desconhecidos := nos_padroes - set(inst.turnos):
        erros.append(f"padrao cita turno que nao existe: {sorted(desconhecidos)}")
    # todo turno com demanda precisa aparecer em algum padrao de descanso, senao ele fica
    # fora das regras — foi exatamente o caso das variantes de enfermeiro
    com_demanda = {s for (_, s), q in inst.demanda.items() if q > 0}
    if de_fora := com_demanda - nos_padroes:
        erros.append(f"turnos com demanda e sem NENHUMA regra de descanso: {sorted(de_fora)}")
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


def conferir_descanso(regime: str, descanso_clt: bool = True,
                      variantes: bool = True) -> tuple[float, list[str]]:
    """Menor intervalo entre o fim de um turno e o inicio do proximo, entre as sequencias
    que o contrato admite. Confere que as regras de descanso codificadas de fato valem.

    Enumera todos os pares (turno no dia d, turno no dia d+k) para k = 1 e 2, descarta os
    proibidos por MaxConsecutiveWorkingDays e pelos padroes indesejados, e mede o intervalo.
    O k = 2 com o dia do meio livre e o caso do descanso semanal: no regime de 8 h e ele que
    tem de dar pelo menos 24 h (CLT art. 67), aproximado por no maximo 6 dias seguidos.
    """
    # As variantes de enfermeiro entram aqui tambem. Ate 23/09 esta conferencia enumerava so
    # os turnos-base, exatamente como o gerador de padroes — as duas listas eram a mesma lista
    # incompleta, escrita duas vezes, e por isso a conferencia nao tinha como pegar o furo.
    # Quem pegou foi a medicao do descanso na ESCALA pronta
    # (`docs/conferencia_descanso_escala.py`), que le os horarios do arquivo em vez de confiar
    # numa lista. Licao: conferencia que compartilha a premissa do que confere nao confere.
    turnos = {}
    for tid, ini, dur, _ in REGIMES[regime]:
        for v in _variantes(tid, variantes):
            turnos[v] = (ini, ini + dur)
    max_consec = MAX_CONSECUTIVOS[regime]
    proibidos = {(va, k, vb)
                 for a, k, b in _pares_proibidos(regime, descanso_clt)
                 for va in _variantes(a, variantes)
                 for vb in _variantes(b, variantes)}

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


def _contrato(regime: str | None, descanso_clt: bool, padroes: tuple[str, ...], *,
              max_atribuicoes: int | None = None, max_consecutivos: int | None = None,
              descricao: str | None = None) -> Contrato:
    """Contrato unico do regime. Os limites legais entram como flexiveis do esquema.

    ATENCAO: no formato do INRC toda restricao de contrato e flexivel. Para o Experimento A,
    o teto de 42 h/semana e o descanso precisam BINDAR, senao "minimo viavel" vira divisao.
    A rigidez e opcao do modelo (`modelo.py`), nao do arquivo — assim a instancia emitida
    continua sendo uma instancia normal do INRC, reutilizavel por terceiros. Ver P7.

    `padroes` vem de fora, de `_padroes`, e NAO e montado aqui. Em 23/09 esta funcao tinha a
    lista de ids escrita a mao: corrigi o gerador de padroes para cobrir as variantes de
    enfermeiro, os padroes novos passaram a ser emitidos no XML, e **nada mudou no resultado**,
    porque o contrato continuou apontando so para os tres ids antigos. Padrao que o contrato
    nao referencia nao e imposto pelo modelo nem cobrado pelo avaliador: existe no arquivo e
    nao vale nada. Era a terceira copia da mesma lista; agora e uma so.
    """
    return Contrato(
        id="0",
        descricao=descricao or f"regime {regime}, 42h/semana",
        weekend_definition="SaturdaySunday",
        padroes_indesejados=padroes,
        single_assignment_per_day=_flex(),
        max_num_assignments=_flex(max_atribuicoes or MAX_ATRIBUICOES[regime]),
        min_num_assignments=_flex(0, ligada=False, peso=0),
        max_consecutive_working_days=_flex(max_consecutivos or MAX_CONSECUTIVOS[regime]),
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


def _padroes(regime: str, descanso_clt: bool, variantes: bool) -> dict[str, Padrao]:
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
    return _padroes_de(_pares_proibidos(regime, descanso_clt), variantes)


def _padroes_de(proibidos, variantes: bool) -> dict[str, Padrao]:
    """Pares proibidos -> padroes indesejados do INRC: s, (salto - 1) folgas, t."""
    padroes = {}
    for a, salto, b in proibidos:
        # ERRO CORRIGIDO EM 23/09: os padroes nomeavam so os turnos-base (N, D, M, T) e
        # deixavam de fora as variantes de enfermeiro (NE, DE, ME, TE), que tem os MESMOS
        # horarios. O solver usou exatamente esse furo: na escala de 8 h apareceu NE as 23:00
        # seguido de M as 07:00 do dia seguinte — ZERO hora de interjornada. A regra estava
        # validada (P7.1 a P7.3); quem falhou foi a codificacao dela. Agora o par proibido se
        # expande sobre todas as variantes de cada turno-base.
        for va in _variantes(a, variantes):
            for vb in _variantes(b, variantes):
                entradas = [EntradaPadrao(va, "Any")]
                entradas += [EntradaPadrao("None", "Any")] * (salto - 1)
                entradas.append(EntradaPadrao(vb, "Any"))
                # ids de salto 1 e 2 mantidos como eram, para o XML do Experimento A nao mudar
                prefixo = {1: "", 2: "36h_"}.get(salto, f"d{salto}_")
                pid = f"clt_{prefixo}{va}_{vb}"
                padroes[pid] = Padrao(id=pid, peso=1, entradas=tuple(entradas))
    return padroes


def pares_proibidos_por_horario(turnos, max_consecutivos: int | None,
                                interjornada: bool = True,
                                descartar: bool = True) -> tuple[tuple[str, int, str], ...]:
    """Sequencias proibidas pelos HORARIOS: (turno s no dia d, salto k, turno t no dia d+k).

    `turnos`: [(id, hora de inicio, duracao em horas)]. O descanso entre s no dia d e t no
    dia d+k, com os dias do meio livres, e (24k + inicio de t) - (inicio de s + duracao de s),
    medido no relogio. O par e proibido se ficar abaixo do exigido depois de s:
    `descanso_exigido` — 36 h depois de turno de 12 h ou mais (art. 59-A), 11 h nos demais
    (art. 66). `interjornada=False` desliga so a regra das 11 h (e o `--sem-descanso-clt`).

    Com o dia do meio TRABALHADO, o descanso que conta e o do par (s, meio), que ja e um par
    de salto 1 — por isso os saltos maiores so precisam do caso com o meio livre. k vai ate 4,
    que cobre qualquer turno de ate 24 h com 36 h de descanso.

    `descartar`: pares de salto 1 sao dois dias seguidos de trabalho, que o contrato ja proibe
    quando `max_consecutivos` < 2. Nao sao emitidos (decisao do Otavio, 29/09: opcao 1) — a
    lista fica identica a escrita a mao antes, e o modelo e o XML do Experimento A nao mudam.
    A equivalencia (sem descarte = com descarte + o que o limite proibe) e teste permanente
    em `src/testes_entrada.py`, para o descarte nunca esconder uma proibicao.

    Substitui a lista escrita a mao, que supunha os horarios 07-19 e 07-15-23 (DECISOES.md,
    "2026-09-29 — Ajustes da Etapa 2"). E a FONTE UNICA das regras de descanso: os padroes
    do XML e a conferencia das sequencias saem daqui.
    """
    proibidos = set()
    for s, ini_s, dur_s in turnos:
        exigido = descanso_exigido(dur_s)
        if exigido == INTERJORNADA and not interjornada:
            continue
        for k in (1, 2, 3, 4):
            if descartar and k == 1 and max_consecutivos is not None and max_consecutivos < 2:
                continue
            for t, ini_t, _ in turnos:
                if 24 * k + ini_t - (ini_s + dur_s) < exigido:
                    proibidos.add((s, k, t))
    return tuple(sorted(proibidos))


def _turnos_base(regime: str) -> list[tuple[str, int, int]]:
    return [(tid, ini, dur) for tid, ini, dur, _ in REGIMES[regime]]


def _pares_proibidos(regime: str, descanso_clt: bool) -> tuple[tuple[str, int, str], ...]:
    """As sequencias proibidas de um regime, GERADAS dos horarios. Ver
    `pares_proibidos_por_horario`. Ate 29/09 esta funcao devolvia uma lista escrita a mao:
    (N, 2, D) no 12x36 — o furo do P7.2, noturno termina 07:00 e diurno de dois dias depois
    comeca 07:00, 24 h — e (N,1,M), (N,1,T), (T,1,M) no de 8 h. O gerador reproduz as duas,
    e o teste de `src/testes_entrada.py` guarda a lista antiga para conferir.
    """
    return pares_proibidos_por_horario(_turnos_base(regime), MAX_CONSECUTIVOS[regime],
                                       interjornada=descanso_clt)


def _variantes(base: str, variantes: bool) -> tuple[str, ...]:
    """O turno-base e, quando o grau exige enfermeiro por janela, a variante de mesmo horario."""
    return (base, f"{base}E") if variantes else (base,)


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


def _equipe(n_enfermeiros: int, n_tecnicos: int, nomes_enfermeiros=None,
            nomes_tecnicos=None) -> dict[str, Profissional]:
    """Equipe informada por quantidade, que e a entrada da ferramenta (DECISOES.md, 29/09).

    Nomes padrao "Enf 1...", "Tec 1..."; listas de nomes opcionais, uma por categoria, do
    tamanho da categoria. Os ids continuam numericos, enfermeiros primeiro, como em
    `_profissionais`.
    """
    if n_enfermeiros < 0 or n_tecnicos < 0 or n_enfermeiros + n_tecnicos == 0:
        raise ValueError("equipe vazia ou com quantidade negativa")
    nomes = []
    for n, lista, padrao in ((n_enfermeiros, nomes_enfermeiros, "Enf"),
                             (n_tecnicos, nomes_tecnicos, "Téc")):
        if lista is None:
            nomes.append([f"{padrao} {i + 1}" for i in range(n)])
        elif len(lista) != n:
            raise ValueError(f"{len(lista)} nomes para {n} profissionais ({padrao})")
        else:
            nomes.append(list(lista))
    todos = nomes[0] + nomes[1]
    if len(set(todos)) != len(todos):
        raise ValueError("nomes repetidos na equipe")
    profs = {}
    for i, nome in enumerate(todos):
        enfermeiro = i < n_enfermeiros
        habs = {HABILIDADE_BASE} | ({HABILIDADE_ENF} if enfermeiro else set())
        profs[str(i)] = Profissional(id=str(i), nome=nome, contrato="0",
                                     habilidades=frozenset(habs))
    return profs


# Nome do grau no texto que o usuario le (os ids ficam sem acento no codigo).
NOME_GRAU = {"minimo": "mínimo", "intermediario": "intermediário",
             "alta": "alta dependência", "semi_intensivo": "semi-intensivo",
             "intensivo": "intensivo"}


def plural(n: int, singular: str, plural_: str) -> str:
    """"1 dia", "2 dias": concordancia nos textos da tela e da planilha."""
    return f"{n} {singular if n == 1 else plural_}"


def grau_do_alerta(grau: str, pacientes: dict[str, float] | None) -> tuple[str, str]:
    """Grau cujo percentual vale no alerta de proporcao, e por que (DECISOES.md, "2026-10-05
    — Grau da proporcao: o grupo de pacientes de maior carga").

    Com pacientes informados, o do GRUPO de maior carga total (pacientes x horas por paciente
    em 24 h), como manda o Parecer (secao 3): o campo da tela nao vale. Sem pacientes, o grau
    informado. Empate: regra nao decidida (PROPOSTAS.md, P8) — conta com o maior percentual dos
    empatados e DIZ isso. Nao confundir com `grau_de_maior_carga` (leitura de 29/09, que monta
    as instancias do caminho por pacientes e fica como esta).
    """
    cargas = {g: p * GRAUS[g].horas_paciente_24h for g, p in (pacientes or {}).items()
              if p > 0}
    if not cargas:
        return grau, "grau informado na tela"
    maior = max(cargas.values())
    empatados = [g for g in GRAUS if g in cargas and abs(cargas[g] - maior) < 1e-9]
    lista = ", ".join(f"{NOME_GRAU[g]} {cargas[g]:g} h" for g in GRAUS if g in cargas)
    if len(empatados) == 1:
        return empatados[0], (f"grupo de pacientes de maior carga por dia: "
                              f"{NOME_GRAU[empatados[0]]} ({lista})")
    escolhido = max(empatados, key=lambda g: GRAUS[g].pct_enfermeiros)
    nomes = " e ".join(NOME_GRAU[g] for g in empatados)
    return escolhido, (f"empate de carga entre {nomes} ({lista}); a regra para empate não está "
                       f"decidida, e a conta usa o maior percentual, {NOME_GRAU[escolhido]}")


def conferir_composicao(inst: Instancia, grau: str,
                        pacientes: dict[str, float] | None = None) -> list[str]:
    """A equipe cumpre a proporcao de enfermeiros do Parecer no QUADRO?

    Com a equipe dada por quantidade, a proporcao deixa de sair por construcao e passa a ser
    conferida. Lista vazia = cumpre. Nao impede resolver: o relatorio diz, o gestor decide.
    O piso de 1 enfermeiro por turno esta na cobertura; se faltar enfermeiro para ele, quem
    responde e o solver, com inviabilidade.
    """
    grau, porque = grau_do_alerta(grau, pacientes)
    g = GRAUS[grau]
    total = len(inst.profissionais)
    n_enf = sum(1 for p in inst.profissionais.values() if HABILIDADE_ENF in p.habilidades)
    exigido = math.ceil(g.pct_enfermeiros * total - 1e-9)
    if n_enf < exigido:
        return [f"{plural(n_enf, 'enfermeiro', 'enfermeiros')} em {total} profissionais; "
                f"o Parecer pede ao menos {g.pct_enfermeiros:.0%} no grau "
                f"{NOME_GRAU.get(grau, grau)}, isto é, {exigido} — {porque}"]
    return []


def alertas_cofen(inst: Instancia, grau: str | None = None,
                  pacientes: dict[str, float] | None = None) -> list[str]:
    """Alertas do COFEN. NUNCA travam: nao mexem no modelo, so informam (DECISOES.md,
    "2026-09-29 — Redesenho da ferramenta" — a CLT e restricao, o COFEN e alerta).

    - proporcao de enfermeiros no quadro, pelo grau predominante informado;
    - turnos em que a demanda nao pede nenhum enfermeiro;
    - com pacientes informados: quadro abaixo do QP completo, mostrando tambem o nucleo.
    """
    alertas = []
    if grau is not None:
        alertas += conferir_composicao(inst, grau, pacientes)
    sem_enf = []
    for d in inst.dias:
        for tid, t in inst.turnos.items():
            if HABILIDADE_ENF in t.habilidades:
                continue                      # a variante de enfermeiro e o proprio posto
            total = inst.demanda_de(d, tid) + inst.demanda_de(d, f"{tid}E")
            if total > 0 and inst.demanda_de(d, f"{tid}E") == 0:
                sem_enf.append((d, tid))
    if sem_enf:
        exemplos = ", ".join(f"{d:%d/%m} {tid}" for d, tid in sem_enf[:3])
        alertas.append(f"{plural(len(sem_enf), 'turno', 'turnos')} sem enfermeiro na demanda "
                       f"(ex.: {exemplos}{', ...' if len(sem_enf) > 3 else ''})")
    if pacientes:
        nucleo, completo = quadro_pessoal(horas_por_dia(pacientes), chs(inst))
        quadro = len(inst.profissionais)
        if quadro < completo:
            virgula = lambda x: f"{x:.2f}".replace(".", ",")  # noqa: E731
            alertas.append(f"quadro de {quadro} abaixo do QP completo do Parecer "
                           f"({virgula(completo)}, com IST de {IST:.0%}); o núcleo "
                           f"assistencial, sem IST, é {virgula(nucleo)}")
    return alertas


def chs(inst: Instancia) -> float:
    """CHS do QP: a media das cargas contratuais da equipe, quando a instancia as tem (caminho
    de turnos configurados); senao, as 42 h, hipotese declarada dos experimentos."""
    return inst.chs_media if inst.chs_media is not None else CARGA_SEMANAL


def _id_profissional(profs: dict[str, Profissional], quem: str) -> str:
    """Profissional pelo id ou pelo nome."""
    if quem in profs:
        return quem
    por_nome = {p.nome: p.id for p in profs.values()}
    if quem not in por_nome:
        raise ValueError(f"profissional inexistente: {quem}")
    return por_nome[quem]


def _indisponiveis(profs: dict[str, Profissional], periodos, inicio: date,
                   fim: date) -> frozenset[tuple[str, date]]:
    """(profissional, data inicial, data final) -> pares (id, dia) indisponiveis.

    O profissional pode vir pelo id ou pelo nome. Periodo que sai do horizonte e recortado;
    periodo inteiramente fora dele e erro, porque quase certamente e data digitada errada.
    """
    pares = set()
    for quem, de, ate in periodos:
        pid = _id_profissional(profs, quem)
        if ate < de:
            raise ValueError(f"indisponibilidade de {quem}: fim {ate} antes do inicio {de}")
        if ate < inicio or de > fim:
            raise ValueError(f"indisponibilidade de {quem} ({de} a {ate}) fora do horizonte "
                             f"{inicio} a {fim}")
        d = max(de, inicio)
        while d <= min(ate, fim):
            pares.add((pid, d))
            d += timedelta(days=1)
    return frozenset(pares)


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


# --- caminho por turnos configurados e demanda informada (DECISOES.md, 29/09) ------------

MAX_CONSECUTIVOS_GENERICO = 6   # descanso semanal (art. 67), aproximado como no regime de 8 h
CATEGORIAS = ("enf", "tec")


def _validar_turnos(turnos) -> list[tuple[str, int, int, str]]:
    """[(id, hora de inicio, duracao em horas, descricao)], conferido."""
    vistos = []
    for item in turnos:
        tid, ini, dur = item[0], item[1], item[2]
        desc = item[3] if len(item) > 3 else tid
        if not tid or not str(tid).isalnum():
            raise ValueError(f"id de turno invalido: {tid!r} (letras e numeros apenas)")
        if not (0 <= ini <= 23) or not (1 <= dur <= 24):
            raise ValueError(f"turno {tid}: inicio {ini} h ou duracao {dur} h fora do intervalo")
        vistos.append((str(tid), int(ini), int(dur), str(desc)))
    ids = [t[0] for t in vistos]
    if len(set(ids)) != len(ids):
        raise ValueError(f"ids de turno repetidos: {ids}")
    # a variante de enfermeiro de "M" e "ME": um turno do usuario com esse id colidiria
    if colisao := {i for i in ids if i.endswith("E") and i[:-1] in ids}:
        raise ValueError(f"id de turno colide com a variante de enfermeiro: {sorted(colisao)}")
    return vistos


FIM_DE_SEMANA = {"sab_dom": ((5, 6), "SaturdaySunday"),
                 "sex_dom": ((4, 5, 6), "FridaySaturdaySunday")}


def demanda_por_turno(turnos, inicio: date, dias: int, demanda_turno,
                      demanda_fds=None, demanda_data=None,
                      fim_de_semana: str = "sab_dom") -> dict[tuple[date, str], int]:
    """Demanda informada pelo usuario -> cobertura por (dia, turno), com a variante de
    enfermeiro. Generalista: `demanda_turno[id] = (enfermeiros, tecnicos)`, com
    `demanda_fds[id]` opcional para o fim de semana (`fim_de_semana`: sabado e domingo, ou
    sexta a domingo). Especifica, por cima da generalista:
    `demanda_data[(data, id, "enf" | "tec")] = n` — um feriado, por exemplo.

    O posto de tecnico (turno-base, habilidade "Enfermagem") pode ser coberto por enfermeiro,
    como no caminho por pacientes; o de enfermeiro (variante "E") so por enfermeiro.
    """
    ids = [t[0] for t in turnos]
    demanda_fds = demanda_fds or {}
    demanda_data = demanda_data or {}
    for chave in (set(demanda_turno) | set(demanda_fds)) - set(ids):
        raise ValueError(f"demanda para turno inexistente: {chave}")
    if falta := set(ids) - set(demanda_turno):
        raise ValueError(f"turnos sem demanda informada: {sorted(falta)}")
    fim = inicio + timedelta(days=dias - 1)
    for (d, tid, cat), n in demanda_data.items():
        if tid not in ids or cat not in CATEGORIAS or not (inicio <= d <= fim) or n < 0:
            raise ValueError(f"demanda especifica invalida: {(d, tid, cat)} = {n}")
    dias_fds = FIM_DE_SEMANA[fim_de_semana][0]
    demanda: dict[tuple[date, str], int] = {}
    for k in range(dias):
        d = inicio + timedelta(days=k)
        for tid in ids:
            base = demanda_fds.get(tid, demanda_turno[tid]) if d.weekday() in dias_fds \
                else demanda_turno[tid]
            enf = demanda_data.get((d, tid, "enf"), base[0])
            tec = demanda_data.get((d, tid, "tec"), base[1])
            if enf < 0 or tec < 0:
                raise ValueError(f"demanda negativa no turno {tid}")
            demanda[(d, f"{tid}E")] = enf
            demanda[(d, tid)] = tec
    return demanda


def _construir_por_turnos(turnos, demanda_turno, demanda_fds, demanda_data, *,
                          n_enfermeiros, n_tecnicos, nomes_enfermeiros, nomes_tecnicos,
                          dias: int, inicio: date, descanso_clt: bool,
                          indisponibilidades, pedidos=(),
                          fim_de_semana: str = "sab_dom", cargas=None) -> Instancia:
    """Instancia com turnos e demanda do usuario. A CLT trava; o COFEN nao entra aqui.

    - regras de descanso GERADAS dos horarios (`pares_proibidos_por_horario`);
    - no maximo 6 dias seguidos (art. 67, aproximado); a alternancia de quem faz so 12 h sai
      sozinha da regra das 36 h;
    - carga contratual semanal por profissional (`cargas`: nome ou id -> horas; quem nao
      aparece fica com 44 h). Dela sai o teto em HORAS no horizonte, rigido no modelo:
      carga x dias disponiveis / 7 (`Instancia.horas_devidas`), porque com turnos de duracoes
      diferentes contar turnos nao limita horas. O `MaxNumAssignments` do XML fica com o teto
      em turnos da maior carga no horizonte inteiro, pelo turno mais curto — nunca mais
      apertado que as horas de ninguem (DECISOES.md, "2026-10-02 — Carga por contrato");
    - o piso de 1 enfermeiro por turno NAO e cobertura: quem define a demanda e o usuario, e
      a falta de enfermeiro vira alerta (`alertas_cofen`).
    """
    if n_enfermeiros is None or n_tecnicos is None:
        raise ValueError("com turnos configurados, informe n_enfermeiros e n_tecnicos")
    turnos = _validar_turnos(turnos)
    base = [(tid, ini, dur) for tid, ini, dur, _ in turnos]
    fim = inicio + timedelta(days=dias - 1)
    profs = _equipe(n_enfermeiros, n_tecnicos, nomes_enfermeiros, nomes_tecnicos)
    carga_semanal = {n: CARGA_CONTRATUAL_PADRAO for n in profs}
    for quem, horas in (cargas or {}).items():
        if not 0 < horas <= CARGA_CONTRATUAL_PADRAO:
            raise ValueError(f"carga de {quem}: {horas:g} h por semana; o limite da CF e "
                             f"{CARGA_CONTRATUAL_PADRAO:g} h")
        carga_semanal[_id_profissional(profs, quem)] = float(horas)
    carga = max(carga_semanal.values()) * dias / 7
    pares = pares_proibidos_por_horario(base, MAX_CONSECUTIVOS_GENERICO,
                                        interjornada=descanso_clt)
    padroes = _padroes_de(pares, variantes=True)
    objetos = {}
    for tid, ini, dur, desc in turnos:
        t_fim = time((ini + dur) % 24)
        objetos[tid] = Turno(id=tid, inicio=time(ini), fim=t_fim, descricao=desc,
                             habilidades=frozenset({HABILIDADE_BASE}))
        objetos[f"{tid}E"] = Turno(id=f"{tid}E", inicio=time(ini), fim=t_fim,
                                   descricao=f"{desc} (enfermeiro)",
                                   habilidades=frozenset({HABILIDADE_ENF}))
    if fim_de_semana not in FIM_DE_SEMANA:
        raise ValueError(f"fim de semana {fim_de_semana!r}; use {sorted(FIM_DE_SEMANA)}")
    contrato = _contrato(None, descanso_clt, tuple(padroes),
                         max_atribuicoes=math.floor(carga / min(d for _, _, d in base)),
                         max_consecutivos=MAX_CONSECUTIVOS_GENERICO,
                         descricao="turnos configurados, carga contratual informada "
                                   "(limite legal de 44h/semana)")
    contrato = dataclasses.replace(contrato,
                                   weekend_definition=FIM_DE_SEMANA[fim_de_semana][1])
    # pedidos de folga: flexiveis, peso 1 — entram na penalidade, nunca travam
    folgas = []
    for quem, d in pedidos:
        if not (inicio <= d <= fim):
            raise ValueError(f"pedido de folga de {quem} em {d}, fora do horizonte")
        folgas.append(Pedido(tipo="folga_dia", profissional=_id_profissional(profs, quem),
                             data=d, peso=1))
    return Instancia(
        id=f"br_turnos_e{len(profs)}",
        arquivo="",
        inicio=inicio,
        fim=fim,
        habilidades=(HABILIDADE_BASE, HABILIDADE_ENF),
        turnos=objetos,
        padroes=padroes,
        contratos={"0": contrato},
        profissionais=profs,
        demanda=demanda_por_turno(turnos, inicio, dias, demanda_turno, demanda_fds,
                                  demanda_data, fim_de_semana),
        pedidos=tuple(folgas),
        indisponiveis=_indisponiveis(profs, indisponibilidades, inicio, fim),
        carga_semanal_h=carga_semanal,
    )


def construir(grau: str | None = None, efetivo: int = 36, regime: str = "12x36",
              regra: str = "teto", porte_horas: float | None = None,
              dias: int = DIAS_HORIZONTE, inicio: date | None = None,
              descanso_clt: bool = True, variacao: float = 0.0, *,
              pacientes: dict[str, float] | None = None,
              razao_fds: float | None = None,
              n_enfermeiros: int | None = None, n_tecnicos: int | None = None,
              nomes_enfermeiros=None, nomes_tecnicos=None,
              indisponibilidades=(), turnos=None, demanda_turno=None, demanda_fds=None,
              demanda_data=None, pedidos=(), fim_de_semana: str = "sab_dom",
              cargas=None) -> Instancia:
    """Monta a instancia brasileira.

    Tres caminhos, que nao se misturam:

    - o de TURNOS CONFIGURADOS (DECISOES.md, "2026-09-29 — Redesenho da ferramenta"):
      `turnos` = [(id, inicio, duracao, descricao)] e a demanda informada por turno —
      `demanda_turno`, `demanda_fds`, `demanda_data`. Ver `_construir_por_turnos`. Nao usa
      regime, grau, porte, pacientes, razao nem variacao;

    - o dos EXPERIMENTOS, que e o de sempre e continua reproduzindo: `grau`, `porte_horas`
      (padrao `PORTE_HORAS`), `efetivo`, `variacao`;
    - o da FERRAMENTA (DECISOES.md, 29/09): `pacientes` por grau (o porte e o grau saem
      deles), `razao_fds`, `n_enfermeiros` + `n_tecnicos` com nomes opcionais.

    Os dois aceitam `indisponibilidades`: lista de (profissional, data inicial, data final),
    com o profissional pelo id ou pelo nome. E restricao RIGIDA — ferias e licencas —, e o
    modelo fixa em zero as atribuicoes da pessoa nesses dias. O XML do INRC nao tem como
    representa-la: `escrever_xml` a deixa de fora, e o arquivo sozinho nao a reproduz.
    """
    if turnos is not None:
        outros = (("pacientes", pacientes), ("porte_horas", porte_horas),
                  ("razao_fds", razao_fds))
        misturados = ([nome for nome, valor in outros if valor is not None]
                      + (["variacao"] if variacao else []))
        if misturados:
            raise ValueError(f"com turnos configurados a demanda e informada por turno; "
                             f"nao use {misturados}")
        if demanda_turno is None:
            raise ValueError("com turnos configurados, informe demanda_turno")
        inicio = inicio or primeira_segunda()
        if inicio.weekday() != 0:
            raise ValueError("o horizonte comeca numa segunda-feira, para fechar 4 fins de semana")
        return _construir_por_turnos(
            turnos, demanda_turno, demanda_fds, demanda_data, n_enfermeiros=n_enfermeiros,
            n_tecnicos=n_tecnicos, nomes_enfermeiros=nomes_enfermeiros,
            nomes_tecnicos=nomes_tecnicos, dias=dias, inicio=inicio,
            descanso_clt=descanso_clt, indisponibilidades=indisponibilidades,
            pedidos=pedidos, fim_de_semana=fim_de_semana, cargas=cargas)
    if demanda_turno is not None or demanda_fds is not None or demanda_data is not None:
        raise ValueError("demanda por turno so vale com turnos configurados (turnos=...)")
    if pedidos or fim_de_semana != "sab_dom" or cargas:
        raise ValueError("pedidos de folga, fim de semana configuravel e carga por contrato "
                         "so valem com turnos configurados (turnos=...); o caminho dos "
                         "experimentos fica com 42 h, hipotese declarada")
    if pacientes is not None:
        if porte_horas is not None:
            raise ValueError("pacientes e porte_horas sao duas formas do porte; use uma so")
        derivado = grau_de_maior_carga(pacientes)
        if grau is not None and grau != derivado:
            raise ValueError(f"grau {grau} informado, mas o de maior carga nos pacientes e "
                             f"{derivado}")
        grau = derivado
        porte_horas = horas_por_dia(pacientes) * dias
    grau = grau or "intermediario"
    porte_horas = PORTE_HORAS if porte_horas is None else porte_horas
    g = GRAUS[grau]
    inicio = inicio or primeira_segunda()
    if inicio.weekday() != 0:
        raise ValueError("o horizonte comeca numa segunda-feira, para fechar 4 fins de semana")
    perfil = perfil_continuo(porte_horas, dias, variacao, inicio, razao_fds=razao_fds)
    duracao = REGIMES[regime][0][2]
    janelas = reagregar(perfil, duracao, regra=regra)
    if (n_enfermeiros is None) != (n_tecnicos is None):
        raise ValueError("informe n_enfermeiros e n_tecnicos juntos")
    if n_enfermeiros is not None:
        profs = _equipe(n_enfermeiros, n_tecnicos, nomes_enfermeiros, nomes_tecnicos)
        efetivo = len(profs)
    else:
        profs, _ = _profissionais(efetivo, g)
    fim = inicio + timedelta(days=dias - 1)
    # os padroes sao montados UMA vez e o contrato recebe os ids deles. Nao repetir a lista.
    padroes = _padroes(regime, descanso_clt, bool(g.piso_enfermeiro_por_janela))
    # os sufixos so aparecem quando o parametro e usado, para os nomes ja publicados nao mudarem
    sufixo = f"_v{variacao:g}".replace(".", "") if variacao else ""
    if razao_fds is not None and razao_fds != 1:
        sufixo += f"_r{razao_fds:.4g}".replace(".", "")
    if pacientes is not None:
        sufixo += f"_h{porte_horas / dias:.4g}".replace(".", "")
    return Instancia(
        id=f"br_{grau}_{regime}_{regra}_e{efetivo}{sufixo}",
        arquivo="",
        inicio=inicio,
        fim=fim,
        habilidades=(HABILIDADE_BASE, HABILIDADE_ENF),
        turnos=_turnos(regime, g),
        padroes=padroes,
        contratos={"0": _contrato(regime, descanso_clt, tuple(padroes))},
        profissionais=profs,
        demanda=_demanda(janelas, regime, g, inicio, dias),
        pedidos=(),
        indisponiveis=_indisponiveis(profs, indisponibilidades, inicio, fim),
    )


def primeira_segunda(ano: int = 2027) -> date:
    d = date(ano, 1, 1)
    return d + timedelta(days=(7 - d.weekday()) % 7)


def quadro_referencia(porte_horas: float = PORTE_HORAS, dias: int = DIAS_HORIZONTE,
                      carga_semanal: float = CARGA_SEMANAL) -> float:
    """QP_ref do Parecer, sem IST. E o denominador do Experimento A — o nucleo de
    `quadro_pessoal`, com o porte do experimento. Uma formula so, nos dois caminhos."""
    return quadro_pessoal(porte_horas / dias, carga_semanal)[0]


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
    print(f"QP completo     {quadro_pessoal(PORTE_HORAS / DIAS_HORIZONTE)[1]:.2f} "
          f"profissionais (com IST de {IST:.0%})")
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
        exigido = DESCANSO_EXIGIDO[regime]
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
    # amarracao: o que a instancia declara chega a valer? Nas 20 combinacoes, porque o furo
    # das variantes de enfermeiro so aparecia nos graus com piso de enfermeiro por janela.
    print()
    print("amarracao (padrao emitido x referenciado pelo contrato x turno com demanda):")
    reprovadas = 0
    for nome_grau in sorted(GRAUS):
        for reg in ("12x36", "8h"):
            for rg in ("teto", "maior_resto"):
                problemas = conferir_amarracao(
                    construir(grau=nome_grau, regime=reg, regra=rg, efetivo=36, variacao=1.0))
                if problemas:
                    reprovadas += 1
                    erros += [f"{nome_grau}/{reg}/{rg}: {p}" for p in problemas]
    print(f"   {20 - reprovadas} de 20 combinacoes ok")

    print()
    if erros:
        print("CONFERENCIAS REPROVARAM:")
        for e in erros:
            print(f"   {e}")
        return 1
    print("conferencias OK: porte, anti-tautologia, tolerancia de um bloco, descanso e"
          " amarracao")
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
    ap.add_argument("--pacientes", nargs="+", metavar="GRAU=N",
                    help="pacientes por grau, ex.: intermediario=30 intensivo=4. Substitui o"
                         " --grau e o porte fixo")
    ap.add_argument("--razao-fds", type=float, default=None,
                    help="demanda do fim de semana / demanda do dia util, de 0 a 1 (1 = igual)")
    ap.add_argument("--enfermeiros", type=int, default=None)
    ap.add_argument("--tecnicos", type=int, default=None)
    a = ap.parse_args()

    if a.conferencia:
        return relatorio_conferencias()

    pacientes = None
    if a.pacientes:
        pacientes = {}
        for item in a.pacientes:
            g, _, n = item.partition("=")
            pacientes[g] = float(n)
    grau = None if pacientes else a.grau
    inst = construir(grau=grau, efetivo=a.efetivo, regime=a.regime, regra=a.regra,
                     descanso_clt=not a.sem_descanso_clt, pacientes=pacientes,
                     razao_fds=a.razao_fds, n_enfermeiros=a.enfermeiros,
                     n_tecnicos=a.tecnicos)
    grau = grau or grau_de_maior_carga(pacientes)
    h_dia = horas_por_dia(pacientes) if pacientes else PORTE_HORAS / DIAS_HORIZONTE
    nucleo, completo = quadro_pessoal(h_dia)
    print(f"grau {grau} | {h_dia:.2f} h/dia | QP nucleo assistencial {nucleo:.2f} | "
          f"QP completo (IST {IST:.0%}) {completo:.2f}")
    print(f"a escala e comparada ao nucleo; equipe informada: {len(inst.profissionais)}")
    for aviso in conferir_composicao(inst, grau):
        print(f"AVISO: {aviso}")
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
