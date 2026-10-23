# HiGHS × SCIP — Fase 1 (bateria), 22/10/2026

Regras registradas antes de rodar: `DECISOES.md`, "2026-10-22 — Bateria HiGHS × SCIP: casos,
regras, critério e regra de troca" (commit `bc11bb9`). Script: `docs/diagnostico/
bateria_solvers.py --todos`. Tabela completa, caso × solver × nível: `bateria/resultado.md`
(gerada pelo script); dados por caso: `bateria/<caso>_<solver>.json` e `.log`; escalas e saídas do
avaliador oficial na mesma pasta. **Nada da ferramenta mudou.**

Máquina: i5-10210U, 11,8 GB, Windows 11; HiGHS 1.15.1 (appsi) e SCIP 10.0 (PySCIPOpt 6.3.0); 600 s
por caso, gap 0,01%, 1 thread; os dois na mesma sessão, um depois do outro, caso a caso. Memória
livre antes de cada caso entre 4,6 e 6,1 GB; pico por processo de 229 a 522 MB. Tempo total ~2 h.
**Tempos: uma máquina, uma configuração — comportamento observado, não resultado geral.**

## Resumo por caso

| Caso | HiGHS | SCIP | Vence |
|---|---|---|---|
| sprint01 | 56, provado, 2,6 s | 56, provado, 2,8 s | empate |
| sprint02 | 58, provado, 2,8 s | 58, provado, 6,5 s | empate |
| long01 | 197, provado, 18,2 s | 197, provado, 33,5 s | empate |
| long02 | 219, provado, 48,4 s | 219, provado, 24,5 s | empate |
| medium_late05 | sem prova; valor relatado 7.435 (ver anomalia), escala gravada 2.199 no avaliador | sem prova; 318 (avaliador 318); limite 53,7 | **SCIP** |
| A36_livre, 30 | etapa 1 **provada** (13) em 13,4 s | etapa 1 **sem prova** em 299 s (15; limite 13) | **HiGHS** |
| A36_fixo, 30 | etapa 1 provada nos dois blocos (0 e 14) | provada nos dois blocos (0 e 14) | empate |
| B11_livre, 89 (HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA) | escala (57, sem prova, limite 0) | **nenhuma escala** em 600 s (a proteção da primeira escala rodou de novo com o resto, sem escala) | **HiGHS** |

Os 4 ótimos de Santos (56, 58, 197, 219) saíram provados nos dois, e o avaliador oficial confere
os quatro nos dois. Nos casos da ferramenta, o avaliador oficial não acusou violação de restrição
dura em nenhuma escala (A36_livre 306 / 312, A36_fixo 222 / 234, B11 1.002 — penalidade INRC das
escalas, não o objetivo da ferramenta). A etapa 2 não provou em nenhum caso da ferramenta (é
registrada, não decide).

## Vitórias e regra de troca

Placar: **SCIP 1 × HiGHS 2**, 5 empates.
- (i) o SCIP vence mais casos do que perde: **não** (1 × 2);
- (ii) o SCIP não perde nenhuma prova que o HiGHS consegue: **não** — perde a do A36_livre;
- (iii) suíte completa depois da troca: não se aplica.

**Fica o HiGHS.** A comparação entra no TCC como avaliação a posteriori (tabela de comportamento
computacional por caso, pedida pelo orientador).

*Leitura adotada na contagem (dita no script antes de rodar):* no B11, quando nenhum prova, quem
tem escala vence quem não tem nenhuma (sem escala = pior que qualquer escala). Sem essa leitura o
B11 seria empate, e o placar 1 × 1 — ainda sem troca, por (ii).

## Anomalia a esclarecer: medium_late05 com HiGHS

O HiGHS relatou 7.435 como melhor solução (`best_feasible_objective` do appsi) ao parar no
limite, mas a escala carregada das variáveis e gravada vale **2.199** no avaliador oficial e no
`avaliacao.py` (os dois concordam). No SCIP, o relatado e a escala batem (318 e 318). Ou o valor
relatado ou os valores carregados não correspondem à mesma solução. **Não muda a vitória** (318 é
menor que os dois números), mas a linha do HiGHS desse caso não vale como número até ser
esclarecida. Na ferramenta, o valor mostrado vem das variáveis carregadas (`valor_objetivo`), e
não do valor relatado pelo solver, e os casos conferidos no avaliador batiam. Diagnóstico proposto
(não rodado; ~10 min): repetir o caso só com o HiGHS e comparar o valor relatado com o objetivo
calculado nas variáveis carregadas e com a integralidade delas.

Também diferente do registrado: em 06/10 o HiGHS chegou a 224 no medium_late05 (seção 1 do
`NUMEROS_TCC.md`), noutra configuração (limite e threads padrão do HiGHS). Hoje, com 1 thread e
600 s, ficou muito pior. É coerente com a afirmação fraca: um caso difícil, sensível à
configuração.
