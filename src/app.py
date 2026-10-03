"""Tela da ferramenta (Streamlit). Roda da raiz, com a .venv ativa:

    streamlit run src\\app.py

So a casca: toda decisao esta em `src/ferramenta.py`. Ordem da especificacao: configuracao
da unidade, equipe, demanda, "conferir com o COFEN" (opcional), resultado. A resolucao fica
atras do botao e o resultado vai para `st.session_state`, porque o Streamlit reexecuta o
script inteiro a cada interacao (DECISOES.md, 29/09).

Visual fica para depois (Etapa 6: o objetivo e o fluxo funcionar).

Os campos que os testes preenchem (`src/testes_ferramenta.py`) sao selectbox, number_input,
text_area e checkbox, com `key` fixa — o AppTest do Streamlit nao edita `st.data_editor`.
As tabelas (turnos, demanda especifica, ferias, pedidos) sao data_editor e comecam num valor
que ja funciona.
"""

from __future__ import annotations

import io
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402

ROTULO_GRAU = {
    "minimo": "Mínimo (4 h/paciente)",
    "intermediario": "Intermediário (6 h)",
    "alta": "Alta dependência (10 h)",
    "semi_intensivo": "Semi-intensivo (10 h)",
    "intensivo": "Intensivo (18 h)",
}
CAT = {"enf": "enf", "tec": "téc"}

st.set_page_config(page_title="Escala de enfermagem", layout="wide")
st.title("Escala de enfermagem")
st.caption("A CLT trava a escala; o COFEN só alerta. Horizonte de 28 dias, começando numa "
           "segunda-feira.")

# --- a) configuracao da unidade -----------------------------------------------------------
st.header("1. Configuração da unidade")
c1, c2, c3, c4 = st.columns(4)
modelo_turnos = c1.selectbox("Modelo de turnos", list(fe.MODELOS), key="modelo")
fim_de_semana = c2.radio("Fim de semana", ("sab_dom", "sex_dom"), key="fds",
                         format_func=lambda f: "sábado e domingo" if f == "sab_dom"
                         else "sexta a domingo")
grau = c3.selectbox("Grau de dependência predominante", list(br.GRAUS), index=1,
                    format_func=ROTULO_GRAU.get, key="grau")
inicio = c4.date_input("Início (segunda-feira)", value=fe.proxima_segunda(),
                       format="DD/MM/YYYY", key="inicio")

st.caption("Turnos: edite nome, início e fim (hora cheia). As regras de descanso da CLT saem "
           "dos horários.")
tabela_turnos = st.data_editor(
    pd.DataFrame(fe.MODELOS[modelo_turnos], columns=["Nome", "Início", "Fim"]),
    num_rows="dynamic", key=f"turnos_{modelo_turnos}", width="content",
    column_config={"Início": st.column_config.NumberColumn(min_value=0, max_value=23, step=1),
                   "Fim": st.column_config.NumberColumn(min_value=0, max_value=23, step=1)})
turnos = [(str(l["Nome"]).strip(), int(l["Início"]), int(l["Fim"]))
          for _, l in tabela_turnos.dropna().iterrows() if str(l["Nome"]).strip()]
nomes_turno = [t[0] for t in turnos]

# --- b) equipe ----------------------------------------------------------------------------
st.header("2. Equipe")
e1, e2 = st.columns(2)
n_enf = e1.number_input("Enfermeiros", min_value=0, value=0, step=1, key="n_enf")
n_tec = e2.number_input("Técnicos e auxiliares", min_value=0, value=0, step=1, key="n_tec")
with st.expander("Nomes (opcional)"):
    n1, n2 = st.columns(2)
    texto_enf = n1.text_area("Enfermeiros, um por linha", key="nomes_enf")
    texto_tec = n2.text_area("Técnicos, um por linha", key="nomes_tec")


def _nomes(texto: str) -> list[str] | None:
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    return linhas or None


nomes_enf, nomes_tec = _nomes(texto_enf), _nomes(texto_tec)
pessoas = ((nomes_enf or [f"Enf {i + 1}" for i in range(int(n_enf))])
           + (nomes_tec or [f"Téc {i + 1}" for i in range(int(n_tec))]))

