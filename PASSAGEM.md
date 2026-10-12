# PASSAGEM — Orientação (ferramenta)

Atualizado em 11/10/2026. Lido primeiro pelo chat de Orientação; atualizado pelo Claude Code ao
fim de cada sessão (dele ou do chat).

## Onde paramos

- Versão citável: v1.2.2. Validação encerrada em 09/10.
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

- Claude Code: nada pendente da sessão de 11/10. Feitos:
  - Sub-MIP do HiGHS 1.15.1, registrada no `DECISOES.md`, P17 item d;
  - busca das 207 + 36 escalas de 18/09: não encontradas (ver "Pendências com a Redação").
  - "shell still running": era um comando travado do próprio Claude Code, já encerrado; nenhum
    processo vivo, nenhuma rodada em andamento.
- Otávio: e-mail ao orientador (confirmar se foi enviado).
- 16–17/10: P18, opção A.

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
