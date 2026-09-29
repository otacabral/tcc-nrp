"""Caso de ponta a ponta PELA TELA (Streamlit AppTest). Roda da raiz, com a .venv ativa:

    python src\\testes_ferramenta.py

O AppTest executa `src/app.py` como o navegador faria: preenche o formulario, clica no botao
e le o que aparece na tela. Caso: a configuracao do Experimento A — 5.920 h em 28 dias, grau
intermediario (35,24 pacientes em media), 12x36, razao 20/29.

- 40 profissionais (14 enfermeiros + 26 tecnicos, a composicao que o Experimento A usou):
  a tela diz "admite escala legal", o QP mostra 35,24 e 40,52, e a planilha abre;
- 39 profissionais (13 + 26): a tela diz que o menor quadro viavel e 40.

Confere tambem que a instancia montada pela tela tem a MESMA demanda da celula do
Experimento A — senao o 40 poderia coincidir por acaso.
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


def confere(condicao: bool, mensagem: str) -> None:
    print(f"   {'ok   ' if condicao else 'FALHA'} {mensagem}")
    if not condicao:
        FALHAS.append(mensagem)


def pela_tela(n_enf: int, n_tec: int) -> AppTest:
    at = AppTest.from_file(str(RAIZ / "src" / "app.py"), default_timeout=1800)
    at.run()
    at.number_input(key="pac_intermediario").set_value(
        br.PORTE_HORAS / br.DIAS_HORIZONTE / br.GRAUS["intermediario"].horas_paciente_24h)
    at.radio[0].set_value("12x36")
    at.number_input(key="n_enf").set_value(n_enf)
    at.number_input(key="n_tec").set_value(n_tec)
    at.text_input(key="razao").set_value("20/29")
    at.date_input(key="inicio").set_value(br.primeira_segunda())
    at.button[0].click()
    at.run()
    return at


def textos(at, tipo) -> list[str]:
    return [el.value for el in getattr(at, tipo)]


def main() -> int:
    print("40 profissionais (14 + 26), 12x36, razao 20/29, pela tela")
    at = pela_tela(14, 26)
    confere(not at.exception, f"sem excecao na tela {[e.value for e in at.exception]}")
    confere(any("admite escala legal" in t for t in textos(at, "success")),
            f"veredito: {textos(at, 'success') + textos(at, 'warning') + textos(at, 'error')}")
    metricas = {m.label: m.value for m in at.metric}
    confere(metricas.get("QP núcleo assistencial") == "35,24",
            f"QP núcleo = {metricas.get('QP núcleo assistencial')}")
    confere(metricas.get("QP completo (IST 15%)") == "40,52",
            f"QP completo = {metricas.get('QP completo (IST 15%)')}")
    r, e = at.session_state["resultado"]
    wb = openpyxl.load_workbook(io.BytesIO(fe.planilha(r, e)))
    confere(wb.sheetnames == ["Escala", "Resumo", "Legenda"],
            f"planilha abre, abas {wb.sheetnames}")
    aba = wb["Escala"]
    confere(aba.max_row == 1 + 40 and aba.max_column == 3 + 28,
            f"aba Escala: {aba.max_row - 1} profissionais x {aba.max_column - 3} dias")
    ref = br.construir(grau="intermediario", regime="12x36", regra="teto", efetivo=40,
                       variacao=1.0)
    confere(r.inst.demanda == ref.demanda,
            "demanda montada pela tela = demanda da celula 12x36 v1 do Experimento A")
    confere(r.conformidade["ok"], "conferencia de descanso da escala: cumpre")

    print("39 profissionais (13 + 26), mesma configuracao, pela tela")
    at = pela_tela(13, 26)
    confere(not at.exception, "sem excecao na tela")
    avisos = textos(at, "warning")
    confere(any("o menor quadro viável é 40" in t and "Faltam 1" in t for t in avisos),
            f"veredito: {avisos + textos(at, 'success') + textos(at, 'error')}")
    r, _ = at.session_state["resultado"]
    # 39 fica abaixo do piso de alternancia (40 na celula v1 do Experimento A): no 12x36
    # ninguem trabalha dois dias seguidos, entao o quadro cobre a SOMA de dois dias. E prova
    # aritmetica de inviabilidade, sem solver — a mesma que o Experimento A usa.
    confere(r.tentativas == [(39, "piso"), (40, "viavel")],
            f"39 inviavel pela aritmetica (piso de alternancia), 40 viavel: {r.tentativas}")

    print()
    if FALHAS:
        print(f"{len(FALHAS)} FALHA(S)")
        return 1
    print("ponta a ponta pela tela OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
