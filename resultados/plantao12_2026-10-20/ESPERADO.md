# Parte 3 (3º bloco, 20/10) — Teste do plantão de 12 h no fim de semana (sem código)

Registrado e commitado **antes** de rodar.

## Caso
- Modelo "6 h de dia + noturno de 12 h" (M 7–13, T 13–19, N 19–7) + 4º turno **D12, 7–19**
  acrescentado na tabela de turnos (a tela tem `num_rows="dynamic"`; o AppTest não edita
  `st.data_editor`, então o caso entra pela mesma `Entrada` que a tela monta).
- Demanda de técnicos — dia útil: M 5, T 5, D12 0, N 4; fim de semana: M 0, T 0, D12 5, N 4.
- 22 profissionais (4 enfermeiros, 18 técnicos), 28 dias, início 04/01/2027, orçamento 20 min.
- **Leitura adotada:** demanda de **enfermeiros 0** em todos os turnos (o pedido só dá técnicos);
  enfermeiro pode cobrir posto de técnico (critério Importante, padrão).

## Esperado
- (a) A ferramenta aceita o 4º turno e a demanda 0 (sem erro de entrada).
- (b) A escala sai legal: veredito "admite escala legal" com 22. Horas de técnico demandadas:
  dia útil 5×6 + 5×6 + 4×12 = 108 h; fim de semana 5×12 + 4×12 = 108 h; 28 dias = 3.024 h,
  contra 22 × 44 × 4 = 3.872 h de contrato (folga de ~22%).
- (c) Nenhum turno nas 36 h depois de um D12 (sábado D12 termina 19h; segunda 7h é o primeiro
  horário liberado), medido na escala, fora do modelo.
- (d) Conferência de descanso: "cumpre".
- (e) Nenhum D12 em dia útil (a cobertura é igualdade: demanda 0 = nenhuma atribuição).

## `pares_proibidos_por_horario` com o D12 entre turnos de 6 h (conta à mão)
Regra: depois de turno ≥ 12 h, 36 h (art. 59-A); depois dos demais, 11 h (art. 66); com um dia
livre no meio, ≥ 24 h (art. 67, folga isolada).
- D12 (7–19) → qualquer turno no dia seguinte: descanso ≤ 24 + 23 − 19 = 28 h < 36 → **proibido**
  (D12, M, T, N). Dois dias depois: 48 + 7 − 19 = 36 h → M e D12 **liberados** (exatamente 36 h).
- N (19–7) → qualquer turno no dia seguinte: proibido; dois dias depois: M e D12 (24 h), T (30 h)
  < 36 → **proibidos**; N (36 h) liberado.
- M (7–13) → D12 no dia seguinte: 18 h ≥ 11 → liberado; T (13–19) → D12 no dia seguinte: 12 h ≥ 11
  → liberado; T → M no dia seguinte: 12 h → liberado.
- Lista esperada (salto 1 e 2): (D12,1,D12) (D12,1,M) (D12,1,N) (D12,1,T) (N,1,D12) (N,1,M)
  (N,1,N) (N,1,T) (N,2,D12) (N,2,M) (N,2,T). *Nota de honestidade: a lista foi impressa pelo
  gerador enquanto este esperado era escrito; bate com a conta à mão acima, que é a referência.*
