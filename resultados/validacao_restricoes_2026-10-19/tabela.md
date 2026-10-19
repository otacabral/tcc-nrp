# Validação por restrição nos 4 ótimos — resultado (19/10/2026)

Gerado por `python docs\diagnostico\validacao_restricoes.py`, sem solver. Esperado registrado antes: `ESPERADO.md` (nesta pasta).

## Resumo

| Instância | Tabela 6 | Penalty do avaliador | Soma por tipo (avaliador) | Soma por tipo (modelo) | Objetivo do modelo (x fixado) | Grade = XML | Duras: avaliador / XML / conferir_rigidas / modelo | Tipos com diferença | Profissionais com diferença | Células prof × tipo com diferença | OK |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|---:|---|
| sprint01 | 56 | 56 | 56 | 56 | 56 | sim | 0 / 0 / 0 / 0 | 0 | 0 | 0 | OK |
| sprint02 | 58 | 58 | 58 | 58 | 58 | sim | 0 / 0 / 0 / 0 | 0 | 0 | 0 | OK |
| long01 | 197 | 197 | 197 | 197 | 197 | sim | 0 / 0 / 0 / 0 | 0 | 0 | 0 | OK |
| long02 | 219 | 219 | 219 | 219 | 219 | sim | 0 / 0 / 0 / 0 | 0 | 0 | 0 | OK |

## sprint01 (Tabela 6 = 56)

- grade do avaliador = escala do XML: sim
- duras: avaliador 0 linha(s) de erro; um turno por dia no XML 0; `conferir_rigidas` 0; restrições do modelo violadas com x fixado 0
- profissionais: 10; com diferença avaliador × modelo: 0; células profissional × tipo com diferença: 0

| Tipo de restrição | Família no modelo | Avaliador | Modelo | Diferença | avaliacao.py |
|---|---|---:|---:|---:|---:|
| fim de semana completo | `complete_weekends` | 0 | 0 | 0 | 0 |
| pedido de folga (dia) | `day_off_requests` | 24 | 24 | 0 | 24 |
| turnos idênticos no fim de semana | `identical_shift_types_during_weekend` | 0 | 0 | 0 | 0 |
| máximo de folgas seguidas | `max_consecutive_free_days` | 0 | 0 | 0 | 0 |
| máximo de dias seguidos de trabalho | `max_consecutive_working_days` | 1 | 1 | 0 | 1 |
| máximo de atribuições | `max_num_assignments` | 30 | 30 | 0 | 30 |
| mínimo de folgas seguidas | `min_consecutive_free_days` | 1 | 1 | 0 | 1 |
| mínimo de dias seguidos de trabalho | `min_consecutive_working_days` | 0 | 0 | 0 | 0 |
| mínimo de atribuições | `min_num_assignments` | 0 | 0 | 0 | 0 |
| pedido de folga (turno) | `shift_off_requests` | 0 | 0 | 0 | 0 |
| padrões indesejados | `unwanted_patterns` | 0 | 0 | 0 | 0 |
| **Total** | | **56** | **56** | **0** | **56** |

## sprint02 (Tabela 6 = 58)

- grade do avaliador = escala do XML: sim
- duras: avaliador 0 linha(s) de erro; um turno por dia no XML 0; `conferir_rigidas` 0; restrições do modelo violadas com x fixado 0
- profissionais: 10; com diferença avaliador × modelo: 0; células profissional × tipo com diferença: 0

