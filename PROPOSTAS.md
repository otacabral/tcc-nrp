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

**Status: VALIDADA em 2026-09-18.** Habilidade é flexível com coeficiente na variável de
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

**Status: VALIDADA em 2026-09-18 — invariante de horas, encaminhamento 1 combinado com o 3.**
O efetivo de 8 horas é recalculado no mesmo critério, e o resultado reportado é a distância
percentual entre o piso aritmético e o efetivo mínimo viável. Decisão registrada no
`DECISOES.md`, entrada "Invariante do Experimento A: horas de assistência", que também marca
como superada a parte da entrada de 08/09 construída sobre o invariante de atribuições.

A aritmética da conversão ficou aberta e virou **P5**, abaixo: a regra de teto por janela não
satisfaz o invariante que esta proposta acabou de adotar.

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

---

## 2026-09-18 — P5: a discretização da demanda em blocos de 12 h

**Status: DISSOLVIDA em 2026-09-21. Não bloqueia mais nada.** Com o perfil assistencial
uniforme do Parecer, cada janela de 8 h e cada janela de 12 h pedem os mesmos 8,81
profissionais, e o resíduo de arredondamento é **idêntico nos dois regimes** (+2,16% pelo
teto). A assimetria que esta proposta media não se coloca na instância brasileira.

Permanecem em vigor as duas medidas que ela originou: emitir as duas instâncias por regra
(teto e maior resto) e conferir o total de horas com tolerância de um bloco.

**O que sobra é achado de metodologia**, não decisão pendente: a reagregação de turnos
sobrepostos em janelas disjuntas domina o efeito de regime na categoria escassa, nas 65 de 69
instâncias do INRC que têm sobreposição. Lugar dele: uma subseção do capítulo de dados. Ver a
nota de contenção no fim deste arquivo.

**Revisão de 18/09, após medir os picos.** A versão anterior desta proposta recomendava a regra
de maior resto. **A recomendação mudou**: nenhuma regra de arredondamento serve, e o motivo
está na seção "O que as medições mostraram". A proposta agora é tornar a discretização
variável do modelo. O histórico fica registrado porque o caminho até aqui é argumento de
metodologia.

### O problema

P4 fixou o invariante: a instância de 12×36 entrega as mesmas **horas de assistência** que o
`long01`, 5.920 h, das quais 384 de enfermeiro-chefe. A conversão é reconstrução: a demanda
vira perfil horário e é reagregada em janelas de 12 h. Falta a aritmética dessa reagregação.

Duas observações preliminares, as duas de correção:

1. **A igualdade exata é impossível.** 5.920 ÷ 12 = 493,33 blocos. O melhor atingível é 493
   blocos (5.916 h, −0,07%) ou 494 (5.928 h, +0,14%). A conferência obrigatória precisa de
   **tolerância de um bloco por categoria**, senão reprova também a conversão correta.
2. **O corte é às 06:30/18:30**, alinhado ao início do turno E. Ele divide o horizonte em
   exatamente 56 janelas. O corte às 07:00 cria uma fatia parcial de 7 h no primeiro dia, e é
   pior por isso: o teto custa +236 h nele contra +224 h no corte alinhado. Todos os números
   abaixo são do corte 06:30.

### O que as medições mostraram

Duas estatísticas importam, e não são a mesma:

- **o total de horas**, que é o invariante do P4;
- **o pico de 48 h**, que é a soma da demanda em quatro janelas consecutivas. Sob 12×36 com
  descanso de 36 horas, um profissional entra em no máximo uma janela a cada quatro, logo o
  efetivo mínimo é pelo menos esse pico. É ele que dimensiona, não a média.

| Regra | Total | Pico de 48 h, total | Pico de 48 h, chefe |
|---|---|---|---|
| demanda exata, fracionária | 5.920 h | 38,67 | 5,33 |
| **teto** | 6.144 h (+3,8%) | **40** (+3,4%) | **8** (+50%) |
| **maior resto por categoria** | 5.916 h (−0,07%) | **40** (+3,4%) | **7** (+31%) |
| **faixa admissível inteira** | — | **[38, 40]** | **[5, 8]** |

Três conclusões, em ordem de importância:

**1. As duas regras enviesam na mesma direção, não em direções opostas.** Nenhuma das duas
suaviza o pico: as duas o inflam. A integerização só pode mover cada janela em ±1, e as
janelas de pico têm fração alta, então sobem nas duas regras. O risco de subdimensionar o pico
— que era a objeção ao maior resto — **não se materializa nesta instância**. O que acontece é
o contrário, e é pior: os dois candidatos inflam o piso de efetivo do 12×36, que é o lado que
o trabalho quer medir.

**2. Logo, reportar a faixa entre as duas regras não mede nada.** No total ela teria largura
zero — 40 contra 40 —, o que passaria falsa impressão de robustez; no chefe, [7, 8], quando a
faixa verdadeira é [5, 8]. As duas regras estão no **topo** dos dois intervalos.

**3. A discretização vale muito.** Entre os extremos admissíveis, o piso de efetivo do 12×36
varia de 38 a 40 no total (5%) e de 5 a 8 no chefe (60%) — para a mesma demanda subjacente e
o mesmo invariante de horas, decidido por escolha puramente aritmética. É grande demais para
resolver por convenção.

**Correção de uma hipótese levantada na revisão.** Não é verdade que o turno DH só exista em
dia útil. Ele ocorre nos sete dias: 2 em dia útil, 1 no sábado e no domingo. O horizonte
inteiro tem essa forma — 29 atribuições em dia útil, 20 no fim de semana, nas cinco categorias
de turno. A média de 1,71 chefe por dia esconde 2 contra 1, não 2,4 contra 0.

### O que se propõe

**Não escolher regra. Tornar a discretização variável do modelo.**

Para cada janela *w* e cada categoria *c*, a demanda `d[c,w]` é **variável inteira** com

- `⌊e[c,w]⌋ ≤ d[c,w] ≤ ⌈e[c,w]⌉`, onde `e[c,w]` é a demanda exata fracionária da janela;
- `Σ_w d[c,w] = N_c`, com `N_c = arredonda(horas da categoria c / 12)` — 493 no total, 32 no
  chefe.

O modelo escolhe a discretização junto com a escala. Nada é arbitrado fora dele.

Medido como MILP sobre o `long01`, isso derruba o piso de efetivo de **40 para 38** no total e
de **8 para 5** no chefe: são os pisos verdadeiros da demanda sob o invariante de horas, e não
o subproduto de uma convenção de arredondamento bem ou mal escolhida.

É a mesma forma da correção já aceita para o Experimento B — em vez de um número que depende
de desempate arbitrário, uma propriedade do conjunto de soluções admissíveis.

### Ressalva honesta

Com `d[c,w]` livre, a janela de pico pode ser servida **abaixo** da demanda exata fracionária:
38 contra 38,67. É legítimo sob o invariante de horas, porque a assistência total é preservada
e apenas realocada dentro da margem que o arredondamento já impõe de qualquer forma. Mas é uma
afirmação que precisa estar escrita no texto: **o 12×36 reorganiza a assistência entre
janelas, e essa reorganização é parte do regime, não artifício da conversão.**

