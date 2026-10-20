"""Parte 7 (20/10): testes do piso por pares de dias (`ferramenta.pares_de_dias`, v1.4.1).

Esperado registrado antes: `resultados/piso_pares_2026-10-20/ESPERADO.md`. Saida em
`resultados/piso_pares_2026-10-20/` (ou na pasta de `PISO_PARES_SAIDA`, para a suite).

    python docs\\diagnostico\\piso_pares.py --seguranca   # sem solver: rodadas registradas
    python docs\\diagnostico\\piso_pares.py --tela        # sem solver: entradas dos testes da tela
    python docs\\diagnostico\\piso_pares.py --controle    # sem solver: Parte 3, 22 recusa e 23 aceita
    python docs\\diagnostico\\piso_pares.py --casos       # sem solver: casos A e B, 36 h e D12 = 11 h
    python docs\\diagnostico\\piso_pares.py --sorteio     # COM solver, so porte pequeno
    python docs\\diagnostico\\piso_pares.py --extra       # sem solver: quadros provados pelo solver

"Piso antigo" = o mesmo `ferramenta.piso` com a conta por pares desligada (`sem_pares`): o que a
v1.4.0 calculava. A conta compartilha com o modelo a regra de descanso (os pares do mesmo
gerador): confere a aritmetica e a coerencia com o modelo, nao a leitura legal.
"""

from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import random
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "docs"), str(AQUI),
                str(RAIZ / "docs" / "demonstracao")]

import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402

_SAIDA = os.environ.get("PISO_PARES_SAIDA")
SAIDA = Path(_SAIDA) if _SAIDA else RAIZ / "resultados" / "piso_pares_2026-10-20"
SEMENTE = 20261020
SORTEIO = 40            # instancias do sorteio pequeno


@contextlib.contextmanager
def sem_pares():
    """`ferramenta.piso` e `motivos_da_trava` como na v1.4.0: a conta por pares nao dispara."""
    original = fe.pares_de_dias
    fe.pares_de_dias = lambda inst, so_enfermeiros=False: (0, None, None, 0, 0, 0, [])
    try:
        yield
    finally:
        fe.pares_de_dias = original


def pisos(e: fe.Entrada) -> tuple[int, int, list, list]:
    """(piso antigo, piso novo, motivos antigos, motivos novos) do quadro informado."""
    inst = fe.montar(e)
    with sem_pares():
        antigo, m_antigos = fe.piso(inst), [m for m, _ in fe.motivos_da_trava(inst)]
    return antigo, fe.piso(inst), m_antigos, [m for m, _ in fe.motivos_da_trava(inst)]


def _carregar(arq: Path) -> dict:
    d = json.loads(arq.read_text(encoding="utf-8"))
    for k in ("menor_viavel", "tentativas"):     # o nivel 3 gravou alguns campos como texto
        if isinstance(d.get(k), str):
            d[k] = None if d[k] == "None" else eval(d[k])  # noqa: S307 (arquivo do repositorio)
    return d


