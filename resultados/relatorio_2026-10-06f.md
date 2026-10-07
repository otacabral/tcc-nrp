# Relatório de 06–07/10/2026 (f)

## Para o Otávio

- **Parte A: não achei defeito.** Com a entrada que você descreveu, o caso 15 + 5 **tem escala** e a ferramenta a encontra:
  - o HiGHS acha escala em 0,4 s e prova o ótimo (18) em 1.078 s;
  - pela tela (`ferramenta.verificar`), dá "Escala gerada; pode haver uma melhor".

  **Não consegui reproduzir** o "o solver falhou" nem os ~30 min.
- **O que preciso de você para fechar a parte A:**
  - o texto da janela do PowerShell onde o Streamlit roda, perto do clique; ela imprime "[ERRO] …" quando a tela diz "o solver falhou";
  - uma captura da tela preenchida antes de "Gerar escala".
- **Partes B, C, D e E: feitas.**
  - material de estudo em `docs/aprendizado/`;
  - bateria desenhada (não rodada) em `docs/bateria_entradas.md`;
  - P11, P12 e P13 no PROPOSTAS;
  - cronograma no DECISOES e no ESTADO_ATUAL.
- **Para decidir:** P12 (orçamento de tempo por clique) e P13 (conta dos "ocupados por dia" no piso e no diagnóstico).
- `git pull` traz tudo. Nada mudou em `src/` nem nos testes.

## Status por parte

| Parte | Status | Commits principais |
|---|---|---|
| E. Cronograma | **feita** | `880e158` |
| D. P11, P12, P3 | **feita** | `25bbf1d` |
| A. Diagnóstico | **feita, sem defeito achado; não reproduzido** (aguarda o console e a captura) | `11e2e7a` (esperado), `8c991b8`, `60a5ab4`, `67d22d7`, `d40e413` (A4 = P13) |
| B. Material de estudo | **feita** | `1284fef` (B1), `9817000`/`130fab3` (B2–B4), `acf7b09` (B5) |
| C. Desenho da bateria | **feita** (desenhada, **não rodada**) | `62bbf4d` |

## Parte A — diagnóstico do caso 15 + 5

**Esperado registrado antes** (`docs/diagnostico/ESPERADO_parte_A.md`, commit `11e2e7a`): pela conta dos ocupados por dia, 20 sobram 4 por dia, e 16 é fronteira.

Todos os logs estão em `resultados/diagnostico_2026-10-07/`. Todos os testes rodaram um por processo, nesta máquina: i5-10210U, `appsi_highs` (HiGHS 1.15.1). Os tempos são limite operacional.

### Prova de que o caso tem escala, antes de rodar o solver

`docs/diagnostico/escala_construida.py` monta uma escala à mão:
- **noturno:** dois grupos que se alternam (3 enfermeiros + 2 técnicos cada, N dia sim, dia não);
- **diurno:** 9 enfermeiros + 1 técnico num ciclo de 3 dias de trabalho por 2 de folga.

Resultado:
```
conferir_rigidas (independente do modelo): ok
descanso medido no relogio: cumpre {'menor_geral': 12.0, 'menor_semanal': 36.0, 'max_consec': 3}
modelo com a escala fixada: optimal | tem solucao True
objetivo da etapa 1 nessa escala: 39
```
**O modelo da ferramenta aceita a escala.** O caso não é inviável.

### A3d — valores gerados para o modelo de 6 h + 12 h (sem solver)

```
MaxNumAssignments: 29 ativa True peso 1
MaxConsecutiveWorkingDays: 6 ativa True
tetos de horas: [176.0]
pares proibidos (turno, salto em dias, turno): [('N', 1, 'M'), ('N', 1, 'N'), ('N', 1, 'T'), ('N', 2, 'M'), ('N', 2, 'T')]
limite_efetivo: 6 | piso: 13
```

Tudo como o esperado:
- 29 = 176 ÷ 6, ou seja, vem do turno mais curto;
- teto de 176 h;
- os pares vêm dos horários reais: depois do N (fim às 07:00), nada no dia seguinte; no outro dia, M dá 24 h e T dá 30 h de descanso, menos que 36 h, e o N (36 h) fica permitido;
- não há regra de 11 h entre M e T, porque do T (19:00) ao M (07:00) são 12 h.

**Nada é calculado como se tudo fosse 12 h.**

### A3a — 15 + 5, limite de 3.600 s

