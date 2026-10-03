# Propostas a validar

Registro de sugestões que afetam formulação, desenho experimental ou escopo.
**Não implementadas até validação.**

Arquivo recriado em 28/09/2026, depois da virada de escopo de 24/09. O `PROPOSTAS.md` do
escopo anterior, com as treze propostas P1–P13, está em
`historico/escopo-comparacao-regimes/PROPOSTAS.md`. A numeração recomeça.

---

## 2026-09-28 — P1: a curva de escalabilidade mede um problema mais fácil do que o da ferramenta

**Status: pendente — será refeita com o modelo final** (decisão do Otávio, 02/10: o modelo
vai mudar para carga por contrato e equilíbrio por fração do contrato). Uma rodada
preliminar foi feita em 02/10 e **não é resultado** — ver o fim desta entrada. Registro
anterior: decidida em 29/09; executa depois da Etapa 7 (ver DECISOES 2026-09-29, Redesenho). Registro anterior (28/09): aguardando
validação. Nada implementado. O experimento rodou como combinado e o
resultado está abaixo; o que proponho é sobre **como lê-lo**, e sobre uma rodada adicional.

*Atualização de 29/09/2026:* desbloqueada: objetivo decidido (ver `DECISOES.md`,
"2026-09-29 — Especificação da ferramenta").

### O que saiu

| N | demanda | variáveis | restrições | veredito | CPU (s) |
|---|---|---|---|---|---|
| 36 (âncora) | 504 | 3.696 | 5.008 | ótimo provado | 39 |
| 40 | 560 | 4.144 | 5.604 | ótimo provado | 63 |
| 60 | 840 | 6.160 | 8.272 | ótimo provado | 65 |
| 80 | 1.120 | 8.232 | 11.018 | ótimo provado | 239 |
| 120 | 1.680 | 12.320 | 16.432 | ótimo provado | 223 |
| 200 | 2.800 | 20.496 | 27.260 | ótimo provado | 549 |

Seis de seis com otimalidade provada, conferência `ok` e 36 h de descanso em todas. **Pelo
critério de 25/09, o warm start heurístico não se justifica nesta faixa.**

### A ressalva, e ela é grande

Na instância brasileira **o objetivo é degenerado**: com os limites legais rígidos, o que
resta ativo no contrato são restrições satisfeitas por qualquer escala, e o ótimo é zero. O
que a curva mediu foi **viabilidade**, não otimização. Assim que o solver acha uma escala
legal, a prova de otimalidade sai de graça, porque o limite inferior já é zero.

A ferramenta, porém, quase certamente vai ter objetivo de verdade: pedidos de folga,
preferências de turno, equilíbrio de carga entre profissionais — que é justamente a função
que o Experimento B já sustenta. **Com objetivo não trivial, a árvore de busca deixa de
fechar por construção**, e a curva pode ser outra.

Ou seja: o resultado responde *"o modelo atual escala até 200"*, e não *"o modelo da
ferramenta escalará até 200"*. São afirmações diferentes, e só a primeira está demonstrada.

### O que proponho

**Repetir a curva depois que a especificação definir o objetivo da ferramenta**, com pedidos
sintéticos ativos — mesmos seis tamanhos, mesmo procedimento. Aí sim a resposta sobre warm
start vale para o produto. Antes disso, a decisão de 25/09 fica respondida só para o caso
degenerado, e é assim que eu escreveria no texto.

Custo: a mesma coisa que custou agora, cerca de 20 minutos de máquina.

### Dois pontos menores, para o texto

**O tempo não é monótono no tamanho**: 239 s em N=80 contra 223 s em N=120. Uma medição por
tamanho é estimativa ruidosa. Como tempo de resolução já é afirmação fraca por critério do
projeto, isso não muda conclusão nenhuma — mas desaconselha qualquer frase do tipo "o tempo
cresce com o tamanho segundo tal padrão".

