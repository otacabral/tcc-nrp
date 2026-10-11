"""Defeito de texto da P17 (11/10): a linha "Escala desta tela" sem melhora da etapa 2. Sem solver.

    python docs\\diagnostico\\p17_frase_conferir.py

O defeito: no caminho SEM prova, quando a etapa 2 nao acha escala mais equilibrada que a da
etapa 1 (o que aconteceu nas 4 rodadas registradas: DECISOES.md, "2026-10-10 — P17"), a tela
dizia "a da etapa 2, com a carga equilibrada entre colegas", o que e falso.

Correcao decidida pelo Otavio (11/10), so no caminho sem prova: quando o criterio final da etapa 2
(soma das amplitudes da fracao do contrato por categoria) NAO for menor que o da etapa 1, a tela
mostra a escala da etapa 1 e a linha passa a ser NOVA (abaixo). Quando for menor, fica a linha
atual. O caminho COM prova nao muda (a demonstracao e o 9d passam por ele).

Este script monta `ferramenta.Resultado` com os indicadores GRAVADOS das rodadas e chama
`frase_vigente`, sem resolver nada. Os casos de 09/10 nao gravaram o criterio; ele e recontado
dos logs: com 44 h para todos, sem ferias e 28 dias, as horas devidas sao 176 h por pessoa, e a
amplitude da fracao de cada categoria e a diferenca maxima de horas / 176 (vale para Otavio, K5 e
K6, conferido nas entradas: `cargas` vazio e nenhuma indisponibilidade).

ESPERADO, registrado e commitado ANTES de implementar:
- K5 de 11/10 (`resultados/p17_diagnostico_2026-10-10/ferramenta.json`), Otavio, K5 e K6 de 09/10
  (`resultados/fechar_v12/p17_*.log`): sem prova, criterio final = etapa 1 -> NOVA;
- 9d (com prova; amplitude 36,4% -> 4,5%, `resultados/fechar_v12/tela_9.log`) -> ATUAL_PROVADO;
- caso sintetico sem prova com melhora (criterio 0,40 -> 0,20) -> ATUAL_SEM_PROVA.
Antes da correcao, os quatro primeiros dao ATUAL_SEM_PROVA (o defeito) e o script FALHA.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import ferramenta as fe  # noqa: E402

NOVA = ("Escala desta tela: a da etapa 1. O equilíbrio de carga não achou, no tempo disponível, "
        "escala mais equilibrada sem piorar o resultado da etapa 1.")
ATUAL_SEM_PROVA = ("Escala desta tela: a da etapa 2, com a carga equilibrada entre colegas, "
                   "sobre uma escala sem prova de ótimo: o equilíbrio não deixou piorar o "
                   "valor achado pela etapa 1.")
ATUAL_PROVADO = "Escala desta tela: a da etapa 2, com a carga equilibrada entre colegas."
DEVIDAS = 44 * 28 / 7


def resultado(ind: dict) -> fe.Resultado:
    return fe.Resultado(veredito=fe.ADMITE, quadro_informado=0, menor_viavel=None, alertas=[],
                        tentativas=[], indicadores=ind)


def do_log(caso: str) -> dict:
    texto = (RAIZ / "resultados" / "fechar_v12" / f"p17_{caso}.log").read_text(encoding="utf-8")
    d = json.loads(texto[texto.index("{"):texto.rindex("}") + 1])
    crit = lambda parte: sum(h / DEVIDAS for h in d[parte]["diferenca_h"].values())
    # o log nao grava "provado"; gap > 0 e escala sem prova (e a frase do log diz "pode haver")
    return {"etapa2": d["etapa2"], "provado": not (d["gap"] or 0) > 1e-9,
            "amplitude_etapa1": crit("etapa1"), "amplitude": crit("final")}


def main() -> int:
    k5 = json.loads((RAIZ / "resultados" / "p17_diagnostico_2026-10-10" / "ferramenta.json")
                    .read_text(encoding="utf-8"))
    casos = [
        ("K5 11/10", {k: k5[k] for k in ("etapa2", "provado", "amplitude", "amplitude_etapa1")},
         NOVA),
        *[(f"{c} 09/10", do_log(c), NOVA) for c in ("otavio", "K5", "K6")],
        ("9d (com prova)", {"etapa2": "ok", "provado": True, "amplitude_etapa1": 0.364,
                            "amplitude": 0.045}, ATUAL_PROVADO),
        ("sintetico sem prova, com melhora", {"etapa2": "ok", "provado": False,
                                              "amplitude_etapa1": 0.40, "amplitude": 0.20},
         ATUAL_SEM_PROVA),
    ]
    ok = True
    for nome, ind, esperado in casos:
        dita = resultado(ind).frase_vigente()
        bate = dita == esperado
        ok &= bate
        print(f"{'ok   ' if bate else 'FALHA'} {nome}: criterio {ind['amplitude_etapa1']:.4f} -> "
              f"{ind['amplitude']:.4f}, provado {ind['provado']}\n      tela: {dita}")
    print("FRASE OK" if ok else "FRASE FALHA")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
