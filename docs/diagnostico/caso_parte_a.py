"""Parte A do diagnostico (07/10): o caso do Otavio, 6 h de dia + noturno de 12 h.

    python docs\\diagnostico\\caso_parte_a.py inspecionar            # A3d, sem solver
    python docs\\diagnostico\\caso_parte_a.py etapa1 --enf 15 --tempo 3600 --log <arq>

Monta a instancia pelo mesmo caminho da tela (`ferramenta.Entrada` -> `ferramenta.montar`) e,
em `etapa1`, monta o modelo como a ferramenta monta a etapa 1 (`ferramenta.pesos` +
`experimento_a.modelo_br`) e resolve uma vez, com o log do HiGHS em arquivo. Nao muda nada
em src/.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402
import modelo  # noqa: E402

TURNOS = fe.MODELOS[next(k for k in fe.MODELOS if k.startswith("6"))]   # M 7-13, T 13-19, N 19-7
DEMANDA = {"M": (2, 1), "T": (2, 1), "N": (3, 2)}
INICIO = date(2026, 10, 12)


def entrada(n_enf: int = 15, n_tec: int = 5) -> fe.Entrada:
    return fe.Entrada(turnos=TURNOS, grau="intermediario", n_enfermeiros=n_enf,
                      n_tecnicos=n_tec, demanda_turno=DEMANDA, inicio=INICIO)


def inspecionar() -> None:
    e = entrada()
    inst = fe.montar(e)
    c = inst.contratos["0"]
    print("turnos:", [(s, str(t.inicio)[:5], str(t.fim)[:5], t.duracao_h, sorted(t.habilidades))
                      for s, t in inst.turnos.items()])
    print("MaxNumAssignments:", c.max_num_assignments.valor, "ativa", c.max_num_assignments.ativa,
          "peso", c.max_num_assignments.peso)
    print("MaxConsecutiveWorkingDays:", c.max_consecutive_working_days.valor,
          "ativa", c.max_consecutive_working_days.ativa)
    print("tetos de horas:", sorted({inst.horas_devidas(n) for n in inst.profissionais}))
    base = [(tid, ini, fe.duracao(ini, fim)) for tid, ini, fim in TURNOS]
    pares = br.pares_proibidos_por_horario(base, c.max_consecutive_working_days.valor,
                                           descartar=False)
    print("pares proibidos (turno, salto em dias, turno):", sorted(pares))
    print("padroes no contrato:", len(c.padroes_indesejados), sorted(c.padroes_indesejados)[:12],
          "...")
    print("limite_efetivo:", fe.limite_efetivo(inst), "| piso:", fe.piso(inst))
    print("motivos simples da trava:", [m for m, _ in fe.motivos_da_trava(inst)])
    horas = sum(q * inst.turnos[s].duracao_h for (_, s), q in inst.demanda.items())
    print("demanda total no horizonte:", horas, "h; capacidade 20 x 176 =", 20 * 176)
    print("demanda por dia:", {s: inst.demanda_de(inst.dias[0], s) for s in inst.turnos})


def etapa1(n_enf: int, n_tec: int, tempo: int, log: str, relaxar: str | None = None) -> None:
    inst = fe.montar(entrada(n_enf, n_tec))
    inst, custo, W = fe.pesos(inst)
    m = ea.modelo_br(inst, custo)
    if relaxar:
        import relaxar as rx
        print("relaxado:", rx.aplicar(m, inst, relaxar))
    d = modelo.dimensao(m)
    print(f"{n_enf}+{n_tec}: {d['variaveis']} variaveis, {d['restricoes']} restricoes; "
          f"limite {tempo} s", flush=True)
    t0 = time.time()
    res = modelo.resolver(m, solver=modelo.SOLVER_PADRAO, tempo_limite=tempo, carregar=False,
                          log_arquivo=log)
    print(f"estado {modelo.estado(res)} | provou otimo {modelo.provou_otimo(res)} | tem "
          f"solucao {modelo.tem_solucao(res)} | gap {modelo.gap_relativo(res)} | "
          f"{time.time() - t0:.1f} s", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("acao", choices=["inspecionar", "etapa1"])
    ap.add_argument("--enf", type=int, default=15)
    ap.add_argument("--tec", type=int, default=5)
    ap.add_argument("--tempo", type=int, default=600)
    ap.add_argument("--log", default=None)
    ap.add_argument("--relaxar", default=None)
    a = ap.parse_args()
    if a.acao == "inspecionar":
        inspecionar()
    else:
        etapa1(a.enf, a.tec, a.tempo, a.log, a.relaxar)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
