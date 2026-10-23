# Sensibilidade ao tempo, HiGHS × SCIP, 3.600 s por caso — PARCIAL (23/10/2026)

Registro antes de rodar: `DECISOES.md`, "2026-10-23 — Sensibilidade ao tempo, HiGHS × SCIP,
3.600 s por caso" (commit `e8a87f2`; `src/` idêntico ao `ed621a2`, com a P20; cada caso registra
o commit e "src sem mudanças"). **ANÁLISE DE SENSIBILIDADE: não reabre a regra de troca de 22/10.**
A seção "Regra de troca" que o script imprime em `resultado.md` é genérica e **não se aplica** a
esta rodada.

## Situação: 4 de 6 rodadas
A rodada foi **interrompida pelo Claude Code por falta de memória na máquina** durante o
`B11_livre_89` com HiGHS (começou com 5,1 GB livres; o pico desse processo não ficou registrado;
depois da interrupção, 5,0 GB livres e nenhum processo da bateria vivo). Não foi relançada (só com
o ok do Otávio). Faltam: B11 com HiGHS e B11 com SCIP (~2 h).

## Resultado das 4 rodadas (i5-10210U, 11,8 GB; HiGHS 1.15.1 e SCIP 10.0; gap 0,01%; 1 thread)

| Caso | Solver | Etapa 1 | Valor do modelo | Valor da escala | Avaliador oficial | Etapa 2 | Memória livre antes | Pico |
|---|---|---|---:|---:|---:|---|---:|---:|
| medium_late05 | HiGHS | sem prova | 224 | 224 | 224 | — (INRC) | 5.096 MB | 527 MB |
| medium_late05 | SCIP | sem prova | 186 | 186 | 186 | — (INRC) | 5.052 MB | 411 MB |
| A36_livre_30 | HiGHS | **provada** (13) | 13 | 13 | 324 (sem violação dura) | sem prova | 5.074 MB | 1.503 MB |
| A36_livre_30 | SCIP | **provada** (13) | 13 | 13 | 330 (sem violação dura) | sem resposta: fica a escala da etapa 1 | 5.184 MB | 460 MB |

(O "avaliador oficial" na ferramenta é a penalidade INRC da escala, não o objetivo da ferramenta.)
Tabela completa por nível: `resultado.md`; dados: `<caso>_<solver>.json` e `.log`.

**Por caso (vitória pela escala, regra de 22/10):**
- `medium_late05`: **SCIP** (186 < 224; nenhum prova). Com 600 s, o HiGHS tinha 2.199 na escala
  (folgas soltas) e o SCIP 318; com 3.600 s, os dois melhoram muito, e o HiGHS chega aos 224 de
  06/10. Valor do modelo = valor da escala nos dois (folgas justas nesses pontos).
- `A36_livre_30`: **empate** — com 3.600 s o SCIP também prova a etapa 1 (13), que em 600 s não
  provava (o HiGHS prova nos dois tempos). A etapa 2 do SCIP não achou escala em 30 min.
- `B11_livre_89`: não rodou até o fim.

**Critérios com folga:** `familias_com_folga_consideradas` = vazio nos dois casos da ferramenta
(como registrado antes); a P20 não alterou nenhum valor.

**Leitura provisória (sem o B11):** com 3.600 s, o SCIP não perde nada para o HiGHS nos dois casos
que terminaram e ganha o medium_late05. Isso vai ao Otávio e ao orientador; não há troca automática.

## Para terminar
Retomar só o B11 (o driver pula o que já tem resultado), de preferência fora do Claude Code (o
Claude Code encerra processos em segundo plano quando a memória aperta), com a memória livre ≥ 3
GB. No PowerShell, um comando por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    python docs\diagnostico\bateria_solvers.py --todos --limite 3600 --saida resultados\solvers_2026-10-23_3600 --casos medium_late05 A36_livre_30 B11_livre_89
