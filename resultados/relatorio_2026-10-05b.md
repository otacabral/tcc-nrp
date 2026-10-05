# Relatório de 05/10/2026 (b) — rodada da P1 com folga

## Para o Otávio

- **A rodada com folga terminou** (atualizado ao fim, 05/10 ~14:08). Os três tamanhos estão completos, sem erro.
- **O que já aparece:** a etapa 2 chega à melhor escala que vai achar **logo no início** (18 s com 44 pessoas, 46 s com 66). Depois gasta o resto dos 900 s sem conseguir provar.
- **Pela conta, essa escala já é a melhor possível** nos dois casos (item 3). O solver é que não consegue provar.
- **O 88 confirmou o padrão:** a escala final veio aos 81 s, e é ótima pela conta.
- **Decisão sua:** o limite de tempo da etapa 2 na tela. Ele não mudou, como você pediu.

---

## 1. O que mudou

- **`escalabilidade_objetivo.py --folga`:** usa a mesma demanda de 40, 60 e 80, com equipe 10% maior.
  - Cada categoria foi escalada por 1,1 e arredondada: 15 + 29 = 44; 22 + 44 = 66; 30 + 58 = 88.
  - Mantém 44 h, 2 pedidos de folga por pessoa (semente 20261002 + N, com N o tamanho da demanda) e 900 s por etapa.
- **Registro novo:** a amplitude por categoria antes e depois da etapa 2.
- **Registro novo:** o tempo até 90% da redução final, lido do log do HiGHS. É a primeira linha da árvore com melhor solução ≤ amplitude da etapa 1 − 0,9 × redução.
- **Arquivos:**
  - CSV: `resultados/escalabilidade_objetivo_folga.csv`;
  - logs do HiGHS: `highs_N<n>_E<equipe>_etapa<k>.log`.
- **PROPOSTAS, P1:** leitura de 03/10 registrada como você ditou (caso mais apertado; prova até 80; 120 sem prova, gap 3,16%; 200 sem escala) e a rodada com folga decidida.
- **Commit:** `bea0300`, feito antes de rodar.

## 2. Como foi rodada

1. **Caso menor até o fim**, antes de lançar: `--folga --n 40`. Log em `folga_teste_N40_2026-10-05.log`. Etapa 1, etapa 2 e CSV completos.
2. **Lançamento às 13:35** (PID 27688): `--folga --n 60 --n 80 --tempo 900`. Log em `resultados/escalabilidade_objetivo/folga_2026-10-05.log`.
   - O 40/44 não foi repetido: a linha dele vem do caso de teste, com o mesmo código, e está no mesmo CSV.
3. **Confirmação no log:** o 66 terminou inteiro (as duas etapas e a linha no CSV) antes deste relatório.

## 3. Resultados até agora

**Máquina:** Intel Core i5-10210U, 12 GB, Windows 11, Python 3.11.9, HiGHS 1.15.1 via appsi. Os tempos são limite operacional desta máquina, uma medição por tamanho.

| Demanda / equipe | Etapa 1 | 1ª escala legal | Etapa 2 | Gap etapa 2 | 90% da redução |
|---|---|---|---|---|---|
| 40 / 44 | ótimo provado, 20,7 s | 1,9 s | **limite de tempo**, 902 s, sem prova | 19,6% | **18,1 s** |
| 60 / 66 | ótimo provado, 39,1 s | 2,2 s | **limite de tempo**, 904 s, sem prova | 26,1% | **45,6 s** |
| 80 / 88 | ótimo provado, 61,5 s | 3,0 s | **limite de tempo**, 907 s, sem prova | 37,5% | **81,1 s** |

**Amplitude da fração** (pontos percentuais), antes e depois da etapa 2:

| Demanda / equipe | Total | Enfermeiros | Técnicos |
|---|---|---|---|
| 40 / 44 | 34,09 → 13,64 | 27,27 → 6,82 | 6,82 → 6,82 |
| 60 / 66 | 20,45 → 13,64 | 13,64 → 6,82 | 6,82 → 6,82 |
| 80 / 88 | 27,27 → 13,64 | 20,45 → 6,82 | 6,82 → 6,82 |

