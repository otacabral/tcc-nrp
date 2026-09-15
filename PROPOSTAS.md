# Propostas a validar

Registro de sugestoes que afetam formulacao, desenho experimental ou escopo.
Nao implementadas ate validacao.

---

## 2026-09-15 — P1: ampliar o conjunto de validação para além do lote early

**Status: VALIDADA em 2026-09-15.** Acrescentar `medium_late05` = 107 ao conjunto de
validação. Decisão registrada em `DECISOES.md`, entrada "Quinto alvo de validação:
`medium_late05`". Refletida no `CONTEXTO_PROJETO.md`, seção 11, e no `PLANO.md`.

### Problema

Os alvos de validação hoje registrados no `CONTEXTO_PROJETO.md`, seção 11, são
`sprint01` = 56, `sprint02` = 58, `long01` = 197 e `long02` = 219. Os quatro pertencem ao
lote *early*. A varredura de 2026-09-15 mostrou que esse lote exercita apenas parte das
restrições flexíveis:

| Restrição flexível | Ativa nos quatro alvos? | Ativa em quantas das 69 |
|---|---|---|
| Máx./mín. de atribuições | sim | 69 |
| Máx./mín. de dias consecutivos de trabalho | sim | 69 |
| Máx./mín. de dias consecutivos de folga | sim | 69 |
| Fins de semana completos | sim | 69 |
| Turnos idênticos no fim de semana | sim | 69 |
| Padrões indesejados | sim | 57 |
| Pedidos de folga (dia e turno) | sim | 49 |
| **Máx. de fins de semana consecutivos** | **não** | 49 |
| **Mín. de fins de semana consecutivos** | **não** | 41 |
| **Sem turno noturno antes de fim de semana livre** | **não** | 44 |
| **Habilidade alternativa** | **não** | 18 |
| Máx. de fins de semana em quatro semanas | não | 0 |

Além disso, no lote *early* todos os pesos valem 1, e a definição de fim de semana é sempre
`SaturdaySunday`. Um erro de multiplicação por peso, ou no tratamento de
`FridaySaturdaySunday`, passaria nos quatro alvos sem ser detectado.

### Amparo na documentação oficial

A descrição da competição (Haspeslagh et al., 2010) trata os lotes *early*, *late* e
*hidden* como **momentos de divulgação**, não como classes de dificuldade ou de cobertura
(Regra 7). A seção 2.2 afirma que instâncias diferentes podem atribuir pesos diferentes às
restrições flexíveis. A própria competição rankeou finalistas sobre *early* + *late* e a
final sobre todas, incluindo as *hidden*. Validar sobre um lote só não tem respaldo no
desenho da competição.

### Proposta

Acrescentar um quinto alvo de validação: **`medium_late05`**, valor ótimo 107 na Tabela 6 de
Santos et al. (2016), com LB = UB e gap 0. Cobre todas as restrições que aparecem ativas em
alguma instância, exceto a de máximo de fins de semana em quatro semanas, que não está ativa
em nenhuma. Tem duas habilidades, pesos diferenciados e pedidos de folga.

Alternativa: `long_late02`, valor ótimo 229, que acrescenta a definição de fim de semana
`FridaySaturdaySunday` e um quarto contrato, mas não tem pedidos de folga.

### Custo

Menor do que parece. Conferir a função objetivo no avaliador oficial **não exige provar o
ótimo**: basta que o valor calculado pelo modelo coincida com o do avaliador em qualquer
escala viável. Só a comparação com o valor da Tabela 6 exige otimalidade, e é um segundo
teste, separável. É validação, não experimento, portanto não disputa o prazo de
congelamento de 14/10.

### Se recusada

Registrar no capítulo de metodologia que a validação cobre 8 das 13 restrições flexíveis, e
que as regras de fim de semana usadas na instância brasileira não têm conferência externa.

---

## 2026-09-15 — P2: escopo das restrições a implementar

**Status: VALIDADA em 2026-09-15, alternativa A′.** Implementar as 13 flexíveis mais as
metades "on" dos pedidos, com ressalva de que três itens não têm conferência externa
possível. Decisão registrada em `DECISOES.md`, entrada "Escopo: implementar as 13 flexíveis,
inclusive as não exercitadas". Refletida no `CONTEXTO_PROJETO.md`, seção 6, e no `PLANO.md`.

### Problema

Duas das 13 restrições flexíveis de Santos et al. (2016) não são exercitadas por nenhuma
instância do INRC-2010:

- **Máximo de fins de semana trabalhados em quatro semanas** (restrição 4): presente nos 235
  contratos das 69 instâncias, porém com `on="0"` em todos.
- **Folgas após uma sequência de turnos noturnos** (restrição 6): o elemento
  `TwoFreeDaysAfterNightShifts` não aparece em nenhum arquivo.

Some-se a isso que os pedidos só aparecem na forma negativa: nenhuma instância traz
`DayOnRequests` ou `ShiftOnRequests`.

Implementar essas restrições é escrever código que nenhum avaliador vai conferir — não há
instância que produza penalidade delas.

### Amparo na documentação oficial

As três constam da definição oficial do problema:

- A seção 2.1 lista, entre os campos do contrato, "maximum number of working weekends in
  four weeks" e "the number of days off after a series of night shifts".
- A seção 2.2.3 dá a semântica formal de "Two free days after a night shift" (Tabela 7):
  o turno noturno recebe um número, os turnos dos dias seguintes recebem números
  consecutivos, `max consecutive = 1`. O número de folgas é fixo em duas — o elemento do XML
  é booleano, sem parâmetro. Ou seja, a semântica está definida mesmo sem instância.
- A seção 2.1 lista pedidos para trabalhar e pedidos para não trabalhar em pé de igualdade;
  a seção 2.2.3 dá a numeração de ambos (`min pert = 1` para os pedidos "on").

Santos et al. (2016) implementam as 13 — as restrições 11 e 12 da formulação deles são
exatamente as duas em questão.

### Proposta

Três alternativas, em ordem de escopo:

- **A′** — implementar as 13, como Santos et al., e mais as metades "on" dos pedidos.
  Registrar no texto que três itens não têm conferência externa possível com esses dados.
- **B′** — implementar 12: as 11 exercitadas mais o máximo de fins de semana em quatro
  semanas, que é barata de escrever e é a que interessa ao regime 12×36. Deixar de fora as
  folgas após noites e as metades "on" dos pedidos.
- **C′** — implementar as 11 exercitadas e justificar a delimitação pelo dado.

Recomendação: **A′**. A semântica das três está fixada na documentação oficial, o custo de
codificação é baixo, e o trabalho se posiciona em relação a uma formulação que as
implementa. "Não implementei porque nenhuma instância usava" é uma delimitação que a banca
pode questionar; "implementei e não pude validar externamente" é uma ressalva de método.

### Consequência para a instância brasileira

Se a instância brasileira precisar limitar fins de semana trabalhados, há duas restrições
candidatas: a de fins de semana consecutivos, exercitada por 49 instâncias e portanto
validável, e a de fins de semana em quatro semanas, não exercitada por nenhuma. Havendo
escolha, usar a primeira.
