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

- **descanso entre turnos**: cada intervalo entre dois turnos consecutivos, contra o minimo
  exigido depois do turno que termina — 36 h depois de turno de 12 h ou mais (art. 59-A) e
  11 h depois dos demais (art. 66). A regra vem de `instancia_br.descanso_exigido`, a mesma
  que gera os pares proibidos. Desde 29/09 vale para qualquer horario de turno, nao so para
  os dois regimes;
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
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from instancia_br import (INTERJORNADA, POS_TURNO_LONGO, TURNO_LONGO,  # noqa: E402
                          descanso_exigido)
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
# art. 66 com folga. O limite passou a vir do regime em 23/09, e desde 29/09 vem da duracao do
# turno que termina — o que da o mesmo resultado nos dois regimes e vale para turno qualquer.


def duracao_h(turno) -> float:
    """Duracao do turno em horas, lida dos horarios do arquivo. Ver `Turno.duracao_h`."""
    return turno.duracao_h


def regime_da_instancia(inst) -> str:
    """Rotulo do regime, so para exibir: 12x36, 8h, ou as duracoes dos turnos.

    Ate 29/09 exigia turnos todos de 8 h ou todos de 12 h, e levantava erro fora disso, porque
    o descanso exigido saia do regime. Agora o exigido sai do turno (`descanso_exigido`), e
    este rotulo nao decide nada.
    """
    duracoes = {round(duracao_h(t)) for t in inst.turnos.values()}
    if duracoes == {12}:
        return "12x36"
    if duracoes == {8}:
        return "8h"
    return "+".join(f"{d}h" for d in sorted(duracoes))


def _inicio_fim(inst, dia, turno_id) -> tuple[datetime, datetime]:
    t = inst.turnos[turno_id]
    ini = datetime.combine(dia, t.inicio)
    fim = datetime.combine(dia, t.fim)
    if t.noturno:                     # atravessa a meia-noite
        fim += timedelta(days=1)
    return ini, fim


def descanso_semanal(inst, blocos: list[tuple[datetime, datetime]],
                     sem_bordas: bool = False) -> list[tuple[int, float | None]]:
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

    `sem_bordas=True` (P15, 09/10): deixa de fora o descanso que comeca no inicio do horizonte
    e o que chega ao fim dele, porque o que vem antes e depois nao e conhecido; a semana sem
    nenhum descanso interno que contenha dia livre vale None. E a medida do ALERTA de 35 h e
    do indicador da tela; a trava de 24 h (`medir`, `cumpre`) continua com as bordas.

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
        maior = None if sem_bordas else 0.0
        for a, b in descansos:
            if sem_bordas and (a == ini_h or b == fim_h):
                continue
            if any(a < datetime.combine(d + timedelta(days=1), datetime.min.time())
                   and b > datetime.combine(d, datetime.min.time()) for d in livres):
                horas = float("inf") if b == fim_h else (b - a).total_seconds() / 3600
                maior = horas if maior is None else max(maior, horas)
        resultado.append((semana, maior))
    return resultado


def semanal_sem_bordas(inst, escala) -> dict[str, float | None]:
    """Por profissional, o menor descanso semanal SEM as bordas do horizonte (P15): o minimo,
    entre as semanas que tem descanso interno, de `descanso_semanal(..., sem_bordas=True)`.
    None para quem nao tem nenhum (sem turno, ou so descansos que encostam nas bordas)."""
    por_prof: dict[str, list] = {n: [] for n in inst.profissionais}
    for (dia, n, turno) in escala:
        por_prof[n].append(_inicio_fim(inst, dia, turno))
    saida = {}
    for n, blocos in por_prof.items():
        if not blocos:
            saida[n] = None
            continue
        valores = [h for _, h in descanso_semanal(inst, sorted(blocos), sem_bordas=True)
                   if h is not None]
        saida[n] = min(valores) if valores else None
    return saida


def medir(inst, escala) -> dict:
    """Intervalos reais, por profissional, entre turnos consecutivos."""
    por_prof: dict[str, list] = {}
    for (dia, n, turno) in escala:
        por_prof.setdefault(n, []).append((dia, turno))

    menor_geral = menor_pos_noturno = menor_folga = float("inf")
    pior_geral = pior_noturno = pior_folga = None
    exigido_no_pior = None
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
            # o exigido depende do turno que TERMINA: 36 h depois de turno de 12 h ou mais,
            # 11 h depois dos demais. Vem dos horarios, nao de uma lista de regimes.
            exigido = descanso_exigido(duracao_h(inst.turnos[turnos[k][1]]), turnos[k][1])
            if intervalo - exigido < menor_folga:
                menor_folga, exigido_no_pior = intervalo - exigido, exigido
                pior_folga = (n, turnos[k], turnos[k + 1], intervalo)
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
            "menor_folga": menor_folga, "pior_folga": pior_folga,
            "exigido_no_pior": exigido_no_pior,
            "menor_pos_noturno": menor_pos_noturno, "pior_noturno": pior_noturno,
            "menor_semanal": menor_semanal, "pior_semanal": pior_semanal,
            "max_consec": max_consec, "profissionais": len(por_prof)}


def fmt_semanal(horas: float | None) -> str:
    """`inf` e a borda aberta: o pior descanso da escala chega ao fim do horizonte. None: sem
    descanso semanal inteiro dentro do periodo (medida sem bordas)."""
    if horas is None:
        return "—"
    return "borda" if horas == float("inf") else f"{horas:.0f} h"


def cumpre(inst, r) -> bool:
    """Veredito de uma escala: descanso entre turnos, dias seguidos e descanso semanal."""
    limite = inst.contratos["0"].max_consecutive_working_days
    teto_consec = limite.valor if limite.ativa else inst.n_dias
    return (r["menor_folga"] >= 0 and r["max_consec"] <= teto_consec
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
        exigido = r["exigido_no_pior"] or 0
        ok = cumpre(inst, r)
        pn = ("-" if r["menor_pos_noturno"] == float("inf")
              else f"{r['menor_pos_noturno']:.0f} h")
        print(f"{rotulo:32s}{r['profissionais']:4d}{regime:>8s}{r['menor_geral']:12.0f} h"
              f"{exigido:7d} h{pn:>14s}"
              f"{r['max_consec']:10d} / {teto_consec:<2d}{fmt_semanal(r['menor_semanal']):>9s}"
              f"{'ok' if ok else 'REPROVA':>10s}")
        if not ok:
            reprovadas.append((rotulo, r))
    print(f"\nexigido, pelo turno que termina: {POS_TURNO_LONGO} h depois de turno de "
          f"{TURNO_LONGO} h ou mais (art. 59-A)")
    print(f"e {INTERJORNADA} h depois dos demais (interjornada do art. 66). 'exigido' e o do par "
          "mais apertado.")
    print("Mais os dias seguidos dentro do limite do contrato, e o")
    print("descanso semanal: em cada semana (segunda a domingo), o maior descanso continuo que")
    print(f"contem um dia sem turno, medido inteiro no relogio, de ao menos {MIN_SEMANAL} h "
          "(art. 67).")
    print("O descanso que chega ao fim do horizonte conta como cumprido (borda aberta): a")
    print("continuidade com o periodo seguinte nao e conferida. 'apos noturno' e informativo.")
    for rotulo, r in reprovadas:
        print(f"\n{rotulo}: par mais apertado {r['pior_folga']} (exigido "
              f"{r['exigido_no_pior']} h), pior caso geral {r['pior_geral']}, pior apos noturno "
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
