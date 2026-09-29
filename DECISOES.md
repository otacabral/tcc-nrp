# Diário de decisões — TCC NRP

> **Arquivo ativo, reclassificado em 29/09/2026.** Cada entrada traz uma marca de status.
> Entradas superadas permanecem como registro; não apagar.

Registro datado de decisões de modelagem e implementação. Matéria-prima dos capítulos de
formulação e de experimentos.

**Regra:** toda decisão não óbvia entra aqui no momento em que é tomada, com data, o que
foi decidido e por quê. Três linhas bastam. Perguntas abertas ficam na seção final até
serem resolvidas — e então viram entrada datada.

---

## 2026-09-08 — Formulação: atribuição, não janelas

**Status: vigente**

Adotada codificação por atribuição (`x[n,s,d]`) com restrições explícitas de janela
deslizante para dias consecutivos.

Não adotadas as variáveis `w[n,d1,d2]` / `r[n,d1,d2]` nem as tabelas σ/τ de Santos et al.
(2016). Aquelas construções servem ao objetivo do artigo original — fortalecer o limite
dual por planos de corte. Este trabalho não persegue desempenho algorítmico, e a
codificação por atribuição permite adaptação direta ao 12×36 e à desagregação por
categoria profissional.

Semântica das restrições (2 rígidas, 13 flexíveis) tomada integralmente de Santos et al.

---

## 2026-09-08 — Cobertura é restrição rígida de igualdade

**Status: vigente**

O elemento `<Preferred>` do XML **não** é preferência: é a demanda obrigatória.

Fonte: Haspeslagh, De Causmaecker, Stølevik e Schaerf, *First International Nurse
Rostering Competition 2010*, anais do PATAT 2010, p. 499–500. O texto declara a demanda
como restrição rígida e lista apenas duas restrições rígidas — cobrir toda a demanda e no
máximo um turno por enfermeira por dia.

Santos et al. (2016) modelam como igualdade (restrição 1). Consistente.

---

## 2026-09-08 — Atributo `on=` deve ser respeitado pelo parser

**Status: vigente**

Cada restrição flexível traz `on="0"` ou `on="1"` indicando se está ativa na instância.
Restrição com `on="0"` não deve entrar no modelo.

Verificado em `sprint01`: os quatro contratos desligam `MaxConsecutiveWorkingWeekends`,
`MinConsecutiveWorkingWeekends` e `MaxWorkingWeekendsInFourWeeks`.

Ignorar isso faz o valor objetivo divergir do avaliador oficial — e o sintoma parece bug
de modelo, não de leitura.

Nota adicional: o formato já prever ativação por restrição é argumento a favor do
experimento de variantes — ligar e desligar regra é mecanismo nativo do benchmark.

Ampliado em 2026-09-15: o `on=` sozinho não cobre todos os casos presentes nos arquivos.
Ver a entrada "Regra geral de ativação de restrição flexível".

---

## 2026-09-08 — Cobertura vem por dia da semana

**Status: vigente**

`CoverRequirements` traz `DayOfWeekCover` (7 blocos, um por dia da semana), não por data.
O parser expande para os dias do horizonte.

Nas instâncias inspecionadas existe apenas `<Preferred>`; não há `<Minimum>` nem
`<Maximum>`.

Confirmado em 2026-09-15 pela varredura das 69 instâncias: todas usam apenas
`DayOfWeekCover`, e dentro de `<Cover>` aparecem apenas `<Shift>` e `<Preferred>`. Nenhuma
usa `DateSpecificCover`. Fonte: `docs/inventario_instancias.csv`, colunas
`blocos_cobertura` e `tags_em_cover`.

Regra de precedência, para o gerador da instância brasileira: a documentação oficial
(seção 3.1) determina que a cobertura por data específica **tem preferência** sobre a
cobertura por dia da semana. Nenhuma instância do INRC exercita isso, mas o parser já
implementa a precedência, e é o mecanismo disponível caso a instância brasileira precise de
demanda diferenciada em datas específicas — feriados, por exemplo. O `src/inspecionar.py`
já expande a cobertura com essa precedência; o parser da Sessão 2 deve fazer o mesmo.

---

## 2026-09-08 — Desagregação por categoria: via tipo de turno

**Status: vigente**

O elemento `<Cover>` aceita apenas `<Shift>` e `<Preferred>` — não aceita `<Skill>`.
A habilidade está pregada no **tipo de turno**.

Em `long01`: o turno `DH` tem horário idêntico ao `D` (08:30–16:30) mas exige `HeadNurse`,
e a cobertura pede 2 de `DH` nos dias úteis. Isso expressa composição de equipe.

Consequência para a instância brasileira: a desagregação enfermeiro/técnico se faz criando
um tipo de turno por par horário×categoria, dentro do esquema oficial. **Não** exige
extensão do formato — o avaliador continua aplicável.

Ressalva a registrar no texto: a cobertura resulta em contagem fixa por categoria, não em
"ao menos 1 das N de um pool comum".

Nota: apenas 6 dos 49 profissionais de `long01` têm a habilidade `HeadNurse`.

Acrescentado em 2026-09-15: nenhum profissional, em nenhuma das 69 instâncias, tem
`HeadNurse` sem ter também `Nurse`. A habilidade é acumulativa, não excludente — os 6
chefes de `long01` podem cobrir qualquer turno, e só eles podem cobrir `DH`. A instância
brasileira precisa decidir se reproduz essa hierarquia (enfermeiro cobre posto de técnico)
ou trata as categorias como disjuntas. Fonte: `docs/inventario_instancias.csv`, coluna
`combinacoes_habilidade`.

---

## 2026-09-08 — 12×36 modelado como MaxConsecutiveWorkingDays = 1

**Status: vigente; complementada por 2026-09-21** (padrão noturno–folga–diurno, `clt_36h_N_D`).

Alternância estrita (12h trabalho, 36h descanso) implica não trabalhar dois dias
consecutivos, o que dá 14 plantões em 28 dias.

Confere com a realidade legal: o art. 59-A da CLT permite o regime; a lei não fixa carga
semanal, e a jurisprudência entende alternância entre semanas de 36h e 48h, média de ~42h
semanais e ~15 plantões por mês.

> *Nota de 29/09/2026:* a "média de ~42h" atribuída à jurisprudência é afirmação sem fonte;
> não citar. As 42 h são aritmética (VIRADA, seção 2.3).

Logo **não** é necessário um `MaxNumAssignments` reduzido em separado — a alternância já é
a restrição correta.

Ressalva a registrar no texto: é aproximação em granularidade de dia, não representação
exata das 36 horas de descanso. O avaliador valida o código, não a fidelidade desta
representação.

Verificar antes de citar: PEC 221/19 e projeto do governo discutem limitar a média a 40h
semanais. Citar com data de consulta.

---

## 2026-09-08 — 12×36 é inviável no efetivo original: vira Experimento A

**Status: superada por 2026-09-18 — Invariante do Experimento A: horas de assistência** (declarado naquela entrada; o restante é desenho da comparação de regimes)

Aritmética sobre `long01`:

| | |
|---|---|
| Demanda total no horizonte (28 dias) | 740 atribuições |
| Profissionais | 49 |
| Capacidade sem limite de dias consecutivos | 49 × 28 = 1.372 → 54% de utilização |
| Capacidade com máx. 1 dia consecutivo | 49 × 14 = 686 → **108% de utilização** |

Passa de 100%: a instância seria **inviável nas restrições rígidas**, sem solução alguma.

