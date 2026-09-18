# Diário de decisões — TCC NRP

Registro datado de decisões de modelagem e implementação. Matéria-prima dos capítulos de
formulação e de experimentos.

**Regra:** toda decisão não óbvia entra aqui no momento em que é tomada, com data, o que
foi decidido e por quê. Três linhas bastam. Perguntas abertas ficam na seção final até
serem resolvidas — e então viram entrada datada.

---

## 2026-09-08 — Formulação: atribuição, não janelas

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

O elemento `<Preferred>` do XML **não** é preferência: é a demanda obrigatória.

Fonte: Haspeslagh, De Causmaecker, Stølevik e Schaerf, *First International Nurse
Rostering Competition 2010*, anais do PATAT 2010, p. 499–500. O texto declara a demanda
como restrição rígida e lista apenas duas restrições rígidas — cobrir toda a demanda e no
máximo um turno por enfermeira por dia.

Santos et al. (2016) modelam como igualdade (restrição 1). Consistente.

---

## 2026-09-08 — Atributo `on=` deve ser respeitado pelo parser

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

Alternância estrita (12h trabalho, 36h descanso) implica não trabalhar dois dias
consecutivos, o que dá 14 plantões em 28 dias.

Confere com a realidade legal: o art. 59-A da CLT permite o regime; a lei não fixa carga
semanal, e a jurisprudência entende alternância entre semanas de 36h e 48h, média de ~42h
semanais e ~15 plantões por mês.

Logo **não** é necessário um `MaxNumAssignments` reduzido em separado — a alternância já é
a restrição correta.

Ressalva a registrar no texto: é aproximação em granularidade de dia, não representação
exata das 36 horas de descanso. O avaliador valida o código, não a fidelidade desta
representação.

Verificar antes de citar: PEC 221/19 e projeto do governo discutem limitar a média a 40h
semanais. Citar com data de consulta.

---

## 2026-09-08 — 12×36 é inviável no efetivo original: vira Experimento A

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

O turno `N` do INRC já atravessa a meia-noite (22:30 → 06:30) e a documentação oficial o
trata como pertencente a um dia; as restrições de dias consecutivos operam em dias.

Adotar a mesma convenção para o plantão noturno de 12h da instância brasileira, e citar a
fonte. Não inventar convenção própria.

---

## 2026-09-08 — Limites do que as medições sustentam

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

---

## 2026-09-18 — Semântica das flexíveis validada fora do modelo

A penalidade de uma escala passou a ser calculada também em Python puro, em
`src/avaliacao.py`, e conferida contra o avaliador oficial **antes** de a função objetivo
existir.

Resultado: 207 escalas nas 69 instâncias, penalidade idêntica à do avaliador em todas, par a
par de profissional × restrição. Das 19 chaves de penalidade, 13 foram exercitadas; as 6 que
ficaram em zero são exatamente as que nenhuma instância produz.

Por que isso vale registro: separa erro de semântica de erro de modelagem. Quando a função
objetivo do Pyomo divergir, a dúvida não será mais "entendi a restrição errado ou linearizei
errado" — a semântica já está fixada contra o árbitro externo, e o que sobra é linearização.

Efeito colateral útil: a decomposição por profissional que o Experimento B exige — penalidade
máxima individual, amplitude, dispersão — sai desse módulo, já que o modelo só devolve o
total.

---

## 2026-09-18 — Funcao objetivo: uma folga por violacao, nao por termo

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

## Perguntas abertas

### Fim de semana incompleto no horizonte

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

### Grau de dependência assistencial da instância brasileira

Não está em base pública — é classificação clínica, não cadastral. Decisão: tratar como
**parâmetro experimental** (mínimo, intermediário, intensivo) em vez de suposição fixa.
A confirmar com o orientador.

### Status jurídico do arcabouço normativo de dimensionamento

A Resolução COFEN 543/2017 foi revogada e há decisões judiciais que suspenderam resoluções
sobre dimensionamento; o Parecer Normativo COFEN nº 1/2024 foi aprovado nos limites das
liminares em vigor.

Verificar status atual em fonte primária, com data de consulta, antes de redigir o capítulo
de fundamentação. As conclusões do trabalho devem ser formuladas de modo a **não depender**
da vigência da norma — a norma é origem declarada dos parâmetros, não fundamento das
conclusões.

---

## Modelo de entrada

```
## AAAA-MM-DD — Título curto da decisão

O que foi decidido, em uma ou duas frases.

Por quê. Se houver fonte, citar.

Ressalva ou consequência, se houver.
```
