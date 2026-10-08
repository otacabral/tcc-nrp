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

## 2026-09-29 — Ajustes da Etapa 2

**Status: vigente**

Decididos pelo Otávio no projeto de redação, sobre as pendências da Parte A da Etapa 2.

**Graus misturados.** A unidade segue o maior percentual de enfermeiros entre os graus
presentes. Equivale a "maior carga"; no empate de horas entre alta dependência e
semi-intensivo (10 h cada), vale o semi-intensivo, 42%. Conservador por construção.
Implementado em `instancia_br.grau_de_maior_carga`.

**Horário dos turnos fica fora das opções avançadas.** Três peças supõem os horários dos dois
regimes (07–15–23 no de 8 h, 07–19 no 12×36): a regra `clt_36h_N_D`, escrita à mão em
`_pares_proibidos`; o `reagregar()`, que usa uma duração única e janelas sem sobreposição; e o
`regime_da_instancia` da conferência de descanso, que só reconhece turnos todos de 8 h ou
todos de 12 h. Limitação declarada.

**Arquivo de configuração = pacote** com o XML do INRC e um complemento com o que o formato
não representa — indisponibilidades, para começar. A implementar junto com o arquivo de
configuração, não agora.

**Interface em Streamlit.** Resolução atrás de botão, resultado em `st.session_state`, barra
de progresso.

**Defeito encontrado e corrigido: o descanso semanal não era medido.** Em
`docs/conferencia_descanso_escala.py`, a linha que deveria guardar o descanso semanal era
`menor_semanal = min(menor_semanal, menor_semanal)`, que não faz nada, e o valor não era
devolvido; só o limite de dias seguidos era conferido. Agora, em cada semana do horizonte
(segunda 00:00 a segunda 00:00), mede-se no relógio o maior descanso contínuo, e a escala
reprova abaixo de 24 h (CLT art. 67). Recortar na semana é a leitura estrita: um descanso que
atravessa a virada de domingo para segunda conta, em cada semana, só a parte que cai nela.

*Reconferência:* as 24 escalas guardadas do Experimento A (12 de 8 h, 12 de 12×36) e as
escalas geradas por `src/testes_entrada.py` passam. Nas de 8 h o maior descanso semanal é
**exatamente 24 h** em todas — no limite, pela sequência noturno → folga → manhã, a mesma do
caso mais apertado da conferência de 21/09. Por ser valor no limite em todas, a medição foi
posta à prova com escalas montadas à mão de resposta conhecida (16 h e 23 h reprovam; 24 h e
33 h aprovam), e acerta as quatro.

*Correção de 29/09, mesmo dia — a regra e o registro acima estão errados em dois pontos, e
ficam como registro do erro.* **(1) O recorte na segunda 00:00 reprovava escala legal:** seis
noites de segunda a sábado deixam 40 h de descanso de domingo a segunda, e o recorte só
enxergava 17 h. Regra adotada (decisão do Otávio): para cada semana, contam os intervalos
contínuos de descanso que contêm algum dia da semana sem turno; o maior deles, medido
**inteiro**, sem recorte, precisa ter ao menos 24 h. No fim do horizonte a **borda é aberta**:
o descanso que chega ao último instante conta como cumprido. **(2) "Exatamente 24 h em todas
as escalas de 8 h" vale para 8 das 12.** Nas outras 4 (`intermediario_8h_teto_e36`,
`intermediario_8h_teto_e37_v1`, `intermediario_8h_teto_e38_v05`, `minimo_8h_teto_e36`), a
aprovação da medição antiga veio de um intervalo entre dois dias trabalhados — manhã de um
dia à tarde do seguinte, 24 h —, que não é descanso semanal. Pela regra nova, sem a borda
aberta, as quatro davam 17 h na semana 4: folga só no último domingo, depois de uma noite de
sábado. Com a borda aberta, as 24 escalas e as dos testes passam; os casos montados à mão
foram refeitos com o valor esperado registrado antes de rodar (0 h reprova; 24 h, 40 h, 40 h
e borda aprovam), e acertam todos.

*Argumento, que substitui a ressalva anterior:* `MaxConsecutiveWorkingDays = 6` implica ao
menos um dia sem turno em cada semana segunda–domingo, que são 7 dias consecutivos. Cada dia
sem turno gera ao menos 24 h de descanso contínuo: o pior caso é noite → folga → manhã, 24 h,
medido. Logo, **dentro do horizonte**, o modelo garante o art. 67 por construção, sob o
critério operacional "ao menos um dia sem turno por semana, com descanso contínuo de 24 h ou
mais, medido inteiro". É critério operacional, sem verificação de jurisprudência sobre
descanso que atravessa a virada da semana.

*Limitação:* cada escala é gerada para um período isolado. A continuidade com os períodos
anterior e seguinte — interjornada e descanso na virada — não é conferida. Observação, não
garantia: com turnos fixos e início sempre numa segunda-feira, a folga no último domingo dura
ao menos até 07:00 da segunda seguinte, ou seja, 24 h. Trabalho futuro: receber os últimos
dias do período anterior como entrada (P3 do `PROPOSTAS.md`).

---

## 2026-09-29 — Redesenho da ferramenta

**Status: vigente**

Decidido pelo Otávio no projeto de redação. Especificação completa no link registrado na P2
e na entrada "2026-09-29 — Especificação da ferramenta". **Regra central: a CLT é restrição —
trava a escala; o COFEN é alerta — nunca trava.**

**Configuração com turnos editáveis.** O usuário define os turnos por hora de início e
duração. Novo caminho de `instancia_br.construir(turnos=...)`; o caminho por pacientes
continua igual, e o Experimento A segue reproduzível.

**Demanda informada pelo usuário.** Generalista: enfermeiros e técnicos por turno, com
valores opcionais diferentes para o fim de semana. Específica: por data × turno × categoria,
partindo da generalista (um feriado, por exemplo). **Cobertura entre categorias (decidido em
29/09; antes "a confirmar"):** enfermeiro pode cobrir posto de técnico, como no caminho por
pacientes; técnico nunca cobre posto de enfermeiro. A saída informa quantos turnos de
enfermeiro foram usados em posto de técnico.

