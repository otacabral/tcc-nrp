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
import prioridades as pr  # noqa: E402

ROTULO_GRAU = {
    "minimo": "Mínimo (4 h/paciente)",
    "intermediario": "Intermediário (6 h)",
    "alta": "Alta dependência (10 h; 36% enfermeiros)",
    "semi_intensivo": "Semi-intensivo (10 h; 42% enfermeiros)",
    "intensivo": "Intensivo (18 h)",
}
CAT = {"enf": "enf", "tec": "téc"}
# rotulo de tela dos turnos dos modelos prontos; o codigo (M, T, N, D) continua sendo o id na
# instancia, no XML e na grade (DECISOES.md, "2026-10-19 — Tela orientada ao usuario"). Nome
# digitado fora deste mapa (ex.: "D12") e o proprio codigo.
ROTULO_TURNO = {"M": "Manhã", "T": "Tarde", "N": "Noite", "D": "Dia"}
CODIGO_TURNO = {v: k for k, v in ROTULO_TURNO.items()}

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

st.caption("Turnos: nome, início e fim (hora cheia).",
           help="Edite os horários ou acrescente uma linha para um turno novo (ex.: D12, 7 a "
                "19). As regras de descanso da CLT saem dos horários: 11 h entre turnos, 36 h "
                "depois de turno de 12 h, e toda folga isolada de pelo menos 24 h.")
tabela_turnos = st.data_editor(
    pd.DataFrame([(ROTULO_TURNO.get(c, c), ini, fim) for c, ini, fim in fe.MODELOS[modelo_turnos]],
                 columns=["Nome", "Início", "Fim"]),
    num_rows="dynamic", key=f"turnos_{modelo_turnos}", width="content",
    column_config={"Início": st.column_config.NumberColumn(min_value=0, max_value=23, step=1),
                   "Fim": st.column_config.NumberColumn(min_value=0, max_value=23, step=1)})
turnos = [(CODIGO_TURNO.get(str(l["Nome"]).strip(), str(l["Nome"]).strip()), int(l["Início"]),
           int(l["Fim"]))
          for _, l in tabela_turnos.dropna().iterrows() if str(l["Nome"]).strip()]
nomes_turno = [t[0] for t in turnos]                        # codigos
rotulo_turno = {c: ROTULO_TURNO.get(c, c) for c in nomes_turno}

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

st.caption("Carga contratual semanal de cada profissional (padrão 44 h).",
           help="O teto vale sobre o período, não por semana (no 12×36 há semanas de 48 h e de "
                "36 h), e desconta férias e licenças. 44 h é o limite da Constituição.")
tabela_cargas = st.data_editor(
    pd.DataFrame({"Profissional": pessoas,
                  "Carga semanal (h)": [br.CARGA_CONTRATUAL_PADRAO] * len(pessoas)}),
    key=f"cargas_{len(pessoas)}", width="content", disabled=["Profissional"],
    column_config={"Carga semanal (h)": st.column_config.SelectboxColumn(
        options=list(br.CARGAS_CONTRATUAIS), required=True)})
cargas = {str(l["Profissional"]): float(l["Carga semanal (h)"])
          for _, l in tabela_cargas.dropna().iterrows()
          if float(l["Carga semanal (h)"]) != br.CARGA_CONTRATUAL_PADRAO}

st.caption("Férias e licenças — nesses dias a pessoa não é escalada (regra rígida).")
tabela_indisp = st.data_editor(
    pd.DataFrame({"Profissional": pd.Series(dtype="str"),
                  "De": pd.Series(dtype="datetime64[ns]"),
                  "Até": pd.Series(dtype="datetime64[ns]")}),
    num_rows="dynamic", key="indisp", width="content",
    column_config={"Profissional": st.column_config.SelectboxColumn(options=pessoas),
                   "De": st.column_config.DateColumn(format="DD/MM/YYYY"),
                   "Até": st.column_config.DateColumn(format="DD/MM/YYYY")})

# --- c) demanda ---------------------------------------------------------------------------
st.header("3. Demanda")
st.caption("Quantas pessoas de cada categoria em cada turno. Valores próprios para o fim de "
           "semana são opcionais.")
