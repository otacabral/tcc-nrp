"""Experimento A: o efetivo minimo viavel em 8 h e em 12x36, a horas de assistencia fixas.

Roda da raiz do repositorio, com a .venv ativa:

    python src\\experimento_a.py --piloto        # 2 celulas, so para ver se anda
    python src\\experimento_a.py                 # as 4 celulas do grau intermediario
    python src\\experimento_a.py --todos         # os 5 graus x 2 regimes x 2 regras

Saida: `resultados/experimento_a.csv`, gravado a cada celula concluida, mesclando com o que
ja estiver la. Separador ";" e utf-8-sig.

## A pergunta

As horas de assistencia sao a primitiva e nao mudam: 5.920 h em 28 dias, do Parecer COFEN.
Mudando so o regime de jornada, **de quantas pessoas se precisa para cobrir a mesma
assistencia sem violar a lei?**

## Por que nao e capacidade dividida por demanda

Porque com os limites legais como restricoes RIGIDAS a resposta nao e uma divisao. O piso de
capacidade — plantoes necessarios dividido pelo maximo de plantoes por pessoa — da **36 nos
dois regimes, em todos os graus**, por construcao do gerador: e o mesmo total de horas. Se a
resposta fosse divisao, o experimento nao teria o que medir.

O que se mede e **a distancia entre esse piso e o menor efetivo que de fato fecha uma escala
legal**. Essa distancia e o custo de encaixe: interjornada de 11 h, descanso semanal,
alternancia do 12x36, e o fato de que as pessoas sao inteiras e os turnos tambem.

## O que este script reporta, e o que nao reporta

Reporta **intervalo**, nunca ponto (decisao de 21/09). Para cada celula:

- `maior_inviavel` — o maior efetivo com INVIABILIDADE PROVADA pelo solver;
- `menor_viavel` — o menor efetivo com escala exibida e conferida;
- `indeterminados` — os efetivos em que o solver bateu no limite de tempo sem decidir.

Se a lista de indeterminados estiver vazia, o minimo viavel e `menor_viavel` e o intervalo e
degenerado. Se nao estiver, o minimo esta em algum lugar do intervalo, e **e o intervalo que
vai para o texto**. Um "nao decidiu" NUNCA e contado como inviavel: seria transformar limite
de tempo em resultado.

## Conferencia

Toda escala viavel e gravada em XML e passada pelo AVALIADOR OFICIAL. O que se exige dele:
zero violacao nas tres familias que aqui sao rigidas (`MaxNumAssignments`,
`MaxConsecutiveWorkingDays`, `UnwantedPatterns`). Se o avaliador cobrar alguma, a escala nao
e legal e a celula falha — a rigidez teria ficado so no modelo. Ver P7.3 e DECISOES.md,
"Definicao de viavel".
"""

from __future__ import annotations

import argparse
import math
import subprocess
import sys
import time
from pathlib import Path

import pyomo.environ as pyo

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import instancia_br as br  # noqa: E402
import modelo  # noqa: E402
import solucao  # noqa: E402
from tabela import mesclar_csv  # noqa: E402

SAIDA = RAIZ / "resultados" / "experimento_a.csv"
ESCALAS = RAIZ / "resultados" / "experimento_a"
AVALIADOR = RAIZ / "avaliador"
CLASSE = "dds.nrp.core.evaluation.ScheduleEvaluator"

# as tres familias que o `rigidas_legais` torna rigidas; o avaliador tem de cobrar zero nelas
NOMES_AVALIADOR = {
    "max_num_assignments": "Maximum number of assignments",
    "max_consecutive_working_days": "Maximum number of consecutive working days",
    "unwanted_patterns": "Unwanted pattern",
}

# Quatro respostas, nao tres. `indeterminado` e "o solver rodou e nao decidiu" — limite de
# tempo, tipicamente. `erro` e "o solver nem chegou a responder". Os dois impedem a conclusao,
# mas por motivos opostos: o primeiro pede mais tempo, o segundo pede conserto. Misturar os
# dois esconde defeito atras de uma palavra que parece resultado — foi o que aconteceu em
# 22/09, quando vinte celulas registraram "indeterminado" e a causa era excecao no codigo.
VIAVEL, INVIAVEL, INDETERMINADO, ERRO = "viavel", "inviavel", "indeterminado", "erro"


