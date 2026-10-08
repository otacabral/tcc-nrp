"""Roda a bateria de entradas, nivel 1 (`docs/bateria_entradas.md`), um caso por processo.

    python docs\\diagnostico\\bateria_rodar.py P08            # um caso; grava o JSON do caso
    python docs\\diagnostico\\bateria_rodar.py --resumo       # tabela de todos os JSON gravados

Pelo mesmo caminho da tela, sem navegador: `Caso` do gerador -> `ferramenta.Entrada` ->
`ferramenta.verificar`, com os limites da tela (600 s e 180 s). O esperado de cada caso e o
da conta independente do gerador (`bateria_desenho.conta`), registrado antes no commit
`62bbf4d`. Nao muda nada em src/.

Traducao do `Caso` para a `Entrada` (declarada em 07/10, antes de rodar):

- profissionais por id ("0", "1", ...: enfermeiros primeiro), o mesmo indice da conta; cargas,
  ferias e pedidos referem-se a esses ids;
- area "nomes": nomes com acento, um por pessoa, sem repeticao (nome repetido e erro de
  entrada, conferido em `testes_entrada.py`, e abortaria o caso); sem a area, nomes padrao;
- ferias (i, a, b): pessoa i, de inicio + a ate inicio + b;
- pedidos (so a quantidade no gerador): o k-esimo e da pessoa (3k + 1) mod N, no dia
  inicio + (5k + 3) mod 28. Pedido nao entra na conta (e flexivel);
- demanda: a do caso, ou (1, 2) por turno, como na conta; grade (k, s) -> (enf, tec) vira
  demanda especifica na data inicio + k, por cima da do fim de semana, como na conta.

Conferencias por caso, todas por fora do modelo (C3 da bateria):

- `solucao.conferir_rigidas`: cobertura e um turno por dia, contando a escala;
- descanso medido no relogio (`conferencia_descanso_escala.medir` / `cumpre`);
- teto de horas: horas trabalhadas <= carga x dias disponiveis / 7, recontado aqui;
- ferias: nenhuma atribuicao em dia indisponivel;
- coerencia com a conta: conta INVIAVEL -> a ferramenta nao pode admitir o quadro informado;
- folga clara (menor folga >= 2) nao pode terminar sem escala;
- honestidade: "faltam N" so com o quadro informado provado inviavel (piso ou solver).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "docs"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import bateria_desenho as bd  # noqa: E402
import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import solucao  # noqa: E402
from conferencia_descanso_escala import cumpre, medir  # noqa: E402

SAIDA = RAIZ / "resultados" / "bateria_2026-10-07"

NOMES = ["Áurea", "Bárbara", "Cássio", "Débora", "Émerson", "Fátima", "Gonçalo", "Hélio",
         "Inês", "Joaquim", "Lúcia", "Mônica", "Natália", "Otávio R.", "Pâmela", "Quênia",
         "Rúbia", "Sérgio", "Tânia", "Úrsula", "Vânia"]


def entrada(c: bd.Caso) -> fe.Entrada:
    turnos = c.turnos or bd.MODELOS[c.modelo]
    n = c.n_enf + c.n_tec
    demanda = c.demanda or {s: (1, 2) for s, _, _ in turnos}
    grade = {}
    for (k, s), (enf, tec) in c.grade.items():
        d = c.inicio + timedelta(days=k)
        grade[(d, s, "enf")], grade[(d, s, "tec")] = enf, tec
    nomes_enf = nomes_tec = None
    if "nomes" in c.areas:
        nomes_enf, nomes_tec = NOMES[:c.n_enf], NOMES[c.n_enf:n]
    return fe.Entrada(
        turnos=list(turnos), grau=c.grau, n_enfermeiros=c.n_enf, n_tecnicos=c.n_tec,
        demanda_turno=demanda, demanda_fds=c.demanda_fds or {}, demanda_data=grade,
        fim_de_semana=c.fds, inicio=c.inicio, nomes_enfermeiros=nomes_enf,
        nomes_tecnicos=nomes_tec,
        indisponibilidades=[(str(i), c.inicio + timedelta(days=a), c.inicio + timedelta(days=b))
                            for i, a, b in c.ferias],
        pedidos=[(str((3 * k + 1) % n), c.inicio + timedelta(days=(5 * k + 3) % 28))
                 for k in range(c.pedidos)],
        pacientes=c.pacientes, cargas={str(i): h for i, h in c.cargas.items()})


def conferir(r) -> dict:
    """Conferencias por fora do modelo, na escala devolvida."""
    inst, escala = r.inst, r.escala
    horas = {n: 0.0 for n in inst.profissionais}
    for _, n, s in escala:
        horas[n] += inst.turnos[s].duracao_h
    acima = [n for n, h in horas.items() if h > inst.horas_devidas(n) + 1e-6]
    em_ferias = [(str(d), n) for d, n, _ in escala if (n, d) in inst.indisponiveis]
    m = medir(inst, escala)
    return {"rigidas": solucao.conferir_rigidas(inst, escala), "descanso_cumpre": cumpre(inst, m),
            "menor_folga_descanso_h": m["menor_folga"], "max_consec": m["max_consec"],
            "acima_do_teto": acima, "trabalha_em_ferias": em_ferias}


def rodar(nome: str) -> int:
    c = next(x for x in bd.CASOS + bd.CONHECIDOS if x.nome.split()[0] == nome)
    esperado, folgas, bloq = bd.conta(c)
    t0 = time.time()
    linhas = []

    def progresso(frac, msg):
        linha = f"[{time.time() - t0:7.1f} s] {msg}"
        linhas.append(linha)
        print(f"{nome} {linha}", flush=True)

    print(f"{nome}: {c.modelo}, {c.n_enf}+{c.n_tec}; esperado pela conta: {esperado} {folgas}",
          flush=True)
    r = fe.verificar(entrada(c), progresso=progresso)
    total = time.time() - t0
    out = {"caso": nome, "modelo": c.modelo, "equipe": f"{c.n_enf}+{c.n_tec}",
           "esperado": esperado, "folgas": folgas, "veredito": r.veredito, "frase": r.frase(),
           "menor_viavel": r.menor_viavel, "tentativas": r.tentativas,
           "diagnostico": r.diagnostico[2] if r.diagnostico else None,
           "provado": r.provado if r.escala else None,
           "gap": r.indicadores.get("gap"), "tempo_etapa1": r.indicadores.get("tempo_etapa1"),
           "tempo_etapa2": r.indicadores.get("tempo_etapa2"),
           "etapa2": r.indicadores.get("etapa2"), "tempo_total": total, "progresso": linhas}
    falhas = []
    if r.escala:
        conf = conferir(r)
        out["conferencia"] = conf
        if conf["rigidas"]:
            falhas.append("rigidas: " + "; ".join(conf["rigidas"][:3]))
        if not conf["descanso_cumpre"]:
            falhas.append("descanso nao cumpre")
        if conf["acima_do_teto"]:
            falhas.append(f"acima do teto de horas: {conf['acima_do_teto']}")
        if conf["trabalha_em_ferias"]:
            falhas.append(f"trabalha em ferias: {conf['trabalha_em_ferias'][:3]}")
    if esperado.startswith("INVIAVEL") and r.veredito == fe.ADMITE:
        falhas.append("conta diz inviavel e a ferramenta admitiu o quadro informado")
    if min(folgas.values()) >= 2 and not r.escala:
        falhas.append("folga clara terminou sem escala")
    if r.veredito == fe.FALTAM and r.tentativas[0][1] not in ("piso", ea.INVIAVEL):
        falhas.append("'faltam N' sem prova do quadro informado")
    out["falhas"] = falhas
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / f"{nome}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1,
                                                   default=str), encoding="utf-8")
    print(f"{nome}: {r.frase()} | {total:.0f} s | falhas: {falhas or 'nenhuma'}", flush=True)
    return 0


def resumo() -> int:
    print("| Caso | Modelo | Equipe | Esperado pela conta | Veredito | Menor viável | Provado | "
          "Etapa 2 | Tempo total | Falhas |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for arq in sorted(SAIDA.glob("*.json")):
        o = json.loads(arq.read_text(encoding="utf-8"))
        print(f"| {o['caso']} | {o['modelo']} | {o['equipe']} | {o['esperado']} | "
              f"{o['veredito']} | {o['menor_viavel']} | {o['provado']} | {o['etapa2']} | "
              f"{o['tempo_total']:.0f} s | {'; '.join(o['falhas']) or 'nenhuma'} |")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("caso", nargs="?")
    ap.add_argument("--resumo", action="store_true")
    a = ap.parse_args()
    return resumo() if a.resumo else rodar(a.caso)


if __name__ == "__main__":
    raise SystemExit(main())
