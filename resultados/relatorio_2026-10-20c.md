# Relatório de 20/10/2026 (c) — sessão da tarde: Partes 0, 1 e 7 a 11

Pedido da Orientação consolidado (20/10, tarde). Sem push. Esperado registrado e commitado antes
de implementar; um commit por parte. Nenhum solver pesado nesta sessão: só as contas sem solver,
o sorteio pequeno (40 instâncias, 54 s) e uma instância mínima para testar a conferência no
avaliador. Tempo é limite operacional, nunca resultado.

Versão citável: **v1.4.0** (tag criada e enviada pelo Otávio; não se mexe).

## Parte 0 — Fim de linha

`git status` no início da sessão: **limpo** (nenhum arquivo modificado; o `PASSAGEM.md` e os 13
arquivos de `resultados/pedidos_2026-10-20/avaliador/` não aparecem). Não houve o que descartar
— nada foi executado com `git checkout --`.

`docs/diagnostico/pedidos_avaliador.py` **regrava em CRLF**: os `teste4.md`/`teste5.md` saem de
`Path.write_text` em modo texto, que no Windows troca `\n` por `\r\n`; os `_avaliador.txt`, pelo
mesmo `write_text` em `src/validar.py` (linha 104). No índice estão em LF
(`git ls-files --eol`: `i/lf w/crlf`), e com `core.autocrlf=true` o Git não os vê como
modificados. Só registrado; nada mudado.

## Parte 1 — DECISOES: fundamento das 36 h (`96e2417`)

Entrada "2026-10-20 — a posteriori: fundamento das 36 h para qualquer plantão de 12 h ou mais":
art. 59 (8 h + 2 extras) e art. 59-A (12 h como exceção, por acordo individual escrito ou
convenção/acordo coletivo, vinculada a 36 h de descanso) → a regra pela duração (≥ 12 h), sem
olhar se o turno é noturno, segue esse desenho. Declarado: (a) justificativa nova, não o motivo
de 29/09; (b) a convenção coletiva do hospital do caso não foi lida; (c) o texto nunca afirma que
o hospital descumpre a lei — "a regra, como modelada, segue o art. 59-A". Sem código.

## Parte 7 — Piso por pares de dias (v1.4.1)

Esperado: `resultados/piso_pares_2026-10-20/ESPERADO.md` (`946e38c`, antes do código).

### A regra, como implementada

Para cada par de dias seguidos (d, d+1): postos de d+1 (todos os turnos) + postos de d em turnos
que **bloqueiam d+1 inteiro** ≤ pessoas disponíveis em pelo menos um dos dois dias (férias e
licenças descontadas). Também só com os postos de enfermeiro e os enfermeiros.

- `ferramenta.bloqueiam_o_dia_seguinte(inst)`: o turno t bloqueia se `(t, 1, u)` está nos pares
  do gerador para **todo** turno u (`pares_proibidos_por_horario(..., descartar=False)`, que lê
  `descanso_exigido`, inclusive `DESCANSO_POR_TURNO`); com o limite efetivo 1, todos. Nunca
  "duração ≥ 12 h" fixo. Conferido: na regra do produto bloqueiam D12 e N; com D12 = 11 h, só N.
- `ferramenta.pares_de_dias(inst, so_enfermeiros)`: o pior par (excesso, dias, as duas parcelas,
  disponíveis, turnos que bloqueiam).
- `ferramenta.piso`: mais um termo no `max` — informado + maior excesso (total ou enfermeiros),
  **só quando o excesso é positivo** (sem excesso o piso fica exatamente o de antes). Quem a
  varredura acrescenta não tem férias e entra nos dois dias; a 2ª composição põe todos os
  acréscimos como enfermeiros, então o excesso de enfermeiros também se traduz em quadro.
- Diagnóstico (`motivos_da_trava`): quando o limite efetivo não é 1 (a "alternância" fica como
  estava), motivo novo **`pares`** ("Dois dias seguidos") ou, só enfermeiros, `categoria` (como
  a alternância de enfermeiros já fazia). Texto do caso A, 36 h:

  > A conta prévia do menor quadro provou, sem o solver, que este quadro não tem escala legal.
  > dom 17/01 e seg 18/01: 17 postos na segunda + 11 no domingo em turnos que impedem a segunda
  > (N, D12: depois deles, o descanso exigido não deixa trabalhar no dia seguinte); são 28 pessoas
  > diferentes, e, descontadas férias e licenças, 22 pessoas estão disponíveis em pelo menos um
  > dos dois dias. Pela conta, faltam pelo menos 6 pessoas.

