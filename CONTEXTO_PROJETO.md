# Contexto — Projeto 1 · INRC 1 · Códigos

## 1. Escopo deste projeto

Este projeto cobre **a implementação em código** do TCC: parser das instâncias, modelo em
Pyomo, validação no avaliador oficial, construção da instância brasileira e execução dos
experimentos.

Não cobre: redação de capítulos, revisão ABNT, leitura de artigos, preparação de reuniões
de orientação, nem mudanças de escopo do trabalho. Isso vive em outro projeto
("TCC · Redação e orientação").

Regra de fronteira: se envolve arquivo do repositório de código, é aqui. Se envolve o texto
do TCC ou o orientador, é lá.

## 2. Quem e o quê

TCC 2 de Engenharia de Produção, CEFET-RJ. Tema: Nurse Rostering Problem (NRP).
Orientador: Prof. Ormeu Coelho da Silva Junior.

**Título de trabalho (em validação com o orientador):** adaptação de um modelo de
Programação Inteira para o NRP ao regime de plantão brasileiro, com experimentos sobre as
instâncias do INRC-2010.

**Objetivo geral:** formular e adaptar um modelo de Programação Inteira para o NRP ao
regime de plantão 12×36 e às exigências normativas de composição de equipe de enfermagem
vigentes no Brasil, validando-o sobre as instâncias públicas do INRC-2010 e avaliando o
efeito dessas características sobre a viabilidade da escala e a distribuição da carga entre
profissionais.

## 3. Herança do TCC 1 — leia antes de sugerir qualquer coisa

O TCC 1 já foi entregue: capítulos 1 a 3 redigidos em ABNT (introdução, revisão de
literatura e metodologia). Aquela revisão de literatura é **narrativa**, construída a partir
de artigos selecionados pelo autor sem protocolo formal de busca.

**Aquele texto foi escrito para um escopo diferente:** estudo de caso com coleta de dados
primários em um hospital real do Rio de Janeiro, validação contra a escala manual da
unidade, e delimitação que **excluía** explicitamente habilidades múltiplas e contratos
heterogêneos.

Esse escopo foi abandonado por inviabilidade de prazo — acesso institucional, negociação com
a chefia de enfermagem e tratamento de dados de pessoal consumiriam o tempo restante.

Consequência prática para este projeto: **não tome o texto do TCC 1 como especificação.**
Habilidades e contratos, que lá estavam fora do escopo, aqui são centrais. O reenquadramento
do texto é tarefa do outro projeto.

O que sobrevive do TCC 1 e continua válido: os fundamentos de PL, PI, MILP, branch-and-bound
e branch-and-cut; a caracterização do NRP e sua complexidade; a classificação de restrições;
os dados do CNES/DATASUS sobre a força de trabalho de enfermagem no Rio de Janeiro; e o
levantamento de formulações de IP para o NRP.

## 3.1 Revisão sistemática — primeira entrega do TCC 2

Já concluída, e distinta da revisão narrativa do TCC 1: protocolo Methodi Ordinatio, buscas
em Scopus e Web of Science, 112 artigos extraídos, 110 com formulação própria, consolidada em
planilha de triagem com 26 colunas.

Boa parte dos artigos citados no TCC 1 aparece também nessa base, o que permitirá reescrever
o capítulo de revisão declarando o protocolo — tarefa do projeto de redação, não deste.

Os achados mobilizáveis como justificativa, todos referentes aos 110 artigos com formulação
própria:

| Achado | Valor |
|---|---|
| Visão de formulação predominante | nurse-task 71 (63%) · nurse-pattern 21 (19%) · nurse-day 4 |
| Método predominante | PLI/PLIM por solver 55 (50%) · Goal Programming 25 (23%) |
| Solver mais utilizado | CPLEX 51 · Gurobi 22 · LINGO 18 |
| Modelam nível de habilidade | 53 (47%) |
| Modelam contratos | 34 (30%) |
| Formulação por padrões em algoritmos exatos dedicados | 13 de 14 (93%) |
| Formulação por padrões nas demais abordagens | 12 de 96 (12%) |

## 4. Natureza do trabalho

O objeto é o **modelo** (formulação), não o **algoritmo**. Resolução por solver de
prateleira. Não se escreve algoritmo de busca, metaheurística, matheurística nem geração de
colunas — nem como sugestão de melhoria.

Justificativa: PLI/PLIM resolvido por solver é a abordagem de 55 dos 110 artigos com
formulação própria da revisão (50%), com CPLEX presente em 51. Não é atalho, é o
procedimento padrão da área.

