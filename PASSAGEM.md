# PASSAGEM — Orientação (ferramenta)

Atualizado em 30/10/2026. Lido primeiro pelo chat de Orientação; atualizado pelo Claude Code ao
fim de cada sessão (dele ou do chat).

## Onde paramos

- **v1.4.5 (30/10) — etapa 2 por min-max, no branch `v1.4.5-minmax`, AINDA SEM MERGE NEM TAG**
  (esperam o ok do Otávio). Pedido do Prof. Ormeu; registro em `DECISOES.md`, "2026-10-30 — Etapa 2
  por min-max (v1.4.5)". A etapa 2 minimiza a **maior** amplitude entre as categorias (variável `t`,
  `t ≥ φmax_g − φmin_g`), sem desempate; a escolha entre etapa 1 e etapa 2 sem prova e a frase do
  equilíbrio passam a usar a maior das duas (`ferramenta.max_amplitude`). Suíte de fechamento
  (`docs/diagnostico/fechar_v145.sh`): **TUDO OK, 20 de 20 passos com código 0**
  (`resultados/v145_2026-10-30/suite/resumo.txt`):
  - identidade v1.4.4 × v1.4.5: 162 XML e LPs da etapa 1 idênticos; 81 LPs da etapa 2 diferentes só
    no objetivo, na variável `amplitude` e nas restrições `amplitude_constraints`
    (`identidade_v145.py`, que lê o LP como conteúdo; o controle pega 4 defeitos plantados);
  - regressão (portão), entradas e os testes 9 (9c, 9d), 9c-tela, 8, 12, p20, opB-b/c/d/e/padroes/
    tela, pref-tela;
  - 9c: técnicos 4,55 pp (o mínimo da conta de `08603c6`), enfermeiros 0 nesta rodada (não exigido);
    9d: 18,2% → 4,5% (na v1.4.4 o mesmo caso dava 36,4% → 4,5%, pela soma: 18,2 + 18,2).
  - Fora da suíte: `p14_conferir.py` (os casos dependem do tempo; o caminho sem prova fica nos
    testes 8 e 9c-tela) e `p17_frase_conferir.py` (falha igual na v1.4.4: espera os textos da tela
    anteriores à v1.4.3).
  - Decisões do Otávio com a Orientação (30/10), feitas no branch:
    - item 3 do p14 passa a "a maior amplitude da fração cumprida ≤ a da etapa 1". A nota está
      datada no DECISOES e no cabeçalho do script (`9ea6831`), e a conferência mudou depois
      (`fa72d36`). Ainda não rodado.
    - `NUMEROS_TCC.md`: as linhas que dependem da etapa 2 (§5, §6, §8 linhas 154–156, §9, §13,
      §15) levam a marca *medido na v1.4.4 (etapa 2 pela soma)*, sem valor mudado; a §7 fica sem
      marca. Seção nova "v1.4.5 — etapa 2 por min-max (30/10/2026), PENDENTE DE APROVAÇÃO", com o
      9c (maior 4,55 pp) e o 9d (18,2% → 4,5%, provado).
    - `resultados/cadeia_validacao_2026-10-24.md`: elo v1.4.4 × v1.4.5 (`cc7763c`).

- **Versão citável: v1.4.4** (v1.4.3 + P20). Tag `v1.4.4` em `e91aa05`, criada pelo Otávio; `main` e a
  tag enviadas ao GitHub. Suíte de fechamento de 23/10: **TUDO OK, 37 de 37 passos com código 0**,
  inclusive `tela_p20` (`resultados/v143_2026-10-23/suite/resumo.txt`). Nenhuma mudança em `src/`
  desde `ed621a2`. A tag v1.4.3 existe, em `704cb6a` (a versão de 22/10, antes da P20); a v1.4.4
  a sucede. *(Corrigido em 23/10: a versão anterior desta linha dizia, errado, que não existia tag
  v1.4.3.)* A tag v1.4.4 não se mexe.
  - O que a v1.4.4 traz em relação à v1.4.2:
    - trava do máximo de dias seguidos só a da CLT; a regra do hospital é preferência (21/10);
    - textos da tela para o gestor, tema escuro, barra pelo relógio (21/10);
    - divisão proporcional do tempo máximo, resultado por nível, seção 5 enxuta (22/10);
    - P20: depois de um nível sem prova, a trava usa o valor verdadeiro da escala (23/10).
- **Código congelado a partir de 23/10:** só correção de defeito, com registro no `DECISOES.md`
  antes (esperado, quando houver teste) e o portão da regressão.