**Quem cobre o quê (lido no código).** Posto de técnico = turno-base, habilidade "Enfermagem";
posto de enfermeiro = variante "E", habilidade de enfermeiro (`instancia_br.demanda_por_turno`).
Enfermeiro tem as duas habilidades; técnico só a base (`instancia_br._equipe`). A ferramenta
resolve com `habilidade_rigida=True` (`experimento_a.modelo_br`), e o critério "habilidade
alternativa" (`alternative_skill_category`) só entra no modelo com habilidade **não** rígida
(`modelo.py`, `if r.ativa and not habilidade_rigida`). Logo: **técnico nunca cobre posto de
enfermeiro, em nenhuma classificação da opção B; enfermeiro cobre os dois.** Por isso há conta
só de enfermeiros e não há conta só de técnicos.

### Testes (entram na suíte da v1.4.1; saída em `resultados/piso_pares_2026-10-20/`)

1. **Segurança** (`piso_pares.py --seguranca`, sem solver): **224 rodadas registradas** —
   P01–P18 (bateria da suíte v1.4.0), K1–K6 (07/10), demonstração 20/19/18 (v1.4.0), nível 3
   (100 casos, 08/10), propriedades (96 variantes, 08/10) e a Parte 3. **Nenhum quadro viável
   recusado.** Mudam piso ou motivos em 28; nas outras 196, piso e motivos iguais aos da v1.4.0.
   Em várias a conta nova bate exatamente o menor viável que o solver achou (N003: 14 → 20 = 20;
   N024: 12 → 16 = 16; N025: 11 → 16 = 16; N034: 14 → 17 = 17). Tabela: `seguranca.md`.
   Testes da tela (`--tela`, sem solver, entradas colhidas trocando o solver por gravadores): 34
   entradas; muda só uma — o último caso do 7.3 (12×36 só enfermeiros, 4, Enf 3 de licença),
   piso 4 → 5; o quadro 4, antes provado pelo solver, passa à conta; motivo e menor viável (5)
   iguais, e o 7.3 confere só motivo, trecho e menor viável. A regressão (INRC) não passa pelo
   `piso`. A identidade 243/243 contra a v1.4.0 roda na suíte (e no teste do script, abaixo).
2. **Sorteio pequeno** (`--sorteio`, com solver): semente **20261020**, **40 instâncias**; turnos
   M 7–13, T 13–19, N 19–7 (12 h) e, em 60%, D12 7–19; 7 a 14 dias; equipe informada de 1
   enfermeiro e 0 a 2 técnicos, subindo até achar escala; férias de um enfermeiro em metade. A
   busca usa o piso **antigo**, para não depender da conta testada; etapa 2 desligada; 60 s por
   resolução. **40 de 40 decididas; piso novo ≤ menor viável em todas; igual em 30.** 54 s no
   total (máquina do Otávio, HiGHS 1.15.1). Tabela: `sorteio.md`.
3. **Controle** (`--controle`): Parte 3 — 22: piso 23, dom 10/01 e seg 11/01, 14 + 9 > 22
   (recusa); 23: aceito. OK.
4. **Casos A e B sem solver** (`--casos`), iguais ao esperado:

   | Regra | Caso | Piso (antes → agora) | Pior par (total) | Enfermeiros | A conta recusa o informado? |
   |---|---|---|---|---|---|
   | 36 h | A (24) | 18 → **30** | dom 17/01–seg 18/01: 17 + 11 contra 22 | 3 + 2 contra 4 | sim; 24 a 29 pela conta, solver a partir de 30 |
   | 36 h | B (89) | 68 → **105** | dom 10/01–seg 11/01: 65 + 40 contra 89 | 10 + 4 contra 15 | sim; **toda a faixa até 101**: "Não há escala legal até 101 profissionais…", 13 tentativas, todas pela conta, sem solver |
   | D12 = 11 h* | A (24) | 18 | 17 + 5 contra 22 (excesso 0) | 3 + 1 contra 4 (0) | **não** |
   | D12 = 11 h* | B (89) | 68 | 65 + 19 contra 89 | 10 + 2 contra 15 | **não** |

   \* HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA. `DESCANSO_POR_TURNO` volta a `{}` ao
   fim (impresso).
