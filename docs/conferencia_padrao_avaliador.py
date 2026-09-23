"""O avaliador oficial nao le o padrao `clt_36h_N_D` como nos o escrevemos.

    python docs\\conferencia_padrao_avaliador.py

Descoberto em 23/09, quando duas celulas do Experimento A reprovaram na conferencia: o
avaliador cobrou `Unwanted pattern` numa escala em que o padrao proibido NAO ocorre.

## O que o padrao deveria dizer

`clt_36h_N_D` = (N, None, D): plantao noturno, dia livre, plantao diurno. No 12x36 o noturno
termina as 07:00 e o diurno de dois dias depois comeca as 07:00 — sao 24 h de descanso, nao as
36 h do art. 59-A. E a unica combinacao com o furo, e existe justamente para fecha-lo (P7.2).

## O que o avaliador faz

Na escala testada ha **zero** ocorrencias de N-livre-D e **49** de N-livre-LIVRE. O avaliador
reporta exatamente 49. Dois testes separam as hipoteses:

1. criar uma ocorrencia de N-livre-D preservando a cobertura (um turno D trocado entre dois
   profissionais) faz a contagem CAIR de 49 para 48 — ou seja, N-livre-D nao e cobrado, e a
   ocorrencia de N-livre-livre que foi destruida deixou de contar;
2. trocar a terceira entrada do padrao de `D` para `N` no XML da instancia **nao muda nada**:
   continua 49.

Conclusao: **depois de uma entrada `None` em posicao nao inicial, o avaliador ignora o tipo de
turno das entradas seguintes e as trata como folga.** O padrao (N, None, D) e pontuado como
(N, folga, folga) — quer dizer, ele penaliza MAIS descanso, o oposto da intencao.

## O que isso NAO contamina

Nenhum dos 59 arquivos do INRC tem `None` em posicao nao inicial: as formas usadas sao
(L,D), (D,E,D), (None,Any,Any) e pares simples. A concordancia das 207 escalas com o avaliador
e os quatro otimos da Tabela 6 seguem valendo. A divergencia e especifica da forma que o nosso
gerador inventou.

## O que fazer com isso

Nao e decisao minha — esta na P13 do `PROPOSTAS.md`, com as opcoes. O que este script faz e
deixar a evidencia reproduzivel.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

AVALIADOR = RAIZ / "avaliador"
CLASSE = "dds.nrp.core.evaluation.ScheduleEvaluator"
CASO = RAIZ / "resultados" / "experimento_a"
NOME = "br_intermediario_12x36_teto_e40_v1"
TRABALHO = RAIZ / "resultados" / "conferencia_padrao"


def avaliar(instancia: Path, solucao: Path) -> str:
    r = subprocess.run(["java", "-cp", str(AVALIADOR / "*"), CLASSE,
                        str(instancia), str(solucao)],
                       capture_output=True, text=True, timeout=300)
    return r.stdout + r.stderr


def cobrados(saida: str) -> int:
    return sum(1 for l in saida.splitlines() if "Unwanted pattern" in l)


def ler_escala(caminho: Path):
    t = caminho.read_text(encoding="utf-8")
    atr = re.findall(r"<Assignment>\s*<Date>(.*?)</Date>\s*<Employee>(.*?)</Employee>"
                     r"\s*<ShiftType>(.*?)</ShiftType>\s*</Assignment>", t, re.S)
    dias = sorted({d for d, _, _ in atr})
    esc = defaultdict(dict)
    for d, n, s in atr:
        esc[n][d] = s
    return dias, esc


def contar(dias, esc, primeiro, terceiro) -> int:
    """Triplas (dia i, dia i+1 LIVRE, dia i+2), com `terceiro=None` significando livre."""
    n = 0
    for m in esc.values():
        for i in range(len(dias) - 2):
            a, b, c = m.get(dias[i]), m.get(dias[i + 1]), m.get(dias[i + 2])
            if a == primeiro and b is None and ((c is None) if terceiro is None
                                                else c == terceiro):
                n += 1
    return n


def varredura_inrc() -> tuple[int, int]:
    """Quantos padroes do INRC tem `None` em posicao nao inicial? Se algum tiver, a
    concordancia das 207 escalas precisa ser reaberta."""
    import glob

    from parser import ler_instancia  # noqa: PLC0415
    total = achados = 0
    for a in sorted(glob.glob(str(RAIZ / "instancias" / "*" / "*" / "*.xml"))):
        for p in ler_instancia(a).padroes.values():
            total += 1
            if "None" in tuple(e.turno for e in p.entradas)[1:]:
                achados += 1
    return total, achados


def main() -> int:
    inst, sol = CASO / f"{NOME}_instancia.xml", CASO / f"{NOME}.xml"
    if not sol.exists():
        print(f"caso ausente: {sol.relative_to(RAIZ)}")
        print("gerar com: python src\\experimento_a.py --sensibilidade")
        return 1
    TRABALHO.mkdir(parents=True, exist_ok=True)
    dias, esc = ler_escala(sol)

    print("=" * 84)
    print("A escala, contada na mao")
    print("=" * 84)
    nd = contar(dias, esc, "N", "D")
    nn = contar(dias, esc, "N", None)
    base = cobrados(avaliar(inst, sol))
    print(f"  N-livre-D  (o que o padrao proibe) : {nd}")
    print(f"  N-livre-LIVRE (descanso de 60 h)   : {nn}")
    print(f"  cobrado pelo avaliador             : {base}")

    print()
    print("=" * 84)
    print("Teste 1 - criar um N-livre-D preservando a cobertura")
    print("=" * 84)
    alvo = None
    for a, m in esc.items():
        for i in range(len(dias) - 2):
            if m.get(dias[i]) == "N" and dias[i + 1] not in m and dias[i + 2] not in m:
                b = next((x for x, m2 in esc.items()
                          if x != a and m2.get(dias[i + 2]) == "D"), None)
                if b:
                    alvo = (a, b, i)
                    break
        if alvo:
            break
    if not alvo:
        print("  nao achei par para a troca nesta escala")
        return 1
    a, b, i = alvo
    texto = sol.read_text(encoding="utf-8")
    padrao = re.compile(r"(<Assignment>\s*<Date>" + re.escape(dias[i + 2])
                        + r"</Date>\s*<Employee>)" + re.escape(b)
                        + r"(</Employee>\s*<ShiftType>D</ShiftType>)")
    novo, trocas = padrao.subn(r"\g<1>" + a + r"\g<2>", texto, count=1)
    assert trocas == 1
    arquivo = TRABALHO / "escala_com_N_livre_D.xml"
    arquivo.write_text(novo, encoding="utf-8")
    esc[a][dias[i + 2]] = "D"
    del esc[b][dias[i + 2]]
    depois = cobrados(avaliar(inst, arquivo))
    print(f"  turno D do dia {dias[i + 2]} passa do profissional {b} para o {a}")
    print(f"  agora ha {contar(dias, esc, 'N', 'D')} ocorrencias de N-livre-D e "
          f"{contar(dias, esc, 'N', None)} de N-livre-LIVRE")
    print(f"  cobrado pelo avaliador: {depois}   (era {base})")
    print(f"  -> {'CAIU' if depois < base else 'nao caiu'}: criar a sequencia proibida "
          f"{'nao aumenta' if depois <= base else 'aumenta'} a conta")

    print()
    print("=" * 84)
    print("Teste 2 - trocar a terceira entrada do padrao de D para N, na instancia")
    print("=" * 84)
    ti = inst.read_text(encoding="utf-8")
    bloco = re.search(r"<Patterns>.*?</Patterns>", ti, re.S).group(0)
    trocado = re.sub(r'(<PatternEntry index="2">\s*<ShiftType>)D(</ShiftType>)',
                     r"\1N\2", bloco)
    outra = TRABALHO / "instancia_N_None_N.xml"
    outra.write_text(ti.replace(bloco, trocado), encoding="utf-8")
    com_n = cobrados(avaliar(outra, sol))
    print(f"  cobrado com a terceira entrada = N: {com_n}   (com D era {base})")
    print(f"  -> {'IDENTICO' if com_n == base else 'mudou'}: a terceira entrada "
          f"{'nao e lida' if com_n == base else 'e lida'}")

    print()
    print("=" * 84)
    print("O que isso contamina no INRC")
    print("=" * 84)
    total, achados = varredura_inrc()
    print(f"  padroes nos arquivos do INRC: {total}")
    print(f"  com 'None' em posicao NAO inicial: {achados}")
    print(f"  -> {'nada a reabrir' if achados == 0 else 'REABRIR a concordancia das 207'}")

    print()
    print("CONCLUSAO: depois de uma entrada `None` em posicao nao inicial, o avaliador trata")
    print("as entradas seguintes como folga, ignorando o tipo de turno declarado. O padrao")
    print("(N, None, D) e pontuado como (N, folga, folga) — penaliza MAIS descanso.")
    print("Ver P13 no PROPOSTAS.md. Arquivos deste teste em resultados/conferencia_padrao/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