**CLT como trava, com diagnóstico do motivo.** *(Registro de 29/09, Etapa 5: o diagnóstico
ainda não estava implementado. Implementado na Etapa 7 — ver "Diagnóstico da trava" abaixo.)*
As regras de descanso deixam de ser escritas
à mão e passam a ser **geradas dos horários** (`pares_proibidos_por_horario`): para cada par
de turnos, o descanso medido no relógio é proibido abaixo de 11 h (art. 66), e abaixo de
36 h depois de turno de 12 h ou mais (art. 59-A). O gerador é a **fonte única** das regras de
descanso — padrões do XML e conferência das sequências saem dele. **Pares já proibidos pelo
limite de dias seguidos do contrato não são emitidos** (opção 1, decisão do Otávio): com o
descarte, a lista gerada é idêntica à escrita à mão nos dois regimes, e o modelo e o XML do
Experimento A não mudam — conferido em 361 XML, byte a byte. **A equivalência é garantida
por teste permanente** (`src/testes_entrada.py`): pares gerados sem descarte = pares com
descarte ∪ pares proibidos pelo limite de dias seguidos. Sem isso, o descarte poderia
esconder uma proibição. A conferência de descanso na escala também passa a tirar o exigido
do turno que termina, e vale para qualquer horário.

No caminho novo, o teto de 42 h/semana é **em horas**, rígido no modelo
(`Instancia.carga_maxima_h`), porque com turnos de durações diferentes contar turnos não
limita horas; e o limite de dias seguidos é 6 (art. 67, aproximado como no regime de 8 h) —
a alternância de quem faz turno de 12 h sai sozinha da regra das 36 h.

**COFEN como alerta** (`instancia_br.alertas_cofen`, que não mexe no modelo): proporção de
enfermeiros no quadro pelo grau predominante informado; turnos sem enfermeiro na demanda;
com pacientes informados, quadro abaixo do QP completo, mostrando também o núcleo. **No
caminho novo, o piso de 1 enfermeiro por turno deixa de ser cobertura rígida** — quem define
a demanda é o usuário — e vira alerta.

**Objetivo (Etapa 7, decisão do Otávio, 29/09).** Evitar enfermeiro em posto de técnico
quando não for necessário, com **pesos inteiros na mesma resolução**: cada turno de enfermeiro
em posto de técnico custa 1; cada pedido de folga não atendido custa W = (número máximo
possível de turnos de enfermeiro em posto de técnico) + 1, e o máximo possível é o total de
postos de técnico do horizonte. Como W passa tudo o que os postos de técnico podem somar,
negar um pedido nunca compensa: primeiro os pedidos, depois o enfermeiro em posto de técnico.
Sem pesos fracionários. Implementado em `ferramenta.pesos`; o modelo ganhou a família
`custo_atribuicao`, vazia no INRC. *Conferido:* no caso de 8 enfermeiros + 5 técnicos, a
contagem caiu de 66 (sem os pesos) para **35, que é o mínimo aritmético** (os técnicos dão
840 h para 1.120 h de posto de técnico), com os 3 pedidos atendidos nos dois casos.

**Equilíbrio ligado na ferramenta.** Com a penalidade da etapa 1 fixada no ótimo, a etapa 2
minimiza a penalidade individual máxima — o mecanismo do Experimento B, sobre o mesmo modelo
(`ferramenta.equilibrar`). Só roda com a etapa 1 ótima e penalidade maior que zero.
*Medido, afirmação fraca:* no 12×36 equivalente ao Experimento A, com 40 profissionais e 20
pedidos, a etapa 1 levou 56,9 s e a etapa 2 90,7 s de CPU (appsi_highs, na máquina do
Otávio); a maior penalidade individual caiu de 10 para 7.

**Diagnóstico da trava.** Quando o quadro informado não tem escala legal, a tela explica o
motivo pela conta mais simples que se aplica, nesta ordem: **horas** (demanda do período
acima de 42 h/semana × equipe); **alternância** do plantão de 12 h (dois dias seguidos somam
mais plantões que a equipe, com o par de dias); **categoria** (horas ou plantões de posto de
enfermeiro acima do que os enfermeiros cobrem); **dia específico** (numa data, descontadas as
férias, sobram menos pessoas que postos); **combinação de regras** (nenhuma conta explica; o
solver provou). Em todos, quantos faltam e o menor quadro viável. Implementado em
`ferramenta.diagnosticar`, só contas, sem solver. Na busca do menor quadro, cada tamanho é
tentado com a composição da regra e, se inviável, com todos os acréscimos como enfermeiros —
enfermeiro cobre tudo o que técnico cobre, então se essa também falha, nenhuma composição
daquele tamanho fecha. *Conferido:* um caso por motivo, com o motivo registrado antes de
rodar; os cinco acertaram, e o 39 do Experimento A cai em alternância.

**Funcionalidades congeladas em 10/10.** **A Etapa 4 (P1, curva de escalabilidade com
objetivo não trivial) passa para depois da Etapa 7.**

*Nota de 02/10 — carga mínima, verificação sem mudança no código.* No caminho de turnos
configurados, o contrato tem **MinNumAssignments desligada** (valor 0, peso 0): nenhuma carga
mínima, nem rígida nem penalizada. **MaxNumAssignments ligada**, valor 14 turnos = 168 h ÷
12 h (o turno mais curto do modelo), rígida por `RIGIDAS_LEGAIS_BR`; o teto que vale é o de
**horas**, 168 h no horizonte (`carga_maxima_h`), também rígido. O mínimo, se existisse,
seria contado em turnos, que é o que o formato do INRC sabe contar. Medido no 12×36
equivalente ao Experimento A, 40 profissionais (14 + 26), objetivo completo (pesos + etapa
de equilíbrio), appsi_highs: **menor carga 120 h, maior 168 h**, com e sem os 20 pedidos de
folga do teste 7.2. Sem pedidos, 22 pessoas ficam em 168 h e 7 em 120 h; média 153,6 h
(512 plantões × 12 h ÷ 40). A etapa de equilíbrio não iguala horas: ela minimiza a
penalidade individual máxima, e horas não são penalidade. Uma diferença de 48 h no mês
entre colegas do mesmo regime é o que pede decisão (carga mínima, ou equilíbrio de horas)
— ver `ESTADO_ATUAL.md`, seção 5.

