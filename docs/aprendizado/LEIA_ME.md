# Material de estudo do código — para quem não programa

Conteúdo da pasta `docs/aprendizado/`:

- **este arquivo:**
  - B1, o que o código faz e o que não faz com o solver;
  - B3, o modelo da instância de brinquedo, linha a linha;
  - B4, como ler o log do HiGHS;
- `PASSEIO_DE_UM_CLIQUE.md` (B5): o caminho de um clique em "Gerar escala" até a planilha;
- `brinquedo.py` (B2): monta a instância de brinquedo pelo mesmo caminho da tela, grava o modelo em `.lp` e roda o HiGHS com log;
- `brinquedo.lp`, `brinquedo_highs.log`, `brinquedo_inviavel_highs.log`: o que o script gerou.

---

## B1. O que o código faz (e não faz) com o solver

Conferido na `v1.0.1`.

**(a) Não existe warm start nem heurística de partida.** A primeira escala vem do próprio HiGHS. `src/modelo.py`, função `resolver` (linhas 464–520), só faz três coisas:
- cria o solver: `pyo.SolverFactory(solver)`, com `appsi_highs` por padrão (`SOLVER_PADRAO`, linha 30);
- passa o limite de tempo;
- passa o arquivo de log.

Nenhum valor inicial é dado às variáveis. Nenhum script do repositório usa "warm start": a palavra só aparece em comentários de `src/escalabilidade.py`, que discutem se valeria a pena tê-lo. No log do HiGHS, a letra no começo da linha mostra qual heurística dele achou a escala; por exemplo, `J` (*feasibility jump*), `L` (busca local num sub-problema), `T` (nó da árvore). Veja a B4.

**(b) O HiGHS roda com os parâmetros padrão, exceto dois:**
- o **tempo-limite** (`opt.config.time_limit` e o argumento `timelimit` da chamada, linhas 478–508);
- o **arquivo de log** (`opt.options["log_file"]`, linha 498).

Não há ajuste de threads, semente, estratégia de busca ou tolerância.

**(c) Tolerância de gap: a padrão do HiGHS**, gap relativo de **0,01%** (`mip_rel_gap` = 1e-4). O próprio log a imprime, por exemplo em `resultados/diagnostico_2026-10-07/A3a_15mais5_3600s.log`, linha 213: `Gap 0% (tolerance: 0.01%)`. "Ótimo provado", na ferramenta, quer dizer gap ≤ 0,01%.

**(d) A tag `v1.0.1` existe** e aponta para o commit `35a9cd178311f8c67678bd7b0322f7136e6bf630` (`35a9cd1`). A `v1.0` aponta para `c64dcf9`.

---

## B2. A instância de brinquedo

`python docs\aprendizado\brinquedo.py`. Monta pelo mesmo caminho da tela (`ferramenta.Entrada`, a chamada de `ferramenta.montar`, `ferramenta.pesos`, `experimento_a.modelo_br`), com uma única diferença: **3 dias** em vez de 28.

- **Turnos:** 12×36, D 7–19 e N 19–7.
- **Equipe:** 2 enfermeiros (Enf 1, Enf 2) e 1 técnico (Téc 1).
- **Pedido de folga:** Enf 2 na segunda.

**Achado ao montar.** Com 3 dias, o teto de horas de cada um é 44 × 3 ÷ 7 = **18,9 h**, ou seja, um plantão de 12 h por pessoa. A primeira versão do brinquedo pedia 5 plantões e deu inviável por isso. A versão final pede **3 postos**: D na segunda (enfermeiro), N na terça (técnico) e D na quarta (enfermeiro).

**Resultado:** ótimo, com objetivo **0**.

| Dia | Quem | Turno |
|---|---|---|
| seg 04/01 | Enf 1 | DE |
| ter 05/01 | Téc 1 | N |
| qua 06/01 | Enf 2 | DE |

O pedido de folga de Enf 2 na segunda foi atendido.

A **variante inviável** pede também um enfermeiro no D de terça: 4 postos para 3 pessoas que só podem fazer um plantão cada.

## B3. O modelo do brinquedo, linha a linha (`brinquedo.lp`)

O `.lp` é o modelo escrito como texto: cada restrição é uma soma de variáveis com um limite. Os nomes trazem os índices:
- `_0_`, `_1_`, `_2_` são as pessoas: 0 = Enf 1, 1 = Enf 2, 2 = Téc 1;
- `2027_01_04` é a data;
- `D` e `N` são os **postos de técnico**; `DE` e `NE` são os **postos de enfermeiro**. O "E" no fim quer dizer "exige enfermeiro".

**As variáveis:**
- **`x(pessoa, turno, dia)`** vale 1 se a pessoa faz aquele turno naquele dia, e 0 se não faz. É a decisão da escala.
  - Só existe onde a habilidade permite: o técnico não tem `x(_2_, DE, …)` nem `x(_2_, NE, …)`, porque não cobre posto de enfermeiro (`modelo.construir`, `habilidade_rigida=True`).
  - O enfermeiro tem as quatro.
