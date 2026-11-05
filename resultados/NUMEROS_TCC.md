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
tolerância nela é desprezível (0,0005 pp sobre 4,55 pp no 9c; *medido na v1.4.4 (etapa 2 pela soma)*).

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
| quase todas | restrições flexíveis ativas, com pesos de 3 a 10 nas restrições suaves dos contratos atribuídos (contratos 0, 1 e 2); padrões indesejados e pedidos de folga com peso 1; o contrato 3 (peso 31 no mínimo de folgas seguidas) não é atribuído a ninguém | idem |
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
| amplitude 0 em todos | etapa 2 degenerada | conta (demanda = capacidade), feita depois | a etapa 2 não é medida por esta curva; *medido na v1.4.4 (etapa 2 pela soma)* |
| 39,8 / 168,0 / 130,1 / 693,0 / 901,9 / 902,8 s | tempo da etapa 1 | — | **limite operacional**; uma medição por tamanho; não monotônico |
| 39,0 / 54,3 / 128,9 / 235,1 / 345,8 s | tempo até a primeira escala legal (HiGHS) | — | **limite operacional** |
| 3.696 a 20.496 variáveis; 12.640 a 69.444 restrições | tamanho do modelo | — | — |

## 6. Ferramenta — P1, rodada com folga de 05/10

Origem: `resultados/escalabilidade_objetivo_folga.csv`; logs `folga_teste_N40_2026-10-05.log` e `folga_2026-10-05.log`. Comando: `python src\escalabilidade_objetivo.py --folga`.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| 13,64 pp nos três tamanhos | amplitude da fração do contrato depois da etapa 2 (6,82 + 6,82) | conta do piso feita **DEPOIS** do resultado: SEM CONFERÊNCIA no sentido estrito | a conta explica, não previu; *medido na v1.4.4 (etapa 2 pela soma)* |
| 34,09 / 20,45 / 27,27 pp | amplitude na escala da etapa 1 | SEM CONFERÊNCIA | *medido na v1.4.4 (etapa 2 pela soma)* |
| etapa 1 ótima em 44, 66 e 88 | prova da etapa 1 | SEM CONFERÊNCIA (estado do solver) | — |
| 18,1 / 45,6 / 81,1 s | tempo até 90% da redução final na etapa 2 | — | **limite operacional**; coincide com a primeira escala da etapa 2; *medido na v1.4.4 (etapa 2 pela soma)* |
| gap 19,6% / 26,1% / 37,5% | gap da etapa 2 em 900 s | — | fraqueza do limite inferior, não distância real; *medido na v1.4.4 (etapa 2 pela soma)* |

## 7. Limites de tempo da tela

