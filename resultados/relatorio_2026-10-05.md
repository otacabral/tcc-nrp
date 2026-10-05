# Relatório de 05/10/2026 — leitura da P1

## Para o Otávio

- **A P1 terminou.** Rodou de 19:33 a 20:22 de 03/10, sem erro e sem interrupção. Os seis tamanhos estão no CSV.
- **Resultado:** a prova de otimalidade fecha até 80 profissionais. Com 120 fica sem prova (gap de 3,2%, ou 2 pedidos de folga de distância). Com 200, nenhuma escala apareceu em 900 s.
- **Ressalva grande:** em todos os tamanhos todo mundo é obrigado a fazer exatamente 168 h. Por isso a etapa 2 (o equilíbrio) não teve o que equilibrar, e a curva não mede o custo dela. Errei no relatório de 03/10 ao dizer que haveria folga nos tamanhos maiores. Está corrigido.
- **Decisão sua:** se o texto precisar falar do custo da etapa 2, é preciso uma rodada com folga na equipe. Está registrado como proposta na P1, sem implementar.

---

## 1. O processo

- O processo (PID 16616) não existe mais: terminou sozinho.
- O log termina com o resumo e "resultado: ...csv". O arquivo de erro está vazio.
- O último arquivo foi gravado às 20:22:15 de 03/10, e a duração total foi de 49 min.
- Não houve suspensão do computador nem erro.

## 2. Quantos tamanhos terminaram inteiros

Os seis tamanhos têm linha no CSV.

- **36, 40, 60 e 80:** as duas etapas gravadas.
- **120:** só a etapa 1, sem prova. A etapa 2 não rodou, como manda a regra: ela só roda com a etapa 1 provada ótima.
- **200:** só a etapa 1, sem nenhuma escala no limite.

## 3. Por tamanho, no formato combinado

Configuração da rodada:
- 12×36, caminho da ferramenta, 44 h para todos;
- 2 pedidos de folga por pessoa, com semente 20261002 + N;
- 900 s por etapa, solver `appsi_highs`.

**Máquina:** Intel Core i5-10210U (4 núcleos, 8 threads), 12 GB, Windows 11, Python 3.11.9, HiGHS 1.15.1 via appsi. Os tempos são limite operacional desta máquina, uma medição por tamanho; não são resultado.

| N | Variáveis / restrições | Etapa 1 | 1ª escala legal | Etapa 2 | Gap final | Otimalidade | Descanso |
|---|---|---|---|---|---|---|---|
| 36 | 3.696 / 12.640 | ótimo, 39,8 s | 39,0 s | ótimo, 10,3 s (1ª escala 9,6 s) | 0% / 0% | provada nas duas | cumpre |
| 40 | 4.144 / 14.300 | ótimo, 168,0 s | 54,3 s | ótimo, 16,2 s (15,4 s) | 0% / 0% | provada nas duas | cumpre |
| 60 | 6.160 / 20.992 | ótimo, 130,1 s | 128,9 s | ótimo, 18,3 s (17,2 s) | 0% / 0% | provada nas duas | cumpre |
| 80 | 8.232 / 28.086 | ótimo, 693,0 s | 235,1 s | ótimo, 34,0 s (32,4 s) | 0% / 0% | provada nas duas | cumpre |
| 120 | 12.320 / 41.872 | **limite de tempo**, 901,9 s | 345,8 s | não rodou | **3,16%** | **não provada** | cumpre |
| 200 | 20.496 / 69.444 | **limite de tempo, sem escala**, 902,8 s | — | não rodou | — | — | sem escala |

**O conteúdo das escalas:**

| N | Penalidade (recontada) | Pedidos negados | Enfermeiro em posto de técnico | Carga | Amplitude da fração |
|---|---|---|---|---|---|
| 36 | 9.541 (9.541) | 21 de 72 | 112 | 168–168 h | 0 → 0 |
| 40 | 10.745 (10.745) | 21 de 80 | 140 | 168–168 h | 0 → 0 |
| 60 | 22.989 (22.989) | 29 de 120 | 224 | 168–168 h | 0 → 0 |
| 80 | 53.572 (53.572) | 50 de 160 | 322 | 168–168 h | 0 → 0 |
| 120 | 102.879 (102.879) | 63 de 240 | 504 | 168–168 h | 0 (sem etapa 2) |
| 200 | — | — | — | — | — |

