"""A1b (08/10): a escala de 17 achada em K3/mais_pessoa (11 enf + 6 tec) vale para K4 (12 + 5)?

    python docs\\diagnostico\\k4_dominancia.py

K3/mais_pessoa NAO e a instancia do K4: o derivado acrescentou um TECNICO a K3 (11 + 5), e o
K4 tem um ENFERMEIRO a mais (12 + 5). Mesma demanda, mesmo modelo de turnos, mesmo inicio,
sem ferias, pedidos nem cargas: as duas equipes diferem so na pessoa "11", tecnico numa e
enfermeiro na outra. Enfermeiro cobre todo posto que tecnico cobre, com o mesmo contrato.
Logo toda escala de 11 + 6 deveria ser escala de 12 + 5.

ESPERADO, registrado antes de rodar (08/10):
1. a etapa 1 de K3/mais_pessoa, 600 s, acha escala de novo (em 08/10 achou, sem prova). Se
   NAO achar, a conferencia nao acontece e isso e dito — nao e defeito, e o solver;
2. a mesma escala, lida no K4 (mesmos ids), passa em `solucao.conferir_rigidas` com
   habilidade rigida, no descanso medido no relogio, no teto de horas, e nao tem atribuicao
   fora do dominio do modelo do K4;
3. o modelo da etapa 1 do K4 com as variaveis fixadas nessa escala da "optimal" em segundos.

Se 2 e 3 passarem: existe escala legal com 17 no K4, e "sem escala em 600 s / ~1.909 s" e
desempenho do solver (camada solver). Se 3 der "infeasible", ha restricao do modelo que
distingue as duas equipes alem da habilidade — defeito a investigar (camada modelo).
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(AQUI))

import bateria_desenho as bd  # noqa: E402
import bateria_propriedades as bp  # noqa: E402
import bateria_rodar as brd  # noqa: E402
import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import modelo  # noqa: E402
import solucao  # noqa: E402

SAIDA = RAIZ / "resultados" / "bateria_2026-10-08" / "k4_dominancia"


def caso(prefixo: str) -> bd.Caso:
    return next(c for c in bp.TODOS if c.nome.startswith(prefixo))


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    arq = SAIDA / "escala_k3_mais_pessoa.json"
    inst_a = fe.montar(bp.derivar(caso("K3"), "mais_pessoa"))
    print("K3/mais_pessoa:", fe._n_enf(inst_a), "enf +",
          len(inst_a.profissionais) - fe._n_enf(inst_a), "tec", flush=True)
    if arq.exists():
        escala = [(date.fromisoformat(d), n, s) for d, n, s in json.loads(arq.read_text())]
        print("escala lida de", arq.name)
    else:
        ip, custo, _ = fe.pesos(inst_a)
        m = ea.modelo_br(ip, custo)
        v, escala, provado, gap = fe.resolver(m, 600)
        print(f"etapa 1 de K3/mais_pessoa, 600 s: {v} | provado {provado} | gap {gap}",
              flush=True)
        if not escala:
            print("SEM ESCALA: a conferencia nao acontece (item 1 do esperado)")
            return 1
        arq.write_text(json.dumps([(str(d), n, s) for d, n, s in escala]))
    print("conferir_rigidas em K3/mais_pessoa:",
          solucao.conferir_rigidas(inst_a, escala, habilidade_rigida=True)[:3] or "ok")

    inst_b = fe.montar(brd.entrada(caso("K4")))
    print("K4:", fe._n_enf(inst_b), "enf +", len(inst_b.profissionais) - fe._n_enf(inst_b),
          "tec")
    diferentes = [n for n in inst_b.profissionais
                  if inst_a.profissionais[n].habilidades != inst_b.profissionais[n].habilidades
                  or inst_a.horas_devidas(n) != inst_b.horas_devidas(n)]
    print("pessoas que diferem entre as duas instancias:", diferentes)
    print("demanda identica:", inst_a.demanda == inst_b.demanda,
          "| turnos identicos:", inst_a.turnos == inst_b.turnos)
    print("conferir_rigidas no K4 (habilidade rigida):",
          solucao.conferir_rigidas(inst_b, escala, habilidade_rigida=True)[:3] or "ok")
    med = fe.medir(inst_b, escala)
    print("descanso no relogio:", "cumpre" if fe.cumpre(inst_b, med) else "NAO CUMPRE",
          {k: med[k] for k in ("menor_folga", "menor_semanal", "max_consec")})
    horas = {n: 0.0 for n in inst_b.profissionais}
    for _, n, s in escala:
        horas[n] += inst_b.turnos[s].duracao_h
    print("acima do teto:", [n for n, h in horas.items() if h > inst_b.horas_devidas(n) + 1e-6]
          or "ninguem")
    ip, custo, _ = fe.pesos(inst_b)
    m = ea.modelo_br(ip, custo)
    tem = {(n, s, d) for d, n, s in escala}
    print("fora do dominio do modelo do K4:", [t for t in tem if t not in m.X][:5] or "nenhuma")
    for (n, s, d) in m.X:
        m.x[n, s, d].fix(1 if (n, s, d) in tem else 0)
    res = modelo.resolver(m, solver=modelo.SOLVER_PADRAO, tempo_limite=120, carregar=False)
    print("modelo da etapa 1 do K4 com a escala fixada:", modelo.estado(res),
          "| tem solucao", modelo.tem_solucao(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