**Os 549 s em N=200 são um requisito de produto, não um resultado.** Uma unidade de 200
profissionais esperando nove minutos por uma escala é uma decisão de projeto de interface —
processamento assíncrono, resultado por e-mail, barra de progresso — e não uma limitação do
método. Vale entrar na especificação como requisito não funcional, com o número medido ao
lado.

### Rodada preliminar de 02/10 — NÃO É RESULTADO

Rodou com o objetivo da ferramenta da época (pesos inteiros + etapa 2 por amplitude de
horas), antes da mudança para carga por contrato. Foi registrada aqui como resultado por
engano e retirada no mesmo dia (o texto retirado fica no histórico do git, commit 85e8983).
Os logs ficam guardados em `resultados/preliminar_P1_2026-10-02/` (não versionado), só como
registro. **Nenhum número desta rodada vai ao texto.** A curva será lançada de novo depois do
item 1 do próximo bloco, com o modelo final, pelo mesmo script
(`src/escalabilidade_objetivo.py`).

---

## 2026-09-29 — P2: especificação da ferramenta

**Status: decidida em 29/09, ver `DECISOES.md`** ("2026-09-29 — Especificação da
ferramenta"). Registro anterior: rascunho, aguardando o orientador. Documento completo:
<https://claude.ai/code/artifact/ebfaeed9-a670-49d7-8f24-0067a43f2f04>

- **Quadro como entrada**: o usuário informa o efetivo; a fórmula do Parecer aparece ao lado
  só para comparação.
- **Composição**: proporção de enfermeiros aplicada ao quadro, com piso de 1 enfermeiro por
  turno.
- **Carga semanal de 42 h.**
- **Horizonte**: início numa segunda-feira, 28 dias.
- **Variação de demanda por dia da semana**: entrada opcional.
- **Objetivo em duas etapas** (proposta): primeiro pedidos, depois equilíbrio entre
  profissionais.
- **Licença MIT** (proposta).

A P1 está desbloqueada: objetivo decidido.

---

## 2026-09-29 — P3: trabalhos futuros

**Status: só registro.** Nada a implementar no TCC.

- **Diagnóstico de turnos descobertos** quando o quadro não basta. Exige cobertura flexível,
  o que muda a definição de viável.
- **Habilidades além de enfermeiro e técnico.**
- **Integração com IA** para converter descrição livre em configuração.
- **Continuidade entre períodos** (acrescentado em 29/09): receber os últimos dias do
  período anterior como entrada, para conferir interjornada e descanso na virada entre uma
  escala e a seguinte. Ver `DECISOES.md`, "2026-09-29 — Ajustes da Etapa 2".

---

## 2026-10-02 — P4: amplitude de carga com férias e licenças

**Status: RESOLVIDA em 02/10 pelo item c) da decisão "2026-10-02 — Carga por contrato"**
(`DECISOES.md`): a etapa 2 passou a equilibrar a fração do contrato cumprida, com
denominador nas horas devidas nos dias disponíveis — uma variante da saída 2 abaixo, que
compara todos. Conferido no teste 9c (03/10): quem tem 14 dias de férias ficou com 81,8% do
devido, dentro da faixa dos demais. Registro anterior: aguardando decisão.

A etapa 2 passou a minimizar a amplitude de carga do período (maior carga − menor carga, em
horas), sobre **todos** os profissionais, como decidido em 02/10. Quem tem férias ou licença
no período tem a carga limitada pelos dias disponíveis: no 12×36, com uma semana de férias,
cabem no máximo 11 plantões nos 21 dias restantes (alternância), 132 h, contra 14 plantões e
168 h de quem está o período inteiro. Essa pessoa vira, por construção, a menor carga, e
a amplitude passa a medir a distância até ela, não o desequilíbrio entre quem trabalhou o
período inteiro. No limite, minimizar a amplitude vira minimizar a maior carga, e a etapa 2
pode **empurrar carga para quem tem férias** até o teto dos dias livres dela, só para
aproximar o piso — o que é o contrário do que se quer.

Duas saídas, as duas mudança de formulação:

