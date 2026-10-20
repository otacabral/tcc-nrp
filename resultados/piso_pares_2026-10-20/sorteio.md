# Teste 2 — sorteio pequeno (semente 20261020, 40 instâncias)

Turnos M 7–13, T 13–19, N 19–7 (12 h) e, em 60%, D12 7–19; 7 a 14 dias; equipe informada de 1 enfermeiro e 0 a 2 técnicos, subindo até achar escala (margem 20); férias de um enfermeiro em metade. Busca com o piso ANTIGO; etapa 2 desligada; 60 s por resolução. HiGHS; tempo é limite operacional.

Decididas pelo solver: 40 de 40. A conta nova sobe o piso em 40; nelas, o piso novo é igual ao menor viável em 30.

| # | Dias | Turnos | Férias | Piso antigo | Piso novo | Menor viável (solver) | Tentativas no solver | Resultado |
|---|---:|---|---|---:|---:|---:|---|---|
| 1 | 12 | M/T/N | sim | 5 | 8 | 8 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'viavel')] | ok |
| 2 | 8 | M/T/N/D12 | sim | 7 | 8 | 9 | [(7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'viavel')] | ok |
| 3 | 12 | M/T/N/D12 | sim | 6 | 10 | 12 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'inviavel'), (11, 'inviavel'), (12, 'viavel')] | ok |
| 4 | 9 | M/T/N/D12 | sim | 6 | 9 | 9 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'viavel')] | ok |
| 5 | 12 | M/T/N | não | 5 | 7 | 7 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'viavel')] | ok |
| 6 | 7 | M/T/N | não | 4 | 5 | 5 | [(4, 'inviavel'), (4, 'inviavel'), (5, 'viavel')] | ok |
| 7 | 13 | M/T/N | sim | 5 | 7 | 8 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'viavel')] | ok |
| 8 | 7 | M/T/N/D12 | sim | 6 | 11 | 11 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'viavel')] | ok |
| 9 | 7 | M/T/N/D12 | não | 5 | 9 | 11 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'viavel')] | ok |
| 10 | 10 | M/T/N | não | 6 | 7 | 7 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'viavel')] | ok |
| 11 | 8 | M/T/N/D12 | sim | 5 | 7 | 7 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'viavel')] | ok |
| 12 | 13 | M/T/N | sim | 6 | 9 | 9 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'viavel')] | ok |
| 13 | 13 | M/T/N/D12 | não | 6 | 10 | 11 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'viavel')] | ok |
| 14 | 8 | M/T/N | não | 5 | 9 | 9 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'viavel')] | ok |
| 15 | 11 | M/T/N/D12 | sim | 5 | 10 | 10 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'viavel')] | ok |
| 16 | 13 | M/T/N/D12 | sim | 7 | 10 | 12 | [(7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'inviavel'), (11, 'inviavel'), (12, 'viavel')] | ok |
| 17 | 7 | M/T/N | não | 7 | 8 | 8 | [(7, 'inviavel'), (7, 'inviavel'), (8, 'viavel')] | ok |
| 18 | 13 | M/T/N | sim | 5 | 8 | 8 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'viavel')] | ok |
| 19 | 9 | M/T/N/D12 | não | 6 | 8 | 9 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'viavel')] | ok |
| 20 | 10 | M/T/N/D12 | sim | 7 | 11 | 11 | [(7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'inviavel'), (11, 'viavel')] | ok |
| 21 | 12 | M/T/N | não | 5 | 6 | 6 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'viavel')] | ok |
| 22 | 8 | M/T/N/D12 | sim | 5 | 8 | 8 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'viavel')] | ok |
| 23 | 14 | M/T/N/D12 | não | 7 | 9 | 9 | [(7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'viavel')] | ok |
| 24 | 12 | M/T/N/D12 | sim | 7 | 10 | 10 | [(7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'viavel')] | ok |
| 25 | 10 | M/T/N/D12 | sim | 6 | 10 | 11 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'viavel')] | ok |
| 26 | 14 | M/T/N/D12 | não | 7 | 10 | 10 | [(7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'viavel')] | ok |
| 27 | 10 | M/T/N/D12 | não | 6 | 10 | 10 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'viavel')] | ok |
| 28 | 12 | M/T/N | não | 6 | 9 | 9 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'viavel')] | ok |
| 29 | 9 | M/T/N/D12 | não | 6 | 9 | 9 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'viavel')] | ok |
| 30 | 10 | M/T/N/D12 | sim | 6 | 9 | 9 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'viavel')] | ok |
| 31 | 9 | M/T/N | sim | 5 | 7 | 7 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'viavel')] | ok |
| 32 | 11 | M/T/N/D12 | não | 6 | 8 | 9 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'viavel')] | ok |
| 33 | 11 | M/T/N | não | 5 | 8 | 8 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'viavel')] | ok |
| 34 | 9 | M/T/N | não | 5 | 7 | 7 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'viavel')] | ok |
| 35 | 11 | M/T/N/D12 | não | 6 | 8 | 11 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'viavel')] | ok |
| 36 | 10 | M/T/N/D12 | não | 5 | 10 | 10 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'viavel')] | ok |
| 37 | 9 | M/T/N/D12 | sim | 6 | 11 | 11 | [(6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'viavel')] | ok |
| 38 | 11 | M/T/N | sim | 5 | 8 | 8 | [(5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'viavel')] | ok |
| 39 | 11 | M/T/N/D12 | sim | 7 | 13 | 13 | [(7, 'inviavel'), (7, 'inviavel'), (8, 'inviavel'), (8, 'inviavel'), (9, 'inviavel'), (9, 'inviavel'), (10, 'inviavel'), (10, 'inviavel'), (11, 'inviavel'), (11, 'inviavel'), (12, 'inviavel'), (12, 'inviavel'), (13, 'viavel')] | ok |
| 40 | 7 | M/T/N | sim | 4 | 7 | 7 | [(4, 'inviavel'), (5, 'inviavel'), (5, 'inviavel'), (6, 'inviavel'), (6, 'inviavel'), (7, 'inviavel'), (7, 'viavel')] | ok |

Tempo total: 54 s

TUDO OK: piso novo <= menor viável em todas
