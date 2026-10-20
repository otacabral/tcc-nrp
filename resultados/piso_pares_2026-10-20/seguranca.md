# Teste 1 — segurança do piso por pares (224 rodadas registradas)

Só as rodadas em que algo muda (28); nas outras 196, piso e motivos iguais aos da v1.4.0.

| Fonte | Caso | Quadro | Menor viável registrado | Piso antigo | Piso novo | Tentativas que passam à conta | Motivos (antigo → novo) | Resultado |
|---|---|---:|---:|---:|---:|---|---|---|
| bateria v1.4.0 | P05 | 14 | 15 | 14 | 15 | 14 (inviavel) | ['categoria', 'alternancia'] | ok |
| demonstração v1.4.0 | demo18 | 28 | 29 | 28 | 29 | 28 (inviavel) | ['alternancia'] | ok |
| nível 3 (08/10) | N001 | 12 | 21 | 21 | 21 | — | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N003 | 16 | 20 | 14 | 20 | 16 (inviavel), 17 (inviavel), 18 (inviavel), 19 (inviavel) | ['categoria', 'categoria'] | ok |
| nível 3 (08/10) | N004 | 12 | None | 18 | 19 | 18 (inviavel), 18 (inviavel) | ['horas', 'dia'] → ['horas', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N006 | 8 | None | 19 | 20 | — | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N009 | 7 | 14 | 14 | 14 | — | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N010 | 10 | 16 | 14 | 14 | — | ['horas', 'dia'] → ['horas', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N012 | 13 | 16 | 14 | 15 | 14 (inviavel) | ['categoria'] → ['categoria', 'pares'] | ok |
| nível 3 (08/10) | N013 | 10 | None | 16 | 18 | 16 (inviavel), 16 (inviavel), 17 (inviavel), 17 (inviavel) | ['horas', 'dia'] → ['horas', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N014 | 11 | 22 | 20 | 22 | 20 (inviavel), 20 (inviavel), 21 (inviavel), 21 (inviavel) | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N015 | 5 | 9 | 8 | 8 | — | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N017 | 7 | 19 | 19 | 19 | — | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N020 | 16 | 21 | 13 | 18 | 16 (inviavel), 17 (inviavel) | ['categoria', 'dia'] → ['categoria', 'categoria', 'dia'] | ok |
| nível 3 (08/10) | N022 | 5 | 11 | 11 | 11 | — | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N024 | 11 | 16 | 12 | 16 | 12 (inviavel), 13 (inviavel), 14 (inviavel), 15 (inviavel) | ['categoria', 'alternancia', 'dia'] | ok |
| nível 3 (08/10) | N025 | 6 | 16 | 11 | 16 | 11 (inviavel), 11 (inviavel), 12 (inviavel), 12 (inviavel), 13 (inviavel), 13 (inviavel), 14 (inviavel), 14 (inviavel), 15 (inviavel), 15 (inviavel) | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N026 | 11 | 19 | 17 | 18 | 17 (inviavel), 17 (inviavel) | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N027 | 13 | 14 | 9 | 14 | 13 (inviavel) | ['categoria'] → ['categoria', 'categoria'] | ok |
| nível 3 (08/10) | N029 | 11 | 13 | 8 | 12 | 11 (inviavel) | ['categoria'] → ['categoria', 'categoria'] | ok |
| nível 3 (08/10) | N030 | 9 | None | 16 | 17 | 16 (inviavel), 16 (inviavel) | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N033 | 6 | 11 | 11 | 11 | — | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N034 | 7 | 17 | 14 | 17 | 14 (inviavel), 14 (inviavel), 15 (inviavel), 15 (inviavel), 16 (inviavel), 16 (inviavel) | ['categoria', 'dia'] → ['categoria', 'pares', 'dia'] | ok |
| nível 3 (08/10) | N035 | 16 | None | 18 | 18 | — | ['horas'] → ['horas', 'pares'] | ok |
| propriedades (08/10) | P05_mais_pessoa | 15 | 16 | 14 | 16 | 15 (inviavel) | ['categoria', 'categoria'] | ok |
| propriedades (08/10) | P05_embaralhado | 14 | 15 | 14 | 15 | 14 (inviavel) | ['categoria', 'alternancia'] | ok |
| propriedades (08/10) | K3_mais_posto | 16 | None | 13 | 17 | 16 (inviavel) | [] → ['pares'] | ok |
| Parte 3 (20/10) | plantao12 | 22 | 23 | 15 | 23 | 22 (inviavel) | [] → ['pares'] | ok |

TUDO OK: nenhum quadro viável recusado
