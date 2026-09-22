# Nota para o projeto de redação — o intervalo individual, medido

**22/09/2026.** A rodada `--por-pessoa` fechou nas duas sprints. Agora cada profissional tem
um **intervalo** `[mínimo, máximo]` entre as escalas ótimas, não só um máximo.

Custo real: 203,7 s e 165,5 s de CPU — cerca de 6 minutos no total, contra os 20 a 25 que eu
tinha estimado. A estimativa saiu de tempos de *parede* de uma rodada antiga com a máquina
ocupada; o custo de CPU por resolução é ~9 s, não ~32 s. Corrigido no cabeçalho do
`experimentos.py` para ninguém mais estimar em cima do número errado.

---

## 1. Os intervalos

`sprint01`, Z\* = 56, dez profissionais, ordenados pelo máximo:

| prof. | contrato (teto) | mínimo | na escala minimax | máximo | amplitude |
|---|---|---|---|---|---|
| 4 | 1 (12) | 2 | 6 | **18** | 16 |
| 5 | 1 (12) | 3 | 7 | **18** | 15 |
| 1 | 0 (16) | 2 | 7 | 16 | 14 |
| 6 | 2 (9) | **0** | 7 | 14 | 14 |
| 2 | 0 (16) | 2 | 7 | 13 | 11 |
| 7 | 2 (9) | 2 | 6 | 13 | 11 |
| 3 | 0 (16) | 1 | 6 | 12 | 11 |
| 0 | 0 (16) | 2 | 5 | 6 | 4 |
| 8 | 3 (8) | **0** | 2 | 6 | 6 |
| 9 | 3 (8) | 1 | 3 | **3** | 2 |

`sprint02` (Z\* = 58) repete o desenho: 4 e 5 no topo com 18, o 9 no fundo com [1, 3], o 6
com mínimo 0 e máximo 15.

**Duas colunas que não podem ser somadas, pelo mesmo motivo.** Os máximos somam 119 contra
Z\* = 56, e os mínimos somam 15 — cada valor vem de uma escala ótima diferente. A única
coluna que é uma escala de verdade é a do meio, que soma exatamente 56.

## 2. O resultado principal desta rodada

Junto com o piso forçado, os dois números dizem uma coisa que nenhum deles diz sozinho:

- **coletivamente forçado**: 30 das 56 unidades de `sprint01` são excesso de jornada que
  existe em toda escala viável (a soma dos tetos não cobre a demanda);
- **individualmente fixado**: a soma dos mínimos individuais é **15** — e isso conta todas as
  famílias, não só o teto.

Os dois são limites inferiores válidos para Z\*, e o coletivo é o dobro do individual. A
leitura: **o sistema é obrigado a pagar 30, mas não é obrigado a cobrar de ninguém em
particular.** Pelo menos metade da penalidade inevitável flutua — existe por aritmética e se
aloja em quem a escolha da escala mandar.

Isso é mais forte do que "há concentração", e é mais defensável do que qualquer afirmação
sobre quem sofre: a carga é estruturalmente inevitável e ao mesmo tempo estruturalmente
não-atribuída.

## 3. Correção — "teto menor, mais exposto" não se sustenta

Na nota de ontem eu escrevi, a partir do `long01`, que o mecanismo é *quanto menor o teto de
jornada, maior a penalidade que a escolha pode impor à pessoa*. **As sprints contradizem
isso.**

| contrato | teto | piso | intervalos em `sprint01` |
|---|---|---|---|
| 1 | 12 | 6 | [2, 18] e [3, 18] — **os mais expostos** |
| 0 | 16 | 9 | [2, 6], [2, 16], [2, 13], [1, 12] |
| 2 | 9 | 4 | [0, 14] e [2, 13] |
| 3 | **8** | 8 | [0, 6] e [1, 3] — **os menos expostos** |

O contrato de menor teto é o *menos* exposto, e o de teto intermediário é o mais. A regra que
eu enunciei era uma leitura de uma instância, não um mecanismo.

**O que parece ser o mecanismo de verdade**, e já explica os dois tracks: a exposição de uma
pessoa depende da **folga do resto do grupo**, não do teto dela. `max p_n` é grande quando os
outros conseguem cobrir a demanda barato sem ela — aí dá para empilhar penalidade em cima
dela sem estourar o total Z\*. O contrato 3 tem piso **igual** ao teto (8 e 8): tirar trabalho
dos outros para dar a ele viola os pisos deles, e o total fixo não deixa. Nas longas, a
mesma ideia com o sinal invertido: os 14 do teto 5 somam 70 de capacidade contra 740 de
demanda, então o sistema é obrigado a sobrecarregá-los.

Para o texto, eu proporia a formulação fraca e verificada — *a exposição individual é
propriedade do arranjo de contratos do grupo, e não se lê do contrato da pessoa isoladamente*
— e não a mecânica do teto. A tabela das longas continua correta como descrição daquelas
instâncias; o que sai é a generalização.

## 4. O que os mínimos autorizam a dizer

Dois profissionais têm mínimo **0** em ambas as sprints (6 e 8): existe escala ótima em que
não carregam nada. Isso substitui com vantagem o caso do profissional 28, que virou
ilustração — agora a invariância é medida nos dois sentidos para todo mundo, não inferida de
um máximo igual a zero.

No outro extremo, o profissional 9 tem intervalo [1, 3] nas duas: **quase invariante**. É a
única pessoa das dez de quem se pode dizer algo próximo de "carrega isto, aconteça o que
acontecer".

## 5. Dois acidentes no arquivo de resultado, os dois consertados

A rodada de hoje **apagou a coluna `observacao`** do resumo — onde estava o registro de que a
máquina ficou suspensa no meio do `long02` — porque trocou `segundos` por `segundos_parede` e
`segundos_cpu`, e o cabeçalho passou a ser o da rodada nova. Era o mesmo acidente de ontem
(perder linhas ao rodar `--alvo`), um nível abaixo: ontem protegi as linhas e não as colunas.

Restaurei os tempos das longas e a observação, e tirei a regra de mesclagem de dentro do
experimento: agora é `src/tabela.py`, que **roda sem Pyomo** e tem os dois acidentes como
caso de teste (`python src\tabela.py`). Os três lugares que duplicavam essa lógica passaram a
importar de lá.

Nenhum número foi perdido — os dois arquivos estão com as quatro instâncias completas.
