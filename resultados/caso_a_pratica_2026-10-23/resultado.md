# Caso A pela prática e sensibilidade (2 ordens) — resultado

Decisão: `DECISOES.md`, "2026-10-23 — Caso A"; esperado: `ESPERADO.md` (registrado antes). v1.4.4; orçamento padrão de 60 min por rodada. **Tempo: limite operacional desta máquina (i5-10210U, 11,8 GB) com o HiGHS 1.15.1 via appsi; uma rodada por ordem.** Números só vão ao `NUMEROS_TCC.md` depois da aprovação do Otávio.

## A11_fixo_24_ordem1 — HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA

- Quadro informado: 24 (4 enf. + 20 téc.); memória livre antes: 6754 MB; pico: 211 MB; commit `ce0f6d9`.
- **Frase da tela:** "O quadro informado admite escala legal. Escala gerada."
- Tempo total: 130.6 s (limite operacional).
- Avaliador oficial (restrição dura): não; descanso no relógio: ok.

Valor de cada bloco: **no fim do bloco** (escala da etapa 1; modelo e escala, com a P20) e **na escala final** (depois da etapa 2, recontado fora do modelo com os coeficientes do bloco). A etapa 2 não pode passar do valor do fim do bloco; pode ficar abaixo.

| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do bloco: escala | Escala final |
|---|---:|---:|---|---:|---:|---:|
| Essencial | 1124 | 4.8 | sim | 0 | 0 | 0 |
| Importante | 980 | 1.4 | sim | 27 | 27 | 27 |
| etapa 2 (equilíbrio) | | | sim (ok) | | | |

- Essencial: 0 violações — a melhor possível.
- Importante: 27 violações — a melhor possível.

| Critério | Importância | Violações (ferramenta) | Avaliador oficial (peso 1) |
|---|---|---:|---:|
| Pedido de folga no dia | Essencial | 0 | 0 |
| Pedidos e regras dos profissionais | Essencial | 0 | 0 |
| Enfermeiro em posto de técnico | Importante | 0 | sem conferência externa |
| Máximo de folgas seguidas | Importante | 22 | 22 |
| Mínimo de fins de semana seguidos trabalhados | Importante | 1 | 1 |
| Mínimo de turnos no período | Importante | 4 | 4 |

Descumprimentos de "Só este turno" por profissional (nível, quantos): nenhum.
Enfermeiros: da unidade (Enf 6118, Enf 4798, Enf 4969, Enf 5993) — nenhum; acrescidos — nenhum.

## A36_fixo_30_ordem1

- Quadro informado: 30 (10 enf. + 20 téc.); memória livre antes: 6797 MB; pico: 1338 MB; commit `ce0f6d9`.
- **Frase da tela:** "O quadro informado admite escala legal. Escala gerada."
- Tempo total: 3601.0 s (limite operacional).
- Avaliador oficial (restrição dura): não; descanso no relógio: ok.

Valor de cada bloco: **no fim do bloco** (escala da etapa 1; modelo e escala, com a P20) e **na escala final** (depois da etapa 2, recontado fora do modelo com os coeficientes do bloco). A etapa 2 não pode passar do valor do fim do bloco; pode ficar abaixo.

| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do bloco: escala | Escala final |
|---|---:|---:|---|---:|---:|---:|
| Essencial | 1124 | 3.3 | sim | 0 | 0 | 0 |
| Importante | 980 | 5.2 | sim | 51 | 51 | 51 |
| etapa 2 (equilíbrio) | | | não (ok) | | | |

- Essencial: 0 violações — a melhor possível.
- Importante: 51 violações — a melhor possível.

| Critério | Importância | Violações (ferramenta) | Avaliador oficial (peso 1) |
|---|---|---:|---:|
| Pedido de folga no dia | Essencial | 0 | 0 |
| Pedidos e regras dos profissionais | Essencial | 0 | 0 |
| Enfermeiro em posto de técnico | Importante | 18 | sem conferência externa |
| Máximo de folgas seguidas | Importante | 22 | 22 |
| Mínimo de fins de semana seguidos trabalhados | Importante | 1 | 1 |
| Mínimo de turnos no período | Importante | 10 | 10 |
| Máx. fins de semana seguidos (3), avaliado com o critério ligado | — | 17 | 17 |