Se o orientador não aceitar essa leitura, a variante é impor `d[c,w] = ⌈e[c,w]⌉` nas janelas de
pico. O piso volta a 40 e 8, declaradamente e por decisão de modelagem, não por acidente de
arredondamento.

### Consequência para o Experimento B

O Experimento B precisa de instância fixa. A saída: rodar o Experimento A com a demanda
variável, **fixar o vetor `d[c,w]` que sair dele** e publicá-lo como a instância de B. O vetor
entra em `resultados/` e no apêndice.

### Encaminhamentos possíveis

1. **Discretização variável no modelo**, com o total por categoria fixado e tolerância de um
   bloco. Piso de efetivo 38 e 5 no `long01`. **Recomendado.**
2. **Discretização variável com proteção de pico** (teto obrigatório nas janelas de máximo).
   Piso 40 e 8, declarado como decisão de modelagem. Escolher esta se subdimensionar pico for
   considerado inaceitável.
3. **Regra fixa de arredondamento** — teto ou maior resto. Não recomendado: as duas caem no
   topo da faixa admissível e inflam o piso do 12×36 em até 60% na categoria escassa, que é a
   variável que o Experimento A compara.

Recomendação: 1, com 2 registrado como variante para a reunião.

### O que sobra como achado, independentemente da escolha

A comparação entre regimes de turno é **sensível à regra de discretização da demanda**, numa
magnitude que chega a 60% do efetivo da categoria mais escassa. A literatura de *nurse
rostering* trabalha sobre instâncias já discretizadas e não discute esse passo. O achado é
legítimo e vale ser dito no texto mesmo que a conclusão principal sobreviva às três opções.

Os números são reproduzíveis por `docs/medicao_conversao_12h.py`.

### Revisão 2, 18/09 — a assimetria entre os dois braços, e o que ela revelou

**Objeção procedente.** Se a demanda por janela vira variável no braço do 12×36, esse braço
ganha um grau de liberdade que o braço de 8 horas não tem: o `long01` roda com a demanda
exatamente como declarada. O 12×36 sai menor em parte porque pôde escolher a própria demanda.
Os números 38 e 5 **não são "os pisos verdadeiros"** — são o piso do 12×36 sob liberdade de
discretização que o outro regime não teve. A afirmação anterior está retirada.

**Mas a simetria proposta não é alcançável no `long01`, e a medição mostra por quê.**

Submeti o `long01` ao **mesmo procedimento** que se aplicaria ao 12×36: reagregar o perfil
horário em janelas de 8 h, sem sobreposição, corte 06:30.

| Janelas | Quantas | Com demanda fracionária | Teto |
|---|---|---|---|
| 8 h, todas as categorias | 84 | **40** | 6.080 h (+2,7%) |
| 8 h, só o chefe | 56 | **56** | 608 h (**+58,3%**) |
| 12 h, todas as categorias | 56 | 56 | 6.144 h (+3,8%) |
| 12 h, só o chefe | 28 | 28 | 576 h (+50,0%) |

**O `long01` não sobrevive ao próprio procedimento.** E o chefe fica *pior* em janelas de 8 h
que em janelas de 12 h: +58,3% contra +50,0%.

A causa está nos horários: E 06:30–14:30, L 14:30–22:30 e N 22:30–06:30 se encaixam, mas
**D e DH vão de 08:30 a 16:30 e atravessam a fronteira das 14:30**. O `long01` não é uma
partição do dia em janelas de 8 h — é um conjunto de **turnos sobrepostos**.

Três consequências:

1. **A observação da revisão está certa e é mais forte do que foi formulada.** A demanda de
   8 h não é só "também uma discretização": ela é um objeto de outro tipo. Tratá-la como
   verdade e a de 12 h como convenção privilegia o benchmark, exatamente como apontado.
2. **Mas dar ±1 aos dois braços não simetriza nada**, porque o braço de 8 h não tem janelas
   para perturbar. Para lhe dar liberdade equivalente seria preciso o perfil assistencial
   contínuo do qual o `long01` teria sido derivado — e esse objeto não existe: os números do
   `long01` são todo o dado disponível. Qualquer liberdade concedida a ele seria inventada.
3. **O resíduo não é do 12×36. É de particionar.** Uma exigência de 1,71 chefe por dia não
   cabe em número inteiro por janela, qualquer que seja a janela. Isso desarma a leitura de
   que "o 12×36 infla o chefe em 50%": infla o particionamento, e o 12×36 até infla menos que
   o particionamento em 8 h.

### Recomendação revisada

**Na calibração sobre o `long01`: reportar intervalo, como a revisão propõe.** O efetivo
mínimo sob 12×36 está em [38, 40] no total e em [5, 8] no chefe; a largura é artefato da
discretização, não propriedade do regime. Não é meio-termo — dado que a simetria não é
alcançável ali, é a afirmação correta.

**Na instância brasileira: simetria por construção, e sai de graça.** O Experimento A roda
sobre a instância brasileira, não sobre o `long01`. Ali o perfil assistencial contínuo **é**
o objeto que as fontes normativas fornecem. Então `src/instancia_br.py` passa a ter como
primitivo **o perfil horário contínuo**, e emite os dois regimes a partir dele pela mesma
regra. Os dois braços discretizam, nenhum é o original, e a objeção da banca não se coloca.
Custa a mesma rodada; muda o que é o primitivo do gerador.

**Serialização: aceito integralmente, com um ajuste.** A demanda variável não serializa, e o
objetivo específico 2 promete instância em XML oficial validada no esquema. A instância tem de
sair com regra declarada e fixa. Só que emitir **uma** obriga a escolher, e a escolha é
justamente o que está em disputa. Emitir **duas** custa quase nada e resolve: uma pelo teto e
outra por maior resto por categoria, as duas válidas no esquema, as duas publicadas. O
intervalo [38, 40] e [5, 8] passa a ter artefato em cada ponta em vez de ser só um número no
texto, e quem reusar escolhe a convenção que preferir com o desvio de cada uma documentado.

Só o teto eu não emitiria sozinho: é conservador no pico, mas entrega ao reusuário uma
instância cuja categoria mais escassa está 50% inflada.

### O que precisa estar escrito no texto

Na categoria do enfermeiro-chefe, a incerteza de discretização — [5, 8], 60% da grandeza — é
**maior do que qualquer efeito de regime que o Experimento A poderia medir**. Ali o
experimento não sustenta afirmação quantitativa. O que sobra é a afirmação qualitativa, que é
o achado: a discretização domina. Melhor declarar isso do que ouvir na defesa.

### Sobre o achado de método

A frase "a literatura trabalha sobre instâncias já discretizadas e não discute esse passo" é
afirmação de novidade e fica **suspensa** até existir coluna na planilha de triagem dos 110.
Sem denominador é "não achei". O achado pode ser apresentado sem ela: o que está medido é que
a discretização domina o resultado nesta instância, e isso não depende de ninguém mais ter
dito ou deixado de dizer.

### Revisão 3, 18/09 — o alcance da afirmação, medido nas 69

