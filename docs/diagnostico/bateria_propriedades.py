"""Propriedades 2 (monotonia) e 3 (ordem) da bateria (`docs/bateria_entradas.md`, C3), sobre
os 24 casos do nivel 1 e do nivel 2. Um caso derivado por processo. SO A ETAPA 1.

    python docs\\diagnostico\\bateria_propriedades.py P08 mais_pessoa   # um derivado
    python docs\\diagnostico\\bateria_propriedades.py --resumo           # confere tudo

**Etapa 2 desligada** (`ferramenta.equilibrar` trocado aqui, sem mexer em src/): o veredito
e o menor quadro saem so da etapa 1 — a etapa 2 so roda depois de a etapa 1 provar o otimo,
fixa esse otimo e troca a escala por outra de mesmo custo. Nada do que estas propriedades
olham depende dela. Limite da etapa 1: o da tela, 600 s.

**Base de comparacao:** os 24 JSON da rodada de 07/10 (`resultados/bateria_2026-10-07/`),
com a etapa 2 ligada — veredito e menor quadro de la tambem sao so da etapa 1.

Derivados (declarados em 08/10, antes de rodar), feitos sobre a `Entrada` do caso, para que
nada mais mude:

- `mais_pessoa`: +1 tecnico de 44 h, no fim da lista (os ids dos outros nao mudam; com
  nomes, "Zélia Nova");
- `mais_posto`: +1 posto de tecnico no 1o turno do modelo, no 4o dia do horizonte
  (inicio + 3), por cima da demanda que la valia;
- `mais_ferias`: +1 dia de ferias para o profissional "0" (um enfermeiro), no primeiro dia a
  partir de inicio + 10 em que ele ainda esta disponivel;
- `embaralhado`: profissionais permutados dentro de cada categoria, com cargas, ferias,
  pedidos e nomes acompanhando a pessoa. Semente `SEMENTE` + indice do caso.

O que se exige (o que pode ser provado, nao mais):

- `mais_pessoa` (quadro Q + 1): com o menor quadro M da base, nenhum tamanho >= M + 1 pode ser
  provado inviavel no derivado. Motivo: a equipe do derivado de tamanho M + 1 com os
  acrescimos todos enfermeiros contem a escala da base em M mais um tecnico, que pode ficar
  sem turno (cobertura e por posto; teto, descanso e dias seguidos so limitam por cima);
- `mais_posto`, `mais_ferias` (mesmo Q): nenhum tamanho que a base provou inviavel (piso ou
  solver) pode ter escala no derivado. Motivo: escala do derivado, tirando o posto a mais ou
  devolvendo o dia de ferias, e escala da base;
- `embaralhado`: mesmo veredito e mesmo menor quadro.

"Nao decidido" num dos lados torna a comparacao inconclusiva (listada a parte, camada solver).
Toda escala do derivado passa tambem pelas conferencias da propriedade 1
(`bateria_rodar.conferir`).
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import random
import sys
import time
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bateria_desenho as bd  # noqa: E402
import bateria_rodar as brd  # noqa: E402
import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402

SEMENTE = 20261008
BASE = RAIZ / "resultados" / "bateria_2026-10-07"
SAIDA = RAIZ / "resultados" / "bateria_2026-10-08" / "parte3"
VARIANTES = ("mais_pessoa", "mais_posto", "mais_ferias", "embaralhado")
TODOS = bd.CASOS + bd.CONHECIDOS


def so_etapa1() -> None:
    """Desliga a etapa 2: `resolver_com_objetivo` fica com a escala da etapa 1."""
    fe.equilibrar = lambda m, inst, z, tempo, **kw: (ea.INDETERMINADO, None, False, None)


def derivar(c: bd.Caso, variante: str) -> fe.Entrada:
    e = brd.entrada(c)
    if variante == "mais_pessoa":
        nomes = None if e.nomes_tecnicos is None else list(e.nomes_tecnicos) + ["Zélia Nova"]
        return dataclasses.replace(e, n_tecnicos=e.n_tecnicos + 1, nomes_tecnicos=nomes)
    if variante == "mais_posto":
        inst = fe.montar(e)
        d, s = e.inicio + timedelta(days=3), e.turnos[0][0]
        grade = dict(e.demanda_data)
        grade[(d, s, "tec")] = inst.demanda_de(d, s) + 1
        return dataclasses.replace(e, demanda_data=grade)
    if variante == "mais_ferias":
        fora = fe.montar(e).indisponiveis
        k = next(k for k in range(10, 28) if ("0", e.inicio + timedelta(days=k)) not in fora)
        d = e.inicio + timedelta(days=k)
        return dataclasses.replace(e, indisponibilidades=list(e.indisponibilidades) + [("0", d, d)])
    if variante == "embaralhado":
        rng = random.Random(SEMENTE + TODOS.index(c))
        enf, tec = list(range(e.n_enfermeiros)), list(range(e.n_enfermeiros, e.quadro))
        rng.shuffle(enf)
        rng.shuffle(tec)
        nova = {antigo: novo for antigo, novo in
                zip(range(e.quadro), enf + tec)}          # pessoa i passa ao id nova[i]
        p = lambda q: str(nova[int(q)])                   # noqa: E731
        nomes_enf = nomes_tec = None
        if e.nomes_enfermeiros is not None:
            todos = list(e.nomes_enfermeiros) + list(e.nomes_tecnicos)
            novos = [None] * e.quadro
            for i, nome in enumerate(todos):
                novos[nova[i]] = nome
            nomes_enf, nomes_tec = novos[:e.n_enfermeiros], novos[e.n_enfermeiros:]
        return dataclasses.replace(
            e, nomes_enfermeiros=nomes_enf, nomes_tecnicos=nomes_tec,
            cargas={p(q): h for q, h in e.cargas.items()},
            indisponibilidades=[(p(q), a, b) for q, a, b in e.indisponibilidades],
            pedidos=[(p(q), d) for q, d in e.pedidos])
    raise ValueError(variante)


def rodar(nome: str, variante: str) -> int:
    so_etapa1()
    c = next(x for x in TODOS if x.nome.split()[0] == nome)
    e = derivar(c, variante)
    t0 = time.time()
    r = fe.verificar(e, progresso=lambda f, msg: print(
        f"{nome}/{variante} [{time.time() - t0:7.1f} s] {msg}", flush=True))
    out = {"caso": nome, "variante": variante, "quadro": e.quadro, "veredito": r.veredito,
           "menor_viavel": r.menor_viavel, "tentativas": r.tentativas,
           "provado": r.provado if r.escala else None, "gap": r.indicadores.get("gap"),
           "tempo_total": time.time() - t0}
    if r.escala:
        out["conferencia"] = brd.conferir(r)
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / f"{nome}_{variante}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(f"{nome}/{variante}: {r.veredito} menor {r.menor_viavel} | "
          f"{out['tempo_total']:.0f} s", flush=True)
    return 0


PROVADO_INVIAVEL = ("piso", ea.INVIAVEL)
DECIDIDOS = (fe.ADMITE, fe.FALTAM, fe.SEM_VIAVEL)


def checar(base: dict, d: dict) -> tuple[str, str]:
    """(situacao, detalhe): situacao em ok / FALHA / inconclusivo."""
    if d["veredito"] not in DECIDIDOS or base["veredito"] not in DECIDIDOS:
        return "inconclusivo", f"base {base['veredito']}, derivado {d['veredito']}"
    v, M, Md = d["variante"], base["menor_viavel"], d["menor_viavel"]
    inviaveis_d = {t[0] for t in d["tentativas"] if t[1] in PROVADO_INVIAVEL}
    inviaveis_b = {t[0] for t in base["tentativas"] if t[1] in PROVADO_INVIAVEL}
    if v == "mais_pessoa":
        if M is None:
            return "ok", "base sem quadro viavel na faixa: nada a exigir"
        ruins = sorted(k for k in inviaveis_d if k >= M + 1)
        if ruins or d["veredito"] == fe.SEM_VIAVEL:
            return "FALHA", f"base viavel em {M}; derivado prova inviavel {ruins or 'toda a faixa'}"
        return "ok", f"base {M}, derivado {Md} (exigido <= {M + 1})"
    if v in ("mais_posto", "mais_ferias"):
        if Md is not None and Md in inviaveis_b:
            return "FALHA", f"base provou {Md} inviavel; derivado tem escala em {Md}"
        return "ok", f"base {M}, derivado {Md} (exigido: nao viavel onde a base provou inviavel)"
    if v == "embaralhado":
        if (d["veredito"], Md) != (base["veredito"], M):
            return "FALHA", f"base {base['veredito']} {M}; embaralhado {d['veredito']} {Md}"
        return "ok", f"{d['veredito']} {Md} nos dois"
    raise ValueError(v)


def falhas_conferencia(d: dict) -> list[str]:
    conf = d.get("conferencia")
    if not conf:
        return []
    f = []
    if conf["rigidas"]:
        f.append("rigidas")
    if not conf["descanso_cumpre"]:
        f.append("descanso")
    if conf["acima_do_teto"]:
        f.append("teto")
    if conf["trabalha_em_ferias"]:
        f.append("ferias")
    return f


def resumo() -> int:
    print("| Caso | Variante | Base (veredito, menor) | Derivado (veredito, menor) | Situação | "
          "Detalhe | Conferências da escala | Tempo |")
    print("|---|---|---|---|---|---|---|---|")
    contagem: dict[str, int] = {}
    for c in TODOS:
        nome = c.nome.split()[0]
        base = json.loads((BASE / f"{nome}.json").read_text(encoding="utf-8"))
        for v in VARIANTES:
            arq = SAIDA / f"{nome}_{v}.json"
            if not arq.exists():
                print(f"| {nome} | {v} | | | NAO RODOU | | | |")
                contagem["nao rodou"] = contagem.get("nao rodou", 0) + 1
                continue
            d = json.loads(arq.read_text(encoding="utf-8"))
            sit, det = checar(base, d)
            conf = falhas_conferencia(d)
            if conf:
                sit = "FALHA"
            contagem[sit] = contagem.get(sit, 0) + 1
            print(f"| {nome} | {v} | {base['veredito']}, {base['menor_viavel']} | "
                  f"{d['veredito']}, {d['menor_viavel']} | {sit} | {det} | "
                  f"{', '.join(conf) or ('ok' if d.get('conferencia') else 'sem escala')} | "
                  f"{d['tempo_total']:.0f} s |")
    print("\n", contagem)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("caso", nargs="?")
    ap.add_argument("variante", nargs="?", choices=VARIANTES)
    ap.add_argument("--resumo", action="store_true")
    a = ap.parse_args()
    return resumo() if a.resumo else rodar(a.caso, a.variante)


if __name__ == "__main__":
    raise SystemExit(main())