- **`y(pessoa, dia)`** vale 1 se a pessoa trabalha naquele dia, em qualquer turno. Serve para contar dias e plantões.

**Os grupos de restrições:**

| Linhas do `.lp` | Nome | O que diz | Quem gera |
|---|---|---|---|
| 3–17 | `objetivo` | o custo a minimizar. **+1** para cada `x` de enfermeiro em posto de técnico (D ou N; pessoas 0 e 1). **+2** para `y(_1_, 04/01)`, que é Enf 2 trabalhando na segunda, o dia em que pediu folga. O 2 é o peso W de cada pedido: o número de postos de técnico do período (1) mais 1, para que negar um pedido custe mais que todo enfermeiro em posto de técnico possível | `ferramenta.pesos` e `modelo.construir` |
| 21–86 | `cobertura` | para cada dia e turno, a soma dos `x` é **igual** à demanda: `= 1` onde há posto, `= 0` onde não há (por exemplo, D de técnico na segunda) | `modelo.construir` |
| 87–143 | `um_turno_por_dia` | cada pessoa faz no máximo um turno por dia: a soma dos `x` da pessoa no dia é ≤ 1 | `modelo.construir` |
| 144–209 | `definicao_y` | liga `y` aos `x`: `y` = soma dos `x` da pessoa no dia | `modelo.construir` (`_liga_y`) |
| 210–248 | `carga_horaria` | **teto de horas**: 12 × (plantões da pessoa) ≤ 18,857 h, a carga contratual nos dias disponíveis. Uma por pessoa | `modelo.construir`, item (IV); `Instancia.horas_devidas` |
| 249–253, 439 e 629–633 | `rigidas_legais`, a primeira de cada pessoa | **máximo de plantões** (`MaxNumAssignments`): a soma dos `y` da pessoa é ≤ 1 | `modelo._adicionar_flexiveis`, família `max_num_assignments`, rígida pela CLT |
| 255–414 e seguintes | `rigidas_legais` com dois `x` | **descanso de 36 h depois de turno de 12 h**: um turno num dia e outro no dia seguinte não podem estar os dois. Exemplos: `x(D, seg) + x(D, ter) ≤ 1` e `x(D, seg) + x(N, ter) ≤ 1` | pares proibidos medidos dos horários (`instancia_br.pares_proibidos_por_horario`), que viram padrões `clt_*` e entram rígidos (família `unwanted_patterns`) |
| 415–438 e seguintes | `rigidas_legais` com dois `x` e um `−y` | **padrão de dois dias** (N, folga, D): `x(N, seg) + x(D, qua) − y(ter) ≤ 1`. N na segunda, folga na terça e D na quarta é proibido: do fim do N (07:00 de terça) ao D de quarta (07:00) são 24 h, menos que as 36 h exigidas. O `−y(ter)` faz a regra só valer quando a terça é folga; se a pessoa trabalha na terça, a regra de um dia já proíbe | padrões `clt_36h_*` |
| 681–720 | `bounds` | cada variável fica entre 0 e 1 | Pyomo |
| 721–760 | `binary` | cada variável só pode ser 0 ou 1 | Pyomo |

**O que não aparece no brinquedo:**
- **o descanso de 11 h**, que só existe com turnos de menos de 12 h (o M e o T do modelo de 8 h ou do de 6 h). Entra do mesmo jeito, como par proibido "turno num dia, outro no dia seguinte", medido dos horários. `instancia_br.pares_proibidos_por_horario` exige 36 h depois de turno de 12 h ou mais e 11 h nos demais;
- **o limite de 6 dias seguidos**, que com 3 dias nunca aperta e por isso não é escrito.

## B4. Como ler o log do HiGHS

### O brinquedo viável (`brinquedo_highs.log`)

`MIP has 117 rows; 39 cols; 309 nonzeros; 39 integer variables (39 binary)`
O problema tem 117 restrições ("rows", linhas) e 39 variáveis ("cols", colunas), todas 0 ou 1.

`Coefficient ranges: Matrix [1e+00, 1e+01] ... Cost [1e+00, 2e+00] ... RHS [1e+00, 2e+01]`
A faixa dos números do modelo:
- coeficientes de 1 a 12 (o 12 é o turno de 12 h no teto de horas);
- custos de 1 a 2 (enfermeiro em posto de técnico; pedido);
- limites até 18,9.

`Presolving model` … `0 rows, 0 cols, 0 nonzeros` … `Presolve: Optimal`
É o **pré-processamento**: antes de buscar, o HiGHS tira o que é óbvio. Variável que só pode ser 0 sai; restrição que já está satisfeita sai. Aqui ele reduziu tudo a zero: o problema se resolveu só com deduções, sem busca.

