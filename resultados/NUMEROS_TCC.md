# Números que podem ir ao texto do TCC

Inventário de 06/10/2026, montado **só lendo arquivos**, sem rodar solver. Um número por linha.

**Conferência** é uma de três:
- avaliador oficial da competição;
- Tabela 6 de Santos et al. (2016);
- conta aritmética registrada **antes** de rodar.

Sem nenhuma das três, a linha leva **SEM CONFERÊNCIA**, com o motivo. Sem origem achada, **ORIGEM NÃO ENCONTRADA**.

Tempo é sempre **limite operacional**, nunca resultado (CLAUDE.md).

**Condição das afirmações de ótimo provado (09/10, decisão do Otávio).** O HiGHS declara
"ótimo" quando o gap relativo fica em até 0,01% (tolerância padrão). A prova vale como ótimo
inteiro porque 0,0001 × objetivo < 1 em todos os casos, exceto na P1 de 03/10 com N = 40, 60 e 80
(seção 5); nesses três, o limite inferior registrado no log é igual ao objetivo (gap 0 exato).
Conferência só de leitura em `resultados/relatorio_2026-10-09c.md` (continuação de 09/10, item 3).
A etapa 2 tem objetivo contínuo (amplitude da fração do contrato) e fica fora deste critério; a
tolerância nela é desprezível (0,0005 pp sobre 4,55 pp no 9c).

**Máquina e solver das medições de 02 a 05/10:** Intel Core i5-10210U (4 núcleos, 8 threads), 12 GB, Windows 11, Python 3.11.9, HiGHS 1.15.1 via `appsi_highs`. Medições anteriores a 02/10 dizem o ambiente na própria linha.

Os comandos rodam da raiz, com a `.venv` ativa.

---

## 1. Validação do motor