Consequência para o desenho: o comparativo não pode manter o efetivo constante. O efetivo
passa a ser **resultado**, não parâmetro fixo.

**Experimento A** — qual o efetivo mínimo viável sob cada regime, para a mesma cobertura?
Estimativa preliminar: ~90 a 100 profissionais sob 12×36, contra 49. É medida de
viabilidade, portanto independente do algoritmo de resolução.

**Experimento B** — com o efetivo dimensionado em cada regime, comparar penalidade total e
sua distribuição entre profissionais.

Dado prático útil ao dimensionamento: no 12×36, 4 profissionais cobrem um posto 24/7.

---

## 2026-09-08 — Convenção do turno noturno

**Status: vigente**

O turno `N` do INRC já atravessa a meia-noite (22:30 → 06:30) e a documentação oficial o
trata como pertencente a um dia; as restrições de dias consecutivos operam em dias.

Adotar a mesma convenção para o plantão noturno de 12h da instância brasileira, e citar a
fonte. Não inventar convenção própria.

---

## 2026-09-08 — Limites do que as medições sustentam

**Status: vigente**

Custo computacional é propriedade da tripla (formulação, algoritmo, instância), não da
instância. Um branch-and-price sobre formulação por padrões pode inverter o ranking.

Afirmações **fortes** (propriedade da instância, independentes do algoritmo):
viabilidade / inviabilidade; valor ótimo comprovado; distribuição da penalidade no ótimo.

Afirmações **médias** (propriedade da formulação): número de variáveis e restrições; valor
do relaxamento linear na raiz; gap de integralidade inicial.

Afirmações **fracas** (dependem do algoritmo): tempo até o ótimo, nós explorados, gap ao
fim de um limite de tempo. Reportar como observação com escopo declarado.

Decorrências operacionais: manter instâncias pequenas o suficiente para provar
otimalidade; usar pesos idênticos entre configurações comparadas; preferir medidas
normalizadas a totais absolutos.

---

## 2026-09-15 — Regra geral de ativação de restrição flexível

**Status: vigente**

Uma restrição flexível entra no modelo se, e somente se, estiver **ligada** e tiver **peso
maior que zero**. "Ligada" significa `on="1"` nas restrições que têm esse atributo
(`MaxNumAssignments`, `MaxConsecutiveWorkingDays` etc.) e conteúdo `true` nas que só têm
peso (`CompleteWeekends`, `NoNightShiftBeforeFreeWeekend`, `AlternativeSkillCategory`,
`IdenticalShiftTypesDuringWeekend`, `SingleAssignmentPerDay`).

Por quê: a varredura de 2026-09-15 mostrou que os dois marcadores se contradizem nos
arquivos, e a decisão anterior — que trata só do `on=` — não cobre todos os casos.
Contagem sobre os 235 contratos das 69 instâncias:

| Situação | Contratos | Efeito da regra adotada |
|---|---|---|
| `on="1"` com peso 0 | 16 | fora do modelo (não penalizaria nada de todo jeito) |
| `on="0"` com peso > 0 | 79 | fora do modelo — o `on=` prevalece sobre o peso |
| conteúdo `false` com peso > 0 | 40 | fora do modelo — o booleano é o interruptor |

Os dois primeiros casos não alteram o valor objetivo: peso 0 não soma. O caso que altera é
o terceiro, e é nele que a regra assume risco.

**Amparo na documentação oficial** (Haspeslagh et al., *First International Nurse Rostering
Competition 2010*, 5 maio 2010), verificado em 2026-09-15:

- O **formato texto**, seção 3.1.2, descreve as restrições sem atributo `on` como
  `CompleteWeekends (on|weight) (<boolean>|<int>)`, e idem para
  `IdenticalShiftTypesDuringWeekend`, `NoNightShiftBeforeFreeWeekend`,
  `TwoFreeDaysAfterNightShifts`, `AlternativeSkillCategory` e `SingleAssignmentPerDay`. Ou
  seja: **o booleano do XML é o campo `on`**. O exemplo do apêndice D confirma a ordem —
  `SingleAssignmentPerDay` aparece como `(1|1)`, ligada com peso 1. Conteúdo `false` é
  restrição desligada, não "ligada com valor falso".
- O **apêndice A** traz o pseudocódigo do avaliador: toda penalidade é `custo × distância`,
  onde o custo é o peso do XML. Com peso 0 a parcela é nula por construção. Logo, a metade
  "peso > 0" da regra não é hipótese adicional — é consequência aritmética do avaliador.

O documento **não** define em prosa o atributo `on=` das demais restrições; ele aparece no
esquema e no formato texto como campo, sem explicação. A leitura adotada é a única
compatível com o formato texto.

**Confirmada no avaliador oficial em 2026-09-15.** Três evidências independentes:

1. *Teste com conteúdo `false` e peso alto.* Em `sprint_hidden06`,
   `NoNightShiftBeforeFreeWeekend` tem conteúdo `false` e peso 10. Gerou-se uma escala viável
   com duas ocorrências de turno noturno na véspera de fim de semana livre — a situação que
   essa restrição penaliza. Na saída detalhada do avaliador, com 12 tipos de violação
   listados, essa restrição não aparece nenhuma vez.
2. *Teste com `on="0"` e peso alto.* Na mesma instância,
   `MinConsecutiveWorkingWeekends` está ligada nos contratos 0 e 1 e desligada no contrato 2,
   com peso 3 nos três. As violações reportadas pelo avaliador, cruzadas por profissional:
   4 nos profissionais do contrato 0, 2 nos do contrato 1, **zero** nos do contrato 2. O peso
   é idêntico; o que muda é o `on=`.
3. *Código-fonte do avaliador.* O `evaluator.jar` foi empacotado com os `.java` junto dos
   `.class`. Em `SchedulingPeriodParser`, as restrições sem atributo `on=` são lidas com
   `mspdo = DatatypeConverter.parseBoolean(elemento.getText())`, e o booleano vai para o
   mesmo campo que o `on=` preenche nas demais. Em
   `MaxAndMinConsecutiveWorkingWeekendsCondition`, a numeração só é construída dentro de
   `if (contract.MIN_CONSECUTIVE_WORKING_WEEKENDS_ON)`, e toda condição nasce com
   `ENABLED = false`.

A regra deixa de ser convenção adotada e passa a ser comportamento verificado.

Fonte dos dados: `docs/inventario_instancias.csv`, colunas `<Restricao>_on`,
`<Restricao>_peso` e `<Restricao>_valor`.

---

## 2026-09-15 — Quinto alvo de validação: `medium_late05`

**Status: vigente**

Acrescentado `medium_late05` (ótimo 107, Tabela 6 de Santos et al., 2016) ao conjunto de
validação, que passa a ser `sprint01` = 56, `sprint02` = 58, `long01` = 197, `long02` = 219
e `medium_late05` = 107.

**Por quê.** Os quatro alvos anteriores pertencem todos ao lote *early*, e a varredura de
2026-09-15 mostrou que nesse lote quatro restrições flexíveis estão desligadas em todos os
contratos: máximo e mínimo de fins de semana consecutivos, turno noturno antes de fim de
semana livre e habilidade alternativa. Além disso, todos os pesos do lote valem 1 e a
definição de fim de semana é sempre `SaturdaySunday`. Um erro de multiplicação por peso, ou
no tratamento de `FridaySaturdaySunday`, passaria nos quatro sem ser detectado. Validar
sobre eles prova 8 das 13 restrições, não as 13.

