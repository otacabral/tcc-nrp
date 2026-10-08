"""Nivel 3 da bateria (`docs/bateria_entradas.md`): lote aleatorio de 100 casos pequenos, SO A
ETAPA 1, 600 s, conferido pelas propriedades 1, 4, 5 e 6 da C3.

    python docs\\diagnostico\\bateria_nivel3.py --gerar        # sorteia e grava os casos (sem solver)
    python docs\\diagnostico\\bateria_nivel3.py N001           # roda um caso
    python docs\\diagnostico\\bateria_nivel3.py --resumo       # confere tudo

O sorteio usa `SEMENTE` e grava `docs/diagnostico/nivel3_casos.json`, commitado ANTES do
primeiro solver. Cada caso roda pelo caminho da tela (`bateria_rodar.entrada` ->
`ferramenta.verificar`), com a etapa 2 desligada como em `bateria_propriedades.py`: as
propriedades conferidas aqui (escala legal, honestidade, folga clara, coerencia com a conta)
so dependem da etapa 1.

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

SEMENTE = 81026
N_CASOS = 100
CASOS_JSON = Path(__file__).resolve().parent / "nivel3_casos.json"
SAIDA = RAIZ / "resultados" / "bateria_2026-10-08" / "parte4"
GRAUS = ["minimo", "intermediario", "alta", "semi_intensivo", "intensivo"]


def sortear() -> list[dict]:
    rng = random.Random(SEMENTE)
    segundas = [date(2026, 10, 5) + timedelta(weeks=k) for k in range(26)]   # ate 29/03/2027
    casos = []
    for i in range(N_CASOS):
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
        casos.append({
            "nome": f"N{i + 1:03d}", "modelo": modelo,
            "fds": rng.choice(["sab_dom", "sex_dom"]), "inicio": str(rng.choice(segundas)),
            "n_enf": n_enf, "n_tec": n_tec, "nomes": rng.random() < 0.5,
            "cargas": cargas, "ferias": ferias, "pedidos": rng.randint(0, 6),
            "demanda": demanda, "demanda_fds": demanda_fds,
            "grade": [[k, s, list(v)] for (k, s), v in grade.items()],
            "pacientes": pacientes, "grau": rng.choice(GRAUS)})
    return casos


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
           "esperado": esperado, "folgas": folgas, "veredito": r.veredito,
           "frase": r.frase(), "menor_viavel": r.menor_viavel, "tentativas": r.tentativas,
           "provado": r.provado if r.escala else None, "gap": r.indicadores.get("gap"),
           "tempo_total": time.time() - t0}
    if r.escala:
        out["conferencia"] = brd.conferir(r)
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / f"{nome}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1,
                                                   default=str), encoding="utf-8")
    print(f"{nome}: {r.veredito} menor {r.menor_viavel} | {out['tempo_total']:.0f} s",
          flush=True)
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
    if min(o["folgas"].values()) >= 2 and o["veredito"] == fe.NAO_DECIDIDO:
        f.append("prop. 5: folga clara terminou sem escala no tempo")
    if o["esperado"].startswith("INVIAVEL") and o["veredito"] == fe.ADMITE:
        f.append("prop. 6: conta inviavel e a ferramenta admitiu")
    return f


def resumo() -> int:
    linhas, esgotados, cont = [], [], {}
    for d in carregar():
        arq = SAIDA / f"{d['nome']}.json"
        if not arq.exists():
            linhas.append(f"| {d['nome']} | {d['modelo']} | | | NAO RODOU | | | |")
            cont["nao rodou"] = cont.get("nao rodou", 0) + 1
            continue
        o = json.loads(arq.read_text(encoding="utf-8"))
        f = falhas(o)
        cont[o["veredito"]] = cont.get(o["veredito"], 0) + 1
        cont["com falha"] = cont.get("com falha", 0) + bool(f)
        folga = min(o["folgas"].values())
        linhas.append(f"| {o['caso']} | {o['modelo']} | {o['equipe']} | {o['esperado']} "
                      f"({folga:g}) | {o['veredito']} | {o['menor_viavel']} | "
                      f"{'; '.join(f) or 'nenhuma'} | {o['tempo_total']:.0f} s |")
        if any(t[1] in (ea.INDETERMINADO, ea.ERRO) for t in o["tentativas"]) or \
                (o["provado"] is False):
            esgotados.append(f"| {o['caso']} | {o['modelo']} | {o['equipe']} | "
                             f"{', '.join(f'{k} {v:g}' for k, v in o['folgas'].items())} | "
                             f"{o['veredito']} | {o['tentativas']} |")
    print("| Caso | Modelo | Equipe | Conta (menor folga) | Veredito | Menor viável | Falhas | "
          "Tempo |")
    print("|---|---|---|---|---|---|---|---|")
    print("\n".join(linhas))
    print("\nEsgotaram o tempo (sem escala, ou escala sem prova):\n")
    print("| Caso | Modelo | Equipe | Folgas pela conta | Veredito | Tentativas |")
    print("|---|---|---|---|---|---|")
    print("\n".join(esgotados) or "| nenhum | | | | | |")
    print("\n", cont)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("caso", nargs="?")
    ap.add_argument("--gerar", action="store_true")
    ap.add_argument("--resumo", action="store_true")
    a = ap.parse_args()
    if a.gerar:
        CASOS_JSON.write_text(json.dumps(sortear(), ensure_ascii=False, indent=1),
                              encoding="utf-8")
        print(f"{N_CASOS} casos gravados em {CASOS_JSON.name} (semente {SEMENTE})")
        return 0
    return resumo() if a.resumo else rodar(a.caso)


if __name__ == "__main__":
    raise SystemExit(main())
