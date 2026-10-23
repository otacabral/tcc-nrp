# PASSAGEM — Orientação (ferramenta)

Atualizado em 23/10/2026. Lido primeiro pelo chat de Orientação; atualizado pelo Claude Code ao
fim de cada sessão (dele ou do chat).

## Onde paramos

- **Versão citável: v1.4.4** (v1.4.3 + P20). Tag `v1.4.4` em `e91aa05`, criada pelo Otávio; `main` e a
  tag enviadas ao GitHub. Suíte de fechamento de 23/10: **TUDO OK, 37 de 37 passos com código 0**,
  inclusive `tela_p20` (`resultados/v143_2026-10-23/suite/resumo.txt`). Nenhuma mudança em `src/`
  desde `ed621a2`. Não existe tag v1.4.3: a v1.4.4 contém tudo. A tag v1.4.4 não se mexe.
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
- **`NUMEROS_TCC.md`:**
  - seção "Comportamento computacional: HiGHS × SCIP" **aprovada em 23/10**;
  - tabela de tamanho (nosso × Santos) **pendente de aprovação**;
  - seção 15 (casos A e B) ainda **proposta, não gravada**;
  - corrigidos dois caracteres de controle da seção 14 (texto de comando, nenhum número mudou).
  - Congelamento dos números: **25/10**.

## Próxima tarefa

**1. Otávio: aprovar (ou corrigir) a seção 15 proposta para o `NUMEROS_TCC.md`** (casos A e B), no
`resultados/relatorio_2026-10-21.md`. Só depois os números vão ao texto.

**2. Otávio: aprovar (ou não) a tabela de tamanho (nosso × Santos)**, pendente no `NUMEROS_TCC.md`.
Antes de citar, conferir a formulação de Santos no artigo (a coluna de Santos é um piso).

**3. Opcional — terminar o B11 da sensibilidade de 3.600 s** (~2 h; só se o Otávio quiser o caso
no texto). Com o Claude Code e outros programas fechados (o avaliador Java pode usar até 6 GB). No
PowerShell, um comando por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    python docs\diagnostico\bateria_solvers.py --todos --limite 3600 --saida resultados\solvers_2026-10-23_3600 --casos medium_late05 A36_livre_30 B11_livre_89

Sensibilidade com 2 ou 3 ordens de critérios: **sem proposta até a decisão do Otávio**.
Congelamento dos números: **25/10**; a partir de 26/10, só escrita.

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
