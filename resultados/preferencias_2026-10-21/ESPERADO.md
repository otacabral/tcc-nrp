# Preferência de máximo de dias seguidos e de máximo de turnos (21/10) — esperado

Registrado e commitado **antes** de implementar e de rodar. Decisão: `DECISOES.md`, "2026-10-21 —
Máximo de dias seguidos e máximo de turnos também como preferência" (com as decisões de
implementação 1 a 6). Script: `docs/diagnostico/preferencias.py`; suíte:
`docs/diagnostico/fechar_v142.sh` (vira v1.4.2 se TUDO OK).

## (a) Identidade com a classificação padrão

Entrada do solver (XML da instância, LP da etapa 1, LP da etapa 2) idêntica à da v1.4.1 nos 81
casos de sempre, acréscimos 0, 1 e 2: **243 de 243**; e também com os pedidos como linhas da
tabela (243 de 243). Worktree de leitura `..\tcc-nrp-v141` na tag v1.4.1.

## (b) Controle: ligar a preferência muda o problema da etapa 1

No primeiro caso da lista (P01), com acréscimo 0:
- máximo de dias seguidos (preferência) em Importante, limite 4 → o LP da etapa 1 **muda** e
  contém `pref_max_consecutive_working_days`; o padrão não contém;
- máximo de turnos em Importante, limite 10 → o LP **muda** e contém `pref_max_num_assignments`;
- limite acima do legal (dias 9; turnos 999) em Importante → o LP muda (a família existe), e o
  limite usado é o legal (decisão 3): conferido no contrato aplicado (`valor` = o legal).

## (c) Caso pequeno, com solver

O caso da Parte 4 de 20/10 (`resultados/max_dias_2026-10-20/ESPERADO.md`): turnos M 7–13 e
T 13–19, 0 enfermeiros, 14 técnicos, demanda M 6 e T 6 todos os dias, 28 dias; máximo rígido do
hospital 6 (o padrão).

**(c1) Preferência de dias seguidos Lp = 4 em Importante** (o resto, padrão).
- Conta, antes de rodar: com no máximo 6 dias seguidos, cada pessoa trabalha no máximo 24 dos
  28 dias (6 + folga, quatro vezes); a demanda é 12 × 28 = 336 = 14 × 24, então **todos
  trabalham exatamente 24 dias e folgam 4**. Com 4 folgas há no máximo 5 sequências, e o
  excesso sobre 4 é pelo menos 24 − 5 × 4 = **4 por pessoa**, atingível (5, 5, 5, 5, 4 com
  folgas isoladas; 2 de folga por dia, 2 × 28 = 56 = 14 × 4). **Esperado: "O quadro informado
  admite escala legal", 56 violações da preferência, provado.**
- Na escala: nenhuma sequência maior que 6, contada fora do modelo **e** no relógio
  (`conformidade["max_consec"]`); conferência do descanso aprovada.
- Violações acima de 4 contadas no script, das sequências da escala, sem `avaliacao.py` nem
  modelo: **= as do "Resultado por critério"** (que vêm do `avaliacao.py`).

**(c2) As duas preferências, em níveis diferentes:** dias Lp = 4 em Importante e turnos γp = 23
em Desejável. Como todos trabalham 24, cada um excede 23 em 1: **14 violações de turnos**,
inevitáveis; **56 de dias seguidos**. Planejamento: Desejável vale no máximo 14 × (28 − 23) =
70; o Importante fundido daria 71 × 336 + 70 ≥ 10.000, então **"em sequência, 2 blocos"**. As
duas contagens do script = as do resultado por critério.

## (d) Regressão

`python src\regressao.py --todos`: os quatro ótimos do INRC (56, 58, 197, 219) sem mudança.

## (e) Identidade nas cinco entradas da fase 2

A36_livre, A36_fixo, A11_fixo, B11_livre, B36_livre, cada uma com o `DESCANSO_POR_TURNO` da sua
rodada; acréscimo 0, e 6 nas do caso A (o quadro 30, que foi ao solver): 8 casos, 24 arquivos,
**idênticos byte a byte** à v1.4.1.

## Testes da tela atualizados com registro (decisão 6)