com_fds = st.checkbox("Fim de semana com demanda própria", key="com_fds")
demanda_turno, demanda_fds = {}, {}
for nome in nomes_turno:
    colunas = st.columns(4 if com_fds else 2)
    enf = colunas[0].number_input(f"{rotulo_turno[nome]}: enfermeiros", min_value=0, value=1,
                                  step=1, key=f"g_{nome}_enf")
    tec = colunas[1].number_input(f"{rotulo_turno[nome]}: técnicos", min_value=0, value=2,
                                  step=1, key=f"g_{nome}_tec")
    demanda_turno[nome] = (int(enf), int(tec))
    if com_fds:
        enf_f = colunas[2].number_input(f"{rotulo_turno[nome]}: enfermeiros (fim de semana)",
                                        min_value=0, value=int(enf), step=1,
                                        key=f"f_{nome}_enf")
        tec_f = colunas[3].number_input(f"{rotulo_turno[nome]}: técnicos (fim de semana)",
                                        min_value=0, value=int(tec), step=1,
                                        key=f"f_{nome}_tec")
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
with st.expander("Conferir com o COFEN (opcional) — pacientes por grau"):
    st.caption("Média diária de pacientes. Serve só para comparar o quadro com o QP do "
               "Parecer; não muda a escala.")
    colunas = st.columns(len(br.GRAUS))
    for coluna, g in zip(colunas, br.GRAUS):
        valor = coluna.number_input(ROTULO_GRAU[g], min_value=0.0, value=0.0, step=1.0,
                                    format="%.2f", key=f"pac_{g}")
        if valor > 0:
            pacientes[g] = valor



def _data(valor) -> date:
    return pd.Timestamp(valor).date()


def _vazio(valor) -> bool:
    try:
        return valor is None or bool(pd.isna(valor)) or str(valor).strip() == ""
    except (TypeError, ValueError):
        return False


def _regras() -> list:
    """As linhas da tabela "Pedidos e regras dos profissionais" (vazia antes de ela aparecer).
    Linha sem profissional e ignorada; o resto e validado por `prioridades.traduzir`."""
    tabela = globals().get("tabela_regras")
    if tabela is None:
        return []
    linhas = []
    for _, l in tabela.iterrows():
        if _vazio(l["Profissional"]):
            continue
        linhas.append(pr.Linha(
            profissional=str(l["Profissional"]),
            dia=None if _vazio(l["Dia"]) else _data(l["Dia"]),
            turno=(None if _vazio(l["Turno"])
                   else CODIGO_TURNO.get(str(l["Turno"]), str(l["Turno"]))),
            tipo=pr.FOLGA if _vazio(l["Tipo"]) else str(l["Tipo"]),
            importancia=None if _vazio(l["Importância"]) else str(l["Importância"])))
    return linhas


def _entrada(prioridades, regras=True) -> fe.Entrada:
    return fe.Entrada(
        turnos=turnos, grau=grau, n_enfermeiros=int(n_enf), n_tecnicos=int(n_tec),
        demanda_turno=demanda_turno, demanda_fds=demanda_fds, demanda_data=demanda_data,
        fim_de_semana=fim_de_semana, inicio=inicio,
        nomes_enfermeiros=nomes_enf, nomes_tecnicos=nomes_tec,
        indisponibilidades=[(str(l["Profissional"]), _data(l["De"]), _data(l["Até"]))
                            for _, l in tabela_indisp.dropna().iterrows()],
        regras=_regras() if regras else [],
        pacientes=pacientes or None, cargas=cargas, prioridades=prioridades)


# --- prioridades da escala (opcao B; DECISOES.md, 14/10 e 19/10) ---------------------------
# Tela orientada ao usuario (DECISOES.md, 2026-10-19): sem a coluna Situacao; as regras da CLT
# ficam no back end; o texto longo vai para o "?" de cada linha e para o GUIA_DE_USO.
st.header("4. Prioridades da escala")
st.caption("Classifique cada critério: Essencial, Importante, Desejável ou Não considerar.",
           help="Os de nível Essencial vêm antes de todos os outros; depois os Importantes; "
                "depois os Desejáveis. Dentro do mesmo nível, cada violação conta 1. Uma "
                "preferência nunca torna a escala impossível: as regras da CLT continuam "
                "rígidas e valem antes de tudo.")