*Nota de 02/10 — o limite de tempo nunca chegava ao HiGHS.* Pelo appsi, o
`LegacySolverInterface.solve` refaz `config.time_limit` a partir do argumento `timelimit`
da chamada, que tem padrão vazio; o limite que `modelo.resolver` gravava antes da chamada
era apagado. É a mesma armadilha já registrada no código para o `load_solution`. Corrigido
passando o limite na chamada; conferido no log do HiGHS ("Time limit reached" em 20,03 s com
limite de 20 s); regressão OK. **Os números registrados não mudam**: todas as resoluções
até aqui terminaram com resposta provada — a maior da curva de escalabilidade antiga levou
549 s, abaixo dos 900 s que se supunha valerem. O que muda é o comportamento: a tela agora
para em 600 s por resolução, em vez de poder rodar sem fim. Achado ao preparar a P1: o teste
rápido com "60 s por etapa" passou de 800 s de CPU.

*Nota de 02/10 — o que a tela diz quando o tempo esgota (decisão do Otávio).* Três desfechos
distintos: **(a)** ótimo provado → "Escala gerada."; **(b)** escala encontrada sem prova →
"Escala gerada; pode haver uma melhor", com o gap da etapa 1; **(c)** tempo esgotado sem
escala → "Não foi possível gerar a escala no tempo disponível." **Nunca "faltam N" em (c)**:
o diagnóstico de falta só aparece com prova de inviabilidade, pela conta ou pelo solver. Se
o quadro informado foi provado curto e o seguinte esgotou o tempo, a tela mostra o
diagnóstico do informado (provado) e diz que o menor quadro viável não foi determinado. Na
situação (b) a etapa 2 não roda (só roda sobre ótimo provado). *Defeito achado ao montar o
teste de (b):* parado no limite de tempo **com** escala, o appsi devolve `maxTimeLimit`, e
`experimento_a.classificar` só reconhecia "optimal" ou "feasible" — classificava como não
decidido e descartava uma escala legal. Corrigido com `modelo.tem_solucao`, que lê o valor
da melhor solução e não o nome do estado. Não afeta nenhum número registrado, porque até
02/10 o limite nunca chegava ao solver e toda resolução terminava com prova. *Testes*
(`src/testes_ferramenta.py`, 8a–8d, esperado registrado antes): os quatro acertaram. Os casos
(b) e (c) dependem da máquina — escolhidos por sondagem no log do HiGHS (no 40 com 20
pedidos, primeira escala aos ~17 s com gap 1,03%, prova aos ~43 s), limites de 25 s e 3 s.

*Nota de 02/10 — a etapa 2 passa a equilibrar HORAS (decisão do Otávio).* Com a penalidade
da etapa 1 fixada no ótimo, a etapa 2 minimiza a **amplitude de carga**: maior carga do
período menos a menor, em horas, sobre todos os profissionais (`ferramenta.preparar_equilibrio`).
A distribuição dos pedidos negados continua informada na tela (quantos, em quantas pessoas,
no máximo quantos por pessoa), mas não é otimizada. **O mecanismo é o do Experimento B** —
fixar o ótimo, otimizar um segundo critério — e o Experimento B continua válido como
demonstração; muda o critério que a ferramenta otimiza. A etapa 2 agora roda também com
penalidade zero, porque a carga pode estar desequilibrada sem pedido negado. *Medido no caso
de 40 profissionais (12×36, 14 + 26, 20 pedidos):* amplitude **72 h na escala da etapa 1 →
48 h**, com otimalidade provada; carga de 120 h a 168 h; 20 de 20 pedidos atendidos. A
amplitude de 48 h é **a menor possível com a penalidade da etapa 1 fixada**, e a conta mostra
por quê: fixado o ótimo, ficam fixos os 96 turnos de enfermeiro em posto de técnico. Os
enfermeiros fazem então 56 + 96 = 152 plantões, 10,86 por pessoa — ao menos um fica com 10
ou menos (120 h). Os técnicos fazem 456 − 96 = 360, mais que 26 × 13 = 338 — ao menos um
fica com 14 (168 h). Logo amplitude ≥ 48 h, e o solver a atinge. A diferença de 48 h da nota
anterior não era acaso da etapa 1: é consequência do objetivo (técnico em posto de técnico
antes de enfermeiro), e equilibrar horas não a remove.
*Afirmação fraca:* etapa 1 em 35,9 s e etapa 2 em 37,5 s de relógio (appsi_highs, Intel
i5-10210U, Windows 11). Questão aberta sobre quem tem férias: ver P4 do `PROPOSTAS.md`.

---

## 2026-10-02 — Carga por contrato

**Status: vigente**

Decidido pelo Otávio no projeto de redação, para o caminho de turnos configurados (a
ferramenta). Implementado em 02–03/10.

**a) Carga contratual por profissional.** Cada profissional tem carga contratual semanal de
30, 36, 40 ou 44 h, informada na tela de equipe. Padrão 44 h, o limite da Constituição
(art. 7º, XIII). `instancia_br.CARGA_CONTRATUAL_PADRAO`, `Instancia.carga_semanal_h`.

**b) O teto vale sobre o horizonte, não por semana**: carga × 4 semanas. O 12×36 tem semanas
de 48 h compensadas por semanas de 36 h (CLT, art. 59-A); um teto semanal o tornaria ilegal.
*Como estava antes (verificado em 02/10):* o teto já era sobre o horizonte — uma restrição por
profissional, soma das horas nos 28 dias ≤ 168 h (42 × 4), igual para todos — mas não
descontava férias.

**c) A etapa 2 minimiza (maior − menor) da FRAÇÃO cumprida**: horas trabalhadas ÷ horas
devidas, com horas devidas = carga semanal × dias disponíveis ÷ 7. Quem tem 44 h e 14 dias
de férias deve 88 h, não 176 h. Resolve a P4 (amplitude distorcida por férias). Quem não tem
dia disponível no período fica fora da fração. Substitui a etapa 2 por horas da nota de 02/10
na entrada "Redesenho"; o mecanismo continua o do Experimento B.

**d) O teto também usa os dias disponíveis** — é a mesma conta das horas devidas,
`Instancia.horas_devidas`, que serve ao teto rígido (`modelo.py`), à conferência
(`solucao.conferir_rigidas`) e ao denominador da fração. Uma conta só, para os três não
divergirem.

**e) O painel do COFEN usa como CHS a média das cargas contratuais da equipe**, e a tela
mostra o valor usado (`instancia_br.chs`).

**f) O caminho por pacientes e o Experimento A ficam intactos**, com 42 h como hipótese
declarada. *Conferido:* 544 XML do caminho dos experimentos e do caminho por pacientes (5
graus × 2 regimes × 2 regras × efetivos 36–44 × 3 variações, mais 4 por pacientes) saem
idênticos byte a byte antes e depois (`docs/conferencia_xml_experimentos.py`). A comparação
foi posta à prova com um byte alterado numa cópia, e acusou. A conferência avulsa dos 361 XML
de 29/09 não ficou no repositório; esta a substitui.

