"""Caso A pela pratica (Orientacao, 23/10): recontagem independente da escala real e as rodadas.

    python docs\\diagnostico\\caso_a_pratica.py --recontar     # sem solver: a escala real
    (as rodadas e a conferencia vem depois, no mesmo arquivo)

Recontagem (DECISOES.md, "2026-10-23 — Caso A: classificacao dos criterios pela escala real e
sensibilidade (2 ordens)"): le `D:\\TCC\\escrita\\fontes\\transcricao_anexoB_massens.csv` com as
leituras da ficha (FICHA_CASO_REALISTA.md, "Contagem na escala real (23/10/2026)") e conta cada
criterio com o `avaliacao.py` — NAO usa o script do chat de Orientacao.

Leituras: linhas diurnas, dia util em branco = trabalho no turno da linha (inclusive 02/11 e
15/11); fim de semana em branco = nao trabalha; P = plantao de 12 h (D12 de dia, N de noite);
F, F2, f2 = folga; FERIAS = ferias. Linhas noturnas: em branco = folga. Ferias e sequencias que
tocam a borda do mes ou as ferias ficam fora: as sequencias (dias, folgas, fins de semana
seguidos) sao contadas so nos blocos inteiros, recortando a janela do inicio do 2o bloco ao fim
do penultimo; o total de turnos, so em quem nao teve ferias; o resto, nos dias fora das ferias.
Calendario: a transcricao nao marca o fim de semana; os P das linhas diurnas so fecham com 27/10
num sabado (2018: 02/11 sexta e 15/11 quinta, as duas colunas sombreadas fora do fim de semana) —
o script confere isso antes de contar.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from datetime import date, time, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "docs"), str(AQUI)]

from avaliacao import violacoes  # noqa: E402
from instancia import Contrato, Flexivel, Instancia, Profissional, Turno  # noqa: E402
from solucao import noites_antes_de_fim_de_semana_livre_por_pessoa  # noqa: E402

CSV = Path(r"D:\TCC\escrita\fontes\transcricao_anexoB_massens.csv")
SAIDA = RAIZ / "resultados" / "caso_a_pratica_2026-10-23"
ANO = 2018
FOLGA = {"F", "F2", "f2"}
# limites padrao da ferramenta (prioridades.CRITERIOS), nao calibrados
LIMITES = {"max_consecutive_working_days": 5, "min_consecutive_working_days": 3,
           "max_consecutive_free_days": 4, "min_consecutive_free_days": 3,
           "max_consecutive_working_weekends": 3, "min_consecutive_working_weekends": 2,
           "max_working_weekends_in_four_weeks": 2, "max_num_assignments": 18,
           "min_num_assignments": 10}
BOOLEANOS = ("complete_weekends", "identical_shift_types_during_weekend",
             "two_free_days_after_night_shifts")
# criterio da ferramenta -> familia do avaliacao.py; classificacao da ficha (lado esperado)
FICHA = [("Máx. dias seguidos, preferência (5)", "max_consecutive_working_days", "violado"),
         ("Mín. dias seguidos (3)", "min_consecutive_working_days", "violado"),
         ("Máx. folgas seguidas (4)", "max_consecutive_free_days", "nunca"),
         ("Mín. folgas seguidas (3)", "min_consecutive_free_days", "violado"),
         ("Máx. fins de semana seguidos (3)", "max_consecutive_working_weekends", "violado"),
         ("Mín. fins de semana seguidos (2)", "min_consecutive_working_weekends", "nunca"),
         ("Fins de semana em 4 semanas (2)", "max_working_weekends_in_four_weeks", "violado"),
         ("Fim de semana completo", "complete_weekends", "violado"),
         # ficha corrigida pela Orientacao (23/10): pela semantica do avaliador, um dia so do fim de
         # semana viola (era "sem ocorrencia")
         ("Mesmo turno no fim de semana", "identical_shift_types_during_weekend", "violado"),
         ("Máx. turnos, preferência (18)", "max_num_assignments", "violado"),
         ("Mín. turnos (10)", "min_num_assignments", "nunca"),
         ("Noturno na véspera de fim de semana livre", "noturno_antes_fds", "violado"),
         ("Duas folgas depois de noites", "two_free_days_after_night_shifts", "violado")]
# Leitura C da borda (Orientacao, 23/10, a posteriori; DECISOES.md, "2026-10-23 — Caso A"): o bloco
# que toca a borda do mes CONTA nos criterios de maximo (se ja passa do limite dentro do mes, a
# violacao e certa) e SAI nos de minimo (pode continuar fora da imagem); o bloco que toca as
# FERIAS sai sempre (o fim das ferias nao se le na imagem)
SEQ_DIAS = {"max": ("max_consecutive_working_days", "max_consecutive_free_days"),
            "min": ("min_consecutive_working_days", "min_consecutive_free_days")}
SEQ_FDS = {"max": ("max_consecutive_working_weekends",),
           "min": ("min_consecutive_working_weekends",)}
TOTAIS = ("max_num_assignments", "min_num_assignments")


HISTORICO = """## Histórico: as três leituras da borda (23/10)