PADRAO = fe.prioridades_padrao()
for _k, (_nivel, _limite) in PADRAO.items():      # padrao antes dos campos (sem value=)
    st.session_state.setdefault(f"prio_{_k}", _nivel)
    if _limite is not None:
        st.session_state.setdefault(f"lim_{_k}", _limite)


def _restaurar():
    for k, (nivel, limite) in PADRAO.items():
        st.session_state[f"prio_{k}"] = nivel
        if limite is not None:
            st.session_state[f"lim_{k}"] = limite


st.button("Restaurar padrão", key="restaurar", on_click=_restaurar)
# regime em que ninguem trabalha dois dias seguidos (o 12x36), pelos horarios da tabela de turnos,
# como `ferramenta.limite_efetivo` — sem depender de a equipe ja estar preenchida
_pares = set(br.pares_proibidos_por_horario(
    [(n, ini, fe.duracao(ini, fim)) for n, ini, fim in turnos], None, descartar=False))
_so_doze = bool(turnos) and all((s, 1, t) in _pares for s, _, _ in turnos for t, _, _ in turnos)
# fora da tela: o pedido de folga no dia (a importancia e da linha da tabela de pedidos), as
# linhas que a CLT ja garante e, no 12x36, as que nunca podem ser atendidas ou que a lei impede
# 21/10: o maximo de dias seguidos e preferencia, oculta no 12x36; a trava e so a da lei
# (DECISOES.md, "2026-10-21 — Maximo de dias seguidos: a trava e so a da CLT")
OCULTOS_12X36 = ("fds_completo", "mesmo_turno_fds", "min_dias_seguidos", "max_dias_seguidos")
NA_TELA = [c for c in pr.CRITERIOS
           if c.id != "pedido_folga" and not c.clt
           and not (_so_doze and c.id in OCULTOS_12X36)]
_visiveis = {c.id for c in NA_TELA}
# criterio oculto vale como o padrao ("Nao considerar"), mesmo se escolhido antes
escolha = {k: (st.session_state[f"prio_{k}"], st.session_state.get(f"lim_{k}"))
           if k in _visiveis or k == "pedido_folga" else PADRAO[k] for k in PADRAO}
try:
    _teto = fe.montar(_entrada(escolha, regras=False)) \
        .contratos["0"].max_num_assignments.valor
except (ValueError, TypeError, KeyError, ZeroDivisionError):
    _teto = None                                          # entrada ainda incompleta
# limites presos pela lei
TETO_LIMITE = {"min_dias_seguidos": br.MAX_CONSECUTIVOS_GENERICO, "min_turnos": _teto,
               "max_dias_seguidos": br.MAX_CONSECUTIVOS_GENERICO, "max_turnos": _teto}
for g, nome_grupo in enumerate(pr.GRUPOS):
    crits = [c for c in NA_TELA if c.grupo == g]
    campos = [c for c in crits if not c.clt]
    k = sum(1 for c in campos if escolha[c.id][0] != pr.NAO)
    with st.expander(f"{nome_grupo} — {k} de {len(campos)} considerados",
                     expanded=(g == 0)):
        if g == 0:
            st.markdown("**Pedidos e regras dos profissionais**")
            st.caption("Folga ou turno fixo, de cada profissional. Importância em branco: "
                       "Essencial para folga num dia; Desejável nos demais.",
                       help="Dia em branco = todos os dias; turno em branco = o dia todo. "
                            "\"Só este turno\" = a pessoa só trabalha naquele turno (várias "
                            "linhas da mesma pessoa somam os turnos). Nenhum pedido torna a "
                            "escala impossível: se a cobertura exigir, a ferramenta descumpre "
                            "o menor número possível, começando pelos de menor importância, "
                            "e diz quantos e de quem.")
            tabela_regras = st.data_editor(
                pd.DataFrame({"Profissional": pd.Series(dtype="str"),
                              "Dia": pd.Series(dtype="datetime64[ns]"),
                              "Turno": pd.Series(dtype="str"),
                              "Tipo": pd.Series(dtype="str"),
                              "Importância": pd.Series(dtype="str")}),
                num_rows="dynamic", key="regras", width="stretch",
                column_config={
                    "Profissional": st.column_config.SelectboxColumn(options=pessoas),
                    "Dia": st.column_config.DateColumn(format="DD/MM/YYYY"),
                    "Turno": st.column_config.SelectboxColumn(
                        options=[rotulo_turno[c] for c in nomes_turno]),
                    "Tipo": st.column_config.SelectboxColumn(options=list(pr.TIPOS),
                                                             default=pr.FOLGA),
                    "Importância": st.column_config.SelectboxColumn(
                        options=list(pr.CONSIDERADOS))})
        cab = st.columns([3, 2, 1])
        for coluna, rotulo in zip(cab, ("Critério", "Importância", "Limite")):
            coluna.caption(rotulo)
        for c in crits:
            col = st.columns([3, 2, 1])
            ajuda = c.ajuda
            if c.sem_conferencia:
                ajuda += (" ⓘ Sem conferência externa: nenhuma instância do benchmark INRC "
                          "a usa ou o avaliador oficial não a pontua.")
            col[0].markdown(c.nome, help=ajuda)
            col[1].selectbox("Importância", pr.NIVEIS, key=f"prio_{c.id}",
                             label_visibility="collapsed")
            if c.limite is not None:
                teto = TETO_LIMITE.get(c.id)
                if teto is not None and st.session_state.get(f"lim_{c.id}", 0) > teto:
                    st.session_state[f"lim_{c.id}"] = teto
                col[2].number_input(c.rotulo_limite, min_value=0, max_value=teto, step=1,
                                    key=f"lim_{c.id}", label_visibility="collapsed")
            st.caption(pr.RESUMO[c.id])
