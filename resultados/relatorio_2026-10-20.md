# Relatório da sessão de 19–20/10/2026 — 3º bloco

Pedido da Orientação (3º bloco, versão final), parcialmente sem supervisão (madrugada de 20/10);
a conexão caiu depois dos testes da Parte 4 e o trabalho foi retomado de manhã. Um commit por
parte, esperado commitado antes de cada teste.

**Estado: Partes 0 a 5 feitas; todos os testes rodados aqui passaram, com uma exceção de
esperado na Parte 3 (b), explicada abaixo. Tag `v1.4.0` NÃO criada: a suíte de fechamento
(`docs/diagnostico/fechar_v140.sh`) é do Otávio, com o Claude Code fechado.**

## Parte 0 — Tag v1.3.0

A suíte de fechamento da v1.3.0 terminou com "TUDO OK" (`a2_comparar`: "TUDO IGUAL"). Tag
`v1.3.0` criada no commit `6f6311f`. Versão citável: **v1.3.0** (PASSAGEM).

## Parte 1 — Registros no DECISOES.md

- "2026-10-19 — Opção B: decisões 4 e 5": decisão 5 aprovada (motivo: "2026-09-15 — Quinto alvo
  de validação", cobertura); decisão 4 substituída pela tela sem Situação; nota para o texto
  (com nível sem prova, a prioridade entre níveis só é garantida nos provados).
- "2026-10-19 — Pedidos e regras por profissional" (MUDANÇA DE FORMULAÇÃO; revê a entrada de
  09/10, que ficou marcada "REVISTA").
- "2026-10-19 — Máximo de dias seguidos como regra do hospital (rígida)".
- "2026-10-19 — Tela orientada ao usuário".

## Parte 2 — Pedidos e regras dos profissionais

Esperado e estimativa: `resultados/pedidos_2026-10-20/ESPERADO.md` (commit `9b88e25`);
implementação `801d675`.

- Tabela no grupo 1 de "Prioridades": Profissional | Dia | Turno | Tipo (Folga / Só este turno) |
  Importância. Tradução para `folga_dia` / `folga_turno` (os pedidos negativos validados do INRC),
  com o nível da linha em `Pedido.nivel`; uma violação por profissional-dia-turno, no nível mais
  alto; "Só este turno" da mesma pessoa e dia se somam. A linha "Pedido de folga no dia" saiu
  das Prioridades. A tela diz quantos pedidos foram descumpridos e de quem.
- **Unidade da folga no dia:** a de sempre, **profissional-dia trabalhado** (`folga_dia`, termo
  y[n, d]) — é o que preserva a identidade. Um dia com todos os turnos proibidos no mesmo nível
  vira um `folga_dia`; senão, um `folga_turno` por turno.

| Teste | Esperado | Resultado |
|---|---|---|
| 1a identidade, sem linhas | 243/243 × v1.3.0 | **243/243** |
| 1b identidade, pedidos como "Folga + dia, Essencial" | 243/243 × v1.3.0 | **243/243**; controle positivo (uma linha a mais muda o LP): ok |
| 2a/2b turno fixo, compatível / forçado | 0 / exatamente 4 | **0 / 4**, provados |
| 2c/2d "Folga + turno", compatível / forçado | 0 / exatamente 4 | **0 / 4**, provados |
| 3a mesma pessoa, Essencial × Desejável | Ess 0, Des 1; Téc 1 em T (invertida: em M) | **igual**, fundido e em sequência forçada |
| 3b três linhas na mesma célula | 1 violação, no Essencial | **1, no Essencial** |
| 4 avaliador oficial × modelo × avaliacao.py, 10 escalas | iguais por profissional | **iguais nas 10** (totais 4 a 9) |
| 5 DayOn/ShiftOn (só leitura) | XSD aceita; avaliador pontua 2 | XSD **aceita**; avaliador pontua **0** (abaixo) |
| 6 nunca trava | viável com 21 no Essencial; `_pequeno` admite 3 | **igual** |

**Premissa compartilhada no teste 4:** as quatro colunas recebem a mesma lista de pedidos gerada
pela tradução da tabela; o teste confere a pontuação dos pedidos e a escrita do XML, não a
tradução (conferida à mão nos testes 2 e 3). A coluna do modelo vem das expressões do próprio
modelo.

**Achado do teste 5 (avaliador oficial):** `DayOnRequests` e `ShiftOnRequests` são aceitos pelo
`docs/scheme_input.xsd` e lidos pelo avaliador (`SchedulingPeriodParser.parseDayOnRequests`),
mas **nunca pontuados**: em `RequestedDayOnCondition` e `RequestedShiftOnCondition` o limite é
`min_pert_nr = 0` (deveria ser 1 para "trabalhar ao menos uma vez"), então nenhuma escala viola;
o rótulo do DayOn ainda diz "Requested day off" (cópia do DayOff). Consequência: pedido
**positivo** não teria conferência externa — reforça a decisão de traduzir tudo para pedidos
negativos. Achado lateral: `instancia_br.escrever_xml` escreve `DayOfWeekCover` vazio para um dia
da semana sem demanda em nenhum turno, e o XSD recusa; não ocorre nos casos da ferramenta com
demanda em todo dia, não foi corrigido (só contornado no teste 5).

## Parte 3 — Plantão de 12 h no fim de semana (sem código)

Esperado `a46bb91`, resultado `bc63f76` (`resultados/plantao12_2026-10-20/`).

- (a) aceita o 4º turno D12 e a demanda 0: **sim**.
- **(b) DIFERENTE do esperado.** Esperado: "admite com 22". Saiu: o **22 é inviável (provado
  pelo solver)** e a escala legal sai com **23** ("Falta 1"). Conta à mão que explica sozinha:
  todo turno de domingo é de 12 h (D12 5 + N 4 = **9 pessoas**), e depois de turno de 12 h vêm
  36 h de descanso — **ninguém que trabalhou no domingo trabalha na segunda**; a segunda pede
  M 5 + T 5 + N 4 = **14**; com 22 sobram 22 − 9 = **13**. A conta de horas do esperado (3.024 h
  contra 3.872 h) não via a trava, que é de dias.
- (c) menor descanso depois de um D12: **36 h** exatas (sábado 19h → segunda 7h); nenhum abaixo.
- (d) conferência de descanso: **cumpre**. (e) D12 em dia útil: **0**.
- `pares_proibidos_por_horario` trata certo o D12 entre turnos de 6 h (lista = conta à mão).
- **Consequência para o caso A:** o quadro precisa cobrir a **segunda-feira depois do fim de
  semana com plantão de 12 h** — quem trabalhou no domingo em turno de 12 h não pode estar na
  segunda. O diagnóstico da tela não tem conta para isso (a da alternância só dispara quando
  todos os turnos são de 12 h); ao escolher o quadro do caso A, fazer esta conta antes.

## Parte 4 — Máximo de dias seguidos do hospital

Esperado `58ba676`, implementação `7efc54f`. Campo no grupo 2, "Obrigatória", 1 a 6 (7 é recusado),
oculto no 12×36; `min(hospital, CLT)` pelo `max_consecutivos` de `instancia_br`.

| Teste | Esperado | Resultado |
|---|---|---|
| identidade (padrão 6) | 243/243 × v1.3.0 | **243/243** |
| 7 | erro de entrada | **recusado** ("acima de 6 a lei não permite, art. 67") |
| com 6 (14 técnicos, M 6 + T 6) | admite 14 | **admite 14**; maior sequência 6 |
| com 4 | "Falta 1; o menor quadro viável é 15"; piso 15; ≤ 4 seguidos | **igual**; maior sequência 4 na escala e no relógio; 14 recusado pela conta |

## Parte 5 — Limpeza da tela

Esperado `ca3690c`; implementação `0bca4c0`; testes `0679462`, `2fc4767`; GUIA `9ced99c`.
Numeração 1–5 (o COFEN sem número, no mesmo lugar); turnos "Manhã/Tarde/Noite" e "Dia/Noite" na
tela, com os códigos M/T/N/D inalterados; graus com a proporção de enfermeiros; "(fim de
semana)"; sem a coluna Situação; sem as linhas da CLT; três critérios ocultos no 12×36; uma linha
de descrição por critério e o texto longo no "?"; limites presos pela lei.

