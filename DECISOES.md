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

> **Superada em 13/10** ("2026-10-13 — Art. 67 com horários editáveis"). O argumento acima
> vale só para os horários dos modelos prontos: com turnos editados na tela, o pior caso
> noite → folga → manhã pode dar menos de 24 h (N 23–07, folga, M 05–13 = 22 h), e o modelo
> **não** garantia o art. 67. Desde 13/10 a garantia vem de uma regra explícita do gerador de
> pares proibidos, não dos horários. O texto acima fica como registro.

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
*Marca de revisão em 30/10/2026:* o critério de minimização muda de **soma das amplitudes por categoria** para **min-max (máxima das amplitudes)**. Ver "2026-10-30 — Etapa 2 por min-max (v1.4.5)".

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

## 2026-10-30 — Etapa 2 por min-max (v1.4.5)

**Status: vigente — MUDANÇA DE FORMULAÇÃO (só a etapa 2)**

Pedido do Prof. Ormeu em 30/10/2026; aprovado pelo Otávio em 30/10/2026; validado pela Orientação.

**Motivo:** a soma das amplitudes não controla como a amplitude se divide entre as categorias (13 + 1 empata com 7 + 7). O min-max força a escolha equilibrada: 7 + 7 é melhor que 13 + 1 ou 14 + 0, porque max(7, 7) = 7 < max(13, 1) = 13 e < max(14, 0) = 14. Referência: Guéret, Prins e Sevaux, *Applications of optimization with Xpress-MP*, seção 2.10.1, "Minimax objective functions".

**Mudança técnica:**
1. Adiciona variável real `t ≥ 0` no modelo da etapa 2.
2. Para cada categoria presente (enfermeiros, técnicos): `t ≥ φmax_g − φmin_g`.
3. Objetivo da etapa 2: `min t` (substitui `min Σ_g (φmax_g − φmin_g)`).
4. Sem critério de desempate: escalas com a mesma maior amplitude empatam — 7 + 0 e 7 + 7 valem 7 (limitação declarada).

**Onde a SOMA das amplitudes decide algo, passa a valer a MAIOR das duas:**
- Escolha entre a escala da etapa 1 e a da etapa 2 quando não há prova (P17): antes `amplitude_etapa2 < soma_etapa1`, agora `max_amplitude_etapa2 < max_amplitude_etapa1`.
- Estado que gera a frase do equilíbrio na tela: mesma mudança.
- As exibições **por categoria** (diferença entre colegas, horas não utilizadas, planilha) **não mudam**. O teste 9c, com min-max, confere a maior amplitude (4,55 pp dos técnicos), e a amplitude dos enfermeiros pode subir de 0 sem custo — não é exigido que fique em 0.

**Não muda:** etapa 1, restrições duras e suaves, divisão do tempo, conferência de descanso, diagnóstico, limite inferior do quadro, caminho do INRC (regressão), textos da tela fora da frase do equilíbrio.

**Suíte:** identidade v1.4.4 × v1.4.5 (XML e LP etapa 1 idênticos; LP etapa 2 diferente só no objetivo e linhas de `t`), regressão (56, 58, 197, 219 idênticos), testes de entrada, testes da ferramenta que passam pela etapa 2 (9, 9c, 9c-tela, 9d, p20, 8, 12, opB-*, pref-tela se existirem) e conferidores (p14, p17) se rodarem.

*Nota de 30/10/2026 (Otávio, com a Orientação), registrada antes de mudar a conferência:* o item 3
do `docs/diagnostico/p14_conferir.py` passa a ser **"a maior amplitude da fração cumprida (critério
da etapa 2) é ≤ a da escala da etapa 1"**. Antes era "diferença máxima de carga entre colegas, em
cada categoria, ≤ a da escala da etapa 1". Motivo: o min-max garante só a maior; a categoria
menor pode subir (limitação já declarada no item 4 acima), e nem a soma garantia o item 3 por
categoria. O p14 continua fora da suíte, porque os casos dependem do tempo; o caminho sem prova
fica coberto pelos testes 8 e 9c-tela.

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

**Status: superada em parte** pela entrada "2026-10-09 — Texto do TCC antecipado para 09/10" (registrada em 11/10): o texto começou em 09/10, não em 13/10, e a semana de testes terminou antes, em 09/10. O congelamento dos números em 16/10 e a janela de tela de 26 a 29/10 continuam. Decidido pelo Otávio em 06/10.

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

**Refeita em 09/10 (madrugada), com o Chrome fechado:** os três feriados colados e conferidos
nas linhas certas; conferidor OK nas três; vereditos, cortes, diagnóstico e mínimos iguais ao
esperado (`882edf1`). Todos os números da seção 9 do `NUMEROS_TCC.md` se confirmaram iguais;
as escalas mudaram (393 a 422 células), os agregados não — mesmas horas, e a contagem de
enfermeiro em posto de técnico já estava no mínimo aritmético. As fotos "equilibrando" desta
rodada saíram com o resultado final (o roteiro esperava a tela terminar antes de fotografar);
foram apagadas e o roteiro, corrigido, sem nova rodada.

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

## 2026-10-09 — P15: alerta de descanso semanal abaixo de 35 h

**Status: vigente.** Decidido pelo Otávio em 09/10. Fecha a P15 (`PROPOSTAS.md`).

**O que entra.** Quando o descanso semanal **medido** de algum profissional na escala gerada
ficar abaixo de 35 h, a tela mostra um **alerta**, com o número de profissionais afetados e a
referência à Súmula 110 do TST. **Não é regra rígida:** nada muda no modelo, na escala nem nos
números; a escala continua valendo.

**Fundamento.** Súmula 110 do TST (Res. 121/2003) e OJ 355 da SDI-1: as horas trabalhadas logo
depois do repouso semanal de 24 h com prejuízo do intervalo de 11 h entre jornadas são pagas
como extras (24 + 11 = 35 h). A súmula atribui **custo**, não proíbe — a mesma lógica do COFEN,
que também entra como alerta. Fonte de apoio: notícia do TRT-3 de 13/11/2015, "Intervalo de 35
horas entre as jornadas semanais deve ser respeitado em turnos de revezamento".

**A trava continua sendo a da lei:** 24 h de repouso semanal (art. 67), 11 h entre jornadas
(art. 66) e 36 h depois de plantão de 12 h (art. 59-A). A regra rígida de 35 h foi para
trabalhos futuros (P3).

**A medida** é a mesma do descanso semanal que a ferramenta já confere
(`conferencia_descanso_escala.descanso_semanal`): por semana, o maior descanso contínuo que
contém um dia sem turno, medido inteiro no relógio. O menor valor de cada profissional,
entre as semanas, é comparado com 35 h.

**Sem as bordas (decisão do Otávio, 09/10, antes de implementar).** O alerta não conta o
descanso que começa no início do horizonte nem o que chega ao fim: o que vem antes e depois não
é conhecido. Achado que motivou: no caso de teste do Otávio, o único descanso abaixo de 35 h
(Téc 5, 31 h) era o da borda inicial — de 00:00 do primeiro dia até o primeiro turno; no meio
do mês, o mínimo era 36 h. **A borda é a mesma limitação da continuidade entre períodos** (P3,
trabalhos futuros: receber os últimos dias do período anterior). A trava de 24 h (`medir`,
`cumpre`) continua com as bordas, como antes. O **indicador** "descanso semanal mínimo" da tela
e da planilha passou a seguir a regra do alerta (sem as bordas): nenhum teste nem número
registrado lê esse valor, e na demonstração ele não muda (36 h). Implementação:
`conferencia_descanso_escala.descanso_semanal(..., sem_bordas=True)` e `semanal_sem_bordas`;
`ferramenta.alertas_descanso`; teste 15 (`src/testes_ferramenta.py`).

---

## 2026-10-09 — P14: etapa 2 também quando a etapa 1 não prova o ótimo

**Status: vigente.** Decidido pelo Otávio em 09/10. Fecha a P14 (`PROPOSTAS.md`). Mudança de
comportamento da orquestração (`ferramenta.resolver_com_objetivo`); o modelo não muda.

**Antes.** Com a etapa 1 terminando com escala mas sem prova de ótimo, a etapa 2 não rodava, e
a escala saía sem equilíbrio de carga (no caso de teste do Otávio de 09/10: 51% a 92% do
contrato, sem equilíbrio). O motivo era o da entrada "Carga por contrato": fixar a penalidade
num valor que não é o ótimo mediria o equilíbrio de outra coisa.

**Agora.** A etapa 2 roda também nesse caso (até 180 s, limitada pelo orçamento do clique), com
a restrição de **não piorar** o valor achado pela etapa 1: penalidade da etapa 2 ≤ valor da
etapa 1 (no caso provado continua `=` ótimo, como antes). A tela diz que o equilíbrio foi feito
sobre uma escala sem prova de ótimo. O gap mostrado continua o da etapa 1 — se a etapa 2 achar
penalidade menor, ele passa a ser um limite folgado (a distância real é menor), e continua
verdadeiro como "distância máxima".

**Salvaguarda (registrada antes de implementar).** No caminho sem prova, se a etapa 2 devolver
escala com o critério de equilíbrio (soma das amplitudes da fração do contrato, por categoria)
**pior** que o da escala da etapa 1 — pode acontecer, porque ela também para no limite e o
HiGHS não parte da escala da etapa 1 —, fica a escala da etapa 1. O caminho provado não ganha a
salvaguarda, para não mudar a demonstração.

---

## 2026-10-09 — Encerramento da validação; próxima frente, o texto

**Status: vigente.** Decidido pelo Otávio em 09/10.

- **A semana de testes termina em 09/10.** Depois das partes A (P15) e B (P14) desta data, a
  versão citável do TCC passa a ser a **`v1.2`** (tag ao fim, com `git push --tags`). *Registro
  de 09/10, tarde: a tag ainda não foi criada — a suíte da parte B foi interrompida por falta de
  memória antes de terminar; ver `resultados/relatorio_2026-10-09b.md`.*
- **Até 16/10** (congelamento dos números, mantido), só entra correção de defeito, com esperado
  registrado antes.
- **Próxima frente: o texto do TCC.**
- Melhorias de tela para a janela de 26 a 29/10 (sem mudar comportamento nem número): lista na
  P16 (`PROPOSTAS.md`).

---

## 2026-10-09 — P17: a etapa 2 parte da escala da etapa 1 quando não há prova

**Status: vigente — implementada; testes pendentes** (rodam com a máquina limpa, antes da
demonstração e da tag `v1.2`; `resultados/relatorio_2026-10-09c.md`). Decisão condicional do
Otávio, 09/10: implementar se a interface com o solver permitisse de forma simples e
documentada. **Permite:** a opção `warmstart` do APPSI do Pyomo, que no HiGHS vira
`setSolution`; a sonda no P08 mostrou "MIP start solution is feasible".

**O que muda.** No caminho sem prova (P14), a etapa 2 recebe a escala da etapa 1 como solução
inicial. Não é heurística: é a solução exata que a etapa 1 achou, e ela cumpre "penalidade ≤
valor da etapa 1" por construção. Com isso a etapa 2 sempre tem escala, e o critério de
equilíbrio nunca piora. No caminho com prova, nada muda (a demonstração tem de sair idêntica).

**Onde.** `modelo.resolver(..., partida=False)` — só a chamada ao solver: com `partida=True`,
passa `warmstart=True`; o modelo (variáveis, restrições, objetivo) não muda, e com o padrão a
chamada é a de sempre. `ferramenta.equilibrar(..., partida=escala)` preenche os extremos da
fração (`f_max`, `f_min`), criados na etapa 2, com os valores da escala da etapa 1, para a
partida ser viável. A salvaguarda da P14 fica, redundante no critério.

**Por quê.** Achado da P14: sem partida, a etapa 2 sem prova entregou escala em 1 de 4 casos;
com "penalidade ≤ valor da etapa 1", achar a primeira escala era tão difícil quanto chegar
àquele valor. Warm start "só como partida" é admitido pelo `CLAUDE.md` (25/09).

**Condições do Otávio (09/10):** em `modelo.py`, só a chamada ao solver muda; a regressão dos 4
ótimos é obrigatória antes dos outros testes; o teste 8b e o conferidor só podem ser revisados
para conferir o comportamento novo, sem afrouxar esperado. O 8b foi apertado (passa a exigir
que a etapa 2 entregue escala), antes de a condição chegar; relatado no relatório 09c. **Decisão do Otávio (09/10): manter o 8b apertado; não reverter.**

---

## 2026-10-09 — Pedido por turno vira trabalho futuro

**Status: REVISTA em 19/10** por "2026-10-19 — Pedidos e regras por profissional" (o pedido por turno passa a ser implementado). Registro original: Decidido pelo Otávio em 09/10. Não implementar antes de 16/10.

**Motivo:** custo de ~1,5 dia; exige mudar um parâmetro de parada do solver (a tolerância
relativa do HiGHS, que com pesos em três níveis deixaria de garantir a prioridade estrita) e,
com isso, refazer a regressão; e a prioridade agora é o texto do TCC.

**Argumento para o texto:** o motor **já suporta** pedido por turno — o tipo `folga_turno`, que
é o `ShiftOffRequest` do INRC, validado pela regressão (as quatro instâncias têm 50 ou 245 desses
pedidos, e os ótimos publicados só batem com eles codificados certo). Faltam a entrada
brasileira, a tela e os pesos. Registrado em P3, "Preferências individuais"; análise e
estimativa em `resultados/relatorio_2026-10-09c.md`, parte B.

---

## 2026-10-09 — Condição das afirmações de ótimo provado: tolerância do HiGHS

**Status: vigente.** Decidido pelo Otávio em 09/10. Nada muda no código.

O HiGHS declara "ótimo" com gap relativo de até 0,01%. Como os objetivos da etapa 1 são
inteiros, a prova vale como ótimo inteiro quando 0,0001 × objetivo < 1 — o que vale em todos os
resultados registrados, exceto na P1 de 03/10 com N = 40, 60 e 80; nesses três, o log mostra
limite inferior igual ao objetivo (gap 0 exato). Registrado no `NUMEROS_TCC.md` como condição
das afirmações de ótimo; conferência em `resultados/relatorio_2026-10-09c.md`.

---

## 2026-10-10 — P17: etapa 2 sem melhora nos três casos difíceis; diagnóstico

**Status: FECHADA em 11/10 — sem defeito; limitação registrada** (decisão do Otávio, 11/10).
Registro anterior: em andamento (10/10). Os números entram no `NUMEROS_TCC.md`, seção 13.

