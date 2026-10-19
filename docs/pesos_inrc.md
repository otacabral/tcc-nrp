# Pesos das restrições flexíveis nas 69 instâncias do INRC-2010

Criado em 19/10/2026 (sessão de 19/10, item 8), para a Redação. Só leitura dos arquivos, sem
solver. Gerado por `python docs\diagnostico\censo_flexiveis.py`; detalhe por instância e
família em `resultados/censo_flexiveis_2026-10-19/censo.csv`, resumo em `censo.md` (mesma
pasta).

**Regra de contagem.** Uma família está ativa num contrato pela regra de 15/09 (`DECISOES.md`,
"2026-09-15 — Regra geral de ativação de restrição flexível": ligada e peso > 0). Os 235
contratos das 69 instâncias contam um a um; padrões indesejados contam por padrão referenciado;
pedidos, por pedido. "Ocorrências" = em quantos contratos (padrões, pedidos) a família está
ativa com aquele peso.

## Por família

| Família (XML) | Instâncias com a família ativa (de 69) | Pesos observados (peso: ocorrências) |
|---|---:|---|
| MaxNumAssignments | 69 | 1: 146 · 3: 74 · 5: 15 |
| MinNumAssignments | 69 | 1: 146 · 3: 74 · 5: 15 |
| MaxConsecutiveWorkingDays | 69 | 1: 146 · 4: 74 · 8: 15 |
| MinConsecutiveWorkingDays | 69 | 1: 146 · 3: 6 · 4: 68 · 7: 15 |
| MaxConsecutiveFreeDays | 69 | 1: 146 · 6: 15 · 7: 74 |
| MinConsecutiveFreeDays | 69 | 1: 147 · 3: 70 · 8: 15 · 31: 3 |
| MaxConsecutiveWorkingWeekends | 49 | 1: 58 · 5: 75 · 10: 15 |
| MinConsecutiveWorkingWeekends | 41 | 1: 33 · 3: 12 · 5: 50 |
| MaxWorkingWeekendsInFourWeeks | 0 | — (desligada nos 235 contratos) |
| CompleteWeekends | 69 | 1: 145 · 10: 90 |
| IdenticalShiftTypesDuringWeekend | 69 | 1: 144 · 10: 90 |
| NoNightShiftBeforeFreeWeekend | 44 | 1: 70 · 10: 75 (o avaliador oficial não a pontua; `DECISOES.md`, 18/09) |
| TwoFreeDaysAfterNightShifts | 0 | — (elemento ausente nas 69) |
| AlternativeSkillCategory | 18 | 1: 25 · 10: 35 |
| Padrões indesejados | 57 | 1: 330 · 3: 5 · 4: 5 · 5: 5 · 7: 10 · 10: 13 |
| Pedido de folga no dia (DayOffRequest) | 49 | 1: 6.285 · 5: 500 |
| Pedido de folga no turno (ShiftOffRequest) | 49 | 1: 6.484 · 3: 250 |
| Pedidos para trabalhar (DayOn / ShiftOn) | 0 | — (nenhuma instância os traz) |

## Por instância

- **41 das 69 instâncias usam só peso 1** em tudo o que está ativo — entre elas todas as
  `early` (sprint, medium e long) e as quatro de validação (`sprint01`, `sprint02`, `long01`,
  `long02`).
- **28 usam pesos diferentes de 1**, em todos os lotes exceto `early`: `late`, `hidden` e `hint`.
- O `medium_late05` (quinto alvo de validação) tem pesos 1, 3, 4, 5, 7, 10 e **31** — o 31 está
  no contrato 3, em `MinConsecutiveFreeDays` com valor 10 (conferido no XML cru, linha 235).
  No contrato 0: 3 (número de atribuições), 4 (dias seguidos), 7 e 3 (folgas seguidas), 5
  (fins de semana seguidos), 10 (fim de semana completo, turnos idênticos, noturno antes de fim
  de semana livre, habilidade).

## O que isso sustenta (e o que não)

- Sustenta: **o INRC não tem um conjunto único de pesos**. O mesmo critério vale 1 numa
  instância e 10 noutra; a descrição oficial (`docs/nrpcompetition_description.pdf`, seção 2.2)
  diz que unidades diferentes dão pesos diferentes. "Usar os pesos do INRC" exige dizer de qual
  instância e por quê. É o fato que o registro da opção B cita (`DECISOES.md`, "2026-10-14").
- Não sustenta: nenhuma afirmação sobre o que os pesos *deveriam* ser, nem sobre o motivo dos
  organizadores para cada valor — a documentação não o diz.
