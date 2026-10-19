# Censo das flexíveis nas 69 instâncias do INRC-2010 (19/10/2026)

Gerado por `python docs\diagnostico\censo_flexiveis.py`, sem solver. Ativa = regra de 15/09 (ligada e peso > 0) em pelo menos um contrato; pedidos e padrões, com peso > 0. Ocorrências = contratos (ou padrões, ou pedidos) em que está ativa. Limite = limite superior de violações por instância, em unidades de excesso (peso 1), somado sobre os profissionais; válido, não justo. Detalhe por instância: `censo.csv`.

| Família | Instâncias com a família ativa (de 69) | Pesos observados (peso: ocorrências) | Limite: fórmula | Maior limite (instância) |
|---|---:|---|---|---|
| `max_num_assignments` | 69 | 1: 146, 3: 74, 5: 15 | D − v por profissional | 862 (long_early04) |
| `min_num_assignments` | 69 | 1: 146, 3: 74, 5: 15 | v por profissional | 400 (long_hint01) |
| `max_consecutive_working_days` | 69 | 1: 146, 4: 74, 8: 15 | D − v por profissional | 1197 (long_hint02) |
| `min_consecutive_working_days` | 69 | 1: 146, 3: 6, 4: 68, 7: 15 | (v − 1) × ⌈D/2⌉ por profissional | 1302 (long_late05) |
| `max_consecutive_free_days` | 69 | 1: 146, 6: 15, 7: 74 | D − v por profissional | 1180 (long_hint01) |
| `min_consecutive_free_days` | 69 | 1: 147, 3: 70, 8: 15, 31: 3 | (v − 1) × ⌈D/2⌉ por profissional | 1330 (medium_hidden01) |
| `max_consecutive_working_weekends` | 49 | 1: 58, 5: 75, 10: 15 | F − v por profissional | 115 (long_hidden05) |
| `min_consecutive_working_weekends` | 41 | 1: 33, 3: 12, 5: 50 | (v − 1) × ⌈F/2⌉ por profissional | 60 (long_hint01) |
| `max_working_weekends_in_four_weeks` | 0 | — | (F − 3) × (4 − v) por profissional | 0 (—) |
| `complete_weekends` | 69 | 1: 145, 10: 90 | por fim de semana, o pior padrão de dias (enumerado) | 560 (long_hidden03) |
| `identical_shift_types_during_weekend` | 69 | 1: 144, 10: 90 | por fim de semana, a pior combinação de turnos (enumerada) | 880 (long_hidden03) |
| `no_night_shift_before_free_weekend` | 44 | 1: 70, 10: 75 | F por profissional (com turno noturno) | 200 (long_hidden01) |
| `two_free_days_after_night_shifts` | 0 | — | 2 × D por profissional (frouxo) | 0 (—) |
| `alternative_skill_category` | 18 | 1: 25, 10: 35 | D por profissional sem todas as habilidades | 1344 (long_hidden01) |
| `unwanted_patterns` | 57 | 1: 330, 3: 5, 4: 5, 5: 5, 7: 10, 10: 13 | por padrão, as posições em que ele pode casar | 10950 (long_hidden01) |
| `day_off_requests` | 49 | 1: 6285, 5: 500 | nº de pedidos | 490 (long_early01) |
| `shift_off_requests` | 49 | 1: 6484, 3: 250 | nº de pedidos | 310 (medium_early01) |
| `day_on_requests` | 0 | — | nº de pedidos | 0 (—) |
| `shift_on_requests` | 0 | — | nº de pedidos | 0 (—) |
