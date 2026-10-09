# Relatório de 09/10/2026 (c) — P17 (etapa 2 partindo da escala da etapa 1) e preferência por turno

Máquina: Intel Core i5-10210U, 12 GB, Windows 11, `appsi_highs` (HiGHS 1.15.1, Pyomo 6.10.1).
Tempos são limite operacional, não resultado.

## Para o Otávio

- **P17 implementada** (a condição se cumpriu: a interface aceita a escala da etapa 1 como
  partida, e a sonda mostrou o HiGHS aceitando). Em `modelo.py` só a chamada ao solver mudou.
  **Nenhum teste rodou** (1,4 GB livres); tudo fica no script do fim, com a regressão primeiro.
- **Relato (condição 2):** o esperado do 8b foi **apertado** antes de a sua condição chegar —
  passa a exigir que a etapa 2 entregue escala. Não afrouxou nada; se preferir como estava,
  reverto.
- **Pedido por turno:** o modelo já aceita (é o `ShiftOffRequest` do INRC, validado pela
  regressão); falta entrada, tela e pesos em três níveis — e há um risco técnico com a
  tolerância do HiGHS. Estimativa ~1,5 dia. Registrado na P3 com as outras duas preferências.
- **Para executar:** fechar os programas da lista e rodar o script (~2,5 h); se "TUDO OK",
  criar a tag com os comandos do fim.
- **Para decidir:** as preferências individuais (P3), quando quiser.


## Parte A — P17

### A1 — dá para entregar a escala da etapa 1 ao HiGHS como solução inicial? **Sim, e é simples.**