> **Nota de 28/10/2026.** Os valores desta seção são os limites fixos de versões anteriores à
> v1.4.0. Na v1.4.4, `ferramenta.py` não tem `TEMPO` nem `TEMPO_ETAPA2` fixos: o campo "Tempo
> máximo para gerar a escala" (padrão 60 min, `ORCAMENTO = 3600 s`) é dividido proporcionalmente
> entre as etapas, conforme `D:\TCC\escrita\insumos\DOSSIE_FERRAMENTA.md`, seção 5. A tabela abaixo
> fica como registro histórico e não deve ser citada como limite da versão citável.

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
| 0 e 4,55 pp | amplitude entre enfermeiros e entre técnicos (9c) | **conta registrada antes**, commit `08603c6` | *medido na v1.4.4 (etapa 2 pela soma)*; reconfirmado na v1.4.5 (seção v1.4.5) |
| 384 h e 232 h; +24,9 pp | horas não utilizadas (enf., téc.); diferença entre categorias (9c) | conta antes (`08603c6`) | — |
| "1 plantão (8 h)" e "nenhuma (0 h)" | diferença entre colegas na tela (9c) | conta antes (05/10) | *medido na v1.4.4 (etapa 2 pela soma)* |
| 36,4 → 4,5 pp | o critério cai da etapa 1 para a etapa 2 (9d) | esperado antes: estritamente menor | o 36,4 depende da escala da etapa 1; *medido na v1.4.4 (etapa 2 pela soma)* |
| 146,9 s | prova da etapa 2 do 9c, rodando sozinho | — | **limite operacional**; já falhou com outro processo junto; *medido na v1.4.4 (etapa 2 pela soma)* |

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
| 1 e 0,6 plantão; 0,2 e 0,6; 0,9 e 0,6 | diferença máxima entre colegas (enf. e téc.) | SEM CONFERÊNCIA | a etapa 2 tem tempo limitado e pode variar entre rodadas; *medido na v1.4.4 (etapa 2 pela soma)* |
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
diferença entre colegas 1 e 0,6, 0,2 e 0,6, 0,9 e 0,6 plantão (*medido na v1.4.4 (etapa 2 pela soma)*). As escalas mudaram (393 a 422
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
| a etapa 2 sem prova nunca piora a etapa 1 | garantia: a etapa 2 parte da escala da etapa 1, com "penalidade ≤ valor da etapa 1" como restrição; no fim, o critério de equilíbrio não sobe | **por construção** (a partida cumpre a restrição; ver `DECISOES.md`, P14 e P17) e conferências 2, 3 e 5 do `p14_conferir.py --p17` (enfermeiros em posto de técnico, diferença por categoria e pedidos, contra a etapa 1 da mesma rodada) nos 3 casos de 09/10 | *medido na v1.4.4 (etapa 2 pela soma)* |
| sem melhora em 3 de 3 (09/10) | Otávio (20 + 10, 6 h + 12 h): penalidade 57, gap 17,5%, diferença 60 h (enf.) e 24 h (téc.); K5 (13 + 5): 21, gap 33,3%, 42 h e 30 h; K6 (15 + 5): 18, gap 5,6%, 48 h e 18 h; final = etapa 1 nos três | **SEM RECONTAGEM INDEPENDENTE**: as escalas não foram gravadas; os números são os da ferramenta | limite de 180 s na etapa 2; a etapa 1 varia a cada rodada; *medido na v1.4.4 (etapa 2 pela soma)* |
| sem melhora no K5 (11/10) | partida aceita pelo HiGHS com critério 0,4091; nenhuma solução melhor em 180 s; dual ~0, gap de 100%; 0 células diferentes entre etapa 1 e final; enf. 120–162 h (42 h; 23,86 pp), téc. 144–174 h (30 h; 17,05 pp); etapa 1 com penalidade 21 e gap 28,6% | **recontagem a partir das escalas gravadas, sem `ferramenta.indicadores` nem o modelo** (`p17_diagnostico_k5.py analisar`): igual à ferramenta; critério recontado = valor da partida no log; esperado commitado antes (`d9c0677`) | uma rodada; limite de 180 s; a etapa 1 varia a cada rodada (gap 28,6% contra 33,3% em 09/10, mesma penalidade 21); *medido na v1.4.4 (etapa 2 pela soma)* |
| sem melhora no teste 8b (11/10) | 12×36, 40 pessoas (14 enf. + 26 téc.), 20 pedidos de folga, limite de 25 s por etapa (teste 8b da tela, rodado para a `v1.2.2`): etapa 1 sem prova (gap 1,03%, 20 de 20 pedidos); critério da etapa 2 0,3409 → 0,3409; a tela mostrou a linha "a da etapa 1" | o teste conferiu, sobre os indicadores da ferramenta, que o critério final = o da etapa 1 e que a linha bate exatamente (`resultados/v122_2026-10-11/tela_8.log`); **SEM RECONTAGEM INDEPENDENTE** (a escala não foi gravada) | limite de 25 s, não o da tela (180 s); *medido na v1.4.4 (etapa 2 pela soma)* |
| **5 de 5 resoluções sem prova, nenhuma melhora** | Otávio, K5 e K6 (09/10), K5 (11/10) e 8b (11/10): em nenhuma a etapa 2 achou escala mais equilibrada que a da etapa 1 no tempo dado | linhas acima; recontagem independente só no K5 de 11/10 | casos de fronteira (6 h + 12 h) e um 12×36 com pedidos; o caminho com prova não está nesta conta (9d melhorou: 36,4 → 4,5 pp); limites da tela, não os do diagnóstico abaixo; *medido na v1.4.4 (etapa 2 pela soma)* |

**Diagnóstico de 11/10 (só teste, fora da ferramenta).** Origem:
`resultados/p17_variantes_2026-10-11/A/` e `B/` (`highs.log`, `escala_final.json`, `resumo.json`).
Comando: `python docs\diagnostico\p17_etapa2_variantes.py <A|B>`, rodado pelo Otávio. Mesmo modelo
da etapa 2 da ferramenta (medido na v1.4.4 (etapa 2 pela soma)), montado por fora, partindo da escala gravada da etapa 1 do K5 de 11/10
(critério 0,4091, penalidade 21). Esperado commitado antes (`195cf9b`). Decisão: `DECISOES.md`,
"2026-10-10 — P17", item d. **Afirmação fraca:** uma rodada, uma partida; tempo é limite
operacional desta máquina (i5-10210U, HiGHS 1.15.1 via `appsi_highs`).

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| B (quebra de simetria, 180 s): **sem melhora** | ordem por horas dentro dos grupos de idênticos (13 enf. e 5 téc.; 16 restrições); partida aceita 0,4091; nenhuma solução melhor; dual ~3e-14, gap 100%; escala final = partida | conferências 1–5 do script; **recontagem independente** das escalas gravadas (`p17_diagnostico_k5.recontar`, sem `ferramenta.indicadores` nem o modelo): critério 0,4091, penalidade 21, descanso e rígidas OK, inclusive desfeita a renumeração | 180 s, o limite da tela; *medido na v1.4.4 (etapa 2 pela soma)* |
| A (1.800 s): **melhora, 0,4091 → 0,1364** | melhoras aos 1.752,1 s (0,1705) e 1.797,4 s (0,1364), as duas pela heurística Sub-MIP do HiGHS (fonte "L" na legenda do log); diferença entre colegas: enf. 42 → 12 h (144–156 h), téc. 30 → 12 h (150–162 h); penalidade 21 (= etapa 1); dual ~2e-14, gap 100% | conferências 1–4 do script; **recontagem independente** das escalas gravadas: critério 0,1364 = melhor do log, penalidade 21, descanso e rígidas OK | a melhora veio a 3 s do fim: pode haver melhor com mais tempo; sem prova de ótimo; 1.800 s está fora do orçamento do clique (20 min); *medido na v1.4.4 (etapa 2 pela soma)* |

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

## 15. Casos realistas A e B (21 e 24/10/2026)

**Aprovada pelo Otávio em 26/10/2026** (transcrição da p. 70 conferida por ele contra a p. 70 em
26/10), com os ajustes da Orientação de 26/10 (período com o ano inferido; tabela da escala real
com as 21 linhas com registro). Fonte dos dados: Massens
(2019), Anexo B (escala real da Clínica Ortovascular) e o restante da ficha do caso
(`D:\TCC\escrita\fontes\FICHA_CASO_REALISTA.md`).

**Ressalvas obrigatórias (valem para 15.1 e 15.2):**
- a composição 10 enfermeiros + 20 técnicos é a da regra `equipe` (a proporção mínima do COFEN para o
  grau intermediário), **não ótimo de custo**; **o 30 vale para qualquer composição** (a conta prévia
  recusa 29 pelo total de pessoas, sem depender da mistura);
- os limites dos critérios são os **padrões da ferramenta, não calibrados** ao hospital;
- tempo só como **limite operacional** (i5-10210U, 11,8 GB, HiGHS 1.15.1 via appsi);
- na 15.2, a etapa 2 do A36 ordem 1 terminou **sem prova** (medido na v1.4.4 (etapa 2 pela soma)) (o equilíbrio de carga pode melhorar); isso
  não afeta os níveis de prioridade, **todos provados**;
- a **penalidade total do avaliador oficial não vai ao texto** (é a do INRC com os pesos gravados no
  XML, não o objetivo da ferramenta); vai "sem violação de restrição dura";
- 11 h depois do D12 é **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA**; o texto não afirma que o
  hospital descumpre a lei ("a regra, como modelada, segue o art. 59-A").

### 15.1 Fase 2 (21/10/2026), classificação padrão

> **Histórico: substituída pela 15c como base do texto do caso A (05/11/2026).**

Origem: `resultados/fase2_2026-10-21/` (JSON, `.txt`, XML da instância e da escala, saída do
avaliador, `resumo.txt`). Comando: `docs/diagnostico/rodar_fase2.sh` (um processo por rodada,
`docs/diagnostico/fase2.py`). Versão **v1.4.1** (`9afa334`). Entradas:
`resultados/caso_a_2026-10-20/entrada.py` e `caso_b_2026-10-20/entrada.py`. Esperados commitados
antes: os `ESPERADO.md` das duas pastas. Classificação padrão, orçamento 60 min, 1.800 s por nível e
na etapa 2. Proposta original: `resultados/relatorio_2026-10-21.md`. Uma rodada por configuração.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| caso A, 36 h: **faltam 6; menor quadro viável 30** (turno fixo e rodízio livre) | 24–29 recusados pela conta prévia (dom 17 + seg 18/01: 17 + 11 = 28 postos contra 22 disponíveis); 30 com escala, etapa 1 provada | cobertura: **avaliador oficial, sem violação de dura**; descanso no relógio: menor 36 h depois de D12 e de N (compartilha a premissa com o modelo); conta à mão no `ESPERADO.md` (≥ 30) | o 30 vale para qualquer composição; 10 + 20 não é ótimo de custo |
| caso A, 30 = 10 enf. + 20 téc.; **13 turnos** de enfermeiro em posto de técnico (rodízio livre; 14 no turno fixo) | composição e uso de enfermeiro em vaga de técnico na escala entregue | recontado dos XMLs, fora da ferramenta | a busca tenta só duas composições por tamanho |
| caso B, 36 h: **não há escala legal até 101** | 89–101 recusados pela conta prévia (dom 10 + seg 11/01: 65 + 40 = 105 contra 89) | conta à mão no `ESPERADO.md` (≥ 105) | a busca vai até 89 + 12; o menor viável não foi determinado (≥ 105 pela conta, condição necessária) |
| **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA:** com 11 h depois do D12, A (turno fixo) admite 24, provado; B admite 89, **sem prova** (gap 100%) | o quanto a regra das 36 h depois do D12 pesa no quadro | avaliador oficial, sem violação de dura (B reconferido com `-Xmx6g`: na rodada, o avaliador tinha parado sem memória); descanso no relógio: D12 → 12 h | parâmetro de pesquisa, fora da tela |

### 15.2 Caso A pela prática e sensibilidade a 2 ordens (24/10/2026)

> **Histórico: substituída pela 15c como base do texto do caso A (05/11/2026).**

Decisão e esperado commitados antes: `DECISOES.md`, "2026-10-23 — Caso A: classificação dos
critérios pela escala real e sensibilidade (2 ordens)"; `resultados/caso_a_pratica_2026-10-23/
ESPERADO.md`. Resultado: `resultado.md` (com o complemento de 24/10) e `recontagem.md`, na mesma
pasta. Versão **v1.4.4** (`src/` idêntico desde `ed621a2`). Comando: `python docs\diagnostico\
caso_a_pratica.py --rodar` (um processo por rodada). Orçamento padrão de 60 min por rodada.
**Esperado cumprido nas três rodadas** (frase, sem violação de dura, descanso, direção da ordem 2
com prova).

**Classificação dos critérios pela escala real** (transcrição célula a célula da p. 70 de Massens,
24 linhas transcritas, 21 com registro contadas; 26/10 a 25/11 (ano não impresso na escala; 2018
inferido pelo calendário: os fins de semana sombreados só caem em sábado e domingo em 2018)).
Regra: violado em alguma ocorrência → Não considerar; nunca violado, com ocorrência → Importante; sem evidência → padrão; Essencial só para regra declarada na fonte (o
turno fixo). Recontagem independente pelo `avaliacao.py`: **os 13 critérios contáveis do mesmo lado
da contagem da ficha**, com a leitura da borda **C, adotada a posteriori (23/10)**: formulada depois
de a recontagem expor a divergência entre a regra escrita na ficha (tirar todo bloco de borda) e a
contagem da ficha; motivo independente do resultado — na borda do mês, o bloco conta nos critérios de
máximo e sai nos de mínimo; o bloco que toca as férias sai sempre. As leituras A e B e o que davam
estão no DECISOES. Nunca violados na prática: máx. folgas seguidas (4), mín. fins de semana seguidos
(2), mín. turnos (10). "Mesmo turno no fim de semana" é violado pela semântica do avaliador (um dia só
do fim de semana já viola): Não considerar, por evidência.

**A escala real, por critério** (21 linhas com registro: 10 diurnas, 5 da noite A, 6 da noite B; as
três linhas sem nenhum registro — 6118, 4798, 6089 — ficam fora da contagem, mas no caso: DECISOES,
"2026-10-23 — Caso A", nota a posteriori de 26/10; a contagem com as 24 linhas, com os mesmos 13
lados, fica no `recontagem.md` como histórico). Limites = os padrões da ferramenta. Conferência:
transcrição célula a célula da p. 70 (chat de Orientação, 23/10), conferida pelo Otávio contra a
p. 70 em 26/10; contagem pelo `avaliacao.py` (recontagem independente; noturno na véspera pelo
contador da ferramenta); leitura C da borda (a posteriori, 23/10); 21 de 24 linhas (a posteriori,
26/10). Totais de turnos só de quem não teve férias. **Ressalva:** um setor, um mês; leituras da
imagem adotadas na ficha (dia útil em branco = trabalho); as três linhas sem registro (6118, 4798,
6089) ficam fora da contagem, mas no caso; não afirma descumprimento de lei.

| Critério (limite padrão) | Violações | Pessoas com violação, por grupo |
|---|---:|---|
| Máx. dias seguidos, preferência (5) | 30 | 9 (diurno 9) |
| Mín. dias seguidos (3) | 302 | 16 (diurno 5, noite A 5, noite B 6) |
| Máx. folgas seguidas (4) | **0** | 0 |
| Mín. folgas seguidas (3) | 359 | 21 (diurno 10, noite A 5, noite B 6) |
| Máx. fins de semana seguidos (3) | 26 | 14 (diurno 9, noite A 3, noite B 2) |
| Mín. fins de semana seguidos (2) | **0** | 0 |
| Fins de semana em 4 semanas (2) | 63 | 19 (diurno 9, noite A 4, noite B 6) |
| Fim de semana completo | 93 | 21 (diurno 10, noite A 5, noite B 6) |
| Mesmo turno no fim de semana | 93 | 21 (diurno 10, noite A 5, noite B 6) |
| Máx. turnos, preferência (18) | 59 | 9 (diurno 9) |
| Mín. turnos (10) | **0** | 0 |
| Noturno na véspera de fim de semana livre | 4 | 4 (noite A 1, noite B 3) |
| Duas folgas depois de noites | 137 | 11 (noite A 5, noite B 6) |

**Ordens:** ordem 1 (a prática) — Essencial: as 29 linhas "Só este turno"; Importante: máx. folgas
seguidas (4), mín. fins de semana seguidos (2), mín. turnos (10), enfermeiro em posto de técnico; o
resto, Não considerar. Ordem 2 — máx. fins de semana seguidos (3) no Essencial; "Só este turno" no
Desejável; o resto igual.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA:** A11 (11 h depois do D12), 24 (4 + 20), ordem 1: "O quadro informado admite escala legal. Escala gerada."; Essencial **0** e Importante **27**, os dois **provados**; etapa 2 provada | frase da tela e prova por nível | avaliador oficial: sem violação de dura; descanso no relógio aprovado | parâmetro de pesquisa; *medido na v1.4.4 (etapa 2 pela soma)* |
| A11, Importante 27 = máx. folgas seguidas **22** + mín. fins de semana seguidos **1** + mín. turnos **4** + enfermeiro em posto de técnico **0**; "Só este turno": **0** quebras | violações por critério | avaliador oficial (critérios ligados, peso 1): **22, 1, 4** — iguais à ferramenta; enfermeiro em posto de técnico: sem conferência externa | os 22 e os 4 são de férias (nota abaixo) |
| A36, 30 (10 + 20), ordem 1: "O quadro informado admite escala legal. Escala gerada."; Essencial **0** e Importante **51**, os dois **provados**; etapa 2 sem prova | frase e prova por nível | avaliador oficial: sem violação de dura; descanso no relógio aprovado | etapa 2 sem prova: o equilíbrio pode melhorar; os níveis de prioridade estão provados; *medido na v1.4.4 (etapa 2 pela soma)* |
| A36 ordem 1, Importante 51 = máx. folgas seguidas **22** + mín. fins de semana seguidos **1** + mín. turnos **10** + enfermeiro em posto de técnico **18**; "Só este turno": **0** quebras; máx. fins de semana seguidos (não considerado nesta ordem, avaliado com o critério ligado): **17** | violações por critério | avaliador oficial (peso 1): **22, 1, 10** e **17** — iguais à ferramenta; posto de técnico: sem conferência externa | dos 10 do mín. turnos, 4 são de férias (Noite A 1) e 6 de enfermeiros com 8–9 turnos |
| A36, 30, ordem 2: "O quadro informado admite escala legal. Escala gerada."; Essencial **0**, Importante **61**, Desejável **7**, os três **provados**; etapa 2 provada | frase e prova por nível | avaliador oficial: sem violação de dura; descanso no relógio aprovado | *medido na v1.4.4 (etapa 2 pela soma)* |
| A36 ordem 2: máx. fins de semana seguidos **0**; Importante 61 = máx. folgas seguidas **22** + mín. fins de semana seguidos **15** + mín. turnos **1** + posto de técnico **23**; "Só este turno": **7** quebras, todas da Noite A 1 | violações por critério | avaliador oficial (peso 1): **0, 22, 15, 1, 7** — iguais à ferramenta; posto de técnico: sem conferência externa | — |
| **Ordem 2 × ordem 1, com prova nos níveis envolvidos:** máx. fins de semana seguidos **0 ≤ 17**; quebras do "Só este turno" **7 ≥ 0** | a direção registrada antes (pôr o máx. fins de semana seguidos no Essencial e o turno fixo no Desejável troca um pelo outro) | as duas escalas avaliadas no avaliador com o critério ligado | uma rodada por ordem; os outros critérios do Importante também mudam (mín. fins de semana seguidos 1 → 15; posto de técnico 18 → 23) |
| enfermeiro em posto de técnico, por origem: A36 ordem 1 — 4 da unidade **6** (38 turnos), 6 acrescidos **12** (56 turnos); ordem 2 — unidade **10** (40 turnos), acrescidos **13** (59 turnos); A11 — **0** (4 enfermeiros, 76 turnos) | quem cobre vaga de técnico, os 4 enfermeiros da unidade (6118, 4798, 4969, 5993) × os 6 acrescidos (Enf 5 a Enf 10) | recontado das escalas gravadas, fora da ferramenta (`--complemento`); soma igual ao resultado por critério (0, 18, 23) | sem conferência externa (o avaliador não pontua) |

**Nota das férias (semântica do INRC, não escolha da ferramenta):** no formato do INRC, dia de férias
conta como dia sem trabalho — o `avaliacao.py` e o avaliador oficial concordam. Com 15 dias de
férias seguidos, o máx. folgas seguidas (4) é violado em pelo menos 15 − 4 = 11: os **22** das três
rodadas são a Tarde 1 e a Noite A 1, 11 cada — com o nível provado, **inevitáveis**. No mín. turnos,
os **4** da Noite A 1 (A11 e A36 ordem 1) vêm da mesma semântica somada ao turno fixo no Essencial
(só noites, em metade do mês) e, com prova, são inevitáveis nessas ordens; na ordem 2, com o turno
fixo no Desejável, a Noite A 1 chega aos 10 turnos à custa das 7 quebras. As linhas "Unwanted
pattern" (ex.: N-null-D12) da saída do avaliador são o artefato dos padrões das 36 h (`DECISOES.md`,
"2026-10-06 — Padrão das 36 h fica no XML (opção (a) da P13)") e não entram na conferência.

## 15b. Tamanho do modelo: nosso × Santos et al. (2016)

**Aprovada pelo Otávio em 24/10/2026.** (O número 15 ficou para a seção dos casos A e B,
aprovada em 26/10.) Levada em 22/10 (pedido do orientador na reunião
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
  28 dias. Conferido no artigo em 24/10 (chat de Orientação): Santos et al. (2016), Ann Oper Res
  239:225–251, seções 3.1–3.2, p. 228–230 — Π = todos os pares (d1, d2) com d1 ≤ d2; w e r
  indexadas por enfermeiro e janela ('O(n × d²) variables w and r'); y por fim de semana; z por par
  de fins de semana (i1 ≤ i2). A conta x + y + w + r + z refeita só pela definição do artigo bate
  nas cinco linhas.
- A tabela compara **tamanho**, não eficiência: as janelas de Santos servem para fortalecer o
  limite dual por planos de corte; este trabalho não persegue desempenho algorítmico
  (`DECISOES.md`, "2026-09-08 — Formulação: atribuição, não janelas").

## 15c. Caso A com a entrada de 04/11 (janela real do Anexo B, férias reais) na v1.4.5 (05/11/2026)

**Aprovada pelo Otávio em 05/11/2026** (validada pela Orientação). Origem: rascunho
`resultados/caso_a_2026-11-04/RASCUNHO_15c.md`, de 05/11.

Decisão e esperado commitados antes: `DECISOES.md`, "2026-11-04 — Caso A: entrada revista…" (itens
a–g) e "2026-11-05 — Limitações declaradas"; `resultados/caso_a_2026-11-04/ESPERADO.md`. Resultado:
`resultados/caso_a_2026-11-04/RELATORIO.md` e `rodadas/` na mesma pasta. Versão **v1.4.5** (`src/` idêntico à tag `634eeb5`).
Comando: `python docs\diagnostico\caso_a_v145.py --rodar`. Orçamento 60 min por rodada; uma rodada
por configuração.

**Substitui as seções 15.1 e 15.2 como base do texto do caso A** (entrada de 04/11, janela real do
Anexo B, v1.4.5); elas ficam como histórico (entrada antiga, v1.4.1 e v1.4.4).

**Ressalvas obrigatórias:**
- janela 29/10–25/11/2018, sem ajuste de demanda nos feriados de 02 e 15/11; equipe de 23 (o 4309
  como técnico de noite é decisão do Otávio; o 6089 fora); a conta dá o mesmo menor quadro (28) com
  22, 23 ou 24 (`ESPERADO.md` §2);
- 9 + 19 é a composição da regra `equipe` (33%, grau intermediário), **não ótimo de custo**;
- limites dos critérios: padrões da ferramenta, não calibrados;
- tempo só como **limite operacional** (i5-10210U, 11,8 GB, HiGHS 1.15.1 via appsi);
- avaliador oficial rodado com o Java em UTC (o horário de verão de 04/11/2018 quebra a contagem de
  dias do avaliador no fuso de São Paulo; saída idêntica nas instâncias antigas com e sem a opção);
- a penalidade total do avaliador não vai ao texto; vai "sem violação de restrição dura";
- na rodada sem linhas (A36_livre_padrao), a etapa 2 terminou **sem prova**: o equilíbrio de carga
  pode melhorar; os níveis de prioridade estão todos provados;
- 11 h depois do D12 é **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA**.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| caso A, 36 h: **faltam 5; menor quadro viável 28** (com as 33 linhas e sem elas) | 23–27 recusados pela conta prévia (dom 04 + seg 05/11: 17 + 10 = 27 postos contra 22 disponíveis); 28 com escala, etapa 1 provada | avaliador oficial, sem violação de dura; descanso no relógio: menor 36 h depois de D12 e N; conta à mão no `ESPERADO.md` (≥ 28) | a recusa de 23–27 vale para qualquer composição; a escala no 28 é com 9 + 19, que não é ótimo de custo |
| no 28, sem linhas: **15 turnos** de enfermeiro em posto de técnico, provado (= a cota inferior da conta, ≥ 15) | quanto a falta de técnicos nos pares dom + seg obriga a usar enfermeiro em vaga de técnico | cota à mão no `ESPERADO.md` §4; recontado da escala | com as linhas no Essencial, 25 |
| linhas "Só este turno" no Essencial: **mínimo de 2 quebras**, provado (padrão e classificação 1) | o quanto o turno fixo da prática cabe no quadro de 28 | quebras recontadas fora da ferramenta, iguais pessoa a pessoa | quem quebra muda com a classificação |
| classificação 2 × 1 no 28: fins de semana seguidos acima de 3 **0 × 13**; quebras das linhas **15 × 2** | o efeito da classificação; direções previstas no `ESPERADO.md` §3 | as duas com prova em todos os níveis; contagem com peso 1 fora da ferramenta | uma rodada por configuração |
| violação inevitável só no máximo de folgas seguidas: **19** (6137: 12; 5976: 7), atingida exatamente nas classificações 1 e 2 | o que as férias impõem | conta à mão no `ESPERADO.md` §4 | o mínimo de turnos **não** é inevitável: a classificação 2 dá 0 (5976 à custa da linha "Só N") |
| **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA:** com 11 h depois do D12, A (turno fixo, classificação 1) **admite 23, provado**; 14 quebras das linhas no Essencial, 0 enfermeiro em posto de técnico | o quanto a regra das 36 h depois do D12 pesa no quadro (28 × 23) | avaliador oficial, sem violação de dura; descanso no relógio: D12 → 12 h; conta à mão (22 contra 22) | parâmetro de pesquisa, fora da tela |
| caso B, 36 h: **não há escala legal até 101** (igual a 15.1) | 89–101 recusados pela conta (105 contra 89) | conta à mão no `ESPERADO.md` §5 | só a janela mudou; o menor viável não foi determinado |
| **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA:** com 11 h depois do D12, B (rodízio livre) **admite 89, sem prova** (0 e 1 violação, limite inferior 0); os mesmos valores da v1.4.1 (15.1) | o quanto a regra das 36 h depois do D12 pesa no caso B | avaliador oficial (`-Xmx6g`), sem violação de dura, na própria rodada; descanso no relógio: D12 → 12 h | parâmetro de pesquisa, fora da tela; sem prova no orçamento de 60 min |


### 15c — complemento (aprovado pelo Otávio em 05/11/2026)

**Complemento aprovado pelo Otávio em 05/11/2026** (validado pela Orientação). Sem rodar nada:
os valores foram lidos dos JSON e das saídas do avaliador em `resultados/caso_a_2026-11-04/`.
Nenhum outro valor do NUMEROS muda.

**1. Por nível e por critério no 28 (9 + 19, turno fixo), classificação 1 × classificação 2**
(`rodadas/A36_fixo_class1.json`, `rodadas/A36_fixo_class2.json`; todos os níveis provados nas
duas):

| Nível / critério | Classificação 1 | Classificação 2 | Conferência |
|---|---:|---:|---|
| **Essencial** | **2** | **0** | — |
| **Importante** | **45** | **41** | — |
| enfermeiro em posto de técnico | 25 | 22 | sem conferência externa: contado pela ferramenta e recontado fora dela (`medir_escala`) |
| máximo de folgas seguidas (4) | 19 | 19 | avaliador oficial com peso 1 (`*_conferencia_escala_avaliador.txt`): 19 e 19 |
| mínimo de turnos (10) | 1 | 0 | avaliador oficial com peso 1: 1 e 0 |
| **Desejável** (linhas "Só este turno") | — | **15** | sem conferência externa: contado pela ferramenta e recontado fora dela, igual pessoa a pessoa |
| máximo de fins de semana seguidos (3) | 13 | 0 | avaliador oficial com peso 1: 13 e 0 |

- Na classificação 1, as linhas estão no Essencial. Os 2 do Essencial são as 2 quebras das linhas,
  porque o pedido de folga no dia dá 0.
- O máximo de fins de semana seguidos não é considerado na classificação 1. Por isso o valor dela
  (13) vem só da conferência com peso 1.
- Nota de conferência sobre as linhas: na instância da conferência elas vão ao XML como pedidos de
  folga de turno (`ShiftOff`). O avaliador conta 2 e 15 em `shift_off_requests`, iguais às quebras.
  Essa tradução das linhas para o XML é nossa, então compartilha a premissa e não vale como
  conferência externa.

**2. Contagem da escala real** (`recontagem_v2.md`). É a contagem nossa sobre a transcrição v2
(leitura C, janela de 31 dias), pela reimplementação da penalidade (`avaliacao.py`), e foi
registrada antes das rodadas (`5d6888d`). As 21 linhas com registro entram; 6118, 4798 e 6089
ficam fora.

| Critério (limite padrão) | Violações | Pessoas com violação | Ocorrências testáveis |
|---|---:|---:|---:|
| Máx. dias seguidos, preferência (5) | 30 | 9 | 211 |
| Mín. dias seguidos (3) | 302 | 16 | 188 |
| Máx. folgas seguidas (4) | 0 | 0 | 208 |
| Mín. folgas seguidas (3) | 359 | 21 | 190 |
| Máx. fins de semana seguidos (3) | 26 | 14 | 23 |
| Mín. fins de semana seguidos (2) | 0 | 0 | 0 (sem evidência) |
| Fins de semana em 4 semanas (2) | 63 | 19 | 20 |
| Fim de semana completo | 93 | 21 | 93 |
| Mesmo turno no fim de semana | 93 | 21 | 93 |
| Máx. turnos, preferência (18) | 59 | 9 | 19 |
| Mín. turnos (10) | 0 | 0 | 19 |
| Noturno na véspera de fim de semana livre | 4 | 4 | 8 |
| Duas folgas depois de noites | 137 | 11 | 146 |

Ressalva: a contagem é sobre a transcrição, não sobre a escala executada, e não passou pelo
avaliador oficial. Os lados (violado / nunca violado / sem evidência) dão a classificação g).

**3. Alertas do COFEN nas rodadas** (campo `alertas_cofen` dos JSON):

| Quadro | Alerta da tela |
|---|---|
| equipe real de 23 (rodadas padrão e A11) | "4 enfermeiros em 23 profissionais; o Parecer pede ao menos 33% no grau intermediário, isto é, 8 — grau informado na tela" |
| quadro de 28 (classificações 1 e 2) | "9 enfermeiros em 28 profissionais; o Parecer pede ao menos 33% no grau intermediário, isto é, 10 — grau informado na tela" |
| todas as rodadas do caso A | "8 turnos sem enfermeiro na demanda (ex.: 03/11 D12, 04/11 D12, 10/11 D12, ...)": os plantões diurnos de fim de semana, com 0 enfermeiros na demanda (decisão d) |

Ressalva: 9 + 19 vem de a busca ter acrescentado as 5 pessoas como enfermeiros. A regra
`ferramenta.equipe` só acrescenta, então o máximo é 4 + 5 = 9, e a regra pediria 10
(`ceil(0,33 × 28)`). Por isso o próprio quadro de 28 dispara o alerta.

## Comportamento computacional: HiGHS × SCIP (22 e 23/10/2026)

**Aprovada pelo Otávio em 23/10/2026**, com a escolha do valor da escala para a rodada de 22/10
(INRC: avaliador oficial; medium_late05 com HiGHS: os 2.199 do diagnóstico; ferramenta: o recálculo
na escala do diagnóstico de 22/10, igual ao valor do modelo nesses casos). A rodada de 3.600 s
continua parcial (B11 não concluído); os números dela valem como estão, com essa ressalva. Pedido do
orientador (reunião de 22/10): tabela
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

Etapa 2 (equilíbrio, registrada, não decide; *medido na v1.4.4 (etapa 2 pela soma)*): não provou em nenhum caso da ferramenta, nos dois
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

Valor do modelo = valor da escala nas quatro rodadas concluídas. Etapa 2 (*medido na v1.4.4 (etapa 2 pela soma)*): não provou; no A36_livre
com SCIP, não achou escala em 2.979 s (fica a escala da etapa 1). Por caso: **medium_late05, SCIP**
(186 < 224, nenhum prova); **A36_livre, empate** (com 3.600 s o SCIP também prova a etapa 1, que em
600 s não provava). Com 3.600 s, o medium_late05 com HiGHS chega aos 224 da seção 1 (06/10).
Leitura provisória, sem o B11: o SCIP não perde nada para o HiGHS nos dois casos concluídos e ganha
um — vai ao Otávio e ao orientador; não há troca automática.

## v1.4.5 — etapa 2 por min-max (30/10/2026), PENDENTE DE APROVAÇÃO

Branch `v1.4.5-minmax`, sem merge nem tag até o ok do Otávio. Decisão: `DECISOES.md`, "2026-10-30 —
Etapa 2 por min-max (v1.4.5)": a etapa 2 passa a minimizar a **maior** amplitude da fração do
contrato entre as categorias, em vez da soma. Origem: `resultados/v145_2026-10-30/`
(`suite/tela_9.log`, na suíte; `tela_9_solo.log`, o teste 9 rodado sozinho antes, com o mesmo
desfecho). Comando: `python src	estes_ferramenta.py 9`. Esperado registrado antes (commits
`ee73ac9` e `d121b8c`). Máquina e solver: i5-10210U, HiGHS 1.15.1 via `appsi_highs`.

A marca *medido na v1.4.4 (etapa 2 pela soma)* no cabeçalho, nas seções 5, 6, 8, 9, 13 e 15 e em "Comportamento computacional: HiGHS × SCIP" quer dizer: o valor
foi medido com a etapa 2 pela soma das amplitudes, como na v1.4.4 e nas versões anteriores. A data
de cada medição está na própria seção. Nenhum desses valores foi refeito com o min-max.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| maior amplitude **4,55 pp** (técnicos 4,55 pp; enfermeiros 0 pp, não exigido) | critério da etapa 2 no 9c | **conta registrada antes** (`08603c6`; esperado do min-max em `ee73ac9` e `d121b8c`): o piso dos técnicos é 1/22 e a dos enfermeiros pode ser 0, logo o mínimo da maior é 1/22 | com min-max sem desempate, a amplitude dos enfermeiros pode subir até 4,55 pp sem custo; o 0 é o observado, não garantido |
| **18,2% → 4,5%**, provado | o critério (maior amplitude) cai da etapa 1 para a etapa 2 (9d) | esperado antes: estritamente menor | o 18,2 depende da escala da etapa 1; pela soma, a mesma linha era 36,4 → 4,5 (seção 8) |