st.caption("Carga contratual semanal de cada profissional. O teto vale sobre o período, "
           "não por semana (no 12×36 há semanas de 48 h e de 36 h), e desconta férias e "
           "licenças. Padrão 44 h, o limite da Constituição.")
tabela_cargas = st.data_editor(
    pd.DataFrame({"Profissional": pessoas,
                  "Carga semanal (h)": [br.CARGA_CONTRATUAL_PADRAO] * len(pessoas)}),
    key=f"cargas_{len(pessoas)}", width="content", disabled=["Profissional"],
    column_config={"Carga semanal (h)": st.column_config.SelectboxColumn(
        options=list(br.CARGAS_CONTRATUAIS), required=True)})
cargas = {str(l["Profissional"]): float(l["Carga semanal (h)"])
          for _, l in tabela_cargas.dropna().iterrows()
          if float(l["Carga semanal (h)"]) != br.CARGA_CONTRATUAL_PADRAO}

f1, f2 = st.columns(2)
with f1:
    st.caption("Férias e licenças — nesses dias a pessoa não é escalada (regra rígida).")
    tabela_indisp = st.data_editor(
        pd.DataFrame({"Profissional": pd.Series(dtype="str"),
                      "De": pd.Series(dtype="datetime64[ns]"),
                      "Até": pd.Series(dtype="datetime64[ns]")}),
        num_rows="dynamic", key="indisp", width="stretch",
        column_config={"Profissional": st.column_config.SelectboxColumn(options=pessoas),
                       "De": st.column_config.DateColumn(format="DD/MM/YYYY"),
                       "Até": st.column_config.DateColumn(format="DD/MM/YYYY")})
with f2:
    st.caption("Pedidos de folga — atendidos quando possível; nunca impedem a escala.")
    tabela_pedidos = st.data_editor(
        pd.DataFrame({"Profissional": pd.Series(dtype="str"),
                      "Data": pd.Series(dtype="datetime64[ns]")}),
        num_rows="dynamic", key="pedidos", width="stretch",
        column_config={"Profissional": st.column_config.SelectboxColumn(options=pessoas),
                       "Data": st.column_config.DateColumn(format="DD/MM/YYYY")})

# --- c) demanda ---------------------------------------------------------------------------
st.header("3. Demanda")
st.caption("Quantas pessoas de cada categoria em cada turno. Valores próprios para o fim de "
           "semana são opcionais.")
com_fds = st.checkbox("Fim de semana com demanda própria", key="com_fds")
demanda_turno, demanda_fds = {}, {}
for nome in nomes_turno:
    colunas = st.columns(4 if com_fds else 2)
    enf = colunas[0].number_input(f"{nome}: enfermeiros", min_value=0, value=1, step=1,
                                  key=f"g_{nome}_enf")
    tec = colunas[1].number_input(f"{nome}: técnicos", min_value=0, value=2, step=1,
                                  key=f"g_{nome}_tec")
    demanda_turno[nome] = (int(enf), int(tec))
    if com_fds:
        enf_f = colunas[2].number_input(f"{nome}: enfermeiros (fds)", min_value=0,
                                        value=int(enf), step=1, key=f"f_{nome}_enf")
        tec_f = colunas[3].number_input(f"{nome}: técnicos (fds)", min_value=0,
                                        value=int(tec), step=1, key=f"f_{nome}_tec")
        demanda_fds[nome] = (int(enf_f), int(tec_f))

dias = [inicio + timedelta(days=k) for k in range(br.DIAS_HORIZONTE)]
dias_fds = br.FIM_DE_SEMANA[fim_de_semana][0]


def _base(d: date, nome: str) -> tuple[int, int]:
    return demanda_fds.get(nome, demanda_turno[nome]) if d.weekday() in dias_fds \
        else demanda_turno[nome]