**Pela documentação e pelo código da interface.** O APPSI do Pyomo tem a opção `warmstart`
(`pyomo/contrib/appsi/base.py`: `SolverConfig.warmstart`, "use os valores atuais das variáveis
como partida"); o `solve` legado a aceita como argumento (`solve(..., warmstart=True)`). Na
interface do HiGHS (`pyomo/contrib/appsi/solvers/highs.py`), `warm_start_capable()` devolve
`True`, e `_warm_start()` monta um `highspy.HighsSolution` com os valores atuais das variáveis
e o entrega com `setSolution` antes de resolver. Não exige trocar a interface nem contorno.

**Um cuidado.** A etapa 2 cria variáveis novas (`f_max`, `f_min`: os extremos da fração do
contrato, por categoria) sem valor; o Pyomo as mandaria como 0, e a partida ficaria inviável.
Elas recebem, antes de resolver, os valores da escala da etapa 1. As variáveis da etapa 1 já têm
os valores da escala dela (`modelo.carregar_solucao`, no mesmo modelo).

**Sonda** (`docs/diagnostico/sonda_warmstart.py`, sem mexer em `src/`; caso P08, o menor;
etapa 2 com "penalidade ≤ valor da etapa 1", 20 s; saída em `resultados/p17_2026-10-09/`):

```
etapa 1: valor 0 | provado True
partida: criterio da etapa 2 na escala da etapa 1 = 0.2576
etapa 2: estado maxTimeLimit | tem solucao True
linhas do log sobre a partida: ['MIP start solution is feasible, objective value is 0.257575757576', ...]
```

O HiGHS **aceita a partida**: a escala da etapa 1 entra como solução viável, com o valor
calculado à parte. A sonda rodou com 1,4 GB livres (o menor caso, ~200 MB, 20 s); os testes do
A2 não, pelo mínimo de 3 GB.

**Onde entra:**
- `src/modelo.py`, função `resolver`: parâmetro novo `partida: bool = False`, que passa
  `warmstart=True` ao `solve`. É "onde a chamada ao solver exige": o modelo (variáveis,
  restrições, objetivo) não muda; com o padrão, a chamada é a de sempre.
- `src/ferramenta.py`: `resolver(m, tempo, partida=False)` repassa; `equilibrar(...,
  partida=escala)` preenche `f_max`/`f_min` com os valores da escala da etapa 1 e pede a partida;
  `resolver_com_objetivo` usa a partida **só no caminho sem prova**.

**Por que só no caminho sem prova:** no caminho provado nada muda — a demonstração (B2a, que o
Otávio roda) tem de sair idêntica, e uma partida mudaria o caminho de busca do HiGHS e, com ele,
possivelmente a escala equilibrada.

**Consequência:** com a partida, o HiGHS começa com a escala da etapa 1 como melhor solução, e
só a troca por outra de critério menor. A etapa 2 sempre entrega escala, e o critério (soma das
amplitudes da fração, por categoria) nunca piora. A salvaguarda da P14 fica, mas passa a ser
redundante no critério; por categoria, uma pode subir se a outra cair mais (o critério é a
soma) — o esperado abaixo confere por categoria, como pedido.

### A2 — esperado, registrado e commitado ANTES de implementar

- **Caso do Otávio, K5, K6** (`python docs\diagnostico\p14_conferir.py <caso> --p17`): as
  cinco conferências da P14 e mais uma — **6. a etapa 2 entrega escala** (`etapa2` == "ok").
  Isto é: enfermeiros em posto de técnico ≤ os da etapa 1; diferença máxima de carga entre
  colegas, em cada categoria, ≤ a da etapa 1; descanso e rígidas OK; pedidos ≥ etapa 1.
- **8b** (teste 8 da tela; esperado refeito no docstring, antes): `etapa2` == "ok" e a linha
  "sobre uma escala sem prova de ótimo".
- **P05, P08, K1:** mesmo veredito e mesmo menor quadro (nos três a etapa 1 prova: o caminho não
  muda).
- **Regressão e suíte da tela:** OK.

**Os testes NÃO rodam nesta sessão** (1,4 GB livres; mínimo de 3 GB). Comandos no fim, para o
Otávio rodar antes da demonstração e da tag.

**Condições do Otávio (09/10), registradas junto do esperado** (chegaram depois de a
implementação estar commitada, `4023949`; conferidas contra ela):
1. **Em `modelo.py`, só a chamada ao solver muda** (receber e repassar a partida); restrições e
   função objetivo intactas. *Conferido:* o diff de `modelo.py` é só a função `resolver`
   (parâmetro `partida` e o `warmstart` na chamada). **A regressão dos 4 ótimos (56, 58, 197,
   219) é obrigatória antes dos outros testes** — é o primeiro passo dos comandos do fim, e o
   script para se ela falhar.
2. **O teste 8b e o conferidor da P14 só podem ser revisados para conferir o comportamento novo;
   nenhum esperado pode ficar mais frouxo.** *Relato:* o esperado do 8b registrado na P14
   (aceitava "sobre uma escala sem prova de ótimo" OU "a da etapa 1") **foi mudado antes desta
   condição chegar** (commit `c5b0f54`), para exigir `etapa2` == "ok" e "sobre uma escala sem
   prova de ótimo". Motivo: com a partida, a etapa 2 sempre tem escala. A mudança **aperta** o
   esperado (deixa de aceitar o desfecho "a da etapa 1"), não afrouxa. O conferidor da P14
   mantém as cinco conferências; a sexta só entra com `--p17`. Se o Otávio preferir o 8b como
   estava, reverte-se.

### A3 — implementação

- `src/modelo.py`, `resolver`: parâmetro `partida: bool = False`; com `True`, passa
  `warmstart=True` ao `solve` (e levanta erro claro se o solver não aceitar). Só a chamada; com
  o padrão, nada muda — a regressão não é afetada, mas roda nos comandos do fim.
- `src/ferramenta.py`: `resolver(m, tempo, partida=False)`; `equilibrar(..., partida=escala)`
  preenche `f_max`/`f_min` com os da escala da etapa 1 e pede a partida;
  `resolver_com_objetivo` passa a escala da etapa 1 só quando a etapa 1 não provou.
- Compila; **nenhum teste rodou nesta sessão** (1,4 GB livres).

### A4 — registro

`DECISOES.md`, "2026-10-09 — P17: a etapa 2 parte da escala da etapa 1 quando não há prova";
`PROPOSTAS.md`, P17 marcada como decidida e implementada, com testes pendentes.

## Parte B — preferência por turno (só leitura)

### a) O modelo aceita pedido por turno? **Sim — o modelo, não a entrada brasileira.**

- **Estrutura:** `src/instancia.py`, `Pedido` (l. 163): `tipo` em `folga_dia | folga_turno |
  trabalho_dia | trabalho_turno`, com `turno` opcional.
- **Modelo:** `src/modelo.py`, `_adicionar_flexiveis`, bloco "pedidos individuais" (l. ~398):
  `folga_turno` entra como `peso × x[pessoa, turno, dia]`, na família `shift_off_requests` —
  o mesmo `ShiftOffRequest` do INRC.
- **Validação no modo INRC: sim.** As quatro instâncias da regressão têm pedidos por turno:
  sprint01 e sprint02, 50 cada; long01 e long02, 245 cada (`<ShiftOff>` nos XML). Os ótimos 56,
  58, 197 e 219 e o espelho do `avaliacao.py` (l. 285, `folga_turno`) só batem com eles
  codificados certo; o leitor (`src/parser.py`, l. 206) confere a contagem contra o arquivo.
- **O que não existe:** o caminho brasileiro (`instancia_br._construir_por_turnos`, l. ~952) só
  cria `folga_dia`; a `Entrada` da ferramenta só tem `pedidos` (pessoa, data); a tela só tem a
  tabela "Pedidos de folga" (pessoa, data).

### b) O que falta para a tela e para a prioridade estrita

**Entrada e tela:**
- `ferramenta.Entrada`: campo `pedidos_turno: list[(pessoa, data, turno)]`.
- `instancia_br._construir_por_turnos`: para cada pedido, conferir pessoa, data e turno, e criar
  `Pedido(tipo="folga_turno")` **para as duas variantes do turno** — no caminho brasileiro cada
  turno configurado vira dois turnos do modelo, o posto de técnico (`N`) e o de enfermeiro
  (`NE`). Como a pessoa faz no máximo um turno por dia, `peso × (x[N] + x[NE])` vale 0 ou
  `peso`: o pedido é negado uma vez só. Para técnico, `NE` não é elegível e o modelo já o pula.
- `app.py`: tabela "Pedidos de turno" (pessoa, data, turno), com o turno numa lista de escolha
  (`st.column_config.SelectboxColumn`) alimentada pelos turnos configurados.
- `ferramenta.indicadores`, tela e planilha: "pedidos de turno atendidos: k de n".

**Prioridade estrita: 1) folga do dia > 2) pedido de turno > 3) enfermeiro em posto de técnico
> 4) equilíbrio (etapa 2).** Com pesos inteiros numa resolução só (como hoje), cada nível tem de
pesar mais que tudo o que vem abaixo somado:
- enfermeiro em posto de técnico: **1** por turno; o máximo possível é `T` (total de postos de
  técnico no horizonte);