**A ressalva procede: o que foi medido não é sobre regime de jornada.** É sobre reagregar
**turnos sobrepostos em janelas disjuntas**. Uma instância cujos turnos já particionam o dia
não tem esse resíduo. Chamar isso de "discretização" no texto convida a pergunta certa — vale
para instâncias sem sobreposição? — com a resposta errada.

**Terminologia fixada para o texto:** *reagregação de turnos sobrepostos em janelas
disjuntas*. "Discretização" só como termo guarda-chuva, nunca como nome do efeito.

**Rodei a medição nas 69**, em `docs/medicao_sobreposicao.py`. Roda em segundos, sem solver.

| | |
|---|---|
| instâncias com turnos que se sobrepõem parcialmente | **65 de 69** |
| instâncias com mais de uma habilidade | 24 de 69 |
| dessas, categoria escassa inflando **mais** em janelas de 8 h que de 12 h | **24 de 24** |
| grupo de controle — as 4 sem sobreposição | 8 h: **+0,0%** · 12 h: +19,1% a +20,0% |

Amplitude na categoria escassa, sempre o `HeadNurse`: de +53,8% a +100,0% em janelas de 8 h,
contra +38,5% a +50,0% em janelas de 12 h. No total, de +1,2% a +18,4% em 8 h.

**O grupo de controle é o que fecha o argumento.** As quatro instâncias sem sobreposição —
`sprint_hidden01`, `02`, `06` e `07`, de três tipos de turno — dão resíduo **exatamente zero**
em janelas de 8 h, porque seus turnos já *são* uma partição em blocos de 8 h; e dão +19% a
+20% em janelas de 12 h. É o comportamento que a explicação prevê, e nenhuma outra explicação
prevê. O mecanismo está isolado: a causa é a sobreposição, não a duração do bloco.

**O que o controle também mostra, e é metade da manchete que precisa cair.** Onde a
comparação é limpa — nas quatro instâncias sem sobreposição — a intuição ingênua está **certa**:
particionar em 12 h custa +19% a +20%, particionar em 8 h não custa nada. A inversão que
encontramos, com o 12×36 distorcendo menos que o arranjo de 8 h, **só existe nas instâncias com
turnos sobrepostos**, e existe porque a sobreposição penaliza o arranjo de 8 h — não porque o
12×36 seja benigno.

Portanto **a inversão é achado sobre o benchmark, não sobre regimes de jornada.** Escrito de
outro jeito, a banca lê que o trabalho mostrou o 12×36 discretizando melhor. Não mostrou.

**Enunciado exato para o texto**, com os denominadores certos — 45 das 69 não distinguem
habilidade, e nelas a expressão "categoria mais escassa" não tem sujeito:

> Em 65 das 69 instâncias do INRC-2010 os turnos se sobrepõem parcialmente. Nas 24 que
> distinguem mais de uma habilidade, a reagregação em janelas disjuntas infla a categoria mais
> escassa em todas as 24, e mais em janelas de 8 h do que de 12 h. Nas 4 instâncias cujos
> turnos particionam o dia, o resíduo em janelas de 8 h é nulo.

Duas frases, dois denominadores, nenhuma extrapolação.

### Armadilha no gerador, revelada pelo próprio grupo de controle

**Requisito, a valer antes de qualquer código do `instancia_br.py`.**

As quatro instâncias de controle dão resíduo zero em 8 h porque **foram declaradas em três
turnos que particionam o dia**. Reagregar em 8 h devolve o original. Não é virtude do regime —
é tautologia.

O mesmo mecanismo espera o gerador brasileiro. Se o perfil contínuo for montado pensando em
"manhã, tarde, noite", que é o hábito natural, o braço de 8 h nasce com resíduo zero e o de
12 h com ~19%. **A assimetria que a Revisão 2 eliminou volta pela porta dos fundos, embutida no
primitivo e desta vez invisível** — não haveria como detectá-la olhando o resultado.

Duas exigências:

1. **O perfil horário contínuo tem de ser derivado da necessidade assistencial hora a hora**,
   nunca de blocos de 8 h nem de 12 h. Vindo do dimensionamento normativo, que dá horas de
   enfermagem por paciente em 24 h, ele sai naturalmente assim. Vindo de "quantos por turno",
   sai viciado.
2. **Conferência obrigatória no gerador:** reagregar o perfil emitido nos dois tamanhos de
   janela e verificar que **nenhum dos dois dá resíduo zero**. Resíduo zero em qualquer um dos
   tamanhos é sintoma de que o primitivo foi construído naquele tamanho, e reprova o perfil.

---

## 2026-09-18 — P6: o objetivo específico 2 mudou de escopo sem ter sido reescrito

**Status: VALIDADA em 2026-09-21.** A reescrita do objetivo específico 2 fica com o projeto de
redação, junto com a reformulação do gap e a menção na delimitação 1.4 de que a instância é
sintética. Porte definido numericamente: 5.920 horas-profissional, o mesmo invariante da P4.

Não era proposta de mudar nada — é o registro de que uma mudança **já tinha acontecido** por
consequência da P5, e precisava ser declarada antes de virar capítulo.

### O que mudou

A Revisão 2 da P5 põe o **perfil assistencial horário contínuo** como primitivo do
`src/instancia_br.py`, para que os dois regimes sejam emitidos do mesmo objeto e a comparação
seja simétrica. Foi decidido por um motivo metodológico estreito, mas tem consequência larga:

- o perfil contínuo vem das **fontes normativas**, não do `long01`;
- logo a instância brasileira **deixa de ser derivada do benchmark** e passa a ser construída
  a partir da norma, usando o `long01` apenas como **referência de porte**;
- o objetivo específico 2, como está escrito, promete outra coisa.

É mudança de escopo, e ela entrou em silêncio.

### O que precisa ser dito

O específico 2 tem de declarar que a instância é **construída a partir de perfil assistencial
derivado de parâmetros normativos, calibrada para o porte de uma instância do benchmark**, e
serializada em XML oficial validado no esquema.

**"Porte" precisa de definição numérica, senão é vago. Porte = total de horas-profissional no
horizonte, igual às 5.920 h do `long01`.** Isso fecha o círculo: o porte passa a ser o próprio
invariante da P4, o mesmo número que governa a comparação entre regimes, e o `long01` fica no
trabalho como **referência de escala** em vez de fonte de demanda. Uma frase amarra as duas
propostas.

A redação exata fica com o projeto de redação. Aqui fica o registro de que a mudança existe,
de onde ela veio e por quê.

### Duas consequências de redação, além do específico 2

1. **A formulação do gap muda.** Não é mais "reparametrizar um benchmark" — é "construir
   instância a partir de parâmetros normativos, calibrada a um benchmark". São lacunas
   diferentes, e a segunda é a que o trabalho de fato preenche.
2. **A delimitação 1.4 precisa dizer que a instância é sintética.** Sem isso, um leitor lê
   estudo de caso onde não há campo, hospital nem dado primário.

### Duas consequências operacionais

**1. O portão das três fontes ficou mais estreito, não menos.** O perfil contínuo deixou de
ser um parâmetro entre outros: ele é **o objeto primitivo**. Sem as fontes não há primitivo,
sem primitivo não há instância, sem instância não há Experimento A nem B. Antes as fontes
alimentavam a instância; agora elas a constituem.

