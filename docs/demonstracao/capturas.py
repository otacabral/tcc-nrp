"""Demonstracao de uso PELA TELA: preenche a tela da ferramenta num navegador (Playwright +
Chrome instalado), gera a escala e guarda capturas e a planilha em `docs/demonstracao/`.

Os dados vem de `caso_clinica_medica.py`; nada e digitado aqui que nao esteja la. Requer o
Streamlit no ar (`streamlit run src\\app.py --server.port 8599`) e `pip install playwright`
(ferramenta de desenvolvimento, fora do requirements.txt; usa o Chrome ja instalado).

    python docs\\demonstracao\\capturas.py rodada1
    python docs\\demonstracao\\capturas.py rodada2 --tec 20

As tabelas da tela (st.data_editor) sao preenchidas por COLAR: seleciona-se a celula com o
teclado e cola-se texto separado por tabulacao, como faria quem copia de uma planilha.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import caso_clinica_medica as caso  # noqa: E402

URL = "http://localhost:8599/"
LARGURA, ALTURA, ALTURA_FOTO = 1400, 1000, 5200
CABECALHO, LINHA = 35, 35


def esperar(pg, ms=1500):
    pg.wait_for_timeout(ms)
    pg.wait_for_function("() => !document.querySelector('[data-testid=\"stStatusWidget\"]')",
                         timeout=600000)


def numero(pg, rotulo, valor):
    campo = pg.locator(f"input[aria-label='{rotulo}']")
    campo.fill(str(valor))
    campo.press("Enter")
    esperar(pg)


def grade(pg, indice):
    g = pg.locator("[data-testid='stDataFrameResizable']").nth(indice)
    g.scroll_into_view_if_needed()
    pg.wait_for_timeout(300)
    return g


def colar(pg, indice_grade, linha, coluna_x, texto, setas_direita=0):
    """Clica na celula (linha, coluna em pixels a partir da borda), anda `setas_direita`
    colunas com o teclado e cola `texto` (TSV)."""
    caixa = grade(pg, indice_grade).bounding_box()
    pg.mouse.click(caixa["x"] + coluna_x, caixa["y"] + CABECALHO + linha * LINHA + LINHA / 2)
    for _ in range(setas_direita):
        pg.keyboard.press("ArrowRight")
    pg.evaluate("t => navigator.clipboard.writeText(t)", texto)
    pg.keyboard.press("Control+V")
    esperar(pg, 2500)


def opcoes(pg) -> list[str]:
    return pg.locator("#portal [role='option']").all_inner_texts()


def opcao(pg, valor: str):
    """Com a celula de lista em edicao, clica na opcao."""
    try:
        pg.get_by_role("option", name=valor, exact=True).click(timeout=10000)
    except Exception:
        pg.screenshot(path=str(AQUI / "erro_preenchimento.png"))
        raise
    esperar(pg, 1500)


def abrir_lista(pg, x, y, tentativas=4):
    """Clica na celula de lista e abre o editor (Enter). Depois de uma reexecucao da pagina
    o primeiro clique as vezes so devolve o foco a grade; por isso confere e repete."""
    for _ in range(tentativas):
        pg.mouse.click(x, y)
        pg.wait_for_timeout(900)
        if not opcoes(pg):
            pg.keyboard.press("Enter")
            pg.wait_for_timeout(700)
        if opcoes(pg):
            return
        pg.keyboard.press("Escape")
    pg.screenshot(path=str(AQUI / "erro_preenchimento.png"))
    raise RuntimeError(f"a lista nao abriu em ({x:.0f}, {y:.0f})")


def editar_data(pg, x, y, colunas_a_direita, d, tentativas=4):
    """Seleciona a celula da primeira coluna da linha (clique em x, y), anda
    `colunas_a_direita` com o teclado, abre o editor de data, digita e confirma. A pagina se
    reexecuta a cada edicao e a grade perde o foco; por isso o clique de novo a cada data."""
    for _ in range(tentativas):
        pg.mouse.click(x, y)
        pg.wait_for_timeout(900)
        for _ in range(colunas_a_direita):
            pg.keyboard.press("ArrowRight")
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(700)
        campo = pg.locator("#portal input")
        if campo.count():
            campo.first.fill(d.strftime("%Y-%m-%d"))
            campo.first.press("Enter")
            esperar(pg, 1500)
            return
        pg.keyboard.press("Escape")
    pg.screenshot(path=str(AQUI / "erro_preenchimento.png"))
    raise RuntimeError("o editor de data nao abriu")


def valor_celula(pg, indice_grade, coluna, linha) -> str | None:
    """Texto da celula na tabela de acessibilidade da grade (so as linhas desenhadas)."""
    c = grade(pg, indice_grade).locator(f"[data-testid='glide-cell-{coluna}-{linha}']")
    return c.first.text_content() if c.count() else None


def carga(pg, linha, valor, tentativas=4):
    """Carga semanal da pessoa na `linha` da tabela de cargas (grade 1, coluna 2). A cada
    tentativa: seleciona uma celula visivel da coluna, sobe ao topo pelo teclado, desce ate a
    linha, abre a lista e escolhe; confere lendo a celula."""
    for _ in range(tentativas):
        caixa = grade(pg, 1).bounding_box()
        abrir_lista(pg, caixa["x"] + caixa["width"] - 40, caixa["y"] + CABECALHO + LINHA / 2)
        pg.keyboard.press("Escape")
        for _ in range(60):
            pg.keyboard.press("ArrowUp")
        for _ in range(linha):
            pg.keyboard.press("ArrowDown")
        pg.keyboard.press("Enter")
        pg.wait_for_timeout(700)
        if opcoes(pg):
            opcao(pg, valor)
            if valor_celula(pg, 1, 2, linha) == valor:
                return
        else:
            pg.keyboard.press("Escape")
    pg.screenshot(path=str(AQUI / "erro_preenchimento.png"))
    raise RuntimeError(f"carga da linha {linha} nao ficou em {valor}")


def linhas_novas(pg, indice_grade, linhas):
    """Tabela vazia com linhas dinamicas: o clique na linha de acrescentar cria a linha e
    abre a lista da primeira coluna (profissional); as datas vem nas colunas seguintes. Se o
    clique so criou a linha (a grade cresceu) sem abrir a lista, abre-se a lista nela."""
    for i, (nome, *datas) in enumerate(linhas):
        caixa = grade(pg, indice_grade).bounding_box()
        y = caixa["y"] + CABECALHO + i * LINHA + LINHA / 2
        for _ in range(4):
            antes = grade(pg, indice_grade).bounding_box()["height"]
            pg.mouse.click(caixa["x"] + 60, y)
            pg.wait_for_timeout(1200)
            if opcoes(pg):
                break
            if grade(pg, indice_grade).bounding_box()["height"] > antes:
                abrir_lista(pg, caixa["x"] + 60, y)
                break
        opcao(pg, nome)
        for k, d in enumerate(datas, start=1):
            editar_data(pg, caixa["x"] + 60, y, k, d)


def preencher(pg, n_tec: int | None):
    e = caso.entrada(n_tec)
    tecnicos = e.nomes_tecnicos
    pg.goto(URL)
    pg.wait_for_selector("text=Gerar escala", timeout=120000)

    # 1. unidade: modelo 12x36 e grau intermediario ja sao o padrao; inicio
    # o campo de data e segmentado (dia / mes / ano): digita-se cada parte
    pg.locator("[data-testid='stDateInput'] [role='spinbutton'][data-type='day']").click()
    pg.keyboard.type(caso.INICIO.strftime("%d%m%Y"), delay=80)
    pg.keyboard.press("Tab")
    esperar(pg)

    # 2. equipe
    numero(pg, "Enfermeiros", len(caso.ENFERMEIROS))
    numero(pg, "Técnicos e auxiliares", len(tecnicos))
    pg.get_by_text("Nomes (opcional)").click()
    esperar(pg, 800)
    for rotulo, nomes in (("Enfermeiros, um por linha", caso.ENFERMEIROS),
                          ("Técnicos, um por linha", tecnicos)):
        area = pg.locator(f"textarea[aria-label='{rotulo}']")
        area.fill("\n".join(nomes))
        area.press("Control+Enter")
        esperar(pg)

    # grades, na ordem da pagina: 0 turnos, 1 cargas, 2 ferias, 3 pedidos, 4 demanda por data
    pessoas = caso.ENFERMEIROS + tecnicos
    pg.get_by_text("2. Equipe").click()           # tira o foco da caixa de nomes
    esperar(pg, 2500)
    for k, n in enumerate(pessoas):
        if n in e.cargas:
            carga(pg, k, str(int(e.cargas[n])))
    linhas_novas(pg, 2, e.indisponibilidades)
    linhas_novas(pg, 3, e.pedidos)

    # 3. demanda
    pg.get_by_text("Fim de semana com demanda própria").click()
    esperar(pg)
    for turno, (enf, tec) in caso.DEMANDA.items():
        numero(pg, f"{turno}: enfermeiros", enf)
        numero(pg, f"{turno}: técnicos", tec)
    for turno, (enf, tec) in caso.DEMANDA_FDS.items():
        numero(pg, f"{turno}: enfermeiros (fds)", enf)
        numero(pg, f"{turno}: técnicos (fds)", tec)
    pg.get_by_text("Demanda específica por data").click()
    esperar(pg, 1500)
    for d in caso.FERIADOS:
        k = (d - caso.INICIO).days
        valores = "\t".join(str(caso.DEMANDA_FERIADO[t][i]) for t in ("D", "N")
                            for i in (0, 1))
        colar(pg, 4, 0, 20, "", 0)                 # foca a grade na primeira linha
        for _ in range(k):
            pg.keyboard.press("ArrowDown")
        pg.keyboard.press("ArrowRight")
        pg.evaluate("t => navigator.clipboard.writeText(t)", valores)
        pg.keyboard.press("Control+V")
        esperar(pg, 2500)

    # 4. COFEN
    pg.get_by_text("4. Conferir com o COFEN").click()
    esperar(pg, 800)
    rotulos = {"minimo": "Mínimo (4 h/paciente)", "intermediario": "Intermediário (6 h)",
               "alta": "Alta dependência (10 h)"}
    for g, v in caso.PACIENTES.items():
        numero(pg, rotulos[g], f"{v:.2f}")


def foto(pg, caminho):
    """Pagina inteira: o Streamlit rola dentro de um conteiner, entao aumenta-se a janela."""
    pg.set_viewport_size({"width": LARGURA, "height": ALTURA_FOTO})
    pg.wait_for_timeout(1500)
    pg.screenshot(path=str(caminho))
    pg.set_viewport_size({"width": LARGURA, "height": ALTURA})
    pg.wait_for_timeout(500)


def pico_mb(filtro: str) -> int:
    """Soma do pico de memoria (PeakWorkingSetSize) dos processos do Windows que casam com o
    filtro WQL, em MB. Lido antes de fechar o navegador."""
    import subprocess
    cmd = ("(Get-CimInstance Win32_Process -Filter \"" + filtro + "\" | "
           "Measure-Object PeakWorkingSetSize -Sum).Sum")
    saida = subprocess.run(["powershell", "-NoProfile", "-Command", cmd],
                           capture_output=True, text=True).stdout.strip()
    return round(float(saida or 0) / 1024)          # PeakWorkingSetSize vem em KB


def picos() -> str:
    import os
    servidor = pico_mb("Name='python.exe' AND CommandLine LIKE '%streamlit run%8599%'")
    chrome = pico_mb("Name='chrome.exe' AND CommandLine LIKE '%remote-debugging-pipe%'")
    roteiro = pico_mb(f"ProcessId={os.getpid()}")
    return (f"PICO DE MEMORIA (MB): servidor Streamlit + solver {servidor}; Chrome do "
            f"Playwright (soma dos processos) {chrome}; este roteiro {roteiro}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rodada", help="nome da rodada, prefixo dos arquivos (rodada1, ...)")
    ap.add_argument("--tec", type=int)
    ap.add_argument("--so-preencher", action="store_true",
                    help="preenche e fotografa a entrada, sem gerar (para conferir)")
    a = ap.parse_args()
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", args=["--disable-gpu", "--renderer-process-limit=1", "--disable-extensions"])
        ctx = b.new_context(viewport={"width": LARGURA, "height": ALTURA},
                            accept_downloads=True, locale="pt-BR")
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=URL)
        pg = ctx.new_page()
        preencher(pg, a.tec)
        foto(pg, AQUI / f"{a.rodada}_entrada.png")
        if a.so_preencher:
            b.close()
            return 0
        pg.get_by_role("button", name="Gerar escala").click()
        pg.wait_for_selector("text=5. Resultado", timeout=3600000)
        esperar(pg, 3000)
        foto(pg, AQUI / f"{a.rodada}_resultado.png")
        resultado = pg.locator("[data-testid='stHeading']", has_text="5. Resultado")
        resultado.scroll_into_view_if_needed()
        botao = pg.get_by_role("button", name="Baixar")
        if botao.count():
            with pg.expect_download() as dl:
                botao.first.click()
            dl.value.save_as(str(AQUI / f"{a.rodada}_escala.xlsx"))
        print(pg.locator("[data-testid='stMain']").inner_text())
        print(picos())
        b.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
