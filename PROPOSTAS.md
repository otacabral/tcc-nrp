# Propostas a validar

Registro de sugestões que afetam formulação, desenho experimental ou escopo.
**Não implementadas até validação.**

Arquivo recriado em 28/09/2026, depois da virada de escopo de 24/09. O `PROPOSTAS.md` do
escopo anterior, com as treze propostas P1–P13, está em
`historico/escopo-comparacao-regimes/PROPOSTAS.md`. A numeração recomeça.

---

## 2026-09-28 — P1: a curva de escalabilidade mede um problema mais fácil do que o da ferramenta

**Status: CONCLUÍDA em 02/10.** Resultado na seção "Rodada de 02/10", no fim desta
entrada. Registro anterior: decidida em 29/09; executa depois da Etapa 7 (ver DECISOES
2026-09-29, Redesenho). Registro anterior (28/09): aguardando
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

### Rodada de 02/10 — com o objetivo da ferramenta

`python src\escalabilidade_objetivo.py --tempo 900`. **Mesmas seis instâncias** da rodada
de 28/09 (12×36, grau intermediário, piso = N); **muda só o objetivo**: o completo da
ferramenta (etapa 1 com pesos inteiros, etapa 2 minimizando a amplitude de carga em horas com
a etapa 1 fixada no ótimo; a etapa 2 só roda sobre ótimo provado) e **2 pedidos de folga por
profissional**, em datas distintas sorteadas com `random.Random(20261002 + N)` — semente
20261002. Limite de **900 s por etapa**, que agora de fato chega ao solver (ver DECISOES,
"Redesenho", nota de 02/10). Máquina: Intel Core i5-10210U (4 núcleos, 8 threads), 12 GB,
Windows 11, Python 3.11.9, HiGHS 1.15.1 via appsi. Uma rodada por tamanho.

| N | pedidos | etapa 1 | 1ª escala legal | gap ao fim | etapa 2 | penalidade | pedidos atendidos |
|---|---|---|---|---|---|---|---|
| 36 | 72 | ótimo provado, 35,8 s | 35,1 s | 0% | ótimo provado, 23,8 s | 9.541 | 51 |
| 40 | 80 | ótimo provado, 27,9 s | 27,4 s | 0% | ótimo provado, 22,0 s | 10.745 | 59 |
| 60 | 120 | ótimo provado, 64,6 s | 63,6 s | 0% | ótimo provado, 223,7 s | 22.989 | 91 |
| 80 | 160 | **sem prova**, 900 s | 112,8 s | **43,0%** | não rodou | 94.042 | 72 |
| 120 | 240 | **sem prova**, 900 s | 240,4 s | **3,2%** | não rodou | 102.879 | 177 |
| 200 | 400 | **sem prova**, 900 s | 287,6 s | **46,3%** | não rodou | 569.083 | 193 |

Tempos de relógio; "1ª escala legal" é o tempo do próprio HiGHS na primeira linha da árvore
com solução, lido do log de cada etapa (`resultados/escalabilidade_objetivo/highs_N*_etapa*.log`).
Toda solução do modelo é legal: a CLT está nas restrições rígidas. Gap = (melhor solução −
melhor limite) ÷ melhor solução, ao fim da etapa.

**Conferências, nas seis escalas finais:** descanso medido no relógio (`conferencia_descanso_
escala`) cumpre em todas — folga mínima exatamente no exigido de 36 h, descanso semanal de
36 h; rígidas OK (`solucao.conferir_rigidas`); penalidade recontada a partir da escala
(pedidos negados × W + enfermeiros em posto de técnico) igual à do solver em todas.

**O que isso responde.** A ressalva da rodada de 28/09 se confirmou: com objetivo de verdade,
**a prova deixa de fechar a partir de N = 80** no limite de 900 s, enquanto com o objetivo
degenerado fechava até 200. Escala legal continua saindo em todos os tamanhos — o que não sai
é a garantia de que é a melhor. **Pelo critério de 25/09, existe agora a faixa em que a prova
não fecha, e o warm start heurístico passa a ter o que acelerar.** Se entra ou não é decisão
do projeto de redação; nada foi implementado.

**Leituras que o texto não deve fazer:**
- O gap **não é monótono** no tamanho (43% em 80, 3,2% em 120, 46% em 200). Uma rodada por
  tamanho, numa máquina; é o mesmo aviso da rodada anterior. Não sustenta frase sobre como o
  gap cresce com N.
- O gap é relativo a uma penalidade dominada pelo peso W dos pedidos negados: 43% de gap não
  quer dizer 43% dos pedidos. Em N = 80, o solver garante só que o ótimo está entre 53.572 e
  94.042.
- A etapa 2 desta curva mede pouco sobre equilíbrio: com o quadro no piso, todos trabalham
  168 h já na etapa 1 (amplitude zero). O que ela custou — 22 a 224 s — foi achar outra escala
  com a mesma penalidade. Isso vale para o requisito de tempo da tela, não para a qualidade do
  equilíbrio.
- Tempo é limite operacional, com máquina e solver nomeados acima — nunca resultado.

**Consequência para a ferramenta, já coberta:** acima de cerca de 60 profissionais com
pedidos, a tela tende a mostrar "Escala gerada; pode haver uma melhor", com o gap, em vez de
"Escala gerada" — que é o desfecho (b) decidido em 02/10. Com o limite de 600 s da tela, a
primeira escala de N = 200 (287,6 s aqui) ainda aparece; a etapa 2 não roda.

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

**Status: aguardando decisão.** Nada implementado além do decidido.

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
