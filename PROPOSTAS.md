# Propostas a validar

Registro de sugestões que afetam formulação, desenho experimental ou escopo.
**Não implementadas até validação.**

Arquivo recriado em 28/09/2026, depois da virada de escopo de 24/09. O `PROPOSTAS.md` do
escopo anterior, com as treze propostas P1–P13, está em
`historico/escopo-comparacao-regimes/PROPOSTAS.md`. A numeração recomeça.

---

## 2026-09-28 — P1: a curva de escalabilidade mede um problema mais fácil do que o da ferramenta

**Status: CONCLUÍDA em 05/10** (decisão do Otávio). Curva principal de 03/10 (caso mais
apertado) e rodada complementar com folga de 05/10, ambas abaixo. Registro anterior:
**rodada pelo caminho da ferramenta em 03/10; resultado registrado em 05/10** (ver
"Rodada de 03/10", no fim desta entrada: a prova fecha até N = 80; a etapa 2 é degenerada
em todos os tamanhos). Registro anterior: **pendente — será refeita com o modelo final** (decisão do Otávio, 02/10: o modelo
vai mudar para carga por contrato e equilíbrio por fração do contrato). *Atualização de
03/10:* lançada às 14:29 de 03/10 com o modelo final (etapa 2 por categoria, P6), 900 s
por etapa. **Correção de 03/10: a rodada morreu às 14:30**, logo depois da etapa 1 de N = 36
(ótimo provado em 27 s), com `TypeError` em `Instancia.horas_devidas`: as instâncias do
caminho antigo (`escalabilidade.construir`) não têm carga contratual, e a fração do contrato
não pode ser calculada. Não gerou CSV e não há resultado. O relatório 03b e o commit
`2284b75` disseram "lançada" sem conferir o primeiro tamanho completo. *Decisão do Otávio
(03/10):* a P1 passa a medir o caminho da FERRAMENTA (`ferramenta.montar`, 44 h para todos,
12×36), com a demanda por turno igual à do caminho antigo em cada tamanho; teste de
equivalência em N = 36 e 40. Ver `resultados/relatorio_2026-10-03c.md`. Uma rodada
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

### Rodada de 03/10, caminho da ferramenta — resultado (registrado em 05/10)

Lançada às 19:33 de 03/10 e terminada normalmente às 20:22, sem erro. Os seis tamanhos têm
linha no CSV; quatro com as duas etapas. Parâmetros: 12×36, 44 h para todos, 2 pedidos por
pessoa (semente 20261002 + N), 900 s por etapa, `appsi_highs`. Log:
`resultados/escalabilidade_objetivo/p1_2026-10-03_ferramenta.log`; CSV:
`resultados/escalabilidade_objetivo.csv`. Máquina: Intel Core i5-10210U (4 núcleos, 8
threads), 12 GB, Windows 11, Python 3.11.9, HiGHS 1.15.1 via appsi. **Tempos são limite
operacional desta máquina, uma medição por tamanho — não resultado.**

| N | etapa 1 | 1ª escala legal | etapa 2 | pedidos negados | enf. em posto de téc. | descanso |
|---|---|---|---|---|---|---|
| 36 | ótimo provado, 40 s | 39 s | ótimo provado, 10 s | 21 de 72 | 112 | cumpre |
| 40 | ótimo provado, 168 s | 54 s | ótimo provado, 16 s | 21 de 80 | 140 | cumpre |
| 60 | ótimo provado, 130 s | 129 s | ótimo provado, 18 s | 29 de 120 | 224 | cumpre |
| 80 | ótimo provado, 693 s | 235 s | ótimo provado, 34 s | 50 de 160 | 322 | cumpre |
| 120 | **sem prova** (limite), gap 3,2% | 346 s | não rodou (etapa 1 sem prova) | 63 de 240; limite inferior 61 | 504 | cumpre |
| 200 | **sem escala** em 900 s (nó raiz não terminou) | — | não rodou | limite inferior 111 de 400 | — | — |

A penalidade recontada a partir da escala bateu com a do solver em todos os tamanhos com
escala. Rígidas OK em todos.

**O que se pode dizer:** com o objetivo da ferramenta, a prova de otimalidade fecha até
N = 80 e deixa de fechar a partir de N = 120 em 900 s nesta máquina. Em N = 120 a escala
existe e a distância é de 2 pedidos (63 negados contra o limite de 61); em N = 200 nenhuma
escala legal apareceu no limite. Pelo critério de 25/09, existe faixa em que a prova não
fecha — é a condição para admitir warm start como partida.