**Conclusão.** O código não tem defeito: a etapa 2 carrega a melhor solução do HiGHS (a), e a
rodada do K5 (b) mostrou o HiGHS sem achar nada melhor que a partida em 180 s. **Limitação:** nos
casos sem prova, a etapa 2 não melhorou em nenhuma das 4 rodadas (Otávio, K5 e K6 em 09/10; K5 em
11/10). *Acréscimo de 11/10:* nem no teste 8b da tela (12×36, 40 pessoas, 20 pedidos, 25 s por
etapa), rodado para a v1.2.2. No K5 de 11/10, o limite inferior do critério ficou em ~0 o tempo todo (gap de 100% ao
fim). A diferença entre colegas é reportada só em horas: nesses casos há plantões de 6 h e de
12 h, e contar plantões não compara cargas. O texto da tela que dizia "com a carga equilibrada
entre colegas" mesmo sem melhora é o defeito do item c.

**O achado.** Na rodada da `v1.2` (`resultados/fechar_v12/p17_*.log`), nos três casos sem
prova (Otávio, K5, K6), os números da escala final são idênticos aos da etapa 1: mesmos
enfermeiros em posto de técnico, mesma fração mínima e máxima, mesma diferença entre colegas por
categoria. As escalas não foram gravadas: a recontagem independente não pôde ser feita. Pelo
`CLAUDE.md`, resultado idêntico é sinal de alarme. A conferência 3 da P17 ("diferença ≤ etapa
1") passa também se a etapa 2 só devolver a partida, então não distingue os dois casos.

**a) Leitura do código (10/10), sem defeito.** No caminho sem prova, a etapa 2 carrega a
**melhor solução que o HiGHS tem ao parar**, que é a partida só se nada melhor apareceu:
- `ferramenta.equilibrar` (`src/ferramenta.py`, l. 376–396) põe nos `f_max`/`f_min` os valores
  da escala da etapa 1 (as variáveis `x` já têm os dela) e chama `resolver(m, tempo,
  partida=True)`;
- `ferramenta.resolver` (l. 352–373) chama `modelo.resolver(..., carregar=False,
  partida=True)`, classifica e, se viável, `modelo.carregar_solucao(m, resultado)` e
  `modelo.atribuicoes(m)` (`x` > 0,5);
- `modelo.resolver` (`src/modelo.py`, l. 507–510 e 518–521) passa `warmstart=True` e
  `load_solutions=False`;
- no Pyomo (`pyomo/contrib/appsi/solvers/highs.py`): `_warm_start` (l. 226–244) entrega os
  valores atuais ao HiGHS com `setSolution`, antes de otimizar (l. 271–272); ao terminar,
  `_postsolve` lê `self._sol = highs.getSolution()` (l. 696), a solução incumbente do HiGHS
  depois da busca; `load_vars`/`get_primals` (l. 745–775) copiam essa solução para as
  variáveis.
- `modelo.carregar_solucao` (l. 538–555) chama `solution_loader.load_vars()`, isto é, a
  solução do HiGHS, não a partida.

Indício a favor: na sonda de 09/10 (P08, 20 s; `resultados/p17_2026-10-09/sonda_highs.log`), o
HiGHS aceitou a partida (0,2576) e a melhorou duas vezes (0,1061 e 0,0682). O código, portanto,
não prende a escala à partida. Nos três casos difíceis falta saber se o HiGHS de fato não
melhorou em 180 s.

**b) Rodada de diagnóstico, um caso (K5, 600 s + 180 s), autorizada.** Script:
`docs/diagnostico/p17_diagnostico_k5.py`. Grava a escala da etapa 1, a da etapa 2 e o log do
HiGHS da etapa 2, e reconta sem `ferramenta.indicadores` nem o modelo. **Esperado, registrado
e commitado antes de rodar:** se o log mostrar solução melhor que a partida, a escala final
difere da etapa 1 e o critério recontado dela é o melhor valor do log; se não mostrar melhora,
as escalas são idênticas célula a célula. Qualquer outro desfecho é defeito. Conferência a
mais: o critério recontado da escala da etapa 1 é o valor da partida aceita no log.

*Resultado (rodada em 11/10, ~00:42–00:55; a pasta tem a data em que o script e o esperado foram
commitados): **ESPERADO OK, desfecho SEM MELHORA.*** Arquivos em
`resultados/p17_diagnostico_2026-10-10/` (o nome fica, para não mudar a referência do commit
`d9c0677`).
- Etapa 1: penalidade 21, sem prova, gap 28,6% em 600 s (em 09/10 foram 21 e 33,3%; a etapa 1
  muda de rodada para rodada).
- HiGHS na etapa 2: partida aceita com valor **0,4091**; nenhuma solução melhor em 180 s
  (1.667 nós); fim com primal 0,4091, dual ~1,2e-14 e gap de 100%.
- **0 células diferentes** entre a escala da etapa 1 e a final.
- Recontagem a partir das escalas gravadas, sem `ferramenta.indicadores` nem o modelo, igual à
  ferramenta: enfermeiros 120–162 h (diferença de 42 h; 23,86 pp), técnicos 144–174 h (30 h;
  17,05 pp); critério 0,4091 = valor da partida no log.
- Teste curto do script antes da rodada (90 s + 20 s, `resultados/p17_diagnostico_teste/`):
  marcado como teste, veredito sem valor.

**c) Defeito de texto (depois de a e b).** Quando a etapa 2 não melhora o critério, a tela diz
"com a carga equilibrada entre colegas", o que é falso. Texto proposto pelo Otávio: "o equilíbrio
não encontrou escala melhor no tempo disponível; mantida a escala da etapa 1".

*Decisão do Otávio (11/10), com o texto final:* quando o critério final da etapa 2 **não** for
menor que o da etapa 1, a linha passa a ser "Escala desta tela: a da etapa 1. O equilíbrio de
carga não achou, no tempo disponível, escala mais equilibrada sem piorar o resultado da etapa
1."; quando for menor, fica a linha atual.

*Como será implementado (registrado antes):* **só no caminho sem prova**. Nele, quando o critério
final não for menor, a ferramenta passa a mostrar a escala da etapa 1 (até aqui só fazia isso
quando o critério piorava, pela salvaguarda da P14). Assim "a da etapa 1" é literalmente
verdade, mesmo no caso, não observado, de o HiGHS trocar a partida por outra escala de mesmo
critério. `etapa2` continua "ok", porque a etapa 2 entregou escala. **O caminho com prova não
muda.** Nele a etapa 2 não parte da escala da etapa 1 e pode devolver outra escala de mesmo
critério; dizer "a da etapa 1" ali seria falso, e trocar a escala mudaria a demonstração. Esse
caso fica para decisão do Otávio, mas não foi observado: o 9d melhorou (36,4 → 4,5 pp), e os
registros da demonstração não guardam o critério da etapa 1 para conferir.

*Esperado, commitado antes de implementar:*
- `docs/diagnostico/p17_frase_conferir.py` (sem solver, com os indicadores gravados): K5 de 11/10
  e Otávio, K5 e K6 de 09/10 → linha nova; 9d (com prova) → linha atual do caminho provado;
  sintético sem prova com melhora → linha atual sem prova. Antes da correção, os quatro
  primeiros falham (rodado: "FRASE FALHA", que é o defeito).
- Teste 8b (`src/testes_ferramenta.py`, esperado refeito no docstring): a linha bate exatamente
  com a de "melhorou" ou com a de "não melhorou", conforme o critério; sem melhora, critério
  final = etapa 1. O 12a (com prova) não muda.
- Regressão primeiro, depois as telas 8 e 12, que leem essa linha. Tudo OK → tag `v1.2.2`.

*Resultado (11/10, uma resolução por processo; logs em `resultados/v122_2026-10-11/`):* tudo
igual ao esperado.
- `p17_frase_conferir.py`: "FRASE OK" nos 6 casos.
- Regressão: 56, 58, 197, 219 = Tabela 6.
- Tela 8: OK. **O 8b também ficou sem melhora** (critério 0,3409 → 0,3409 em 25 s) e mostrou a
  linha nova. É a 5ª resolução sem prova em que a etapa 2 não melhora.
- Tela 12: OK (12a, com prova: linha "a da etapa 2, com a carga equilibrada entre colegas").

Correção em `src/ferramenta.py` (`resolver_com_objetivo` e `Resultado.frase_vigente`), só no
caminho sem prova; `modelo.py` intacto. Tag `v1.2.2`.

**d) Adendo de 11/10 — diagnóstico da etapa 2 no K5, SÓ TESTE** (decisão do Otávio, 11/10). Nada
muda em `src/`, na ferramenta ou na `v1.2.2`, qualquer que seja o resultado. Script:
`docs/diagnostico/p17_etapa2_variantes.py`. Ele monta por fora o modelo da etapa 2 do K5 (as
mesmas funções da ferramenta, com penalidade ≤ 21) e parte da escala da etapa 1 gravada em
`resultados/p17_diagnostico_2026-10-10/` (critério 0,4091).
- **A) Tempo:** o mesmo modelo, com limite de 1.800 s.
- **B) Simetria:** limite de 180 s, com ordem por horas dentro de cada grupo de profissionais
  idênticos (no K5, os 13 enfermeiros e os 5 técnicos). A partida é a mesma escala, renumerada
  por horas decrescentes.

**Esperado, commitado antes de rodar:** "melhora" e "sem melhora" são válidos nas duas.
Conferências obrigatórias:
- partida aceita = 0,4091;
- havendo melhora, critério recontado sem `ferramenta.indicadores` = o melhor do log;
- penalidade ≤ 21, recontada da escala;
- descanso e rígidas OK;
- em B, a escala final, desfeita a renumeração, é legal na instância original.

Ressalva: uma rodada, uma partida; tempo é limite operacional.

*Resultado (11/10, rodadas do Otávio: B ~12:38–12:41, A ~12:42–13:12; i5-10210U, HiGHS 1.15.1;
`resultados/p17_variantes_2026-10-11/A/` e `B/`):* as duas dentro do esperado, todas as
conferências OK. Recontagem refeita depois, sem solver, a partir das escalas gravadas: bate.
- **B (simetria, 180 s): SEM MELHORA.** Grupos de 13 e 5, 16 restrições de ordem. Partida aceita
  (0,4091), nenhuma solução melhor, dual ~3e-14, gap de 100%, 1.315 nós. Escala final = partida
  (0 atribuições diferentes); conferência 5 OK.
- **A (tempo, 1.800 s): MELHORA.** Partida aceita (0,4091). Melhoras aos 1.752,1 s (0,1705) e
  aos 1.797,4 s (0,1364), as duas com fonte "L" no log, que a legenda do próprio log do HiGHS
  1.15.1 define como "L => Sub-MIP" (heurística que resolve um MIP menor). Fim: primal 0,1364,
  dual ~2e-14, gap de 100%, 14.455 nós. Penalidade recontada 21 (= etapa 1). Diferença entre
  colegas: enfermeiros 42 → 12 h (120–162 → 144–156 h), técnicos 30 → 12 h (144–174 → 150–162 h).
  Descanso e rígidas OK.

**Leitura (decisão do Otávio, 11/10).** Nos casos de fronteira, a limitação da etapa 2 é de
**tempo, não de alcance**: existe escala muito mais equilibrada com a mesma penalidade, e o HiGHS
só a achou aos ~29 min. A melhora veio a 3 s do fim, então pode haver melhora maior com mais
tempo. A quebra de simetria não antecipou a melhora em 180 s. O limite inferior continuou ~0 nas
duas: nenhuma prova de que 0,1364 seja o melhor. **A ferramenta não muda:** o orçamento do clique
(20 min, P12) não comportaria uma etapa 2 desse tamanho. Uma rodada, uma partida; tempo é limite
operacional desta máquina. Desdobramento: `PROPOSTAS.md`, P19 (a) e (d).

*Nota para o referencial (2.4.3) e o método (11/10, só leitura): o que é a fonte "L" (Sub-MIP).*
- **Versão que roda:** pacote `highspy` 1.15.1; biblioteca "Running HiGHS 1.15.1 (git hash:
  04024d7)", impressa pelo próprio HiGHS no `.venv`. Os `highs.log` gravados via `appsi_highs`
  não trazem essa linha de cabeçalho. A tag `v1.15.1` do repositório oficial aponta para o
  commit `04024d701f79feb8e2f18bc3df0dffc04ef05088`, o mesmo do binário. Fonte:
  <https://github.com/ERGO-Code/HiGHS/tree/v1.15.1>. O `.venv` só tem o binário.
- **O que o código chama de sub-MIP:** `HighsPrimalHeuristics::solveSubMip`
  (`highs/mip/HighsPrimalHeuristics.cpp`, linha 77). Copia o modelo com limites de variáveis
  mais apertados (parte das variáveis inteiras fixadas pela heurística que chama), resolve essa
  cópia com o próprio resolvedor de MIP do HiGHS e, se achar solução, a oferece ao problema
  principal com a fonte `kSolutionSourceSubMip` (linha 238). A letra "L" e o nome "Sub-MIP"
  vêm de `highs/mip/HighsMipSolverData.h`, linha 53, e de `HighsMipSolverData.cpp`, linhas
  113–115.
- **Limites da cópia** (`solveSubMip`, linhas 92–130):
  - nós, folhas e nós sem melhora limitados pela heurística que chama;
  - o tempo restante do problema principal;
  - o valor da melhor solução como corte;
  - gap absoluto pequeno;
  - sem detecção de simetria;
  - `mip_heuristic_effort` = 0,8 dentro da cópia.
- **Quem chama** (nomes como estão no código):
  - `rootReducedCost` (linha 314; chamada na 369), só na raiz;
  - `RENS` (linha 394; chamada na 627), na raiz e, durante a árvore, só enquanto não há
    incumbente;
  - `RINS` (linha 661; chamada na 938), durante a árvore, quando já há incumbente.
- **Quando disparam:**
  - Na raiz: `HighsMipSolverData.cpp`, linhas 2363–2398.
  - Na árvore: `HighsMipSolver::run`, a função `runHeuristics` (`HighsMipSolver.cpp`, linhas
    746–795). Ela é chamada na linha 847 só se `moreHeuristicsAllowed()` permitir.
  - Essa função (`HighsMipSolverData.cpp`, linhas 669 em diante) limita a fração de iterações
    de LP gasta em heurísticas, que vem de `mip_heuristic_effort` (linha 764).
