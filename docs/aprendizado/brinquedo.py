"""Instancia de brinquedo (parte B2, 07/10), para estudar o modelo e o log do HiGHS.

    python docs\\aprendizado\\brinquedo.py

O que monta: 12x36 (D 7-19, N 19-7), 3 dias (segunda a quarta), 2 enfermeiros + 1 tecnico,
1 pedido de folga.
- Demanda: D com 1 enfermeiro todos os dias; N com 1 tecnico na segunda e na quarta, e
  nenhum na terca (grade por data).
- No 12x36 quem trabalha num dia folga no seguinte. Entao, a cada dois dias seguidos, os
  postos tem de caber em 3 pessoas: seg + ter = 2 + 1 = 3 e ter + qua = 1 + 2 = 3. Cabe
  justinho.
- Pedido de folga: Enf 2 na segunda. Pode ser atendido: Enf 1 faz o D de segunda e de quarta,
  Enf 2 o de terca, e o tecnico o N de segunda e de quarta.

A VARIANTE INVIAVEL poe 1 tecnico tambem no N de terca: seg + ter passa a pedir 4 pessoas
diferentes, e so ha 3.

Monta pelo mesmo caminho da tela: `ferramenta.Entrada` e a mesma chamada que
`ferramenta.montar` faz (`instancia_br.construir`), com uma diferenca so, `dias=3` — a tela
fixa 28 dias. Depois `ferramenta.pesos` e `experimento_a.modelo_br`, como na etapa 1.
Grava `brinquedo.lp` (o modelo legivel) e os logs do HiGHS ao lado deste arquivo.
"""

from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402
import modelo  # noqa: E402

SEG = br.primeira_segunda()


def instancia(inviavel: bool = False):
    ter = SEG + timedelta(days=1)
    e = fe.Entrada(turnos=[("D", 7, 19), ("N", 19, 7)], grau="intermediario",
                   n_enfermeiros=2, n_tecnicos=1,
                   demanda_turno={"D": (1, 0), "N": (0, 1)},
                   demanda_data={} if inviavel else {(ter, "N", "tec"): 0},
                   inicio=SEG, pedidos=[("Enf 2", SEG)])
    # a mesma chamada de `ferramenta.montar`, com dias=3
    return br.construir(
        turnos=[(nome, ini, fe.duracao(ini, fim), nome) for nome, ini, fim in e.turnos],
        demanda_turno=e.demanda_turno, demanda_fds=e.demanda_fds,
        demanda_data=e.demanda_data, fim_de_semana=e.fim_de_semana, inicio=e.inicio,
        n_enfermeiros=e.n_enfermeiros, n_tecnicos=e.n_tecnicos, nomes_enfermeiros=None,
        nomes_tecnicos=None, indisponibilidades=[], pedidos=e.pedidos, cargas={}, dias=3)


def resolver(inst, log: Path, lp: Path | None = None):
    inst, custo, W = fe.pesos(inst)
    m = ea.modelo_br(inst, custo)
    if lp is not None:
        m.write(str(lp), io_options={"symbolic_solver_labels": True})
    res = modelo.resolver(m, solver=modelo.SOLVER_PADRAO, tempo_limite=60, carregar=False,
                          log_arquivo=str(log))
    print(f"{log.name}: estado {modelo.estado(res)} | W = {W}")
    if modelo.tem_solucao(res) and modelo.carregar_solucao(m, res):
        print("   objetivo", modelo.valor_objetivo(m))
        for d, n, s in sorted(modelo.atribuicoes(m)):
            print(f"   {d:%a %d/%m} {inst.profissionais[n].nome:6s} {s}")
    return m


def main() -> int:
    resolver(instancia(), AQUI / "brinquedo_highs.log", AQUI / "brinquedo.lp")
    resolver(instancia(inviavel=True), AQUI / "brinquedo_inviavel_highs.log")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
