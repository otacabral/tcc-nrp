# Relatório de 11/10/2026 (a): P17 fechada, defeito de texto corrigido, v1.2.2

Máquina: Intel Core i5-10210U, 12 GB, Windows 11, `appsi_highs` (HiGHS 1.15.1). Tempos são
limite operacional, não resultado.

## Para o Otávio

- **P17 fechada, sem defeito.** O K5 rodou e saiu como o esperado previa: sem melhora. A
  recontagem independente bate com a ferramenta.
- **Defeito de texto corrigido.** Quando a etapa 2 não melhora (caminho sem prova), a tela agora
  diz "a da etapa 1". Regressão e telas 8 e 12 OK.
- **Tag v1.2.2 criada.** É a nova versão citável. Push feito no fim, porque nada divergiu.
- **Achado:** o teste 8b também ficou sem melhora. São 5 resoluções sem prova, e em nenhuma a
  etapa 2 melhorou.
- **Para decidir:** o caso, não observado, do caminho COM prova sem melhora (ver B3).

## A. P17: diagnóstico fechado

**A1. Rodada do K5** (feita por você em 11/10, ~00:42–00:55; a pasta
`resultados/p17_diagnostico_2026-10-10/` mantém o nome do dia do esperado, commit `d9c0677`).
`python docs\diagnostico\p17_diagnostico_k5.py analisar` refeito aqui, sem solver:

| | etapa 1 | final | ferramenta, etapa 1 | ferramenta, final |
|---|---|---|---|---|
| enfermeiros: diferença (h) | 42 | 42 | 42,0 | 42,0 |
| enfermeiros: horas mín.–máx. | 120–162 | 120–162 | — | — |
| enfermeiros: amplitude da fração (pp) | 23,86 | 23,86 | — | — |
| técnicos: diferença (h) | 30 | 30 | 30,0 | 30,0 |
| técnicos: horas mín.–máx. | 144–174 | 144–174 | — | — |
| técnicos: amplitude da fração (pp) | 17,05 | 17,05 | — | — |
| critério (soma das amplitudes) | 0,4091 | 0,4091 | 0,4091 | 0,4091 |

- **Log do HiGHS:** partida aceita com valor 0,4091; nenhuma solução melhor em 180 s (1.667 nós,
  475.109 iterações de LP); fim com primal 0,4091, dual ~1,2e-14 e gap de 100%.
- **Escalas:** 0 células diferentes entre a da etapa 1 e a final.
- **Etapa 1:** penalidade 21, gap 28,6% (em 09/10: 21 e 33,3%).
- **Veredito:** ESPERADO OK, desfecho SEM MELHORA.
- **Teste curto** (`resultados/p17_diagnostico_teste/`, 90 s + 20 s): marcado como teste num
  `LEIA_ME.txt`; o veredito dele não vale.
- **Commit `0adcc45`:** as duas pastas versionadas (`git add -f`).

**A2. `DECISOES.md`, "2026-10-10 — P17": FECHADA.** Sem defeito. Limitação: nos casos sem prova,
a etapa 2 não melhorou em nenhuma das 4 rodadas, nem no 8b (B2). O limite inferior do critério
ficou em ~0. A diferença entre colegas é reportada só em horas: há plantões de 6 h e de 12 h, e
contar plantões não compara cargas.

**A3. `NUMEROS_TCC.md`, seção 13 nova:**
- garantia "nunca piora": por construção e pelas conferências 2, 3 e 5;
- 3 casos de 09/10: sem melhora, **SEM RECONTAGEM INDEPENDENTE**;
- K5 de 11/10: sem melhora, com recontagem a partir das escalas gravadas, igual à ferramenta;
- ressalvas: 180 s, e a etapa 1 varia a cada rodada.

## B. Defeito de texto da tela (item c)

