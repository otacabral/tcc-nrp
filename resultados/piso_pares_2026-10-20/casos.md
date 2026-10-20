# Teste 4 — casos A e B sem solver

- 36 h, A turno fixo (24): piso 30; pior par dom 17/01 e seg 18/01: 17 + 11 contra 22 disponíveis (excesso 6); enfermeiros 3 + 2 contra 4 (excesso 1); bloqueiam o dia seguinte: ['D12', 'N'] — ok
- 36 h, A rodízio livre (24): piso 30; pior par dom 17/01 e seg 18/01: 17 + 11 contra 22 disponíveis (excesso 6); enfermeiros 3 + 2 contra 4 (excesso 1); bloqueiam o dia seguinte: ['D12', 'N'] — ok
- 36 h, B (89): piso 105; pior par dom 10/01 e seg 11/01: 65 + 40 contra 89 disponíveis (excesso 16); enfermeiros 10 + 4 contra 15 (excesso -1); bloqueiam o dia seguinte: ['D12', 'N'] — ok
HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA
- D12 = 11 h, A turno fixo (24): piso 18; pior par dom 17/01 e seg 18/01: 17 + 5 contra 22 disponíveis (excesso 0); enfermeiros 3 + 1 contra 4 (excesso 0); bloqueiam o dia seguinte: ['N'] — ok
- D12 = 11 h, A rodízio livre (24): piso 18; pior par dom 17/01 e seg 18/01: 17 + 5 contra 22 disponíveis (excesso 0); enfermeiros 3 + 1 contra 4 (excesso 0); bloqueiam o dia seguinte: ['N'] — ok
- D12 = 11 h, B (89): piso 68; pior par seg 04/01 e ter 05/01: 65 + 19 contra 89 disponíveis (excesso -5); enfermeiros 10 + 2 contra 15 (excesso -3); bloqueiam o dia seguinte: ['N'] — ok
- 36 h, B pela ferramenta: Não há escala legal até 101 profissionais; o menor quadro viável está acima disso. (tentativas: 13, todas pela conta: True) — ok

DESCANSO_POR_TURNO ao fim: {}

OK