def _entrada_py(pasta: str):
    spec = importlib.util.spec_from_file_location(f"entrada_{pasta}",
                                                  RAIZ / "resultados" / pasta / "entrada.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rodadas():
    """(fonte, nome, Entrada, registro) de cada rodada registrada com resultado do solver."""
    import bateria_desenho as bd
    import bateria_nivel3 as n3
    import bateria_propriedades as bp
    import bateria_rodar as brr
    import caso_clinica_medica as cc
    import plantao12
    casos = {c.nome.split()[0]: c for c in bd.CASOS + bd.CONHECIDOS}
    for k in range(1, 19):
        nome = f"P{k:02d}"
        yield ("bateria v1.4.0", nome, brr.entrada(casos[nome]),
               _carregar(RAIZ / "resultados" / "v140_2026-10-20" / "bateria" / f"{nome}.json"))
    for k in range(1, 7):
        nome = f"K{k}"
        yield ("bateria 07/10", nome, brr.entrada(casos[nome]),
               _carregar(RAIZ / "resultados" / "bateria_2026-10-07" / f"{nome}.json"))
    for tec in (20, 19, 18):
        yield ("demonstração v1.4.0", f"demo{tec}", cc.entrada(tec),
               _carregar(RAIZ / "resultados" / "v140_2026-10-20" / "demo" / f"demo{tec}.json"))
    for d in n3.carregar():
        arq = RAIZ / "resultados" / "bateria_2026-10-08" / "parte4" / f"{d['nome']}.json"
        if arq.exists():
            yield "nível 3 (08/10)", d["nome"], brr.entrada(n3.caso(d)), _carregar(arq)
    for c in bp.TODOS:
        nome = c.nome.split()[0]
        for v in bp.VARIANTES:
            arq = RAIZ / "resultados" / "bateria_2026-10-08" / "parte3" / f"{nome}_{v}.json"
            if arq.exists():
                yield "propriedades (08/10)", f"{nome}_{v}", bp.derivar(c, v), _carregar(arq)
    yield ("Parte 3 (20/10)", "plantao12", plantao12.entrada(),
           {"menor_viavel": 23, "tentativas": [[22, "inviavel", 4, 18], [23, "viavel", 5, 18]],
            "veredito": "faltam"})


def seguranca() -> int:
    """Teste 1: em toda rodada registrada com quadro viavel, o piso novo <= esse quadro. Lista
    as tentativas que mudam (solver -> conta) e os motivos do diagnostico que mudam."""
    linhas = ["| Fonte | Caso | Quadro | Menor viável registrado | Piso antigo | Piso novo | "
              "Tentativas que passam à conta | Motivos (antigo → novo) | Resultado |",
              "|---|---|---:|---:|---:|---:|---|---|---|"]
    falhas = n = mudam = 0
    for fonte, nome, e, reg in rodadas():
        n += 1
        antigo, novo, m_a, m_n = pisos(e)
        menor = reg.get("menor_viavel")
        menor = int(menor) if menor not in (None, "None") else None
        ok = menor is None or novo <= menor
        falhas += not ok
        passam = [f"{t[0]} ({t[1]})" for t in reg.get("tentativas") or []
                  if t[1] != "piso" and t[0] < novo]
        if novo != antigo or m_a != m_n or not ok:
            mudam += 1
            linhas.append(f"| {fonte} | {nome} | {e.quadro} | {menor} | {antigo} | {novo} | "
                          f"{', '.join(passam) or '—'} | "
                          f"{m_a if m_a == m_n else f'{m_a} → {m_n}'} | "
                          f"{'ok' if ok else 'FALHA: recusa quadro viável'} |")
    texto = [f"# Teste 1 — segurança do piso por pares ({n} rodadas registradas)", "",
             f"Só as rodadas em que algo muda ({mudam}); nas outras {n - mudam}, piso e motivos "
             f"iguais aos da v1.4.0.", "", *linhas, "",
             "TUDO OK: nenhum quadro viável recusado" if not falhas
             else f"{falhas} FALHA(S): quadro viável recusado"]
    _gravar("seguranca.md", texto)
    return 1 if falhas else 0


def tela() -> int:
    """As entradas que os testes da tela passam a `ferramenta.verificar`, colhidas sem solver
    (verificar, resolver_com_objetivo e resolver_instancia trocados por gravadores). Os testes
    em si falham aqui — so as entradas interessam. Piso antigo x novo em cada uma."""
    import testes_ferramenta as tf
    vistas = []

    def verificar(e, *a, **k):
        vistas.append((caso_atual[0], e))
        return fe.Resultado(veredito=fe.NAO_DECIDIDO, quadro_informado=e.quadro,
                            menor_viavel=None, alertas=[], tentativas=[])

    caso_atual = [""]
    fe.verificar = verificar
    fe.resolver_com_objetivo = lambda inst, *a, **k: (ea.INDETERMINADO, inst, None, {})
    ea.resolver_instancia = lambda inst, *a, **k: (ea.INDETERMINADO, None, None)
    with open(os.devnull, "w", encoding="utf-8") as nulo:
        for nome, func in tf.CASOS.items():
            caso_atual[0] = nome
            with contextlib.redirect_stdout(nulo):
                try:
                    func()
                except Exception:  # noqa: BLE001 — o caso para no primeiro uso do resultado
                    pass
    linhas = ["| Teste | Quadro | Piso antigo | Piso novo | Motivos (antigo → novo) |",
              "|---|---:|---:|---:|---|"]
    mudam = 0
    por_teste = {}
    for nome, e in vistas:
        por_teste[nome] = por_teste.get(nome, 0) + 1
        try:
            antigo, novo, m_a, m_n = pisos(e)
        except ValueError:
            continue                      # entrada errada de proposito (teste de erro)
        if antigo != novo or m_a != m_n:
            mudam += 1
            linhas.append(f"| {nome} | {e.quadro} | {antigo} | {novo} | {m_a} → {m_n} |")
    texto = [f"# Testes da tela — entradas colhidas sem solver: {len(vistas)}", "",
             "Entradas por teste: " + ", ".join(f"{k} {v}" for k, v in por_teste.items()), "",
             "Testes sem entrada colhida chamam o solver por outro caminho ou montam a "
             "instância direto; a suíte os roda inteiros.", "",
             f"Entradas em que o piso ou os motivos mudam: {mudam}", "", *linhas]
    _gravar("tela.md", texto)
    print(f"{len(vistas)} entradas; {mudam} com piso ou motivos diferentes")
    return 0


def controle() -> int:
    """Teste 3: Parte 3 (so tecnicos, sem ferias) — 22 recusado pela conta, 23 aceito."""
    import plantao12
    e = plantao12.entrada()
    inst22, inst23 = fe.montar(e), fe.montar(e, 1)
    total22, total23 = fe.pares_de_dias(inst22), fe.pares_de_dias(inst23)
    ok = fe.piso(inst22) == 23 and total22[0] == 1 and total22[3:6] == (14, 9, 22) \
        and total23[0] <= 0 and fe.piso(inst23) <= 23
    texto = ["# Teste 3 — controle (Parte 3)", "",
             f"- 22: piso {fe.piso(inst22)}; pior par {fe.rotulo_dia(total22[1])} e "
             f"{fe.rotulo_dia(total22[2])}: {total22[3]} + {total22[4]} > {total22[5]} "
             f"(excesso {total22[0]})",
             f"- 23: piso {fe.piso(inst23)}; pior par excesso {total23[0]} (aceito pela conta)",
             "", "OK" if ok else "FALHA"]
    _gravar("controle.md", texto)
    return 0 if ok else 1


ESPERADO_CASOS = {   # (regra, caso): (piso, excesso total, excesso de enfermeiros, recusa?)
    ("36 h", "A turno fixo"): (30, 6, 1, True), ("36 h", "A rodízio livre"): (30, 6, 1, True),
    ("36 h", "B"): (105, 16, -1, True),
    ("D12 = 11 h", "A turno fixo"): (None, 0, 0, False),
    ("D12 = 11 h", "A rodízio livre"): (None, 0, 0, False),
    ("D12 = 11 h", "B"): (None, -5, -3, False),
}


def casos() -> int:
    """Teste 4: casos A e B sem solver (montar + piso), na regra do produto e sob D12 = 11 h
    (HIPOTESE DE SENSIBILIDADE — NAO REGRA DA FERRAMENTA; o parametro volta vazio)."""
    a, b = _entrada_py("caso_a_2026-10-20"), _entrada_py("caso_b_2026-10-20")
    entradas = {"A turno fixo": a.entrada("turno_fixo"), "A rodízio livre": a.entrada("rodizio_livre"),
                "B": b.entrada()}
    texto, falhas = ["# Teste 4 — casos A e B sem solver", ""], 0
    try:
        for regra, param in (("36 h", {}), ("D12 = 11 h", {"D12": 11})):
            br.DESCANSO_POR_TURNO.clear()
            br.DESCANSO_POR_TURNO.update(param)
            if param:
                texto.append("HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA")
            for nome, e in entradas.items():
                inst = fe.montar(e)
                p, tot, enf = fe.piso(inst), fe.pares_de_dias(inst), fe.pares_de_dias(inst, True)
                esp_piso, esp_tot, esp_enf, recusa = ESPERADO_CASOS[(regra, nome)]
                ok = (tot[0] == esp_tot and enf[0] == esp_enf and (p > e.quadro) == recusa
                      and (esp_piso is None or p == esp_piso))
                falhas += not ok
                texto.append(f"- {regra}, {nome} ({e.quadro}): piso {p}; pior par "
                             f"{fe.rotulo_dia(tot[1])} e {fe.rotulo_dia(tot[2])}: {tot[3]} + "
                             f"{tot[4]} contra {tot[5]} disponíveis (excesso {tot[0]}); "
                             f"enfermeiros {enf[3]} + {enf[4]} contra {enf[5]} (excesso {enf[0]})"
                             f"; bloqueiam o dia seguinte: {sorted(fe.bloqueiam_o_dia_seguinte(inst))}"
                             f" — {'ok' if ok else 'FALHA'}")
        br.DESCANSO_POR_TURNO.clear()             # a regra do produto (36 h) de novo
        if fe.piso(fe.montar(entradas["B"])) <= entradas["B"].quadro + fe.MARGEM:
            raise RuntimeError("B: a conta nao recusa a faixa inteira; verificar chamaria o solver")
        r = fe.verificar(entradas["B"])           # todos os quadros caem na conta: sem solver
        ok = r.veredito == fe.SEM_VIAVEL and all(t[1] == "piso" for t in r.tentativas)
        falhas += not ok
        texto.append(f"- 36 h, B pela ferramenta: {r.frase()} (tentativas: "
                     f"{len(r.tentativas)}, todas pela conta: "
                     f"{all(t[1] == 'piso' for t in r.tentativas)}) — {'ok' if ok else 'FALHA'}")
    finally:
        br.DESCANSO_POR_TURNO.clear()
    texto += ["", f"DESCANSO_POR_TURNO ao fim: {br.DESCANSO_POR_TURNO}", "",
              "OK" if not falhas else f"{falhas} FALHA(S)"]
    _gravar("casos.md", texto)
    return 1 if falhas else 0


# --- teste 2: sorteio pequeno, com solver -------------------------------------------------------

def sortear(rng: random.Random) -> fe.Entrada:
    """Instancia pequena: turnos de 6 h e de 12 h (M, T, N 12 h, as vezes D12), 7 a 14 dias,
    demanda baixa com picos depois de dias de 12 h, ferias em metade dos casos."""
    turnos = [("M", 7, 13), ("T", 13, 19), ("N", 19, 7)]
    if rng.random() < 0.6:
        turnos.append(("D12", 7, 19))
    dias = rng.randint(7, 14)
    inicio = date(2027, 1, 4) + timedelta(days=7 * rng.randint(0, 8))
    zero = {s: (0, 0) for s, _, _ in turnos}
    grade = {}
    for k in range(dias):
        d = inicio + timedelta(days=k)
        for s, _, _ in turnos:
            if s == "D12" and d.weekday() < 5 and rng.random() < 0.7:
                continue
            grade[(d, s, "enf")] = rng.choice((0, 0, 1))
            grade[(d, s, "tec")] = rng.choice((0, 1, 1, 2))
    n_enf, n_tec = 1, rng.randint(0, 2)
    ferias = []
    if rng.random() < 0.5:
        a = rng.randint(0, dias - 2)
        ferias.append(("0", inicio + timedelta(days=a),
                       inicio + timedelta(days=min(dias - 1, a + rng.randint(0, 3)))))
    e = fe.Entrada(turnos=turnos, grau="intermediario", n_enfermeiros=n_enf, n_tecnicos=n_tec,
                   demanda_turno=zero, demanda_data=grade, inicio=inicio,
                   indisponibilidades=ferias)
    return e, dias


def sorteio() -> int:
    """Teste 2: o solver acha o menor quadro viavel (com o piso ANTIGO, para a busca nao usar a
    conta testada); afirma piso novo <= menor viavel em todas. Etapa 2 desligada."""
    import bateria_propriedades as bp
    bp.so_etapa1()
    rng = random.Random(SEMENTE)
    br_construir = br.construir
    linhas = ["| # | Dias | Turnos | Férias | Piso antigo | Piso novo | Menor viável (solver) | "
              "Tentativas no solver | Resultado |", "|---|---:|---|---|---:|---:|---:|---|---|"]
    falhas = decididos = apertou = justos = 0
    t0 = time.time()
    for i in range(SORTEIO):
        e, dias = sortear(rng)
        fe_dias = dias

        def construir(*a, fe_dias=fe_dias, **k):
            k.setdefault("dias", fe_dias)
            return br_construir(*a, **k)

        br.construir = construir           # o horizonte do sorteio (a Entrada nao tem `dias`)
        try:
            antigo, novo, _, _ = pisos(e)
            with sem_pares():
                r = fe.verificar(e, tempo=60, margem=20, orcamento=600)
        finally:
            br.construir = br_construir
        menor = r.menor_viavel
        ok = menor is None or novo <= menor
        decidido = menor is not None and all(t[1] in ("piso", ea.INVIAVEL, ea.VIAVEL)
                                             for t in r.tentativas)
        decididos += decidido
        apertou += novo > antigo
        justos += decidido and novo == menor and novo > antigo
        falhas += not ok
        linhas.append(f"| {i + 1} | {dias} | {'/'.join(t[0] for t in e.turnos)} | "
                      f"{'sim' if e.indisponibilidades else 'não'} | {antigo} | {novo} | {menor} | "
                      f"{[(t[0], t[1]) for t in r.tentativas if t[1] != 'piso']} | "
                      f"{'ok' if ok else 'FALHA'}{'' if decidido else ' (não decidido)'} |")
    texto = [f"# Teste 2 — sorteio pequeno (semente {SEMENTE}, {SORTEIO} instâncias)", "",
             "Turnos M 7–13, T 13–19, N 19–7 (12 h) e, em 60%, D12 7–19; 7 a 14 dias; equipe "
             "informada de 1 enfermeiro e 0 a 2 técnicos, subindo até achar escala (margem 20); "
             "férias de um enfermeiro em metade. Busca com o piso ANTIGO; etapa 2 desligada; "
             "60 s por resolução. HiGHS; tempo é limite operacional.", "",
             f"Decididas pelo solver: {decididos} de {SORTEIO}. A conta nova sobe o piso em "
             f"{apertou}; nelas, o piso novo é igual ao menor viável em {justos}.", "",
             *linhas, "", f"Tempo total: {time.time() - t0:.0f} s", "",
             "TUDO OK: piso novo <= menor viável em todas" if not falhas
             else f"{falhas} FALHA(S)"]
    _gravar("sorteio.md", texto)
    return 1 if falhas or decididos < SORTEIO // 2 else 0


# --- item extra: quadros que o solver teve de provar inviaveis --------------------------------

_LINHA = re.compile(r"\[\s*([\d.]+) s\] (.*)")
_QUADRO = re.compile(r"(\d+) profissionais")


def tempos(progresso: list[str]) -> dict[int, float]:
    """Segundos de solver por quadro, das linhas de progresso (soma das composicoes)."""
    eventos = []
    for linha in progresso:
        m = _LINHA.search(linha)
        if m:
            q = _QUADRO.search(m.group(2))
            solver = "etapa 1" in m.group(2) or "testando quadro" in m.group(2)
            eventos.append((float(m.group(1)), int(q.group(1)) if q and solver else None))
    saida: dict[int, float] = {}
    for (t, q), (t2, _) in zip(eventos, eventos[1:]):
        if q is not None:
            saida[q] = saida.get(q, 0.0) + t2 - t
    return saida


def extra() -> int:
    """Leitura, sem codigo novo na ferramenta: os quadros provados inviaveis pelo SOLVER (sem a
    conta previa) nas rodadas registradas, com o tempo de cada um, e se a conta nova os recusa."""
    linhas = ["| Fonte | Caso | Quadro provado inviável pelo solver | Tempo de solver (s) | "
              "Recusado pela conta nova? |", "|---|---|---:|---:|---|"]
    n = 0
    for fonte, nome, e, reg in rodadas():
        tent = reg.get("tentativas") or []
        viaveis = {t[0] for t in tent if t[1] == ea.VIAVEL}   # 2a composicao viavel: nao conta
        inv = sorted({t[0] for t in tent if t[1] == ea.INVIAVEL} - viaveis)
        if not inv:
            continue
        prog = reg.get("progresso")
        if prog is None:
            log = RAIZ / "resultados" / "bateria_2026-10-08" / "parte4" / f"{nome}.log"
            prog = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
        seg = tempos(prog)
        novo = pisos(e)[1]
        for q in inv:
            n += 1
            linhas.append(f"| {fonte} | {nome} | {q} | "
                          f"{f'{seg[q]:.1f}' if q in seg else 'não registrado'} | "
                          f"{'sim' if q < novo else 'não'} |")
    texto = ["# Item extra — quadros provados inviáveis pelo solver, sem conta prévia", "",
             f"{n} quadros. Tempo: soma das composições do quadro, das linhas de progresso "
             "(máquina do Otávio, HiGHS 1.15.1, 600 s por resolução nas rodadas de 07–08/10 e "
             "nas a2; limite operacional, não resultado).", "", *linhas]
    _gravar("extra.md", texto)
    return 0


def _gravar(nome: str, texto: list[str]) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / nome).write_text("\n".join(texto) + "\n", encoding="utf-8")
    print("\n".join(texto[-30:]))


def main() -> int:
    acoes = {"--seguranca": seguranca, "--tela": tela, "--controle": controle,
             "--casos": casos, "--sorteio": sorteio, "--extra": extra}
    return acoes[sys.argv[1]]()


if __name__ == "__main__":
    raise SystemExit(main())
