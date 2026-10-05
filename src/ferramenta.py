"""A ferramenta, sem tela: configuracao da unidade -> veredito do quadro, escala e planilha.

`src/app.py` e so a casca Streamlit em volta disto. Separado de proposito: o que decide o
veredito tem de poder ser testado sem navegador (`src/testes_ferramenta.py`).

Caminho: turnos configurados e demanda informada por turno (DECISOES.md, "2026-09-29 —
Redesenho da ferramenta"). A CLT trava; o COFEN e alerta. O caminho por pacientes fica so no
painel "Conferir com o COFEN" (QP) e nos experimentos.

Resolve com as MESMAS opcoes de modelo do Experimento A (`experimento_a.resolver_instancia`):
limites legais rigidos, habilidade rigida. A funcao objetivo e a penalidade das flexiveis —
aqui, na pratica, os pedidos de folga nao atendidos.

O veredito do quadro:

- **admite escala legal** — o quadro informado tem escala que cumpre cobertura e lei;
- **faltam N; o menor quadro viavel e X** — o quadro informado e inviavel, com prova do
  solver ou da aritmetica, e X e o primeiro viavel subindo o quadro;
- **nao decidido** — o solver bateu no limite de tempo sem escala: "nao foi possivel gerar a
  escala no tempo disponivel". Nunca e contado como inviavel, e nunca vira "faltam N".

Com escala, a frase separa o otimo provado ("escala gerada") da escala achada no limite de
tempo sem prova ("pode haver uma melhor", com o gap). DECISOES.md, "Redesenho", 02/10.

Ao subir o quadro, as pessoas acrescentadas entram primeiro como enfermeiros — ate o que a
demanda de enfermeiro exige em horas e ate a proporcao do grau — e depois como tecnicos.
Ninguem da equipe informada e retirado. O diagnostico do MOTIVO da inviabilidade e a
Etapa 7.
"""

from __future__ import annotations

import dataclasses
import io
import math
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "docs"))

import experimento_a as ea  # noqa: E402
import instancia_br as br  # noqa: E402
import modelo  # noqa: E402
from conferencia_descanso_escala import cumpre, fmt_semanal, medir  # noqa: E402

MARGEM = 12          # quantos quadros acima do informado tentar antes de desistir
TEMPO = 600          # limite da etapa 1, em segundos (decidido em 05/10)
# Limite da etapa 2 (equilibrio), decisao do Otavio em 05/10: max(120 s; 1,5 x o tempo em que
# o caso de 88 profissionais da rodada com folga chegou a 90% da reducao final, 81,1 s),
# arredondado para cima ao minuto: max(120; 121,7) -> 180 s. Ver PROPOSTAS.md, P1. A etapa 2
# usa o menor entre este e o limite da etapa 1 (os testes encurtam `TEMPO`).
TEMPO_ETAPA2 = 180

ADMITE, FALTAM, NAO_DECIDIDO, SEM_VIAVEL = "admite", "faltam", "nao_decidido", "sem_viavel"

# Modelos prontos de turnos: (nome, inicio, fim), em horas cheias.
MODELOS = {
    "12×36 (7h–19h / 19h–7h)": [("D", 7, 19), ("N", 19, 7)],
    "8 h em três turnos": [("M", 7, 15), ("T", 15, 23), ("N", 23, 7)],
    "6 h de dia + noturno de 12 h": [("M", 7, 13), ("T", 13, 19), ("N", 19, 7)],
}


def duracao(inicio: int, fim: int) -> int:
    return (fim - inicio) % 24 or 24


@dataclass
class Entrada:
    turnos: list[tuple[str, int, int]]                 # (nome, inicio, fim)
    grau: str                                           # grau de dependencia predominante
    n_enfermeiros: int
    n_tecnicos: int
    demanda_turno: dict[str, tuple[int, int]]           # nome -> (enfermeiros, tecnicos)
    demanda_fds: dict[str, tuple[int, int]] = field(default_factory=dict)
    demanda_data: dict[tuple[date, str, str], int] = field(default_factory=dict)
    fim_de_semana: str = "sab_dom"
    inicio: date | None = None
    nomes_enfermeiros: list[str] | None = None
    nomes_tecnicos: list[str] | None = None
    indisponibilidades: list[tuple[str, date, date]] = field(default_factory=list)
    pedidos: list[tuple[str, date]] = field(default_factory=list)
    pacientes: dict[str, float] | None = None           # painel "Conferir com o COFEN"
    # carga contratual semanal, por nome (ou id); quem nao aparece fica com 44 h, e quem a
    # varredura acrescenta tambem (DECISOES.md, "2026-10-02 — Carga por contrato")
    cargas: dict[str, float] = field(default_factory=dict)

    @property
    def quadro(self) -> int:
        return self.n_enfermeiros + self.n_tecnicos