5. **Premissa compartilhada (declarada):** a conta lê os pares do mesmo gerador que o modelo
   (`pares_proibidos_por_horario` / `descanso_exigido`). Confere a **aritmética** e a
   **coerência com o modelo**, não a leitura legal da regra das 36 h (nem a das 11 h).

**Mudanças esperadas na suíte da v1.4.1** (registradas antes de ela rodar): (a2) **P05**: a
tentativa (14, "inviavel", 4, 10) vira (14, "piso", None, None) — admitida em
`identidade_opcao_b_rodadas.ADMITIDAS`, só com `A2_PISO_PARES=1`; qualquer outra diferença
falha. demo18: o 28 também passa à conta, mas a comparação da demonstração não olha as
tentativas (frase, menor viável 29 e motivo "alternancia" iguais). Tela 7.3: acima. Nada mais.

### Item extra (só leitura) — condições necessárias que já existiam e o que o solver teve de provar

Condições necessárias aplicadas **antes** da Parte 7:

- `ferramenta.piso` (decide quais quadros vão ao solver):
  1. **Capacidade de horas**: horas demandadas ≤ soma dos tetos individuais (carga contratual ×
     dias disponíveis / 7); o que falta, em acréscimos de 44 h.
  2. **Janela de L + 1 dias** (`experimento_a.piso_de_alternancia`, com L = `limite_efetivo`):
     N ≥ ⌈demanda da janela / L⌉; com L = 1 (só turnos de 12 h), a soma de dois dias. **Sem
     férias.**
- `ferramenta.diagnosticar` / `motivos_da_trava` (só explicam o quadro informado, **depois** de
  recusado; não decidem nada):
  3. **Horas de enfermeiro**: horas de posto de enfermeiro ≤ tetos dos enfermeiros (com L = 1,
     teto = mín(contrato, 12 h × Σ⌈bloco/2⌉)).
  4. **Horas de técnico**: o que os técnicos não cobrem ≤ folga de horas dos enfermeiros.
  5. **Par de dias com L = 1** (alternância), **com férias**: total e só enfermeiros.
  6. **Dia específico**: por dia, pessoas e enfermeiros disponíveis ≥ postos.

  As contas 3 a 6 **não** estão no `piso`: quando disparam num quadro, quem o recusa é o solver
  (ex.: P05, 14 — a alternância com férias do diagnóstico já o explicava). Só leitura; nenhuma
  conta nova proposta ou implementada além da da Parte 7.

Quadros que o solver teve de provar inviáveis (sem conta prévia) nas rodadas registradas: **53**
(um quadro com uma composição inviável e a outra viável não conta). A conta da Parte 7 recusa
**34** deles; **19** continuam com o solver. Tempo: soma das composições do quadro, das linhas
de progresso (máquina do Otávio, HiGHS 1.15.1; 600 s por resolução nas rodadas de 07–08/10 e nas
a2) — limite operacional, não resultado.

