# Relatório de 06/10/2026 (a) — sessão sem supervisão

## Para o Otávio

- **Os seis itens foram feitos.** A suíte final passou inteira (17 de 17), e a tag **`v1.0`** foi criada e enviada.
- **Notas antigas:** nenhuma foi movida. As quatro têm achados que só existem nelas; a lista está no item 2.
- **Números para o texto:** `resultados/NUMEROS_TCC.md`. Quatro números ficaram com ORIGEM NÃO ENCONTRADA no comando que os reproduz.
- **Para decidir:** o que fazer com o conteúdo exclusivo das quatro notas.
- `git pull` traz tudo; `git pull --tags` traz a tag.

## Status por item

| Item | Status | Commit |
|---|---|---|
| 1. `resultados/NUMEROS_TCC.md` | **feito** | `0f96caf` |
| 2. Notas antigas em `docs/` | **feito**: nenhuma movida (conteúdo exclusivo em todas) | `1518318` |
| 3. `GUIA_DE_USO.md` | **feito**: capturas finais, textos atuais dos alertas, grau e pedidos | `9d112da` |
| 4. Suíte completa final | **feito**: 17 de 17 OK | `ebdaa4f` |
| 5. Tag | **feito**: `v1.0` | tag `fa2e2c1` → commit `c64dcf9` |
| 6. Este relatório | feito | o seguinte |

Nada falhou. Respeitei as travas: nada mudou em `src/` nem nos testes, nada foi apagado ou movido, e não usei reset, rebase nem force push.

## Item 1 — NUMEROS_TCC.md

Um número por linha, com valor, o que mede, origem, comando, conferência e ressalva. As seções são:
1. validação do motor;
2. Experimento A;
3. Experimento B;
4. piso forçado;
5. P1, curva de 03/10;
6. P1, rodada com folga;
7. limites de 600 s e 180 s, com a derivação;
8. testes 9a–9d;
9. demonstração da clínica (20, 19 e 18 técnicos);
10. escalabilidade de 28/09.

Os tempos aparecem só como limite operacional, com a máquina e o solver.

**ORIGEM NÃO ENCONTRADA:**
- o comando da rodada de `medium_late05` (107 contra 716);
- o script que gerou as 207 escalas heurísticas e as 36 adversárias da validação de 18/09. O resultado está no DECISOES; o script não está no repositório.

**SEM CONFERÊNCIA**, por não ter avaliador, Tabela 6 nem conta registrada antes:
- os mínimos e máximos individuais do Experimento B;
- os estados do solver na P1 (prova até 80 etc.);
- o piso de 13,64 pp da rodada com folga, porque a conta foi feita depois;
- a maior parte dos indicadores da demonstração (fração cumprida, horas não utilizadas, diferença entre colegas).

## Item 4 — Suíte completa final

Configuração:
- Um teste por processo. Cada log está em `resultados/suite_2026-10-06/`, e o resumo em `suite.json`.
- O executor da suíte ficou no scratchpad, fora do repositório, porque as travas proíbem mexer em `src/` e nos testes.
- O pico de memória é a soma do `PeakWorkingSetSize` dos processos do teste, lida a cada 5 s. Nos testes de poucos segundos (4b, 7.4, XML) a leitura pode ter subestimado o pico.

Máquina: i5-10210U, 12 GB, Windows 11, HiGHS 1.15.1 via appsi. Os tempos são limite operacional.

| Teste | Resultado | Tempo (s) | Pico de memória (MB) | Menor memória livre (MB) |
|---|---|---|---|---|
| regressao --todos | OK | 121.6 | 478 | 1481 |
| testes_entrada | OK | 19.5 | 106 | 1704 |
| tela 1-2 | OK | 413.6 | 306 | 919 |
| tela 3 | OK | 192.0 | 310 | 2103 |
| tela 4 | OK | 184.4 | 509 | 2221 |
| tela 4b | OK | 5.9 | 39 | 2688 |
| tela 5 | OK | 191.5 | 445 | 1677 |
| tela 7.1 | OK | 187.7 | 354 | 2080 |
| tela 7.2 | OK | 223.4 | 249 | 2390 |
| tela 7.3 | OK | 930.4 | 560 | 1944 |
| tela 7.4 | OK | 5.8 | 39 | 2584 |
| tela 8 | OK | 225.2 | 445 | 2227 |
| tela 9 | OK | 515.2 | 381 | 2060 |
| tela 9b-sem-teto | OK | 11.6 | 168 | 2545 |
| tela 9c-tela | OK | 29.4 | 334 | 2461 |
| XML gerar | OK | 5.8 | 23 | 2730 |
| XML comparar | OK | 11.5 | 18 | 2721 |