- **Opções e padrões** (`highs/lp_data/HighsOptions.h`, linhas 1224–1257; conferidos no `.venv`
  com `getOptionValue` e na documentação oficial,
  <https://ergo-code.github.io/HiGHS/stable/options/definitions/>):

  | Opção | Padrão |
  |---|---|
  | `mip_heuristic_effort` | 0,05 (faixa 0–1) |
  | `mip_heuristic_run_rins` | true |
  | `mip_heuristic_run_rens` | true |
  | `mip_heuristic_run_root_reduced_cost` | true |

- **No K5 (rodada A):** as duas melhoras saíram com "L" em plena árvore (nós 14.154 e 14.378),
  bem depois do último reinício da busca (linha 186 do log). Já havia incumbente (a partida).
  Pelo código acima, o único caminho de sub-MIP nessa situação é o `RINS`. O log, porém, não
  registra o nome da heurística: a leitura "foi o RINS" é inferência pelo código, não
  observação.

---

## 2026-10-13 — Art. 67 com horários editáveis

**Status: vigente.** Correção de defeito antes do congelamento (16/10). Decisão do Otávio:
correção (a) + (b). Esperado registrado e commitado antes de implementar
(`resultados/relatorio_2026-10-13a.md`). Supera, na entrada "2026-09-29 — Ajustes da Etapa 2",
a afirmação "o modelo garante o art. 67 por construção" (marcada lá, sem apagar).

**Defeito.** Com turnos editados na tela, o art. 67 (24 h de descanso semanal) não era
garantido pelo modelo. N 23–07, folga, M 05–13 = 22 h: passa nas 11 h e não era proibido. A
conferência no relógio (`medir`/`cumpre`) reprovava, mas a ferramenta entregava a escala com
"admite escala legal", só com a métrica "NÃO CUMPRE", e a busca do menor quadro a contava como
viável. O argumento de 29/09 (pior caso noite → folga → manhã = 24 h) só vale para os horários
dos modelos prontos.

**(a) Regra no modelo.** `instancia_br.pares_proibidos_por_horario` (fonte única) proíbe também
(s, 2, t) quando 48 + início de t − (início de s + duração de s) < 24 h. Critério conservador:
**toda** folga isolada dá ao menos 24 h; com no máximo 6 dias seguidos, toda janela de 7 dias
tem um dia sem turno, logo há ao menos um descanso de 24 h por semana. Salto 3 não precisa: com
dois dias livres o descanso é ≥ 72 − (23 + 24) = 25 h (início ≤ 23 h, duração ≤ 24 h, limites
de `_validar_turnos`); conferido por enumeração em `testes_entrada.py`. A regra vale com ou sem
`interjornada` (o `--sem-descanso-clt` continua desligando só as 11 h), como o limite de 6 dias.
O id do padrão de salto 2 continua `clt_36h_…` (nome histórico; trocar mudaria os XML).

**(b) Segunda proteção na ferramenta.** Se `cumpre()` reprovar a escala achada, ela não é
entregue: veredito "não decidido", sem escala nem planilha, a busca do menor quadro para ali
(a escala não conta como viável e o quadro não foi provado inviável), e a tela mostra em
vermelho "A escala encontrada não cumpre a conferência de descanso (art. 67): <medida>. Não use
esta escala." O artigo entre parênteses acompanha o que reprovou (art. 66 ou 59-A para o
intervalo entre turnos, art. 67 para o semanal e os dias seguidos). Com (a), não deve
acontecer; teste 16 de `testes_ferramenta.py` (escala montada à mão que reprova).

**Efeito nos números: nenhum.** Os modelos prontos (12×36, 8 h em três turnos, 6 h + noturno
12 h), os regimes do caminho por pacientes e todo caso da bateria e dos testes com horários
próprios dão no mínimo 24 h na folga isolada: nenhum par novo. Conferido byte a byte: os 544
XML da grade dos experimentos e os 96 XML do caminho por turnos (bateria P e K, demonstração,
casos de diagnóstico, os três modelos), antes × depois, idênticos. Controle positivo: o XML do
caso 23–07 + 05–13 muda (ganha o padrão N, folga, M).

---

## 2026-10-09 — Texto do TCC antecipado para 09/10

**Status: vigente.** Decidido pelo Otávio em 09/10; registrado em 11/10. Altera a entrada
"2026-10-06 — Cronograma" (E2).

Com a validação encerrada em 09/10 ("2026-10-09 — Encerramento da validação"), antes do fim da
semana de testes prevista (08 a 12/10), o texto do TCC começa em 09/10. **Cronograma vigente:**
- texto do TCC: **09 a 25/10**;
- números congelados: **16/10** (até lá, só correção de defeito, com esperado registrado antes);
- melhoria de tela e textos de ajuda: **26 a 29/10**, sem mudar comportamento nem número;
- reorganização das pastas (P18, opção A): 16–17/10;
- entrega: **04/11**.

*19/10: cronograma substituído por "2026-10-19 — Cronograma: ferramenta até 25/10, entrega em
06/11".*

---

## 2026-10-14 — Função objetivo por níveis escolhidos pelo gestor (opção B)

**Status: vigente — MUDANÇA DE FORMULAÇÃO da função objetivo da ferramenta. Implementação:
pendente** (bloco seguinte da Orientação). Aprovada pelo Prof. Ormeu em 14/10/2026, 19h58
(mensagem e áudio do Otávio); registrada em 19/10 a pedido da Orientação.

**Decisão.** O gestor classifica cada critério — pedidos de folga, enfermeiro em posto de
técnico e as suaves do INRC — em **Essencial / Importante / Desejável / Não considerar**. A
otimização é **lexicográfica entre níveis**; dentro do nível, **peso 1 por violação**; empate =
mesmo nível. **Padrão = a ferramenta atual**: pedidos de folga Essencial; enfermeiro em posto de
técnico Importante; demais Não considerar. O equilíbrio de carga (etapa 2) continua como último
passo fixo, depois dos níveis.

**Motivo** (Otávio, 14/10, 18h; texto em `D:\TCC\escrita\RETORNO_ORMEU_14-10.md`, seção
"Justificativa da opção B"). Peso é informação de **quantidade** ("um pedido negado vale 7 fins
de semana incompletos"), que ninguém sabe justificar — nem o INRC, cujos pesos variam por
instância (todas as suaves com peso 1 em `sprint01` e `long01`; de 3 a 10 em `medium_late05` (restrições dos contratos atribuídos; padrões e pedidos com peso 1 —
precisão de 26/10)).
A descrição oficial da competição (`docs/nrpcompetition_description.pdf`, seção 2.2) chama a
divisão entre duras e suaves de "rather arbitrary" e diz que unidades diferentes dão pesos
diferentes. Ordem é informação de **prioridade** ("o pedido importa mais que o fim de semana
completo"), que o gestor responde com segurança; a otimização por níveis usa só essa
informação. **Custo declarado:** sem compensação entre níveis (é o significado de
"Essencial"); compensação possível dentro do nível (empate).

**Relação com o que existe.** A ferramenta já é um caso particular: a etapa 1 combina pedidos
(peso W) e enfermeiro em posto de técnico (peso 1) com W maior que o máximo possível da segunda
parcela ("2026-09-29 — Redesenho da ferramenta", item Objetivo; `ferramenta.pesos`). A opção B
generaliza essa ordem fixa para uma ordem escolhida. Nada é superado enquanto não for
implementada; depois, a entrada de 29/09 passa a descrever o caso padrão.

**Teste obrigatório da implementação:** com a classificação padrão, XML, números e textos
idênticos aos da `v1.2.3`.

Diagnóstico para a implementação (como a etapa 1 combina hoje os critérios, gap do HiGHS, os 13
critérios, limites superiores, orçamento): `resultados/relatorio_2026-10-19.md`, item 3.

---

## 2026-10-19 — Cronograma: ferramenta até 25/10, entrega em 06/11

**Status: vigente.** Pedido da Orientação, 19/10. Substitui o cronograma de "2026-10-09 — Texto
do TCC antecipado para 09/10".

- **19 a 25/10:** modificações na ferramenta (opção B, orçamento configurável, validação por
  restrição). **Congelamento dos números em 25/10** (substitui 16/10).
- **20/10:** reunião com o orientador.
- **26/10 a 01/11:** só escrita. **02 a 06/11:** revisão do orientador.
- **Entrega: 06/11** (substitui 04/11).
- Retirado "nada muda na ferramenta até 26/10".
- **P18 (reorganizar pastas): CORTADA.** Mudar caminhos agora quebraria os comandos do
  `NUMEROS_TCC.md`.
- **P16 (melhorias de tela):** só se sobrar tempo nesta semana; o item "veredito próprio para
  escala reprovada na conferência" segue com prioridade baixa.
- **`MAPA_CODIGO.md`:** só depois dos itens 3, 4 e 7 da sessão de 19/10, se houver tempo, com
  os caminhos atuais (sem P18).

---

## 2026-10-19 — Limitações declaradas: domingo no art. 67 e escala do art. 386

**Status: vigente.** Pendentes desde 13/10; registradas em 19/10 a pedido da Orientação. Fontes:
"2026-10-13 — Art. 67 com horários editáveis" (acima) e, só leitura, o fichamento da CLT da
Redação (`D:\TCC\escrita\fontes\fichamentos\Camada 7 - Contexto Brasileiro e Hospitalar\clt.md`,
CLT-003 e CLT-004) e `D:\TCC\escrita\REUNIAO_ORMEU_14-10.md`, item 5.

**(a) Domingo no art. 67.** O art. 67 assegura 24 h consecutivas de descanso semanal que,
"salvo motivo de conveniência pública ou necessidade imperiosa do serviço, deverá coincidir
com o domingo, no todo ou em parte" (CLT-003). A ferramenta garante as 24 h (toda folga isolada
≥ 24 h e no máximo 6 dias seguidos, entrada de 13/10) e as mede no relógio, mas **não impõe que
o descanso caia no domingo**, nem com que frequência.

**(b) Art. 386.** "Havendo trabalho aos domingos, será organizada uma escala de revezamento
quinzenal, que favoreça o repouso dominical" (CLT-004; o artigo está no capítulo da proteção do
trabalho da mulher). A ferramenta **não recebe o sexo dos profissionais** (decisão do trabalho)
e **não impõe essa escala**.

**Contorno pelo gestor, e do que ele depende.** O gestor pode pedir folga no domingo para quem
precisar, como pedido de folga. Isso é **forma de uso, não cumprimento da lei**: o pedido é
critério flexível. Hoje ele tem prioridade sobre enfermeiro em posto de técnico (peso W), mas
pode ser negado quando a cobertura e as regras de descanso não o comportam. **Com a opção B, o
contorno depende da classificação**: com pedidos em Essencial (o padrão), só perdem para as
regras rígidas; em nível mais baixo, podem perder também para os critérios dos níveis acima;
em "Não considerar", o contorno deixa de existir.

**O que falta registrar (não inventado aqui):** se o domingo e o art. 386 vão como trabalho
futuro (o fichamento CLT-004 sugere a 6.3, "como hipótese"); a frequência mínima de domingos
livres que a jurisprudência ou norma aplicável exigiria para o art. 67 (não pesquisada); e se a
jurisprudência sobre o art. 386 (o fichamento cita o RE 1.403.904 do STF) entra no texto — o
fichamento proíbe citá-la sem o acórdão lido.

---

## 2026-10-19 — Orçamento por clique configurável, padrão 60 min

**Status: vigente. Implementação: pendente, junto com a opção B, não antes.** Pedido da
Orientação, 19/10.

**Motivo.** Relato do Otávio: na reunião de 14/10, o Prof. Ormeu considerou razoável estender o
tempo de execução até 1 h – 1 h 30.

**Decisão.** O orçamento por clique da P12 ("2026-10-08 — P12 aprovada", 20 min) passa a
**parâmetro da tela, padrão 60 min**.

**O que continua valendo.** A bateria, a demonstração e todos os números do `NUMEROS_TCC.md`
continuam válidos como estão, **declarados "com orçamento de 20 min"**. Não rodam de novo.
Rodadas novas (caso realista A e B, sensibilidade) usam 60 min. Onde o orçamento mora hoje e o
que muda para virar parâmetro: `resultados/relatorio_2026-10-19.md`, item 3e.

---

## 2026-10-19 — Opção B: mecanismo, tempo e critérios expostos