- **HiGHS × SCIP** (pedido do orientador, 22/10; **nada da ferramenta mudou**):
  - Fase 0 (`resultados/solvers_2026-10-22/relatorio_fase0.md`): SCIP 10.0 por pip (PySCIPOpt 6.3.0,
    no `.venv`, fora do `requirements.txt`); partida aceita; regra de 09/10 e fusão valem; o mesmo
    modelo nos dois (com controle).
  - Bateria de 600 s, 22/10 (`relatorio_fase1.md`): SCIP 1 × HiGHS 2, 5 empates. **Regra de troca:
    fica o HiGHS.** Anomalia do medium_late05 esclarecida (folgas soltas: modelo 7.435, escala 2.199)
    e levou à P20.
  - Sensibilidade ao tempo, 3.600 s, 23/10 — **parcial, 4 de 6**
    (`resultados/solvers_2026-10-23_3600/relatorio_parcial.md`). O Claude Code a interrompeu por
    memória no B11/HiGHS. medium_late05: SCIP 186 × HiGHS 224; A36_livre: empate (13 provado nos
    dois). Falta o B11. Não reabre a regra de 22/10.
- **Caso A pela prática (24/10): TUDO OK**, esperado cumprido nas três rodadas (frase, sem
  violação de dura, descanso, direção da ordem 2 com prova). Resultado e complemento só leitura (por
  enfermeiro: unidade × acrescidos; violações por profissional com as férias; nota do "Unwanted
  pattern") em `resultados/caso_a_pratica_2026-10-23/resultado.md`. Sem solver daqui em diante.
- **Escala real recontada com 21 linhas (26/10):** a Orientação decidiu contar só as linhas com
  algum registro; as três vazias (6118, 4798, 6089) ficam fora da contagem, mas no caso (24 pessoas;
  rodadas de 21 e 24/10 valem). Recontagem (`recontagem.md`): **os 13 critérios do mesmo lado**;
  só mudam contagens dentro do lado (mín. folgas seguidas 371 → 359; máx. turnos 68 → 59). A
  contagem com 24 linhas ficou como histórico.
- **Cadeia de validação até a v1.4.4** (24/10, só leitura): `resultados/cadeia_validacao_2026-10-24.md`
  — em que versão cada evidência rodou, o que mudou depois e o que a liga à v1.4.4. Para a bateria,
  nenhuma restrição dura mudou (art. 67 sem par novo); K1–K6, propriedades e nível 3 não foram
  refeitos.
- **`NUMEROS_TCC.md`:**
  - seção "Comportamento computacional: HiGHS × SCIP" **aprovada em 23/10**;
  - seção **15b** (tamanho do modelo, nosso × Santos) **aprovada em 24/10**, com a formulação de
    Santos conferida no artigo;
  - seção **15** (casos A e B: 15.1 fase 2 de 21/10; 15.2 caso A pela prática de 24/10) **aprovada
    em 26/10**, com a transcrição da p. 70 conferida pelo Otávio, o período com o ano inferido e a
    tabela da escala real com as 21 linhas;
  - corrigidos dois caracteres de controle da seção 14 (texto de comando, nenhum número mudou).
  - Congelamento dos números: **25/10**; a seção 15 foi aprovada em 26/10, com as rodadas já
    feitas (sem solver depois de 24/10).

## Próxima tarefa

**0. Fechar a v1.4.5:** o merge no `main`, a tag `v1.4.5` e o push são **feitos pelo Otávio**.
O item 3 do p14 e as marcas do NUMEROS já foram decididos e feitos em 30/10. A seção v1.4.5 do
NUMEROS espera aprovação. Depois do merge: `MAPA_CODIGO.md` (o `identidade_v145.py`, o
`fechar_v145.sh`, o `max_amplitude` e o `maior_amplitude` do p14). As linhas 485 e 521 do NUMEROS
(HiGHS × SCIP, "etapa 2 não provou") também foram medidas pela soma e ficaram sem marca, porque
estão fora da lista da decisão; decidir se marca.

**1. Semana de escrita (26/10 a 30/10):** a Orientação monta um pacote de base por bloco para a
Redação, no formato de `D:\TCC\escrita\texto\esqueletos\PACOTE_B1_26-10.md` (afirmações L/F/A com
fonte, perguntas de banca, o que não escrever). O cronograma e a situação de cada seção estão no
PASSAGEM de `D:\TCC\escrita`. A ferramenta está congelada (só correção de defeito, com registro no
DECISOES antes). Seção 15 do NUMEROS aprovada em 26/10 e cadeia de validação
(`resultados/cadeia_validacao_2026-10-24.md`) são fonte do texto; onde a cadeia diz "não coberto", o
texto não afirma a ligação.

**2. Opcional — terminar o B11 da sensibilidade de 3.600 s** (~2 h; só se o Otávio quiser o caso
no texto). Com o Claude Code e outros programas fechados (o avaliador Java pode usar até 6 GB). No
PowerShell, um comando por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    python docs\diagnostico\bateria_solvers.py --todos --limite 3600 --saida resultados\solvers_2026-10-23_3600 --casos medium_late05 A36_livre_30 B11_livre_89

Sensibilidade com 2 ou 3 ordens de critérios: **sem proposta até a decisão do Otávio**.
Congelamento dos números: **25/10**; a partir de 26/10, só escrita (a seção 15 entrou em 26/10
por aprovação, sem número novo além da recontagem de 21 linhas, que é só leitura).

## Worktrees de leitura (D:\dev)

`D:\dev\tcc-nrp-v123`, `D:\dev\tcc-nrp-v130`, `D:\dev\tcc-nrp-v140`, `D:\dev\tcc-nrp-v141` e
`D:\dev\tcc-nrp-v142` são **worktrees de leitura** (cópias da v1.2.3, v1.3.0, v1.4.0, v1.4.1 e
v1.4.2 para as conferências de
identidade). Ninguém trabalha nelas;
o Claude Code só abre `D:\dev\tcc-nrp`. As da v1.2.3 e v1.3.0 têm cópias de scripts de identidade
deixadas pelas suítes antigas, por isso o `--force`. Para removê-las **depois da entrega**, da
raiz, um por linha:

    cd D:\dev\tcc-nrp
    git worktree remove --force ..\tcc-nrp-v123
    git worktree remove --force ..\tcc-nrp-v130
    git worktree remove --force ..\tcc-nrp-v140
    git worktree remove --force ..\tcc-nrp-v141
    git worktree remove --force ..\tcc-nrp-v142

(apaga só as pastas; as tags e o histórico ficam).

## Decisões de 26/10

- Orientação: na contagem da escala real entram só as 21 linhas com registro (nota a posteriori no
  DECISOES "2026-10-23 — Caso A"); a entrada do caso não muda. Recontagem sem mudança de lado.
- Seção 15 do NUMEROS_TCC aprovada pelo Otávio, com os ajustes (a)–(d) da Orientação.
- Precisão dos pesos do medium_late05 (commit `d9705c4`): pesos de 3 a 10 nas restrições suaves dos
  contratos atribuídos (0, 1 e 2); padrões indesejados e pedidos de folga com peso 1; contrato 3
  (peso 31) sem ninguém; sprint01 e long01 com todos os pesos 1 (ou 0, quando desligada). Conferido
  no XML. Frase admitida no texto: "No medium_late05, os pesos das restrições suaves dos contratos
  atribuídos vão de 3 a 10; os padrões indesejados e os pedidos de folga têm peso 1. No sprint01 e
  no long01, todas as restrições ativas têm peso 1." O peso 31 não vai ao texto.
- Sessão a pedido da Orientação (tarde de 26/10; nada em `src/`):
  1. DECISOES, entrada das 36 h de 20/10: nota de 26/10 (correção de citação) — as 8 h diárias são do
     art. 58 da CLT (CLT-005), e o art. 59 admite até 2 h extras (CLT-006); conferidos no Planalto.
     O texto de 20/10 fica como está.
  2. DECISOES, entrada nova "2026-10-26 — Limitações declaradas: duração diária do turno e limite
     semanal de horas": a v1.4.4 aceita turno de 1 a 24 h (início 0–23 h, hora cheia) e não verifica a
     duração máxima diária (arts. 58, 59 e 59-A) nem um limite semanal; carga 30/36/40/44 h com o teto
     no horizonte (02/10, item b). Para a duração do turno não há motivo registrado: limitação
     declarada a posteriori. Frase admitida no texto na entrada.
  3. DECISOES, entrada nova "2026-10-26 — Capturas da tela da v1.4.4 para o texto (4.7)", registrada
     antes de rodar (exceção à regra "sem solver depois de 24/10"). Rodada `rodada2_18tec_v144` (nome
     novo, para não sobrescrever a origem da seção 9 do NUMEROS): **esperado cumprido** — "Falta 1; o
     menor quadro viável é 29", motivo único "Alternância" (ter 03/11 e qua 04/11: 28 plantões, 27
     pessoas), alerta do QP; conferidor da planilha OK. O `capturas.py` foi ajustado à tela da v1.4.4
     (rótulos da demanda, ordem das grades, pedidos na seção 4, rótulo da alta dependência, aviso da
     etapa 1); ensaio só de preenchimento antes da rodada. Nenhum número novo.
  4. GUIA_DE_USO, seção 6: linha do motivo "Dois dias seguidos" na tabela do diagnóstico (faltava
     desde a v1.4.1).
  5. Comandos da identidade do pacote B2 (Apêndice C) conferidos em PowerShell, sem mudar a forma:
     "243 arquivos; 243 identicos; 0 diferentes".