`Status Optimal | Primal bound 0 | Dual bound 0 | Gap 0% (tolerance: 0.01%)`
- **Primal bound**: o custo da melhor escala achada (0).
- **Dual bound**: o limite inferior, isto é, nenhuma escala custa menos que isso (0).
- **Gap**: a distância entre os dois. Com 0%, está **provado** que não há escala melhor.

### O brinquedo inviável (`brinquedo_inviavel_highs.log`)

`Presolving model` … `Presolve: Infeasible` … `Status Infeasible | Primal bound inf`

O pré-processamento **prova** que não existe escala. Deduzindo de restrição em restrição, ele chega a uma contradição: 4 postos, 3 pessoas, um plantão cada. "Primal bound inf" quer dizer que nenhuma escala existe.

### Uma prova de inviabilidade com árvore de busca

`resultados/diagnostico_2026-10-07/inviavel_16_10mais6.log`: o caso da parte A com 16 = 10 + 6, provado inviável em 15 s.

```
        Nodes      |    B&B Tree     |            Objective Bounds              |  Dynamic Constraints |       Work
Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time
         0       0         0   0.00%   0               inf                  inf        0      0      0         0     0.6s
       110       0        53 100.00%   inf             inf                  inf     5150    185   1634     29374    15.0s
Status Infeasible
```

Aqui o pré-processamento não bastou, e o HiGHS **dividiu o problema em casos**: é a árvore, "B&B" (*branch and bound*), do tipo "se Fulano faz N na segunda… / se não faz…".
- Ele visitou 110 casos e todos deram impossível: "Expl." chegou a 100%.
- O limite inferior virou "inf": nenhum ramo tem escala.

**É assim que a ferramenta prova "inviável, provado pelo solver"**, e daí tira o "faltam N".

### As colunas da árvore

Exemplo: `A3a_15mais5_3600s.log`, o caso do Otávio.

```
 J       0       0         0   0.00%   -inf            50                 Large        0      0      0         0     0.4s
         0       0         0   0.00%   14              50                72.00%        0      0      2      1960     0.6s
 L       0       0         0   0.00%   14              22                36.36%     1128    137     75     11347    16.7s
 T    5335      80       969   0.73%   16.33333333     18                 9.26%     9222    273   9329     1509k   826.1s
      6900       0      1720 100.00%   18              18                 0.00%     9858    291   8867     2127k  1077.0s
```

| Coluna | O que é |
|---|---|
| **Src** | quem achou a escala nova dessa linha. `J` = *feasibility jump*, heurística rápida (aqui, aos 0,4 s). `L` = sub-MIP, que resolve um pedaço do problema. `T` = um nó da árvore. Em branco = linha de acompanhamento, sem escala nova. A legenda completa está no começo de todo log |
| **Proc.** | quantos nós (casos) da árvore já foram processados |
| **InQueue** | quantos casos ainda esperam na fila |
| **Leaves** | quantos casos já foram fechados de vez (folhas): resolvidos ou descartados |
| **Expl.** | a fração da árvore já explorada. 100% = busca completa, como aos 1.077 s |
| **BestBound** | o **limite inferior**: nenhuma escala custa menos que isto. Começa em 14, que é a "relaxação linear" (o problema com as variáveis podendo valer frações), e sobe conforme a busca descarta casos |
| **BestSol** | o custo da **melhor escala achada** até ali: 50, depois 22, 21, … e 18 |
| **Gap** | (BestSol − BestBound) ÷ BestSol. Aparece "Large" enquanto o limite ainda é −inf. Em 0% (com tolerância de 0,01%), o ótimo está provado |
| **Cuts** | desigualdades extras que o HiGHS deduz e acrescenta para apertar o limite inferior ("cortes") |
| **InLp** | quantos desses cortes estão em uso agora |
| **Confl.** | "conflitos": combinações que ele aprendeu serem impossíveis, para não repetir |
| **LpIters** | o total de passos do método que resolve os problemas lineares, uma medida de trabalho. "2127k" = 2,1 milhões |
| **Time** | segundos desde o início |

**O log que o Otávio viu** ("Time limit reached", Primal bound inf, Dual bound 14, 2.083 nós, Expl. 70,11%, 600 s) se lê assim:
- em 600 s, nenhuma escala foi achada (BestSol = inf);
- o limite inferior ficou em 14;
- a busca tinha explorado 70% da árvore quando o tempo acabou.

Nas rodadas de 07/10, com a entrada descrita, a heurística `J` achou escala aos 0,4 s em todas as vezes. E o HiGHS roda de forma determinística ("Using 1 max workers. Parallel search off"). Por isso a conclusão da parte A: o modelo resolvido no clique do Otávio não era o desta entrada. Ver `resultados/relatorio_2026-10-06f.md`.
