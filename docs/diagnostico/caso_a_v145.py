"""Caso A com a entrada revista (04/11) e caso B, tudo na v1.4.5 — rodadas de 05/11/2026.

Decisao: `DECISOES.md`, "2026-11-04 — Caso A: entrada revista pela leitura independente do Anexo
B; rodadas na v1.4.5". Pedido: `D:\\TCC\\escrita\\plano_noite\\PROMPT_CLAUDE_CODE_RODADAS_v145.md`.
Esperado (sem solver, registrado antes): `resultados/caso_a_2026-11-04/ESPERADO.md`. Nada em
`src/` muda; este script so chama a ferramenta (`ferramenta.verificar`, o caminho da tela).

    python docs\\diagnostico\\caso_a_v145.py --esperado       # as contas do ESPERADO, sem solver
    python docs\\diagnostico\\caso_a_v145.py --montar         # monta cada rodada, sem solver
    python docs\\diagnostico\\caso_a_v145.py --rodada NOME    # uma rodada (um processo)
    python docs\\diagnostico\\caso_a_v145.py --rodar          # o mestre: todas, em sequencia
    python docs\\diagnostico\\caso_a_v145.py --relatorio      # so le os JSON e escreve o relatorio

O mestre roda cada rodada num processo proprio, na ordem do pedido. Antes de cada uma: >= 3 GB
livres (espera ate 15 min); senao, "PARADO (memoria)" no resumo e segue para a proxima. Retomada:
`RETOMAR=1` (ou `--retomar`) pula as rodadas com JSON gravado; sem ela, o mestre se recusa a rodar
se a pasta de saida ja tiver JSON (nada se sobrescreve). Orcamento: o padrao da ferramenta (60 min
por rodada, `ferramenta.ORCAMENTO`; tempo por nivel dividido pela propria ferramenta).

As rodadas de 11 h sao HIPOTESE DE SENSIBILIDADE — NAO REGRA DA FERRAMENTA: rotulo no nome dos
arquivos e na primeira linha do log, do JSON e do relatorio; o parametro volta a {} ao fim.
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "docs"), str(AQUI)]

import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402
import prioridades as pr  # noqa: E402

PASTA_A = RAIZ / "resultados" / "caso_a_2026-11-04"
PASTA_B = RAIZ / "resultados" / "caso_b_2026-11-04"
# so o teste do script muda estes tres (a regra de 03/10: o menor caso ate o fim, fora da pasta)
SAIDA = Path(os.environ.get("V145_SAIDA") or PASTA_A / "rodadas")
RESUMO = SAIDA / "resumo.txt"
HIPOTESE = "HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA"
PREFIXO_HIP = "HIPOTESE_SENSIBILIDADE_"
ONZE = {"D12": 11}
MEMORIA_MIN_MB = int(os.environ.get("V145_MINIMO_MB") or 3 * 1024)
ESPERA_MIN = 15
# 05/11: o avaliador oficial (Java) no fuso do Windows (E. South America, America/Sao_Paulo)
# quebra nesta janela (ArrayIndexOutOfBoundsException em Schedule.<init>): o horario de verao de
# 2018 comecou em 04/11/2018, e a meia-noite desse dia nao existe nesse fuso. Com o JVM em UTC ele
# roda; nas rodadas antigas (2027, sem horario de verao) a saida e identica byte a byte com e sem
# a opcao (controle em resultados/caso_a_2026-11-04/RELATORIO.md). So o ambiente do processo muda;
# `src/validar.py` fica como esta.
JAVA_FUSO = "-Duser.timezone=UTC"
os.environ["JAVA_TOOL_OPTIONS"] = JAVA_FUSO
ENF_UNIDADE = ("Enf 6118", "Enf 4798", "Enf 4969", "Enf 5993")
FERIAS_DE = {"Téc 6137": "31/10–15/11", "Téc 5976": "15/11–25/11"}

# rodada: caso, rodada da entrada, classificacao (None = padrao), importancia das linhas,
# DESCANSO_POR_TURNO, de onde vem o quadro (None = o da entrada, 23 no A e 89 no B)
RODADAS = {
    "A36_fixo_padrao": ("A", "turno_fixo", None, pr.ESSENCIAL, {}, None),
    "A36_livre_padrao": ("A", "rodizio_livre", None, None, {}, None),
    "A36_fixo_class1": ("A", "turno_fixo", 1, pr.ESSENCIAL, {}, "rodada1"),
    "A36_fixo_class2": ("A", "turno_fixo", 2, pr.DESEJAVEL, {}, "rodada1"),
    PREFIXO_HIP + "A11_fixo_class1": ("A", "turno_fixo", 1, pr.ESSENCIAL, ONZE, None),
    "B36_livre": ("B", None, None, None, {}, None),
    PREFIXO_HIP + "B11_livre": ("B", None, None, None, ONZE, None),
}


def _modulo(pasta: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, pasta / "entrada.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def classificacao(k: int | None) -> dict | None:
    """(g) do DECISOES de 04/11. Classificacao 1: Importante = max. folgas seguidas (4), min.
    turnos (10) e enfermeiro em posto de tecnico; o resto como no padrao (pedido de folga no
    Essencial, sem pedidos nesta entrada; os outros em Nao considerar). O min. fins de semana
    seguidos sai do Importante (revisa a ordem 1 de 23/10). Classificacao 2: + max. fins de semana
    seguidos (3) no Essencial; as linhas vao ao Desejavel pela importancia da linha (`RODADAS`)."""
    if k is None:
        return None
    p = fe.prioridades_padrao()
    p.update(max_folgas_seguidas=(fe.IMPORTANTE, 4), min_turnos=(fe.IMPORTANTE, 10),
             enf_posto_tec=(fe.IMPORTANTE, None))
    if k == 2:
        p["max_fds_seguidos"] = (fe.ESSENCIAL, 3)
    return p


def _rodada1() -> tuple[int, int, int, str] | None:
    """O menor quadro e a composicao achados na rodada 1: do A36_fixo_padrao; se ele nao
    determinar, do A36_livre_padrao. (quadro, enfermeiros, tecnicos, de onde)."""
    for nome in ("A36_fixo_padrao", "A36_livre_padrao"):
        arq = SAIDA / f"{nome}.json"
        if not arq.exists():
            continue
        d = json.loads(arq.read_text(encoding="utf-8"))
        if d.get("veredito") in (fe.ADMITE, fe.FALTAM) and d.get("menor_viavel"):
            q = d["menor_viavel"]
            t = [x for x in d["tentativas"] if x[0] == q and x[1] == "viavel"]
            if t:
                return q, t[-1][2], t[-1][3], nome
    return None


def com_quadro(e: fe.Entrada, quadro: int, n_enf: int) -> fe.Entrada:
    """A entrada informada com `quadro` pessoas, `n_enf` enfermeiros: os acrescimos com os nomes
    que a busca da ferramenta da (`ferramenta.equipe` ou a segunda tentativa, so enfermeiros)."""
    acrescimo = quadro - e.quadro
    if acrescimo == 0:
        return e
    ne, nt, nomes_e, nomes_t = fe.equipe(e, acrescimo, fe._horas_enfermeiro(e))
    if ne != n_enf:                       # a 2a tentativa: os acrescimos todos como enfermeiros
        ne, nt = e.n_enfermeiros + acrescimo, e.n_tecnicos
        nomes_e = list(e.nomes_enfermeiros or []) + [f"Enf {e.n_enfermeiros + i + 1}"
                                                     for i in range(acrescimo)]
        nomes_t = e.nomes_tecnicos
    if ne != n_enf:
        raise ValueError(f"composição {n_enf} enfermeiros não reproduzida ({ne})")
    return dataclasses.replace(e, n_enfermeiros=ne, n_tecnicos=nt, nomes_enfermeiros=nomes_e,
                               nomes_tecnicos=nomes_t)


def entrada(nome: str, exigir_rodada1: bool = True) -> tuple[fe.Entrada, str | None]:
    """(Entrada, observacao). Rodada 2 sem rodada 1 decidida: ValueError (o mestre pula)."""
    caso, rod, k, imp, _, quadro = RODADAS[nome]
    if caso == "B":
        return _modulo(PASTA_B, "entrada_b_v145").entrada(), None
    mod = _modulo(PASTA_A, "entrada_a_v145")
    e = mod.entrada(rod, importancia=imp or pr.ESSENCIAL, prioridades=classificacao(k))
    obs = None
    if quadro == "rodada1":
        r1 = _rodada1()
        if r1 is None:
            if exigir_rodada1:
                raise ValueError("a rodada 1 não determinou o menor quadro")
            r1 = (28, 9, 19, "ESPERADO (só para a montagem sem solver)")
        q, ne, nt, de = r1
        e = com_quadro(e, q, ne)
        if e.n_tecnicos != nt:
            raise ValueError(f"composição {ne} + {nt} não reproduzida ({e.n_enfermeiros} + "
                             f"{e.n_tecnicos})")
        obs = f"quadro e composição da rodada 1: {q} ({ne} + {nt}), lidos de {de}"
    return e, obs


# --- medicoes fora do modelo (sem compartilhar a lista de linhas com o modelo) ------------------

def _base(inst, s: str) -> str:
    return s[:-1] if br.HABILIDADE_ENF in inst.turnos[s].habilidades else s


def turnos_permitidos() -> dict[str, set[str]]:
    """Das 33 linhas da entrada (nome -> turnos-base permitidos), para contar as quebras do turno
    fixo direto na escala — tambem na rodada sem linhas."""
    mod = _modulo(PASTA_A, "entrada_a_v145_linhas")
    perm: dict[str, set[str]] = {}
    for l in mod.regras_turno_fixo():
        perm.setdefault(l.profissional, set()).add(l.turno)
    return perm


def medir_escala(inst, escala) -> dict:
    nome = {i: p.nome for i, p in inst.profissionais.items()}
    enf = {i for i, p in inst.profissionais.items() if br.HABILIDADE_ENF in p.habilidades}
    perm = turnos_permitidos()
    quebras, turnos, em_tec = Counter(), Counter(), Counter()
    for _, n, s in escala:
        pn = nome[n]
        if pn in perm and _base(inst, s) not in perm[pn]:
            quebras[pn] += 1
        if n in enf:
            turnos[pn] += 1
            em_tec[pn] += br.HABILIDADE_ENF not in inst.turnos[s].habilidades
    enfs = sorted((nome[n] for n in enf), key=lambda x: (x not in ENF_UNIDADE, x))
    return {"quebras_turno_fixo_medidas": dict(quebras),
            "enfermeiros_detalhe": [{"nome": x, "origem": "unidade" if x in ENF_UNIDADE else "acrescido",
                             "turnos": turnos[x], "em_posto_de_tecnico": em_tec[x]}
                            for x in enfs],
            "enf_posto_tec_unidade": sum(em_tec[x] for x in enfs if x in ENF_UNIDADE),
            "enf_posto_tec_acrescidos": sum(em_tec[x] for x in enfs if x not in ENF_UNIDADE)}


def _familias(arq: Path, inst) -> dict:
    from validacao_restricoes import ler_avaliador
    _, custos, total, erros = ler_avaliador(arq)
    nome = {i: p.nome for i, p in inst.profissionais.items()}
    soma, por = Counter(), {}
    for (n, fam), c in custos.items():
        soma[fam] += c
        if c:
            por.setdefault(fam, {})[nome.get(n, n)] = c
    return {"por_familia": dict(soma), "por_pessoa": por, "total": total}


def maquina() -> dict:
    def ps(cmd):
        try:
            return subprocess.run(["powershell.exe", "-NoProfile", "-Command", cmd],
                                  capture_output=True, text=True, timeout=60).stdout.strip()
        except Exception:  # noqa: BLE001
            return None
    from importlib.metadata import version
    return {"cpu": ps("(Get-CimInstance Win32_Processor).Name"),
            "ram_gb": ps("[math]::Round((Get-CimInstance Win32_ComputerSystem)"
                         ".TotalPhysicalMemory/1GB,1)"),
            "sistema": platform.platform(), "python": platform.python_version(),
            "solver": f"HiGHS {version('highspy')} (highspy, via Pyomo {version('pyomo')} appsi)",
            "java_memoria": __import__("validar").MEMORIA_JAVA,
            "java_tool_options": os.environ.get("JAVA_TOOL_OPTIONS")}


def versao() -> dict:
    def git(*a):
        return subprocess.run(["git", *a], cwd=RAIZ, capture_output=True, text=True,
                              check=False).stdout.strip()
    return {"versao": git("describe", "--tags", "--always"), "commit": git("rev-parse", "HEAD"),
            "src_alterado": bool(git("status", "--porcelain", "--", "src")),
            "diff_src_v145": bool(git("diff", "v1.4.5", "--", "src"))}


# --- uma rodada ------------------------------------------------------------------------------

def rodada(nome: str) -> int:
    import fase2
    from bateria_solvers import memoria_livre_mb, pico_mb
    caso, rod, k, imp, param, _ = RODADAS[nome]
    if param:
        print(HIPOTESE, flush=True)
    e, obs = entrada(nome)
    out = {"aviso": HIPOTESE if param else "regra da ferramenta (36 h depois de turno ≥ 12 h)",
           "rodada": nome, "caso": caso, "classificacao": k if k else "padrão",
           "importancia_linhas": imp if rod == "turno_fixo" else None,
           "n_linhas": len(e.regras), "descanso_por_turno": param, "observacao": obs,
           **versao(), "maquina": maquina(), "memoria_livre_mb_antes": memoria_livre_mb(),
           "quadro_informado": e.quadro, "enfermeiros": e.n_enfermeiros,
           "tecnicos": e.n_tecnicos, "orcamento_s": fe.ORCAMENTO}
    print(f"{nome}: quadro {e.quadro} ({e.n_enfermeiros} + {e.n_tecnicos}); {len(e.regras)} "
          f"linhas; classificação {out['classificacao']}; {obs or ''}", flush=True)
    t0 = time.time()
    eventos = []

    def progresso(_f, msg):
        linha = f"[{time.time() - t0:7.1f} s] {msg}"
        eventos.append(linha)
        print(linha, flush=True)

    fe.TEMPO = fe.TEMPO_ETAPA2 = None          # o produto: so o orcamento de 60 min
    if os.environ.get("V145_ORCAMENTO"):        # so o teste do script (fora da pasta de saida)
        fe.ORCAMENTO = int(os.environ["V145_ORCAMENTO"])
        out["orcamento_s"] = fe.ORCAMENTO
    br.DESCANSO_POR_TURNO.clear()
    br.DESCANSO_POR_TURNO.update(param)
    try:
        base = fe.montar(e)
        out["piso"] = fe.piso(base)
        r = fe.verificar(e, progresso=progresso)
    finally:
        br.DESCANSO_POR_TURNO.clear()
    print(f"DESCANSO_POR_TURNO ao fim: {br.DESCANSO_POR_TURNO}", flush=True)
    from piso_pares import tempos
    seg = tempos(eventos)
    ind = r.indicadores or {}
    vistos = set()
    tent = []
    for q, status, ne, nt in r.tentativas:
        tent.append({"quadro": q, "status": status, "enfermeiros": ne, "tecnicos": nt,
                     "quem_provou": ("conta" if status == "piso" else
                                     "solver" if status in ("viavel", "inviavel") else "—"),
                     "segundos": None if q in vistos else seg.get(q)})
        vistos.add(q)
    out.update(
        frase=r.frase(), frase_vigente=r.frase_vigente() if r.escala else None,
        veredito=r.veredito, menor_viavel=r.menor_viavel,
        tentativas=[list(t) for t in r.tentativas], tentativas_detalhe=tent,
        diagnostico=({"motivo": r.diagnostico[0], "titulo": fe.TITULO.get(r.diagnostico[0]),
                      "frase": r.diagnostico[1]} if r.diagnostico else None),
        provado_etapa1=bool(ind.get("provado")), partes=ind.get("partes"),
        blocos=ind.get("blocos"), caminho=ind.get("caminho"), etapa2=ind.get("etapa2"),
        provado_etapa2=ind.get("provado_etapa2"), amplitude_etapa1=ind.get("amplitude_etapa1"),
        amplitude=ind.get("amplitude"), frase_equilibrio=fe.frase_equilibrio(r) if r.escala
        else None,
        frases_por_nivel=[f for _, f in fe.frases_por_nivel(r)] if r.escala else [],
        criterios=r.criterios, descumpridos=r.descumpridos, alertas_cofen=r.alertas,
        descanso_ok=(r.conformidade or {}).get("ok"), tempo_total_s=round(time.time() - t0, 1),
        progresso=eventos)
    SAIDA.mkdir(parents=True, exist_ok=True)

    def gravar():
        out["pico_memoria_mb"] = pico_mb()
        texto = json.dumps(out, ensure_ascii=False, indent=1, default=str)
        if param:   # primeira linha util do JSON: o rotulo (1o campo; o JSON continua valido)
            assert texto.splitlines()[1].strip().startswith('"aviso"')
        (SAIDA / f"{nome}.json").write_text(texto, encoding="utf-8")

    erros = out["erros_pos_solver"] = []

    def passo(rotulo, f):
        """Cada medicao depois do solver: o erro fica registrado e o JSON e regravado; o
        resultado do solver (ja gravado) nao se perde."""
        try:
            f()
        except Exception:  # noqa: BLE001
            erros.append(f"{rotulo}: {traceback.format_exc().splitlines()[-1]}")
            traceback.print_exc()
        gravar()

    if r.escala:
        out["escala_quadro"] = len(r.inst.profissionais)
        out["escala"] = sorted([str(d), r.inst.profissionais[n].nome, s] for d, n, s in r.escala)
    gravar()                                  # o resultado do solver, antes de qualquer medicao
    if r.escala:
        conf = {}

        def relogio():
            br.DESCANSO_POR_TURNO.update(param)
            try:
                out["menor_descanso_h"] = fase2.menor_descanso(r.inst, r.escala)
                conf["base"] = fe.montar(com_quadro(e, len(r.inst.profissionais), sum(
                    1 for p in r.inst.profissionais.values()
                    if br.HABILIDADE_ENF in p.habilidades)))
            finally:
                br.DESCANSO_POR_TURNO.clear()

        passo("medição na escala", lambda: out.update(medir_escala(r.inst, r.escala)))
        passo("descanso no relógio e instância de conferência", relogio)
        # (1) restricao dura: a instancia da rodada (pesos da classificacao) no avaliador oficial
        passo("avaliador (restrição dura)",
              lambda: out.update(avaliador=fase2.avaliador(r.inst, r.escala, SAIDA, nome)))

        # (2) por criterio, peso 1, com os criterios da classificacao ligados: no A36, os da
        # classificacao 2 (contem os da 1 e o max. fins de semana seguidos); no A11, os da 1. No
        # caso B nao ha criterio com conferencia externa no padrao: so a restricao dura (e o
        # avaliador do caso B e o que pesa na memoria).
        def conferencia():
            pn = pr.normalizar(classificacao(1 if param else 2))
            coef = {**{c.id: 1 for c in pr.CRITERIOS},
                    **{pr.REGRAS + x: 1 for x in pr.CONSIDERADOS}}
            unidade, _ = pr.aplicar(conf["base"], pn, coef, br.HABILIDADE_ENF)
            out["contagem_peso1"] = [list(x) for x in pr.resultado(unidade, r.escala, pn,
                                                                    br.HABILIDADE_ENF)]
            c = fase2.avaliador(unidade, r.escala, SAIDA, nome + "_conferencia")
            arq = SAIDA / f"{nome}_conferencia_escala_avaliador.txt"
            out["conferencia"] = {**c, **(_familias(arq, unidade) if arq.exists() else {})}

        if caso == "A":
            passo("conferência por critério (peso 1)", conferencia)
    print(f"{'[' + HIPOTESE + '] ' if param else ''}{nome}: {r.frase()} | menor viável "
          f"{r.menor_viavel} | avaliador: "
          f"{(out.get('avaliador') or {}).get('hard_constraints_violation', '-')} | "
          f"{out['tempo_total_s']:.0f} s", flush=True)
    return 0


# --- o mestre --------------------------------------------------------------------------------

def _resumo(linha: str) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    with open(RESUMO, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%d/%m %H:%M:%S')} | {linha}\n")
    print(linha, flush=True)


def rodar(retomar: bool) -> int:
    from bateria_solvers import _sem_suspensao, memoria_livre_mb
    _sem_suspensao()
    feitos = sorted(p.name for p in SAIDA.glob("*.json")) if SAIDA.exists() else []
    if feitos and not retomar:
        print(f"PARADO: {SAIDA} já tem {feitos}; para continuar, RETOMAR=1 (nada se sobrescreve)")
        return 1
    _resumo(f"INÍCIO ({'retomada' if retomar else 'primeira'}) — {versao()}")
    so = [x for x in os.environ.get("V145_SO", "").split(",") if x]
    for nome in RODADAS:
        if so and nome not in so:
            continue
        if (SAIDA / f"{nome}.json").exists():
            _resumo(f"{nome}: já feito (JSON gravado)")
            continue
        if RODADAS[nome][5] == "rodada1" and _rodada1() is None:
            _resumo(f"{nome}: PULADA — a rodada 1 não determinou o menor quadro")
            continue
        fim = time.time() + 60 * ESPERA_MIN
        livre = memoria_livre_mb()
        while livre < MEMORIA_MIN_MB and time.time() < fim:
            time.sleep(30)
            livre = memoria_livre_mb()
        if livre < MEMORIA_MIN_MB:
            _resumo(f"{nome}: PARADO (memória) — {livre} MB livres depois de {ESPERA_MIN} min "
                    f"(mínimo {MEMORIA_MIN_MB} MB); segue para a próxima")
            continue
        _resumo(f"{nome}: começando (memória livre {livre} MB)")
        t0 = time.time()
        with open(SAIDA / f"{nome}.log", "w", encoding="utf-8") as f:
            if RODADAS[nome][4]:
                f.write(HIPOTESE + "\n")
                f.flush()
            cod = subprocess.run([sys.executable, __file__, "--rodada", nome], stdout=f,
                                 stderr=subprocess.STDOUT, cwd=RAIZ,
                                 env={**os.environ, "PYTHONIOENCODING": "utf-8"}).returncode
        ultima = (SAIDA / f"{nome}.log").read_text(encoding="utf-8").strip().splitlines()[-1:]
        _resumo(f"{nome}: código {cod} | {time.time() - t0:.0f} s | {' '.join(ultima)}")
        if cod != 0 or not (SAIDA / f"{nome}.json").exists():
            _resumo(f"{nome}: PARADO (erro; ver {nome}.log); segue para a próxima")
    try:
        relatorio()
        _resumo("relatório automático escrito (rodadas/resultado_automatico.md)")
    except Exception:  # noqa: BLE001
        _resumo("relatório automático FALHOU: " + traceback.format_exc().splitlines()[-1])
    _resumo("FIM")
    return 0


# --- montagem sem solver e as contas do ESPERADO ----------------------------------------------

def montar() -> int:
    for nome, (caso, rod, k, imp, param, _) in RODADAS.items():
        e, obs = entrada(nome, exigir_rodada1=False)
        br.DESCANSO_POR_TURNO.clear()
        br.DESCANSO_POR_TURNO.update(param)
        try:
            inst = fe.montar(e)
            blocos = pr.planejar(inst, pr.normalizar(e.prioridades), br.HABILIDADE_ENF)
            piso = fe.piso(inst)
            bloq = sorted(fe.bloqueiam_o_dia_seguinte(inst))
        finally:
            br.DESCANSO_POR_TURNO.clear()
        ferias = Counter(inst.profissionais[n].nome for n, _ in inst.indisponiveis)
        print(f"{nome}: {'[' + HIPOTESE + '] ' if param else ''}início {e.inicio} "
              f"({e.inicio.strftime('%a')}), {len(inst.dias)} dias; quadro {e.quadro} "
              f"({e.n_enfermeiros} + {e.n_tecnicos}); linhas {len(e.regras)} "
              f"({sorted({l.importancia for l in e.regras})}); férias {dict(ferias)}; "
              f"blocos {[(b.niveis, b.maximo) for b in blocos]}; bloqueiam {bloq}; piso {piso}"
              f"{'; ' + obs if obs else ''}", flush=True)
    print(f"DESCANSO_POR_TURNO ao fim: {br.DESCANSO_POR_TURNO}")
    return 0


def esperado() -> int:
    mod = _modulo(PASTA_A, "entrada_a_v145_esp")
    for param in ({}, ONZE):
        for eq in (22, 23, 24):
            for ef in (0, 1):
                br.DESCANSO_POR_TURNO.clear()
                br.DESCANSO_POR_TURNO.update(param)
                try:
                    e = mod.entrada("turno_fixo", equipe=eq, enf_fds=ef)
                    inst = fe.montar(e)
                    p, pe = fe.pares_de_dias(inst), fe.pares_de_dias(inst, True)
                    piso = fe.piso(inst)
                finally:
                    br.DESCANSO_POR_TURNO.clear()
                print(f"{'11 h (hipótese)' if param else '36 h'} | equipe {eq} | enf. no plantão "
                      f"{ef} | par {fe.rotulo_dia(p[1])} + {fe.rotulo_dia(p[2])}: {p[3]} + {p[4]} "
                      f"= {p[3] + p[4]} contra {p[5]} (excesso {p[0]}) | só enf.: excesso {pe[0]} "
                      f"| piso {piso} | linhas {len(e.regras)}")
    e = mod.entrada("turno_fixo")
    for a in (5, 6, 7):
        print(f"composição com +{a}: {fe.equipe(e, a, fe._horas_enfermeiro(e))[:2]}")
    eb = _modulo(PASTA_B, "entrada_b_v145_esp").entrada()
    for param in ({}, ONZE):
        br.DESCANSO_POR_TURNO.clear()
        br.DESCANSO_POR_TURNO.update(param)
        try:
            inst = fe.montar(eb)
            print(f"B {'11 h (hipótese)' if param else '36 h'}: piso {fe.piso(inst)}; par "
                  f"{fe.pares_de_dias(inst)[:1]}")
        finally:
            br.DESCANSO_POR_TURNO.clear()
    return 0


# --- relatorio automatico (so le os JSON; o RELATORIO.md comenta este) ----------------------

def _sim(x) -> str:
    return "sim" if x else "não"


def relatorio() -> int:
    nome_id = {c.nome: c.id for c in pr.CRITERIOS}
    res = {n: json.loads((SAIDA / f"{n}.json").read_text(encoding="utf-8"))
           for n in RODADAS if (SAIDA / f"{n}.json").exists()}
    resumo = RESUMO.read_text(encoding="utf-8") if RESUMO.exists() else ""
    L = ["# Rodadas de 05/11 (v1.4.5) — resultado automático", "",
         "Gerado por `docs/diagnostico/caso_a_v145.py --relatorio`, só lendo os JSON desta pasta. "
         "O comentário contra o esperado está no `RELATORIO.md` da pasta de cima. **Tempo: limite "
         "operacional, não resultado** (máquina e solver em cada rodada).", "",
         "## Resumo do mestre", "", "```", resumo.strip(), "```", ""]
    for n in RODADAS:
        d = res.get(n)
        L.append(f"## {n}" + (f" — {HIPOTESE}" if RODADAS[n][4] else ""))
        L.append("")
        if d is None:
            L += ["Sem JSON: não rodou (ver o resumo acima).", ""]
            continue
        m = d.get("maquina") or {}
        L += [f"- Versão `{d.get('versao')}` (`{str(d.get('commit'))[:7]}`); `src/` alterado: "
              f"{_sim(d.get('src_alterado'))}; diferente da v1.4.5: {_sim(d.get('diff_src_v145'))}.",
              f"- Máquina: {m.get('cpu')}, {m.get('ram_gb')} GB; {m.get('solver')}; avaliador "
              f"Java {m.get('java_memoria')} {m.get('java_tool_options') or ''}. Memória livre antes: {d.get('memoria_livre_mb_antes')}"
              f" MB; pico: {d.get('pico_memoria_mb')} MB.",
              f"- Entrada: quadro {d['quadro_informado']} ({d['enfermeiros']} + {d['tecnicos']}); "
              f"classificação {d['classificacao']}; {d['n_linhas']} linhas"
              f"{' (' + str(d['importancia_linhas']) + ')' if d.get('importancia_linhas') else ''}"
              f"{'; ' + d['observacao'] if d.get('observacao') else ''}.",
              f"- **Frase da tela:** \"{d['frase']}\"",
              f"- Frase vigente: {d.get('frase_vigente')}; equilíbrio: {d.get('frase_equilibrio')}",
              f"- Piso (conta prévia): {d.get('piso')}; menor viável: {d.get('menor_viavel')}.",
              "- Tentativas: " + "; ".join(
                  f"{t['quadro']} {t['status']} ({t['quem_provou']}"
                  f"{', ' + str(t['enfermeiros']) + ' + ' + str(t['tecnicos']) if t['enfermeiros'] is not None else ''}"
                  f"{', ' + str(round(t['segundos'])) + ' s' if t.get('segundos') else ''})"
                  for t in d.get("tentativas_detalhe") or []) + ".",
              f"- Diagnóstico: {(d.get('diagnostico') or {}).get('titulo')} — "
              f"{(d.get('diagnostico') or {}).get('frase', '—')[:700]}",
              f"- Etapa 2: {d.get('etapa2')}; provada: {d.get('provado_etapa2')}; maior amplitude "
              f"etapa 1 → final: {d.get('amplitude_etapa1')} → {d.get('amplitude')}.",
              f"- Conferência de descanso no relógio: {d.get('descanso_ok')}; menor descanso (h): "
              f"{d.get('menor_descanso_h')}.",
              f"- Avaliador oficial, restrição dura: "
              f"{(d.get('avaliador') or {}).get('hard_constraints_violation', '— (sem escala)')}"
              f"{'; recusa: ' + str(d['avaliador'].get('recusa')) if (d.get('avaliador') or {}).get('recusa') else ''}.",
              f"- Tempo total: {d.get('tempo_total_s')} s (limite operacional; orçamento "
              f"{d.get('orcamento_s')} s).",
              f"- Erros depois do solver: {d.get('erros_pos_solver') or 'nenhum'}.", ""]
        if not d.get("partes"):
            continue
        coefs = {tuple(b[0]): b[1] for b in d.get("blocos") or []}
        L += ["| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do "
              "bloco: escala | Escala final |", "|---|---:|---:|---|---:|---:|---:|"]
        for p in d["partes"]:
            nv = p.get("niveis") or []
            coef = coefs.get(tuple(nv), {})
            final = sum(coef.get(pr.REGRAS + c[0] if c[1] == pr.NOME_REGRAS else nome_id.get(c[1]),
                                 0) * c[2] for c in d.get("criterios") or [] if c[0] in nv)
            L.append(f"| {' + '.join(nv)} | {p.get('limite')} | {round(p.get('tempo', 0), 1)} | "
                     f"{_sim(p.get('provado'))} | {p.get('valor_modelo', p.get('valor'))} | "
                     f"{p.get('valor')} | {final if coef else '—'} |")
        L += ["", *[f"- {f}" for f in d.get("frases_por_nivel") or []], "",
              "| Critério | Importância | Violações (ferramenta) | Avaliador oficial, peso 1 |",
              "|---|---|---:|---:|"]
        conf = (d.get("conferencia") or {}).get("por_familia") or {}
        fam_de = {c.nome: c.familia for c in pr.CRITERIOS}
        fam_de[pr.NOME_REGRAS] = "shift_off_requests"
        for c in d.get("criterios") or []:
            fam = fam_de.get(c[1])
            ext = ("sem conferência externa" if fam in (pr.CUSTO, None) or not d.get("conferencia")
                   else str(conf.get(fam, 0)))
            L.append(f"| {c[1]} | {c[0]} | {c[2]} | {ext} |")
        if d.get("contagem_peso1"):
            L += ["", "Conferência com peso 1 (critérios da classificação "
                  f"{'1' if RODADAS[n][4] else '2'} ligados): "
                  + "; ".join(f"{c[1]} {c[2]}" for c in d["contagem_peso1"])
                  + f". Avaliador oficial por família: {conf}."]
        desc = d.get("descumpridos") or []
        med = d.get("quebras_turno_fixo_medidas") or {}
        L += ["", "Quebras do turno fixo por profissional — pela ferramenta (nível, quantas): "
              + ("; ".join(f"{p} ({nv}, {q})" for nv, p, q in desc) or "nenhuma")
              + ". Medidas na escala, contra as 33 linhas da entrada (também na rodada sem "
              "linhas): " + ("; ".join(f"{p} {q}" for p, q in sorted(med.items())) or "nenhuma")
              + f" (total {sum(med.values())})."]
        L += ["", f"Enfermeiro em posto de técnico: 4 da unidade **{d.get('enf_posto_tec_unidade')}**"
              f", acrescidos **{d.get('enf_posto_tec_acrescidos')}**. Por enfermeiro: "
              + "; ".join(f"{x['nome']} ({x['origem']}) {x['turnos']} turnos, "
                          f"{x['em_posto_de_tecnico']} em posto de técnico"
                          for x in d.get("enfermeiros_detalhe") or []) + "."]
        pp = (d.get("conferencia") or {}).get("por_pessoa") or {}
        if pp:
            L += ["", "Por pessoa, avaliador oficial com peso 1 (férias: 6137 em 31/10–15/11, 5976 "
                  "em 15/11–25/11):"]
            for fam, rot, piso_inev in (("max_consecutive_free_days", "Máx. folgas seguidas (4)",
                                         {"Téc 6137": 12, "Téc 5976": 7}),
                                        ("min_num_assignments", "Mín. turnos (10)",
                                         {"Téc 5976": 2})):
                por = pp.get(fam, {})
                inev = sum(min(v, piso_inev.get(p, 0)) for p, v in por.items())
                L.append(f"- {rot}: total {sum(por.values())}; "
                         + (", ".join(f"{p} {v}{' (férias ' + FERIAS_DE[p] + ')' if p in FERIAS_DE else ''}"
                                      for p, v in sorted(por.items())) or "nenhuma")
                         + f". Inevitável pela conta do ESPERADO §4: {inev}"
                         f" ({', '.join(f'{p} ≥ {k}' for p, k in piso_inev.items())}"
                         f"{'; o do 5976 só com a linha Só N cumprida' if fam == 'min_num_assignments' else ''})"
                         f"; evitável: {sum(por.values()) - inev}.")
        L.append("")
    (SAIDA / "resultado_automatico.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--esperado", action="store_true")
    ap.add_argument("--montar", action="store_true")
    ap.add_argument("--rodada", choices=list(RODADAS))
    ap.add_argument("--rodar", action="store_true")
    ap.add_argument("--retomar", action="store_true")
    ap.add_argument("--relatorio", action="store_true")
    a = ap.parse_args()
    if a.rodada:
        try:
            sys.exit(rodada(a.rodada))
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            print(f"ERRO de código ou de entrada em {a.rodada}")
            sys.exit(1)
    sys.exit(esperado() if a.esperado else montar() if a.montar else
             rodar(a.retomar or os.environ.get("RETOMAR") == "1") if a.rodar else
             relatorio() if a.relatorio else 2)