A escolha do `medium_late05` entre as 60 instâncias com valor de referência se deu por
cobertura: é a que exercita todas as restrições que aparecem ligadas em alguma instância do
benchmark, e ainda tem duas habilidades, pesos diferenciados de 1 a 10 e pedidos de folga.
Tem gap 0 na Tabela 6, ou seja, 107 é ótimo comprovado, não melhor solução conhecida.

Amparo: a documentação oficial (Haspeslagh et al., 2010) trata os lotes *early*, *late* e
*hidden* como momentos de divulgação (Regra 7), não como classes de dificuldade, e a seção
2.2 declara que instâncias diferentes podem atribuir pesos diferentes às restrições. A
própria competição rankeou finalistas sobre *early* + *late*. Validar sobre um lote só não
tem respaldo no desenho da competição.

Custo baixo, porque conferir a função objetivo no avaliador não exige provar o ótimo: basta
que o valor interno coincida com o do avaliador em qualquer escala viável. A comparação com
o 107 é um segundo teste, separável. É validação, não experimento, e não disputa o prazo de
congelamento de 14/10.

Proposta P1 do `PROPOSTAS.md`, validada em 2026-09-15.

---

## 2026-09-15 — Escopo: implementar as 13 flexíveis, inclusive as não exercitadas

**Status: vigente**

O modelo implementa as 13 restrições flexíveis da definição oficial, mais as metades "on"
dos pedidos (`DayOnRequests` e `ShiftOnRequests`), mesmo que três desses itens não sejam
exercitados por nenhuma instância do INRC-2010:

| Item | Situação nos dados |
|---|---|
| Máximo de fins de semana trabalhados em quatro semanas | presente nos 235 contratos, `on="0"` em todos |
| Folgas após sequência de turnos noturnos | elemento ausente em todas as 69 instâncias |
| Pedidos para trabalhar (dia e turno) | nenhuma instância traz `DayOnRequests` ou `ShiftOnRequests` |

**Por quê.** As três constam da definição oficial do problema, com semântica fixada: a seção
2.1 lista o máximo de fins de semana em quatro semanas e as folgas após noites entre os
campos do contrato; a seção 2.2.3 dá a numeração formal de "Two free days after a night
shift" (Tabela 7), com o número de folgas fixo em duas — o elemento do XML é booleano e não
tem parâmetro; e os pedidos "on" têm numeração própria, com `min pert = 1`. Santos et al.
(2016) implementam as 13 — as restrições 11 e 12 da formulação deles são justamente as duas
em questão.

Como o trabalho se posiciona em relação a essa formulação, implementar menos exigiria
justificar a diferença. "Não implementei porque nenhuma instância usava" é uma delimitação
que a banca pode questionar; "implementei e não pude validar externamente" é uma ressalva de
método.

**Ressalva obrigatória no texto:** esses três itens não têm conferência externa possível com
os dados do INRC-2010. Nenhuma instância produz penalidade deles, então nem o avaliador
oficial nem a Tabela 6 dizem se a implementação está correta. Devem ser declarados como
implementados e não validados.

**Consequência para a instância brasileira:** havendo escolha entre limitar fins de semana
pela restrição de fins de semana consecutivos (exercitada por 49 instâncias, portanto
validável) ou pela de fins de semana em quatro semanas (exercitada por nenhuma), usar a
primeira.

Proposta P2 do `PROPOSTAS.md`, alternativa A′, validada em 2026-09-15.

---

## 2026-09-15 — Cobertura: igualdade também onde a demanda não é declarada

**Status: vigente**

No modelo, para **todo** par (dia, tipo de turno) do horizonte, a soma das atribuições é
igual à demanda. Quando o bloco de cobertura do dia da semana não lista um turno, a demanda
daquele turno naquele dia é zero — e a igualdade proíbe qualquer atribuição a ele. Não é
"sem restrição".

Exemplo concreto: em `long01` o turno `DH` só aparece na cobertura dos dias úteis. Pela regra
adotada, ninguém faz `DH` no sábado e no domingo.

Por quê: a documentação oficial (2.2.1) exige que toda a demanda seja atendida, e Santos et
al. (2016) modelam a cobertura como igualdade, não como limite inferior. Com desigualdade, o
modelo poderia alocar profissionais além do necessário sem custo nenhum enquanto a função
objetivo estiver incompleta, e mais tarde usaria a folga para diluir penalidades.

Conferido: o modelo mínimo com essa regra produziu escala aceita pelo avaliador oficial nas
69 instâncias. O avaliador rejeita tanto cobertura excedida quanto turno não atribuído, o que
é consistente com igualdade.

Implementado em `src/modelo.py`, restrição `cobertura`.

---

## 2026-09-18 — Restrição não pontuada pelo avaliador fica fora da função objetivo

**Status: vigente**

`NoNightShiftBeforeFreeWeekend` **não entra na função objetivo nas instâncias do INRC**.
Continua implementada e documentada em `src/avaliacao.py`, e volta a valer na instância
brasileira.

**Por quê.** O avaliador oficial não pontua essa restrição. Verificado em 2026-09-18 no
código-fonte que acompanha o `evaluator.jar`: o campo `NO_NIGHT_FREE` é lido pelo parser,
guardado no contrato e reescrito na saída, mas nenhuma condição o lê — a classe que monta as
condições da numeração instancia treze, e não há nenhuma para esta. Confirmado
empiricamente: o rótulo "No night shift before free weekend" não aparece na saída detalhada
em nenhuma instância, nem quando a restrição está ligada com peso 10 e a escala contém
exatamente a situação que ela penalizaria.

**Consequência.** A restrição está ligada em 44 das 69 instâncias, entre elas a
`medium_late05`, que é alvo de validação. Implementá-la com peso faria o valor do modelo
divergir do avaliador nessas 44 — e o sintoma pareceria erro da nossa função objetivo.

**Relação com a P2.** A P2, validada em 15/09, mandou implementar as 13 flexíveis. Esta
entrada não a revoga: o modelo cobre as 13. O que muda é que uma delas fica com peso zero
nas instâncias do INRC, por divergência declarada do avaliador — situação diferente das
outras três, que apenas não são exercitadas pelos dados. Na instância brasileira, onde não há
avaliador para contradizer e a regra tem sentido clínico, ela entra normalmente.

O mesmo vale, sem consequência prática, para `MaxWorkingWeekendsInFourWeeks`: também não tem
classe de condição no avaliador, e está desligada nos 235 contratos.

**Contagem correta das 13, para o texto** (corrigida em 2026-09-18; a redação anterior somava
15 porque contava os pedidos "on" como restrições à parte):

| Situação | Quantas | Quais |
|---|---|---|
| Implementadas e validadas contra o avaliador e contra ótimos publicados | 10 | número de atribuições; dias consecutivos de trabalho; dias consecutivos de folga; fins de semana consecutivos; fim de semana completo; turnos idênticos no fim de semana; habilidade alternativa; padrões indesejados; pedido de dia; pedido de turno |
| Implementadas sem conferência externa possível | 2 | máximo de fins de semana em quatro semanas; folgas após noites |
| Fora da função objetivo por divergência declarada do avaliador | 1 | turno noturno antes de fim de semana livre |

Os pedidos "on" — trabalhar num dia ou num turno — não são restrições à parte: são a metade
positiva das restrições 12 e 13, cujas metades negativas estão validadas. Estão implementadas
e nenhuma instância as exercita.

