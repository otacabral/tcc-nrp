"""Caso de teste do Otavio de 09/10 (P15 e P14): 6 h + noturno de 12 h, fim de semana de sexta
a domingo, alta dependencia, 20 enfermeiros + 10 tecnicos, todos 44 h, inicio 12/10/2026.

    python docs\\diagnostico\\caso_otavio_0910.py rodar <saida.json>    # resolve e grava a escala
    python docs\\diagnostico\\caso_otavio_0910.py semanal <saida.json>  # descanso semanal por pessoa

`rodar` usa o caminho da tela (`ferramenta.verificar`) com os limites da tela. `semanal`
nao resolve nada: le a escala gravada e mostra, por pessoa e por semana, o maior descanso
continuo (a medida de `conferencia_descanso_escala.descanso_semanal`), marcando o que comeca
na borda inicial do horizonte (00:00 do primeiro dia), onde o periodo anterior e desconhecido.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "docs"))

import ferramenta as fe  # noqa: E402
import conferencia_descanso_escala as cd  # noqa: E402

TURNOS = [("M", 7, 13), ("T", 13, 19), ("N", 19, 7)]
DEMANDA = {"M": (2, 3), "T": (2, 3), "N": (3, 3)}
DEMANDA_FDS = {"M": (2, 4), "T": (2, 4), "N": (3, 3)}


def entrada() -> fe.Entrada:
    return fe.Entrada(turnos=TURNOS, grau="alta", n_enfermeiros=20, n_tecnicos=10,
                      demanda_turno=DEMANDA, demanda_fds=DEMANDA_FDS, fim_de_semana="sex_dom",
                      inicio=date(2026, 10, 12))


def rodar(saida: Path) -> None:
    t0 = time.time()
    r = fe.verificar(entrada(), progresso=lambda f, m: print(f"[{time.time() - t0:6.0f} s] {m}",
                                                            flush=True))
    ind = r.indicadores
    print(r.frase())
    print({k: ind.get(k) for k in ("enf_em_posto_tec", "fracao_min", "fracao_max", "gap",
                                    "provado", "etapa2", "penalidade")})
    print("descanso semanal minimo:", r.conformidade and r.conformidade["menor_semanal"])
    saida.write_text(json.dumps([(str(d), n, s) for d, n, s in r.escala]))


def semanal(arq: Path) -> None:
    inst = fe.montar(entrada())
    escala = [(date.fromisoformat(d), n, s) for d, n, s in json.loads(arq.read_text())]
    inicio = datetime.combine(inst.inicio, datetime.min.time())
    por = {}
    for d, n, s in escala:
        por.setdefault(n, []).append((d, s))
    abaixo = []
    for n, ts in sorted(por.items(), key=lambda x: int(x[0])):
        blocos = sorted(cd._inicio_fim(inst, d, s) for d, s in ts)
        semanas = cd.descanso_semanal(inst, blocos)
        menor = min(h for _, h in semanas)
        primeiro = blocos[0][0]
        borda = (primeiro - inicio).total_seconds() / 3600
        if menor < 35:
            abaixo.append(n)
        print(f"{inst.profissionais[n].nome:7s} semanas {[round(h, 1) for _, h in semanas]} "
              f"| menor {menor:.0f} h | descanso da borda inicial {borda:.0f} h"
              f"{'  <-- a menor semana pode ser a da borda' if abs(borda - menor) < 1e-6 else ''}")
    print(f"abaixo de 35 h: {len(abaixo)} profissionais")


if __name__ == "__main__":
    acao, arq = sys.argv[1], Path(sys.argv[2])
    rodar(arq) if acao == "rodar" else semanal(arq)
