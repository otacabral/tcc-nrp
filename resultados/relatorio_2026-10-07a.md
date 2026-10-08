# Relatório de 07/10/2026 (a) — bateria de entradas, nível 1 e casos conhecidos

## Para o Otávio

- **24 casos rodados, zero falhas nas conferências.** Toda escala gerada passou em cobertura,
  descanso medido no relógio, teto de horas e férias, conferidos por fora do modelo.
- **Os três casos que a conta diz inviáveis (P05, P11, K2) deram "faltam N"**, com o menor
  quadro coerente com a conta e o diagnóstico apontando os mesmos motivos.
- **Achado:** na família da parte A (6 h + noturno de 12 h, demanda alta de enfermeiro), K3
  (16) e K4 (17) terminam sem escala em 600 s, e K5 (18) e K6 (20) dão escala sem prova. K4
  tem folga 1 na conta: não se sabe se a escala existe.
- **Observação de uso:** em 19 dos 20 casos com etapa 2, a escala da etapa 1 sai em 1 a 21 s
  (P10: 274 s) e a etapa 2 usa até os 180 s. O usuário espera ~3 min com a barra parada.
- **Para decidir:** P12 (indicador de progresso) e se vale rodar K4 com limite maior.

Decisão: `DECISOES.md`, "2026-10-07 — Bateria de entradas começa em 07/10". Esperado: conta
independente de `docs/diagnostico/bateria_desenho.py`, registrada no commit `62bbf4d`.
Script: `docs/diagnostico/bateria_rodar.py`. Um caso por processo, em sequência, pelo caminho
de `ferramenta.verificar` (sem navegador), limites da tela (600 s e 180 s).

Máquina: a mesma do relatório de 06–07/10 (i5-10210U), `appsi_highs` (HiGHS 1.15.1). Tempos
são limite operacional, não resultado.

## Antes do solver

Os 24 casos montam sem erro de entrada, e em todos as horas de demanda e de teto da instância
batem com as da conta independente (folga em horas idêntica, caso a caso).

## Resultado

| Caso | Modelo | Equipe | Esperado pela conta | Veredito | Menor viável | Ótimo provado (etapa 1) | Etapa 1 | Etapa 2 | Falhas |
|---|---|---|---|---|---|---|---|---|---|
| P01 | 8h | 5+9 | gera escala | admite | 14 | sim | 1 s | 180 s | nenhuma |
| P02 | 6+12 | 6+6 | gera escala | admite | 12 | sim | 1 s | 53 s | nenhuma |
| P03 | 12x36 | 5+10 | gera escala | admite | 15 | sim | 2 s | 180 s | nenhuma |
| P04 | 8h | 8+6 | gera escala | admite | 14 | sim | 4 s | 2 s | nenhuma |
| P05 | 12x36 | 4+10 | **inviável** | faltam 1 | 15 | sim | 9 s | 180 s | nenhuma |
| P06 | 6+12 | 10+4 | gera escala | admite | 14 | sim | 4 s | 181 s | nenhuma |
| P07 | 8h | 5+8 | gera escala | admite | 13 | sim | 3 s | 97 s | nenhuma |
| P08 | 12x36 | 8+4 | gera escala | admite | 12 | sim | 2 s | 180 s | nenhuma |
| P09 | 8h | 6+9 | gera escala | admite | 15 | sim | 1 s | 54 s | nenhuma |
| P10 | 6+12 | 12+4 | gera escala | admite | 16 | sim | 274 s | 181 s | nenhuma |
| P11 | 12x36 | 4+9 | **inviável** | faltam 1 | 14 | sim | 5 s | 181 s | nenhuma |
| P12 | 8h | 7+6 | gera escala | admite | 13 | sim | 1 s | 88 s | nenhuma |
| P13 | 12x36 | 5+9 | gera escala | admite | 14 | sim | 3 s | 180 s | nenhuma |
| P14 | 6+12 | 11+5 | gera escala | admite | 16 | sim | 3 s | 181 s | nenhuma |
| P15 | 6+12 | 10+5 | gera escala | admite | 15 | sim | 2 s | 180 s | nenhuma |
| P16 | 8h | 9+7 | gera escala | admite | 16 | sim | 5 s | 180 s | nenhuma |
| P17 | 12x36 | 5+10 | gera escala | admite | 15 | sim | 9 s | 180 s | nenhuma |
| P18 | 6+12 | 12+5 | gera escala | admite | 17 | sim | 18 s | 181 s | nenhuma |
| K1 | 8h | 6+10 | gera escala | admite | 16 | sim | 1 s | 181 s | nenhuma |
| K2 | 12x36 | 3+6 | **inviável** | faltam 7 | 16 | sim | 21 s | 18 s | nenhuma |
| K3 | 6+12 | 11+5 | fronteira (folga 0) | **não decidido** | — | — | 600 s, sem escala | não rodou | nenhuma |
| K4 | 6+12 | 12+5 | gera escala (folga 1) | **não decidido** | — | — | 600 s, sem escala | não rodou | nenhuma* |
| K5 | 6+12 | 13+5 | gera escala (folga 2) | admite, sem prova (gap 33,3%) | 18 | não | 601 s | não rodou | nenhuma |
| K6 | 6+12 | 15+5 | gera escala (folga 4) | admite, sem prova (gap 15,8%) | 20 | não | 602 s | não rodou | nenhuma |

