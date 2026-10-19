# Como trabalhar neste repositório

Instruções para o Claude Code. Isto é **protocolo de trabalho** — como agir. O **conteúdo**
— escopo, decisões, parâmetros normativos, resultados — está nos arquivos abaixo.

**Leia primeiro `ESTADO_ATUAL.md`**, antes de qualquer coisa. É o arquivo curto que diz onde
o trabalho está e aponta para os outros. Depois dele, conforme a tarefa:

- `PASSAGEM.md` — onde a última sessão parou e a próxima tarefa; lido primeiro pelos chats e
  atualizado pelo Claude Code ao fim de cada sessão.
- `VIRADA_ESCOPO_2026-09-24.md` — escopo e parâmetros normativos.
- `MAPA_CODIGO.md` — inventário do código, arquivo por arquivo.
- `DECISOES.md` — decisões de modelagem. Foi para `historico/` na virada de escopo de 24/09
  e voltou à raiz como arquivo ativo em 29/09. Cada entrada traz marca de status (vigente,
  superada, registro do escopo anterior); vale o que a marca diz.

---

## O que é o trabalho

TCC de Engenharia de Produção (CEFET-RJ, entrega 06/11/2026, adiada de 04/11 em 19/10). Uma **ferramenta de apoio à
decisão** que gera escalas de enfermagem a partir dos parâmetros de dimensionamento do COFEN
e da legislação trabalhista brasileira, com o motor de otimização validado contra o benchmark
INRC-2010, que tem ótimos publicados.

Escopo mudou em 24/09: antes era comparar regimes de jornada. Os experimentos daquele escopo
passam a ser validação e demonstração de uso. Os documentos antigos estão em
`historico/escopo-comparacao-regimes/` — consulta, não referência ativa.

**Congelamento de resultado numérico: 25/10/2026** (adiado de 16/10 em 19/10). Cronograma:
19–25/10 modificações na ferramenta; 26/10–01/11 só escrita; 02–06/11 revisão do orientador
(`DECISOES.md`, "2026-10-19 — Cronograma").

## Stack

Python, Pyomo, HiGHS. Avaliador oficial em Java (`avaliador/`, não versionado). A `.venv`
precisa estar ativa: `.\.venv\Scripts\Activate.ps1`.

O solver é parâmetro da chamada, não do modelo.

Heurística de warm start passou a ser admitida em 25/09, revertendo em parte a exclusão
anterior — mas **só como partida** (solução inicial e corte superior), nunca substituindo a
prova de otimalidade, e só se a curva de escalabilidade mostrar faixa em que a prova não
fecha. Fora isso: sem metaheurística, sem geração de colunas. O objeto é o modelo.

## Regras de trabalho

**Melhorias de implementação** — estrutura, forma de escrever restrições, organização dos
experimentos, ordem das tarefas: aplicar direto, sem perguntar.

**Mudanças de formulação, desenho experimental ou escopo**: registrar em `PROPOSTAS.md` com o
raciocínio completo e **não implementar**. O Otávio valida com o chat de Orientação, que lê
o `PROPOSTAS.md` direto desta pasta. O `PROPOSTAS.md` da raiz é o vigente; o do escopo anterior
está em `historico/escopo-comparacao-regimes/`.

**Nenhum resultado numérico vale** sem conferência no avaliador oficial ou contra a Tabela 6
de Santos et al. (2016). `python src\regressao.py` é o portão: roda antes de qualquer
alteração no modelo entrar.

**Git**: o Otávio é iniciante. Dar o comando exato e dizer o que ele faz. Nunca `rebase` nem
`amend` em commit antigo — o registro de que as decisões tiveram data e motivo é evidência do
trabalho.

**Decisão de modelagem não óbvia**: lembrar de registrar, com data.

**Execução longa** (regra de 03/10): antes de lançar, rodar o menor caso até o fim; depois de
lançar, só relatar que está rodando após o primeiro caso completo aparecer no log.

**Fim de sessão** (regra de 11/10): atualizar o `PASSAGEM.md` — onde paramos, próxima tarefa,
decisões da sessão, pendências com a Redação — e commitar. Vale também para sessões em que o
trabalho veio do chat de Orientação.

## Formato das respostas

Começar com uma seção curta **"Para o Otávio"**: o que mudou, o que ele precisa executar, o
que precisa de decisão. Máximo cinco linhas, sem jargão.

Terminar com um bloco separado, título **"LEVAR PARA O CHAT DE ORIENTAÇÃO"**, listando o que
mudou na pasta na sessão — todo arquivo de decisão, proposta, número ou passagem editado ou
criado —, com uma linha sobre o que mudou em cada. Se nenhum, escrever "LEVAR PARA O CHAT DE
ORIENTAÇÃO: nada". **Não omitir.**

Os chats leem esta pasta direto, sem upload: o de Orientação só lê; o de Redação lê esta pasta
e escreve em `D:\TCC\escrita`. O Claude Code é o único que escreve aqui. O bloco final serve
para o chat saber o que reler — decisão registrada aqui que ele não relê vira capítulo escrito
com decisão superada.

## O que este repositório aprendeu errando

Três erros de codificação num único dia (23/09) passaram por todas as conferências existentes.
O padrão é sempre o mesmo, e vale como critério:

**Conferência que compartilha premissa com o que confere não confere nada.** As regras de
descanso da CLT não cobriam metade dos tipos de turno, e a conferência que deveria pegar isso
enumerava a mesma lista incompleta. Quem pegou foi uma medição feita a partir dos horários no
arquivo, sem usar nenhuma lista.

**Lista duplicada é o defeito.** O mesmo conjunto de pares proibidos existia em três lugares.
Corrigir dois não mudou nada, porque o terceiro — o contrato — continuava apontando para os
ids antigos, e padrão que o contrato não referencia não vale nada.

**Resultado idêntico depois de uma correção é sinal de alarme**, não de estabilidade. Duas
vezes num dia isso significou que a correção não tinha chegado ao código que rodava.

Daí as conferências existentes: `conferir_amarracao` (o que está escrito chega a valer?),
`docs/conferencia_descanso_escala.py` (mede o relógio, não confia em lista) e o portão da
regressão.

## Afirmações fracas

Tempo de resolução **nunca** vai ao texto como resultado — só como limite operacional, com
máquina e solver nomeados. O mesmo vale para qualquer coisa medida numa configuração só.
