"""Nivel 3 da bateria (`docs/bateria_entradas.md`): lote aleatorio de 100 casos pequenos,
ESTRATIFICADO pela conta, SO A ETAPA 1, 600 s por resolucao e no maximo 15 min por caso,
conferido pelas propriedades 1, 4, 5 e 6 da C3.

    python docs\\diagnostico\\bateria_nivel3.py --gerar        # sorteia e grava os casos (sem solver)
    python docs\\diagnostico\\bateria_nivel3.py --lote         # roda todos, pulando os ja feitos
    python docs\\diagnostico\\bateria_nivel3.py N001           # roda um caso, sem limite por caso
    python docs\\diagnostico\\bateria_nivel3.py --resumo       # confere tudo

**Sorteio estratificado (decisao do Otavio, 08/10):** 40 casos de folga clara (menor folga da
conta >= 2), 30 de fronteira (menor folga 0 ou 1) e 30 inviaveis pela conta (alguma folga
negativa). Sorteia candidatos nas faixas abaixo, com `SEMENTE`, calcula a conta de cada um e
fica com os primeiros que caem em cada estrato, ate completar. Grava
`docs/diagnostico/nivel3_casos_estratificado.json`, com o esperado da conta de cada caso,
commitado ANTES do primeiro solver.

**Sorteio de 07/10 DESCARTADO antes de rodar** (semente 81026,
`docs/diagnostico/nivel3_casos.json`, que fica no repositorio como registro): 78 dos 100
casos nasciam inviaveis pela conta, e a propriedade 5 (folga clara) so valeria em 17.
Nenhum caso dele foi resolvido.

Cada caso roda pelo caminho da tela (`bateria_rodar.entrada` -> `ferramenta.verificar`), com
a etapa 2 desligada como em `bateria_propriedades.py`: as propriedades conferidas aqui
(escala legal, honestidade, folga clara, coerencia com a conta) so dependem da etapa 1.
Em `--lote`, cada caso e um processo, com limite de 15 min (`LIMITE_CASO`); esgotado, o
processo e encerrado, o caso entra como "nao determinado (15 min)" e o lote segue.

Faixas (as do desenho, decididas em 07/10; o que o desenho nao fixa esta marcado *):

- modelo: 12x36, 8h, 6+12, horarios do modelo; fim de semana sab-dom ou sex-dom;
- inicio: uma segunda entre 05/10/2026 e 29/03/2027;
- 3 a 8 enfermeiros, 2 a 12 tecnicos; nomes com acento em metade dos casos*;
- carga 44 h com 70%; 30, 36 ou 40 h com 10% cada;
- 0 a 2 periodos de ferias de 1 a 10 dias, pessoas diferentes;
- 0 a 6 pedidos de folga (pessoa e dia sorteados*);
- demanda geral: 1 a 2 enfermeiros e 0 a 4 tecnicos por turno;
- fim de semana proprio em 30% dos casos, sorteado nas mesmas faixas*;
- 0 a 2 datas editadas na grade, cada uma num turno sorteado, nas mesmas faixas*;
- pacientes em 40% dos casos: 1 ou 2 graus, de 2 a 15 pacientes cada*;
- grau predominante sorteado entre os 5*.

Conferencias (C3):

1. toda escala: cobertura e um turno por dia, descanso no relogio, teto de horas, ferias
   (`bateria_rodar.conferir`);
4. honestidade: "faltam N" so com o quadro informado provado inviavel (piso ou solver);
   "provado" so com gap <= 1e-4; frase sem "pode haver uma melhor" so com prova;
5. folga clara (menor folga da conta >= 2) nao termina "nao decidido";
6. conta INVIAVEL -> a ferramenta nao admite o quadro informado.

Casos que esgotam o tempo sao listados a parte, com modelo e folga pela conta.
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bateria_desenho as bd  # noqa: E402
import bateria_propriedades as bp  # noqa: E402
import bateria_rodar as brd  # noqa: E402
import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402

SEMENTE = 20261008
SEMENTE_07_10 = 81026            # sorteio descartado antes de rodar (ver o cabecalho)
ESTRATOS = {"folga_clara": 40, "fronteira": 30, "inviavel": 30}
LIMITE_CASO = 15 * 60            # segundos por caso, no --lote
CASOS_JSON = Path(__file__).resolve().parent / "nivel3_casos_estratificado.json"
CASOS_JSON_07_10 = Path(__file__).resolve().parent / "nivel3_casos.json"
SAIDA = RAIZ / "resultados" / "bateria_2026-10-08" / "parte4"
GRAUS = ["minimo", "intermediario", "alta", "semi_intensivo", "intensivo"]
SEGUNDAS = [date(2026, 10, 5) + timedelta(weeks=k) for k in range(26)]   # ate 29/03/2027


def estrato(folgas: dict) -> str:
    menor = min(folgas.values())
    return "inviavel" if menor < 0 else "fronteira" if menor < 2 else "folga_clara"


def sortear_07_10() -> list[dict]:
    """O sorteio de 07/10, descartado antes de rodar. Mantido so para reproduzir o registro."""
    rng = random.Random(SEMENTE_07_10)
    return [sortear_um(rng, f"N{i + 1:03d}") for i in range(100)]


def sortear() -> tuple[list[dict], int]:
    """Estratificado: sorteia candidatos ate encher cada estrato. Devolve (casos, sorteados)."""
    rng = random.Random(SEMENTE)
    falta = dict(ESTRATOS)
    casos, sorteados = [], 0
    while any(falta.values()):
        sorteados += 1
        c = sortear_um(rng, "")
        esperado, folgas, _ = bd.conta(caso(c))
        e = estrato(folgas)
        if falta[e]:
            falta[e] -= 1
            c.update(nome=f"N{len(casos) + 1:03d}", estrato=e, esperado=esperado,
                     folgas=folgas)
            casos.append(c)
    return casos, sorteados


def sortear_um(rng: random.Random, nome: str) -> dict:
    modelo = rng.choice(list(bd.MODELOS))
    turnos = [s for s, _, _ in bd.MODELOS[modelo]]
    n_enf, n_tec = rng.randint(3, 8), rng.randint(2, 12)
    n = n_enf + n_tec
    cargas = {}
    for p in range(n):
        x = rng.random()
        if x >= 0.7:
            cargas[p] = 30 if x < 0.8 else 36 if x < 0.9 else 40
    ferias = []
    for p in rng.sample(range(n), rng.randint(0, 2)):
        ini = rng.randint(0, 27)
        ferias.append((p, ini, min(27, ini + rng.randint(1, 10) - 1)))
    faixa = lambda: (rng.randint(1, 2), rng.randint(0, 4))   # noqa: E731
    demanda = {s: faixa() for s in turnos}
    demanda_fds = {s: faixa() for s in turnos} if rng.random() < 0.3 else None
    grade = {}
    for _ in range(rng.randint(0, 2)):
        grade[(rng.randint(0, 27), rng.choice(turnos))] = faixa()
    pacientes = None
    if rng.random() < 0.4:
        pacientes = {g: rng.randint(2, 15) for g in rng.sample(GRAUS, rng.randint(1, 2))}
    return {
        "nome": nome, "modelo": modelo,
        "fds": rng.choice(["sab_dom", "sex_dom"]), "inicio": str(rng.choice(SEGUNDAS)),
        "n_enf": n_enf, "n_tec": n_tec, "nomes": rng.random() < 0.5,
        "cargas": cargas, "ferias": ferias, "pedidos": rng.randint(0, 6),
        "demanda": demanda, "demanda_fds": demanda_fds,
        "grade": [[k, s, list(v)] for (k, s), v in grade.items()],
        "pacientes": pacientes, "grau": rng.choice(GRAUS)}


def caso(d: dict) -> bd.Caso:
    """Do JSON para o `Caso` do gerador — a mesma estrutura do nivel 1, a mesma `conta`."""
    return bd.Caso(
        d["nome"], {"modelo"} | ({"nomes"} if d["nomes"] else set()), modelo=d["modelo"],
        fds=d["fds"], inicio=date.fromisoformat(d["inicio"]), n_enf=d["n_enf"],
        n_tec=d["n_tec"], cargas={int(k): v for k, v in d["cargas"].items()},
        ferias=[tuple(f) for f in d["ferias"]], pedidos=d["pedidos"],
        demanda={s: tuple(v) for s, v in d["demanda"].items()},
        demanda_fds=({s: tuple(v) for s, v in d["demanda_fds"].items()}
                     if d["demanda_fds"] else None),
        grade={(k, s): tuple(v) for k, s, v in d["grade"]}, pacientes=d["pacientes"],
        grau=d["grau"])


def carregar() -> list[dict]:
    return json.loads(CASOS_JSON.read_text(encoding="utf-8"))


def rodar(nome: str) -> int:
    bp.so_etapa1()
    d = next(x for x in carregar() if x["nome"] == nome)
    c = caso(d)
    esperado, folgas, _ = bd.conta(c)
    t0 = time.time()
    print(f"{nome}: {c.modelo}, {c.n_enf}+{c.n_tec}; conta: {esperado} {folgas}", flush=True)
    r = fe.verificar(brd.entrada(c), progresso=lambda f, msg: print(
        f"{nome} [{time.time() - t0:7.1f} s] {msg}", flush=True))
    out = {"caso": nome, "modelo": c.modelo, "equipe": f"{c.n_enf}+{c.n_tec}",
           "estrato": d["estrato"], "esperado": esperado, "folgas": folgas,
           "veredito": r.veredito, "frase": r.frase(), "menor_viavel": r.menor_viavel,
           "tentativas": r.tentativas, "provado": r.provado if r.escala else None,
           "gap": r.indicadores.get("gap"), "tempo_total": time.time() - t0}
    if r.escala:
        out["conferencia"] = brd.conferir(r)
    gravar(nome, out)
    print(f"{nome}: {r.veredito} menor {r.menor_viavel} | {out['tempo_total']:.0f} s",
          flush=True)
    return 0


def gravar(nome: str, out: dict) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / f"{nome}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1,
                                                   default=str), encoding="utf-8")


NAO_DETERMINADO = "nao_determinado_15min"


def lote() -> int:
    """Todos os casos, um processo cada, ate LIMITE_CASO; pula os que ja tem resultado."""
    for d in carregar():
        nome = d["nome"]
        if (SAIDA / f"{nome}.json").exists():
            continue
        SAIDA.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        with open(SAIDA / f"{nome}.log", "w", encoding="utf-8") as log:
            try:
                subprocess.run([sys.executable, str(Path(__file__).resolve()), nome],
                               stdout=log, stderr=subprocess.STDOUT, timeout=LIMITE_CASO)
            except subprocess.TimeoutExpired:
                gravar(nome, {"caso": nome, "modelo": d["modelo"],
                              "equipe": f"{d['n_enf']}+{d['n_tec']}", "estrato": d["estrato"],
                              "esperado": d["esperado"], "folgas": d["folgas"],
                              "veredito": NAO_DETERMINADO, "frase": "", "menor_viavel": None,
                              "tentativas": [], "provado": None, "gap": None,
                              "tempo_total": time.time() - t0})
        if not (SAIDA / f"{nome}.json").exists():
            print(f"{nome}: o processo terminou sem gravar resultado (ver {nome}.log)",
                  flush=True)
            continue
        o = json.loads((SAIDA / f"{nome}.json").read_text(encoding="utf-8"))
        print(f"{nome} [{o['estrato']}]: {o['veredito']} menor {o['menor_viavel']} | "
              f"{o['tempo_total']:.0f} s | falhas: {falhas(o) or 'nenhuma'}", flush=True)
    return 0


def falhas(o: dict) -> list[str]:
    f = [f"prop. 1: {x}" for x in bp.falhas_conferencia(o)]
    t0 = o["tentativas"][0][1] if o["tentativas"] else None
    if o["veredito"] == fe.FALTAM and t0 not in ("piso", ea.INVIAVEL):
        f.append("prop. 4: 'faltam N' sem prova do quadro informado")
    if o["provado"] and (o["gap"] or 0) > 1e-4:
        f.append(f"prop. 4: 'provado' com gap {o['gap']}")
    if o["provado"] is False and "pode haver uma melhor" not in o["frase"]:
        f.append("prop. 4: escala sem prova sem o aviso 'pode haver uma melhor'")
    if min(o["folgas"].values()) >= 2 and o["veredito"] in (fe.NAO_DECIDIDO, NAO_DETERMINADO):
        f.append("prop. 5: folga clara terminou sem escala no tempo")
    if o["esperado"].startswith("INVIAVEL") and o["veredito"] == fe.ADMITE:
        f.append("prop. 6: conta inviavel e a ferramenta admitiu")
    return f


def resumo() -> int:
    linhas, esgotados, cont = [], [], {}
    for d in carregar():
        arq = SAIDA / f"{d['nome']}.json"
        if not arq.exists():
            linhas.append(f"| {d['nome']} | {d['estrato']} | {d['modelo']} | | | NAO RODOU "
                          f"| | | |")
            cont["nao rodou"] = cont.get("nao rodou", 0) + 1
            continue
        o = json.loads(arq.read_text(encoding="utf-8"))
        f = falhas(o)
        cont[o["veredito"]] = cont.get(o["veredito"], 0) + 1
        cont["com falha"] = cont.get("com falha", 0) + bool(f)
        folga = min(o["folgas"].values())
        linhas.append(f"| {o['caso']} | {o['estrato']} | {o['modelo']} | {o['equipe']} | "
                      f"{o['esperado']} ({folga:g}) | {o['veredito']} | {o['menor_viavel']} | "
                      f"{'; '.join(f) or 'nenhuma'} | {o['tempo_total']:.0f} s |")
        if o["veredito"] == NAO_DETERMINADO or o["provado"] is False or \
                any(t[1] in (ea.INDETERMINADO, ea.ERRO) for t in o["tentativas"]):
            esgotados.append(f"| {o['caso']} | {o['estrato']} | {o['modelo']} | "
                             f"{o['equipe']} | "
                             f"{', '.join(f'{k} {v:g}' for k, v in o['folgas'].items())} | "
                             f"{o['veredito']} | {o['tentativas']} |")
    print("| Caso | Estrato | Modelo | Equipe | Conta (menor folga) | Veredito | Menor viável "
          "| Falhas | Tempo |")
    print("|---|---|---|---|---|---|---|---|---|")
    print("\n".join(linhas))
    print("\nEsgotaram o tempo (sem escala, escala sem prova ou 15 min):\n")
    print("| Caso | Estrato | Modelo | Equipe | Folgas pela conta | Veredito | Tentativas |")
    print("|---|---|---|---|---|---|---|")
    print("\n".join(esgotados) or "| nenhum | | | | | | |")
    print("\n", cont)
    return 0


def tabela_sorteio() -> None:
    contagem: dict = {}
    for d in carregar():
        contagem[(d["modelo"], d["estrato"])] = contagem.get((d["modelo"], d["estrato"]), 0) + 1
    print("| Modelo | Folga clara | Fronteira | Inviável | Total |")
    print("|---|---|---|---|---|")
    for m in bd.MODELOS:
        v = [contagem.get((m, e), 0) for e in ESTRATOS]
        print(f"| {m} | {' | '.join(map(str, v))} | {sum(v)} |")
    tot = [sum(contagem.get((m, e), 0) for m in bd.MODELOS) for e in ESTRATOS]
    print(f"| **Total** | {' | '.join(map(str, tot))} | {sum(tot)} |")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("caso", nargs="?")
    ap.add_argument("--gerar", action="store_true")
    ap.add_argument("--lote", action="store_true")
    ap.add_argument("--resumo", action="store_true")
    a = ap.parse_args()
    if a.gerar:
        casos, sorteados = sortear()
        CASOS_JSON.write_text(json.dumps(casos, ensure_ascii=False, indent=1),
                              encoding="utf-8")
        print(f"{len(casos)} casos gravados em {CASOS_JSON.name} (semente {SEMENTE}; "
              f"{sorteados} candidatos sorteados)")
        tabela_sorteio()
        return 0
    if a.lote:
        return lote()
    return resumo() if a.resumo else rodar(a.caso)


if __name__ == "__main__":
    raise SystemExit(main())