A primeira recontagem usou a regra então escrita na ficha (leitura A: tirar todo bloco que toca a
borda do mês ou as férias) e pôs o máx. fins de semana seguidos do outro lado da ficha, porque os
diurnos trabalham os 5 fins de semana do mês (um bloco que toca as duas bordas). A Orientação
decidiu pela leitura C (DECISOES.md, "2026-10-23 — Caso A", a posteriori), com motivo independente
do resultado: na borda do mês, nos critérios de máximo, o bloco conta (se já passa do limite dentro
do mês, a violação é certa) e, nos de mínimo, sai (pode continuar fora da imagem); o bloco que toca
as férias sai sempre (o fim das férias não se lê na imagem — o que descarta a B).

| Leitura | Máx. fins de semana seguidos | Máx. folgas seguidas | Reproduz a ficha? |
|---|---|---|---|
| A — tirar todo bloco que toca a borda ou as férias | nunca | nunca | não (máx. fins de semana) |
| B — nos de máximo, contar os blocos de borda e também os que tocam as férias; nos de mínimo, tirar | violado (26, em 14 pessoas) | violado (1: o 5976, 5 dias sem trabalho de 21 a 25/11, logo depois das férias de 15 a 20/11) | não (máx. folgas) |
| C — nos de máximo, contar o bloco de borda do mês; nos de mínimo, tirar; o que toca as férias, sempre tirar | violado | nunca | sim |