def classificar(resultado) -> str:
    """Tres respostas, nao duas. `maxTimeLimit` nao e inviabilidade."""
    e = modelo.estado(resultado).lower()
    if "infeasible" in e:
        return INVIAVEL
    if "optimal" in e or "feasible" in e:
        return VIAVEL
    return INDETERMINADO


def piso_de_capacidade(inst, regime: str) -> int:
    """Plantoes necessarios / maximo de plantoes por pessoa. E o denominador do experimento."""
    return math.ceil(inst.demanda_total / br.MAX_ATRIBUICOES[regime])


def conferir_no_avaliador(inst, escala, arquivo: Path) -> list[str]:
    """Roda o avaliador oficial e exige zero nas tres familias rigidas.

    Devolve a lista de problemas; vazia = escala legal. Se o `java` nao estiver disponivel a
    conferencia nao acontece, e isso e dito em voz alta em vez de passar batido.
    """
    solucao.escrever_xml(inst, escala, arquivo)
    entrada = arquivo.with_name(f"{inst.id}_instancia.xml")
    br.escrever_xml(inst, entrada)
    try:
        r = subprocess.run(
            ["java", "-cp", str(AVALIADOR / "*"), CLASSE, str(entrada), str(arquivo)],
            capture_output=True, text=True, timeout=300)
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return [f"avaliador nao rodou ({type(e).__name__}) - escala NAO conferida"]
    saida = r.stdout + r.stderr
    arquivo.with_suffix(".avaliador.txt").write_text(saida, encoding="utf-8")
    if "Hard constraints violation" in saida:
        return ["o avaliador reprovou as rigidas (cobertura ou um turno por dia)"]
    return [f"o avaliador cobrou {rotulo}, que aqui e rigida"
            for rotulo in NOMES_AVALIADOR.values() if rotulo in saida]


def tentar(grau: str, regime: str, regra: str, efetivo: int, solver: str,
           tempo: int | None) -> tuple[str, object, object]:
    """Uma resolucao de viabilidade. NUNCA levanta: a resposta pode ser "inviavel".

    Resolve com `carregar=False` porque aqui a inviabilidade e resposta esperada, e o
    appsi/HiGHS levanta `RuntimeError` se tentar carregar solucao que nao existe. A solucao
    so e carregada depois de o veredito dizer que ha uma.

    Qualquer excecao inesperada vira ERRO, nunca INVIAVEL: confundir "o solver quebrou" com
    "nao existe escala legal" produziria um efetivo minimo inflado, e ninguem notaria olhando
    so o CSV. E ERRO em vez de INDETERMINADO porque as duas coisas pedem providencias
    diferentes — mais tempo contra conserto de codigo.
    """
    inst = br.construir(grau=grau, regime=regime, regra=regra, efetivo=efetivo)
    m = modelo.construir(inst, flexiveis=True, habilidade_rigida=True,
                         noite_antes_de_fds_livre=True,
                         rigidas_legais=modelo.RIGIDAS_LEGAIS_BR)
    try:
        resultado = modelo.resolver(m, solver=solver, tempo_limite=tempo, carregar=False)
    except Exception as e:  # noqa: BLE001
        print(f"      [ERRO] o solver levantou {type(e).__name__}: {e}")
        return ERRO, inst, None
    veredito = classificar(resultado)
    if veredito != VIAVEL:
        return veredito, inst, None
    if not modelo.carregar_solucao(m, resultado):
        print("      [ERRO] solver declarou viavel mas nao entregou solucao")
        return ERRO, inst, None
    return VIAVEL, inst, modelo.atribuicoes(m)


