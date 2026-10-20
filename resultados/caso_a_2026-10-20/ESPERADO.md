# Caso A (Massens 2019, Clínica Ortovascular) — esperado, ANTES de qualquer rodada (20/10)

Entrada: `entrada.py` nesta pasta (fase 1; as rodadas são da fase 2, depois da suíte e da tag
v1.4.0). Duas rodadas, classificação padrão, orçamento 60 min: **turno fixo** ("Só este turno",
Essencial) e **rodízio livre** (sem linhas).

## Conta à mão — a segunda-feira depois do fim de semana com plantão de 12 h

Regra usada (a mesma do modelo — ver "premissa compartilhada"): depois de turno de 12 h ou mais,
36 h de descanso. Logo: quem trabalha no **domingo** (D12 ou N, ambos de 12 h) não trabalha na
segunda; quem faz **N no sábado** (termina domingo 7h) só pode fazer **N** na segunda (M, T e D12
da segunda ficam a 24 h, 24 h e 30 h); quem faz D12 no sábado pode fazer M na segunda (36 h
exatas).

| | Técnicos | Enfermeiros | Total |
|---|---:|---:|---:|
| Segunda: postos M + T + N | 5 + 5 + 4 = 14 | 1 + 1 + 1 = 3 | **17** |
| Domingo: D12 + N (bloqueia a segunda inteira) | 5 + 4 = 9 | 1 + 1 = 2 | **11** |
| Sábado N (só pode a N da segunda) | 4 | 1 | 5 |

- Conta do pedido: **17 + 11 = 28 > 24**.
- Mesma conta, separando o sábado: domingo 11 + sábado N 5 (que cobrem a N da segunda, 5) +
  M e T da segunda 12 = **28**. O sábado não muda o total, porque quem fez N no sábado cobre
  exatamente a N da segunda.
- **Enfermeiros sozinhos** (técnico não cobre posto de enfermeiro): domingo 2 + segunda 3 =
  **5 > 4**. O caso não fecha nem na categoria: falta ao menos 1 enfermeiro.
- **Férias (leitura adotada: 05–19/01 e 15–29/01):** no fim de semana de 16–18/01 as duas pessoas
  de férias estão fora; a conta exige 28 pessoas **disponíveis** nesses três dias → quadro ≥
  **30**. No de 09–11/01 só uma está fora → ≥ 29. O piso do caso A com estas férias é **30**.
- **Carga (44 h):** não aperta. Horas demandadas: dia útil 132 h/dia × 20 + fim de semana
  132 h/dia × 8 = 3.696 h; 24 pessoas × 176 h = 4.224 h, menos ~189 h de férias.

**Esperado:** não fecha com 24; menor quadro **≥ 28** (pedido da Orientação); com as férias
desta entrada, **≥ 30**. Nas duas rodadas o mesmo veredito: as linhas da rodada 1 são Essencial
mas não rígidas (Parte 2, teste 6).

## Conferência contra a Parte 3

Parte 3 (só técnicos, sem férias): segunda 14 + domingo 9 = **23**, e a ferramenta deu **23**
(22 inviável provado). A conta é a mesma; o caso A acrescenta os enfermeiros (3 + 2) e as férias.

## O que a ferramenta vai fazer (lido no código, sem rodar)

- O piso dela (`ferramenta.piso`) dá **18**: horas e janela de 7 dias (L = 6). **Não vê** a conta
  da segunda-feira; cada quadro de 24 até o mínimo precisa ser provado inviável **pelo solver**,
  dentro do orçamento de 60 min (até 6 provas: 24 a 29).
- Os acréscimos entram primeiro como **enfermeiros**, até a proporção do grau (33% no
  intermediário; `ferramenta.equipe`) — o menor quadro viável deve vir com mais enfermeiros e
  com enfermeiro em posto de técnico. As pessoas acrescentadas não têm linha na rodada 1 nem
  férias.
- Diagnóstico de 24: a alternância (`motivos_da_trava`) só é testada quando todos os turnos são de
  12 h; aqui não. Esperado: motivo **"combinação"** (nenhuma conta simples), com "O solver
  provou…", porque o 24 não cai no piso.
- Se o orçamento acabar antes de provar, a tela diz "O quadro informado é insuficiente; o menor
  quadro viável não foi determinado em 60 min" — resultado possível, não defeito.

## Premissa compartilhada

A regra das 36 h depois de turno ≥ 12 h entra **nos dois lados**: na conta à mão e no modelo
(`instancia_br.descanso_exigido`, usada por `pares_proibidos_por_horario`), e também na
conferência de descanso (`docs/conferencia_descanso_escala.py` importa as mesmas constantes). A
conta confere a aritmética da segunda-feira, **não** a leitura legal da regra.