@dataclass
class Resultado:
    veredito: str
    quadro_informado: int
    menor_viavel: int | None
    alertas: list[str]
    tentativas: list[tuple]                # (quadro, veredito ou "piso", enfermeiros, tecnicos)
    qp: tuple[float, float] | None = None  # (nucleo, completo), com pacientes informados
    inst: object = None
    escala: tuple = ()
    conformidade: dict | None = None
    indicadores: dict = field(default_factory=dict)
    diagnostico: tuple[str, str] | None = None   # (motivo, explicacao), sem escala legal
    chs: float | None = None               # CHS do QP: media das cargas contratuais

    @property
    def faltam(self) -> int | None:
        return None if self.menor_viavel is None else self.menor_viavel - self.quadro_informado

    @property
    def provado(self) -> bool:
        return bool(self.indicadores.get("provado"))

    def frase_escala(self) -> str:
        """(a) otimo provado -> "escala gerada"; (b) escala sem prova -> "pode haver uma
        melhor", com o gap da etapa 1 (DECISOES.md, "Redesenho", 02/10)."""
        if self.provado:
            return "Escala gerada."
        gap = self.indicadores.get("gap")
        if gap is None or math.isinf(gap):
            return "Escala gerada; pode haver uma melhor."
        gap_txt = f"{gap:.1%}".replace(".", ",")
        return (f"Escala gerada; pode haver uma melhor (gap {gap_txt}: distância máxima "
                f"até a melhor possível).")

    def frase(self) -> str:
        if self.veredito == ADMITE:
            return f"O quadro informado admite escala legal. {self.frase_escala()}"
        if self.veredito == FALTAM:
            return (f"{'Falta' if self.faltam == 1 else 'Faltam'} {self.faltam}; o menor "
                    f"quadro viável é {self.menor_viavel}. "
                    f"{self.frase_escala()}")
        if self.veredito == SEM_VIAVEL:
            return (f"Não há escala legal até {self.quadro_informado + MARGEM} profissionais; "
                    f"o menor quadro viável está acima disso.")
        # (c) tempo esgotado sem escala. NUNCA "faltam N": falta so se afirma com prova.
        if self.diagnostico:
            return ("Não foi possível gerar a escala no tempo disponível com mais "
                    "profissionais; o menor quadro viável não foi determinado.")
        return "Não foi possível gerar a escala no tempo disponível."


# --- montagem -----------------------------------------------------------------------------

def _horas_enfermeiro(e: Entrada) -> float:
    """Horas de posto de enfermeiro exigidas no horizonte — so enfermeiro cobre."""
    inst = montar(e)
    return sum(q * inst.turnos[s].duracao_h for (_, s), q in inst.demanda.items()
               if br.HABILIDADE_ENF in inst.turnos[s].habilidades)


def equipe(e: Entrada, acrescimo: int, horas_enf: float | None = None):
    """A equipe informada mais `acrescimo` pessoas: primeiro enfermeiros, ate o que a demanda
    de enfermeiro exige em horas e ate a proporcao do grau; depois tecnicos."""
    total = e.quadro + acrescimo
    pct = br.GRAUS[e.grau].pct_enfermeiros
    base = montar(e)
    cobrem = sum(base.horas_devidas(p.id) for p in base.profissionais.values()
                 if br.HABILIDADE_ENF in p.habilidades)
    falta_h = max(0.0, (horas_enf or 0) - cobrem)
    exigidos = max(math.ceil(pct * total - 1e-9),
                   e.n_enfermeiros + math.ceil(falta_h / _teto_padrao() - 1e-9))
    n_enf = max(e.n_enfermeiros, min(e.n_enfermeiros + acrescimo, exigidos))
    n_tec = total - n_enf
    extras_enf, extras_tec = n_enf - e.n_enfermeiros, n_tec - e.n_tecnicos
    nomes_enf = nomes_tec = None
    if e.nomes_enfermeiros is not None:
        nomes_enf = list(e.nomes_enfermeiros) + [
            f"Enf {e.n_enfermeiros + i + 1}" for i in range(extras_enf)]
    if e.nomes_tecnicos is not None:
        nomes_tec = list(e.nomes_tecnicos) + [
            f"Téc {e.n_tecnicos + i + 1}" for i in range(extras_tec)]
    return n_enf, n_tec, nomes_enf, nomes_tec


def _teto_padrao() -> float:
    """Teto no horizonte de quem a varredura acrescenta: 44 h, sem ferias."""
    return br.CARGA_CONTRATUAL_PADRAO * br.DIAS_HORIZONTE / 7