**Ressalva grande — a etapa 2 é degenerada em todos os tamanhos, por construção.** A
instância de escalabilidade foi montada para o piso cair em N (`escalabilidade.porte_para`):
a demanda é 14N plantões, exatamente a capacidade de N pessoas a 14 plantões. Com a
alternância do 12×36, todo mundo faz exatamente 14 plantões (168 h), e a amplitude da fração
é 0 já na etapa 1, em todos os tamanhos. A etapa 2 só reencontra uma escala com a penalidade
fixada; o tempo dela não mede a dificuldade de equilibrar. **O relatório de 03/10 (03c)
afirmou que nos tamanhos maiores haveria folga — estava errado**: os 164,4–167,4 h do
docstring de `escalabilidade.py` são horas de porte, não de demanda.

**Também forçados pela conta, não escolhidos pelo solver:** os turnos de enfermeiro em posto de
técnico, (técnicos × 14) contra 28 × 2 × (técnicos por turno). Em N = 36: 24 × 14 = 336 para
448, faltam 112. A parte do objetivo que o solver de fato decide são os pedidos de folga. E a
liberdade de cada pessoa é pequena: 14 dias de trabalho em 28 sem dois seguidos admitem só
C(15, 14) = 15 conjuntos de dias.

**Leitura decidida pelo Otávio (05/10).** A rodada de 03/10 mede o **caso mais apertado**:
demanda = 168 h por pessoa, sem folga. Nela, a prova fecha até N = 80; N = 120 tem escala
legal sem prova (gap 3,16%); N = 200 fica sem escala em 900 s. Tempo é limite operacional
desta máquina, não resultado.

**Decidido em 05/10: rodada complementar com folga** (`escalabilidade_objetivo.py --folga`),
para medir a etapa 2: mesma demanda de 40, 60 e 80, equipe 10% maior (44, 66, 88), 12×36,
44 h, 2 pedidos por pessoa (mesma semente), 900 s por etapa. Registra também a amplitude por
categoria antes e depois da etapa 2 e o tempo até 90% da redução final, para decidir o limite
da etapa 2 na tela. O limite da etapa 1 na tela fica em 600 s (decidido); o da etapa 2 não
muda até essa rodada terminar.

**Rodada com folga — resultado (05/10).** Terminou normalmente, sem erro. CSV:
`resultados/escalabilidade_objetivo_folga.csv`; logs `folga_teste_N40_2026-10-05.log` (40/44,
o caso de teste rodado até o fim antes do lançamento) e `folga_2026-10-05.log` (60/66 e
80/88). Máquina: i5-10210U, 12 GB, Windows 11, Python 3.11.9, HiGHS 1.15.1 via appsi. Tempos são
limite operacional desta máquina, uma medição por tamanho.

| Demanda / equipe | Etapa 1 | 1ª escala | Etapa 2 | Gap etapa 2 | Amplitude enf. | Amplitude téc. | Total | 90% da redução |
|---|---|---|---|---|---|---|---|---|
| 40 / 44 | ótimo provado, 21 s | 1,9 s | limite, sem prova, 902 s | 19,6% | 27,27 → 6,82 | 6,82 → 6,82 | 34,09 → 13,64 | 18 s |
| 60 / 66 | ótimo provado, 39 s | 2,2 s | limite, sem prova, 904 s | 26,1% | 13,64 → 6,82 | 6,82 → 6,82 | 20,45 → 13,64 | 46 s |
| 80 / 88 | ótimo provado, 62 s | 3,0 s | limite, sem prova, 907 s | 37,5% | 20,45 → 6,82 | 6,82 → 6,82 | 27,27 → 13,64 | 81 s |

Em todos: pedidos atendidos 100%; descanso e rígidas OK; penalidade recontada = a do solver.
Nos três, a primeira escala da etapa 2 já foi a final: o "90% da redução" coincide com ela, e
nenhuma melhora veio depois.

**A escala final é ótima pela conta, não pela prova do solver** (conta feita DEPOIS de ver o
resultado; aritmética, independente do solver). Com a penalidade presa no ótimo e todos os
pedidos atendidos, o total de enfermeiros em posto de técnico é fixo. Cada plantão vale 12 / 176 =
6,82 pp. Uma categoria só tem amplitude 0 se os seus plantões se dividirem igualmente:
enfermeiros 163/15 = 10,87, 237/22 = 10,77, 323/30 = 10,77; técnicos 397/29 = 13,69,
603/44 = 13,70, 797/58 = 13,74. Nenhuma divisão é exata, então o piso é 2 × 6,82 = 13,64 pp nos
três — o valor encontrado. Os gaps (19,6%, 26,1%, 37,5%) são fraqueza do limite inferior do
solver.