def celula(grau: str, regime: str, regra: str, solver: str, tempo: int | None,
           margem: int, verboso: bool = True) -> dict:
    """Varre o efetivo para cima a partir do piso de capacidade, e para no primeiro viavel.

    Varredura linear, nao busca binaria, de proposito: a busca binaria precisa que cada
    resposta seja definitiva, e aqui ela pode ser "nao decidiu". Um indeterminado no meio de
    uma binaria contamina metade do intervalo em silencio. Linear a partir do piso tambem e
    barata quando a resposta esta perto dele, que e a expectativa.
    """
    base = br.construir(grau=grau, regime=regime, regra=regra, efetivo=36)
    piso = piso_de_capacidade(base, regime)
    rotulo = f"{grau}/{regime}/{regra}"
    if verboso:
        print(f"\n{rotulo}: demanda {base.demanda_total} plantoes, "
              f"teto {br.MAX_ATRIBUICOES[regime]} por pessoa, piso de capacidade {piso}")

    maior_inviavel, menor_viavel, indeterminados, problemas = None, None, [], []
    t0 = time.process_time()

    # Sonda em `piso - 1`, ANTES da varredura. Serve a duas coisas. Primeira: fecha o
    # intervalo por baixo — sem ela, uma celula viavel ja no piso sai com `maior_inviavel`
    # vazio, e o intervalo fica aberto num lado. Segunda, e mais importante: e um teste do
    # MODELO contra a aritmetica. Com um profissional a menos a capacidade nao cobre a
    # demanda, entao a resposta TEM de ser inviavel. Se vier viavel, a cobertura ou o teto
    # nao estao valendo, e o resultado da celula nao vale nada.
    # Limite proprio, mais curto: com capacidade menor que a demanda a propria relaxacao
    # linear ja e inviavel, entao o solver decide em instantes. Se demorar, e sinal de que o
    # modelo nao e o que eu penso, e nao vale gastar o limite inteiro vinte vezes.
    erros = []
    veredito, _, _ = tentar(grau, regime, regra, piso - 1, solver, min(tempo or 120, 120))
    if verboso:
        print(f"   efetivo {piso - 1:3d}: {veredito:14s} (sonda abaixo do piso)", flush=True)
    if veredito == INVIAVEL:
        maior_inviavel = piso - 1
    elif veredito == VIAVEL:
        problemas.append(f"CONTRADICAO: efetivo {piso - 1} viavel, abaixo do piso de "
                         f"capacidade {piso}. A cobertura ou o teto nao estao valendo.")
        print(f"      {problemas[-1]}")
    elif veredito == ERRO:
        erros.append(piso - 1)
        problemas.append(f"a sonda em {piso - 1} deu erro: o intervalo fica aberto por baixo")
    else:
        indeterminados.append(piso - 1)

    for efetivo in range(piso, piso + margem + 1):
        c0 = time.process_time()
        veredito, inst, escala = tentar(grau, regime, regra, efetivo, solver, tempo)
        seg = time.process_time() - c0
        if verboso:
            print(f"   efetivo {efetivo:3d}: {veredito:14s} ({seg:6.1f}s de CPU)", flush=True)
        if veredito == INVIAVEL:
            maior_inviavel = efetivo
        elif veredito == INDETERMINADO:
            indeterminados.append(efetivo)
        elif veredito == ERRO:
            # nao e viavel nem inviavel: nao da para continuar subindo como se soubesse algo
            erros.append(efetivo)
            problemas.append(f"erro do solver em {efetivo}; a varredura parou aqui")
            break
        else:
            ESCALAS.mkdir(parents=True, exist_ok=True)
            problemas += conferir_no_avaliador(inst, escala, ESCALAS / f"{inst.id}.xml")
            if problemas:
                print(f"      CONFERENCIA FALHOU: {problemas}")
            menor_viavel = efetivo
            break

    return {
        "grau": grau, "regime": regime, "regra": regra,
        "demanda_plantoes": base.demanda_total,
        "teto_por_pessoa": br.MAX_ATRIBUICOES[regime],
        "piso_de_capacidade": piso,
        "quadro_referencia": round(br.quadro_referencia(), 2),
        "maior_inviavel": maior_inviavel if maior_inviavel is not None else "",
        "menor_viavel": menor_viavel if menor_viavel is not None else "",
        "indeterminados": ",".join(str(x) for x in indeterminados),
        "erros_do_solver": ",".join(str(x) for x in erros),
        "intervalo": (f"[{maior_inviavel + 1}, {menor_viavel}]"
                      if maior_inviavel is not None and menor_viavel is not None
                      else f"[?, {menor_viavel}]" if menor_viavel is not None else "[?, ?]"),
        "distancia_do_piso": (f"{(menor_viavel - piso) / piso:.1%}"
                              if menor_viavel is not None else ""),
        "conferencia": "ok" if menor_viavel is not None and not problemas
                       else ("; ".join(problemas) if problemas else "sem viavel na faixa"),
        "segundos_cpu": round(time.process_time() - t0, 1),
        "solver": solver,
    }