**2. As duas instâncias emitidas têm de sair do mesmo perfil contínuo**, diferindo apenas na
regra de reagregação. Se cada uma nascer de um perfil diferente, o par deixa de medir o efeito
da regra e passa a medir a diferença entre dois perfis. Isso é implementação e já está no
`PLANO.md` como requisito do gerador, não como sugestão.

---

## 2026-09-21 — P7: três lacunas encontradas ao escrever o gerador

**Status: VALIDADAS em 2026-09-21, as três. Implementadas.** P7.1 fica ligada por padrão com
`--sem-descanso-clt` só para medir o efeito; P7.2 virou o padrão indesejado `clt_36h_N_D`;
P7.3 virou a flag `rigidas_legais` em `modelo.py`, com o conjunto `RIGIDAS_LEGAIS_BR`.
A definição de viável está registrada no `DECISOES.md`, entrada de 21/09.

**Conferência do descanso, rodada em `src/instancia_br.py --conferencia`:** enumerando todas
as sequências que o contrato admite, o menor intervalo é **36 h no 12×36** (exatamente o
art. 59-A, depois da P7.2) e **16 h de interjornada no de 8 h**, com **24 h no caso do dia
livre** — que é o descanso semanal do art. 67, atingido no limite pela sequência noturno dia
*d* → manhã dia *d*+2. As duas regras valem, e valem justas.

### P7.1 — O item 7 da decisão de 21/09 veio com o marcador em branco

A decisão relatada traz "Descanso no regime de 8 h — **[A VALIDAR / VALIDADO]**". O
marcador não foi resolvido. Implementei como **ligado por padrão**, pelo argumento da
própria decisão: sem as regras de descanso o braço de 8 h ganha liberdade que o 12×36 não
tem, e a comparação fica enviesada. A flag `--sem-descanso-clt` desliga, para medir o efeito.

Só precisa de um "validado" ou de um "não".

### P7.2 — No 12×36, `MaxConsecutiveWorkingDays = 1` não garante as 36 h após o plantão noturno

A decisão de 08/09 encoda o 12×36 como um dia sim, um dia não. Isso basta para o plantão
diurno, mas **não para o noturno**:

| Sequência | Fim | Início seguinte | Descanso | `MaxConsec = 1` permite? |
|---|---|---|---|---|
| Diurno dia *d* → diurno dia *d*+2 | 19:00 *d* | 07:00 *d*+2 | 36 h | sim, e está correto |
| **Noturno dia *d* → diurno dia *d*+2** | **07:00 *d*+1** | **07:00 *d*+2** | **24 h** | **sim, e está errado** |
| Noturno *d* → noturno *d*+2 | 07:00 *d*+1 | 19:00 *d*+2 | 60 h | sim, correto |

Conserto: um padrão indesejado de três entradas — noturno, folga, diurno. Uma linha no
gerador.

**Por que importa agora.** O braço de 8 h acabou de ganhar as três proibições de
interjornada (P7.1). Deixar o 12×36 com um furo de descanso é a assimetria da Revisão 2 de
novo, com os papéis trocados: desta vez favorecendo o 12×36.

### P7.3 — Os limites legais são flexíveis no formato do INRC, e o Experimento A precisa que binde

No esquema oficial toda restrição de contrato é flexível, com peso. O teto de 42 h/semana
(`MaxNumAssignments`) e o descanso entram como flexíveis com peso 1 — se o modelo os tratar
assim, "efetivo mínimo viável" vira capacidade dividida por demanda, e o Experimento A perde
o conteúdo: qualquer efetivo é viável, basta pagar a penalidade.

Duas saídas, e a escolha é de formulação:

1. **Flag `rigidas_legais` em `modelo.py`** (recomendado): as restrições marcadas como de
   origem legal entram como rígidas. O arquivo XML emitido continua sendo uma instância
   normal do INRC, reutilizável por terceiros e aceita pelo avaliador oficial — a rigidez é
   opção de quem resolve, não propriedade do arquivo.
2. **Peso alto no arquivo.** Não recomendado: distorce o objetivo, contamina o Experimento B
   e entrega ao reusuário uma instância com pesos arbitrários.

Recomendação: 1. É a mesma forma da flag `habilidade_rigida` que a P3 já reservou para esta
instância.

---

## 2026-09-21 — P7.4 (revisão): aplicado o critério, sobra quase nada do `long01`

**Status: RESOLVIDA em 2026-09-21.** As duas reclassificações foram aceitas e o critério ganhou
um degrau a mais: **uma restrição é estrutural quando o regime determina se ela pode ser
violada** — forçando a violação, como `complete_weekends`, ou impedindo-a, como
`identical_shift_types_during_weekend`. A família de fins de semana **não é ligada**, por ser
quase estrutural no efetivo mínimo e por não ter conferência externa possível. O núcleo do
Experimento B migrou para as quatro instâncias do INRC com ótimo provado. Decisão registrada
no `DECISOES.md`, entrada de 21/09 "Experimento B: núcleo no INRC".

O diagnóstico abaixo é o que motivou a mudança, e fica como matéria-prima do capítulo.

### Os valores reais dos contratos do `long01`

Três contratos: `fulltime`, `75_time`, `50_percent`.

| Restrição flexível | c0 | c1 | c2 | Entra? |
|---|---|---|---|---|
| single_assignment_per_day | sim/p1 | sim/p1 | sim/p1 | não — é rígida de fato |
| max_num_assignments | 16/p1 | 12/p1 | 5/p1 | não — é o limite legal, rígido por P7.3 |
| min_num_assignments | 6/p1 | 6/p1 | 3/p1 | não — estrutural (piso de jornada) |
| max_consecutive_working_days | 7/p1 | 5/p1 | 5/p1 | **não — estrutural** |
| min_consecutive_working_days | 1/p1 | 1/p1 | 2/p1 | **não — estrutural** |
| max_consecutive_free_days | 5/p1 | 7/p1 | 8/p1 | **não — estrutural** |
| min_consecutive_free_days | 1/p1 | 1/p1 | 1/p1 | **não — estrutural** |
| max_consecutive_working_weekends | off | off | off | queria entrar, mas **não há o que herdar** |
| min_consecutive_working_weekends | off | off | off | idem |
| max_working_weekends_in_four_weeks | off | off | off | idem |
| **complete_weekends** | **sim/p1** | **sim/p1** | **sim/p1** | **NÃO — ver abaixo** |
| **identical_shift_types_during_weekend** | **sim/p1** | **sim/p1** | **sim/p1** | **NÃO — ver abaixo** |
| no_night_shift_before_free_weekend | off | off | off | não — o avaliador não a pontua |
| two_free_days_after_night_shifts | ausente | ausente | ausente | não existe no arquivo |
| alternative_skill_category | off | off | off | não |
| padrões indesejados (0, 1, 2) | p1 | p1 | p1 | não — referenciam os turnos do `long01` |
| pedidos de folga | 490 de dia + 245 de turno, peso 1 | | | **sim** |

### Os dois itens que a lista classificou errado

