# Parte A — esperado registrado ANTES de reproduzir (07/10/2026)

## O caso do Otávio (entrada exata)

- **Modelo de turnos** "6 h de dia + noturno de 12 h": M 7–13, T 13–19, N 19–7. Fim de semana sábado e domingo. Início 12/10/2026 (segunda). Grau intermediário. Sem pacientes.
- **Equipe:** 15 enfermeiros + 5 técnicos, todos com 44 h. Sem férias, licenças nem pedidos.
- **Demanda, todos os dias** (sem fim de semana próprio; grade por data não editada):
  - M: 2 enfermeiros + 1 técnico;
  - T: 2 enfermeiros + 1 técnico;
  - N: 3 enfermeiros + 2 técnicos.
- **O que a tela mostrou:** "Não foi possível gerar a escala no tempo disponível" e "20 profissionais (15 enf. + 5 téc.): o solver falhou".
- **Log do HiGHS** (copiado pelo Otávio): "Time limit reached", Primal bound inf, Dual bound 14, 2.083 nós, Expl. 70,11%, 600,01 s.

## A conta (projeto de redação): condição necessária, não prova

O N de 12 h exige 36 h de descanso. Quem faz N no dia d não trabalha em d + 1 e só volta no N de d + 2.

Ocupados por dia = 5 (descansando do N da véspera) + 5 (no N) + 6 (M e T) = **16**. Entre eles, pelo menos **10 enfermeiros**: 3 no N, 3 descansando do N, 4 em M e T.

**Esperado:**
- **20 (15 + 5):** sobram 4 por dia. A conta não vê impedimento.
- **16:** fronteira, com zero de folga.
- **Se 20 for inviável**, há uma combinação de regras que a conta não enxerga. Achá-la é o objetivo da parte A.

## Esperado de cada teste (A3), registrado antes de cada um

- **a) 15 + 5, limite de 3.600 s.** Pela conta não há impedimento, então o esperado é **achar escala**. Se esgotar de novo sem escala, ou provar inviabilidade, o impedimento está numa regra que a conta não vê.
- **b) Monotonia, com 22, 24 e 26** (acréscimos como enfermeiros), 600 s cada. Esperado: **todos acham escala**, porque mais gente nunca piora. Se nenhum fechar, há uma regra bloqueando independentemente do quadro.
- **c) Uma regra relaxada por vez**, 600 s cada, numa cópia do modelo em `docs/diagnostico/`. Esperado: **pelo menos uma remoção destrava**, e é ela que aponta a regra que aperta.
- **d) Valores gerados para este modelo de turnos.** Esperado:
  - `MaxNumAssignments` = floor(176 ÷ 6) = **29**, porque o turno mais curto tem 6 h;
  - teto de horas = **176 h** por pessoa;
  - pares proibidos tirados dos horários reais: depois do N, 36 h, ou seja, nada no dia seguinte; entre turnos diurnos de 6 h, 11 h de interjornada;
  - nada calculado como se todos os turnos tivessem 12 h.
- **e) 10 + 5:** confirmar no log o que foi "o solver falhou" em 16 (11 + 5) e explicar a duração total.
- **f)** Classificar o caso: entrada problemática, defeito (arquivo e linha) ou dificuldade do solver.

## Reprodução pelo caminho da tela (registrada antes de rodar, 07/10)

**Resultado do A3a, que motiva esta reprodução:** 15 + 5, limite de 3.600 s. Ótimo **provado**, valor 18, em 1.077,7 s. A primeira escala saiu aos 0,4 s (heurística "J" do HiGHS).

**Esperado** para `python docs\diagnostico\caso_parte_a.py verificar --enf 15 --tec 5`, que passa por `ferramenta.verificar` com os limites da tela (600 s e 180 s):
- veredito "admite", escala gerada sem prova: "pode haver uma melhor", com gap;
- tentativas `[(20, 'viavel', 15, 5)]`;
- etapa 2 "não rodou", porque a etapa 1 não prova o ótimo em 600 s.

Se sair "erro" ("o solver falhou"), o defeito está na orquestração, e o print `[ERRO] ...` da `ferramenta.resolver` diz qual.

**Resultado (07/10):** igual ao esperado. Veredito "admite", com "Escala gerada; pode haver uma melhor (gap 15,8% …)", tentativas `[(20, 'viavel', 15, 5)]`, em 601,5 s. A etapa 2 não rodou. **O "o solver falhou" do Otávio não se reproduz** com a entrada descrita, nesta máquina.

## A3e — 10 + 5 pelo caminho da tela (registrado antes de rodar, 07/10)

**Esperado:**
- 15: "piso" (inviável pela aritmética, por horas);
- 16 (10 + 6): "inviavel", provado pelo solver;
- 16 (11 + 5): é a **fronteira** da conta dos ocupados por dia (folga 0), então qualquer uma das três respostas legítimas pode sair: "viavel", "inviavel" ou "indeterminado" (sem escala no tempo);
- "erro" ("o solver falhou") **não** é resposta legítima: indicaria defeito de orquestração, com o motivo no print `[ERRO]`.

**Duração esperada:** até cerca de 600 s por resolução que não fecha, mais 180 s de etapa 2 se houver prova.
