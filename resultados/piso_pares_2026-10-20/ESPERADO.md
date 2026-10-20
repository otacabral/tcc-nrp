# Parte 7 — piso por pares de dias (v1.4.1): esperado, ANTES de implementar (20/10)

Pedido da Orientação, 20/10 (tarde). Objetivo: recusar sem solver os quadros que dois dias
seguidos já provam insuficientes. Hoje o piso (`ferramenta.piso`) dá 18 no caso A e 68 no B, e
cada quadro até o mínimo gasta o orçamento do solver.

## A regra (condição NECESSÁRIA, não suficiente)

Para cada par de dias consecutivos (d, d+1) do horizonte:

    postos exigidos em d+1 (todos os turnos)
  + postos exigidos em d em turnos que BLOQUEIAM o dia d+1 inteiro
  <= pessoas disponíveis em pelo menos um dos dois dias (férias e licenças descontadas)

- **Bloqueia o dia d+1 inteiro**: o turno t forma par proibido de salto 1 com TODOS os turnos de
  d+1. Tirado dos pares que o gerador já calcula (`instancia_br.pares_proibidos_por_horario`,
  `descartar=False`, que usa `descanso_exigido`, inclusive `DESCANSO_POR_TURNO`), nunca de
  "duração ≥ 12 h". Com o limite efetivo de dias seguidos = 1 (`limite_efetivo`), todo turno
  bloqueia. A conta acompanha horários editados e a hipótese de 11 h.
- Por quê: quem faz turno que bloqueia d+1 não trabalha em d+1, e cada pessoa faz no máximo um
  turno por dia; logo as duas parcelas são pessoas diferentes.
- **Também só para enfermeiros** (posto de enfermeiro, a variante "E", só enfermeiro cobre):
  mesma conta com os postos de enfermeiro e os enfermeiros disponíveis. **Não** há conta só de
  técnicos: enfermeiro ocupa posto de técnico, e essa conta recusaria quadro viável.
- Leitura do código sobre quem cobre o quê (a registrar no relatório): a ferramenta resolve com
  `habilidade_rigida=True` (`experimento_a.modelo_br`), e com isso o critério "habilidade
  alternativa" não entra no modelo (`modelo.py`, `if r.ativa and not habilidade_rigida`): técnico
  NUNCA cobre posto de enfermeiro, em nenhuma classificação. Enfermeiro tem as duas habilidades
  (`instancia_br._equipe`) e cobre os dois postos.
- Como vira quadro: as pessoas acrescentadas não têm férias e estão nos dois dias; logo o menor
  quadro é o informado + o maior excesso (total), e o informado + o maior excesso de enfermeiros
  (a 2ª composição da varredura põe todos os acréscimos como enfermeiros). Entra em
  `ferramenta.piso` como mais um termo do `max`.
- Diagnóstico: quando a conta dispara no quadro informado e o limite efetivo não é 1 (a
  "alternância" existente fica como está), o motivo diz "A conta prévia do menor quadro provou…"
  com o par de dias e os números, no formato "dom 17/01 e seg 18/01: 17 postos na segunda + 11 no
  domingo em turnos que impedem a segunda (D12, N); disponíveis 22". Motivo novo
  `pares` ("Dois dias seguidos"); o de enfermeiros sai como `categoria`, como já faz a
  alternância de enfermeiros.

## Esperado

| Caso | Conta (pior par) | Quadro informado | Esperado |
|---|---|---:|---|
| Parte 3 (só técnicos, sem férias) | seg 14 + dom 9 = **23** | 22 | 22 recusado pela conta; 23 aceito (conta 23 ≤ 23) |
| Caso A, 36 h | total 17 + 11 = **28** sem férias; enfermeiros 3 + 2 = 5 > 4; em 17–18/01 as duas pessoas de férias estão fora: 28 > 22 | 24 | piso **30**; 24 a 29 recusados pela conta; o solver começa em 30 |
| Caso B, 36 h | 65 + 40 = **105** | 89 | 105 > 101 (89 + MARGEM 12): veredito "Não há escala legal até 101 profissionais…", provado pela conta, **sem solver** |
| Caso A, `{"D12": 11}` | 17 + 5 = **22**; com férias 22 ≤ 22; enfermeiros 3 + 1 = 4 ≤ 4 | 24 | a conta **não** recusa 24 |
| Caso B, `{"D12": 11}` | 65 + 19 = **84** | 89 | a conta **não** recusa 89 |

Caso B por par (seg depois de dom): segunda M 4+19, T 4+19, N 2+17 = 65; domingo D12 2+19 e N 2+17
= 40, os dois de 12 h, bloqueiam a segunda. Enfermeiros: 10 + 4 = 14 ≤ 15.

**Instâncias registradas** (P01–P18, K1–K6, demonstração, regressão, os 243 da identidade, testes
da tela): **nenhum quadro viável recusado**. Mudanças admitidas nas rodadas registradas: uma
tentativa `(q, "inviavel", e, t)` provada pelo solver pode virar `(q, "piso", None, None)`, só
com q abaixo do menor quadro viável registrado. Qualquer outra diferença (menor viável, frase,
veredito) é falha. A lista exata das que mudam sai da análise sem solver (item extra do
relatório) e é registrada **antes** da suíte da v1.4.1.

A regressão (INRC) não passa por `ferramenta.piso`: idêntica. A entrada do solver (`montar`) não
muda: **243/243 idênticos à v1.4.0**.

## Testes (entram na suíte da v1.4.1)

1. **Segurança**: em todas as rodadas registradas com quadro viável, o piso novo ≤ esse quadro;
   identidade 243/243 contra a v1.4.0.
2. **Sorteio pequeno**: instâncias pequenas com turnos de 12 h e de 6 h, semente fixa, poucas
   pessoas, 7 a 14 dias; o solver acha o menor quadro viável; afirmar piso ≤ menor viável em
   todas. Quantas e a semente: no relatório.
3. **Controle**: Parte 3 com 22 (recusa) e 23 (aceita).
4. **Casos A e B** conferidos sem solver (`montar` + `piso`), nas duas regras.

## Premissa compartilhada (declarada)

A conta lê os pares do mesmo gerador que o modelo (`pares_proibidos_por_horario` /
`descanso_exigido`). Ela confere a **aritmética** e a **coerência com o modelo**, não a leitura
legal da regra das 36 h (nem a das 11 h da hipótese).
