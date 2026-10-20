# Relatório de 20/10/2026 (b) — fase 1 do caso A e ajuste de texto

Sem solver e sem a suíte. Esperado registrado e commitado antes de cada etapa; commit depois de
cada uma; sem push.

## A) Ajuste de texto (item 7 das leituras adotadas)

Feito (esperado `cf84428`, ajuste `cf1d893`; `resultados/texto_piso_2026-10-20/`).
Quando o quadro informado é recusado pelo **piso** e nenhuma conta simples explica, o diagnóstico
diz agora "A conta prévia do menor quadro provou, sem o solver, que as regras juntas… não admitem
escala com este quadro"; quando foi o solver, a frase de antes, idêntica byte a byte. Só a frase:
`diagnosticar(inst, por_conta)` e, em `verificar`, `por_conta = (primeira tentativa == "piso")`,
informação que já existia. Entrada do solver: **243/243** idêntica à v1.3.0. Nenhum teste
conferia a frase; o `max-dias` ganhou duas conferências (registrado no DECISOES, "2026-10-20 —
Diagnóstico 'combinação': a frase diz quem provou"). Conferido aqui **sem solver**
(`verificar(margem=0)`, o 14 cai no piso): OK. O `max-dias` completo roda na suíte.

## B) Diagnóstico (só leitura; DECISOES.md e código)

**a) De onde vem "36 h depois de turno de 12 h".**
- Código: `src/instancia_br.py`, linhas 123–132 — `POS_TURNO_LONGO = 36` (comentário "art.
  59-A: doze horas seguidas por trinta e seis de descanso"), `TURNO_LONGO = 12` e
  `descanso_exigido(duracao_h)`: 36 h se a duração ≥ 12 h, 11 h (art. 66) nos demais.
  `pares_proibidos_por_horario` chama `descanso_exigido` para cada turno, pela **duração**, sem
  olhar o regime.
- DECISOES: o motivo registrado da regra pela duração é **"2026-09-29 — Redesenho da
  ferramenta"** (linha ~1156): "para cada par de turnos, o descanso medido no relógio é
  proibido abaixo de 11 h (art. 66), e abaixo de 36 h depois de turno de 12 h ou mais (art.
  59-A)". Antes, no escopo de regimes: "2026-09-08 — 12×36 modelado como MaxConsecutiveWorkingDays
  = 1" e "2026-09-21 — Definição de viável, e limites legais como rígidos" (36 h no 12×36, art.
  59-A: "doze horas seguidas por trinta e seis horas ininterruptas de descanso").
- Base legal que consta: **CLT, art. 59-A**.
- **Para o D12 especificamente — um plantão de 12 h isolado, dentro de um regime de 6 h — não há
  motivo registrado.** As entradas tratam do 12×36 (o regime do art. 59-A) e, em 29/09, estendem
  a regra a "turno de 12 h ou mais" sem discutir turno de 12 h fora do regime 12×36. Não há
  entrada que diga se o art. 59-A se aplica a um plantão de 12 h avulso no fim de semana.

**b) O descanso é editável sem mexer em código?** **Não.** 36 h, 12 h e 11 h são constantes de
`instancia_br.py`; não estão na tela, na `Entrada` nem nos parâmetros de `construir`. O único
parâmetro, `descanso_clt` (e `--sem-descanso-clt`), desliga só a regra das 11 h (`interjornada`)
— a das 36 h continua — e a `Entrada` da ferramenta nem o expõe (`montar` usa o padrão). Pela tela,
o que muda o descanso é o **horário**: um turno de menos de 12 h (ex.: 7–18) cai na regra das
11 h.

