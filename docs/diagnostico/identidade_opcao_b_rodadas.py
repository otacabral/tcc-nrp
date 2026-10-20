"""Opcao B, teste (a2): rodadas com a classificacao padrao e os limites da v1.2.3.

Esperado registrado antes: `resultados/opcao_b_2026-10-19/ESPERADO.md`, item (a2). Limites
600 s / 180 s / orcamento 20 min, como nas rodadas registradas.

    python docs\\diagnostico\\identidade_opcao_b_rodadas.py P01      # um caso da bateria
    python docs\\diagnostico\\identidade_opcao_b_rodadas.py demo20   # uma rodada da demo
    python docs\\diagnostico\\identidade_opcao_b_rodadas.py --comparar

Bateria: `bateria_rodar.rodar` com saida em `resultados/opcao_b_2026-10-19/bateria/`,
comparada campo a campo com `resultados/bateria_2026-10-07/`. Demonstracao: `fe.verificar` sem
a tela, comparada com os valores do NUMEROS_TCC, secao 9.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "docs"), str(AQUI),
                str(RAIZ / "docs" / "demonstracao")]

import bateria_rodar as brr  # noqa: E402
import ferramenta as fe  # noqa: E402

fe.TEMPO, fe.TEMPO_ETAPA2, fe.ORCAMENTO = 600, 180, 20 * 60
# pasta de saida: a da v1.3.0 por padrao; a suite da v1.4.0 (20/10) passa outra pela variavel
# de ambiente A2_SAIDA, para nao sobrescrever o registro da v1.3.0
_A2 = os.environ.get("A2_SAIDA")
SAIDA = Path(_A2) if _A2 else RAIZ / "resultados" / "opcao_b_2026-10-19"
REGISTRADA = RAIZ / "resultados" / "bateria_2026-10-07"
CAMPOS = ("veredito", "frase", "menor_viavel", "tentativas", "diagnostico", "provado",
          "etapa2", "falhas")
# Parte 7 (20/10, v1.4.1): quadros que a rodada registrada provou inviaveis pelo SOLVER e que a
# conta por pares de dias passa a recusar sem solver — a tentativa vira (q, "piso", None, None).
# Lista tirada sem solver e registrada antes da suite (resultados/piso_pares_2026-10-20/
# seguranca.md). Vale so com A2_PISO_PARES=1 (suite da v1.4.1); qualquer outra diferenca falha.
ADMITIDAS = {"P05": [14]}

# NUMEROS_TCC.md, secao 9 (rodadas de 05/10, refeitas em 09/10)
DEMO = {
    20: {"frase": "O quadro informado admite escala legal. Escala gerada.", "alertas": 0,
         "enf_em_posto_tec": 24, "menor_viavel": 30},
    19: {"frase": "O quadro informado admite escala legal. Escala gerada.", "alertas": 1,
         "enf_em_posto_tec": 36, "menor_viavel": 29},
    18: {"frase": "Falta 1; o menor quadro viável é 29. Escala gerada.", "alertas": None,
         "enf_em_posto_tec": 34, "menor_viavel": 29, "diagnostico": "alternancia"},
}


def demo(tec: int) -> int:
    import caso_clinica_medica as cc
    r = fe.verificar(cc.entrada(tec))
    ind = r.indicadores
    out = {"tec": tec, "frase": r.frase(), "frase_vigente": r.frase_vigente(),
           "menor_viavel": r.menor_viavel, "tentativas": r.tentativas,
           "diagnostico": list(r.diagnostico) if r.diagnostico else None,
           "alertas": r.alertas, "enf_em_posto_tec": ind.get("enf_em_posto_tec"),
           "pedidos": f"{ind.get('pedidos_atendidos')} de {ind.get('pedidos_total')}",
           "descanso": r.conformidade["ok"] if r.conformidade else None,
           "provado": r.provado, "caminho": ind.get("caminho"), "criterios": r.criterios,
           "fracao": (ind.get("fracao_min"), ind.get("fracao_max")),
           "diferenca": {g: fe.fmt_diferenca(c) for g, c in ind.get("categorias", {}).items()},
           "nao_utilizadas": {g: round(c["nao_utilizadas"])
                              for g, c in ind.get("categorias", {}).items()}}
    (SAIDA / "demo").mkdir(parents=True, exist_ok=True)
    (SAIDA / "demo" / f"demo{tec}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, default=str)[:600], flush=True)
    return 0


def comparar() -> int:
    linhas, falhas = [], 0
    for nova in sorted((SAIDA / "bateria").glob("*.json")):
        a = json.loads((REGISTRADA / nova.name).read_text(encoding="utf-8"))
        b = json.loads(nova.read_text(encoding="utf-8"))
        if os.environ.get("A2_PISO_PARES") == "1":
            q_conta = ADMITIDAS.get(nova.stem, [])
            a["tentativas"] = [[t[0], "piso", None, None] if t[0] in q_conta
                               and t[1] == "inviavel" else t for t in a["tentativas"]]
        dif = [c for c in CAMPOS if json.dumps(a.get(c), default=str)
               != json.dumps(b.get(c), default=str)]
        if a.get("conferencia") and b.get("conferencia"):
            for k in ("rigidas", "descanso_cumpre", "acima_do_teto", "trabalha_em_ferias"):
                if a["conferencia"][k] != b["conferencia"][k]:
                    dif.append(f"conferencia.{k}")
        falhas += bool(dif) or bool(b.get("falhas"))
        linhas.append(f"| {nova.stem} | {b['veredito']} | {b['menor_viavel']} | "
                      f"{'iguais' if not dif else 'DIFERENTES: ' + ', '.join(dif)} |")
    for tec, esp in DEMO.items():
        arq = SAIDA / "demo" / f"demo{tec}.json"
        if not arq.exists():
            linhas.append(f"| demo{tec} | (não rodou) | | |")
            falhas += 1
            continue
        b = json.loads(arq.read_text(encoding="utf-8"))
        dif = [k for k in ("frase", "enf_em_posto_tec", "menor_viavel") if b[k] != esp[k]]
        if esp["alertas"] is not None and len(b["alertas"]) != esp["alertas"]:
            dif.append("alertas")
        if esp.get("diagnostico") and (not b["diagnostico"]
                                       or b["diagnostico"][0] != esp["diagnostico"]):
            dif.append("diagnostico")
        if b["pedidos"] != "6 de 6" or b["descanso"] is not True:
            dif.append("pedidos/descanso")
        falhas += bool(dif)
        linhas.append(f"| demo{tec} | {b['frase']} | {b['menor_viavel']} | "
                      f"{'iguais' if not dif else 'DIFERENTES: ' + ', '.join(dif)}; etapa 2: "
                      f"fração {b['fracao']}, diferença {b['diferenca']}, não utilizadas "
                      f"{b['nao_utilizadas']} |")
    texto = ["| Caso | Veredito / frase | Menor quadro | Comparação |", "|---|---|---|---|",
             *linhas, "", "TUDO IGUAL" if not falhas else f"{falhas} COM DIFERENÇA"]
    (SAIDA / "identidade_a2.md").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print("\n".join(texto))
    return 1 if falhas else 0


def main() -> int:
    arg = sys.argv[1]
    if arg == "--comparar":
        return comparar()
    if arg.startswith("demo"):
        return demo(int(arg[4:]))
    brr.SAIDA = SAIDA / "bateria"
    return brr.rodar(arg)


if __name__ == "__main__":
    raise SystemExit(main())
