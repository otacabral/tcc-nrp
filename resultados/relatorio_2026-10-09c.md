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