```
 J       0       0         0   0.00%   -inf            50                 Large        0      0      0         0     0.4s
         0       0         0   0.00%   14              50                72.00%        0      0      2      1960     0.6s
 L       0       0         0   0.00%   14              22                36.36%     1128    137     75     11347    16.7s
 T    5335      80       969   0.73%   16.33333333     18                 9.26%     9222    273   9329     1509k   826.1s
      6900       0      1720 100.00%   18              18                 0.00%     9858    291   8867     2127k  1077.0s
  Status            Optimal
```
**Acha escala aos 0,4 s e prova o ótimo de 18 aos 1.077 s.** O limite inferior da raiz é 14, o mesmo do log do Otávio.

### Reprodução pelo caminho da tela, 15 + 5 (`ferramenta.verificar`, 600 s e 180 s)

```
[    0.0 s] testando quadro de 20 profissionais
[  601.5 s] veredito: admite | frase: O quadro informado admite escala legal. Escala gerada; pode haver uma melhor (gap 15,8%: distância máxima até a melhor possível).
tentativas: [(20, 'viavel', 15, 5)]
```
Saiu igual ao esperado registrado antes: **a tela gera escala.**

### A3e — 10 + 5 pelo caminho da tela

```
[    0.0 s] testando quadro de 15 profissionais
[    0.0 s] testando quadro de 16 profissionais
[  613.5 s] veredito: nao_decidido | frase: Não foi possível gerar a escala no tempo disponível com mais profissionais; o menor quadro viável não foi determinado.
tentativas: [(15, 'piso', None, None), (16, 'inviavel', 10, 6), (16, 'indeterminado', 11, 5)]
```

- 16 (10 + 6) foi **provado inviável** em ~15 s. Log `inviavel_16_10mais6.log`: 110 nós, Expl. 100%.
- 16 (11 + 5), que é **exatamente a fronteira da conta**, terminou "indeterminado": sem escala em 600 s. É uma resposta legítima.
- **Em nenhum momento saiu "erro"** ("o solver falhou").
- **Duração:** cerca de 15 s + 600 s = 613 s. Os ~30 min do Otávio não se reproduzem.

### A3b — monotonia (acréscimos como enfermeiros, 600 s cada)

| Quadro | Primeira escala | Estado em 600 s |
|---|---|---|
| 22 (17 + 5) | 0,5 s (valor 64) | sem prova, gap 16,7% |
| 24 (19 + 5) | 0,5 s (78) | sem prova, gap 21,1% |
| 26 (21 + 5) | 0,5 s (82) | **ótimo provado** em 415 s |

Todos acham escala, então **nenhuma regra bloqueia independentemente do quadro**.

### A3c — uma regra relaxada por vez (15 + 5, 600 s cada)

| Regra relaxada | Primeira escala | Estado |
|---|---|---|
| sem limite de 6 dias seguidos (no modelo, é também o "descanso semanal": não há restrição própria dele) | 0,5 s (64) | gap 10,5% |
| sem as proibições de descanso entre turnos | 0,5 s (86) | gap 30,0% |
| sem máximo de plantões | 0,4 s (50) | gap 15,8% |
| sem teto de horas | 0,4 s (49) | gap 21,1% |

**Nenhuma remoção é necessária: nada trava.**

### A3f — classificação

**Não é entrada problemática (com a entrada descrita), não é defeito demonstrado e não é dificuldade do solver em achar escala.** Com a entrada descrita, a ferramenta faz o que deve: gera escala, sem prova do ótimo em 600 s, porque a prova leva cerca de 1.078 s. Isso é dificuldade do solver **em provar**, não em achar.

**O resultado do Otávio não se reproduz.** Duas evidências dizem que o modelo resolvido no clique dele não era o desta entrada:
1. O HiGHS roda determinístico ("Using 1 max workers. Parallel search off"). Com este modelo, a heurística `J` acha escala aos 0,4 s em todas as rodadas (7 de 7). O log dele ficou 600 s sem escala, com 70% da árvore explorada.
2. "o solver falhou" é o rótulo de **erro**: exceção do solver, ou "declarou viável mas não entregou solução" (`ferramenta.resolver`, linhas 307–318). Ficar sem escala no tempo dá outro texto: "sem escala no tempo disponível — nem provado inviável". Isso aconteceu aqui no 16 (11 + 5).

