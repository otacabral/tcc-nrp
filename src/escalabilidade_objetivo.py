"""Curva de escalabilidade COM OBJETIVO NAO TRIVIAL — P1 do `PROPOSTAS.md` (Etapa 4).

Roda da raiz do repositorio, com a .venv ativa:

    python src\\escalabilidade_objetivo.py                  # 36, 40, 60, 80, 120, 200
    python src\\escalabilidade_objetivo.py --n 40           # so esse
    python src\\escalabilidade_objetivo.py --tempo 900      # limite POR ETAPA, em segundos
    python src\\escalabilidade_objetivo.py --equivalencia   # caminho novo x antigo, N=36 e 40
    python src\\escalabilidade_objetivo.py --folga          # rodada complementar, equipe +10%

Saida: `resultados/escalabilidade_objetivo.csv`, gravado a cada tamanho concluido, e o log
do HiGHS de cada etapa em `resultados/escalabilidade_objetivo/highs_N<n>_etapa<k>.log`.

## O que muda em relacao a `escalabilidade.py`

**Caminho das instancias (decisao do Otavio, 03/10): o da FERRAMENTA.** Cada tamanho e
montado pela mesma funcao que a tela usa (`ferramenta.montar`: turnos 12x36 de 7h-19h e
19h-7h, demanda por turno, carga contratual de 44 h para todos), com a demanda por turno e a
composicao (enfermeiros + tecnicos) IGUAIS as que o caminho antigo
(`escalabilidade.construir`: 12x36, grau intermediario, porte escolhido para o piso cair em
N) gera para aquele tamanho — `construir` confere a igualdade da demanda dia a dia. O caminho
antigo fica intacto para o Experimento A. Motivo: a etapa 2 equilibra a fracao do contrato,
e as instancias do caminho antigo nao tem carga contratual — a rodada de 03/10 14:29 morreu
na primeira etapa 2 por isso.

**Teste de equivalencia** (`--equivalencia`). Esperado registrado ANTES de rodar (03/10): em
N = 36 e N = 40, a viabilidade pelo caminho novo e a mesma do caminho antigo, resolvendo so
as rigidas (sem objetivo), limite de 900 s cada:
- N = 36 (12 + 24, 1 + 8 por turno, demanda constante): VIAVEL nos dois. E a ancora do
  Experimento A — 36 viavel com demanda constante.
- N = 40 (14 + 26, 1 + 9 por turno, demanda constante): VIAVEL nos dois, como o caminho
  antigo deu na curva de escalabilidade (otimo provado).
- Conta, sem solver: demanda do caminho novo = a do antigo em cada (dia, turno); e o piso da
  ferramenta (`ferramenta.piso`) = N nos dois tamanhos (a alternancia soma dois dias: 2 x 18 =
  36 e 2 x 20 = 40; as horas, 6.048 h e 6.720 h, cabem em N x 176 h).
Diferencas declaradas entre os caminhos: o novo tem teto de 176 h (o antigo, 14 plantoes =
168 h, e o novo mantem MaxNumAssignments = 14); as regras de descanso do novo sao geradas dos
horarios. Nos dois, com 12 h, ninguem passa de 14 plantoes (9b-sem-teto, 03/10).

**Rodada complementar COM FOLGA** (`--folga`; decisao do Otavio, 05/10). Na curva principal
a demanda e 14N plantoes, a capacidade exata de N pessoas: todo mundo faz 168 h e a etapa 2
e degenerada (amplitude 0 ja na etapa 1). A rodada complementar usa a MESMA demanda dos
tamanhos 40, 60 e 80 com equipe 10% maior (44, 66 e 88), cada categoria arredondada a
partir de 1,1 x a do caminho antigo (40: 14 + 26 -> 15 + 29; 60: 20 + 40 -> 22 + 44; 80:
27 + 53 -> 30 + 58), 44 h, 2 pedidos por pessoa com a mesma semente (SEMENTE + N, N o
tamanho da demanda). Registra, alem do de sempre: amplitude por categoria antes e depois da
etapa 2 e o tempo em que a etapa 2 chegou a 90% da reducao final, lido do log do HiGHS
(primeira linha da arvore com melhor solucao <= amplitude da etapa 1 - 0,9 x reducao).
Saida: `resultados/escalabilidade_objetivo_folga.csv`; logs `highs_N<n>_E<equipe>_etapa<k>.log`.

O modelo e o mesmo (`ea.modelo_br`, as mesmas opcoes da ferramenta). Muda:

- **pedidos de folga sinteticos**: 2 por profissional, em datas distintas sorteadas com
  `random.Random(SEMENTE + N)` — a semente esta registrada abaixo, e cada tamanho tem a sua
  sequencia, reproduzivel sozinho com `--n`;
- **o objetivo completo da ferramenta** (DECISOES.md, "Redesenho"): etapa 1 com pesos
  inteiros (`ferramenta.pesos`: enfermeiro em posto de tecnico custa 1, pedido negado custa
  W); etapa 2 com a penalidade presa no otimo, minimizando a amplitude da fracao do
  contrato cumprida DENTRO de cada categoria — enfermeiros + tecnicos
  (`ferramenta.preparar_equilibrio`; DECISOES.md, "Carga por contrato", P6 decidida em
  03/10). Como na ferramenta, a etapa 2 so roda se a etapa 1 provou otimalidade.

Com isso o limite inferior deixa de ser zero por construcao, e a prova de otimalidade passa
a custar alguma coisa — e isso que a P1 queria medir.

Por etapa registra-se: estado do solver, se provou otimalidade, gap ao fim, tempo de relogio
e **tempo ate a primeira escala legal** — lido do log do HiGHS (primeira linha da arvore com
solucao finita, na coluna de tempo do proprio HiGHS). Toda solucao do modelo e legal: a CLT
esta nas restricoes rigidas.

Tempo de resolucao e LIMITE OPERACIONAL, nao resultado (CLAUDE.md): registra-se com a
maquina e o solver nomeados. O que interessa e se a prova fecha.
"""

