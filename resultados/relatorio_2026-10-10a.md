# Relatório de 10/10/2026 (a): P17 (leitura do código), v1.2.1, P18 decidida

Nesta data, só documento e versionamento. Nenhum código de `src/` mudou e nenhum solver rodou
nesta sessão. A rodada de diagnóstico do K5 foi autorizada, mas não rodou: havia 2,8 GB livres,
abaixo do mínimo de 3 GB, e ela fica com o Otávio.

## Para o Otávio

- **P17:** pela leitura do código, a etapa 2 carrega a melhor escala que o HiGHS tem quando para,
  e não a partida. Sem defeito. Falta a rodada do K5 para saber se, nos casos difíceis, o HiGHS de
  fato não melhorou em 180 s.
- **v1.2.1 é a versão citável:** código idêntico ao da v1.2, mais 23 arquivos de evidência que o
  `NUMEROS_TCC.md` cita e que estavam fora do git.
- **P18 decidida:** opção A, execução em 16–17/10.
- **Para executar:** a rodada do K5 (comandos no fim).

## 1. Recontagem pedida da P17 (manhã de 10/10): NÃO GRAVADO

O `docs/diagnostico/p14_conferir.py` grava só um resumo em JSON, não a escala de nenhuma das duas
etapas. O único arquivo de escala do caso do Otávio (`resultados/p14_p15_2026-10-09/
otavio_antes_escala.json`, 12:46 de 09/10) é de outra rodada, anterior à P14. Como a etapa 1 para no
limite de tempo e muda de rodada para rodada, ele não serve. Não houve recontagem e nada rodou de
novo.

O que os logs da v1.2 dizem (`resultados/fechar_v12/p17_*.log`):

| Caso | Configuração | Penalidade etapa 1 | Gap | Fração mín–máx (todos) | Diferença máx. entre colegas, enf / téc |
|---|---|---|---|---|---|
| Otávio | 20 enf + 10 téc, 44 h; M 7–13, T 13–19, N 19–07; demanda (enf, téc) M (2,3), T (2,3), N (3,3); fim de semana sex–dom M (2,4), T (2,4), N (3,3); alta; 28 dias desde 12/10/2026; 0 pedidos | 57 | 17,5% | 51,1–92,0% | 60 h / 24 h |
| K5 | 13 enf + 5 téc, 44 h; mesmos turnos; M (2,1), T (2,1), N (3,2); fim de semana sáb–dom sem demanda própria; intermediário; 28 dias desde 12/10/2026; 0 pedidos | 21 | 33,3% | 68,2–98,9% | 42 h / 30 h |
| K6 | 15 enf + 5 téc; o resto igual ao K5 | 18 | 5,6% | 61,4–95,5% | 48 h / 18 h |

Nos três casos, os números da etapa 1 e os da escala final são **idênticos**. Pelo `CLAUDE.md`,
resultado idêntico é sinal de alarme. A conferência 3 ("diferença ≤ etapa 1") passa também se a
etapa 2 só devolver a partida, então não distingue os dois casos. O log não traz a amplitude por
categoria nem a diferença em plantões.

## 2. Saída do conferidor da demonstração da v1.2

Os `resultados/fechar_v12/demo_*.log` têm 0 KB porque o `docs/demonstracao/rodar_rodada.sh` manda
toda a saída, inclusive a do `conferir_planilhas.py`, para `docs/demonstracao/<rodada>_tela.txt`.
O `fechar_v12.sh` exige a linha "planilhas da demonstracao: OK" nesse arquivo e para se não a
encontrar. Nas três rodadas (arquivos de 18:22, 18:26 e 18:32 de 09/10) aparecem as linhas:
"cobertura contra a demanda DECLARADA no caso: igual em todos os dias", "rigidas ok | descanso
cumpre | teto ok | ferias ok", "planilhas da demonstracao: OK" e "status 0".

## 3. P17: leitura do código (sem defeito)

Pergunta: quando a etapa 2 para por tempo, com partida, que valores são carregados? Resposta: os
da **melhor solução do HiGHS no momento em que ele para**. Essa solução é a partida só se nada
melhor apareceu.

- `src/ferramenta.py`, l. 376–396 (`equilibrar`): copia para `f_max`/`f_min` os valores da escala
  da etapa 1 (as variáveis `x` já têm os dela) e chama `resolver(m, tempo, partida=True)`.
- `src/ferramenta.py`, l. 352–373 (`resolver`): `modelo.resolver(..., carregar=False,
  partida=True)`, depois `modelo.carregar_solucao` e `modelo.atribuicoes` (`x` > 0,5).
- `src/modelo.py`, l. 507–510 e 518–521: `warmstart=True` e `load_solutions=False`.
- Pyomo, `pyomo/contrib/appsi/solvers/highs.py`: `_warm_start` (l. 226–244) entrega a partida com
  `setSolution` antes de otimizar (l. 271–272); `_postsolve` lê `highs.getSolution()` (l. 696), a
  incumbente depois da busca; `load_vars`/`get_primals` (l. 745–775) copiam essa solução para as
  variáveis.
- `src/modelo.py`, l. 538–555 (`carregar_solucao`): `solution_loader.load_vars()`, isto é, a
  solução do HiGHS.

Indício a favor: na sonda de 09/10 (P08, 20 s; `resultados/p17_2026-10-09/sonda_highs.log`), o
HiGHS aceitou a partida (0,2576) e melhorou duas vezes (0,1061 e 0,0682).

## 4. P17: rodada de diagnóstico do K5 (pendente)

