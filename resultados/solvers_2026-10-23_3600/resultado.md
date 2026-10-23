# Bateria HiGHS × SCIP — resultado

Regras: `DECISOES.md`, "2026-10-22 — Bateria HiGHS × SCIP" (registrada antes de rodar). i5-10210U, 11,8 GB, Windows 11; HiGHS 1.15.1 (appsi) e SCIP 10.0 (PySCIPOpt 6.3.0); 3600 s por caso, gap 0,01%, 1 thread. **Tempos: uma máquina e uma configuração só — comportamento observado, não resultado geral.**

| Caso | Solver | Nível | Variáveis | Restrições | Limite (s) | Tempo (s) | Melhor escala | Melhor limite | Gap | Ótimo provado | Avaliador oficial |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| medium_late05 | HiGHS | objetivo único (INRC) | 15.320 | 13.060 | 3600 | 3.602,7 | 224,00 | 64,00 | 71,43% | não | 224 |
| medium_late05 | SCIP | objetivo único (INRC) | 15.320 | 13.060 | 3600 | 3.600,4 | 186,00 | 58,49 | 68,56% | não | 186 |
| A36_livre_30 | HiGHS | etapa 1: Essencial + Importante | 5.320 | 20.264 | 1799 | 14,4 | 13,00 | 13,00 | 0,00% | sim |  |
| A36_livre_30 | HiGHS | etapa 2 (equilíbrio) | 5.324 | 20.325 | 3585 | 3.586,5 | 0,03 | 0,00 | 98,37% | não | 324 |
| A36_livre_30 | SCIP | etapa 1: Essencial + Importante | 5.320 | 20.264 | 1799 | 620,0 | 13,00 | 13,00 | 0,00% | sim |  |
| A36_livre_30 | SCIP | etapa 2 (equilíbrio) | 5.324 | 20.325 | 2979 | 2.978,9 | — | 0,00 | — | não | 330 |
| B11_livre_89 | HiGHS | (não rodou) | | | | | | | | | |
| B11_livre_89 | SCIP | (não rodou) | | | | | | | | | |

## Vitórias por caso (regra registrada)

Valores da etapa 1 por bloco: **modelo** (o objetivo no ponto do solver) e **escala** (recalculado fora do modelo, na escala entregue; sem prova, a vitória conta por ele).

| Caso | HiGHS: provou / modelo / escala | SCIP: provou / modelo / escala | Vence |
|---|---|---|---|
| medium_late05 | não / ['224,00'] / ['224,00'] | não / ['186,00'] / ['186,00'] | SCIP |
| A36_livre_30 | sim / ['13,00'] / ['13,00'] | sim / ['13,00'] / ['13,00'] | empate |
| B11_livre_89 | | | (incompleto) |

Placar: SCIP 1 × HiGHS 0, 1 empate(s).

## Regra de troca

- (i) o SCIP vence mais casos do que perde: **sim** (1 × 0);
- (ii) o SCIP não perde nenhuma prova que o HiGHS consegue: **sim**;
- (iii) suíte completa depois da troca: a rodar só se (i) e (ii) valerem.

**Bateria incompleta: a regra não pode ser aplicada.**
