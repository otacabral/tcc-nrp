"""Desenho da bateria de entradas (parte C, 07/10): monta os casos, confere a cobertura de
pares de areas editaveis e calcula o ESPERADO PELA CONTA de cada um. Nao resolve nada.

    python docs\\diagnostico\\bateria_desenho.py

A conta e INDEPENDENTE da ferramenta (nao usa `ferramenta.piso` nem `motivos_da_trava`, para
nao conferir a ferramenta com a propria premissa — CLAUDE.md). So condicoes NECESSARIAS:

1. horas: demanda do periodo <= soma de (carga x dias disponiveis / 7) de todos; e o mesmo so
   para os postos de enfermeiro contra os enfermeiros;
2. ocupados por dia: o descanso entre turnos e medido dos HORARIOS (36 h depois de turno de
   12 h ou mais, 11 h nos demais; CLT). Se um turno s proibe TODOS os turnos do dia seguinte,
   quem fez s em d - 1 nao trabalha em d. Entao, em cada dia d:
   postos(d) + postos dos turnos "que bloqueiam o dia seguinte" em d - 1
       <= pessoas disponiveis em d - 1 ou em d.
   O mesmo so para enfermeiros e postos de enfermeiro.

Veredito esperado: "INVIAVEL pela conta" se alguma falha; "FRONTEIRA" se a menor folga e 0;
"GERA ESCALA (esperado)" caso contrario — a conta e so necessaria, entao "gera escala" e
expectativa, nao prova: um "sem escala" ai e o que a bateria quer achar.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from datetime import date, timedelta

DIAS = 28
INICIO_PADRAO = date(2026, 10, 12)

MODELOS = {
    "12x36": [("D", 7, 19), ("N", 19, 7)],
    "8h": [("M", 7, 15), ("T", 15, 23), ("N", 23, 7)],
    "6+12": [("M", 7, 13), ("T", 13, 19), ("N", 19, 7)],
}

AREAS = ["modelo", "horarios", "fds_def", "inicio", "composicao", "nomes", "cargas", "ferias",
         "pedidos", "demanda", "fds_propria", "grade_data", "pacientes", "grau"]


@dataclass
class Caso:
    nome: str
    areas: set
    modelo: str = "12x36"
    turnos: list | None = None          # horarios editados; None = os do modelo
    fds: str = "sab_dom"
    inicio: date = INICIO_PADRAO
    n_enf: int = 4
    n_tec: int = 8
    cargas: dict = field(default_factory=dict)     # indice da pessoa -> horas
    ferias: list = field(default_factory=list)     # (indice, dia ini, dia fim) relativos
    pedidos: int = 0
    demanda: dict | None = None         # turno -> (enf, tec)
    demanda_fds: dict | None = None
    grade: dict = field(default_factory=dict)      # (dia relativo, turno) -> (enf, tec)
    pacientes: dict | None = None
    grau: str = "intermediario"


def dur(ini, fim):
    return (fim - ini) % 24 or 24


def bloqueia_dia_seguinte(turnos):
    """Turnos s tais que, feitos em d - 1, impedem qualquer turno em d (medido no relogio)."""
    saida = set()
    for s, ini_s, fim_s in turnos:
        d_s = dur(ini_s, fim_s)
        exige = 36 if d_s >= 12 else 11
        fim_abs = ini_s + d_s                       # horas a partir de 00:00 de d - 1
        if all((24 + ini_t) - fim_abs < exige for _, ini_t, _ in turnos):
            saida.add(s)
    return saida


def conta(c: Caso):
    turnos = c.turnos or MODELOS[c.modelo]
    duracoes = {s: dur(i, f) for s, i, f in turnos}
    fds_dias = {5, 6} if c.fds == "sab_dom" else {4, 5, 6}
    dias = [c.inicio + timedelta(days=k) for k in range(DIAS)]
    padrao = c.demanda or {s: (1, 2) for s, _, _ in turnos}

    def dem(k, s):
        if (k, s) in c.grade:
            return c.grade[(k, s)]
        if c.demanda_fds and dias[k].weekday() in fds_dias:
            return c.demanda_fds.get(s, padrao[s])
        return padrao[s]

    n = c.n_enf + c.n_tec
    enf = set(range(c.n_enf))
    fora = {i: set() for i in range(n)}
    for i, a, b in c.ferias:
        fora[i] |= set(range(a, b + 1))
    disp = {i: DIAS - len(fora[i]) for i in range(n)}
    carga = {i: c.cargas.get(i, 44) for i in range(n)}
    teto = {i: carga[i] * disp[i] / 7 for i in range(n)}

    h_tot = sum(sum(dem(k, s)) * duracoes[s] for k in range(DIAS) for s in duracoes)
    h_enf = sum(dem(k, s)[0] * duracoes[s] for k in range(DIAS) for s in duracoes)
    folgas = {"horas": sum(teto.values()) - h_tot,
              "horas_enf": sum(teto[i] for i in enf) - h_enf}
    bloq = bloqueia_dia_seguinte(turnos)
    pior, pior_enf = None, None
    for k in range(DIAS):
        anterior = k - 1
        ocup = sum(sum(dem(k, s)) for s in duracoes)
        ocup_enf = sum(dem(k, s)[0] for s in duracoes)
        if anterior >= 0:
            ocup += sum(sum(dem(anterior, s)) for s in bloq)
            ocup_enf += sum(dem(anterior, s)[0] for s in bloq)
        pessoas = sum(1 for i in range(n) if k not in fora[i] or
                      (anterior >= 0 and anterior not in fora[i]))
        pessoas_enf = sum(1 for i in enf if k not in fora[i] or
                          (anterior >= 0 and anterior not in fora[i]))
        f, fe_ = pessoas - ocup, pessoas_enf - ocup_enf
        pior = f if pior is None else min(pior, f)
        pior_enf = fe_ if pior_enf is None else min(pior_enf, fe_)
    folgas["ocupados_dia"] = pior
    folgas["ocupados_dia_enf"] = pior_enf
    menor = min(folgas.values())
    veredito = ("INVIAVEL pela conta" if menor < 0 else
                "FRONTEIRA" if menor == 0 else "GERA ESCALA (esperado)")
    return veredito, folgas, sorted(bloq)


SEG = INICIO_PADRAO
CASOS = [
    Caso("P01", {"modelo", "horarios", "fds_def", "inicio", "composicao", "nomes"},
         modelo="8h", turnos=[("M", 6, 14), ("T", 14, 22), ("N", 22, 6)], fds="sex_dom",
         inicio=date(2026, 11, 30), n_enf=5, n_tec=9),
    Caso("P02", {"modelo", "cargas", "ferias", "pedidos", "demanda", "fds_propria"},
         modelo="6+12", n_enf=6, n_tec=6, cargas={0: 36, 6: 30, 7: 30}, ferias=[(1, 0, 6)],
         pedidos=4, demanda={"M": (1, 1), "T": (1, 1), "N": (1, 1)},
         demanda_fds={"M": (1, 0), "T": (1, 0)}),
    Caso("P03", {"modelo", "grade_data", "pacientes", "grau", "horarios", "cargas"},
         modelo="12x36", turnos=[("D", 8, 20), ("N", 20, 8)], n_enf=5, n_tec=10,
         cargas={3: 40, 10: 36}, grade={(2, "D"): (1, 2)}, pacientes={"minimo": 6, "alta": 3},
         grau="alta"),
    Caso("P04", {"fds_def", "composicao", "ferias", "grade_data", "grau", "pedidos"},
         modelo="8h", fds="sex_dom", n_enf=8, n_tec=6, ferias=[(9, 10, 20)], pedidos=6,
         grade={(4, "N"): (1, 1)}, grau="semi_intensivo"),
    Caso("P05", {"inicio", "cargas", "demanda", "pacientes", "nomes", "ferias"},
         modelo="12x36", inicio=date(2027, 1, 4), n_enf=4, n_tec=10, cargas={5: 30},
         demanda={"D": (1, 3), "N": (1, 2)}, ferias=[(0, 20, 27)],
         pacientes={"intermediario": 10}),
    Caso("P06", {"horarios", "pedidos", "fds_propria", "grau", "inicio", "composicao"},
         modelo="6+12", turnos=[("M", 6, 12), ("T", 12, 18), ("N", 18, 6)],
         inicio=date(2026, 12, 28), n_enf=10, n_tec=4, pedidos=3,
         demanda={"M": (1, 1), "T": (1, 1), "N": (2, 1)}, demanda_fds={"M": (1, 0)},
         grau="minimo"),
    Caso("P07", {"nomes", "grade_data", "fds_propria", "modelo", "pacientes", "ferias"},
         modelo="8h", n_enf=5, n_tec=8, ferias=[(5, 0, 13)], demanda_fds={"N": (1, 1)},
         grade={(0, "M"): (1, 1), (14, "T"): (1, 1)}, pacientes={"minimo": 4, "intermediario": 6}),
    Caso("P08", {"composicao", "cargas", "pacientes", "fds_def", "demanda", "grade_data"},
         modelo="12x36", fds="sex_dom", n_enf=8, n_tec=4, cargas={0: 36, 1: 36},
         demanda={"D": (1, 1), "N": (1, 1)}, grade={(6, "N"): (2, 1)},
         pacientes={"semi_intensivo": 4}),
    Caso("P09", {"ferias", "grau", "horarios", "demanda", "inicio", "nomes"},
         modelo="8h", turnos=[("M", 7, 15), ("T", 15, 23), ("N", 23, 7)],
         inicio=date(2026, 10, 26), n_enf=6, n_tec=9, ferias=[(7, 3, 9), (8, 3, 9)],
         demanda={"M": (1, 2), "T": (1, 2), "N": (1, 1)}, grau="alta"),
    Caso("P10", {"pedidos", "pacientes", "composicao", "horarios", "ferias", "fds_def"},
         modelo="6+12", turnos=[("M", 7, 13), ("T", 13, 19), ("N", 19, 7)], fds="sex_dom",
         n_enf=12, n_tec=4, pedidos=5, ferias=[(13, 0, 6)],
         demanda={"M": (1, 1), "T": (1, 1), "N": (2, 1)}, pacientes={"intermediario": 8}),
    Caso("P11", {"fds_propria", "cargas", "nomes", "grau", "fds_def", "grade_data"},
         modelo="12x36", fds="sex_dom", n_enf=4, n_tec=9, cargas={4: 40, 5: 40},
         demanda_fds={"D": (1, 2), "N": (1, 2)}, grade={(20, "D"): (1, 4)}, grau="intensivo"),
    Caso("P12", {"demanda", "inicio", "pedidos", "grade_data", "composicao", "modelo"},
         modelo="8h", inicio=date(2026, 11, 2), n_enf=7, n_tec=6, pedidos=7,
         demanda={"M": (1, 1), "T": (1, 1), "N": (1, 1)}, grade={(0, "M"): (1, 0)}),
    Caso("P13", {"pacientes", "inicio", "fds_propria", "horarios", "ferias", "cargas"},
         modelo="12x36", turnos=[("D", 6, 18), ("N", 18, 6)], inicio=date(2026, 12, 21),
         n_enf=5, n_tec=9, cargas={2: 36}, ferias=[(6, 0, 13)],
         demanda_fds={"D": (1, 2)}, pacientes={"minimo": 5, "intermediario": 5}),
    Caso("P14", {"grau", "demanda", "nomes", "cargas", "composicao", "pedidos"},
         modelo="6+12", n_enf=11, n_tec=5, cargas={0: 30, 15: 36}, pedidos=2,
         demanda={"M": (1, 1), "T": (1, 1), "N": (2, 1)}, grau="semi_intensivo"),
    Caso("P15", {"modelo", "fds_def", "pedidos", "pacientes", "demanda", "inicio"},
         modelo="6+12", fds="sex_dom", inicio=date(2027, 2, 1), n_enf=10, n_tec=5, pedidos=4,
         demanda={"M": (2, 0), "T": (1, 1), "N": (2, 1)}, pacientes={"alta": 2, "minimo": 6}),
    Caso("P16", {"horarios", "grau", "fds_propria", "composicao", "ferias", "nomes", "pedidos"},
         modelo="8h", turnos=[("M", 6, 14), ("T", 14, 22), ("N", 22, 6)], n_enf=9, n_tec=7,
         ferias=[(2, 21, 27)], pedidos=3, demanda_fds={"M": (1, 1), "T": (1, 1)},
         grau="minimo"),
    Caso("P17", {"cargas", "fds_def", "grade_data", "inicio", "pacientes", "modelo", "demanda"},
         modelo="12x36", fds="sex_dom", inicio=date(2026, 11, 9), n_enf=5, n_tec=10,
         cargas={9: 36, 10: 36}, demanda={"D": (1, 3), "N": (1, 2)},
         grade={(11, "D"): (1, 2)}, pacientes={"intermediario": 12}),
    Caso("P18", {"nomes", "grade_data", "demanda", "ferias", "horarios", "grau", "fds_propria"},
         modelo="6+12", turnos=[("M", 6, 12), ("T", 12, 18), ("N", 18, 6)], n_enf=12, n_tec=5,
         ferias=[(12, 7, 13)], demanda={"M": (1, 1), "T": (1, 1), "N": (2, 1)},
         demanda_fds={"N": (2, 1)}, grade={(10, "N"): (3, 1)}, grau="alta"),
]


def caso_A(n_enf, nome):
    return Caso(nome, {"modelo", "composicao", "demanda"}, modelo="6+12", n_enf=n_enf, n_tec=5,
                demanda={"M": (2, 1), "T": (2, 1), "N": (3, 2)})


CONHECIDOS = [
    Caso("K1 folga clara", {"modelo"}, modelo="8h", n_enf=6, n_tec=10,
         demanda={"M": (1, 1), "T": (1, 1), "N": (1, 1)}),
    Caso("K2 inviavel pela conta", {"modelo"}, modelo="12x36", n_enf=3, n_tec=6,
         demanda={"D": (1, 3), "N": (1, 3)}),
    caso_A(11, "K3 parte A com 16 (11+5): fronteira"),
    caso_A(12, "K4 parte A com 17 (12+5)"),
    caso_A(13, "K5 parte A com 18 (13+5)"),
    caso_A(15, "K6 parte A com 20 (15+5): o caso do Otavio"),
]


def main() -> int:
    pares = {frozenset(p) for p in itertools.combinations(AREAS, 2)}
    cobertos = {frozenset(p) for c in CASOS for p in itertools.combinations(sorted(c.areas), 2)}
    faltam = sorted(tuple(sorted(p)) for p in pares - cobertos)
    print(f"pares de areas: {len(pares)}; cobertos: {len(pares & cobertos)}; faltam: {faltam}")
    print("\n| Caso | Áreas editadas | Modelo | Equipe | Esperado pela conta | Folgas (h, h enf, ocupados/dia, ocupados/dia enf) |")
    print("|---|---|---|---|---|---|")
    for c in CASOS + CONHECIDOS:
        v, f, bloq = conta(c)
        print(f"| {c.nome} | {', '.join(sorted(c.areas))} | {c.modelo} | {c.n_enf}+{c.n_tec} | "
              f"{v} | {f['horas']:.0f}; {f['horas_enf']:.0f}; {f['ocupados_dia']}; "
              f"{f['ocupados_dia_enf']} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
