"""Parte C (09/10): o tempo-limite de 600 s da etapa 1 cobre a ultima melhora da escala?
So leitura: nenhum solver.

    python docs\\diagnostico\\analise_tempo_limite.py

1. Logs do HiGHS que existem (parte A do diagnostico, 07/10; K4 de 08/10): por log, tempo ate
   a primeira solucao, ate a ULTIMA melhora da melhor solucao (BestSol), ate a prova (ou "sem
   prova") e o gap final.
2. A bateria (07/10, propriedades de 08/10, nivel 3 de 09/10) nao gravou o log do HiGHS (rodou
   pelo caminho da tela). Dela sai so o que os JSON tem: provou ou nao, tempo e gap. Para os
   casos com prova, a ultima melhora acontece antes da prova, entao o tempo da prova e um
   limite superior dela; para os sem prova, a ultima melhora e desconhecida.
"""

from __future__ import annotations

import glob
import json
import re
import statistics
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
LINHA = re.compile(r"^\s*([A-Za-z])?\s+\d+\s+\d+\s+\d+\s+[\d.]+%\s+(\S+)\s+(\S+)\s+(\S+).*?\s([\d.]+)s\s*$")

LOGS = {
    "diagnostico_2026-10-07/A3a_15mais5_3600s.log": ("6+12", "K6 (15+5), etapa 1, 3.600 s"),
    "diagnostico_2026-10-07/A3b_22.log": ("6+12", "parte A, 22 pessoas, 600 s"),
    "diagnostico_2026-10-07/A3b_24.log": ("6+12", "parte A, 24 pessoas, 600 s"),
    "diagnostico_2026-10-07/A3b_26.log": ("6+12", "parte A, 26 pessoas, 600 s"),
    "diagnostico_2026-10-07/A3c_sem_6_dias.log": ("6+12", "parte A, relaxado: sem limite de 6 dias"),
    "diagnostico_2026-10-07/A3c_sem_descanso_entre_turnos.log": ("6+12", "parte A, relaxado: sem descanso entre turnos"),
    "diagnostico_2026-10-07/A3c_sem_max_atribuicoes.log": ("6+12", "parte A, relaxado: sem teto de atribuicoes"),
    "diagnostico_2026-10-07/A3c_sem_teto_horas.log": ("6+12", "parte A, relaxado: sem teto de horas"),
    "diagnostico_2026-10-07/inviavel_16_10mais6.log": ("6+12", "parte A, 16 (10+6), prova de inviabilidade"),
    "bateria_2026-10-08/parte2/highs_17.log": ("6+12", "K4 (12+5), 3.600 s, interrompido por memoria"),
}


def num(x: str) -> float | None:
    try:
        return float(x)
    except ValueError:
        return None


def ler_log(arq: Path) -> dict:
    primeira = ultima = None
    melhor = None
    for linha in arq.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINHA.match(linha)
        if not m:
            continue
        sol, t = num(m.group(3)), float(m.group(5))
        if sol is None or sol == float("inf"):
            continue
        if primeira is None:
            primeira = t
        if melhor is None or sol < melhor - 1e-9:
            melhor, ultima = sol, t
    texto = arq.read_text(encoding="utf-8", errors="replace")
    status = re.search(r"Status\s+(.+)", texto)
    gap = re.search(r"\n\s+Gap\s+(\S+)", texto)
    timing = re.search(r"Timing\s+([\d.]+)", texto)
    tempos = [float(x) for x in re.findall(r"\s([\d.]+)s\s*$", texto, re.M)]
    return {"primeira": primeira, "ultima": ultima, "melhor": melhor,
            "status": status.group(1).strip() if status else "sem relatorio (interrompido)",
            "gap": gap.group(1) if gap else "—",
            "fim": float(timing.group(1)) if timing else (max(tempos) if tempos else None)}


def bateria() -> list[dict]:
    """Um registro por resolucao da etapa 1 que se pode isolar: o caso admite o quadro
    informado na primeira tentativa (uma resolucao so). Tempo: `tempo_etapa1` quando existe
    (07/10); senao o tempo total do caso, que e o da etapa 1 (etapa 2 desligada)."""
    linhas = []
    fontes = [("bateria_2026-10-07", "07/10"), ("bateria_2026-10-08/parte3", "08/10 prop."),
              ("bateria_2026-10-08/parte4", "09/10 nivel 3")]
    estrato = {}
    for f in glob.glob(str(RAIZ / "docs/diagnostico/nivel3_casos_estratificado.json")):
        estrato = {d["nome"]: d["estrato"] for d in json.loads(Path(f).read_text(encoding="utf-8"))}
    for pasta, rotulo in fontes:
        for arq in sorted((RAIZ / "resultados" / pasta).glob("*.json")):
            o = json.loads(arq.read_text(encoding="utf-8"))
            t = o.get("tentativas") or []
            if o.get("veredito") != "admite" or len(t) != 1:
                continue
            modelo = o.get("modelo")
            if modelo is None:          # parte 3: o modelo vem do caso de origem
                import sys
                sys.path.insert(0, str(RAIZ / "docs" / "diagnostico"))
                import bateria_desenho as bd
                c = next(x for x in bd.CASOS + bd.CONHECIDOS if x.nome.split()[0] == o["caso"])
                modelo = c.modelo
            linhas.append({"fonte": rotulo, "caso": o["caso"] + ("/" + o["variante"] if "variante" in o else ""),
                           "modelo": modelo, "estrato": estrato.get(o["caso"], "—"),
                           "provado": bool(o.get("provado")),
                           "tempo": o.get("tempo_etapa1") or o.get("tempo_total"),
                           "gap": o.get("gap")})
    return linhas


def main() -> None:
    print("## 1. Logs do HiGHS que existem\n")
    print("| Log | Modelo | O que é | 1ª solução | Última melhora | Fim | Status | Gap final |")
    print("|---|---|---|---|---|---|---|---|")
    for rel, (modelo, oque) in LOGS.items():
        r = ler_log(RAIZ / "resultados" / rel)
        f = lambda x: "—" if x is None else f"{x:.0f} s"   # noqa: E731
        print(f"| `{Path(rel).name}` | {modelo} | {oque} | {f(r['primeira'])} | {f(r['ultima'])} "
              f"| {f(r['fim'])} | {r['status']} | {r['gap']} |")
    lin = bateria()
    print(f"\n## 2. Bateria: {len(lin)} resoluções isoláveis da etapa 1 (admite na 1ª tentativa)\n")
    print("| Modelo | Estrato | Resoluções | Com prova | Tempo até a prova: mediana / máximo | Sem prova (600 s) |")
    print("|---|---|---|---|---|---|")
    chaves = sorted({(x["modelo"], x["estrato"]) for x in lin})
    for m, e in chaves:
        g = [x for x in lin if (x["modelo"], x["estrato"]) == (m, e)]
        p = [x["tempo"] for x in g if x["provado"]]
        sp = [x for x in g if not x["provado"]]
        med = f"{statistics.median(p):.0f} / {max(p):.0f} s" if p else "—"
        print(f"| {m} | {e} | {len(g)} | {len(p)} | {med} | {len(sp)} "
              f"{'(' + ', '.join(x['caso'] for x in sp) + ')' if sp else ''} |")
    tot_p = sum(1 for x in lin if x["provado"])
    print(f"\nCom prova: {tot_p} de {len(lin)} ({100 * tot_p / len(lin):.0f}%).")


if __name__ == "__main__":
    main()