| Valor | O que mede | Origem | Comando | Conferência | Ressalva |
|---|---|---|---|---|---|
| 56 | ótimo de `sprint01` (sprint_early01) | `resultados/consolidado.csv`; saída do `regressao.py` | `python src\regressao.py --todos` | Tabela 6 de Santos et al. (2016); **avaliador oficial reconfirmado em 06/10** com `src/validar.py` corrigido (commit `e9e0da4`): `python src\validar.py instancias/sprint/sprint/sprint01.xml resultados/sprint01_completo.xml --objetivo 56` → "os dois valores batem" | a coluna `avaliador_oficial` do `consolidado.csv` (18/09) não tem origem documentada; a reconfirmação de 06/10 a substitui |
| 58 | ótimo de `sprint02` | idem | idem | Tabela 6; **avaliador oficial reconfirmado em 06/10** com `src/validar.py` corrigido (commit `e9e0da4`): `python src\validar.py instancias/sprint/sprint/sprint02.xml resultados/sprint02_completo.xml --objetivo 58` → "os dois valores batem" | idem |
| 197 | ótimo de `long01` | idem | idem | Tabela 6; **avaliador oficial reconfirmado em 06/10** com `src/validar.py` corrigido (commit `e9e0da4`): `python src\validar.py instancias/long/long/long01.xml resultados/long01_completo.xml --objetivo 197` → "os dois valores batem" | idem |
| 219 | ótimo de `long02` | idem | idem | Tabela 6; **avaliador oficial reconfirmado em 06/10** com `src/validar.py` corrigido (commit `e9e0da4`): `python src\validar.py instancias/long/long/long02.xml resultados/long02_completo.xml --objetivo 219` → "os dois valores batem" | idem |
| ~~107 (publicado) contra 716 (obtido)~~ **SUPERADA em 06/10** pela linha seguinte | ~~`medium_late05` não fechou no limite (520 s)~~ | `resultados/consolidado.csv` | ORIGEM NÃO ENCONTRADA (comando da rodada) | avaliador dá 716 à escala obtida | ambiente "HiGHS via SciPy, container de desenvolvimento", 15/09 |
| 107 (publicado) contra **224** (obtido); limite inferior 63; gap 71,88%; estado `maxTimeLimit` (sem prova) | `medium_late05`, alvo de validação, rodado de novo em 06/10 com limite de 3.600 s | `resultados/medium_late05_2026-10-06/` (`resumo.json`, `highs.log`, `medium_late05_escala.xml`) | `python docs\rodar_medium_late05.py` (esperado registrado antes, commit `b9921fb`) | **avaliador oficial: 224**, reconfirmado em 06/10 com `src/validar.py` corrigido (commit `e9e0da4`): `python src\validar.py instancias/medium/medium_late_xml/medium_late05.xml resultados/medium_late05_2026-10-06/medium_late05_escala.xml --objetivo 224` → "os dois valores batem"; `avaliacao.py`: 224 | não reproduz o ótimo de 107: entra como limite declarado (P9: não fechar antes de 04/11). 3.604 s de relógio é **limite operacional** (i5-10210U, `appsi_highs`, HiGHS 1.15.1). 15.320 variáveis e 13.060 restrições |
odar_medium_late05.py` (esperado registrado antes, commit `b9921fb`) | **avaliador oficial: 224** na escala gravada (`java -cp "avaliador/*" dds.nrp.core.evaluation.ScheduleEvaluator ...`); `avaliacao.py`: 224 | não reproduz o ótimo de 107: entra como limite declarado. 3.604 s de relógio é **limite operacional** (i5-10210U, `appsi_highs`, HiGHS 1.15.1). 15.320 variáveis e 13.060 restrições |
| 207 escalas em 69 instâncias | penalidade de `avaliacao.py` idêntica à do avaliador, par a par (profissional × restrição) | **não encontrada após busca no histórico do git (11/10)**: nem o script nem as escalas (descrição em `DECISOES.md`, "2026-09-18 — Semântica das flexíveis validada fora do modelo") | ORIGEM NÃO ENCONTRADA (o script das escalas heurísticas não está no repositório) | avaliador oficial | escalas heurísticas, não do modelo; **registro histórico (`DECISOES.md`, 18/09); não citar no capítulo de resultados** |
| 36 escalas adversárias em 6 instâncias | idem, casos construídos | **não encontrada após busca no histórico do git (11/10)**: nem o script nem as escalas | ORIGEM NÃO ENCONTRADA (script) | avaliador oficial | 207 + 36 = as "243 escalas de teste" da especificação; **registro histórico (`DECISOES.md`, 18/09); não citar no capítulo de resultados** |
| 116 contra 0 | cobranças do avaliador ao padrão (noturno, folga, diurno) contra violações reais | `ESTADO_ATUAL.md` (P13); `docs/para_orientacao_2026-09-23.md` | `python docs\conferencia_padrao_avaliador.py` | o próprio avaliador | demonstra o comportamento, não o código do avaliador |
| 304 padrões em 59 arquivos, nenhum no formato | varredura do INRC pelo formato lido errado | idem | idem | aritmética sobre os arquivos | — |

**Caracterização do `medium_late05`** (lida do arquivo em 06/10, sem solver; detalhe no
`resultados/relatorio_2026-10-06c.md`, item 3):

| Valor | O que é | Origem |
|---|---|---|
| 30 | profissionais, em 3 contratos com gente (15, 10 e 5); um quarto contrato, `night`, não tem ninguém | `instancias/medium/medium_late_xml/medium_late05.xml`, lido por `src/parser.py` |
| 28 | dias do horizonte (01/01/2010 a 28/01/2010) | idem |
| 5 | tipos de turno, todos de 8 h (E, D, DH, L, N); `DH` exige `HeadNurse`, que 3 pessoas têm | idem |
| 390 | pedidos de folga (300 por turno, 90 por dia) | idem |
| quase todas | restrições flexíveis ativas, com pesos de 1 a 10 | idem |
| 7 | padrões indesejados por contrato | idem |

**Ressalva.** É **comparação de estrutura** com a instância da demonstração (30 pessoas em
12×36, 2 turnos de 12 h, CLT rígida, só os pedidos de folga flexíveis). Ter quase tudo flexível e
com peso é **explicação provável** da diferença de dificuldade, **não causa demonstrada**:
nenhum experimento isolou os fatores.

## 2. Experimento A (efetivo mínimo; escopo anterior, hoje validação)

Origem: `resultados/experimento_a.csv`. Comando: `python src\experimento_a.py`. A conferência é a coluna `conferencia` do CSV mais a do texto.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| 36 em 20 de 20 células | menor quadro viável com demanda constante (5 graus × 2 regimes × 2 regras); 35 inviável, com prova | avaliador oficial nas escalas de 36 (`ok`); conta: 5.920 h ÷ 168 h = 35,24 | as 20 células são a mesma aritmética, não 20 testes independentes |
| 35,24 | quadro de referência do Parecer, demanda constante | conta: 5.920 ÷ 168 | — |
| 40 (12×36) | menor quadro viável com metade e com a forma inteira da variação medida em `long01` (intermediário, regra "teto") | medição direta de descanso no relógio (`docs\conferencia_descanso_escala.py`). **Não** o avaliador: ele cobra o padrão das 36 h, que aqui é rígido (P13) | uma forma de variação só (29 contra 20 atribuições, `long01`) |
| 38 (8 h, metade da variação) | idem, regime de 8 h | avaliador oficial (`ok`) | idem |
| 37 (8 h, variação inteira) | idem | avaliador oficial (`ok`) | idem |
| +5,3% e +8,1% | distância do 12×36 ao piso, nas duas variações | aritmética sobre o CSV (`distancia_do_piso`) | — |
| 36 h e 16 h (exigidos 36 h e 11 h) | menor descanso medido entre turnos, 12×36 e 8 h | medição no relógio | fonte: `docs/para_orientacao_2026-09-23.md`; não está no CSV |
| 44,4 s (12×36, quadro 36) | tempo de CPU | — | **limite operacional**, ambiente de 23/09 |

## 3. Experimento B (concentração de penalidade, INRC)

Origem: `resultados/experimento_b_resumo.csv` e `experimento_b.csv`. Comando: `python src\experimentos.py` (`--por-pessoa` para os intervalos).

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| 7 a 18 (`sprint01`); 7 a 18 (`sprint02`); 11 a 19 (`long01`); 14 a 20 (`long02`) | menor e maior penalidade possível do mais penalizado, entre as escalas de custo ótimo | Z* pela Tabela 6. Os mínimos e máximos: **SEM CONFERÊNCIA** externa — medidos pelo modelo; a decomposição por profissional fecha contra `avaliacao.py` na regressão, e esse foi validado contra o avaliador | — |
| 1,25 / 1,21 / 2,74 / 3,13 | concentração inevitável (sprint01, sprint02, long01, long02) | SEM CONFERÊNCIA (razão sobre os números acima) | — |
| 2,57 / 2,57 / 1,73 / 1,43 | margem de gestão | SEM CONFERÊNCIA | — |
| intervalo [mín., máx.] por profissional em `sprint01` e `sprint02`; soma dos mínimos 15, contra piso coletivo 30 | intervalo individual entre escalas ótimas | SEM CONFERÊNCIA | tabela só em `docs/nota_intervalo_individual_2026-09-22.md` |
| 203,7 s e 165,5 s | CPU da rodada `--por-pessoa` | — | **limite operacional** |

## 4. Piso forçado (aritmética do custo, INRC)

Origem: `docs/nota_piso_forcado_2026-09-22.md` e `docs/nota_conferencias_contrato_2026-09-22.md`. Comandos: `python docs\conferencia_piso_forcado.py` e `python docs\conferencia_contratos.py`.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| 30, 32, 150, 160 | excesso forçado D − C (sprint01, sprint02, long01, long02) | conta sobre os arquivos; igual à soma dos excessos que o avaliador reporta nas escalas ótimas | — |
| 54%, 55%, 76%, 73% | fração de Z* já forçada (E ÷ Z*) | Tabela 6 (Z*) e aritmética (E) | — |
| 54% a 61% (10 sprint_early); 73% a 81% (5 long_early) | idem, no lote *early* inteiro | Tabela 6 e aritmética | faixas estreitas porque a demanda é a mesma dentro do track; não se estende a `late` nem `hidden` |
| custo = excesso, até 13 | o avaliador conta o teto por atribuição excedente | avaliador oficial | — |
| igualdade exata em 4 de 4; ninguém abaixo do próprio teto | soma dos excessos = D − C nas escalas ótimas | avaliador oficial e contagem na escala | observação nas quatro escalas, não teorema |

## 5. Ferramenta — P1, curva de 03/10 (caso mais apertado, sem folga)

Origem: `resultados/escalabilidade_objetivo.csv` e `resultados/escalabilidade_objetivo/p1_2026-10-03_ferramenta.log`. Comando: `python src\escalabilidade_objetivo.py --tempo 900`.

Configuração: 12×36, 44 h para todos, 2 pedidos por pessoa (semente 20261002 + N), 900 s por etapa.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| prova fecha até N = 80 | etapa 1 com ótimo provado em 36, 40, 60 e 80 | **SEM CONFERÊNCIA** (estado do solver). A penalidade recontada a partir da escala é igual à do solver em todos os tamanhos com escala | demanda = 14N, todos em 168 h |
| N = 120: sem prova, gap 3,16%; 63 pedidos negados, limite inferior 61 | etapa 1 no limite | SEM CONFERÊNCIA (log do HiGHS) | — |
| N = 200: sem escala em 900 s; limite inferior de 111 pedidos negados | etapa 1 no limite | SEM CONFERÊNCIA (log do HiGHS) | — |
| 112, 140, 224, 322, 504 | turnos de enfermeiro em posto de técnico (N = 36, 40, 60, 80, 120) | conta: técnicos × 14 contra postos de técnico, feita **depois** de rodar | forçados pela conta |
| 21, 21, 29, 50, 63 | pedidos de folga negados (de 72, 80, 120, 160, 240) | SEM CONFERÊNCIA | — |
| amplitude 0 em todos | etapa 2 degenerada | conta (demanda = capacidade), feita depois | a etapa 2 não é medida por esta curva |
| 39,8 / 168,0 / 130,1 / 693,0 / 901,9 / 902,8 s | tempo da etapa 1 | — | **limite operacional**; uma medição por tamanho; não monotônico |
| 39,0 / 54,3 / 128,9 / 235,1 / 345,8 s | tempo até a primeira escala legal (HiGHS) | — | **limite operacional** |
| 3.696 a 20.496 variáveis; 12.640 a 69.444 restrições | tamanho do modelo | — | — |

## 6. Ferramenta — P1, rodada com folga de 05/10

Origem: `resultados/escalabilidade_objetivo_folga.csv`; logs `folga_teste_N40_2026-10-05.log` e `folga_2026-10-05.log`. Comando: `python src\escalabilidade_objetivo.py --folga`.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| 13,64 pp nos três tamanhos | amplitude da fração do contrato depois da etapa 2 (6,82 + 6,82) | conta do piso feita **DEPOIS** do resultado: SEM CONFERÊNCIA no sentido estrito | a conta explica, não previu |
| 34,09 / 20,45 / 27,27 pp | amplitude na escala da etapa 1 | SEM CONFERÊNCIA | — |
| etapa 1 ótima em 44, 66 e 88 | prova da etapa 1 | SEM CONFERÊNCIA (estado do solver) | — |
| 18,1 / 45,6 / 81,1 s | tempo até 90% da redução final na etapa 2 | — | **limite operacional**; coincide com a primeira escala da etapa 2 |
| gap 19,6% / 26,1% / 37,5% | gap da etapa 2 em 900 s | — | fraqueza do limite inferior, não distância real |

## 7. Limites de tempo da tela

| Valor | O que mede | Origem | Conferência | Ressalva |
|---|---|---|---|---|
| 600 s | limite da etapa 1 | `src/ferramenta.py` (`TEMPO`); decidido em 05/10 | — | decisão, não medição |
| 180 s | limite da etapa 2 = max(120 s; 1,5 × 81,1 s = 121,7 s), arredondado para cima ao minuto | `ferramenta.TEMPO_ETAPA2`; `DECISOES.md`, "Carga por contrato", item i | conta sobre o 81,1 s da rodada com folga | o 81,1 s é limite operacional desta máquina |

## 8. Testes da carga por contrato (9a–9d)

Origem: `src/testes_ferramenta.py`. Comandos: `python src\testes_ferramenta.py 9` e `... 9b-sem-teto`. Logs da suíte de 06/10 em `resultados/suite_2026-10-06/`.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| 112 h (teto 120 h); 168 h (teto 176 h) | maior carga entre os de 30 h e entre os de 44 h (9a) | esperado antes (03/10): ninguém passa do teto | — |
| 14 plantões | máximo no 12×36 com 44 h (9b) | esperado antes | não separa alternância de teto |
| 14 plantões, provado | máximo sem teto de horas e sem `MaxNumAssignments` (9b-sem-teto) | esperado antes (03/10) | quem limita é a alternância |
| 0 e 4,55 pp | amplitude entre enfermeiros e entre técnicos (9c) | **conta registrada antes**, commit `08603c6` | — |
| 384 h e 232 h; +24,9 pp | horas não utilizadas (enf., téc.); diferença entre categorias (9c) | conta antes (`08603c6`) | — |
| "1 plantão (8 h)" e "nenhuma (0 h)" | diferença entre colegas na tela (9c) | conta antes (05/10) | — |
| 36,4 → 4,5 pp | o critério cai da etapa 1 para a etapa 2 (9d) | esperado antes: estritamente menor | o 36,4 depende da escala da etapa 1 |
| 146,9 s | prova da etapa 2 do 9c, rodando sozinho | — | **limite operacional**; já falhou com outro processo junto |

## 9. Demonstração: clínica médica (05/10, 21h; refeita em 09/10 com o roteiro corrigido)

Origem: `docs/demonstracao/rodada1_tela.txt`, `rodada2_19tec_tela.txt` e `rodada2_18tec_tela.txt`, com capturas e planilhas ao lado. Comando: `bash docs/demonstracao/rodar_rodada.sh rodada1` (e `rodada2_19tec --tec 19`, `rodada2_18tec --tec 18`).

Configuração: equipe 10 + 20, 12×36, de 02/11 a 29/11/2026.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| 20 técnicos: admite, 0 alertas | rodada 1 | conta registrada antes (`docs/demonstracao/cortes_esperados.md`, commit `ee7af24`) | — |
| 24 | turnos de enfermeiro em posto de técnico, 20 técnicos | conta antes: mínimo 24 | igual ao mínimo |
| 19 técnicos: admite, 1 alerta (QP completo 29,85; núcleo 25,96) | primeira transição | conta antes | — |
| 36 | turnos de enfermeiro em posto de técnico, 19 técnicos | conta antes: mínimo 36 | igual ao mínimo |
| 18 técnicos: "Falta 1; o menor quadro viável é 29"; diagnóstico "Alternância" (ter 03/11 e qua 04/11: 28 plantões, 27 pessoas) | trava | conta antes, palavra por palavra | — |
| 34 | turnos de enfermeiro em posto de técnico na escala de 29 (10 + 19) | SEM CONFERÊNCIA | — |
| 84 h contra 32 h e 40 h | carga por grupo de pacientes → grau intermediário, 33% | conta antes (commit `0618788`) | — |
| 26,08 / 30,00; 25,96 / 29,85; 25,82 / 29,70 | QP núcleo / completo (30, 29 e 28 pessoas) | aritmética do Parecer: 156 h/dia × 7 ÷ CHS; × 1,15 | — |
| 6 de 6 | pedidos atendidos nas três rodadas | SEM CONFERÊNCIA | — |
| 68%–100%; 82%–100%; 75%–100% | contrato cumprido (mín.–máx.) | SEM CONFERÊNCIA | — |
| 432 / 108 h; 288 / 108 h; 312 / 116 h | horas de contrato não utilizadas (enf. / téc.) | SEM CONFERÊNCIA | — |
| 1 e 0,6 plantão; 0,2 e 0,6; 0,9 e 0,6 | diferença máxima entre colegas (enf. e téc.) | SEM CONFERÊNCIA | a etapa 2 tem tempo limitado e pode variar entre rodadas |
| 301–331 MB (servidor + solver); 569–600 MB (Chrome) | pico de memória por rodada | — | **limite operacional** |

**Defeito e correção (08–09/10).** Nas rodadas de 05/10, o roteiro que digita a entrada na
tela (`docs/demonstracao/capturas.py`) pôs a demanda de feriado de **sex 20/11 em ter 24/11**.
Achado em 08/10 por `docs/demonstracao/conferir_planilhas.py`, que compara a planilha baixada
com a demanda **declarada** no caso. Corrigido (o roteiro acha a linha pela data e confere a
colagem); esperado registrado antes (commit `882edf1`); as três rodadas refeitas em 09/10, de
madrugada, com o conferidor passando nas três (cobertura igual à declarada em todos os dias,
rígidas, descanso, teto, férias). **Todos os valores da tabela acima se confirmaram, iguais**:
24, 36 e 34 turnos de enfermeiro em posto de técnico (os mínimos da conta), 6 de 6 pedidos,
contrato cumprido 68–100%, 82–100% e 75–100%, horas não utilizadas 432/108, 288/108 e 312/116 h,
diferença entre colegas 1 e 0,6, 0,2 e 0,6, 0,9 e 0,6 plantão. As escalas mudaram (393 a 422
células diferentes; 20/11 agora com a cobertura de feriado); os agregados não, porque as horas
de demanda são as mesmas (4.308 h) e a contagem de enfermeiro em posto de técnico já estava no
mínimo aritmético. Detalhe em `resultados/relatorio_2026-10-09a.md`.

## 10. Escalabilidade de 28/09 (objetivo trivial)

Origem: `resultados/escalabilidade.csv`. Comando: `python src\escalabilidade.py`.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| ótimo provado em 6 de 6 (N de 36 a 200) | viabilidade, com objetivo degenerado (ótimo = 0) | SEM CONFERÊNCIA (estado do solver); descanso medido `ok` | mede viabilidade, não otimização (P1) |
| 549,2 s (N = 200) | tempo de CPU | — | **limite operacional**; a P1 substitui esta curva como medida do produto |

## 11. Bateria de entradas (07 e 08/10)

Origem: `resultados/bateria_2026-10-07/` e `resultados/bateria_2026-10-08/`; relatórios
`resultados/relatorio_2026-10-07a.md`, `relatorio_2026-10-08a.md` e `relatorio_2026-10-08b.md`.
Comandos: `python docs\diagnostico\bateria_rodar.py <caso>`,
`python docs\diagnostico\bateria_propriedades.py <caso> <derivado>`,
`python docs\diagnostico\k4_dominancia.py`. Esperado: a conta independente de
`docs/diagnostico/bateria_desenho.py` (commit `62bbf4d`) e os cabeçalhos dos scripts,
commitados antes de rodar.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| 24 casos, 0 falhas | nível 1 (P01–P18) e nível 2 (K1–K6): toda escala passa em cobertura, descanso no relógio, teto de horas e férias, conferidos fora do modelo | conta registrada antes (`62bbf4d`) | cobertura de pares de áreas da tela, não de todas as entradas possíveis |
| 3 de 3 | casos inviáveis pela conta (P05, P11, K2) que dão "faltam N", com menor quadro coerente com a conta | conta registrada antes | — |
| 96 derivados, 0 violações (88 ok, 8 inconclusivos) | propriedades 2 (monotonia: +1 pessoa, +1 posto, +1 dia de férias) e 3 (ordem dos profissionais), só etapa 1, 600 s | o que cada derivado exige foi registrado antes (`bateria_propriedades.py`, commit `ff54b2b`) | os 8 inconclusivos são todos de K3 e K4, cuja base terminou "não decidido": sem veredito na base, não há o que comparar |
| escala legal com 17 (12 + 5) existe no K4 | escala achada para 11 + 6 (K3 + 1 técnico) fixada no modelo do K4: `conferir_rigidas` ok, descanso cumpre, teto ok, modelo "optimal" | esperado registrado antes (commit `57de0c4`) | as duas instâncias diferem só na pessoa "11" (técnico numa, enfermeiro na outra); enfermeiro cobre todo posto de técnico |
| K4 sem escala em 600 s (07/10), em ~1.909 s (08/10) e K4/embaralhado sem escala em 600 s | **variação de desempenho do solver na fronteira** (folga 1 pela conta), não defeito: a escala existe | idem | **limite operacional**; o de ~1.909 s foi interrompido por falta de memória. Vai para as limitações: casos de fronteira podem não ser decididos no tempo e na memória disponíveis |
| K3 (16): não determinado | sem escala em 600 s (07/10 e 08/10, 4 derivados) | — | não rodado de novo com tempo longo (decisão do Otávio, 08/10) |
| 100 casos, estratificados pela conta: 40 folga clara, 30 fronteira, 30 inviáveis | nível 3 sorteado em 08/10 (semente 20261008), rodado em 09/10 | esperados da conta commitados antes (`b8ce2ae`) | **a folga clara ficou concentrada no 8 h (26 de 40; 12×36 9, 6 h + 12 h 5)**: a propriedade 5 (folga clara não termina sem escala) fica mais testada nesse modelo; a fronteira concentra-se no 12×36 (14) e no 6 h + 12 h (14) |
| 100 casos, 0 falhas | nível 3, propriedades 1 (93 escalas conferidas fora do modelo), 4 (honestidade), 5 (40 de 40 de folga clara admitem) e 6 (nenhum dos 30 inviáveis pela conta admitido); só etapa 1, 600 s | esperados da conta commitados antes (`b8ce2ae`); detalhe em `resultados/relatorio_2026-10-09a.md` | 63 admitem, 30 "faltam N" (20 provados pelo piso, 10 pelo solver) |
| 7 de 100 não decididos, todos no 6 h + noturno de 12 h | nível 3: 6 sem resposta em 600 s, 1 no limite de 15 min por caso (2 da fronteira, 5 dos inviáveis) | — | **limite operacional**; mesma família do K3/K4: vai para as limitações. Nos inviáveis, o quadro informado foi dado como insuficiente pela conta e a busca parou sem afirmar o menor viável |

## 12. Tempo-limite da etapa 1 (09/10, só leitura)

Origem: `docs/diagnostico/analise_tempo_limite.py`; saída em
`resultados/p14_p15_2026-10-09/analise_tempo_limite.md`; texto em
`resultados/relatorio_2026-10-09b.md`, parte C. **Afirmação fraca:** i5-10210U, HiGHS 1.15.1
via `appsi_highs`, parâmetros padrão, instâncias da bateria (até 20 pessoas, 28 dias).
Justificativa operacional do limite de 600 s, não resultado.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| 149 de 161 (93%) | resoluções da etapa 1 na bateria que provaram o ótimo antes de 600 s; nelas, a última melhora vem antes da prova, então os 600 s a cobrem | estado do solver gravado em cada JSON | só as resoluções isoláveis (admite na 1ª tentativa); a bateria não gravou o log do HiGHS, então não há tempo até a 1ª solução nem até a última melhora dela |
| 274 s | maior tempo até a prova, nessas 149 (P10, 6 h + 12 h); mediana de 1 a 3 s por modelo e estrato | — | **limite operacional** |
| 12 de 161 | resoluções sem prova em 600 s: todas da família de fronteira do 6 h + noturno de 12 h (K3 a K6 e derivados) | — | a última melhora delas é desconhecida |
| 826 s | última melhora no único log longo dessa família (K6, 15 + 5, limite de 3.600 s): aos 600 s a melhor escala valia 19, o ótimo 18 veio aos 826 s e foi provado aos 1.077 s | log do HiGHS (`resultados/diagnostico_2026-10-07/A3a_15mais5_3600s.log`) | uma instância só |

## 13. P17 — etapa 2 sem prova (09 e 11/10)

Origem: `resultados/fechar_v12/p17_otavio.log`, `p17_K5.log` e `p17_K6.log` (09/10; mesmo
conteúdo em `resultados/p14_p15_2026-10-09/p17_*.json`) e `resultados/p17_diagnostico_2026-10-10/`
(K5, rodada em 11/10). Comandos: `python docs\diagnostico\p14_conferir.py <caso> --p17` e
`python docs\diagnostico\p17_diagnostico_k5.py rodar` (o `analisar` refaz a recontagem sem
solver). Decisão: `DECISOES.md`, "2026-10-10 — P17" (fechada em 11/10). **Afirmação fraca:**
i5-10210U, HiGHS 1.15.1 via `appsi_highs`, limites da tela (600 s + 180 s). Diferença entre
colegas só em horas: nesses casos há plantões de 6 h e de 12 h, e contar plantões não compara
cargas.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| a etapa 2 sem prova nunca piora a etapa 1 | garantia: a etapa 2 parte da escala da etapa 1, com "penalidade ≤ valor da etapa 1" como restrição; no fim, o critério de equilíbrio não sobe | **por construção** (a partida cumpre a restrição; ver `DECISOES.md`, P14 e P17) e conferências 2, 3 e 5 do `p14_conferir.py --p17` (enfermeiros em posto de técnico, diferença por categoria e pedidos, contra a etapa 1 da mesma rodada) nos 3 casos de 09/10 | — |
| sem melhora em 3 de 3 (09/10) | Otávio (20 + 10, 6 h + 12 h): penalidade 57, gap 17,5%, diferença 60 h (enf.) e 24 h (téc.); K5 (13 + 5): 21, gap 33,3%, 42 h e 30 h; K6 (15 + 5): 18, gap 5,6%, 48 h e 18 h; final = etapa 1 nos três | **SEM RECONTAGEM INDEPENDENTE**: as escalas não foram gravadas; os números são os da ferramenta | limite de 180 s na etapa 2; a etapa 1 varia a cada rodada |
| sem melhora no K5 (11/10) | partida aceita pelo HiGHS com critério 0,4091; nenhuma solução melhor em 180 s; dual ~0, gap de 100%; 0 células diferentes entre etapa 1 e final; enf. 120–162 h (42 h; 23,86 pp), téc. 144–174 h (30 h; 17,05 pp); etapa 1 com penalidade 21 e gap 28,6% | **recontagem a partir das escalas gravadas, sem `ferramenta.indicadores` nem o modelo** (`p17_diagnostico_k5.py analisar`): igual à ferramenta; critério recontado = valor da partida no log; esperado commitado antes (`d9c0677`) | uma rodada; limite de 180 s; a etapa 1 varia a cada rodada (gap 28,6% contra 33,3% em 09/10, mesma penalidade 21) |
| sem melhora no teste 8b (11/10) | 12×36, 40 pessoas (14 enf. + 26 téc.), 20 pedidos de folga, limite de 25 s por etapa (teste 8b da tela, rodado para a `v1.2.2`): etapa 1 sem prova (gap 1,03%, 20 de 20 pedidos); critério da etapa 2 0,3409 → 0,3409; a tela mostrou a linha "a da etapa 1" | o teste conferiu, sobre os indicadores da ferramenta, que o critério final = o da etapa 1 e que a linha bate exatamente (`resultados/v122_2026-10-11/tela_8.log`); **SEM RECONTAGEM INDEPENDENTE** (a escala não foi gravada) | limite de 25 s, não o da tela (180 s) |
| **5 de 5 resoluções sem prova, nenhuma melhora** | Otávio, K5 e K6 (09/10), K5 (11/10) e 8b (11/10): em nenhuma a etapa 2 achou escala mais equilibrada que a da etapa 1 no tempo dado | linhas acima; recontagem independente só no K5 de 11/10 | casos de fronteira (6 h + 12 h) e um 12×36 com pedidos; o caminho com prova não está nesta conta (9d melhorou: 36,4 → 4,5 pp); limites da tela, não os do diagnóstico abaixo |

**Diagnóstico de 11/10 (só teste, fora da ferramenta).** Origem:
`resultados/p17_variantes_2026-10-11/A/` e `B/` (`highs.log`, `escala_final.json`, `resumo.json`).
Comando: `python docs\diagnostico\p17_etapa2_variantes.py <A|B>`, rodado pelo Otávio. Mesmo modelo
da etapa 2 da ferramenta, montado por fora, partindo da escala gravada da etapa 1 do K5 de 11/10
(critério 0,4091, penalidade 21). Esperado commitado antes (`195cf9b`). Decisão: `DECISOES.md`,
"2026-10-10 — P17", item d. **Afirmação fraca:** uma rodada, uma partida; tempo é limite
operacional desta máquina (i5-10210U, HiGHS 1.15.1 via `appsi_highs`).

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| B (quebra de simetria, 180 s): **sem melhora** | ordem por horas dentro dos grupos de idênticos (13 enf. e 5 téc.; 16 restrições); partida aceita 0,4091; nenhuma solução melhor; dual ~3e-14, gap 100%; escala final = partida | conferências 1–5 do script; **recontagem independente** das escalas gravadas (`p17_diagnostico_k5.recontar`, sem `ferramenta.indicadores` nem o modelo): critério 0,4091, penalidade 21, descanso e rígidas OK, inclusive desfeita a renumeração | 180 s, o limite da tela |
| A (1.800 s): **melhora, 0,4091 → 0,1364** | melhoras aos 1.752,1 s (0,1705) e 1.797,4 s (0,1364), as duas pela heurística Sub-MIP do HiGHS (fonte "L" na legenda do log); diferença entre colegas: enf. 42 → 12 h (144–156 h), téc. 30 → 12 h (150–162 h); penalidade 21 (= etapa 1); dual ~2e-14, gap 100% | conferências 1–4 do script; **recontagem independente** das escalas gravadas: critério 0,1364 = melhor do log, penalidade 21, descanso e rígidas OK | a melhora veio a 3 s do fim: pode haver melhor com mais tempo; sem prova de ótimo; 1.800 s está fora do orçamento do clique (20 min) |

## 14. Validação por restrição nos 4 ótimos (19/10/2026)

Aprovada pelo Otávio em 19/10 (2º bloco). Esperado commitado antes (`8d20313`; controle,
`d44daef`); relatório `resultados/relatorio_2026-10-19.md`, seção 4. Sem solver.

| Número | O que é | Arquivo | Comando | Conferência | Ressalva |
|---|---|---|---|---|---|
| duras = **0** nas 4 escalas ótimas (56, 58, 197, 219) | cobertura pelo avaliador oficial; um turno por dia contado no XML; `conferir_rigidas`; restrições do modelo com x fixado | `resultados/validacao_restricoes_2026-10-19/tabela.md` | `python docs\diagnostico\validacao_restricoes.py` | avaliador oficial (saídas de `resultados/<inst>_completo_avaliador.txt`) | o avaliador só checa cobertura; um-turno-por-dia vem da contagem no XML |
| penalidade por tipo, avaliador × modelo: diferença **0** em todos os tipos; somas **56, 58, 197, 219** | 6 tipos com custo nas 4 escalas (máximo de turnos, dias seguidos, mínimos de dias e de folgas seguidos, pedido de folga, padrão indesejado) | idem, `por_tipo.csv` | idem | avaliador oficial | a coluna "modelo" é o próprio código da função objetivo, com x fixado; a independência está no avaliador |
| diferença **0** por profissional (10, 10, 49, 49) e por profissional × tipo | | `por_profissional.csv` | idem | avaliador oficial | idem |
| controle: 20 escalas perturbadas (penalidade 69–250), avaliador = modelo em todos os tipos e células; a conferência acusa as 20 contra a saída da original | | `controle/controle.md` | `python docs\diagnostico\validacao_restricoes_controle.py` | avaliador oficial, rodado em 19/10 | perturbações aleatórias, semente 20261019; 11 tipos de violação exercitados |

Substitui, como evidência de restrições, as 207 + 36 escalas de 18/09 (perdidas; seção 1).

## PENDENTE DE APROVAÇÃO — Tamanho do modelo: nosso × Santos et al. (2016)

**Não aprovada: não citar até o Otávio aprovar.** Levada em 22/10 (pedido do orientador na reunião
de 22/10, junto da bateria HiGHS × SCIP). Origem: `docs/diferencas_inrc_ferramenta.md`, parte (a);
contagem do nosso modelo por `docs/diagnostico/tamanho_modelos.py` (sem solver; os mesmos números
saíram de novo em 22/10 pela `bateria_solvers.py --montar`, e o HiGHS e o SCIP recebem exatamente
esse problema — identidade da Fase 0, `resultados/solvers_2026-10-22/relatorio_fase0.md`).

| Instância | Nosso: variáveis | Nosso: restrições | Santos: x + y + w + r + z | dos quais w + r |
|---|---:|---:|---:|---:|
| sprint01 (10 enf., 4 turnos, 28 dias) | 2.978 | 2.450 | ≥ 9.380 | 8.120 |
| sprint02 | 2.992 | 2.464 | ≥ 9.380 | 8.120 |
| long01 (49 enf., 5 turnos) | 15.029 | 10.857 | ≥ 47.334 | 39.788 |
| long02 | 15.120 | 10.948 | ≥ 47.334 | 39.788 |
| medium_late05 (30 enf., 5 turnos) | 15.320 | 13.060 | ≥ 28.980 | 24.360 |

**Ressalvas (obrigatórias junto da tabela):**
- **A coluna de Santos é um piso**: só as variáveis x, y, w, r, z, pela definição do artigo; as
  folgas α (dependem das suaves ativas) e as restrições de Santos não foram contadas. "≥" é parte
  do número.
- As janelas w e r de Santos são uma por par de dias d1 ≤ d2: 28 × 29 ÷ 2 = 406 por enfermeiro em
  28 dias. Conferir a formulação **no artigo** antes de citar (a leitura veio do fichamento da
  Redação, `docs/diferencas_inrc_ferramenta.md`).
- A tabela compara **tamanho**, não eficiência: as janelas de Santos servem para fortalecer o
  limite dual por planos de corte; este trabalho não persegue desempenho algorítmico
  (`DECISOES.md`, "2026-09-08 — Formulação: atribuição, não janelas").

## PENDENTE DE APROVAÇÃO — Comportamento computacional: HiGHS × SCIP (22 e 23/10/2026)

**Não aprovada: não citar até o Otávio aprovar.** Pedido do orientador (reunião de 22/10): tabela
de comportamento computacional por caso, com o SCIP (gratuito) ao lado do HiGHS. Regras registradas
antes de rodar: `DECISOES.md`, "2026-10-22 — Bateria HiGHS × SCIP" e "2026-10-23 — Sensibilidade
ao tempo, HiGHS × SCIP, 3.600 s por caso". Relatórios: `resultados/solvers_2026-10-22/
relatorio_fase1.md` e `resultados/solvers_2026-10-23_3600/relatorio_parcial.md`; dados por caso
(JSON, log, escala e saída do avaliador oficial) nas mesmas pastas.

**Condições, iguais para os dois:** o mesmo modelo (identidade do problema recebido pelos dois
provada na Fase 0, com controle; no SCIP o objetivo vai como custo, sem o epígrafo da interface do
Pyomo); gap de parada 0,01%; 1 thread; caso a caso, os dois na mesma sessão; o HiGHS rodou de novo;
toda escala no avaliador oficial. Nos casos da ferramenta, o tempo do caso é dividido pela regra da
v1.4.3 (classificação padrão: um bloco da etapa 1 e a etapa 2, metade e metade, com a proteção da
primeira escala). **Afirmação fraca:** i5-10210U, 11,8 GB, Windows 11; HiGHS 1.15.1 (appsi) e SCIP
10.0 (PySCIPOpt 6.3.0); uma rodada por caso. **Tempo é comportamento observado nesta máquina e nesta
configuração, nunca resultado geral sobre os solvers.**

**Colunas:** "Escala" = o valor da etapa 1 na escala entregue, recalculado fora do modelo (INRC:
avaliador oficial e `avaliacao.py`; ferramenta: coeficiente × violações pelo `prioridades.resultado`)
— sem prova, a vitória conta por ele. "Limite" = melhor limite inferior do solver. "Gap" = (escala −
limite) ÷ escala. "Tempo" = tempo da etapa 1 (no INRC, a resolução única). "Avaliador" = penalidade
INRC da escala final no avaliador oficial (na ferramenta, não é o objetivo da ferramenta).

### Rodada de 22/10 — 600 s por caso (completa)

| Caso | Solver | Variáveis | Restrições | Escala | Limite | Gap | Tempo (s) | Ótimo provado | Avaliador |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| sprint01 | HiGHS | 2.978 | 2.450 | 56 | 56 | 0% | 2,6 | sim | 56 |
| sprint01 | SCIP | 2.978 | 2.450 | 56 | 56 | 0% | 2,8 | sim | 56 |
| sprint02 | HiGHS | 2.992 | 2.464 | 58 | 58 | 0% | 2,8 | sim | 58 |
| sprint02 | SCIP | 2.992 | 2.464 | 58 | 58 | 0% | 6,5 | sim | 58 |
| long01 | HiGHS | 15.029 | 10.857 | 197 | 197 | 0% | 18,2 | sim | 197 |
| long01 | SCIP | 15.029 | 10.857 | 197 | 197 | 0% | 33,5 | sim | 197 |
| long02 | HiGHS | 15.120 | 10.948 | 219 | 219 | 0% | 48,4 | sim | 219 |
| long02 | SCIP | 15.120 | 10.948 | 219 | 219 | 0% | 24,5 | sim | 219 |
| medium_late05 | HiGHS | 15.320 | 13.060 | **2.199** (modelo: 7.435) | 59 | 97,3% | 602,5 | não | 2.199 |
| medium_late05 | SCIP | 15.320 | 13.060 | 318 | 53,7 | 83,1% | 600,4 | não | 318 |
| A36_livre, 30 (10 + 20) | HiGHS | 5.320 | 20.264 | 13 | 13 | 0% | 13,4 | sim | 306 |
| A36_livre, 30 | SCIP | 5.320 | 20.264 | 15 | 13 | 13,3% | 299,5 | não | 312 |
| A36_fixo, 30 — Essencial | HiGHS | 5.320 | 20.264 | 0 | 0 | 0% | 5,5 | sim | |
| A36_fixo, 30 — Importante | HiGHS | 5.320 | 20.265 | 14 | 14 | 0% | 1,7 | sim | 222 |
| A36_fixo, 30 — Essencial | SCIP | 5.320 | 20.264 | 0 | 0 | 0% | 32,7 | sim | |
| A36_fixo, 30 — Importante | SCIP | 5.320 | 20.265 | 14 | 14 | 0% | 5,8 | sim | 234 |
| B11_livre, 89 (15 + 74)* | HiGHS | 14.140 | 32.268 | 57 | 0 | 100% | 301,2 | não | 1.002 |
| B11_livre, 89* | SCIP | 14.140 | 32.268 | sem escala | 0 | — | 300,6 + 299,1 | não | — |

\* HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA (`DESCANSO_POR_TURNO = {"D12": 11}`). No
SCIP, a fatia da etapa 1 (300 s) acabou sem escala, a proteção da primeira escala rodou de novo com
o resto (299 s) e também não achou.

Etapa 2 (equilíbrio, registrada, não decide): não provou em nenhum caso da ferramenta, nos dois
solvers. Vitórias (regra de 22/10: vence quem prova onde o outro não prova; se nenhum prova, a
escala de menor valor; sem escala perde para quem tem; gap menor sozinho não conta): **SCIP 1
(medium_late05) × HiGHS 2 (A36_livre, B11), 5 empates. Regra de troca: fica o HiGHS** (o SCIP não
vence mais do que perde e perde a prova do A36_livre).

**Anomalia do medium_late05 com HiGHS (esclarecida):** o HiGHS parou no limite marcando **7.435** no
modelo, mas a escala vale **2.199** no avaliador oficial e no `avaliacao.py`. Nenhum dos dois está
errado: 7.435 é o objetivo do modelo no ponto entregue (o appsi, o HiGHS e o recálculo nas variáveis
carregadas dão o mesmo), e 2.199 é a penalidade da escala. Integralidade perfeita (desvio 0,0).
Causa: folgas e auxiliares soltas num ponto sem prova (cada folga só tem limite inferior, α ≥
excesso). Por família, modelo × escala: mínimo de turnos 666 × 0; máximo de folgas seguidas 777 × 7;
mesmo turno no fim de semana 2.480 × 440. Diagnóstico: `DECISOES.md`, "2026-10-22 — Anomalia do
medium_late05 (HiGHS)"; `resultados/solvers_2026-10-22/anomalia/`. Consequência na ferramenta:
P20 (`DECISOES.md`, "2026-10-23 — P20 aprovada").

### Rodada de 23/10 — 3.600 s por caso (sensibilidade ao tempo; PARCIAL)

Código da ferramenta: `ed621a2` (com a P20; `src/` idêntico no commit usado, `e8a87f2`). **Análise
de sensibilidade: não reabre a regra de troca de 22/10.** Os casos da ferramenta não usam critérios
com folga (registrado por caso), então a P20 não alterou valor nenhum; no INRC ela não age.

| Caso | Solver | Variáveis | Restrições | Escala | Limite | Gap | Tempo (s) | Ótimo provado | Avaliador |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| medium_late05 | HiGHS | 15.320 | 13.060 | 224 | 64 | 71,4% | 3.602,7 | não | 224 |
| medium_late05 | SCIP | 15.320 | 13.060 | 186 | 58,5 | 68,6% | 3.600,4 | não | 186 |
| A36_livre, 30 | HiGHS | 5.320 | 20.264 | 13 | 13 | 0% | 14,4 | sim | 324 |
| A36_livre, 30 | SCIP | 5.320 | 20.264 | 13 | 13 | 0% | 620,0 | sim | 330 |
| B11_livre, 89* | HiGHS | 14.140 | 32.268 | **não concluído** | | | | | |
| B11_livre, 89* | SCIP | 14.140 | 32.268 | **não rodou** | | | | | |

**B11 não concluído — motivo:** o Claude Code encerrou a rodada por falta de memória na máquina. O
B11 com HiGHS terminou os 3.600 s do solver (a escala foi gravada) e foi encerrado na conferência
pelo avaliador oficial (Java, até 6 GB, `-Xmx6g`), sem gravar o resultado; a escala desse ponto fica
fora da tabela. O B11 com SCIP não começou. Faltam ~2 h, a rodar fora do Claude Code.

Valor do modelo = valor da escala nas quatro rodadas concluídas. Etapa 2: não provou; no A36_livre
com SCIP, não achou escala em 2.979 s (fica a escala da etapa 1). Por caso: **medium_late05, SCIP**
(186 < 224, nenhum prova); **A36_livre, empate** (com 3.600 s o SCIP também prova a etapa 1, que em
600 s não provava). Com 3.600 s, o medium_late05 com HiGHS chega aos 224 da seção 1 (06/10).
Leitura provisória, sem o B11: o SCIP não perde nada para o HiGHS nos dois casos concluídos e ganha
um — vai ao Otávio e ao orientador; não há troca automática.