def gravar(linhas: list[dict]) -> None:
    """Mescla por (grau, regime, regra). A regra esta em `src/tabela.py`, com os testes."""
    mesclar_csv(SAIDA, linhas, ("grau", "regime", "regra"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--todos", action="store_true", help="os cinco graus, nao so o do meio")
    ap.add_argument("--piloto", action="store_true",
                    help="so 12x36/teto e 8h/teto no grau intermediario, para medir o tempo")
    ap.add_argument("--grau", action="append", choices=sorted(br.GRAUS))
    ap.add_argument("--solver", default=modelo.SOLVER_PADRAO)
    ap.add_argument("--tempo", type=int, default=600,
                    help="limite por resolucao, em segundos (padrao 600)")
    ap.add_argument("--margem", type=int, default=12,
                    help="quantos efetivos acima do piso tentar antes de desistir")
    ap.add_argument("--quieto", action="store_true")
    a = ap.parse_args()

    graus = a.grau or (sorted(br.GRAUS) if a.todos else ["intermediario"])
    celulas = [(g, r, x) for g in graus for r in ("12x36", "8h")
               for x in ("teto", "maior_resto")]
    if a.piloto:
        celulas = [("intermediario", "12x36", "teto"), ("intermediario", "8h", "teto")]

    print(f"Experimento A: {len(celulas)} celulas, solver {a.solver}, "
          f"limite {a.tempo}s por resolucao")
    print("Horas de assistencia fixas em 5.920 h; muda so o regime. O piso de capacidade e")
    print("36 nos dois regimes por construcao — o que se mede e a distancia ate ele.")

    linhas = []
    for grau, regime, regra in celulas:
        linhas.append(celula(grau, regime, regra, a.solver, a.tempo, a.margem, not a.quieto))
        gravar(linhas)

    print(f"\n{'celula':36s}{'piso':>6s}{'intervalo':>12s}{'distancia':>11s}"
          f"{'indet.':>8s}{'erros':>8s}{'conferencia':>14s}")
    for r in linhas:
        conf = str(r["conferencia"])
        print(f"  {r['grau']:15s}{r['regime']:7s}{r['regra']:12s}{r['piso_de_capacidade']:6d}"
              f"{r['intervalo']:>12s}{str(r['distancia_do_piso']):>11s}"
              f"{str(r['indeterminados']):>8s}{str(r['erros_do_solver']):>8s}"
              f"{(conf if len(conf) <= 13 else conf[:10] + '...'):>14s}")
    print(f"\nresultado: {SAIDA}")
    print("escalas e saidas do avaliador: resultados/experimento_a/")

    fechadas = [r for r in linhas if r["conferencia"] == "ok" and r["maior_inviavel"] != ""]
    com_erro = [r for r in linhas if r["erros_do_solver"]]
    print(f"\ncelulas com intervalo FECHADO nos dois lados e conferencia ok: "
          f"{len(fechadas)} de {len(linhas)}")
    if com_erro:
        print(f"celulas com erro do solver: {len(com_erro)} — o intervalo delas esta aberto,")
        print("e 'aberto' nao e resultado. Conferir a mensagem antes de ler qualquer numero.")
    print()
    print("LEITURA: comparar os dois regimes pelo INTERVALO inteiro, nunca pela ponta que")
    print("favorece. Onde houver indeterminado, o minimo esta dentro do intervalo, nao no")
    print("`menor_viavel`. Celula com `conferencia` diferente de `ok` nao vale como resultado.")
    return 1 if com_erro else 0


if __name__ == "__main__":
    raise SystemExit(main())
