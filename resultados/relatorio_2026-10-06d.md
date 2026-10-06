# Relatório de 06/10/2026 (d)

## Para o Otávio

- **Tag `v1.0.1` criada e enviada.** É a versão citável do TCC: commit `35a9cd1`, objeto da tag `a43f502`.
- **`NUMEROS_TCC.md` atualizado:** os 4 ótimos e o `medium_late05` com a conferência no avaliador reconfirmada pelo `validar.py` corrigido, mais a caracterização do `medium_late05` com a ressalva pedida.
- **Corrigi um erro meu no `NUMEROS_TCC.md`:** o comando do `medium_late05` estava gravado com um caractere de controle no lugar do `\r` de `docs\rodar_...`.
- Nada a executar: `git pull` e `git pull --tags`.

## Item 1 — Tag v1.0.1

- **Commit marcado:** `35a9cd1`, que traz a nota do ESTADO_ATUAL e as atualizações do NUMEROS_TCC.
- **Tag anotada:** `v1.0.1`, objeto `a43f5023d85a94d26cccf076f21fced674b9a368`, apontando para `35a9cd178311f8c67678bd7b0322f7136e6bf630`.
- **Enviada** com `git push --tags` e conferida no servidor.
- **Motivo:** a correção do `src/validar.py` depois da `v1.0`.
- **A suíte não rodou de novo:** nenhum teste usa o `validar.py`, e as cinco conferências (56, 58, 197, 219, 224) já tinham sido refeitas.
- **ESTADO_ATUAL.md:** nota "v1.0.1 — versão citável do TCC".

## Item 2 — NUMEROS_TCC.md

**a) As linhas de 56, 58, 197, 219 e 224** agora trazem a conferência no avaliador oficial, reconfirmada em 06/10 com o `validar.py` corrigido (commit `e9e0da4`), e o comando que reproduz cada uma:
- ótimos: `python src\validar.py instancias/<...>.xml resultados/<instância>_completo.xml --objetivo <Z>`;
- `medium_late05`: `... resultados/medium_late05_2026-10-06/medium_late05_escala.xml --objetivo 224`.

Nos 4 ótimos, uma ressalva nova: a coluna `avaliador_oficial` do `consolidado.csv` (18/09) não tem origem documentada, e a reconfirmação de 06/10 a substitui.

**b) Caracterização do `medium_late05`** no fim da seção 1: 30 profissionais, 28 dias, 5 turnos de 8 h, 390 pedidos de folga, quase todas as flexíveis ativas com pesos de 1 a 10 e 7 padrões indesejados. A ressalva diz que é comparação de estrutura com a instância da demonstração, explicação provável da diferença de dificuldade e **não causa demonstrada**, porque nenhum experimento isolou os fatores.

**Correção:** o comando do `medium_late05` (`python docs\rodar_medium_late05.py`) estava gravado com um caractere de controle no lugar do `\r` do caminho. O erro entrou quando gravei a linha em 06/10, item 4 da sessão (b).

**Conferência de codificação:** a edição desta vez tropeçou em acentos passados pelo terminal. Varri 57 arquivos (DECISOES, PROPOSTAS, ESTADO_ATUAL, guia, README, CLAUDE, relatórios, `docs/`, `src/`) atrás de caractere de substituição e de acento corrompido: **nenhum encontrado**.

---

## LEVAR PARA O PROJETO DE REDACAO

- **`ESTADO_ATUAL.md`**: nota de 06/10 — versão citável do TCC = `v1.0.1` (commit `35a9cd1`).
- **`resultados/NUMEROS_TCC.md`**:
  - conferência no avaliador reconfirmada em 06/10 nos 4 ótimos e no `medium_late05`, com os comandos;
  - caracterização do `medium_late05`, com a ressalva de que não é causa demonstrada;
  - comando do `medium_late05` corrigido.
- `DECISOES.md`, `PROPOSTAS.md` e `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
