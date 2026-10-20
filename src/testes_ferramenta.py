"""Casos de ponta a ponta PELA TELA (Streamlit AppTest). Roda da raiz, com a .venv ativa:

    python src\\testes_ferramenta.py

O AppTest executa `src/app.py` como o navegador faria: escolhe o modelo de turnos, preenche
equipe e demanda, clica no botao e le o que aparece na tela. Esperado registrado ANTES de
rodar (29/09, Etapa 6):

1. 12x36, demanda por turno equivalente a celula v1 do Experimento A (razao 20/29): D e N
   com 1 enfermeiro + 9 tecnicos nos dias uteis e 1 + 6 no fim de semana. 40 (14 + 26):
   "admite escala legal", sem alerta, e a demanda montada e IDENTICA a da celula — senao o
   40 poderia coincidir por acaso.
2. Mesma configuracao com 39 (13 + 26): "Faltam 1; o menor quadro viavel e 40". O 39 cai no
   piso de alternancia: so ha turnos de 12 h, a regra das 36 h proibe dois dias seguidos, e
   o quadro cobre a soma de dois dias uteis (20 + 20).
3. Modelo 6 h + 12 h, M e T com 1 + 3, N com 1 + 2, 7 + 12: gera escala; descanso cumpre.
4. Poucos enfermeiros: 8 h, M e T com 1 + 3, N com 1 + 2, 5 + 15: gera escala E mostra o
   alerta vermelho de composicao (o intermediario pede 7 em 20).
5. Enfermeiro em posto de tecnico: 8 h, M e T com 1 + 2, N com 1 + 1, 8 + 5. Os tecnicos
   dao 5 x 168 = 840 h para 1.120 h de posto de tecnico: faltam 280 h = 35 turnos de 8 h, que
   so enfermeiro pode cobrir. Gera escala, com contagem >= 35 na tela.
   ESPERADO REFEITO EM 03/10, DEPOIS de ver o resultado (30), por ser aritmetico e
   independente do solver: a conta acima usava 42 h. Com a carga padrao de 44 h
   (DECISOES.md, "Carga por contrato"), os tecnicos dao 5 x 176 = 880 h; faltam 1.120 - 880 =
   240 h = 30 turnos de 8 h. Esperado: contagem >= 30 na tela.

Os tres desfechos do tempo (02/10, DECISOES.md "Redesenho"), esperado registrado ANTES de
rodar. O limite e encurtado em `fe.TEMPO`, que a tela le na chamada. Os casos (b) e (c)
dependem da maquina: foram escolhidos por sondagem no log do HiGHS em 02/10 (i5-10210U) —
no 40 com 20 pedidos, primeira escala aos ~17 s com gap 1,03% e prova aos ~43 s; sem
pedidos, prova aos ~14 s. Numa maquina muito diferente, os limites podem precisar de ajuste.

8a. Otimo provado: o caso 5 com limite de 600 s. Tela: success "O quadro informado admite
    escala legal. Escala gerada." e nenhum "pode haver uma melhor".
8b. Escala sem prova: o 40 do 12x36 com os 20 pedidos do 7.2, limite de 25 s. Tela: warning
    que comeca por "O quadro informado admite escala legal. Escala gerada; pode haver uma
    melhor (gap", nenhum success; escala e planilha na tela; equilibrio "nao rodou".
    ESPERADO REFEITO EM 09/10, ANTES de implementar a P14 (DECISOES.md, "2026-10-09 — P14"):
    com a etapa 1 sem prova, a etapa 2 passa a rodar (limite de 25 s aqui, o da etapa 1). O
    equilibrio NAO pode dizer "nao rodou"; a linha "Escala desta tela" diz "sobre uma escala sem
    prova de otimo" se a etapa 2 entregou escala, ou "a da etapa 1" se nao; os 20 pedidos
    continuam atendidos (a etapa 2 nao pode piorar a penalidade, e negar um pedido custa mais
    que todos os postos de tecnico).
    ESPERADO REFEITO EM 09/10, ANTES de implementar a P17 (etapa 2 partindo da escala da etapa
    1): a etapa 2 SEMPRE entrega escala -> `etapa2` == "ok", e a linha diz "sobre uma escala sem
    prova de otimo".
    ESPERADO REFEITO EM 11/10, ANTES de corrigir o texto (DECISOES.md, "2026-10-10 — P17", item
    c): `etapa2` continua "ok". A linha "Escala desta tela" passa a depender de a etapa 2 ter
    melhorado o criterio (`amplitude` < `amplitude_etapa1`): se melhorou, e exatamente a linha
    atual ("a da etapa 2, com a carga equilibrada entre colegas, sobre uma escala sem prova de
    otimo: ..."); se nao melhorou, e exatamente "Escala desta tela: a da etapa 1. O equilibrio
    de carga nao achou, no tempo disponivel, escala mais equilibrada sem piorar o resultado da
    etapa 1.", e `amplitude` == `amplitude_etapa1`. Nenhum desfecho fica sem conferencia.
    Pedidos entram por fora da tela (o AppTest nao edita a tabela): `fe.verificar` e
    embrulhado para acrescenta-los a entrada que a tela montou.
8c. Tempo esgotado sem escala: o 40 sem pedidos, limite de 3 s. Tela: error "Sem resposta em
    3 s com 40 profissionais: o solver nao achou escala nem provou que ela nao existe.";
    nenhum "Faltam" em lugar nenhum; sem diagnostico, sem escala, sem botao de planilha.
    (Texto ate 08/10: "Nao foi possivel gerar a escala no tempo disponivel." — trocado pela
    P12, DECISOES.md, "2026-10-08 — P12 aprovada"; esperado novo registrado antes.)
8d. Quadro provado curto pela conta, e o seguinte sem escala no tempo: o 39, limite de 3 s.
    O 39 cai no piso (alternancia), o 40 esgota o tempo. Tela: o diagnostico de alternancia
    aparece (provado pela conta); a frase e "O quadro informado e insuficiente. Sem resposta
    em 3 s com 40 profissionais: o menor quadro viavel nao foi determinado."; nenhum
    "Faltam 1". (Texto ate 08/10: "Nao foi possivel gerar a escala no tempo disponivel com
    mais profissionais; o menor quadro viavel nao foi determinado.")

P12 (08/10), esperado registrado ANTES de implementar (`resultados/relatorio_2026-10-08b.md`):

12a. Escala da etapa 1 mostrada ja: no caso 5, a ferramenta avisa a escala da etapa 1 ANTES de
     comecar a etapa 2, e essa escala cumpre o descanso. Pela tela, a linha "Escala desta
     tela: ..." concorda com o desfecho da etapa 2, e a grade da tela e igual a da planilha e
     a `r.escala`, celula a celula.
12c. Erro tecnico: com o solver trocado por um que levanta excecao, o caso 5 mostra "Erro
     tecnico ao resolver com 13 profissionais; detalhes no console.", nenhum "o solver falhou"
     em lugar nenhum, e o console recebe o traceback com a mensagem da excecao.
12d. Orcamento do clique: o 8d com o orcamento reduzido a 3 s (limite por resolucao de 600 s).
     O 39 cai no piso; o 40 fica sem resposta, ou nem e tentado, porque o orcamento acaba.
     Tela: "O quadro informado e insuficiente; o menor quadro viavel nao foi determinado em
     3 s.", diagnostico de alternancia, nenhum "Falta".

P15 (09/10), esperado registrado ANTES de implementar (`resultados/relatorio_2026-10-09b.md`).
Alerta de descanso semanal abaixo de 35 h, SEM as bordas do horizonte (decisao do Otavio,
09/10): nao conta o descanso que comeca no inicio do periodo nem o que chega ao fim, porque o
que vem antes e depois nao e conhecido. A trava de 24 h (`medir`/`cumpre`) nao muda.

15a. Caso montado a mao (8 h; inicio na primeira segunda; a escala nao precisa ser legal, so
     exercita a medida):
     - pessoa "0": T (15-23) de segunda a sexta, folga no sabado, M (7-15) no domingo, depois
       nada. Descanso de sexta 23:00 a domingo 07:00 = 32 h, interno, contem o sabado: 32 h;
     - pessoa "1": M de segunda a sexta, folga sabado e domingo, M de segunda a sexta da
       semana 2, depois nada: 64 h;
     - pessoa "2": folga na segunda, M de terca a domingo, depois nada. O unico descanso da
       semana 1 que contem dia livre e o da borda inicial (00:00 de segunda a 07:00 de terca =
       31 h): sem as bordas, nao conta.
     Esperado: `medir` (trava de 24 h, com bordas) da 31 h, como hoje; o minimo sem bordas e
     32 h; o alerta diz 1 profissional, o menor 32 h, e cita a Sumula 110.
15b. As tres planilhas da demonstracao (12x36, `docs/demonstracao/rodada*_escala.xlsx`): sem
     alerta; minimo sem bordas >= 35 h.
15c. A escala do caso do Otavio de 09/10 (`resultados/p14_p15_2026-10-09/otavio_antes_escala.json`;
     6 h + 12 h): sem alerta (o unico descanso abaixo de 35 h e o da borda inicial, 31 h, do
     Tec 5); minimo sem bordas 36 h; `medir` continua dando 31 h.
15d. Tela (caso 5, 8 h): o indicador "descanso semanal" da tela mostra o minimo sem bordas da
     escala; com o alerta do 15a posto no resultado, a tela o mostra em amarelo (warning), com
     o texto da ferramenta.

Art. 67 com horarios editaveis (13/10), esperado registrado ANTES de implementar
(`resultados/relatorio_2026-10-13a.md`, item 4):

16. Escala montada a mao que reprova: turnos N 23-07 e M 05-13, uma pessoa no ciclo N, folga, M
    ao longo dos 28 dias (toda folga isolada entre N e M: 22 h), entregue no lugar da
    resolucao. `verificar`: veredito nao e "admite"; `r.escala` vazia; a frase contem "nao
    cumpre a conferencia de descanso (art. 67)", "22 h" e "Nao use esta escala"; a tentativa
    fica como reprovada. Pela tela: a frase em `st.error`; nenhum "admite escala legal",
    nenhum botao de planilha.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import openpyxl  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

import ferramenta as fe  # noqa: E402
import solucao  # noqa: E402
import instancia_br as br  # noqa: E402
import prioridades as pr  # noqa: E402

# Opcao B (19/10; DECISOES.md, "2026-10-19 — Opcao B", decisao de implementacao 7): os testes
# verificam comportamento, nao limite, e rodam com os limites da v1.2.3 (600 s, 180 s, 20 min),
# com os quais os esperados foram registrados. Os padroes novos ficam guardados aqui e o caso
# "opB-padroes" os confere.
PADROES_NOVOS = (fe.TEMPO, fe.TEMPO_ETAPA2, fe.ORCAMENTO)
fe.TEMPO, fe.TEMPO_ETAPA2, fe.ORCAMENTO = 600, 180, 20 * 60

FALHAS: list[str] = []
M12, M8, M6 = list(fe.MODELOS)


def confere(condicao: bool, mensagem: str) -> None:
    print(f"   {'ok   ' if condicao else 'FALHA'} {mensagem}")
    if not condicao:
        FALHAS.append(mensagem)


def pela_tela(modelo: str, n_enf: int, n_tec: int, demanda: dict, fds: dict | None = None,
              grau: str = "intermediario") -> AppTest:
    at = AppTest.from_file(str(RAIZ / "src" / "app.py"), default_timeout=1800)
    at.run()
    at.selectbox(key="modelo").set_value(modelo)
    at.selectbox(key="grau").set_value(grau)
    at.date_input(key="inicio").set_value(br.primeira_segunda())
    at.number_input(key="n_enf").set_value(n_enf)
    at.number_input(key="n_tec").set_value(n_tec)
    if fds:
        at.checkbox(key="com_fds").check()
    at.run()
    for nome, (enf, tec) in demanda.items():
        at.number_input(key=f"g_{nome}_enf").set_value(enf)
        at.number_input(key=f"g_{nome}_tec").set_value(tec)
    for nome, (enf, tec) in (fds or {}).items():
        at.number_input(key=f"f_{nome}_enf").set_value(enf)
        at.number_input(key=f"f_{nome}_tec").set_value(tec)
    at.run()
    at.button(key="gerar").click()
    at.run()
    return at


ADMITE_OK = "O quadro informado admite escala legal. Escala gerada."


def textos(at, tipo) -> list[str]:
    return [el.value for el in getattr(at, tipo)]


def metricas(at) -> dict:
    return {m.label: m.value for m in at.metric}


def caso_experimento_a() -> None:
    demanda, fds = {"D": (1, 9), "N": (1, 9)}, {"D": (1, 6), "N": (1, 6)}
    print("1. 12x36, demanda equivalente ao Experimento A (razao 20/29), 40 = 14 + 26")
    at = pela_tela(M12, 14, 26, demanda, fds)
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    confere(textos(at, "success") == [ADMITE_OK],
            f"veredito: {textos(at, 'success') + textos(at, 'warning')}")
    confere(textos(at, "error") == [], f"sem alerta: {textos(at, 'error')}")
    r, e = at.session_state["resultado"]
    ref = br.construir(grau="intermediario", regime="12x36", regra="teto", efetivo=40,
                       variacao=1.0)
    confere(r.inst.demanda == ref.demanda, "demanda montada pela tela = celula v1 do "
                                           "Experimento A")
    confere(r.tentativas == [(40, "viavel", 14, 26)], f"tentativas {r.tentativas}")
    wb = openpyxl.load_workbook(io.BytesIO(fe.planilha(r, e)))
    confere(wb.sheetnames == ["Escala", "Resumo", "Legenda", "Prioridades"],
            f"planilha abre, abas: {wb.sheetnames}")
    confere(wb["Escala"].max_row == 41, f"planilha, aba Escala max_row: {wb['Escala'].max_row}")
    confere(r.conformidade["ok"], "conferencia de descanso: cumpre")

    print("2. mesma configuracao, 39 = 13 + 26")
    at = pela_tela(M12, 13, 26, demanda, fds)
    confere(not at.exception, "sem excecao na tela")
    confere(textos(at, "warning") == ["Falta 1; o menor quadro viável é 40. Escala gerada."],
            f"veredito: {textos(at, 'warning') + textos(at, 'success')}")
    r, _ = at.session_state["resultado"]
    confere(r.tentativas == [(39, "piso", None, None), (40, "viavel", 14, 26)],
            f"tentativas {r.tentativas}")
    confere(r.diagnostico is not None and r.diagnostico[0] == fe.ALTERNANCIA,
            f"diagnostico na tela: {r.diagnostico}")
    confere(len(at.get("subheader")) and any("Alternância" in s.value
                                             for s in at.get("subheader")),
            "janela do diagnostico aparece na tela")


def caso_6h_12h() -> None:
    print("3. modelo 6 h + 12 h, 7 + 12")
    at = pela_tela(M6, 7, 12, {"M": (1, 3), "T": (1, 3), "N": (1, 2)})
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    confere(textos(at, "success") == [ADMITE_OK],
            f"veredito: {textos(at, 'success') + textos(at, 'warning')}")
    confere(metricas(at).get("Conferência de descanso") == "cumpre",
            f"conferencia de descanso na tela: {metricas(at).get('Conferência de descanso')}")


def caso_poucos_enfermeiros() -> None:
    print("4. poucos enfermeiros: 8 h, 5 + 15")
    at = pela_tela(M8, 5, 15, {"M": (1, 3), "T": (1, 3), "N": (1, 2)})
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    confere(textos(at, "success") == [ADMITE_OK],
            f"ainda gera a escala: {textos(at, 'success') + textos(at, 'warning')}")
    alertas = textos(at, "error")
    confere(len(alertas) == 1 and alertas[0].startswith("Alerta COFEN (não impede a escala)")
            and "5 enfermeiros em 20" in alertas[0] and "isto é, 7" in alertas[0],
            f"alerta vermelho: {alertas}")


def caso_enfermeiro_em_posto_de_tecnico() -> None:
    print("5. enfermeiro em posto de tecnico: 8 h, 8 + 5")
    at = pela_tela(M8, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)})
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    confere(textos(at, "success") == [ADMITE_OK],
            f"veredito: {textos(at, 'success') + textos(at, 'warning')}")
    # rotulo encurtado em 05/10 (cortava na tela); o "turnos" foi para a ajuda da metrica
    n = int(metricas(at).get("Enfermeiro em posto de técnico", -1))
    confere(n >= 30, f"contagem na tela: {n} turnos de enfermeiro em posto de tecnico (>= 30)")


# --- Etapa 7, sem tela (a tela nao edita as tabelas de ferias e pedidos no AppTest) ------

M8_TURNOS, M12_TURNOS = fe.MODELOS[M8], fe.MODELOS[M12]


def _entrada(turnos, n_enf, n_tec, demanda, **extra) -> fe.Entrada:
    return fe.Entrada(turnos=turnos, grau="intermediario", n_enfermeiros=n_enf,
                      n_tecnicos=n_tec, demanda_turno=demanda,
                      inicio=br.primeira_segunda(), **extra)


def dia(k: int):
    from datetime import timedelta
    return br.primeira_segunda() + timedelta(days=k)


def caso_objetivo() -> None:
    """Esperado registrado antes: a contagem cai de 71 para 35 ou perto (<= 40), e os 3
    pedidos continuam atendidos."""
    import experimento_a as ea
    import modelo
    print("7.1 objetivo: enfermeiro em posto de tecnico so quando necessario (8 + 5)")
    pedidos = [("Enf 1", dia(3)), ("Téc 2", dia(7)), ("Téc 4", dia(15))]
    e = _entrada(M8_TURNOS, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)}, pedidos=pedidos)
    antes_v, inst, antes = ea.resolver_instancia(fe.montar(e), modelo.SOLVER_PADRAO, fe.TEMPO)
    ind_antes = fe.indicadores(inst, antes)
    r = fe.verificar(e)
    ind = r.indicadores
    confere(r.veredito == fe.ADMITE, f"veredito {r.veredito}")
    print(f"      sem os pesos (Etapa 6): {ind_antes['enf_em_posto_tec']} turnos, pedidos "
          f"{ind_antes['pedidos_atendidos']}/{ind_antes['pedidos_total']}")
    confere(ind["enf_em_posto_tec"] <= 40,
            f"com os pesos: {ind['enf_em_posto_tec']} turnos de enfermeiro em posto de "
            f"tecnico (minimo aritmetico 30 com 44 h; era 35 com 42 h)")
    confere(ind["pedidos_atendidos"] == 3 and
            ind["pedidos_atendidos"] >= ind_antes["pedidos_atendidos"],
            f"pedidos atendidos {ind['pedidos_atendidos']}/3, sem piorar")
    # postos de tecnico no horizonte: (2 + 2 + 1) por dia x 28 dias = 140; W = 141
    confere(ind["peso_pedido"] == 141,
            f"peso de cada pedido = {ind['peso_pedido']} (140 postos de tecnico + 1)")
    confere(r.conformidade["ok"], "conferencia de descanso cumpre")


def caso_tempo_40() -> None:
    """So relata: tempo da etapa de equilibrio num caso de 40 profissionais."""
    print("7.2 equilibrio: 12x36 do Experimento A, 40 profissionais, 20 pedidos de folga")
    nomes = [f"Enf {i + 1}" for i in range(14)] + [f"Téc {i + 1}" for i in range(26)]
    pedidos = [(nomes[i], dia((3 * i) % 28)) for i in range(20)]
    e = _entrada(M12_TURNOS, 14, 26, {"D": (1, 9), "N": (1, 9)},
                 demanda_fds={"D": (1, 6), "N": (1, 6)}, pedidos=pedidos)
    r = fe.verificar(e)
    ind = r.indicadores
    confere(r.veredito == fe.ADMITE and ind["etapa2"] == "ok", f"etapa 2: {ind['etapa2']}")
    print(f"      relogio: etapa 1 {ind['tempo_etapa1']:.1f} s | etapa 2 "
          f"{ind['tempo_etapa2']:.1f} s (appsi_highs, esta maquina) | penalidade "
          f"{ind['penalidade']} | pedidos {ind['pedidos_atendidos']}/{ind['pedidos_total']} "
          f"| enf em posto tec {ind['enf_em_posto_tec']} | amplitude da fracao "
          f"{ind['amplitude_etapa1']:.1%} -> {ind['amplitude']:.1%} "
          f"({'provada' if ind['provado_etapa2'] else 'SEM prova'}) | carga "
          f"{ind['horas_min']:g}-{ind['horas_max']:g} h | pedidos negados: no maximo "
          f"{ind['negados_max']} por pessoa")
    c = r.inst.contratos["0"]
    print(f"      contrato: MinNumAssignments ligada={c.min_num_assignments.ligada} "
          f"valor={c.min_num_assignments.valor} peso={c.min_num_assignments.peso} | "
          f"MaxNumAssignments ligada={c.max_num_assignments.ligada} "
          f"valor={c.max_num_assignments.valor} peso={c.max_num_assignments.peso} | "
          f"tetos em horas {sorted({r.inst.horas_devidas(n) for n in r.inst.profissionais})}")


def _todos_textos(at) -> list[str]:
    return [x for tipo in ("success", "warning", "error", "info", "caption", "markdown")
            for x in textos(at, tipo)]


def casos_tempo() -> None:
    """Os tres desfechos do tempo — esperado no docstring do modulo, registrado antes."""
    import dataclasses
    demanda, fds = {"D": (1, 9), "N": (1, 9)}, {"D": (1, 6), "N": (1, 6)}
    nomes = [f"Enf {i + 1}" for i in range(14)] + [f"Téc {i + 1}" for i in range(26)]
    pedidos = tuple((nomes[i], dia((3 * i) % 28)) for i in range(20))
    original_tempo, original_verificar = fe.TEMPO, fe.verificar
    try:
        print("8a. otimo provado: caso 5, limite 600 s")
        at = pela_tela(M8, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)})
        confere(textos(at, "success") == [ADMITE_OK], f"tela: {textos(at, 'success')}")
        confere(not any("pode haver" in t for t in _todos_textos(at)), "sem 'pode haver'")

        print("8b. escala sem prova: 40 com 20 pedidos, limite 25 s")
        fe.TEMPO = 25
        fe.verificar = lambda e, **kw: original_verificar(
            dataclasses.replace(e, pedidos=pedidos), **kw)
        at = pela_tela(M12, 14, 26, demanda, fds)
        fe.verificar = original_verificar
        avisos = textos(at, "warning")
        confere(len(avisos) == 1 and avisos[0].startswith(
            "O quadro informado admite escala legal. Escala gerada; pode haver uma melhor "
            "(gap"), f"tela: {avisos}")
        confere(textos(at, "success") == [], f"sem success: {textos(at, 'success')}")
        r, _ = at.session_state["resultado"]
        confere(bool(r.escala) and len(at.get("download_button")) == 1,
                "escala e planilha na tela")
        confere(not any(t.startswith("Equilíbrio de carga: não rodou")
                        for t in textos(at, "caption")),
                f"P14: a etapa 2 rodou ({r.indicadores.get('etapa2')})")
        vigente = [t for t in textos(at, "caption") if t.startswith("Escala desta tela:")]
        confere(r.indicadores.get("etapa2") == "ok",
                f"P17: a etapa 2 entregou escala ({r.indicadores.get('etapa2')})")
        # 11/10 (P17, item c): a linha diz a verdade sobre a etapa 2 ter melhorado ou nao
        a1, a2 = r.indicadores.get("amplitude_etapa1"), r.indicadores.get("amplitude")
        melhorou = a1 is not None and a2 is not None and a2 < a1 - 1e-9
        if melhorou:
            linha_esperada = ("Escala desta tela: a da etapa 2, com a carga equilibrada entre "
                              "colegas, sobre uma escala sem prova de ótimo: o equilíbrio não "
                              "deixou piorar o valor achado pela etapa 1.")
        else:
            linha_esperada = ("Escala desta tela: a da etapa 1. O equilíbrio de carga não "
                              "achou, no tempo disponível, escala mais equilibrada sem piorar o "
                              "resultado da etapa 1.")
            confere(a1 is not None and a2 is not None and abs(a2 - a1) <= 1e-9,
                    f"sem melhora, o criterio final e o da etapa 1 ({a1} -> {a2})")
        confere(vigente == [linha_esperada],
                f"escala vigente: {vigente} (criterio {a1} -> {a2})")
        # 05/10: com todos os pedidos atendidos, a tela diz isso, e nao "negados: 0, em 0"
        confere("Todos os 20 pedidos de folga foram atendidos." in textos(at, "caption")
                and not any("negados: 0" in t for t in textos(at, "caption")),
                f"pedidos: {[t for t in textos(at, 'caption') if 'edidos' in t]}")
        print(f"      gap {r.indicadores['gap']:.2%} | pedidos "
              f"{r.indicadores['pedidos_atendidos']}/{r.indicadores['pedidos_total']}")

        print("8c. tempo esgotado sem escala: 40 sem pedidos, limite 3 s")
        fe.TEMPO = 3
        at = pela_tela(M12, 14, 26, demanda, fds)
        confere(textos(at, "error") == ["Sem resposta em 3 s com 40 profissionais: o solver "
                                        "não achou escala nem provou que ela não existe."],
                f"tela: {textos(at, 'error')}")
        confere(not any("Falta" in t for t in _todos_textos(at)), "nenhum 'Falta'")
        r, _ = at.session_state["resultado"]
        confere(r.diagnostico is None and not r.escala
                and len(at.get("download_button")) == 0, "sem diagnostico, escala nem planilha")

        print("8d. 39 provado curto pela conta, 40 sem escala no tempo: limite 3 s")
        at = pela_tela(M12, 13, 26, demanda, fds)
        r, _ = at.session_state["resultado"]
        confere(r.tentativas == [(39, "piso", None, None), (40, "indeterminado", 14, 26)],
                f"tentativas {r.tentativas}")
        confere(r.diagnostico is not None and r.diagnostico[0] == fe.ALTERNANCIA,
                f"diagnostico de alternancia: {r.diagnostico}")
        esperado = ("O quadro informado é insuficiente. Sem resposta em 3 s com 40 "
                    "profissionais: o menor quadro viável não foi determinado.")
        confere(esperado in textos(at, "error"), f"tela: {textos(at, 'error')}")
        confere(not any("Falta" in t for t in _todos_textos(at)), "nenhum 'Falta'")
    finally:
        fe.TEMPO, fe.verificar = original_tempo, original_verificar


def casos_carga() -> None:
    """Carga por contrato (DECISOES.md, "2026-10-02 — Carga por contrato"). Sem tela: o
    AppTest nao edita a tabela de cargas. Esperado registrado ANTES de rodar (03/10):

    9a. Equipe mista 30/44 h: 8 h em tres turnos, M e T com 1 + 3, N com 1 + 2 (2.464 h no
        periodo); 6 + 12, com Enf 1, Enf 2 e Tec 1 a Tec 4 em 30 h (teto 120 h) e o resto em
        44 h (teto 176 h). Capacidade 6 x 120 + 12 x 176 = 2.832 h. Esperado: admite; nenhum
        de 30 h passa de 120 h, nenhum de 44 h passa de 176 h; `conferir_rigidas` sem
        problema.
    9b. 12x36 com 44 h: o 40 do Experimento A (14 + 26), carga padrao. Esperado: ninguem
        passa de 14 plantoes. RESSALVA registrada antes: com 44 h o teto e 176 h, e 15
        plantoes dariam 180 h — o teto tambem para em 14. Alternancia (28 dias, um plantao a
        cada dois dias) e teto coincidem; o teste nao separa qual dos dois limita.
    9c. Ferias: o caso 9a com todos em 44 h e Tec 1 de ferias nos 14 primeiros dias (deve
        88 h). Media esperada da fracao: 2.464 / (17 x 176 + 88) = 80%. Esperado: a fracao de
        Tec 1 fica entre a menor e a maior fracao dos demais, e a amplitude final e no
        maximo 10 pontos percentuais (turnos de 8 h dao degraus de 4,5 pp em 176 h e de
        9 pp em 88 h). Em HORAS, Tec 1 fica bem abaixo dos demais — e e isso que a fracao
        deixa de punir.
    9d. Equilibrio por fracao reduz a amplitude: no mesmo caso 9c, amplitude da etapa 2
        estritamente menor que a da escala da etapa 1.

    RESULTADO DE 03/10 (anotado depois de rodar; o esperado acima NAO foi alterado): 9a, 9b,
    9d e a primeira metade de 9c acertaram. A segunda metade de 9c FALHOU: amplitude final
    27,3%, provada otima, contra <= 10 pp esperados. O ERRO E DO ESPERADO: ele tratou a equipe
    como um grupo so (media 80%) e errou as horas de posto de tecnico (sao 1.792 h, nao
    1.680). Com a penalidade da etapa 1 fixada em 0, enfermeiro nao ocupa posto de tecnico:
    os 6 enfermeiros cobrem exatamente as 672 h de posto de enfermeiro (112 h = 63,6%), e os
    tecnicos, 1.792 h — com 11 deles em <= 152 h nao fecha (11 x 152 + 88 = 1.760), entao
    alguem chega a 160 h (90,9%). Amplitude >= 27,3 pp, que e o que o solver provou. Parado
    para decisao do Otavio (ver resultados/relatorio_2026-10-03.md); nao corrigido aqui.

    ESPERADO NOVO DE 9c, PELO CRITERIO POR CATEGORIA (P6 decidida em 03/10: a etapa 2 soma a
    amplitude entre enfermeiros e a amplitude entre tecnicos). Conta registrada ANTES de rodar,
    03/10. Supoe, como no resultado de 03/10, penalidade da etapa 1 = 0 (nenhum enfermeiro em
    posto de tecnico); tecnico nao cobre posto de enfermeiro. As categorias nao se tocam.
    - Enfermeiros: posto de enfermeiro = 3 turnos x 28 dias = 84 turnos = 672 h para 6 de
      44 h (176 h devidas). 84 / 6 = 14 turnos = 112 h cada, 63,6%. Amplitude 0.
    - Tecnicos: posto de tecnico = (3 + 3 + 2) x 28 = 224 turnos = 1.792 h. Tec 1 deve 88 h
      (fracao em degraus de 1/11 = 9,09 pp); os outros 11 devem 176 h (degraus de 1/22 =
      4,55 pp). Amplitude 0 exige x/11 = y/22 com todos os y iguais: x + 11 x 2x = 23x = 224,
      sem inteiro. Logo a amplitude e >= 1/22 = 4,55 pp. Ela e atingida com Tec 1 em 10 turnos
      (80 h, 90,9%) e os outros somando 214 = 5 x 20 + 6 x 19 (90,9% e 86,4%). Com Tec 1 em
      9 (81,8%) os outros somam 215 > 11 x 19, entao alguem fica em 20 (90,9%): 9,09 pp. Com
      11 (100%) os outros precisariam de >= 21 cada: 11 + 231 > 224. Unico jeito de 4,55 pp:
      Tec 1 em 10 turnos.
    - Esperado: amplitude dos enfermeiros 0; dos tecnicos 4,55 pp (1/22); criterio (soma)
      4,55 pp, provado; Tec 1 em 90,9%, dentro da faixa dos tecnicos (86,4%-90,9%). Ressalva:
      a conta supoe que 20 turnos em 28 dias para um tecnico e 10 turnos em 14 dias para Tec 1
      cabem nas regras de descanso — o resultado de 03/10 ja teve tecnico em 160 h (20 turnos).
    - Mostrado a parte (nao otimizado): fracao media dos enfermeiros 672 / 1.056 = 63,6%, dos
      tecnicos 1.792 / 2.024 = 88,5%; diferenca +24,9 pp. Horas de contrato nao utilizadas:
      enfermeiros 1.056 - 672 = 384 h; tecnicos 2.024 - 1.792 = 232 h.
    - 9d: o criterio da etapa 2 (soma por categoria) estritamente menor que o da escala da
      etapa 1, medido pelo mesmo criterio.

    9b-sem-teto (acrescentado em 03/10, esperado registrado ANTES de rodar). O 9b nao separa
    alternancia de teto. Para separar, desligam-se OS DOIS limites de numero que poderiam
    parar em 14: o teto de horas (`carga_horaria`, 176 h) e o `MaxNumAssignments` do contrato,
    que no 12x36 fica em floor(176 / 12) = 14 e e rigido no modelo brasileiro — desligar so o
    teto de horas deixaria esse parando em 14. E, em vez de olhar a escala da ferramenta (a
    demanda soma 512 plantoes para 40 pessoas, 12,8 em media; ninguem PRECISA passar de 14),
    MAXIMIZA-SE o numero de plantoes de Tec 1, so com as rigidas. Esperado: 14, provado
    otimo — 28 dias sem dois dias seguidos de trabalho (a regra das 36 h, gerada dos
    horarios) admitem no maximo 14. Se der 14, quem limita e a alternancia.

    RESULTADO DE 03/10, criterio por categoria (anotado depois de rodar): 9c acertou em tudo
    (enfermeiros 0, tecnicos 4,55 pp provado, Tec 1 em 90,9%, 384 h e 232 h nao utilizadas,
    +24,9 pp entre categorias); 9d 36,4 -> 4,5 pp; 9b-sem-teto deu 14, provado.

    EXIBICAO DA ETAPA 2 (decisao de 05/10: diferenca maxima de carga entre colegas, em
    plantoes e horas, no lugar do gap). Esperado registrado ANTES de rodar, 05/10, pela escala
    unica de 4,55 pp do 9c: fracao media dos tecnicos 1.792 / 2.024; desvio de cada um = horas -
    media x horas devidas. Tec 1: 80 - 77,9 = +2,1; em 160 h: +4,2; em 152 h: -3,8. Diferenca
    4,2 + 3,8 = 8 h = 1 plantao de 8 h -> "1 plantão (8 h)". Enfermeiros, todos em 112 h:
    "nenhuma (0 h)".

    9c SEM EXIGIR PROVA (decisao do Otavio, 05/10). Esperado registrado ANTES de rodar, 05/10.
    O 9c deixa de exigir que a etapa 2 prove o otimo dentro do limite de 180 s: a prova
    dentro do limite depende da carga da maquina — 146,9 s rodando sozinho, e falhou em 05/10
    com outro processo rodando junto (uma instalacao de pacote). Passa a conferir so que a
    amplitude atingiu o piso da conta ja registrado no commit 08603c6: enfermeiros 0,
    tecnicos 1/22 = 4,55 pp, criterio 4,55 pp; e a tela da etapa 2, "nenhuma (0 h)" e
    "1 plantão (8 h)". Se o tempo nao bastar para chegar ao piso, o teste falha — e isso e
    informacao, nao ruido.

    9c-TELA (acrescentado em 05/10, esperado registrado ANTES de rodar). Se a etapa 2 nao
    provar, a tela e a planilha NAO podem dizer "provado". Para o cenario existir com
    certeza, o limite da etapa 2 e encurtado para 20 s (`fe.TEMPO_ETAPA2`), e o caso 9c entra
    pela tela (as ferias por fora, como os pedidos do 8b). Esperado: a etapa 2 termina sem
    prova; nenhum texto da tela (success, warning, error, info, caption, markdown, metricas,
    subtitulos) nem celula da planilha contem "provad"; a tela mostra a linha "Diferença
    máxima de carga entre colegas".
    """
    print("9a. equipe mista 30/44 h: 8 h, 6 + 12")
    demanda = {"M": (1, 3), "T": (1, 3), "N": (1, 2)}
    trinta = ["Enf 1", "Enf 2", "Téc 1", "Téc 2", "Téc 3", "Téc 4"]
    e = _entrada(M8_TURNOS, 6, 12, demanda, cargas={n: 30 for n in trinta})
    r = fe.verificar(e)
    confere(r.veredito == fe.ADMITE, f"veredito {r.veredito}")
    if r.escala:
        horas = {n: 0.0 for n in r.inst.profissionais}
        for _, n, t in r.escala:
            horas[n] += r.inst.turnos[t].duracao_h
        nome = {n: p.nome for n, p in r.inst.profissionais.items()}
        h30 = max(h for n, h in horas.items() if nome[n] in trinta)
        h44 = max(h for n, h in horas.items() if nome[n] not in trinta)
        confere(h30 <= 120, f"maior carga entre os de 30 h: {h30:g} h (teto 120 h)")
        confere(h44 <= 176, f"maior carga entre os de 44 h: {h44:g} h (teto 176 h)")
        prob = solucao.conferir_rigidas(r.inst, r.escala, habilidade_rigida=True)
        confere(not prob, f"conferir_rigidas: {prob[:2] or 'ok'}")

    print("9b. 12x36 com 44 h: 40 = 14 + 26")
    e = _entrada(M12_TURNOS, 14, 26, {"D": (1, 9), "N": (1, 9)},
                 demanda_fds={"D": (1, 6), "N": (1, 6)})
    r = fe.verificar(e)
    plantoes: dict[str, int] = {}
    for _, n, _t in r.escala:
        plantoes[n] = plantoes.get(n, 0) + 1
    confere(r.veredito == fe.ADMITE and max(plantoes.values()) <= 14,
            f"maior numero de plantoes: {max(plantoes.values(), default=0)} (<= 14)")
    print(f"      teto em horas {sorted({r.inst.horas_devidas(n) for n in r.inst.profissionais})}"
          f" h; 15 plantoes seriam 180 h")

    print("9c/9d. ferias: 8 h, 6 + 12 em 44 h, Tec 1 de ferias nos 14 primeiros dias")
    e = _entrada(M8_TURNOS, 6, 12, demanda,
                 indisponibilidades=[("Téc 1", dia(0), dia(13))])
    r = fe.verificar(e)
    ind = r.indicadores
    confere(r.veredito == fe.ADMITE and ind.get("etapa2") == "ok",
            f"veredito {r.veredito}, etapa 2 {ind.get('etapa2')}")
    if r.escala:
        f = fe.fracoes(r.inst, r.escala)
        tec1 = next(n for n, p in r.inst.profissionais.items() if p.nome == "Téc 1")
        outros = [v for n, v in f.items() if n != tec1]
        horas = {n: v * r.inst.horas_devidas(n) for n, v in f.items()}
        print(f"      Tec 1: {horas[tec1]:g} h de 88 h devidas = {f[tec1]:.1%} | demais: "
              f"{min(outros):.1%}-{max(outros):.1%} "
              f"({min(horas[n] for n in f if n != tec1):g}-"
              f"{max(horas[n] for n in f if n != tec1):g} h)")
        confere(min(outros) - 1e-9 <= f[tec1] <= max(outros) + 1e-9,
                "9c: fracao de Tec 1 dentro da faixa dos demais")
        cat = ind["categorias"]
        print(f"      enfermeiros {cat[fe.ENF]['fracao_min']:.1%}-{cat[fe.ENF]['fracao_max']:.1%}"
              f", nao utilizadas {cat[fe.ENF]['nao_utilizadas']:g} h | tecnicos "
              f"{cat[fe.TEC]['fracao_min']:.1%}-{cat[fe.TEC]['fracao_max']:.1%}, nao "
              f"utilizadas {cat[fe.TEC]['nao_utilizadas']:g} h | diferenca entre categorias "
              f"{ind['diferenca_categorias'] * 100:+.1f} pp | penalidade {ind['penalidade']}")
        tec = [v for n, v in f.items() if n != tec1 and fe.categoria(r.inst, n) == fe.TEC]
        confere(min(tec) - 1e-9 <= f[tec1] <= max(tec) + 1e-9,
                f"9c: Tec 1 ({f[tec1]:.1%}) dentro da faixa dos tecnicos "
                f"({min(tec):.1%}-{max(tec):.1%})")
        confere(abs(cat[fe.ENF]["amplitude"]) <= 1e-6,
                f"9c: amplitude entre enfermeiros {cat[fe.ENF]['amplitude']:.2%} (esperado 0)")
        confere(abs(cat[fe.TEC]["amplitude"] - 1 / 22) <= 1e-6,
                f"9c: amplitude entre tecnicos {cat[fe.TEC]['amplitude']:.2%} (esperado 4,55%)")
        # Decisao de 05/10: NAO se exige prova dentro do limite (ver docstring de
        # `casos_carga`, "9c SEM EXIGIR PROVA"); confere-se o piso da conta.
        confere(abs(ind["amplitude"] - 1 / 22) <= 1e-6,
                f"9c: criterio da etapa 2 {ind['amplitude']:.2%} (piso da conta 4,55%; "
                f"provado no limite: {ind['provado_etapa2']}, informativo)")
        confere(abs(cat[fe.ENF]["nao_utilizadas"] - 384) <= 1e-6
                and abs(cat[fe.TEC]["nao_utilizadas"] - 232) <= 1e-6,
                "9c: horas nao utilizadas 384 h (enf) e 232 h (tec)")
        confere(fe.fmt_diferenca(cat[fe.TEC]) == "1 plantão (8 h)"
                and fe.fmt_diferenca(cat[fe.ENF]) == "nenhuma (0 h)",
                f"9c: diferenca entre colegas: tecnicos {fe.fmt_diferenca(cat[fe.TEC])!r}, "
                f"enfermeiros {fe.fmt_diferenca(cat[fe.ENF])!r}")
        confere(ind["amplitude"] < ind["amplitude_etapa1"] - 1e-9,
                f"9d: amplitude {ind['amplitude_etapa1']:.1%} na etapa 1 -> "
                f"{ind['amplitude']:.1%} na etapa 2 ({'provada' if ind['provado_etapa2'] else 'SEM prova'})"
                f"; etapa 2 em {ind['tempo_etapa2']:.1f} s")


def caso_9c_tela() -> None:
    """Esperado no docstring de `casos_carga` (9c-TELA), registrado antes de rodar."""
    import dataclasses
    print("9c-tela. 9c pela tela, etapa 2 com limite de 20 s: nada pode dizer 'provado'")
    ferias = [("Téc 1", dia(0), dia(13))]
    original_tempo2, original_verificar = fe.TEMPO_ETAPA2, fe.verificar
    try:
        fe.TEMPO_ETAPA2 = 20
        fe.verificar = lambda e, **kw: original_verificar(
            dataclasses.replace(e, indisponibilidades=ferias), **kw)
        at = pela_tela(M8, 6, 12, {"M": (1, 3), "T": (1, 3), "N": (1, 2)})
    finally:
        fe.TEMPO_ETAPA2, fe.verificar = original_tempo2, original_verificar
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    r, e = at.session_state["resultado"]
    ind = r.indicadores
    confere(ind.get("etapa2") == "ok" and not ind.get("provado_etapa2"),
            f"cenario do teste: etapa 2 {ind.get('etapa2')}, provada: "
            f"{ind.get('provado_etapa2')} (esperado: ok, sem prova)")
    tela = _todos_textos(at) + [str(m.label) for m in at.metric] + \
        [str(m.value) for m in at.metric] + [s.value for s in at.get("subheader")]
    wb = openpyxl.load_workbook(io.BytesIO(fe.planilha(r, e)))
    planilha_txt = [str(c.value) for ws in wb.worksheets for linha in ws.iter_rows()
                    for c in linha if c.value is not None]
    com_prova = [t for t in tela + planilha_txt if "provad" in t.lower()]
    confere(not com_prova, f"nenhum 'provado' na tela nem na planilha: {com_prova[:3]}")
    confere(any("Diferença máxima de carga entre colegas" in t for t in textos(at, "caption")),
            "a tela mostra a diferenca maxima de carga entre colegas")


def caso_9b_sem_teto(tempo: int = 600) -> None:
    """Esperado no docstring de `casos_carga` (9b-sem-teto), registrado antes de rodar."""
    import dataclasses
    import experimento_a as ea
    import pyomo.environ as pyo
    print("9b-sem-teto. 12x36, 14 + 26, sem teto de horas e sem MaxNumAssignments: maximo de "
          "plantoes de Tec 1")
    e = _entrada(M12_TURNOS, 14, 26, {"D": (1, 9), "N": (1, 9)},
                 demanda_fds={"D": (1, 6), "N": (1, 6)})
    inst = fe.montar(e)
    inst = dataclasses.replace(inst, contratos={
        k: dataclasses.replace(c, max_num_assignments=dataclasses.replace(
            c.max_num_assignments, ligada=False)) for k, c in inst.contratos.items()})
    m = ea.modelo_br(inst)
    confere(hasattr(m, "carga_horaria"), "o modelo tem o teto de horas (a desligar)")
    m.carga_horaria.deactivate()
    tec1 = next(n for n, p in inst.profissionais.items() if p.nome == "Téc 1")
    m.objetivo.deactivate()
    m.max_tec1 = pyo.Objective(expr=sum(m.y[tec1, d] for d in inst.dias), sense=pyo.maximize)
    veredito, escala, provado, gap = fe.resolver(m, tempo)
    n = sum(1 for _, p, _t in escala if p == tec1) if escala else None
    confere(veredito == ea.VIAVEL and provado and n == 14,
            f"maximo de plantoes de Tec 1 sem os dois tetos: {n} (esperado 14, provado: "
            f"{provado})")


DIAGNOSTICOS = [
    # (rotulo, entrada, motivo esperado, menor viavel esperado, trecho esperado no texto)
    ("horas: 8 h, 1+3 por turno, 4 + 10",
     lambda: _entrada(M8_TURNOS, 4, 10, {"M": (1, 3), "T": (1, 3), "N": (1, 3)}),
     fe.HORAS, None, "faltam pelo menos 2"),
    ("alternancia: Experimento A com 39",
     lambda: _entrada(M12_TURNOS, 13, 26, {"D": (1, 9), "N": (1, 9)},
                      demanda_fds={"D": (1, 6), "N": (1, 6)}),
     fe.ALTERNANCIA, 40, "seg 04/01 e ter 05/01"),
    ("categoria: 8 h, 1+2 por turno, 3 + 20",
     lambda: _entrada(M8_TURNOS, 3, 20, {"M": (1, 2), "T": (1, 2), "N": (1, 2)}),
     fe.CATEGORIA, 24, "pelo menos 1 enfermeiro"),
    ("dia: 8 h, 1+2, 6 + 8, Tec 1 a 6 de licenca em 14/01",
     lambda: _entrada(M8_TURNOS, 6, 8, {"M": (1, 2), "T": (1, 2), "N": (1, 2)},
                      indisponibilidades=[(f"Téc {i}", dia(10), dia(10))
                                          for i in range(1, 7)]),
     fe.DIA, 15, "qui 14/01"),
    # P7 (05/10): esperado refeito pela conta ANTES de rodar. Teto de cada um = menor entre
    # contrato nos dias disponiveis e 12 h x soma de ceil(bloco/2): Enf 1, 2, 4 = min(176,
    # 168) = 168 h; Enf 3 (licenca sab 09 e dom 10/01) = min(44 x 26/7 = 163,4; 12 x (3 +
    # 11) = 168) = 163,4 h. Enfermeiros: 672 h de posto contra 667,4 h -> CATEGORIA (horas).
    # Par sab 09 / dom 10/01: 4 plantoes, 3 pessoas disponiveis -> ALTERNANCIA (par). Era
    # "combinacao"; passa a motivo mais especifico, e verdadeiro.
    ("combinacao -> categoria: 12x36 so enfermeiro, 4, Enf 3 de licenca 09 e 10/01",
     lambda: _entrada(M12_TURNOS, 4, 0, {"D": (1, 0), "N": (1, 0)},
                      indisponibilidades=[("Enf 3", dia(5), dia(6))]),
     fe.CATEGORIA, 5, "sáb 09/01 e dom 10/01"),
]


def casos_grau_alerta() -> None:
    """Grau do alerta de proporcao com graus misturados (DECISOES.md, "2026-10-05 — Grau da
    proporcao: o grupo de pacientes de maior carga"). So contas, sem solver. Esperado
    registrado ANTES de rodar (05/10):

    4b. Clinica da demonstracao (8 minimos, 14 intermediarios, 4 de alta dependencia): carga
        por grupo = 8 x 4 = 32 h, 14 x 6 = 84 h, 4 x 10 = 40 h -> grupo de maior carga
        INTERMEDIARIO, 33%. Com 10 enfermeiros em 30: nenhum alerta de proporcao (exige
        ceil(0,33 x 30) = 10). Com 8 em 30, o alerta diz "intermediário", "84 h" e "10".
    4c. Campo da tela diz intermediario, pacientes 2 minimos + 5 de alta dependencia: 8 h
        contra 50 h -> ALTA, 36%. Com 8 enfermeiros em 30: alerta com "alta dependência" e
        "isto é, 11" (ceil(0,36 x 30) = 10,8 -> 11) — o campo nao vale com pacientes.
    4d. Sem pacientes: vale o campo (intermediario, 33%), e o alerta diz que e o grau
        informado; com 8 em 30, "isto é, 10".
    4e. Empate (3 minimos = 12 h, 2 intermediarios = 12 h): regra NAO decidida (P8). A
        ferramenta nao escolhe em silencio: o alerta diz "empate" e nomeia os dois graus.
    """
    import dataclasses
    sys.path.insert(0, str(RAIZ / "docs" / "demonstracao"))
    import caso_clinica_medica as caso
    e = caso.entrada()
    inst = fe.montar(e)
    n_enf = sum(1 for p in inst.profissionais.values() if br.HABILIDADE_ENF in p.habilidades)
    print(f"4b. grau do alerta, clinica da demonstracao ({n_enf} enf. em {len(inst.profissionais)})")
    g, texto_g = br.grau_do_alerta("intermediario", caso.PACIENTES)
    confere(g == "intermediario" and "84 h" in texto_g, f"grau {g}: {texto_g}")
    prop = [a for a in br.alertas_cofen(inst, e.grau, caso.PACIENTES) if "Parecer pede" in a]
    confere(not prop if n_enf >= 10 else prop, f"alerta de proporcao: {prop}")
    base8 = _equipe_mista(8, 22)
    a8 = [a for a in br.alertas_cofen(base8, "intermediario", caso.PACIENTES)
          if "Parecer pede" in a]
    confere(len(a8) == 1 and "intermediário" in a8[0] and "84 h" in a8[0]
            and "isto é, 10" in a8[0], f"8 em 30: {a8}")

    print("4c. pacientes mandam no grau, nao o campo")
    a = [x for x in br.alertas_cofen(base8, "intermediario", {"minimo": 2, "alta": 5})
         if "Parecer pede" in x]
    confere(len(a) == 1 and "alta dependência" in a[0] and "isto é, 11" in a[0], f"{a}")

    print("4d. sem pacientes, vale o campo")
    a = [x for x in br.alertas_cofen(base8, "intermediario", None) if "Parecer pede" in x]
    confere(len(a) == 1 and "informado" in a[0] and "isto é, 10" in a[0], f"{a}")

    print("4e. empate: a ferramenta diz, nao escolhe em silencio")
    a = [x for x in br.alertas_cofen(base8, "intermediario", {"minimo": 3, "intermediario": 2})
         if "Parecer pede" in x or "empate" in x.lower()]
    confere(any("empate" in x.lower() and "mínimo" in x and "intermediário" in x for x in a),
            f"{a}")


def _equipe_mista(n_enf: int, n_tec: int):
    """Instancia de 12x36 com n_enf + n_tec, so para os alertas (sem solver)."""
    return fe.montar(_entrada(M12_TURNOS, n_enf, n_tec, {"D": (1, 5), "N": (1, 5)}))


def casos_diagnostico_p7() -> None:
    """P7, diagnostico da trava (DECISOES.md, "2026-10-05 — Diagnostico da trava: teto pela
    alternancia e ferias no par"). So contas, sem solver. Esperado registrado ANTES de rodar
    (05/10), pela conta de `docs/demonstracao/cortes_esperados.md`, refeita aqui com o teto
    novo:

    7.4a. Clinica medica da demonstracao, 8 + 20, feriados 02/11 e 15/11 (os da demonstracao
          de 05/10; o 20/11 fica de fora aqui de proposito, para o teste nao depender do
          roteiro). Tetos: tecnicos 3.132 h para 3.456 h de posto de tecnico -> faltam 324 h;
          enfermeiros 1.212 h para 900 h de posto -> folga 312 h. 324 > 312: HORAS dispara,
          com "324 h" e "312 h" no texto. Par ter 03/11 e qua 04/11: 28 plantoes, 27 pessoas
          disponiveis (Karen Dias de ferias): ALTERNANCIA dispara, com "28 plantões" e "27".
          Os dois motivos, nessa ordem.
    7.4b. A mesma com 8 + 21: tecnicos faltam 156 h, folga 312 h; par 28 para 28. Nenhum
          motivo simples dispara.
    7.4c. Teto de uma pessoa: 44 h com o horizonte inteiro no 12x36 = 168 h (14 plantoes,
          nao 176 h); Karen Dias (44 h, ferias de 02 a 15/11) = 84 h (7 plantoes em 14 dias);
          36 h = 144 h. Teto e limite SUPERIOR: na escala de 30 da rodada 1 de 05/10, ninguem
          passou dele.
    """
    import dataclasses
    from datetime import date
    sys.path.insert(0, str(RAIZ / "docs" / "demonstracao"))
    import caso_clinica_medica as caso
    feriados = (date(2026, 11, 2), date(2026, 11, 15))

    # A equipe e os feriados de 05/10 (8 enfermeiros; 22 tecnicos na lista; feriados 02 e
    # 15/11), congelados aqui: o roteiro mudou depois (10 + 20, 20/11 feriado) e o esperado
    # deste teste foi registrado sobre a equipe antiga.
    enf8 = caso.ENFERMEIROS[:8]
    tec22 = caso.TECNICOS + [n for n in ("Cíntia Zanetti", "Diego Amaral")
                             if n not in caso.TECNICOS]

    def entrada(n_tec):
        e = caso.entrada(min(n_tec, len(caso.TECNICOS)))
        tecnicos = tec22[:n_tec]
        return dataclasses.replace(
            e, n_enfermeiros=8, nomes_enfermeiros=enf8, n_tecnicos=n_tec,
            nomes_tecnicos=tecnicos,
            cargas={n: c for n, c in e.cargas.items() if n in enf8 + tecnicos},
            indisponibilidades=[f for f in caso.FERIAS if f[0] in enf8 + tecnicos],
            pedidos=[x for x in caso.PEDIDOS if x[0] in enf8 + tecnicos],
            demanda_data={k: v for k, v in e.demanda_data.items() if k[0] in feriados})

    print("7.4a. P7: clinica medica, 8 + 20")
    inst = fe.montar(entrada(20))
    motivos = fe.motivos_da_trava(inst)
    texto = " ".join(t for _, t in motivos)
    print(f"      {[m for m, _ in motivos]}: {texto}")
    confere([m for m, _ in motivos] == [fe.HORAS, fe.ALTERNANCIA],
            f"motivos {[m for m, _ in motivos]} (esperado horas, alternancia)")
    confere("324 h" in texto and "312 h" in texto, "horas: 324 h contra 312 h no texto")
    confere("ter 03/11 e qua 04/11" in texto and "28 plantões" in texto and " 27 " in texto,
            "par ter 03/11 e qua 04/11: 28 plantoes, 27 pessoas")
    d = fe.diagnosticar(inst)
    confere(d[0] == fe.HORAS and d[2] == [fe.HORAS, fe.ALTERNANCIA],
            f"diagnosticar: motivo {d[0]}, todos {d[2]}")

    print("7.4b. P7: clinica medica, 8 + 21")
    motivos = fe.motivos_da_trava(fe.montar(entrada(21)))
    confere(motivos == [], f"nenhum motivo simples: {[m for m, _ in motivos]}")

    print("7.4c. P7: teto de cada pessoa")
    inst = fe.montar(entrada(22))
    nome = {p.nome: n for n, p in inst.profissionais.items()}
    tetos = {n: fe.teto_horas(inst, nome[n]) for n in ("Ana Ribeiro", "Karen Dias",
                                                      "Gabriela Pires")}
    confere(tetos == {"Ana Ribeiro": 168, "Karen Dias": 84, "Gabriela Pires": 144},
            f"tetos {tetos} (esperado 168, 84, 144)")
    import openpyxl as ox
    planilha = RAIZ / "docs" / "demonstracao" / "rodada1_escala.xlsx"
    if planilha.exists():
        ws = ox.load_workbook(planilha)["Escala"]
        cab = [c.value for c in ws[1]]
        excede = []
        for linha in ws.iter_rows(min_row=2, values_only=True):
            n = linha[0]
            plantoes = sum(1 for v in linha[3:] if v and v != "indisp.")
            if n in nome and plantoes * 12 > fe.teto_horas(inst, nome[n]) + 1e-9:
                excede.append(n)
        confere(not excede and cab[0] == "Profissional",
                f"na escala da rodada 1, ninguem acima do teto: {excede}")


def casos_diagnostico() -> None:
    print("7.3 diagnostico da trava (motivo esperado registrado antes)")
    for rotulo, entrada, motivo, menor, trecho in DIAGNOSTICOS:
        r = fe.verificar(entrada())
        obtido = r.diagnostico[0] if r.diagnostico else None
        confere(obtido == motivo, f"{rotulo}: motivo {obtido} (esperado {motivo})")
        if r.diagnostico:
            confere(trecho in r.diagnostico[1], f"   texto: {r.diagnostico[1]}")
        if menor is None:
            confere(r.menor_viavel is not None and r.menor_viavel >= 16,
                    f"   {r.frase()}")
        else:
            confere(r.menor_viavel == menor, f"   {r.frase()} tentativas {r.tentativas}")


# --- P12 (08/10): escala da etapa 1 ja, mensagens de falha, orcamento do clique -----------

def tabela_da_escala(at):
    """A grade da escala na tela, achada pelas colunas (Categoria, Turnos), nao pela posicao:
    o formulario tem outras cinco tabelas antes dela (turnos, cargas, ferias, pedidos, demanda
    por data). Exige exatamente uma: se a grade provisoria da etapa 1 nao tivesse sido apagada,
    seriam duas. Correcao de 08/10 (autorizada pelo Otavio): ate entao o 12a lia
    `at.dataframe[0]`, que e a tabela de turnos — defeito do teste, nao da ferramenta."""
    escalas = [t.value for t in at.dataframe
               if list(t.value.columns[:2]) == ["Categoria", "Turnos"]]
    confere(len(escalas) == 1, f"uma so grade de escala na tela: {len(escalas)}")
    return escalas[0] if escalas else None


def confere_tela_e_planilha(at, r, e) -> None:
    """12a: a grade da tela e a da planilha baixada, e a planilha e `r.escala`, celula a
    celula. Separado para o teste do teste rodar a mesma conferencia com uma escala alterada."""
    import pandas as pd
    grade_tela = tabela_da_escala(at)
    grade_planilha = pd.read_excel(io.BytesIO(fe.planilha(r, e)), sheet_name="Escala",
                                   index_col=0)
    confere(grade_tela is not None
            and list(grade_tela.index) == list(grade_planilha.index)
            and grade_tela.fillna("").astype(str).values.tolist()
            == grade_planilha.fillna("").astype(str).values.tolist(),
            "grade da tela = grade da planilha")
    planilha = openpyxl.load_workbook(io.BytesIO(fe.planilha(r, e)))["Escala"]
    celulas = {(row[0], col): v for row in planilha.iter_rows(min_row=2, values_only=True)
               for col, v in enumerate(row[3:])}
    rot = {s: (t.id[:-1] + "*" if br.HABILIDADE_ENF in t.habilidades else t.id)
           for s, t in r.inst.turnos.items()}
    confere(all(celulas.get((r.inst.profissionais[n].nome, r.inst.indice(d))) == rot[s]
                for d, n, s in r.escala)
            and sum(1 for v in celulas.values() if v and v != "indisp.") == len(r.escala),
            "planilha = r.escala, celula a celula")


def casos_p12() -> None:
    """12a, 12c e 12d — esperado no docstring do modulo, registrado antes de implementar."""
    import contextlib
    import modelo
    caso5 = (M8, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)})

    print("12a. escala da etapa 1 avisada antes da etapa 2 (caso 5)")
    eventos = []
    e = _entrada(M8_TURNOS, 8, 5, caso5[3])
    fe.verificar(e, aviso=lambda evento, **d: eventos.append((evento, d)))
    nomes = [ev for ev, _ in eventos]
    confere("escala_etapa1" in nomes and "etapa2" in nomes
            and nomes.index("escala_etapa1") < nomes.index("etapa2"),
            f"ordem dos avisos: {nomes}")
    d1 = dict(eventos)["escala_etapa1"]
    confere(fe.cumpre(d1["inst"], fe.medir(d1["inst"], d1["escala"])),
            "a escala da etapa 1 cumpre o descanso")
    at = pela_tela(*caso5)
    r, e = at.session_state["resultado"]
    linha = [t for t in textos(at, "caption") if t.startswith("Escala desta tela:")]
    etapa2 = r.indicadores.get("etapa2")
    if etapa2 == "ok":
        confere(linha == ["Escala desta tela: a da etapa 2, com a carga equilibrada entre "
                          "colegas."], f"linha da escala vigente: {linha} (etapa 2 {etapa2})")
    else:
        confere(len(linha) == 1 and "a da etapa 1" in linha[0],
                f"linha da escala vigente: {linha} (etapa 2 {etapa2})")
    confere_tela_e_planilha(at, r, e)

    print("12c. erro tecnico: solver que levanta excecao (caso 5)")
    original = modelo.resolver

    def quebrado(*a, **k):
        raise RuntimeError("falha simulada do solver (teste 12c)")

    console = io.StringIO()
    modelo.resolver = quebrado
    try:
        with contextlib.redirect_stdout(console), contextlib.redirect_stderr(console):
            at = pela_tela(*caso5)
    finally:
        modelo.resolver = original
    confere(textos(at, "error") == ["Erro técnico ao resolver com 13 profissionais; detalhes "
                                    "no console."], f"tela: {textos(at, 'error')}")
    confere(not any("solver falhou" in t for t in _todos_textos(at)), "nenhum 'o solver falhou'")
    saida = console.getvalue()
    confere("Traceback" in saida and "falha simulada do solver (teste 12c)" in saida,
            f"console com o traceback: {saida[-300:]!r}")

    print("12d. orcamento do clique de 3 s: o 39 cai no piso, o 40 nao e decidido")
    demanda, fds = {"D": (1, 9), "N": (1, 9)}, {"D": (1, 6), "N": (1, 6)}
    original_orc = fe.ORCAMENTO
    fe.ORCAMENTO = 3
    try:
        at = pela_tela(M12, 13, 26, demanda, fds)
    finally:
        fe.ORCAMENTO = original_orc
    r, _ = at.session_state["resultado"]
    confere(r.tentativas[0] == (39, "piso", None, None)
            and all(t[0] == 40 for t in r.tentativas[1:]) and not r.escala,
            f"tentativas {r.tentativas}")
    confere("O quadro informado é insuficiente; o menor quadro viável não foi determinado em "
            "3 s." in textos(at, "error"), f"tela: {textos(at, 'error')}")
    confere(r.diagnostico is not None and r.diagnostico[0] == fe.ALTERNANCIA,
            f"diagnostico de alternancia: {r.diagnostico}")
    confere(not any("Falta" in t for t in _todos_textos(at)), "nenhum 'Falta'")


# --- P15 (09/10): alerta de descanso semanal abaixo de 35 h, sem as bordas -----------------

def casos_p15() -> None:
    """15a a 15d — esperado no docstring do modulo, registrado antes de implementar."""
    import json
    from datetime import date
    import pandas as pd
    sys.path.insert(0, str(RAIZ / "docs" / "demonstracao"))
    sys.path.insert(0, str(RAIZ / "docs" / "diagnostico"))
    import conferencia_descanso_escala as cd
    import caso_clinica_medica as caso
    import conferir_planilhas as cp
    import caso_otavio_0910 as co

    print("15a. caso montado: 32 h interno, 31 h so na borda")
    inst = fe.montar(_entrada(M8_TURNOS, 1, 2, {"M": (0, 1), "T": (0, 1), "N": (0, 0)}))
    d = inst.dias
    escala = ([(d[k], "0", "T") for k in range(5)] + [(d[6], "0", "M")]
              + [(d[k], "1", "M") for k in list(range(5)) + list(range(7, 12))]
              + [(d[k], "2", "M") for k in range(1, 7)])
    m = fe.medir(inst, escala)
    interno = cd.semanal_sem_bordas(inst, escala)
    alertas = fe.alertas_descanso(inst, escala)
    confere(m["menor_semanal"] == 31, f"medir (trava, com bordas): {m['menor_semanal']} h (31)")
    confere(interno == {"0": 32, "1": 64, "2": None}, f"sem bordas por pessoa: {interno}")
    confere(len(alertas) == 1 and "1 profissional" in alertas[0] and "32 h" in alertas[0]
            and "Súmula 110" in alertas[0], f"alerta: {alertas}")

    print("15b. planilhas da demonstracao (12x36): sem alerta")
    for rodada, tec in cp.RODADAS.items():
        tab = pd.read_excel(RAIZ / "docs" / "demonstracao" / f"{rodada}_escala.xlsx",
                            sheet_name="Escala", index_col=0)
        e = caso.entrada(tec)
        inst_d = cp.instancia(e, list(tab.index))
        cod = {v: k for k, v in fe.rotulos(inst_d).items()}
        nome = {p.nome: n for n, p in inst_d.profissionais.items()}
        esc = [(dd, nome[pessoa], cod[c]) for pessoa, linha in tab.iterrows()
               for k, dd in enumerate(inst_d.dias)
               if isinstance(c := linha.iloc[2 + k], str) and c and c != "indisp."]
        valores = [v for v in cd.semanal_sem_bordas(inst_d, esc).values() if v is not None]
        confere(not fe.alertas_descanso(inst_d, esc) and min(valores) >= 35,
                f"{rodada}: sem alerta; minimo sem bordas {min(valores):g} h")

    print("15c. caso do Otavio de 09/10 (6 h + 12 h): so a borda fica abaixo de 35 h")
    inst_o = fe.montar(co.entrada())
    arq = RAIZ / "resultados" / "p14_p15_2026-10-09" / "otavio_antes_escala.json"
    esc_o = [(date.fromisoformat(x), n, s) for x, n, s in json.loads(arq.read_text())]
    valores = [v for v in cd.semanal_sem_bordas(inst_o, esc_o).values() if v is not None]
    confere(not fe.alertas_descanso(inst_o, esc_o), "sem alerta")
    confere(min(valores) == 36, f"minimo sem bordas {min(valores):g} h (36)")
    confere(fe.medir(inst_o, esc_o)["menor_semanal"] == 31, "medir (trava) continua 31 h")

    print("15d. tela: indicador sem bordas e alerta em amarelo")
    original = fe.verificar

    def com_alerta(e, **kw):
        r = original(e, **kw)
        r.alertas_descanso = alertas
        return r

    fe.verificar = com_alerta
    try:
        at = pela_tela(M8, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)})
    finally:
        fe.verificar = original
    r, _ = at.session_state["resultado"]
    semanal = fe.fmt_semanal(r.conformidade["menor_semanal_interno"])
    confere(any(f"descanso semanal {semanal}" in t for t in textos(at, "caption")),
            f"indicador sem bordas na tela ({semanal})")
    confere(alertas[0] in textos(at, "warning"), f"alerta em amarelo: {textos(at, 'warning')}")


# --- 13/10: escala que reprova na conferencia de descanso nao e entregue --------------------

EDITADOS = [("N", 23, 7), ("M", 5, 13)]


def _reprovada(inst):
    """Ciclo N, folga, M: toda folga isolada da 22 h (N termina 07:00, M comeca 05:00)."""
    return [(d, "0", "NM"[k % 3 // 2]) for k, d in enumerate(inst.dias) if k % 3 != 1]


def caso_reprovada() -> None:
    """16 — esperado no docstring do modulo, registrado antes de implementar."""
    original = fe.resolver_com_objetivo
    editada = fe.montar(_entrada(EDITADOS, 1, 1, {"N": (0, 0), "M": (0, 0)}))
    m = fe.medir(editada, _reprovada(editada))
    confere(m["menor_semanal"] == 22 and not fe.cumpre(editada, m),
            f"escala montada: descanso semanal {m['menor_semanal']:g} h, reprova")

    def entrega_reprovada(inst, tempo, aviso=None, prazo=None):
        return fe.ea.VIAVEL, editada, _reprovada(editada), {}

    fe.resolver_com_objetivo = entrega_reprovada
    try:
        print("16. sem tela")
        r = fe.verificar(_entrada(EDITADOS, 1, 1, {"N": (0, 0), "M": (0, 0)}), tempo=5)
        frase = r.frase()
        confere(r.veredito != fe.ADMITE and not r.escala and r.menor_viavel is None,
                f"veredito {r.veredito}, sem escala")
        confere("não cumpre a conferência de descanso (art. 67)" in frase and "22 h" in frase
                and frase.endswith("Não use esta escala."), f"frase: {frase}")
        confere(r.tentativas and r.tentativas[0][1] == fe.REPROVADA,
                f"tentativas {r.tentativas}")
        print("16. pela tela")
        at = pela_tela(M8, 1, 1, {"M": (0, 0), "T": (0, 0), "N": (0, 0)})
    finally:
        fe.resolver_com_objetivo = original
    r, _ = at.session_state["resultado"]
    confere(r.frase() in textos(at, "error"), f"erro na tela: {textos(at, 'error')}")
    confere(not any("admite escala legal" in t for t in _todos_textos(at)),
            "nenhum 'admite escala legal'")
    confere(len(at.get("download_button")) == 0, "sem botao de planilha")


# --- Opcao B (19/10): prioridades da escala --------------------------------------------------
# Esperado registrado antes de implementar: resultados/opcao_b_2026-10-19/ESPERADO.md.

def _pequeno(pedidos: bool = True, prioridades=None) -> fe.Entrada:
    """12x36, 1 enfermeiro + 2 tecnicos, D com 1 tecnico por dia, N sem demanda; pedidos de
    folga dos dois tecnicos no primeiro dia (ESPERADO.md, item b)."""
    ini = br.primeira_segunda()
    return fe.Entrada(turnos=M12_TURNOS, grau="intermediario", n_enfermeiros=1, n_tecnicos=2,
                      demanda_turno={"D": (0, 1), "N": (0, 0)}, inicio=ini,
                      pedidos=[("Téc 1", ini), ("Téc 2", ini)] if pedidos else [],
                      prioridades=prioridades)


def _por_criterio(r) -> dict:
    return {nome: (v, k) for _, nome, v, k in r.criterios}


def _todas_suaves(nivel) -> dict:
    p = fe.prioridades_padrao()
    for c in pr.CRITERIOS:
        if not c.clt and c.id not in ("pedido_folga", "enf_posto_tec"):
            p[c.id] = (nivel, c.limite)
    return p


def caso_opb_sequencia() -> None:
    """(b) sequencia = definicao: (0, 1, 14), fundido e em sequencia, e a definicao a parte."""
    import pyomo.environ as pyo
    import experimento_a as ea
    import modelo
    p = dict(fe.prioridades_padrao(), min_turnos=(fe.DESEJAVEL, 14))
    nomes = ("Pedido de folga no dia", "Enfermeiro em posto de técnico",
             "Mínimo de turnos no período")
    for rotulo, limite_fusao, caminho in (("fundido", pr.LIMITE_FUSAO, "fundido"),
                                          ("em sequencia", 0, "em sequência, 3 blocos")):
        print(f"opB-b. caso pequeno, 3 niveis, caminho {rotulo}")
        original = pr.LIMITE_FUSAO
        pr.LIMITE_FUSAO = limite_fusao
        try:
            r = fe.verificar(_pequeno(prioridades=p))
        finally:
            pr.LIMITE_FUSAO = original
        c = _por_criterio(r)
        confere(r.veredito == fe.ADMITE and r.provado, f"{rotulo}: veredito {r.veredito}, "
                                                       f"provado {r.provado}")
        confere(r.indicadores.get("caminho") == caminho,
                f"{rotulo}: caminho {r.indicadores.get('caminho')}")
        confere([c.get(n, (None,))[0] for n in nomes] == [0, 1, 14],
                f"{rotulo}: violacoes por nivel {[c.get(n) for n in nomes]}")
        confere(c.get(nomes[0]) == (0, 0) and c.get(nomes[1]) == (1, 1)
                and c.get(nomes[2]) == (14, 2), f"{rotulo}: resultado por criterio {c}")
        if limite_fusao == 0:
            confere([n.get("valor") for n in r.indicadores.get("niveis", [])] == [0, 1, 14]
                    and all(n.get("provado") for n in r.indicadores["niveis"]),
                    f"niveis {r.indicadores.get('niveis')}")
    print("opB-b. definicao a parte: cada nivel sozinho, com os anteriores presos")
    inst = fe.montar(_pequeno(prioridades=p))
    pn = pr.normalizar(p)
    unidade, custo = pr.aplicar(inst, pn, {x.id: 1 for x in pr.CRITERIOS}, br.HABILIDADE_ENF)
    m = ea.modelo_br(unidade, custo)
    valores = []
    for i, familias in enumerate((["day_off_requests"], ["custo_atribuicao"],
                                  ["min_num_assignments"])):
        expr = sum(m.parcela[f] for f in familias)
        m.del_component(m.objetivo)
        m.objetivo = pyo.Objective(expr=expr, sense=pyo.minimize)
        res = modelo.resolver(m, tempo_limite=600, carregar=False)
        confere(modelo.provou_otimo(res) and modelo.carregar_solucao(m, res),
                f"definicao, nivel {i + 1}: {modelo.estado(res)}")
        valores.append(round(pyo.value(expr)))
        m.add_component(f"preso_{i}", pyo.Constraint(expr=expr <= valores[-1]))
    confere(valores == [0, 1, 14], f"definicao: {valores}")
    print("opB-b. classificacao invertida (enfermeiro Essencial, pedidos Importante)")
    inv = dict(p, pedido_folga=(fe.IMPORTANTE, None), enf_posto_tec=(fe.ESSENCIAL, None))
    r = fe.verificar(_pequeno(prioridades=inv))
    c = _por_criterio(r)
    confere([c.get(n, (None,))[0] for n in (nomes[1], nomes[0], nomes[2])] == [0, 1, 14],
            f"invertida: {c}")


def caso_opb_fusao() -> None:
    """(c) o plano: padrao fundido; suaves no Desejavel em sequencia (2 blocos)."""
    sys.path.insert(0, str(RAIZ / "docs" / "demonstracao"))
    import caso_clinica_medica as cc
    print("opB-c. plano da demonstracao, classificacao padrao")
    inst = fe.montar(cc.entrada())
    blocos = pr.planejar(inst, pr.normalizar(None), br.HABILIDADE_ENF)
    confere(len(blocos) == 1 and blocos[0].coef == {"pedido_folga": 286, "enf_posto_tec": 1}
            and blocos[0].maximo == 2001,
            f"padrao: {[(b.niveis, b.coef, b.maximo) for b in blocos]}")
    print("opB-c. plano com as suaves no Desejavel")
    p = _todas_suaves(fe.DESEJAVEL)
    blocos = pr.planejar(inst, pr.normalizar(p), br.HABILIDADE_ENF)
    confere(len(blocos) == 2 and blocos[0].coef == {"pedido_folga": 286, "enf_posto_tec": 1}
            and set(blocos[1].coef.values()) == {1} and len(blocos[1].coef) == 11,
            f"suaves no Desejavel: {[(b.niveis, b.coef, b.maximo) for b in blocos]}")
    print("opB-c. rodada da demonstracao com as suaves no Desejavel (600/180/20 min)")
    e = cc.entrada()
    e.prioridades = p
    r = fe.verificar(e)
    confere(r.indicadores.get("caminho") == "em sequência, 2 blocos",
            f"caminho {r.indicadores.get('caminho')}; tentativas {r.tentativas}")
    confere(bool(r.escala) and r.conformidade and r.conformidade["ok"],
            f"escala entregue e cumpre o descanso: {r.frase()}")
    print("   ", r.frase(), r.indicadores.get("niveis"), r.criterios)


def caso_opb_situacao() -> None:
    """(d) uma situacao por mensagem, e a rodada pequena do mesmo turno no fim de semana."""
    print("opB-d. situacao antes de resolver")
    p = dict(fe.prioridades_padrao(), min_dias_seguidos=(fe.NAO, 2), min_turnos=(fe.NAO, 20))
    s = fe.situacoes(_pequeno(prioridades=p))
    confere(s["min_dias_seguidos"] == pr.CLT_PREVALECE and s["min_turnos"] == pr.CLT_PREVALECE,
            f"12x36, minimo de dias seguidos 2 e minimo de turnos 20: {s}")
    s = fe.situacoes(_pequeno(prioridades=dict(p, min_turnos=(fe.NAO, 10))))
    confere(s["min_turnos"] == pr.OK, f"minimo de turnos 10: {s['min_turnos']}")
    confere(s["fds_completo"] == pr.NUNCA and s["mesmo_turno_fds"] == pr.NUNCA,
            f"12x36, fins de semana: {s['fds_completo']} / {s['mesmo_turno_fds']}")
    confere(all(s[k] == pr.GARANTIDO for k in ("max_dias_seguidos", "max_turnos",
                                                "seq_indesejadas")), "ja garantido pela CLT")
    s8 = fe.situacoes(_entrada(M8_TURNOS, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)}))
    confere(s8["fds_completo"] == pr.OK and s8["mesmo_turno_fds"] == pr.OK
            and s8["min_dias_seguidos"] == pr.OK
            and all(s8[k] == pr.GARANTIDO for k in ("max_dias_seguidos", "max_turnos",
                                                     "seq_indesejadas")),
            f"8 h em tres turnos: {s8}")
    print("opB-d. rodada pequena: mesmo turno e fim de semana completo no Essencial (12x36)")
    p = dict(fe.prioridades_padrao(), fds_completo=(fe.ESSENCIAL, None),
             mesmo_turno_fds=(fe.ESSENCIAL, None))
    r = fe.verificar(_pequeno(pedidos=False, prioridades=p))
    c = _por_criterio(r)
    confere(r.veredito == fe.ADMITE and bool(r.escala), f"veredito {r.veredito}")
    confere(c.get("Mesmo turno no fim de semana", (None,))[0] == 8
            and c.get("Fim de semana completo", (None,))[0] == 8, f"violacoes {c}")


def caso_opb_essencial() -> None:
    """(e) todas as suaves no Essencial nao tornam impossivel a escala que a CLT admite."""
    casos = (("caso pequeno (12x36, 1 + 2)", lambda pp: _pequeno(prioridades=pp)),
             ("caso 5 (8 h, 8 + 5)", lambda pp: _entrada(
                 M8_TURNOS, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)}, prioridades=pp)))
    for rotulo, faz in casos:
        print(f"opB-e. {rotulo}: padrao x todas as suaves no Essencial")
        a = fe.verificar(faz(None))
        b = fe.verificar(faz(_todas_suaves(fe.ESSENCIAL)))
        confere(a.veredito == b.veredito == fe.ADMITE and a.menor_viavel == b.menor_viavel,
                f"{rotulo}: {a.veredito}/{a.menor_viavel} x {b.veredito}/{b.menor_viavel}")
        confere(bool(b.escala) and b.conformidade["ok"], f"{rotulo}: escala cumpre")
        print("   ", b.indicadores.get("caminho"), b.criterios)


def caso_opb_padroes() -> None:
    """Os padroes novos: 1800 s, 1800 s, 60 min; o campo da tela abre em 60."""
    print("opB-padroes. limites e orcamento padrao")
    confere(PADROES_NOVOS == (1800, 1800, 3600), f"padroes {PADROES_NOVOS}")
    guardado = fe.ORCAMENTO
    fe.ORCAMENTO = PADROES_NOVOS[2]
    try:
        at = AppTest.from_file(str(RAIZ / "src" / "app.py"), default_timeout=300)
        at.run()
        confere(at.number_input(key="orcamento").value == 60,
                f"campo de orcamento: {at.number_input(key='orcamento').value}")
    finally:
        fe.ORCAMENTO = guardado


def caso_opb_tela() -> None:
    """A tabela "Prioridades da escala" pela tela, e o "Resultado por criterio"."""
    print("opB-tela. tabela, padrao, restaurar, aviso, orcamento")
    at = AppTest.from_file(str(RAIZ / "src" / "app.py"), default_timeout=1800)
    at.run()
    grupos = [x for x in at.expander if any(x.label.startswith(g) for g in pr.GRUPOS)]
    confere([x.label for x in grupos] == [
        "Pedidos e qualificação — 1 de 1 considerados",
        "Sequências de trabalho e folga — 0 de 2 considerados",
        "Fins de semana — 0 de 3 considerados", "Noturno e carga — 0 de 3 considerados"],
        f"grupos {[x.label for x in grupos]}")
    confere(grupos and grupos[0].proto.expanded and not any(x.proto.expanded
                                                            for x in grupos[1:]),
            "grupo 1 aberto, 2 a 4 recolhidos")
    # 3o bloco (20/10): o pedido de folga no dia saiu das Prioridades (a importancia e da linha
    # da tabela "Pedidos e regras dos profissionais", que fica no grupo 1)
    # 3o bloco, Parte 5 (20/10): no 12x36 ficam ocultos o minimo de dias seguidos, o fim de
    # semana completo e o mesmo turno no fim de semana
    padrao = {k: v[0] for k, v in fe.prioridades_padrao().items()
              if k not in ("pedido_folga", "min_dias_seguidos", "fds_completo",
                           "mesmo_turno_fds")}
    confere("**Pedidos e regras dos profissionais**" in textos(at, "markdown"),
            "tabela de pedidos e regras no grupo 1")
    confere({k: at.selectbox(key=f"prio_{k}").value for k in padrao} == padrao,
            "importancia padrao")
    # 3o bloco, Parte 4 (20/10): o maximo de dias seguidos virou campo do hospital, oculto no
    # 12x36 (o modelo padrao da tela); ficam duas linhas cinza
    confere(sum(1 for x in textos(at, "markdown") if pr.GARANTIDO in x) == 0,
            "nenhuma linha 'ja garantido pela CLT' (Parte 5: regras da CLT no back end)")
    confere(not any(x.key == "max_dias" for x in at.number_input),
            "maximo de dias seguidos do hospital oculto no 12x36")
    at.selectbox(key="prio_min_folgas_seguidas").set_value(fe.DESEJAVEL)
    at.run()
    confere(any(x.label == "Sequências de trabalho e folga — 1 de 2 considerados"
                for x in at.expander), "contador muda")
    at.button(key="restaurar").click()
    at.run()
    confere(at.selectbox(key="prio_min_folgas_seguidas").value == fe.NAO, "restaurar padrao")
    confere(not any("estão no nível" in x for x in textos(at, "info")), "sem aviso no padrao")
    at.selectbox(key="prio_min_folgas_seguidas").set_value(fe.IMPORTANTE)
    at.run()
    confere(any("Todos os critérios considerados estão no nível Importante" in x
                for x in textos(at, "info")), f"aviso de mesmo nivel: {textos(at, 'info')}")
    at.button(key="restaurar").click()
    at.run()
    capturado = {}
    original = fe.verificar

    def espiao(e, **kw):
        capturado.update(kw, prioridades=e.prioridades)
        return original(e, **kw)

    fe.verificar = espiao
    try:
        caso5 = (M8, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)})
        at = pela_tela(*caso5)
        confere(capturado.get("orcamento") is None and capturado.get("prioridades") is None,
                f"padrao: orcamento {capturado.get('orcamento')}, prioridades "
                f"{capturado.get('prioridades')}")
        r, e = at.session_state["resultado"]
        confere("**Resultado por critério**" in textos(at, "markdown"),
                "tabela de resultado na tela")
        df = [d.value for d in at.dataframe if list(d.value.columns)[:2] == ["Nível", "Critério"]]
        confere(len(df) == 1 and df[0].values.tolist() == [list(x) for x in r.criterios]
                and len(r.criterios) == 2, f"resultado por criterio: {r.criterios}")
        aba = openpyxl.load_workbook(io.BytesIO(fe.planilha(r, e)))["Prioridades"]
        linhas = [list(x) for x in aba.iter_rows(min_row=2, values_only=True)]
        confere(linhas == [list(x) for x in r.criterios], f"aba Prioridades: {linhas}")
        print("opB-tela. orcamento editado chega ao verificar")
        capturado.clear()
        at.number_input(key="orcamento").set_value(2)
        at.run()
        at.button(key="gerar").click()
        at.run()
        confere(capturado.get("orcamento") == 120, f"orcamento {capturado.get('orcamento')}")
    finally:
        fe.verificar = original


# --- Pedidos e regras dos profissionais (3o bloco, 20/10) -------------------------------------
# Esperado registrado antes de implementar: resultados/pedidos_2026-10-20/ESPERADO.md.

T8 = [("M", 7, 8, "M"), ("T", 15, 8, "T"), ("N", 23, 8, "N")]


def _sete_dias(demanda, n_tec, nomes=None, demanda_data=None):
    """Modelo 8 h, 7 dias a partir da primeira segunda, so tecnicos."""
    return br.construir(turnos=T8, demanda_turno=demanda, demanda_data=demanda_data,
                        n_enfermeiros=0, n_tecnicos=n_tec, nomes_tecnicos=nomes, dias=7,
                        inicio=br.primeira_segunda())


def _resolver_regras(inst, regras, tempo=120):
    inst = fe.com_regras(inst, regras)
    v, inst_p, escala, info = fe.resolver_com_objetivo(inst, tempo)
    por_nivel = {}
    if escala:
        for nivel, nome, viol, _ in pr.resultado(inst_p, escala, pr.normalizar(None),
                                                 br.HABILIDADE_ENF):
            if nome == pr.NOME_REGRAS:
                por_nivel[nivel] = viol
    return v, inst_p, escala, info, por_nivel


def caso_ped_contas() -> None:
    """2. turno fixo e "Folga + turno": compativel = 0; forcado = exatamente 4 (conta a mao)."""
    L = pr.Linha
    equipes = [L(n, None, t, pr.SO_TURNO) for n, t in zip("ABCDEF", "MMTTNN")]
    sem_noite = [L(n, None, "N", pr.FOLGA) for n in "ABCD"]
    for rotulo, demanda, regras, k in (
            ("2a. turno fixo compativel", (1, 1, 1), equipes, 0),
            ("2b. turno fixo, manha 2", (2, 1, 1), equipes, 4),
            ("2c. folga no noturno compativel", (1, 1, 1), sem_noite, 0),
            ("2d. folga no noturno, noite 2", (1, 1, 2), sem_noite, 4)):
        print(rotulo)
        inst = _sete_dias({s: (0, q) for s, q in zip("MTN", demanda)}, 6, list("ABCDEF"))
        v, _, escala, info, por_nivel = _resolver_regras(inst, regras)
        confere(v == "viavel" and info["provado"], f"viavel e provado: {v}, {info['provado']}")
        confere(por_nivel == {pr.DESEJAVEL: k}, f"violacoes {por_nivel}, esperado {k}")


def caso_ped_niveis() -> None:
    """3. niveis por linha: conflito na mesma pessoa; tres linhas na mesma celula."""
    L = pr.Linha
    d1 = br.primeira_segunda()
    zero = {"M": (0, 0), "T": (0, 0), "N": (0, 0)}
    casos = [("3a. L1 Essencial, L2 Desejavel", fe.ESSENCIAL, fe.DESEJAVEL, "T", None),
             ("3a. invertida", fe.DESEJAVEL, fe.ESSENCIAL, "M", None),
             ("3a. em sequencia forcada (fusao zerada)", fe.ESSENCIAL, fe.DESEJAVEL, "T", 0),
             ("3a. invertida, em sequencia forcada", fe.DESEJAVEL, fe.ESSENCIAL, "M", 0)]
    original = pr.LIMITE_FUSAO
    for rotulo, n1, n2, turno, fusao in casos:
        print(rotulo)
        pr.LIMITE_FUSAO = original if fusao is None else fusao
        inst = _sete_dias(zero, 2, demanda_data={(d1, "M", "tec"): 1, (d1, "T", "tec"): 1})
        regras = [L("Téc 1", d1, "M", pr.FOLGA, n1), L("Téc 1", d1, "M", pr.SO_TURNO, n2)]
        v, inst_p, escala, info, por_nivel = _resolver_regras(inst, regras)
        tec1 = [s for d, n, s in escala
                if inst_p.profissionais[n].nome == "Téc 1" and d == d1]
        confere(info["provado"] and por_nivel.get(fe.ESSENCIAL, 0) == 0
                and por_nivel.get(fe.DESEJAVEL, 0) == 1,
                f"Essencial 0, Desejavel 1: {por_nivel}")
        confere(tec1 == [turno], f"Tec 1 no d1: {tec1}, esperado {turno}")
        if fusao == 0:
            confere(info["caminho"].startswith("em sequência"), f"caminho {info['caminho']}")
    pr.LIMITE_FUSAO = original
    print("3b. tres linhas na mesma celula: uma violacao, no Essencial")
    inst = _sete_dias(zero, 1, demanda_data={(d1, "M", "tec"): 1})
    regras = [L("Téc 1", d1, None, pr.FOLGA, fe.DESEJAVEL),
              L("Téc 1", d1, "M", pr.FOLGA, fe.ESSENCIAL),
              L("Téc 1", None, "M", pr.FOLGA, fe.DESEJAVEL)]
    v, inst_p, escala, info, por_nivel = _resolver_regras(inst, regras)
    confere(v == "viavel" and por_nivel.get(fe.ESSENCIAL) == 1
            and por_nivel.get(fe.DESEJAVEL, 0) == 0,
            f"uma violacao no Essencial: {por_nivel}")
    confere(sum(1 for _ in pr.descumpridos(inst_p, escala)) == 1, "uma so descumprida")


def caso_ped_nunca_trava() -> None:
    """6. pedidos nunca tornam impossivel uma escala que a CLT admite."""
    L = pr.Linha
    print("6a. caso 2a com folga Essencial em todos os turnos para todos")
    inst = _sete_dias({"M": (0, 1), "T": (0, 1), "N": (0, 1)}, 6, list("ABCDEF"))
    regras = [L(n, None, t, pr.FOLGA, fe.ESSENCIAL) for n in "ABCDEF" for t in "MTN"]
    v, _, escala, info, por_nivel = _resolver_regras(inst, regras)
    confere(v == "viavel" and por_nivel == {fe.ESSENCIAL: 21},
            f"viavel com 21 no Essencial: {v}, {por_nivel}")
    print("6b. 12x36 1 + 2 pelo verificar, folga Essencial em todos os turnos para os 3")
    import dataclasses
    e = _pequeno(pedidos=False)
    e = dataclasses.replace(e, regras=[L(n, None, t, pr.FOLGA, fe.ESSENCIAL)
                                       for n in ("Enf 1", "Téc 1", "Téc 2") for t in "DN"])
    r = fe.verificar(e)
    confere(r.veredito == fe.ADMITE and r.menor_viavel == 3,
            f"admite 3: {r.veredito}, {r.menor_viavel}")
    confere(r.conformidade and r.conformidade["ok"], "escala cumpre o descanso")
    confere(any(x[0] == fe.ESSENCIAL for x in r.descumpridos),
            f"descumpridos informados: {r.descumpridos}")


def caso_max_dias() -> None:
    """Parte 4: maximo de dias seguidos do hospital (esperado em
    resultados/max_dias_2026-10-20/ESPERADO.md)."""
    import dataclasses
    import experimento_a as ea
    from datetime import timedelta
    base = fe.Entrada(turnos=[("M", 7, 13), ("T", 13, 19)], grau="intermediario",
                      n_enfermeiros=0, n_tecnicos=14,
                      demanda_turno={"M": (0, 6), "T": (0, 6)}, inicio=br.primeira_segunda())
    print("max-dias. 7 (acima da lei) e erro de entrada")
    try:
        fe.montar(dataclasses.replace(base, max_dias_seguidos=7))
        confere(False, "7 deveria ser recusado")
    except ValueError as x:
        confere("art. 67" in str(x), f"erro: {x}")
    for L, piso, frase in ((6, 14, ADMITE_OK),
                           (4, 15, "Falta 1; o menor quadro viável é 15. Escala gerada.")):
        print(f"max-dias. maximo {L}")
        e = dataclasses.replace(base, max_dias_seguidos=L)
        inst = fe.montar(e)
        confere(fe.limite_efetivo(inst) == L and fe.piso(inst) == piso,
                f"limite efetivo {fe.limite_efetivo(inst)}, piso {fe.piso(inst)}")
        r = fe.verificar(e)
        confere(r.frase() == frase, f"veredito: {r.frase()}")
        if not r.escala:
            continue
        dias = list(r.inst.dias)
        trab = {(n, d) for d, n, _ in r.escala}
        maior = 0
        for n in r.inst.profissionais:
            seq = 0
            for d in dias:
                seq = seq + 1 if (n, d) in trab else 0
                maior = max(maior, seq)
        confere(maior <= L and r.conformidade["max_consec"] <= L and r.conformidade["ok"],
                f"maior sequencia na escala {maior}, no relogio {r.conformidade['max_consec']}")
        if L == 4:
            confere(r.tentativas[0][:2] == (14, "piso"), f"14 pela conta: {r.tentativas}")
            confere(r.diagnostico is not None and r.diagnostico[0] == fe.COMBINACAO,
                    f"diagnostico: {r.diagnostico and r.diagnostico[0]}")


def caso_tela_limpa() -> None:
    """Parte 5: limpeza da tela (esperado em resultados/tela_2026-10-20/ESPERADO.md)."""
    at = AppTest.from_file(str(RAIZ / "src" / "app.py"), default_timeout=1800)
    at.run()
    print("tela-limpa. numeracao, rotulos, linhas fora")
    confere([h.value for h in at.header] == ["1. Configuração da unidade", "2. Equipe",
                                             "3. Demanda", "4. Prioridades da escala"],
            f"cabecalhos {[h.value for h in at.header]}")
    confere(any(x.label == "Conferir com o COFEN (opcional) — pacientes por grau"
                for x in at.expander), "COFEN sem o 4.")
    graus = at.selectbox(key="grau").options
    confere("Alta dependência (10 h; 36% enfermeiros)" in graus
            and "Semi-intensivo (10 h; 42% enfermeiros)" in graus, f"graus {graus}")
    confere([x.label for x in at.number_input if x.key == "pac_alta"]
            == ["Alta dependência (10 h; 36% enfermeiros)"], "grau no painel do COFEN")
    todos = _todos_textos(at) + [x.label for x in at.number_input]
    confere(not any("Situação" in t or pr.GARANTIDO in t or "(fds)" in t for t in todos),
            "sem Situacao, sem 'ja garantido', sem '(fds)'")
    confere([x.label for x in at.number_input if x.key and x.key.startswith("g_")]
            == ["Dia: enfermeiros", "Dia: técnicos", "Noite: enfermeiros", "Noite: técnicos"],
            "12x36: Dia e Noite")
    ocultos = ("prio_min_dias_seguidos", "prio_fds_completo", "prio_mesmo_turno_fds")
    chaves = {x.key for x in at.selectbox}
    confere(not any(k in chaves for k in ocultos), "12x36: tres criterios ocultos")
    at.checkbox(key="com_fds").check()
    at.selectbox(key="modelo").set_value(M8)
    at.run()
    confere([x.label for x in at.number_input if x.key and x.key.startswith("f_")][:2]
            == ["Manhã: enfermeiros (fim de semana)", "Manhã: técnicos (fim de semana)"],
            "8 h: Manha, Tarde, Noite; '(fim de semana)'")
    chaves = {x.key for x in at.selectbox}
    confere(all(k in chaves for k in ocultos), "8 h: os tres criterios visiveis")
    print("tela-limpa. caso 5 pela tela = o mesmo pelo back end")
    capturado = {}
    original = fe.verificar

    def espiao(e, **kw):
        capturado["e"] = e
        return original(e, **kw)

    fe.verificar = espiao
    try:
        at = pela_tela(M8, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)})
    finally:
        fe.verificar = original
    e = capturado["e"]
    confere(e.turnos == list(fe.MODELOS[M8]), f"codigos dos turnos: {e.turnos}")
    r, _ = at.session_state["resultado"]
    ref = fe.verificar(e)
    confere(textos(at, "success") == [ADMITE_OK], f"veredito {textos(at, 'success')}")
    confere((r.veredito, r.menor_viavel, r.indicadores["enf_em_posto_tec"],
             r.indicadores["pedidos_total"]) ==
            (ref.veredito, ref.menor_viavel, ref.indicadores["enf_em_posto_tec"],
             ref.indicadores["pedidos_total"]),
            f"tela {r.veredito} {r.indicadores['enf_em_posto_tec']} = back end "
            f"{ref.veredito} {ref.indicadores['enf_em_posto_tec']}")


CASOS = {"1-2": caso_experimento_a, "3": caso_6h_12h, "4": caso_poucos_enfermeiros,
         "5": caso_enfermeiro_em_posto_de_tecnico, "7.1": caso_objetivo, "7.2": caso_tempo_40,
         "7.3": casos_diagnostico, "8": casos_tempo, "9": casos_carga,
         "9b-sem-teto": caso_9b_sem_teto, "9c-tela": caso_9c_tela,
         "7.4": casos_diagnostico_p7, "4b": casos_grau_alerta, "12": casos_p12,
         "15": casos_p15, "16": caso_reprovada,
         "opB-b": caso_opb_sequencia, "opB-c": caso_opb_fusao, "opB-d": caso_opb_situacao,
         "opB-e": caso_opb_essencial, "opB-padroes": caso_opb_padroes,
         "opB-tela": caso_opb_tela,
         "ped-2": caso_ped_contas, "ped-3": caso_ped_niveis, "ped-6": caso_ped_nunca_trava,
         "max-dias": caso_max_dias, "tela-limpa": caso_tela_limpa}


def main() -> int:
    """Sem argumento, todos. Com argumentos, so os casos nomeados — para rodar um por vez
    quando falta memoria: `python src\\testes_ferramenta.py 7.2`."""
    for nome in sys.argv[1:] or CASOS:
        CASOS[nome]()
    print()
    if FALHAS:
        print(f"{len(FALHAS)} FALHA(S)")
        return 1
    print("ponta a ponta pela tela OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
