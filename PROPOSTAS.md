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

---

## 2026-09-18 — P3: habilidade como restrição flexível, não como domínio

**Status: VALIDADA em 2026-09-22.** Habilidade é flexível com coeficiente na variável de
atribuição; a versão rígida fica como divergência declarada, reservada à instância brasileira.
Decisão registrada em `DECISOES.md`, entrada "Habilidade é restrição flexível, não restrição
de domínio", que também registra por que o teste das duas leituras foi cancelado.

### O que se propõe

Adotar a habilidade como **restrição flexível com coeficiente na variável de atribuição**,
que é a formulação de Santos et al. (2016), e tratar a versão rígida — profissional só pode
cobrir turno cuja habilidade ele tem — como **divergência declarada de modelagem, reservada
à instância brasileira**.

### Por quê

- Santos et al. (2016, p. 228) declaram duas rígidas, as mesmas da documentação oficial, e
  listam habilidade alternativa entre as 13 flexíveis (item 10).
- Na p. 231, as flexíveis 10 e 13 são penalizadas diretamente nos coeficientes de `x[n,s,d]`,
  pelo coeficiente ν. Habilidade, na referência, é custo na atribuição.
- Coincide com o que o código do `evaluator.jar` faz (ver `DECISOES.md`, 15/09): `hasSkill`
  só aparece dentro de `AlternativeSkillCondition`, sob a flag; não há checagem rígida.

### Consequência para o teste planejado nas semanas 2-3

O teste das duas leituras contra `long01` = 197 **não distingue as hipóteses**. Em `long01` a
restrição está desligada, logo ν = 0 e a habilidade não custa nada. A leitura rígida restringe
o conjunto viável, então só pode dar ótimo maior ou igual a 197 — e, se a restrição não for
ativa no ótimo, dá exatamente 197 também. Empate não decide nada.

O que muda no plano: a rodada **livre** continua valendo, e é a rodada de validação — se ela
der exatamente 197, o modelo está certo. A rodada rígida deixa de ser necessária para
validar; vira diagnóstico opcional.

### Consequência para o código

`src/modelo.py` hoje tem `habilidade_rigida=True` como padrão, restringindo o domínio das
variáveis. Validada esta proposta, o padrão inverte: variáveis para todo (n, s, d), com
penalidade ν quando a restrição estiver ativa. A flag permanece, para a instância brasileira.

---

## 2026-09-18 — P4: o invariante do Experimento A precisa ser declarado

**Status:** aguardando validação. **É a proposta mais consequente aberta até aqui, e a única
que precisa do orientador antes de qualquer código da semana 4.**

### O problema

O Experimento A compara o efetivo mínimo viável sob turnos de 8 horas e sob 12×36 "para a
mesma cobertura assistencial". A expressão é ambígua, e a escolha decide o **sinal** do
resultado principal do trabalho.

| Invariante | O que acontece com `long01` | Efetivo mínimo sob 12×36 |
|---|---|---|
| **Atribuições** (740 nos dois regimes) | as 740 atribuições passam de 8h para 12h: a assistência entregue sobe de 5.920 h para 8.880 h, mais 50% | ⌈740/14⌉ = **53**, contra 49 |
| **Horas** (5.920 h nos dois regimes) | mesma assistência entregue | ⌈(5920/12)/14⌉ = **36**, contra 49 |

Pelo invariante de atribuições, o 12×36 "exige mais gente" — mas exige porque comprou 50% mais
cuidado. Pelo invariante de horas, o 12×36 **economiza cerca de 27% do efetivo**.

### O que isso derruba

A entrada do `DECISOES.md` de 08/09, "12×36 é inviável no efetivo original: vira Experimento
A", está construída sobre o invariante de atribuições: 740 atribuições contra capacidade de
49 × 14 = 686, dando 108% de utilização. Sob o invariante de horas não há inviabilidade
nenhuma — sobra folga. A motivação registrada do Experimento A depende de uma escolha que
nunca foi declarada.

A estimativa de "90 a 100 profissionais" registrada na mesma entrada não decorre de nenhum
dos dois invariantes. Pela aritmética da própria entrada o piso é 53.

### Agravante: o baseline não é um regime de 8 horas brasileiro

`long01` opera a 54% de utilização — 49 profissionais para 740 atribuições em 28 dias, cerca
de 15 turnos por pessoa, algo como 30 horas semanais. Comparar esse baseline com um 12×36 em
utilização plena mistura mudança de regime com mudança de utilização, e são efeitos separáveis.

### Por que isso é risco de banca

Uma banca de Engenharia de Produção sabe que o 12×36 é adotado em hospital brasileiro em parte
por economizar efetivo. Um resultado afirmando que ele quase dobra o efetivo será lido como
artefato de modelagem — e a leitura estará correta. Isso está no objetivo geral do trabalho,
não numa nota de rodapé.

### Encaminhamentos possíveis, a levar ao orientador

1. **Invariante de horas**, com o efetivo de 8 horas recalculado no mesmo critério de
   utilização do 12×36. A pergunta vira "quanto de efetivo cada regime exige para a mesma
   assistência", e o resultado esperado é economia, não inviabilidade.
2. **Invariante de horas com as restrições legais brasileiras como rígidas** — descanso de 36
   horas, teto mensal, composição mínima por categoria. Aqui o efetivo mínimo deixa de ser
   divisão e passa a depender do modelo, que é o que dá conteúdo ao Experimento A.
3. **Deslocar o peso do trabalho para o Experimento B**: com cada regime no seu efetivo
   mínimo, comparar a distribuição da penalidade entre profissionais. Sobrevive a qualquer
   escolha de invariante, e é afirmação forte pela classificação do próprio `CONTEXTO` §5.

Recomendação: 2 como desenho principal, com 3 como resultado que não depende dele.
