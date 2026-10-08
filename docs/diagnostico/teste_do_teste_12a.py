"""Teste do teste 12a (08/10): a conferencia "grade da tela = grade da planilha" pega uma
planilha diferente da tela?

    python docs\\diagnostico\\teste_do_teste_12a.py

Roda o caso 5 pela tela (o mesmo do 12a) e passa a MESMA conferencia do 12a
(`testes_ferramenta.confere_tela_e_planilha`) duas vezes, sem mexer em src/:

1. com o resultado alterado em memoria: uma atribuicao da escala troca de turno (M <-> T, com
   ou sem *), entao a planilha gerada desse resultado difere da grade que a tela mostrou;
2. com o resultado como a tela o guardou.

ESPERADO, registrado antes de rodar: em 1, a conferencia "grade da tela = grade da planilha"
FALHA (e so ela: "planilha = r.escala" continua valendo, porque planilha e escala alterada
concordam entre si); em 2, nenhuma falha.
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import testes_ferramenta as tf  # noqa: E402

TROCA = {"M": "T", "T": "M", "ME": "TE", "TE": "ME"}


def main() -> int:
    at = tf.pela_tela(tf.M8, 8, 5, {"M": (1, 2), "T": (1, 2), "N": (1, 1)})
    r, e = at.session_state["resultado"]

    k = next(i for i, (_, _, s) in enumerate(r.escala) if s in TROCA)
    d, n, s = r.escala[k]
    alterada = list(r.escala)
    alterada[k] = (d, n, TROCA[s])
    print(f"1. resultado alterado em memoria: {n} em {d}, {s} -> {TROCA[s]}")
    tf.FALHAS.clear()
    tf.confere_tela_e_planilha(at, dataclasses.replace(r, escala=tuple(alterada)), e)
    falhas_1 = list(tf.FALHAS)

    print("2. resultado como a tela o guardou")
    tf.FALHAS.clear()
    tf.confere_tela_e_planilha(at, r, e)
    falhas_2 = list(tf.FALHAS)

    ok = falhas_1 == ["grade da tela = grade da planilha"] and falhas_2 == []
    print(f"\nfalhas em 1: {falhas_1}\nfalhas em 2: {falhas_2}")
    print("TESTE DO TESTE OK: pega a diferenca e passa sem ela" if ok else
          "TESTE DO TESTE FALHOU")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
