"""Fase 2 (casos A e B), uma rodada por processo — chamado por `docs/diagnostico/rodar_fase2.sh`.

    python docs\\diagnostico\\fase2.py <rodada> <pasta de saida>            # roda (solver)
    python docs\\diagnostico\\fase2.py <rodada> <pasta de saida> --montar   # so monta, sem solver

Rodadas (pedido da Orientacao de 20/10, Parte 9), classificacao padrao, orcamento 60 min,
1.800 s por nivel e na etapa 2:

- A36_livre — caso A, 36 h (a regra do produto), rodizio livre;
- A36_fixo  — caso A, 36 h, turno fixo ("So este turno", Essencial);
- A11_fixo  — caso A, DESCANSO_POR_TURNO = {"D12": 11}, turno fixo;
- B11_livre — caso B, {"D12": 11};
- B36_livre — caso B, 36 h (esperado: recusado pela conta ate 101, em segundos).

As de 11 h sao HIPOTESE DE SENSIBILIDADE — NAO REGRA DA FERRAMENTA: o rotulo e a primeira linha
do log e do relatorio .txt, o primeiro campo do JSON e o comeco do nome dos arquivos; o
parametro volta a {} ao fim e o valor e impresso. Esperados: `resultados/caso_a_2026-10-20/
ESPERADO.md` e `resultados/caso_b_2026-10-20/ESPERADO.md`.

"Nao decidido" nao e falha: o codigo de saida so e diferente de 0 com erro de codigo ou de
entrada. A conferencia do descanso no relogio compartilha a premissa com o modelo (a mesma
`descanso_exigido`); a da cobertura e externa: o avaliador oficial na escala gerada.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "docs"), str(AQUI)]

import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402

ROTULO = "HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA"
PREFIXO = "HIPOTESE_SENSIBILIDADE_"
ORCAMENTO, TEMPO_NIVEL = 60 * 60, 1800
RODADAS = {   # nome: (caso, rodada da entrada, DESCANSO_POR_TURNO)
    "A36_livre": ("caso_a_2026-10-20", "rodizio_livre", {}),
    "A36_fixo": ("caso_a_2026-10-20", "turno_fixo", {}),
    "A11_fixo": ("caso_a_2026-10-20", "turno_fixo", {"D12": 11}),
    "B11_livre": ("caso_b_2026-10-20", None, {"D12": 11}),
    "B36_livre": ("caso_b_2026-10-20", None, {}),
}


def entrada(nome: str) -> fe.Entrada:
    pasta, rodada, _ = RODADAS[nome]
    spec = importlib.util.spec_from_file_location(f"entrada_{pasta}",
                                                  RAIZ / "resultados" / pasta / "entrada.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.entrada(rodada) if rodada else mod.entrada()


def versao() -> dict:
    def git(*a):
        return subprocess.run(["git", *a], cwd=RAIZ, capture_output=True, text=True,
                              check=False).stdout.strip()
    return {"versao": git("describe", "--tags", "--always"), "commit": git("rev-parse", "HEAD"),
            "alteracoes_locais": bool(git("status", "--porcelain", "--", "src"))}


def menor_descanso(inst, escala) -> dict[str, float | None]:
    """Menor descanso no relogio depois de D12 e depois de N, ate o turno seguinte da mesma
    pessoa. Mesma premissa do modelo (os horarios da instancia)."""
    por = {}
    for d, n, s in escala:
        t = inst.turnos[s]
        ini = datetime.combine(d, t.inicio)
        por.setdefault(n, []).append((ini, ini + timedelta(hours=t.duracao_h),
                                      s[:-1] if br.HABILIDADE_ENF in t.habilidades else s))
    menor: dict[str, float | None] = {"D12": None, "N": None}
    for lista in por.values():
        lista.sort()
        for (_, fim, s), (ini2, _, _) in zip(lista, lista[1:]):
            if s in menor:
                h = (ini2 - fim).total_seconds() / 3600
                menor[s] = h if menor[s] is None else min(menor[s], h)
    return menor


def avaliador(inst, escala, pasta: Path, base: str) -> dict:
    """Conferencia externa da cobertura: XML da instancia (com os pedidos) e da escala, XSD e o
    avaliador oficial. Recusa do XSD ou do avaliador fica registrada; nada e contornado."""
    import pedidos_avaliador as pa
    from solucao import escrever_xml as escrever_solucao
    from solucao import validar_xsd as xsd_solucao
    from validacao_restricoes import ler_avaliador
    from validar import AvaliadorIndisponivel, avaliar
    out = {}
    try:
        xml_inst = pa.escrever_instancia(inst, pasta / f"{base}_instancia.xml")
        out["xsd_instancia"] = br.validar_xsd(xml_inst)[:5]
        sol = escrever_solucao(inst, escala, pasta / f"{base}_escala.xml", validar=False)
        out["xsd_escala"] = xsd_solucao(sol)[:5]
        penalidade, resumida, _ = avaliar(xml_inst, sol)
        _, _, _, erros = ler_avaliador(sol.with_name(sol.stem + "_avaliador.txt"))
        out["penalidade_avaliador"] = penalidade
        out["hard_constraints_violation"] = "sim" if any("Hard" in e for e in erros) else "não"
        out["erros_avaliador"] = erros[:5]
        if penalidade is None:
            out["recusa"] = resumida[:500]
    except AvaliadorIndisponivel as x:
        out["hard_constraints_violation"] = "avaliador não rodou"
        out["recusa"] = str(x)
    except Exception as x:  # noqa: BLE001 — recusa do XSD/avaliador: registrar, nao contornar
        out["hard_constraints_violation"] = "não conferido"
        out["recusa"] = f"{type(x).__name__}: {x}"
    return out


def rodar(nome: str, pasta: Path, so_montar: bool) -> int:
    caso, _, param = RODADAS[nome]
    hipotese = bool(param)
    base = (PREFIXO if hipotese else "") + nome
    if hipotese:
        print(ROTULO, flush=True)
    pasta.mkdir(parents=True, exist_ok=True)
    e = entrada(nome)
    t0 = time.time()
    eventos = []

    def progresso(frac, msg):
        linha = f"[{time.time() - t0:7.1f} s] {msg}"
        eventos.append(linha)
        print(f"{nome} {linha}", flush=True)

    try:
        br.DESCANSO_POR_TURNO.clear()
        br.DESCANSO_POR_TURNO.update(param)
        print(f"{nome}: {caso}, quadro {e.quadro} ({e.n_enfermeiros} + {e.n_tecnicos}); "
              f"DESCANSO_POR_TURNO = {br.DESCANSO_POR_TURNO}", flush=True)
        inst = fe.montar(e)
        piso = fe.piso(inst)
        print(f"{nome}: montado; piso (conta prévia) {piso}; turnos que bloqueiam o dia "
              f"seguinte {sorted(fe.bloqueiam_o_dia_seguinte(inst))}", flush=True)
        if so_montar:
            return 0
        fe.ORCAMENTO, fe.TEMPO, fe.TEMPO_ETAPA2 = ORCAMENTO, TEMPO_NIVEL, TEMPO_NIVEL
        r = fe.verificar(e, progresso=progresso)
    finally:
        br.DESCANSO_POR_TURNO.clear()
        print(f"DESCANSO_POR_TURNO ao fim: {br.DESCANSO_POR_TURNO}", flush=True)
    total = time.time() - t0
    from piso_pares import tempos
    seg = tempos(eventos)
    vistos = set()
    tentativas = []
    for q, status, n_enf, n_tec in r.tentativas:
        tentativas.append({"quadro": q, "status": status, "enfermeiros": n_enf,
                           "tecnicos": n_tec,
                           "segundos": None if q in vistos else seg.get(q),
                           "quem_provou": "conta" if status == "piso" else "solver"})
        vistos.add(q)
    ind = r.indicadores
    out = {"aviso": ROTULO if hipotese else "regra do produto (36 h depois de turno ≥ 12 h)",
           "rodada": nome, "caso": caso, "descanso_por_turno": param, **versao(),
           "orcamento_s": ORCAMENTO, "limite_por_nivel_s": TEMPO_NIVEL,
           "frase": r.frase(), "frase_vigente": r.frase_vigente() if r.escala else None,
           "veredito": r.veredito, "quadro_informado": e.quadro, "piso": piso,
           "tentativas": tentativas, "menor_viavel": r.menor_viavel,
           "provado": ("sim" if r.provado else "não") if r.escala else None,
           "gap": None if r.provado or not r.escala else ind.get("gap"),
           "diagnostico": ({"motivo": r.diagnostico[0], "frase": r.diagnostico[1]}
                           if r.diagnostico else None),
           "criterios": [{"nivel": c[0], "nome": c[1], "violacoes": c[2]}
                         for c in (r.criterios or [])],
           "so_este_turno_descumpridas": ([{"nivel": n, "profissional": p, "quantas": k}
                                           for n, p, k in r.descumpridos]
                                          if RODADAS[nome][1] == "turno_fixo" else None),
           "alertas_cofen": r.alertas, "tempo_total_s": round(total, 1),
           "progresso": eventos}
    if r.escala:
        br.DESCANSO_POR_TURNO.update(param)     # a medicao no relogio na mesma regra da rodada
        try:
            out["menor_descanso_h"] = menor_descanso(r.inst, r.escala)
            out["conferencia_descanso"] = r.conformidade.get("ok") if r.conformidade else None
        finally:
            br.DESCANSO_POR_TURNO.clear()
        out["avaliador"] = avaliador(r.inst, r.escala, pasta, base)
        out["avaliador"]["premissa"] = (
            "a cobertura é conferida fora do modelo (avaliador oficial); a conferência do "
            "descanso no relógio compartilha a premissa com o modelo (descanso_exigido)")
    (pasta / f"{base}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1,
                                                   default=str), encoding="utf-8")
    linha = (f"{'[' + ROTULO + '] ' if hipotese else ''}{nome}: {r.frase()} | menor viável "
             f"{r.menor_viavel} | tentativas "
             f"{[(t['quadro'], t['quem_provou'] if t['status'] == 'piso' else t['status']) for t in tentativas]}"
             f" | avaliador: {out.get('avaliador', {}).get('hard_constraints_violation', '-')} "
             f"| {total:.0f} s")
    texto = ([ROTULO] if hipotese else []) + [
        f"# Fase 2 — {nome}", "", f"- versão {out['versao']} ({out['commit'][:7]})",
        f"- frase: {out['frase']}", f"- frase vigente: {out['frase_vigente']}",
        f"- piso (conta prévia): {piso}; menor viável: {r.menor_viavel}; provado: "
        f"{out['provado']}; gap: {out['gap']}",
        f"- tentativas: {tentativas}", f"- diagnóstico: {out['diagnostico']}",
        f"- critérios: {out['criterios']}",
        f"- Só este turno descumpridas: {out['so_este_turno_descumpridas']}",
        f"- menor descanso no relógio: {out.get('menor_descanso_h')}",
        f"- alertas COFEN: {r.alertas}", f"- avaliador: {out.get('avaliador')}",
        f"- tempo total: {total:.0f} s (limite operacional, não resultado)", "", linha]
    (pasta / f"{base}.txt").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print(linha, flush=True)
    return 0


def main() -> int:
    nome, pasta = sys.argv[1], Path(sys.argv[2])
    try:
        return rodar(nome, pasta, "--montar" in sys.argv[3:])
    except Exception:  # noqa: BLE001 — erro de codigo ou de entrada: PARADO no script
        traceback.print_exc()
        print(f"ERRO de código ou de entrada em {nome}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