## Decisões de 24/10

- Orientação: leitura C da borda (a posteriori) registrada no DECISOES "2026-10-23 — Caso A", com A
  e B; "mesmo turno no fim de semana" pela semântica do avaliador.
- Caso A pela prática rodado na v1.4.4: TUDO OK. Seção 15 do NUMEROS_TCC gravada como pendente.
- Seção 15b (nosso × Santos) aprovada, com a conferência no artigo.

## Decisões de 23/10 (v1.4.4)

- DECISOES "2026-10-23 — P20 aprovada: trava pelo valor verdadeiro depois de nível sem prova"
  (implementação; o modelo não muda). Teste `p20`: modelo 763, escala 224, o Essencial não piora.
- DECISOES "2026-10-23 — Sensibilidade ao tempo, HiGHS × SCIP, 3.600 s por caso" (análise de
  sensibilidade; vitória pela escala; não reabre a regra de 22/10).
- DECISOES de 22/10: "Bateria HiGHS × SCIP" (casos, regras, vitória e regra de troca) e "Anomalia do
  medium_late05 (HiGHS): folgas soltas na solução sem prova".
- Suíte da v1.4.3 + P20: TUDO OK (37 de 37); tag v1.4.4. **Código congelado**: só correção de
  defeito, com registro.

## Decisões de 22/10 (v1.4.3, acréscimo)