\* A propriedade "folga clara não termina sem escala" exige folga ≥ 2; K4 tem 1. Não é falha
pela regra registrada, mas é a expectativa não cumprida (achado abaixo).

**Inviáveis:**
- **P05:** 14 provado inviável pelo solver; 15 viável, com o acréscimo como enfermeiro.
  Diagnóstico da ferramenta: categoria e alternância. A conta independente dá horas de
  enfermeiro −18 h e ocupados por dia −1: os mesmos dois motivos, por código separado.
- **P11:** 13 descartado pelo piso, sem solver; 14 viável.
- **K2:** de 9 a 15, descartados pelo piso; 16 viável. "Faltam 7" = ocupados por dia −7 na conta.

## Achado: a família da parte A no limite de 600 s

Demanda M 2+1, T 2+1, N 3+2 (11 postos por dia, 7 de enfermeiro), modelo 6 h + noturno de 12 h.

- K3 (16) e K4 (17): o HiGHS não acha escala nenhuma em 600 s. A tela diz "Não foi possível
  gerar a escala no tempo disponível" e não afirma "faltam N" — o comportamento honesto
  previsto.
- K5 (18) e K6 (20): acha escala, não prova. A etapa 2 não roda.
- Os P com o mesmo modelo e demanda menor (P02, P06, P10, P14, P15, P18) provam o ótimo; o
  mais lento é o P10 (274 s).
- K6 é o caso do Otávio da parte A. **Por script, dá escala** — de novo não reproduz o "o
  solver falhou" visto na tela.

**Camada (C4):** solver ou modelo, não determinada. Para K4, não há escala conhecida que o
modelo recuse (o teste da parte A, a escala construída à mão, foi feito com 20). Sem isso,
não dá para separar "não existe" de "existe e o HiGHS não achou em 600 s".

**Próximo passo proposto, não executado:** rodar K4 só na etapa 1 com limite de 3.600 s
(`docs/diagnostico/caso_parte_a.py etapa1 --enf 12 --tempo 3600 --log ...`), como foi feito
com o 15 + 5 na parte A. Se achar escala, a camada é solver (tempo); se provar inviável, a
conta da bateria está frouxa e K4 entra como inviável com prova.

## Observação de uso (para a P12)

Nos 20 casos com etapa 2, a escala da etapa 1 sai em 1 a 21 s (exceto P10: 274 s). Em 15
desses 20, a etapa 2 usa os 180 s inteiros (aviso `'aborted' status, but containing a
solution` no log). Na tela, isso é a barra parada por ~3 min com uma escala já pronta.

## O que a bateria ainda não cobriu

- propriedades de monotonia e de ordem (C3, itens 2 e 3): pedem pares de casos derivados;
- honestidade lida no texto da tela e da planilha (C3, item 4): aqui foi lida no `Resultado`,
  não pela tela (AppTest);
- nível 3 (lote aleatório).

Arquivos: `resultados/bateria_2026-10-07/` (um `.log` e um `.json` por caso).