from __future__ import annotations

import argparse
import dataclasses
import math
import platform
import random
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import escalabilidade as esc  # noqa: E402
import experimento_a as ea  # noqa: E402
import ferramenta as fe  # noqa: E402
import instancia_br as br  # noqa: E402
import modelo  # noqa: E402
import solucao  # noqa: E402
from instancia import Pedido  # noqa: E402
from tabela import mesclar_csv  # noqa: E402

SAIDA = RAIZ / "resultados" / "escalabilidade_objetivo.csv"
SAIDA_FOLGA = RAIZ / "resultados" / "escalabilidade_objetivo_folga.csv"
TAMANHOS_FOLGA = [40, 60, 80]
FOLGA = 1.10
ESCALAS = RAIZ / "resultados" / "escalabilidade_objetivo"

SEMENTE = 20261002         # data da rodada; cada tamanho usa SEMENTE + N
PEDIDOS_POR_PESSOA = 2

# linha da arvore do HiGHS: "Src Proc. InQueue | Leaves Expl. | BestBound BestSol Gap | ...
# Time". O BestSol e o 7o campo depois da letra de origem (opcional); o tempo, o ultimo.
_LINHA_ARVORE = re.compile(
    r"^\s*[A-Za-z]?\s+\d+\s+\d+\s+\d+\s+[\d.]+%\s+(\S+)\s+(\S+)\s+.*?([\d.]+)s\s*$")


TURNOS_12X36 = fe.MODELOS[next(k for k in fe.MODELOS if k.startswith("12"))]


def construir(n: int, equipe: int | None = None):
    """A instancia do tamanho `n` pelo caminho da FERRAMENTA, com a demanda por turno e a
    composicao do caminho antigo (`escalabilidade.construir`). Falha alto se a demanda nao
    for constante no caminho antigo ou nao sair igual no novo."""
    antiga = esc.construir(n)
    d0 = antiga.dias[0]
    por_turno = {s: (antiga.demanda_de(d0, f"{s}E"), antiga.demanda_de(d0, s))
                 for s in ("D", "N")}
    for d in antiga.dias:
        for s, (enf, tec) in por_turno.items():
            if (antiga.demanda_de(d, f"{s}E"), antiga.demanda_de(d, s)) != (enf, tec):
                raise RuntimeError(f"N={n}: demanda do caminho antigo nao e constante em {d}")
    n_enf = sum(1 for p in antiga.profissionais.values() if br.HABILIDADE_ENF in p.habilidades)
    n_tec = len(antiga.profissionais) - n_enf
    if equipe is not None:      # rodada com folga: cada categoria escalada e arredondada
        n_enf = round(n_enf * equipe / n)
        n_tec = equipe - n_enf
    e = fe.Entrada(turnos=TURNOS_12X36, grau="intermediario", n_enfermeiros=n_enf,
                   n_tecnicos=n_tec, demanda_turno=por_turno, inicio=antiga.inicio)
    inst = fe.montar(e)
    for d in antiga.dias:
        for s in antiga.turnos:
            if inst.demanda_de(d, s) != antiga.demanda_de(d, s):
                raise RuntimeError(f"N={n}: demanda nova != antiga em {d}, {s}")
    if set(inst.turnos) != set(antiga.turnos) or len(inst.profissionais) != (equipe or n):
        raise RuntimeError(f"N={n}: turnos ou equipe diferem do caminho antigo")
    return inst


