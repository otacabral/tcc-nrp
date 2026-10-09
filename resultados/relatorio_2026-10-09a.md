# Relatório de 09/10/2026 (a) — demonstração refeita, tag v1.1, nível 3

Máquina: Intel Core i5-10210U, 12 GB, Windows 11, `appsi_highs` (HiGHS 1.15.1). Tempos são
limite operacional, não resultado.

## Para o Otávio

- **Demonstração refeita e conferida.** Os três feriados entraram nas datas certas; o
  conferidor passou nas três rodadas; vereditos, cortes, diagnóstico e todos os números saíram
  **iguais** aos de antes (as escalas mudaram, os totais não — explicado abaixo).
- **Tag `v1.1` criada e enviada** (commit `d397c40`).
- **Nível 3: 100 de 100 casos rodaram, 0 falhas** nas propriedades 1, 4, 5 e 6. 40 de 40 casos
  de folga clara geraram escala; nenhum caso inviável pela conta foi admitido.
- **7 casos não decididos, todos no modelo 6 h + noturno de 12 h** — a mesma família do K3/K4.
  Vai para as limitações; nada a corrigir.
- Nada para você executar. Nenhuma decisão pendente desta sessão.


## 1. Demonstração refeita com o roteiro corrigido

**Antes de rodar.**
- Roteiro corrigido (`docs/demonstracao/capturas.py`, função `colar_na_data`): acha a linha
  do feriado pela data e confere a colagem. Esperado registrado e commitado antes (`882edf1`,
  seção de 08/10 de `docs/demonstracao/cortes_esperados.md`).
- Chrome: janelas fechadas pelo Otávio; ficaram processos do Chrome em segundo plano
  (`--no-startup-window`, ~900 MB). Memória livre antes de começar: 3,5 GB.
- Teste do roteiro sem gerar escala (`capturas.py teste_preencher --so-preencher`): os três
  feriados colados e conferidos nas linhas certas (02/11 na linha 0, 15/11 na 13, 20/11 na 18).

**As três rodadas** (`bash docs/demonstracao/rodar_rodada.sh …`, um processo por rodada,
conferidor no fim de cada uma):

| Rodada | Esperado (`882edf1`) | 05/10 (feriado em 24/11) | 09/10 (feriado em 20/11) | Conferidor |
|---|---|---|---|---|
| 20 téc. (30) | admite, 0 alertas, enf. em posto téc. ≥ 24 | admite, 0 alertas, 24 | **admite, 0 alertas, 24** | OK |
| 19 téc. (29) | admite, 1 alerta (QP 29,85), ≥ 36 | admite, 1 alerta, 36 | **admite, 1 alerta (QP 29,85), 36** | OK |
| 18 téc. (28) | falta 1, menor 29; alternância em 03–04/11 (28 plantões, 27 pessoas); ≥ 34 na escala de 29 | idem, 34 | **idem, 34** | OK |

**Os demais números, lado a lado** (aba Resumo das planilhas):

| | 20 téc. — 05/10 → 09/10 | 19 téc. — 05/10 → 09/10 | 18 téc. (escala de 29) — 05/10 → 09/10 |
|---|---|---|---|
| pedidos atendidos | 6 de 6 → 6 de 6 | 6 de 6 → 6 de 6 | 6 de 6 → 6 de 6 |
| contrato cumprido (mín.–máx.) | 68–100% → 68–100% | 82–100% → 82–100% | 75–100% → 75–100% |
| horas não utilizadas (enf. / téc.) | 432 / 108 h → 432 / 108 h | 288 / 108 h → 288 / 108 h | 312 / 116 h → 312 / 116 h |
| diferença entre colegas (enf. / téc.) | 1 / 0,6 plantão → 1 / 0,6 | 0,2 / 0,6 → 0,2 / 0,6 | 0,9 / 0,6 → 0,9 / 0,6 |
| conferência de descanso | cumpre → cumpre | cumpre → cumpre | cumpre → cumpre |