| Tipo de restrição | Família no modelo | Avaliador | Modelo | Diferença | avaliacao.py |
|---|---|---:|---:|---:|---:|
| fim de semana completo | `complete_weekends` | 0 | 0 | 0 | 0 |
| pedido de folga (dia) | `day_off_requests` | 24 | 24 | 0 | 24 |
| turnos idênticos no fim de semana | `identical_shift_types_during_weekend` | 0 | 0 | 0 | 0 |
| máximo de folgas seguidas | `max_consecutive_free_days` | 0 | 0 | 0 | 0 |
| máximo de dias seguidos de trabalho | `max_consecutive_working_days` | 0 | 0 | 0 | 0 |
| máximo de atribuições | `max_num_assignments` | 32 | 32 | 0 | 32 |
| mínimo de folgas seguidas | `min_consecutive_free_days` | 1 | 1 | 0 | 1 |
| mínimo de dias seguidos de trabalho | `min_consecutive_working_days` | 1 | 1 | 0 | 1 |
| mínimo de atribuições | `min_num_assignments` | 0 | 0 | 0 | 0 |
| pedido de folga (turno) | `shift_off_requests` | 0 | 0 | 0 | 0 |
| padrões indesejados | `unwanted_patterns` | 0 | 0 | 0 | 0 |
| **Total** | | **58** | **58** | **0** | **58** |

## long01 (Tabela 6 = 197)

- grade do avaliador = escala do XML: sim
- duras: avaliador 0 linha(s) de erro; um turno por dia no XML 0; `conferir_rigidas` 0; restrições do modelo violadas com x fixado 0
- profissionais: 49; com diferença avaliador × modelo: 0; células profissional × tipo com diferença: 0

| Tipo de restrição | Família no modelo | Avaliador | Modelo | Diferença | avaliacao.py |
|---|---|---:|---:|---:|---:|
| fim de semana completo | `complete_weekends` | 0 | 0 | 0 | 0 |
| pedido de folga (dia) | `day_off_requests` | 44 | 44 | 0 | 44 |
| turnos idênticos no fim de semana | `identical_shift_types_during_weekend` | 0 | 0 | 0 | 0 |
| máximo de folgas seguidas | `max_consecutive_free_days` | 0 | 0 | 0 | 0 |
| máximo de dias seguidos de trabalho | `max_consecutive_working_days` | 0 | 0 | 0 | 0 |
| máximo de atribuições | `max_num_assignments` | 150 | 150 | 0 | 150 |
| mínimo de dias seguidos de trabalho | `min_consecutive_working_days` | 0 | 0 | 0 | 0 |
| mínimo de atribuições | `min_num_assignments` | 0 | 0 | 0 | 0 |
| pedido de folga (turno) | `shift_off_requests` | 0 | 0 | 0 | 0 |
| padrões indesejados | `unwanted_patterns` | 3 | 3 | 0 | 3 |
| **Total** | | **197** | **197** | **0** | **197** |

## long02 (Tabela 6 = 219)

- grade do avaliador = escala do XML: sim
- duras: avaliador 0 linha(s) de erro; um turno por dia no XML 0; `conferir_rigidas` 0; restrições do modelo violadas com x fixado 0
- profissionais: 49; com diferença avaliador × modelo: 0; células profissional × tipo com diferença: 0

| Tipo de restrição | Família no modelo | Avaliador | Modelo | Diferença | avaliacao.py |
|---|---|---:|---:|---:|---:|
| fim de semana completo | `complete_weekends` | 0 | 0 | 0 | 0 |
| pedido de folga (dia) | `day_off_requests` | 47 | 47 | 0 | 47 |
| turnos idênticos no fim de semana | `identical_shift_types_during_weekend` | 0 | 0 | 0 | 0 |
| máximo de folgas seguidas | `max_consecutive_free_days` | 0 | 0 | 0 | 0 |
| máximo de dias seguidos de trabalho | `max_consecutive_working_days` | 0 | 0 | 0 | 0 |
| máximo de atribuições | `max_num_assignments` | 160 | 160 | 0 | 160 |
| mínimo de dias seguidos de trabalho | `min_consecutive_working_days` | 1 | 1 | 0 | 1 |
| mínimo de atribuições | `min_num_assignments` | 0 | 0 | 0 | 0 |
| pedido de folga (turno) | `shift_off_requests` | 0 | 0 | 0 | 0 |
| padrões indesejados | `unwanted_patterns` | 11 | 11 | 0 | 11 |
| **Total** | | **219** | **219** | **0** | **219** |

## Por profissional

Arquivo `por_profissional.csv` (instância, profissional, avaliador, modelo, diferença, avaliacao.py). Por tipo: `por_tipo.csv`.

