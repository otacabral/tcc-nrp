"""O descanso REAL de uma escala, medido hora a hora. Sem avaliador, sem solver.

    python docs\\conferencia_descanso_escala.py

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
- **descanso semanal (art. 67)**: maior intervalo sem trabalhar em cada semana, minimo 24 h.

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


def medir(inst, escala) -> dict:
    """Intervalos reais, por profissional, entre turnos consecutivos."""
    por_prof: dict[str, list] = {}
    for (dia, n, turno) in escala:
        por_prof.setdefault(n, []).append((dia, turno))

    menor_geral = menor_pos_noturno = float("inf")
    pior_geral = pior_noturno = None
    max_consec = 0
    menor_semanal = float("inf")
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
            if intervalo >= MIN_SEMANAL:
                menor_semanal = min(menor_semanal, menor_semanal)
        # maior sequencia de dias trabalhados
        seq = melhor = 0
        anterior = None
        for d, _ in turnos:
            seq = seq + 1 if anterior is not None and (d - anterior).days == 1 else 1
            melhor = max(melhor, seq)
            anterior = d
        max_consec = max(max_consec, melhor)
        # maior folga da pessoa em cada semana do horizonte
        for semana in range(inst.n_dias // 7):
            janela = [d for d, _ in turnos
                      if semana * 7 <= (d - inst.inicio).days < (semana + 1) * 7]
            if len(janela) < 7:
                continue                     # ha dia livre na semana: folga >= 24 h
            menor_semanal = 0
    return {"menor_geral": menor_geral, "pior_geral": pior_geral,
            "menor_pos_noturno": menor_pos_noturno, "pior_noturno": pior_noturno,
            "max_consec": max_consec, "profissionais": len(por_prof)}


def main() -> int:
    print(f"{'escala':18s}{'N':>4s}{'regime':>8s}{'descanso min':>14s}{'exigido':>9s}"
          f"{'apos noturno':>14s}{'dias seguidos':>15s}{'veredito':>10s}")
    faltando, reprovadas = [], []
    for rotulo, nome in CASOS:
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
        ok = r["menor_geral"] >= exigido and r["max_consec"] <= teto_consec
        pn = ("-" if r["menor_pos_noturno"] == float("inf")
              else f"{r['menor_pos_noturno']:.0f} h")
        print(f"{rotulo:18s}{r['profissionais']:4d}{regime:>8s}{r['menor_geral']:12.0f} h"
              f"{exigido:7d} h{pn:>14s}"
              f"{r['max_consec']:10d} / {teto_consec:<2d}{'ok' if ok else 'REPROVA':>10s}")
        if not ok:
            reprovadas.append((rotulo, r))
    print(f"\nexigido, por regime: {DESCANSO_EXIGIDO['12x36']} h no 12x36 (art. 59-A, a"
          f" contrapartida da jornada de 12 h) e {DESCANSO_EXIGIDO['8h']} h no de 8 h")
    print("(interjornada do art. 66). Mais os dias seguidos dentro do limite do contrato, que")
    print("aproxima o descanso semanal do art. 67. 'apos noturno' e informativo.")
    for rotulo, r in reprovadas:
        print(f"\n{rotulo}: pior caso geral {r['pior_geral']}, pior apos noturno "
              f"{r['pior_noturno']}")
    if faltando:
        print(f"\nescalas ausentes ({len(faltando)}): "
              + ", ".join(faltando))
        print("gerar com: python src\\experimento_a.py --sensibilidade")
    if not reprovadas and not faltando:
        print("\nTodas as escalas respeitam as regras do proprio regime, medidas no relogio.")
    return 1 if reprovadas else 0


if __name__ == "__main__":
    raise SystemExit(main())
