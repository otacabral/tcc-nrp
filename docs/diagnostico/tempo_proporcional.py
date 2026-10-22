"""22/10: divisao proporcional do tempo maximo (DECISOES.md, "2026-10-22 — Divisao proporcional
do tempo maximo"; esperado em resultados/trava_clt_2026-10-21/ESPERADO.md, acrescimo de 22/10).

    python docs\\diagnostico\\tempo_proporcional.py --conta   # sem solver: (b), (c) e as frases
    python docs\\diagnostico\\tempo_proporcional.py --caso    # COM solver: (d), ~12 min

Sem `TEMPO`/`TEMPO_ETAPA2` (o produto): este script NAO importa o `testes_ferramenta.py`, que os
poe nos valores dos testes ao ser importado.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(RAIZ / "src")]

import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402
import prioridades as pr  # noqa: E402

E, I, D = pr.ESSENCIAL, pr.IMPORTANTE, pr.DESEJAVEL
falhas = 0


def confere(ok, msg):
    global falhas
    falhas += not ok
    print(f"   {'ok   ' if ok else 'FALHA'} {msg}", flush=True)


def _blocos(*grupos):
    return [pr.Bloco(list(g), {}, 0) for g in grupos]


def conta() -> int:
    print("(b) divisao no inicio, em minutos")
    casos = [("1 nivel ou bloco fundido", _blocos([E, I])), ("E | I", _blocos([E], [I])),
             ("E | D", _blocos([E], [D])), ("I | D", _blocos([I], [D])),
             ("E | I | D", _blocos([E], [I], [D])), ("E+I | D", _blocos([E, I], [D]))]
    for nome, b in casos:
        w = fe.pesos_das_partes(b)
        print(f"   {nome:26s} pesos {[round(x, 4) for x in w]} | " + " | ".join(
            f"{T} min: " + " / ".join(f"{T * x:.1f}" for x in w) for T in (20, 60, 120)))
    w1 = fe.pesos_das_partes(_blocos([E, I]))
    confere([60 * x for x in w1] == [30, 30], "padrao a 60 min = 30 + 30")
    confere(fe.pesos_das_partes([]) == [0.5, 0.5], "sem bloco: 30 + 30 tambem")
    w = fe.pesos_das_partes(_blocos([E], [I], [D]))

    print("(c) 60 min, 3 niveis separados, tempos gastos simulados")
    inicio = []
    resta = 3600.0
    for k in range(4):                    # cada parte usa toda a sua fatia
        inicio.append(fe.fatia(resta, w, k))
        resta -= inicio[-1]
    confere([round(x / 60, 1) for x in inicio] == [15, 9, 6, 30], f"inicio {[x / 60 for x in inicio]}")
    resta = 3600 - 120                    # o Essencial prova em 2 min
    imp = fe.fatia(resta, w, 1)
    resta_d = resta - imp                 # o Importante usa tudo
    des = fe.fatia(resta_d, w, 2)
    et2_cheio = resta_d - des             # o Desejavel usa tudo
    et2_1min = resta_d - 60               # o Desejavel prova em 1 min
    confere(round(imp / 60, 1) == 11.6, f"Importante {imp / 60:.2f} min (11,6)")
    confere(round(des / 60, 1) == 7.7, f"Desejavel {des / 60:.2f} min (7,7)")
    confere(round(et2_cheio / 60, 1) == 38.7, f"etapa 2 {et2_cheio / 60:.2f} min (38,7)")
    confere(round(et2_1min / 60, 1) == 45.4, f"etapa 2 com o Desejavel em 1 min "
                                              f"{et2_1min / 60:.2f} min (45,4)")
    import time
    prazo = time.time() + 3600
    confere(fe._limite_da_parte(prazo, w, 0, None) in (899, 900), "limite da parte 0: 900 s")
    confere(fe._limite_da_parte(prazo, w, 0, 25) == 25, "com teto (testes): o teto")
    confere(fe._limite_da_parte(None, w, 0, 600) == 600, "sem prazo (chamada direta): o teto")

    print("frases por nivel (resultado montado a mao)")
    blocos = [([E], {"pedido_folga": 1}, 10), ([I], {"enf_posto_tec": 1}, 50),
              ([D], {"min_turnos": 1}, 99)]
    criterios = [(E, "Pedido de folga no dia", 0, 0), (I, "Enfermeiro em posto de técnico", 7, 3),
                 (D, "Mínimo de turnos no período", 14, 2)]
    partes = [{"niveis": [E], "valor": 0, "provado": True, "gap": 0.0},
              {"niveis": [I], "valor": 7, "provado": False, "gap": 0.5},
              {"niveis": [D], "veredito": "não rodou: orçamento"}]
    r = fe.Resultado(veredito=fe.ADMITE, quadro_informado=3, menor_viavel=3, alertas=[],
                     tentativas=[], indicadores={"blocos": blocos, "partes": partes},
                     criterios=criterios)
    frases = [f for _, f in fe.frases_por_nivel(r)]
    esperadas = ["Essencial: 0 violações — a melhor possível.",
                 "Importante: 7 violações. Nenhuma escala tem menos de 4.",
                 "Desejável: não deu tempo de otimizar; a escala mantém o resultado dos níveis "
                 "acima."]
    confere(frases == esperadas, f"provado / limite 3,5 -> 4 / nao rodou: {frases}")
    partes[1]["gap"] = 1.0
    confere(fe.frases_por_nivel(r)[1][1] == "Importante: 7 violações. Não deu tempo de saber "
            "quanto dá para melhorar.", "limite 0 (gap 100%)")
    # bloco fundido: Essencial coef 51 (Importante vale no maximo 50); limite 120 -> Essencial
    # >= teto((120 - 50) / 51) = 2
    r.indicadores = {"blocos": [([E, I], {"pedido_folga": 51, "enf_posto_tec": 1}, 0)],
                     "partes": [{"niveis": [E, I], "valor": 160, "provado": False,
                                 "gap": 40 / 160}]}
    r.criterios = [(E, "Pedido de folga no dia", 3, 2), (I, "Enfermeiro em posto de técnico", 7, 3)]
    confere(fe.frases_por_nivel(r)[0][1] == "Essencial e Importante: 3 e 7 violações. Nenhuma "
            "escala tem menos de 2 no nível Essencial.", f"fundido: {fe.frases_por_nivel(r)}")
    r.indicadores = {"etapa2": "ok", "provado_etapa2": True}
    confere(fe.frase_equilibrio(r) == "Equilíbrio entre colegas: o melhor possível.", "etapa 2")
    print("conta " + ("OK" if not falhas else f"com {falhas} FALHA(S)"))
    return 1 if falhas else 0


def _quarenta(orc_pedidos=True):
    ini = br.primeira_segunda()
    nomes = [f"Enf {i + 1}" for i in range(14)] + [f"Téc {i + 1}" for i in range(26)]
    pedidos = [(nomes[i], ini + timedelta(days=(3 * i) % 28)) for i in range(20)]
    return fe.Entrada(turnos=fe.MODELOS[list(fe.MODELOS)[0]], grau="intermediario",
                      n_enfermeiros=14, n_tecnicos=26,
                      demanda_turno={"D": (1, 9), "N": (1, 9)},
                      demanda_fds={"D": (1, 6), "N": (1, 6)}, inicio=ini,
                      pedidos=pedidos if orc_pedidos else [])


def _pequeno():
    ini = br.primeira_segunda()
    return fe.Entrada(turnos=fe.MODELOS[list(fe.MODELOS)[0]], grau="intermediario",
                      n_enfermeiros=1, n_tecnicos=2, demanda_turno={"D": (0, 1), "N": (0, 0)},
                      inicio=ini, pedidos=[("Téc 1", ini), ("Téc 2", ini)])


def rodada(rotulo, e, orcamento):
    print(f"{rotulo}: tempo maximo {orcamento} s, 3 niveis separados", flush=True)
    original = pr.LIMITE_FUSAO
    pr.LIMITE_FUSAO = 0                   # forca os tres niveis em blocos separados
    try:
        r = fe.verificar(e, orcamento=orcamento)
    finally:
        pr.LIMITE_FUSAO = original
    ind = r.indicadores or {}
    partes = ind.get("partes", [])
    for k, p in enumerate(partes):
        extra = (f" | protecao: mais {p['protecao']} s (gastou {p['tempo_protecao']:.1f} s)"
                 if "protecao" in p else "")
        print(f"   parte {k} {'+'.join(p.get('niveis', []))}: limite {p['limite']} s, gastou "
              f"{p['tempo']:.1f} s, {'provado' if p.get('provado') else p.get('veredito', 'sem prova')}"
              f"{extra}")
    print(f"   etapa 2: limite {ind.get('limite_etapa2')} s, gastou "
          f"{ind.get('tempo_etapa2', 0):.1f} s, {ind.get('etapa2')}")
    print(f"   {r.frase()} | caminho {ind.get('caminho')}")
    for _, f in fe.frases_por_nivel(r):
        print(f"   {f}")
    confere(bool(r.escala) and r.conformidade["ok"], "escala entregue, descanso ok")
    confere(ind.get("caminho") == "em sequência, 3 blocos", f"caminho {ind.get('caminho')}")
    w = fe.pesos_das_partes(_blocos([E], [I], [D]))
    # o que cabe no tempo maximo e o tempo GASTO (o limite de cada parte e calculado no inicio
    # dela, sobre o que resta; quem termina antes deixa a soma dos limites passar do maximo).
    # Folga de 15 s: com limites de poucos segundos o HiGHS passa do limite (medido em 22/10:
    # 6,1 s com limite de 1 s)
    gasto = sum(p["tempo"] for p in partes) + ind.get("tempo_etapa2", 0)
    confere(gasto <= orcamento + 15, f"tempo gasto nas partes {gasto:.1f} s <= {orcamento} s "
                                     f"(+ 15 s de folga)")
    for p in partes:
        confere(p["limite"] is None or p["limite"] <= orcamento,
                f"limite {p['limite']} s <= {orcamento} s")
    # sobra passa adiante: se as anteriores terminaram antes do limite, sem proteção, a parte k
    # recebe pelo menos a fatia do inicio (orcamento x peso)
    for k in range(1, len(partes)):
        if all(p["tempo"] < p["limite"] and "protecao" not in p for p in partes[:k]):
            confere(partes[k]["limite"] >= int(orcamento * w[k]) - 1,
                    f"parte {k}: limite {partes[k]['limite']} s >= fatia do inicio "
                    f"{orcamento * w[k]:.0f} s (sobra passou adiante)")
    return r, partes


def caso() -> int:
    rodada("(d1) caso pequeno (12x36, 1 + 2, pedidos no primeiro dia)",
           dataclasses.replace(_pequeno(), prioridades=_tres()), 60)
    r, partes = rodada("(d2) 40 (14 + 26) com 20 pedidos", dataclasses.replace(
        _quarenta(), prioridades=_tres()), 60)
    if partes and "protecao" in partes[0]:
        confere(bool(r.escala), "protecao da primeira escala: a fatia do Essencial acabou sem "
                                "escala, a resolucao seguiu com o resto e a escala saiu")
    else:
        print("   (a fatia do Essencial bastou para achar escala: a protecao nao disparou)")
    rodada("(d3) 40 (14 + 26) com 20 pedidos", dataclasses.replace(
        _quarenta(), prioridades=_tres()), 600)
    print("caso " + ("OK" if not falhas else f"com {falhas} FALHA(S)"))
    return 1 if falhas else 0


def _tres():
    return dict(fe.prioridades_padrao(), min_turnos=(fe.DESEJAVEL, 14))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--conta", action="store_true")
    ap.add_argument("--caso", action="store_true")
    a = ap.parse_args()
    sys.exit(conta() if a.conta else caso() if a.caso else 2)