Descumprimentos de "Só este turno" por profissional (nível, quantos): nenhum.
Enfermeiros: da unidade (Enf 6118, Enf 4798, Enf 4969, Enf 5993) — nenhum; acrescidos — nenhum.

## A36_fixo_30_ordem2

- Quadro informado: 30 (10 enf. + 20 téc.); memória livre antes: 6830 MB; pico: 450 MB; commit `ce0f6d9`.
- **Frase da tela:** "O quadro informado admite escala legal. Escala gerada."
- Tempo total: 642.7 s (limite operacional).
- Avaliador oficial (restrição dura): não; descanso no relógio: ok.

Valor de cada bloco: **no fim do bloco** (escala da etapa 1; modelo e escala, com a P20) e **na escala final** (depois da etapa 2, recontado fora do modelo com os coeficientes do bloco). A etapa 2 não pode passar do valor do fim do bloco; pode ficar abaixo.

| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do bloco: escala | Escala final |
|---|---:|---:|---|---:|---:|---:|
| Essencial | 899 | 5.0 | sim | 0 | 0 | 0 |
| Importante | 718 | 8.7 | sim | 61 | 61 | 61 |
| Desejável | 597 | 17.1 | sim | 7 | 7 | 7 |
| etapa 2 (equilíbrio) | | | sim (ok) | | | |

- Essencial: 0 violações — a melhor possível.
- Importante: 61 violações — a melhor possível.
- Desejável: 7 violações — a melhor possível.

| Critério | Importância | Violações (ferramenta) | Avaliador oficial (peso 1) |
|---|---|---:|---:|
| Pedido de folga no dia | Essencial | 0 | 0 |
| Máximo de fins de semana seguidos trabalhados | Essencial | 0 | 0 |
| Enfermeiro em posto de técnico | Importante | 23 | sem conferência externa |
| Máximo de folgas seguidas | Importante | 22 | 22 |
| Mínimo de fins de semana seguidos trabalhados | Importante | 15 | 15 |
| Mínimo de turnos no período | Importante | 1 | 1 |
| Pedidos e regras dos profissionais | Desejável | 7 | 7 |
| Máx. fins de semana seguidos (3), avaliado com o critério ligado | — | 0 | 0 |

Descumprimentos de "Só este turno" por profissional (nível, quantos): Noite A 1 (Desejável, 7).
Enfermeiros: da unidade (Enf 6118, Enf 4798, Enf 4969, Enf 5993) — nenhum; acrescidos — nenhum.

## Complemento (24/10, só leitura das escalas gravadas)

Sem solver: as escalas e as saídas do avaliador gravadas na rodada; a instância de cada rodada remontada pela mesma entrada (`caso_a_pratica.py --complemento`).

### A11_fixo_24_ordem1 — HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA

| Enfermeiro | Origem | Turnos | Em posto de técnico |
|---|---|---:|---:|
| Enf 4798 | unidade | 14 | 0 |
| Enf 4969 | unidade | 24 | 0 |
| Enf 5993 | unidade | 24 | 0 |
| Enf 6118 | unidade | 14 | 0 |
| **4 da unidade** | | **76** | **0** |

- Máximo de folgas seguidas (4), avaliador oficial (peso 1): **22** — Noite A 1 11 (férias), Tarde 1 11 (férias). Das quais de quem tem férias: 22.
- Mínimo de turnos (10), avaliador oficial (peso 1): **4** — Noite A 1 4 (férias). Das quais de quem tem férias: 4.
- Férias na rodada: Noite A 1 (15 dias), Tarde 1 (15 dias).

### A36_fixo_30_ordem1

