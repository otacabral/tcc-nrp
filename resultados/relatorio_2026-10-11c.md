# Relatório de 11/10/2026 (c): reorganização dos chats, Sub-MIP, escalas de 18/09

Só documentos e leitura. **Nada mudou em `src/` nem na `v1.2.2`.**

## Para o Otávio

- **Os chats passam a ler a pasta direto.** O `PASSAGEM.md` é novo. `CLAUDE.md`, `LEIA_PRIMEIRO.md`
  e a seção 7 do `ESTADO_ATUAL.md` foram reescritos (autorização de 11/10).
- **Sub-MIP (letra "L"):** é o HiGHS resolvendo uma cópia menor do problema, com parte das
  variáveis fixadas. Três heurísticas a usam; no K5, pelo código, foi o RINS.
- **Escalas de 18/09:** nem o script nem as escalas existem. No `NUMEROS_TCC.md`, as linhas
  viraram registro histórico, que não vai ao capítulo de resultados.
- **Shell:** não havia nada rodando de quem quer que seja (item 6).

## 1–3. Reorganização dos chats

**`PASSAGEM.md` (novo, na raiz):**
- conteúdo inicial do Otávio, com o acréscimo D: "Números citáveis: `resultados/NUMEROS_TCC.md`";
- no fim da sessão, atualizado com o resultado dos itens 4–6.

**`CLAUDE.md`:**
- regra nova "Fim de sessão": atualizar o `PASSAGEM.md` e commitar;
- o bloco final passa a se chamar "LEVAR PARA O CHAT DE ORIENTAÇÃO" e lista o que mudou na pasta;
- a frase "o projeto de redação não tem acesso a esta pasta" saiu; entrou a divisão nova:
  - Orientação só lê;
  - Redação lê e escreve em `D:\TCC\escrita`;
  - o Claude Code é o único que escreve aqui;
- congelamento dos números: 16/10;
- saiu a regra "reescrita de arquivo de contexto está congelada" (vencida, item A);
- corrigida a frase de que o `PROPOSTAS.md` "se recria": ele existe e é o vigente;
- o `PASSAGEM.md` entrou na lista de leitura.

**`LEIA_PRIMEIRO.md`, reescrito como mapa da pasta:**
- saíram o "sem acesso", as cópias no Projeto, a seção de duplicatas e os dois avisos sobre as
  instruções antigas;
- a ordem de leitura começa pelo `PASSAGEM.md`;
- a tabela de arquivos-ponte inclui o `PASSAGEM.md` e o `NUMEROS_TCC.md`, com caminho;
- os arquivos citados passaram a ter caminho real:
  - relatórios em `resultados/`;
  - fontes que não estão no repositório, em `D:\TCC\acervo`, `D:\TCC\escrita\fontes` e
    `D:\TCC\arquivo_morto`;
  - o `s1047901415946.pdf` não foi achado pelo nome.

**`ESTADO_ATUAL.md`:** a seção 7 foi reescrita, sem upload, com os três papéis e os
arquivos-ponte. A frase de abertura do arquivo também foi ajustada.

## 4. Sub-MIP no HiGHS 1.15.1

Registrado no `DECISOES.md`, P17, item d, como nota "para o referencial (2.4.3) e o método".

**Versão que roda:**
- pacote `highspy`: 1.15.1;
- banner da biblioteca: "Running HiGHS 1.15.1 (git hash: 04024d7)";
- a tag `v1.15.1` do ERGO-Code/HiGHS aponta para o commit `04024d701f79…`, o mesmo hash;
- os logs via `appsi_highs` não trazem o banner.

**Fonte:** <https://github.com/ERGO-Code/HiGHS/tree/v1.15.1>, arquivos baixados e lidos nessa
tag.