**Resultado idêntico depois de uma correção é sinal de alarme** (`CLAUDE.md`), então foi
conferido que a correção chegou à escala:

| Rodada | Células diferentes (grade antiga × nova) | 20/11 antes → agora | 24/11 antes → agora |
|---|---|---|---|
| 20 téc. | 422 | D 6, D* 2, N 5 → D 4, D* 1, N 4 | D 4, D* 1, N 4 → D 6, D* 2, N 5 |
| 19 téc. | 393 | idem | idem |
| 18 téc. | 416 | idem | idem |

As escalas mudaram; os agregados não, porque as horas de demanda são as mesmas (4.308 h) e a
contagem de enfermeiro em posto de técnico já estava no mínimo aritmético nas três rodadas.

**Conferidor** (`docs/demonstracao/conferir_planilhas.py`, independente da entrada), nas três:
cobertura igual à demanda declarada em todos os dias; rígidas ok; descanso cumpre (menor folga
0 h, semanal 36 h, 1 dia seguido); teto ok; férias ok.

**Tempos do clique** (limite operacional, máquina acima): escala da etapa 1 na tela aos 10, 12
e 30 s; resultado final aos 194, 94 e 214 s. Memória livre mínima: 2,7 GB na rodada 1.

**Defeito menor, achado ao conferir as capturas:** as fotos `*_equilibrando.png` saíram com o
resultado final, não com a caixa provisória: depois de ver o aviso, o roteiro chamava
`esperar()`, que aguarda a tela terminar de calcular. A detecção do aviso vale (o texto
"Escala pronta; equilibrando" foi achado na tela aos 10–30 s); a foto não. As três fotos foram
apagadas, o roteiro corrigido (sem nova rodada), e o guia não cita a imagem.

## 2. Arquivos que citam a demonstração — atualizados

- `resultados/NUMEROS_TCC.md`, seção 9: a ressalva de 08/10 virou o registro do defeito e da
  correção, com os valores confirmados.
- `GUIA_DE_USO.md`: o que a tela mostra durante o cálculo (fases, escala da etapa 1, limite de
  20 min), as mensagens novas de tempo esgotado e de erro técnico, e a nota sobre o conferidor
  das planilhas. Os números da demonstração no guia não mudam.
- `docs/demonstracao/`: capturas de entrada e resultado, planilhas, textos da tela e memória
  das três rodadas, de 09/10.
- `DECISOES.md`: o registro da demonstração refeita, na entrada do defeito.
- `ESTADO_ATUAL.md`: nota da `v1.1`.

## 3. Tag v1.1

Tag anotada `v1.1` no commit `d397c40` ("v1.1: demonstracao refeita com o roteiro corrigido…"), enviada
com `git push origin main --tags`. Criada **depois** de a demonstração bater inteira com o
esperado de `882edf1`. O `ESTADO_ATUAL.md` registra a `v1.1` como a versão citável do TCC.

## 4. Nível 3 estratificado

`python docs\diagnostico\bateria_nivel3.py --lote`, sem supervisão, de 02:40 até ~04:30 de
09/10. Semente 20261008; casos e esperados commitados antes (`b8ce2ae`). Só a etapa 1, 600 s por
resolução, no máximo 15 min por caso, um processo por caso. Memória livre ao começar: 3,33 GB
(o mínimo combinado era 3 GB). O primeiro caso (N001) rodou sozinho até o fim antes do lote.
**Não caiu por memória; os 100 casos rodaram.** Soma dos tempos: 1,7 h (limite operacional).

**Propriedades (C3 do desenho):** **0 falhas em 100 casos.**

| Propriedade | Onde vale | Resultado |
|---|---|---|
| 1. Toda escala passa nas conferências por fora do modelo (cobertura e um turno por dia, descanso no relógio, teto de horas, férias) | 93 casos com escala | 93 de 93 |
| 4. Honestidade: "faltam N" só com o quadro informado provado inviável; "provado" só com gap ≤ 0,01%; escala sem prova com o aviso "pode haver uma melhor" | 30 "faltam" (20 provados pelo piso, 10 pelo solver); 92 escalas provadas; 1 sem prova (N026, gap 36,2%, com o aviso) | sem violação |
| 5. Folga clara (menor folga da conta ≥ 2) não termina sem escala | 40 casos | 40 de 40 admitem |
| 6. Conta inviável → a ferramenta não admite o quadro informado | 30 casos | nenhum admitido |

