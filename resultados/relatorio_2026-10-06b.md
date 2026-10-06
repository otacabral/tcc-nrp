# Relatório de 06/10/2026 (b) — sessão sem supervisão

*(Escrito item a item; a versão final está no fim.)*

## Item 1 — Notas de `docs/` ficam como metodologia ativa: FEITO

- `DECISOES.md`: entrada nova "2026-10-06 — Notas de 22 e 23/09 ficam em docs/ como metodologia ativa".
- `ESTADO_ATUAL.md`: a dívida "Destino de quatro notas" está riscada e aponta para a decisão.
- Nada foi movido. Commit `05481ac`.

## Item 2 — Padrão das 36 h, opção (a) ou (b): SÓ RELATO

**O código aplica hoje a opção (a): o padrão fica no arquivo XML.**

- `src/instancia_br.py`, `_padroes_de` (linhas 553–572): transforma cada par proibido com salto 2 em padrão indesejado, com id `clt_36h_<turno>_<turno>` e entradas (turno, `None`, turno).
- `src/instancia_br.py`, `escrever_xml`: escreve os padrões em `<Patterns>` (linhas 1126–1128) e os referencia no `<UnwantedPatterns>` do contrato (linhas 1163–1166).
- No modelo, os mesmos pares valem como restrição **rígida** (`modelo.RIGIDAS_LEGAIS_BR` inclui `unwanted_patterns`).

**Registro de escolha: nenhum encontrado.**
- A P13, que propunha (a) ou (b), está no `historico/escopo-comparacao-regimes/PROPOSTAS.md` com status "aguardando validação" (23/09).
- O último texto dela inclina para a (b), mas diz "Continua sendo decisão de vocês".
- A virada de escopo de 24/09 (`VIRADA_ESCOPO_2026-09-24.md`, seção 4) mandou "as propostas P10, P11 e P13 na forma em que estavam pendentes" para o histórico, sem decidir.
- O `ESTADO_ATUAL.md` lista o achado sem a escolha.
- Nos commits que tratam da P13 (`3e87391`, `14de9f4`, `02e96ea`, de 23/09), também não há escolha.

**Conclusão:** a (a) é o estado de fato, porque os padrões já eram emitidos desde antes do achado (commits `0426a8f`, `548e536`, `c785292`). Não é uma escolha registrada.

## Item 3 — Script das 207 + 36 escalas de 18/09: NÃO ENCONTRADO

Onde procurei:
- **Ramos:** só existe `main` (e `origin/main`).
- **Arquivos apagados** (`git log --all --diff-filter=D`): só as capturas antigas da demonstração.
- **Todo `.py` que já entrou no repositório** (`git log --all --name-only`): 29 arquivos. Nenhum gera escalas heurísticas.
- **Buscas no conteúdo de todos os commits** (`git log --all -S`): "guloso", "advers", "gerador", "heuristica", "random", "aleat". Só aparecem documentos que *descrevem* as escalas e, no `random`, a semente dos pedidos da P1.
- **`historico/`:** só `nota_passagem_2026-09-18.md`, que descreve os seis geradores em texto.

**Onde o resultado está descrito:** `DECISOES.md`, "2026-09-18 — Semântica das flexíveis validada fora do modelo", que entrou no commit `337d8ba` (18/09, 03:06). Esse commit só alterou `.md`, `src/avaliacao.py` e `src/modelo.py`; nenhum gerador.

Não restaurei nem recriei nada. O `NUMEROS_TCC.md` já marca essas linhas como ORIGEM NÃO ENCONTRADA.
