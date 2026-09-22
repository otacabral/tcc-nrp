"""Conferencias 2 e 3 do achado do contrato (projeto de redacao, 22/09).

Roda da raiz do repositorio. Nao usa Pyomo: le as instancias com o `parser.py` e o perfil
ja medido em `resultados/experimento_b.csv`.

    python docs\\conferencia_contratos.py

Conferencia 3 — inventario de contratos das quatro instancias. Hipotese do projeto de
redacao: a diferenca de concentracao inevitavel entre sprints (1,2x) e longas (2,7x e 3,1x)
vem de heterogeneidade de contrato, nao de tamanho.

Conferencia 2 — correlacao long01 x long02 DENTRO de cada grupo de contrato. Os 0,89 globais
sao esperados se o contrato explica a exposicao, ja que as duas instancias compartilham os
mesmos 49 profissionais. Correlacao intragrupo e o que separa efeito individual de efeito de
contrato.

Alem das duas, o que apareceu ao fazer a 2 e nao estava pedido:

- **piso aritmetico** — a cobertura e igualdade, entao o total de atribuicoes de qualquer
  escala viavel e a demanda `D`. Se `D` passa da soma dos tetos, o excesso e forcado, e com
  peso 1 isso e piso para `Z*`. De 73% a 81% de `Z*` nas longas;
- **par controlado** — dentro de cada track do lote *early*, as instancias sao identicas em
  tudo menos nos contratos. Nao sao cenarios diferentes;
- **serie** — o mesmo vale para as 10 sprints e as 5 longas do lote, contra a Tabela 6;
- **eixo 2** — a habilidade `HeadNurse`, que so pesa onde o teto e baixo.

Ver `docs/nota_conferencias_contrato_2026-09-22.md`, e P10 e P11 no `PROPOSTAS.md`.
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from parser import ler_instancia  # noqa: E402

ALVOS = [
    ("sprint01", "instancias/sprint/sprint/sprint01.xml"),
    ("sprint02", "instancias/sprint/sprint/sprint02.xml"),
    ("long01", "instancias/long/long/long01.xml"),
    ("long02", "instancias/long/long/long02.xml"),
]


def pearson(xs, ys):
    if len(xs) < 3 or statistics.pstdev(xs) == 0 or statistics.pstdev(ys) == 0:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return num / den


def ler_perfil(caminho: Path) -> dict:
    perfil = {}
    with caminho.open(newline="", encoding="utf-8-sig") as f:
        for l in csv.DictReader(f, delimiter=";"):
            v = l.get("pena_maxima_entre_otimos", "")
            if v not in ("", None):
                perfil[(l["instancia"], l["profissional"])] = int(v)
    return perfil


# --- conferencia 3 --------------------------------------------------------------------

def inventario():
    print("=" * 88)
    print("CONFERENCIA 3 - inventario de contratos")
    print("=" * 88)
    tabela = {}
    for nome, caminho in ALVOS:
        inst = ler_instancia(str(RAIZ / caminho))
        grupos = {}
        for p in inst.profissionais.values():
            grupos.setdefault(p.contrato, []).append(p.id)
        print(f"\n{nome}: {len(inst.profissionais)} profissionais, {inst.n_dias} dias, "
              f"{len(grupos)} contrato(s), {len(inst.turnos)} turnos, "
              f"demanda total {inst.demanda_total}")
        print(f"  {'contrato':14s}{'n':>4s}{'teto':>6s}{'piso':>6s}{'teto/dias':>11s}"
              f"{'max dias seg.':>15s}{'n flexiveis ativas':>21s}")
        for c, membros in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
            ct = inst.contratos[c]
            teto = ct.max_num_assignments
            piso = ct.min_num_assignments
            seg = ct.max_consecutive_working_days
            t = teto.valor if teto.ativa else None
            print(f"  {c:14s}{len(membros):4d}"
                  f"{(str(t) if t is not None else '-'):>6s}"
                  f"{(str(piso.valor) if piso.ativa else '-'):>6s}"
                  f"{(f'{t / inst.n_dias:.2f}' if t is not None else '-'):>11s}"
                  f"{(str(seg.valor) if seg.ativa else '-'):>15s}"
                  f"{len(ct.ativas()):21d}")
            tabela[(nome, c)] = (len(membros), t)
        tetos = [t for (i, _), (_, t) in tabela.items() if i == nome and t is not None]
        if tetos:
            print(f"  amplitude de teto: {min(tetos)} a {max(tetos)}"
                  f"  ({max(tetos) / min(tetos):.1f}x)" if min(tetos) else "")
    return tabela


# --- conferencia 2 --------------------------------------------------------------------

def correlacao(perfil):
    print()
    print("=" * 88)
    print("CONFERENCIA 2 - correlacao long01 x long02, global e dentro de cada contrato")
    print("=" * 88)
    inst = ler_instancia(str(RAIZ / "instancias/long/long/long01.xml"))
    inst2 = ler_instancia(str(RAIZ / "instancias/long/long/long02.xml"))
    mesmos = {p: inst.profissionais[p].contrato for p in inst.profissionais}
    outros = {p: inst2.profissionais[p].contrato for p in inst2.profissionais}
    print(f"\nmesmo conjunto de profissionais: {set(mesmos) == set(outros)}")
    print(f"mesmo contrato para cada um:     {mesmos == outros}")

    pares = [(p, perfil[("long01", p)], perfil[("long02", p)])
             for p in mesmos if ("long01", p) in perfil and ("long02", p) in perfil]
    xs = [a for _, a, _ in pares]
    ys = [b for _, _, b in pares]
    r = pearson(xs, ys)
    print(f"\nglobal (N={len(pares)}): r = {r:.3f}")

    print(f"\n  {'contrato':14s}{'n':>4s}{'teto':>6s}{'media 01':>10s}{'media 02':>10s}"
          f"{'dp 01':>8s}{'dp 02':>8s}{'r intragrupo':>15s}")
    for c in sorted({mesmos[p] for p in mesmos}):
        sub = [(a, b) for p, a, b in pares if mesmos[p] == c]
        if not sub:
            continue
        a = [x for x, _ in sub]
        b = [y for _, y in sub]
        rc = pearson(a, b)
        ct = inst.contratos[c]
        teto = ct.max_num_assignments.valor if ct.max_num_assignments.ativa else None
        print(f"  {c:14s}{len(sub):4d}{(str(teto) if teto else '-'):>6s}"
              f"{statistics.fmean(a):10.2f}{statistics.fmean(b):10.2f}"
              f"{statistics.pstdev(a):8.2f}{statistics.pstdev(b):8.2f}"
              f"{(f'{rc:.3f}' if rc is not None else 'n/d'):>15s}")

    # quanto do sinal global e contrato: correlacao dos desvios em torno da media do grupo
    med01 = {c: statistics.fmean([a for p, a, _ in pares if mesmos[p] == c])
             for c in {mesmos[p] for p in mesmos}}
    med02 = {c: statistics.fmean([b for p, _, b in pares if mesmos[p] == c])
             for c in {mesmos[p] for p in mesmos}}
    dx = [a - med01[mesmos[p]] for p, a, _ in pares]
    dy = [b - med02[mesmos[p]] for p, _, b in pares]
    rd = pearson(dx, dy)
    print(f"\ncorrelacao dos DESVIOS em torno da media do proprio contrato (N={len(dx)}): "
          f"r = {rd:.3f}")
    print("  e a correlacao intragrupo agregada: o que sobra do individuo depois de tirar")
    print("  o contrato. Perto de zero = a exposicao e do contrato, nao da pessoa.")

    # o contrato sozinho como preditor
    prev = [med01[mesmos[p]] for p, _, _ in pares]
    ss_tot = sum((a - statistics.fmean(xs)) ** 2 for a in xs)
    ss_res = sum((a - q) ** 2 for a, q in zip(xs, prev))
    print(f"\nlong01: variancia do maximo explicada so pelo contrato: "
          f"R2 = {1 - ss_res / ss_tot:.3f}")
    prev2 = [med02[mesmos[p]] for p, _, _ in pares]
    ss_tot2 = sum((b - statistics.fmean(ys)) ** 2 for b in ys)
    ss_res2 = sum((b - q) ** 2 for b, q in zip(ys, prev2))
    print(f"long02: variancia do maximo explicada so pelo contrato: "
          f"R2 = {1 - ss_res2 / ss_tot2:.3f}")


# --- deficit de teto ------------------------------------------------------------------

def deficit_de_teto():
    """Quanto da penalidade total e excesso de atribuicao FORCADO pela aritmetica.

    A cobertura entra como igualdade, entao o numero total de atribuicoes de qualquer escala
    viavel e exatamente a demanda `D`. Se `D` passa da soma dos tetos de jornada `C`, os
    `D - C` excedentes existem em TODA escala viavel — otima ou nao. Como o peso de
    `max_num_assignments` e 1 em todos os contratos das quatro instancias, isso e um piso
    para a parcela da familia e, portanto, para `Z*`.

    Nao depende de resolver nada, e nao depende de qual otimo o solver devolve. E a unica
    parte da composicao da penalidade que e invariante por construcao.
    """
    print()
    print("=" * 88)
    print("PISO ARITMETICO - excesso de atribuicao forcado pela demanda")
    print("=" * 88)
    print(f"\n  {'instancia':10s}{'D':>6s}{'soma tetos':>12s}{'excesso':>9s}{'Z*':>6s}"
          f"{'piso/Z*':>9s}{'por pessoa':>12s}{'media Z*/N':>12s}")
    zs = {"sprint01": 56, "sprint02": 58, "long01": 197, "long02": 219}
    for nome, caminho in ALVOS:
        inst = ler_instancia(str(RAIZ / caminho))
        c = sum(inst.contrato_de(p).max_num_assignments.valor
                for p in inst.profissionais
                if inst.contrato_de(p).max_num_assignments.ativa)
        d, z, n = inst.demanda_total, zs[nome], len(inst.profissionais)
        e = d - c
        print(f"  {nome:10s}{d:6d}{c:12d}{e:9d}{z:6d}{e / z:8.0%}{e / n:12.2f}{z / n:12.2f}")
    print("\n  'por pessoa' = excesso forcado / N. E quanto de penalidade media cada um")
    print("  carrega antes de qualquer escolha de escala. Comparar com a media Z*/N.")

    # O mesmo raciocinio aplicado ao MAXIMO individual: menor `t` tal que, se ninguem passa
    # `teto + t` atribuicoes (e ninguem passa de um turno por dia), a demanda ainda cabe.
    # E piso valido para `min_do_max`, olhando so a familia do teto — e, como se ve, um piso
    # FRACO. Serve para mostrar que a concentracao medida NAO se explica pelo teto sozinho.
    print(f"\n  {'instancia':10s}{'piso so pelo teto':>19s}{'piso Z*/N':>11s}"
          f"{'min_do_max medido':>19s}")
    medidos = {"sprint01": 7, "sprint02": 7, "long01": 11, "long02": 14}
    for nome, caminho in ALVOS:
        inst = ler_instancia(str(RAIZ / caminho))
        tetos = [inst.contrato_de(p).max_num_assignments.valor for p in inst.profissionais]
        t = 0
        while sum(min(inst.n_dias, x + t) for x in tetos) < inst.demanda_total:
            t += 1
        piso_media = -(-zs[nome] // len(inst.profissionais))
        print(f"  {nome:10s}{t:19d}{piso_media:11d}{medidos[nome]:19d}")
    print("\n  Os dois pisos ficam MUITO abaixo do medido. A concentracao nao vem do teto")
    print("  sozinho: vem do acoplamento entre estourar o teto e violar dias consecutivos,")
    print("  fim de semana e padroes. Nao usar estes numeros como explicacao do maximo.")


def par_controlado():
    """O que de fato distingue `long01` de `long02` — e `sprint01` de `sprint02`.

    Conferido em 22/09, depois que a correlacao de 0,89 pediu explicacao: as duas instancias
    de cada par tem **a mesma demanda, os mesmos pedidos, os mesmos profissionais, as mesmas
    habilidades e os mesmos turnos**. A unica diferenca esta nos parametros dos contratos.
    """
    print()
    print("=" * 88)
    print("O QUE DIFERE DENTRO DE CADA PAR")
    print("=" * 88)
    pares = [("sprint01", "instancias/sprint/sprint/sprint01.xml",
              "sprint02", "instancias/sprint/sprint/sprint02.xml"),
             ("long01", "instancias/long/long/long01.xml",
              "long02", "instancias/long/long/long02.xml")]
    for n1, c1, n2, c2 in pares:
        a, b = ler_instancia(str(RAIZ / c1)), ler_instancia(str(RAIZ / c2))
        iguais = [campo for campo in ("habilidades", "turnos", "padroes", "profissionais",
                                      "demanda", "pedidos", "inicio", "fim")
                  if getattr(a, campo) == getattr(b, campo)]
        print(f"\n{n1} x {n2}: identicos em {len(iguais)} de 8 campos "
              f"({', '.join(iguais)})")
        for c in sorted(a.contratos):
            for nome in a.contratos[c].restricoes():
                fa, fb = getattr(a.contratos[c], nome), getattr(b.contratos[c], nome)
                if (fa.ativa, fa.valor, fa.peso) != (fb.ativa, fb.valor, fb.peso):
                    marca = "" if not (fa.ativa or fb.ativa) else "  <- ativa"
                    print(f"   contrato {c:2s} {nome:32s} {str(fa.valor):>4s} -> "
                          f"{str(fb.valor):>4s}{marca}")


TABELA6 = {
    "sprint01": 56, "sprint02": 58, "sprint03": 51, "sprint04": 59, "sprint05": 58,
    "sprint06": 54, "sprint07": 56, "sprint08": 56, "sprint09": 55, "sprint10": 52,
    "long01": 197, "long02": 219, "long03": 240, "long04": 303, "long05": 284,
}


def serie():
    """O lote *early* inteiro: 10 sprints e 5 longas, todas com otimo provado na Tabela 6.

    Conferido em 22/09 no nivel do XML bruto (hash de cada bloco, sem passar pelo parser):
    dentro de cada track, `<CoverRequirements>`, `<DayOffRequests>`, `<ShiftOffRequests>`,
    `<Employees>`, `<ShiftTypes>` e `<Skills>` sao IDENTICOS em todos os arquivos. So o bloco
    `<Contracts>` muda. O lote nao e um conjunto de cenarios: e UM cenario por track, com
    variacoes de regra de contrato.

    Os valores da Tabela 6 abaixo foram transcritos de Santos et al. (2016), p. 248-249. Os
    quatro ja usados como alvo de validacao batem, o que serve de conferencia da transcricao.
    """
    print()
    print("=" * 88)
    print("O LOTE EARLY COMO SERIE - excesso forcado x otimo provado")
    print("=" * 88)
    for track, padrao in (("sprint", "instancias/sprint/sprint/*.xml"),
                          ("long", "instancias/long/long/*.xml")):
        print(f"\n  {'instancia':10s}{'D':>5s}{'soma tetos':>12s}{'excesso E':>11s}"
              f"{'Z* (Tab.6)':>12s}{'E/Z*':>7s}")
        razoes = []
        for caminho in sorted((RAIZ / Path(padrao).parent).glob("*.xml")):
            inst = ler_instancia(str(caminho))
            z = TABELA6.get(inst.id)
            if z is None:
                continue
            c = sum(inst.contrato_de(p).max_num_assignments.valor
                    for p in inst.profissionais
                    if inst.contrato_de(p).max_num_assignments.ativa)
            e = inst.demanda_total - c
            razoes.append(e / z)
            print(f"  {inst.id:10s}{inst.demanda_total:5d}{c:12d}{e:11d}{z:12d}{e / z:7.0%}")
        print(f"  faixa de E/Z* no track {track}: {min(razoes):.0%} a {max(razoes):.0%}")
    print("\n  O excesso forcado e calculado sem resolver nada e sem olhar para a Tabela 6.")
    print("  CUIDADO: as faixas sao estreitas e sao 10 e 5 pontos. Vale como faixa observada,")
    print("  nao como lei — e nao vale fora do lote early, onde a demanda muda.")


def habilidade():
    """O segundo eixo estrutural: a habilidade `HeadNurse` nas longas."""
    print()
    print("=" * 88)
    print("EIXO 2 - habilidade, dentro do mesmo contrato")
    print("=" * 88)
    perfil = ler_perfil(RAIZ / "resultados" / "experimento_b.csv")
    for nome in ("long01", "long02"):
        inst = ler_instancia(str(RAIZ / f"instancias/long/long/{nome}.xml"))
        chefes = {p.id for p in inst.profissionais.values() if "HeadNurse" in p.habilidades}
        dh = sum(q for (_, t), q in inst.demanda.items() if t == "DH")
        print(f"\n{nome}: turno DH exige HeadNurse; demanda DH = {dh} em {inst.n_dias} dias,"
              f" {len(chefes)} habilitados ({dh / len(chefes):.1f} por pessoa)")
        for c in sorted({p.contrato for p in inst.profissionais.values()}):
            ms = [p.id for p in inst.profissionais.values() if p.contrato == c]
            a = [perfil[(nome, m)] for m in ms if m in chefes]
            b = [perfil[(nome, m)] for m in ms if m not in chefes]
            teto = inst.contratos[c].max_num_assignments.valor
            print(f"  contrato {c} (teto {teto:2d}): HeadNurse n={len(a)} max medio "
                  f"{statistics.fmean(a):5.2f} | demais n={len(b)} max medio "
                  f"{statistics.fmean(b):5.2f}")
        top = sorted(((perfil[(nome, p)], p) for p in inst.profissionais), reverse=True)[:6]
        print("  seis maiores: " + ", ".join(
            f"{p}={v} (contrato {inst.profissionais[p].contrato}"
            f"{', HeadNurse' if p in chefes else ''})" for v, p in top))


def main() -> int:
    perfil = ler_perfil(RAIZ / "resultados" / "experimento_b.csv")
    inventario()
    correlacao(perfil)
    deficit_de_teto()
    par_controlado()
    serie()
    habilidade()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
