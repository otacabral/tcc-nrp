# Mapa do código — o que é cada arquivo e o que serve à ferramenta

**28/09/2026.** Escrito depois da virada de escopo de 24/09, para responder a uma pergunta
simples: *destes treze arquivos, quais são a ferramenta e quais são o trabalho anterior?*

Não é triagem de decisões — essa sai no projeto de redação depois da especificação. É
inventário de código.

**A descoberta ao montar o mapa:** duas coisas que nasceram como experimento **já são funções
da ferramenta**, só que sem interface. Estão marcadas com ⭐ abaixo.

---

## Núcleo — vira produto

| Arquivo | O que faz |
|---|---|
| `src/instancia.py` | As estruturas de dados: turno, contrato, profissional, padrão, demanda. Sem Pyomo, sem XML. É a fronteira que permite a instância brasileira entrar sem tocar no modelo. |
| `src/modelo.py` | **O motor.** Monta o problema de programação inteira: 2 restrições rígidas, 13 flexíveis, limites legais endurecíveis por flag. É o que a interface vai chamar. |
| `src/instancia_br.py` | **A tradução da norma.** Parecer COFEN + CLT → instância resolvível. Recebe grau de dependência, porte, regime, efetivo e devolve o problema montado. Na ferramenta, isto é a camada que fica atrás do formulário. Desde 29/09: caminho por turnos configurados e demanda informada; `pares_proibidos_por_horario`, fonte única das regras de descanso; `alertas_cofen`, que não trava. |
| `src/solucao.py` | Escreve a escala produzida e valida contra o esquema. É a saída. |
| `src/tabela.py` | Gravação de CSV por mesclagem, com testes próprios. Utilitário. |
| `src/ferramenta.py` | **A ferramenta sem tela** (29/09): entrada do formulário → veredito do quadro ("admite escala legal" / "faltam N; o menor quadro viável é X"), QP em duas parcelas, escala conferida e planilha `.xlsx`. Resolve pelo `experimento_a.tentar`, sem copiar a configuração do modelo. |
| `src/app.py` | **A tela** (Streamlit): `streamlit run src\app.py`. Só a casca de `ferramenta.py`. Desde 29/09 (Etapa 6), na ordem da especificação: unidade (modelo de turnos editável, fim de semana, grau), equipe (férias, pedidos de folga), demanda por turno (generalista e específica), painel COFEN opcional, resultado com alertas em vermelho. |
| `src/testes_ferramenta.py` | Ponta a ponta pela tela (AppTest): configuração do Experimento A, 12×36, razão 20/29 — 40 admite, 39 diz que o menor viável é 40, QP 35,24 e 40,52, planilha abre. |
| `src/testes_entrada.py` | Testes das entradas da ferramenta (29/09): pacientes, QP em duas parcelas, razão fim de semana/dia útil, equipe por quantidade, indisponibilidade. Reproduz 40 e 37 do Experimento A pela razão 20/29. `--rapido` pula o solver. |

## Já são funções da ferramenta, sem interface

| Arquivo | A função que ele é |
|---|---|
| ⭐ `src/experimento_a.py` | *"O quadro que a fórmula do COFEN dá admite escala legal?"* Varre o efetivo, prova inviabilidade abaixo do mínimo e exibe escala acima. **É o caso de uso principal da ferramenta** — o gestor calcula o quadro pela fórmula e quer saber se ele fecha. |
| ⭐ `docs/conferencia_descanso_escala.py` | *"Esta escala é legal?"* Mede o descanso real entre plantões a partir dos horários, sem depender de padrão nem de avaliador. **É o relatório de conformidade** que o usuário precisa ver junto com a escala. |
| ⭐ `src/experimentos.py` | Entre escalas de mesmo custo ótimo, mede quanto a carga individual pode variar. **É a base do "me dê a escala mais equilibrada"** em vez de aceitar a que o solver devolveu por acaso. |

## Validação — a prova de que o motor funciona

Não entram no produto, mas sustentam o capítulo que diz que ele está correto. Não apagar.

