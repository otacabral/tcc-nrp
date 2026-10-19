"""Tamanho do modelo: o nosso (medido no Pyomo) e o de Santos et al. (2016) (pela definicao).

Item 8 da sessao de 19/10, para o comparativo pedido pelo orientador. Sem solver: so monta o
modelo e conta (`modelo.dimensao`). Nao afirma eficiencia: tamanho nao diz tempo de resolucao.

Santos et al. (2016), secao 3.2 (variaveis), conforme o fichamento da Redacao (SA16-019 a
SA16-020, conferido na versao publicada em 13/10): x[n,s,d]; y[n,i] por fim de semana;
w[n,d1,d2] e r[n,d1,d2] para todo par d1 <= d2 (|D|(|D|+1)/2 janelas); z[n,i1,i2] para todo
par de fins de semana i1 <= i2. As folgas alfa dependem de quais suaves estao ativas e NAO sao
contadas aqui — por isso a coluna de Santos e um limite INFERIOR do numero de variaveis dele.
Conferir no artigo antes de ir ao texto.

    python docs\\diagnostico\\tamanho_modelos.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "docs" / "demonstracao")]

import modelo  # noqa: E402
from parser import ler_instancia  # noqa: E402

SAIDA = RAIZ / "resultados" / "tamanho_modelos_2026-10-19"
ALVOS = [("sprint01", "instancias/sprint/sprint/sprint01.xml"),
         ("sprint02", "instancias/sprint/sprint/sprint02.xml"),
         ("long01", "instancias/long/long/long01.xml"),
         ("long02", "instancias/long/long/long02.xml"),
         ("medium_late05", "instancias/medium/medium_late_xml/medium_late05.xml")]


def santos(inst) -> dict[str, int]:
    N, S, D = len(inst.profissionais), len(inst.turnos), len(inst.dias)
    F = max(len(inst.fins_de_semana(c)) for c in inst.contratos)
    janelas = D * (D + 1) // 2
    return {"x": N * S * D, "y": N * F, "w": N * janelas, "r": N * janelas,
            "z": N * F * (F + 1) // 2}


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    linhas = []
    for nome, caminho in ALVOS:
        inst = ler_instancia(RAIZ / caminho)
        d = modelo.dimensao(modelo.construir(inst))
        s = santos(inst)
        linhas.append((nome, len(inst.profissionais), len(inst.turnos), len(inst.dias),
                       d["variaveis"], d["restricoes"], s["x"], s["y"], s["w"], s["r"],
                       s["z"], sum(s.values())))
    # a ferramenta: o caso da demonstracao (rodada 1), com as opcoes da etapa 1
    import caso_clinica_medica as cc  # noqa: E402
    import experimento_a as ea  # noqa: E402
    import ferramenta as fe  # noqa: E402
    inst = fe.montar(cc.entrada())
    inst_p, custo, _ = fe.pesos(inst)
    d = modelo.dimensao(ea.modelo_br(inst_p, custo))
    linhas.append(("ferramenta: demonstracao, rodada 1 (etapa 1)", len(inst.profissionais),
                   len(inst.turnos), len(inst.dias), d["variaveis"], d["restricoes"],
                   "", "", "", "", "", ""))
    cab = ["instancia", "profissionais", "turnos", "dias", "nosso_variaveis",
           "nosso_restricoes", "santos_x", "santos_y", "santos_w", "santos_r", "santos_z",
           "santos_x_y_w_r_z"]
    with open(SAIDA / "tamanho.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(cab)
        w.writerows(linhas)
    for l in linhas:
        print(l)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