def montar(e: Entrada, acrescimo: int = 0, horas_enf: float | None = None,
           so_enfermeiros: bool = False):
    """So a instancia, sem resolver. Levanta ValueError com mensagem legivel se a entrada
    estiver errada (turno repetido, nome inexistente, data fora do horizonte...).

    `so_enfermeiros`: os `acrescimo` entram todos como enfermeiros — a segunda tentativa de
    cada quadro na varredura (ver `verificar`)."""
    if acrescimo == 0:
        n_enf, n_tec, nomes_enf, nomes_tec = (e.n_enfermeiros, e.n_tecnicos,
                                              e.nomes_enfermeiros, e.nomes_tecnicos)
    elif so_enfermeiros:
        n_enf, n_tec = e.n_enfermeiros + acrescimo, e.n_tecnicos
        nomes_enf = (None if e.nomes_enfermeiros is None else list(e.nomes_enfermeiros)
                     + [f"Enf {e.n_enfermeiros + i + 1}" for i in range(acrescimo)])
        nomes_tec = e.nomes_tecnicos
    else:
        n_enf, n_tec, nomes_enf, nomes_tec = equipe(e, acrescimo, horas_enf)
    return br.construir(
        turnos=[(nome, ini, duracao(ini, fim), nome) for nome, ini, fim in e.turnos],
        demanda_turno=e.demanda_turno, demanda_fds=e.demanda_fds,
        demanda_data=e.demanda_data, fim_de_semana=e.fim_de_semana, inicio=e.inicio,
        n_enfermeiros=n_enf, n_tecnicos=n_tec, nomes_enfermeiros=nomes_enf,
        nomes_tecnicos=nomes_tec, indisponibilidades=e.indisponibilidades,
        pedidos=e.pedidos, cargas=e.cargas)


def limite_efetivo(inst) -> int:
    """Maximo de dias seguidos que as regras DE FATO permitem.

    O contrato diz 6 (art. 67). Mas se a regra das 36 h proibe qualquer turno no dia seguinte
    a qualquer turno — so turnos de 12 h, como no 12x36 —, ninguem trabalha dois dias
    seguidos, e o limite efetivo e 1. E o que faz o piso de alternancia enxergar a soma de
    dois dias, como no Experimento A.
    """
    base = [(s, t.inicio.hour, t.duracao_h) for s, t in inst.turnos.items()
            if br.HABILIDADE_ENF not in t.habilidades]
    L = inst.contratos["0"].max_consecutive_working_days.valor
    pares = set(br.pares_proibidos_por_horario(base, L, descartar=False))
    if all((s, 1, t) in pares for s, _, _ in base for t, _, _ in base):
        return 1
    return L


def piso(inst) -> int:
    """Menor quadro que a aritmetica admite, sem solver: o informado mais quantos acrescimos
    de 44 h faltam para as horas da demanda caberem nos tetos individuais (carga contratual
    nos dias disponiveis), e a soma de dias seguidos quando o limite efetivo aperta."""
    horas = sum(q * inst.turnos[s].duracao_h for (_, s), q in inst.demanda.items())
    cobrem = sum(inst.horas_devidas(n) for n in inst.profissionais)
    capacidade = 0
    if horas > cobrem + 1e-9:
        capacidade = len(inst.profissionais) + math.ceil((horas - cobrem) / _teto_padrao()
                                                         - 1e-9)
    return max(capacidade, ea.piso_de_alternancia(inst, limite_efetivo(inst)))


def _faltam(k: int, singular: str, plural_: str) -> str:
    """"falta pelo menos 1 enfermeiro" / "faltam pelo menos 2 enfermeiros"."""
    return f"{'falta' if k == 1 else 'faltam'} pelo menos {br.plural(k, singular, plural_)}"


# --- veredito -----------------------------------------------------------------------------

def indicadores(inst, escala) -> dict:
    """O que a tela mostra ao lado da escala."""
    enf = {p.id for p in inst.profissionais.values() if br.HABILIDADE_ENF in p.habilidades}
    em_posto_tec = sum(1 for _, n, s in escala
                       if n in enf and br.HABILIDADE_ENF not in inst.turnos[s].habilidades)
    horas: dict[str, float] = {n: 0.0 for n in inst.profissionais}
    for _, n, s in escala:
        horas[n] += inst.turnos[s].duracao_h
    trabalhados = {(n, d) for d, n, _ in escala}
    pedidos = [p for p in inst.pedidos if p.tipo == "folga_dia"]
    atendidos = sum(1 for p in pedidos if (p.profissional, p.data) not in trabalhados)
    negados: dict[str, int] = {}
    for p in pedidos:
        if (p.profissional, p.data) in trabalhados:
            negados[p.profissional] = negados.get(p.profissional, 0) + 1
    f = fracoes(inst, escala) if inst.carga_semanal_h is not None else {}
    cat = por_categoria(inst, escala) if inst.carga_semanal_h is not None else {}
    return {"enf_em_posto_tec": em_posto_tec,
            "fracao_min": min(f.values(), default=0.0),
            "fracao_max": max(f.values(), default=0.0),
            "categorias": cat,
            "diferenca_categorias": (diferenca_entre_categorias(inst, escala)
                                     if inst.carga_semanal_h is not None else None),
            "negados_max": max(negados.values(), default=0),
            "com_pedido_negado": len(negados),
            "horas_min": min(horas.values()), "horas_max": max(horas.values()),
            "pedidos_total": len(pedidos), "pedidos_atendidos": atendidos,
            "atribuicoes": len(escala)}


# --- objetivo: pesos inteiros, depois equilibrio -------------------------------------------

