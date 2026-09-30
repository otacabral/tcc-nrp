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
- **nao decidido** — o solver bateu no limite de tempo. Nunca e contado como inviavel.

Ao subir o quadro, as pessoas acrescentadas entram primeiro como enfermeiros — ate o que a
demanda de enfermeiro exige em horas e ate a proporcao do grau — e depois como tecnicos.
Ninguem da equipe informada e retirado. O diagnostico do MOTIVO da inviabilidade e a
Etapa 7.
"""

from __future__ import annotations

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
TEMPO = 600          # limite por resolucao, em segundos

ADMITE, FALTAM, NAO_DECIDIDO = "admite", "faltam", "nao_decidido"

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

    @property
    def quadro(self) -> int:
        return self.n_enfermeiros + self.n_tecnicos


@dataclass
class Resultado:
    veredito: str
    quadro_informado: int
    menor_viavel: int | None
    alertas: list[str]
    tentativas: list[tuple[int, str]]      # (quadro, veredito ou "piso")
    qp: tuple[float, float] | None = None  # (nucleo, completo), com pacientes informados
    inst: object = None
    escala: tuple = ()
    conformidade: dict | None = None
    indicadores: dict = field(default_factory=dict)

    @property
    def faltam(self) -> int | None:
        return None if self.menor_viavel is None else self.menor_viavel - self.quadro_informado

    def frase(self) -> str:
        if self.veredito == ADMITE:
            return "O quadro informado admite escala legal."
        if self.veredito == FALTAM:
            return f"Faltam {self.faltam}; o menor quadro viável é {self.menor_viavel}."
        return ("Não decidido: o solver atingiu o limite de tempo antes de concluir. "
                "O quadro mínimo não foi determinado.")


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
    carga = br.CARGA_SEMANAL * br.DIAS_HORIZONTE / 7
    exigidos = max(math.ceil(pct * total - 1e-9),
                   math.ceil((horas_enf or 0) / carga - 1e-9))
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


def montar(e: Entrada, acrescimo: int = 0, horas_enf: float | None = None):
    """So a instancia, sem resolver. Levanta ValueError com mensagem legivel se a entrada
    estiver errada (turno repetido, nome inexistente, data fora do horizonte...)."""
    n_enf, n_tec, nomes_enf, nomes_tec = (
        (e.n_enfermeiros, e.n_tecnicos, e.nomes_enfermeiros, e.nomes_tecnicos)
        if acrescimo == 0 else equipe(e, acrescimo, horas_enf))
    return br.construir(
        turnos=[(nome, ini, duracao(ini, fim), nome) for nome, ini, fim in e.turnos],
        demanda_turno=e.demanda_turno, demanda_fds=e.demanda_fds,
        demanda_data=e.demanda_data, fim_de_semana=e.fim_de_semana, inicio=e.inicio,
        n_enfermeiros=n_enf, n_tecnicos=n_tec, nomes_enfermeiros=nomes_enf,
        nomes_tecnicos=nomes_tec, indisponibilidades=e.indisponibilidades,
        pedidos=e.pedidos)


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
    """Menor quadro que a aritmetica admite: horas de demanda / teto de horas por pessoa, e
    a soma de dias seguidos quando o limite efetivo de dias seguidos aperta. Sem solver."""
    horas = sum(q * inst.turnos[s].duracao_h for (_, s), q in inst.demanda.items())
    capacidade = math.ceil(horas / inst.carga_maxima_h - 1e-9)
    return max(capacidade, ea.piso_de_alternancia(inst, limite_efetivo(inst)))


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
    return {"enf_em_posto_tec": em_posto_tec,
            "horas_min": min(horas.values()), "horas_max": max(horas.values()),
            "pedidos_total": len(pedidos), "pedidos_atendidos": atendidos,
            "atribuicoes": len(escala)}


def verificar(e: Entrada, progresso=lambda frac, msg: None, tempo: int = TEMPO,
              margem: int = MARGEM) -> Resultado:
    """Veredito do quadro, com a escala do menor quadro viavel encontrado."""
    base = montar(e)                          # valida a entrada antes de gastar solver
    horas_enf = _horas_enfermeiro(e)
    alertas = br.alertas_cofen(base, e.grau, e.pacientes)
    qp = br.quadro_pessoal(br.horas_por_dia(e.pacientes)) if e.pacientes else None
    minimo = piso(base)
    r = Resultado(veredito=NAO_DECIDIDO, quadro_informado=e.quadro, menor_viavel=None,
                  alertas=alertas, tentativas=[], qp=qp)

    for acrescimo in range(0, margem + 1):
        quadro = e.quadro + acrescimo
        progresso(acrescimo / (margem + 1), f"testando quadro de {quadro} profissionais")
        if quadro < minimo:
            # inviavel pela aritmetica, sem solver
            r.tentativas.append((quadro, "piso"))
            continue
        inst = montar(e, acrescimo, horas_enf)
        veredito, inst, escala = ea.resolver_instancia(inst, modelo.SOLVER_PADRAO, tempo)
        r.tentativas.append((quadro, veredito))
        if veredito == ea.VIAVEL:
            r.veredito = ADMITE if acrescimo == 0 else FALTAM
            r.menor_viavel, r.inst, r.escala = quadro, inst, escala
            m = medir(inst, escala)
            r.conformidade = {"ok": cumpre(inst, m), **m}
            r.indicadores = indicadores(inst, escala)
            break
        if veredito != ea.INVIAVEL:
            # indeterminado ou erro: nao da para dizer que o minimo esta acima daqui
            break
    progresso(1.0, "concluido")
    return r


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
        ("Grau de dependência predominante", e.grau),
        ("Turnos de enfermeiro em posto de técnico", ind.get("enf_em_posto_tec")),
        ("Pedidos de folga atendidos",
         f"{ind.get('pedidos_atendidos')} de {ind.get('pedidos_total')}"),
        ("Carga horária no período (mín.–máx.)",
         f"{ind.get('horas_min', 0):g}–{ind.get('horas_max', 0):g} h"),
        ("Descanso mínimo entre turnos (medido)", f"{c.get('menor_geral', 0):.0f} h"),
        ("Descanso semanal mínimo (medido)", fmt_semanal(c.get("menor_semanal", 0))),
        ("Maior sequência de dias trabalhados", c.get("max_consec")),
        ("Conferência de descanso", "cumpre" if c.get("ok") else "NÃO CUMPRE"),
    ]
    if r.qp:
        linhas += [("QP núcleo assistencial (sem IST)", round(r.qp[0], 2)),
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