| Arquivo | O que faz |
|---|---|
| `src/regressao.py` | **O portão.** 4 instâncias × 4 conferências. Roda antes de qualquer alteração no modelo entrar. Continua valendo no escopo novo. |
| `src/avaliacao.py` | Reimplementação da penalidade em Python puro. É o oráculo: existe para o modelo ter com quem discordar. |
| `src/validar.py` | Chama o avaliador oficial da competição (Java) e compara. |
| `src/parser.py` | Lê o XML do INRC. Necessário para a validação; e se a ferramenta um dia importar instâncias, é por aqui. |
| `src/inspecionar.py` | Varredura das 69 instâncias do benchmark. Serviu ao levantamento inicial; consulta. |

## Rodando agora

| Arquivo | O que faz |
|---|---|
| `src/escalabilidade.py` | Curva 40–200 profissionais: até que tamanho a prova fecha. Decide se o warm start heurístico é necessário. |
| `src/escalabilidade_objetivo.py` | A mesma curva com o objetivo da ferramenta e 2 pedidos de folga por pessoa (P1, 02/10). Registra, por etapa, prova, gap e tempo até a primeira escala legal. |

## Acréscimos de 19–20/10 (opção B, 3º bloco, Parte 6, Partes 7–9)

**Núcleo (`src/`):**

| Arquivo | O que faz |
|---|---|
| `src/prioridades.py` | **Opção B** (19/10): a função objetivo por níveis escolhidos pelo gestor. Só contas, sem solver: catálogo dos critérios, máximo de violações de cada um, plano de resolução (`planejar`: que níveis se fundem num bloco), aplicação dos pesos na instância (`aplicar`), resultado por critério, e a tabela "Pedidos e regras dos profissionais" (`Linha`, `traduzir`, `descumpridos`; 3º bloco, 19–20/10). |
| `src/ferramenta.py` (20/10, tarde) | **Piso por pares de dias** (Parte 7, v1.4.1): `bloqueiam_o_dia_seguinte` (turnos que impedem qualquer turno no dia seguinte, tirados dos pares do gerador) e `pares_de_dias` (postos de d+1 + postos de d nesses turnos ≤ disponíveis em ao menos um dos dois dias; total e só enfermeiros). Entra no `piso` e no diagnóstico (motivo `pares`, "Dois dias seguidos"). |
| `src/instancia_br.py` (20/10) | `DESCANSO_POR_TURNO`: parâmetro de pesquisa (vazio no produto) lido por `descanso_exigido` — fonte única do gerador e da conferência no relógio. |

**Diagnóstico e suítes (`docs/diagnostico/`), sem entrar no produto:**

| Arquivo | O que faz |
|---|---|
| `censo_flexiveis.py` | Censo das flexíveis nas 69 instâncias do INRC e limite superior de violações (19/10). Sem solver. |
| `tamanho_modelos.py` | Tamanho do nosso modelo (Pyomo) e o de Santos et al. (2016) pela definição (19/10). Sem solver; não afirma eficiência. |
| `validacao_restricoes.py`, `validacao_restricoes_controle.py` | Validação por restrição nos 4 ótimos (56, 58, 197, 219) contra a saída do avaliador oficial, e o controle positivo (19/10). |
| `identidade_opcao_b.py`, `identidade_3bloco.py` | Identidade da entrada do solver (XML + LP das etapas 1 e 2) entre duas árvores (`git worktree`), byte a byte: 81 casos × 3 arquivos = 243. |
| `identidade_opcao_b_rodadas.py` | Teste (a2): rodadas da bateria (P01–P18) e da demonstração com os limites da v1.2.3, comparadas com o registrado. Desde 20/10 (tarde), `A2_PISO_PARES=1` admite só as tentativas listadas em `ADMITIDAS` (Parte 7). |
| `pedidos_avaliador.py` | Pedidos da tabela conferidos no avaliador oficial (20/10): escreve a instância com os pedidos (`escrever_instancia`). Os `teste4/5.md` e os `_avaliador.txt` (estes por `src/validar.py`) saem em CRLF: `write_text` em modo texto no Windows. |
| `plantao12.py` | Parte 3 (20/10): plantão de 12 h no fim de semana; 22 inviável, 23 viável. |
| `piso_pares.py` | Parte 7 (20/10, tarde): testes do piso por pares — segurança nas 224 rodadas registradas, entradas dos testes da tela, controle (Parte 3), casos A e B, sorteio pequeno com solver, e a tabela do item extra. |
| `fase2.py` | Parte 9: uma rodada da fase 2 (casos A e B; 36 h e a hipótese D12 = 11 h), com o JSON por rodada e a conferência no avaliador oficial. `--montar` = sem solver. |
| `fechar_v130.sh`, `fechar_v140.sh`, `fechar_v141.sh` | Suítes de fechamento de cada versão (um processo por teste, para na primeira falha, `RETOMAR=1`). A da v1.4.1 compara a identidade com a v1.4.0 (`../tcc-nrp-v140`); `PULAR_SOLVER=1` testa o script. |
| `rodar_fase2.sh` | Parte 9: as cinco rodadas da fase 2, com a memória livre conferida antes de cada uma (`PULAR_SOLVER=1` testa o script). |