def equivalencia(solver: str, tempo: int) -> int:
    """Esperado no docstring do modulo, registrado antes de rodar."""
    falhas = 0
    for n in (36, 40):
        antiga, nova = esc.construir(n), construir(n)
        p = fe.piso(nova)
        print(f"### N={n}: piso da ferramenta no caminho novo = {p} (esperado {n}) | "
              f"carga {sorted(set(nova.carga_semanal_h.values()))} h | MaxNumAssignments "
              f"{nova.contratos['0'].max_num_assignments.valor}", flush=True)
        falhas += p != n
        vereditos = {}
        for nome, inst in (("antigo", antiga), ("novo", nova)):
            t0 = time.time()
            v, _, escala = ea.resolver_instancia(inst, solver, tempo)
            ok = escala is not None and not solucao.conferir_rigidas(
                inst, escala, habilidade_rigida=True)
            vereditos[nome] = v
            print(f"### N={n} caminho {nome}: {v} ({time.time() - t0:.0f} s) | rigidas "
                  f"{'ok' if ok else '-'}", flush=True)
        igual = vereditos["antigo"] == vereditos["novo"] == ea.VIAVEL
        falhas += not igual
        print(f"   {'ok   ' if igual else 'FALHA'} N={n}: antigo {vereditos['antigo']}, novo "
              f"{vereditos['novo']} (esperado viavel nos dois)", flush=True)
    print("equivalencia OK" if not falhas else f"{falhas} FALHA(S)")
    return 1 if falhas else 0


def com_pedidos(inst, n: int):
    """2 pedidos de folga por profissional, em datas distintas sorteadas. Peso 1 aqui;
    `ferramenta.pesos` troca pelo W, como faz na tela."""
    rng = random.Random(SEMENTE + n)
    pedidos = []
    for p in sorted(inst.profissionais, key=modelo._chave):
        for d in sorted(rng.sample(list(inst.dias), PEDIDOS_POR_PESSOA)):
            pedidos.append(Pedido(tipo="folga_dia", profissional=p, data=d, peso=1))
    return dataclasses.replace(inst, pedidos=tuple(pedidos))


def primeira_solucao_s(log: str) -> float | None:
    """Tempo do HiGHS na primeira linha da arvore com melhor solucao finita."""
    for linha in log.splitlines():
        achou = _LINHA_ARVORE.match(linha)
        if achou:
            try:
                melhor = float(achou.group(2))
            except ValueError:
                continue
            if math.isfinite(melhor):
                return float(achou.group(3))
    return None


def trajetoria(log: str) -> list[tuple[float, float]]:
    """(tempo do HiGHS, melhor solucao) em cada linha da arvore com solucao finita."""
    pontos = []
    for linha in log.splitlines():
        achou = _LINHA_ARVORE.match(linha)
        if achou:
            try:
                melhor = float(achou.group(2))
            except ValueError:
                continue
            if math.isfinite(melhor):
                pontos.append((float(achou.group(3)), melhor))
    return pontos


def tempo_ate_fracao(log: Path, inicio: float, final: float,
                     fracao: float = 0.9) -> float | None:
    """Tempo do HiGHS em que a melhor solucao da etapa 2 chegou a `fracao` da reducao final
    (de `inicio`, a amplitude da escala da etapa 1, a `final`). None se nao houve reducao ou
    o log nao mostra."""
    if not log.exists() or inicio - final <= 1e-9:
        return None
    alvo = inicio - fracao * (inicio - final) + 1e-6
    for t, melhor in trajetoria(log.read_text(encoding="utf-8", errors="replace")):
        if melhor <= alvo:
            return t
    return None


def _resolver(m, solver: str, tempo: int, log: Path) -> dict:
    """Resolve com o log do HiGHS em `log` e devolve o que a P1 registra. Nunca levanta."""
    log.parent.mkdir(parents=True, exist_ok=True)
    log.unlink(missing_ok=True)
    t0 = time.time()
    try:
        resultado = modelo.resolver(m, solver=solver, tempo_limite=tempo, carregar=False,
                                    log_arquivo=str(log))
    except Exception as e:  # noqa: BLE001
        return {"estado": f"erro: {type(e).__name__}: {e}", "resultado": None,
                "relogio_s": round(time.time() - t0, 1), "otimo": False, "gap": "",
                "primeira_s": None}
    return {"estado": modelo.estado(resultado), "resultado": resultado,
            "relogio_s": round(time.time() - t0, 1),
            "otimo": modelo.provou_otimo(resultado),
            "gap": esc.folga_relativa(resultado),
            "primeira_s": primeira_solucao_s(log.read_text(encoding="utf-8", errors="replace")
                                             if log.exists() else "")}


