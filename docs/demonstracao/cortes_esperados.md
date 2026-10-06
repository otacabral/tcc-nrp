# Demonstração — cortes esperados pela conta (versão de 05/10, noite)

**Registrado em 05/10/2026, ANTES de refazer as rodadas pela tela**, depois de duas decisões
do Otávio: a equipe da rodada 1 passa a 10 enfermeiros + 20 técnicos (33/67 do Parecer), e o
20/11 é feriado como o 02/11. A versão anterior deste arquivo (equipe 8 + 22, 20/11 dia útil)
está no histórico do git (commit `006d83a`).

Conta sem solver e sem as contas da ferramenta: `python docs\demonstracao\conta_cortes.py`.
Técnicos retirados do fim da lista do caso (os últimos são os de 36 h); enfermeiros fixos em 10.
Os alertas do COFEN são os do próprio Parecer (`instancia_br.alertas_cofen`), já com o grau do
grupo de maior carga (intermediário: 84 h contra 32 h e 40 h).

| técnicos | total | horas posto téc. | tetos dos téc. | enf. em posto téc. (mín.) | folga dos enf. | pior par de dias (demanda / disponíveis) | alertas COFEN | trava pela conta |
|---|---|---|---|---|---|---|---|---|
| 20 | 30 | 3420 h | 3132 h | 24 | 660 h | 03/11–04/11: 28 / 29 | 0 | não |
| 19 | 29 | 3420 h | 2988 h | 36 | 660 h | 03/11–04/11: 28 / 28 | 1 | não |
| 18 | 28 | 3420 h | 2844 h | 48 | 660 h | 03/11–04/11: 28 / 27 | 1 | dois dias seguidos |
| 17 | 27 | 3420 h | 2700 h | 60 | 660 h | 03/11–04/11: 28 / 26 | 1 | horas, dois dias seguidos |
| 16 | 26 | 3420 h | 2556 h | 72 | 660 h | 03/11–04/11: 28 / 25 | 1 | horas, dois dias seguidos |
| 15 | 25 | 3420 h | 2412 h | 84 | 660 h | 03/11–04/11: 28 / 24 | 1 | horas, dois dias seguidos |
| 14 | 24 | 3420 h | 2268 h | 96 | 660 h | 03/11–04/11: 28 / 23 | 1 | horas, dois dias seguidos |
| 13 | 23 | 3420 h | 2100 h | 110 | 660 h | 03/11–04/11: 28 / 22 | 1 | horas, dois dias seguidos |
| 12 | 22 | 3420 h | 1932 h | 124 | 660 h | 03/11–04/11: 28 / 21 | 1 | horas, dois dias seguidos |

"Enf. em posto téc. (mín.)" é o mínimo que a conta de horas obriga; o solver pode precisar de
mais. "Trava pela conta" = alguma conta já prova que não há escala.

## Esperado

| Rodada | Técnicos (quadro) | Esperado |
|---|---|---|
| 1 | 20 (30) | **admite**; **zero alertas do COFEN** (proporção: 10 enfermeiros, o Parecer pede ceil(0,33 × 30) = 10; QP completo 29,995 ≤ 30); enfermeiro em posto de técnico **≥ 24** (faltam 288 h de técnico: 3.420 h de posto contra 3.132 h de tetos) |
| 2 | 19 (29) | **admite**; **1 alerta**: "quadro de 29 abaixo do QP completo do Parecer (29,85, com IST de 15%); o núcleo assistencial, sem IST, é 25,96"; enfermeiro em posto de técnico ≥ 36 |
| 2 | 18 (28) | **trava**: "Falta 1; o menor quadro viável é 29". O diagnóstico deve mostrar **só "Alternância do plantão de 12 h"**: ter 03/11 e qua 04/11 somam 28 plantões, e há 27 pessoas disponíveis em pelo menos um dos dois dias (Karen Dias de férias). **"Horas" não dispara**: faltam 576 h de técnico, contra 660 h de folga dos enfermeiros. 1 alerta: "quadro de 28 abaixo do QP completo do Parecer (29,70, ...); o núcleo ... é 25,82" |

**Transições:**
- sem alerta → com alerta: de **20 para 19** técnicos;
- enfermeiro em posto de técnico: **já em 20** (pela conta, ≥ 24) — não há corte "limpo" sem ele;
- trava: em **18** técnicos, pelo par de dias.

**Conferência cruzada, sem solver:** o diagnóstico da ferramenta (`motivos_da_trava`), calculado
depois da conta acima, dá o mesmo: nenhum motivo em 20 e 19; "alternância" em 18.

## Resultado pela tela (05/10/2026, 21h, anotado DEPOIS de rodar; o esperado acima não mudou)

| Técnicos | Esperado | Saiu na tela |
|---|---|---|
| 20 (rodada 1) | admite; 0 alertas; enf. em posto de téc. ≥ 24 | admite; **0 alertas**; **24** — o mínimo da conta |
| 19 | admite; 1 alerta (QP 29,85); ≥ 36 | admite; **1 alerta**, texto idêntico ao esperado; **36** — o mínimo da conta |
| 18 | trava; "Falta 1; o menor quadro viável é 29"; diagnóstico só "Alternância" (ter 03/11 e qua 04/11, 28 plantões, 27 pessoas); 1 alerta (QP 29,70) | **igual**, palavra por palavra. A escala de 29 é 10 enfermeiros + 19 técnicos, com 34 turnos de enfermeiro em posto de técnico |