- pedido de turno negado: **W₂ = T + 1**;
- folga do dia negada: **W₁ = W₂ · S + T + 1**, com `S` = número de pedidos de turno.
- O equilíbrio continua na etapa 2, com a penalidade presa (ou ≤, sem prova).

Sem pedidos de turno (`S` = 0), `W₁ = T + 1` = o `W` de hoje: **o objetivo de todo caso sem
pedido de turno fica idêntico.**

**Risco de pesos grandes: a tolerância relativa do HiGHS.** O HiGHS para quando o gap relativo
fica em 0,01% (`mip_rel_gap` padrão; o log diz "tolerance: 0.01%"). Hoje isso é seguro na
prática: na demonstração há `T` = 285 postos de técnico (3.420 h ÷ 12 h), então `W` = 286; o
objetivo é 24 sem pedido negado e ~310 com um, e 0,01% disso é 0,03 < 1. Só passaria de 1 com 35
ou mais folgas negadas (35 × 286 ≈ 10.000). Com três níveis, `W₁` cresce com `S`: com `T` = 285 e
`S` = 50, `W₁` = 287 × 50 + 286 = 14.636, e **uma** folga negada já põe 0,01% do objetivo acima
de 1 — o HiGHS poderia declarar "ótimo" uma escala com um enfermeiro em posto de técnico a mais. Correção: tolerância absoluta abaixo de 1 (`mip_abs_gap` = 0,99, válida porque o objetivo
é inteiro) ou `mip_rel_gap` = 0. É parâmetro da chamada ao solver, mas muda o critério de parada
de toda resolução: precisa de esperado e da regressão. Alternativa sem pesos grandes: resolver em
camadas (lexicográfico, como a etapa 2 já faz) — mais resoluções, mais tempo.

### c) Esforço e risco

| Item | Estimativa |
|---|---|
| Entrada, `instancia_br`, `pesos` em três níveis, indicadores | 3–4 h |
| Tela (tabela com lista de turnos, validação, textos), planilha, guia | 2–3 h |
| Tolerância do solver (`mip_abs_gap`) com esperado | 1 h + rodadas |
| Testes novos (pedido de turno atendido; prioridade estrita; turno apagado) | 2 h + máquina |
| Suíte completa, regressão, 544 XML, demonstração | ~2,5 h de máquina |

- **Números da demonstração e da bateria:** não devem mudar — nenhum caso tem pedido de turno,
  e com `S` = 0 os pesos são os de hoje. A tolerância absoluta, se entrar, pode mudar *quando* o
  solver para (não o ótimo provado); tem de ser conferida na demonstração e na bateria.
