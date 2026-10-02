"""Experimento A: o efetivo minimo viavel em 8 h e em 12x36, a horas de assistencia fixas.

Roda da raiz do repositorio, com a .venv ativa:

    python src\\experimento_a.py --sensibilidade   # A VARREDURA QUE INTERESSA (ver abaixo)
    python src\\experimento_a.py --piloto        # 2 celulas, so para ver se anda
    python src\\experimento_a.py                 # as 4 celulas do grau intermediario
    python src\\experimento_a.py --todos         # os 5 graus x 2 regimes x 2 regras

Saida: `resultados/experimento_a.csv`, gravado a cada celula concluida, mesclando com o que
ja estiver la. Separador ";" e utf-8-sig.

## A pergunta

As horas de assistencia sao a primitiva e nao mudam: 5.920 h em 28 dias, do Parecer COFEN.
Mudando so o regime de jornada, **de quantas pessoas se precisa para cobrir a mesma
assistencia sem violar a lei?**

## O que a rodada de demanda PLANA respondeu, e o escopo dela

Vinte celulas, intervalo [36, 36] em todas, distancia 0,0%. **A leitura autorizada e estreita**
(projeto de redacao, 23/09): *sob demanda uniforme, nenhuma restricao de escalonamento aperta
alem do teto de horas, em nenhum dos dois regimes*. NAO e "o regime nao muda o efetivo".

O motivo do escopo estreito: com perfil uniforme **nenhuma restricao tinha como apertar**. A
alternancia do 12x36 preenche janelas alternadas exatamente; a composicao por categoria fecha
sozinha porque a proporcao e igual em toda janela; o piso de um enfermeiro por turno fica
longe do limite. E as vinte celulas sao a mesma aritmetica replicada, nao vinte testes
independentes.

O que sobrevive como achado: as regras de descanso, **inclusive as 36 h apos o noturno**, nao
forcam ociosidade no 12x36 — e a sonda provando 35 inviavel e afirmacao forte.

## A varredura que interessa: `--sensibilidade`

A hipotese do trabalho e sobre demanda que VARIA. Com demanda plana a rigidez do 12x36 sai de
graca e a hipotese nao chega a ser testada. `--sensibilidade` varia a demanda entre dias
mantendo o nivel: grau intermediario, dois regimes, regra de teto, variacao 0, 0,5 e 1.

A forma da variacao e **medida no `long01`** — 29 atribuicoes por dia util contra 20 por dia
de fim de semana —, nao arbitrada. E a mesma logica de "calibrado ao porte" que ja governa o
nivel, estendida do nivel para a forma. Ver `instancia_br.fatores_por_dia`.

## Os dois pisos

- **piso de capacidade** = plantoes / teto de plantoes por pessoa. E o denominador da coluna
  `distancia_do_piso`, nas rodadas antigas e nas novas;
- **piso de alternancia** = o limite que vem de `max_consecutive_working_days`. No 12x36, onde
  o limite e 1 dia, dois dias seguidos precisam de gente inteiramente diferente, entao o
  efetivo tem de cobrir a SOMA de dois dias consecutivos. Com demanda plana nunca aperta; com
  demanda variando, pode passar do piso de capacidade — e e exatamente a rigidez em questao.

A varredura comeca no maior dos dois. Os dois sao limites inferiores validos, calculados sem
resolver nada.

## O que este script reporta, e o que nao reporta

Reporta **intervalo**, nunca ponto (decisao de 21/09). Para cada celula:

- `maior_inviavel` — o maior efetivo com INVIABILIDADE PROVADA pelo solver;
- `menor_viavel` — o menor efetivo com escala exibida e conferida;
- `indeterminados` — os efetivos em que o solver bateu no limite de tempo sem decidir;
- `erros_do_solver` — os efetivos em que o solver nem chegou a responder.

Se indeterminados e erros estiverem vazios, o intervalo e degenerado e o minimo e exato. Se
nao, o minimo esta DENTRO do intervalo, e e o intervalo que vai para o texto. Um "nao decidiu"
NUNCA e contado como inviavel: seria transformar limite de tempo em resultado.

**Tempo de resolucao e afirmacao fraca** pelo criterio do projeto: cabe uma frase no capitulo
de metodo, com escopo declarado, nunca um resultado.

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
import csv
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
    if "optimal" in e or "feasible" in e or modelo.tem_solucao(resultado):
        return VIAVEL           # parado no limite de tempo com escala tambem e viavel
    return INDETERMINADO


def piso_de_capacidade(inst, regime: str) -> int:
    """Plantoes necessarios / maximo de plantoes por pessoa. E o denominador do experimento."""
    return math.ceil(inst.demanda_total / br.MAX_ATRIBUICOES[regime])


def piso_de_alternancia(inst, limite: int | None = None) -> int:
    """Segundo piso, que so aparece quando a demanda varia entre dias.

    Se o contrato limita a `L` dias consecutivos de trabalho, entao em qualquer janela de
    `L + 1` dias seguidos cada pessoa trabalha no maximo `L` deles. Logo
    `N >= ceil(demanda da janela / L)`. E limite inferior valido, sem resolver nada.

    No 12x36 `L = 1`, e o limite vira **a soma de dois dias consecutivos**: quem trabalha hoje
    nao pode trabalhar amanha, entao os dois dias precisam de gente diferente. Com demanda
    plana isso nunca aperta — dois dias iguais somam o dobro da media e sobra efetivo. Com
    demanda variando, dois dias UTEIS seguidos somam muito mais que a media, e o limite pode
    passar do piso de capacidade. E exatamente a rigidez que o Experimento A com demanda plana
    nao tinha como medir.

    Devolve 0 quando o contrato nao limita dias consecutivos.

    `limite` substitui o do contrato quando outra regra aperta mais — com turnos
    configurados so de 12 h, a regra das 36 h ja proibe dois dias seguidos, embora o contrato
    diga 6 (ver `ferramenta.limite_efetivo`).
    """
    c = inst.contratos["0"].max_consecutive_working_days
    if limite is None:
        if not c.ativa or c.valor < 1:
            return 0
        limite = c.valor
    L = limite
    dias = inst.dias
    por_dia = {d: 0 for d in dias}
    for (d, _), q in inst.demanda.items():
        por_dia[d] = por_dia.get(d, 0) + q
    if L >= len(dias):
        return 0
    return max(math.ceil(sum(por_dia[d] for d in dias[i:i + L + 1]) / L)
               for i in range(len(dias) - L))


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
           tempo: int | None, variacao: float = 0.0, **entrada) -> tuple[str, object, object]:
    """Uma resolucao de viabilidade. NUNCA levanta: a resposta pode ser "inviavel".

    Resolve com `carregar=False` porque aqui a inviabilidade e resposta esperada, e o
    appsi/HiGHS levanta `RuntimeError` se tentar carregar solucao que nao existe. A solucao
    so e carregada depois de o veredito dizer que ha uma.

    Qualquer excecao inesperada vira ERRO, nunca INVIAVEL: confundir "o solver quebrou" com
    "nao existe escala legal" produziria um efetivo minimo inflado, e ninguem notaria olhando
    so o CSV. E ERRO em vez de INDETERMINADO porque as duas coisas pedem providencias
    diferentes — mais tempo contra conserto de codigo.

    `entrada` vai direto para `instancia_br.construir` (razao_fds, indisponibilidades...),
    para os testes da ferramenta resolverem com as MESMAS opcoes de modelo daqui, sem copia.
    """
    inst = br.construir(grau=grau, regime=regime, regra=regra, efetivo=efetivo,
                        variacao=variacao, **entrada)
    return resolver_instancia(inst, solver, tempo)


def modelo_br(inst, custo_atribuicao=None):
    """O modelo com as opcoes da instancia brasileira. As opcoes moram SO aqui: limites
    legais rigidos, habilidade rigida, noite antes de fim de semana livre ligada."""
    return modelo.construir(inst, flexiveis=True, habilidade_rigida=True,
                            noite_antes_de_fds_livre=True,
                            rigidas_legais=modelo.RIGIDAS_LEGAIS_BR,
                            custo_atribuicao=custo_atribuicao)


def resolver_instancia(inst, solver: str, tempo: int | None,
                       custo_atribuicao=None) -> tuple[str, object, object]:
    """O miolo de `tentar`, para uma instancia ja montada — a de turnos configurados, por
    exemplo."""
    veredito, escala = resolver_modelo(modelo_br(inst, custo_atribuicao), solver, tempo)
    return veredito, inst, escala


def resolver_modelo(m, solver: str, tempo: int | None) -> tuple[str, object]:
    """Resolve um modelo ja montado. NUNCA levanta. Devolve (veredito, escala ou None); o
    modelo fica com a solucao carregada, para quem quiser resolver de novo por cima dele."""
    try:
        resultado = modelo.resolver(m, solver=solver, tempo_limite=tempo, carregar=False)
    except Exception as e:  # noqa: BLE001
        print(f"      [ERRO] o solver levantou {type(e).__name__}: {e}")
        return ERRO, None
    veredito = classificar(resultado)
    if veredito != VIAVEL:
        return veredito, None
    if not modelo.carregar_solucao(m, resultado):
        print("      [ERRO] solver declarou viavel mas nao entregou solucao")
        return ERRO, None
    return VIAVEL, modelo.atribuicoes(m)


def celula(grau: str, regime: str, regra: str, solver: str, tempo: int | None,
           margem: int, verboso: bool = True, variacao: float = 0.0) -> dict:
    """Varre o efetivo para cima a partir do piso de capacidade, e para no primeiro viavel.

    Varredura linear, nao busca binaria, de proposito: a busca binaria precisa que cada
    resposta seja definitiva, e aqui ela pode ser "nao decidiu". Um indeterminado no meio de
    uma binaria contamina metade do intervalo em silencio. Linear a partir do piso tambem e
    barata quando a resposta esta perto dele, que e a expectativa.
    """
    base = br.construir(grau=grau, regime=regime, regra=regra, efetivo=36, variacao=variacao)
    piso_cap = piso_de_capacidade(base, regime)
    piso_alt = piso_de_alternancia(base)
    # A varredura comeca no MAIOR dos dois limites conhecidos. Comecar abaixo dele seria
    # gastar resolucoes provando de novo, com solver, o que a aritmetica ja diz.
    piso = max(piso_cap, piso_alt)
    rotulo = f"{grau}/{regime}/{regra}/v{variacao:g}"
    if verboso:
        extra = (f", piso de alternancia {piso_alt}" + ("  <-- e ele que manda"
                 if piso_alt > piso_cap else "")) if piso_alt else ""
        print(f"\n{rotulo}: demanda {base.demanda_total} plantoes, "
              f"teto {br.MAX_ATRIBUICOES[regime]} por pessoa, "
              f"piso de capacidade {piso_cap}{extra}")

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
    veredito, _, _ = tentar(grau, regime, regra, piso - 1, solver, min(tempo or 120, 120),
                            variacao)
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
        veredito, inst, escala = tentar(grau, regime, regra, efetivo, solver, tempo, variacao)
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
        "grau": grau, "regime": regime, "regra": regra, "variacao": variacao,
        "demanda_plantoes": base.demanda_total,
        "teto_por_pessoa": br.MAX_ATRIBUICOES[regime],
        "piso_de_capacidade": piso_cap,
        "piso_de_alternancia": piso_alt,
        "piso_usado": piso,
        "quadro_referencia": round(br.quadro_referencia(), 2),
        "maior_inviavel": maior_inviavel if maior_inviavel is not None else "",
        "menor_viavel": menor_viavel if menor_viavel is not None else "",
        "indeterminados": ",".join(str(x) for x in indeterminados),
        "erros_do_solver": ",".join(str(x) for x in erros),
        "intervalo": (f"[{maior_inviavel + 1}, {menor_viavel}]"
                      if maior_inviavel is not None and menor_viavel is not None
                      else f"[?, {menor_viavel}]" if menor_viavel is not None else "[?, ?]"),
        # o denominador continua sendo o piso de CAPACIDADE, para a coluna significar a
        # mesma coisa nas rodadas antigas e nas novas. O piso de alternancia vai ao lado.
        "distancia_do_piso": (f"{(menor_viavel - piso_cap) / piso_cap:.1%}"
                              if menor_viavel is not None else ""),
        "conferencia": "ok" if menor_viavel is not None and not problemas
                       else ("; ".join(problemas) if problemas else "sem viavel na faixa"),
        "segundos_cpu": round(time.process_time() - t0, 1),
        "solver": solver,
    }


CHAVE = ("grau", "regime", "regra", "variacao")


def _migrar_variacao() -> None:
    """As rodadas ate 23/09 nao tinham a coluna `variacao`, e ela entrou na CHAVE.

    Sem isto as vinte linhas antigas seriam descartadas na mesclagem, porque nao tem valor
    para uma coluna da chave — a mesma perda de linhas de 22/09, entrando por outra porta.
    Todas elas foram rodadas com demanda plana, entao a migracao e escrever `0.0` onde falta.
    Idempotente: depois da primeira vez nao acha mais nada para mexer.
    """
    if not SAIDA.exists():
        return
    with SAIDA.open(newline="", encoding="utf-8-sig") as f:
        leitor = csv.DictReader(f, delimiter=";")
        colunas = list(leitor.fieldnames or [])
        if "variacao" in colunas:
            return
        linhas = [dict(l, variacao="0.0") for l in leitor]
    if not linhas:
        return
    colunas.insert(colunas.index("regra") + 1 if "regra" in colunas else len(colunas),
                   "variacao")
    with SAIDA.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=colunas, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)
    print(f"   [migracao] {len(linhas)} linhas antigas marcadas com variacao = 0.0")


def gravar(linhas: list[dict]) -> None:
    """Mescla por (grau, regime, regra, variacao).

    A variacao entra na chave: sem ela, uma rodada de sensibilidade sobrescreveria a celula
    de demanda plana, que e o ponto de comparacao.
    """
    _migrar_variacao()
    mesclar_csv(SAIDA, linhas, CHAVE)


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
    ap.add_argument("--sensibilidade", action="store_true",
                    help="a varredura de variacao de demanda entre dias: grau intermediario,"
                         " dois regimes, regra de teto, variacao 0, 0,5 e 1. Prioridade 1 do"
                         " projeto de redacao, 23/09")
    ap.add_argument("--variacao", action="append", type=float,
                    help="nivel de variacao de demanda entre dias; pode repetir. 0 = plano,"
                         " 1 = a forma medida no long01 (29 uteis contra 20 no fim de semana)")
    a = ap.parse_args()

    graus = a.grau or (sorted(br.GRAUS) if a.todos else ["intermediario"])
    variacoes = a.variacao or [0.0]
    celulas = [(g, r, x, v) for g in graus for r in ("12x36", "8h")
               for x in ("teto", "maior_resto") for v in variacoes]
    if a.piloto:
        celulas = [("intermediario", "12x36", "teto", 0.0), ("intermediario", "8h", "teto", 0.0)]
    if a.sensibilidade:
        celulas = [("intermediario", r, "teto", v)
                   for v in (a.variacao or [0.0, 0.5, 1.0]) for r in ("12x36", "8h")]

    print(f"Experimento A: {len(celulas)} celulas, solver {a.solver}, "
          f"limite {a.tempo}s por resolucao")
    print("Horas de assistencia fixas em 5.920 h; muda so o regime. O piso de capacidade e")
    print("36 nos dois regimes por construcao — o que se mede e a distancia ate ele.")

    linhas = []
    for grau, regime, regra, variacao in celulas:
        linhas.append(celula(grau, regime, regra, a.solver, a.tempo, a.margem,
                             not a.quieto, variacao))
        gravar(linhas)

    print(f"\n{'celula':38s}{'var':>5s}{'p.cap':>7s}{'p.alt':>7s}{'intervalo':>12s}"
          f"{'dist':>8s}{'indet.':>8s}{'erros':>7s}{'conf':>6s}")
    for r in linhas:
        conf = str(r["conferencia"])
        print(f"  {r['grau']:15s}{r['regime']:7s}{r['regra']:12s}{r['variacao']:5.1f}"
              f"{r['piso_de_capacidade']:7d}{r['piso_de_alternancia']:7d}"
              f"{r['intervalo']:>12s}{str(r['distancia_do_piso']):>8s}"
              f"{str(r['indeterminados']):>8s}{str(r['erros_do_solver']):>7s}"
              f"{('ok' if conf == 'ok' else 'FALHA'):>6s}")
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