**Restante, por tamanho:**
- **40 / 44:**
  - todos os 88 pedidos atendidos; 107 turnos de enfermeiro em posto de técnico;
  - carga de 120 a 168 h; horas não utilizadas: 684 h dos enfermeiros e 340 h dos técnicos;
  - descanso e rígidas OK; penalidade recontada igual (107).
- **60 / 66:**
  - todos os 132 pedidos atendidos; 181 turnos de enfermeiro em posto de técnico;
  - carga de 120 a 168 h;
  - descanso e rígidas OK; penalidade recontada igual (181).
- **80 / 88:**
  - todos os 176 pedidos atendidos; 267 turnos de enfermeiro em posto de técnico;
  - carga de 120 a 168 h; horas não utilizadas: 1.404 h dos enfermeiros e 644 h dos técnicos;
  - descanso e rígidas OK; penalidade recontada igual (267).

**A primeira escala da etapa 2 já é a final.** Nos dois casos, o "90% da redução" coincide com a primeira escala da etapa 2, e nenhuma melhora veio depois.

**Pela conta, essa escala já é ótima.** Cada plantão de 12 h vale 12 ÷ 176 = 6,82 pp da fração. Uma categoria só tem amplitude 0 se o número de plantões dela se dividir igualmente entre as pessoas:

| Demanda / equipe | Enfermeiros | Técnicos |
|---|---|---|
| 40 / 44 | (56 postos + 107 em posto de técnico) ÷ 15 = 10,87 | (504 − 107) ÷ 29 = 13,69 |
| 60 / 66 | (56 + 181) ÷ 22 = 10,77 | (784 − 181) ÷ 44 = 13,70 |
| 80 / 88 | (56 + 267) ÷ 30 = 10,77 | (1.064 − 267) ÷ 58 = 13,74 |

Nenhum dos quatro valores é inteiro, então cada categoria tem amplitude de pelo menos 6,82 pp. O total não pode ficar abaixo de 13,64 pp, e foi exatamente o que a etapa 2 achou nos dois casos.

- O total de enfermeiros em posto de técnico não muda na etapa 2, porque a penalidade fica presa no ótimo e todos os pedidos foram atendidos.
- Os gaps de 19,6% e 26,1% são **fraqueza do limite inferior do solver**, não distância real.
- Fiz esta conta **depois** de ver o resultado. Ela é aritmética e não depende do solver, mas não foi registrada antes.

**O que isso sugere para a tela (a decisão é sua).**
- Um limite curto para a etapa 2 perderia pouco nestes casos: a melhor escala apareceu em 18 s, 46 s e 81 s.
- Com 600 s, a tela esperaria quase tudo à toa.
- Outra possibilidade é a ferramenta reconhecer o piso aritmético e parar quando chegar nele. Isso é mudança de formulação; se você quiser, registro como proposta. **Não implementei.**

## 4. Commits

| Commit | Conteúdo |
|---|---|
| `bea0300` | `--folga`, registros novos, PROPOSTAS (leitura de 03/10 e rodada decidida); feito antes de rodar |
| `a0169ce` | Este relatório, parcial |
| o seguinte | Este relatório completo; resultado na P1; nota no ESTADO_ATUAL |

---

## LEVAR PARA O PROJETO DE REDACAO

- **`PROPOSTAS.md`**, P1:
  - leitura decidida: a rodada de 03/10 mede o caso mais apertado (168 h por pessoa); a prova fecha até 80; 120 tem escala sem prova (gap 3,16%); 200 fica sem escala em 900 s; tempo é limite operacional;
  - rodada com folga decidida, com seus parâmetros.
  - resultado da rodada com folga: tabela por tamanho; a escala da etapa 2 é ótima pela conta, e os gaps são fraqueza do limite inferior do solver.
- **`ESTADO_ATUAL.md`**: nota de 05/10 (tarde) no item 1 das pendências; pendente a decisão do limite da etapa 2.
- `DECISOES.md` e `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
