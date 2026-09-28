# Propostas a validar

Registro de sugestões que afetam formulação, desenho experimental ou escopo.
**Não implementadas até validação.**

Arquivo recriado em 28/09/2026, depois da virada de escopo de 24/09. O `PROPOSTAS.md` do
escopo anterior, com as treze propostas P1–P13, está em
`historico/escopo-comparacao-regimes/PROPOSTAS.md`. A numeração recomeça.

---

## 2026-09-28 — P1: a curva de escalabilidade mede um problema mais fácil do que o da ferramenta

**Status: aguardando validação.** Nada implementado. O experimento rodou como combinado e o
resultado está abaixo; o que proponho é sobre **como lê-lo**, e sobre uma rodada adicional.

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