**Verifiquei que não é outro Python:** nem o Python global nem o Anaconda da máquina têm Pyomo ou Streamlit. A tela só pode ter rodado com a `.venv` (Pyomo 6.10.1, HiGHS 1.15.1).

**Hipóteses, da mais à menos provável (nenhuma demonstrada):**
- **(a) Entrada efetiva diferente da descrita.** Por exemplo, um número da demanda que não "pegou" (no Streamlit o valor só vale depois de Enter ou de sair do campo), a caixa do fim de semana próprio, ou a grade por data feita antes de mudar a demanda.
- **(b) Servidor do Streamlit iniciado antes de uma atualização do código.** O Streamlit reexecuta o `app.py` a cada clique, mas os módulos importados (`ferramenta`, `modelo`) podem ficar na versão antiga.
- **(c) Interação com a página durante o cálculo,** que reinicia o script.

**Evidência pedida ao Otávio:**
1. o texto da janela do PowerShell com o Streamlit (linhas "[ERRO] …");
2. uma captura da tela preenchida;
3. se mexeu na página durante o cálculo;
4. quando o Streamlit foi aberto, em relação ao último `git pull`.

**Nenhum defeito foi achado, então a parte A não foi parada.**

### A4 — candidata a melhoria (não implementada)

`PROPOSTAS.md`, **P13** nova: a conta dos "ocupados por dia" (turnos que bloqueiam o dia seguinte) no piso e no diagnóstico. Teria mostrado 16 como fronteira. Já está escrita, de forma independente, em `docs/diagnostico/bateria_desenho.py`.

## Parte B — material de estudo

Tudo em `docs/aprendizado/`:
- **`LEIA_ME.md`:**
  - B1: sem warm start; HiGHS com parâmetros padrão, exceto o tempo; gap de 0,01%; `v1.0.1` = `35a9cd1`;
  - B2: a instância de brinquedo;
  - B3: o `.lp` linha a linha;
  - B4: o log do HiGHS — pré-processamento, limite, árvore, gap, prova de ótimo e de inviabilidade, e as colunas do log da parte A;
- **`PASSEIO_DE_UM_CLIQUE.md`** (B5): o caminho do clique até a planilha, incluindo a busca do menor quadro e o tempo máximo teórico (cerca de 4 h 30 min, calculado sobre os limites);
- **`brinquedo.py`, `brinquedo.lp`, `brinquedo_highs.log`, `brinquedo_inviavel_highs.log`.**

**Achado na B2:** com um horizonte de 3 dias, o teto de horas proporcional (44 × 3 ÷ 7 = 18,9 h) permite um plantão de 12 h só. A primeira versão do brinquedo era inviável por isso. A tela usa sempre 28 dias.

## Parte C — bateria (desenhada, não rodada)

`docs/bateria_entradas.md` (e o gerador `docs/diagnostico/bateria_desenho.py`, só conta):
- 14 áreas editáveis;
- **18 casos cobrindo os 91 pares de áreas**, cada um com esperado pela conta: 16 "gera escala (esperado)" e 2 "inviável pela conta";
- 6 casos de resposta conhecida, incluindo o da parte A (20) e as variantes com 16 (fronteira), 17 e 18;
- lote aleatório de cerca de 200 casos;
- 6 propriedades automáticas e 5 camadas de classificação.

Só roda por decisão sua.

## Partes D e E

- **E:** congelamento dos números em 16/10; semana de testes de 08 a 12/10; texto de 13 a 25/10; tela de 26 a 29/10. Registrado no `DECISOES.md` e no `ESTADO_ATUAL.md`.
- **D:** P11 (parada por estagnação, trabalho futuro, na P3), P12 (orçamento por clique, aguardando decisão) e o replanejamento no meio do período na P3.

---

## LEVAR PARA O PROJETO DE REDACAO

- **`DECISOES.md`**: entrada nova "2026-10-06 — Cronograma: semana de testes e congelamento dos números em 16/10" (E1–E3).
- **`ESTADO_ATUAL.md`**: seção 2 com as datas novas (testes de 08 a 12/10, congelamento em 16/10, texto, tela).
- **`PROPOSTAS.md`**:
  - P11 (trabalho futuro);
  - P12 (aguardando decisão);
  - **P13 nova** (ocupados por dia no piso e no diagnóstico; candidata, não implementar);
  - P3 com o replanejamento no meio do período e a parada por estagnação.
- **Para decidir:** P12 e P13; e o envio do console e da captura do caso 15 + 5 para fechar a parte A.
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