- **Rígidas e descanso:** OK em todos os tamanhos com escala. O descanso entre plantões fica em exatamente 36 h (folga mínima de 0 h acima do exigido) e o descanso semanal em 36 h.
- **Limites inferiores**, tirados do log do HiGHS:
  - **N = 120:** limite inferior 99.629. Tirando os 504 turnos de enfermeiro em posto de técnico, que são forçados, sobram (99.629 − 504) ÷ 1.625 = **pelo menos 61 pedidos negados**. A escala encontrada nega 63.
  - **N = 200:** o nó raiz não terminou em 900 s. O limite inferior é 305.563, ou seja, **pelo menos 111 de 400 pedidos negados** (já descontados os 868 turnos forçados).

## 4. Como ler

**O que se pode dizer.** Com o objetivo da ferramenta, a prova fecha até N = 80 e deixa de fechar a partir de N = 120, em 900 s, nesta máquina.

- Pelo critério de 25/09, existe faixa em que a prova não fecha. É a condição para admitir warm start, só como partida.
- Em N = 120 há escala legal, a 2 pedidos do limite inferior. Em N = 200 não há escala.
- Os tempos não crescem de forma regular com o tamanho (168 s em 40 contra 130 s em 60). Isso reforça que tempo não vai ao texto como resultado.

**Ressalva 1: a etapa 2 é degenerada em toda a curva, por construção.**
- A instância de escalabilidade põe o piso exatamente em N (`escalabilidade.porte_para`). A demanda fica em 14N plantões, que é exatamente a capacidade de N pessoas fazendo 14 plantões cada.
- Com a alternância do 12×36, todos fazem 14 plantões (168 h). A amplitude já é 0 na etapa 1, e a etapa 2 só reencontra uma escala.
- O tempo da etapa 2 não mede a dificuldade de equilibrar.
- **O relatório 03c errou ao dizer que haveria folga nos tamanhos maiores.** Os 164,4–167,4 h do docstring são horas de porte, não de demanda. A correção está no topo do 03c.

**Ressalva 2: boa parte do objetivo é aritmética.**
- Os turnos de enfermeiro em posto de técnico são forçados: técnicos × 14 contra 56 × técnicos por turno. Em N = 36, 336 para 448, faltam 112.
- O que o solver decide de fato são os pedidos de folga.
- E cada pessoa tem pouca liberdade: 14 dias de trabalho em 28, sem dois seguidos, admitem só C(15, 14) = 15 conjuntos de dias.
- A curva mede, portanto, o custo de atender pedidos sob uma alternância apertada. É um problema real, mas mais estreito do que "o objetivo da ferramenta" sugere.

**Proposta, registrada na P1 e não implementada (desenho experimental):** se o texto precisar falar do custo da etapa 2, rodá-la numa instância com folga. Por exemplo, a mesma demanda com equipe N + k. Sem isso, a P1 responde só pela etapa 1. A decisão é sua.

## 5. Registros e commit

- `PROPOSTAS.md`, P1:
  - status atualizado;
  - seção nova "Rodada de 03/10 — resultado", com as tabelas, as duas ressalvas e a proposta.
- `ESTADO_ATUAL.md`: nota de 05/10 no item 1 das pendências.
- `resultados/relatorio_2026-10-03c.md`: nota de correção no topo (a "folga nos tamanhos maiores").
- Este relatório.

---

## LEVAR PARA O PROJETO DE REDACAO

- **`PROPOSTAS.md`**, P1:
  - resultado da rodada de 03/10: a prova fecha até 80, fica sem prova em 120 (gap de 3,2%, 2 pedidos) e não acha escala em 200;
  - ressalva: a etapa 2 é degenerada em todos os tamanhos (demanda = 14N), e os turnos de enfermeiro em posto de técnico são forçados pela conta;
  - **proposta nova, aguardando decisão:** medir a etapa 2 numa instância com folga.
- **`ESTADO_ATUAL.md`**: nota de 05/10 no item 1 das pendências (P1).
- `DECISOES.md`: sem mudança.
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