**Argumento.** As 42 h do 12×36 decorrem da alternância — 14 plantões de 12 h em 28 dias são
168 h, ou 42 h por semana —, não de um teto. Fixar 42 h para todo contrato confunde
consequência do regime com regra. E o levantamento do projeto de redação aponta contratos
heterogêneos em só 30% dos estudos: tratar a carga como dado do contrato, e não como
constante, é o que o caso real pede.

**Consequências na ferramenta.** Quem a varredura do menor quadro acrescenta entra com 44 h.
O piso e o diagnóstico da trava passam a comparar as horas da demanda com a soma dos tetos
individuais (carga nos dias disponíveis), e dizem "faltam pelo menos k de 44 h".
`MaxNumAssignments` do XML fica com a maior carga no horizonte inteiro ÷ turno mais curto —
nunca mais apertado que as horas de ninguém (no modelo de 6 h: 29, antes 28).

**Testes** (`src/testes_ferramenta.py`, `casos_carga`, esperado registrado antes, 03/10):
- **9a, acertou:** em equipe mista 30/44 h, a maior carga entre os de 30 h foi 112 h (teto
  120 h) e entre os de 44 h, 168 h (teto 176 h); rígidas OK.
- **9b, acertou, com ressalva registrada antes de rodar:** no 12×36 com 44 h, ninguém passa
  de 14 plantões. Mas o teto de 176 h também para em 14 (15 plantões dariam 180 h), então o
  teste não separa alternância de teto.
- **9c, metade acertou:** quem tem 14 dias de férias ficou com 72 h de 88 h devidas,
  81,8%, dentro da faixa dos demais (63,6%–90,9%). Em horas, ficaria em 72 h contra 112–160 h.
- **9c, a outra metade falhou:** amplitude final de 27,3% contra ≤ 10 pp esperados. **O erro
  é do esperado**, e a conta mostra por quê. Com a penalidade da etapa 1 fixada em zero,
  enfermeiro não ocupa posto de técnico. Os enfermeiros cobrem exatamente o posto de
  enfermeiro (63,6% cada), e os técnicos não cabem abaixo de 90,9%; o mínimo é 27,3 pp, e o
  solver o provou.
- **9d, acertou:** o equilíbrio por fração reduziu a amplitude de 45,5% para 27,3%.

**Esperados antigos que a carga de 44 h desatualizou (03/10, não corrigidos — parado por
regra).** O caso 5 da tela e o 7.1 esperavam ≥ 35 turnos de enfermeiro em posto de técnico,
"mínimo aritmético" calculado com 42 h: 5 técnicos × 168 h = 840 h para 1.120 h de posto. Com
o padrão de 44 h, os técnicos dão 5 × 176 = 880 h, faltam 240 h = **30 turnos**, e o solver deu
exatamente 30 — o caso 5 falha (≥ 35), o 7.1 passa (sua condição é ≤ 35), mas o texto dele
ainda diz "mínimo aritmético 35". Ambos precisam do esperado refeito com 44 h.

**Suíte de 03/10:** `regressao.py --todos` OK (os 4 ótimos da Tabela 6); `testes_entrada.py`
completo OK; testes da tela: casos 1–4 OK, caso 5 FALHA (acima), 7.1 OK; a suíte foi
interrompida pelo sistema por falta de memória durante o 7.2 — 7.2, 7.3 e 8a–8d **não
rodaram** depois da carga por contrato. Os testes 9a–9d rodaram à parte (acima).

**O que a falha do 9c revela: decisão em aberto, P6 do `PROPOSTAS.md`.** Com enfermeiros
dedicados ao posto de enfermeiro, a amplitude da fração fica presa à razão entre posto de
enfermeiro e posto de técnico, não às férias. A P1 não foi relançada: o bloco parou aqui por
regra.

**g) Adendo de 03/10 — a etapa 2 equilibra DENTRO de cada categoria (P6 decidida pelo
Otávio).** Substitui o critério do item c) quanto ao alcance: a etapa 2, com a etapa 1 fixada
no ótimo, minimiza (maior − menor fração entre enfermeiros) + (maior − menor fração entre
técnicos). A fração continua a do item c). A diferença ENTRE categorias não é otimizada: vem
da demanda de cada posto frente ao tamanho de cada categoria, e a tela e a planilha a mostram
à parte (fração média dos técnicos − fração média dos enfermeiros, em pontos percentuais).
`ferramenta.preparar_equilibrio`, `ferramenta.por_categoria`. Motivo: a amplitude da equipe
inteira media a razão entre os postos, não a justiça entre colegas que fazem o mesmo trabalho
(P6).

**h) Indicador novo, sem mudança no modelo: horas de contrato não utilizadas por
categoria** = horas contratadas nos dias disponíveis − horas escaladas. Na tela (uma linha por
categoria, com a faixa da fração) e na planilha (aba Resumo).

**Esperados corrigidos ou novos (03/10).**
- **9c**, refeito pelo critério por categoria, com a conta registrada ANTES de rodar (commit
  `08603c6`): enfermeiros cobrem 672 h ÷ 6 = 112 h cada, amplitude 0; técnicos cobrem
  1.792 h, e como 23x = 224 não tem inteiro, a amplitude mínima é 1/22 = 4,55 pp, atingida só
  com Téc 1 em 10 turnos (90,9%). **Acertou em tudo:** enfermeiros 0, técnicos 4,55 pp,
  provado; Téc 1 em 90,9%, dentro da faixa dos técnicos (86,4%–90,9%); horas não utilizadas
  384 h (enfermeiros) e 232 h (técnicos); diferença entre categorias +24,9 pp, como na conta.
- **9d:** o critério caiu de 36,4 pp na escala da etapa 1 para 4,5 pp, provado.
- **Caso 5 da tela:** esperado refeito para ≥ 30, pela conta com o padrão de 44 h (5 × 176 =
  880 h para 1.120 h de posto de técnico, faltam 240 h = 30 turnos). **Corrigido depois de ver o
  resultado (30)** — admitido por ser aritmético e independente do solver. O texto do 7.1
  também passou a dizer "mínimo aritmético 30"; a condição do 7.1 (≤ 40) não mudou. Ambos
  deram 30.