---

## 2026-09-18 — Semântica das flexíveis validada fora do modelo

**Status: vigente**

A penalidade de uma escala passou a ser calculada também em Python puro, em
`src/avaliacao.py`, e conferida contra o avaliador oficial **antes** de a função objetivo
existir.

Resultado: 207 escalas nas 69 instâncias, penalidade idêntica à do avaliador em todas, par a
par de profissional × restrição. Mais 36 escalas adversárias em 6 instâncias, também idênticas.

**Procedência das escalas** — o texto vai precisar disso, porque tamanho de conjunto de teste
não é cobertura. Nenhuma das escalas veio do modelo nem de solver: todas foram construídas por
heurísticas próprias, com vieses diferentes de propósito.

| Gerador | O que produz | Para que serve |
|---|---|---|
| guloso aleatório | atende a demanda sorteando quem está livre | caso geral, escalas densas |
| guloso ignorando habilidade | idem, sem respeitar a habilidade do turno | exercita a habilidade alternativa |
| concentrado | sempre os mesmos profissionais primeiro | produz ociosos e horizontes cheios |
| janelas | cada profissional só aceita dias de uma janela sorteada | blocos curtos e folgas longas |
| alternado | prefere quem não trabalhou no dia anterior | blocos de tamanho 1 em série |
| bordas | concentra o trabalho no início ou no fim do horizonte | convenções de borda do horizonte |

Que as escalas não venham do solver é a parte importante: se viessem, seriam todas de
penalidade baixa e estruturalmente parecidas, e exercitariam pouco cada restrição. A cobertura
efetiva está medida: 13 das 19 chaves de penalidade dispararam, com milhares de violações
cada.

As 6 chaves que ficaram em zero **não têm todas o mesmo motivo**, e a distinção importa:

| Chave | Por que zero |
|---|---|
| máximo de fins de semana em quatro semanas | desligada nos 235 contratos |
| folgas após noites | elemento ausente em todas as instâncias |
| pedidos "on" de dia e de turno | nenhuma instância traz esses blocos |
| turno noturno antes de fim de semana livre | **está ligada em 44 instâncias; é o avaliador que não a pontua** |

As três primeiras linhas são ausência de dado. A última é divergência declarada, e as 44
instâncias em que a restrição está ligada funcionam como teste: em todas elas o cálculo com
peso zero coincidiu com o avaliador.

Esse teste só vale se a situação penalizável de fato ocorreu nas escalas. Medido: das 44
instâncias com a restrição ligada, **43 tiveram pelo menos uma ocorrência** de turno noturno
na véspera de fim de semana livre, num total de 815 ocorrências, considerando apenas
profissionais cujo contrato tem a restrição ativa. A única sem nenhuma é a `sprint_late02`,
que não tem tipo de turno noturno — a situação é impossível ali por construção. Ou seja, o
teste cobriu todas as instâncias em que ele podia existir.

Por que isso vale registro: separa erro de semântica de erro de modelagem. Quando a função
objetivo do Pyomo divergir, a dúvida não será mais "entendi a restrição errado ou linearizei
errado" — a semântica já está fixada contra o árbitro externo, e o que sobra é linearização.

Efeito colateral útil: a decomposição por profissional que o Experimento B exige — penalidade
máxima individual, amplitude, dispersão — sai desse módulo, já que o modelo só devolve o
total.

---

## 2026-09-18 — Funcao objetivo: uma folga por violacao, nao por termo

**Status: vigente**

A funcao objetivo lineariza a semantica fixada em `src/avaliacao.py`. Duas convencoes de
construcao, ambas com consequencia numerica:

**Uma variavel de folga por violacao, com tantos limites inferiores quantos forem
necessarios.** O erro que isso corrige foi real: o padrao "livre na sexta, trabalha no fim de
semana" gerava uma folga por dia do fim de semana, entao quem trabalhasse sabado e domingo
pagava duas vezes. O avaliador cobra uma vez por semana. No `long02` isso valia 16 pontos, e
era a diferenca entre provar 221 e provar o otimo correto, 219.

**Contagem por janela, quando a penalidade e proporcional ao excesso.** Para o maximo de dias
consecutivos com limite L, uma folga por janela de L+1 dias reproduz exatamente `bloco - L`,
porque um bloco de tamanho R contem R-L janelas inteiras. Para o minimo, um indicador por
(inicio, tamanho de bloco curto), com dia virtual de folga fora do horizonte — bloco encostado
na borda conta.

A funcao objetivo e montada **por familia de restricao** (`m.parcela[familia]`). Nao e
enfeite: foi a decomposicao que localizou o erro acima, e e a mesma decomposicao que o
Experimento B precisa.

**Resultado da validacao**, com o modelo completo e habilidade tratada como flexivel:

| Instancia | Otimo provado | Tabela 6 | Avaliador oficial |
|---|---|---|---|
| sprint01 | 56 | 56 | 56 |
| sprint02 | 58 | 58 | 58 |
| long01 | 197 | 197 | 197 |
| long02 | 219 | 219 | 219 |

Os tres valores coincidem em cada linha: funcao objetivo do modelo, `avaliacao.py` e avaliador
oficial. `medium_late05` = 107 segue pendente por tempo de solver, nao por semantica.

Ressalva de leitura, para nao virar erro no texto: quando o solver para no limite de tempo, as
folgas nao estao apertadas e o valor da funcao objetivo fica **acima** da penalidade real da
escala. Só vale comparar objetivo com penalidade quando a otimalidade foi provada; fora disso,
a penalidade que conta e a calculada pelo `avaliacao.py` sobre a escala.

---

## 2026-09-18 — Habilidade é restrição flexível, não restrição de domínio

**Status: vigente**

O profissional pode ser atribuído a turno cuja habilidade ele não tem; a atribuição é
**penalizada, não proibida**. A penalidade entra como coeficiente na própria variável de
atribuição `x[n,s,d]`, quando a restrição está ativa no contrato.

**Por quê.** Três evidências convergentes:

1. *A formulação de referência.* Santos et al. (2016, p. 228) declaram duas restrições
   rígidas — cobrir a demanda e um turno por pessoa por dia — e listam a habilidade
   alternativa entre as 13 flexíveis, item 10. Na p. 231, as flexíveis 10 e 13 são penalizadas
   diretamente nos coeficientes de `x`, pelo coeficiente ν.
2. *O avaliador oficial.* `hasSkill` aparece num único ponto do código, dentro de
   `AlternativeSkillCondition`, sob a flag do contrato. Não há checagem rígida de habilidade em
   lugar nenhum: as únicas rígidas são cobertura excedida e turno não atribuído.
3. *A reprodução do ótimo.* Com essa leitura, `long01` dá **exatamente 197**, com otimalidade
   provada — o valor da Tabela 6.

**A versão rígida passa a ser divergência declarada de modelagem**, não interpretação
disputada do benchmark. Ela fica reservada à instância brasileira, onde compor equipe por
categoria é justamente o mecanismo em estudo. A flag permanece no código:
`construir(inst, habilidade_rigida=True)` e `--habilidade-rigida` na linha de comando.

**Por que o teste planejado foi cancelado.** O `PLANO.md` mandava rodar as duas leituras
contra `long01` = 197 e ver qual batia. O item foi removido, e o motivo fica aqui para não
ser reaberto: as duas leituras **não são distinguíveis** por esse teste. Em `long01` a
restrição está desligada, logo o coeficiente é zero e a habilidade não custa nada; a leitura
rígida apenas restringe o conjunto viável, então só pode devolver 197 ou mais. Se devolvesse
197 também, o empate não diria nada. A rodada que valia é a livre, e ela já foi feita.

