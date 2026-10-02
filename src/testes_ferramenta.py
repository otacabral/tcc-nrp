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
    Pedidos entram por fora da tela (o AppTest nao edita a tabela): `fe.verificar` e
    embrulhado para acrescenta-los a entrada que a tela montou.
8c. Tempo esgotado sem escala: o 40 sem pedidos, limite de 3 s. Tela: error "Nao foi possivel
    gerar a escala no tempo disponivel."; nenhum "Faltam" em lugar nenhum; sem diagnostico,
    sem escala, sem botao de planilha.
8d. Quadro provado curto pela conta, e o seguinte sem escala no tempo: o 39, limite de 3 s.
    O 39 cai no piso (alternancia), o 40 esgota o tempo. Tela: o diagnostico de alternancia
    aparece (provado pela conta); a frase e "Nao foi possivel gerar a escala no tempo
    disponivel com mais profissionais; o menor quadro viavel nao foi determinado."; nenhum
    "Faltam 1".
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
import instancia_br as br  # noqa: E402

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
    confere(wb.sheetnames == ["Escala", "Resumo", "Legenda"]
            and wb["Escala"].max_row == 41, f"planilha abre: {wb.sheetnames}")
    confere(r.conformidade["ok"], "conferencia de descanso: cumpre")

    print("2. mesma configuracao, 39 = 13 + 26")
    at = pela_tela(M12, 13, 26, demanda, fds)
    confere(not at.exception, "sem excecao na tela")
    confere(textos(at, "warning") == ["Faltam 1; o menor quadro viável é 40. Escala gerada."],
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
            and "5 enfermeiros em 20" in alertas[0] and "isto e, 7" in alertas[0],
            f"alerta vermelho: {alertas}")


def caso_enfermeiro_em_posto_de_tecnico() -> None:
    print("5. enfermeiro em posto de tecnico: 8 h, 8 + 5")
    at = pela_tela(M8, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)})
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    confere(textos(at, "success") == [ADMITE_OK],
            f"veredito: {textos(at, 'success') + textos(at, 'warning')}")
    n = int(metricas(at).get("Turnos de enfermeiro em posto de técnico", -1))
    confere(n >= 35, f"contagem na tela: {n} turnos de enfermeiro em posto de tecnico (>= 35)")


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
            f"tecnico (minimo aritmetico 35)")
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
        confere(any(t.startswith("Equilíbrio de carga: não rodou") for t in textos(at, "caption")),
                "equilibrio nao rodou")
        print(f"      gap {r.indicadores['gap']:.2%} | pedidos "
              f"{r.indicadores['pedidos_atendidos']}/{r.indicadores['pedidos_total']}")

        print("8c. tempo esgotado sem escala: 40 sem pedidos, limite 3 s")
        fe.TEMPO = 3
        at = pela_tela(M12, 14, 26, demanda, fds)
        confere(textos(at, "error") == ["Não foi possível gerar a escala no tempo disponível."],
                f"tela: {textos(at, 'error')}")
        confere(not any("Faltam" in t for t in _todos_textos(at)), "nenhum 'Faltam'")
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
        esperado = ("Não foi possível gerar a escala no tempo disponível com mais "
                    "profissionais; o menor quadro viável não foi determinado.")
        confere(esperado in textos(at, "error"), f"tela: {textos(at, 'error')}")
        confere(not any("Faltam" in t for t in _todos_textos(at)), "nenhum 'Faltam'")
    finally:
        fe.TEMPO, fe.verificar = original_tempo, original_verificar


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
    ("combinacao: 12x36 so enfermeiro, 4, Enf 3 de licenca 09 e 10/01",
     lambda: _entrada(M12_TURNOS, 4, 0, {"D": (1, 0), "N": (1, 0)},
                      indisponibilidades=[("Enf 3", dia(5), dia(6))]),
     fe.COMBINACAO, 5, "solver provou"),
]


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


def main() -> int:
    caso_experimento_a()
    caso_6h_12h()
    caso_poucos_enfermeiros()
    caso_enfermeiro_em_posto_de_tecnico()
    caso_objetivo()
    caso_tempo_40()
    casos_diagnostico()
    casos_tempo()
    print()
    if FALHAS:
        print(f"{len(FALHAS)} FALHA(S)")
        return 1
    print("ponta a ponta pela tela OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
