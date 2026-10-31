"""Identidade da v1.4.5 (30/10, etapa 2 por min-max) contra a v1.4.4, nos 81 casos de
`identidade_3bloco.py --gravar`.

    python docs\\diagnostico\\identidade_v145.py <pasta_v144> <pasta_nova>
    python docs\\diagnostico\\identidade_v145.py --controle <pasta_v144> <pasta_nova>

Confere: (1) XML e LP da etapa 1 identicos byte a byte; (2) LP da etapa 2 com a diferenca
restrita a mudanca de formulacao: lido como conteudo (restricao por nome, termos sem ordem,
limites e tipos como conjunto), porque o Pyomo reordena termos e limites quando aparece uma
variavel nova. Fora o objetivo, a variavel `amplitude` e as restricoes `amplitude_constraints`,
tudo tem de ser igual. O objetivo antigo tem de ser soma de f_max(g) - f_min(g); o novo, so
`amplitude`; e tem de haver exatamente uma restricao amplitude >= f_max(g) - f_min(g) por
categoria g do objetivo antigo.
"""

from __future__ import annotations

import filecmp
import sys
from pathlib import Path

NOVA_VAR = "amplitude"
NOVA_RESTR = "amplitude_constraints"


def ler_lp(caminho: Path):
    """Devolve (objetivo, restricoes, outras secoes) de um LP do Pyomo."""
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    secao, objetivo, restricoes, outras = None, [], {}, {}
    bloco: list[str] = []

    def fecha_bloco():
        if not bloco:
            return
        nome = bloco[0].rstrip(":")
        if nome in restricoes:
            raise ValueError(f"{caminho.name}: restricao repetida {nome}")
        sentido = bloco[-1]
        restricoes[nome] = (frozenset(bloco[1:-1]), sentido)
        bloco.clear()

    for bruta in linhas:
        l = bruta.strip()
        if l.startswith("\\*"):
            continue
        if l in ("min", "max"):
            secao = "obj"
            objetivo.append(l)
            continue
        if l == "s.t.":
            secao = "st"
            continue
        if secao == "st" and l in ("bounds", "binary", "general", "integer", "semi-continuous",
                                   "end"):
            fecha_bloco()
        if l in ("bounds", "binary", "general", "integer", "semi-continuous", "end"):
            secao = l
            outras.setdefault(l, set())
            continue
        if secao == "obj":
            if l:
                objetivo.append(l)
        elif secao == "st":
            if l:
                bloco.append(l)
            else:
                fecha_bloco()
        elif secao is not None and l:
            if l in outras[secao]:
                raise ValueError(f"{caminho.name}: linha repetida em {secao}: {l}")
            outras[secao].add(l)
    return objetivo, restricoes, outras


def termos_objetivo(objetivo):
    # objetivo = ["min", "<rotulo>:", termos...]
    assert objetivo[0] == "min", objetivo[:2]
    return set(objetivo[2:])


def conferir_etapa2(a: Path, b: Path) -> list[str]:
    erros = []
    obj_a, rest_a, out_a = ler_lp(a)
    obj_b, rest_b, out_b = ler_lp(b)

    termos_a = termos_objetivo(obj_a)
    grupos = sorted(t[len("+1 f_max("):-1] for t in termos_a if t.startswith("+1 f_max("))
    esperado_a = {f"+1 f_max({g})" for g in grupos} | {f"-1 f_min({g})" for g in grupos}
    if not grupos or termos_a != esperado_a:
        erros.append(f"objetivo antigo nao e soma de amplitudes: {sorted(termos_a)}")
    if termos_objetivo(obj_b) != {f"+1 {NOVA_VAR}"}:
        erros.append(f"objetivo novo nao e so {NOVA_VAR}: {obj_b[2:]}")

    novas = {n: r for n, r in rest_b.items() if NOVA_RESTR in n}
    resto_b = {n: r for n, r in rest_b.items() if NOVA_RESTR not in n}
    if any(NOVA_RESTR in n or NOVA_VAR in " ".join(r[0]) for n, r in rest_a.items()):
        erros.append("a v1.4.4 ja tinha amplitude nas restricoes")
    if rest_a != resto_b:
        so_a = set(rest_a) - set(resto_b)
        so_b = set(resto_b) - set(rest_a)
        mud = [n for n in set(rest_a) & set(resto_b) if rest_a[n] != resto_b[n]]
        erros.append(f"restricoes antigas diferem: so v144 {len(so_a)}, so nova {len(so_b)}, "
                     f"mudadas {len(mud)} (ex.: {sorted(so_a | so_b | set(mud))[:3]})")

    formas = {(r[0], r[1]) for r in novas.values()}
    esperadas = {(frozenset({f"-1 {NOVA_VAR}", f"+1 f_max({g})", f"-1 f_min({g})"}), "<= 0")
                 for g in grupos}
    if len(novas) != len(grupos) or formas != esperadas:
        erros.append(f"restricoes novas fora do esperado: {len(novas)} para {len(grupos)} "
                     f"categorias; {sorted((sorted(f), s) for f, s in formas)}")

    for secao in set(out_a) | set(out_b):
        sa, sb = out_a.get(secao, set()), out_b.get(secao, set())
        extra = {l for l in sb - sa if NOVA_VAR in l.split()}
        if secao == "bounds":
            if extra != {f"0 <= {NOVA_VAR} <= +inf"}:
                erros.append(f"limite da variavel nova fora do esperado: {sorted(extra)}")
        if sa != sb - extra:
            erros.append(f"secao {secao} difere: so v144 {sorted(sa - sb)[:3]}, "
                         f"so nova {sorted(sb - sa - extra)[:3]}")
    return erros


