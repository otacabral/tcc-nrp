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


# --- as rodadas (DECISOES.md, "2026-10-23 — Caso A"; esperado em ESPERADO.md) ---------------------

HIPOTESE = "HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA"
RODADAS = {"A11_fixo_24_ordem1": ("A11_fixo", 0, 1),
           "A36_fixo_30_ordem1": ("A36_fixo", 6, 1),
           "A36_fixo_30_ordem2": ("A36_fixo", 6, 2)}
ENF_UNIDADE = ("Enf 6118", "Enf 4798", "Enf 4969", "Enf 5993")
MEMORIA_MIN_MB = 3 * 1024


def ordem(k: int) -> dict:
    """Ordem 1 (a pratica) e ordem 2. As linhas "So este turno" ficam na tabela de pedidos (a
    importancia e da linha): Essencial na ordem 1, Desejavel na ordem 2 (`entrada`)."""
    import ferramenta as fe
    p = fe.prioridades_padrao()           # pedido Essencial, enf. em posto de tecnico Importante
    p.update(max_folgas_seguidas=(fe.IMPORTANTE, 4), min_fds_seguidos=(fe.IMPORTANTE, 2),
             min_turnos=(fe.IMPORTANTE, 10), enf_posto_tec=(fe.IMPORTANTE, None))
    if k == 2:
        p["max_fds_seguidos"] = (fe.ESSENCIAL, 3)
    return p


def entrada(nome: str):
    """A Entrada da rodada: o A36_fixo informado com 30 (a composicao da regra `equipe`, a mesma
    que a busca montou em 21/10), as linhas "So este turno" com a importancia da ordem."""
    import dataclasses
    import fase2
    import ferramenta as fe
    import prioridades as pr
    base, acrescimo, k = RODADAS[nome]
    e = fase2.entrada(base)
    if acrescimo:
        n_enf, n_tec, ne, nt = fe.equipe(e, acrescimo, fe._horas_enfermeiro(e))
        e = dataclasses.replace(e, n_enfermeiros=n_enf, n_tecnicos=n_tec, nomes_enfermeiros=ne,
                                nomes_tecnicos=nt)
    nivel = pr.ESSENCIAL if k == 1 else pr.DESEJAVEL
    regras = [dataclasses.replace(l, importancia=nivel) for l in e.regras]
    return dataclasses.replace(e, regras=regras, prioridades=ordem(k))


def _familias(arq: Path) -> dict:
    """Soma por familia do que o avaliador oficial cobrou (`validacao_restricoes.ler_avaliador`)."""
    from validacao_restricoes import ler_avaliador
    _, custos, total, erros = ler_avaliador(arq)
    soma = Counter()
    for (_, fam), c in custos.items():
        soma[fam] += c
    return {"por_familia": dict(soma), "total": total, "erros": erros}


