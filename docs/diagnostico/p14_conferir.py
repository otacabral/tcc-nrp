"""Conferencia da P14 (09/10): etapa 2 tambem quando a etapa 1 termina sem prova.

    python docs\\diagnostico\\p14_conferir.py otavio      # o caso de teste do Otavio de 09/10
    python docs\\diagnostico\\p14_conferir.py K5          # K5 ou K6 da bateria

Pelo caminho da tela (`ferramenta.verificar`), limites da tela. Grava a saida em
`resultados/p14_p15_2026-10-09/p14_<caso>.json`.

ESPERADO, registrado ANTES de implementar (`resultados/relatorio_2026-10-09b.md`, parte B), nos
tres casos (otavio, K5, K6), comparando com a escala que a etapa 1 achou NA MESMA RODADA (a
etapa 1 para no limite de tempo e pode achar escalas diferentes a cada execucao):
1. a etapa 2 roda: `etapa2` nao comeca por "nao rodou" e `tempo_etapa2` > 0;
2. turnos de enfermeiro em posto de tecnico da escala final <= os da escala da etapa 1;
3. a maior amplitude da fracao cumprida (criterio da etapa 2) <= a da escala da etapa 1
   (redacao de 30/10, abaixo);
4. descanso conferido: `conformidade["ok"]` e `solucao.conferir_rigidas` sem problema;
5. pedidos atendidos da escala final >= os da etapa 1 (o otavio e K5/K6 nao tem pedidos).

P17 (09/10), com `--p17`, esperado registrado ANTES de implementar a partida da etapa 2:
6. a etapa 2 SEMPRE entrega escala (`etapa2` == "ok"): ela parte da escala da etapa 1, que
   cumpre "nao piorar" por construcao.
A saida vai para `p17_<caso>.json`.

Nota de 30/10/2026 (v1.4.5, etapa 2 por min-max; DECISOES.md, "2026-10-30 — Etapa 2 por min-max
(v1.4.5)"), registrada ANTES de mudar a conferencia: o item 3 era "diferenca maxima de carga entre
colegas, em cada categoria, <= a da escala da etapa 1". O min-max garante so a maior amplitude; a
categoria menor pode subir (limitacao declarada), e nem a soma garantia o item 3 por categoria.
Fora da suite da v1.4.5 (os casos dependem do tempo); o caminho sem prova fica coberto pelos
testes 8 e 9c-tela. Os JSON de 09/10 foram gerados com o item 3 antigo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(AQUI))

import ferramenta as fe  # noqa: E402
import solucao  # noqa: E402

SAIDA = RAIZ / "resultados" / "p14_p15_2026-10-09"


def entrada(nome: str):
    if nome == "otavio":
        import caso_otavio_0910 as co
        return co.entrada()
    import bateria_propriedades as bp
    import bateria_rodar as brd
    return brd.entrada(next(c for c in bp.TODOS if c.nome.startswith(nome)))


def main() -> int:
    nome = sys.argv[1]
    p17 = "--p17" in sys.argv[2:]
    r = fe.verificar(entrada(nome))
    ind = r.indicadores
    e1 = ind.get("etapa1", {})
    cat = ind.get("categorias", {})
    ok = {
        "1 etapa 2 rodou": not str(ind.get("etapa2", "")).startswith(("não rodou", "nao rodou"))
                           and ind.get("tempo_etapa2", 0) > 0,
        "2 enf em posto tec <= etapa 1": ind["enf_em_posto_tec"] <= e1.get("enf_em_posto_tec", -1),
        "3 diferenca por categoria <= etapa 1": all(
            cat[g]["diferenca_h"] <= e1["categorias"][g]["diferenca_h"] + 1e-6 for g in cat),
        "4 descanso e rigidas": bool(r.conformidade and r.conformidade["ok"])
                                and not solucao.conferir_rigidas(r.inst, r.escala,
                                                                 habilidade_rigida=True),
        "5 pedidos >= etapa 1": ind["pedidos_atendidos"] >= e1.get("pedidos_atendidos", 10**9),
    }
    if p17:
        ok["6 etapa 2 entregou escala"] = ind.get("etapa2") == "ok"
    out = {"caso": nome, "frase": r.frase(), "vigente": r.frase_vigente(),
           "etapa2": ind.get("etapa2"), "tempo_etapa1": ind.get("tempo_etapa1"),
           "tempo_etapa2": ind.get("tempo_etapa2"), "gap": ind.get("gap"),
           "penalidade_etapa1": ind.get("penalidade"),
           "etapa1": {"enf_em_posto_tec": e1.get("enf_em_posto_tec"),
                      "pedidos_atendidos": e1.get("pedidos_atendidos"),
                      "fracao": (e1.get("fracao_min"), e1.get("fracao_max")),
                      "diferenca_h": {g: c["diferenca_h"] for g, c in e1.get("categorias", {}).items()}},
           "final": {"enf_em_posto_tec": ind["enf_em_posto_tec"],
                     "pedidos_atendidos": ind["pedidos_atendidos"],
                     "fracao": (ind["fracao_min"], ind["fracao_max"]),
                     "diferenca_h": {g: c["diferenca_h"] for g, c in cat.items()}},
           "descanso_semanal_sem_bordas": r.conformidade and r.conformidade.get("menor_semanal_interno"),
           "conferencias": ok}
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / f"{'p17' if p17 else 'p14'}_{nome}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1,
                                                       default=str), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    rotulo = "P17" if p17 else "P14"
    print(f"{rotulo} OK" if all(ok.values()) else f"{rotulo} FALHA")
    return 0 if all(ok.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
