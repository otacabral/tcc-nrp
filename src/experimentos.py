"""Experimento B: o intervalo da penalidade individual maxima entre as escalas otimas.

Roda da raiz do repositorio, com a .venv ativa:

    python src\\experimentos.py                      # sprint01 e sprint02
    python src\\experimentos.py --alvo long01        # uma instancia so
    python src\\experimentos.py --forma A --alvo long01   # reserva, 3 resolucoes

Saida: `resultados/experimento_b.csv` (uma linha por instancia x profissional) e
`experimento_b_resumo.csv`, gravados a cada alvo concluido. Durante a forma B, o perfil
parcial e gravado a cada profissional em `experimento_b_parcial_<instancia>.csv`, apagado
quando o alvo fecha — uma queda nao joga fora a rodada. Separador ";" e utf-8-sig.

**Custo de tempo, medido em 22/09 com relogio de CPU.** Fixar o total em Z* encarece cada
resolucao: `sprint01` leva 2,5 s para o otimo simples e **~9 s de CPU** por resolucao com Z*
fixado. A rodada `--por-pessoa` completa das duas sprints (22 resolucoes cada) deu 203,7 s e
165,5 s de CPU — cerca de 6 minutos no total.

Cuidado ao estimar a partir de rodada antiga: os numeros de 21/09 eram de PARADE (385 s em
`sprint01`), com a maquina fazendo outras coisas, e dao ~3x o custo real. Uma estimativa
feita com eles erra o tempo para mais na mesma proporcao — foi o que aconteceu em 22/09.
Nas longas, medido: `long01` 4.166 s e `long02` 11.565 s de parede na forma B sem
`--por-pessoa`; contar em horas e usar `--alvo`.

## A pergunta

Entre as escalas de custo minimo, **quanto a distribuicao da penalidade entre profissionais
pode variar**? Reportar a dispersao de UMA solucao otima seria reportar o desempate do
solver, que muda com a versao e com a semente. Com Z* fixado como restricao e a dispersao
otimizada nos dois sentidos, o que se afirma e propriedade do CONJUNTO de otimos.

A pergunta nao depende de regime de jornada, entao roda nas instancias do INRC com otimo
provado — sem dado sintetico, com a penalidade do proprio benchmark. Ver DECISOES.md, 21/09.

## A medida

Penalidade individual maxima, `max_n p_n`. Conferido em 21/09: a penalidade decompoe
exatamente por profissional (soma = Z*, sem sobra) e cada parcela bate com o avaliador
oficial. Entao `max_n p_n` e participacao num total fixo, e o valor fica sempre em
`[teto(Z*/N), Z*]`.

## Por que fixar o total ja garante que a escala e otima

Cada folga e uma variavel continua limitada por baixo pelo excesso que ela representa. Somar
todas e exigir que de exatamente Z* forca duas coisas ao mesmo tempo: a escala tem de ser
otima (senao a soma dos limites passaria de Z*, que e o minimo) e **cada folga tem de valer
exatamente o seu limite** (senao a soma passaria). Logo `p_n` e a penalidade real da pessoa,
nao um valor inflado pelo solver.

## As duas formas de maximizar

Minimizar o maximo e o minimax usual: uma variavel `t`, N restricoes `t >= p_n`, minimizar
`t`. Uma resolucao.

Maximizar o maximo e maximizar funcao convexa — nao convexo, precisa de disjuncao:

- **forma B**, uma resolucao por profissional: maximiza `p_n` com *n* fixo e toma o maior.
  N resolucoes, independentes entre si, e devolve o **perfil completo** — quanto cada pessoa
  pode ser feita carregar entre os otimos, que e o que vai para o capitulo de resultados.
- **forma A**, binarias: `z_n` escolhe de quem e o maximo, `t <= p_n + M(1 - z_n)`, com
  **M = Z\\***, que e valido e justo porque `0 <= p_n <= Z\\*`. Uma resolucao, +N binarias, e
  devolve so o maximo geral — sem perfil.

Decisao de 21/09: **forma B nas sprints; forma A como reserva nas longas**, se as 49
resolucoes ficarem lentas.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
import time
from pathlib import Path

import pyomo.environ as pyo

sys.path.insert(0, str(Path(__file__).resolve().parent))

import modelo  # noqa: E402
from avaliacao import por_profissional  # noqa: E402
from instancia import Instancia  # noqa: E402
from parser import ler_instancia  # noqa: E402
from tabela import mesclar_csv  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "resultados" / "experimento_b.csv"

ALVOS = [
    ("sprint01", "instancias/sprint/sprint/sprint01.xml", 56),
    ("sprint02", "instancias/sprint/sprint/sprint02.xml", 58),
    ("long01", "instancias/long/long/long01.xml", 197),
    ("long02", "instancias/long/long/long02.xml", 219),
]


# --- montagem -------------------------------------------------------------------------

def _com_otimo_fixado(inst: Instancia, z: int) -> pyo.ConcreteModel:
    """Modelo completo com a penalidade total presa em Z*, e sem funcao objetivo.

    Quem chamar poe a sua propria objetivo. `m.objetivo` original e desativada em vez de
    removida, para o modelo continuar legivel em dump.
    """
    m = modelo.construir(inst)
    m.objetivo.deactivate()
    m.otimo_fixado = pyo.Constraint(expr=sum(m.parcela[f] for f in m.parcela) == z)
    return m


def _resolver(m, solver, tempo, rotulo) -> None:
    res = modelo.resolver(m, solver=solver, tempo_limite=tempo)
    if not modelo.resolvido(res):
        raise RuntimeError(f"{rotulo}: sem otimo provado ({modelo.estado(res)})")


def _composicao(m, n: str) -> dict:
    """De que familias e feita a penalidade de `n` NESTA escala. Leitura, custo zero.

    CUIDADO ao ler: a composicao NAO e invariante. Entre as escalas otimas em que `p_n` vale
    o mesmo numero, as familias que o compoem podem mudar — o que sai aqui e a escala que o
    solver devolveu, nao propriedade do conjunto de otimos. Ver PROPOSTAS.md, P10.
    """
    valores = {f: round(pyo.value(m.pena_familia[n, f])) for f in m.parcela}
    return {f: v for f, v in valores.items() if v != 0}


def minimo_do_maximo(inst: Instancia, z: int, solver: str, tempo: int | None):
    """Menor penalidade individual maxima entre as escalas otimas. Minimax, uma resolucao."""
    m = _com_otimo_fixado(inst, z)
    m.t = pyo.Var(domain=pyo.NonNegativeReals)
    m.teto_pena = pyo.Constraint(list(inst.profissionais),
                                 rule=lambda m, n: m.t >= m.pena[n])
    m.minimax = pyo.Objective(expr=m.t, sense=pyo.minimize)
    _resolver(m, solver, tempo, f"{inst.id} minimax")
    perfil = {n: round(pyo.value(m.pena[n])) for n in inst.profissionais}
    comp = {n: _composicao(m, n) for n in inst.profissionais}
    return round(pyo.value(m.t)), perfil, modelo.atribuicoes(m), comp


def maximo_por_profissional(inst: Instancia, z: int, solver: str, tempo: int | None,
                            verboso: bool = True):
    """Forma B: para cada profissional, o maior `p_n` atingivel entre as escalas otimas.

    Imprime o andamento e grava o parcial a cada resolucao. Sao N resolucoes; no `long02`
    isso passa de duas horas, e sem gravacao incremental uma queda perto do fim jogaria fora
    a rodada inteira. O parcial vai para `experimento_b_parcial_<instancia>.csv`, que e
    apagado quando o alvo fecha.
    """
    total = len(inst.profissionais)
    parcial = SAIDA.with_name(f"experimento_b_parcial_{inst.id}.csv")
    perfil = _retomar(parcial, z)
    comp = {}
    if perfil:
        print(f"      retomando: {len(perfil)} de {total} ja estavam no parcial", flush=True)
    for i, n in enumerate(inst.profissionais, 1):
        if n in perfil:
            continue
        t0, c0 = time.time(), time.process_time()
        m = _com_otimo_fixado(inst, z)
        m.maximiza = pyo.Objective(expr=m.pena[n], sense=pyo.maximize)
        _resolver(m, solver, tempo, f"{inst.id} max p[{n}]")
        perfil[n] = round(pyo.value(m.pena[n]))
        comp[n] = _composicao(m, n)
        seg, cpu = time.time() - t0, time.process_time() - c0
        if verboso:
            # o relogio de parede conta o tempo em que a maquina ficou suspensa; o de CPU
            # nao. Quando os dois se afastam muito, o numero de parede nao mede nada.
            marca = "" if seg < 2 * cpu + 10 else f" [PAREDE {seg:.0f}s, MAQUINA SUSPENSA?]"
            print(f"      [{i:3d}/{total}] profissional {n:>4s}: max {perfil[n]:3d} "
                  f"({cpu:.1f}s de CPU, faltam ~{(total - i) * cpu / 60:.0f} min){marca}",
                  flush=True)
        _gravar_parcial(parcial, inst.id, z, perfil)
    return max(perfil.values()), perfil, comp


def _retomar(caminho: Path, z: int) -> dict:
    """Le o parcial de uma rodada interrompida, para nao refazer o que ja fechou.

    Existe porque em 22/09 a tampa do notebook foi fechada no meio do `long02`: o processo
    ficou suspenso dez horas e voltou do ponto em que estava. Se tivesse morrido, seriam duas
    horas de resolucoes jogadas fora. So retoma se o Z* do arquivo for o mesmo — parcial de
    outra rodada nao serve.
    """
    if not caminho.exists():
        return {}
    try:
        with caminho.open(newline="", encoding="utf-8-sig") as f:
            linhas = list(csv.DictReader(f, delimiter=";"))
        if not linhas or int(linhas[0]["Z"]) != z:
            return {}
        return {l["profissional"]: int(l["pena_maxima_entre_otimos"]) for l in linhas}
    except (KeyError, ValueError):
        return {}


def _gravar_parcial(caminho: Path, instancia: str, z: int, perfil: dict) -> None:
    caminho.parent.mkdir(exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["instancia", "Z", "profissional", "pena_maxima_entre_otimos"])
        w.writerows([[instancia, z, n, v] for n, v in perfil.items()])


def minimo_por_profissional(inst: Instancia, z: int, solver: str, tempo: int | None,
                            verboso: bool = True):
    """Para cada profissional, o MENOR `p_n` atingivel entre as escalas otimas.

    Simetrico do maximo, e responde outra pergunta: quem carrega penalidade **inevitavel**.
    "O profissional X sofre pelo menos Y violacoes em qualquer escala otima" identifica quem
    absorve a carga estruturalmente. Junto com o maximo, da o intervalo de cada pessoa — quem
    esta travado e quem tem margem. Decisao de 22/09, projeto de redacao.

    Sem isso, a unica invariancia demonstravel e a de quem tem maximo zero, porque ai o
    minimo tambem e zero por construcao.
    """
    perfil = {}
    total = len(inst.profissionais)
    for i, n in enumerate(inst.profissionais, 1):
        t0 = time.time()
        m = _com_otimo_fixado(inst, z)
        m.minimiza = pyo.Objective(expr=m.pena[n], sense=pyo.minimize)
        _resolver(m, solver, tempo, f"{inst.id} min p[{n}]")
        perfil[n] = round(pyo.value(m.pena[n]))
        if verboso:
            seg = time.time() - t0
            print(f"      [min {i:3d}/{total}] profissional {n:>4s}: min {perfil[n]:3d} "
                  f"({seg:.1f}s, faltam ~{(total - i) * seg / 60:.0f} min)", flush=True)
    return perfil


def maximo_geral(inst: Instancia, z: int, solver: str, tempo: int | None):
    """Forma A: binarias escolhem de quem e o maximo. M = Z*, valido porque 0 <= p_n <= Z*.

    Devolve so o maximo geral — nao ha perfil por profissional nesta forma.
    """
    m = _com_otimo_fixado(inst, z)
    profs = list(inst.profissionais)
    m.z = pyo.Var(profs, domain=pyo.Binary)
    m.um_escolhido = pyo.Constraint(expr=sum(m.z[n] for n in profs) == 1)
    m.t = pyo.Var(domain=pyo.NonNegativeReals)
    m.seletor = pyo.Constraint(profs, rule=lambda m, n: m.t <= m.pena[n] + z * (1 - m.z[n]))
    m.maximiza = pyo.Objective(expr=m.t, sense=pyo.maximize)
    _resolver(m, solver, tempo, f"{inst.id} maximax")
    return round(pyo.value(m.t)), {}, {}


def _gravar_composicao(instancia: str, z: int, comp_min: dict, comp_max: dict) -> None:
    """`resultados/experimento_b_composicao.csv`: de que familia e feita cada penalidade.

    Uma linha por (instancia, escala, profissional, familia), so com valor diferente de
    zero. `escala` diz de qual resolucao veio: `minimax` e a escala que minimiza o maior
    `p_n` — a mesma para todo mundo; `maximo_proprio` e, para cada pessoa, a escala que
    maximiza a penalidade DELA. Mescla com o arquivo, como os outros dois.

    Sai de graca: sao as mesmas resolucoes do experimento, lidas com mais detalhe. NAO e
    invariante — ver o aviso em `_composicao` e a P10.

    Numa rodada RETOMADA de um parcial, so os profissionais resolvidos nesta rodada tem
    linha em `maximo_proprio`: o parcial guarda o valor de `p_n`, nao a escala. Para a
    composicao completa de uma instancia, rodar ela inteira de uma vez.
    """
    novas = [{"instancia": instancia, "Z": z, "escala": escala, "profissional": n,
              "familia": f, "valor": v}
             for escala, d in (("minimax", comp_min), ("maximo_proprio", comp_max))
             for n, fam in d.items() for f, v in sorted(fam.items())]
    if not novas:
        return
    # a escala inteira e refeita a cada rodada: apagar as linhas antigas desta instancia
    # evita misturar composicoes de rodadas diferentes, que podem ser escalas diferentes.
    mesclar_csv(SAIDA.with_name("experimento_b_composicao.csv"), novas,
                ("instancia", "escala", "profissional", "familia"),
                remover=lambda k: k[0] == instancia)


# --- execucao -------------------------------------------------------------------------

def _gravar(linhas: list[dict], resumos: list[dict]) -> None:
    """Grava MESCLANDO com o que ja esta no arquivo.

    Com `--alvo`, cada rodada traz so uma instancia. Escrever por cima apagaria as anteriores
    — foi o que aconteceu em 22/09: rodar `--alvo long01` apagou as duas sprints do CSV.
    A chave e (instancia, profissional) no perfil e (instancia) no resumo: rodar de novo a
    mesma instancia atualiza as linhas dela e preserva as outras.

    As COLUNAS tambem se preservam, e por um motivo aprendido errando duas vezes. Na primeira,
    escrever por cima apagou LINHAS de outras instancias. Consertei preenchendo com vazio o
    que faltasse — mas so nas linhas, e o cabecalho continuava sendo o da rodada nova. Na
    segunda, em 22/09, a rodada `--por-pessoa` trocou a coluna `segundos` por
    `segundos_parede` e `segundos_cpu`, e a coluna `observacao` das longas — onde estava o
    registro da maquina suspensa — sumiu do arquivo inteiro. Perder coluna e tao ruim quanto
    perder linha, e mais silencioso. A regra mora em `src/tabela.py`, que roda sem Pyomo e tem
    os dois acidentes como caso de teste: `python src\\tabela.py`.
    """
    mesclar_csv(SAIDA, linhas, ("instancia", "profissional"))
    mesclar_csv(SAIDA.with_name("experimento_b_resumo.csv"), resumos, ("instancia",))


def rodar(nome: str, caminho: str, z_tabela: int, forma: str, solver: str,
          tempo: int | None, verboso: bool = True,
          por_pessoa: bool = False) -> tuple[dict, list[dict]]:
    inst = ler_instancia(caminho)
    n_prof = len(inst.profissionais)
    # dois relogios: o de parede conta o tempo em que a maquina ficou suspensa, o de CPU nao.
    # Para o texto vale o de CPU — tempo de resolucao e afirmacao fraca, mas tem de ser
    # medida, nao soma de espera.
    t0, c0 = time.time(), time.process_time()

    # 1) o otimo, que tambem confere a Tabela 6 antes de qualquer coisa
    m0 = modelo.construir(inst)
    _resolver(m0, solver, tempo, f"{nome} otimo")
    z = modelo.valor_objetivo(m0)
    if z != z_tabela:
        raise RuntimeError(f"{nome}: objetivo {z}, esperado {z_tabela} (Tabela 6)")

    # 2) o lado do minimo
    mn, perfil_min, escala_min, comp_min = minimo_do_maximo(inst, z, solver, tempo)
    conferencia = por_profissional(inst, escala_min)
    divergem = [n for n in inst.profissionais if perfil_min[n] != conferencia.get(n, 0)]
    if divergem:
        raise RuntimeError(f"{nome}: m.pena diverge de avaliacao.py na escala minimax "
                           f"em {len(divergem)} profissionais")

    # 3) o lado do maximo
    if forma == "B":
        mx, perfil_max, comp_max = maximo_por_profissional(inst, z, solver, tempo, verboso)
        SAIDA.with_name(f"experimento_b_parcial_{inst.id}.csv").unlink(missing_ok=True)
    else:
        mx, perfil_max, comp_max = maximo_geral(inst, z, solver, tempo)
    _gravar_composicao(nome, z, comp_min, comp_max)

    # 4) o lado do minimo POR PESSOA, opcional: dobra o numero de resolucoes
    perfil_min_pessoa = minimo_por_profissional(inst, z, solver, tempo, verboso) \
        if por_pessoa else {}

    piso_teorico = math.ceil(z / n_prof)
    media = z / n_prof
    # As duas grandezas que vao para o texto sao razoes sobre a MEDIA Z*/N, nao sobre Z*.
    # Dividir pelo total encolhe mecanicamente quando N cresce, e a comparacao entre
    # instancias de tamanhos diferentes vira aritmetica em vez de propriedade do problema.
    # Correcao do projeto de redacao, 22/09.
    resumo = {
        "instancia": nome, "Z": z, "profissionais": n_prof, "forma": forma,
        "media_por_profissional": round(media, 2),
        "piso_teorico": piso_teorico, "min_do_max": mn, "max_do_max": mx,
        "amplitude": mx - mn,
        "concentracao_inevitavel": round(mn / media, 2),   # min do max / media
        "margem_de_gestao": round(mx / mn, 2),             # max do max / min do max
        "segundos_parede": round(time.time() - t0, 1),
        "segundos_cpu": round(time.process_time() - c0, 1), "solver": solver,
    }
    linhas = [{
        "instancia": nome, "Z": z, "profissional": n,
        "pena_na_escala_minimax": perfil_min[n],
        "pena_minima_entre_otimos": perfil_min_pessoa.get(n, ""),
        "pena_maxima_entre_otimos": perfil_max.get(n, ""),
    } for n in inst.profissionais]
    return resumo, linhas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--todos", action="store_true", help="inclui long01 e long02")
    ap.add_argument("--forma", default="B", choices=("A", "B"),
                    help="B: uma resolucao por profissional, com perfil. A: binarias")
    ap.add_argument("--solver", default=modelo.SOLVER_PADRAO)
    ap.add_argument("--tempo", type=int, default=None, help="limite por resolucao, em segundos")
    ap.add_argument("--alvo", action="append",
                    help="roda so esta instancia; pode repetir. Util para as longas, que"
                         " levam horas na forma B")
    ap.add_argument("--quieto", action="store_true", help="sem o andamento resolucao a resolucao")
    ap.add_argument("--por-pessoa", action="store_true",
                    help="tambem o MINIMO de cada profissional, dando o intervalo individual."
                         " Dobra o numero de resolucoes: minutos nas sprints, horas nas longas")
    a = ap.parse_args()

    alvos = ALVOS if a.todos else ALVOS[:2]
    if a.alvo:
        escolhidos = {x.lower() for x in a.alvo}
        alvos = [x for x in ALVOS if x[0].lower() in escolhidos]
        if not alvos:
            print(f"alvo desconhecido; escolha entre {[x[0] for x in ALVOS]}")
            return 1
    print(f"Experimento B, forma {a.forma}, solver {a.solver}, {len(alvos)} alvos")
    print(f"{'instancia':10s}{'Z':>5s}{'N':>4s}{'media':>7s}{'min max':>9s}"
          f"{'max max':>9s}{'concentr':>10s}{'margem':>8s}{'seg':>8s}")
    resumos, linhas = [], []
    for nome, caminho, z in alvos:
        try:
            r, ls = rodar(nome, caminho, z, a.forma, a.solver, a.tempo, not a.quieto,
                          a.por_pessoa)
        except RuntimeError as e:
            print(f"   FALHOU {e}")
            return 1
        resumos.append(r)
        linhas += ls
        _gravar(linhas, resumos)   # grava a cada alvo: uma queda nao perde o que ja rodou
        print(f"{r['instancia']:10s}{r['Z']:5d}{r['profissionais']:4d}"
              f"{r['media_por_profissional']:7.2f}{r['min_do_max']:9d}{r['max_do_max']:9d}"
              f"{r['concentracao_inevitavel']:9.1f}x{r['margem_de_gestao']:7.1f}x"
              f"{r['segundos_cpu']:8.1f}")

    resumo_csv = SAIDA.with_name("experimento_b_resumo.csv")
    print()
    print(f"perfil por profissional: {SAIDA}")
    print(f"resumo:                  {resumo_csv}")
    print()
    print("Leitura, em multiplos da media Z*/N — NUNCA em porcentagem de Z*, que encolhe")
    print("mecanicamente quando N cresce:")
    print("  concentracao inevitavel = min do max / media. Quanto a pessoa mais sobrecarregada")
    print("     carrega mesmo na escala otima mais equilibrada. Nenhuma escolha evita isso.")
    print("  margem de gestao = max do max / min do max. Quanto a escolha entre escalas otimas")
    print("     muda a carga de quem sai pior. E o espaco de decisao que o custo total deixa.")
    print("Sao grandezas distintas: uma instancia pode ter muita concentracao e pouca margem.")
    print("No lote early todos os pesos valem 1, entao penalidade = contagem de violacoes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