| Pergunta | Resposta | Onde |
|---|---|---|
| o que é sub-MIP | `HighsPrimalHeuristics::solveSubMip`: resolve com o próprio MIP do HiGHS uma cópia do modelo com limites de variáveis apertados; a solução achada entra como fonte `kSolutionSourceSubMip` ("L", "Sub-MIP") | `highs/mip/HighsPrimalHeuristics.cpp`:77 e :238; `HighsMipSolverData.h`:53; `HighsMipSolverData.cpp`:113–115 |
| quem chama | `rootReducedCost`, `RENS`, `RINS` | `HighsPrimalHeuristics.cpp`:314/369, :394/627, :661/938 |
| quando | raiz: `rootReducedCost` e `RENS`; árvore: `RENS` sem incumbente, `RINS` com incumbente, se `moreHeuristicsAllowed()` deixar | `HighsMipSolverData.cpp`:2363–2398; `HighsMipSolver.cpp`:746–795 e :847; `HighsMipSolverData.cpp`:669 |
| opções (padrão) | `mip_heuristic_effort` 0,05; `mip_heuristic_run_rins` true; `mip_heuristic_run_rens` true; `mip_heuristic_run_root_reduced_cost` true; dentro da cópia, `mip_heuristic_effort` = 0,8 | `highs/lp_data/HighsOptions.h`:1224–1257; `HighsPrimalHeuristics.cpp`:130; conferido no `.venv` e em <https://ergo-code.github.io/HiGHS/stable/options/definitions/> |

**No K5:** "foi o RINS" é **inferência pelo código**. As melhoras saíram na árvore, com
incumbente, depois do último reinício. O log não registra o nome da heurística.

## 5. As 207 escalas heurísticas e as 36 adversárias de 18/09

**Resultado: não encontrado, nem o script nem as escalas.** Não recriei nada.

**Script:** não existe.
- **Todos os arquivos `.py` que já passaram pelo git** (`git log --all --name-only`): nenhum gera
  escalas heurísticas ou adversárias.
  - O `src/avaliacao.py` (commit `4fde6c3`, 18/09 02:34) é o calculador de penalidade conferido
    nessas escalas, não o gerador.
- **Arquivos apagados** (`--diff-filter=D`): só imagens e planilhas da demonstração
  (`docs/demonstracao/`).
- **Renomeações:** só a ida dos documentos do escopo anterior para `historico/` e duas telas da
  demonstração.
- **Sem `stash`** e sem objetos soltos (`git fsck --lost-found`).
- **Busca de 06/10** (`relatorio_2026-10-06b.md`, commit `b9ed680`): no conteúdo de todos os
  commits, por "guloso", "advers", "gerador", "heuristica", "random" e "aleat". Só aparecem
  documentos que descrevem as escalas.
- **Transcrições do Claude Code:** a mais antiga é de 24/09. Não há registro da sessão de 18/09.

**Escalas (XMLs de solução e saídas do avaliador):** não existem.
- **No git:** nenhum arquivo de solução de 18/09. Os XMLs de solução versionados são outros:
  - os ótimos de sprint01, sprint02, long01 e long02;
  - o `medium_late05` (06/10);
  - os de 15/09 (`*_escala_trivial.xml`);
  - os do experimento A (22/09).
- **No disco** (`D:\` inteiro e `C:\Users\Otavio` fora do `AppData`), arquivos de 16 a 19/09:
  só `src/avaliacao.py`, `docs/medicao_conversao_12h.py`, `docs/medicao_sobreposicao.py` e
  `resultados/consolidado.csv`.
- **Em `avaliador/`:** só os 4 `.jar`.
- **Em `resultados/pyomo.zip`:** só a biblioteca Pyomo.
- **Não dá para conferir "207 em 69" nem "36 em 6":** não há arquivo para contar. Os números
  existem só no texto do `DECISOES.md` (18/09) e na `nota_passagem_2026-09-18.md`.

**Registrado no `NUMEROS_TCC.md`, seção 1**, nas duas linhas e só nas colunas de origem e de
ressalva:
- origem: "não encontrada após busca no histórico do git (11/10)";
- ressalva: "registro histórico (`DECISOES.md`, 18/09); não citar no capítulo de resultados".
- Nenhum número mudou.

## 6. "Shell still running"

- **O que era:** um comando meu desta sessão, a primeira tentativa de recontar as escalas de A
  e B. Um `cat` solto ficou esperando entrada e o comando travou, sem fazer nada.
- **O que aconteceu com ele:** o Claude Code o encerrou sozinho, por falta de memória
  (notificação "killed"). A recontagem foi refeita num comando separado, que terminou normalmente.
- **Conferido depois:** nenhum processo Python, shell, Streamlit ou HiGHS vivo
  (`Get-CimInstance Win32_Process`).
- **Não era** rodada em andamento nem algo lançado pelo Otávio. Não havia o que encerrar.
- **Nesta sessão:** encerrei também um `find` meu (PID 20880), a busca do item 5 no disco
  inteiro, que estava lenta. Ela foi refeita em duas partes menores.