- DECISOES "2026-10-22 — Divisão proporcional do tempo máximo; resultado por nível; seção 5
  enxuta" (PARÂMETRO DE PROJETO e TELA; revisa o item b de "2026-10-19 — Opção B"). Decisões de
  implementação: etapa 1 sempre com 50% (os 50 : 30 : 20 entre os níveis presentes — é o que faz
  o padrão dar 30 + 30); proteção = resolver de novo com o resto; `TEMPO`/`TEMPO_ETAPA2` só como
  teto dos testes; M do bloco fundido só para o nível de cima; defeito do nome `p` corrigido em
  `_niveis_em_sequencia`.

## Decisões de 21/10 (noite, v1.4.3, continuação)

- DECISOES "2026-10-21 — Textos para o gestor, tema claro e barra pelo relógio" (TELA e
  REDAÇÃO): textos sem termos de Pesquisa Operacional; "?" dos critérios com exemplos conferidos;
  campo "Tempo máximo para gerar a escala"; tema escuro (o claro, trocado no mesmo dia a pedido
  do Otávio); barra pelo relógio com o cálculo numa
  thread de trabalho (plano B não usado).

## Decisões de 21/10 (noite, v1.4.3)

- DECISOES "2026-10-21 — Máximo de dias seguidos: a trava é só a da CLT; a regra do hospital é
  preferência" (mudança de ENTRADA e TELA; revisa "2026-10-19 — Máximo de dias seguidos como regra
  do hospital (rígida)", que ganhou marca de revisão). Regra da ferramenta: duro = lei ou físico;
  tudo o que o hospital quer é critério classificável.
- Suíte reduzida justificada no mesmo registro (a identidade prova que o problema enviado ao
  solver não mudou); não rodam as a2 nem os testes de tela que não tocam no campo.
- Teste max-dias reescrito com registro antes: o caso "hospital = 4 → Falta 1; o menor quadro
  viável é 15" deixa de existir.

## Decisões de 21/10 (manhã)

- DECISOES "2026-10-21 — Máximo de dias seguidos e máximo de turnos também como preferência"
  (MUDANÇA DE FORMULAÇÃO; revisa o item c de "2026-10-19 — Opção B"): famílias de preferência
  separadas das rígidas, com a expressão do INRC; limite usado = min(preferência, legal); padrão
  "Não considerar"; limites padrão 5 e 18 (contrato 0 do `medium_late05`).
- DECISOES "2026-10-21 — Correção de defeito: avaliador sem memória lido como 'sem violação'".
- Limitação declarada (caso A): a busca tenta só a composição da regra `equipe` e "todos
  enfermeiros"; o 30 vale para qualquer composição, mas 10 + 20 não é ótimo de custo.

