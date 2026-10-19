# PASSAGEM — Orientação (ferramenta)

Atualizado em 19/10/2026. Lido primeiro pelo chat de Orientação; atualizado pelo Claude Code ao
fim de cada sessão (dele ou do chat).

## Onde paramos

- Versão citável: **v1.2.3** (13/10). Tag no GitHub (conferido em 19/10). Os commits de 19/10
  ainda não foram enviados (push do Otávio).
- **Opção B aprovada** pelo Prof. Ormeu (14/10, 19h58) e registrada (`DECISOES.md`,
  "2026-10-14 — Função objetivo por níveis escolhidos pelo gestor (opção B)"): MUDANÇA DE
  FORMULAÇÃO, **implementação pendente**. Nada de código de produto mudou em 19/10.
- **Validação por restrição nos 4 ótimos: feita e OK** (`resultados/validacao_restricoes_2026-10-19/`):
  duras 0; penalidade por tipo e por profissional, avaliador × modelo, diferença 0; controle
  positivo com 20 escalas perturbadas reavaliadas no avaliador oficial, OK. Seção proposta
  para o `NUMEROS_TCC.md` no `resultados/relatorio_2026-10-19.md`, seção 4 — **não incluída,
  aguarda aprovação**.
- Números citáveis: `resultados/NUMEROS_TCC.md` (inalterado). Congelamento: **25/10**.
- Reorganização dos chats (11/10): os chats leem esta pasta direto; só o Claude Code escreve
  aqui; a Redação escreve em `D:\TCC\escrita`.

## Próxima tarefa

- **Claude Code: implementação da opção B**, depois da decisão da Orientação sobre o
  diagnóstico (`resultados/relatorio_2026-10-19.md`, seção 3). Decisões pendentes:
  1. **pesos escalonados × resoluções em sequência** (3d): com 3 níveis no caso da
     demonstração, o coeficiente de Essencial passa de 1,3 milhão e o gap padrão do HiGHS
     (0,01%) deixa de provar o ótimo dos níveis de baixo; em sequência, cada nível fica abaixo
     de 10.000 e a condição de 09/10 vale. A etapa 2 já é feita em sequência;
  2. **quais critérios entram** (3c): máximo de dias seguidos, máximo de turnos e padrões
     indesejados são rígidos pela CLT na ferramenta; a versão "preferência" deles exige família
     própria no modelo. Habilidade alternativa contradiz a habilidade rígida. Pedido por turno
     tinha virado trabalho futuro em 09/10;
  3. **orçamento × limite por resolução** (3e): 60 min de orçamento não dão mais que 600 s a
     uma resolução (etapa 1) nem mais que 180 s à etapa 2;
  4. teste de identidade com a classificação padrão: rodar com o orçamento de 20 min, ou
     registrar antes a troca dos textos "20 min" → "60 min".
- Junto com a B: orçamento por clique configurável, padrão 60 min (`DECISOES.md`, 19/10).
- Depois, se houver tempo: `MAPA_CODIGO.md` (caminhos atuais, sem P18); P16.
- Otávio: enviar os commits — `git push origin main` (manda os commits de 19/10 para o GitHub;
  a tag `v1.2.3` já está lá).
- Otávio: aprovar (ou não) a seção 14 proposta para o `NUMEROS_TCC.md`.

## Decisões da sessão de 19/10

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

- 19–25/10: modificações na ferramenta (opção B, orçamento configurável).
- 20/10: reunião com o orientador.
- **Números congelados: 25/10** (substitui 16/10).
- 26/10–01/11: só escrita. 02–06/11: revisão do orientador.
- **Entrega: 06/11** (substitui 04/11).
- P18: cortada. P16: só se sobrar tempo.