Conferências dentro dos logs:
- nenhum log contém "FALHA";
- a regressão deu 56, 58, 197 e 219, iguais à Tabela 6;
- o 9c atingiu o piso (0 e 4,55 pp); a prova saiu dentro do limite e é só informativa;
- o 7.4 mostrou os dois motivos (horas e alternância);
- os 544 XML são idênticos ao commit `cec3d8e`, com 0 diferentes.

## Item 5 — Tag

- A nota de fechamento do `ESTADO_ATUAL.md` (ferramenta fechada, v1.0) está no commit `c64dcf9`.
- A tag anotada `v1.0` (objeto `fa2e2c1`) aponta para esse commit e foi enviada (`git push --tags`).
- Confirmado no servidor: `refs/tags/v1.0` → `c64dcf9`.

## Item 2 — Notas antigas em `docs/`: NENHUMA movida (feito)

Para cada nota, procurei os achados citáveis em `DECISOES.md`, `VIRADA_ESCOPO_2026-09-24.md` e `ESTADO_ATUAL.md`. **As quatro têm conteúdo que só existe nelas**, então ficam em `docs/`. Não movi nem apaguei nada.

| Nota | Já está nos arquivos ativos | Só existe na nota |
|---|---|---|
| `nota_conferencias_contrato_2026-09-22.md` | O piso forçado em faixas (54–61% sprint, 73–81% long), no ESTADO_ATUAL | (1) `long01`/`long02` são a mesma instância com outros contratos, e o lote *early* tem 2 cenários com 10 e 5 variações de contrato (hash dos blocos do XML); (2) correlação dentro do grupo de contrato (r = 0,551; R² 0,714 e 0,835) e os dois eixos da exposição, contrato × habilidade (`HeadNurse` no teto 5); (3) a "cauda baixa" de teto 5 das longas, contra a contagem de contratos das sprints; (4) a tabela do piso por instância (D, C, E, Z*) |
| `nota_intervalo_individual_2026-09-22.md` | O método do intervalo [mín., máx.] (DECISOES, Experimento B) | A tabela de intervalos por profissional de `sprint01`/`sprint02`; soma dos mínimos individuais 15, contra piso coletivo 30 ("forçado, mas não atribuído"); a correção "teto menor, mais exposto" não se sustenta, e o mecanismo da folga do grupo; profissional 9 quase invariante [1, 3] |
| `nota_piso_forcado_2026-09-22.md` | As faixas E/Z* (ESTADO_ATUAL) | Avaliador oficial conta o teto **por atribuição** (`cost = excess`, até 13); `MaxNumAssignments` ativo com peso 1 em todos os contratos das 15 instâncias *early*; soma dos excessos = D − C com **igualdade exata** nas quatro, e ninguém abaixo do próprio teto ("no ótimo o teto vira piso"), com a separação entre o que é teorema e o que é observação |
| `para_orientacao_2026-09-23.md` | 36 nos dois regimes; 40 contra 37–38; o achado dos 116 do avaliador e a varredura de 304 padrões (ESTADO_ATUAL) | As diferenças +5,3% e +8,1%; o descanso medido (36 h e 16 h, contra 36 h e 11 h exigidos); a decisão (a)/(b) sobre o padrão das 36 h no arquivo — não achei registro dela nos três arquivos; a lista de pendências daquela data |

**Para decidir:** o conteúdo exclusivo dessas notas deve virar entrada no DECISOES (para depois as notas irem ao histórico) ou elas ficam em `docs/` como metodologia ativa? Pela trava de hoje, não reescrevi nada.

---

## LEVAR PARA O PROJETO DE REDACAO

- **`ESTADO_ATUAL.md`**: nota de 06/10 — ferramenta fechada, v1.0, suíte 17 de 17.
- **`resultados/NUMEROS_TCC.md`** (novo): o inventário dos números citáveis, com origem e conferência. É o arquivo de referência para o capítulo de resultados.
- **`GUIA_DE_USO.md`**: capturas finais e textos atuais.
- `DECISOES.md`, `PROPOSTAS.md` e `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
- **Para decidir:** o conteúdo exclusivo das quatro notas de `docs/` (item 2) vira entrada no DECISOES, para as notas irem ao histórico, ou elas ficam como metodologia ativa?
