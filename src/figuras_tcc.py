"""Tabelas e figuras do capitulo de resultados, a partir dos CSVs da P1. Roda da raiz:

    python src\\figuras_tcc.py

Le:
- `resultados/escalabilidade_objetivo.csv` — curva principal (caso mais apertado, demanda =
  168 h por pessoa), com o log `resultados/escalabilidade_objetivo/p1_*_ferramenta.log`;
- `resultados/escalabilidade_objetivo_folga.csv` — rodada complementar com folga (equipe +10%),
  com os logs `resultados/escalabilidade_objetivo/folga_*.log`.

Escreve em `resultados/figuras/`: as tabelas (.csv e .md), as figuras (.png) e
`legendas.md`, com uma legenda curta e a origem (arquivo e data) de cada uma.

**Nenhum numero e digitado aqui**: tudo sai dos CSVs; a maquina e o solver saem dos logs; a
data, da data de gravacao do CSV. As legendas descrevem o que esta na figura, sem
interpretar resultado (PROPOSTAS.md, P1, e CLAUDE.md: tempo e limite operacional).
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
RES = RAIZ / "resultados"
LOGS = RES / "escalabilidade_objetivo"
SAIDA = RES / "figuras"
CURVA = RES / "escalabilidade_objetivo.csv"
FOLGA = RES / "escalabilidade_objetivo_folga.csv"


def ler(caminho: Path) -> pd.DataFrame:
    return pd.read_csv(caminho, sep=";", encoding="utf-8-sig")


def data_de(caminho: Path) -> str:
    return datetime.fromtimestamp(caminho.stat().st_mtime).strftime("%d/%m/%Y")


def maquina(padrao: str) -> str:
    """Linha '### Maquina:' do log da rodada (o log do HiGHS nao traz a versao)."""
    logs = sorted(LOGS.glob(padrao))
    texto = logs[-1].read_text(encoding="utf-8", errors="replace") if logs else ""
    m = re.search(r"### Maquina: (.+)", texto)
    return m.group(1).strip() if m else "não registrada no log"


def origem(caminho: Path, padrao_log: str, df: pd.DataFrame) -> str:
    solver = ", ".join(sorted(set(df["solver"].astype(str))))
    return (f"Origem: {caminho.relative_to(RAIZ).as_posix()} (gravado em {data_de(caminho)}). "
            f"Máquina: {maquina(padrao_log)}. Solver: {solver} (highspy {version('highspy')} "
            f"instalado ao gerar esta figura).")


ESTADO = {"optimal": "ótimo", "maxTimeLimit": "limite de tempo",
          "nao rodou (etapa 1 sem prova)": "não rodou (etapa 1 sem prova)",
          "nao rodou (etapa 1 sem escala)": "não rodou (etapa 1 sem escala)"}


def estado(x) -> str:
    return "" if pd.isna(x) else ESTADO.get(str(x), str(x))


def gap(x) -> str:
    return "" if pd.isna(x) else str(x).replace(".", ",")


def pp(x) -> str:
    return "" if pd.isna(x) else f"{float(x) * 100:.2f}".replace(".", ",")


def num(x, casas=1) -> str:
    return "" if pd.isna(x) or x == "" else f"{float(x):.{casas}f}".replace(".", ",")


def sim_nao(x) -> str:
    return "" if pd.isna(x) else ("sim" if str(x) == "True" else "não")


def tabela_md(df: pd.DataFrame) -> str:
    linhas = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    linhas += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(linhas) + "\n"


def rodape(fig, texto: str) -> None:
    fig.text(0.01, 0.01, texto, fontsize=7, color="#555555", wrap=True)


def tabela_curva(c: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "N": c["N"],
        "Variáveis": c["variaveis"],
        "Restrições": c["restricoes"],
        "Etapa 1: estado": c["etapa1_estado"].map(estado),
        "Etapa 1: ótimo provado": c["etapa1_otimo"].map(sim_nao),
        "Etapa 1: gap": c["etapa1_gap"].map(gap),
        "Etapa 1: tempo (s)": c["etapa1_relogio_s"].map(num),
        "1ª escala legal (s)": c["etapa1_primeira_escala_s"].map(num),
        "Etapa 2: estado": c["etapa2_estado"].map(estado),
        "Etapa 2: tempo (s)": c.get("etapa2_relogio_s", pd.Series(dtype=float)).map(num),
        "Pedidos atendidos": [("" if pd.isna(a) else f"{int(a)} de {int(t)}")
                              for a, t in zip(c["pedidos_atendidos"], c["pedidos"])],
        "Enf. em posto de téc.": c["enf_em_posto_tec"].map(lambda x: "" if pd.isna(x)
                                                           else int(x)),
        "Descanso": c["descanso_ok"].map(lambda x: "" if pd.isna(x)
                                         else ("cumpre" if str(x) == "True" else "não cumpre")),
    })


def tabela_folga(f: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "Demanda (N)": f["N"],
        "Equipe": f["equipe"],
        "Etapa 1: ótimo provado": f["etapa1_otimo"].map(sim_nao),
        "Etapa 1: tempo (s)": f["etapa1_relogio_s"].map(num),
        "1ª escala legal (s)": f["etapa1_primeira_escala_s"].map(num),
        "Etapa 2: estado": f["etapa2_estado"].map(estado),
        "Etapa 2: gap": f["etapa2_gap"].map(gap),
        "Etapa 2: tempo (s)": f["etapa2_relogio_s"].map(num),
        "Etapa 2: 90% da redução (s)": f["etapa2_90pct_s"].map(num),
        "Amplitude enf. antes (pp)": f["amplitude_enfermeiros_etapa1"].map(pp),
        "Amplitude enf. depois (pp)": f["amplitude_enfermeiros_etapa2"].map(pp),
        "Amplitude téc. antes (pp)": f["amplitude_tecnicos_etapa1"].map(pp),
        "Amplitude téc. depois (pp)": f["amplitude_tecnicos_etapa2"].map(pp),
        "Descanso": f["descanso_ok"].map(lambda x: "cumpre" if str(x) == "True"
                                         else "não cumpre"),
    })


def figura_tempos_curva(c: pd.DataFrame, ori: str) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.2))
    x = list(range(len(c)))          # um tamanho por posicao: 36 e 40 nao se sobrepoem
    ax.plot(x, c["etapa1_relogio_s"], marker="o", label="Etapa 1: tempo de relógio")
    ax.plot(x, c["etapa1_primeira_escala_s"], marker="s", linestyle="--",
            label="Até a primeira escala legal (HiGHS)")
    limite = c["limite_s"].iloc[0]
    ax.axhline(limite, color="#999999", linewidth=1, linestyle=":",
               label=f"Limite por etapa ({int(limite)} s)")
    sem = [i for i, ok in enumerate(c["etapa1_otimo"].astype(str)) if ok != "True"]
    ax.scatter(sem, c["etapa1_relogio_s"].iloc[sem], s=90, facecolors="none",
               edgecolors="#c0392b", linewidths=1.5, label="Etapa 1 sem prova de otimalidade",
               zorder=3)
    ax.set_xlabel("Profissionais (N)")
    ax.set_ylabel("Segundos")
    ax.set_xticks(x)
    ax.set_xticklabels([str(int(n)) for n in c["N"]])
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.subplots_adjust(bottom=0.22)
    rodape(fig, ori)
    caminho = SAIDA / "fig_p1_tempos_etapa1.png"
    fig.savefig(caminho, dpi=200)
    plt.close(fig)
    return caminho


def figura_folga(f: pd.DataFrame, ori: str) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.2))
    rotulos = [f"{int(n)} / {int(e)}" for n, e in zip(f["N"], f["equipe"])]
    pos = range(len(f))
    largura = 0.2
    series = [("amplitude_enfermeiros_etapa1", "Enfermeiros, etapa 1", "#9ecae1"),
              ("amplitude_enfermeiros_etapa2", "Enfermeiros, etapa 2", "#3182bd"),
              ("amplitude_tecnicos_etapa1", "Técnicos, etapa 1", "#fdae6b"),
              ("amplitude_tecnicos_etapa2", "Técnicos, etapa 2", "#e6550d")]
    for k, (col, nome, cor) in enumerate(series):
        ax.bar([p + (k - 1.5) * largura for p in pos], f[col].astype(float) * 100, largura,
               label=nome, color=cor)
    ax.set_xticks(list(pos))
    ax.set_xticklabels(rotulos)
    ax.set_xlabel("Demanda (N) / equipe")
    ax.set_ylabel("Amplitude da fração do contrato (pp)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.subplots_adjust(bottom=0.22)
    rodape(fig, ori)
    caminho = SAIDA / "fig_folga_amplitude.png"
    fig.savefig(caminho, dpi=200)
    plt.close(fig)
    return caminho


def figura_folga_tempo(f: pd.DataFrame, ori: str) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.2))
    rotulos = [f"{int(n)} / {int(e)}" for n, e in zip(f["N"], f["equipe"])]
    pos = list(range(len(f)))
    ax.bar([p - 0.2 for p in pos], f["etapa2_90pct_s"].astype(float), 0.4,
           label="Etapa 2: 90% da redução final", color="#3182bd")
    ax.bar([p + 0.2 for p in pos], f["etapa2_relogio_s"].astype(float), 0.4,
           label="Etapa 2: tempo de relógio total", color="#bdbdbd")
    ax.set_xticks(pos)
    ax.set_xticklabels(rotulos)
    ax.set_xlabel("Demanda (N) / equipe")
    ax.set_ylabel("Segundos")
    ax.set_ylim(0, float(f["etapa2_relogio_s"].max()) * 1.3)   # espaco para a legenda
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    fig.subplots_adjust(bottom=0.22)
    rodape(fig, ori)
    caminho = SAIDA / "fig_folga_tempo_etapa2.png"
    fig.savefig(caminho, dpi=200)
    plt.close(fig)
    return caminho


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    c = ler(CURVA).sort_values("N")
    f = ler(FOLGA).sort_values("N")
    ori_c = origem(CURVA, "p1_*_ferramenta.log", c)
    ori_f = origem(FOLGA, "folga_*.log", f)

    legendas = ["# Tabelas e figuras do capítulo de resultados\n",
                "Geradas por `src/figuras_tcc.py`. Nenhum número digitado à mão. Tempo é "
                "limite operacional desta máquina, uma medição por tamanho.\n"]
    itens = []

    t1 = tabela_curva(c)
    t1.to_csv(SAIDA / "tab_p1_curva.csv", sep=";", index=False, encoding="utf-8-sig")
    (SAIDA / "tab_p1_curva.md").write_text(tabela_md(t1), encoding="utf-8")
    itens.append(("tab_p1_curva (.csv, .md)",
                  "Curva de escalabilidade com o objetivo da ferramenta, caso sem folga "
                  "(demanda igual à capacidade de N pessoas a 168 h): estado, prova e tempo "
                  "de cada etapa, por tamanho.", ori_c))

    t2 = tabela_folga(f)
    t2.to_csv(SAIDA / "tab_p1_folga.csv", sep=";", index=False, encoding="utf-8-sig")
    (SAIDA / "tab_p1_folga.md").write_text(tabela_md(t2), encoding="utf-8")
    itens.append(("tab_p1_folga (.csv, .md)",
                  "Rodada com folga (mesma demanda, equipe 10% maior): etapas 1 e 2 e "
                  "amplitude da fração do contrato por categoria, antes e depois da etapa 2.",
                  ori_f))

    figura_tempos_curva(c, ori_c)
    itens.append(("fig_p1_tempos_etapa1.png",
                  "Tempo de relógio da etapa 1 e tempo até a primeira escala legal, por "
                  "tamanho; marcados os tamanhos em que a etapa 1 terminou sem prova de "
                  "otimalidade.", ori_c))
    figura_folga(f, ori_f)
    itens.append(("fig_folga_amplitude.png",
                  "Amplitude da fração do contrato cumprida, por categoria, na escala da "
                  "etapa 1 e na da etapa 2, por tamanho da rodada com folga.", ori_f))
    figura_folga_tempo(f, ori_f)
    itens.append(("fig_folga_tempo_etapa2.png",
                  "Etapa 2 da rodada com folga: tempo até 90% da redução final da amplitude "
                  "e tempo de relógio total, por tamanho.", ori_f))

    for nome, texto, ori in itens:
        legendas.append(f"## {nome}\n\n{texto}\n\n*{ori}*\n")
    (SAIDA / "legendas.md").write_text("\n".join(legendas), encoding="utf-8")
    for nome, _, _ in itens:
        print(nome)
    print(f"em {SAIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