Não é trabalho de competição. O objetivo não é superar as submissões do INRC em tempo ou
qualidade. O afastamento em relação às melhores soluções conhecidas é reportado como
posicionamento, não como resultado adverso.

## 5. Desenho experimental

Duas bases, com papéis distintos e não redundantes:

- **INRC-2010 — base de validação.** Instâncias públicas, avaliador oficial, valores ótimos
  comprovados em Santos et al. (2016). Serve para provar que o modelo está correto. É a
  única oportunidade de conferência externa em todo o trabalho.
- **Instância representativa brasileira — base de experimentação.** Derivada de `long01`
  como molde, reparametrizada com dimensionamento de pessoal de enfermagem brasileiro e
  regime de plantão 12×36. É onde as perguntas de pesquisa são respondidas.

A sequência é deliberada: o INRC prova que o modelo está correto, porque há conferência
externa; a instância brasileira, que não dispõe de referência pública, produz os resultados.

Verificou-se que a instância brasileira **cabe dentro do esquema XML oficial** — não exige
extensão do formato. Logo o avaliador oficial permanece aplicável também a ela. Ver
`DECISOES.md`, entrada sobre desagregação por categoria.

### Experimento A — efetivo mínimo viável por regime

Para a mesma cobertura assistencial, qual o efetivo mínimo viável sob turnos de 8 horas e
sob plantão de 12×36?

Motivação: sob `MaxConsecutiveWorkingDays = 1`, a demanda de `long01` (740 atribuições)
excede a capacidade de 49 profissionais (686). A instância seria inviável nas restrições
rígidas. O efetivo passa portanto a ser **resultado**, não parâmetro fixo.

É medida de viabilidade — independente do algoritmo de resolução.

### Experimento B — penalidade e sua distribuição

Com o efetivo dimensionado em cada regime, comparar penalidade total e sua distribuição
entre profissionais: penalidade máxima individual, amplitude entre o mais e o menos
penalizado, dispersão em relação à média.

É propriedade da instância no ótimo — independente do algoritmo.

### O que as medições sustentam

Custo computacional é propriedade da tripla (formulação, algoritmo, instância), não da
instância. Um branch-and-price sobre formulação por padrões pode inverter o ranking.

| Força | Medida |
|---|---|
| **Forte** — propriedade da instância | viabilidade / inviabilidade; valor ótimo comprovado; distribuição da penalidade no ótimo |
| **Média** — propriedade da formulação | número de variáveis e restrições; relaxamento linear na raiz; gap de integralidade inicial |
| **Fraca** — depende do algoritmo | tempo até o ótimo; nós explorados; gap ao fim de um limite de tempo |

Decorrências operacionais, que valem como restrição de projeto:

- manter as instâncias pequenas o suficiente para **provar otimalidade** nas duas
  configurações comparadas;
- pesos **idênticos** entre configurações comparadas;
- preferir medidas normalizadas (penalidade por profissional, dispersão) a totais absolutos,
  que não são comparáveis entre instâncias de tamanhos e pesos diferentes;
- medidas de tempo entram como observação com escopo declarado, nunca como conclusão sobre
  dificuldade intrínseca.

## 6. Formulação adotada

Referência: **SANTOS, H. G.; TOFFOLO, T. A. M.; GOMES, R. A. M.; RIBAS, S. Integer
programming techniques for the nurse rostering problem. Annals of Operations Research,
v. 239, p. 225-251, 2016.**

Toma-se de Santos et al. a **semântica das restrições**: 2 rígidas, 13 flexíveis, lógica de
fim de semana por contrato, padrões de turno e de dia.

**Divergência declarada.** Não se adotam as variáveis de janela `w[n,d1,d2]` / `r[n,d1,d2]`
nem as tabelas de penalidade pré-calculadas (σ, τ). Aquelas construções servem ao objetivo do
artigo original — fortalecer o limite dual por planos de corte. Adota-se codificação por
atribuição: variável binária `x[n,s,d]` com restrições explícitas de janela deslizante para
dias consecutivos.

Razões: (i) o objeto deste trabalho é o efeito de decisões de modelagem, não desempenho
algorítmico; (ii) a codificação por atribuição permite adaptação direta ao regime 12×36 e à
desagregação da cobertura por categoria profissional, o que o esquema de janelas com σ
pré-calculado não permite sem recalcular a tabela inteira; (iii) a visão nurse-task é 63% da
literatura revisada (71 de 110), contra 4 trabalhos em nurse-day.

