## 1. Logs do HiGHS que existem

| Log | Modelo | O que é | 1ª solução | Última melhora | Fim | Status | Gap final |
|---|---|---|---|---|---|---|---|
| `A3a_15mais5_3600s.log` | 6+12 | K6 (15+5), etapa 1, 3.600 s | 0 s | 826 s | 1077 s | Optimal | 0% |
| `A3b_22.log` | 6+12 | parte A, 22 pessoas, 600 s | 0 s | 305 s | 600 s | Time limit reached | 16.67% |
| `A3b_24.log` | 6+12 | parte A, 24 pessoas, 600 s | 0 s | 160 s | 600 s | Time limit reached | 21.05% |
| `A3b_26.log` | 6+12 | parte A, 26 pessoas, 600 s | 0 s | 358 s | 414 s | Optimal | 0% |
| `A3c_sem_6_dias.log` | 6+12 | parte A, relaxado: sem limite de 6 dias | 0 s | 66 s | 600 s | Time limit reached | 10.53% |
| `A3c_sem_descanso_entre_turnos.log` | 6+12 | parte A, relaxado: sem descanso entre turnos | 0 s | 273 s | 600 s | Time limit reached | 30% |
| `A3c_sem_max_atribuicoes.log` | 6+12 | parte A, relaxado: sem teto de atribuicoes | 0 s | 175 s | 600 s | Time limit reached | 15.79% |
| `A3c_sem_teto_horas.log` | 6+12 | parte A, relaxado: sem teto de horas | 0 s | 277 s | 600 s | Time limit reached | 21.05% |
| `inviavel_16_10mais6.log` | 6+12 | parte A, 16 (10+6), prova de inviabilidade | — | — | 15 s | Infeasible | inf |
| `highs_17.log` | 6+12 | K4 (12+5), 3.600 s, interrompido por memoria | — | — | 1909 s | sem relatorio (interrompido) | — |

## 2. Bateria: 161 resoluções isoláveis da etapa 1 (admite na 1ª tentativa)

| Modelo | Estrato | Resoluções | Com prova | Tempo até a prova: mediana / máximo | Sem prova (600 s) |
|---|---|---|---|---|---|
| 12x36 | folga_clara | 9 | 9 | 1 / 2 s | 0  |
| 12x36 | fronteira | 11 | 11 | 1 / 6 s | 0  |
| 12x36 | — | 21 | 21 | 2 / 9 s | 0  |
| 6+12 | folga_clara | 5 | 5 | 1 / 4 s | 0  |
| 6+12 | fronteira | 10 | 10 | 3 / 29 s | 0  |
| 6+12 | — | 42 | 30 | 2 / 274 s | 12 (K5, K6, K3/mais_pessoa, K4/mais_pessoa, K5/embaralhado, K5/mais_ferias, K5/mais_pessoa, K5/mais_posto, K6/embaralhado, K6/mais_ferias, K6/mais_pessoa, K6/mais_posto) |
| 8h | folga_clara | 26 | 26 | 1 / 5 s | 0  |
| 8h | fronteira | 2 | 2 | 1 / 1 s | 0  |
| 8h | — | 35 | 35 | 1 / 5 s | 0  |

Com prova: 149 de 161 (93%).