Script `docs/diagnostico/p17_diagnostico_k5.py`. **O esperado foi commitado antes de rodar, no
commit `d9c0677`, junto com a entrada do `DECISOES.md` ("2026-10-10 — P17: etapa 2 sem melhora
nos três casos difíceis; diagnóstico").**

- **O que faz:** roda o K5 pelo caminho da tela (600 s + 180 s) e grava a escala da etapa 1 (pelo
  `aviso` que a tela usa), a da etapa 2 e o log do HiGHS da etapa 2 (`log_file`, que é só opção de
  saída). Nada de `src/` muda.
- **Recontagem:** sem `ferramenta.indicadores` nem o modelo, a partir das escalas. Calcula horas e
  plantões por pessoa, a diferença máxima entre colegas por categoria (em horas e em plantões), a
  amplitude da fração por categoria (pp) e o critério da etapa 2.
- **Do log:** lê a partida aceita, as melhoras (tempo e valor) e os limites primal e dual no fim.
- **Esperado:** se o log mostrar solução melhor que a partida, a escala final difere da etapa 1, e o
  critério recontado dela é o melhor valor do log. Se não mostrar melhora, as escalas são idênticas
  célula a célula. Qualquer outro desfecho é defeito. A mais: o critério recontado da escala da
  etapa 1 tem de ser o valor da partida no log.
- **Leitor do log:** conferido sem solver, no log da sonda de 09/10 (partida 0,2576; melhoras
  0,1061 e 0,0682; primal 0,0682; dual 0,0621).
- **Ressalva:** a etapa 1 para no limite de tempo, então a escala desta rodada pode não ser a de
  09/10. A rodada diagnostica o mecanismo; não reproduz aquela escala.

Comandos (PowerShell, na raiz, com no mínimo 3 GB livres e Chrome e Claude Code fechados):

```
.\.venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING = "utf-8"
python docs\diagnostico\p17_diagnostico_k5.py rodar --teste --saida resultados\p17_diagnostico_teste
python docs\diagnostico\p17_diagnostico_k5.py rodar
```

O primeiro comando é o teste curto (90 s + 20 s; regra de 03/10); basta terminar sem
`Traceback`. O segundo é a rodada (~13 min), com saída em `resultados/p17_diagnostico_2026-10-10/`.
Depois disso vem o defeito de texto (1c): "com a carga equilibrada entre colegas" quando a etapa 2
não melhora.

## 5. v1.2.1: evidência citada versionada

`docs/diagnostico/citados_fora_do_git.py` lê o `NUMEROS_TCC.md` inteiro e lista todo caminho
citado que o `git ls-files` não tem. Somou também os `*_completo_avaliador.txt` e os
`p17_*.json`, por pedido do Otávio, e os três logs do HiGHS da condição de ótimo, que o cabeçalho
do `NUMEROS_TCC.md` cita pelo sentido ("o limite inferior registrado no log"). A primeira versão
lia só o que estava entre crases e achou 14 arquivos: uma crase sem par desalinhava os pares. A
versão final lê o texto inteiro.

**23 arquivos, 286,5 KB:**
- `resultados/escalabilidade.csv`, `escalabilidade_objetivo.csv` e `escalabilidade_objetivo_folga.csv`;
- `resultados/escalabilidade_objetivo/`: `p1_2026-10-03_ferramenta.log`, `folga_2026-10-05.log`,
  `folga_teste_N40_2026-10-05.log` e `highs_N40_etapa1.log`, `highs_N60_etapa1.log`, `highs_N80_etapa1.log`;
- `resultados/experimento_a.csv`, `experimento_b.csv` e `experimento_b_resumo.csv`;
- `resultados/{sprint01,sprint02,long01,long02}_completo.xml` e os quatro `*_completo_avaliador.txt`;
- `resultados/p14_p15_2026-10-09/p17_{otavio,K5,K6}.json`.

Fora da lista: `pyomo.zip`, descartáveis e `instancias/` (dado público).

- **Depois do `git add -f`:** "0 arquivos fora do git", e nenhum caminho citado aponta para arquivo
  inexistente.
- **Código:** `git diff v1.2 HEAD -- src/` vazio.
- **Commit e tag:** commit `032dede`, tag `v1.2.1` ("v1.2 + evidencia citada versionada; codigo
  identico a v1.2"), enviados ao GitHub.
- **A v1.2 não saiu do lugar:** continua no commit `04f3156`.
- **`ESTADO_ATUAL.md`:** a versão citável passou a ser a `v1.2.1`.

## 6. P18 decidida e classificação da `bateria_2026-10-09/`

- **Decisão:** opção A, execução em 16–17/10, depois do congelamento dos números (`PROPOSTAS.md`,
  P18). Só quatro itens que ninguém cita como evidência vão para `historico/`, e
  `resultados/LEIA_ME.md` serve de índice. Inventário arquivo por arquivo em
  `docs/inventario_pastas_2026-10-10.csv` (742 arquivos).
- **`resultados/bateria_2026-10-09/` não é o nível 3 da bateria.** São os 6 arquivos da parte B2d
  da suíte da P14 (P08, P05 e K1 contra 07/10), gravados pelo `docs/diagnostico/suite_p14.sh` às
  13:14–13:21 de 09/10. O nível 3 (100 casos) está em `resultados/bateria_2026-10-08/parte4/`
  (199 arquivos, já versionados e citados pela seção 11 do `NUMEROS_TCC.md`).
- **Classificação:** apoio; fica onde está. O `NUMEROS_TCC.md` não muda.

## Commits de 10/10

- `5836767`: `ESTADO_ATUAL.md`, a v1.2 como versão citável.
- `ede4978`: P18 (proposta) e inventário.
- `d9c0677`: P17, leitura do código, script do K5 e esperado, antes de rodar.
- `032dede`: v1.2.1, os 23 arquivos, a P18 decidida e a nota no `ESTADO_ATUAL.md` (tag `v1.2.1`).
