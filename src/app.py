"""Tela da ferramenta (Streamlit). Roda da raiz, com a .venv ativa:

    streamlit run src\\app.py

So a casca: toda decisao esta em `src/ferramenta.py`. A resolucao fica atras do botao e o
resultado vai para `st.session_state`, porque o Streamlit reexecuta o script inteiro a cada
interacao — sem isso, cada clique resolveria de novo (DECISOES.md, 29/09).
"""

from __future__ import annotations

import io
import sys
from datetime import date
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

st.set_page_config(page_title="Escala de enfermagem", layout="wide")
st.title("Escala de enfermagem")
st.caption("Dimensionamento do Parecer Normativo COFEN nº 1/2024 e limites da CLT. "
           "Horizonte de 28 dias, começando numa segunda-feira.")

with st.form("entrada"):
    st.subheader("Pacientes")
    st.caption("Média diária de pacientes em cada grau de dependência.")
    colunas = st.columns(len(br.GRAUS))
    pacientes = {}
    for coluna, g in zip(colunas, br.GRAUS):
        pacientes[g] = coluna.number_input(ROTULO_GRAU[g], min_value=0.0, value=0.0,
                                           step=1.0, format="%.2f", key=f"pac_{g}")

    st.subheader("Equipe e período")
    c1, c2, c3, c4 = st.columns(4)
    regime = c1.radio("Regime", ("12x36", "8h"),
                      format_func=lambda r: "12×36" if r == "12x36" else "8 horas (3 turnos)")
    n_enf = c2.number_input("Enfermeiros", min_value=0, value=0, step=1, key="n_enf")
    n_tec = c3.number_input("Técnicos e auxiliares", min_value=0, value=0, step=1,
                            key="n_tec")
    inicio = c4.date_input("Início (segunda-feira)", value=fe.proxima_segunda(),
                           format="DD/MM/YYYY", key="inicio")
    razao = st.text_input(
        "Demanda do fim de semana em relação ao dia útil",
        value="100%", key="razao",
        help="100% = mesma demanda todos os dias. Aceita 70%, 0,7 ou 20/29. "
             "O total de horas do período não muda; muda só a distribuição.")

    with st.expander("Nomes (opcional)"):
        n1, n2 = st.columns(2)
        nomes_enf = n1.text_area("Enfermeiros, um por linha", key="nomes_enf")
        nomes_tec = n2.text_area("Técnicos, um por linha", key="nomes_tec")

    st.subheader("Férias e licenças")
    st.caption("Profissional pelo nome (ou “Enf 1”, “Téc 3” se não houver nomes). "
               "Nesses dias a pessoa não é escalada.")
    indisp = st.data_editor(
        pd.DataFrame({"Profissional": pd.Series(dtype="str"),
                      "De": pd.Series(dtype="datetime64[ns]"),
                      "Até": pd.Series(dtype="datetime64[ns]")}),
        num_rows="dynamic", width="stretch", key="indisp",
        column_config={"De": st.column_config.DateColumn(format="DD/MM/YYYY"),
                       "Até": st.column_config.DateColumn(format="DD/MM/YYYY")})

    gerar = st.form_submit_button("Gerar escala", type="primary")


def _nomes(texto: str) -> list[str] | None:
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    return linhas or None


def _data(valor) -> date:
    return pd.Timestamp(valor).date()


if gerar:
    try:
        indisponibilidades = [(str(l["Profissional"]).strip(), _data(l["De"]), _data(l["Até"]))
                              for _, l in indisp.dropna(how="all").iterrows()
                              if str(l["Profissional"]).strip()]
        if inicio.weekday() != 0:
            raise ValueError(f"o início precisa ser numa segunda-feira; "
                             f"{inicio:%d/%m/%Y} não é")
        entrada = fe.Entrada(
            pacientes={g: p for g, p in pacientes.items() if p > 0},
            regime=regime, n_enfermeiros=int(n_enf), n_tecnicos=int(n_tec),
            razao_fds=fe.ler_razao(razao), inicio=inicio,
            nomes_enfermeiros=_nomes(nomes_enf), nomes_tecnicos=_nomes(nomes_tec),
            indisponibilidades=indisponibilidades)
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

if "resultado" in st.session_state:
    r, e = st.session_state["resultado"]
    st.divider()
    if r.veredito == fe.ADMITE:
        st.success(r.frase())
    elif r.veredito == fe.FALTAM:
        st.warning(r.frase())
    else:
        st.error(r.frase())

    q1, q2, q3 = st.columns(3)
    q1.metric("QP núcleo assistencial", f"{r.qp_nucleo:.2f}".replace(".", ","),
              help="Horas por dia × 7 / 42 h. É com ele que a escala é comparada.")
    q2.metric("QP completo (IST 15%)", f"{r.qp_completo:.2f}".replace(".", ","),
              help="Núcleo × 1,15. O IST cobre férias e ausências que a escala não modela.")
    q3.metric("Quadro informado", r.quadro_informado)
    for aviso in r.avisos:
        st.warning(f"Composição: {aviso}")
    with st.expander("Como o veredito foi obtido"):
        explica = {"piso": "inviável pela aritmética — a capacidade ou a alternância de "
                           "plantões não cobre a demanda",
                   "inviavel": "inviável, provado pelo solver",
                   "viavel": "viável — escala encontrada e conferida",
                   "indeterminado": "não decidido no limite de tempo",
                   "erro": "o solver falhou"}
        for quadro, v in r.tentativas:
            st.write(f"{quadro} profissionais: {explica.get(v, v)}")

    if r.escala:
        c = r.conformidade
        st.caption(
            f"Escala para {r.menor_viavel} profissionais · descanso mínimo entre turnos "
            f"{c['menor_geral']:.0f} h · descanso semanal {fe.fmt_semanal(c['menor_semanal'])}"
            f" · conferência de descanso: {'cumpre' if c['ok'] else 'NÃO CUMPRE'}")
        dados = fe.planilha(r, e)
        st.download_button("Baixar planilha (.xlsx)", dados,
                           file_name=f"escala_{r.inst.inicio:%Y-%m-%d}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument."
                                "spreadsheetml.sheet")
        st.dataframe(pd.read_excel(io.BytesIO(dados), sheet_name="Escala", index_col=0),
                     width="stretch")
