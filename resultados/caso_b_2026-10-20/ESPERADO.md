# Caso B (Massens 2019, quatro setores somados) — esperado, ANTES da rodada (20/10)

Entrada: `entrada.py` nesta pasta. 89 pessoas (15 enfermeiros, 74 técnicos), rodízio livre,
classificação padrão, 44 h, sem férias, orçamento 60 min. Rodada de porte; só na fase 2.

## Conta à mão (a mesma do caso A)

| | Técnicos | Enfermeiros | Total |
|---|---:|---:|---:|
| Segunda: M + T + N | 19 + 19 + 17 = 55 | 4 + 4 + 2 = 10 | **65** |
| Domingo: D12 + N | 19 + 17 = 36 | 2 + 2 = 4 | **40** |
| Sábado N (só a N da segunda) | 17 | 2 | 19 |

- Conta do pedido: **65 + 40 = 105 > 89**. Separando o sábado: 40 + 19 + (M e T da segunda) 46 =
  **105**; o sábado não muda o total.
- Enfermeiros sozinhos: domingo 4 + sábado N 2 + M e T da segunda 8 = 14 ≤ 15: a categoria fecha;
  quem falta são técnicos (ou enfermeiros em posto de técnico).
- Carga 44 h: não aperta (13.920 h demandadas; 89 × 176 = 15.664 h).

**Esperado:** não fecha com 89; menor quadro **≥ 105**.

## O que a ferramenta vai fazer (lido no código, sem rodar)

- Piso dela: **68** (não vê a segunda-feira).
- **A busca vai só até 89 + 12 = 101** (`ferramenta.MARGEM` = 12), abaixo de 105. Mesmo que o
  solver prove cada quadro de 89 a 101 inviável dentro dos 60 min, o veredito máximo possível é
  "Não há escala legal até 101 profissionais; o menor quadro viável está acima disso". O mais
  provável, pelo porte (NUMEROS_TCC §11–12: o modelo 6 h + 12 h concentrou os não decididos), é o
  orçamento acabar antes: "O quadro informado é insuficiente; o menor quadro viável não foi
  determinado em 60 min" (se o 89 for provado inviável) ou "Sem resposta…". **Nenhum desses é
  "faltam N"**. Leitura para a Orientação: o caso B, como está, não mede o menor quadro; mede o
  porte.

## Conferência contra a Parte 3 e premissa compartilhada

Parte 3: 14 + 9 = 23, igual ao resultado da ferramenta. A regra das 36 h entra na conta e no modelo
(e na conferência de descanso) — a conta confere a aritmética, não a regra.

## Sob D12 = 11 h — hipótese de sensibilidade, não regra da ferramenta (acréscimo de 20/10, Parte 6, antes de rodar)

Mesmas regras do caso A (ver o ESPERADO do caso A): só a noite de domingo bloqueia a segunda
inteira; a noite de sábado só pode fazer a N da segunda.

| | Técnicos | Enfermeiros | Total |
|---|---:|---:|---:|
| Segunda: M + T + N | 55 | 10 | 65 |
| Domingo N (bloqueia a segunda) | 17 | 2 | **19** |
| Sábado N (só a N da segunda, que pede 17 + 2) | 17 | 2 | 19 |

- Conta: 65 + 19 = **84 ≤ 89**; separando o sábado: 19 + 19 + 46 = 84.
- Enfermeiros: 2 + 2 + 8 = 12 ≤ 15; técnicos: 17 + 17 + 38 = 72 ≤ 74 (folga de 2).
- Carga 44 h: não aperta.

**Esperado sob 11 h:** a conta (necessária, não suficiente) **cabe em 89**; o 89 fica dentro da
busca (sem o problema da margem do caso com 36 h). Leitura preliminar do Otávio ("B deve caber"):
**confere** quanto à conta. O veredito é do solver, e o risco de porte continua (NUMEROS_TCC §11–12).

**Premissa compartilhada:** a mesma do caso A.

## Depois da Parte 7 (v1.4.1) — quem prova: conta x solver (acréscimo de 20/10, tarde, antes de rodar)

Conferido sem solver (`docs/diagnostico/piso_pares.py --casos`):

- **36 h (B36_livre):** piso **105** (era 68). Pior par: dom 10/01 e seg 11/01 — 65 + 40 contra
  89 disponíveis. Como 105 > 101 (89 + `MARGEM` 12), **todos os quadros de 89 a 101 são recusados
  pela conta**: veredito **"Não há escala legal até 101 profissionais; o menor quadro viável está
  acima disso."**, provado pela conta, **sem solver, em segundos** (conferido: 13 tentativas,
  todas "piso"). Diagnóstico: "Dois dias seguidos". A rodada B36 deixa de medir porte.
- **D12 = 11 h (B11_livre) — hipótese de sensibilidade, não regra da ferramenta:** piso 68; a
  conta não recusa 89 (65 + 19 = 84 ≤ 89; enfermeiros 10 + 2 = 12 ≤ 15). O veredito é do solver,
  e o risco de porte continua.
