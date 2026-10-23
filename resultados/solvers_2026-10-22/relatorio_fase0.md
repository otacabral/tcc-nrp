# HiGHS × SCIP — Fase 0 (viabilidade), 22/10/2026

Pedido do orientador (reunião de 22/10): tabela de comportamento computacional por caso e teste
do SCIP. CBC fora. Nesta fase **nada da ferramenta mudou** (`app.py`, `ferramenta.py`,
`modelo.py`, `requirements.txt` intocados). Script separado: `docs/diagnostico/comparar_solvers.py`.
Máquina: i5-10210U, 11,8 GB, Windows 11, Python 3.11.9, Pyomo 6.10.1, HiGHS 1.15.1, SCIP 10.0.

| Item | Situação |
|---|---|
| 1. Instalação por pip | **passa** |
| 2. Warmstart | **passa** (com controle) |
| 3. Tolerâncias | **passa**, com duas ressalvas de interface |
| 4. Identidade do modelo | **passa** (com controle), depois de corrigir a reescrita do objetivo |
| 5. Inventário | feito (abaixo) |
| 6. Fumaça | **passa** (sprint01: os dois provam 56; avaliador oficial 56 nas duas escalas), depois de corrigir um travamento da captura do log do SCIP (abaixo) |

## 1. Instalação
`pip install pyscipopt==6.3.0` no `.venv`. O wheel para Windows traz o SCIP 10.0 dentro; nenhum
instalador fora do pip. `pip --dry-run` antes: só entra o PySCIPOpt; Pyomo 6.10.1, highspy
1.15.1 e numpy 2.4.6 não mudam (conferido depois da instalação). Fica no `.venv`, **fora do
`requirements.txt`** (só entraria numa troca). Para tirar: `pip uninstall pyscipopt`.

**Ressalva de interface (não óbvia):** o `SolverFactory("scip_direct")` do Pyomo 6.10.1 é a
interface nova embrulhada no estilo antigo; ela declara `warm_start_capable() = False` e não
implementa `logfile` (`NotImplementedError`). O caminho que funciona é a interface nova direta
(`pyomo.contrib.solver.solvers.scip.scip_direct.ScipDirect`), com `time_limit`, `rel_gap`,
`threads`, `warmstart_discrete_vars` e o log em `results.solver_log`.

## 2. Warmstart
O Pyomo entrega ao SCIP uma solução **parcial** (só as variáveis inteiras); o SCIP a completa
pela heurística `completesol` e a registra no log.
- sprint01: a escala ótima do HiGHS como partida → "feasible solution found by completesol
  heuristic after 0.0 seconds, objective value 5.600000e+01" e "transformed 1/1 original
  solutions"; o SCIP provou 56 em ~2 s.
- Opção B, 3 níveis em sequência (o caso pequeno do teste opB-b): os blocos 2 e 3 partem da
  escala do bloco anterior, e o log mostra o `completesol` com os valores 1 e 14; valores por
  nível **0, 1, 14** — os mesmos da ferramenta com o HiGHS.
- Controle: sem partida, a linha do `completesol` não aparece.