- **Regressão: sim, obrigatória** se a chamada ao solver mudar (tolerância). Se só a entrada
  brasileira mudar, o modelo não muda e a regressão segue valendo, mas roda pelo portão.
- **XML do caminho dos experimentos:** a mudança em `instancia_br` tem de manter os 544 XML
  idênticos (parâmetro novo com padrão vazio).
- **Risco principal:** a tolerância (acima). Risco secundário: a contagem de "atendidos" na tela
  tem de olhar as duas variantes do turno.

### d) Turnos editáveis: o que acontece com pedidos já lançados?

O pedido guarda o **nome** do turno (escolhido numa lista, não digitado). Se o usuário depois
**renomear ou apagar** o turno na configuração:
- **Proposta:** a tabela de pedidos de turno **não se refaz sozinha** (é dado do usuário, ao
  contrário da grade de demanda por data, que se refaz quando os turnos mudam). Os pedidos que
  apontam para turno que não existe mais ficam **marcados** na tabela, e "Gerar escala" mostra
  "Entrada inválida: pedido de turno de Ana Ribeiro em 20/11 para o turno 'N', que não existe
  mais" — **nem apagar em silêncio, nem trocar de turno por conta própria**. É o mesmo
  tratamento que a ferramenta já dá a demanda para turno inexistente
  (`instancia_br.demanda_por_turno`: "demanda para turno inexistente").
- Renomear (N → Noite) quebra o pedido do mesmo jeito; o usuário corrige escolhendo de novo na
  lista. Custo: incluído na linha "tela" da estimativa (+1 teste).

### Registro na P3

`PROPOSTAS.md`, P3: "Preferências individuais" — (1) pedido por turno (com esta análise);
(2) indisponibilidade recorrente (ex.: segundo vínculo toda terça); (3) marcação por
profissional "exige 35 h de descanso semanal". Decisão do Otávio depois.

## Para rodar: fechar a v1.2 (P14 + P17 + demonstração)

### Antes: feche estes programas

- **Chrome** — inclusive o que fica rodando em segundo plano: botão direito no ícone do Chrome
  perto do relógio → Sair. Se não houver ícone: Gerenciador de Tarefas → "Google Chrome" →
  Finalizar tarefa.
- **Claude Code** (este terminal) e o app do Claude: ocupavam ~870 MB na última rodada.
- Qualquer Streamlit aberto (janela do PowerShell com `streamlit run`: Ctrl+C e feche).
- Outros programas pesados (Teams, Word com documentos grandes, etc.).

### Confira a memória livre (mínimo 3 GB)

No PowerShell:

```
(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
```

O número é a memória livre em GB. Se for **menor que 3**, feche mais programas ou reinicie o
computador antes. (O script também confere, antes de começar e antes de cada rodada da
demonstração, e para sozinho abaixo de 3 GB.)

### Rode tudo (uma vez, ~2,5 h; a ordem e as paradas estão no script)

No PowerShell, na pasta do repositório:

```
cd D:\dev\tcc-nrp
.\.venv\Scripts\Activate.ps1
& "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v12.sh
```

O script, na ordem, **parando na primeira falha**:
1. regressão dos 4 ótimos (56, 58, 197, 219) — obrigatória antes de tudo;
2. testes de entrada;
3. P17 no caso do Otávio, K5 e K6 (a etapa 2 sempre entrega escala e não piora);
4. P08, P05 e K1, comparados com 07/10;
5. a suíte da tela inteira (8, 15, 12, 1-2, 3, 4, 4b, 5, 7.1–7.4, 9, 9b, 9c);
6. a demonstração pela tela (B2a), com o conferidor, e a comparação com 24/36/34 e 6 de 6.

Resumo em `resultados\fechar_v12\resumo.txt`. A última linha diz **"TUDO OK"** ou
**"PARADO: …"** com o motivo.

### Se terminar com "TUDO OK": commit e tag v1.2

```
git add -f resultados/fechar_v12
git add docs/demonstracao
git commit -m "v1.2: P14 e P17 conferidas, demonstracao identica"
git tag -a v1.2 -m "v1.2: P15, P14 e P17; validacao encerrada"
git push origin main --tags
```

- `git add -f resultados/fechar_v12`: põe os logs no commit (a pasta `resultados/` é ignorada
  pelo git, por isso o `-f`).
- `git add docs/demonstracao`: as capturas e planilhas novas da demonstração.
- `git tag -a v1.2 …`: marca este commit como a versão citável.
- `git push origin main --tags`: envia o commit e a tag para o GitHub.

### Se terminar com "PARADO"