**Status: vigente — MUDANÇA DE FORMULAÇÃO** (complementa "2026-10-14 — Função objetivo por
níveis escolhidos pelo gestor (opção B)"). Decisões da Orientação sobre o
`resultados/relatorio_2026-10-19.md`, seção 3, aprovadas pelo Otávio em 19/10 (2º bloco).

**(a) Mecanismo.** Níveis resolvidos **em sequência**, cada nível com o valor do anterior preso
como restrição (o mesmo mecanismo da etapa 2). **Regra de fusão:** níveis vizinhos são
resolvidos juntos por coeficiente (W = máximo do bloco de baixo + 1) somente se o objetivo
máximo do bloco fundido for **< 10.000** (condição de "2026-10-09 — Condição das afirmações de
ótimo provado"); caso contrário, resolução separada. Máximos por nível: as fórmulas do censo de
19/10 (relatório, 3d). Motivo: com pesos escalonados em 3 níveis o coeficiente chega a ~1,36
milhão e o gap padrão deixa de provar os níveis de baixo. Com a classificação padrão (pedidos ≤
6 × 286 + enfermeiro em posto de técnico ≤ 285 = 2.001), a fusão reproduz o caminho atual.

*(22/10: o limite por resolução foi revisto — ver "2026-10-22 — Divisão proporcional do tempo
máximo"; o texto abaixo fica como registro.)*
**(b) Tempo.** Orçamento por clique **60 min** (campo na tela, em minutos). Limite por
resolução: **1.800 s em cada nível da etapa 1 e 1.800 s na etapa 2**, sempre min(limite, o que
resta). Motivo: P17, o K5 melhorou a etapa 2 aos ~29 min com 1.800 s (`NUMEROS_TCC.md`, seção
13). A bateria, a demonstração e os números atuais continuam válidos, declarados "orçamento 20
min, 600 s / 180 s"; não rodam de novo.

**(c) Critérios na tela** (numeração de Santos et al.):
- **expostos:** 1 mínimo de turnos; 2 mínimo de dias seguidos; 3 máximo e mínimo de folgas
  seguidas; 4 máximo e mínimo de fins de semana seguidos; 5 fins de semana em 4 semanas; 6 fim
  de semana completo; 7 mesmo turno no fim de semana; 8 noturno antes de fim de semana livre;
  9 duas folgas após noites; e os que já existem (pedido de folga no dia; enfermeiro em posto de
  técnico);
- **"já garantido pela CLT"**, na tabela, sem campo de preferência: máximo de dias seguidos;
  máximo de turnos; sequências indesejadas. Preferência mais apertada = trabalho futuro (exige
  família própria no modelo); *(REVISADO em 21/10 para o máximo de dias seguidos e o máximo de
  turnos por "2026-10-21 — Máximo de dias seguidos e máximo de turnos também como preferência";
  sequências indesejadas continuam só rígidas)*
- **fora:** habilidade alternativa (contradiz a habilidade rígida); pedidos por turno e pedidos
  para trabalhar (trabalho futuro, mantida "2026-10-09 — Pedido por turno vira trabalho
  futuro");
- **sem conferência externa** (ⓘ na ajuda): fins de semana em 4 semanas; duas folgas após
  noites; noturno antes de fim de semana livre (o avaliador não a pontua).

**Decisões de implementação (Claude Code, 19/10; não óbvias, registradas antes de
implementar):**
1. **Peso dentro do bloco = coeficiente do nível.** Cada família considerada entra no contrato
   (ou nos pedidos, ou no custo por atribuição) com peso igual ao coeficiente do seu nível no
   bloco; num bloco de um nível só, peso 1. Assim a função objetivo do bloco é a soma das
   parcelas das suas famílias, e o modelo (`modelo.py`) não muda. Famílias não consideradas
   ficam como hoje no contrato (desligadas), para o XML da instância não mudar com o padrão.
2. **Máximo de "enfermeiro em posto de técnico"** = total de postos de técnico do horizonte, e
   de "pedido de folga" = número de pedidos — os mesmos da `ferramenta.pesos` de hoje (é o que
   faz W = 286 na demonstração).
3. **Nível resolvido sem prova:** o nível seguinte prende "≤ valor achado" (como a P14) e parte
   da escala achada (como a P17). A escala é "sem prova" se algum nível não provou; o gap
   mostrado é o do primeiro nível sem prova.
4. **Situação, calculada antes de resolver** *(SUBSTITUÍDA em 19/10 por "2026-10-19 — Tela orientada ao usuário": a coluna sai da tela)*:
   - "a CLT prevalece": o limite pedido vai além do que a lei permite no regime — mínimo de dias
     seguidos acima do máximo de dias seguidos que as regras de descanso admitem (1 no 12×36, 6
     nos demais); mínimo de turnos acima do teto legal de turnos do contrato. O critério continua
     valendo; a escala sai legal e a preferência fica sem atender onde a lei impede;
   - "nunca será atendido neste regime": fim de semana completo e mesmo turno no fim de semana
     quando ninguém pode trabalhar dois dias seguidos (12×36) e o fim de semana tem demanda — quem
     trabalha no fim de semana trabalha um dia só e viola;
   - "já garantido pela CLT": as três linhas sem campo;
   - "ok": os demais.
   *Leitura do pedido da Orientação ("limite mais frouxo que a lei"):* com as três famílias
   legais sem campo, nenhum limite exposto pode ser "mais frouxo" que a lei; a situação "a CLT
   prevalece" ficou para o limite que **contradiz** a lei. Levar à Orientação.
5. **Limite padrão de cada critério com parâmetro**, quando o gestor o liga: os valores do
   contrato 0 do `medium_late05` (mínimo de turnos 10; mínimo de dias seguidos 3; máximo de
   folgas seguidas 4; mínimo de folgas seguidas 3; máximo de fins de semana seguidos 3; mínimo 2).
   Fins de semana em 4 semanas: 2 (nenhuma instância do INRC liga; valor de exemplo, sem fonte).
   O gestor edita.
6. **Resultado por critério:** contado na escala final, fora do modelo, por `avaliacao.py`
   (excesso por família) e, para o noturno antes de fim de semana livre, que o `avaliacao.py` não
   pontua, por `solucao.noites_antes_de_fim_de_semana_livre`; enfermeiro em posto de técnico e
   pedidos, pela contagem que a tela já usa (`ferramenta.indicadores`).
7. **Os testes da tela rodam com os limites da v1.2.3** (600 s / 180 s / 20 min): verificam
   comportamento, não limite. Um teste confere os padrões novos (1.800 s, 1.800 s, 60 min) e que
   o campo da tela chega ao `verificar`.

**Defeito do teste 1-2, corrigido com autorização do Otávio (19/10).** Na suíte de fechamento
da v1.3.0, o caso 1-2 falhou só no item "planilha abre": ele exigia as abas `["Escala",
"Resumo", "Legenda"]`, e a planilha trouxe `['Escala', 'Resumo', 'Legenda', 'Prioridades']`.
Causa: o teste é anterior à opção B, que acrescenta a aba "Prioridades" — acréscimo previsto
no esperado registrado e commitado antes de implementar (`resultados/opcao_b_2026-10-19/
ESPERADO.md`, linha 37: "as abas Escala, Resumo e Legenda não mudam; entra a aba
'Prioridades'"). A ferramenta estava certa; o teste ficou desatualizado. Correção: a
conferência, que era conjunta (abas **e** `max_row` da aba Escala = 41), foi separada em duas
— abas == `["Escala", "Resumo", "Legenda", "Prioridades"]` e `wb["Escala"].max_row == 41` —,
porque com a condição conjunta não se sabia se a segunda parte tinha passado. Nada mais mudou
no teste nem na ferramenta.

---

## 2026-10-19 — Opção B: decisões 4 e 5

**Status: vigente.** Decisão da Orientação sobre as duas leituras de implementação da entrada
"2026-10-19 — Opção B: mecanismo, tempo e critérios expostos" (relatório 19b, seção 1), registrada
em 20/10 (3º bloco).

**Decisão 5 (limites padrão) — aprovada.** Os limites padrão dos critérios com parâmetro são os do
contrato 0 do `medium_late05`. Motivo, do registro: o `medium_late05` foi escolhido por
**cobertura** — é a instância que exercita todas as restrições que aparecem ligadas em alguma
instância do benchmark ("2026-09-15 — Quinto alvo de validação: `medium_late05`").
**Fins de semana em 4 semanas = 2** fica, marcado na ajuda da tela e no `GUIA_DE_USO.md` como
"valor de exemplo, sem fonte (suposição declarada)". Nunca apresentá-lo como valor do INRC.

**Decisão 4 (mensagens da coluna Situação) — SUBSTITUÍDA** por "2026-10-19 — Tela orientada ao
usuário" (Parte 5 do 3º bloco): a coluna Situação sai da tela. As regras de cálculo ficam em
`prioridades.situacoes` (back end), sem uso na tela.

**Nota para o texto.** Com um nível resolvido sem prova (decisão de implementação 3), a
prioridade entre níveis só é garantida nos níveis provados: um nível de baixo pode ter sido
resolvido sobre um valor do nível de cima que não é o ótimo. A tela e o resultado por critério
informam o gap do primeiro nível sem prova.

---

## 2026-10-19 — Pedidos e regras por profissional; revisa 2026-10-09 (Pedido por turno vira trabalho futuro)

**Status: vigente — MUDANÇA DE FORMULAÇÃO** (extensão da opção B). Decisão do Otávio, 19/10,
validada pela Orientação; registrada antes de implementar (20/10).

**Por quê.** Hospitais brasileiros costumam ter equipes fixas por turno (caso Massens 2019:
equipes de manhã, tarde e noite fixas) e profissionais com pedidos de dia e de turno. A
ferramenta precisa distinguir **regra do hospital** de **desejo do profissional**.

**O que muda.**
- Uma tabela "Pedidos e regras dos profissionais": Profissional | Dia (em branco = todos os
  dias) | Turno (em branco = o dia todo) | Tipo ∈ {Folga, Só este turno} | Importância ∈
  {Essencial, Importante, Desejável}. Linha sem dia e sem turno é inválida.
- **A importância fica na linha, não no critério:** o mesmo tipo pode ser regra do hospital
  (Essencial) ou desejo do profissional (Desejável); quem distingue é o gestor. Padrão de linha
  nova: Folga com dia e sem turno → Essencial (= v1.3.0); as demais → Desejável.
- **Tradução, sempre para pedidos negativos já validados** (`DayOffRequest` / `ShiftOffRequest`
  do INRC):
  - Folga + dia → folga no dia;
  - Folga + dia + turno → folga naquele turno daquele dia;
  - Folga + turno → folga naquele turno em todos os dias;
  - Só este turno (+ dia opcional) → folga em todos os outros turnos no(s) dia(s); várias linhas
    "Só este turno" da mesma pessoa e dia se somam (Manhã e D12 = pode Manhã ou D12).
- **Função objetivo:** cada linha pertence ao nível da sua Importância. Violação =
  profissional-dia-turno trabalhado contra a linha; para folga no dia, a unidade que o motor já
  usa (profissional-dia trabalhado), para preservar a identidade. Se várias linhas proíbem o
  mesmo profissional-dia-turno, conta **uma** violação, no nível mais alto entre elas. Peso 1 por
  violação dentro do nível. Entra no plano de níveis e na regra de fusão como os critérios
  existentes; o máximo de violações de cada nível vem das linhas da tabela.
- **Em Essencial nada é rígido:** a tela informa quantos pedidos foram descumpridos e de quem.
  Cobertura e CLT continuam rígidas.
- A tabela de Prioridades deixa de ter a linha "Pedido de folga no dia" (a importância é coluna
  da tabela de pedidos). No grupo 1 ("Pedidos e qualificação") ficam a tabela de pedidos e a
  linha "Enfermeiro em posto de técnico".
- Sem linhas na tabela, nada muda (nível vazio não gera resolução).

**Teste opB-tela atualizado com autorização prévia do pedido (20/10)**, como no precedente do
teste 1-2: com a linha "Pedido de folga no dia" fora da tabela de Prioridades, o grupo 1 passa
de "2 de 2" para "1 de 1 considerados", a conferência da importância padrão deixa de incluir
`pedido_folga` (não há mais campo), e o aviso de mesmo nível é provocado pondo "mínimo de folgas
seguidas" em Importante (antes, o pedido de folga em Importante). Acrescentada a conferência de
que a tabela "Pedidos e regras dos profissionais" aparece no grupo 1. O texto de resultado não
mudou. O critério `pedido_folga` continua no back end (caminho antigo, `Entrada.pedidos`) e na
linha "Pedido de folga no dia" do resultado por critério, que fica 0 quando só há a tabela nova.

**Motivo da revisão de 09/10.** (i) A tolerância do solver deixou de ser problema: com os níveis
em sequência (opção B), a prioridade entre níveis vem da sequência, não de pesos escalonados, e
só se fundem níveis cujo bloco fica abaixo de 10.000; (ii) o motor já suporta
`folga_turno`, validado pelas quatro instâncias da regressão (50 ou 245 pedidos de turno cada).
A entrada "2026-10-09 — Pedido por turno vira trabalho futuro" fica marcada como revista.

---

## 2026-10-19 — Máximo de dias seguidos como regra do hospital (rígida)

> **Revisada em 21/10 (v1.4.3)** por "2026-10-21 — Máximo de dias seguidos: a trava é só a da
> CLT; a regra do hospital é preferência": o campo rígido do hospital sai da tela e da entrada. O
> texto abaixo fica como registro.

**Status: vigente — mudança de PARÂMETRO, não de formulação.** Registrada antes de implementar
(20/10).

O gestor informa um máximo de dias seguidos de trabalho; a ferramenta usa **min(hospital, CLT)**,
pelo `max_consecutivos` de `instancia_br` (o mesmo parâmetro que hoje recebe o 6 do art. 67). O
campo não aceita valor acima da lei (6); no 12×36 a linha não aparece (o limite efetivo já é 1).
Padrão 6 = comportamento atual. É regra rígida, como a da CLT: pode levar a "faltam N", e isso é
resultado, não defeito.

**Teste opB-tela atualizado (20/10, Parte 4)**, como no precedente do teste 1-2: a linha cinza
"Máximo de dias seguidos de trabalho — já garantido pela CLT" virou o campo do hospital; no
12×36 (o modelo padrão da tela, em que o teste roda) o campo fica oculto. O esperado passa de
"três linhas 'já garantido pela CLT'" para **duas** (sequências indesejadas; máximo de turnos) e
ganha a conferência de que o campo novo **não aparece no 12×36**. Nenhum texto de resultado
mudou. Resultado da Parte 4 (esperado em `resultados/max_dias_2026-10-20/ESPERADO.md`):
identidade 243/243 com a v1.3.0; 7 recusado; com 6, admite 14; com 4, "Falta 1; o menor quadro
viável é 15", maior sequência 4 na escala e no relógio, o 14 recusado pela conta (piso com L = 4).

---

## 2026-10-19 — Tela orientada ao usuário

**Status: vigente.** Registrada antes de implementar (20/10).

- Sem a coluna Situação (substitui a decisão de implementação 4 da opção B; ver "2026-10-19 —
  Opção B: decisões 4 e 5").
- Explicações longas vão para o "?" de cada campo (parâmetro `help` do Streamlit) e para o
  `GUIA_DE_USO.md`; na tela, uma linha por campo.
- As regras da CLT ficam no back end: as linhas "Sequências indesejadas" e "Máximo de turnos no
  período" saem da tela; no 12×36 saem também as que nunca podem ser atendidas ou que a lei
  impede (fim de semana completo, mesmo turno no fim de semana, mínimo de dias seguidos).
- Mensagens de resultado (veredito, alertas, diagnóstico, resultado por critério) não mudam.

**Implementada em 20/10 (Parte 5).** Decisões de implementação e esperado em
`resultados/tela_2026-10-20/ESPERADO.md` (rótulos dos turnos só na tela, com os códigos M, T, N,
D inalterados na instância, no XML e na grade; critério oculto no 12×36 vale como "Não
considerar"). Identidade com a v1.3.0: 243/243. **Teste opB-tela atualizado**, como no precedente
do 1-2: no 12×36 (modelo padrão da tela) os grupos passam a "Sequências de trabalho e folga — 0 de
2" e "Fins de semana — 0 de 3" (três critérios ocultos), a importância padrão conferida exclui os
ocultos, e as linhas "já garantido pela CLT" passam de 2 a **0**. Nenhum texto de resultado
mudou.

---

## 2026-10-20 — Diagnóstico "combinação": a frase diz quem provou (conta prévia ou solver)

**Status: vigente.** Ajuste de texto pedido pela Orientação (item 7 das leituras adotadas do
relatório de 20/10). Esperado registrado antes: `resultados/texto_piso_2026-10-20/ESPERADO.md`.

Quando nenhuma conta simples explica a trava, o texto dizia sempre "O solver provou que as regras
juntas… não admitem escala com este quadro" — inclusive quando o quadro informado foi recusado
pelo **piso** (conta prévia), sem solver (ex.: máximo de 4 dias seguidos do hospital). Agora
`diagnosticar(inst, por_conta)` diz "A conta prévia do menor quadro provou, sem o solver, que…"
quando a primeira tentativa foi "piso"; no resto, a frase de antes, idêntica. Nenhuma lógica nova
(o "piso" já estava em `r.tentativas`); entrada do solver idêntica (243/243 × v1.3.0).
**Teste:** nenhum teste conferia a frase; o `max-dias` ganhou duas conferências (o texto novo no
caso do piso; o de antes sem o parâmetro) — acréscimo, como no precedente do 1-2. Conferido aqui
sem solver (`verificar(margem=0)`): OK.

---

## 2026-10-20 — a posteriori: descanso depois do D12 como parâmetro de pesquisa

**Status: vigente. Registro A POSTERIORI — não é o motivo original da regra.** Pedido da
Orientação, 20/10 (Parte 6), depois do diagnóstico do relatório 20b, item B.

**Fato.** A regra vem de "2026-09-29 — Redesenho da ferramenta": "abaixo de 36 h depois de turno
de 12 h ou mais (art. 59-A)". Ela é aplicada pela **duração** do turno, sem olhar o regime
(`instancia_br.descanso_exigido`). Nenhuma entrada deste arquivo discute se ela vale para um
plantão **avulso** de 12 h (o D12, 7–19, no fim de semana) dentro de um regime de 6 h; as entradas
anteriores (08/09, 21/09) tratam do regime 12×36.

**Decisão.**
- O **produto mantém 36 h** depois de todo turno de 12 h ou mais: leitura conservadora, e a
  entrada do solver fica idêntica à da v1.3.0.
- **Para pesquisa**, passa a existir um parâmetro de descanso **por código de turno**
  (`instancia_br.DESCANSO_POR_TURNO`, vazio por padrão), **não exposto na tela nem na
  `Entrada`**, usado só em experimentos rotulados **"hipótese de sensibilidade, não regra da
  ferramenta"**. Valor testado: **D12 → 11 h** (interjornada, art. 66). A noite de 12 h continua
  com 36 h.
- O gerador de pares (`pares_proibidos_por_horario`) e a conferência no relógio
  (`docs/conferencia_descanso_escala.medir`) leem a **mesma** fonte (`descanso_exigido`), como no
  art. 67.
- O texto do TCC **não afirma que o hospital descumpre a lei**: a sensibilidade mostra o efeito de
  uma leitura, não julga a prática.

---

## 2026-10-20 — a posteriori: fundamento das 36 h para qualquer plantão de 12 h ou mais

**Status: vigente. Registro A POSTERIORI — justificativa nova, não era o motivo registrado em
29/09.** Pedido da Orientação, 20/10 (tarde). Sem mudança de código.

**Justificativa (do Otávio).** O art. 59 da CLT limita a jornada diária a 8 h, mais até 2 h
extras. O art. 59-A admite 12 h seguidas como **exceção**, por acordo individual escrito ou
convenção/acordo coletivo, e vincula essa exceção a 36 h ininterruptas de descanso. Logo, um
turno de 12 h ou mais só cabe dentro do desenho do art. 59-A, e a regra da ferramenta — 36 h
depois de todo turno com duração ≥ 12 h, sem olhar se o turno é noturno nem se o regime da
unidade é 12×36 — segue esse desenho. É a leitura que sustenta a decisão de manter as 36 h no
produto ("2026-10-20 — a posteriori: descanso depois do D12 como parâmetro de pesquisa").

**Declarações.**
- (a) É **justificativa nova**: o registro de 29/09 ("Redesenho da ferramenta") cita o art. 59-A
  mas não discute o plantão de 12 h avulso; este texto não reescreve o motivo daquela data.
- (b) A **convenção coletiva** do hospital do caso **não foi lida**. Ela pode prever outro arranjo
  (compensação, banco de horas); a ferramenta não a conhece.
- (c) O texto **nunca afirma que o hospital descumpre a lei**. A frase admitida é: "a regra, como
  modelada, segue o art. 59-A". A sensibilidade com D12 = 11 h continua rotulada como hipótese,
  não regra da ferramenta.

**Nota de 26/10 (correção de citação; raciocínio e código não mudam):** o limite de 8 h diárias é
do art. 58 da CLT (CLT-005); o art. 59 admite o acréscimo de até 2 h extras (CLT-006), conferidos
no Planalto em 26/10. O texto de 20/10 fica como está.

---

## 2026-10-20 — Piso por pares de dias (v1.4.1)

**Status: vigente.** Pedido da Orientação, 20/10 (tarde, Parte 7). Esperado em
`resultados/piso_pares_2026-10-20/ESPERADO.md` (`946e38c`), código em `0b1defe`.

**Decisão.** O piso da ferramenta (`ferramenta.piso`, que decide quais quadros vão ao solver)
ganha uma condição necessária: em cada par de dias seguidos, postos do segundo dia + postos do
primeiro em turnos que **bloqueiam o segundo inteiro** ≤ pessoas disponíveis em ao menos um dos
dois (férias descontadas); também só com enfermeiros (técnico não cobre posto de enfermeiro:
habilidade rígida). "Bloqueia" sai dos pares do gerador (`pares_proibidos_por_horario`), nunca
de "duração ≥ 12 h" fixo: acompanha horários editados e o `DESCANSO_POR_TURNO`. O diagnóstico
ganha o motivo "Dois dias seguidos" ("A conta prévia do menor quadro provou…", com o par e os
números); a "alternância" do 12×36 fica como estava.

**Por quê.** Sem ela, a conta prévia dava 18 (caso A) e 68 (caso B), e cada quadro abaixo do
mínimo gastava orçamento do solver; com ela, 30 e 105 (o B fica todo recusado pela conta até 101).

**Ressalvas.** A entrada do solver não muda (243/243 idênticos à v1.4.0). Mudam só tentativas
antes provadas pelo solver, que passam à conta (na suíte: P05, 14; demo18, 28; tela 7.3, 4). A
conta compartilha a regra de descanso com o modelo: confere a aritmética e a coerência, não a
leitura legal. Testes: `resultados/relatorio_2026-10-20c.md`, Parte 7.

---

## 2026-10-21 — Correção de defeito: avaliador sem memória lido como "sem violação"

**Status: vigente — correção de defeito** (não muda modelo nem formulação).

**O defeito.** Na fase 2 (21/10), a rodada B11_livre (89 profissionais) registrou "penalidade
do avaliador 43, sem violação de dura". O avaliador oficial, nas duas chamadas, tinha parado com
`java.lang.OutOfMemoryError: Java heap space` (heap padrão da JVM nesta máquina: ~3 GB). O
`validar._numero` não achou número de penalidade e caiu no "último inteiro da saída" — o 43 era
o número de linha `ScheduleEvaluator.java:43` do stack trace —, e o `fase2.py` procurou "Hard"
nas linhas de erro de uma saída que não tinha nenhuma: "não". **Conferência que não rodou foi
registrada como conferência aprovada.** As outras três escalas da fase 2 (A36_livre, A36_fixo,
A11_fixo) têm a saída completa; nelas o número bate com o da saída detalhada.

**Reconferência (21/10, mesmo XML, sem tocar na escala):** `java -Xmx6g …`: penalidade do
avaliador **714**, saída detalhada completa, nenhuma linha "Hard constraints". Saídas em
`resultados/fase2_2026-10-21/HIPOTESE_SENSIBILIDADE_B11_livre_escala_avaliador_Xmx6g*.txt`. Os
arquivos originais ficam como estão (evidência do defeito).

**Correção.** `validar._executar`: código de saída diferente de 0 ou "Exception in thread" na
saída levanta `AvaliadorIndisponivel` (o `fase2.py` já registra isso como "avaliador não
rodou"); e a JVM do avaliador roda com `-Xmx6g` (`validar.MEMORIA_JAVA`). Nenhum número citável
muda: os da regressão vêm de instâncias pequenas, com saída completa.

---

## 2026-10-21 — Máximo de dias seguidos e máximo de turnos também como preferência

**Status: vigente — MUDANÇA DE FORMULAÇÃO** (revisa "2026-10-19 — Opção B: mecanismo, tempo e
critérios expostos", item c: "preferência mais apertada = trabalho futuro"). Pedido do Otávio,
21/10, via chat de Orientação; registrada antes de implementar.

**Decisão.** Os dois limites passam a existir em dois papéis, em famílias separadas do modelo:
- *(21/10, v1.4.3: o rígido passa a ser só o legal, 6; ver a entrada seguinte)*
- **rígido**, como hoje: máximo de dias seguidos = min(hospital, 6) (art. 67 e "2026-10-19 —
  Máximo de dias seguidos como regra do hospital"); teto de turnos e teto de horas do contrato.
  Nada disso muda, e o teto de turnos rígido **não** sai (tirá-lo quebraria a identidade com a
  v1.4.1 sem ganho);
- **preferência**, critério classificável como os outros (Essencial, Importante, Desejável, Não
  considerar), com a mesma expressão do INRC e folga α:
  - máximo de dias seguidos: α ≥ Σ_{d=t..t+Lp} y − Lp, por profissional e janela, com
    Lp ≤ min(L_hospital, 6);
  - máximo de turnos: α ≥ Σ_d y − γp, por profissional, com γp ≤ o teto de turnos do contrato.

**Por quê.** A CLT trava; a preferência do hospital é critério classificável — o que o
orientador pediu em 14/10: manter o modelo perto do INRC e endurecer só o que a lei exige.

**Decisões de implementação (Claude Code, 21/10; não óbvias):**
1. **Famílias próprias:** `pref_max_consecutive_working_days` e `pref_max_num_assignments`,
   campos novos do contrato (`instancia.Contrato`), ausentes por padrão. Não vão ao XML do INRC
   (o formato não tem duas versões da mesma restrição); ficam fora de `RESTRICOES`. Sem elas
   ativas, o modelo não ganha variável nem restrição: com a classificação padrão, o LP é o da
   v1.4.1.
2. **Padrão: "Não considerar"**; limite padrão quando o gestor liga: os do contrato 0 do
   `medium_late05`, como os outros critérios ("Opção B", decisão de implementação 5) — 5 dias
   seguidos e 18 turnos.
3. **Limite acima do legal:** a tela não aceita (o campo tem o legal como máximo). No back end,
   o limite usado é **min(preferência, legal)** — a mesma regra do campo rígido do hospital; uma
   preferência no legal ou acima nunca é violada, porque a rígida já a garante.
4. **No 12×36 a linha de dias seguidos não aparece**, como o campo rígido (ninguém trabalha dois
   dias seguidos; nenhuma preferência ≥ 1 seria violada).
5. **Resultado por critério:** contado fora do modelo pelo `avaliacao.py` (a semântica conferida
   contra o avaliador oficial), com o contrato da família INRC correspondente trocado pelo
   limite da preferência.
6. **Testes atualizados com registro** (como o precedente do 1-2): opB-d (as duas linhas deixam
   de ser "já garantido pela CLT"); opB-tela (o grupo "Noturno e carga" passa de 3 para 4
   critérios; o máximo de dias seguidos fica oculto no 12×36); opB-e (o "todas as suaves no
   Essencial" passa a incluir as duas preferências). Esperado em
   `resultados/preferencias_2026-10-21/ESPERADO.md`.

**Ressalva.** O avaliador oficial não confere a preferência (o XML só tem a versão rígida, com
o limite legal); a contagem é do `avaliacao.py`, que foi conferido contra o avaliador nas
famílias INRC de mesma expressão.

**Teste opB-c atualizado a posteriori (21/10, suíte da v1.4.2; autorizado pelo Otávio, como o
precedente do 1-2):** "todas as suaves no Desejável" passa de 11 para 13 critérios e o máximo do
bloco, de 5.010 para 6.120 (+ 690 dos dias seguidos, + 420 dos turnos); conferido contra a v1.4.1
que não há outra diferença no plano (`resultados/preferencias_2026-10-21/ESPERADO.md`, segundo
acréscimo).

---

## 2026-10-21 — Máximo de dias seguidos: a trava é só a da CLT; a regra do hospital é preferência

**Status: vigente — mudança de ENTRADA e TELA, não de formulação** (revisa "2026-10-19 — Máximo de
dias seguidos como regra do hospital (rígida)"). Pedido do Otávio, 21/10; registrada antes de
implementar. Versão v1.4.3.

**Decisão.** O máximo de dias seguidos rígido passa a ser **só o da lei**: 6 (art. 67; no 12×36, a
regra das 36 h já impede dois dias seguidos). O campo rígido do hospital (v1.4.0) sai da tela e da
`Entrada`. A vontade do hospital entra pela preferência de dias seguidos (v1.4.2), critério
classificável, com o limite do campo preso ao legal.

**Por quê (Otávio, 21/10).** Em toda a ferramenta a vontade do hospital é critério classificável:
na tabela de pedidos, regra do hospital = Essencial, que não é rígido. O campo rígido do hospital
era a única exceção. Regra da ferramenta: **duro = lei ou físico** (cobertura, CLT, horas do
contrato, férias); **tudo o que o hospital quer é critério classificável**. Quem quiser que a regra
do hospital pese quase como trava põe a preferência de dias seguidos no Essencial, acima de tudo o
que é Importante ou Desejável.

**O que muda e o que não muda.**
- `src/modelo.py` e `src/instancia_br.py` **intocados**. A trava continua sendo a mesma restrição
  do contrato (`max_consecutive_working_days`), agora sempre com o valor legal. `instancia_br`
  continua aceitando `max_consecutivos` de 1 a 6 (o caminho dos experimentos e testes de entrada o
  usam); só a ferramenta deixa de passar outro valor que não o 6.
- `src/ferramenta.py`: `Entrada.max_dias_seguidos` sai; `montar` passa o legal
  (`MAX_CONSECUTIVOS_GENERICO`). Com o padrão de antes (6), a entrada enviada ao solver é a mesma —
  é o que a identidade confere.
- `src/app.py`: a linha "Máximo de dias seguidos de trabalho — Obrigatória" sai; o limite máximo dos
  campos de dias seguidos (preferência e mínimo) passa a ser o legal. Ajuda da linha da preferência:
  "a lei trava em 6; a regra do seu hospital vai aqui, como preferência; no Essencial ela pesa acima
  de tudo o que é Importante ou Desejável".
- `src/prioridades.py`: **só texto** (ajuda e resumo da linha, que apontavam para "o campo acima", e
  dois comentários). `limite_usado` = min(preferência, legal) fica como está: o "legal" lido do
  contrato agora é sempre a lei.
- **Consequência:** um hospital com regra de 4 dias deixa de receber "Falta N" por causa dela. A
  escala sai com o quadro que a lei admite, e as sequências acima de 4 aparecem no "Resultado por
  critério". É a mesma lógica dos pedidos: preferência nunca torna a escala impossível.

**Suíte reduzida (v1.4.3), justificativa.** A mudança é só de entrada e tela; modelo e solver estão
intocados. A identidade (243/243 na classificação padrão e 24/24 nas entradas da fase 2, byte a
byte contra a v1.4.2) prova que o problema enviado ao solver não mudou nos casos em que o campo
estava no padrão — e nenhum teste fora do `max-dias` usava outro valor. Por isso não rodam as
rodadas a2 nem os testes da tela que não tocam no campo nem na preferência de dias: a identidade
os cobre. Rodam: identidade, regressão dos 4 ótimos, testes de entrada, piso (segurança, controle,
casos), o caso pequeno das preferências e os testes da tela que usam o campo removido ou a
preferência de dias (lista e motivo em `resultados/trava_clt_2026-10-21/ESPERADO.md`).

**Teste max-dias reescrito (registrado antes):** o caso "hospital = 4 → Falta 1; o menor quadro
viável é 15" era trava e deixa de existir. Substituem-no: (i) a preferência 4 no Essencial com 14
técnicos — escala sai com 14, violações contadas fora do modelo = resultado por critério; (ii) para
não perder a cobertura do texto "A conta prévia do menor quadro provou" (só o max-dias o testava),
o mesmo caso com 13 técnicos e a lei (6): piso pela janela de 7 dias = 14 → "Falta 1; o menor
quadro viável é 14".

---

## 2026-10-21 — Textos para o gestor, tema claro e barra pelo relógio

**Status: vigente — mudança de TELA e de REDAÇÃO, não de formulação** (v1.4.3, continuação). Pedido
do Otávio, 21/10 (noite); esperado registrado antes (`resultados/trava_clt_2026-10-21/ESPERADO.md`,
acréscimo da noite).

- **Textos:** todos os textos da tela e as mensagens do resultado reescritos para um gestor de
  enfermagem que usa a ferramenta pela primeira vez, sem termos de Pesquisa Operacional ("solver",
  "gap", "etapa 1/2", "veredito", "piso", "conta prévia", "inviável") nem siglas sem explicação.
  A linha pequena sob cada critério saiu; a explicação toda vai para o "?". Só a redação muda:
  nenhuma conta, nenhum número; as frases que o TCC cita ("Faltam N; o menor quadro viável é X",
  "O quadro informado admite escala legal", "Não há escala legal até N") ficam. Muda o
  complemento da frase sem prova de ótimo (o "gap"). Antes × depois:
  `resultados/textos_tela_2026-10-21.md`. Cada exemplo do "?" foi conferido pela contagem da
  ferramenta (`avaliacao.py`); dois exemplos foram corrigidos (o texto, não a conta): o de dias
  seguidos passa ao limite padrão (5 → 6 dias = 1 violação), e os de fim de semana dizem que
  valem para sábado e domingo.
- **Campo "Tempo máximo para gerar a escala (minutos)"**, o antigo "Orçamento do clique", com a
  mesma chave (`orcamento`) e o mesmo padrão (60 min).
- **Tema claro:** `.streamlit/config.toml` com `base = "light"`. *Revisado no mesmo dia (21/10,
  Otávio, ao ver a tela): tema **escuro**, `base = "dark"` — o claro ficou feio.*
- **Barra pelo relógio:** fração = tempo decorrido ÷ tempo máximo, até 99% enquanto calcula, com o
  texto da parte em que está; ao terminar, completa até 100% em ~3 s e só então mostra o
  resultado. *Implementação (Claude Code, não óbvia):* o cálculo (`fe.verificar`) roda numa
  thread de trabalho que não chama o Streamlit; a thread do script espera por ela em passos de
  até 1 s, anda a barra e desenha a escala provisória. Nenhuma chamada do Streamlit sai da
  thread do script, por isso não foi preciso `add_script_run_ctx` (o plano B não foi usado). Se
  a tela for reexecutada no meio, o cálculo para na próxima parte, como antes. A barra não muda
  o resultado (medido: mesmo caso com e sem a barra, mesmo resultado; tempo no relatório).
- **Fora do escopo, ficam:** os alertas do COFEN e as mensagens de erro de dado são escritos em
  `instancia_br.py` (intocado); a tela ganhou uma legenda que explica QP e IST.
- **Testes atualizados com registro** (precedente do 1-2): 8, 12, opB-tela, pref-tela, max-dias
  (textos que mudaram). A suíte da v1.4.3 roda uma vez, depois da revisão do Otávio.

---

## 2026-10-22 — Divisão proporcional do tempo máximo; resultado por nível; seção 5 enxuta

**Status: vigente — mudança de PARÂMETRO DE PROJETO (tempo) e de TELA, não de formulação**
(v1.4.3, acréscimo; revisa o item b de "2026-10-19 — Opção B: mecanismo, tempo e critérios
expostos"). Pedido do Otávio, 21–22/10; esperado registrado antes
(`resultados/trava_clt_2026-10-21/ESPERADO.md`, acréscimo de 22/10).

**Problema.** Cada resolução recebia min(1.800 s, o que resta). Com 20 min a etapa 2 podia não
rodar; com 3 níveis separados, o nível 3 e a etapa 2 ficavam sem tempo; com 120 min cada parte
seguia presa em 30 min. O campo da tela não se comportava como o gestor espera.

**Regra (parâmetro de projeto, sem calibração; sensibilidade só se o orientador pedir).**
Etapa 1 : etapa 2 = 50 : 50; dentro da etapa 1, Essencial : Importante : Desejável = 50 : 30 : 20.
Níveis fundidos num bloco somam os pesos; nível vazio não entra. No início de cada parte k:

    tempo_k = tempo que resta × peso_k ÷ (soma dos pesos das partes que ainda faltam, incluindo k)

A sobra de quem termina antes passa adiante, redividida na mesma proporção. Vale sobre o tempo
que resta em cada quadro tentado: quadros recusados pela conta prévia não gastam tempo;
tentativas sem escala gastam. **Proteção da primeira escala:** a primeira resolução do quadro
recebe a sua fatia; se ela acabar sem escala, segue com todo o tempo que resta. Os níveis
seguintes e a etapa 2 partem da escala anterior. Sem teto fixo de 1.800 s.

**Decisões de implementação (Claude Code, 22/10; não óbvias):**
1. **Leitura dos pesos com nível vazio.** A leitura literal ("nível vazio não entra", os outros
   pesos como estão) daria, no padrão fundido Essencial+Importante a 60 min, 0,40 : 0,50 → 26,7 +
   33,3 min, e não os 30 + 30 que o pedido manda conferir. Adotado: **a etapa 1 fica sempre com
   50%**, e os 50 : 30 : 20 se dividem entre os níveis presentes. Com os três níveis separados dá
   0,25 / 0,15 / 0,10 / 0,50, como no pedido; o padrão dá 30 + 30. Levado ao Otávio.
2. **Proteção = resolver de novo.** O HiGHS, pelo Pyomo, não aceita "pare no tempo t se já houver
   escala; senão continue". A proteção roda a resolução de novo com o tempo que resta,
   recomeçando do zero (sem escala não há de onde partir). Custo declarado: o tempo da fatia é
   gasto duas vezes no pior caso.
3. **`TEMPO` e `TEMPO_ETAPA2` viram teto opcional, só para os testes** (`None` no produto). Os
   testes os põem em 600 / 180 s (ou 25 s e 3 s no teste 8) para encurtar as rodadas; com teto,
   a cadeia da primeira resolução (com a proteção) também não passa dele. Chamada direta de
   `resolver_com_objetivo` sem prazo usa o teto por resolução, como antes.
4. **Resultado por nível, em vez de um gap só.** Provado: "<Nível>: N violações — a melhor
   possível."; sem prova: "… Nenhuma escala tem menos de M." (M = limite inferior do solver,
   arredondado para cima, nunca acima de N), ou "Não deu tempo de saber quanto dá para melhorar"
   se o limite for 0; não rodou: "não deu tempo de otimizar; a escala mantém o resultado dos
   níveis acima". **Bloco fundido:** o objetivo soma os níveis com coeficientes (o de cima =
   máximo do resto do bloco + 1), e o limite inferior não é contagem de violações. O M é dado só
   para o nível de cima, M = ⌈(limite − (coef − 1)) ÷ coef⌉, porque o resto do bloco vale no
   máximo coef − 1. A frase principal perde o gap ("Escala gerada; pode haver uma melhor."). As
   três frases citadas no TCC não mudam.
5. **Defeito corrigido de passagem:** em `_niveis_em_sequencia`, o resultado "provado" de cada
   bloco era guardado no nome `p`, o mesmo da classificação que `expressao_pedidos` lê no bloco
   seguinte. Com pedido sem nível (caminho antigo), linhas na tabela de pedidos e dois blocos ou
   mais, isso daria erro de tipo. Renomeado (`prova`). Nos casos que funcionavam, nada muda no que
   vai ao solver.

**Seção "5. Resultado" enxuta (só texto e arrumação):** alerta de descanso semanal em uma linha
(o texto mora em `ferramenta.alertas_descanso`; o fundamento — Súmula 110, OJ 355, 24 + 11 = 35 h,
bordas — vai para o "?"); diferença entre categorias sem número negativo ("a menos" / "a mais");
"maior sequência de trabalho na escala", "menor descanso entre turnos", "menor descanso
semanal" (medidas, não regras); legendas num painel "Detalhes da escala", fechado; "sem pedidos"
no lugar de "0 de 0"; uma frase por nível acima das linhas daquele nível na tabela "Resultado
por critério"; "Equilíbrio entre colegas: o melhor possível / pode haver uma escala mais
equilibrada".

**NUMEROS_TCC não muda:** os números foram medidos com os limites antigos, declarados no arquivo.

---

## 2026-10-22 — Bateria HiGHS × SCIP: casos, regras, critério e regra de troca

**Status: vigente — DESENHO EXPERIMENTAL registrado ANTES de rodar** (ok do Otávio, 22/10, depois
da Fase 0 em `resultados/solvers_2026-10-22/relatorio_fase0.md`). Origem: reunião de 22/10 — o
orientador pediu uma tabela de comportamento computacional por caso e sugeriu o SCIP (gratuito);
o CBC fica fora (na experiência dele, resultado ruim). Não há motivo registrado para a escolha
original do HiGHS. **Nada da ferramenta muda nesta bateria.**

**Casos (8), a partir do `NUMEROS_TCC.md`:**
1–4. `sprint01`, `sprint02`, `long01`, `long02` — os 4 ótimos de Santos et al. (2016), Tabela 6
   (56, 58, 197, 219); modelo INRC (`modelo.construir`), objetivo único.
5. `medium_late05` — o alvo de validação do INRC que o HiGHS não provou (224 contra 107
   publicado; seção 1).
6. A36_livre com quadro 30 (10 enfermeiros + 20 técnicos, a composição da regra `equipe`, a do
   menor quadro viável da fase 2) — ferramenta, classificação padrão.
7. A36_fixo com quadro 30 (10 + 20; 29 linhas "Só este turno", Essencial) — ferramenta.
8. B11_livre com quadro 89 (15 + 74) — **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA**
   (`DESCANSO_POR_TURNO = {"D12": 11}`). É o único caso B que usa solver: o B36 é recusado pela
   conta prévia até 101, sem solver, e não compara solvers. *Leitura adotada de "B" (Claude
   Code); levar ao Otávio.*

**Regras, iguais para os dois:**
- o mesmo modelo (identidade provada na Fase 0, com controle); no SCIP, o objetivo vai direto como
  custo (`ScipObjetivoDireto`), e não no epígrafo que a interface do Pyomo 6.10.1 cria;
- **600 s por caso**: nos casos INRC, uma resolução de 600 s; nos da ferramenta, os 600 s
  divididos pela regra da v1.4.3 ("2026-10-22 — Divisão proporcional do tempo máximo"), com a
  proteção da primeira escala e a etapa 2 (com a classificação padrão: um bloco e a etapa 2,
  300 + 300 s no início);
- gap relativo de parada **0,01%** e **1 thread** nos dois (HiGHS: `mip_rel_gap`, `threads`; SCIP:
  `limits/gap`, `lp/threads`);
- a mesma máquina (i5-10210U, 11,8 GB) e a mesma sessão; os dois solvers um depois do outro, caso
  a caso; o **HiGHS roda de novo** (nenhum log antigo é reaproveitado);
- toda escala passa pelo **avaliador oficial** (INRC: `validar.avaliar`; ferramenta: o mesmo
  caminho da fase 2, `fase2.avaliador`, com o XML da instância e os pedidos);
- memória: a bateria só começa com ≥ 3 GB livres, e a memória livre é registrada antes de cada
  caso.
- Implementação: `docs/diagnostico/bateria_solvers.py`. Nos casos da ferramenta, a bateria chama
  `ferramenta.resolver_com_objetivo` (a ferramenta como está) e troca, só no processo da
  bateria, a função que chama o solver (`ferramenta.resolver`) por uma que usa o HiGHS ou o SCIP
  com as regras acima. O HiGHS vai pelo appsi, como na ferramenta, com 1 thread e o gap
  explícitos.

**O que se registra, por caso × solver × nível** (nível = cada bloco da etapa 1, e a etapa 2):
variáveis, restrições, tempo da etapa, melhor escala (limite superior), melhor limite inferior,
gap (a mesma fórmula nos dois: (escala − limite) ÷ |escala|), ótimo provado (sim/não), e o
avaliador oficial na escala final do caso.

**Vitória por caso** (Otávio, 22/10): o SCIP vence o caso se **provar o ótimo onde o HiGHS não
prova**, ou, quando **nenhum dos dois prova**, se achar uma escala de **valor menor**. Vale o
simétrico para o HiGHS. **Gap menor, sozinho, não conta.** O resto é empate (inclusive os dois
provarem). Nos casos da ferramenta, conta a etapa 1 (o valor da classificação do gestor); a etapa
2 é registrada, não decide.

**Regra de troca:** a ferramenta passa para o SCIP se, e somente se, (i) o SCIP vencer mais casos
do que perder, (ii) não perder nenhuma prova de ótimo que o HiGHS consegue e (iii) passar na suíte
completa depois da troca. Senão fica o HiGHS, e a comparação entra no TCC como avaliação a
posteriori.

**Por que a exigência:** a troca custa ~15 a 20 h de máquina e refazer as seções 1 e 5–14 do
`NUMEROS_TCC.md`, perto da entrega; só se justifica com ganho real para o gestor.

**Afirmação fraca:** tempos de uma máquina e de uma configuração só; vão ao texto como
comportamento observado nessas condições, nunca como resultado geral sobre os solvers.

---

## 2026-10-22 — Anomalia do medium_late05 (HiGHS): folgas soltas na solução sem prova

**Status: vigente — ACHADO DE DIAGNÓSTICO; correção na ferramenta PROPOSTA, não implementada**
(`PROPOSTAS.md`, P20). Diagnóstico pedido pelo Otávio depois da bateria HiGHS × SCIP; só o HiGHS,
nas condições da bateria (600 s, gap 0,01%, 1 thread). Script `docs/diagnostico/
anomalia_medium_late05.py`; saída `resultados/solvers_2026-10-22/anomalia/diagnostico.json`.

**O que se viu (reproduzido):** o HiGHS parou no limite sem prova e informou 7.435; a escala
carregada vale 2.199 no avaliador oficial e no `avaliacao.py` (sem violação de restrição dura).

**Nenhum dos dois números está errado — medem coisas diferentes:**
- 7.435 é o objetivo do **modelo** no ponto que o HiGHS entregou: o valor informado pelo appsi
  (`best_feasible_objective`), o do próprio HiGHS, o objetivo recalculado nas variáveis
  carregadas e custo × valor das colunas dão todos 7.435;
- 2.199 é a **penalidade verdadeira da escala** (as variáveis de atribuição desse mesmo ponto);
- **não é tolerância de integralidade**: o maior desvio de 0/1 nas 5.160 variáveis inteiras é
  0,0;
- **causa: folgas e auxiliares soltas.** No modelo, cada folga só tem limite inferior (α ≥
  excesso), e a minimização é que a aperta; num ponto sem prova, o solver pode entregar α maior
  que o necessário. Por família, modelo × escala: mínimo de turnos 666 × 0; máximo de folgas
  seguidas 777 × 7; mesmo turno no fim de semana 2.480 × 440; mínimo de dias seguidos 1.440 ×
  516; máximo de turnos 516 × 78; fim de semana completo 480 × 240 (este por auxiliares de
  início de bloco); iguais onde o custo cai direto na atribuição (habilidade 310, pedidos 47 e
  30, máximo de dias seguidos 96).
- Nos pontos **provados ótimos** isso não acontece (folga solta aumentaria o objetivo): os 4
  ótimos de Santos batem com o avaliador, como sempre bateram.

**Na bateria:** só o medium_late05 com HiGHS teve a diferença (SCIP: 318 e 318). A linha certa é
**escala 2.199** (o valor do modelo, 7.435, fica registrado ao lado); o gap pela escala é
(2.199 − 59) ÷ 2.199 = 97,3%. A vitória do SCIP não muda (318 < 2.199). Nos casos da ferramenta
sem prova (A36_livre com SCIP, 15; B11 com HiGHS, 57), o valor do modelo bate com o recalculado
na escala gravada pelo próprio `prioridades.resultado`: a classificação padrão só tem custo direto
na atribuição (pedido de folga e enfermeiro em posto de técnico), sem folgas.

**Pode afetar a ferramenta?**
- **O que a tela mostra, não:** os números por critério ("Resultado por critério", pedidos, "N
  violações") são contados na escala pelo `avaliacao.py`, fora do modelo; o M ("nenhuma escala
  tem menos de M") vem do limite inferior, que continua valendo.
- **O que a ferramenta carrega adiante, sim, em tese:** o valor de um nível sem prova é preso para
  os níveis seguintes (`expr ≤ z`, opção B em sequência) e para a etapa 2 (penalidade ≤ z, P14).
  Com folgas soltas, esse z é maior que o valor verdadeiro da escala, e o nível seguinte ou a etapa
  2 poderiam piorar a contagem verdadeira de um nível acima até z — o contrário do que a P14 e a
  opção B prometem ("sem piorar"). Só acontece com critérios de folga considerados pelo gestor
  (mínimos e máximos de dias, folgas, fins de semana, turnos, preferências) **e** um nível que
  termine sem prova. Na classificação padrão não acontece (sem folgas). Não observado em
  nenhuma rodada registrada; correção proposta (P20), não implementada.

---

## 2026-10-23 — P20 aprovada: trava pelo valor verdadeiro depois de nível sem prova

**Status: vigente — mudança de IMPLEMENTAÇÃO do mecanismo de níveis (o modelo não muda).**
Aprovada pelo Otávio em 23/10, depois do diagnóstico "2026-10-22 — Anomalia do medium_late05
(HiGHS): folgas soltas na solução sem prova"; `PROPOSTAS.md`, P20. Registrada antes de
implementar; esperado em `resultados/p20_2026-10-23/ESPERADO.md`.

**Decisão.** Ao fechar um nível **sem prova**, a trava f_k ≤ valor usa o valor **recalculado na
escala** — as folgas e auxiliares apertadas ao mínimo que a escala exige —, e não o valor do
modelo no ponto entregue pelo solver. A escala de partida do nível seguinte vai com as folgas
recalculadas, para não violar a nova trava. Vale também para a trava da etapa 2 (penalidade ≤ z,
P14). Nível com prova: nada muda.

**Como (decisão de implementação, Claude Code):** fixar as atribuições `x` da escala, resolver de
novo só as folgas e auxiliares (o objetivo do nível continua o mesmo; `y` sai de `x` por
igualdade), soltar o `x`. É o próprio modelo que dá o mínimo — a mesma semântica, sem uma segunda
contagem que pudesse divergir. Limite do aperto: min(60 s, o que resta), no mínimo 1 s; se falhar,
fica o valor do modelo (como antes) e isso é registrado. O LP enviado na primeira resolução de cada
nível não muda — a identidade 243/243 e 24/24 tem de continuar valendo.

**Por quê.** Com folgas soltas, a trava fica frouxa e o que vem depois pode piorar a contagem
verdadeira de um nível acima — o contrário do que a opção B e a P14 prometem ("sem piorar").

**Suíte:** não roda agora (fica para sexta à noite, decisão do Otávio); rodam o teste novo e os
testes rápidos da opção B.

---

## 2026-10-23 — Sensibilidade ao tempo, HiGHS × SCIP, 3.600 s por caso

**Status: vigente — ANÁLISE DE SENSIBILIDADE, registrada ANTES de rodar.** Pedido do Otávio, 23/10.
**Não reabre a regra de troca de 22/10** ("2026-10-22 — Bateria HiGHS × SCIP"): qualquer resultado
entra no texto; se o SCIP passar à frente, isso vai ao Otávio e ao orientador, sem troca
automática. Nada da ferramenta muda.

**Código da ferramenta:** commit `ed621a2` (já com a P20); cada caso registra o commit e se havia
mudança em `src/` (não deve haver).

**Casos (3):** `medium_late05` (INRC), `A36_livre_30` (10 + 20) e `B11_livre_89` (15 + 74,
HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA) — os três em que a bateria de 22/10 não
empatou. **4º caso: não cabe.** Os três usam o tempo inteiro nos dois solvers (na ferramenta, a
etapa 2 nunca provou e vai até o limite), então são 3 × 2 × 3.600 s = 6 h; um 4º somaria 2 h, e
com montagem, aperto e avaliador passaria das 8 h pedidas.

**Regras (as de 22/10):** o mesmo modelo; **3.600 s por caso** (o orçamento padrão da ferramenta;
nos casos da ferramenta, divididos pela regra da v1.4.3: com a classificação padrão, um bloco e a
etapa 2, 30 + 30 min no início, com a proteção da primeira escala); gap 0,01%; 1 thread; a mesma
máquina e a mesma sessão; caso a caso, os dois solvers um depois do outro; o HiGHS roda de novo;
toda escala passa pelo avaliador oficial. Limite duro por processo: 7.200 s (passou, o processo é
encerrado e registrado). Memória: ≥ 3 GB livres antes de cada caso (espera até 15 min; senão para
e registra); a memória livre é registrada. A máquina não suspende (o driver pede ao Windows).
Saída: `resultados/solvers_2026-10-23_3600/`. Comando: `python docs\diagnostico\
bateria_solvers.py --todos --limite 3600 --saida resultados\solvers_2026-10-23_3600 --casos
medium_late05 A36_livre_30 B11_livre_89`.

**Ajuste ao registro (Otávio, 23/10):** em todo caso **sem prova**, o "valor" de cada solver é o da
**escala** — recalculado fora do modelo e conferido no avaliador oficial —, não o do modelo (ver
"2026-10-22 — Anomalia do medium_late05"). A tabela registra os dois; **a vitória conta pela
escala**. No INRC, o da escala é o `avaliacao.py` (que bate com o avaliador oficial); na
ferramenta, cada bloco da etapa 1 recontado na escala entregue (`prioridades.resultado`,
coeficiente × violações).

**Critérios com folga (para a P20 não interferir):** os dois casos da ferramenta usam a
classificação padrão — só pedido de folga (Essencial; o A36_livre e o B11 não têm pedidos) e
enfermeiro em posto de técnico (Importante), que caem direto na atribuição, sem folgas; cada caso
registra `familias_com_folga_consideradas` (esperado: vazio). O aperto da P20 roda (é o
comportamento da ferramenta em nível sem prova), mas sem folgas não muda o valor; fica registrado.
O `medium_late05` é INRC: tem restrições com folga, mas é resolvido direto (`modelo.construir`), fora
do mecanismo de níveis — a P20 não age nele, e o valor da escala vem do `avaliacao.py`.

**Afirmação fraca:** uma máquina, uma configuração, uma rodada por caso.

---

## 2026-10-23 — Caso A: classificação dos critérios pela escala real e sensibilidade (2 ordens)

**Status: vigente — DESENHO EXPERIMENTAL registrado ANTES de rodar** (Orientação, 23/10). Código
congelado na v1.4.4: nada em `src/` muda. Esperado: `resultados/caso_a_pratica_2026-10-23/
ESPERADO.md`. Script: `docs/diagnostico/caso_a_pratica.py`.

**Base.** `D:\TCC\escrita\fontes\FICHA_CASO_REALISTA.md`, seção "Contagem na escala real
(23/10/2026)" (corrigida pela Orientação em 23/10), e a transcrição célula a célula da p. 70 de
Massens (2019), `D:\TCC\escrita\fontes\transcricao_anexoB_massens.csv` (24 linhas, 26/10 a
25/11). **Regra de classificação:** violado em alguma ocorrência → Não considerar; nunca violado,
com ocorrência → Importante; sem evidência → padrão da ferramenta; Essencial só para regra
declarada na fonte (turno fixo). **Limites = os padrões da ferramenta, não calibrados ao
hospital.** A contagem é sobre a escala do hospital no formato do INRC; não afirma descumprimento
de lei.

**Recontagem independente** (`caso_a_pratica.py --recontar`; `recontagem.md`): lê o CSV com as
leituras da ficha e conta cada critério com o `avaliacao.py` (o noturno na véspera, com o contador
da ferramenta, que o `avaliacao.py` não pontua), sem reaproveitar o script do chat. Calendário: a
transcrição não marca o fim de semana; os P das linhas diurnas só fecham com 27/10 num sábado
(2018; 02/11 sexta e 15/11 quinta são as duas colunas sombreadas fora do fim de semana) — o script
confere. **Resultado, com a leitura C abaixo: os 13 critérios contáveis ficam do mesmo lado da
ficha.**

**Leitura da borda — a posteriori, 23/10 (leitura C).** Ressalva: formulada **depois** de a
recontagem expor a divergência entre a regra escrita na ficha (tirar todo bloco de borda) e a
contagem da ficha (que, nos fins de semana, contou os blocos de borda). Motivo, independente do
resultado:
- **borda do mês:** nos critérios de **máximo**, o bloco conta (se já passa do limite dentro do mês,
  a violação é certa, qualquer que seja o resto); nos de **mínimo**, sai (pode continuar fora da
  imagem);
- **férias:** o bloco que toca as férias **sai sempre** (o fim das férias não se lê na imagem; o
  branco de 21 a 25/11 do 5976 pode ser continuação). Isso descarta a leitura B.

As três leituras e o que cada uma dava (com o `avaliacao.py`):

| Leitura | Máx. fins de semana seguidos | Máx. folgas seguidas | Reproduz a ficha? |
|---|---|---|---|
| A — tirar todo bloco que toca a borda do mês ou as férias (a regra antes escrita na ficha) | nunca violado | nunca violado | não |
| B — nos de máximo, contar os blocos de borda e os que tocam as férias; nos de mínimo, tirar | violado (26, em 14 pessoas) | violado (1: o 5976, 21 a 25/11, logo depois das férias) | não |
| **C** — nos de máximo, contar o bloco de borda do mês; nos de mínimo, tirar; o que toca as férias, sempre tirar | violado | nunca violado | sim |

**"Mesmo turno no fim de semana":** vale a semântica do `avaliacao.py`/avaliador oficial (trabalhar
um só dia do fim de semana já viola: 93 violações, 21 pessoas). A ficha foi corrigida pela
Orientação (dizia "sem ocorrência"). Classificação: Não considerar, agora por evidência.

**Linhas contadas — a posteriori, 26/10** (Orientação). Na contagem da escala real (a evidência para
classificar os critérios) entram **só as linhas do Anexo B com pelo menos um registro: 21 de 24**.
Ficam fora as três linhas sem nenhum registro: **6118 e 4798** (enfermeiros diurnos) e **6089**
(integral). Motivo: linha vazia não mostra prática; pela leitura "dia útil em branco = trabalho", ela
viraria trabalho em todo dia útil, e o vazio no fim de semana só seria folga por suposição. Apoio: no
Apêndice A de Massens (escala recriada pelo algoritmo do autor), o enfermeiro diurno faz plantão de
supervisão em alguns fins de semana (fichamento MAS-014, `D:\TCC\escrita\fontes\fichamentos\Camada 7
...\massens.md`). **A entrada do caso não muda:** o caso continua com 24 pessoas, e as rodadas de 21
e 24/10 continuam valendo. A Orientação conferiu à mão que os três critérios nunca violados (máx.
folgas seguidas 4, mín. fins de semana seguidos 2, mín. turnos 10) continuam nunca violados sem as
três linhas; recontagem com as 21 linhas em `recontagem.md` (a de 24 linhas fica como histórico).
Se algum critério mudasse de lado, a regra era parar e levar à Orientação.

**As duas ordens:**
- **Ordem 1 (a prática):** Essencial = as linhas "Só este turno" da A36_fixo (29 linhas); Importante =
  máx. folgas seguidas (4), mín. fins de semana seguidos (2), mín. turnos (10) e enfermeiro em posto
  de técnico; todo o resto, Não considerar (pedido de folga: não há pedidos).
- **Ordem 2:** máx. fins de semana seguidos (3) no Essencial; as linhas "Só este turno" no
  Desejável; o resto igual à ordem 1.

**Rodadas (3):**
1. A11_fixo com 24 (4 enfermeiros + 20 técnicos), **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA
   FERRAMENTA** (`DESCANSO_POR_TURNO = {"D12": 11}`), ordem 1;
2. A36_fixo com 30 — 10 enfermeiros (os 4 da unidade: 6118, 4798, 4969 e 5993, mais 6 acrescidos
   pela regra `equipe`, Enf 5 a Enf 10) + 20 técnicos, a composição que a busca achou em 21/10
   (informada direto; conferido sem solver que a instância é a mesma que a busca montou) —, ordem 1;
3. A36_fixo com 30, ordem 2.

**Regras:** orçamento padrão de 60 min por rodada (regra de tempo da v1.4.3, com a P20); uma rodada
por processo; ≥ 3 GB livres antes de cada uma (registrado); suspensão do Windows desativada; na
ordem acima, a A11 primeiro e até o fim (regra de 03/10); retomada pula o que já tem resultado. Se
a noite der problema, a ordem 2 é a primeira a sair. Os resultados separam os 4 enfermeiros da
unidade dos 6 acrescidos.

**Conferência:** avaliador oficial nas três escalas (restrição dura). Por critério, a contagem da
ferramenta comparada com o avaliador oficial numa instância com os critérios da ordem ligados e
peso 1, onde o avaliador pontua; onde não pontua (enfermeiro em posto de técnico), "sem conferência
externa". Máx. fins de semana seguidos nas **duas** escalas do A36, avaliado com o avaliador numa
instância com o critério ligado (a ordem 1 não o tem ligado).

**Números** só vão ao `NUMEROS_TCC.md` depois da aprovação do Otávio. **Afirmação fraca:** um setor,
um mês, uma rodada por ordem; tempo como limite operacional (máquina e solver nomeados).

*31/10: a transcrição passou a ser versionada em resultados/caso_a_pratica_2026-10-23/; mesmo
conteúdo (conferido pela recontagem idêntica).* A cópia foi feita de
`D:\TCC\escrita\insumos\caso_realista\transcricao_anexoB_massens.csv` e é idêntica byte a byte.
O `recontagem.md` gerado de novo por `caso_a_pratica.py --recontar` só difere do anterior no
caminho da linha "Fonte"; todas as contagens são iguais.

---

## 2026-10-26 — Limitações declaradas: duração diária do turno e limite semanal de horas

**Status: vigente — declaração, sem mudança de código** (Orientação, 26/10).

**O que a v1.4.4 aceita.** Turnos com início de 0 a 23 h e duração de 1 a 24 h, em hora cheia
(validação dos turnos em `instancia_br.py`, `_validar_turnos`; duração por `ferramenta.duracao`).
Carga contratual de 30, 36, 40 ou 44 h por semana (`instancia_br.CARGAS_CONTRATUAIS`), com o teto
sobre o horizonte, não por semana ("2026-10-02 — Carga por contrato", item b, motivo registrado lá:
o 12×36 tem semanas de 48 h compensadas por semanas de 36 h).

**O que não é verificado:**
- a **duração máxima diária do turno** (CLT, arts. 58, 59 e 59-A): um turno de 1 a 24 h é aceito;
- um **limite semanal de horas**.

Para a duração do turno **não há motivo registrado**; é **limitação declarada a posteriori**. Para
o limite semanal, o motivo é o do item b de 02/10.

**Frase admitida no texto:** "A ferramenta não verifica a duração máxima diária do turno, que aceita
de 1 a 24 h, nem um limite semanal de horas; a carga contratual é limitada no horizonte de 28 dias."

---

## 2026-10-26 — Capturas da tela da v1.4.4 para o texto (4.7)

**Status: vigente — registrada ANTES de rodar** (Orientação, 26/10). Código congelado: nada em
`src/` muda.

**O quê.** Uma rodada da demonstração com 18 técnicos (`docs/demonstracao`, a rodada
`rodada2_18tec`) na v1.4.4, **só para as capturas** (tela de entrada e resultado). Gravada com o
nome `rodada2_18tec_v144`, para não sobrescrever os arquivos de 09/10, que são a origem da seção 9
do `NUMEROS_TCC.md`.

**Exceção** à regra "sem solver depois de 24/10". Motivo: as capturas anteriores a 21/10 estão
superadas pelos textos da tela de 21/10.

**Esperado** (= `NUMEROS_TCC.md`, seção 9, as linhas "conta antes"):
- frase "Falta 1; o menor quadro viável é 29";
- motivo "Alternância" (ter 03/11 e qua 04/11: 28 plantões, 27 pessoas), **único motivo**;
- o alerta do QP.

**Regras.** Nenhum número novo vai ao NUMEROS nem ao texto. Se a frase, o menor quadro ou o motivo
diferirem, **parar e relatar** (é achado, não captura). Se o `capturas.py` precisar de ajuste aos
textos novos da tela, ajustar só em `docs/demonstracao`. Execução longa: o menor caso até o fim antes
(regra de 03/10) — aqui, o preenchimento da tela sem gerar (`--so-preencher`), antes da rodada.

---

## 2026-11-05 — Limitações declaradas: intervalo intrajornada (art. 71) e hora noturna reduzida (art. 73, § 1º)

**Status: vigente — declaração a posteriori, sem mudança de código** (pedido do Otávio, 04/11).

**O que a ferramenta faz.** Cada turno é um bloco contínuo, com início e duração. As horas de um
turno são a duração pelos horários (`instancia.Turno.duracao_h`), e é essa duração que entra no
teto de horas do contrato (`modelo.py`, restrição (IV), `carga_horaria`) e no descanso exigido
depois do turno (`instancia_br.descanso_exigido`, chamada pelo gerador de pares
`pares_proibidos_por_horario`).

**O que não é modelado:**
- o **intervalo para repouso ou alimentação** (CLT, art. 71): não há pausa dentro do turno, e o
  intervalo não é descontado das horas;
- a **hora noturna reduzida** de 52 min 30 s (CLT, art. 73, § 1º): o turno noturno conta pelas
  horas do relógio.

**Não há motivo registrado.** É limitação declarada a posteriori, como a de 26/10 ("Limitações
declaradas: duração diária do turno e limite semanal de horas").

---

## 2026-11-04 — Caso A: entrada revista pela leitura independente do Anexo B; rodadas na v1.4.5

**Status: vigente — DESENHO EXPERIMENTAL registrado ANTES de rodar; aprovado pelo Otávio em
04/11/2026, validado pela Orientação.** É mudança de desenho experimental com o código congelado:
**tudo roda na v1.4.5 (tag `v1.4.5`, `634eeb5`), e nada em `src/` muda.** A entrada de 20/10
(`resultados/caso_a_2026-10-20/entrada.py`) e os resultados de 21 e 24/10 ficam como estão, como
registro do que rodou. Exceção ao congelamento dos números de 25/10, por decisão do Otávio.
Pedido: `D:\TCC\escrita\plano_noite\PROMPT_CLAUDE_CODE_RODADAS_v145.md`. Entrada nova, esperado e
resultados em `resultados/caso_a_2026-11-04/`; scripts em `docs/diagnostico/caso_a_v145.py` (as
rodadas) e `docs/diagnostico/caso_a_pratica.py --recontar --v2` (a recontagem).

**Motivo.** O Capítulo 5 juntava números de três versões (v1.4.1, v1.4.3/`ed621a2` e v1.4.4), e a
entrada tinha suposições que a própria fonte permite evitar. Uma leitura independente de Massens
(2019), feita num chat só com o PDF, e a conferência do Otávio na p. 70 levaram às decisões abaixo.

**Decisões:**
- **(a) Janela real do Anexo B:** 29/10 a 25/11/2018, 28 dias a partir de uma segunda. O Anexo B
  vai de 26/10 a 25/11; descartam-se 26 a 28/10. Substitui o mês de janeiro de 2027 e as datas
  supostas das férias. Os feriados de 02/11 e 15/11 (colunas sombreadas em dia útil) ficam **sem
  ajuste de demanda**, porque o Anexo B não muda nada nessas colunas. A ferramenta aceita 2018
  (conferido sem solver).
- **(b) Férias reais, pela faixa cinza** (conferida pelo Otávio na p. 70): o 6137 de 31/10 a
  15/11; o 5976 de 15/11 até o fim da janela.
- **(c) Equipe de 23:**
  - 4 enfermeiros: 6118 (manhã), 4798 (tarde), 4969 e 5993 (noite);
  - 19 técnicos: manhã 5762, 6262, 5697, 6017 e 6209; tarde 6003, 6052, 6271, 6187 e 6137; noite A
    4158, 5595, 5976 e 5337; noite B 4178, 5923, 4789 e 3602; e o volante 4309, como técnico de
    noite.
  - **O 4309 como técnico tem evidência dividida; é decisão do Otávio.** A favor: na escala do
    setor ele segue o regime dos técnicos noturnos (folgas de fim de semana, que os enfermeiros
    noturnos não têm), e a folga do Téc. 17 do Apêndice A (27/10) só aparece no Anexo B na linha
    dele. Contra: o texto chama de enfermeiros os volantes do hospital (p. 47).
  - **A linha 6089 sai da equipe:** o horário dela (8–12:30/13:30–17:48) não corresponde a nenhum
    turno e a linha não tem nenhum registro; o Apêndice A tem 22 pessoas (4 enfermeiros e 18
    técnicos). A sensibilidade da conta prévia com 22, 23 e 24 cobre as duas linhas.
  - Os cartões-ponto são usados como nomes.
- **(d) Demanda:**
  - dias úteis: manhã 1 enfermeiro + 5 técnicos, tarde 1 + 5, noite 1 + 4, plantão 0 + 0;
  - fim de semana: manhã 0, tarde 0, noite 1 + 4 e **plantão diurno 0 enfermeiro + 5 técnicos**.
    O Anexo B não tem enfermeiro no fim de semana; a Tabela 13 tem 2 enfermeiros no fim de semana
    para os quatro setores.
  - Turnos como antes: M 7–13, T 13–19, N 19–7, D12 7–19.
- **(e) Turno fixo para todos com horário na escala:** linhas "Só este turno", sem dia. Cada técnico
  da manhã tem M e D12, cada técnico da tarde T e D12, cada técnico da noite e o 4309 N, e os
  enfermeiros 6118 M, 4798 T, 4969 e 5993 N. Total: **33 linhas**. Os acrescentados pela busca não
  têm linha nem férias.
- **(f)** Carga de 44 h para todos; grau intermediário (suposição declarada); sem painel de
  pacientes; sem pedidos de folga.
- **(g) Classificação 1 (a prática):**
  - Essencial: as 33 linhas;
  - Importante: máximo de dias livres seguidos (4), mínimo de turnos (10) e enfermeiro em posto de
    técnico;
  - o resto, Não considerar.
  - **O mínimo de fins de semana seguidos sai do Importante** (revisa a ordem 1 de "2026-10-23 —
    Caso A"). Na escala real, toda sequência de fins de semana trabalhados toca a borda do mês ou as
    férias, e pela leitura C nenhuma é contável nos critérios de mínimo. O "nunca violado" de 23/10
    não tinha ocorrência testável, e a regra de 23/10 manda: sem evidência → padrão.
  - **Classificação 2:** máximo de fins de semana seguidos (3) no Essencial e as 33 linhas no
    Desejável; o resto igual à classificação 1.

**Antes de rodar:**
- **Transcrição revista** (`resultados/caso_a_2026-11-04/transcricao_anexoB_massens_v2.csv`): é a v1
  com a faixa de férias completa.
- **Recontagem** pela leitura C, na janela de 31 dias, com o número de ocorrências testáveis de cada
  critério. Se algum lado mudar além do do mínimo de fins de semana seguidos, a mudança é
  registrada e vai ao relatório, e as rodadas seguem com a classificação g), porque a regra foi
  fixada antes.
- **Esperado sem solver** (`ESPERADO.md`). A bateria HiGHS × SCIP **não é refeita**: a regra de troca
  de 22/10 não se reabre, o INRC não mudou e a etapa 1 é idêntica na v1.4.5. A seção fica como
  está, declarada como rodada anterior, com a entrada de 21/10.

**Rodadas, nesta ordem** (orçamento padrão de 60 min por rodada; um processo por rodada; ≥ 3 GB
livres antes de cada uma, com espera de até 15 min; senão, PARADO registrado e segue para a
próxima):
1. A, 36 h, classificação padrão, com as 33 linhas em Essencial (`A36_fixo`) e sem linhas
   (`A36_livre`). Sem importância preenchida, a ferramenta poria as linhas em Desejável
   (`prioridades.importancia_padrao`); o "fixo" da fase 2 usava Essencial.
2. A, 36 h, classificação 1 e classificação 2, no menor quadro e na composição achados na rodada 1.
   Lidos da saída do `A36_fixo` (se ele não determinar, do `A36_livre`; se nenhum determinar, a
   rodada 2 é pulada, com registro).
3. A, **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA** (`DESCANSO_POR_TURNO = {"D12": 11}`),
   classificação 1, equipe de 23.
4. Caso B na v1.4.5: B36 (89) e B11 (89, hipótese), mesma entrada de 20/10 com a janela a), e o
   avaliador oficial em `-Xmx6g`.

**Em toda rodada:**
- frase da tela, prova por nível, valores por nível e por critério e status da etapa 2;
- violações das linhas "Só este turno" por profissional;
- enfermeiro em posto de técnico, separando os 4 da unidade dos acrescentados;
- avaliador oficial: restrição dura e, por critério, com peso 1 numa instância com os critérios da
  classificação ligados (no A36 com as linhas, os da classificação 2, que contém os da 1);
- conferência de descanso no relógio;
- máquina e solver.

As violações **inevitáveis** (as férias contam como dias livres e não reduzem o mínimo de turnos)
são separadas das evitáveis, por critério e por pessoa.

**Números** só vão ao `NUMEROS_TCC.md` depois do ok do Otávio, como proposta de seção 15c.
**Afirmação fraca:** um setor, um mês, uma rodada por classificação; o tempo vale só como limite
operacional (máquina e solver nomeados).

**Nota de 05/11/2026 — avaliador oficial em UTC.** Nas rodadas desta entrada, o avaliador oficial
(Java) rodou com `JAVA_TOOL_OPTIONS=-Duser.timezone=UTC`, posto só no ambiente do script
(`docs/diagnostico/caso_a_v145.py`).
- **Motivo:** o horário de verão de 2018 começou à 0 h de 04/11/2018. Essa meia-noite não existe
  no fuso de São Paulo, e no fuso do Windows a contagem de dias do avaliador perde um dia
  (`ArrayIndexOutOfBoundsException` em `Schedule.<init>`).
- **Controle:** nas instâncias de 2027, a saída do avaliador é idêntica byte a byte com e sem a
  opção (md5 em `A11_fixo_24_ordem1` e `A36_fixo_30_ordem2_conferencia`).
- **`src/validar.py` não muda:** o código está congelado, e o avaliador é de validação, não do
  produto.

---

## Modelo de entrada

```
## AAAA-MM-DD — Título curto da decisão

O que foi decidido, em uma ou duas frases.

Por quê. Se houver fonte, citar.

Ressalva ou consequência, se houver.
```