Proposta P3 do `PROPOSTAS.md`, validada em 2026-09-18.

---

## 2026-09-18 — Invariante do Experimento A: horas de assistência

**Status: vigente; motivo original superado.** Motivo atual: a ferramenta converte o Parecer em horas de assistência e reagrega por regime. A consequência 3 é registro do escopo anterior.

O Experimento A compara os dois regimes a **horas de assistência constantes**, não a
atribuições constantes. A instância de 12×36 tem de entregar a mesma assistência em
horas-profissional que a instância de 8 horas de onde ela foi derivada.

**Por quê.** Sob o invariante de atribuições, passar 740 turnos de 8 h para 12 h compra 50%
mais cuidado e depois cobra esse cuidado como se fosse custo do regime: o 12×36 apareceria
exigindo mais gente por um motivo que não é o regime. A comparação só isola o efeito do
regime se a assistência entregue for a mesma nos dois lados. Resolve a proposta P4.

**Consequências declaradas:**

1. A conversão da demanda de 8 h para blocos de 12 h é **reconstrução**, não reetiquetagem:
   a demanda vira um perfil horário e é reagregada nas janelas de 12 h.
2. O efetivo do regime de 8 horas é **recalculado** no mesmo critério do 12×36. O baseline
   deixa de ser os 49 profissionais do `long01`, que operam a 54% de utilização e não
   representam um regime de 8 horas brasileiro. Comparar 49 com um 12×36 em utilização plena
   misturaria mudança de regime com mudança de utilização.
3. O resultado do Experimento A é a **distância percentual entre o piso aritmético e o efetivo
   mínimo viável**, em cada regime — não o número absoluto de profissionais. O piso vem da
   divisão horas/capacidade; o mínimo viável vem do modelo. A diferença entre os dois é o que
   as restrições custam, e é o que o modelo tem a dizer.

   *Nota de 29/09/2026:* a consequência 3 é registro do escopo anterior.

**Ressalva.** A entrada de 08/09 "12×36 é inviável no efetivo original: vira Experimento A"
foi construída sobre o invariante de atribuições e **está superada** nessa parte: sob o
invariante de horas não há inviabilidade no efetivo original. A estimativa de "90 a 100
profissionais" registrada lá não decorre de nenhum dos dois invariantes e não deve ser usada.

**Pendência aberta.** A regra aritmética da conversão ainda não está fechada: a regra de teto
por janela não satisfaz este invariante. Ver P5 no `PROPOSTAS.md`.

---

## 2026-09-18 — Composição da equipe e grau de dependência são parâmetros de entrada

**Status: vigente; motivo original superado.** Motivo atual: numa ferramenta, composição e grau de dependência são dados que o usuário informa, não constantes do código (o motivo registrado era a análise de sensibilidade do objetivo específico 5).

A instância brasileira é construída por `src/instancia_br.py` com **composição da equipe por
categoria** (enfermeiro / técnico) e **grau de dependência assistencial** como parâmetros de
entrada, variáveis, e não como valores fixados no código.

**Por quê.** O objetivo específico 5 é análise de sensibilidade. Se a composição e o grau de
dependência estiverem embutidos no construtor, a análise de sensibilidade exige editar código
a cada cenário, e o que for publicado no texto não é reprodutível a partir de um comando. Como
parâmetros, cada cenário é uma linha em `resultados/consolidado.csv` com os parâmetros na
própria linha.

**Consequência.** O grau de dependência assistencial deixa de ser pergunta aberta: não está em
base pública porque é classificação clínica, não cadastral, e por isso entra como parâmetro em
três níveis (mínimo, intermediário, intensivo) em vez de suposição única. O mesmo vale para a
composição por categoria, cuja origem normativa é declarada mas cujo valor é varrido.

---

## 2026-09-18 — Experimento B: fixar o ótimo e reportar a amplitude da dispersão

**Status: vigente**

No Experimento B, a distribuição da penalidade entre profissionais é medida **com o valor
ótimo Z\* fixado como restrição**, resolvendo duas vezes: uma minimizando a medida de
dispersão e outra maximizando-a. O resultado reportado é a **amplitude** entre os dois, não um
número único.

**Por quê.** O problema tem ótimos múltiplos: várias escalas distintas alcançam o mesmo Z\*, e
elas distribuem a penalidade de maneiras diferentes entre as pessoas. Reportar a dispersão de
*uma* solução ótima é reportar o desempate arbitrário do solver, que muda com a versão, com a
semente e com a ordem das restrições. Com Z\* fixado e a dispersão otimizada nos dois sentidos,
o que se afirma é uma propriedade do conjunto de ótimos, não do solver.

**Consequência.** Cada célula do Experimento B custa três resoluções, não uma: o ótimo e os
dois extremos. As instâncias precisam ser pequenas o bastante para provar otimalidade três
vezes — exigência que já estava no `PLANO.md` e agora tem motivo registrado.

**Ressalva.** Se a amplitude sair estreita, a afirmação fica forte: a distribuição é
propriedade do ótimo. Se sair larga, a afirmação vira outra e igualmente publicável: o critério
de penalidade total **não determina** a distribuição, e escolher entre ótimos é decisão de
gestão que o modelo não toma sozinho. Os dois desfechos servem ao trabalho; nenhum deles é
resultado negativo.

---

## 2026-09-21 — Instância brasileira: parâmetros do Parecer Normativo COFEN nº 1/2024

**Status: vigente**

A instância brasileira é construída a partir do Parecer Normativo COFEN nº 1/2024, calibrada
ao porte do `long01`. Parâmetros extraídos e conferidos na fonte primária pelo projeto de
redação; **não reinterpretar a norma no código**.

| Grau | Horas/paciente/24 h | % enfermeiros | % técnicos |
|---|---|---|---|
| Mínimo | 4 | 33% (mínimo que garanta 1 por turno) | 67% |
| Intermediário | 6 | 33% (mínimo que garanta 1 por turno) | 67% |
| Alta dependência | 10 | 36% | 64% |
| Semi-intensivo | 10 | 42% | 58% |
| Intensivo | 18 | 52% | 48% |

**O que foi decidido:**

1. **Porte** = 5.920 horas-profissional em 28 dias = 211,43 h/dia. É o mesmo número do
   invariante da P4, o que amarra as duas propostas: o `long01` fica como referência de
   escala, não como fonte de demanda.
2. **Perfil uniforme nas 24 h.** O Parecer dá horas por paciente em 24 h, sem curva horária.
   Logo 211,43 / 24 = **8,81 profissionais presentes em qualquer hora**.
3. **Carga semanal de 42 h nos dois regimes.** No 12×36 é estrutural (máx. 14 plantões em
   28 dias); no de 8 h entra como `MaxNumAssignments` = 21.
4. **Quadro de referência** do Experimento A, sem IST: QP_ref = 211,43 × 7 / 42 = **35,24**.
   A fórmula do Parecer (QP = THE × DS × (1 + IST) / CHS) **não depende de regime de
   jornada** — dá o mesmo quadro para os dois. É isso que o Experimento A põe à prova.
5. **Grau de dependência como parâmetro**, com o porte fixo em todos os níveis: o que muda é
   só a composição exigida (33% a 52% de enfermeiros). Isola o efeito da composição.
