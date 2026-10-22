# PASSAGEM — Orientação (ferramenta)

Atualizado em 22/10/2026. Lido primeiro pelo chat de Orientação; atualizado pelo Claude Code ao
fim de cada sessão (dele ou do chat).

## Onde paramos

- **Versão citável: v1.4.2** (suíte TUDO OK em `resultados/v142_2026-10-21/suite/resumo.txt`,
  depois da parada em tela_opB-c e do RETOMAR; tag criada e enviada pelo Otávio). Máximo de dias
  seguidos e máximo de turnos também como preferência. A tag v1.4.2 não se mexe.
- **v1.4.3, acréscimo de 22/10: divisão proporcional do tempo máximo, resultado por nível e
  seção 5 enxuta** — implementados e commitados, **à espera da revisão do Otávio na tela**. Metade
  do tempo para as prioridades (50 : 30 : 20 entre os níveis presentes), metade para o equilíbrio;
  a sobra passa adiante; proteção da primeira escala. Frases por nível acima da tabela; a frase
  principal perde o gap. Leitura dos pesos com nível vazio a confirmar (DECISOES de 22/10, decisão
  de implementação 1). A suíte da v1.4.3 continua sem rodar: roda uma só, depois da revisão.
- **v1.4.3, continuação (21/10, noite): textos da tela para o gestor, tema claro e barra pelo
  relógio** — implementados e commitados, **à espera da revisão do Otávio na tela**. Antes ×
  depois em `resultados/textos_tela_2026-10-21.md`; exemplos do "?" conferidos pela contagem
  (15 de 15; dois exemplos corrigidos no texto). A suíte da v1.4.3 que tinha sido lançada foi
  cancelada (Ctrl+C) e roda **uma vez só**, depois da revisão.
- **v1.4.3 implementada, suíte por rodar** (21/10, noite): a trava do máximo de dias seguidos
  passa a ser **só a da CLT** (6; no 12×36, a regra das 36 h). O campo rígido do hospital saiu da
  tela e da `Entrada`; a regra do hospital vai pela preferência de dias seguidos (no Essencial,
  pesa acima de tudo o que é Importante ou Desejável). `modelo.py` e `instancia_br.py` intocados.
  - Já conferido nesta sessão: identidade 243/243 (sem linhas e com linhas) e 24/24 da fase 2
    contra a v1.4.2 (teste do script sem solver); regressão 56, 58, 197, 219; testes de entrada;
    piso (segurança, controle, casos); max-dias reescrito (preferência 4 no Essencial com 14:
    escala sai, 96 = 96; 13 técnicos: "Falta 1; o menor quadro viável é 14", texto da conta
    prévia); pref-tela e opB-d OK.
  - Esperado: `resultados/trava_clt_2026-10-21/ESPERADO.md`. Worktree `D:\dev\tcc-nrp-v142` criado.
- `NUMEROS_TCC.md`: sem mudança (nenhum número usou o campo do hospital ≠ 6). Seção 15 (casos A
  e B) ainda **proposta, não gravada**. Congelamento dos números: **25/10**.
- Não enviado ao GitHub: os commits da v1.4.3 (vão no push depois da tag).

- **HiGHS × SCIP, Fase 0 (22/10, pedido do orientador)** — relatório em
  `resultados/solvers_2026-10-22/relatorio_fase0.md`; script `docs/diagnostico/comparar_solvers.py`.
  Itens 1 a 4 passam: SCIP 10.0 por pip (PySCIPOpt 6.3.0, instalado no `.venv`, fora do
  `requirements.txt`); partida aceita (log do SCIP, `completesol`, com controle); regra de 09/10
  e fusão W = M + 1 valem (o gap do SCIP é mais exigente); o modelo recebido pelos dois é o mesmo
  (com controle), depois de desfazer, no script, a reescrita do objetivo que a interface do
  Pyomo faz para o SCIP. Fumaça interrompida por falta de memória (1,8 GB livres). **Nada da
  ferramenta mudou.** Depois da fumaça, a Fase 1 (bateria) só com o ok do Otávio.

## Próxima tarefa

**0. Otávio: revisar a tela.** Abrir a ferramenta (um por linha):

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    streamlit run src\app.py

Conferir os textos contra `resultados/textos_tela_2026-10-21.md`, o tema escuro e a barra (gerar
uma escala pequena). Aprovar ou pedir ajustes ao Claude Code. **Só depois** rodar a suíte.

**1. Otávio: suíte reduzida da v1.4.3** (~1 h 45 nesta máquina, i5-10210U, HiGHS 1.15.1; o opB-e
sozinho leva ~35 min, e o caso com solver da divisão do tempo, ~12 min). Com o Claude Code e o Chrome fechados. Antes, apagar a pasta da suíte
cancelada (o RETOMAR a pegaria). No PowerShell, um comando por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    Remove-Item -Recurse -Force resultados\v143_2026-10-21
    & "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v143.sh

