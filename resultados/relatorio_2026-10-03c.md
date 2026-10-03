# Relatório da sessão de 03/10/2026 (noite)

## Para o Otávio

- **A P1 está rodando.** Desta vez conferi no log: o primeiro tamanho (36) terminou inteiro, com as duas etapas e o CSV gravado. Ela foi lançada às 19:33 e leva até cerca de 3 h.
- A P1 agora mede o caminho da **ferramenta**, com 44 h para todos. O teste de equivalência deu viável nos dois caminhos, em 36 e em 40, como registrado antes.
- Os registros que diziam "P1 lançada" foram corrigidos. A regra nova de execução longa está no CLAUDE.md.
- Uma ressalva para a leitura (item 4): em N = 36 a etapa 2 não tem o que equilibrar, porque a conta obriga todo mundo a 168 h.
- Nada a decidir agora. Os números da curva ficam para a próxima sessão.

---

## 1. O que aconteceu com a rodada das 14:29

Ela morreu às **14:30 de 03/10**, logo depois da etapa 1 de N = 36, com `TypeError` em `Instancia.horas_devidas`.

- As instâncias do caminho antigo (`escalabilidade.construir`) não têm carga contratual (`carga_semanal_h=None`).
- A etapa 2 precisa da carga para calcular a fração do contrato.
- O defeito vinha da carga por contrato (02–03/10), não da P6.
- O relatório 03b afirmou que a P1 estava rodando depois de olhar só o começo do log.

Os logs dessa rodada estão guardados em `resultados/escalabilidade_objetivo/rodada_morta_2026-10-03_14h29/`.

## 2. O que mudou

| Item | Onde |
|---|---|
| A P1 monta cada tamanho pela função da tela (`ferramenta.montar`): 12×36 de 7h–19h e 19h–7h, 44 h para todos. Demanda por turno e composição iguais às do caminho antigo, conferidas dia a dia; se não baterem, o script falha | `escalabilidade_objetivo.construir` |
| Teste de equivalência, com esperado registrado no commit `463c500` **antes** de rodar | `escalabilidade_objetivo.py --equivalencia` |
| O CSV ganhou a coluna `caminho` | idem |
| O caminho antigo ficou intacto (Experimento A) | `escalabilidade.py` sem mudança |
| Descrição do contrato: "carga contratual informada (limite legal de 44h/semana)", no lugar de "42h/semana" | `instancia_br.py:908` |
| Regra nova de execução longa | `CLAUDE.md` |

**Demanda por tamanho** (constante nos 28 dias, enfermeiro + técnico por turno, D e N):

| N | equipe | por turno |
|---|---|---|
| 36 | 12 + 24 | 1 + 8 |
| 40 | 14 + 26 | 1 + 9 |
| 60 | 20 + 40 | 1 + 14 |
| 80 | 27 + 53 | 1 + 19 |
| 120 | 40 + 80 | 1 + 29 |
| 200 | 66 + 134 | 1 + 49 |

Pela conta, o piso da ferramenta (`ferramenta.piso`) dá **N nos seis tamanhos**.

## 3. Conferências

| Conferência | Esperado (registrado antes) | Saiu |
|---|---|---|
| Equivalência N = 36, só as regras rígidas, 900 s | viável nos dois | antigo **viável** (49 s), novo **viável** (43 s); rígidas OK nos dois |
| Equivalência N = 40 | viável nos dois | antigo **viável** (65 s), novo **viável** (64 s); rígidas OK nos dois |
| Piso da ferramenta no caminho novo | 36 e 40 | 36 e 40 |
| 544 XML, contra o commit `cec3d8e` | idênticos | **0 diferentes**. A mudança de descrição só toca o caminho de turnos configurados, que não está na grade |
| `--n 36` até o fim, antes de lançar | etapa 1, etapa 2 e CSV | etapa 1 ótima (38 s), etapa 2 ótima (11 s), CSV gravado, descanso OK, rígidas OK, penalidade recontada = 9.541 |

Os tempos acima são limite operacional, não resultado.

## 4. A curva

- **Comando:** `python src\escalabilidade_objetivo.py --tempo 900`, lançado às **19:33** (PID 16616).
- **Log:** `resultados\escalabilidade_objetivo\p1_2026-10-03_ferramenta.log`.
- **CSV:** `resultados\escalabilidade_objetivo.csv`.

Pela regra nova, conferi no log antes de dizer que está rodando:
- **N = 36 completo:** etapa 1 com ótimo provado, primeira escala legal aos 39 s; etapa 2 com ótimo provado; penalidade 9.541; 51 de 72 pedidos atendidos; 112 turnos de enfermeiro em posto de técnico; descanso OK.
- **CSV gravado.**
- **N = 40 em andamento.**

**Ressalvas para quando os números chegarem:**
- **Em N = 36 a etapa 2 é degenerada.** A demanda soma 6.048 h, que são 36 × 168 h: todo mundo é obrigado a fazer exatamente 14 plantões. A amplitude já é 0 na etapa 1. Nos tamanhos maiores há folga (de 164,4 a 167,4 h por pessoa, pelo docstring de `escalabilidade.py`), e a etapa 2 passa a ter o que fazer.
- **Os 112 turnos de enfermeiro em posto de técnico em N = 36 são forçados pela conta.** Os 24 técnicos dão 24 × 14 = 336 turnos para 448 postos de técnico.
- **O modelo do caminho novo é maior.** Em N = 36 tem 12.640 restrições, contra 5.008 no antigo, com as mesmas 3.696 variáveis. Entram o teto de horas e as regras de descanso geradas dos horários. A curva nova não é comparável, linha a linha, com a de 28/09.

**Máquina:** Intel Core i5-10210U, 12 GB, Windows 11, Python 3.11.9, HiGHS 1.15.1 via appsi.

## 5. Commits

| Commit | Conteúdo |
|---|---|
| `463c500` | P1 pelo caminho da ferramenta, equivalência com esperado registrado antes, descrição do contrato, regra no CLAUDE.md |
| o seguinte | Correções do PROPOSTAS, do ESTADO_ATUAL e do relatório 03b; este relatório. O `2284b75` ficou como estava |

---

## LEVAR PARA O PROJETO DE REDACAO

- **`PROPOSTAS.md`**, P1:
  - correção: a rodada das 14:29 morreu às 14:30 por falta de carga contratual nas instâncias do caminho antigo, sem resultado;
  - decisão: a P1 passa a medir o caminho da ferramenta (44 h, 12×36, demanda igual à do caminho antigo), com teste de equivalência.
- **`ESTADO_ATUAL.md`**: nota de correção no item 2 das pendências.
- **`CLAUDE.md`**: regra nova de execução longa. É protocolo de trabalho, não decisão de modelagem; vai na lista só por ter mudado.
- `DECISOES.md`: sem mudança. A troca de caminho da P1 é desenho experimental, e o registro está na P1 do `PROPOSTAS.md`.
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