**Para o limite da etapa 2 na tela (decisão do Otávio):** a melhor escala veio entre 18 s e 81 s;
o resto dos 900 s não melhorou nada.

**Leitura decidida pelo Otávio (05/10).** Com folga, a etapa 2 acha a melhor escala cedo — 18 s
com 44 profissionais, 46 s com 66, 81 s com 88 — e o restante do tempo vai na prova, que não
fecha em 900 s. A amplitude obtida coincide com o piso aritmético (2 × 6,82 = 13,64 pp); a conta
foi feita APÓS o resultado e é explicação, não previsão. Tempo é limite operacional desta
máquina. **Consequência (05/10):** limite da etapa 2 na tela = max(120 s; 1,5 × 81,1 s) =
121,7 s, arredondado para cima ao minuto = **180 s** (`ferramenta.TEMPO_ETAPA2`); a etapa 1
continua com 600 s. A etapa 2 deixa de mostrar gap e mostra a diferença máxima de carga entre
colegas dentro de cada categoria, em plantões e horas (`DECISOES.md`, "Carga por contrato",
item i).

**Proposta original (05/10, agora decidida acima):** se o texto precisar dizer algo sobre
o custo da etapa 2, rodar a etapa 2 numa instância com folga — por exemplo, a mesma demanda com
equipe N + k — e declarar que a curva de 03/10 mede a etapa 1. Sem isso, a P1 responde à
pergunta da etapa 1 (pesos inteiros, pedidos) e a etapa 2 fica sem medição.

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
  *Acrescentado em 06/10:* **replanejamento no meio do período** — receber a escala em vigor,
  fixar os dias já cumpridos e minimizar mudanças. Recalcular do zero com novo início não
  substitui isso.
- **Critério de parada por estagnação do gap** (acrescentado em 06/10, P11). Ver P11.
- **Arquivo de configuração** (acrescentado em 05/10, decisão do Otávio): o pacote com o XML
  no formato INRC mais o complemento com o que o formato não representa (indisponibilidades),
  para baixar e carregar na tela, com validação e resumo em português. Ver `DECISOES.md`,
  "2026-10-05 — Arquivo de configuração vira trabalho futuro".
- **Fechar o `medium_late05`** (acrescentado em 06/10, P9): provar o ótimo de 107 exigiria
  formulação reforçada ou solver comercial. Ver P9.
- **Teste da ferramenta com quem monta escala** (acrescentado em 06/10, da P10 descartada):
  validação de face com enfermeiros que montam escala de verdade. No texto, entra como
  limitação declarada. Ver P10 e P5.
- **Parar a etapa 2 ao atingir o piso aritmético da amplitude** (acrescentado em 05/10, P1):
  simples só com contrato e turno homogêneos e sem indisponibilidade. Na rodada com folga, a
  etapa 2 chegou ao piso entre 18 e 81 s e gastou o resto do tempo tentando provar.
- **Recuperar o resultado na tela quando a conexão do navegador cai durante o cálculo**
  (acrescentado em 08/10, da P12): guardar o resultado no servidor, indexado pela entrada,
  para que a sessão nova, depois de reconectar, mostre o que já foi calculado em vez do
  formulário vazio. Motivo: em 07/10, uma queda de conexão (`ConnectionResetError` 10054 no
  console do Streamlit) fez a tela voltar ao formulário sem resultado.
- **Descanso semanal de 35 h como regra rígida** (acrescentado em 09/10, da P15): hoje é alerta
  (Súmula 110 do TST atribui custo, não proíbe). Endurecer exigiria uma restrição nova no
  modelo — o descanso semanal hoje só é medido na escala pronta, não é restrição.
- **Preferências individuais** (acrescentado em 09/10, por pedido do Otávio; decisão depois):
  (1) **pedido por turno** ("não quero o turno X no dia D"): o modelo já aceita (`folga_turno`,
  o `ShiftOffRequest` do INRC, validado pela regressão); falta a entrada brasileira, a tela e a
  prioridade estrita em três níveis de peso, com o cuidado da tolerância relativa do HiGHS —
  análise e estimativa em `resultados/relatorio_2026-10-09c.md`, parte B;
  (2) **indisponibilidade recorrente** (ex.: segundo vínculo toda terça);
  (3) **marcação por profissional "exige 35 h de descanso semanal"** (a P15 é alerta para todos).
