# PASSAGEM — Orientação (ferramenta)

Atualizado em 13/10/2026. Lido primeiro pelo chat de Orientação; atualizado pelo Claude Code ao
fim de cada sessão (dele ou do chat).

## Onde paramos

- Versão citável: **v1.2.3** (13/10, correção do art. 67; nenhum número muda). Validação
  encerrada em 09/10.
- Números citáveis: `resultados/NUMEROS_TCC.md`.
- P17 fechada, sem defeito.
  - Nos limites da tela, a etapa 2 não melhorou em nenhuma das 5 resoluções sem prova.
  - K5 com 1800 s: diferença entre colegas, enf. 42 → 12 h, aos ~29 min (Sub-MIP).
  - Simetria sem efeito em 180 s.
  - Limitação de tempo, não de alcance. P19 = trabalho futuro (a–d).
- Nada muda na ferramenta até 26/10, exceto correção de defeito.
- Reorganização dos chats (11/10): os chats leem esta pasta direto.
  - Orientação só lê.
  - Redação lê e escreve em `D:\TCC\escrita`.
  - Só o Claude Code escreve aqui.
  - Sem upload; as cópias no Projeto do claude.ai foram aposentadas.

## Próxima tarefa

- Claude Code: nada pendente da sessão de 13/10. Feito: correção do art. 67 com horários
  editáveis, (a) + (b), com esperado commitado antes; suíte completa OK; tag `v1.2.3`
  (`resultados/relatorio_2026-10-13a.md`).
- Sessão de 11/10, feitos:
  - Sub-MIP do HiGHS 1.15.1, registrada no `DECISOES.md`, P17 item d;
  - busca das 207 + 36 escalas de 18/09: não encontradas (ver "Pendências com a Redação").
  - "shell still running": era um comando travado do próprio Claude Code, já encerrado; nenhum
    processo vivo, nenhuma rodada em andamento.
- Otávio: e-mail ao orientador (confirmar se foi enviado).
- Otávio: enviar a tag ao GitHub — `git push origin main` e depois `git push origin v1.2.3`.
- Santos et al. (2016) está no acervo (achado pelo md5 em 13/10); caminho no `LEIA_PRIMEIRO.md`.
  As cópias do Projeto podem ser apagadas sem perder o artigo.
- 16–17/10: P18, opção A.
- Depois da P18: MAPA_CODIGO.md (pedido da Redação, sustenta a 4.2 e o Apêndice C). Só
  documentação; na mesma sessão da P18 ou na seguinte. Pedido de 11/10, em resumo:
  1. todo `src/` e os scripts de `docs/`, com caminhos pós-P18: papel (produto, validação,
     teste, experimento, diagnóstico) e módulos do projeto que importa ou chama;
  2. fluxo de um clique no `ferramenta.py`, pelos nomes das funções, sem número de linha: conta
     (veredito do quadro), etapa 1, etapa 2 com e sem prova, menor quadro, diagnóstico,
     conferência fora do modelo (descanso no relógio), planilha;
  3. índice reverso script → seções e linhas do `NUMEROS_TCC.md`, sem copiar comandos;
  4. tirar "Rodando agora" e "O que isso sugere para a construção da ferramenta"; o escopo
     anterior fica, marcado como histórico;
  5. cabeçalho "conferido na versão <tag ou commit>, <data>";
  6. conferir que todo comando da coluna "Comando" do `NUMEROS_TCC.md` aponta para arquivo que
     existe (sem rodar); corrigir só o caminho e listar no relatório;
  7. depois da P16 (fim de 29/10): reconferir os nomes de função do item 2 e atualizar a versão
     no cabeçalho.

## Decisões da sessão de 13/10

- **Art. 67 com horários editáveis** (`DECISOES.md`, 2026-10-13). Com turno editado na tela, a
  folga isolada podia dar menos de 24 h (N 23–07, folga, M 05–13 = 22 h) e a ferramenta
  entregava a escala como "admite escala legal".
  - (a) o modelo proíbe a folga isolada abaixo de 24 h (fonte única: o gerador de pares);
  - (b) se a conferência no relógio reprovar, erro em vermelho, sem escala, e a busca para;
  - a regra vale também com `--sem-descanso-clt`; o id do padrão segue `clt_36h_…`.
- A afirmação de 29/09 "o modelo garante o art. 67 por construção" ficou marcada como
  superada (vale só para os horários dos modelos prontos).

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

- Números congelados: 16/10.
- P18: 16–17/10.
- Texto: até 25/10.
- Tela (P16): 26–29/10.
- Entrega: 04/11.