**`complete_weekends` é estrutural, e é o caso mais grave de todos.** Sob 12×36 com
`MaxConsecutiveWorkingDays = 1` rígido, **ninguém pode trabalhar sábado e domingo**. Logo todo
profissional que trabalha um dia de fim de semana viola a restrição, sempre.

A conta, no efetivo 36: sábado pede 2 janelas × 9 = 18 blocos, domingo idem, e nenhum desses
36 blocos pode ser da mesma pessoa. São 36 pessoas violando, uma vez por fim de semana, em
quatro fins de semana: **144 de penalidade estrutural, inevitável, só no braço do 12×36** —
com o efetivo inteiro violando toda semana. No braço de 8 h a restrição é satisfazível com
zero. É exatamente a armadilha que a P7.4 foi criada para evitar, e é o maior termo.

**`identical_shift_types_during_weekend` é estrutural na direção oposta.** No 12×36 ninguém
trabalha os dois dias do fim de semana, então a restrição é **vacuamente satisfeita** e vale
zero sempre; no de 8 h pode ser violada. Penaliza um braço só, pelo mesmo motivo.

Regra que os dois casos sugerem, e que vale registrar: **uma restrição é estrutural quando o
próprio regime determina se ela pode ser violada** — seja forçando a violação, seja
impedindo-a. Não basta perguntar se ela "significa a mesma coisa": `complete_weekends`
significa exatamente a mesma coisa nos dois regimes, e é justamente por isso que ela captura
a diferença de regime em vez da qualidade da escala.

### O que sobra

Aplicado o critério corrigido, **a única família comparável que o `long01` tem com peso é a
dos pedidos de folga.** A família de fins de semana — a que o critério mais claramente
aprova — está **desligada nos três contratos**, então não há peso nenhum a herdar dela.

E há um segundo problema: **a instância brasileira não tem pedidos.** Pedidos são por
profissional; o gerador não cria nenhum. Hoje, a penalidade do Experimento B seria zero nos
dois braços.

### Encaminhamentos

1. **Gerar pedidos de folga na instância brasileira, por regra declarada** (quantos por
   profissional, sorteados com semente fixa e publicada), e medir o Experimento B sobre o
   atendimento de pedidos: quantos ficam sem atender e como se distribuem entre as pessoas.
   É medida de equidade, é neutra entre regimes e é o que a família sobrevivente mede.
   **Recomendado.**
2. **Ligar a família de fins de semana** (máximo/mínimo de fins de semana consecutivos) com
   valores e pesos **declarados por nós** — o `long01` não os fornece. Deixa de ser "pesos
   herdados"; passa a ser parâmetro do experimento, o que é defensável desde que dito.
3. **Só (1)**, e declarar no texto que o Experimento B mede uma dimensão de equidade, não a
   penalidade total do benchmark.

Recomendação: 1 + 2, com os pesos de (2) declarados como escolha e varridos se houver tempo.
A frase "pesos herdados do `long01`, declarados" precisa ser reescrita de qualquer forma: não
há o que herdar na família que interessa.

---

## 2026-09-21 — P9: a medida de dispersão do Experimento B

**Status: VALIDADA em 2026-09-21. Implementada em `src/experimentos.py`.** Penalidade
individual máxima; **forma B** (uma resolução por profissional) nas sprints, guardando o
máximo de cada um; **forma A** (binárias, `M = Z*`) como reserva nas longas; minimax no lado
do mínimo. Decisão registrada no `DECISOES.md`, entrada de 21/09.

### A medida se sustenta

**Penalidade individual máxima.** Conferido em 21/09: a penalidade decompõe **exatamente** por
profissional — Σ p_n = Z\* nas quatro instâncias, sem sobra — e cada parcela bate com o
avaliador oficial nos 118 profissionais. Então `max_n p_n` é participação num total fixo, é
linear, e tem leitura gerencial direta. Sem ressalva.

Duas balizas úteis para o texto. O valor fica sempre em **[⌈Z\*/N⌉, Z\*]**: em `sprint01`,
entre 6 e 56. E o ótimo arbitrário que já temos salvo dá `max p_n` = 14 em `sprint01`, 12 em
`sprint02`, 16 em `long01` e 15 em `long02` — um ponto dentro do intervalo que o experimento
vai medir, útil para calibrar expectativa.

### Minimizar é trivial; maximizar é a decisão

**Minimizar** é o minimax usual: uma variável contínua *t*, N restrições `t >= p_n`, minimizar
*t*. Linear, barato, nada a decidir.

**Maximizar** o máximo é maximizar uma função convexa — não convexo, precisa de disjunção.
Duas formas:

| | Como | Custo | Subproduto |
|---|---|---|---|
| **A. binárias** | `z_n ∈ {0,1}`, `Σ z_n = 1`, `t <= p_n + M(1 − z_n)`, maximizar *t* | 1 resolução, +N binárias | — |
| **B. uma resolução por profissional** | maximizar `p_n` com *n* fixo, tomar o maior | N resoluções, paralelizáveis | o **perfil por profissional**: quanto cada um pode ser feito carregar entre os ótimos |

Sobre o Big-M de (A): **`M = Z\*` é válido e justo**, porque `0 <= p_n <= Σ p_k = Z\*`. Não há
patologia de Big-M aqui — o limitante é exato, não arbitrado.

**Recomendação: B nas duas `sprint`, A como reserva nas duas `long`.** Nas sprints são 10
resoluções independentes, cada uma mais fácil que a com binárias, e o perfil por profissional
que sai de graça é resultado melhor do que o número único: permite dizer *quanto cada posição
pode ser feita carregar*, não só *quanto a pior posição carrega*. Nas longas são 49 resoluções,
e aí (A) com uma resolução e 49 binárias tende a compensar.

### Pré-requisito: escrito em 21/09, depois que o portão fechou

**`m.pena[n]` existe.** A regressão do item 6 passou — `sprint01` = 56 com ótimo provado — e
então a segunda alteração do `modelo.py` entrou: `m.pena[n]` como `Expression` ao lado de
`m.parcela[familia]`. As duas decomposições convivem, uma por família e outra por pessoa.

Ela também **não foi executada aqui** (o Pyomo continua fora do ambiente da sessão), e por
isso entrou junto o `src/regressao.py`: um comando que confere os quatro alvos em quatro
dimensões cada — ótimo provado, valor da Tabela 6, espelho do `avaliacao.py`, e o invariante
`sum(m.pena[n]) == objetivo` com igualdade profissional por profissional. **A P9 não avança
antes dessa regressão passar.**

O registro do diagnóstico original fica abaixo, porque explica por que a mudança era pequena.

**`modelo.py` não sabia calcular `p_n`.** A função objetivo é montada por família de restrição
(`m.parcela[familia]`), não por profissional — foi assim que ela nasceu, para permitir a
comparação restrição por restrição com o `avaliacao.py`.

A mudança é pequena e o terreno é favorável: **toda** folga é criada dentro do laço
`for n in profissionais`, e o laço dos pedidos itera sobre `Pedido`, que carrega o campo
`profissional`. Basta `nova_folga` receber a quem a folga pertence, acumular por profissional
e expor `m.pena[n]` como `Expression` ao lado de `m.parcela[familia]`. As duas decomposições
convivem: uma por família, outra por pessoa.

