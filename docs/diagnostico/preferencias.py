"""Preferencia de maximo de dias seguidos e de maximo de turnos (21/10) — testes (b), (c) e (e).

Esperado registrado antes: `resultados/preferencias_2026-10-21/ESPERADO.md`. Decisao:
`DECISOES.md`, "2026-10-21 — Maximo de dias seguidos e maximo de turnos tambem como preferencia".

    python docs\\diagnostico\\preferencias.py --controle <pasta>                 # (b), sem solver
    python docs\\diagnostico\\preferencias.py --caso-pequeno                     # (c), com solver
    python docs\\diagnostico\\preferencias.py --gravar-fase2 <pasta> [--raiz R]  # (e), sem solver
    python docs\\diagnostico\\identidade_opcao_b.py --comparar <v141> <nova>

`--raiz R`: grava com o codigo da arvore R (o worktree da v1.4.1, `..\\tcc-nrp-v141`), que tem o
`fase2.py` e o `identidade_opcao_b.py` commitados; sem `--raiz`, a arvore deste arquivo.

(c) conta as violacoes direto das sequencias da escala, sem `avaliacao.py` e sem modelo, e
compara com o "Resultado por criterio" (que vem do `avaliacao.py`).
"""

from __future__ import annotations

import argparse
import dataclasses
import filecmp
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _caminhos(raiz: Path) -> None:
    """O codigo da arvore `raiz` na frente; esta pasta sai do sys.path (senao o `fase2.py` e o
    `identidade_opcao_b.py` daqui sombreariam os da outra arvore)."""
    sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != AQUI]
    sys.path[:0] = [str(raiz / "docs" / "diagnostico"), str(raiz / "docs"), str(raiz / "src")]


# --- (e) identidade nas cinco entradas da fase 2 ----------------------------------------------

ACRESCIMOS = {"A36_livre": (0, 6), "A36_fixo": (0, 6), "A11_fixo": (0, 6),
              "B11_livre": (0,), "B36_livre": (0,)}


def gravar_fase2(pasta: Path) -> int:
    import fase2
    import identidade_opcao_b as io_b
    br, fe = fase2.br, fase2.fe
    pasta.mkdir(parents=True, exist_ok=True)
    print(f"codigo de {Path(fe.__file__).resolve().parents[1]}")
    n = 0
    for nome, acrescimos in ACRESCIMOS.items():
        _, _, param = fase2.RODADAS[nome]
        e = fase2.entrada(nome)
        br.DESCANSO_POR_TURNO.clear()
        br.DESCANSO_POR_TURNO.update(param)
        try:
            horas_enf = fe._horas_enfermeiro(e)
            for a in acrescimos:
                io_b.gravar_caso(pasta, f"{nome}_a{a}", fe.montar(e, a, horas_enf),
                                 e.prioridades)
                n += 1
        finally:
            br.DESCANSO_POR_TURNO.clear()
        print(nome, flush=True)
    print(f"{n} casos, {3 * n} arquivos em {pasta}")
    return 0


# --- (b) controle -----------------------------------------------------------------------------

def controle(pasta: Path) -> int:
    import identidade_opcao_b as io_b
    import prioridades as pr
    fe, br = io_b.fe, io_b.br
    pasta.mkdir(parents=True, exist_ok=True)
    nome, e = next(io_b.entradas())
    inst = fe.montar(e)
    padrao = fe.prioridades_padrao()
    casos = {"padrao": padrao,
             "dias4": dict(padrao, max_dias_seguidos=(fe.IMPORTANTE, 4)),
             "turnos10": dict(padrao, max_turnos=(fe.IMPORTANTE, 10)),
             "acima": dict(padrao, max_dias_seguidos=(fe.IMPORTANTE, 9),
                           max_turnos=(fe.IMPORTANTE, 999))}
    lp = {}
    for rotulo, p in casos.items():
        io_b.gravar_caso(pasta, f"{nome}_{rotulo}", inst, p)
        lp[rotulo] = (pasta / f"{nome}_{rotulo}_etapa1.lp").read_text(encoding="utf-8")
    falhas = 0

    def confere(ok, msg):
        nonlocal falhas
        falhas += not ok
        print(f"   {'ok   ' if ok else 'FALHA'} {msg}")

    confere("pref_" not in lp["padrao"], "padrao: nenhuma familia pref_ no LP")
    for rotulo, familia in (("dias4", pr.PREF_DIAS), ("turnos10", pr.PREF_TURNOS)):
        muda = not filecmp.cmp(pasta / f"{nome}_padrao_etapa1.lp",
                               pasta / f"{nome}_{rotulo}_etapa1.lp", shallow=False)
        confere(muda and familia in lp[rotulo], f"{rotulo}: LP muda e contem {familia}")
    confere(pr.PREF_DIAS in lp["acima"] and pr.PREF_TURNOS in lp["acima"],
            "acima do legal: as duas familias existem")
    p = pr.normalizar(casos["acima"])
    aplicada, _ = pr.aplicar(inst, p, {k: 1 for k in p}, br.HABILIDADE_ENF)
    c0, c1 = inst.contratos["0"], aplicada.contratos["0"]
    confere(c1.pref_max_consecutive_working_days.valor == c0.max_consecutive_working_days.valor
            and c1.pref_max_num_assignments.valor == c0.max_num_assignments.valor,
            f"acima do legal: limite usado = o legal ({c1.pref_max_consecutive_working_days.valor}"
            f" dias, {c1.pref_max_num_assignments.valor} turnos)")
    print(f"controle {'OK' if not falhas else f'com {falhas} FALHA(S)'}")
    return 1 if falhas else 0


