# Nota de passagem para o projeto de redação — 18/09/2026

Continua a nota de 15/09, que cobriu as Sessões 1 a 3. Esta cobre a semana 2: função
objetivo completa e validação contra a Tabela 6.

Subir junto: `CONTEXTO_PROJETO.md`, `DECISOES.md`, `PROPOSTAS.md`, `PLANO.md` e, se ainda não
foram, `docs/formato_instancias.md` e a nota de 15/09.

---

## 1. O resultado que muda o estado do trabalho

O modelo completo reproduz os valores ótimos da Tabela 6 de Santos et al. (2016):

| Instância | Modelo | Tabela 6 | Avaliador oficial |
|---|---|---|---|
| sprint01 | 56 | 56 | 56 |
| sprint02 | 58 | 58 | 58 |
| long01 | 197 | 197 | 197 |
| long02 | 219 | 219 | 219 |

Todos com otimalidade provada. Três caminhos independentes concordam em cada linha: o valor
da função objetivo do modelo, o calculador de penalidade em Python e o avaliador oficial da
competição.

Isso é o marco que o plano colocava no fim da semana 3. Pendente: `medium_late05` = 107, que
não fechou no tempo de solver disponível — limitação computacional, não de formulação. A
Tabela 3 do próprio artigo mostra o CPLEX precisando de cerca de uma hora e de solução
inicial gulosa para fechar essa instância.

**O que ainda não pode ser escrito como resultado:** nada sobre a instância brasileira, que
não existe; e nenhuma afirmação sobre tempo de resolução, que depende de solver e máquina e
está classificada como afirmação fraca no CONTEXTO, seção 5.

## 2. O método, que vale um parágrafo de metodologia

A semântica das 13 restrições flexíveis foi fixada **antes** de a função objetivo existir,
num calculador de penalidade em Python puro (`src/avaliacao.py`), conferido contra o avaliador
oficial em 207 escalas geradas nas 69 instâncias — comparando cada par profissional ×
restrição, não apenas o total. Igualdade exata em todas.

Só depois disso a função objetivo foi escrita, e o teste dela passou a ser interno: escala
fixada no modelo, valor da objetivo igual ao do calculador. Esse teste encontrou um erro real
de linearização que valia 2 pontos no ótimo do `long02`.

A frase defensável para o texto é estreita e vale a pena manter estreita: *a interpretação de
cada restrição flexível foi validada contra o avaliador oficial antes da construção do modelo,
e a linearização foi validada contra essa interpretação*. Não é "o modelo deu o número certo
no fim".

## 3. Decisões novas no DECISOES.md

- **18/09 — Restrição não pontuada pelo avaliador fica fora da função objetivo.**
  `NoNightShiftBeforeFreeWeekend` é lida pelo avaliador e nunca usada por nenhuma condição
  dele. Está ligada em 44 das 69 instâncias; implementá-la com peso faria o modelo divergir
  nessas 44. Fica implementada e documentada, com peso zero nas instâncias do INRC, e volta a
  valer na instância brasileira.
- **18/09 — Semântica das flexíveis validada fora do modelo.** O método descrito acima.
- **18/09 — Função objetivo: uma folga por violação, não por termo.** As duas convenções de
  linearização e o erro que elas corrigiram.

## 4. Propostas ainda abertas

- **P3 — habilidade como restrição flexível, não como domínio.** Ganhou confirmação empírica:
  com a habilidade tratada como flexível, `long01` dá exatamente 197. Falta a validação
  formal.
- **P4 — o invariante do Experimento A.** Continua sendo a proposta mais consequente aberta, e
  a única que precisa do orientador antes de qualquer código da semana 4. Nada mudou nela
  nesta semana.

## 5. Estado do cronograma

Semanas 2 e 3 essencialmente cumpridas, com quatro dias de folga em relação ao plano. O que
resta nelas: `medium_late05`, a medição de solver, e a validação formal da P3.

A semana 4 — instância brasileira — está bloqueada pela P4, não por código.