## Decisões de 20/10 (tarde)

- DECISOES "2026-10-20 — a posteriori: fundamento das 36 h para qualquer plantão de 12 h ou mais"
  (art. 59 e 59-A; justificativa nova; convenção coletiva não lida; o texto não afirma
  descumprimento: "a regra, como modelada, segue o art. 59-A").
- DECISOES "2026-10-20 — Piso por pares de dias (v1.4.1)".
- Leitura registrada: técnico nunca cobre posto de enfermeiro (habilidade rígida; o critério
  "habilidade alternativa" não entra no modelo da ferramenta); por isso a conta só de
  enfermeiros existe e a só de técnicos não.
- Item extra (só leitura): 53 quadros provados inviáveis pelo solver nas rodadas registradas; a
  conta nova recusa 34. As contas do diagnóstico (horas por categoria, dia específico,
  alternância com férias) não entram no piso — registrado, **sem proposta** (decisão da
  Orientação).

## Decisões de 20/10 (Parte 6)

- DECISOES "2026-10-20 — a posteriori: descanso depois do D12 como parâmetro de pesquisa": o
  produto mantém 36 h; `DESCANSO_POR_TURNO` (vazio por padrão, fora da tela) só para experimento
  rotulado. Testado: padrão 243/243 com a v1.3.0; D12 = 11 h libera D12 → M no dia seguinte, a noite
  continua 36 h; o relógio acompanha o gerador. O texto não afirma que o hospital descumpre a lei.

## Decisões de 20/10 (fase 1 do caso A)

- Diagnóstico "combinação": "A conta prévia do menor quadro provou…" quando foi o piso
  (`DECISOES.md`, 2026-10-20). Entrada do solver idêntica (243/243).
- Achado de leitura: a regra das 36 h vale por **duração** (≥ 12 h), registrada em "2026-09-29 —
  Redesenho da ferramenta" com base no art. 59-A; **não há motivo registrado** para aplicá-la a um
  plantão de 12 h avulso (D12) fora do regime 12×36. Não é editável sem código.

## Decisões da sessão de 19–20/10 (3º bloco)

- DECISOES: "Opção B: decisões 4 e 5" (5 aprovada; 4 substituída pela tela sem Situação);
  "Pedidos e regras por profissional" (MUDANÇA DE FORMULAÇÃO; revê 09/10); "Máximo de dias
  seguidos como regra do hospital"; "Tela orientada ao usuário". Testes da tela atualizados com
  registro: 1-2 (aba Prioridades) e opB-tela (Partes 2, 4 e 5).
- Leituras adotadas: relatório de 20/10, seção "Leituras adotadas" (9 itens).
- Achado: o avaliador oficial não pontua DayOn/ShiftOn (limite 0 no código do jar); a ferramenta
  só usa pedidos negativos, que ele pontua.

## Decisões da sessão de 19/10 (2º bloco)

- Opção B: níveis em sequência, fusão por coeficiente se o bloco fundido < 10.000; 1.800 s por
  nível e na etapa 2; orçamento 60 min editável; 13 critérios com campo, 3 "já garantido pela
  CLT"; habilidade alternativa e pedidos por turno/para trabalhar fora.
- Os testes da tela rodam com os limites da v1.2.3 (600/180/20 min); um teste confere os padrões
  novos.

## Decisões da sessão de 19/10 (1º bloco)

- Opção B registrada (aprovação do Ormeu, 14/10); orçamento configurável, padrão 60 min,
  registrado (implementar junto com a B; bateria, demonstração e números atuais ficam
  declarados "com orçamento de 20 min").
- Cronograma: ferramenta 19–25/10; números congelados em 25/10; só escrita 26/10–01/11;
  revisão do orientador 02–06/11; **entrega 06/11**. **P18 cortada.** P16 só se sobrar tempo.
- Limitações declaradas: domingo no art. 67 e art. 386; o contorno pelo pedido de folga depende
  da classificação na opção B.
- Documentos novos: `docs/diferencas_inrc_ferramenta.md`, `docs/pesos_inrc.md`.

## Decisões da sessão de 13/10

- **Art. 67 com horários editáveis** (`DECISOES.md`, 2026-10-13). Com turno editado na tela, a
  folga isolada podia dar menos de 24 h (N 23–07, folga, M 05–13 = 22 h) e a ferramenta
  entregava a escala como "admite escala legal".
  - (a) o modelo proíbe a folga isolada abaixo de 24 h (fonte única: o gerador de pares);
  - (b) se a conferência no relógio reprovar, erro em vermelho, sem escala, e a busca para;
  - a regra vale também com `--sem-descanso-clt`; o id do padrão segue `clt_36h_…`.
