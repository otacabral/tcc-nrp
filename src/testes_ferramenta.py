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


def textos(at, tipo) -> list[str]:
    return [el.value for el in getattr(at, tipo)]


def metricas(at) -> dict:
    return {m.label: m.value for m in at.metric}


def caso_experimento_a() -> None:
    demanda, fds = {"D": (1, 9), "N": (1, 9)}, {"D": (1, 6), "N": (1, 6)}
    print("1. 12x36, demanda equivalente ao Experimento A (razao 20/29), 40 = 14 + 26")
    at = pela_tela(M12, 14, 26, demanda, fds)
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    confere(textos(at, "success") == ["O quadro informado admite escala legal."],
            f"veredito: {textos(at, 'success') + textos(at, 'warning')}")
    confere(textos(at, "error") == [], f"sem alerta: {textos(at, 'error')}")
    r, e = at.session_state["resultado"]
    ref = br.construir(grau="intermediario", regime="12x36", regra="teto", efetivo=40,
                       variacao=1.0)
    confere(r.inst.demanda == ref.demanda, "demanda montada pela tela = celula v1 do "
                                           "Experimento A")
    confere(r.tentativas == [(40, "viavel")], f"tentativas {r.tentativas}")
    wb = openpyxl.load_workbook(io.BytesIO(fe.planilha(r, e)))
    confere(wb.sheetnames == ["Escala", "Resumo", "Legenda"]
            and wb["Escala"].max_row == 41, f"planilha abre: {wb.sheetnames}")
    confere(r.conformidade["ok"], "conferencia de descanso: cumpre")

    print("2. mesma configuracao, 39 = 13 + 26")
    at = pela_tela(M12, 13, 26, demanda, fds)
    confere(not at.exception, "sem excecao na tela")
    confere(textos(at, "warning") == ["Faltam 1; o menor quadro viável é 40."],
            f"veredito: {textos(at, 'warning') + textos(at, 'success')}")
    r, _ = at.session_state["resultado"]
    confere(r.tentativas == [(39, "piso"), (40, "viavel")], f"tentativas {r.tentativas}")


def caso_6h_12h() -> None:
    print("3. modelo 6 h + 12 h, 7 + 12")
    at = pela_tela(M6, 7, 12, {"M": (1, 3), "T": (1, 3), "N": (1, 2)})
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    confere(textos(at, "success") == ["O quadro informado admite escala legal."],
            f"veredito: {textos(at, 'success') + textos(at, 'warning')}")
    confere(metricas(at).get("Conferência de descanso") == "cumpre",
            f"conferencia de descanso na tela: {metricas(at).get('Conferência de descanso')}")


def caso_poucos_enfermeiros() -> None:
    print("4. poucos enfermeiros: 8 h, 5 + 15")
    at = pela_tela(M8, 5, 15, {"M": (1, 3), "T": (1, 3), "N": (1, 2)})
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    confere(textos(at, "success") == ["O quadro informado admite escala legal."],
            f"ainda gera a escala: {textos(at, 'success') + textos(at, 'warning')}")
    alertas = textos(at, "error")
    confere(len(alertas) == 1 and alertas[0].startswith("Alerta COFEN (não impede a escala)")
            and "5 enfermeiros em 20" in alertas[0] and "isto e, 7" in alertas[0],
            f"alerta vermelho: {alertas}")


def caso_enfermeiro_em_posto_de_tecnico() -> None:
    print("5. enfermeiro em posto de tecnico: 8 h, 8 + 5")
    at = pela_tela(M8, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)})
    confere(not at.exception, f"sem excecao na tela {[x.value for x in at.exception]}")
    confere(textos(at, "success") == ["O quadro informado admite escala legal."],
            f"veredito: {textos(at, 'success') + textos(at, 'warning')}")
    n = int(metricas(at).get("Turnos de enfermeiro em posto de técnico", -1))
    confere(n >= 35, f"contagem na tela: {n} turnos de enfermeiro em posto de tecnico (>= 35)")


def main() -> int:
    caso_experimento_a()
    caso_6h_12h()
    caso_poucos_enfermeiros()
    caso_enfermeiro_em_posto_de_tecnico()
    print()
    if FALHAS:
        print(f"{len(FALHAS)} FALHA(S)")
        return 1
    print("ponta a ponta pela tela OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