| Teste | Resultado |
|---|---|
| identidade × v1.3.0 | **243/243** |
| tela-limpa (novo) | **OK** — inclusive caso 5 pela tela = pelo back end, códigos M/T/N |
| opB-tela (esperado atualizado, registrado no DECISOES) | **OK** |
| 16, 4b, 7.4, 9c-tela | **OK** sem mudança |

## Testes atualizados (texto da tela removido), todos registrados no DECISOES

- opB-tela, Parte 2: grupo 1 "1 de 1"; aviso de mesmo nível provocado por outro critério.
- opB-tela, Parte 4: duas linhas cinza; campo oculto no 12×36.
- opB-tela, Parte 5: "0 de 2", "0 de 3"; nenhuma linha cinza.

## Leituras adotadas

1. Nível da linha guardado em `Pedido.nivel` (campo opcional; o modelo não lê; o XML não muda).
2. "Só este turno" de várias linhas da mesma pessoa e dia: permitidos = união; nível da proibição =
   o mais alto entre essas linhas.
3. Enfermeiro: o turno u da tabela vale pelo posto de técnico e pelo de enfermeiro (u e uE); uma
   violação por dia, porque ninguém faz dois turnos no mesmo dia.
4. Pedidos do caminho antigo (`Entrada.pedidos`) e linhas da tabela não são deduplicados entre
   si (a tela só usa a tabela; o caminho antigo fica para código e testes).
5. A linha "Pedido de folga no dia" continua no resultado por critério (0 quando só há a tabela
   nova), para não mudar o que a v1.3.0 mostrava.
6. Parte 3: demanda de **enfermeiros 0** em todos os turnos (o pedido só dava técnicos).
7. Parte 4: não há mensagem de diagnóstico própria para máximo entre 2 e 5; o piso e o limite
   efetivo usam o valor do hospital. O texto "combinação de regras" diz "O solver provou…" mesmo
   quando quem provou foi o piso — imprecisão que já existia no padrão; não corrigida.
8. Parte 5: critério oculto no 12×36 vale como "Não considerar", mesmo se escolhido antes.
9. Parte 5: rótulo → código por mapa fixo (Manhã→M, Tarde→T, Noite→N, Dia→D); outro nome é o
   próprio código.

## O que falta

- **Suíte de fechamento da v1.4.0** (Otávio, com o Claude Code fechado; comando no PASSAGEM). Ela
  roda também o que não rodou aqui depois da Parte 5: 9b-sem-teto, 3, 4, 5, 15, 7.1, 7.2, 8, 12, 1-2, 9, 7.3,
  opB-b/c/d/e/padroes, ped-*, max-dias, o avaliador dos pedidos e o (a2). Se "TUDO OK": tag
  `v1.4.0`.
- `MAPA_CODIGO.md` não foi atualizado com os arquivos de 19–20/10 (`src/prioridades.py` e os
  scripts de `docs/diagnostico/`).
- Nada enviado ao GitHub.
- Tempo é limite operacional, não resultado.