def pesos(inst):
    """Objetivo da ferramenta em UMA resolucao, com pesos inteiros (DECISOES.md, "Redesenho"):

    - cada turno de enfermeiro em posto de tecnico custa 1;
    - cada pedido de folga nao atendido custa W = (maximo possivel de turnos de enfermeiro em
      posto de tecnico) + 1. O maximo possivel e o total de postos de tecnico do horizonte.

    Como W passa o maior custo que os postos de tecnico podem somar, negar um pedido nunca
    compensa: primeiro atendem-se os pedidos, depois evita-se enfermeiro em posto de tecnico.
    Devolve (instancia com os pedidos pesados, custo por atribuicao, W).
    """
    base = [s for s, t in inst.turnos.items() if br.HABILIDADE_ENF not in t.habilidades]
    enf = [p.id for p in inst.profissionais.values() if br.HABILIDADE_ENF in p.habilidades]
    maximo = sum(q for (_, s), q in inst.demanda.items() if s in base)
    W = maximo + 1
    inst = dataclasses.replace(
        inst, pedidos=tuple(dataclasses.replace(p, peso=W) for p in inst.pedidos))
    return inst, {(n, s): 1 for n in enf for s in base}, W


def resolver(m, tempo: int | None) -> tuple[str, object, bool, float | None]:
    """Resolve um modelo ja montado. Devolve (veredito, escala ou None, provou_otimo, gap).

    O veredito de `ea.resolver_modelo` junta "otimo provado" e "solucao no limite de tempo"
    em VIAVEL; a tela precisa separar os dois (escala gerada / pode haver uma melhor). Nunca
    levanta: excecao do solver vira ERRO, como em `ea.resolver_modelo`."""
    try:
        resultado = modelo.resolver(m, solver=modelo.SOLVER_PADRAO, tempo_limite=tempo,
                                    carregar=False)
    except Exception as e:  # noqa: BLE001
        print(f"      [ERRO] o solver levantou {type(e).__name__}: {e}")
        return ea.ERRO, None, False, None
    veredito = ea.classificar(resultado)
    if veredito != ea.VIAVEL:
        return veredito, None, False, None
    if not modelo.carregar_solucao(m, resultado):
        print("      [ERRO] solver declarou viavel mas nao entregou solucao")
        return ea.ERRO, None, False, None
    return (veredito, modelo.atribuicoes(m), modelo.provou_otimo(resultado),
            modelo.gap_relativo(resultado))


def equilibrar(m, inst, z: int, tempo: int | None) -> tuple[str, object, bool, float | None]:
    """Segunda etapa: com a penalidade total presa no otimo `z`, minimiza a amplitude da
    FRACAO CUMPRIDA — horas trabalhadas / horas devidas (carga contratual nos dias
    disponiveis), maior menos menor — DENTRO de cada categoria: amplitude entre enfermeiros
    + amplitude entre tecnicos (DECISOES.md, "2026-10-02 — Carga por contrato", P6 decidida
    em 03/10). A diferenca ENTRE categorias nao e otimizada: vem da demanda de cada posto
    frente ao tamanho de cada categoria, e e mostrada a parte (`por_categoria`). O mecanismo
    e o do Experimento B (fixar o otimo, otimizar um segundo criterio), sobre o mesmo modelo,
    sem monta-lo de novo; muda o criterio."""
    preparar_equilibrio(m, inst, z)
    return resolver(m, tempo)


def categoria(inst, n: str) -> str:
    """ENF ou TEC: a categoria do profissional, pela habilidade."""
    return ENF if br.HABILIDADE_ENF in inst.profissionais[n].habilidades else TEC


ENF, TEC = "enfermeiros", "tecnicos"
NOME_CATEGORIA = {ENF: "Enfermeiros", TEC: "Técnicos"}


def preparar_equilibrio(m, inst, z: int) -> None:
    """Troca o objetivo do modelo pelo da etapa 2, sem resolver. Separado de `equilibrar`
    para a curva de escalabilidade (`src/escalabilidade_objetivo.py`) resolver por conta
    propria e cronometrar."""
    import pyomo.environ as pyo
    # quem nao tem dia disponivel nao deve hora nenhuma: fica fora da fracao
    devidas = {n: inst.horas_devidas(n) for n in inst.profissionais}
    termos: dict[str, list] = {n: [] for n, h in devidas.items() if h > 0}
    for (n, s, d) in m.X:
        if n in termos:
            termos[n].append(inst.turnos[s].duracao_h * m.x[n, s, d])
    grupos = sorted({categoria(inst, n) for n in termos})
    m.objetivo.deactivate()
    m.total_no_otimo = pyo.Constraint(expr=m.objetivo.expr == z)
    m.fracao = pyo.Expression(list(termos), rule=lambda m, n: sum(termos[n]) / devidas[n])
    m.f_max = pyo.Var(grupos, domain=pyo.NonNegativeReals)
    m.f_min = pyo.Var(grupos, domain=pyo.NonNegativeReals)
    m.teto_fracao = pyo.Constraint(list(termos),
                                   rule=lambda m, n: m.f_max[categoria(inst, n)] >= m.fracao[n])
    m.piso_fracao = pyo.Constraint(list(termos),
                                   rule=lambda m, n: m.f_min[categoria(inst, n)] <= m.fracao[n])
    m.objetivo_equilibrio = pyo.Objective(
        expr=sum(m.f_max[g] - m.f_min[g] for g in grupos), sense=pyo.minimize)