Termina com "TUDO OK" ou "PARADO: ..." na última linha de
`resultados/v143_<data>/suite/resumo.txt`. Se for interrompida (memória, queda), **retomar** —
pula o que já passou e continua na mesma pasta —, um por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    $env:RETOMAR = "1"
    & "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v143.sh
    Remove-Item Env:RETOMAR

Diferenças admitidas: só as do `resultados/trava_clt_2026-10-21/ESPERADO.md` (max-dias
reescrito; pref-tela com a parte de 8 h; e, no acréscimo da noite, os textos de 8, 12, opB-tela,
pref-tela e max-dias). Qualquer outra diferença é falha. O `Remove-Item` é só para a primeira
vez: ao retomar, não apagar a pasta.

**2. Só com TUDO OK: tag v1.4.3 e envio** (um por linha; a tag marca a versão, o push manda os
commits e a tag ao GitHub):

    git tag -a v1.4.3 -m "v1.4.3: trava de dias seguidos so a da CLT; regra do hospital e preferencia"
    git push origin main
    git push origin v1.4.3

Se "PARADO": não criar a tag; abrir o log indicado e trazer ao Claude Code.

**3. Otávio: aprovar (ou corrigir) a seção 15 proposta para o `NUMEROS_TCC.md`** (casos A e B), no
`resultados/relatorio_2026-10-21.md`. Só depois os números vão ao texto.

Sensibilidade com 2 ou 3 ordens de critérios: **sem proposta até a decisão do Otávio**.
Congelamento dos números: **25/10**.

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

- **22/10 (se aprovado e a suíte fechar):** (1) a frase sem prova passa a "Escala gerada; pode
  haver uma melhor." — o quanto pode melhorar sai por nível ("Importante: 7 violações. Nenhuma
  escala tem menos de 4."); não usar mais o "gap" no texto como saída da ferramenta. (2) A
  divisão do tempo é **parâmetro de projeto, sem calibração** (50 : 50; 50 : 30 : 20); declarar
  assim. Os números do NUMEROS_TCC foram medidos com os limites antigos, declarados. (3) O alerta
  de descanso semanal virou uma linha; o fundamento (Súmula 110, OJ 355) fica no "?".

- **21/10 (noite, textos da tela, se aprovados e a suíte fechar):** frases citáveis que mudam —
  lista antes × depois no topo de `resultados/textos_tela_2026-10-21.md`. Em resumo: "pode haver
  uma melhor (gap X: …)" → "pode haver uma melhor: esta escala pode ser até X pior que a melhor
  possível, e com mais tempo a ferramenta poderia melhorá-la"; "o solver não achou escala nem
  provou que ela não existe" → "a ferramenta não encontrou escala nem conseguiu mostrar que ela
  não existe"; "Escala desta tela: a da etapa 2…" → "Esta escala tem a carga equilibrada entre
  colegas."; "Orçamento do clique" → "Tempo máximo para gerar a escala"; "Como o veredito foi
  obtido" → "Como o resultado foi obtido". As frases "Faltam N; o menor quadro viável é X", "O
  quadro informado admite escala legal" e "Não há escala legal até N" **não mudaram**. A barra
  agora anda pelo relógio (o `GUIA_DE_USO.md` dizia "a barra não tem relógio"; atualizado).

- **21/10 (noite, v1.4.3, se a suíte fechar):** (1) a ferramenta não tem mais "máximo de dias
  seguidos do hospital" rígido: a trava é só a da lei (6); a regra do hospital é preferência. O
  texto não pode citar o caso "hospital = 4 → Falta 1; 15" como comportamento da ferramenta. (2)
  Frase de princípio admitida: "duro = lei ou físico (cobertura, CLT, horas do contrato, férias);
  tudo o que o hospital quer é critério classificável". (3) O `GUIA_DE_USO.md` foi atualizado: tirou
  o campo do hospital e explica as duas preferências (resolve o item (3) de 21/10, manhã).

- **21/10:** (1) números da fase 2 só depois de o Otávio aprovar a seção 15 proposta
  (`resultados/relatorio_2026-10-21.md`); A11 e B11 só como "HIPÓTESE DE SENSIBILIDADE — NÃO REGRA
  DA FERRAMENTA". (2) A penalidade do avaliador (288, 216, 96, 714) não vai ao texto como
  resultado: só "sem violação de dura". (3) O `GUIA_DE_USO.md` ainda não cita as duas
  preferências novas da tela. (4) A preferência não tem conferência no avaliador oficial (o XML só
  tem a versão rígida); a contagem é do `avaliacao.py`. (5) O texto não pode mais dizer que
  máximo de dias seguidos e máximo de turnos são só "garantidos pela CLT": viraram também
  preferência classificável (na v1.4.2, se a suíte fechar).

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
