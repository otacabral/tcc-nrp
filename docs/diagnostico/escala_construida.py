"""Parte A: uma escala construida A MAO para o caso 15 + 5, conferida contra o proprio modelo.

    python docs\\diagnostico\\escala_construida.py

ESPERADO, registrado antes de rodar (07/10): a escala abaixo e viavel. A conferencia fixa as
variaveis do modelo da etapa 1 da ferramenta (o mesmo de `caso_parte_a.py etapa1`) nos
valores dela e resolve: o esperado e "optimal" em segundos. Se der "infeasible", a restricao
violada e a regra que a conta dos ocupados por dia nao enxerga.

A escala:
- noturno: dois grupos que se alternam. Grupo A (dias pares do horizonte): Enf 1 a 3 em NE,
  Tec 1 e 2 em N. Grupo B (dias impares): Enf 4 a 6 em NE, Tec 3 e 4 em N. Cada um faz N
  dia sim, dia nao: 14 noturnos = 168 h <= 176 h; depois do N, 48 h ate o proximo (exige 36 h);
  nunca 2 dias seguidos.
- diurno: Enf 7 a 15 e Tec 5 (10 pessoas) num ciclo de 5 dias, 3 trabalhados e 2 de folga
  (pessoa k trabalha no dia d se (d + k) mod 5 < 3): 6 pessoas por dia, exatamente os 6 postos
  de M e T (ME 2, TE 2, M 1, T 1). Tec 5, quando trabalha, fica com M; os enfermeiros cobrem o
  resto, inclusive o posto de tecnico que sobrar. Do T (fim 19:00) ao M do dia seguinte (07:00)
  sao 12 h (exige 11 h); no maximo 3 dias seguidos.
"""

from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(AQUI))

import pyomo.environ as pyo  # noqa: E402

import caso_parte_a as caso  # noqa: E402
import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import modelo  # noqa: E402
import solucao  # noqa: E402


def construir(inst):
    nome = {p.nome: n for n, p in inst.profissionais.items()}
    escala = []
    for i, d in enumerate(inst.dias):
        if i % 2 == 0:
            noite = [("Enf 1", "NE"), ("Enf 2", "NE"), ("Enf 3", "NE"), ("Téc 1", "N"), ("Téc 2", "N")]
        else:
            noite = [("Enf 4", "NE"), ("Enf 5", "NE"), ("Enf 6", "NE"), ("Téc 3", "N"), ("Téc 4", "N")]
        escala += [(d, nome[p], s) for p, s in noite]
        diurnos = [f"Enf {k}" for k in range(7, 16)] + ["Téc 5"]
        hoje = [p for k, p in enumerate(diurnos) if (i + k) % 5 < 3]
        assert len(hoje) == 6, (i, hoje)
        postos = ["ME", "ME", "TE", "TE", "M", "T"]
        if "Téc 5" in hoje:
            escala.append((d, nome["Téc 5"], "M"))
            hoje.remove("Téc 5")
            postos.remove("M")
        for p, s in zip(hoje, postos):
            escala.append((d, nome[p], s))
    return escala


def main() -> int:
    inst = fe.montar(caso.entrada(15, 5))
    escala = construir(inst)
    problemas = solucao.conferir_rigidas(inst, escala, habilidade_rigida=True)
    print("conferir_rigidas (independente do modelo):", problemas[:5] or "ok")
    med = fe.medir(inst, escala)
    print("descanso medido no relogio:", "cumpre" if fe.cumpre(inst, med) else "NAO CUMPRE",
          {k: med[k] for k in ("menor_geral", "menor_semanal", "max_consec") if k in med})
    inst_p, custo, W = fe.pesos(inst)
    m = ea.modelo_br(inst_p, custo)
    tem = {(n, s, d) for d, n, s in escala}
    fora = [t for t in tem if t not in m.X]
    print("atribuicoes fora do dominio do modelo:", fora[:5] or "nenhuma")
    for (n, s, d) in m.X:
        m.x[n, s, d].fix(1 if (n, s, d) in tem else 0)
    res = modelo.resolver(m, solver=modelo.SOLVER_PADRAO, tempo_limite=120, carregar=False)
    print("modelo com a escala fixada:", modelo.estado(res), "| tem solucao",
          modelo.tem_solucao(res))
    if modelo.tem_solucao(res) and modelo.carregar_solucao(m, res):
        print("objetivo da etapa 1 nessa escala:", modelo.valor_objetivo(m))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
