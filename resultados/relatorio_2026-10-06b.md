# Relatório de 06/10/2026 (b) — sessão sem supervisão

## Para o Otávio

- **Os quatro itens foram feitos.** Nada foi movido, apagado ou alterado em `src/` e nos testes.
- **`medium_late05` em 3.600 s: 224, sem prova** (limite inferior 63, gap 71,88%). O publicado é 107. O avaliador oficial confirma 224 na escala gravada.
- **Achei um defeito no `src/validar.py`:** ele não consegue chamar o avaliador ("Syntax error"). Chamado direto, o avaliador funciona. Não corrigi, por causa das travas.
- **O padrão das 36 h:** o código aplica a opção (a), o padrão no arquivo, e não há registro de quem escolheu. O script das 207 + 36 escalas não está em lugar nenhum do repositório.
- **Para decidir:** registrar (a) ou (b) como decisão; e se o `validar.py` entra como correção de defeito.

## Status por item

| Item | Status | Commit |
|---|---|---|
| 1. Notas ficam em `docs/` | **feito** | `05481ac` |
| 2. Padrão das 36 h: (a) ou (b) | **feito** (só relato) | `b9ed680` |
| 3. Script das 207 + 36 | **feito**: não encontrado | `b9ed680` |
| 4. `medium_late05` em 3.600 s | **feito**: 224, sem prova | `b9921fb` (esperado), `00a35b0` (resultado) |
| 5. Este relatório | feito | o seguinte |

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

## Item 4 — `medium_late05`, de novo, com limite de 3.600 s: FEITO

**Esperado registrado antes** (commit `b9921fb`, docstring de `docs/rodar_medium_late05.py`):
- publicado: 107 (Tabela 6, gap 0);
- se provar o ótimo, 107; se não, registra-se o que vier, e o avaliador tem de dar o mesmo valor do modelo;
- valor abaixo de 107 seria defeito.

**Como rodou:** sozinho, sem outro processo Python. Memória livre ao lançar: cerca de 1 GB. Não caiu.

| | |
|---|---|
| Valor da melhor escala | **224** |
| Limite inferior (dual bound, log do HiGHS) | **63** |
| Gap | **71,88%** |
| Estado do solver | `maxTimeLimit`: **sem prova** |
| Tempo de relógio | 3.604,1 s (**limite operacional**) |
| Modelo | 15.320 variáveis, 13.060 restrições |
| `avaliacao.py` na escala | 224 |
| **Avaliador oficial** na escala gravada | **224** |
| Máquina | Intel Core i5-10210U, 12 GB, Windows 11, Python 3.11.9, `appsi_highs` (HiGHS 1.15.1) |

**Leitura:**
- O ótimo publicado (107) não foi reproduzido em 3.600 s. A melhor escala achada (224) está longe dele, e o limite inferior (63) também.
- Isso não indica defeito: o valor é ≥ 107 e o avaliador concorda com o modelo.
- O `medium_late05` continua como limite declarado da validação.
- A rodada de 15/09 (716 em 520 s, em outro ambiente) foi superada.

Arquivos em `resultados/medium_late05_2026-10-06/`: `resumo.json`, `highs.log`, `medium_late05_escala.xml` e `medium_late05_escala_avaliador.txt`.

**`NUMEROS_TCC.md`:** a linha antiga ficou marcada como SUPERADA, e há uma linha nova com o 224, o limite inferior, o gap, o estado, a conferência no avaliador e o comando.

### Defeito achado e NÃO corrigido (trava: nada em `src/`)

`src/validar.py` chama o avaliador com `java -cp avaliador/evaluator.jar ...` (linha 56, `JAR` na linha 34 e vizinhas).

- Assim o avaliador responde "Syntax error" e o script acusa "divergência" que não existe: o `resumo.json` registra `validar_codigo = 1`.
- Chamado como manda o README, com o classpath curinga `java -cp "avaliador/*" dds.nrp.core.evaluation.ScheduleEvaluator <instância> <solução>`, ele lê os arquivos e dá **224**.
- O `.log` cru do validar está em `medium_late05_escala_avaliador.txt`.

**Para decidir:** entra como correção de defeito, com esperado registrado antes? As conferências que passam pelo `validar.py` podem estar afetadas. A regressão não está: ela não usa o `validar.py`.

---

## LEVAR PARA O PROJETO DE REDACAO

- **`DECISOES.md`**: entrada nova "2026-10-06 — Notas de 22 e 23/09 ficam em docs/ como metodologia ativa".
- **`ESTADO_ATUAL.md`**: dívida "Destino de quatro notas" riscada, apontando para a decisão.
- **`resultados/NUMEROS_TCC.md`**: linha do `medium_late05` superada e linha nova (224, limite inferior 63, gap 71,88%, sem prova, avaliador 224).
- `PROPOSTAS.md` e `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
- **Para decidir:**
  - o padrão das 36 h no arquivo: (a) manter, que é o que o código faz hoje, ou (b) tirar. Hoje não há registro de escolha;
  - a correção do `validar.py` (classpath).