def controle(a: Path, b: Path, caso: str = "demo19_a1_etapa2.lp") -> int:
    """Controle positivo: defeitos plantados numa copia do LP novo tem de ser pegos."""
    import re
    import tempfile
    t = (b / caso).read_text(encoding="utf-8")
    cab, corpo = t.split("s.t.", 1)
    plantas = {
        "coeficiente de restricao antiga": cab + "s.t." + corpo.replace("\n+1 ", "\n+2 ", 1),
        "falta uma restricao de amplitude": re.sub(
            r"c_u_amplitude_constraints\(2\)_:\n(?:.*\n)*?<= 0\n\n", "", t),
        "limite de f_max mudado": t.replace("0 <= f_max(tecnicos) <= +inf",
                                            "0 <= f_max(tecnicos) <= 1"),
        "termo a mais no objetivo": t.replace("+1 amplitude\n",
                                              "+1 amplitude\n+1 f_max(tecnicos)\n", 1),
    }
    falhas = 0 if not conferir_etapa2(a / caso, b / caso) else 1
    with tempfile.TemporaryDirectory() as d:
        for nome, texto in plantas.items():
            p = Path(d) / caso
            p.write_text(texto, encoding="utf-8")
            pego = texto != t and bool(conferir_etapa2(a / caso, p))
            print(f"controle: {nome}: {'pego (ok)' if pego else 'NAO PEGO (falhou)'}")
            falhas += not pego
    print("CONTROLE OK" if not falhas else "CONTROLE FALHOU")
    return 1 if falhas else 0


def main() -> int:
    if sys.argv[1] == "--controle":
        return controle(Path(sys.argv[2]), Path(sys.argv[3]))
    a, b = Path(sys.argv[1]), Path(sys.argv[2])
    nomes = sorted(p.name for p in a.iterdir())
    if nomes != sorted(p.name for p in b.iterdir()):
        print("LISTAS DIFERENTES")
        return 1
    fixos = [n for n in nomes if not n.endswith("_etapa2.lp")]
    etapa2 = [n for n in nomes if n.endswith("_etapa2.lp")]
    dif_fixos = [n for n in fixos if not filecmp.cmp(a / n, b / n, shallow=False)]
    etapa2_identicos = [n for n in etapa2 if filecmp.cmp(a / n, b / n, shallow=False)]
    falhas = {}
    for n in etapa2:
        erros = conferir_etapa2(a / n, b / n)
        if erros:
            falhas[n] = erros
    print(f"{len(fixos)} arquivos XML + etapa 1: {len(fixos) - len(dif_fixos)} identicos, "
          f"{len(dif_fixos)} diferentes")
    for n in dif_fixos:
        print("   DIFERENTE:", n)
    print(f"{len(etapa2)} LPs da etapa 2: {len(etapa2) - len(falhas)} com a diferenca restrita "
          f"ao min-max, {len(falhas)} fora; {len(etapa2_identicos)} identicos byte a byte "
          f"(esperado 0: a formulacao mudou)")
    for n, erros in falhas.items():
        for e in erros:
            print(f"   FORA: {n}: {e}")
    ok = not dif_fixos and not falhas and not etapa2_identicos and len(etapa2) == len(fixos) // 2
    print("IDENTIDADE V145 OK" if ok else "IDENTIDADE V145 FALHOU")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