- A afirmação de 29/09 "o modelo garante o art. 67 por construção" ficou marcada como
  superada (vale só para os horários dos modelos prontos).
- P16, item novo (pedido da Orientação): veredito próprio para a escala reprovada na
  conferência, no lugar de "nao_decidido"; mesma frase e mesmo comportamento. Prioridade
  baixa; janela de 26–29/10.

## Decisões das sessões de 09 a 11/10

- v1.2.1: evidência citada versionada.
- v1.2.2: frase da tela quando a etapa 2 não melhora (caminho sem prova).
- Texto do TCC antecipado para 09/10.
- P17: diagnóstico só como teste, sem mexer na ferramenta. Resultado:
  - A (1800 s): melhora;
  - B (simetria, 180 s): sem melhora.
- P18 opção A; P19 registrada, com (d) "busca longa"; item novo na P16.
- 11/10, reorganização dos chats:
  - `PASSAGEM.md` criado;
  - `CLAUDE.md`, `LEIA_PRIMEIRO.md` e a seção 7 do `ESTADO_ATUAL.md` reescritos;
  - bloco final das respostas: "LEVAR PARA O CHAT DE ORIENTAÇÃO";
  - congelamento dos números em 16/10.

## Pendências com a Redação

- **26/10:** (1) Seção 15 aprovada: pode ir ao texto. (2) Escala real: dizer "24 linhas transcritas,
  21 com registro contadas"; as três linhas sem registro (6118, 4798, 6089) ficam fora da contagem,
  mas no caso; o ano (2018) é inferido pelo calendário, não impresso na escala. (3) A tabela da
  escala real vai com a ressalva: um setor, um mês; leituras da imagem adotadas na ficha (dia útil
  em branco = trabalho); não afirma descumprimento de lei.
- **26/10 (b):** (1) A tabela "Pedidos e regras dos profissionais" (DECISOES 2026-10-19; GUIA_DE_USO)
  entra nos pacotes de 4.1 e 4.7. A Redação já a incluiu na 4.5 com (F23)-(F24), pela entrada
  vigente de 19/10; o PACOTE_B1_26-10 não a citava. (2) Perguntas ao Prof. Ormeu, ainda sem resposta
  (estão no PASSAGEM da Redação): instituição (CEFET/RJ), título, declaração de uso de IA, banca.
- **26/10 (c):** (1) Capturas da v1.4.4 para a 4.7: `docs/demonstracao/rodada2_18tec_v144_entrada.png`,
  `_equilibrando.png` e `_resultado.png` (texto da tela em `_tela.txt`). Substituem as de 09/10 só
  como imagem; os números da seção 9 do NUMEROS continuam com origem nos arquivos de 09/10. O texto
  não cita o tempo da rodada. (2) Apêndice C: os cinco comandos da identidade funcionam em PowerShell
  como estão no PACOTE_B2_26-10 — tirar o `[CONFERIR COMANDO]`. A pasta `$env:TEMP\id` é criada
  pelo script; a gravação na cópia da v1.4.2 regrava um `.pyc` versionado de lá (inofensivo; o
  Claude Code restaurou).
- **26/10 (d):** a conferência fora do modelo **na entrega** (`ferramenta.verificar` →
  `conferencia_descanso_escala.cumpre`) cobre só **descanso entre turnos, descanso semanal e dias
  seguidos**. Cobertura, um turno por dia, teto de horas e férias são restrições do modelo, conferidas
  fora dele por `solucao.conferir_rigidas` **apenas nos testes** (`testes_ferramenta`,
  `testes_entrada`, `bateria_rodar`, `conferir_planilhas`; também no `main` de linha de comando do
  `modelo.py` e na `escalabilidade.py`, que não são o caminho da entrega). O pacote B2 (4.2, item 4) e o
  texto da 4.3/4.4 diziam mais que isso; a Redação corrige o texto. Não é defeito da ferramenta: nada
  muda no código. (Conferido no código em 26/10: `ferramenta.py` só chama `cumpre`; `conferir_rigidas`
  não aparece em `ferramenta.py` nem em `app.py`.)

