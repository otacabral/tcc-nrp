"""Diagnostico da P17 (10/10): a etapa 2 sem prova, partindo da escala da etapa 1, melhorou?

    python docs\\diagnostico\\p17_diagnostico_k5.py rodar      # K5, 600 s + 180 s (~13 min)
    python docs\\diagnostico\\p17_diagnostico_k5.py analisar   # so le o que foi gravado
    python docs\\diagnostico\\p17_diagnostico_k5.py rodar --teste --saida <pasta>
                                                  # 90 s + 20 s, so para ver o script rodar

Motivo: em 09/10 (`resultados/fechar_v12/p17_*.log`), nos tres casos dificeis (otavio, K5, K6),
os numeros da etapa 1 e os da escala final sairam identicos, e as escalas nao foram gravadas.

`rodar`: o K5 pelo caminho da tela (`ferramenta.verificar`, limites da tela: 600 s na etapa 1,
180 s na etapa 2), como no `fechar_v12.sh`. Nada de `src/` muda; o script so (1) recebe a escala
da etapa 1 pelo `aviso` que a tela usa e (2) pede ao HiGHS o log da etapa 2 (`log_file`, opcao
de saida, que nao muda a busca). Grava em `resultados/p17_diagnostico_2026-10-10/`:
`etapa1_escala.json`, `etapa2_escala.json`, `highs_etapa2.log` e `ferramenta.json` (o que a
ferramenta disse, para comparar).

`analisar`: NAO usa `ferramenta.indicadores`, `ferramenta.por_categoria` nem o modelo. Le as
duas escalas e reconta, com as duracoes tiradas dos horarios da `Entrada` e a categoria pelo
indice (os `n_enfermeiros` primeiros sao enfermeiros; conferido: so eles fazem turno de posto de
enfermeiro): horas e plantoes por pessoa, diferenca maxima entre colegas por categoria (horas e
plantoes), amplitude da fracao do contrato por categoria (pp) e o criterio da etapa 2 (soma das
amplitudes). Le o log do HiGHS: valor da partida aceita, solucoes melhoradas (tempo, valor),
limites primal e dual no fim.

ESPERADO, registrado e commitado ANTES de rodar (decisao do Otavio, 10/10):
- se o log mostrar solucao MELHOR que a partida (limite primal final < valor da partida), a
  escala final DIFERE da etapa 1 e o criterio recontado dela e o melhor valor do log;
- se o log NAO mostrar melhora, as duas escalas sao IDENTICAS celula a celula.
Qualquer outro desfecho e defeito. Conferencia a mais, sem premissa comum com a ferramenta: o
criterio recontado da escala da etapa 1 e o valor da partida que o HiGHS aceitou.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(AQUI))

CASO = "K5"
SAIDA_PADRAO = RAIZ / "resultados" / "p17_diagnostico_2026-10-10"
HORIZONTE = 28          # dias (especificacao de 29/09)
CARGA = 44.0            # horas por semana; o K5 nao edita cargas (conferido na Entrada)
TOL = 1e-6


def entrada():
    import bateria_propriedades as bp
    import bateria_rodar as brd
    return brd.entrada(next(c for c in bp.TODOS if c.nome.startswith(CASO)))


def rodar(saida: Path, teste: bool) -> None:
    import ferramenta as fe
    import modelo

    saida.mkdir(parents=True, exist_ok=True)
    log2 = saida / "highs_etapa2.log"
    if log2.exists():
        log2.unlink()
    original = modelo.resolver

    def com_log(m, *a, partida=False, **kw):
        if partida:                       # so a etapa 2 sem prova pede partida
            kw["log_arquivo"] = str(log2)
        return original(m, *a, partida=partida, **kw)

    modelo.resolver = com_log
    capturado = {}

    def aviso(evento, **dados):
        if evento == "escala_etapa1":
            capturado["escala"] = dados["escala"]

    kw = {}
    if teste:
        fe.TEMPO_ETAPA2 = 20
        kw["tempo"] = 90
    r = fe.verificar(entrada(), aviso=aviso,
                     progresso=lambda f, msg: print(f"  {msg}", flush=True), **kw)
    if "escala" not in capturado:
        raise SystemExit("a escala da etapa 1 nao chegou pelo aviso: nada a comparar")

    def gravar(nome, escala):
        (saida / nome).write_text(json.dumps([(str(d), n, s) for d, n, s in escala]),
                                  encoding="utf-8")

    gravar("etapa1_escala.json", capturado["escala"])
    gravar("etapa2_escala.json", r.escala)
    ind = r.indicadores
    (saida / "ferramenta.json").write_text(json.dumps({
        "frase": r.frase(), "vigente": r.frase_vigente(), "etapa2": ind.get("etapa2"),
        "tempo_etapa1": ind.get("tempo_etapa1"), "tempo_etapa2": ind.get("tempo_etapa2"),
        "provado": ind.get("provado"), "gap": ind.get("gap"), "penalidade": ind.get("penalidade"),
        "amplitude_etapa1": ind.get("amplitude_etapa1"), "amplitude": ind.get("amplitude"),
        "etapa1": ind.get("etapa1"), "categorias": ind.get("categorias"),
    }, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("gravado em", saida)


# --- analise: nada de ferramenta, nada de modelo ------------------------------------------

def _dur(ini: int, fim: int) -> int:
    return (fim - ini) % 24 or 24


def recontar(escala, e) -> dict:
    dur = {s: _dur(i, f) for s, i, f in e.turnos}
    n_total = e.n_enfermeiros + e.n_tecnicos
    enf = {str(i) for i in range(e.n_enfermeiros)}
    pessoas = [str(i) for i in range(n_total)]
    horas = Counter({p: 0.0 for p in pessoas})
    plantoes = Counter({p: 0 for p in pessoas})
    for _, n, s in escala:
        base = s if s in dur else s[:-1]
        if base not in dur:
            raise SystemExit(f"turno {s} sem horario na Entrada")
        if s != base and n not in enf:
            raise SystemExit(f"{n} nao e enfermeiro e fez {s}, posto de enfermeiro: a regra da "
                             f"categoria pelo indice nao vale")
        horas[n] += dur[base]
        plantoes[n] += 1
    devidas = CARGA * HORIZONTE / 7
    out = {}
    for g, membros in (("enfermeiros", sorted(enf, key=int)),
                       ("tecnicos", [p for p in pessoas if p not in enf])):
        h = [horas[p] for p in membros]
        q = [plantoes[p] for p in membros]
        out[g] = {"horas_min": min(h), "horas_max": max(h), "diferenca_h": max(h) - min(h),
                  "plantoes_min": min(q), "plantoes_max": max(q),
                  "diferenca_plantoes": max(q) - min(q),
                  "amplitude_pp": 100 * (max(h) - min(h)) / devidas}
    out["criterio"] = sum(out[g]["amplitude_pp"] for g in ("enfermeiros", "tecnicos")) / 100
    return out


def ler_log(caminho: Path) -> dict:
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    partida = re.search(r"MIP start solution is feasible, objective value is ([-\d.eE+]+)", texto)
    linhas, melhoras, ultima = [], [], None
    for linha in texto.splitlines():
        t = linha.split()
        if not t or not linha.rstrip().endswith("s") or "%" not in linha:
            continue
        src, resto = (t[0], t[1:]) if t[0].isalpha() else ("", t)
        if len(resto) != 12:
            continue
        try:
            sol = float(resto[5])
        except ValueError:
            continue
        linhas.append(linha)
        if ultima is None or sol < ultima - 1e-12:
            melhoras.append({"fonte": src, "tempo": resto[11], "valor": sol, "limite": resto[4]})
            ultima = sol

    def campo(nome):
        m = re.search(rf"^\s*{nome}\s+(.+?)\s*$", texto, re.M)
        return m.group(1) if m else None

    return {"partida": float(partida.group(1)) if partida else None,
            "rejeitada": "MIP start solution is infeasible" in texto or
                         "MIP start solution is not feasible" in texto,
            "melhoras_na_tabela": melhoras,
            "primal": campo("Primal bound"), "dual": campo("Dual bound"),
            "gap": campo("Gap"), "status": campo("Status"),
            "linhas_da_tabela": len(linhas)}


def _num(texto):
    try:
        x = float(texto.split()[0])
    except (AttributeError, IndexError, ValueError):
        return None
    return x if abs(x) != float("inf") else None


def analisar(saida: Path) -> int:
    e = entrada()
    if e.cargas or e.indisponibilidades:
        raise SystemExit("o K5 deveria ter 44 h para todos e nenhuma ferias: a conta de horas "
                         "devidas abaixo nao vale")
    le = lambda nome: [(date.fromisoformat(d), n, s)
                       for d, n, s in json.loads((saida / nome).read_text(encoding="utf-8"))]
    e1, e2 = le("etapa1_escala.json"), le("etapa2_escala.json")
    c1 = {(d, n): s for d, n, s in e1}
    c2 = {(d, n): s for d, n, s in e2}
    diferentes = sorted(k for k in set(c1) | set(c2) if c1.get(k) != c2.get(k))
    r1, r2 = recontar(e1, e), recontar(e2, e)
    lg = ler_log(saida / "highs_etapa2.log")
    fe_json = json.loads((saida / "ferramenta.json").read_text(encoding="utf-8"))

    print(f"K5: {e.n_enfermeiros} enf + {e.n_tecnicos} tec, turnos {e.turnos}, "
          f"{HORIZONTE} dias desde {e.inicio}, {len(e.pedidos)} pedidos")
    print(f"ferramenta: etapa2 = {fe_json['etapa2']!r}; provado = {fe_json['provado']}; "
          f"gap = {fe_json['gap']}; tempos {fe_json['tempo_etapa1']:.0f} s + "
          f"{fe_json['tempo_etapa2']:.0f} s")
    print(f"log do HiGHS: partida aceita = {lg['partida']} (rejeitada: {lg['rejeitada']}); "
          f"status {lg['status']}; primal {lg['primal']}; dual {lg['dual']}; gap {lg['gap']}")
    print("solucoes na tabela do log (cada vez que a melhor caiu):")
    for mm in lg["melhoras_na_tabela"]:
        print(f"   {mm['fonte'] or '-':2s} t = {mm['tempo']:>8s}  valor {mm['valor']:.10f}  "
              f"limite {mm['limite']}")
    print(f"celulas (pessoa, dia) diferentes entre etapa 1 e final: {len(diferentes)}")
    for k in diferentes[:20]:
        print(f"   {k[0]} prof {k[1]}: {c1.get(k, '-')} -> {c2.get(k, '-')}")
    print("\nrecontagem a partir das escalas (sem ferramenta.indicadores):")
    print("| | etapa 1 | final | ferramenta, etapa 1 | ferramenta, final |")
    print("|---|---|---|---|---|")
    f1 = (fe_json.get("etapa1") or {}).get("categorias", {})
    f2 = fe_json.get("categorias") or {}
    for g in ("enfermeiros", "tecnicos"):
        print(f"| {g}: diferenca (h) | {r1[g]['diferenca_h']:g} | {r2[g]['diferenca_h']:g} | "
              f"{f1.get(g, {}).get('diferenca_h')} | {f2.get(g, {}).get('diferenca_h')} |")
        print(f"| {g}: diferenca (plantoes) | {r1[g]['diferenca_plantoes']} | "
              f"{r2[g]['diferenca_plantoes']} | - | - |")
        print(f"| {g}: horas min-max | {r1[g]['horas_min']:g}-{r1[g]['horas_max']:g} | "
              f"{r2[g]['horas_min']:g}-{r2[g]['horas_max']:g} | - | - |")
        print(f"| {g}: amplitude da fracao (pp) | {r1[g]['amplitude_pp']:.4f} | "
              f"{r2[g]['amplitude_pp']:.4f} | - | - |")
    print(f"| criterio (soma das amplitudes) | {r1['criterio']:.10f} | {r2['criterio']:.10f} | "
          f"{fe_json.get('amplitude_etapa1')} | {fe_json.get('amplitude')} |")

    falhas = []
    if lg["partida"] is None:
        falhas.append("o log nao mostra a partida aceita")
    elif abs(lg["partida"] - r1["criterio"]) > TOL:
        falhas.append(f"criterio recontado da etapa 1 ({r1['criterio']:.10f}) != valor da "
                      f"partida no log ({lg['partida']})")
    primal = _num(lg["primal"])
    if primal is None:
        falhas.append("o log nao tem limite primal final")
    elif lg["partida"] is not None:
        melhorou = primal < lg["partida"] - TOL
        if melhorou:
            if not diferentes:
                falhas.append("o log mostra melhora, mas as escalas sao identicas")
            if abs(r2["criterio"] - primal) > TOL:
                falhas.append(f"criterio recontado da final ({r2['criterio']:.10f}) != melhor "
                              f"do log ({primal})")
        elif diferentes:
            falhas.append(f"o log nao mostra melhora, mas {len(diferentes)} celulas mudaram")
        print(f"\ndesfecho: {'MELHOROU' if melhorou else 'SEM MELHORA'} "
              f"(partida {lg['partida']}, primal final {primal})")
    for g in ("enfermeiros", "tecnicos"):
        for r, f, nome in ((r1, f1, "etapa 1"), (r2, f2, "final")):
            v = f.get(g, {}).get("diferenca_h")
            if v is not None and abs(v - r[g]["diferenca_h"]) > TOL:
                falhas.append(f"{g}, {nome}: recontagem {r[g]['diferenca_h']} h != ferramenta {v} h")
    print("ESPERADO OK" if not falhas else "DEFEITO OU DIVERGENCIA:\n  - " + "\n  - ".join(falhas))
    return 0 if not falhas else 1


if __name__ == "__main__":
    acao = sys.argv[1]
    saida = (Path(sys.argv[sys.argv.index("--saida") + 1]) if "--saida" in sys.argv
             else SAIDA_PADRAO)
    if acao == "rodar":
        rodar(saida, "--teste" in sys.argv)
        raise SystemExit(analisar(saida))
    raise SystemExit(analisar(saida))