demanda_data: dict[tuple[date, str, str], int] = {}
with st.expander("Demanda específica por data (feriados, eventos) — opcional"):
    st.caption("Preenchida a partir da demanda acima; edite só o que muda. Mudar a demanda "
               "acima refaz esta grade.")
    grade = pd.DataFrame(
        {f"{nome} {CAT[c]}": [_base(d, nome)[i] for d in dias]
         for nome in nomes_turno for i, c in enumerate(("enf", "tec"))},
        index=[fe.rotulo_dia(d) for d in dias])
    assinatura = hash((tuple(nomes_turno), tuple(sorted(demanda_turno.items())),
                       tuple(sorted(demanda_fds.items())), fim_de_semana, inicio))
    editada = st.data_editor(grade, key=f"especifica_{assinatura}", width="stretch")
    for k, d in enumerate(dias):
        for nome in nomes_turno:
            for i, c in enumerate(("enf", "tec")):
                valor = int(editada.iloc[k][f"{nome} {CAT[c]}"])
                if valor != _base(d, nome)[i]:
                    demanda_data[(d, nome, c)] = valor

# --- d) conferir com o COFEN --------------------------------------------------------------
pacientes = {}
with st.expander("4. Conferir com o COFEN (opcional) — pacientes por grau"):
    st.caption("Média diária de pacientes. Serve só para comparar o quadro com o QP do "
               "Parecer; não muda a escala.")
    colunas = st.columns(len(br.GRAUS))
    for coluna, g in zip(colunas, br.GRAUS):
        valor = coluna.number_input(ROTULO_GRAU[g], min_value=0.0, value=0.0, step=1.0,
                                    format="%.2f", key=f"pac_{g}")
        if valor > 0:
            pacientes[g] = valor

gerar = st.button("Gerar escala", type="primary", key="gerar")


def _data(valor) -> date:
    return pd.Timestamp(valor).date()


if gerar:
    try:
        if inicio.weekday() != 0:
            raise ValueError(f"o início precisa ser numa segunda-feira; "
                             f"{inicio:%d/%m/%Y} não é")
        entrada = fe.Entrada(
            turnos=turnos, grau=grau, n_enfermeiros=int(n_enf), n_tecnicos=int(n_tec),
            demanda_turno=demanda_turno, demanda_fds=demanda_fds, demanda_data=demanda_data,
            fim_de_semana=fim_de_semana, inicio=inicio,
            nomes_enfermeiros=nomes_enf, nomes_tecnicos=nomes_tec,
            indisponibilidades=[(str(l["Profissional"]), _data(l["De"]), _data(l["Até"]))
                                for _, l in tabela_indisp.dropna().iterrows()],
            pedidos=[(str(l["Profissional"]), _data(l["Data"]))
                     for _, l in tabela_pedidos.dropna().iterrows()],
            pacientes=pacientes or None, cargas=cargas)
        fe.montar(entrada)                    # erro de entrada aparece antes do solver
    except (ValueError, TypeError) as erro:
        st.session_state.pop("resultado", None)
        st.error(f"Entrada inválida: {erro}")
    else:
        barra = st.progress(0.0, text="preparando")
        resultado = fe.verificar(entrada,
                                 progresso=lambda f, msg: barra.progress(f, text=msg))
        barra.empty()
        st.session_state["resultado"] = (resultado, entrada)