def fracoes(inst, escala) -> dict[str, float]:
    """Fracao cumprida por profissional: horas trabalhadas / horas devidas nos dias
    disponiveis. Quem nao deve hora nenhuma (o periodo todo de ferias) fica de fora."""
    horas = {n: 0.0 for n in inst.profissionais}
    for _, n, s in escala:
        horas[n] += inst.turnos[s].duracao_h
    return {n: h / inst.horas_devidas(n) for n, h in horas.items()
            if inst.horas_devidas(n) > 0}


def por_categoria(inst, escala) -> dict[str, dict]:
    """Por categoria: faixa e amplitude da fracao cumprida, fracao media (horas escaladas /
    horas contratadas nos dias disponiveis) e HORAS DE CONTRATO NAO UTILIZADAS (contratadas
    nos dias disponiveis - escaladas). So leitura da escala; nao entra no modelo."""
    f = fracoes(inst, escala)
    horas = {n: 0.0 for n in inst.profissionais}
    for _, n, s in escala:
        horas[n] += inst.turnos[s].duracao_h
    duracoes = {t.duracao_h for t in inst.turnos.values()}
    saida = {}
    for g in (ENF, TEC):
        membros = [n for n in inst.profissionais if categoria(inst, n) == g]
        if not membros:
            continue
        fg = [f[n] for n in membros if n in f]
        devidas = sum(inst.horas_devidas(n) for n in membros)
        escaladas = sum(horas[n] for n in membros)
        # diferenca maxima de carga entre colegas (decisao de 05/10): o desvio de cada um em
        # relacao a sua parte justa — a fracao media da categoria aplicada as SUAS horas
        # devidas —, maior menos menor. Com contrato e disponibilidade iguais, e a diferenca
        # de horas entre quem mais e quem menos trabalhou; com ferias ou contratos
        # diferentes, nao pune quem deve menos horas.
        media = escaladas / devidas if devidas else 0.0
        desvio = [horas[n] - media * inst.horas_devidas(n) for n in membros
                  if inst.horas_devidas(n) > 0]
        dif_h = max(desvio) - min(desvio) if desvio else 0.0
        saida[g] = {"diferenca_h": dif_h,
                    "diferenca_plantoes": (dif_h / next(iter(duracoes))
                                           if len(duracoes) == 1 else None),
                    "fracao_min": min(fg, default=0.0), "fracao_max": max(fg, default=0.0),
                    "amplitude": max(fg) - min(fg) if fg else 0.0,
                    "fracao_media": media,
                    "devidas": devidas, "escaladas": escaladas,
                    "nao_utilizadas": devidas - escaladas}
    return saida


def amplitude(inst, escala) -> float:
    """O criterio da etapa 2: (maior - menor fracao cumprida) entre enfermeiros + o mesmo
    entre tecnicos. 0 = dentro de cada categoria, todos cumprem a mesma parte do contrato."""
    return sum(c["amplitude"] for c in por_categoria(inst, escala).values())


def fmt_diferenca(cat: dict) -> str:
    """"1 plantão (12 h)", "0,7 plantão (8 h)", "nenhuma (0 h)"; so horas se os turnos
    tiverem duracoes diferentes."""
    h = cat["diferenca_h"]
    if h < 0.05:
        return "nenhuma (0 h)"
    horas = f"{h:.0f} h" if abs(h - round(h)) < 0.05 else f"{h:.1f} h".replace(".", ",")
    p = cat.get("diferenca_plantoes")
    if p is None:
        return horas
    if abs(p - round(p)) < 0.05:
        n = round(p)
        return f"{n} plant{'ão' if n == 1 else 'ões'} ({horas})"
    return f"{p:.1f} plantão ({horas})".replace(".", ",", 1)


def diferenca_entre_categorias(inst, escala) -> float | None:
    """Fracao media dos tecnicos - fracao media dos enfermeiros. Mostrada a parte, nao
    otimizada (P6, 03/10). None se faltar uma das categorias."""
    c = por_categoria(inst, escala)
    return c[TEC]["fracao_media"] - c[ENF]["fracao_media"] if ENF in c and TEC in c else None