- **Mostrar a melhor escala encontrada durante a busca da etapa 1**, antes do fim do tempo-limite
  (acrescentado em 09/10, decisão do Otávio): exige rodar o solver em paralelo à tela, como o
  relógio ao vivo da P12.

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

**Status: RESOLVIDA em 03/10 — saída 1, decisão do Otávio**: a etapa 2 equilibra dentro de
cada categoria (amplitude entre enfermeiros + amplitude entre técnicos), e a diferença entre
categorias é mostrada à parte, não otimizada; com ela, um indicador novo de horas de contrato
não utilizadas por categoria. Implementada e testada em 03/10 — ver `DECISOES.md`, "2026-10-02
— Carga por contrato", itens g) e h). O 9c, refeito por este critério com a conta registrada
antes, acertou (enfermeiros 0, técnicos 4,55 pp, provado).

*Registro anterior:* aguardando decisão. Achado pelo teste 9c (`DECISOES.md`,
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


---

## 2026-10-05 — P7: o diagnóstico da trava diz "combinação" quando uma conta simples explica

**Status: DECIDIDA em 05/10 pelo Otávio — implementar como correção do diagnóstico** (sem
mudar modelo nem objetivo). Ver `DECISOES.md`, "2026-10-05 — Diagnóstico da trava: teto pela
alternância e férias no par". *Registro anterior:* aguardando decisão. Achado ao preparar a
rodada 2 da demonstração (`docs/demonstracao/cortes_esperados.md`).

**O que acontece.** Na clínica médica da demonstração com 20 técnicos (28 pessoas), duas
contas simples já mostram que não há escala: (a) as horas de técnico que faltam (324 h) passam
da folga dos enfermeiros (312 h), contando o teto de cada um pela alternância do 12×36 (14
plantões = 168 h); (b) no par 03–04/11, 28 plantões para 27 pessoas disponíveis, porque uma
técnica está de férias. O diagnóstico da ferramenta (`ferramenta.diagnosticar`) não enxerga
nenhuma das duas e diz "combinação de regras":

- a regra de alternância compara a soma de dois dias com o quadro inteiro, sem descontar quem
  está de férias num dos dois dias;
- a regra de horas usa o teto do contrato (176 h para 44 h), não o menor entre ele e o da
  alternância, e não separa as horas do posto de técnico (que só técnico ou enfermeiro cobre)
  da folga dos enfermeiros.

**Por que importa.** "Combinação de regras" diz ao gestor que não há explicação simples,
quando há: "no par 03–04/11, com Karen de férias, faltam pessoas" é acionável.

**Proposta:** nas duas regras, descontar as férias do par e usar o teto pela alternância.
Mudança de funcionalidade, com o congelamento em 10/10: decisão do Otávio.

---

## 2026-10-05 — P8: empate de carga entre grupos de pacientes, no alerta de proporção

**Status: DECIDIDA em 05/10 pelo Otávio** — mantém o comportamento atual: o alerta avisa o
empate e usa o maior percentual dos empatados; escolha da ferramenta (conservadora), não regra
do Parecer. Ver `DECISOES.md`, "2026-10-05 — Empate de carga entre grupos de pacientes".
*Registro anterior:* aguardando decisão. Aberta pela decisão "2026-10-05 — Grau da
proporção: o grupo de pacientes de maior carga".

O Parecer manda seguir o grupo de maior carga de trabalho, mas não diz o que fazer quando dois
grupos têm a mesma carga (por exemplo, 3 de cuidados mínimos = 12 h e 2 intermediários = 12 h).
Enquanto não houver decisão, a ferramenta diz no alerta que houve empate, nomeia os graus e
conta com o maior percentual dos empatados, declarando isso. Saídas possíveis: maior
percentual (conservador); maior número de pacientes ("prevalência", a palavra dos exercícios);
ou exigir que o usuário escolha.

---

## 2026-10-06 — P9: fechar o `medium_late05`

**Status: decidida em 06/10 pelo Otávio — NÃO executar antes de 04/11.** Recomendação de não
executar, acatada; vai para trabalhos futuros (P3).

**O que se sabe.** Em 06/10, com limite de 3.600 s, `appsi_highs`: melhor escala de **224**,
limite inferior **63**, gap **71,88%**, sem prova; o ótimo publicado é 107 (Tabela 6). O
avaliador oficial e o `avaliacao.py` confirmam 224 na escala obtida
(`resultados/medium_late05_2026-10-06/`; `resultados/relatorio_2026-10-06b.md`).

**Por que não executar.** Mais tempo e ajuste de parâmetros do HiGHS têm efeito marginal: o gap
de 71,88% vem do **limite inferior fraco** (63 contra 107), não de falta de busca por escala.
Fechar exigiria **formulação reforçada** — mudança de formulação, fora do congelamento — ou
**solver comercial**, o que muda o solver da validação.

**O que a validação do modelo já tem sem isso:** os 4 ótimos provados (56, 58, 197, 219 =
Tabela 6) e, no `medium_late05`, a concordância modelo = `avaliacao.py` = avaliador oficial
em 224 — que confere a semântica das restrições e dos pesos que só essa instância exercita,
mesmo sem o ótimo.

---

## 2026-10-06 — P10: validação de face com quem monta escala

**Status: DESCARTADA em 06/10 pelo Otávio** — sem contato viável no prazo. Não será feita no
TCC. Vai para trabalhos futuros (P3) como "teste da ferramenta com quem monta escala"; no texto,
entra como **limitação declarada**.

*Nota de numeração:* a P10 foi proposta no projeto de redação e não tinha entrada neste arquivo
(aqui não há P9). É o mesmo tema da P5 (teste de uso qualitativo com 1 ou 2 profissionais, não
executada por decisão de 02/10); as duas levam à mesma limitação declarada.

---

## 2026-10-06 — P11: critério de parada por estagnação do gap

**Status: trabalho futuro** (decisão do Otávio, 06/10; não implementar). Entra na P3.

**A ideia.** Parar a etapa 1 quando nem a melhor escala nem o limite inferior melhoram em T
segundos; ou aceitar uma tolerância de gap declarada.

**Validação proposta.** Medir nos logs do HiGHS o tempo até a escala final, até a prova e as
estagnações, como foi feito para os 180 s da etapa 2 (P1, rodada com folga).

**Limite.** Não acelera a prova de inviabilidade na busca do menor quadro, e aumentaria os
"não determinado".

**Risco.** Gap parado que fecha de repente: a parada cortaria a prova logo antes de ela sair.

---

## 2026-10-06 — P12: orçamento total de tempo por clique

**Status: DECIDIDA em 07/10 pelo Otávio — aprovada, exceto o item adicional** (tetos do
diagnóstico no piso), que fica para decisão depois porque muda quais quadros vão ao solver.
Ver `DECISOES.md`, "2026-10-08 — P12 aprovada". *Status anterior: aguardando decisão do
Otávio.*

**A proposta:**
- um limite total por clique em "Gerar escala" (por exemplo, 15 min). Esgotado, a tela mostra
  só o que foi provado: nunca "faltam N" sem prova de inviabilidade;
- um indicador de progresso: o quadro em teste e o tempo decorrido;
- trocar "o solver falhou" por um texto que diga o que houve (por exemplo, "sem resposta em
  10 min").

**Item adicional:** usar em `ferramenta.piso` os tetos do diagnóstico de 05/10
(`ferramenta.teto_horas`: carga nos dias disponíveis e alternância do 12×36), para descartar
por conta os tamanhos que a aritmética prova insuficientes, sem gastar solver neles.

**Condição, se aprovada:** a demonstração da clínica sai idêntica, com esperado registrado
antes.

---

## 2026-10-07 — P13: conta de "ocupados por dia" no piso e no diagnóstico, para turnos de 12 h ou mais

**Status: candidata a melhoria — NÃO implementar** (parte A do diagnóstico de 07/10). *Não
confundir com a P13 do escopo anterior, que está no histórico e foi fechada em 06/10.*

**O que falta hoje.** Com turnos de 12 h ou mais misturados a turnos curtos (o modelo "6 h de dia
+ noturno de 12 h"), nem o `ferramenta.piso` nem o diagnóstico da trava (`motivos_da_trava`)
fazem a conta do descanso pós-noturno. Quem faz o noturno de 12 h no dia d não trabalha em
d + 1. Então, em cada dia, os postos do dia **mais** os postos do noturno da véspera têm de
caber nas pessoas disponíveis.

**O caso que mostrou isso.** No caso do Otávio (M 2 + 1, T 2 + 1, N 3 + 2), a conta dá 16
ocupados por dia, com pelo menos 10 enfermeiros: 16 é fronteira (`docs/diagnostico/`). O piso
da ferramenta dá 13, por horas, e o diagnóstico não vê motivo simples. A regra dos dois dias
seguidos só existe hoje para o 12×36 puro (`limite_efetivo` = 1).

**Proposta.** Generalizar a conta dos dois dias seguidos para "turnos que bloqueiam o dia
seguinte", medidos dos horários, nas duas condições: todos e só enfermeiros. A conta já está
escrita, independente da ferramenta, em `docs/diagnostico/bateria_desenho.py` (`conta`).

**Condição, se aprovada:** é mudança de funcionalidade (piso e diagnóstico), fora do
congelamento, salvo se for tratada como correção de defeito. Tem de passar com esperado
registrado antes, e a demonstração da clínica tem de sair idêntica.

---

## 2026-10-09 — P15: descanso semanal abaixo de 35 h

**Status: DECIDIDA em 09/10 pelo Otávio — entra como ALERTA, não como regra rígida.** Ver
`DECISOES.md`, "2026-10-09 — P15: alerta de descanso semanal abaixo de 35 h". A regra rígida
foi para trabalhos futuros (P3). *Proposta originada no projeto de redação; registrada aqui ao
ser decidida.*

**A questão.** A CLT (art. 67) exige repouso semanal de 24 h, e a ferramenta trava abaixo
disso. A jurisprudência soma a ele o intervalo de 11 h entre jornadas (art. 66): Súmula 110 do
TST (Res. 121/2003) e OJ 355 da SDI-1 mandam pagar como extras as horas que invadem as 11 h
depois do repouso de 24 h — 24 + 11 = 35 h.

---

## 2026-10-09 — P14: etapa 2 também sem prova da etapa 1

**Status: DECIDIDA em 09/10 pelo Otávio — aprovada.** Ver `DECISOES.md`, "2026-10-09 — P14:
etapa 2 também quando a etapa 1 não prova o ótimo". *Proposta originada no projeto de redação;
registrada aqui ao ser decidida.*

**A questão.** Quando a etapa 1 termina com escala mas sem prova de ótimo, a etapa 2 não rodava,
e a escala saía sem equilíbrio de carga entre colegas. Proposta: rodar a etapa 2 com a restrição
de não piorar o valor da etapa 1, em vez de exigir o ótimo provado.

---

## 2026-10-09 — P16: melhorias de tela para a janela de 26 a 29/10

**Status: lista aprovada pelo Otávio em 09/10, para a janela de 26 a 29/10** (melhoria de tela
e textos de ajuda, sem mudar comportamento nem número; `DECISOES.md`, "2026-10-06 —
Cronograma", E2). Nada implementado.

- "Pedidos de folga atendidos: 0 de 0" → "sem pedidos de folga".
- Mostrar o gap em unidades do problema, não em %. Exemplo: "esta escala usa 57 turnos de
  enfermeiro em vaga de técnico; o melhor possível está entre 47 e 57".
- Separar visualmente "o seu quadro" da "escala sugerida" na tela de quadro insuficiente.

---

## 2026-10-09 — P17: warm start da etapa 2 com a escala da etapa 1

**Status: DECIDIDA em 09/10 pelo Otávio — implementada** (decisão condicional: a interface
permitia de forma simples e documentada). Ver `DECISOES.md`, "2026-10-09 — P17". Testes
pendentes, para rodar com a máquina limpa. *Status anterior: candidata — não implementar.*

**O achado.** Com a P14, a etapa 2 roda também quando a etapa 1 não prova o ótimo, com a
restrição de não piorar o valor dela. Em 4 resoluções sem prova (caso do Otávio de 09/10, K5,
K6, teste 8b), só o K5 entregou escala no tempo; nas outras 3 ficou a escala da etapa 1
(`resultados/relatorio_2026-10-09b.md`, parte B). Causa provável: a etapa 2 não parte da escala
da etapa 1 (o código não usa warm start); com "penalidade ≤ valor da etapa 1", achar a primeira
escala é tão difícil quanto chegar àquele valor (no caso do Otávio, 600 s).

**Proposta.** Passar a escala da etapa 1 ao HiGHS como solução inicial da etapa 2. É warm start
"só como partida", admitido pelo `CLAUDE.md` (25/09): não substitui prova nenhuma — a etapa 2
não prova nada no caminho sem prova. Garante que a etapa 2 sempre tenha escala e dispensa a
salvaguarda. Exige conferir se o `appsi_highs` aceita solução inicial e se a demonstração sai
idêntica (no caminho provado, a etapa 2 também ganharia a partida).

