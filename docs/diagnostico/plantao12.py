"""3o bloco (20/10), Parte 3: teste do plantao de 12 h no fim de semana (sem codigo novo na
ferramenta). Esperado registrado antes: `resultados/plantao12_2026-10-20/ESPERADO.md`.

Modelo "6 h + noturno de 12 h" com um 4o turno D12 (7-19); demanda de tecnicos no dia util
M 5, T 5, D12 0, N 4 e no fim de semana M 0, T 0, D12 5, N 4; 4 enfermeiros e 18 tecnicos;
28 dias a partir de 04/01/2027; orcamento de 20 min. As conferencias (c) e (e) sao feitas na
escala, pelos horarios, fora do modelo.

    python docs\\diagnostico\\plantao12.py
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402

SAIDA = RAIZ / "resultados" / "plantao12_2026-10-20"
TURNOS = [("M", 7, 13), ("T", 13, 19), ("N", 19, 7), ("D12", 7, 19)]


def entrada() -> fe.Entrada:
    return fe.Entrada(
        turnos=TURNOS, grau="intermediario", n_enfermeiros=4, n_tecnicos=18,
        demanda_turno={"M": (0, 5), "T": (0, 5), "N": (0, 4), "D12": (0, 0)},
        demanda_fds={"M": (0, 0), "T": (0, 0), "N": (0, 4), "D12": (0, 5)},
        inicio=date(2027, 1, 4))


def intervalos(inst, escala):
    """(profissional, inicio, fim, turno) de cada atribuicao, no relogio."""
    saida = []
    for d, n, s in escala:
        t = inst.turnos[s]
        ini = datetime.combine(d, t.inicio)
        saida.append((n, ini, ini + timedelta(hours=t.duracao_h), s.rstrip("E")))
    return sorted(saida)


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    e = entrada()
    try:
        fe.montar(e)
        aceita, erro = True, ""
    except ValueError as x:
        aceita, erro = False, str(x)
    print(f"(a) aceita o 4o turno e a demanda 0: {aceita} {erro}", flush=True)
    r = fe.verificar(e, orcamento=20 * 60,
                     progresso=lambda f, msg: print(f"      {msg}", flush=True))
    linhas = [f"(a) aceita o 4º turno e a demanda 0: {'sim' if aceita else 'NÃO ' + erro}",
              f"(b) veredito: {r.frase()} (tentativas {r.tentativas}; caminho "
              f"{r.indicadores.get('caminho')}; provado {r.indicadores.get('provado')}; gap "
              f"{r.indicadores.get('gap')})"]
    ok = aceita and r.escala and r.veredito == fe.ADMITE
    if r.escala:
        inst = r.inst
        iv = intervalos(inst, r.escala)
        menor, quebras = None, []
        for (n1, i1, f1, s1), (n2, i2, f2, s2) in zip(iv, iv[1:]):
            if n1 == n2 and s1 == "D12":
                folga = (i2 - f1).total_seconds() / 3600
                menor = folga if menor is None else min(menor, folga)
                if folga < 36:
                    quebras.append((n1, f1, i2, folga))
        d12_util = [(d, n) for d, n, s in r.escala if s.rstrip("E") == "D12"
                    and d.weekday() not in br.FIM_DE_SEMANA["sab_dom"][0]]
        d12_fds = sum(1 for d, n, s in r.escala if s.rstrip("E") == "D12")
        c = r.conformidade
        linhas += [f"(c) depois de um D12, menor descanso até o turno seguinte da mesma pessoa: "
                   f"{menor} h; abaixo de 36 h: {len(quebras)} {quebras[:5]}",
                   f"(d) conferência de descanso: {'cumpre' if c['ok'] else 'NÃO CUMPRE'} "
                   f"(menor entre turnos {c['menor_geral']:.0f} h; máximo de dias seguidos "
                   f"{c['max_consec']})",
                   f"(e) D12 em dia útil: {len(d12_util)} (D12 no fim de semana: {d12_fds})",
                   f"enfermeiro em posto de técnico: {r.indicadores['enf_em_posto_tec']}; "
                   f"contrato cumprido {r.indicadores['fracao_min']:.0%}–"
                   f"{r.indicadores['fracao_max']:.0%}"]
        ok = ok and not quebras and c["ok"] and not d12_util
        grade = fe.grade(inst, r.escala)
        grade.to_csv(SAIDA / "escala.csv", encoding="utf-8")
    linhas.append("TUDO OK" if ok else "FALHOU")
    texto = ["# Parte 3 — plantão de 12 h no fim de semana: resultado (20/10/2026)", "",
             "Esperado: `ESPERADO.md` nesta pasta. Orçamento 20 min; HiGHS 1.15.1. Tempo é limite "
             "operacional, não resultado.", ""] + [f"- {l}" for l in linhas]
    (SAIDA / "resultado.md").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print("\n".join(linhas))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