- **9b-sem-teto**, variante nova, esperado registrado antes: desligados o teto de horas E o
  `MaxNumAssignments` (que no 12×36 é floor(176/12) = 14 e é rígido — desligar só o teto de
  horas deixaria esse limite parando em 14), maximizou-se o número de plantões de Téc 1.
  **Deu 14, provado ótimo.** Quem limita é a alternância (regra das 36 h), não o teto.

**Suíte completa de 03/10, depois do adendo (um teste por processo, por memória):** tela 1–5,
7.1, 7.2, 7.3, 8a–8d, 9a–9d e 9b-sem-teto OK; `regressao.py --todos` OK (56, 58, 197, 219 =
Tabela 6); `testes_entrada.py` OK; 544 XML idênticos byte a byte ao commit `cec3d8e`.
Observação, não resultado: no 7.2 (40 profissionais, 20 pedidos) a etapa 2 por categoria
parou no limite de 600 s sem provar (amplitude 34,1 → 13,6 pp); no 9c provou em 111 s.
Máquina: i5-10210U, 12 GB, Windows 11, HiGHS 1.15.1 via appsi.

**i) Adendo de 05/10 — limite e exibição da etapa 2 (decisão do Otávio).**
- **Limite da etapa 2 na tela: 180 s** = max(120 s; 1,5 × 81,1 s), arredondado para cima ao
  minuto; 81,1 s é o tempo em que a etapa 2 do caso de 88 profissionais da rodada com folga
  chegou a 90% da redução final (`PROPOSTAS.md`, P1). A etapa 1 continua com 600 s. A etapa 2
  usa o menor dos dois limites (os testes encurtam o da etapa 1). `ferramenta.TEMPO_ETAPA2`.
- **A etapa 2 não mostra gap.** Na tela e na planilha mostra a **diferença máxima de carga
  entre colegas dentro de cada categoria**, em plantões e em horas ("1 plantão (12 h)"). O gap
  continua só para a etapa 1.
- **Definição (decisão de implementação, não óbvia):** o desvio de cada profissional em relação à
  sua parte justa — horas trabalhadas − (fração média da categoria × suas horas devidas) —,
  maior menos menor. Com contrato e disponibilidade iguais, é a diferença de horas entre quem
  mais e quem menos trabalhou. Com férias ou contratos diferentes, não pune quem deve menos
  horas (o mesmo cuidado da P4). Em plantões só quando todos os turnos têm a mesma duração;
  senão, só horas. `ferramenta.por_categoria`, `ferramenta.fmt_diferenca`. No 9c, esperado
  registrado antes: técnicos "1 plantão (8 h)", enfermeiros "nenhuma (0 h)".
- **Adendo de 05/10 ao item i — o teste 9c não exige prova (decisão do Otávio).** A prova de
  ótimo da etapa 2 dentro dos 180 s depende da carga da máquina: 146,9 s rodando sozinho;
  falhou em 05/10 com outro processo rodando junto. O 9c passa a conferir que a amplitude
  atingiu o piso da conta registrado no commit `08603c6` (enfermeiros 0, técnicos 4,55 pp;
  tela "nenhuma (0 h)" e "1 plantão (8 h)"), sem exigir prova. Teste novo, 9c-tela: com a
  etapa 2 encurtada para 20 s, para que termine sem prova, nem a tela nem a planilha podem
  dizer "provado".

---

## 2026-10-05 — Arquivo de configuração vira trabalho futuro

**Status: vigente**

Decidido pelo Otávio em 05/10. O arquivo de configuração — o pacote com o XML no formato INRC
mais um complemento com o que o formato não representa, para baixar e carregar na tela —
**sai do TCC e vira trabalho futuro** (`PROPOSTAS.md`, P3). Não será implementado.

**Altera** a adição "arquivo de configuração no formato INRC" da especificação de 29/09
(entrada "2026-09-29 — Especificação da ferramenta", em Configuração; e "Arquivo de
configuração = pacote", em "Ajustes da Etapa 2"). A especificação já o marcava como de menor
prioridade, a virar trabalho futuro se não estivesse pronto em 10/10.

**Motivo.** O congelamento das funcionalidades é em 10/10, e a demonstração de uso tem
prioridade. A reprodutibilidade dos resultados do TCC não depende do arquivo: está no
repositório e nos scripts (`src/regressao.py`, `src/escalabilidade_objetivo.py`,
`src/figuras_tcc.py`, `docs/demonstracao/`).

**Código parcial (verificado em 05/10):** nenhum. Não há código do pacote nem do
complemento. O que existe e continua é anterior e serve aos experimentos e à validação:
`instancia_br.escrever_xml` (escreve a instância no formato INRC, para o avaliador oficial) e
`src/parser.py` (lê as instâncias do INRC).

---

## 2026-10-05 — Diagnóstico da trava: teto pela alternância e férias no par

**Status: vigente**

Decidido pelo Otávio em 05/10 (fecha a P7). **Correção do diagnóstico da trava**
(`ferramenta.diagnosticar`); o modelo e o objetivo não mudam. O diagnóstico só afirma
condições NECESSÁRIAS: cada motivo que ele mostra é uma conta que, sozinha, prova que não há
escala.

**a) Teto de cada pessoa** (`ferramenta.teto_horas`) = o menor entre a carga contratual nos dias
disponíveis e, quando ninguém pode trabalhar dois dias seguidos (12×36), a duração do turno
mais longo × a soma, por bloco de dias disponíveis seguidos, de ceil(tamanho / 2). É limite
superior válido: num bloco de b dias sem dois seguidos cabem no máximo ceil(b / 2) plantões.
Com 44 h e o horizonte inteiro no 12×36: 168 h (14 plantões), não 176 h.

**b) Duas condições por categoria**, com o enfermeiro podendo cobrir posto de técnico:
- *horas*: primeiro os enfermeiros (horas do posto de enfermeiro contra os tetos deles — se
  falta, motivo "Categoria"); depois os técnicos (horas do posto de técnico contra os tetos dos
  técnicos mais a folga dos enfermeiros — se falta, motivo "Horas");
- *par de dias seguidos no 12×36*: os plantões do par contra as pessoas disponíveis em pelo
  menos um dos dois dias, descontando férias e licenças (motivo "Alternância"); e o mesmo só
  para enfermeiros e posto de enfermeiro (motivo "Categoria"), quando o par geral não dispara.

