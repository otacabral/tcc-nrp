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

**Status:** aguardando validação. Bloqueia a instância brasileira. É desenho experimental, não
implementação — por isso está aqui e não foi aplicada.

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

**Status:** aguardando validação. Não é proposta de mudar nada — é o registro de que uma
mudança **já aconteceu** por consequência da P5, e precisa ser declarada antes de virar
capítulo.

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

**Status:** aguardando validação. O critério da decisão de 21/09 está certo; a **lista de
quais restrições entram está errada em dois itens**, e o que sobra depois de corrigi-la é
pequeno demais para sustentar o Experimento B como desenhado.

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

## Nota de contenção, 18/09 — o lugar do achado da reagregação

O achado já rendeu três revisões, uma varredura nas 69, um grupo de controle e dois scripts.
É metodologia, **não é o resultado do TCC**. O lugar dele é uma subseção do capítulo de dados,
justificando por que a instância brasileira nasce de perfil contínuo. Só isso.

O resultado do trabalho continua sendo o Experimento A e o B, que ainda não rodaram e dependem
de três fontes normativas que ainda não existem. **O achado está fechado**: as próximas horas
vão para as fontes, não para mais uma medição sobre ele. Registrado aqui para que nenhuma
sessão futura o reabra por parecer interessante.