**Veredito por estrato:**

| Estrato | Casos | Admite | Faltam N | Não decidido (600 s) | Não determinado (15 min) |
|---|---|---|---|---|---|
| Folga clara | 40 | 40 | 0 | 0 | 0 |
| Fronteira (folga 0 ou 1) | 30 | 23 | 5 | 2 | 0 |
| Inviável pela conta | 30 | 0 | 25 | 4 | 1 |
| **Total** | **100** | **63** | **30** | **6** | **1** |

Na fronteira, a conta é só condição necessária: 23 admitiram, e 5 a ferramenta provou
insuficientes. Isso não contradiz nada: folga 0 ou 1 pela conta não garante escala.

**Casos não decididos, à parte — todos no modelo 6 h + noturno de 12 h:**

| Caso | Estrato | Equipe | Menor folga da conta | O que aconteceu |
|---|---|---|---|---|
| N005 | fronteira | 8 + 9 | 0 (ocupados por dia) | 17 provado inviável pelo solver; 18 sem resposta em 600 s |
| N072 | fronteira | 8 + 11 | 0 (ocupados por dia e por dia de enf.) | 19 (o informado) sem resposta em 600 s |
| N004 | inviável | 8 + 4 | −1.011 h; ocupados por dia −7 | 12 a 17 pelo piso; 18 provado inviável pelo solver (as duas composições); 19 sem resposta em 600 s |
| N013 | inviável | 7 + 3 | −957 h; ocupados por dia −8 | 10 a 15 pelo piso; 16 e 17 provados inviáveis pelo solver; 18 sem resposta |
| N030 | inviável | 3 + 6 | −1.223 h; ocupados por dia −8 | 9 a 15 pelo piso; 16 provado inviável pelo solver; 17 sem resposta |
| N035 | inviável | 7 + 9 | −282 h; ocupados por dia −2 | 16 e 17 pelo piso; 18 provado inviável pelo solver; 19 sem resposta |
| N006 | inviável | 5 + 3 | −1.847 h; ocupados por dia −12 | 15 min sem terminar (processo encerrado pelo lote) |

**Por modelo e estrato:**

| Modelo | Folga clara | Fronteira | Inviável | Não decididos |
|---|---|---|---|---|
| 12×36 | 9 | 14 | 7 | 0 |
| 8 h | 26 | 2 | 9 | 0 |
| 6 h + 12 h | 5 | 14 | 14 | **7** (2 da fronteira, 5 dos inviáveis) |

Leitura: os 7 não decididos estão todos no 6 h + noturno de 12 h, o mesmo modelo da família
K3/K4 da parte A, cuja escala com 17 existe mas o solver nem sempre acha em 600 s. Nos
inviáveis, a ferramenta já disse que o quadro informado é insuficiente quando a conta provou
(o piso), e parou sem afirmar o menor quadro viável — o comportamento honesto. É a mesma
limitação registrada em 08/10 (`DECISOES.md`, "Bateria: K3/K4 longos não rodam de novo"):
casos de fronteira e desta família podem não ser decididos no tempo e na memória disponíveis.
O piso da ferramenta não enxerga a conta de "ocupados por dia" para turnos de 12 h misturados a
turnos curtos (P13, candidata a melhoria, não implementada): por isso, nos inviáveis do 6 h +
12 h, a busca chega ao solver em tamanhos que a conta da bateria já prova insuficientes.

Arquivos: `resultados/bateria_2026-10-08/parte4/` (um `.json` e um `.log` por caso),
`nivel3_lote.log`, `nivel3_resumo.md` (a tabela de todos os 100).
