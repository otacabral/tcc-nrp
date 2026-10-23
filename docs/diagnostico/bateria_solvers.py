"""Bateria HiGHS x SCIP (DECISOES.md, "2026-10-22 — Bateria HiGHS x SCIP: casos, regras,
criterio e regra de troca", registrada antes de rodar). NAO mexe na ferramenta.

    python docs\\diagnostico\\bateria_solvers.py --todos          # os 8 casos, os dois solvers
    python docs\\diagnostico\\bateria_solvers.py --relatorio      # so refaz a tabela e a regra
    python docs\\diagnostico\\bateria_solvers.py --caso C --solver S   # um (chamado pelo --todos)
    python docs\\diagnostico\\bateria_solvers.py --montar         # sem solver: so os tamanhos

Cada caso x solver roda num processo proprio (isolamento e memoria), com limite duro de 1.200 s.
O --todos retoma: o que ja tem JSON em resultados/solvers_2026-10-22/bateria/ nao roda de novo.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import math
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "docs"), str(AQUI)]

SAIDA = RAIZ / "resultados" / "solvers_2026-10-22" / "bateria"
LIMITE = 600                 # s por caso (regra registrada)
DURO = 1200                  # s: o processo e encerrado se passar disto (registrado como tal)
MEMORIA_MIN_MB = 3 * 1024
SOLVERS = ("HiGHS", "SCIP")
INRC = {"sprint01": ("instancias/sprint/sprint/sprint01.xml", 56),
        "sprint02": ("instancias/sprint/sprint/sprint02.xml", 58),
        "long01": ("instancias/long/long/long01.xml", 197),
        "long02": ("instancias/long/long/long02.xml", 219),
        "medium_late05": ("instancias/medium/medium_late_xml/medium_late05.xml", 107)}
FERRAMENTA = {"A36_livre_30": ("A36_livre", 6), "A36_fixo_30": ("A36_fixo", 6),
              "B11_livre_89": ("B11_livre", 0)}
CASOS = list(INRC) + list(FERRAMENTA)
ESCOLHIDOS = list(CASOS)     # --casos (23/10: a rodada de sensibilidade usa 3 casos)
HIPOTESE = "HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA"


# --- memoria (Windows, sem psutil) ---------------------------------------------------------------

class _Mem(ctypes.Structure):
    _fields_ = [("dwLength", wintypes.DWORD), ("dwMemoryLoad", wintypes.DWORD),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def memoria_livre_mb() -> int:
    m = _Mem()
    m.dwLength = ctypes.sizeof(_Mem)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return int(m.ullAvailPhys / 2**20)


class _Proc(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)]


def pico_mb() -> int:
    c = _Proc()
    c.cb = ctypes.sizeof(_Proc)
    k32, psapi = ctypes.windll.kernel32, ctypes.windll.psapi
    k32.GetCurrentProcess.restype = wintypes.HANDLE      # sem isto o handle -1 vira 0 em 64 bits
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(_Proc), wintypes.DWORD]
    psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return int(c.PeakWorkingSetSize / 2**20)


# --- a chamada do solver, igual para os dois -----------------------------------------------------

def resolvedor(solver: str, registro: list):
    """Funcao com a assinatura de `ferramenta.resolver` (veredito, escala, provado, gap), que
    resolve com o HiGHS ou o SCIP pelas regras da bateria e registra cada chamada."""
    import comparar_solvers as cs
    import experimento_a as ea
    import modelo
    f = cs.highs if solver == "HiGHS" else cs.scip

    def resolver(m, tempo, partida=False):
        nv, ni, nc = cs._tamanho(m)
        limite = LIMITE if tempo is None else max(1, int(tempo))
        try:
            d, _ = f(m, limite, partida=partida)
        except Exception as x:  # noqa: BLE001 — erro do solver: registra, nao contorna
            registro.append({"variaveis": nv, "inteiras": ni, "restricoes": nc,
                             "limite": limite, "partida": partida, "erro": repr(x)})
            return ea.ERRO, None, False, None
        estado = d["estado"].lower()
        if d["ub"] is not None:
            veredito = ea.VIAVEL
        elif "infeasible" in estado:
            veredito = ea.INVIAVEL
        else:
            veredito = ea.INDETERMINADO
        registro.append({"variaveis": nv, "inteiras": ni, "restricoes": nc, "limite": limite,
                         "partida": partida, "tempo": round(d["tempo"], 2), "ub": d["ub"],
                         "lb": d["lb"], "gap": d["gap"], "provado": d["provado"],
                         "estado": d["estado"], "veredito": veredito})
        escala = modelo.atribuicoes(m) if veredito == ea.VIAVEL else None
        return veredito, escala, bool(d["provado"]), d["gap"]

    return resolver


# --- um caso x um solver (num processo proprio) ----------------------------------------------------

def rodar(caso: str, solver: str) -> dict:
    commit = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    sujo = bool(subprocess.run(["git", "-C", str(RAIZ), "status", "--porcelain", "src"],
                               capture_output=True, text=True).stdout.strip())
    out = {"caso": caso, "solver": solver, "memoria_livre_mb_antes": memoria_livre_mb(),
           "limite_caso_s": LIMITE, "commit_ferramenta": commit, "src_com_mudancas": sujo}
    registro: list = []
    t0 = time.time()
    if caso in INRC:
        import modelo
        import validar
        from parser import ler_instancia
        from solucao import escrever_xml
        arq, ref = INRC[caso]
        inst = ler_instancia(str(RAIZ / arq))
        m = modelo.construir(inst)
        v, escala, provado, _ = resolvedor(solver, registro)(m, LIMITE)
        for k, r in enumerate(registro):
            r["nivel"] = "objetivo único (INRC)"
        out.update(referencia=ref, provado_etapa1=provado,
                   valores_etapa1=[registro[0].get("ub")] if registro else [])
        if escala:
            # 23/10 (sensibilidade): o valor da ESCALA, fora do modelo (avaliacao.py), alem do
            # do modelo; sem prova, a vitoria conta por ele
            from avaliacao import penalidade
            out["valores_modelo_etapa1"] = out["valores_etapa1"]
            out["valores_escala_etapa1"] = [penalidade(inst, escala)]
            sol = SAIDA / f"{caso}_{solver}_escala.xml"
            escrever_xml(inst, escala, sol)
            valor, _, _ = validar.avaliar(RAIZ / arq, sol)
            out["avaliador"] = {"penalidade_avaliador": valor}
    else:
        import fase2
        import ferramenta as fe
        import instancia_br as br
        nome, acrescimo = FERRAMENTA[caso]
        param = fase2.RODADAS[nome][2]
        if param:
            out["aviso"] = HIPOTESE
        e = fase2.entrada(nome)
        fe.TEMPO = fe.TEMPO_ETAPA2 = None           # a regra do produto (v1.4.3), sem teto
        fe.resolver = resolvedor(solver, registro)   # so neste processo
        br.DESCANSO_POR_TURNO.clear()
        br.DESCANSO_POR_TURNO.update(param)
        try:
            inst = fe.montar(e, acrescimo, fe._horas_enfermeiro(e))
            out["quadro"] = len(inst.profissionais)
            out["enfermeiros"] = fe._n_enf(inst)
            v, inst_p, escala, info = fe.resolver_com_objetivo(
                inst, None, prazo=time.time() + LIMITE, prioridades=e.prioridades)
        finally:
            br.DESCANSO_POR_TURNO.clear()
        # as chamadas na ordem: cada parte da etapa 1 (1, ou 2 com a protecao) e a etapa 2
        # chamadas por parte: 1, +1 com a protecao da primeira escala, +1 com o aperto da P20
        # (nivel sem prova; 23/10); "nao rodou" = nenhuma
        i = 0
        for parte in info.get("partes", []):
            if str(parte.get("veredito", "")).startswith("não rodou"):
                continue
            rotulo = "etapa 1: " + " + ".join(parte.get("niveis") or ["(sem nível)"])
            n = 1 + ("protecao" in parte)
            for k in range(n + ("aperto" in parte)):
                if i < len(registro):
                    registro[i]["nivel"] = rotulo + (" — aperto P20 (x fixo)" if k == n else "")
                    i += 1
        for r in registro[i:]:
            r["nivel"] = "etapa 2 (equilíbrio)"
        out.update(caminho=info.get("caminho"), provado_etapa1=bool(info.get("provado")),
                   valores_etapa1=[p.get("valor") for p in info.get("partes", [])],
                   valores_modelo_etapa1=[p.get("valor_modelo", p.get("valor"))
                                          for p in info.get("partes", [])],
                   partes=info.get("partes"), etapa2=info.get("etapa2"),
                   provado_etapa2=info.get("provado_etapa2"))
        if escala:
            # 23/10 (sensibilidade): o valor de cada bloco da etapa 1 na ESCALA FINAL, fora do
            # modelo (prioridades.resultado, coeficiente x violacoes)
            import prioridades as pr
            pn = pr.normalizar(e.prioridades)
            coefs = {tuple(n): c for n, c, _ in info.get("blocos", [])}
            nome_id = {c.nome: c.id for c in pr.CRITERIOS}
            linhas = pr.resultado(inst_p, escala, pn, br.HABILIDADE_ENF)
            valores = []
            for parte in info.get("partes", []):
                niveis = parte.get("niveis") or []
                coef = coefs.get(tuple(niveis), {})
                valores.append(sum(coef.get(pr.REGRAS + nv if nome == pr.NOME_REGRAS
                                            else nome_id[nome], 0) * v
                                   for nv, nome, v, _ in linhas if nv in niveis))
            out["valores_escala_etapa1"] = valores
            out["criterios"] = linhas
            out["familias_com_folga_consideradas"] = sorted(
                c.id for c in pr.considerados(pn)
                if c.familia not in (pr.PEDIDO, pr.CUSTO) and not c.clt)
            out["avaliador"] = fase2.avaliador(inst_p, escala, SAIDA, f"{caso}_{solver}")
    out.update(veredito=v, tempo_total_s=round(time.time() - t0, 1), chamadas=registro,
               pico_memoria_mb=pico_mb())
    return out


# --- relatorio, vitorias e regra --------------------------------------------------------------------

def _num(x, casas=0):
    if x is None:
        return "—"
    if isinstance(x, float) and math.isinf(x):
        return "∞"
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def vencedor(h: dict, s: dict) -> str:
    """Regra registrada: vence quem prova onde o outro nao prova; se nenhum prova, a escala de
    valor menor (sem escala = pior que qualquer escala); gap sozinho nao conta; o resto empata.
    Nos casos da ferramenta, a etapa 1 (os valores por bloco, em ordem)."""
    ph, ps = bool(h.get("provado_etapa1")), bool(s.get("provado_etapa1"))
    if ph != ps:
        return "HiGHS" if ph else "SCIP"
    if ph and ps:
        return "empate"
    # 23/10: sem prova, conta o valor da ESCALA (fora do modelo) quando registrado
    chave = "valores_escala_etapa1"
    vh = [math.inf if x is None else x for x in h.get(chave, h.get("valores_etapa1")) or [None]]
    vs = [math.inf if x is None else x for x in s.get(chave, s.get("valores_etapa1")) or [None]]
    vh = [round(x, 6) for x in vh]
    vs = [round(x, 6) for x in vs]
    if vh == vs:
        return "empate"
    return "HiGHS" if vh < vs else "SCIP"


def relatorio() -> str:
    linhas = ["# Bateria HiGHS × SCIP — resultado", "",
              "Regras: `DECISOES.md`, \"2026-10-22 — Bateria HiGHS × SCIP\" (registrada antes de "
              "rodar). i5-10210U, 11,8 GB, Windows 11; HiGHS 1.15.1 (appsi) e SCIP 10.0 "
              f"(PySCIPOpt 6.3.0); {LIMITE} s por caso, gap 0,01%, 1 thread. **Tempos: uma máquina e "
              "uma configuração só — comportamento observado, não resultado geral.**", "",
              "| Caso | Solver | Nível | Variáveis | Restrições | Limite (s) | Tempo (s) | "
              "Melhor escala | Melhor limite | Gap | Ótimo provado | Avaliador oficial |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|"]
    res = {}
    for caso in ESCOLHIDOS:
        for solver in SOLVERS:
            arq = SAIDA / f"{caso}_{solver}.json"
            if not arq.exists():
                linhas.append(f"| {caso} | {solver} | (não rodou) | | | | | | | | | |")
                continue
            d = json.loads(arq.read_text(encoding="utf-8"))
            res[(caso, solver)] = d
            av = (d.get("avaliador") or {}).get("penalidade_avaliador")
            if d.get("estourou"):
                linhas.append(f"| {caso} | {solver} | processo encerrado no limite duro de "
                              f"{DURO} s | | | | | | | | não | — |")
                continue
            for k, c in enumerate(d.get("chamadas", [])):
                if "erro" in c:
                    linhas.append(f"| {caso} | {solver} | {c.get('nivel')} | {c['variaveis']} | "
                                  f"{c['restricoes']} | {c['limite']} | — | erro: {c['erro'][:60]} "
                                  f"| | | | |")
                    continue
                linhas.append(
                    f"| {caso} | {solver} | {c.get('nivel', '?')}{' (partida)' if c['partida'] else ''} | "
                    f"{_num(c['variaveis'])} | {_num(c['restricoes'])} | {c['limite']} | "
                    f"{_num(c['tempo'], 1)} | {_num(c['ub'], 2)} | {_num(c['lb'], 2)} | "
                    f"{'—' if c['gap'] is None else _num(100 * c['gap'], 2) + '%'} | "
                    f"{'sim' if c['provado'] else 'não'} | "
                    f"{_num(av) if k == len(d['chamadas']) - 1 else ''} |")
    linhas += ["", "## Vitórias por caso (regra registrada)", "",
               "Valores da etapa 1 por bloco: **modelo** (o objetivo no ponto do solver) e "
               "**escala** (recalculado fora do modelo, na escala entregue; sem prova, a vitória "
               "conta por ele).", "",
               "| Caso | HiGHS: provou / modelo / escala | SCIP: provou / modelo / escala | Vence |",
               "|---|---|---|---|"]
    placar = {"HiGHS": 0, "SCIP": 0, "empate": 0}
    perde_prova = []
    for caso in ESCOLHIDOS:
        h, s = res.get((caso, "HiGHS")), res.get((caso, "SCIP"))
        if not h or not s:
            linhas.append(f"| {caso} | | | (incompleto) |")
            continue
        v = vencedor(h, s)
        placar[v] += 1
        if h.get("provado_etapa1") and not s.get("provado_etapa1"):
            perde_prova.append(caso)
        def _lado(d):
            modelo_ = d.get("valores_modelo_etapa1", d.get("valores_etapa1")) or []
            escala_ = d.get("valores_escala_etapa1")
            return (f"{'sim' if d.get('provado_etapa1') else 'não'} / "
                    f"{[_num(x, 2) for x in modelo_]} / "
                    f"{[_num(x, 2) for x in escala_] if escala_ is not None else 'sem escala'}")
        linhas.append(f"| {caso} | {_lado(h)} | {_lado(s)} | {v} |")
    completo = all((c, sv) in res for c in ESCOLHIDOS for sv in SOLVERS)
    i = placar["SCIP"] > placar["HiGHS"]
    ii = not perde_prova
    linhas += ["", f"Placar: SCIP {placar['SCIP']} × HiGHS {placar['HiGHS']}, "
               f"{placar['empate']} empate(s).", "",
               "## Regra de troca", "",
               f"- (i) o SCIP vence mais casos do que perde: **{'sim' if i else 'não'}** "
               f"({placar['SCIP']} × {placar['HiGHS']});",
               f"- (ii) o SCIP não perde nenhuma prova que o HiGHS consegue: "
               f"**{'sim' if ii else 'não'}**"
               f"{'' if ii else ' (perde em: ' + ', '.join(perde_prova) + ')'};",
               "- (iii) suíte completa depois da troca: "
               + ("a rodar só se (i) e (ii) valerem." if i and ii else "não se aplica."), "",
               ("**Bateria incompleta: a regra não pode ser aplicada.**" if not completo else
                "**Conclusão:** " + ("(i) e (ii) valem; a troca depende de (iii), a suíte completa "
                                     "depois da troca — decisão do Otávio." if i and ii else
                                     "fica o HiGHS; a comparação entra no TCC como avaliação a "
                                     "posteriori."))]
    texto = "\n".join(linhas) + "\n"
    (SAIDA / "resultado.md").write_text(texto, encoding="utf-8")
    return texto


def _sem_suspensao() -> None:
    """23/10: a maquina nao suspende enquanto o driver roda (ES_CONTINUOUS | ES_SYSTEM_REQUIRED)."""
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)


def _espera_memoria(minutos: int = 15) -> int:
    """Espera ate ter MEMORIA_MIN_MB livres (no maximo `minutos`); devolve a memoria livre."""
    fim = time.time() + 60 * minutos
    livre = memoria_livre_mb()
    while livre < MEMORIA_MIN_MB and time.time() < fim:
        time.sleep(30)
        livre = memoria_livre_mb()
    return livre


def todos() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    _sem_suspensao()
    livre = memoria_livre_mb()
    print(f"memoria livre {livre} MB", flush=True)
    if livre < MEMORIA_MIN_MB:
        print(f"PARADO: menos de {MEMORIA_MIN_MB} MB livres; feche programas e rode de novo")
        return 1
    for caso in ESCOLHIDOS:
        for solver in SOLVERS:
            arq = SAIDA / f"{caso}_{solver}.json"
            if arq.exists():
                print(f"{caso} {solver}: ja feito", flush=True)
                continue
            livre = _espera_memoria()
            if livre < MEMORIA_MIN_MB:
                print(f"PARADO: {caso} {solver}: so {livre} MB livres depois de 15 min",
                      flush=True)
                return 1
            print(f"{caso} {solver}: comecando (memoria livre {livre} MB)", flush=True)
            t0 = time.time()
            log = SAIDA / f"{caso}_{solver}.log"
            with open(log, "w", encoding="utf-8") as f:
                try:
                    p = subprocess.run([sys.executable, __file__, "--caso", caso, "--solver", solver,
                                        "--limite", str(LIMITE), "--saida", str(SAIDA)],
                                       stdout=f, stderr=subprocess.STDOUT, timeout=DURO)
                    cod = p.returncode
                except subprocess.TimeoutExpired:
                    cod = "limite duro"
            if not arq.exists():
                arq.write_text(json.dumps({"caso": caso, "solver": solver,
                                           "estourou": cod == "limite duro", "codigo": str(cod),
                                           "memoria_livre_mb_antes": livre},
                                          ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{caso} {solver}: codigo {cod}, {time.time() - t0:.0f} s", flush=True)
    print(relatorio())
    return 0


def montar() -> int:
    """Sem solver: tamanho do modelo de cada caso (a etapa 1, como sera resolvida)."""
    import comparar_solvers as cs
    import fase2
    import ferramenta as fe
    import instancia_br as br
    import modelo
    from parser import ler_instancia
    for caso in CASOS:
        if caso in INRC:
            m = modelo.construir(ler_instancia(str(RAIZ / INRC[caso][0])))
        else:
            nome, ac = FERRAMENTA[caso]
            e = fase2.entrada(nome)
            br.DESCANSO_POR_TURNO.clear()
            br.DESCANSO_POR_TURNO.update(fase2.RODADAS[nome][2])
            try:
                m = fe.modelo_etapa1(fe.montar(e, ac, fe._horas_enfermeiro(e)), e.prioridades)[0]
            finally:
                br.DESCANSO_POR_TURNO.clear()
        nv, ni, nc = cs._tamanho(m)
        print(f"{caso}: {nv} variaveis ({ni} inteiras), {nc} restricoes", flush=True)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--relatorio", action="store_true")
    ap.add_argument("--montar", action="store_true")
    ap.add_argument("--caso", choices=CASOS)
    ap.add_argument("--solver", choices=SOLVERS)
    ap.add_argument("--limite", type=int, default=LIMITE, help="s por caso (padrao 600)")
    ap.add_argument("--saida", type=Path, default=SAIDA)
    ap.add_argument("--casos", nargs="+", choices=CASOS)
    a = ap.parse_args()
    LIMITE, SAIDA = a.limite, a.saida
    DURO = max(DURO, 2 * LIMITE)          # processo encerrado se passar disto (registrado)
    if a.casos:
        ESCOLHIDOS[:] = a.casos
    if a.caso and a.solver:
        SAIDA.mkdir(parents=True, exist_ok=True)
        d = rodar(a.caso, a.solver)
        (SAIDA / f"{a.caso}_{a.solver}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        print(f"{a.caso} {a.solver}: {d['veredito']} | etapa 1 provada {d.get('provado_etapa1')} "
              f"| valores {d.get('valores_etapa1')} | {d['tempo_total_s']} s | pico "
              f"{d['pico_memoria_mb']} MB | avaliador "
              f"{(d.get('avaliador') or {}).get('penalidade_avaliador')}")
        sys.exit(0)
    sys.exit(todos() if a.todos else relatorio() and 0 if a.relatorio else montar() if a.montar
             else 2)