O diagnóstico mostra **todos** os motivos que disparam, cada um com os números; o título junta
os nomes. A ordem: horas, par, dia específico; "combinação de regras" só quando nenhum dispara.

**Esperado registrado antes de rodar** (`src/testes_ferramenta.py`, 7.3 e 7.4): na clínica da
demonstração com 20 técnicos, "Horas" (324 h contra 312 h) e "Alternância" (ter 03/11 e qua
04/11: 28 plantões, 27 pessoas); com 21, nenhum; o caso "combinação" do 7.3 passa a "Categoria"
(672 h contra 667,4 h) e "Alternância" (sáb 09 e dom 10/01, 4 plantões para 3 pessoas) — motivo
mais específico e verdadeiro; os outros quatro mantêm o motivo.

**Fica igual:** `ferramenta.piso` (que decide se um quadro vai ao solver) continua com a conta
antiga; trocá-la mudaria quais quadros o solver tenta. Não pedido.

---

## 2026-10-05 — Grau da proporção: o grupo de pacientes de maior carga

**Status: vigente.** Decidido pelo Otávio em 05/10. **Corrige a leitura** da regra de graus
misturados da entrada "2026-09-29 — Ajustes da Etapa 2" ("vale o maior percentual de
enfermeiros entre os graus presentes").

**O que o Parecer diz** (Parecer Normativo nº 1/2024/COFEN, seção 3, distribuição
percentual; conferido no PDF oficial em 05/10,
<https://www.cofen.gov.br/wp-content/uploads/2024/03/Parecer-Normativo-1-2024.pdf>):

> "Quando houver diferentes tipos de cuidados em pacientes em um mesmo setor, a distribuição
> de profissionais por categoria deverá seguir o tipo de cuidado, cujo grupo de pacientes
> apresentar a maior carga de trabalho para assistência de Enfermagem."

Os dois exercícios resolvidos com dependência plena (Anexo II, Saúde Mental e Psiquiatria)
seguem o grupo de maior carga, e não o grau mais grave presente:

- Exercício 1: 70 de dependência discreta, 25 intermediária, 15 plena, taxa de ocupação 75%
  (52,5; 18,75; 11,25). "A carga de trabalho de maior prevalência é dependência discreta,
  portanto: 33% Enfermeiros". Carga por grupo: 52,5 × 4 = 210 h; 18,75 × 6 = 112,5 h;
  11,25 × 10 = 112,5 h.
- Exercício 2: 12 discreta, 5 intermediária, 3 plena, ocupação 100%. Mesma frase, 33%. Carga:
  48 h, 30 h, 30 h.

O exercício de clínica médica do mesmo Anexo também fecha com essa leitura: mínimos 16 × 4 =
64 h, intermediários 8 × 6 = 48 h, alta 5,6 × 10 = 56 h, semi 2,4 × 10 = 24 h. O Parecer usa
"Prevalência Cuidados Mínimos, portanto, 33%".

**Na ferramenta:**
- Com pacientes por grau informados na tela, o alerta de proporção usa o grau do grupo de
  maior carga total (pacientes × horas por paciente em 24 h) e diz qual grau usou e por quê
  (`instancia_br.grau_do_alerta`).
- O campo "Grau de dependência predominante" só vale sem pacientes informados.
- **Empate** entre grupos: a regra não está decidida (P8). A ferramenta não escolhe em
  silêncio: o alerta diz que houve empate e nomeia os graus. Conta, enquanto isso, com o maior
  percentual dos empatados, e diz isso.

**O que NÃO muda:** o modelo. `instancia_br.grau_de_maior_carga`, a leitura de 29/09, continua
no caminho por pacientes de `instancia_br.construir`, que monta instâncias (e entra nos 544 XML
da conferência). Trocá-la mudaria o modelo desse caminho. Fica como divergência declarada entre
o caminho por pacientes (experimentos) e o alerta da tela.

**Esperado registrado antes de rodar** (`src/testes_ferramenta.py`, caso 4b): na clínica da
demonstração, 32 h, 84 h e 40 h → intermediário, 33%.

**A divergência não afeta resultado** (verificado em 05/10, sem alterar nada). As únicas
instâncias do caminho por pacientes são as 4 da conferência dos XML
(`docs/conferencia_xml_experimentos.py`): 8 h e 12×36, com e sem razão de fim de semana, todas
com 10 pacientes de cuidado mínimo e 12 intermediários — graus misturados. Nas 4, as duas
leituras dão o mesmo grau, intermediário (pela de 29/09, empate de 33% resolvido pela ordem da
tabela; pela de 05/10, 72 h contra 40 h), e o mesmo percentual, 33%. E nenhum número que vai ao
texto vem desse caminho: o Experimento A monta cada instância com um grau só
(`experimento_a.py`), a escalabilidade com o intermediário (`escalabilidade.py`), a P1 e a
demonstração pelo caminho de turnos configurados, e as tabelas e figuras de
`resultados/figuras/` saem dos CSVs da P1.

---

## 2026-10-05 — Empate de carga entre grupos de pacientes (fecha a P8)

**Status: vigente.** Decidido pelo Otávio em 05/10. Mantém o comportamento que já estava no
código: quando dois ou mais grupos de pacientes têm a mesma carga, o alerta de proporção avisa
o empate, nomeia os graus e usa o **maior percentual** entre os empatados
(`instancia_br.grau_do_alerta`). É **escolha da ferramenta, conservadora** — não regra do
Parecer, que não trata empate. Sem mudança de código. Teste: `src/testes_ferramenta.py`, 4e.

---

## 2026-10-05 — Congelamento das funcionalidades antecipado para 05/10

**Status: vigente.** Decidido pelo Otávio em 05/10. O congelamento das funcionalidades passa
de 10/10 para **05/10**. De 05/10 a 10/10 só entra **correção de defeito**, com o esperado
registrado antes de rodar. Nenhuma função nova. O congelamento de resultado numérico
continua em 14/10 e a entrega em 04/11.

---

## 2026-10-06 — Notas de 22 e 23/09 ficam em docs/ como metodologia ativa

**Status: vigente.** Decidido pelo Otávio em 06/10. As quatro notas
`docs/nota_conferencias_contrato_2026-09-22.md`, `docs/nota_intervalo_individual_2026-09-22.md`,
`docs/nota_piso_forcado_2026-09-22.md` e `docs/para_orientacao_2026-09-23.md` **ficam em
`docs/`** como metodologia ativa, e não vão para `historico/`: cada uma tem achados citáveis que
só existem nela (lista no `resultados/relatorio_2026-10-06a.md`, item 2). Fecha a dívida do
`ESTADO_ATUAL.md`.

---

## 2026-10-06 — Padrão das 36 h fica no XML (opção (a) da P13)

**Status: vigente.** Decidido pelo Otávio em 06/10. **Decisão registrada em 06/10 sobre um
comportamento que o código já aplicava antes de 23/09:** os padrões `clt_36h_*` continuam
escritos no XML das instâncias brasileiras (`instancia_br._padroes_de`, que gera os padrões, e
`instancia_br.escrever_xml`, que os escreve em `<Patterns>` e no `<UnwantedPatterns>` do
contrato) — a opção (a) da P13. No modelo, os mesmos pares continuam rígidos.

**Motivo.** A opção (b), tirar os padrões do XML, alteraria os 544 XML da conferência e
exigiria refazer os experimentos. E nas instâncias brasileiras a regra das 36 h não depende do
avaliador oficial: é conferida por **medição direta do descanso** na escala
(`docs/conferencia_descanso_escala.py`), porque o avaliador lê o padrão como (noturno, folga,
folga) e cobra violações que não existem (P13; `ESTADO_ATUAL.md`, achado metodológico).

Fecha a P13 (`historico/escopo-comparacao-regimes/PROPOSTAS.md`).

---

## 2026-10-06 — Correção de defeito: `src/validar.py` não conseguia chamar o avaliador

**Status: vigente.** Correção de defeito, permitida pelo congelamento das funcionalidades.

**O defeito, presente desde a criação do arquivo** (commit `603d1f7`, 15/09; nenhuma linha
mudou depois):
- o classpath tinha só `avaliador/evaluator.jar`, sem as dependências (dom4j, jaxen,
  jaxb-api): o Java falha com `NoClassDefFoundError` (linha 56);
- a chamada resumida passava `-p` **depois** dos arquivos (linha 94): o avaliador responde
  "Syntax error", como o próprio README avisa desde 15/09;
- a penalidade é lida só da chamada resumida; quebrada, ela sai `None` ("não interpretado"), e
  o script acusa divergência.

Achado em 06/10, ao rodar o `medium_late05` (`resultados/relatorio_2026-10-06b.md`). Caminho
absoluto com contrabarra também é recusado pelo avaliador ("Invalid file path"); com barra
normal, funciona.

**Nenhum resultado registrado passou por ele** (verificado em 06/10). O `validar.py` nunca
podia devolver um número do avaliador. Os scripts que gravam conferências chamam o Java
direto, do jeito certo (`java -cp "avaliador/*"`): `experimento_a.py`,
`docs/conferencia_piso_forcado.py` e `docs/conferencia_padrao_avaliador.py`. Nenhum script
importa o `validar.py`. A coluna `avaliador_oficial` do `resultados/consolidado.csv` (18/09)
não tem origem documentada, mas o `validar.py` não teria como produzir aqueles números (56,
58, 197, 219).

**Correção** (como no README): classpath `avaliador/*`; `-p` antes dos arquivos; caminhos
passados com barra normal.

**Esperado registrado ANTES de rodar** (06/10): o `validar.py` dá 56, 58, 197 e 219 nas escalas
ótimas da regressão (`resultados/sprint01_completo.xml`, `sprint02_completo.xml`,
`long01_completo.xml`, `long02_completo.xml`, de 22/09) e 224 na escala do `medium_late05`
(`resultados/medium_late05_2026-10-06/medium_late05_escala.xml`), com "os dois valores batem"
em cada uma.

**Resultado (06/10, depois da correção, uma conferência por processo):** 56, 58, 197, 219 e
224, "os dois valores batem" nas cinco — igual ao esperado. A do `medium_late05` foi chamada
com caminho absoluto e contrabarra, de propósito, para pôr à prova a troca para barra normal.

---

## 2026-10-06 — Cronograma: semana de testes e congelamento dos números em 16/10

**Status: vigente.** Decidido pelo Otávio em 06/10.

- **E1. O congelamento dos números passa de 14/10 para 16/10**, para acomodar a semana de
  testes. Motivo: uma correção de defeito achado na bateria pode mudar a demonstração.
- **E2. Ordem do trabalho:**
  1. semana de testes, de 08 a 12/10: diagnóstico e bateria de entradas variadas;
  2. fechamento técnico até 16/10: suíte, demonstração refeita se preciso, `v1.1`;
  3. texto do TCC, de 13 a 25/10;
  4. melhoria de tela e textos de ajuda, de 26 a 29/10, enquanto o rascunho está com o
     orientador — sem mudar comportamento nem número, com as capturas finais refeitas no fim.
- **E3. Até 16/10, só correção de defeito**, com esperado registrado antes.

Altera a data de 14/10 do `ESTADO_ATUAL.md` (seção 2) e da entrada "2026-10-05 —
Congelamento das funcionalidades antecipado para 05/10", que mantinha 14/10.

---

## 2026-10-07 — Bateria de entradas começa em 07/10, antes de fechar a parte A

**Status: vigente.** Decidido pelo Otávio em 07/10.

A bateria (`docs/bateria_entradas.md`), que só rodaria depois de resolvida a parte A do
diagnóstico, começa já em 07/10, pelo nível 1 e pelos casos conhecidos (K1–K6), por script
(`docs/diagnostico/bateria_rodar.py`), sem navegador.

Por quê: duas tentativas do Otávio pela tela terminaram sem resultado. A segunda foi queda de
conexão do navegador (`ConnectionResetError` 10054 no console do Streamlit, sem "[ERRO]" e
sem queda do processo). Rodar por script tira a conexão do caminho e grava tempos por caso.

A parte A continua aberta (console e captura do caso 15 + 5). O esperado de cada caso é o da
conta independente, registrado antes no commit `62bbf4d`; a tradução de cada caso para a
`Entrada` foi declarada no cabeçalho do script antes de rodar.

---

## 2026-10-08 — Bateria: K3/K4 longos não rodam de novo; nível 3 estratificado

**Status: vigente.** Decidido pelo Otávio em 08/10.

- **K3 e K4 com 3.600 s não rodam de novo.** O K4 com ~1.909 s foi interrompido por falta de
  memória (`resultados/relatorio_2026-10-08a.md`). Em 08/10 a escala com 17 do K4 foi
  confirmada por outro caminho: a escala achada para K3 + 1 técnico (11 + 6), fixada no modelo
  do K4 (12 + 5), passa em todas as conferências e o modelo a aceita (`k4_dominancia.py`).
  Registro: **a escala com 17 existe; o solver nem sempre a acha em 600 s (variação de
  desempenho na fronteira)**. O K3 (16) fica não determinado. **Vai para as limitações:**
  casos de fronteira podem não ser decididos no tempo e na memória disponíveis.
- **Nível 3 resorteado antes de rodar, estratificado pela conta:** 40 casos de folga clara,
  30 de fronteira e 30 inviáveis (semente 20261008). O sorteio de 07/10 (semente 81026) fica
  registrado como **descartado antes de rodar**: 78 de 100 casos nasciam inviáveis pela conta,
  e a propriedade 5 (folga clara) valeria em só 17. Só etapa 1, 600 s por resolução, no
  máximo 15 min por caso; esgotado, o caso é "não determinado" e o lote segue.

---

## 2026-10-08 — Demonstração: feriado de 20/11 digitado em 24/11 (defeito do roteiro, corrigido)

**Status: vigente.** Correção de defeito antes do congelamento dos números (16/10),
autorizada pelo Otávio em 08/10.

**O defeito.** O roteiro que digita a demonstração na tela (`docs/demonstracao/capturas.py`)
colava a demanda de feriado na grade "Demanda específica por data" clicando na **primeira linha
visível** e descendo `k` linhas com a seta. Depois da colagem do 15/11, a grade ficava rolada:
a primeira linha visível já não era a do 02/11, e a do **20/11 caiu em ter 24/11**. Aconteceu
nas três rodadas de 05/10 e de novo nas de 08/10 (manhã). O 02/11 e o 15/11 entraram certos.
A ferramenta cobriu exatamente o que recebeu; o erro foi da entrada.

**Como foi achado.** Por um conferidor **independente da entrada**
(`docs/demonstracao/conferir_planilhas.py`, 08/10): lê a planilha baixada, remonta a escala e
compara a cobertura, dia a dia, com a demanda **declarada** em `caso_clinica_medica.py` — não
com a que a tela recebeu.

**Por que as conferências de 05/10 não o pegaram.** Todas partiam da entrada que a tela
recebeu: a conferência de descanso, a cobertura do modelo e o texto da tela concordavam entre
si porque compartilhavam a mesma entrada errada. É o padrão do `CLAUDE.md`: "conferência que
compartilha premissa com o que confere não confere nada". A conta dos cortes
(`cortes_esperados.md`) usava os dados declarados, mas não olhava a planilha.

**Consequência.** Pela conta, as duas entradas têm as mesmas horas (4.308 h), o mesmo pior par
de dias (28, em 03–04/11), o mesmo piso e os mesmos motivos: vereditos, cortes e diagnóstico
não mudam. Os números que saem do solver (enfermeiro em posto de técnico acima do mínimo,
frações, horas não utilizadas, diferença entre colegas) vinham da entrada errada.

**Correção.** O roteiro acha a linha pela **data**: lê a data da linha selecionada, anda a
diferença de dias, confere que a linha é a da data antes de colar e confere os valores colados
nela. O conferidor roda no fim de cada rodada (`rodar_rodada.sh`), e a rodada falha se ele
falhar. Esperado registrado antes de refazer (`cortes_esperados.md`, seção de 08/10).

---

## 2026-10-08 — P12 aprovada: progresso na tela, escala da etapa 1 mostrada já, orçamento de 20 min por clique

**Status: vigente.** Aprovada pelo Otávio em 07/10; implementada em 08/10 como **correção de
usabilidade na semana de testes**: nenhuma regra, nenhum modelo e nenhum número muda.
`modelo.py` e `instancia_br.py` não são alterados.

**Por quê.** Na bateria de 07/10 (`resultados/relatorio_2026-10-07a.md`), em 19 de 20 casos
a escala ficou pronta em até 21 s e, em 15, a etapa 2 usou os 180 s inteiros: o usuário
esperava ~3 min com a escala pronta e a barra parada, sem sinal de progresso. Duas tentativas
do Otávio pela tela terminaram sem resultado, e a tela não dizia o que estava acontecendo.

**O que entra:**
- a escala da etapa 1 aparece assim que a etapa 1 termina, marcada como "escala pronta;
  equilibrando a carga entre colegas (até 3 min)"; quando a etapa 2 termina, a tela diz qual
  escala vale; a planilha é sempre a escala da tela;
- durante o cálculo, a tela mostra a fase, o quadro em teste e o limite de tempo da fase;
- "o solver falhou" deixa de existir: tempo esgotado sem escala → "sem resposta em 10 min com
  N profissionais"; erro técnico → "erro técnico ao resolver; detalhes no console", com a
  exceção no console;
- orçamento total de **20 min por clique**: esgotado, a busca para e a tela mostra só o que
  foi provado; nunca "faltam N" sem prova.

**O que não entra:** o item adicional da P12 (tetos do diagnóstico no piso) — muda quais
quadros vão ao solver; fica para decisão depois.

**Condição:** a demonstração da clínica (20/19/18 técnicos) sai com os mesmos números,
vereditos e textos de diagnóstico; P05, P08 e K1 da bateria, com o mesmo veredito e o mesmo
menor quadro. Esperado registrado antes de implementar (`resultados/relatorio_2026-10-08b.md`).

**Defeito do teste 12a, corrigido com autorização do Otávio (08/10).** Na primeira suíte, o item
"grade da tela = grade da planilha" falhou. Causa: o teste lia `at.dataframe[0]`, que é a
tabela de **turnos** do formulário; a tela tem seis tabelas, e a escala é a única cujas colunas
começam por "Categoria" e "Turnos". A ferramenta estava certa: a grade da tela era idêntica à
da planilha, célula a célula. Correção: o teste acha a grade pela característica (colunas
Categoria e Turnos), exigindo **exatamente uma** — pega também uma grade provisória que não
tenha sido apagada —; o esperado não mudou. Teste do teste
(`docs/diagnostico/teste_do_teste_12a.py`, esperado commitado antes): com uma atribuição trocada
em memória, a conferência **falha**; com a escala real, **passa**.

---

## Modelo de entrada

```
## AAAA-MM-DD — Título curto da decisão

O que foi decidido, em uma ou duas frases.

Por quê. Se houver fonte, citar.

Ressalva ou consequência, se houver.
```