**B1. Esperado antes** (commit `ee8620c`):
- `docs/diagnostico/p17_frase_conferir.py` monta o `Resultado` com os indicadores gravados e
  confere a linha, sem solver. Nos casos de 09/10, o critério sai dos logs: diferença em horas
  ÷ 176 h, válido porque todos têm 44 h e nenhum tem férias.
- Antes da correção, deu "FRASE FALHA" nos 4 casos sem melhora, que é o próprio defeito.
- O esperado do 8b foi refeito no docstring: a linha tem de bater exatamente com a de "melhorou"
  ou com a de "não melhorou", conforme o critério.

**B2. Correção** (`src/ferramenta.py`; `modelo.py` intacto), só no caminho sem prova:
- `resolver_com_objetivo`: sem prova e com critério final não menor que o da etapa 1, devolve a
  escala da etapa 1. A salvaguarda da P14 já fazia isso quando o critério piorava; agora vale
  também para o empate. `etapa2` continua "ok".
- `Resultado.frase_vigente`: nesse caso, a linha é "Escala desta tela: a da etapa 1. O
  equilíbrio de carga não achou, no tempo disponível, escala mais equilibrada sem piorar o
  resultado da etapa 1."

**Resultados, um processo por teste** (`resultados/v122_2026-10-11/`):

| Passo | Resultado |
|---|---|
| `p17_frase_conferir.py` | FRASE OK (K5 de 11/10, Otávio, K5 e K6 de 09/10 → linha nova; 9d → linha com prova; sintético com melhora → linha atual sem prova) |
| `regressao.py --todos` | OK: 56, 58, 197, 219 = Tabela 6 |
| tela 8 | OK. **8b sem melhora**: critério 0,3409 → 0,3409 em 25 s, linha nova, 20/20 pedidos, gap 1,03% |
| tela 12 | OK. 12a com prova: "a da etapa 2, com a carga equilibrada entre colegas." |

**B3. O que ficou de fora, para decisão.** No caminho **com prova**, a etapa 2 não parte da
escala da etapa 1 e pode devolver outra escala de mesmo critério. Ali, dizer "a da etapa 1"
seria falso, e trocar a escala mudaria a demonstração. Por isso esse caminho não mudou. O caso
não foi observado: o 9d melhorou (36,4 → 4,5 pp), e os registros da demonstração não guardam o
critério da etapa 1, então não dá para conferir sem rodar.

**B4. Tag `v1.2.2`** no commit desta sessão. O `ESTADO_ATUAL.md` e o `LEIA_PRIMEIRO.md` citam a
v1.2.2.

## C. Pendentes de 10/10

- **C5.** `DECISOES.md`, entrada nova "2026-10-09 — Texto do TCC antecipado para 09/10" (texto de
  09 a 25/10, números congelados em 16/10, tela de 26 a 29/10, entrega em 04/11). A entrada de
  06/10 ("Cronograma") ganhou a marca "superada em parte", apontando para ela. No
  `ESTADO_ATUAL.md`, seção 2, o texto passou a "09–25/10/2026".
- **C6. Conferência do Cowork (só leitura):** nada inesperado.
  - `git status`: só as minhas alterações desta sessão.
  - Arquivos com data de 10/10: só os meus (os mesmos da conferência de 10/10, 20:52–21:39).
  - Arquivos com data de 11/10: a sua rodada do K5 e do teste (00:36–00:55) e o meu trabalho
    desta sessão (01:07 em diante).
  - Observação: o `INVENTARIO_dev.md` e a pasta `Claude outputs/`, ambos fora do git, não estão
    mais na pasta. Imagino que você os tenha movido na sua organização. Nenhum arquivo
    versionado foi afetado.
- **C7. Push** de commits e tags: feito.

## Commits desta sessão

`0adcc45` (P17 fechada, NUMEROS seção 13, pastas do diagnóstico), `ee8620c` (esperado do item c,
antes) e o commit da v1.2.2 (correção, logs, C5, notas e este relatório).