_usados = ([escolha[c.id][0] for c in NA_TELA if not c.clt and escolha[c.id][0] != pr.NAO]
           + [l.importancia or pr.importancia_padrao(l) for l in _regras()])
_niveis = set(_usados)
if len(_usados) > 1 and len(_niveis) == 1:
    st.info(f"Todos os critérios considerados estão no nível {_niveis.pop()}: entre eles há "
            f"compensação — uma violação de um vale o mesmo que uma de outro.")

# orcamento do clique (DECISOES.md, 19/10, item b): padrao = `fe.ORCAMENTO`, lido na chamada;
# o campo so vai ao `verificar` quando o gestor o muda (os testes encurtam `fe.ORCAMENTO`)
_orc_padrao = max(1, round(fe.ORCAMENTO / 60))
orcamento_min = st.number_input("Orçamento do clique (minutos)", min_value=1, step=1,
                                value=_orc_padrao, key="orcamento",
                                help="Tempo máximo de um clique em \"Gerar escala\". Esgotado, "
                                     "a ferramenta para e mostra só o que foi provado.")
gerar = st.button("Gerar escala", type="primary", key="gerar")


if gerar:
    try:
        if inicio.weekday() != 0:
            raise ValueError(f"o início precisa ser numa segunda-feira; "
                             f"{inicio:%d/%m/%Y} não é")
        entrada = _entrada(None if escolha == PADRAO else escolha)
        fe.montar(entrada)                    # erro de entrada aparece antes do solver
    except (ValueError, TypeError) as erro:
        st.session_state.pop("resultado", None)
        st.error(f"Entrada inválida: {erro}")
    else:
        barra = st.progress(0.0, text="preparando")
        # P12: a escala da etapa 1 aparece aqui enquanto a etapa 2 equilibra a carga. Sem
        # botao de planilha neste intervalo: um clique reexecutaria a tela e interromperia
        # o calculo. A planilha vem com o resultado final, e e a escala que a tela mostra.
        provisoria = st.empty()

        def aviso(evento, **d):
            if evento != "escala_etapa1":
                return
            with provisoria.container(border=True):
                st.info(f"Escala pronta; equilibrando a carga entre colegas (até "
                        f"{fe.fmt_tempo(d['limite'])}).")
                st.caption("A planilha fica disponível quando o equilíbrio terminar.")
                st.dataframe(fe.grade(d["inst"], d["escala"]).fillna(""), width="stretch")

        resultado = fe.verificar(entrada,
                                 progresso=lambda f, msg: barra.progress(f, text=msg),
                                 aviso=aviso,
                                 orcamento=(None if orcamento_min == _orc_padrao
                                            else orcamento_min * 60))
        barra.empty()
        provisoria.empty()
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
        motivo, texto, *todos = r.diagnostico
        titulo = " · ".join(fe.TITULO[m] for m in (todos[0] if todos else [motivo]))
        with st.container(border=True, key="diagnostico"):
            st.subheader(f"Por que não há escala legal com {r.quadro_informado}: {titulo}")
            st.write(texto)
            st.write(r.frase())
    for alerta in r.alertas:
        st.error(f"Alerta COFEN (não impede a escala): {alerta}")
    for alerta in r.alertas_descanso:
        st.warning(alerta)    # o texto vem inteiro da ferramenta (P15)

    if r.escala:
        ind, c = r.indicadores, r.conformidade
        m = st.columns(5)
        m[0].metric("Quadro da escala", r.menor_viavel)
        m[1].metric("Enfermeiro em posto de técnico", ind["enf_em_posto_tec"],
                    help="Turnos em que um enfermeiro cobriu vaga de técnico.")
        m[2].metric("Pedidos de folga atendidos",
                    f"{ind['pedidos_atendidos']} de {ind['pedidos_total']}")
        m[3].metric("Contrato cumprido (mín.–máx.)",
                    f"{ind['fracao_min']:.0%}–{ind['fracao_max']:.0%}",
                    help=f"Horas trabalhadas ÷ horas contratadas nos dias disponíveis. Em "
                         f"horas: {ind['horas_min']:g}–{ind['horas_max']:g} h no período.")
        m[4].metric("Conferência de descanso", "cumpre" if c["ok"] else "NÃO CUMPRE")
        st.caption(r.frase_vigente())
        st.caption(f"Descanso mínimo entre turnos {c['menor_geral']:.0f} h · descanso "
                   f"semanal {fe.fmt_semanal(c['menor_semanal_interno'])} · no máximo "
                   f"{br.plural(c['max_consec'], 'dia seguido', 'dias seguidos')}")
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
            # a etapa 2 nao mostra gap (decisao de 05/10): mostra a diferenca de carga
            # entre colegas da mesma categoria, que e o que o gestor le
            dif = " · ".join(f"{fe.NOME_CATEGORIA[g].lower()}: {fe.fmt_diferenca(cat)}"
                             for g, cat in ind.get("categorias", {}).items())
            entre = ("de mesmo custo" if r.provado else "que não pioram o valor da etapa 1 "
                     "(a etapa 1 não provou o ótimo)")
            st.caption(f"Equilíbrio de carga dentro de cada categoria, entre as escalas "
                       f"{entre}. Diferença máxima de carga entre colegas — {dif}.")
        elif equilibrio:
            st.caption(f"Equilíbrio de carga: {equilibrio}.")
        if ind["pedidos_total"] and ind["pedidos_atendidos"] == ind["pedidos_total"]:
            st.caption(f"Todos os {ind['pedidos_total']} pedidos de folga foram atendidos."
                       if ind["pedidos_total"] > 1 else "O pedido de folga foi atendido.")
        elif ind["pedidos_total"]:
            st.caption(f"Pedidos de folga negados: {ind['pedidos_total'] - ind['pedidos_atendidos']}"
                       f", em {br.plural(ind['com_pedido_negado'], 'profissional', 'profissionais')}; no máximo "
                       f"{ind['negados_max']} por pessoa.")
        if r.descumpridos:
            por_nivel = {}
            for nivel, nome, q in r.descumpridos:
                por_nivel.setdefault(nivel, []).append(f"{nome} {q}")
            st.caption("Pedidos e regras descumpridos — " + "; ".join(
                f"{nivel}: {', '.join(v)}" for nivel, v in por_nivel.items()) + ".")
        elif e.regras:
            st.caption("Todos os pedidos e regras da tabela foram atendidos.")
        if r.criterios:
            st.markdown("**Resultado por critério**")
            st.dataframe(fe.tabela_criterios(r), hide_index=True)
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
                   "indeterminado": f"sem resposta em {fe.fmt_tempo(fe.TEMPO)} — nem provado "
                                    f"inviável",
                   "erro": "erro técnico ao resolver; detalhes no console",
                   fe.ORCAMENTO_ESGOTADO: "não testado: o orçamento do clique acabou",
                   fe.REPROVADA: "escala encontrada, mas reprovada na conferência de "
                                 "descanso — não entregue"}
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