## Acréscimos de 21/10 (preferências de dias seguidos e de turnos; defeito do avaliador)

| Arquivo | O que mudou |
|---|---|
| `src/instancia.py` | `Contrato.pref_max_consecutive_working_days` e `pref_max_num_assignments` (ausentes por padrão; fora de `RESTRICOES` e do XML). |
| `src/modelo.py` | Duas famílias de **preferência**, com folga e a expressão do INRC (janela de dias seguidos; teto de turnos), separadas das rígidas, que não mudaram. Só existem quando ativas. |
| `src/prioridades.py` | "Máximo de dias seguidos (preferência)" e "Máximo de turnos no período" viram critérios com nível e limite (`PREF_DIAS`, `PREF_TURNOS`); `limite_usado` = min(preferência, legal); `violacoes_preferencia` conta fora do modelo pelo `avaliacao.py`. |
| `src/app.py` | As duas linhas na tela, com importância e limite (máximo = o legal); a de dias abaixo do campo rígido do hospital; oculta no 12×36. |
| `src/validar.py` | Correção de defeito: avaliador que para (código ≠ 0 ou "Exception in thread") levanta `AvaliadorIndisponivel`; JVM com `-Xmx6g` (`MEMORIA_JAVA`). |
| `src/testes_ferramenta.py` | Caso novo `pref-tela`; opB-d e opB-tela atualizados com registro. |
| `docs/diagnostico/preferencias.py` | Testes (b) controle, (c) caso pequeno com solver e (e) identidade nas cinco entradas da fase 2 (`--raiz` grava com o código de outra árvore). |
| `docs/diagnostico/fechar_v142.sh` | Suíte da v1.4.2: a da v1.4.1 com a identidade contra `../tcc-nrp-v141` e os testes das preferências; `RETOMAR=1`, `PULAR_SOLVER=1`. |

## Acréscimos de 21/10, v1.4.3 (a trava de dias seguidos é só a da CLT)