def resolver_com_objetivo(inst, tempo: int | None) -> tuple[str, object, object, dict]:
    """Etapa 1 (pesos) e, havendo escala provada otima, etapa 2 (equilibrio de horas).

    A etapa 2 so roda com a etapa 1 provada OTIMA: fixar num valor que nao e o otimo mediria
    o equilibrio de outra coisa. Roda tambem com penalidade zero — a carga pode estar
    desequilibrada mesmo sem pedido negado. `info["provado"]` e `info["gap"]` sao os da
    etapa 1, que e o que diz se pode haver escala melhor."""
    import time
    inst, custo, W = pesos(inst)
    m = ea.modelo_br(inst, custo)
    t0 = time.time()
    veredito, escala, provado, gap = resolver(m, tempo)
    info = {"peso_pedido": W, "tempo_etapa1": time.time() - t0, "tempo_etapa2": 0.0,
            "provado": provado, "gap": gap, "etapa2": "nao rodou"}
    if veredito != ea.VIAVEL:
        return veredito, inst, None, info
    z = modelo.valor_objetivo(m)
    info["penalidade"] = z
    info["amplitude_etapa1"] = amplitude(inst, escala)
    if not provado:
        info["etapa2"] = "não rodou: a etapa 1 não provou o ótimo no tempo disponível"
        return veredito, inst, escala, info
    t0 = time.time()
    tempo2 = TEMPO_ETAPA2 if tempo is None else min(TEMPO_ETAPA2, tempo)
    v2, escala2, provado2, gap2 = equilibrar(m, inst, z, tempo2)
    info["tempo_etapa2"] = time.time() - t0
    if v2 == ea.VIAVEL:
        info.update(etapa2="ok", provado_etapa2=provado2, gap_etapa2=gap2,
                    amplitude=amplitude(inst, escala2))
        return veredito, inst, escala2, info
    info["etapa2"] = f"sem resposta ({v2}); fica a escala da etapa 1"
    return veredito, inst, escala, info


# --- diagnostico da trava ----------------------------------------------------------------

HORAS, ALTERNANCIA, CATEGORIA, DIA, COMBINACAO = (
    "horas", "alternancia", "categoria", "dia", "combinacao")
TITULO = {HORAS: "Horas", ALTERNANCIA: "Alternância do plantão de 12 h",
          CATEGORIA: "Categoria", DIA: "Dia específico", COMBINACAO: "Combinação de regras"}


def diagnosticar(inst) -> tuple[str, str]:
    """Por que o quadro informado nao tem escala legal: o diagnostico MAIS SIMPLES que se
    aplica, nesta ordem (especificacao, Etapa 7). Devolve (motivo, explicacao).

    So contas, sem solver. Chamado quando o quadro informado ja foi provado inviavel (pelo
    solver ou pelo piso); se nenhuma conta simples explica, e a combinacao de regras.
    """
    enf = {p.id for p in inst.profissionais.values() if br.HABILIDADE_ENF in p.habilidades}
    N, E = len(inst.profissionais), len(enf)
    cobrem = sum(inst.horas_devidas(n) for n in inst.profissionais)
    cobrem_enf = sum(inst.horas_devidas(n) for n in enf)
    teto = _teto_padrao()
    dur = {s: t.duracao_h for s, t in inst.turnos.items()}
    posto_enf = {s for s, t in inst.turnos.items() if br.HABILIDADE_ENF in t.habilidades}
    por_dia = {d: sum(inst.demanda_de(d, s) for s in inst.turnos) for d in inst.dias}
    enf_dia = {d: sum(inst.demanda_de(d, s) for s in posto_enf) for d in inst.dias}

    horas = sum(q * dur[s] for (_, s), q in inst.demanda.items())
    if horas > cobrem + 1e-9:
        k = math.ceil((horas - cobrem) / teto - 1e-9)
        return HORAS, (f"A demanda do período soma {horas:g} h. Pelas cargas contratuais, "
                       f"descontadas férias e licenças, as {N} pessoas trabalham no máximo "
                       f"{cobrem:.0f} h. Pela conta, {_faltam(k, 'profissional', 'profissionais')} "
                       f"de {br.CARGA_CONTRATUAL_PADRAO:g} h.")

    L = limite_efetivo(inst)
    if L == 1:
        d, soma = max(((inst.dias[i], por_dia[inst.dias[i]] + por_dia[inst.dias[i + 1]])
                       for i in range(len(inst.dias) - 1)), key=lambda x: x[1])
        if soma > N:
            return ALTERNANCIA, (
                f"Com plantões de 12 h ninguém trabalha dois dias seguidos (a folga depois do "
                f"plantão é de 36 h). {rotulo_dia(d)} e {rotulo_dia(d + timedelta(days=1))} "
                f"somam {soma} plantões, que precisam de {soma} pessoas diferentes; a equipe "
                f"tem {N}. Pela conta, {_faltam(soma - N, 'pessoa', 'pessoas')}.")

    horas_enf = sum(q * dur[s] for (_, s), q in inst.demanda.items() if s in posto_enf)
    if horas_enf > cobrem_enf + 1e-9:
        k = math.ceil((horas_enf - cobrem_enf) / teto - 1e-9)
        return CATEGORIA, (f"Os turnos que pedem enfermeiro somam {horas_enf:g} h, e só "
                           f"enfermeiro os cobre. Pelas cargas contratuais, {E} enfermeiros "
                           f"trabalham no máximo {cobrem_enf:.0f} h. Pela conta, "
                           f"{_faltam(k, 'enfermeiro', 'enfermeiros')} de "
                           f"{br.CARGA_CONTRATUAL_PADRAO:g} h.")
    if L == 1:
        d, soma = max(((inst.dias[i], enf_dia[inst.dias[i]] + enf_dia[inst.dias[i + 1]])
                       for i in range(len(inst.dias) - 1)), key=lambda x: x[1])
        if soma > E:
            return CATEGORIA, (f"{rotulo_dia(d)} e {rotulo_dia(d + timedelta(days=1))} pedem "
                               f"{soma} plantões de enfermeiro, que precisam de {soma} "
                               f"enfermeiros diferentes; há {E}. Pela conta, "
                               f"{_faltam(soma - E, 'enfermeiro', 'enfermeiros')}.")

    for d in inst.dias:
        fora = {n for n, dd in inst.indisponiveis if dd == d}
        livres, livres_enf = N - len(fora), E - len(fora & enf)
        if livres < por_dia[d] or livres_enf < enf_dia[d]:
            return DIA, (f"Em {rotulo_dia(d)}, descontadas férias e licenças, sobram "
                         f"{br.plural(livres, 'pessoa', 'pessoas')} "
                         f"({br.plural(livres_enf, 'enfermeiro', 'enfermeiros')}) para "
                         f"{br.plural(por_dia[d], 'posto', 'postos')} "
                         f"({enf_dia[d]} de enfermeiro).")

    return COMBINACAO, ("Nenhuma conta simples explica: horas, alternância, categoria e cada "
                        "dia fecham separados. O solver provou que as regras juntas — "
                        "descanso entre turnos, dias seguidos, férias e licenças — não "
                        "admitem escala com este quadro.")