# --- e) resultado -------------------------------------------------------------------------
if "resultado" in st.session_state:
    r, e = st.session_state["resultado"]
    st.header("5. Resultado")
    if r.veredito == fe.ADMITE and r.provado:
        st.success(r.frase())
    elif r.veredito in (fe.ADMITE, fe.FALTAM):
        st.warning(r.frase())
    else:
        st.error(r.frase())
    if r.diagnostico:
        motivo, texto = r.diagnostico
        with st.container(border=True, key="diagnostico"):
            st.subheader(f"Por que não há escala legal com {r.quadro_informado}: "
                         f"{fe.TITULO[motivo]}")
            st.write(texto)
            st.write(r.frase())
    for alerta in r.alertas:
        st.error(f"Alerta COFEN (não impede a escala): {alerta}")

    if r.escala:
        ind, c = r.indicadores, r.conformidade
        m = st.columns(5)
        m[0].metric("Quadro da escala", r.menor_viavel)
        m[1].metric("Turnos de enfermeiro em posto de técnico", ind["enf_em_posto_tec"])
        m[2].metric("Pedidos de folga atendidos",
                    f"{ind['pedidos_atendidos']} de {ind['pedidos_total']}")
        m[3].metric("Contrato cumprido (mín.–máx.)",
                    f"{ind['fracao_min']:.0%}–{ind['fracao_max']:.0%}",
                    help=f"Horas trabalhadas ÷ horas contratadas nos dias disponíveis. Em "
                         f"horas: {ind['horas_min']:g}–{ind['horas_max']:g} h no período.")
        m[4].metric("Conferência de descanso", "cumpre" if c["ok"] else "NÃO CUMPRE")
        st.caption(f"Descanso mínimo entre turnos {c['menor_geral']:.0f} h · descanso "
                   f"semanal {fe.fmt_semanal(c['menor_semanal'])} · no máximo "
                   f"{c['max_consec']} dias seguidos")
        for g, cat in ind.get("categorias", {}).items():
            st.caption(f"{fe.NOME_CATEGORIA[g]}: {cat['fracao_min']:.0%}–"
                       f"{cat['fracao_max']:.0%} do contrato cumprido · "
                       f"{cat['nao_utilizadas']:.0f} h de contrato não utilizadas "
                       f"(de {cat['devidas']:.0f} h contratadas nos dias disponíveis).")
        if ind.get("diferenca_categorias") is not None:
            st.caption(f"Diferença entre categorias: técnicos cumprem em média "
                       f"{ind['diferenca_categorias'] * 100:+.0f} pontos percentuais do "
                       f"contrato em relação aos enfermeiros. Ela não é otimizada: vem da "
                       f"demanda de cada posto frente ao tamanho de cada categoria.")
        equilibrio = ind.get("etapa2")
        if equilibrio == "ok":
            sem_prova = "" if ind["provado_etapa2"] else " (sem prova de que é a menor)"
            st.caption(f"Equilíbrio de carga dentro de cada categoria: entre as escalas de "
                       f"mesmo custo, a diferença entre a maior e a menor fração do contrato "
                       f"cumprida, somada entre enfermeiros e entre técnicos, caiu de "
                       f"{ind['amplitude_etapa1'] * 100:.0f} para "
                       f"{ind['amplitude'] * 100:.0f} pontos percentuais{sem_prova}.")
        elif equilibrio:
            st.caption(f"Equilíbrio de carga: {equilibrio}.")
        if ind["pedidos_total"]:
            st.caption(f"Pedidos de folga negados: {ind['pedidos_total'] - ind['pedidos_atendidos']}"
                       f", em {ind['com_pedido_negado']} profissional(is); no máximo "
                       f"{ind['negados_max']} por pessoa.")
    if r.qp:
        q1, q2 = st.columns(2)
        st.caption(f"CHS usada no QP: {r.chs:.1f} h por semana, a média das cargas "
                   f"contratuais da equipe.".replace(".", ",", 1))
        q1.metric("QP núcleo assistencial", f"{r.qp[0]:.2f}".replace(".", ","),
                  help=f"Horas por dia × 7 / CHS ({r.chs:g} h).")
        q2.metric("QP completo (IST 15%)", f"{r.qp[1]:.2f}".replace(".", ","),
                  help="Núcleo × 1,15. O IST cobre férias e ausências que a escala não "
                       "modela.")
    with st.expander("Como o veredito foi obtido"):
        explica = {"piso": "inviável pela aritmética — horas ou alternância de plantões não "
                           "cobrem a demanda",
                   "inviavel": "inviável, provado pelo solver",
                   "viavel": "viável — escala encontrada e conferida",
                   "indeterminado": "sem escala no tempo disponível — nem provado inviável",
                   "erro": "o solver falhou"}
        for quadro, v, n_enf_t, n_tec_t in r.tentativas:
            composicao = f" ({n_enf_t} enf. + {n_tec_t} téc.)" if n_enf_t is not None else ""
            st.write(f"{quadro} profissionais{composicao}: {explica.get(v, v)}")

    if r.escala:
        dados = fe.planilha(r, e)
        st.download_button("Baixar planilha (.xlsx)", dados,
                           file_name=f"escala_{r.inst.inicio:%Y-%m-%d}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument."
                                "spreadsheetml.sheet")
        grade = pd.read_excel(io.BytesIO(dados), sheet_name="Escala", index_col=0)
        # celula vazia = folga; sem o fillna a tela mostraria "None"
        st.dataframe(grade.fillna(""), width="stretch")
        st.caption("Código com * = posto de enfermeiro.")