**c) O que a ferramenta entrega com quadro abaixo do mínimo.** `verificar` tenta o informado e
depois +1, +2 … até `MARGEM` = 12 acima (cada quadro: primeiro a composição da regra de
`equipe`, que acrescenta enfermeiros até a proporção do grau; se inviável, todos os acréscimos
como enfermeiros). Quadro abaixo do piso aritmético é recusado sem solver ("piso").
- Achou: **"Falta(m) N; o menor quadro viável é X. Escala gerada."**, com a escala do quadro X
  (os acrescentados aparecem como "Enf k"/"Téc k") e, se o informado foi provado inviável (conta
  ou solver), o quadro "Por que não há escala legal com {informado}" (diagnóstico).
- Toda a faixa provada inviável: "Não há escala legal até {informado + 12} profissionais; o
  menor quadro viável está acima disso."
- Tempo ou orçamento acabou sem decidir: nunca "faltam N" (só com prova); "O quadro informado é
  insuficiente; o menor quadro viável não foi determinado em …" (se o informado foi provado
  inviável) ou "Sem resposta em … com X profissionais…".

## C) Entradas

`resultados/caso_a_2026-10-20/entrada.py` (rodadas `turno_fixo` e `rodizio_livre`) e
`resultados/caso_b_2026-10-20/entrada.py`. Conferidas com `ferramenta.montar` (sem solver): A com
24 pessoas, 30 dias-pessoa de férias, 1.316 pedidos de turno gerados pelas linhas da rodada 1 e
nenhum na 2; B com 89.

## D) Esperado (commitado antes: `1688d4d`)

| | Conta do pedido | Com sábado e categorias | Férias | Esperado |
|---|---|---|---|---|
| Caso A | 17 + 11 = **28** > 24 | igual (o sábado N cobre a N da segunda); **enfermeiros 2 + 3 = 5 > 4** | 05–19/01 e 15–29/01: fim de semana de 16–18/01 sem as duas → **≥ 30** | não fecha com 24; ≥ 28 (≥ 30 com estas férias) |
| Caso B | 65 + 40 = **105** > 89 | igual; enfermeiros 14 ≤ 15 (faltam técnicos) | nenhuma | não fecha com 89; ≥ 105 |
| Parte 3 | 14 + 9 = 23 | — | — | a ferramenta deu **23** (22 provado inviável): a conta bate |

O que muda em relação à conta do pedido: **sábado** — não muda o total; **carga 44 h** — não
aperta em nenhum dos dois; **férias** — no caso A sobem o piso para 30; **enfermeiros** — no caso
A a categoria sozinha não fecha (5 > 4).

**Dois avisos para a fase 2 (lidos no código):**
1. O piso da ferramenta não vê a conta da segunda-feira (dá 18 no A e 68 no B): cada quadro
   abaixo do mínimo precisa ser provado inviável pelo solver, dentro dos 60 min.
2. **Caso B: a busca vai só até 89 + 12 = 101 < 105.** O veredito melhor possível é "Não há
   escala legal até 101"; o provável, pelo porte, é o orçamento acabar antes. O caso B como está
   não mede o menor quadro.

**Premissa compartilhada:** a regra das 36 h entra na conta à mão, no modelo e na conferência de
descanso (mesmas constantes de `instancia_br`). A conta confere a aritmética, não a regra.

## Leituras adotadas

1. Ids dos 18 técnicos das equipes não foram passados: nomes provisórios por equipe ("Manhã 1"…
   "Noite B 4"); trocar pelo id do Anexo B não muda o modelo.
2. 6089 é técnico, sem linha (pedido); 4309 é o volante noturno, "Só este turno" Noite.
3. Férias: dia 5 e dia 15 lidos como **datas do mês** (05/01 e 15/01/2027); duração de **15 dias**
   para as duas (cenário 2 de Massens: tarde 15; noite A 15); a pessoa da noite é da equipe A.
4. Enfermeiros no fim de semana: D12 1 e N 1 (pedido; a ficha diz "provável").
5. Na rodada 1, as pessoas acrescentadas pela busca do menor quadro não têm linha nem férias.

Nada enviado ao GitHub. Nenhuma rodada feita; nenhuma sensibilidade nova proposta.