def _faltam(k: int, singular: str, plural_: str) -> str:
    """"falta pelo menos 1 enfermeiro" / "faltam pelo menos 2 enfermeiros"."""
    return f"{'falta' if k == 1 else 'faltam'} pelo menos {br.plural(k, singular, plural_)}"


# --- veredito -----------------------------------------------------------------------------

def verificar(e: Entrada, progresso=lambda frac, msg: None, tempo: int | None = None,
              margem: int = MARGEM) -> Resultado:
    """Veredito do quadro, com a escala do menor quadro viavel encontrado.

    Cada quadro acima do informado e tentado com a composicao da regra (`equipe`) e, se der
    inviavel, com todos os acrescimos como enfermeiros: enfermeiro cobre tudo o que tecnico
    cobre, entao se esta segunda tambem e inviavel, nenhuma composicao desse tamanho fecha.
    """
    tempo = TEMPO if tempo is None else tempo  # lido na chamada: os testes o encurtam
    base = montar(e)                          # valida a entrada antes de gastar solver
    horas_enf = _horas_enfermeiro(e)
    alertas = br.alertas_cofen(base, e.grau, e.pacientes)
    chs = br.chs(base)
    qp = br.quadro_pessoal(br.horas_por_dia(e.pacientes), chs) if e.pacientes else None
    minimo = piso(base)
    r = Resultado(veredito=NAO_DECIDIDO, quadro_informado=e.quadro, menor_viavel=None,
                  alertas=alertas, tentativas=[], qp=qp, chs=chs)

    decidido = True
    for acrescimo in range(0, margem + 1):
        quadro = e.quadro + acrescimo
        progresso(acrescimo / (margem + 1), f"testando quadro de {quadro} profissionais")
        if quadro < minimo:
            r.tentativas.append((quadro, "piso", None, None))   # aritmetica, sem solver
            continue
        candidatas = [montar(e, acrescimo, horas_enf)]
        if acrescimo:
            so_enf = montar(e, acrescimo, horas_enf, so_enfermeiros=True)
            if so_enf.profissionais.keys() != candidatas[0].profissionais.keys() or \
                    _n_enf(so_enf) != _n_enf(candidatas[0]):
                candidatas.append(so_enf)
        for inst in candidatas:
            veredito, inst, escala, info = resolver_com_objetivo(inst, tempo)
            r.tentativas.append((quadro, veredito, _n_enf(inst),
                                 len(inst.profissionais) - _n_enf(inst)))
            if veredito != ea.INVIAVEL:
                break
        if veredito == ea.VIAVEL:
            r.veredito = ADMITE if acrescimo == 0 else FALTAM
            r.menor_viavel, r.inst, r.escala = quadro, inst, escala
            m = medir(inst, escala)
            r.conformidade = {"ok": cumpre(inst, m), **m}
            r.indicadores = {**indicadores(inst, escala), **info}
            break
        if veredito != ea.INVIAVEL:
            decidido = False     # indeterminado ou erro: o minimo nao esta provado acima
            break
    if r.veredito != ADMITE and r.tentativas and r.tentativas[0][1] in ("piso", ea.INVIAVEL):
        r.diagnostico = diagnosticar(base)
    if decidido and r.veredito == NAO_DECIDIDO:
        r.veredito = SEM_VIAVEL  # toda a faixa foi provada inviavel
    progresso(1.0, "concluido")
    return r


def _n_enf(inst) -> int:
    return sum(1 for p in inst.profissionais.values() if br.HABILIDADE_ENF in p.habilidades)


# --- planilha -----------------------------------------------------------------------------

DIAS_PT = ("seg", "ter", "qua", "qui", "sex", "sáb", "dom")