`src/modelo.py` e `src/instancia_br.py` intocados (`DECISOES.md`, "2026-10-21 — Máximo de dias
seguidos: a trava é só a da CLT; a regra do hospital é preferência").

| Arquivo | O que mudou |
|---|---|
| `src/ferramenta.py` | `Entrada.max_dias_seguidos` sai; `montar` passa sempre `max_consecutivos=br.MAX_CONSECUTIVOS_GENERICO` (6). |
| `src/app.py` | Sai a linha rígida do hospital (chave `max_dias`) e o parâmetro `max_dias` de `_entrada`; `TETO_LIMITE` dos dias seguidos = o legal (6). |
| `src/prioridades.py` | Só texto: ajuda e resumo da preferência de dias seguidos ("a lei trava em 6; a regra do seu hospital vai aqui…"), dois comentários. |
| `src/testes_ferramenta.py` | `max-dias` reescrito para a preferência (4 no Essencial: 96 = 96; 13 técnicos: "Falta 1; …14", texto da conta prévia); `pref-tela` com a parte de 8 h (sem o campo; teto 6; ajuda). |
| `docs/diagnostico/fechar_v143.sh` | Suíte reduzida da v1.4.3: identidade contra `../tcc-nrp-v142`, regressão, entradas, piso e os testes da tela do campo, da preferência de dias, dos textos novos e da barra; `RETOMAR=1`, `PULAR_SOLVER=1`. |
| `src/app.py` (textos, 21/10 noite) | Textos para o gestor (sem termos de Pesquisa Operacional); sem a linha pequena sob cada critério; campo "Tempo máximo para gerar a escala (minutos)" (key `orcamento`); legenda de QP e IST; `_equilibrio` traduz o estado do equilíbrio de carga; **barra pelo relógio**: `fe.verificar` numa thread de trabalho que não chama o Streamlit, a thread do script anda a barra (decorrido ÷ tempo máximo, até 99%) e desenha a escala provisória; no fim, ~3 s até 100%. |
| `src/ferramenta.py`, `src/prioridades.py` (textos, 21/10 noite) | Só redação: frases do resultado, diagnóstico, barra, planilha, "?" dos critérios; `prioridades.RESUMO` removido (a linha pequena saiu da tela); coluna "Nível" → "Importância". Nenhuma conta mudou. Antes × depois em `resultados/textos_tela_2026-10-21.md`. |
| `src/ferramenta.py` (tempo, 22/10) | `pesos_das_partes`, `fatia`, `_limite_da_parte`, `_primeira` (proteção da primeira escala): divisão proporcional do tempo máximo (etapa 1 : etapa 2 = 50 : 50; 50 : 30 : 20 entre os níveis presentes); `TEMPO`/`TEMPO_ETAPA2` = `None` (teto só dos testes); `info["partes"]` (limite e tempo gasto de cada parte); `frases_por_nivel`, `frase_equilibrio`; `alertas_descanso` em uma linha e `FUNDAMENTO_SEMANAL`; frase principal sem gap. |
| `src/app.py` (seção 5, 22/10) | Uma tabela por nível com a frase acima; frase do equilíbrio; painel "Detalhes da escala" (fechado) com as legendas; "sem pedidos"; "Por que 35 h?". |
| `docs/diagnostico/tempo_proporcional.py` | `--conta` (sem solver: tabela 20/60/120 min, conta 15/9/6/30 e sobra, frases por nível) e `--caso` (com solver: proteção da primeira escala e sobra adiante). |
| `src/ferramenta.py` (P20, 23/10) | `_apertar` e `_valor_preso`: depois de um nível sem prova, fixa as atribuições, aperta folgas e auxiliares e prende o valor verdadeiro (`expr ≤ z` e a etapa 2); `info["partes"]` guarda `valor_modelo`, `valor` (apertado), `limite_inferior`, `aperto`. Com prova, nada muda. |
| `src/testes_ferramenta.py` (P20) | `p20`: caso 5, todas as suaves no Essencial, blocos separados, 30 s; o Essencial não piora na escala final. |
| `docs/diagnostico/bateria_solvers.py`, `comparar_solvers.py`, `anomalia_medium_late05.py` | HiGHS × SCIP (22/10): bateria, Fase 0 e o diagnóstico das folgas soltas. Fora da ferramenta. |
| `.streamlit/config.toml` | Tema escuro (`base = "dark"`; o claro foi trocado no mesmo dia, a pedido do Otávio). |

## Escopo anterior — referência, não produto

Ficam em `docs/`. Produziram achados que vão ao texto como metodologia.

| Arquivo | O que produziu |
|---|---|
| `docs/conferencia_padrao_avaliador.py` | A demonstração de que o avaliador oficial lê o padrão das 36 h como (noturno, folga, folga). |
| `docs/conferencia_contratos.py` | O piso forçado e a descoberta de que o lote *early* é um cenário por track, não 15 independentes. |
| `docs/conferencia_piso_forcado.py` | As duas declarações que sustentam o piso aritmético. |
| `docs/medicao_conversao_12h.py`, `docs/medicao_sobreposicao.py` | A reagregação de turnos sobrepostos (P5). |

Os documentos do escopo anterior estão em `historico/escopo-comparacao-regimes/`, exceto o
`DECISOES.md`, que voltou à raiz como arquivo ativo em 29/09.

---

## O que isso sugere para a construção da ferramenta

O motor está pronto e validado. O que **não** existe é: camada de entrada que não seja código
Python, apresentação da escala em formato legível por gestor, e o relatório de conformidade
como saída de produto em vez de saída de terminal.

Ou seja — a parte difícil já passou. O que falta é a casca. Isso é uma boa notícia para o
prazo, e é o que a especificação precisa delimitar.

**Uma pendência de risco que a especificação vai ter de encarar:** o tempo de resolução. O
`experimento_a.py` leva de 1 a 43 segundos por tentativa de efetivo, e a curva de
escalabilidade está medindo o que acontece com 200 profissionais. Uma interface web que faz o
usuário esperar não é a mesma coisa que um script que roda no terminal.