def _registrar(linha: dict, etapa: str, r: dict) -> None:
    linha.update({f"{etapa}_estado": r["estado"], f"{etapa}_otimo": r["otimo"],
                  f"{etapa}_gap": r["gap"], f"{etapa}_relogio_s": r["relogio_s"],
                  f"{etapa}_primeira_escala_s": r["primeira_s"]})
    print(f"   ### {etapa}: {r['estado']} | provou otimo: {'sim' if r['otimo'] else 'NAO'} | "
          f"gap {r['gap'] or '-'} | relogio {r['relogio_s']} s | primeira escala legal "
          f"{r['primeira_s'] if r['primeira_s'] is not None else '-'} s (HiGHS)", flush=True)


def rodar(n: int, solver: str, tempo: int, equipe: int | None = None) -> dict:
    inst = construir(n, equipe)
    tag = f"N{n}" if equipe is None else f"N{n}_E{equipe}"
    p = fe.piso(inst)
    if p != n:
        raise RuntimeError(f"N={n}: piso deu {p}, esperado {n} — a escala de demanda quebrou")
    inst, custo, W = fe.pesos(com_pedidos(inst, n))
    m = ea.modelo_br(inst, custo)
    d = modelo.dimensao(m)
    print(f"\n### N = {n:3d}, equipe {len(inst.profissionais)}: {len(inst.pedidos)} pedidos, W = {W}, {d['variaveis']} "
          f"variaveis, {d['restricoes']} restricoes", flush=True)

    linha = {"N": n, "equipe": len(inst.profissionais), "caminho": "ferramenta (44 h)", "pedidos": len(inst.pedidos), "peso_pedido": W, "semente": SEMENTE + n,
             "variaveis": d["variaveis"], "restricoes": d["restricoes"], "limite_s": tempo,
             "solver": solver}

    # etapa 1: pesos inteiros
    r1 = _resolver(m, solver, tempo, ESCALAS / f"highs_{tag}_etapa1.log")
    _registrar(linha, "etapa1", r1)
    if r1["resultado"] is None or not modelo.tem_solucao(r1["resultado"]) \
            or not modelo.carregar_solucao(m, r1["resultado"]):
        linha["etapa2_estado"] = "nao rodou (etapa 1 sem escala)"
        print("   ### sem escala na etapa 1", flush=True)
        return linha
    escala = modelo.atribuicoes(m)
    z = modelo.valor_objetivo(m)
    linha.update(penalidade=z, amplitude_etapa1=fe.amplitude(inst, escala),
                 **{f"amplitude_{g}_etapa1": c["amplitude"]
                    for g, c in fe.por_categoria(inst, escala).items()})

    # etapa 2: equilibrio de horas, so com a etapa 1 provada otima (como na ferramenta)
    if not r1["otimo"]:
        linha["etapa2_estado"] = "nao rodou (etapa 1 sem prova)"
    else:
        fe.preparar_equilibrio(m, inst, z)
        log2 = ESCALAS / f"highs_{tag}_etapa2.log"
        r2 = _resolver(m, solver, tempo, log2)
        _registrar(linha, "etapa2", r2)
        if r2["resultado"] is not None and modelo.tem_solucao(r2["resultado"]) \
                and modelo.carregar_solucao(m, r2["resultado"]):
            escala = modelo.atribuicoes(m)
            linha["amplitude_etapa2"] = fe.amplitude(inst, escala)
            linha.update({f"amplitude_{g}_etapa2": c["amplitude"]
                          for g, c in fe.por_categoria(inst, escala).items()})
            linha["etapa2_90pct_s"] = tempo_ate_fracao(log2, linha["amplitude_etapa1"],
                                                       linha["amplitude_etapa2"])
            print(f"   ### etapa 2: amplitude {linha['amplitude_etapa1']:.2%} -> "
                  f"{linha['amplitude_etapa2']:.2%} | por categoria "
                  + " | ".join(f"{g} {linha[f'amplitude_{g}_etapa1']:.2%} -> "
                               f"{linha[f'amplitude_{g}_etapa2']:.2%}"
                               for g in (fe.ENF, fe.TEC) if f"amplitude_{g}_etapa2" in linha)
                  + f" | 90% da reducao aos {linha['etapa2_90pct_s']} s (HiGHS)", flush=True)

    # conferencias da escala final: rigidas e descanso medido no relogio
    ind = fe.indicadores(inst, escala)
    med = fe.medir(inst, escala)
    problemas = solucao.conferir_rigidas(inst, escala, habilidade_rigida=True)
    descanso_ok = fe.cumpre(inst, med)
    linha.update(pedidos_atendidos=ind["pedidos_atendidos"],
                 enf_em_posto_tec=ind["enf_em_posto_tec"], negados_max=ind["negados_max"],
                 horas_min=ind["horas_min"], horas_max=ind["horas_max"],
                 diferenca_categorias=ind["diferenca_categorias"],
                 **{f"{chave}_{g}": c[chave] for g, c in ind["categorias"].items()
                    for chave in ("amplitude", "nao_utilizadas")},
                 descanso_ok=descanso_ok, menor_folga_h=med["menor_folga"],
                 menor_semanal_h=med["menor_semanal"], max_consec=med["max_consec"],
                 rigidas="; ".join(problemas) or "ok")
    # a penalidade tem de bater com o que a escala mostra: pedidos negados x W + enf em tec
    recontada = (ind["pedidos_total"] - ind["pedidos_atendidos"]) * W + ind["enf_em_posto_tec"]
    linha["penalidade_recontada"] = recontada
    ESCALAS.mkdir(parents=True, exist_ok=True)
    solucao.escrever_xml(inst, escala, ESCALAS / f"{inst.id}_objetivo.xml", penalidade=z)
    print(f"   ### penalidade {z} (recontada {recontada}) | pedidos "
          f"{ind['pedidos_atendidos']}/{ind['pedidos_total']} | enf em posto tec "
          f"{ind['enf_em_posto_tec']} | amplitude da fracao {linha['amplitude_etapa1']:.1%}"
          f" -> {linha.get('amplitude_etapa2', '-')} | carga {ind['horas_min']:g}-"
          f"{ind['horas_max']:g} h | descanso {'ok' if descanso_ok else 'FALHA'} (folga minima "
          f"{med['menor_folga']:g} h acima do exigido, semanal {med['menor_semanal']:g} h) | "
          f"rigidas {linha['rigidas']}", flush=True)
    return linha


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", action="append", type=int, help="tamanho; pode repetir")
    ap.add_argument("--solver", default=modelo.SOLVER_PADRAO)
    ap.add_argument("--tempo", type=int, default=900, help="limite POR ETAPA (padrao 900 s)")
    ap.add_argument("--folga", action="store_true",
                    help="rodada complementar: demanda de 40, 60, 80 com equipe 10%% maior")
    ap.add_argument("--equivalencia", action="store_true",
                    help="so o teste de equivalencia caminho novo x antigo (N=36 e 40)")
    a = ap.parse_args()
    if a.equivalencia:
        return equivalencia(a.solver, a.tempo)

    print(f"### Curva com objetivo nao trivial (P1). Solver {a.solver}, limite {a.tempo} s por "
          f"etapa, semente {SEMENTE} (+N).")
    print(f"### Maquina: {platform.processor()} | {platform.platform()} | "
          f"Python {platform.python_version()}", flush=True)
    if a.folga:
        print(f"### Rodada COM FOLGA: equipe = round({FOLGA} x N), mesma demanda.", flush=True)
    saida = SAIDA_FOLGA if a.folga else SAIDA
    linhas = []
    for n in a.n or (TAMANHOS_FOLGA if a.folga else esc.TAMANHOS):
        try:
            linhas.append(rodar(n, a.solver, a.tempo,
                                equipe=round(FOLGA * n) if a.folga else None))
        except RuntimeError as e:
            print(f"   FALHOU {e}")
            return 1
        mesclar_csv(saida, linhas, ("N", "equipe") if a.folga else ("N",))

    print("\n### resumo")
    for r in linhas:
        print(f"### N={r['N']:3d} equipe {r['equipe']:3d} | etapa 1 {r.get('etapa1_estado')} gap "
              f"{r.get('etapa1_gap') or '-'} {r.get('etapa1_relogio_s')} s (1a escala "
              f"{r.get('etapa1_primeira_escala_s')} s) | etapa 2 {r.get('etapa2_estado')} gap "
              f"{r.get('etapa2_gap') or '-'} {r.get('etapa2_relogio_s', '-')} s | penalidade "
              f"{r.get('penalidade', '-')} | descanso "
              f"{'ok' if r.get('descanso_ok') else 'FALHA/sem escala'} | amplitude "
              f"{r.get('amplitude_etapa1', '-')} -> {r.get('amplitude_etapa2', '-')} (90% aos "
              f"{r.get('etapa2_90pct_s', '-')} s)")
    print(f"\nresultado: {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