- **opB-d:** "máximo de dias seguidos" e "máximo de turnos" deixam de ser "já garantido pela
  CLT" (situação "ok"); "sequências indesejadas" continua.
- **opB-tela:** "Noturno e carga — 0 de 4 considerados" (era 0 de 3); o máximo de dias seguidos
  (preferência) fica oculto no 12×36, como o campo rígido.
- **opB-e:** "todas as suaves no Essencial" inclui as duas preferências; o veredito e o menor
  quadro continuam iguais aos do padrão.
- **pref-tela (novo):** na tela padrão (12×36), "Máximo de turnos no período" aparece com
  importância "Não considerar" e o campo de limite tem como máximo o teto legal de turnos do
  contrato; o valor padrão (18) é rebaixado ao teto se passar dele; a linha de dias seguidos
  (preferência) não aparece.

Qualquer outra diferença na suíte é falha.

---

## Acréscimo a posteriori (21/10, depois de rodar o (c)) — o esperado de 56 estava errado

**O que deu:** (c1) e (c2) com **96** violações da preferência de dias seguidos, provado; contagem
do script = resultado por critério (96 = 96); (c2) turnos 14 = 14, como esperado.

**Por que o 56 estava errado:** a conta ignorou a cobertura. Com sequências 5, 5, 5, 5, 4 as
folgas de cada pessoa só podem cair nos dias 4, 5, 10, 11, 16, 17, 22 e 23 (contando do 0), mas a
demanda (12 de 14 por dia) exige **2 folgas em todos os 28 dias**. O 56 é inatingível.

**A conta certa (limite inferior, feita depois de ver o resultado):** a violação é uma janela de
5 dias seguidos toda trabalhada (é a expressão do modelo). Cada pessoa tem 24 janelas: 14 × 24 =
336. Uma folga no dia d quebra no máximo w(d) janelas da pessoa, w = 1, 2, 3, 4, 5, …, 5, 4, 3, 2,
1 (soma nos 28 dias = 120). Com exatamente 2 folgas por dia, no máximo 2 × 120 = 240 janelas
quebradas: **violações ≥ 336 − 240 = 96**, com igualdade se ninguém tiver duas folgas na mesma
janela. O solver achou e provou 96. O teste (c) passa a esperar 96 — conta registrada **depois**
do resultado, então vale como conferência da coerência, não como previsão.

**Ajuste do teste pref-tela (sem mudar o esperado):** na tela vazia a instância não monta e não
há teto legal; o teste preenche a equipe (4 + 8) antes de conferir o campo.

---

## Acréscimo a posteriori (21/10, suíte da v1.4.2 parada em tela_opB-c) — não previsto antes

O teste opB-c ("plano com as suaves no Desejável") exigia 11 critérios no bloco Desejável. Com as
duas preferências novas, "todas as suaves" passa a ter 13. **Este esperado não previu isso** (a
decisão 6 listou opB-d, opB-tela e opB-e, e esqueceu o opB-c).

Conferido pelo código, comparando o plano da v1.4.1 (worktree `..\tcc-nrp-v141`) com o novo, na
mesma entrada (demonstração, 30 pessoas, 28 dias): bloco 1 idêntico (Essencial + Importante,
pedido 286, enfermeiro em posto de técnico 1, máximo 2.001); no bloco Desejável, os 11 critérios
antigos com o mesmo coeficiente, o mesmo limite e o mesmo máximo; **a única diferença são
`max_dias_seguidos` e `max_turnos`**. Máximo do bloco: 5.010 (v1.4.1) + 690 (dias: 30 × (28 − 5)) +
420 (turnos: 30 × (28 − 14), o 18 rebaixado ao teto legal de 14) = **6.120**. O teste passa a
conferir 13 critérios, os dois novos presentes e o máximo 6.120. O resto do opB-c já tinha passado
na suíte (2 blocos; escala entregue e descanso cumprido; Essencial + Importante = 24, provado).

Os outros testes ainda não rodados na suíte foram conferidos: só o opB-e usa "todas as suaves", e
confere veredito e escala, não o plano (passou com o código novo antes da suíte, assim como o
opB-tela); os demais não usam a classificação, e as rodadas a2 usam a padrão.
