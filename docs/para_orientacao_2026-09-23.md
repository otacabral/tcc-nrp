# TCC — situação em 23/09/2026, para a orientação

Três resultados fechados, uma decisão a tomar e uma lista curta do que ainda não está
resolvido. Tudo abaixo é reproduzível com um comando; os arquivos estão no repositório.

---

## 1. Efetivo mínimo com demanda constante: os dois regimes empatam

A instância brasileira parte do Parecer Normativo COFEN nº 1/2024: 5.920 horas de assistência
em 28 dias, 42 h semanais nos dois regimes. A pergunta é de quantas pessoas se precisa para
cobrir essa assistência sem violar a lei, mudando só o regime de jornada.

**Resposta: 36 pessoas, nos dois regimes, em 20 combinações** (5 graus de dependência × 2
regimes × 2 regras de arredondamento da demanda).

O resultado é fechado dos dois lados: 35 pessoas é **inviável com prova do solver**, e 36 tem
escala exibida e aprovada pelo avaliador oficial da competição. Não é "36 basta" — é "36 é o
mínimo".

**A explicação é aritmética e vale a pena dizer assim:** 14 plantões de 12 h e 21 plantões de
8 h dão os mesmos 168 h em 28 dias, porque o teto legal é 42 h semanais nos dois. E
5.920 ÷ 168 = 35,24, que é exatamente o quadro de referência do próprio Parecer. O mínimo
viável é o teto disso.

**O que isso autoriza dizer, e o escopo é estreito de propósito:** *sob demanda constante,
nenhuma restrição de escalonamento aperta além do teto de horas, em nenhum dos dois regimes.*
Não é "o regime não muda o efetivo" — com demanda constante nenhuma restrição tinha como
apertar, e as 20 combinações são a mesma aritmética repetida, não 20 testes independentes.

O que sobrevive como achado positivo: **as regras de descanso, inclusive as 36 h após o
plantão noturno do 12×36, não forçam ociosidade.** Isso não era óbvio antes de medir.

## 2. Com a demanda variando entre dias, os regimes se separam

Com demanda constante a rigidez do 12×36 sai de graça. A hipótese do trabalho é sobre demanda
que varia, então a demanda passou a variar entre dias úteis e fins de semana, **mantendo o
total de horas**. A forma da variação foi medida na instância `long01` do próprio benchmark —
29 atribuições por dia útil contra 20 por dia de fim de semana — em vez de arbitrada.

| variação | 12×36 | 8 h | diferença |
|---|---|---|---|
| nenhuma (demanda constante) | 36 | 36 | — |
| metade da forma medida | **40** | 38 | +2 pessoas (+5,3%) |
| forma medida inteira | **40** | 37 | +3 pessoas (+8,1%) |

**O mecanismo é demonstrável sem resolver nada.** No 12×36 ninguém pode trabalhar dois dias
seguidos. Logo dois dias consecutivos exigem gente inteiramente diferente, e o efetivo tem de
cobrir a **soma** de dois dias seguidos. Com demanda constante isso nunca aperta; com demanda
variando, dois dias úteis seguidos somam bem mais que a média, e esse limite passa o da
capacidade. É exatamente a rigidez que o trabalho se propôs a medir.

Todas as escalas foram verificadas no relógio: 36 h de descanso entre plantões no 12×36 e 16 h
no de 8 h, contra 36 h e 11 h exigidos.

## 3. Achado metodológico: o avaliador oficial lê um dos padrões errado

A regra das 36 h do 12×36 é escrita no formato da competição como a sequência proibida
*(noturno, folga, diurno)*. O avaliador oficial **não a lê assim**. Três testes:

1. na escala testada há **zero** ocorrências da sequência proibida, e o avaliador cobra **116**
   violações;
2. criar uma ocorrência real da sequência, preservando a cobertura, faz a conta **cair**;
3. trocar o terceiro elemento da sequência no arquivo de entrada **não muda nada**.

A regra que explica os três: **depois de uma entrada "folga" em posição não inicial, o
avaliador ignora o tipo de turno das entradas seguintes e as trata como folga.** O padrão
acaba penalizando *mais* descanso, o oposto da intenção. A previsão por essa regra bate
exatamente com as 116 cobranças.

**Isso não contamina o restante do trabalho.** Varri os 59 arquivos do INRC: 304 padrões,
**nenhum** com esse formato. A concordância das 207 escalas conferidas contra o avaliador e os
quatro ótimos reproduzidos da Tabela 6 de Santos et al. (2016) seguem valendo sem ressalva.

**Cuidado que eu declararia:** o que está demonstrado é *comportamento*, não código — não li o
fonte do avaliador. A afirmação segura é "o avaliador pontua esse padrão como (noturno, folga,
folga) nas nossas instâncias, e aqui está o teste".

---

## A decisão que preciso levar

A regra do projeto é que nenhum resultado numérico vale sem conferência no avaliador oficial.
Para a regra das 36 h, na instância brasileira, essa conferência é impossível. Duas saídas:

**(a) Manter o padrão no arquivo e declarar a divergência no texto.** A instância continua
autodescritiva, mas publicamos um artefato que o avaliador oficial pontua com 116 violações
inexistentes, e o texto precisa explicar por que ignorar aquele número.

**(b) Tirar o padrão do arquivo e deixar a regra das 36 h apenas no modelo.** O arquivo volta a
ser pontuado corretamente, mas a regra passa a existir só no código e no texto — quem pegar a
instância não a reproduz.

Procurei uma terceira via — escrever a regra sem a entrada de folga no meio — e não há: o
formato só expressa dias consecutivos, e a regra é um salto de dois dias.

---

## O que ainda não está resolvido

- A varredura de sensibilidade cobriu **um grau de dependência** (intermediário) e uma regra de
  arredondamento. Ampliá-la é barato e ainda não foi feito.
- A forma da variação de demanda é **uma só**, calibrada no `long01`. Duas ou três formas
  distinguiriam efeito de forma de efeito de nível.
- As duas células de 12×36 com variação estão validadas pela **medição direta de descanso**, não
  pelo avaliador oficial — é o que a decisão acima resolve.
- O Experimento B, sobre distribuição de carga entre profissionais, está fechado nas quatro
  instâncias do INRC e ainda não foi estendido à instância brasileira.

## Nota sobre o processo, que talvez interesse

Só hoje o encadeamento de conferências pegou três erros de codificação que teriam passado
despercebidos e produzido resultados errados publicáveis: regras de descanso que não cobriam
metade dos tipos de turno; uma correção que não teve efeito porque o contrato apontava para a
lista antiga; e uma conferência minha que reprovava escala legal por aplicar ao regime de 8 h
uma regra que é do 12×36.

Nenhum dos três foi pego pelas conferências que já existiam — todas compartilhavam a premissa
do que conferiam. Quem pegou foi uma medição feita **a partir dos horários no arquivo**, sem
usar nenhuma das listas. Isso virou critério: conferência que compartilha premissa com o que
confere não confere.