# --- (c) caso pequeno, com solver ---------------------------------------------------------------

def _sequencias(inst, escala) -> dict[str, list[int]]:
    """Tamanhos das sequencias de dias trabalhados de cada pessoa, direto da escala."""
    trab = {(n, d) for d, n, _ in escala}
    saida = {}
    for n in inst.profissionais:
        seqs, k = [], 0
        for d in inst.dias:
            if (n, d) in trab:
                k += 1
            elif k:
                seqs.append(k)
                k = 0
        if k:
            seqs.append(k)
        saida[n] = seqs
    return saida


def caso_pequeno() -> int:
    import ferramenta as fe
    import instancia_br as br
    base = fe.Entrada(turnos=[("M", 7, 13), ("T", 13, 19)], grau="intermediario",
                      n_enfermeiros=0, n_tecnicos=14,
                      demanda_turno={"M": (0, 6), "T": (0, 6)}, inicio=br.primeira_segunda())
    padrao = fe.prioridades_padrao()
    # 96, nao 56: o esperado de 56 ignorava a cobertura (2 folgas por dia); a conta de 96 foi
    # feita DEPOIS de rodar (ESPERADO.md, "Acrescimo a posteriori"): 14 x 24 janelas de 5 dias
    # - 2 folgas/dia x 120 janelas quebradas no maximo = 96
    rodadas = (("c1", dict(padrao, max_dias_seguidos=(fe.IMPORTANTE, 4)), 96, None, "fundido"),
               ("c2", dict(padrao, max_dias_seguidos=(fe.IMPORTANTE, 4),
                           max_turnos=(fe.DESEJAVEL, 23)), 96, 14, "em sequência, 2 blocos"))
    falhas = 0

    def confere(ok, msg):
        nonlocal falhas
        falhas += not ok
        print(f"   {'ok   ' if ok else 'FALHA'} {msg}", flush=True)

    for rotulo, p, esp_dias, esp_turnos, caminho in rodadas:
        print(f"({rotulo}) {p['max_dias_seguidos']} dias; {p['max_turnos']} turnos", flush=True)
        r = fe.verificar(dataclasses.replace(base, prioridades=p))
        print(f"   {r.frase()} | caminho {r.indicadores.get('caminho')} | {r.criterios}")
        confere(r.veredito == fe.ADMITE and r.menor_viavel == 14 and r.provado,
                f"veredito {r.veredito}, menor viavel {r.menor_viavel}, provado {r.provado}")
        confere(r.indicadores.get("caminho") == caminho,
                f"caminho {r.indicadores.get('caminho')} (esperado {caminho})")
        if not r.escala:
            continue
        seqs = _sequencias(r.inst, r.escala)
        maior = max((s for v in seqs.values() for s in v), default=0)
        confere(maior <= 6 and r.conformidade["max_consec"] <= 6 and r.conformidade["ok"],
                f"maior sequencia na escala {maior}, no relogio {r.conformidade['max_consec']}, "
                f"descanso {'ok' if r.conformidade['ok'] else 'REPROVADO'}")
        por = {nome: v for _, nome, v, _ in r.criterios}
        dias = sum(max(0, s - 4) for v in seqs.values() for s in v)
        confere(dias == por.get("Máximo de dias seguidos (preferência)") == esp_dias,
                f"dias seguidos acima de 4: script {dias}, resultado por criterio "
                f"{por.get('Máximo de dias seguidos (preferência)')}, esperado {esp_dias}")
        if esp_turnos is not None:
            turnos = {}
            for _, n, _ in r.escala:
                turnos[n] = turnos.get(n, 0) + 1
            exc = sum(max(0, t - 23) for t in turnos.values())
            confere(exc == por.get("Máximo de turnos no período") == esp_turnos,
                    f"turnos acima de 23: script {exc}, resultado por criterio "
                    f"{por.get('Máximo de turnos no período')}, esperado {esp_turnos}")
    print(f"caso pequeno {'OK' if not falhas else f'com {falhas} FALHA(S)'}")
    return 1 if falhas else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--controle", type=Path)
    ap.add_argument("--caso-pequeno", action="store_true")
    ap.add_argument("--gravar-fase2", type=Path)
    ap.add_argument("--raiz", type=Path, default=AQUI.parents[1])
    a = ap.parse_args()
    _caminhos(a.raiz.resolve())
    if a.gravar_fase2:
        return gravar_fase2(a.gravar_fase2.resolve())
    if a.controle:
        return controle(a.controle.resolve())
    return caso_pequeno()


if __name__ == "__main__":
    raise SystemExit(main())
