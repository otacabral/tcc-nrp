# Relatório de 09/10/2026 (a) — demonstração refeita, tag v1.1, nível 3

Máquina: Intel Core i5-10210U, 12 GB, Windows 11, `appsi_highs` (HiGHS 1.15.1). Tempos são
limite operacional, não resultado.

<!-- PARA_O_OTAVIO -->

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

<!-- TAG -->

## 4. Nível 3 estratificado

<!-- NIVEL3 -->