Santos et al. entra como referência de formulação e fonte de valores de comparação — não
como código a reproduzir.

**Escopo das restrições, decidido em 2026-09-15.** Implementam-se as 13 flexíveis, mais as
metades "on" dos pedidos (`DayOnRequests`, `ShiftOnRequests`), mesmo que três desses itens
não sejam exercitados por nenhuma instância do INRC-2010: o máximo de fins de semana em
quatro semanas (`on="0"` nos 235 contratos), as folgas após sequência de turnos noturnos
(elemento ausente em todas) e os pedidos para trabalhar. A semântica dos três está fixada na
documentação oficial, e Santos et al. os implementam. Ressalva a declarar no texto: esses
três são implementados **sem conferência externa possível** — nenhuma instância produz
penalidade deles, então nem o avaliador nem a Tabela 6 atestam a implementação. Ver
`DECISOES.md`, entrada de 15/09.

## 7. Estrutura das instâncias do INRC-2010

Formato XML, raiz `SchedulingPeriod`, com dez blocos: `StartDate`, `EndDate`, `Skills`,
`ShiftTypes`, `Patterns`, `Contracts`, `Employees`, `CoverRequirements`, `DayOffRequests`,
`ShiftOffRequests`.

Pontos de atenção verificados nos arquivos originais e na documentação oficial:

- **`<Preferred>` é demanda obrigatória, não preferência.** A documentação oficial
  (Haspeslagh et al., PATAT 2010, p. 499-500) declara a cobertura como restrição rígida e
  lista apenas duas rígidas: cobrir toda a demanda e no máximo um turno por enfermeira por
  dia. Santos et al. modelam como igualdade. O nome do elemento é enganoso.
- **Atributo `on="0"` / `on="1"`** em cada restrição flexível indica se ela está ativa
  naquela instância. Restrição com `on="0"` não entra no modelo. Ignorar isso faz o valor
  objetivo divergir do avaliador — e o sintoma parece bug de modelo, não de leitura.
- **Habilidade está pregada no tipo de turno, não na cobertura.** `<Cover>` aceita apenas
  `<Shift>` e `<Preferred>`. A desagregação por categoria se faz criando um tipo de turno por
  par horário×categoria: em `long01`, o turno `DH` tem horário idêntico ao `D`
  (08:30-16:30) mas exige `HeadNurse`, com cobertura própria de 2 nos dias úteis. É isso que
  Santos et al. querem dizer com "turnos e habilidades são diretamente relacionados".
- **`CoverRequirements` vem por dia da semana** (`DayOfWeekCover`, 7 blocos), não por data.
  O parser expande para os dias do horizonte.
- **Turno noturno atravessa a meia-noite** — `N` vai de 22:30 a 06:30 — e a documentação o
  trata como pertencente a um dia. Adotar a mesma convenção, não inventar outra.
- **Cada instância vem em XML e em texto**; a solução para o avaliador vai em XML.
- **Nomenclatura:** o lote *early* tem arquivos sem o sufixo. O que a literatura chama de
  `sprint_early01` é o `sprint01.xml` da pasta sem sufixo. Mapear ao cruzar com a Tabela 6 de
  Santos et al.
- Lotes: *early* (sem sufixo), *late*, *hidden* e *hint*. **Corrigido em 2026-09-15 pela
  varredura das instâncias:** apenas o lote *early* usa pesos uniformes 0/1. Os lotes
  *late*, *hidden* e *hint* usam pesos diferenciados por tipo de restrição — valores 3, 4,
  5, 7 e 10, e 31 em três instâncias `medium`. A redação anterior atribuía os pesos
  diferenciados só ao lote *hint*, o que está errado. Consequência: material para análise
  de sensibilidade existe nos três lotes, não em três instâncias por track.
- **A pasta tem 69 arquivos XML, não 60:** as 60 instâncias da competição mais 9 do lote
  *hint* (3 por track). Santos et al. (2016) reportam resultados para as 60; as `hint` não
  têm valor de referência na Tabela 6 e só podem ser conferidas pelo avaliador oficial, que
  pontua uma escala dada mas não prova otimalidade. Verificado em 2026-09-15; inventário
  completo em `docs/inventario_instancias.csv`.

## 8. Stack

- Python + Pyomo — camada de modelagem, independente do solver
- HiGHS como solver padrão; CPLEX ou Gurobi se houver licença acadêmica institucional
  (a troca não exige reescrever o modelo)
- Git para versionamento
- Avaliador oficial da competição (Java) para validação