Foi exatamente isso que foi feito: `nova_folga` e `somar` passaram a registrar o dono do
termo, e `m.pena[n]` soma os termos de cada pessoa.

---

## Nota de contenção, 18/09 — o lugar do achado da reagregação

O achado já rendeu três revisões, uma varredura nas 69, um grupo de controle e dois scripts.
É metodologia, **não é o resultado do TCC**. O lugar dele é uma subseção do capítulo de dados,
justificando por que a instância brasileira nasce de perfil contínuo. Só isso.

O resultado do trabalho continua sendo o Experimento A e o B, que ainda não rodaram e dependem
de três fontes normativas que ainda não existem. **O achado está fechado**: as próximas horas
vão para as fontes, não para mais uma medição sobre ele. Registrado aqui para que nenhuma
sessão futura o reabra por parecer interessante.

---

## 2026-09-22 — P10: a conferência 1 como está pedida não é bem posta

**Status: RECUSADA em 2026-09-22, e a pergunta fica respondida por outro caminho.** Decisão
do projeto de redação: não medir a composição, nem por intervalo nem por escala testemunha.
O piso aritmético já responde a pergunta agregada e é mais forte que as duas alternativas;
reportar a composição de uma escala testemunha reintroduziria o desempate do solver um nível
abaixo. O `resultados/experimento_b_composicao.csv` **fica gravado como dado, sem nenhuma
afirmação apoiada nele**. Reavaliar depois do Experimento A.

A instrumentação que já entrou (`m.pena_familia[n, f]`, a conferência cruzada na regressão e
a gravação do CSV) permanece: não custa resolução, não entra em restrição nem no objetivo, e
é o que torna a reavaliação barata se ela vier. O que não existe é leitura publicável dela.

O registro abaixo fica como escrito, porque é o raciocínio que levou à recusa.

---

**Status original: aguardando validação.** Pedido do projeto de redação, 22/09, conferência 1:
"composição da penalidade máxima por família, nos três grupos de contrato. Aplicar a
decomposição do `avaliacao.py` às escalas de máximo."

**Não implementei a medição.** Implementei só a instrumentação que a torna possível
(`m.pena_familia[n, f]` no `modelo.py`, gravação em `experimento_b_composicao.csv`), porque
ela sai de graça das mesmas resoluções. A medição em si esbarra no problema abaixo.

### O problema

A regra de decisão proposta — *"se for dominada por excesso de atribuições, a afirmação
encolhe; se estiver espalhada, o achado é mais geral"* — supõe que a composição de `max p_n`
seja única. Ela não é.

A resolução que maximiza `p_n` fixa **o total em Z\*** e **maximiza a soma** das parcelas da
pessoa. Não fixa de que famílias essa soma é feita. Entre as escalas ótimas em que `p_n` vale
19, umas podem ter 19 unidades de excesso de jornada e outras 10 de excesso e 9 de dias
consecutivos. O solver devolve uma delas, e a escolha é desempate — a mesma coisa que o
Experimento B foi desenhado para não reportar. Ler a composição de uma escala e concluir
"dominada por excesso" repete, um nível abaixo, o erro que o experimento evita um nível
acima.

Há duas razões para desconfiar que o caso não é degenerado aqui. As famílias **estão
acopladas**: passar alguém do teto de 5 para 24 atribuições em 28 dias viola também
`max_consecutive_working_days`, então parte da composição é forçada e parte é escolha. E a
troca entre famílias **é barata**, porque nas quatro instâncias todo peso vale 1 — uma
unidade de excesso de jornada custa o mesmo que uma de dias consecutivos, e o solver não tem
preferência entre elas.

### A parte que é invariante, e já está medida

Uma parte da pergunta se responde **sem resolver nada**, e essa parte é sólida. A cobertura é
igualdade, então o total de atribuições de qualquer escala viável é exatamente a demanda `D`.
Se `D` passa da soma dos tetos de jornada `C`, os `D − C` excedentes existem em toda escala
viável, e como o peso é 1 isso é piso para `Z*`:

| | D | soma dos tetos | excesso forçado | Z\* | piso/Z\* |
|---|---|---|---|---|---|
| sprint01 | 152 | 122 | 30 | 56 | 54% |
| sprint02 | 152 | 120 | 32 | 58 | 55% |
| long01 | 740 | 590 | 150 | 197 | 76% |
| long02 | 740 | 580 | 160 | 219 | 73% |

Isto é `docs/conferencia_contratos.py`. No **total**, a resposta à conferência 1 é sim: a
penalidade é dominada por excesso de atribuição, e por aritmética, não por propriedade do
ótimo. O que não se segue disso é a composição **da penalidade individual máxima**, que é o
que a conferência pede.

### O que proponho no lugar

Perguntar em forma de intervalo, e só para quem importa. Para o profissional que detém
`max_do_max` (o 4 nas duas longas), e para a família `max_num_assignments`:

- mínimo da parcela dessa família, sujeito a total = Z\* **e** `p_n` = máximo conhecido;
- máximo da mesma parcela, sob as mesmas restrições.

Se o mínimo já é alto, a dominância é invariante e a afirmação forte se sustenta. Se o
intervalo for largo, a composição é escolha de gestão — o que é achado, não fracasso: diz que
a *mesma* carga máxima pode ser entregue como excesso de jornada ou como sequência ruim de
dias, e essa é uma alavanca de gestão que o total esconde.

Custo: 2 resoluções por (pessoa, família). Restrito a 1 pessoa e 2 ou 3 famílias em cada
longa, são 8 a 12 resoluções — dezenas de minutos, não horas. As duas restrições extras
tendem a deixar cada resolução **mais fácil** que as do experimento, não mais difícil.

### Se a resposta for "mede na escala e segue"

Também é defensável, desde que o texto diga o que está dizendo: *"na escala que maximiza a
penalidade do profissional 4, ela se compõe assim"* — uma escala testemunha, não propriedade
do conjunto. O `experimento_b_composicao.csv` já sai com a coluna `escala` justamente para
isso. O que não dá é usar essa leitura para decidir entre "afirmação forte" e "afirmação
encolhida", porque a decisão ficaria com o desempate do solver.

---

## 2026-09-22 — P11: o lote *early* é uma série controlada; o Experimento B pode usá-la

**Status: NÃO AGORA, decidido em 2026-09-22 — e há problema de desenho antes do custo.**

A objeção do projeto de redação, que é melhor que a minha proposta: entre `long01` e `long02`
mudam **onze parâmetros ao mesmo tempo**. Cinco pontos assim não dão dose-resposta; dão cinco
observações num espaço multidimensional. Eu tinha tratado a série como se fosse um eixo, e ela
não é — a tabela da seção "O que se ganha no lugar" mostra três linhas mudando juntas, e
nenhuma delas isolada.

A consequência prática: **antes de gastar dez horas de máquina, escrever qual afirmação exata
as cinco instâncias sustentariam.** Se a resposta for "que apertar contrato piora as três
medidas", dois pontos já dizem isso e cinco não dizem mais. Se for dose-resposta, cinco pontos
multidimensionais não dão, e a rodada seria desperdiçada.