def rodada(nome: str) -> dict:
    import time as relogio
    import fase2
    import ferramenta as fe
    import instancia_br as br
    import prioridades as pr
    from bateria_solvers import memoria_livre_mb, pico_mb
    base, _, k = RODADAS[nome]
    param = fase2.RODADAS[base][2]
    e = entrada(nome)
    out = {"rodada": nome, "ordem": k, "aviso": HIPOTESE if param else None,
           "descanso_por_turno": param, "memoria_livre_mb_antes": memoria_livre_mb(),
           "quadro_informado": e.quadro, "enfermeiros": e.n_enfermeiros, "tecnicos": e.n_tecnicos,
           "commit": __import__("subprocess").run(["git", "-C", str(RAIZ), "rev-parse", "--short",
                                                   "HEAD"], capture_output=True,
                                                  text=True).stdout.strip()}
    if param:
        print(HIPOTESE, flush=True)
    fe.TEMPO = fe.TEMPO_ETAPA2 = None                 # o produto: so o orcamento de 60 min
    t0 = relogio.time()
    br.DESCANSO_POR_TURNO.clear()
    br.DESCANSO_POR_TURNO.update(param)
    try:
        r = fe.verificar(e, progresso=lambda f, m: print(f"[{relogio.time() - t0:7.1f} s] {m}",
                                                         flush=True))
        base_conf = fe.montar(e)                       # para a conferencia, na mesma regra
    finally:
        br.DESCANSO_POR_TURNO.clear()
    ind = r.indicadores or {}
    out.update(frase=r.frase(), veredito=r.veredito, menor_viavel=r.menor_viavel,
               tentativas=r.tentativas, provado_etapa1=bool(ind.get("provado")),
               partes=ind.get("partes"), blocos=ind.get("blocos"), etapa2=ind.get("etapa2"),
               provado_etapa2=ind.get("provado_etapa2"), caminho=ind.get("caminho"),
               frases_por_nivel=[f for _, f in fe.frases_por_nivel(r)] if r.escala else [],
               criterios=r.criterios, descumpridos=r.descumpridos,
               descanso_ok=(r.conformidade or {}).get("ok"),
               tempo_total_s=round(relogio.time() - t0, 1))
    if r.escala:
        SAIDA.mkdir(parents=True, exist_ok=True)
        # (1) restricao dura: a instancia da rodada (pesos da ordem) no avaliador oficial
        out["avaliador"] = fase2.avaliador(r.inst, r.escala, SAIDA, nome)
        # (2) por criterio: os criterios da ordem ligados, peso 1 (no A36, os da ordem 2, que
        # incluem o max. fins de semana seguidos — assim as duas escalas sao avaliadas nele)
        pn = pr.normalizar(ordem(2 if base == "A36_fixo" else k))
        coef = {**{c.id: 1 for c in pr.CRITERIOS}, **{pr.REGRAS + x: 1 for x in pr.CONSIDERADOS}}
        unidade, _ = pr.aplicar(base_conf, pn, coef, br.HABILIDADE_ENF)
        conf = fase2.avaliador(unidade, r.escala, SAIDA, nome + "_conferencia")
        out["conferencia"] = {**conf, **_familias(SAIDA / f"{nome}_conferencia_escala_avaliador.txt")}
        out["contagem_peso1"] = [list(x) for x in pr.resultado(unidade, r.escala, pn,
                                                                br.HABILIDADE_ENF)]
    out["pico_memoria_mb"] = pico_mb()
    return out


def rodar() -> int:
    import json
    import subprocess
    from bateria_solvers import _espera_memoria, _sem_suspensao
    SAIDA.mkdir(parents=True, exist_ok=True)
    _sem_suspensao()
    for nome in RODADAS:
        arq = SAIDA / f"{nome}.json"
        if arq.exists():
            print(f"{nome}: ja feito", flush=True)
            continue
        livre = _espera_memoria()
        if livre < MEMORIA_MIN_MB:
            print(f"PARADO: {nome}: so {livre} MB livres depois de 15 min", flush=True)
            return 1
        print(f"{nome}: comecando (memoria livre {livre} MB)", flush=True)
        with open(SAIDA / f"{nome}.log", "w", encoding="utf-8") as f:
            cod = subprocess.run([sys.executable, __file__, "--rodada", nome], stdout=f,
                                 stderr=subprocess.STDOUT).returncode
        print(f"{nome}: codigo {cod}", flush=True)
        if cod != 0 or not arq.exists():
            print(f"PARADO: {nome} falhou (ver {nome}.log)", flush=True)
            return 1
    relatorio()
    print("TUDO OK", flush=True)
    return 0