"Mesmo turno no fim de semana": pela semântica do `avaliacao.py`/avaliador oficial, quem trabalha um
só dia do fim de semana viola; a ficha (que dizia "sem ocorrência") foi corrigida pela Orientação;
a classificação continua Não considerar, agora por evidência."""


def _turnos():
    def t(i, a, b):
        return Turno(id=i, inicio=time(a), fim=time(b), descricao=i, habilidades=frozenset())
    return {"M": t("M", 7, 13), "T": t("T", 13, 19), "I": t("I", 6, 18),
            "D12": t("D12", 7, 19), "N": t("N", 19, 7)}


def _contrato():
    f = {k: Flexivel(True, True, 1, v) for k, v in LIMITES.items()}
    f.update({k: Flexivel(True, True, 1, None) for k in BOOLEANOS})
    ausente = Flexivel.ausente()
    return Contrato(id="0", descricao="caso A, limites padrao da ferramenta",
                    weekend_definition="SaturdaySunday", padroes_indesejados=(),
                    single_assignment_per_day=ausente, alternative_skill_category=ausente,
                    no_night_shift_before_free_weekend=Flexivel(True, True, 1, None), **f)


def ler():
    """(pessoas, dias, escala {(n, d): turno}, ferias {(n, d)}, grupo {n})."""
    with open(CSV, encoding="utf-8") as arq:
        linhas = list(csv.reader(arq))
    cab = linhas[0]
    dias = [date(ANO, int(c.split("/")[1]), int(c.split("/")[0])) for c in cab[3:]]
    escala, ferias, grupo, pessoas = {}, set(), {}, []
    erros = []
    for linha in linhas[1:]:
        n, horario, g = linha[0], linha[1], linha[2]
        pessoas.append(n)
        grupo[n] = g
        diurno = g == "dia"
        turno_linha = ("T" if horario.startswith("12:50") else
                       "I" if horario.startswith("06:00") else "M")
        for d, c in zip(dias, linha[3:]):
            c = c.strip()
            fds = d.weekday() >= 5
            if c == "FERIAS":
                ferias.add((n, d))
            elif c in FOLGA:
                continue
            elif c == "P":
                if diurno and not fds:
                    erros.append(f"{n} {d}: P de dia fora do fim de semana")
                escala[(n, d)] = "D12" if diurno else "N"
            elif c == "":
                if diurno and not fds:
                    escala[(n, d)] = turno_linha
            else:
                erros.append(f"{n} {d}: celula desconhecida {c!r}")
    return pessoas, dias, escala, ferias, grupo, erros


def _inst(pessoas, ini, fim):
    return Instancia(id="caso_a_real", arquivo=str(CSV), inicio=ini, fim=fim, habilidades=(),
                     turnos=_turnos(), padroes={}, contratos={"0": _contrato()},
                     profissionais={n: Profissional(n, n, "0", frozenset()) for n in pessoas},
                     demanda={}, pedidos=())


def _segmentos(dias, fora):
    """Trechos maximos de dias consecutivos fora das ferias."""
    segs, atual = [], []
    for d in dias:
        if d in fora:
            if atual:
                segs.append(atual)
            atual = []
        else:
            atual.append(d)
    if atual:
        segs.append(atual)
    return segs


def _blocos(marcas):
    blocos, ini = [], 0
    for i in range(1, len(marcas) + 1):
        if i == len(marcas) or marcas[i] != marcas[ini]:
            blocos.append((ini, i - 1))
            ini = i
    return blocos


def _janela(blocos, modo: str, ini_ferias: bool, fim_ferias: bool):
    """Indices (primeiro, ultimo) dos blocos contados na leitura C: o da ponta sai se a ponta e
    ferias (sempre) ou se o criterio e de minimo (borda do mes tambem); None se nao sobra bloco."""
    i = 1 if (ini_ferias or modo == "min") else 0
    j = len(blocos) - (2 if (fim_ferias or modo == "min") else 1)
    return (i, j) if i <= j else None


def _conta(inst, escala_seg, familias):
    """Violacoes do avaliacao.py (e do contador da ferramenta, no noturno) so das `familias`."""
    esc = [(d, n, s) for (n, d), s in escala_seg.items()]
    c = Counter()
    for v in violacoes(inst, esc):
        if v.restricao in familias:
            c[(v.restricao, v.profissional)] += v.excesso
    if "noturno_antes_fds" in familias:
        for n, k in noites_antes_de_fim_de_semana_livre_por_pessoa(inst, esc).items():
            c[("noturno_antes_fds", n)] += k
    return c


def recontar() -> int:
    pessoas, dias, escala, ferias, grupo, erros = ler()
    if erros:
        print("PARADO: leitura da transcricao nao fecha com o calendario:", *erros[:10], sep="\n  ")
        return 1
    total = Counter()                 # (familia, pessoa) -> excesso
    ocorrencias = Counter()           # familia -> pessoas com ocorrencia possivel
    for n in pessoas:
        fora = {d for (m, d) in ferias if m == n}
        for seg in _segmentos(dias, fora):
            esc_seg = {(n, d): s for (m, d), s in escala.items() if m == n and d in seg}
            # as pontas do trecho: borda do mes ou ferias
            ini_ferias, fim_ferias = seg[0] != dias[0], seg[-1] != dias[-1]
            # sequencias de dias/folgas, pela leitura C
            marcas = [(n, d) in esc_seg for d in seg]
            b = _blocos(marcas)
            for modo, familias in SEQ_DIAS.items():
                ij = _janela(b, modo, ini_ferias, fim_ferias)
                if ij:
                    ini, fim = seg[b[ij[0]][0]], seg[b[ij[1]][1]]
                    janela = {k: v for k, v in esc_seg.items() if ini <= k[1] <= fim}
                    total.update(_conta(_inst([n], ini, fim), janela, familias))
            # fins de semana seguidos, pela leitura C (blocos de fins de semana inteiros)
            inst_seg = _inst([n], seg[0], seg[-1])
            fdss = [f for f in inst_seg.fins_de_semana("0") if f.completo]
            trab = [any((n, d) in esc_seg for d in f.datas) for f in fdss]
            if any(trab):
                ocorrencias["fds_trabalhado"] += 1
            bf = _blocos(trab) if trab else []
            for modo, familias in SEQ_FDS.items():
                ij = _janela(bf, modo, ini_ferias, fim_ferias) if bf else None
                if ij:
                    ini, fim = fdss[bf[ij[0]][0]].datas[0], fdss[bf[ij[1]][1]].datas[-1]
                    janela = {k: v for k, v in esc_seg.items() if ini <= k[1] <= fim}
                    total.update(_conta(_inst([n], ini, fim), janela, familias))
            # o resto, no trecho fora das ferias (fins de semana inteiros, noites, 4 semanas)
            resto = ("max_working_weekends_in_four_weeks", "complete_weekends",
                     "identical_shift_types_during_weekend", "two_free_days_after_night_shifts",
                     "noturno_antes_fds")
            total.update(_conta(inst_seg, esc_seg, resto))
            if any(sum((n, d) in esc_seg for d in f.datas) == 2 for f in fdss):
                ocorrencias["fds_dois_dias"] += 1
        # totais de turnos: so quem nao teve ferias
        if not fora:
            esc_n = {k: v for k, v in escala.items() if k[0] == n}
            total.update(_conta(_inst([n], dias[0], dias[-1]), esc_n, TOTAIS))
    linhas = ["| Critério (limite padrão) | Na recontagem (avaliacao.py) | Pessoas com violação | "
              "Ficha (Orientação) | Mesmo lado? |", "|---|---|---:|---|---|"]
    mudou = []
    for rotulo, fam, ficha in FICHA:
        por = {n: v for (f, n), v in total.items() if f == fam and v > 0}
        lado = "violado" if por else "nunca"
        igual = lado == ficha
        if not igual:
            mudou.append(rotulo)
        grupos = Counter(grupo[n] for n in por)
        linhas.append(f"| {rotulo} | {lado}: {sum(por.values())} violação(ões) | {len(por)} "
                      f"({', '.join(f'{g} {k}' for g, k in sorted(grupos.items())) or '—'}) | "
                      f"{ficha} | {'sim' if igual else '**NÃO**'} |")
    texto = ["# Caso A — recontagem independente da escala real (23/10/2026)", "",
             f"Fonte: `{CSV}` (24 linhas, 26/10 a 25/11/{ANO}); leituras da ficha (corrigida pela "
             "Orientação em 23/10); contagem pelo `avaliacao.py` (noturno na véspera: contador da "
             "ferramenta, que o avaliacao.py não pontua). Borda e férias pela **leitura C** "
             "(Orientação, 23/10, a posteriori): bloco que toca a borda do mês conta nos critérios "
             "de máximo e sai nos de mínimo; bloco que toca as férias sai sempre. Totais de turnos "
             "só sem férias. Calendário conferido: todo P das linhas diurnas cai em sábado ou "
             "domingo (27/10/2018 é sábado).", "", *linhas, "",
             (f"**Os {len(FICHA)} critérios contáveis ficam do mesmo lado da ficha.**" if not mudou
              else "**PARAR: mudaram de lado: " + "; ".join(mudou) + "** (levar à Orientação)."),
             "", HISTORICO]
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / "recontagem.md").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print("\n".join(texto))
    return 1 if mudou else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--recontar", action="store_true")
    a = ap.parse_args()
    sys.exit(recontar() if a.recontar else 2)
