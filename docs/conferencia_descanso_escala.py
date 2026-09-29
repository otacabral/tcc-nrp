"""O descanso REAL de uma escala, medido hora a hora. Sem avaliador, sem solver.

    python docs\\conferencia_descanso_escala.py            # os casos do Experimento A
    python docs\\conferencia_descanso_escala.py --todas    # toda escala em resultados/experimento_a

Existe por causa da P13: o avaliador oficial nao pontua o padrao `clt_36h_N_D` como o
escrevemos, entao ele nao serve para atestar a regra das 36 h. Esta conferencia mede o
descanso direto na escala — pega os horarios dos turnos no XML da instancia, ordena as
atribuicoes de cada profissional e calcula o intervalo entre o fim de um turno e o inicio do
proximo. Nao depende de padrao nenhum, nem da leitura que o avaliador faz dele.

Nao substitui o avaliador nas outras familias: ele continua sendo o arbitro da cobertura, do
teto de jornada e dos dias consecutivos. Substitui-o **so** onde ele nao consegue ler o que
esta escrito.

O que confere, por escala:

- **descanso entre turnos**: menor intervalo entre dois turnos consecutivos, contra o minimo
  do regime — 36 h no 12x36 (art. 59-A, contrapartida da jornada de 12 h) e 11 h no de 8 h
  (interjornada do art. 66). O limite vem de `instancia_br.DESCANSO_EXIGIDO`, a mesma tabela
  que a conferencia das sequencias admitidas usa;
- **apos turno que atravessa a meia-noite**: informativo, para ver o pior caso do noturno;
- **dias consecutivos**: maior sequencia de dias trabalhados, contra o limite do contrato;
- **descanso semanal (art. 67)**: em cada semana (segunda a domingo), o maior descanso
  continuo que contem um dia sem turno, medido inteiro, minimo 24 h. Medido de fato so desde
  29/09 — ver `descanso_semanal`.

`conferir_descanso` no `instancia_br.py` faz coisa diferente e complementar: enumera as
sequencias que o CONTRATO admite. Esta aqui mede o que a escala de fato entregou.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from instancia_br import DESCANSO_EXIGIDO  # noqa: E402
from parser import ler_instancia  # noqa: E402
from solucao import ler_xml  # noqa: E402

CASOS = [
    ("12x36 v1   e40", "br_intermediario_12x36_teto_e40_v1"),
    ("12x36 v0,5 e40", "br_intermediario_12x36_teto_e40_v05"),
    ("8h    v1   e37", "br_intermediario_8h_teto_e37_v1"),
    ("8h    v0   e36", "br_intermediario_8h_teto_e36"),
    ("12x36 v0   e36", "br_intermediario_12x36_teto_e36"),
]
PASTA = RAIZ / "resultados" / "experimento_a"

MIN_SEMANAL = 24

# ERRO CORRIGIDO EM 23/09: esta conferencia exigia 36 h depois de QUALQUER turno que
# atravessasse a meia-noite, inclusive no regime de 8 h, onde o turno N vai de 23:00 as 07:00.
# As 36 h sao do art. 59-A, que e a contrapartida da jornada de 12 h e nao existe no de 8 h.
# Com isso ela reprovava escala legal — o 8 h aparecia com 16 h de intervalo, que cumpre o
# art. 66 com folga. O limite agora vem do regime, e o regime sai da duracao do turno.


def regime_da_instancia(inst) -> str:
    """Deduz o regime pela duracao do turno: 12 h e o 12x36, 8 h e o de tres turnos.

    Deduzir em vez de receber por parametro e de proposito: assim a conferencia le o que o
    ARQUIVO diz, e nao o que quem chamou acha que ele diz.
    """
    duracoes = set()
    for t in inst.turnos.values():
        h = (datetime.combine(date.min, t.fim) - datetime.combine(date.min, t.inicio))
        duracoes.add(round(h.total_seconds() / 3600) % 24 or 24)
    if duracoes == {12}:
        return "12x36"
    if duracoes == {8}:
        return "8h"
    raise ValueError(f"nao reconheci o regime: duracoes de turno {sorted(duracoes)}")


def _inicio_fim(inst, dia, turno_id) -> tuple[datetime, datetime]:
    t = inst.turnos[turno_id]
    ini = datetime.combine(dia, t.inicio)
    fim = datetime.combine(dia, t.fim)
    if t.noturno:                     # atravessa a meia-noite
        fim += timedelta(days=1)
    return ini, fim


def descanso_semanal(inst, blocos: list[tuple[datetime, datetime]]) -> list[tuple[int, float]]:
    """Maior descanso continuo de cada semana do horizonte, medido no relogio (CLT art. 67).

    Regra (DECISOES.md, "2026-09-29 — Ajustes da Etapa 2"): para cada semana, de segunda a
    domingo, contam os intervalos continuos de descanso que contem algum dia DA SEMANA sem
    turno atribuido a pessoa; o maior deles precisa ter ao menos 24 h. O intervalo e medido
    INTEIRO, sem recorte na virada da semana — um descanso de sabado a segunda conta com o
    tamanho que tem.

    Semana sem nenhum dia sem turno vale 0 h. No comeco do horizonte o descanso comeca no
    inicio do primeiro dia. No FIM, a borda e aberta (decisao do Otavio, 29/09): o descanso
    que chega ao fim do horizonte conta como cumprido e vale `inf`, porque o que vem depois
    e outro periodo, fora do escopo da escala. A continuidade entre periodos nao e conferida
    — limitacao declarada no DECISOES.md.

    Devolve [(semana, horas)] para as semanas inteiras do horizonte, contadas do primeiro dia.

    HISTORICO. Ate 29/09 o descanso semanal nao era medido: a linha que deveria guarda-lo era
    `menor_semanal = min(menor_semanal, menor_semanal)`, que nao faz nada. A primeira correcao
    recortava o descanso na segunda 00:00, e reprovava escala legal — seis noites de segunda a
    sabado deixam 40 h de descanso de domingo a segunda, e o recorte so enxergava 17 h. A
    segunda versao media o descanso inteiro mas cortava no fim do horizonte, e reprovava a
    folga no ultimo domingo (17 h, da noite de sabado ate a meia-noite).
    """
    ini_h = datetime.combine(inst.inicio, datetime.min.time())
    fim_h = max([datetime.combine(inst.fim + timedelta(days=1), datetime.min.time())]
                + [b for _, b in blocos])
    descansos, cursor = [], ini_h
    for a, b in sorted(blocos):
        if a > cursor:
            descansos.append((cursor, a))
        cursor = max(cursor, b)
    if fim_h > cursor:
        descansos.append((cursor, fim_h))
    com_turno = {a.date() for a, _ in blocos}   # o turno pertence ao dia em que comeca

    resultado = []
    for semana in range(inst.n_dias // 7):
        livres = [inst.inicio + timedelta(days=7 * semana + k) for k in range(7)]
        livres = [d for d in livres if d not in com_turno]
        maior = 0.0
        for a, b in descansos:
            if any(a < datetime.combine(d + timedelta(days=1), datetime.min.time())
                   and b > datetime.combine(d, datetime.min.time()) for d in livres):
                horas = float("inf") if b == fim_h else (b - a).total_seconds() / 3600
                maior = max(maior, horas)
        resultado.append((semana, maior))
    return resultado


def medir(inst, escala) -> dict:
    """Intervalos reais, por profissional, entre turnos consecutivos."""
    por_prof: dict[str, list] = {}
    for (dia, n, turno) in escala:
        por_prof.setdefault(n, []).append((dia, turno))

    menor_geral = menor_pos_noturno = float("inf")
    pior_geral = pior_noturno = None
    max_consec = 0
    menor_semanal, pior_semanal = float("inf"), None
    for n, turnos in por_prof.items():
        turnos.sort()
        blocos = [_inicio_fim(inst, d, t) for d, t in turnos]
        for k in range(len(blocos) - 1):
            fim = blocos[k][1]
            proximo = blocos[k + 1][0]
            intervalo = (proximo - fim).total_seconds() / 3600
            if intervalo < menor_geral:
                menor_geral, pior_geral = intervalo, (n, turnos[k], turnos[k + 1])
            if inst.turnos[turnos[k][1]].noturno and intervalo < menor_pos_noturno:
                menor_pos_noturno, pior_noturno = intervalo, (n, turnos[k], turnos[k + 1])
        for semana, horas in descanso_semanal(inst, blocos):
            if horas < menor_semanal:
                menor_semanal, pior_semanal = horas, (n, semana + 1)
        # maior sequencia de dias trabalhados
        seq = melhor = 0
        anterior = None
        for d, _ in turnos:
            seq = seq + 1 if anterior is not None and (d - anterior).days == 1 else 1
            melhor = max(melhor, seq)
            anterior = d
        max_consec = max(max_consec, melhor)
    return {"menor_geral": menor_geral, "pior_geral": pior_geral,
            "menor_pos_noturno": menor_pos_noturno, "pior_noturno": pior_noturno,
            "menor_semanal": menor_semanal, "pior_semanal": pior_semanal,
            "max_consec": max_consec, "profissionais": len(por_prof)}


def fmt_semanal(horas: float) -> str:
    """`inf` e a borda aberta: o pior descanso da escala chega ao fim do horizonte."""
    return "borda" if horas == float("inf") else f"{horas:.0f} h"


def cumpre(inst, r) -> bool:
    """Veredito de uma escala: descanso entre turnos, dias seguidos e descanso semanal."""
    limite = inst.contratos["0"].max_consecutive_working_days
    teto_consec = limite.valor if limite.ativa else inst.n_dias
    exigido = DESCANSO_EXIGIDO[regime_da_instancia(inst)]
    return (r["menor_geral"] >= exigido and r["max_consec"] <= teto_consec
            and r["menor_semanal"] >= MIN_SEMANAL)


def main() -> int:
    todas = "--todas" in sys.argv
    casos = CASOS
    if todas:
        casos = [(p.stem.removesuffix("_instancia").removeprefix("br_"),
                  p.stem.removesuffix("_instancia"))
                 for p in sorted(PASTA.glob("*_instancia.xml"))]
    print(f"{'escala':32s}{'N':>4s}{'regime':>8s}{'descanso min':>14s}{'exigido':>9s}"
          f"{'apos noturno':>14s}{'dias seguidos':>15s}{'semanal':>9s}{'veredito':>10s}")
    faltando, reprovadas = [], []
    for rotulo, nome in casos:
        inst_arq, sol_arq = PASTA / f"{nome}_instancia.xml", PASTA / f"{nome}.xml"
        if not sol_arq.exists():
            faltando.append(nome)
            continue
        inst = ler_instancia(str(inst_arq))
        _, _, escala = ler_xml(sol_arq)
        r = medir(inst, escala)
        limite = inst.contratos["0"].max_consecutive_working_days
        teto_consec = limite.valor if limite.ativa else inst.n_dias
        regime = regime_da_instancia(inst)
        exigido = DESCANSO_EXIGIDO[regime]
        ok = cumpre(inst, r)
        pn = ("-" if r["menor_pos_noturno"] == float("inf")
              else f"{r['menor_pos_noturno']:.0f} h")
        print(f"{rotulo:32s}{r['profissionais']:4d}{regime:>8s}{r['menor_geral']:12.0f} h"
              f"{exigido:7d} h{pn:>14s}"
              f"{r['max_consec']:10d} / {teto_consec:<2d}{fmt_semanal(r['menor_semanal']):>9s}"
              f"{'ok' if ok else 'REPROVA':>10s}")
        if not ok:
            reprovadas.append((rotulo, r))
    print(f"\nexigido, por regime: {DESCANSO_EXIGIDO['12x36']} h no 12x36 (art. 59-A, a"
          f" contrapartida da jornada de 12 h) e {DESCANSO_EXIGIDO['8h']} h no de 8 h")
    print("(interjornada do art. 66). Mais os dias seguidos dentro do limite do contrato, e o")
    print("descanso semanal: em cada semana (segunda a domingo), o maior descanso continuo que")
    print(f"contem um dia sem turno, medido inteiro no relogio, de ao menos {MIN_SEMANAL} h "
          "(art. 67).")
    print("O descanso que chega ao fim do horizonte conta como cumprido (borda aberta): a")
    print("continuidade com o periodo seguinte nao e conferida. 'apos noturno' e informativo.")
    for rotulo, r in reprovadas:
        print(f"\n{rotulo}: pior caso geral {r['pior_geral']}, pior apos noturno "
              f"{r['pior_noturno']}, pior semanal {fmt_semanal(r['menor_semanal'])} "
              f"(profissional, semana) = {r['pior_semanal']}")
    if faltando:
        print(f"\nescalas ausentes ({len(faltando)}): "
              + ", ".join(faltando))
        print("gerar com: python src\\experimento_a.py --sensibilidade")
    if not reprovadas and not faltando:
        print("\nTodas as escalas respeitam as regras do proprio regime, medidas no relogio.")
    return 1 if reprovadas else 0


if __name__ == "__main__":
    raise SystemExit(main())