| Enfermeiro | Origem | Turnos | Em posto de técnico |
|---|---|---:|---:|
| Enf 4798 | unidade | 8 | 1 |
| Enf 4969 | unidade | 10 | 1 |
| Enf 5993 | unidade | 10 | 2 |
| Enf 6118 | unidade | 10 | 2 |
| **4 da unidade** | | **38** | **6** |
| Enf 10 | acrescido | 10 | 2 |
| Enf 5 | acrescido | 10 | 2 |
| Enf 6 | acrescido | 9 | 1 |
| Enf 7 | acrescido | 9 | 3 |
| Enf 8 | acrescido | 9 | 3 |
| Enf 9 | acrescido | 9 | 1 |
| **6 acrescidos** | | **56** | **12** |

- Máximo de folgas seguidas (4), avaliador oficial (peso 1): **22** — Noite A 1 11 (férias), Tarde 1 11 (férias). Das quais de quem tem férias: 22.
- Mínimo de turnos (10), avaliador oficial (peso 1): **10** — Noite A 1 4 (férias), Enf 4798 2, Enf 6 1, Enf 7 1, Enf 8 1, Enf 9 1. Das quais de quem tem férias: 4.
- Férias na rodada: Tarde 1 (15 dias), Noite A 1 (15 dias).

### A36_fixo_30_ordem2

| Enfermeiro | Origem | Turnos | Em posto de técnico |
|---|---|---:|---:|
| Enf 4798 | unidade | 10 | 3 |
| Enf 4969 | unidade | 10 | 2 |
| Enf 5993 | unidade | 10 | 3 |
| Enf 6118 | unidade | 10 | 2 |
| **4 da unidade** | | **40** | **10** |
| Enf 10 | acrescido | 10 | 1 |
| Enf 5 | acrescido | 10 | 3 |
| Enf 6 | acrescido | 9 | 2 |
| Enf 7 | acrescido | 10 | 2 |
| Enf 8 | acrescido | 10 | 2 |
| Enf 9 | acrescido | 10 | 3 |
| **6 acrescidos** | | **59** | **13** |

- Máximo de folgas seguidas (4), avaliador oficial (peso 1): **22** — Noite A 1 11 (férias), Tarde 1 11 (férias). Das quais de quem tem férias: 22.
- Mínimo de turnos (10), avaliador oficial (peso 1): **1** — Enf 6 1. Das quais de quem tem férias: 0.
- Férias na rodada: Tarde 1 (15 dias), Noite A 1 (15 dias).

### Notas

- **Férias (semântica do INRC, não escolha da ferramenta):** no formato do INRC, dia de férias conta como dia sem trabalho — o `avaliacao.py` e o avaliador oficial concordam. Com 15 dias de férias seguidos, o máximo de folgas seguidas (4) é violado em pelo menos 15 − 4 = 11 por pessoa: os 22 das três rodadas são a Tarde 1 e a Noite A 1, 11 cada, e com o nível provado são inevitáveis. No mínimo de turnos, os 4 da Noite A 1 (A11 e A36 ordem 1) vêm da mesma semântica somada ao turno fixo no Essencial (só noites, em metade do mês) e, com prova, são inevitáveis nessas ordens; na ordem 2, com o "Só este turno" no Desejável, a Noite A 1 chega aos 10 turnos à custa de 7 quebras do turno fixo. Os outros 6 do mínimo de turnos no A36 ordem 1 (Enf 4798, 6, 7, 8, 9) e o 1 da ordem 2 (Enf 6) não têm relação com férias.
- **"Unwanted pattern"** (ex.: N-null-D12) na saída do avaliador: é o artefato conhecido dos padrões das 36 h (`DECISOES.md`, "2026-10-06 — Padrão das 36 h fica no XML (opção (a) da P13)": o avaliador lê o padrão como noturno, folga, folga e cobra violações que não existem). Não entra na conferência; a regra das 36 h é conferida pela medição do descanso no relógio (aprovada nas três rodadas).