def rotulo_dia(d: date) -> str:
    return f"{DIAS_PT[d.weekday()]} {d:%d/%m}"


def planilha(r: Resultado, e: Entrada) -> bytes:
    """A escala em .xlsx: aba Escala (profissional x dia), Resumo e Legenda."""
    import pandas as pd

    inst = r.inst
    rotulo = {s: (t.id[:-1] + "*" if br.HABILIDADE_ENF in t.habilidades else t.id)
              for s, t in inst.turnos.items()}
    dias = inst.dias
    grade = {p.nome: [""] * len(dias) for p in inst.profissionais.values()}
    for d, n, s in r.escala:
        grade[inst.profissionais[n].nome][inst.indice(d)] = rotulo[s]
    for n, d in inst.indisponiveis:
        grade[inst.profissionais[n].nome][inst.indice(d)] = "indisp."
    categoria = {p.nome: ("Enfermeiro" if br.HABILIDADE_ENF in p.habilidades else "Técnico")
                 for p in inst.profissionais.values()}
    escala = pd.DataFrame.from_dict(grade, orient="index", columns=[rotulo_dia(d) for d in dias])
    escala.insert(0, "Categoria", [categoria[n] for n in escala.index])
    escala.insert(1, "Turnos", [sum(1 for c in linha if c and c != "indisp.")
                                for linha in grade.values()])
    escala.index.name = "Profissional"

    c, ind = r.conformidade or {}, r.indicadores
    linhas = [
        ("Veredito", r.frase()),
        ("Quadro informado", r.quadro_informado),
        ("Quadro desta escala", r.menor_viavel),
        ("Período", f"{inst.inicio:%d/%m/%Y} a {inst.fim:%d/%m/%Y}"),
        ("Grau de dependência predominante", br.NOME_GRAU.get(e.grau, e.grau)),
        ("Turnos de enfermeiro em posto de técnico", ind.get("enf_em_posto_tec")),
        ("Pedidos de folga atendidos",
         f"{ind.get('pedidos_atendidos')} de {ind.get('pedidos_total')}"),
        ("Carga horária no período (mín.–máx.)",
         f"{ind.get('horas_min', 0):g}–{ind.get('horas_max', 0):g} h"),
        ("Fração do contrato cumprida (mín.–máx.)",
         f"{ind.get('fracao_min', 0):.0%}–{ind.get('fracao_max', 0):.0%}"),
    ]
    for g, cat in ind.get("categorias", {}).items():
        nome = NOME_CATEGORIA[g].lower()
        linhas += [
            (f"Diferença máxima de carga entre colegas, {nome}", fmt_diferenca(cat)),
            (f"Fração do contrato cumprida, {nome} (mín.–máx.)",
             f"{cat['fracao_min']:.0%}–{cat['fracao_max']:.0%}"),
            (f"Horas de contrato não utilizadas, {nome}",
             f"{cat['nao_utilizadas']:.0f} h de {cat['devidas']:.0f} h contratadas nos dias "
             f"disponíveis"),
        ]
    if ind.get("diferenca_categorias") is not None:
        linhas.append(("Diferença entre categorias na fração média (técnicos − enfermeiros; "
                       "não otimizada)", f"{ind['diferenca_categorias'] * 100:+.0f} pp"))
    linhas += [
        ("Descanso mínimo entre turnos (medido)", f"{c.get('menor_geral', 0):.0f} h"),
        ("Descanso semanal mínimo (medido)", fmt_semanal(c.get("menor_semanal", 0))),
        ("Maior sequência de dias trabalhados", c.get("max_consec")),
        ("Conferência de descanso", "cumpre" if c.get("ok") else "NÃO CUMPRE"),
    ]
    if r.qp:
        linhas += [("CHS do QP (média das cargas contratuais)", f"{r.chs:g} h"),
                   ("QP núcleo assistencial (sem IST)", round(r.qp[0], 2)),
                   ("QP completo (com IST de 15%)", round(r.qp[1], 2))]
    linhas += [("Alerta COFEN (não impede a escala)", a) for a in r.alertas]
    resumo = pd.DataFrame(linhas, columns=["Item", "Valor"])
    legenda = pd.DataFrame(
        [(rotulo[s], f"{t.inicio:%H:%M}", f"{t.fim:%H:%M}",
          "posto de enfermeiro" if br.HABILIDADE_ENF in t.habilidades
          else "posto de técnico (enfermeiro também pode cobrir)")
         for s, t in inst.turnos.items()]
        + [("indisp.", "", "", "férias ou licença")],
        columns=["Código", "Início", "Fim", "Descrição"])

    saida = io.BytesIO()
    with pd.ExcelWriter(saida, engine="openpyxl") as w:
        escala.to_excel(w, sheet_name="Escala")
        resumo.to_excel(w, sheet_name="Resumo", index=False)
        legenda.to_excel(w, sheet_name="Legenda", index=False)
    return saida.getvalue()


def proxima_segunda(hoje: date | None = None) -> date:
    hoje = hoje or date.today()
    return hoje + timedelta(days=(7 - hoje.weekday()) % 7 or 7)