**Onde a dose-resposta cabe de verdade:** na instância brasileira, variando **um parâmetro
por vez** — que é justamente o que o gerador permite e o benchmark não, porque lá os
parâmetros vêm amarrados no arquivo. E depois de 14/10.

O que sobra desta proposta e vale sozinho, sem rodar nada: **o fato de o lote *early* ser uma
série controlada precisa entrar no texto**, porque afeta como se lê qualquer média sobre ele,
inclusive as de outros autores. Isso não custa máquina nenhuma.

O registro abaixo fica como escrito.

---

**Status original: aguardando validação.** Não implementado: só rodar `long03`, `long04` e `long05`
no Experimento B já é desenho experimental novo.

### O fato, conferido em 22/09

Fui atrás da correlação de 0,89 entre `long01` e `long02` e achei o motivo dela. As duas
instâncias **não são cenários diferentes**. Conferido em dois níveis independentes — pelo
`parser.py` e por hash dos blocos do XML bruto, para não depender do meu próprio código:

| bloco do XML | 10 `sprint_early` | 5 `long_early` |
|---|---|---|
| `CoverRequirements` | 1 versão | 1 versão |
| `DayOffRequests`, `ShiftOffRequests` | 1 versão | 1 versão |
| `Employees`, `ShiftTypes`, `Skills` | 1 versão | 1 versão |
| **`Contracts`** | **10 versões** | **5 versões** |

`DayOnRequests` e `ShiftOnRequests` estão ausentes em todos. **O lote *early* é um cenário
por track com variações de regra de contrato.** Todas com ótimo provado na Tabela 6.

Isso invalida a frase que mandei ontem — *"a exposição é propriedade da pessoa, não sorteio
da instância"* — porque não há sorteio: é o mesmo mês, os mesmos pedidos, a mesma cobertura.

### O que se ganha no lugar, e é melhor

Um experimento controlado sobre **regra de contrato**, que é o objeto do trabalho, com tudo o
mais fixo. Os dois pontos que já temos:

| | `long01` | `long02` |
|---|---|---|
| dias consecutivos (teto, três contratos) | 7 / 5 / 5 | 4 / 4 / 4 |
| piso de atribuições | 6 / 6 / 3 | 8 / 6 / 4 |
| teto de atribuições | 16 / 12 / 5 | 16 / 11 / 5 |
| Z\* | 197 | 219 |
| concentração inevitável | 2,74× | 3,13× |
| margem de gestão | 1,73× | 1,43× |

Apertar a regra aumentou o custo, aumentou a concentração e reduziu a margem — as três na
direção ruim, ao mesmo tempo. Com dois pontos isso é observação. Com cinco vira resultado.

### A proposta

Rodar o Experimento B, forma B, em `long03` (Z\* = 240), `long04` (303) e `long05` (284),
fechando a série de cinco. Os valores da Tabela 6 estão em Santos et al. (2016), p. 248, e
os três têm ótimo provado, então o portão de validação de sempre continua valendo.

O que a série de cinco permitiria afirmar, e hoje não dá:

1. Se concentração e margem se movem **monotonicamente** com o aperto da regra, ou se `01` e
   `02` foram coincidência.
2. Se a faixa `E/Z*` (excesso forçado sobre o ótimo) de 73% a 81% se mantém, e se o excesso
   forçado prevê o ótimo dentro da série.
3. Um eixo de comparação para a instância brasileira: 12×36 contra 8 h é exatamente uma
   troca de regra de contrato com demanda fixa — o mesmo desenho, com outra regra.

**Custo.** `long01` levou 69 min e `long02` 193 min, então a série toda é da ordem de 6 a 10
horas de máquina, em rodadas separadas de madrugada. Não bloqueia o Experimento A.

**Contra.** O Experimento A é o resultado central e ainda não rodou; a P11 é aprofundamento
do B. Se o prazo apertar, ela cai inteira sem prejuízo do trabalho — e a observação da série
controlada continua valendo como nota metodológica sobre o benchmark, que não custa nada.

**Independente da decisão:** o fato da série controlada precisa entrar no texto de qualquer
forma, porque afeta como se lê qualquer média sobre o lote *early* — inclusive as de outros
autores. Não são médias sobre cenários independentes.

---

## 2026-09-22 — P12: o Experimento A responde zero, e a causa é a demanda achatada

**Status: DECISÃO 1 ACEITA em 2026-09-23, com o escopo estreitado. DECISÃO 2 DISSOLVIDA —
não era decisão nova. Prioridade 1 definida: sensibilidade à variação de demanda.**

O projeto de redação aceitou o resultado com a leitura estreita — *sob demanda uniforme,
nenhuma restrição de escalonamento aperta além do teto de horas* —, não "o regime não muda o
efetivo". Motivo: com perfil uniforme nenhuma restrição tinha como apertar, e as vinte células
são a mesma aritmética replicada, não vinte testes independentes. Registrado em `DECISOES.md`,
entrada de 23/09.

A decisão 2 caiu porque eu errei o diagnóstico: o núcleo do Experimento B ficou no INRC porque
a instância brasileira **não tem restrição flexível** e a penalidade seria zero — não porque a
pergunta não dependesse de regime. Isso não mudou. O que cabe é a extensão já decidida em
21/09: pedidos de folga sintéticos calibrados no `long01`, várias sementes, grau intermediário.
Ganhou prioridade, mas entra **depois** da sensibilidade de demanda.

**Implementado em 23/09** (execução de desenho validado, não proposta): variação de demanda
entre dias no gerador, com a forma medida no `long01` e o nível preservado; o piso de
alternância no `experimento_a.py`; e a varredura `--sensibilidade`. O registro abaixo fica
como escrito.

---

**Status original: aguardando validação.** Não implementei nada. O piloto rodou, o resultado está no
`resultados/experimento_a.csv`, e o que ele mostra exige uma decisão antes de virar capítulo.

### O que saiu

| célula | piso de capacidade | menor efetivo viável | distância |
|---|---|---|---|
| `intermediario` / 12x36 / teto | 36 | **36** | **0,0%** |
| `intermediario` / 8h / teto | 36 | **36** | **0,0%** |

Os dois regimes fecham escala legal **exatamente no piso aritmético**. A conferência no
avaliador oficial passou nos dois: zero violação nas três famílias que aqui são rígidas.

### Por que isso é zero, e por que eu desconfio do zero

Fui ver a demanda que o gerador emite. Com a regra `teto`, no grau `intermediario`:

- 12x36: 8 + 1 profissionais em cada turno, **todos os 28 dias**, sem exceção. D = 504;
- capacidade: 36 pessoas × 14 plantões = **504**. Demanda e capacidade são o mesmo número;
- 8 h: 8 + 1 em cada um dos três turnos, todos os dias. D = 756 = 36 × 21.

Ou seja: a instância pede um **empacotamento perfeito**, e existe um. O piso é atingido
porque a demanda é rigorosamente uniforme — o gerador deriva tudo de um perfil assistencial
horário constante, que é o que o Parecer COFEN sustenta, já que ele **não fornece curva
horária**.