| Fonte | Caso | Quadro | Solver (s) | Recusado pela conta nova? |
|---|---|---:|---:|---|
| bateria v1.4.0 | P05 | 14 | 0.8 | sim |
| demonstração v1.4.0 | demo18 | 28 | não registrado | sim |
| nível 3 (08/10) | N003 | 16 | 0.6 | sim |
| nível 3 (08/10) | N003 | 17 | 0.6 | sim |
| nível 3 (08/10) | N003 | 18 | 0.6 | sim |
| nível 3 (08/10) | N003 | 19 | 0.7 | sim |
| nível 3 (08/10) | N004 | 18 | 2.9 | sim |
| nível 3 (08/10) | N005 | 17 | 1.3 | não |
| nível 3 (08/10) | N010 | 14 | 1.7 | não |
| nível 3 (08/10) | N010 | 15 | 89.7 | não |
| nível 3 (08/10) | N012 | 14 | 1.1 | sim |
| nível 3 (08/10) | N012 | 15 | 0.8 | não |
| nível 3 (08/10) | N013 | 16 | 2.1 | sim |
| nível 3 (08/10) | N013 | 17 | 2.1 | sim |
| nível 3 (08/10) | N014 | 20 | 2.6 | sim |
| nível 3 (08/10) | N014 | 21 | 2.7 | sim |
| nível 3 (08/10) | N015 | 8 | 0.7 | não |
| nível 3 (08/10) | N016 | 18 | 0.9 | não |
| nível 3 (08/10) | N020 | 16 | 0.6 | sim |
| nível 3 (08/10) | N020 | 17 | 0.5 | sim |
| nível 3 (08/10) | N020 | 18 | 0.5 | não |
| nível 3 (08/10) | N020 | 19 | 0.7 | não |
| nível 3 (08/10) | N020 | 20 | 0.5 | não |
| nível 3 (08/10) | N023 | 14 | 1.8 | não |
| nível 3 (08/10) | N024 | 12 | 0.5 | sim |
| nível 3 (08/10) | N024 | 13 | 0.6 | sim |
| nível 3 (08/10) | N024 | 14 | 0.4 | sim |
| nível 3 (08/10) | N024 | 15 | 0.6 | sim |
| nível 3 (08/10) | N025 | 11 | 1.2 | sim |
| nível 3 (08/10) | N025 | 12 | 1.3 | sim |
| nível 3 (08/10) | N025 | 13 | 1.3 | sim |
| nível 3 (08/10) | N025 | 14 | 1.5 | sim |
| nível 3 (08/10) | N025 | 15 | 1.6 | sim |
| nível 3 (08/10) | N026 | 17 | 2.4 | sim |
| nível 3 (08/10) | N026 | 18 | 162.4 | não |
| nível 3 (08/10) | N027 | 13 | 0.7 | sim |
| nível 3 (08/10) | N029 | 11 | 0.6 | sim |
| nível 3 (08/10) | N029 | 12 | 16.7 | não |
| nível 3 (08/10) | N030 | 16 | 3.3 | sim |
| nível 3 (08/10) | N034 | 14 | 1.7 | sim |
| nível 3 (08/10) | N034 | 15 | 1.6 | sim |
| nível 3 (08/10) | N034 | 16 | 1.9 | sim |
| nível 3 (08/10) | N035 | 18 | 3.0 | não |
| nível 3 (08/10) | N052 | 12 | 0.6 | não |
| nível 3 (08/10) | N066 | 17 | 0.9 | não |
| nível 3 (08/10) | N067 | 18 | 36.4 | não |
| nível 3 (08/10) | N071 | 16 | 0.6 | não |
| nível 3 (08/10) | N074 | 10 | 3.3 | não |
| propriedades (08/10) | P05_mais_pessoa | 15 | não registrado | sim |
| propriedades (08/10) | P05_embaralhado | 14 | não registrado | sim |
| propriedades (08/10) | K3_mais_posto | 16 | não registrado | sim |
| propriedades (08/10) | K3_mais_ferias | 16 | não registrado | não |
| Parte 3 (20/10) | plantao12 | 22 | não registrado | sim |

## Parte 8 — Suíte da v1.4.1

`docs/diagnostico/fechar_v141.sh`: o conteúdo do `fechar_v140.sh` + os testes da Parte 7
(`piso_seguranca`, `piso_controle`, `piso_casos`, sem solver, logo depois da identidade;
`piso_sorteio` antes da regressão) + a a2 com `A2_PISO_PARES=1`. Identidade contra a **v1.4.0**,
no worktree `..\tcc-nrp-v140` (criado nesta sessão: `git worktree add ..\tcc-nrp-v140 v1.4.0`);
os scripts de identidade já estão commitados na v1.4.0, então nada é copiado para o worktree.
Saída em `resultados/v141_<data>/suite/`; `RETOMAR=1` retoma a pasta mais recente (ou a de
`V141_DATA`). Os worktrees v123 e v130 ficam.

