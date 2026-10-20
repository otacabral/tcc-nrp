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
