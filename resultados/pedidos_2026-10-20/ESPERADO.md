# Parte 2 (3º bloco, 20/10) — Pedidos e regras dos profissionais: estimativa e esperado

Registrado e commitado **antes** de implementar. Decisão: `DECISOES.md`, "2026-10-19 — Pedidos e
regras por profissional". Ponto de parada: 21/10 (se não estiver tudo verde, para, registra e
fica como limitação declarada).

## Estimativa (esforço real)

| Peça | O que é | Esforço |
|---|---|---|
| Tradução | `prioridades`: linha → pedidos negativos (`folga_dia` / `folga_turno`), uma violação por profissional-dia-turno no nível mais alto | ~1,5 h |
| Níveis | pedidos por nível no plano de blocos e na fusão; objetivo do bloco em sequência com só os pedidos do bloco | ~1,5 h |
| Tela | tabela "Pedidos e regras dos profissionais" no lugar da de pedidos; sai a linha "Pedido de folga no dia" das Prioridades; pedidos descumpridos por pessoa no resultado | ~1,5 h |
| Testes 1–6 | identidade (LP), contas pequenas, avaliador oficial | ~3 h, rodadas curtas (casos de 7 dias) |

Total ~7–8 h de trabalho. Rodadas: casos pequenos (segundos); identidade sem solver (~2 min por
árvore).

## Decisões de implementação (registradas antes)

1. **Onde fica o nível.** `instancia.Pedido` ganha o campo opcional `nivel` (padrão `None`). O
   modelo não o lê; o XML não muda. `None` = pedido do caminho antigo (`Entrada.pedidos`, lista de
   (nome, data)), com o nível da classificação `pedido_folga` (padrão Essencial), como na v1.3.0.
   As linhas da tabela nova vão em `Entrada.regras` e saem com `nivel` preenchido.
2. **Tradução, por profissional n e dia d**, sobre os turnos da tela (u):
   - nível de (n, d, u) = o mais alto entre as linhas que proíbem u em d;
   - "Só este turno": por (n, d), o conjunto permitido é a união dos turnos das linhas "Só este
     turno" que valem em d (com o dia d ou sem dia); o nível da proibição é o mais alto entre
     essas linhas (leitura adotada);
   - se **todos** os turnos de d ficam proibidos **no mesmo nível**, sai **um** `folga_dia` (a
     unidade de hoje: profissional-dia trabalhado — é o que preserva a identidade); senão, um
     `folga_turno` por turno proibido, com o seu nível. Para enfermeiro, o turno u vira os dois
     postos (u e uE, o de enfermeiro), e como ninguém faz dois turnos no mesmo dia continua uma
     violação por profissional-dia-turno.
   - `folga_dia` sai na ordem da primeira linha que o gerou (com só "Folga + dia", a ordem da
     tabela — a mesma do caminho antigo).
3. **Máximo de violações de um nível** = número de `folga_dia` do nível + número de pares
   (profissional, dia) com algum `folga_turno` do nível.
4. **Objetivo de um bloco em sequência** = parcelas das famílias do bloco, e, para pedidos, só os
   pedidos dos níveis do bloco (soma de peso × y ou peso × x). Sem linhas novas, igual ao de hoje.
5. **Validação da linha:** sem dia e sem turno → inválida; "Só este turno" sem turno → inválida;
   profissional, turno e dia têm de existir no horizonte. Importância em branco → padrão (Folga
   com dia e sem turno: Essencial; demais: Desejável).

## Testes e esperado

### 1. Identidade (sem solver; LP com `symbolic_solver_labels`)
- **1a.** Sem linhas novas → os 243 arquivos (81 casos × XML, LP etapa 1, LP etapa 2) idênticos
  aos da **v1.3.0** (worktree `../tcc-nrp-v130`). Esperado: **243 de 243**.
- **1b.** Os mesmos casos com os pedidos de folga passados como linhas "Folga + dia, Essencial"
  da tabela nova (`Entrada.regras`) → idênticos aos da v1.3.0 com os pedidos no caminho antigo.
  Esperado: **243 de 243**.
- Controle positivo: uma linha "Folga + turno" a mais muda o LP da etapa 1. Esperado: muda.

### 2. Conta (modelo 8 h: M 7–15, T 15–23, N 23–7; 7 dias a partir de uma segunda; 0 enfermeiros
e 6 técnicos A–F; carga 44 h → no máximo 5 turnos de 8 h por pessoa no período)
- **2a. Turno fixo compatível.** Demanda de técnicos M 1, T 1, N 1 por dia. Linhas "Só este
  turno" (Desejável, sem dia): A, B → M; C, D → T; E, F → N. Cada equipe de 2 cobre os 7 turnos
  do seu horário (capacidade 10). Esperado: **0 violações**.
