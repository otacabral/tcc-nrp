"""As duas declaracoes que o projeto de redacao pediu antes de o piso forcado virar texto.

    python docs\\conferencia_piso_forcado.py

O piso e: a cobertura entra como igualdade, entao o total de atribuicoes de qualquer escala
viavel e exatamente a demanda `D`. Se `D` passa da soma dos tetos `C`, os `D - C` excedentes
existem em toda escala viavel, e com peso 1 isso e limite inferior para `Z*`.

O argumento so fecha se duas coisas forem verdade. Este script confere as duas.

**Declaracao 1 — a violacao de teto e contada POR ATRIBUICAO EXCEDENTE, nao por profissional
em violacao.** Se fosse binaria por pessoa, `D - C` nao seria limite: 30 excedentes
concentrados em 2 pessoas custariam 2, nao 30. Conferido contra o AVALIADOR OFICIAL, nao
contra o `avaliacao.py` nem contra o `modelo.py` — os dois sao meus, e o que esta em jogo e
justamente se eu li a regra certa.

Nao foi preciso teste construido: o avaliador **imprime `excess` e `cost` em campos
separados**, por profissional, e nas escalas otimas ja gravadas aparecem linhas como
`Maximum number of assignments: excess = 13, pos = 111, cost = 13`. `cost == excess` com
`excess` de 13 responde a pergunta sozinho — se fosse binaria por pessoa, o custo seria 1.
(A primeira versao deste script montava escalas artificiais com `teto + k` dias; o avaliador
aborta antes de calcular as flexiveis quando a cobertura nao fecha, entao o caminho nao
servia. Fica registrado porque a tentativa custou tempo.)

**Declaracao 2 — `MaxNumAssignments` esta ativo em todos os contratos das quinze instancias
do lote early.** Se algum contrato nao tem teto, a soma dos tetos nao e limite de capacidade:
as pessoas daquele contrato absorveriam qualquer excesso de graca, e `D - C` deixaria de ser
piso. Conferido contrato a contrato, com a regra de ativacao do projeto (ligada E peso > 0).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from collections import Counter  # noqa: E402

from parser import ler_instancia  # noqa: E402
from solucao import ler_xml  # noqa: E402


AVALIADOR = RAIZ / "avaliador"
CLASSE = "dds.nrp.core.evaluation.ScheduleEvaluator"
SAIDA = RAIZ / "resultados" / "conferencia_piso"

EARLY = ([(f"sprint{i:02d}", f"instancias/sprint/sprint/sprint{i:02d}.xml")
          for i in range(1, 11)]
         + [(f"long{i:02d}", f"instancias/long/long/long{i:02d}.xml") for i in range(1, 6)])


def avaliar(instancia: Path, solucao: Path) -> str:
    r = subprocess.run(
        ["java", "-cp", str(AVALIADOR / "*"), CLASSE, str(instancia), str(solucao)],
        capture_output=True, text=True, timeout=300)
    return r.stdout + r.stderr


# --- declaracao 1 ---------------------------------------------------------------------

ESCALAS = [
    ("sprint01", "instancias/sprint/sprint/sprint01.xml", "resultados/sprint01_completo.xml"),
    ("sprint02", "instancias/sprint/sprint/sprint02.xml", "resultados/sprint02_completo.xml"),
    ("long01", "instancias/long/long/long01.xml", "resultados/long01_completo.xml"),
    ("long02", "instancias/long/long/long02.xml", "resultados/long02_completo.xml"),
]

# "Maximum number of assignments: excess = 9 , pos = 111, cost = 9"
LINHA = re.compile(r"Maximum number of assignments:\s*excess\s*=\s*(\d+).*?cost\s*=\s*(\d+)")


def declaracao_1() -> bool:
    """O proprio avaliador oficial responde, sem teste construido.

    Na saida detalhada ele imprime, por profissional, uma linha com `excess` e `cost`
    separados. Se `cost == excess` quando `excess > 1`, a contagem e por atribuicao
    excedente. Se `cost == 1` com `excess` maior, seria binaria por pessoa.

    Junto vem a conferencia do proprio piso: a soma dos excessos que o avaliador reporta nas
    escalas otimas tem de ser >= `D - C`. A desigualdade e identidade aritmetica — o total de
    atribuicoes e `D`, entao `sum_n max(0, a_n - teto_n) >= sum_n (a_n - teto_n) = D - C` —,
    e ver o avaliador obedecer a ela e a conferencia empirica do argumento.
    """
    print("=" * 88)
    print("DECLARACAO 1 - a violacao de teto e por atribuicao excedente ou por pessoa?")
    print("=" * 88)
    print("\nLido da saida detalhada do AVALIADOR OFICIAL sobre as escalas otimas ja gravadas.")
    ok = True
    for nome, inst_caminho, sol_caminho in ESCALAS:
        sol = RAIZ / sol_caminho
        if not sol.exists():
            print(f"\n  {nome}: escala ausente em {sol_caminho} — pulada")
            continue
        inst = ler_instancia(str(RAIZ / inst_caminho))
        saida = avaliar(RAIZ / inst_caminho, sol)
        SAIDA.mkdir(parents=True, exist_ok=True)
        (SAIDA / f"{nome}_avaliador.txt").write_text(saida, encoding="utf-8")
        pares = [(int(a), int(b)) for a, b in LINHA.findall(saida)]
        if not pares:
            print(f"\n  {nome}: o avaliador nao reportou MaxNumAssignments — conferir a saida")
            ok = False
            continue
        lineares = all(c == e for e, c in pares)
        maior = max(e for e, _ in pares)
        soma = sum(e for e, _ in pares)
        c = sum(inst.contrato_de(p).max_num_assignments.valor for p in inst.profissionais
                if inst.contrato_de(p).max_num_assignments.ativa)
        piso = inst.demanda_total - c
        print(f"\n  {nome}: {len(pares)} profissionais com excesso, maior excesso {maior}")
        print(f"     cost == excess em todas as linhas? {lineares}")
        print(f"     soma dos excessos = {soma}   |   D - C = {piso}   |   "
              f"{soma} >= {piso}? {soma >= piso}")
        exemplo = max(pares)
        print(f"     linha exemplo: excess = {exemplo[0]}, cost = {exemplo[1]}")
        # A igualdade `soma == piso` nao e obrigatoria: ela so acontece se NINGUEM ficar
        # abaixo do proprio teto. Quando acontece, diz algo forte sobre o otimo — o teto de
        # jornada funciona como piso. Conferido direto na escala, contando atribuicoes.
        _, _, escala = ler_xml(sol)
        conta = Counter(a[1] for a in escala)
        abaixo = [p for p in inst.profissionais
                  if inst.contrato_de(p).max_num_assignments.ativa
                  and conta.get(p, 0) < inst.contrato_de(p).max_num_assignments.valor]
        print(f"     profissionais ABAIXO do proprio teto nesta escala otima: {len(abaixo)}"
              f"{'  -> o teto virou piso' if not abaixo else '  ' + str(abaixo[:5])}")
        ok &= lineares and maior > 1 and soma >= piso
    print("\n  cost == excess com excess > 1 => contagem POR ATRIBUICAO excedente.")
    print("  Saida completa do avaliador em resultados/conferencia_piso/.")
    return ok


# --- declaracao 2 ---------------------------------------------------------------------

def declaracao_2() -> bool:
    """`MaxNumAssignments` ativo em todo contrato das quinze instancias do lote early."""
    print()
    print("=" * 88)
    print("DECLARACAO 2 - MaxNumAssignments ativo em todos os contratos das 15 early")
    print("=" * 88)
    print(f"\n  {'instancia':10s}{'contratos':>10s}{'com teto ativo':>16s}"
          f"{'pessoas sem teto':>18s}{'tetos':>22s}")
    tudo_ok = True
    for nome, caminho in EARLY:
        inst = ler_instancia(str(RAIZ / caminho))
        ativos = {c: ct.max_num_assignments for c, ct in inst.contratos.items()}
        com = [c for c, f in ativos.items() if f.ativa]
        sem_teto = [p for p in inst.profissionais
                    if not inst.contrato_de(p).max_num_assignments.ativa]
        tetos = sorted(f.valor for f in ativos.values() if f.ativa)
        ok = len(com) == len(ativos) and not sem_teto
        tudo_ok &= ok
        print(f"  {nome:10s}{len(ativos):10d}{len(com):16d}{len(sem_teto):18d}"
              f"{str(tetos):>22s}{'' if ok else '   <-- FALHA'}")
    # o peso importa tanto quanto a ativacao: peso 1 e o que faz o excesso valer 1 por unidade
    pesos = set()
    for nome, caminho in EARLY:
        inst = ler_instancia(str(RAIZ / caminho))
        pesos |= {ct.max_num_assignments.peso for ct in inst.contratos.values()
                  if ct.max_num_assignments.ativa}
    print(f"\n  pesos distintos de MaxNumAssignments no lote: {sorted(pesos)}")
    print(f"  {'TODOS os contratos tem teto ativo.' if tudo_ok else 'HA CONTRATO SEM TETO.'}")
    if pesos != {1}:
        print("  ATENCAO: peso diferente de 1 — o piso passa a ser sum(peso * excesso), e a")
        print("  tabela de E/Z* precisa ser refeita com o peso dentro.")
    return tudo_ok


def main() -> int:
    ok2 = declaracao_2()
    ok1 = declaracao_1()
    print()
    print("Declaracao 2:", "OK" if ok2 else "FALHOU")
    print("Declaracao 1:", "OK" if ok1 else "FALHOU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