6. **Composição no quadro, não na cobertura** (leitura literal do Parecer): o percentual se
   aplica a quantos enfermeiros são contratados, e a cobertura só carrega o piso de 1
   enfermeiro por janela onde a norma o prevê — mínimo e intermediário. No código isso vira
   um turno genérico por janela mais um turno de enfermeiro com cobertura 1.
7. **A proporção profissional/paciente por turno não é usada.** Era da Resolução 543/2017,
   revogada. O Parecer não a traz.
8. **Fora de escopo, declarado:** IST de 15%, 5% de educação permanente, enfermeiros para
   atividades gerenciais e acréscimo de 10% por restrição de atividade. São fatores de
   dimensionamento, fora do horizonte de escalonamento, e o IST é multiplicativo igual nos
   dois regimes — não altera a comparação relativa. Robustez a ausências fica como trabalho
   futuro.

**Consequência a declarar no texto.** Manter o porte fixo em todos os graus significa que a
unidade representada **muda de tamanho** conforme o grau: 52,9 pacientes no mínimo contra
11,7 no intensivo. O número de pacientes nunca entra no modelo — a escala só vê horas e
composição — mas precisa estar no texto para o leitor saber o que a instância representa.

**Controle do desenho, não resultado.** O piso aritmético de efetivo é **36 nos dois
regimes** — 8,81 por janela vira 9 pelo teto, dando 216 h/dia (+2,16%) e 36 profissionais
tanto em 8 h quanto em 12×36. Isso sai **por construção**, porque a carga semanal foi
igualada em 42 h; não é achado e não deve ser reportado como tal. A forma correta para a
metodologia:

> Com a carga semanal igualada, o piso aritmético coincide nos dois regimes, de modo que
> qualquer diferença no mínimo viável decorre das restrições de escalonamento.

A P5 também não se coloca nesta instância: com perfil uniforme o resíduo de arredondamento é
idêntico nos dois regimes.

---

## 2026-09-21 — Definição de viável, e limites legais como rígidos

**Status: vigente; motivo original superado.** Motivo atual: a ferramenta promete escala em conformidade legal, então limite legal não pode ser trocado por penalidade (o motivo registrado era não esvaziar o Experimento A).

**Viável = satisfaz a cobertura e todos os limites legais de jornada e descanso.** As demais
restrições flexíveis entram apenas na penalidade, que é objeto do Experimento B.

É a definição que vai para o capítulo de método, e ela decide o que o Experimento A mede.

**Por quê.** No formato do INRC toda restrição de contrato é flexível, com peso. Se os
limites legais forem tratados assim, "efetivo mínimo viável" vira capacidade dividida por
demanda: qualquer efetivo é viável, basta pagar a penalidade. O experimento perderia o
conteúdo.

**Como.** Flag `rigidas_legais` em `modelo.py`, com o conjunto `RIGIDAS_LEGAIS_BR`
(`max_num_assignments`, `max_consecutive_working_days`, `unwanted_patterns`). O limite vira
restrição rígida em vez de ganhar folga — mesma expressão, sem Big-M e sem peso alto. O
padrão é vazio, o que preserva o comportamento do INRC e mantém os quatro ótimos publicados
reproduzindo.

**O XML continua sendo instância normal do INRC.** A rigidez é opção de quem resolve, não
propriedade do arquivo: uma escala que respeita os limites tem violação zero neles, e o
avaliador oficial cobra zero. A instância segue reutilizável por terceiros.

**Regras de descanso codificadas, e conferidas.** `src/instancia_br.py --conferencia`
enumera todas as sequências que o contrato admite e mede o intervalo:

| Regime | Menor intervalo | Exigido | Caso mais apertado |
|---|---|---|---|
| 12×36 | **36 h** | 36 h (CLT art. 59-A) | diurno *d* → diurno *d*+2, e noturno *d* → noturno *d*+2 |
| 8 h | **16 h** | 11 h (art. 66) | manhã *d* → manhã *d*+1 |
| 8 h, com o dia do meio livre | **24 h** | 24 h (art. 67) | noturno *d* → manhã *d*+2 |

As duas regras valem, e valem justas — o descanso semanal é atingido no limite.

**No 12×36, `MaxConsecutiveWorkingDays = 1` não bastava.** O plantão noturno termina às 07:00
do dia seguinte; com o dia do meio livre, o diurno de dois dias depois começa às 07:00 — são
24 h, não 36. Única combinação com o furo. Corrigido pelo padrão indesejado `clt_36h_N_D`
(noturno, folga, diurno). Não é escolha de modelagem: o art. 59-A fala em doze horas seguidas
por trinta e seis horas ininterruptas de descanso. Propostas P7.1, P7.2 e P7.3, validadas em
21/09.

**Consequência a observar na análise:** a proibição tende a separar a equipe em turmas fixas
de dia e de noite. Vale olhar isso nas escalas do Experimento B.

---

## 2026-09-21 — Experimento B: núcleo no INRC, e o que entra na penalidade comparada

**Status: vigente.** As subseções têm marca própria.

### Restrição estrutural: a regra

**Status: registro do escopo anterior.** A função "escala mais equilibrada"
(`src/experimentos.py`) não usa esta regra: fixa Z\* sobre o modelo completo, com todas as
famílias que a instância liga.

**Uma restrição é estrutural quando o regime determina se ela pode ser violada.** Três
degraus:

| O regime… | Exemplo | Tratamento |
|---|---|---|
| força ou impede a violação | `complete_weekends`, `identical_shift_types_during_weekend` | fora da penalidade comparada |
| altera a chance de violação | pedidos de folga | dentro, lido como efeito do regime |
| não interfere | — | dentro |

Os pedidos ficam no degrau do meio: na mesma carga de 42 h semanais o 12×36 folga 14 dos 28
dias e o de 8 h folga 7, então um pedido sorteado cai em folga com probabilidades diferentes.
É efeito real do regime, não artefato.

**Leitura obrigatória no texto:** *o regime concede mais dias livres na mesma carga* — nunca
*as escalas são mais justas*.

### A família de fins de semana não é ligada

**Status: registro do escopo anterior.** A função "escala mais equilibrada" não usa esta
regra: nas instâncias do INRC a família entra como o XML define.

Dois motivos. **Quase estrutural no efetivo mínimo:** perto do máximo de 14 plantões o 12×36
opera quase em alternância estrita, e alternância estrita numa semana de 7 dias cai em um dia
de todo fim de semana — a família fica quase determinada pelo regime justamente onde o
experimento mede. **Sem conferência externa:** o máximo de fins de semana em quatro semanas é
uma das duas implementadas sem conferência possível; ligá-la com valores nossos apoiaria o
resultado em código nunca validado.

### O núcleo do Experimento B roda no INRC, com ótimo provado

**Status: vigente.** É a base da função "escala mais equilibrada".

A pergunta central — *entre as escalas de custo mínimo, quanto a distribuição da penalidade
entre profissionais pode variar* — **não depende de regime**. Roda nas quatro instâncias com
Z\* provado: `sprint01` = 56, `sprint02` = 58, `long01` = 197, `long02` = 219. Sem dado
sintético: a penalidade é a do próprio benchmark.

Ordem: as duas `sprint` primeiro (10 profissionais, otimalidade tripla praticamente garantida);
as `long` se fecharem no tempo. Se não fecharem, o experimento fica nas sprints, declarado.