Então o zero é honesto, mas é o zero do caso mais fácil possível. A pergunta do Experimento A
— *o regime de jornada muda o efetivo necessário?* — recebe a resposta "não", e recebe essa
resposta num cenário construído de um jeito que torna difícil ela ser outra coisa.

### As três saídas, e eu não escolho nenhuma

**(a) Aceitar o zero como resultado.** É defensável e é barato: *a escolha de regime não custa
efetivo a horas de assistência constantes; as regras de descanso da CLT são absorvidas sem
pessoa a mais nos dois regimes.* Resultado negativo, mas limpo, conferido no avaliador, e com
a ressalva da uniformidade declarada em voz alta. A comparação entre regimes migra para o
Experimento B — distribuição —, que é onde já há sinal.

**(b) Variar o perfil horário.** Um perfil com pico diurno faria o empacotamento perfeito
sumir e a distância aparecer, provavelmente diferente entre 8 h e 12x36. **Mas a curva seria
inventada**: o Parecer não tem essa informação, e o TCC passou três semanas estabelecendo que
o perfil contínuo é a primitiva justamente para não inventar repartição. Trocar isso é
reabrir a P5 pela porta dos fundos. Se for por aqui, a curva precisa de fonte.

**(c) Variar o horizonte ou o porte para quebrar a divisibilidade.** 5.920 h / 28 dias cai
redondo; outro porte não cairia. É mais barato que (b) e não inventa curva nenhuma — mas
mede sensibilidade à aritmética, não ao regime, e o achado seria sobre divisibilidade.

### O que eu recomendaria, se me perguntarem

(a), com a ressalva escrita, **e** rodar as vinte células antes de decidir — custa cerca de 15
minutos de máquina e dá o quadro inteiro em vez de duas células. Se as vinte derem zero, o
resultado negativo está sustentado em 5 graus × 2 regimes × 2 regras, e isso é bem mais forte
que duas linhas. Se alguma não der zero, a decisão muda sozinha.

Rodar as vinte é execução do desenho já validado, não desenho novo — **isso eu faço sem
esperar**, é só o comando `python src\experimento_a.py --todos`. O que não faço é (b) ou (c).

### Atualização de 22/09, mais tarde: as vinte células rodaram

Rodei o que disse que rodaria sem esperar. **As vinte deram o mesmo resultado:**

- efetivo mínimo viável = **36** em todas, igual ao piso de capacidade, distância **0,0%**;
- **conferência no avaliador oficial: `ok` nas vinte** — zero violação nas três famílias que
  aqui são rígidas (`MaxNumAssignments`, `MaxConsecutiveWorkingDays`, `UnwantedPatterns`);
- custo: de 1,8 s a 56,4 s de CPU por célula. O 12x36 é sistematicamente mais caro de
  resolver que o de 8 h (dezenas de segundos contra poucos), o que é sinal de que a
  alternância está de fato restringindo — não é um modelo frouxo devolvendo qualquer coisa.

O resultado negativo está sustentado em 5 graus × 2 regimes × 2 regras, com escala exibida e
conferida em cada célula. **A opção (a) ficou mais forte do que quando escrevi a proposta.**

**O que ainda falta, e é honesto dizer:** o intervalo está fechado só por cima. A sonda em
`efetivo = 35`, que deveria provar inviabilidade e fechar por baixo, **quebrou nas vinte** —
defeito meu no código, não do modelo (o solver levantava exceção em vez de devolver o
veredito; consertado depois). Até a sonda rodar, o que está demonstrado é *"36 basta"*, não
*"36 é o mínimo"*. O mínimo não pode ser menor por aritmética de capacidade, mas aritmética
não é o mesmo que o modelo ter dito.

### Fechamento de 23/09: o intervalo fechou dos dois lados nas vinte

A sonda consertada rodou. **As vinte células dão intervalo `[36, 36]`** — 35 com inviabilidade
provada pelo solver, 36 com escala exibida e conferência `ok` no avaliador oficial. Não é mais
"36 basta": é **36 é o mínimo**, demonstrado nos dois sentidos, em 5 graus × 2 regimes ×
2 regras.

**E o zero tem explicação mecânica, o que o torna menos frágil do que eu supus.** Os dois
regimes dão a mesma capacidade por pessoa *em horas*, porque o teto legal é o mesmo:

| regime | plantões em 28 dias | duração | horas | por semana |
|---|---|---|---|---|
| 12x36 | 14 | 12 h | 168 | **42 h** |
| 8 h | 21 | 8 h | 168 | **42 h** |

5.920 h ÷ 168 h = 35,24 pessoas, que é exatamente o `QP_ref` do Parecer. O mínimo viável é o
teto disso, 36, nos dois regimes. **O que o experimento demonstra não é que a distância é
zero, e sim que as regras de descanso não chegam a apertar: o que determina o efetivo é o
teto de 42 h/semana, e ele é igual nos dois regimes por lei.** No 12x36 a alternância um-sim-
um-não dá 14 plantões em 28 dias, exatamente o teto, e satisfaz as 36 h de descanso por
construção; no de 8 h, 21 dias de trabalho e 7 de folga sobram para o descanso semanal.

Isso é resultado, e é mais forte que "0,0%": **o modelo reproduz o QP do Parecer e mostra que
as regras de descanso não acrescentam nada a ele.**

**A ressalva da uniformidade continua valendo, mas menor do que eu escrevi.** Nas células
`teto` a demanda é rigorosamente uniforme e a capacidade iguala a demanda — empacotamento
perfeito. Nas células `maior_resto` a demanda **não** é uniforme (7 e 8 alternando conforme o
dia) e há folga de 11 plantões, e o resultado é o mesmo 36. É teste fraco de robustez, porque
a não-uniformidade é pequena, mas não é nulo.

**Um achado sobre o modelo, não sobre o regime:** o 12x36 é muito mais caro de resolver —
mediana de 23,9 s de CPU contra 5,0 s no de 8 h, com pico de 59,9 s. Mesma pergunta, mesma
resposta, cinco vezes a busca. A alternância rígida corta o espaço de um jeito que o solver
sente.

### Se o zero for aceito, para onde vai a comparação entre regimes

O Experimento A responde "o regime não muda o efetivo". A pergunta comparativa do trabalho
fica sem veículo, e há um óbvio: **rodar o Experimento B na instância brasileira**, com
efetivo fixo em 36, comparando a distribuição da penalidade entre 8 h e 12x36.

É exatamente o desenho que o projeto de redação pediu ao recusar a P11 — **um parâmetro por
vez, na instância brasileira** —, e aqui o parâmetro é o regime, com horas, porte, grau e
efetivo todos fixos. Mas contraria a decisão de 21/09, que restringiu o Experimento B às
instâncias do INRC justamente porque a pergunta dele não dependia de regime. Agora depende,
por um motivo que não existia então: A voltou nulo.

**Não implemento.** É mudança de escopo do Experimento B e precisa de validação. Se for
aprovada, o custo é da ordem do Experimento B numa instância de 36 pessoas — as sprints, com
10, levaram 6 minutos; com 36 deve ficar em dezenas de minutos por regime.