## 3. Tolerâncias
Fixados nos dois: gap relativo de parada 1e-4 (0,01%; no HiGHS é o padrão, aqui explícito) e 1
thread (SCIP `lp/threads` = 1, e o SCIP padrão não é paralelo; HiGHS `threads` = 1).
- **Regra de 09/10** ("ótimo provado" vale como ótimo inteiro quando 0,0001 × objetivo < 1):
  **continua válida**, e mais forte. O HiGHS mede o gap como (escala − limite) ÷ |escala|; o
  SCIP, como (escala − limite) ÷ min(|escala|, |limite|), que é **maior ou igual** num problema
  de minimização com valores positivos. Parar com gap ≤ 1e-4 no SCIP implica gap ≤ 1e-4 na
  medida do HiGHS. Com limite 0 e escala > 0, o gap do SCIP é infinito: ele só para provando.
  O SCIP ainda detecta que o objetivo é inteiro ("transformed objective value is always
  integral") e pode parar quando o limite arredondado para cima alcança a escala.
- **Fusão W = M + 1** (`LIMITE_FUSAO` = 10.000, escolhido para o gap de 0,01% provar o ótimo
  inteiro): depende só de o objetivo ser inteiro e da regra acima → **continua válida**.
- **O que depende do HiGHS** (de interface, não de matemática): (a) o Pyomo traduz a parada do
  SCIP pelo gap (`gaplimit`) para `convergenceCriteriaSatisfied` → "ótimo", como faz com o
  HiGHS; mas `modelo.provou_otimo`, `gap_relativo`, `tem_solucao` e `estado` leem os campos do
  resultado no formato antigo do appsi, e teriam de ser reescritos para o formato novo; (b) a
  partida do HiGHS é a solução inteira (`setSolution`), a do SCIP é parcial e completada pelo
  SCIP — aceita nos testes, mas é outro mecanismo.

## 4. Identidade do modelo
**Achado:** a interface `ScipDirect` do Pyomo 6.10.1 **reescreve o objetivo como epígrafo**:
cria uma variável z, a restrição z ≥ objetivo e minimiza z. É equivalente, mas não é o problema
que o HiGHS recebe (no HiGHS o objetivo vai como custo das colunas), e o epígrafo pode
atrapalhar o SCIP (o objetivo deixa de estar nas colunas). No script de comparação, uma
subclasse (`ScipObjetivoDireto`) passa o objetivo direto, como custo; só esse método muda.

Prova: o problema é lido **de dentro de cada solver** depois de recebido (HiGHS: `getLp()`;
SCIP: o problema original, não o pré-processado) e posto em forma canônica — colunas por nome
da variável do Pyomo (limites e custo), as mesmas inteiras, linhas como conjunto de
(coeficientes por variável, limites; "≥" virado para "≤"), constante do objetivo.
- sprint01 (INRC): 2.978 variáveis (1.400 inteiras), 2.450 restrições — **iguais**.
- Instância da ferramenta (12×36, 4 + 8, padrão): 1.232 variáveis (todas inteiras), 4.288
  restrições — **iguais**.
- Controle: uma linha a mais só no SCIP é acusada.

## 5. Inventário do que depende do HiGHS (sem alterar nada)
**Código:**
- `modelo.py`: `SOLVER_PADRAO = "appsi_highs"`; `resolver` (dialeto do appsi: `config.time_limit`,
  `load_solutions`, `warmstart`, `log_file`, as duas armadilhas de 22/09 e 02/10); `estado`,
  `provou_otimo`, `gap_relativo`, `tem_solucao`, `carregar_solucao` (formato antigo do
  resultado).
- `ferramenta.py`: `resolver`, `equilibrar` (partida da P17) e o comentário da salvaguarda P14.
- `prioridades.py`: comentário do `LIMITE_FUSAO` (a regra vale; o texto cita o HiGHS).
- `escalabilidade_objetivo.py` e `figuras_tcc.py`: leem o **log do HiGHS** (tempo até a
  primeira escala, 90% da redução) — precisariam de um leitor do log do SCIP.
- Interface do SCIP no Pyomo: a correção do epígrafo e a interface nova (item 1).
- `requirements.txt`: `+ pyscipopt==6.3.0` (o `highspy` pode ficar).

**Textos:** a tela e o `GUIA_DE_USO.md` não citam o HiGHS (conferido). `CLAUDE.md` (stack),
`ESTADO_ATUAL.md`, `DECISOES.md` (regra de 09/10, P14, P17) e `NUMEROS_TCC.md` (17 menções:
"Máquina e solver", "afirmação fraca", limites) citam.

**`NUMEROS_TCC.md`, o que teria de ser refeito numa troca:**
- Medidas de tempo, gap ou prova, todas do HiGHS: seção 1 (o `medium_late05`, 224 sem prova,
  gap 71,88%), 5 e 6 (curvas da P1), 7 (limites), 10 (escalabilidade), 11 (bateria: provas e
  tempos), 12 (tempo-limite da etapa 1), 13 (P17).
- Valores que vêm de uma escala específica (ótimos alternativos podem mudar o número mesmo com
  o mesmo valor ótimo): 8 (carga por contrato 9a–9d), 9 (demonstração: diferença de carga,
  frações, etapa 2), 14 (validação por restrição: a divisão por tipo nos 4 ótimos).
- Não mudam: os valores ótimos provados (56, 58, 197, 219; o mesmo modelo), o menor quadro
  quando provado, e as contas sem solver (seção 4, piso).

**Tempo de máquina de uma troca (estimativa grosseira, a partir das rodadas registradas):**
regressão ~1 min; suíte completa ~4 a 5 h; bateria P01–P18 e K1–K6 ~2 a 3 h; nível 3 e
propriedades ~3 a 4 h; curvas da P1 ~3 a 4 h; P17 e `medium_late05` ~2 a 3 h; demonstração
~10 min. **Total: ~15 a 20 h de máquina**, sem contar reescrever o leitor de log e refazer
as figuras.

## 6. Fumaça e estimativa da bateria
**Achado (travamento, não lentidão):** as duas primeiras tentativas pararam com o processo em CPU
zero — a primeira foi depois encerrada pelo Claude Code por falta de memória na máquina, a
segunda ficou 37 min parada numa resolução de limite 120 s. Causa: o `ScipDirect` do Pyomo lê o
log do SCIP por um pipe, numa thread do Python, enquanto o `optimize()` do PySCIPOpt segura o
GIL. Com log maior que o buffer do pipe (o sprint01 sem partida dá 5,8 KB), o SCIP espera a
thread esvaziar o pipe e a thread espera o GIL. No script, a captura passou a um arquivo
temporário, que não enche (`_log_em_arquivo`); a ferramenta não usa o SCIP e não é afetada.
**Numa troca, a ferramenta precisaria da mesma correção** (ou de log desligado), senão trava em
qualquer caso de log grande.

Depois da correção (i5-10210U, 1 thread, gap 0,01%, limite 600 s; tempo medido numa
configuração só, não é resultado):

| Solver | Variáveis | Restrições | Tempo (s) | Melhor escala | Melhor limite | Gap | Ótimo provado | Avaliador oficial |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| HiGHS 1.15.1 | 2.978 | 2.450 | 3,2 | 56 | 56 | 0,00% | sim | 56 |
| SCIP 10.0 | 2.978 | 2.450 | 2,2 | 56 | 56 | 0,00% | sim | 56 |

Sem partida, o SCIP provou 56 em ~2 s (19 soluções no caminho). Warmstart refeito com o
controle: tudo OK. Memória do processo no sprint01: ~200 MB (observada durante a rodada; o pico
nos casos maiores não foi medido).
- **Estimativa da bateria (pior caso, pelo limite):** casos × 2 solvers × 600 s. Com os casos a
  propor depois do ok (os 4 ótimos de Santos, `medium_late05`, A36 com quadro 30 e B — ~7
  casos): **até ~2,5 h**, mais o avaliador oficial. A memória por caso do SCIP não foi medida:
  a exigência de ≥ 3 GB livres no sábado é necessária, e hoje não estava atendida.