**Verificado em 21/09, antes de qualquer otimização.** A penalidade decompõe exatamente por
profissional, e cada parcela individual bate com o avaliador oficial:

| Instância | Z\* | Σ p_n | Profissionais | Divergências por profissional | max p_n | zerados |
|---|---|---|---|---|---|---|
| `sprint01` | 56 | 56 | 10 | **0** | 14 | 0 |
| `sprint02` | 58 | 58 | 10 | **0** | 12 | 1 |
| `long01` | 197 | 197 | 49 | **0** | 16 | 8 |
| `long02` | 219 | 219 | 49 | **0** | 15 | 4 |

Duas consequências. A soma das parcelas individuais é **exatamente** Z\*, então a fatia do
profissional mais penalizado é participação num total fixo — a medida do Experimento B está
bem definida. E **todo número que o Experimento B reportar tem conferência externa**: o
avaliador oficial imprime o custo por empregado, e ele coincide com o `avaliacao.py` nos 118
profissionais das quatro instâncias. A coluna "max p_n" é de **um** ótimo arbitrário; o
experimento é justamente medir o intervalo em que ela pode variar.

### Versão por regime: extensão, só se sobrar tempo antes de 14/10

**Status: registro do escopo anterior.**

Instância brasileira, grau intermediário apenas, penalidade só de pedidos de folga gerados por
regra declarada: mesma taxa por profissional que o `long01`, mesma divisão entre pedido de dia
e de turno, mesmo peso — só a posição é sorteada, com **várias sementes publicadas** e a
variação entre elas reportada. Uma semente só é anedota.

A frase "pesos herdados do `long01`, declarados" sai do registro: na família que interessa não
havia o que herdar.

---

## 2026-09-22 — Medida de dispersão do Experimento B: penalidade individual máxima

**Status: vigente**

A dispersão comparada é a **penalidade individual máxima**, `max_n p_n`, com o total fixado
em Z\*. O reportado é o **intervalo** entre o mínimo e o máximo que ela pode assumir entre as
escalas ótimas. Resolve a proposta P9.

**Por que a medida se sustenta.** A penalidade decompõe exatamente por profissional (soma =
Z\*, conferido nas quatro instâncias contra o avaliador oficial), então `max_n p_n` é
participação num total fixo. É linear, e tem leitura gerencial direta: *entre as escalas
ótimas, quem sai pior recebe entre tanto e tanto*. O valor fica sempre em `[⌈Z*/N⌉, Z*]`.

**Por que fixar o total já garante escala ótima.** Cada folga é variável contínua limitada
por baixo pelo excesso que representa. Exigir que a soma dê exatamente Z\* força duas coisas
de uma vez: a escala tem de ser ótima, senão a soma dos limites passaria de Z\*, que é o
mínimo; e cada folga tem de valer exatamente o seu limite, senão a soma passaria. Logo `p_n`
é a penalidade real da pessoa, não um valor inflado pelo solver. O mesmo vale para os termos
que não usam folga — fins de semana completos, turnos idênticos, habilidade e pedidos são
funções exatas das variáveis de atribuição, sem folga nenhuma.

**As formas.** Minimizar o máximo é minimax: uma variável `t`, N restrições `t >= p_n`, uma
resolução. Maximizar o máximo é maximizar função convexa, então precisa de disjunção:

| Forma | Como | Custo | Devolve |
|---|---|---|---|
| **B** | uma resolução por profissional, maximizando `p_n` | N resoluções independentes | o **perfil completo** |
| **A** | binárias `z_n`, `Σ z_n = 1`, `t <= p_n + M(1 − z_n)`, com **M = Z\*** | 1 resolução, +N binárias | só o máximo geral |

`M = Z\*` é válido e justo, porque `0 <= p_n <= Z\*` — não há patologia de Big-M.

**Adotado:** forma B nas duas `sprint`, guardando o máximo de **cada** profissional, porque o
perfil completo vai para o capítulo de resultados; forma A como reserva nas duas `long`, se as
49 resoluções ficarem lentas. Implementado em `src/experimentos.py`.

**Como ler o resultado, nos dois desfechos.** Amplitude estreita: a distribuição é propriedade
do ótimo. Amplitude larga: o critério de penalidade total **não determina** a distribuição, e
escolher entre ótimos é decisão de gestão que o modelo não toma sozinho. Os dois são
publicáveis; nenhum é resultado negativo.

---

## Perguntas abertas

### Fim de semana incompleto no horizonte

**Status: fechada** em 29/09/2026. A ferramenta exige início numa segunda-feira e horizonte
de 28 dias; mês civil arbitrário é limitação declarada.

O horizonte pode começar ou terminar no meio de um fim de semana, deixando um bloco parcial —
um domingo solto no primeiro dia, por exemplo. As restrições de fim de semana (completos,
turnos idênticos, consecutivos) precisam de uma convenção para esses blocos: ignorar,
avaliar como se fossem completos, ou avaliar proporcionalmente.

Nas 69 instâncias do INRC **não ocorre**: todos os blocos de todos os contratos são completos,
verificado em 2026-09-15 pelo `src/parser.py`. Por isso a pergunta não bloqueia a validação.

Ela bloqueia a instância brasileira, cuja data de início ainda não foi escolhida. Saída mais
simples: escolher início e fim que fechem fins de semana completos, e a pergunta desaparece.
`Instancia.fins_de_semana()` já marca cada bloco com `completo=True/False`.

### A habilidade é restrição rígida ou flexível?

**Status: fechada** em 2026-09-18, pela entrada "Habilidade é restrição flexível, não restrição de domínio".

`AlternativeSkillCategory` aparece ora com conteúdo `true`, ora `false`, e o peso nem
sempre acompanha. A varredura de 2026-09-15 separou os casos em que isso importa dos casos
em que não importa:

| Instâncias | Conteúdo e peso | Importa? |
|---|---|---|
| duas habilidades (todas as `long`, `medium_hidden`, `medium_late05`) | `true` sempre com peso > 0; `false` sempre com peso 0 | sim — e são coerentes |
| uma habilidade só (todas as `sprint`, demais `medium`) | inclui `false` com peso 10 | não — sem segunda habilidade a restrição não tem o que penalizar |

Ou seja: a incoerência que motivou esta pergunta (`false` com peso 10, em `sprint_hint01`)
está inteira no grupo em que a restrição é inócua. Nas instâncias em que ela pode morder,
valor e peso são coerentes. Isso elimina a hipótese de "valor residual" como problema
prático, mas **não** resolve o que `false` significa.

**Correção de 2026-09-15: a leitura que estava registrada aqui como provável está
invertida.** Esta entrada dizia que `false` significaria categoria alternativa proibida, isto
é, restrição de domínio. Para o avaliador oficial, é o contrário.

*O que a documentação oficial diz* (seção 2.2.3, "Alternative skill", Tabela 10): cada
unidade de tempo em que o profissional não tem a habilidade exigida recebe um número próprio,
com `max pert = 0`. Ou seja, quando a restrição está ligada, cada atribuição fora da
habilidade custa uma vez o peso. O documento não diz o que acontece quando ela está
desligada.

*O que o código do avaliador faz.* `hasSkill` aparece em um único ponto de todo o código,
dentro de `AlternativeSkillCondition`, sob `if (contract.ALTERNATIVE_SKILL)`. Com a flag em
`false`, a condição não é sequer construída. As únicas checagens rígidas do avaliador são
cobertura excedida (`NoShiftToAssignException`) e turno não atribuído (`AllShiftsAssigned`).
Não existe checagem rígida de habilidade em lugar nenhum.