- **24/10:** (1) Cadeia de validação: `resultados/cadeia_validacao_2026-10-24.md` — o texto diz em
  que versão cada evidência rodou; onde a tabela diz "não coberto", não afirma a ligação (ex.: K1–K6,
  propriedades e nível 3 não foram refeitos depois de 07–09/10; a comparação por tipo com o avaliador
  da §14 não foi refeita na v1.4.4). (2) Caso A pela prática (seção 15.2, só depois da aprovação):
  as férias no INRC contam como dias sem trabalho — os 22 de máx. folgas seguidas são de férias
  (semântica do INRC, não escolha da ferramenta); os 4 da Noite A 1 no mín. turnos são inevitáveis só
  com o turno fixo no Essencial; a penalidade total do avaliador não vai ao texto; as linhas
  "Unwanted pattern" do avaliador são o artefato da P13. (3) A contagem da escala real é sobre o
  formato do INRC e não afirma descumprimento de lei.

- **v1.4.4 — suíte fechada em 23/10 (TUDO OK, 37 de 37): passam a valer as entradas de 21 e 22/10
  que diziam "se a suíte fechar"** (consolidadas aqui):
  - (a) **Dias seguidos:** a ferramenta não tem mais o "máximo de dias seguidos do hospital"
    rígido. A trava é só a da lei (6; no 12×36, a regra das 36 h), e a regra do hospital é
    preferência. Não citar o caso "hospital = 4 → Falta 1; 15" como comportamento da ferramenta.
    Frase de princípio admitida: "duro = lei ou físico (cobertura, CLT, horas do contrato, férias);
    tudo o que o hospital quer é critério classificável".
  - (b) **Máximo de dias seguidos e máximo de turnos** são também preferência classificável
    (desde a v1.4.2): o texto não pode dizer que são só "garantidos pela CLT". A preferência não
    tem conferência no avaliador oficial (o XML só tem a versão rígida); a contagem é do
    `avaliacao.py`.
  - (c) **Frases da tela que o texto pode citar, na forma final** (antes × depois em
    `resultados/textos_tela_2026-10-21.md`):
    - sem prova: "Escala gerada; pode haver uma melhor." O quanto pode melhorar sai por nível
      ("Importante: 7 violações. Nenhuma escala tem menos de 4."). A versão intermediária de 21/10
      ("…pode ser até X pior…") foi substituída em 22/10. Não usar mais "gap" como saída da
      ferramenta;
    - sem resposta: "a ferramenta não encontrou escala nem conseguiu mostrar que ela não existe";
    - "Esta escala tem a carga equilibrada entre colegas.";
    - "Tempo máximo para gerar a escala" (era "Orçamento do clique");
    - "Como o resultado foi obtido" (era "Como o veredito foi obtido").
    - **Não mudaram:** "Faltam N; o menor quadro viável é X", "O quadro informado admite escala
      legal" e "Não há escala legal até N".
  - (d) **Divisão do tempo:** é parâmetro de projeto, sem calibração (etapa 1 : etapa 2 = 50 : 50;
    50 : 30 : 20 entre os níveis presentes); declarar assim. Os números do NUMEROS_TCC foram
    medidos com os limites antigos, declarados lá.
  - (e) **Tela:** o alerta de descanso semanal virou uma linha, com o fundamento (Súmula 110, OJ
    355) no "?". A barra anda pelo relógio. O tema é escuro.
  - (f) **P20:** depois de um nível sem prova, a trava usa o valor verdadeiro da escala (folgas
    apertadas). Um nível sem prova não piora na escala final. A nota de 20/10 ("com nível sem
    prova, a prioridade entre níveis só é garantida nos provados") continua valendo quanto ao
    ótimo.
  - (g) O `GUIA_DE_USO.md` está atualizado com tudo isso (resolve o item (3) de 21/10).
- **HiGHS × SCIP (23/10):** a seção do `NUMEROS_TCC.md` foi aprovada e pode ir ao texto (tempos
  com a afirmação fraca; a rodada de 3.600 s é parcial). Para a seção 2.4.3 ("por que o HiGHS"):
  não há motivo registrado para a escolha original; a comparação entra como avaliação a
  posteriori.
- **21/10, ainda pendente:** (1) os números da fase 2 só vão ao texto depois de o Otávio aprovar a
  seção 15 proposta (`resultados/relatorio_2026-10-21.md`); A11 e B11 só como "HIPÓTESE DE
  SENSIBILIDADE — NÃO REGRA DA FERRAMENTA". (2) A penalidade do avaliador (288, 216, 96, 714) não
  vai ao texto como resultado; só "sem violação de dura".

- **20/10 (tarde):** (1) fundamento das 36 h: a frase admitida é "a regra, como modelada, segue o
  art. 59-A" — nunca "o hospital descumpre"; a convenção coletiva do caso não foi lida. (2) Na
  v1.4.1 o diagnóstico tem o motivo novo "Dois dias seguidos" (a conta da segunda-feira depois
  do fim de semana com plantão de 12 h); o `GUIA_DE_USO.md` ainda não o cita. (3) A conta prévia
  é condição necessária e compartilha a regra de descanso com o modelo: confere a aritmética,
  não a lei. Números da fase 2 só depois das rodadas.

- **3º bloco (20/10):** `GUIA_DE_USO.md` com a tabela "Pedidos e regras dos profissionais", o
  máximo de dias seguidos do hospital e a tela sem Situação; o texto não pode mais citar a coluna
  Situação nem "já garantido pela CLT" na tela. Fins de semana em 4 semanas = 2 é **valor de
  exemplo, sem fonte (suposição declarada)**, nunca valor do INRC. Nota para o texto: com nível
  sem prova, a prioridade entre níveis só é garantida nos provados. O avaliador oficial não
  pontua DayOn/ShiftOn (relatório de 20/10) — pode ir como limitação do benchmark.

- **Opção B (19/10, 2º bloco):** a função objetivo da ferramenta passa a ser por níveis
  escolhidos pelo gestor; o `GUIA_DE_USO.md` tem a seção nova; os números de antes ficam
  declarados "orçamento 20 min, 600 s / 180 s". Ainda sem tag (suíte incompleta).
- **19/10, prontos para leitura:** `docs/diferencas_inrc_ferramenta.md` (comparativo pedido
  pelo orientador; sem afirmar eficiência), `docs/pesos_inrc.md` (o INRC não tem um conjunto
  único de pesos: 41 instâncias só com peso 1, 28 com 1 a 10, e um 31 no `medium_late05`) e a
  especificação dos testes (`resultados/relatorio_2026-10-19.md`, seção 8; versões de Pyomo,
  Streamlit e Java das rodadas antigas não foram registradas).
- **Contagem de Santos:** x + y + w + r + z pela definição, sem as folgas α (limite inferior),
  tirada do fichamento; **conferir no artigo antes de ir ao texto**.
- **Validação por restrição:** os números só vão ao texto depois de o Otávio aprovar a seção 14
  proposta para o `NUMEROS_TCC.md`.
- **Limitações (19/10):** domingo no art. 67 e art. 386 registrados no `DECISOES.md`; o que
  falta (trabalho futuro? jurisprudência?) está listado lá.

- **Art. 67 (13/10):** onde o texto disser que o modelo garante o descanso semanal "por
  construção" ou pelos horários, trocar pela regra explícita: toda folga isolada ≥ 24 h, mais
  no máximo 6 dias seguidos (`DECISOES.md`, "2026-10-13 — Art. 67 com horários editáveis"). E
  a segunda proteção: escala que reprova na conferência no relógio não é entregue.

- **Seção 2.4.3:** gap de otimalidade, heurísticas primais no solver, HiGHS e por que ele
  (ferramenta gratuita). Fontes a conferir.
  - Material pronto: `DECISOES.md`, P17 item d, nota "para o referencial (2.4.3) e o método".
  - O que tem: o que é o sub-MIP do HiGHS 1.15.1; as três heurísticas que o usam (RENS, RINS,
    rootReducedCost); quando disparam; as opções `mip_heuristic_*` com os padrões.
  - Tudo com arquivo e linha na tag `v1.15.1` do ERGO-Code/HiGHS.
  - "Foi o RINS no K5" é inferência pelo código, não observação.
- **Limitação da P17:** números só da seção 13 do `NUMEROS_TCC.md`.
- **207 escalas heurísticas + 36 adversárias (18/09):** nem o script nem as escalas existem.
  - Busca feita em todo o histórico do git, nos arquivos apagados, em `historico/` e no disco.
  - Os números ficam como **registro histórico** (`DECISOES.md`, 18/09). **Não citar no
    capítulo de resultados** (`NUMEROS_TCC.md`, seção 1).
  - O método (conferir a semântica fora do modelo antes da função objetivo) pode ser descrito;
    a contagem não vai como resultado.

## Cronograma

- 19–25/10: modificações na ferramenta (opção B em 19/10; 3º bloco em 19–20/10; caso realista A a seguir).
- 20/10: reunião com o orientador.
- **Números congelados: 25/10** (substitui 16/10).
- 26/10–01/11: só escrita. 02–06/11: revisão do orientador.
- **Entrega: 06/11** (substitui 04/11).
- P18: cortada. P16: só se sobrar tempo.
