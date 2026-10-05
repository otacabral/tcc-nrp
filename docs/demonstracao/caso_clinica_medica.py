"""Caso da demonstracao de uso (Capitulo 5): clinica medica, 12x36, novembro de 2026.

Os DADOS do caso moram aqui, num lugar so: este arquivo os entrega a `capturas.py`, que os
digita na tela, e a `dimensionar`, que confere sem a tela qual quadro admite escala legal.
Rodar da raiz, com a .venv ativa:

    python docs\\demonstracao\\caso_clinica_medica.py             # rodada 1 (o quadro do caso)
    python docs\\demonstracao\\caso_clinica_medica.py --tec 20    # mesma unidade, 20 tecnicos

Nomes ficticios.

Como a demanda dos dias especiais foi lancada (declarado em 05/10):

- 02/11 (Finados, segunda-feira, PRIMEIRO dia do horizonte): lancado como feriado, com a
  demanda reduzida DEMANDA_FERIADO (1 enfermeiro + 4 tecnicos em cada turno), no lugar da
  de dia util (2 + 6 de dia, 1 + 5 a noite).
- 15/11 (Proclamacao da Republica, domingo): lancado como feriado, DEMANDA_FERIADO. Como cai
  no fim de semana, so muda o turno do dia: 1 + 4 no lugar de 1 + 5; a noite ja era 1 + 4.
- 20/11 (sexta-feira, Dia Nacional de Zumbi e da Consciencia Negra, feriado nacional desde
  2024, Lei 14.759/2023): lancado como feriado, como o 02/11, a partir de 05/10 (decisao do
  Otavio). Ate o relatorio 05e entrou como dia util (2 + 6 / 1 + 5) — escolha do roteiro; a
  ferramenta nao tem lista de feriados, feriado e demanda especifica por data.
- O primeiro dia (02/11) nao tem continuidade com o periodo anterior: a ferramenta gera cada
  escala de 28 dias isolada, e o descanso na virada de outubro para novembro nao e conferido
  (PROPOSTAS.md, P3, trabalho futuro "continuidade entre periodos").
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

# Equipe da rodada 1 (decisao do Otavio, 05/10): 10 enfermeiros + 20 tecnicos = 30, a
# proporcao 33/67 do Parecer no grau intermediario. Ate 05/10 (relatorios 05d e 05e) eram
# 8 + 22: Icaro Mendes e Julia Freitas entraram; Cintia Zanetti e Diego Amaral (44 h) sairam.
ENFERMEIROS = ["Ana Ribeiro", "Bruno Teixeira", "Carla Nunes", "Daniel Moura",
               "Elisa Campos", "Fábio Lacerda", "Gabriela Pires", "Heitor Sales",
               "Ícaro Mendes", "Júlia Freitas"]
TECNICOS = ["Ingrid Alves", "João Barros", "Karen Dias", "Leonardo Faria", "Marta Gomes",
            "Nelson Hora", "Olívia Jardim", "Paulo Lima", "Quitéria Melo", "Rafael Neves",
            "Sandra Oliveira", "Tiago Prado", "Úrsula Queiroz", "Vítor Rocha",
            "Wanda Siqueira", "Xavier Torres", "Yara Uchoa", "Zeca Valente",
            "Alice Werneck", "Breno Xavier"]

# carga contratual: quem nao aparece fica com 44 h (padrao da tela)
CARGAS_36 = ["Gabriela Pires", "Heitor Sales", "Wanda Siqueira", "Xavier Torres",
             "Yara Uchoa", "Zeca Valente", "Alice Werneck", "Breno Xavier"]

# demanda geral (dias uteis) e do fim de semana: (enfermeiros, tecnicos) por turno
DEMANDA = {"D": (2, 6), "N": (1, 5)}
DEMANDA_FDS = {"D": (1, 5), "N": (1, 4)}
# feriados: escala reduzida, igual a do domingo menos um tecnico de dia
FERIADOS = [date(2026, 11, 2), date(2026, 11, 15), date(2026, 11, 20)]
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