- **2b. Turno fixo que força trocas.** Demanda M 2, T 1, N 1. Manhãs = 14; A e B fazem no máximo
  10 → pelo menos **k = 4** manhãs com outra equipe. Atingível (conta à mão): A M d1–d5; B M
  d3–d7; C T d1–d4 e M d7; D T d5–d7; E M d1, M d2, N d5–d7; F N d1–d4 e M d6 (todas as
  sequências respeitam 11 h, 36 h e a folga isolada de 24 h; ninguém passa de 5 turnos).
  Esperado: mínimo **exatamente 4**.
- **2c. "Folga + turno" compatível.** Demanda M 1, T 1, N 1; linhas "Folga, turno N" (Desejável)
  para A, B, C, D. E e F cobrem as 7 noites (capacidade 10). Esperado: **0**.
- **2d. "Folga + turno" que força.** Demanda M 1, T 1, N 2: noites = 14, E e F fazem no máximo
  10 → **k = 4**. Atingível: E N d1–d5; F N d3–d7; A N d1, N d2, M d4–d6; B M d1–d3, N d6, N d7;
  C T d1–d4 e M d7; D T d5–d7. Esperado: mínimo **exatamente 4**.

### 3. Níveis por linha (7 dias, 8 h)
- **3a. Mesma pessoa, Essencial × Desejável em conflito.** 2 técnicos; demanda só no d1: M 1,
  T 1 (os demais dias zero). Téc 1: L1 "Folga, d1, turno M" (Essencial) e L2 "Só este turno M,
  d1" (Desejável). As duas pessoas trabalham no d1; Téc 1 faz M (viola L1) ou T (viola L2).
  Esperado: **Essencial 0, Desejável 1, Téc 1 em T no d1**. Invertendo os níveis (L1 Desejável,
  L2 Essencial): **Essencial 0, Desejável 1, Téc 1 em M no d1**.
- **3b. Mesmo profissional-dia-turno proibido por três linhas.** 1 técnico; demanda só no d1:
  M 1. Linhas: "Folga, d1" (Desejável), "Folga, d1, turno M" (Essencial), "Folga, turno M"
  (Desejável). Ele precisa trabalhar M no d1. Esperado: **uma** violação, no **Essencial**;
  Desejável 0 (não 3 violações).

### 4. Validação externa (avaliador oficial)
Instância XML sintética do caso 2b (formato INRC, `DayOffRequests`/`ShiftOffRequests` gerados
pela tabela, peso 1; acrescento uma "Folga, d2" de A e uma "Folga, d4, turno T" de C, para os
dois tipos aparecerem). Escalas: a da ferramenta e 9 perturbadas (trocas que preservam a
cobertura) = **10**. Esperado: penalidade de pedidos por profissional, avaliador = modelo =
`avaliacao.py`, nas 10; o total dos pedidos do avaliador = soma das violações contadas pelo
resultado por critério. **Premissa compartilhada:** a tradução tabela → pedidos é a mesma para
os três (o avaliador recebe os pedidos que o código gerou); o teste confere a **pontuação** dos
pedidos e a escrita do XML, não a tradução — a tradução é conferida pelas contas à mão (2 e 3).

### 5. Só leitura: `DayOnRequests` / `ShiftOnRequests`
- O `docs/scheme_input.xsd` declara os dois (lido: linhas 21 e 23; tipos nas 200 e 227).
  Esperado: instância sintética com eles **valida** no XSD.
- Instância: 1 técnico, 7 dias, turnos M/T/N, sem demanda; DayOn em d1 (peso 1) e ShiftOn M em
  d2 (peso 1); escala: T no d2 e nada mais. Esperado do avaliador: "Requested day on" 1 e
  "Requested shift on" 1 → **2** pelos pedidos (além do que as regras do contrato pontuarem).
  Nada vai à tela.

### 6. Pedidos nunca tornam impossível uma escala que a CLT admite
- Caso 2a com linhas "Folga" (Essencial) para os 6 profissionais em todos os turnos (sem dia):
  esperado **viável**, com **21** violações no Essencial (cada um dos 21 turnos demandados viola
  uma linha).
- `_pequeno` (12×36, 1 + 2) pelo `verificar`, com "Folga" Essencial em todos os turnos para os
  3: esperado **admite 3**, como sem linhas.