## 9. Operação: dois projetos, um repositório

| Onde | O quê |
|---|---|
| **Este projeto (Códigos)** | parser, modelo, experimentos, arquivos do repositório |
| **Projeto de Redação** | capítulos, revisão ABNT, artigos, reuniões com o orientador |
| **Chat de escopo do usuário** | mudanças de rumo, arbitragem de propostas estruturais |

`DECISOES.md` é a ponte entre os dois projetos: este projeto **produz** decisões, o de
redação as **consome** para escrever os capítulos de formulação e de experimentos. As cópias
em Contexto são estáticas — o usuário re-sobe nos dois periodicamente.

**Modo de trabalho:** Cowork quando envolve arquivos do repositório (varrer instâncias,
escrever o parser, rodar experimentos). Chat para dúvida pontual de modelagem ou revisão de
um trecho colado.

## 10. Protocolo de colaboração

As decisões em `DECISOES.md` foram tomadas com contexto que não está aqui: reuniões de
orientação, restrições de prazo, checagens contra a documentação oficial. Isso não as torna
definitivas — torna sua revisão dependente de contexto externo.

**Sugestões de implementação são bem-vindas e aplicam-se direto:** estrutura de código, forma
de escrever restrições, organização dos experimentos, ordem das tarefas, ferramentas.

**Sugestões que afetem formulação, desenho experimental ou escopo** vão para `PROPOSTAS.md`
como proposta a validar, com o raciocínio completo, e não são implementadas até validação.
Motivo prático: proposta boa no meio de uma tarefa de código é distração, mesmo sendo boa.
Registrada, vira insumo; discutida na hora, vira desvio.

## 11. Convenções de trabalho

- Nenhum resultado numérico vale sem passar pelo avaliador oficial ou ser conferível contra a
  Tabela 6 de Santos et al. (2016). Alvos de validação: `sprint01` = 56, `sprint02` = 58,
  `long01` = 197, `long02` = 219 e `medium_late05` = 107.
- **`medium_late05` acrescentado em 2026-09-15.** Os quatro alvos anteriores são todos do
  lote *early*, que desliga quatro restrições flexíveis e usa peso 1 em todas — validar só
  neles prova 8 das 13 restrições. O `medium_late05` exercita todas as que aparecem ligadas
  em alguma instância, com pesos de 1 a 10, duas habilidades e pedidos de folga, e tem gap 0
  na Tabela 6. Ver `DECISOES.md`, entrada de 15/09.
- Toda decisão de modelagem não óbvia vai para `DECISOES.md` no momento em que é tomada, com
  data e justificativa. Três linhas bastam. Esse arquivo é a matéria-prima dos capítulos.
- O Passo 3 do pipeline — validação no avaliador — não é postergado. Sem conferência externa,
  nenhum resultado posterior tem credibilidade.
- **Entrega do TCC: 04/11/2026. Congelamento de resultado numérico: 14/10/2026.** Depois do
  congelamento, nenhum experimento novo — apenas texto. Experimento que não rodou até 13/10
  não entra no trabalho. Regra que protege as três semanas finais de redação e evita o padrão
  de falha mais comum neste tipo de trabalho: chegar à reta final ainda experimentando
  enquanto o prazo de redação se esgota.

### Cronograma deste projeto

| Semana | Datas | Marco |
|---|---|---|
| 1 | 09–15/09 | Parser + modelo mínimo + escala aprovada pelo avaliador oficial |
| 3 | 23–29/09 | Modelo completo validado — `sprint01` = 56, `long01` = 197 |
| 4 | 30/09–06/10 | Instância brasileira construída |
| 5 | 07–13/10 | Experimentos A e B rodados |

O marco da semana 1 é o de maior risco do cronograma inteiro: sem conferência externa, nada
do que vem depois tem credibilidade. As semanas 2, 6, 7 e 8 pertencem ao projeto de redação.

## 12. Pipeline

| # | Etapa | Marco verificável |
|---|---|---|
| 1 | Leitor das instâncias do INRC em XML | Parâmetros carregados corretamente |
| 2 | Modelo mínimo — só as duas restrições rígidas | Uma escala viável gerada |
| 3 | Modelo completo e **validação no avaliador oficial** | **Valor objetivo igual ao do avaliador** |
| 4 | Adaptação ao contexto brasileiro: desagregação por categoria, regime 12×36, modularização das restrições flexíveis | Instância brasileira resolvida |
| 5 | Experimentos A e B | Tabelas de resultado e medidas de dispersão |
