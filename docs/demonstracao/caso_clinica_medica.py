"""Caso da demonstracao de uso (Capitulo 5): clinica medica, 12x36, novembro de 2026.

Os DADOS do caso moram aqui, num lugar so: este arquivo os entrega a `capturas.py`, que os
digita na tela, e a `dimensionar`, que confere sem a tela qual quadro admite escala legal.
Rodar da raiz, com a .venv ativa:

    python docs\\demonstracao\\caso_clinica_medica.py             # rodada 1 (o quadro do caso)
    python docs\\demonstracao\\caso_clinica_medica.py --tec 20    # mesma unidade, 20 tecnicos

Nomes ficticios. Feriados nacionais do periodo: 02/11 (Finados, segunda) e 15/11
(Proclamacao da Republica, domingo).
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import ferramenta as fe  # noqa: E402

INICIO = date(2026, 11, 2)
MODELO = next(k for k in fe.MODELOS if k.startswith("12"))
GRAU = "intermediario"

ENFERMEIROS = ["Ana Ribeiro", "Bruno Teixeira", "Carla Nunes", "Daniel Moura",
               "Elisa Campos", "Fábio Lacerda", "Gabriela Pires", "Heitor Sales"]
TECNICOS = ["Ingrid Alves", "João Barros", "Karen Dias", "Leonardo Faria", "Marta Gomes",
            "Nelson Hora", "Olívia Jardim", "Paulo Lima", "Quitéria Melo", "Rafael Neves",
            "Sandra Oliveira", "Tiago Prado", "Úrsula Queiroz", "Vítor Rocha",
            "Wanda Siqueira", "Xavier Torres", "Yara Uchoa", "Zeca Valente",
            "Alice Werneck", "Breno Xavier", "Cíntia Zanetti", "Diego Amaral"]

# carga contratual: quem nao aparece fica com 44 h (padrao da tela)
CARGAS_36 = ["Gabriela Pires", "Heitor Sales", "Wanda Siqueira", "Xavier Torres",
             "Yara Uchoa", "Zeca Valente", "Alice Werneck", "Breno Xavier"]

# demanda geral (dias uteis) e do fim de semana: (enfermeiros, tecnicos) por turno
DEMANDA = {"D": (2, 6), "N": (1, 5)}
DEMANDA_FDS = {"D": (1, 5), "N": (1, 4)}
# feriados: escala reduzida, igual a do domingo menos um tecnico de dia
FERIADOS = [date(2026, 11, 2), date(2026, 11, 15)]
DEMANDA_FERIADO = {"D": (1, 4), "N": (1, 4)}

FERIAS = [("Carla Nunes", date(2026, 11, 16), date(2026, 11, 29)),
          ("Karen Dias", date(2026, 11, 2), date(2026, 11, 15))]
PEDIDOS = [("Ana Ribeiro", date(2026, 11, 20)), ("João Barros", date(2026, 11, 7)),
           ("Marta Gomes", date(2026, 11, 24)), ("Rafael Neves", date(2026, 11, 13)),
           ("Tiago Prado", date(2026, 11, 28)), ("Daniel Moura", date(2026, 11, 10))]

# painel do COFEN: media diaria de pacientes por grau
PACIENTES = {"minimo": 8.0, "intermediario": 14.0, "alta": 4.0}


def demanda_data(modelo_turnos=MODELO) -> dict:
    """Demanda especifica dos feriados, no formato da tela: (data, turno, "enf"/"tec")."""
    saida = {}
    for d in FERIADOS:
        for turno, (enf, tec) in DEMANDA_FERIADO.items():
            saida[(d, turno, "enf")] = enf
            saida[(d, turno, "tec")] = tec
    return saida


def entrada(n_tec: int | None = None) -> fe.Entrada:
    tecnicos = TECNICOS if n_tec is None else TECNICOS[:n_tec]
    return fe.Entrada(
        turnos=fe.MODELOS[MODELO], grau=GRAU, n_enfermeiros=len(ENFERMEIROS),
        n_tecnicos=len(tecnicos), demanda_turno=DEMANDA, demanda_fds=DEMANDA_FDS,
        demanda_data=demanda_data(), inicio=INICIO, nomes_enfermeiros=ENFERMEIROS,
        nomes_tecnicos=tecnicos,
        indisponibilidades=[f for f in FERIAS if f[0] in ENFERMEIROS + tecnicos],
        pedidos=[p for p in PEDIDOS if p[0] in ENFERMEIROS + tecnicos],
        pacientes=PACIENTES, cargas={n: 36 for n in CARGAS_36 if n in tecnicos + ENFERMEIROS})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tec", type=int, help="quantos tecnicos (os primeiros da lista)")
    a = ap.parse_args()
    e = entrada(a.tec)
    print(f"{e.n_enfermeiros} enfermeiros + {e.n_tecnicos} tecnicos = {e.quadro}; piso "
          f"{fe.piso(fe.montar(e))}", flush=True)
    r = fe.verificar(e)
    print(r.frase())
    print("tentativas", r.tentativas)
    print("diagnostico", r.diagnostico)
    print("alertas", r.alertas)
    if r.escala:
        ind = r.indicadores
        print({k: ind.get(k) for k in ("enf_em_posto_tec", "pedidos_atendidos",
                                        "pedidos_total", "fracao_min", "fracao_max",
                                        "etapa2", "tempo_etapa1", "tempo_etapa2", "gap")})
        for g, c in ind["categorias"].items():
            print(g, fe.fmt_diferenca(c), f"nao utilizadas {c['nao_utilizadas']:.0f} h")
        print("descanso", r.conformidade["ok"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
