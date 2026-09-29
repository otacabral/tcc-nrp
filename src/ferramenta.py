"""A ferramenta, sem tela: entrada do formulario -> veredito do quadro, escala e planilha.

`src/app.py` e so a casca Streamlit em volta disto. Separado de proposito: o que decide o
veredito tem de poder ser testado sem navegador (`src/testes_ferramenta.py`).

Entradas: as da especificacao (DECISOES.md, 29/09). Pacientes por grau, regime, equipe por
quantidade com nomes opcionais, razao fim de semana / dia util, inicio numa segunda-feira,
indisponibilidades. Sem opcoes avancadas.

Resolve com as MESMAS opcoes de modelo do Experimento A (`experimento_a.tentar`): limites
legais rigidos, habilidade rigida, regra de teto. Nao ha copia dessa configuracao aqui.

O veredito do quadro:

- **admite escala legal** — o quadro informado tem escala que cumpre cobertura e lei;
- **faltam N; o menor quadro viavel e X** — o quadro informado e inviavel, com prova do
  solver, e X e o primeiro viavel subindo o quadro. Os quadros entre o informado e X foram
  provados inviaveis pelo solver ou pela aritmetica (pisos de capacidade e de alternancia);
- **nao decidido** — o solver bateu no limite de tempo em algum quadro. Nunca e contado como
  inviavel.

Ao subir o quadro, as pessoas acrescentadas entram primeiro como enfermeiros, ate a proporcao
do Parecer, e depois como tecnicos. Ninguem da equipe informada e retirado.
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


@dataclass
class Entrada:
    pacientes: dict[str, float]
    regime: str
    n_enfermeiros: int
    n_tecnicos: int
    razao_fds: float = 1.0
    inicio: date | None = None
    nomes_enfermeiros: list[str] | None = None
    nomes_tecnicos: list[str] | None = None
    indisponibilidades: list[tuple[str, date, date]] = field(default_factory=list)

    @property
    def grau(self) -> str:
        return br.grau_de_maior_carga(self.pacientes)

    @property
    def quadro(self) -> int:
        return self.n_enfermeiros + self.n_tecnicos


@dataclass
class Resultado:
    veredito: str
    quadro_informado: int
    menor_viavel: int | None
    grau: str
    horas_dia: float
    qp_nucleo: float
    qp_completo: float
    avisos: list[str]
    tentativas: list[tuple[int, str]]      # (quadro, veredito ou "piso")
    inst: object = None
    escala: tuple = ()
    conformidade: dict | None = None

    @property
    def faltam(self) -> int | None:
        return None if self.menor_viavel is None else self.menor_viavel - self.quadro_informado

    def frase(self) -> str:
        if self.veredito == ADMITE:
            return "O quadro informado admite escala legal."
        if self.veredito == FALTAM:
            return (f"Faltam {self.faltam}; o menor quadro viável é {self.menor_viavel}.")
        return ("Não decidido: o solver atingiu o limite de tempo antes de concluir. "
                "O quadro mínimo não foi determinado.")


def equipe(e: Entrada, acrescimo: int) -> tuple[int, int, list[str] | None, list[str] | None]:
    """A equipe informada mais `acrescimo` pessoas: enfermeiros ate a proporcao, depois tecnicos."""
    total = e.quadro + acrescimo
    pct = br.GRAUS[e.grau].pct_enfermeiros
    n_enf = max(e.n_enfermeiros,
                min(e.n_enfermeiros + acrescimo, math.ceil(pct * total - 1e-9)))
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


def _parametros(e: Entrada, acrescimo: int) -> dict:
    n_enf, n_tec, nomes_enf, nomes_tec = equipe(e, acrescimo)
    return dict(pacientes=e.pacientes, razao_fds=e.razao_fds, inicio=e.inicio,
                n_enfermeiros=n_enf, n_tecnicos=n_tec, nomes_enfermeiros=nomes_enf,
                nomes_tecnicos=nomes_tec, indisponibilidades=e.indisponibilidades)


def montar(e: Entrada, acrescimo: int = 0):
    """So a instancia, sem resolver. Levanta ValueError com mensagem legivel se a entrada
    estiver errada (grau desconhecido, nome repetido, data fora do horizonte...)."""
    return br.construir(grau=e.grau, regime=e.regime, **_parametros(e, acrescimo))


def verificar(e: Entrada, progresso=lambda frac, msg: None, tempo: int = TEMPO,
              margem: int = MARGEM) -> Resultado:
    """Veredito do quadro, com a escala do menor quadro viavel encontrado."""
    base = montar(e)                          # valida a entrada antes de gastar solver
    h_dia = br.horas_por_dia(e.pacientes)
    nucleo, completo = br.quadro_pessoal(h_dia)
    avisos = br.conferir_composicao(base, e.grau)
    piso = max(ea.piso_de_capacidade(base, e.regime), ea.piso_de_alternancia(base))
    tentativas: list[tuple[int, str]] = []
    r = Resultado(veredito=NAO_DECIDIDO, quadro_informado=e.quadro, menor_viavel=None,
                  grau=e.grau, horas_dia=h_dia, qp_nucleo=nucleo, qp_completo=completo,
                  avisos=avisos, tentativas=tentativas)

    for acrescimo in range(0, margem + 1):
        quadro = e.quadro + acrescimo
        progresso(acrescimo / (margem + 1), f"testando quadro de {quadro} profissionais")
        if quadro < piso:
            # inviavel pela aritmetica, sem solver: capacidade ou alternancia nao cobrem
            tentativas.append((quadro, "piso"))
            continue
        veredito, inst, escala = ea.tentar(e.grau, e.regime, "teto", quadro,
                                           modelo.SOLVER_PADRAO, tempo,
                                           **_parametros(e, acrescimo))
        tentativas.append((quadro, veredito))
        if veredito == ea.VIAVEL:
            r.veredito = ADMITE if acrescimo == 0 else FALTAM
            r.menor_viavel, r.inst, r.escala = quadro, inst, escala
            m = medir(inst, escala)
            r.conformidade = {"ok": cumpre(inst, m), **m}
            break
        if veredito != ea.INVIAVEL:
            # indeterminado ou erro: nao da para dizer que o minimo esta acima daqui
            break
    progresso(1.0, "concluido")
    return r


# --- planilha -----------------------------------------------------------------------------

DIAS_PT = ("seg", "ter", "qua", "qui", "sex", "sáb", "dom")


def planilha(r: Resultado, e: Entrada) -> bytes:
    """A escala em .xlsx: aba Escala (profissional x dia), Resumo e Legenda."""
    import pandas as pd

    inst = r.inst
    rotulo = {s: (t.id[:-1] + "*" if t.id.endswith("E") else t.id)
              for s, t in inst.turnos.items()}
    dias = inst.dias
    colunas = [f"{DIAS_PT[d.weekday()]} {d:%d/%m}" for d in dias]
    grade = {p.nome: [""] * len(dias) for p in inst.profissionais.values()}
    for d, n, s in r.escala:
        grade[inst.profissionais[n].nome][inst.indice(d)] = rotulo[s]
    for n, d in inst.indisponiveis:
        grade[inst.profissionais[n].nome][inst.indice(d)] = "indisp."
    categoria = {p.nome: ("Enfermeiro" if br.HABILIDADE_ENF in p.habilidades else "Técnico")
                 for p in inst.profissionais.values()}
    escala = pd.DataFrame.from_dict(grade, orient="index", columns=colunas)
    escala.insert(0, "Categoria", [categoria[n] for n in escala.index])
    escala.insert(1, "Turnos", [sum(1 for c in linha if c and c != "indisp.")
                                for linha in grade.values()])
    escala.index.name = "Profissional"

    c = r.conformidade or {}
    resumo = pd.DataFrame([
        ("Veredito", r.frase()),
        ("Grau que governa a composição", r.grau),
        ("Horas de enfermagem por dia", round(r.horas_dia, 2)),
        ("QP núcleo assistencial (sem IST)", round(r.qp_nucleo, 2)),
        ("QP completo (com IST de 15%)", round(r.qp_completo, 2)),
        ("Quadro informado", r.quadro_informado),
        ("Quadro desta escala", r.menor_viavel),
        ("Regime", e.regime),
        ("Período", f"{inst.inicio:%d/%m/%Y} a {inst.fim:%d/%m/%Y}"),
        ("Razão fim de semana / dia útil", f"{e.razao_fds:.2%}"),
        ("Descanso mínimo entre turnos (medido)", f"{c.get('menor_geral', 0):.0f} h"),
        ("Descanso semanal mínimo (medido)", fmt_semanal(c.get("menor_semanal", 0))),
        ("Maior sequência de dias trabalhados", c.get("max_consec")),
        ("Conferência de descanso", "cumpre" if c.get("ok") else "NÃO CUMPRE"),
    ] + [("Aviso", a) for a in r.avisos], columns=["Item", "Valor"])
    legenda = pd.DataFrame(
        [(rotulo[s], f"{t.inicio:%H:%M}", f"{t.fim:%H:%M}", t.descricao)
         for s, t in inst.turnos.items()]
        + [("indisp.", "", "", "férias ou licença")],
        columns=["Código", "Início", "Fim", "Descrição"])

    saida = io.BytesIO()
    with pd.ExcelWriter(saida, engine="openpyxl") as w:
        escala.to_excel(w, sheet_name="Escala")
        resumo.to_excel(w, sheet_name="Resumo", index=False)
        legenda.to_excel(w, sheet_name="Legenda", index=False)
    return saida.getvalue()


def ler_razao(texto: str) -> float:
    """'70%', '0,7', '0.7' ou '20/29' -> fracao em [0, 1]."""
    t = texto.strip().replace(",", ".").replace(" ", "")
    if not t:
        return 1.0
    if t.endswith("%"):
        valor = float(t[:-1]) / 100
    elif "/" in t:
        a, b = t.split("/", 1)
        valor = float(a) / float(b)
    else:
        valor = float(t)
    if not 0 <= valor <= 1:
        raise ValueError(f"a razão precisa estar entre 0% e 100%; veio {texto}")
    return valor


def proxima_segunda(hoje: date | None = None) -> date:
    hoje = hoje or date.today()
    return hoje + timedelta(days=(7 - hoje.weekday()) % 7 or 7)