Teste do script **sem solver** (`PULAR_SOLVER=1 V141_DATA=teste_script`): identidade **243/243 idênticos à v1.4.0**
(sem linhas e com os pedidos como linhas), controle positivo OK, `piso_seguranca` "TUDO OK:
nenhum quadro viável recusado", `piso_controle` OK, `piso_casos` OK, "TESTE DO SCRIPT OK";
com `RETOMAR=1`, pulou tudo. O worktree v1.4.0 continua limpo (`git status` vazio). A
comparação da a2 foi testada com um JSON simulado do P05 (tentativa 14 → "piso"): com
`A2_PISO_PARES=1`, "TUDO IGUAL"; sem, "DIFERENTES: tentativas". A pasta de teste foi apagada.
A suíte completa (com solver) é do Otávio.

## Parte 9 — Script da fase 2

`docs/diagnostico/rodar_fase2.sh` + `docs/diagnostico/fase2.py` (uma rodada por processo). Cinco
rodadas, na ordem: A36_livre, A36_fixo, A11_fixo, B11_livre, B36_livre; classificação padrão,
orçamento 60 min, 1.800 s por nível e na etapa 2. Saída em `resultados/fase2_<data>/`: por
rodada, `<nome>.json` (campos pedidos: versão e commit, frase e frase vigente, tentativas com
quadro/status/enfermeiros/técnicos/segundos/quem provou, menor viável, provado e gap,
diagnóstico, critérios, "Só este turno" descumpridas e de quem no turno fixo, menor descanso no
relógio depois de D12 e de N, alertas do COFEN, tempo total, conferência no avaliador),
`<nome>.txt`, `<nome>.log` e uma linha no `resumo.txt`.

- Memória: antes de cada rodada, `FreePhysicalMemory` do Windows; abaixo de 3 GB, "PARADO: menos
  de 3 GB livres".
- 11 h: arquivos `HIPOTESE_SENSIBILIDADE_<nome>.*`; a primeira linha do log e do `.txt` é
  "HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA"; o JSON começa pelo campo `aviso` com o
  mesmo texto; ao fim, `DESCANSO_POR_TURNO` volta a `{}` e o valor é impresso (no processo da
  rodada e num processo novo, no fim do script).
- "Não decidido" não é falha; PARADO só com erro de código ou de entrada (código de saída do
  `fase2.py`) ou memória.
- Conferência externa da cobertura: XML da instância (com os pedidos) e da escala, XSD e o
  avaliador oficial; registra "Hard constraints violation: sim/não"; recusa do XSD ou do
  avaliador fica registrada, sem contorno. Declarado no JSON: a conferência do descanso no
  relógio compartilha a premissa com o modelo.

Teste sem solver (`PULAR_SOLVER=1 FASE2_DATA=teste_script`): as cinco entradas montam (pisos
30, 30, 18, 68, 105; bloqueiam [D12, N] nas de 36 h e [N] nas de 11 h); `DESCANSO_POR_TURNO ao
fim: {}` em todas e num processo novo; "TESTE DO SCRIPT OK"; `RETOMAR=1` pulou as cinco; com o
limite de memória forçado (`MINIMO_GB=999`, só para o teste) saiu "PARADO: menos de 3 GB livres".
Conferência no avaliador testada numa instância mínima de 4 turnos com D12 (7 pessoas, 14 dias,
uma resolução de segundos): **XSD da instância e da escala sem erro; o avaliador aceitou;
"Hard constraints violation: não"**; menor descanso depois de D12 e de N: 36 h. A pasta
`resultados/fase2_teste_script/` foi apagada.

Os `ESPERADO.md` dos casos A e B ganharam a seção "Depois da Parte 7 (v1.4.1) — quem prova:
conta x solver": A começa em 30 (24 a 29 pela conta); B36 recusado pela conta até 101, em
segundos; sob 11 h a conta não recusa nem A (24) nem B (89).

## Parte 10 — MAPA_CODIGO.md

Seção nova "Acréscimos de 19–20/10": `src/prioridades.py`, o piso por pares em
`src/ferramenta.py`, `DESCANSO_POR_TURNO` em `src/instancia_br.py` e os scripts de
`docs/diagnostico/` de 19–20/10 e desta sessão.

## Parte 11 — PASSAGEM

Atualizado: versão citável v1.4.0; próxima tarefa do Otávio = suíte da v1.4.1 (com RETOMAR),
tag v1.4.1 e push, depois a fase 2; worktrees de leitura e o comando para removê-los;
sensibilidade com 2 ou 3 ordens sem proposta até a decisão do Otávio; congelamento em 25/10.