1. **Amplitude só entre quem não tem indisponibilidade no período.** Simples; quem tem férias
   fica fora do critério (mas continua sob o teto de 42 h/semana).
2. **Amplitude da carga proporcional** — horas ÷ dias disponíveis × 28. Compara todos, mas
   introduz uma divisão por constante por pessoa (continua linear, porque os dias
   disponíveis são dado).

Recomendo a 1, por ser a que se explica em uma frase na tela. Enquanto não decidido, a
ferramenta faz o que foi decidido (todos), e a tela mostra a amplitude que resultou.

---

## 2026-10-02 — P5: teste de uso qualitativo com 1 ou 2 profissionais de enfermagem

**Status: não executada, por decisão** (Otávio, 02/10). O escopo está congelado, e o
orientador já aceitou a validação sem teste em hospital: o motor é validado contra o
benchmark INRC-2010, com ótimos publicados, e a conformidade legal é conferida por medição
independente do modelo (`docs/conferencia_descanso_escala.py`).

O que seria: uma ou duas enfermeiras com experiência em montar escala usariam a ferramenta
numa configuração real da unidade delas e diriam, em entrevista curta, se a escala é
aplicável e o que falta. Mediria usabilidade e aderência à prática, que nenhuma das
conferências atuais mede.

**Entra no texto como limitação declarada**: a ferramenta não foi testada por usuários
finais; a validação cobre a correção do motor e a conformidade legal, não a adoção.

---

## 2026-10-03 — P6: a amplitude da fração fica presa à separação entre categorias

**Status: aguardando decisão.** Nada implementado. Achado pelo teste 9c (`DECISOES.md`,
"2026-10-02 — Carga por contrato").

**O que acontece.** A etapa 1 penaliza enfermeiro em posto de técnico. Quando os enfermeiros
bastam para o posto de enfermeiro, o ótimo é não usar nenhum enfermeiro em posto de técnico, e
a etapa 2, que fixa esse ótimo, herda a separação. Os enfermeiros cumprem a fração que o posto
de enfermeiro dá (no 9c, 672 h ÷ 6 = 112 h, 63,6%), os técnicos a que o posto de técnico dá
(≥ 88,5% em média, 90,9% no máximo pelos degraus de 8 h). A amplitude mínima é a diferença
entre as duas, **27,3 pp no 9c** (e, pelo critério anterior em horas, os 48 h do caso de 40 do 12×36) — e equilibrar não mexe nisso.
A amplitude que a tela mostra mede, então, a razão entre a demanda de cada categoria e o
tamanho de cada categoria, não a justiça da escala.

**Por que importa.** A tela diz "a diferença entre a maior e a menor fração caiu para 27%", e
um gestor lê isso como desequilíbrio entre colegas. Na verdade é desequilíbrio entre
categorias, que vem do quadro informado (enfermeiros de sobra para o posto deles), e a
resposta certa seria "há enfermeiros ociosos em relação ao contrato".

**Três saídas, todas mudança de formulação ou de apresentação:**

1. **Equilibrar dentro de cada categoria**: amplitude entre enfermeiros + amplitude entre
   técnicos (ou a maior das duas). Mede justiça entre colegas que fazem o mesmo trabalho. A
   diferença entre categorias passa a ser informada à parte.
2. **Manter o critério e explicar na tela**: mostrar a fração média por categoria ao lado da
   amplitude, com a frase "enfermeiros cumprem X% do contrato porque o posto de enfermeiro
   não ocupa mais que isso".
3. **Deixar a etapa 1 trocar enfermeiro em posto de técnico por equilíbrio** — mexe na
   prioridade decidida em 29/09 (pedidos, depois enfermeiro em posto de técnico) e não
   recomendo.

Recomendo a 1, com a informação da 2 na tela. É troca de critério da etapa 2, que é decisão do
projeto de redação.

**Impacto na P1:** nenhum sobre o que a P1 mede (prova e gap por etapa), mas a P1 deve rodar
com o critério final da etapa 2. Por isso não foi relançada em 03/10.