def relatorio() -> int:
    import json
    import prioridades as pr
    from validacao_restricoes import NOME_PT  # noqa: F401  (rotulos do avaliador, se precisar)
    fam_de = {c.nome: c.familia for c in pr.CRITERIOS}
    fam_de[pr.NOME_REGRAS] = "shift_off_requests"
    res = {n: json.loads((SAIDA / f"{n}.json").read_text(encoding="utf-8"))
           for n in RODADAS if (SAIDA / f"{n}.json").exists()}
    L = ["# Caso A pela prática e sensibilidade (2 ordens) — resultado", "",
         "Decisão: `DECISOES.md`, \"2026-10-23 — Caso A\"; esperado: `ESPERADO.md` (registrado "
         "antes). v1.4.4; orçamento padrão de 60 min por rodada. **Tempo: limite operacional desta "
         "máquina (i5-10210U, 11,8 GB) com o HiGHS 1.15.1 via appsi; uma rodada por ordem.** "
         "Números só vão ao `NUMEROS_TCC.md` depois da aprovação do Otávio.", ""]
    for n, d in res.items():
        L += [f"## {n}" + (f" — {d['aviso']}" if d.get("aviso") else ""), "",
              f"- Quadro informado: {d['quadro_informado']} ({d['enfermeiros']} enf. + "
              f"{d['tecnicos']} téc.); memória livre antes: {d['memoria_livre_mb_antes']} MB; "
              f"pico: {d.get('pico_memoria_mb')} MB; commit `{d.get('commit')}`.",
              f"- **Frase da tela:** \"{d['frase']}\"",
              f"- Tempo total: {d['tempo_total_s']} s (limite operacional).",
              f"- Avaliador oficial (restrição dura): "
              f"{(d.get('avaliador') or {}).get('hard_constraints_violation', '—')}; descanso no "
              f"relógio: {'ok' if d.get('descanso_ok') else d.get('descanso_ok')}.", "",
              "Valor de cada bloco: **no fim do bloco** (escala da etapa 1; modelo e escala, com a "
              "P20) e **na escala final** (depois da etapa 2, recontado fora do modelo com os "
              "coeficientes do bloco). A etapa 2 não pode passar do valor do fim do bloco; pode "
              "ficar abaixo.", "",
              "| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do "
              "bloco: escala | Escala final |", "|---|---:|---:|---|---:|---:|---:|"]
        nome_id = {c.nome: c.id for c in pr.CRITERIOS}
        coefs = {tuple(b[0]): b[1] for b in d.get("blocos") or []}
        for p in d.get("partes") or []:
            niveis = p.get("niveis") or []
            coef = coefs.get(tuple(niveis), {})
            final = sum(coef.get(pr.REGRAS + nv if nc == pr.NOME_REGRAS else nome_id.get(nc), 0) * v
                        for nv, nc, v, _ in d.get("criterios") or [] if nv in niveis)
            L.append(f"| {' + '.join(niveis)} | {p.get('limite')} | "
                     f"{round(p.get('tempo', 0), 1)} | {'sim' if p.get('provado') else 'não'} | "
                     f"{p.get('valor_modelo', p.get('valor'))} | {p.get('valor')} | "
                     f"{final if coef else '—'} |")
        L.append(f"| etapa 2 (equilíbrio) | | | {'sim' if d.get('provado_etapa2') else 'não'} "
                 f"({d.get('etapa2')}) | | | |")
        L += ["", *[f"- {f}" for f in d.get("frases_por_nivel") or []], "",
              "| Critério | Importância | Violações (ferramenta) | Avaliador oficial (peso 1) |",
              "|---|---|---:|---:|"]
        conf = (d.get("conferencia") or {}).get("por_familia") or {}
        for nivel, nome_c, v, _ in d.get("criterios") or []:
            fam = fam_de.get(nome_c)
            externo = ("sem conferência externa" if fam in (pr.CUSTO, None) or
                       fam not in conf and v else str(conf.get(fam, 0)))
            L.append(f"| {nome_c} | {nivel} | {v} | {externo} |")
        if "max_consecutive_working_weekends" in conf or n.startswith("A36"):
            L.append(f"| Máx. fins de semana seguidos (3), avaliado com o critério ligado | — | "
                     f"{next((x[2] for x in d.get('contagem_peso1') or [] if x[1].startswith('Máximo de fins de semana')), '—')} | "
                     f"{conf.get('max_consecutive_working_weekends', 0)} |")
        desc = d.get("descumpridos") or []
        L += ["", "Descumprimentos de \"Só este turno\" por profissional (nível, quantos): "
              + ("; ".join(f"{p} ({nv}, {q})" for nv, p, q in desc) if desc else "nenhum") + "."]
        enf = [(nv, p, q) for nv, p, q in desc if p.startswith("Enf ")]
        L.append("Enfermeiros: da unidade (" + ", ".join(ENF_UNIDADE) + ") — "
                 + (", ".join(f"{p} {q}" for _, p, q in enf if p in ENF_UNIDADE) or "nenhum")
                 + "; acrescidos — "
                 + (", ".join(f"{p} {q}" for _, p, q in enf if p not in ENF_UNIDADE) or "nenhum")
                 + ".")
        L.append("")
    (SAIDA / "resultado.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


MARCA_COMPLEMENTO = "## Complemento (24/10, só leitura das escalas gravadas)"


def complemento() -> int:
    """24/10 (pedido da Orientacao): so leitura das escalas gravadas, sem solver. (a) enfermeiro
    em posto de tecnico e turnos por enfermeiro, os 4 da unidade x os 6 acrescidos; (b) violacoes
    por profissional em max. folgas seguidas e min. turnos (avaliador oficial, peso 1), marcando
    quem tem ferias; (c) a nota das linhas "Unwanted pattern". Acrescenta (ou troca) a secao no
    resultado.md."""
    import xml.etree.ElementTree as ET
    import fase2
    import ferramenta as fe
    import instancia_br as br
    from validacao_restricoes import ler_avaliador
    L = [MARCA_COMPLEMENTO, "",
         "Sem solver: as escalas e as saídas do avaliador gravadas na rodada; a instância de cada "
         "rodada remontada pela mesma entrada (`caso_a_pratica.py --complemento`).", ""]
    for nome, (base, _, _) in RODADAS.items():
        e = entrada(nome)
        br.DESCANSO_POR_TURNO.clear()
        br.DESCANSO_POR_TURNO.update(fase2.RODADAS[base][2])
        try:
            inst = fe.montar(e)
        finally:
            br.DESCANSO_POR_TURNO.clear()
        nomes = {i: p.nome for i, p in inst.profissionais.items()}
        enf = [i for i, p in inst.profissionais.items() if br.HABILIDADE_ENF in p.habilidades]
        enf.sort(key=lambda i: (nomes[i] not in ENF_UNIDADE, nomes[i]))
        esc = [(a.findtext("Employee"), a.findtext("ShiftType"))
               for a in ET.parse(SAIDA / f"{nome}_escala.xml").getroot().iter("Assignment")]
        turnos, tec = Counter(), Counter()
        for n, s in esc:
            if n in enf:
                turnos[n] += 1
                tec[n] += br.HABILIDADE_ENF not in inst.turnos[s].habilidades
        L += [f"### {nome}" + (f" — {HIPOTESE}" if fase2.RODADAS[base][2] else ""), "",
              "| Enfermeiro | Origem | Turnos | Em posto de técnico |", "|---|---|---:|---:|"]
        for grupo in (True, False):
            sel = [n for n in enf if (nomes[n] in ENF_UNIDADE) == grupo]
            for n in sel:
                L.append(f"| {nomes[n]} | {'unidade' if grupo else 'acrescido'} | {turnos[n]} | "
                         f"{tec[n]} |")
            if sel:
                L.append(f"| **{'4 da unidade' if grupo else str(len(sel)) + ' acrescidos'}** | | "
                         f"**{sum(turnos[n] for n in sel)}** | **{sum(tec[n] for n in sel)}** |")
        _, custos, _, _ = ler_avaliador(SAIDA / f"{nome}_conferencia_escala_avaliador.txt")
        ferias = Counter(n for n, _ in inst.indisponiveis)
        L.append("")
        for fam, rot in (("max_consecutive_free_days", "Máximo de folgas seguidas (4)"),
                         ("min_num_assignments", "Mínimo de turnos (10)")):
            por = sorted(((nomes.get(n, n), v, n in ferias) for (n, f), v in custos.items()
                          if f == fam and v), key=lambda x: (not x[2], x[0]))
            tot = sum(v for _, v, _ in por)
            de_ferias = sum(v for _, v, f in por if f)
            L.append(f"- {rot}, avaliador oficial (peso 1): **{tot}** — "
                     + (", ".join(f"{p} {v}{' (férias)' if f else ''}" for p, v, f in por) or "nenhuma")
                     + f". Das quais de quem tem férias: {de_ferias}.")
        L.append(f"- Férias na rodada: {', '.join(f'{nomes[n]} ({k} dias)' for n, k in ferias.items())}.")
        L.append("")
    L += ["### Notas", "",
          "- **Férias (semântica do INRC, não escolha da ferramenta):** no formato do INRC, dia de "
          "férias conta como dia sem trabalho — o `avaliacao.py` e o avaliador oficial concordam. "
          "Com 15 dias de férias seguidos, o máximo de folgas seguidas (4) é violado em pelo menos "
          "15 − 4 = 11 por pessoa: os 22 das três rodadas são a Tarde 1 e a Noite A 1, 11 cada, e "
          "com o nível provado são inevitáveis. No mínimo de turnos, os 4 da Noite A 1 (A11 e A36 "
          "ordem 1) vêm da mesma semântica somada ao turno fixo no Essencial (só noites, em metade "
          "do mês) e, com prova, são inevitáveis nessas ordens; na ordem 2, com o \"Só este turno\" "
          "no Desejável, a Noite A 1 chega aos 10 turnos à custa de 7 quebras do turno fixo. Os "
          "outros 6 do mínimo de turnos no A36 ordem 1 (Enf 4798, 6, 7, 8, 9) e o 1 da ordem 2 (Enf "
          "6) não têm relação com férias.",
          "- **\"Unwanted pattern\"** (ex.: N-null-D12) na saída do avaliador: é o artefato conhecido "
          "dos padrões das 36 h (`DECISOES.md`, \"2026-10-06 — Padrão das 36 h fica no XML (opção (a) "
          "da P13)\": o avaliador lê o padrão como noturno, folga, folga e cobra violações que não "
          "existem). Não entra na conferência; a regra das 36 h é conferida pela medição do descanso "
          "no relógio (aprovada nas três rodadas).", ""]
    arq = SAIDA / "resultado.md"
    texto = arq.read_text(encoding="utf-8")
    if MARCA_COMPLEMENTO in texto:
        texto = texto[:texto.index(MARCA_COMPLEMENTO)].rstrip("\n") + "\n"
    arq.write_text(texto.rstrip("\n") + "\n\n" + "\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


def montar_sem_solver() -> int:
    """Teste do script: monta as tres entradas e a instancia de conferencia, sem solver."""
    import fase2
    import ferramenta as fe
    import instancia_br as br
    import prioridades as pr
    for nome, (base, _, k) in RODADAS.items():
        e = entrada(nome)
        br.DESCANSO_POR_TURNO.clear()
        br.DESCANSO_POR_TURNO.update(fase2.RODADAS[base][2])
        try:                                   # o piso le o descanso: dentro do parametro
            inst = fe.montar(e)
            blocos = pr.planejar(inst, pr.normalizar(e.prioridades), br.HABILIDADE_ENF)
            piso = fe.piso(inst)
        finally:
            br.DESCANSO_POR_TURNO.clear()
        print(f"{nome}: quadro {e.quadro} ({e.n_enfermeiros} + {e.n_tecnicos}); linhas "
              f"{len(e.regras)} ({sorted({l.importancia for l in e.regras})}); blocos "
              f"{[(b.niveis, b.maximo) for b in blocos]}; piso {piso}", flush=True)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--recontar", action="store_true")
    ap.add_argument("--rodar", action="store_true")
    ap.add_argument("--rodada", choices=list(RODADAS))
    ap.add_argument("--relatorio", action="store_true")
    ap.add_argument("--montar", action="store_true")
    ap.add_argument("--complemento", action="store_true")
    a = ap.parse_args()
    if a.rodada:
        import json
        d = rodada(a.rodada)
        SAIDA.mkdir(parents=True, exist_ok=True)
        (SAIDA / f"{a.rodada}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1,
                                                           default=str), encoding="utf-8")
        print(f"{a.rodada}: {d['frase']} | {d['tempo_total_s']} s")
        sys.exit(0)
    sys.exit(recontar() if a.recontar else rodar() if a.rodar else complemento() if a.complemento
             else relatorio() if a.relatorio
             else montar_sem_solver() if a.montar else 2)
