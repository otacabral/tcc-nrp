"""medium_late05, alvo de validacao (DECISOES.md, "2026-09-15 — Quinto alvo de validacao"),
rodado de novo nesta maquina. Da raiz, com a .venv ativa e nada pesado rodando junto:

    python docs\\rodar_medium_late05.py              # limite 3600 s

Monta o modelo como `src/regressao.py` monta os quatro alvos (`modelo.construir(inst)`, as
opcoes do INRC), resolve com `appsi_highs` e o limite dado, grava o log do HiGHS, a escala
obtida e um resumo em `resultados/medium_late05_2026-10-06/`, e confere a escala no avaliador
oficial (`src/validar.py`) e no `avaliacao.py`.

ESPERADO, registrado ANTES de rodar (06/10/2026): o otimo publicado e **107** (Tabela 6 de
Santos et al., 2016, gap 0). Em 15/09, num container de desenvolvimento (HiGHS via SciPy), o
limite de 520 s deu 716 sem prova (`resultados/consolidado.csv`). Esperado aqui: se o solver
provar otimalidade dentro de 3600 s, o valor e 107 e o avaliador oficial da 107 na escala
gravada. Se nao provar, registra-se o que vier — valor da melhor escala, limite inferior, gap,
estado — e o avaliador tem de dar, na escala gravada, o mesmo valor do modelo. Qualquer valor
abaixo de 107 seria defeito (o otimo esta provado na Tabela 6).
"""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import modelo  # noqa: E402
from avaliacao import penalidade  # noqa: E402
from parser import ler_instancia  # noqa: E402
from solucao import escrever_xml  # noqa: E402

INSTANCIA = RAIZ / "instancias" / "medium" / "medium_late_xml" / "medium_late05.xml"
PUBLICADO = 107
SAIDA = RAIZ / "resultados" / "medium_late05_2026-10-06"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tempo", type=int, default=3600)
    ap.add_argument("--solver", default=modelo.SOLVER_PADRAO)
    a = ap.parse_args()
    SAIDA.mkdir(parents=True, exist_ok=True)
    log = SAIDA / "highs.log"
    inst = ler_instancia(str(INSTANCIA))
    m = modelo.construir(inst)
    d = modelo.dimensao(m)
    print(f"medium_late05: {d['variaveis']} variaveis, {d['restricoes']} restricoes; "
          f"solver {a.solver}, limite {a.tempo} s", flush=True)
    t0 = time.time()
    res = modelo.resolver(m, solver=a.solver, tempo_limite=a.tempo, carregar=False,
                          log_arquivo=str(log))
    relogio = time.time() - t0
    texto = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    dual = re.findall(r"Dual bound\s+(\S+)", texto)
    primal = re.findall(r"Primal bound\s+(\S+)", texto)
    r = {"instancia": "medium_late05", "publicado": PUBLICADO, "solver": a.solver,
         "limite_s": a.tempo, "relogio_s": round(relogio, 1), "estado": modelo.estado(res),
         "provou_otimo": modelo.provou_otimo(res), "gap": modelo.gap_relativo(res),
         "limite_inferior_log": dual[-1] if dual else None,
         "melhor_valor_log": primal[-1] if primal else None,
         "maquina": f"{platform.processor()} | {platform.platform()} | "
                    f"Python {platform.python_version()}"}
    if modelo.tem_solucao(res) and modelo.carregar_solucao(m, res):
        z = modelo.valor_objetivo(m)
        escala = modelo.atribuicoes(m)
        r["valor_modelo"] = z
        r["valor_avaliacao_py"] = penalidade(inst, escala)
        sol = SAIDA / "medium_late05_escala.xml"
        escrever_xml(inst, escala, sol, penalidade=z)
        aval = subprocess.run([sys.executable, str(RAIZ / "src" / "validar.py"),
                               str(INSTANCIA), str(sol), "--objetivo", str(z)],
                              capture_output=True, text=True, cwd=RAIZ)
        r["validar_saida"] = (aval.stdout + aval.stderr).strip()[-1500:]
        r["validar_codigo"] = aval.returncode
    (SAIDA / "resumo.json").write_text(json.dumps(r, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