*Confirmação empírica.* Resolveu-se o modelo mínimo de `long01` nas duas leituras. Com
habilidade livre, 46 atribuições ao turno `DH` couberam a profissionais sem `HeadNurse`, e o
avaliador devolveu 1516 — contra 1517 da versão rígida. Nenhuma penalidade foi cobrada pelas
46 violações.

**Consequência para o método de resolução — também registrado errado antes.** Esta entrada
dizia que a pergunta se resolveria na validação do Passo 3, no avaliador. Não se resolve: o
avaliador é indiferente à habilidade quando a flag está em `false`, então ele aceita as duas
leituras. Quem arbitra é a **Tabela 6**: `long_early01` tem ótimo comprovado em 197, e as
duas leituras geram modelos diferentes — se `false` = proibido, o ótimo é ≥ 197; se
`false` = livre, é ≤ 197. Reproduzir 197 exige a leitura certa.

A flag já existe no código: `construir(inst, habilidade_rigida=...)` em `src/modelo.py`, e
`--habilidade-livre` na linha de comando. O teste roda nas semanas 2-3, quando a função
objetivo estiver completa — antes disso não há o que comparar com 197.

Ressalva a registrar no texto, qualquer que seja o resultado: se a leitura rígida for a que
reproduz a literatura, o modelo será mais restritivo que o avaliador. Isso é uma escolha de
modelagem declarada, não um erro — e é defensável, porque compor equipe por categoria é
justamente o mecanismo que a instância brasileira usa.

Alternativa ainda não consultada: o relatório técnico da competição (CODeS/Technical
Report/2010/1, citado nos anais do PATAT 2010) traz a descrição formal das restrições.

### ~~Grau de dependência assistencial da instância brasileira~~ — FECHADA em 18/09

**Status: fechada** em 2026-09-18.

Resolvida: entra como parâmetro de entrada em três níveis, junto com a composição por
categoria. Ver a entrada "Composição da equipe e grau de dependência são parâmetros de
entrada". Mantida aqui só para não parecer que a pergunta foi esquecida.

### Status jurídico do arcabouço normativo de dimensionamento

**Status: aberta.** A verificação em fonte primária, com data de consulta, continua pendente para o capítulo de fundamentação.

A Resolução COFEN 543/2017 foi revogada e há decisões judiciais que suspenderam resoluções
sobre dimensionamento; o Parecer Normativo COFEN nº 1/2024 foi aprovado nos limites das
liminares em vigor.

Verificar status atual em fonte primária, com data de consulta, antes de redigir o capítulo
de fundamentação. As conclusões do trabalho devem ser formuladas de modo a **não depender**
da vigência da norma — a norma é origem declarada dos parâmetros, não fundamento das
conclusões.

---

## 2026-09-23 — O efetivo é determinado pelo teto de 42 h semanais, não pelas regras de descanso

**Status: vigente; motivo original superado.** Motivo atual: o efetivo 36 = teto de 35,24 serve como conferência independente de que a tradução da norma está correta (VIRADA, seção 3); a consequência sobre a hipótese do trabalho e a prioridade 1 eram do escopo anterior.

O Experimento A, sob **demanda uniforme**, fecha em efetivo mínimo 36 nos dois regimes, nas
vinte células. A leitura adotada é: **sob demanda uniforme, nenhuma restrição de escalonamento
aperta além do teto de horas, em nenhum dos dois regimes.**

Por quê. Os dois regimes entregam a mesma capacidade por pessoa em horas, porque o teto legal
é o mesmo: 14 plantões × 12 h = 21 plantões × 8 h = 168 h em 28 dias = 42 h por semana. E
5.920 h ÷ 168 h = 35,24, que é exatamente o `QP_ref` do Parecer Normativo COFEN nº 1/2024. O
mínimo viável é o teto disso, 36. O modelo reproduz o QP do Parecer por um caminho
independente e mostra que as regras de descanso não acrescentam nada a ele.

**Escopo, e é estreito de propósito.** A afirmação NÃO é "o regime não muda o efetivo". Com
perfil uniforme nenhuma restrição tinha como apertar: a alternância do 12×36 preenche janelas
alternadas exatamente, a composição por categoria fecha sozinha porque a proporção é igual em
toda janela, e o piso de um enfermeiro por turno fica longe do limite. As vinte células são a
mesma aritmética replicada, não vinte testes independentes. Decisão do projeto de redação,
23/09.

O que sobrevive como achado positivo: as regras de descanso, **inclusive as 36 h após o
plantão noturno**, não forçam ociosidade no 12×36. E a sonda provando o efetivo 35 inviável é
afirmação forte — o mínimo é exato, não apenas suficiente.

Consequência. A hipótese do trabalho é sobre demanda que varia, e ela não foi testada aqui.
A sensibilidade à variação de demanda entre dias passa a ser a prioridade 1, com a forma da
variação calibrada no `long01` (29 atribuições por dia útil contra 20 por dia de fim de
semana) e o nível mantido em 211,4 h/dia. Ver P12 no `PROPOSTAS.md` e
`docs/nota_experimento_a_2026-09-23.md`.

## 2026-09-23 — Tempo de resolução é afirmação fraca

**Status: vigente**

Tempos de resolução — inclusive a assimetria medida entre 12×36 e 8 h — entram como **uma
frase no capítulo de método, com escopo declarado**, nunca como resultado. Critério do projeto
de redação, reafirmado em 23/09.

---

## 2026-09-29 — Especificação da ferramenta

**Status: vigente**

Especificação completa:
<https://claude.ai/code/artifact/ebfaeed9-a670-49d7-8f24-0067a43f2f04>. Decidida pelo
Otávio no projeto de redação; o orientador é informado na reunião. Fecha a P2.

**Título.** "Ferramenta de apoio à decisão para escalas de enfermagem baseada em Programação
Inteira: conformidade com o dimensionamento do COFEN e a legislação trabalhista".

**Objetivo.** Minimizar a penalidade total, que inclui os pedidos. Entre as escalas
empatadas, a de menor penalidade individual máxima (mecanismo do Experimento B).

**Entradas.**
- Pacientes por grau de dependência. O percentual de enfermeiros vem do grau de maior carga.
- Quadro por quantidade de enfermeiros e de técnicos; nomes opcionais.
- QP em duas parcelas; a escala é comparada ao núcleo sem IST, porque o IST cobre ausências
  que a escala não modela.
- Variação de demanda como razão fim de semana / dia útil, com o total de horas preservado.

**Regras.**
- Proporção de enfermeiros no quadro, com piso de 1 enfermeiro por turno.
- Carga de 42 h semanais.
- Início numa segunda-feira, horizonte de 28 dias.
- Indisponibilidade rígida para férias e licenças; pedidos continuam flexíveis.

**Configuração.**
- Opções avançadas recolhidas, e só depois de o formulário básico funcionar. Critério para
  uma opção entrar: o motor já suporta, não mexe na garantia legal, custa no máximo meio dia.
- Arquivo de configuração no formato INRC, para baixar e carregar, com validação (esquema e
  conferência de descanso) e resumo em português antes de resolver.

**Licença.** MIT.

---

## Modelo de entrada

```
## AAAA-MM-DD — Título curto da decisão

O que foi decidido, em uma ou duas frases.

Por quê. Se houver fonte, citar.

Ressalva ou consequência, se houver.
```