Não crie a tag. Me traga o `resultados\fechar_v12\resumo.txt` e o `.log` do passo que parou.
Se parou por memória, feche mais programas e rode o mesmo comando de novo (ele recomeça do
início).

---

# Continuação (09/10, noite) — decisões e conferência da tolerância

## Para o Otávio (continuação)

- **8b mantido apertado** e **pedido por turno em trabalho futuro**: registrados.
- **Conferência da tolerância: PARADA, como pedido.** Três "ótimos provados" da curva da P1 de
  03/10 (N = 40, 60, 80) têm 0,0001 × objetivo ≥ 1. **Mas os logs do HiGHS mostram, nos três,
  limite inferior = objetivo** (prova exata, gap 0). Nada mudou no `NUMEROS_TCC.md`.
- **Para decidir:** registrar no `NUMEROS_TCC.md` a condição em duas formas (abaixo).

## 1 e 2 — registros

- **8b:** `DECISOES.md`, entrada da P17: "manter o 8b apertado; não reverter".
- **Pedido por turno:** `DECISOES.md`, "2026-10-09 — Pedido por turno vira trabalho futuro",
  com o motivo (1,5 dia; mudança da tolerância do solver e regressão; prioridade do texto) e o
  argumento (o motor já suporta `folga_turno`, validado pela regressão; faltam a entrada
  brasileira, a tela e os pesos); P3 atualizada.

## 3 — a tolerância relativa do HiGHS (0,01%) afeta algum "ótimo provado" registrado?

Só leitura, sem solver. O HiGHS declara "ótimo" quando o gap relativo fica ≤ 0,01%. Como os
objetivos da etapa 1 são inteiros, se 0,0001 × objetivo < 1 a prova vale como ótimo inteiro.

| Resultado com prova | Objetivo | 0,0001 × objetivo |
|---|---|---|
| INRC (seção 1): sprint01, sprint02, long01, long02 | 56, 58, 197, 219 | 0,006 a 0,022 |
| Experimento B (seção 3): menor e maior penalidade do mais penalizado | até 20 | ≤ 0,002 |
| 9b-sem-teto (seção 8): máximo de plantões | 14 | 0,001 |
| Demonstração (seção 9), etapa 1 | 24, 36, 34 (nenhum pedido negado) | ≤ 0,004 |
| P1 com folga, 05/10 (seção 6): N = 44, 66, 88 | 107, 181, 267 | ≤ 0,03 |
| Bateria (seções 11 e 12): 198 resoluções com prova (07/10, 08/10, 09/10) | teto W × pedidos + T, no máximo 1.966 | **≤ 0,197** (`resultados/p17_2026-10-09/tolerancia_bateria.txt`) |
| **P1 de 03/10 (seção 5): N = 36** | 9.541 | 0,95 |
| **P1 de 03/10: N = 40** | 10.745 | **1,07** |
| **P1 de 03/10: N = 60** | 22.989 | **2,30** |
| **P1 de 03/10: N = 80** | 53.572 | **5,36** |

**Três ≥ 1: P1 de 03/10 com N = 40, 60 e 80.** Na regra combinada, isso é parada.

**O que os logs dizem** (`resultados/escalabilidade_objetivo/highs_N{40,60,80}_etapa1.log`,
relatório final do HiGHS, com até 12 algarismos significativos):

| N | Primal bound | Dual bound | Gap |
|---|---|---|---|
| 40 | 10745 | 10745 | 0% |
| 60 | 22989 | 22989 | 0% |
| 80 | 53572 | 53572 | 0% |

Nos três, o limite inferior **é igual** ao objetivo: a prova é exata, não "dentro da tolerância".
Os números da seção 5 (21, 21, 29 e 50 pedidos negados; 140, 224 e 322 enfermeiros em posto de
técnico) **não estão em risco**. O risco seria uma rodada futura parar com gap entre 0 e 0,01%
num objetivo grande — o que não aconteceu em nenhuma registrada.

**Fora do critério inteiro:** a etapa 2 tem objetivo **contínuo** (amplitude da fração do
contrato); a tolerância de 0,01% sobre 4,55 pp (9c) é 0,0005 pp — irrelevante, mas o argumento
do "objetivo inteiro" não se aplica a ela.

**Proposta de registro no `NUMEROS_TCC.md` (NÃO feito, por causa da parada):** como condição
das afirmações de ótimo — "a prova vale como ótimo inteiro porque 0,0001 × objetivo < 1 (todos
os casos, exceto a P1 de 03/10 com N = 40, 60 e 80); nesses três, o limite inferior registrado
no log é igual ao objetivo (gap 0 exato)".
