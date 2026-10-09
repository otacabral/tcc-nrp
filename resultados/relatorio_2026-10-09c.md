# Relatório de 09/10/2026 (c) — P17 (etapa 2 partindo da escala da etapa 1) e preferência por turno

Máquina: Intel Core i5-10210U, 12 GB, Windows 11, `appsi_highs` (HiGHS 1.15.1, Pyomo 6.10.1).
Tempos são limite operacional, não resultado.

<!-- PARA_O_OTAVIO -->

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
