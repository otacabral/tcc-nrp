# Opção B — esperado dos testes (registrado ANTES de implementar, 19/10/2026)

Decisão: `DECISOES.md`, "2026-10-19 — Opção B: mecanismo, tempo e critérios expostos".
Nada de `src/` mudou até o commit deste arquivo.

## (a) Identidade com a classificação padrão

Classificação padrão (pedido de folga = Essencial; enfermeiro em posto de técnico =
Importante; demais = Não considerar), orçamento 20 min, limites 600 s / 180 s.

**(a1) Entrada do solver idêntica, byte a byte, `v1.2.3` (git worktree) × depois.** Script
`docs/diagnostico/identidade_opcao_b.py`, rodado nas duas árvores. Casos: bateria nível 1
(P01–P18) e nível 2 (K1–K6), as três rodadas da demonstração (20, 19 e 18 técnicos), cada um
com acréscimos 0, 1 e 2 (a busca do menor quadro) — 81 casos. Para cada caso, três arquivos:
1. o XML da instância (`instancia_br.escrever_xml`);
2. o modelo da etapa 1 em formato LP (`symbolic_solver_labels`), como o solver o recebe;
3. o modelo da etapa 2 em LP (etapa 1 + `preparar_equilibrio` com z = 0).

**Esperado: 243 de 243 idênticos.** Controle positivo: com uma suave ligada (mínimo de folgas
seguidas no Desejável), o LP da etapa 1 do caso P01 **muda**.

**(a2) Rodadas.** Com os mesmos limites (600/180/20 min):
- bateria nível 1 (P01–P18), pelo `bateria_rodar` com saída em
  `resultados/opcao_b_2026-10-19/bateria/`: veredito, menor quadro, tentativas, diagnóstico,
  frase, `provado`, `etapa2` e as conferências **iguais** aos JSON de
  `resultados/bateria_2026-10-07/`, sem falha;
- demonstração (20, 19, 18 técnicos), por `fe.verificar` sem a tela: frases, tentativas,
  diagnóstico e alertas iguais aos de 09/10; enfermeiro em posto de técnico **24, 36, 34**;
  pedidos **6 de 6**; descanso cumpre.
- Os números da etapa 2 (fração do contrato, diferença entre colegas) dependem do limite de
  tempo e podem variar entre rodadas mesmo com o mesmo código (NUMEROS_TCC, seção 9, ressalva):
  são comparados e listados, mas diferença neles não reprova a identidade — (a1) é a prova de
  que a entrada do solver é a mesma.
- Tela: só acréscimos. Os textos que já existiam (veredito, linha "Escala desta tela",
  diagnóstico, alertas, legendas) não mudam; entram a tabela "Prioridades da escala", o campo
  de orçamento e a tabela "Resultado por critério". Na planilha, as abas Escala, Resumo e
  Legenda não mudam; entra a aba "Prioridades".

## (b) Sequência = definição (conta registrada antes)

Caso pequeno, 12×36 (D 7–19, N 19–7), início numa segunda, 28 dias, **1 enfermeiro + 2
técnicos**, demanda **D: 0 enf + 1 téc; N: 0 + 0** todos os dias, cargas de 44 h, pedidos de
folga de **Téc 1 e Téc 2 no primeiro dia**. Níveis: pedido de folga = Essencial; enfermeiro em
posto de técnico = Importante; mínimo de turnos (v = 14) = Desejável.

Conta: no 12×36 ninguém trabalha dois dias seguidos, e o teto é 14 plantões (176 h ÷ 12 h);
cada pessoa faz no máximo 14 dos 28 dias.
- Essencial: os dois pedidos atendidos (o dia 1 fica com o enfermeiro) → **0**;
- Importante: com os pedidos atendidos, o dia 1 exige o enfermeiro em posto de técnico; um basta
  (técnicos em dias pares e ímpares de 2 a 28: 14 + 13) → **1**;
- Desejável: enfermeiro com 1 turno (13 abaixo de 14); técnicos somam 27 com no máximo 14 cada →
  pelo menos 1 → **14**.

**Esperado: (0, 1, 14)**, pelo caminho fundido (padrão da regra) **e** pelo caminho em sequência
forçado (limite de fusão = 0), e igual à definição resolvida à parte (cada nível sozinho, com os
anteriores presos, em modelo montado no teste). Resultado por critério: pedidos 0 violações /
0 profissionais; enfermeiro em posto de técnico 1 / 1; mínimo de turnos 14 / 2.
Classificação invertida (enfermeiro em posto de técnico Essencial, pedidos Importante):
**(0, 1, 14)** também (enfermeiro não trabalha; um pedido negado; mínimo: 14 do enfermeiro).

## (c) Fusão

Sem resolver (o plano sai das fórmulas):
- demonstração, classificação padrão: **1 bloco** (fundido), coeficientes pedido 286 e
  enfermeiro em posto de técnico 1, máximo 2.001;
- demonstração com todas as suaves expostas no Desejável (limites padrão): **2 blocos** — {pedido
  286, enfermeiro 1} e {suaves, peso 1} — porque (máx. das suaves + 1) × 285 + máx. ≥ 10.000;
- o caminho usado vai ao console ("[prioridades] caminho: fundido" / "em sequência, N blocos") e
  ao `info["caminho"]`. Uma rodada da demonstração com as suaves no Desejável (limites
  600/180/20) mostra "em sequência, 2 blocos" e entrega escala que cumpre o descanso.

## (d) Situação, uma por mensagem

- 12×36, mínimo de dias seguidos = 2 → **"a CLT prevalece"**; mínimo de turnos = 20 (teto 14) →
  **"a CLT prevalece"**; mínimo de turnos = 10 → "ok";
- 12×36, fim de semana completo e mesmo turno no fim de semana → **"nunca será atendido neste
  regime"**; no 8 h em três turnos → "ok";
- máximo de dias seguidos, máximo de turnos, sequências indesejadas → **"já garantido pela
  CLT"**, em qualquer regime;
- **rodada pequena** (conferir o "mesmo turno no fim de semana", que o relatório 3c leu do
  código): o caso de (b) sem pedidos, com mesmo turno no fim de semana e fim de semana completo
  no Essencial. Conta: cada fim de semana tem 2 plantões de técnico em dias seguidos, feitos
  por pessoas diferentes, cada uma um dia só → 1 violação por pessoa-fim de semana → **8** em
  cada critério (4 fins de semana × 2), escala entregue.

## (e) Suave no Essencial não torna a escala impossível

- o caso de (b) e o caso 5 da tela (8 h, 8 + 5) com **todas** as suaves expostas no Essencial
  (limites padrão): veredito igual ao da classificação padrão (admite, mesmo quadro), escala que
  cumpre o descanso.

## Tela e padrões

- teste novo "17" (AppTest): a tabela "Prioridades da escala" existe com os 4 grupos, o grupo 1
  aberto, os padrões da ferramenta atual, "Restaurar padrão" volta ao padrão, o aviso de "todos
  no mesmo nível" aparece quando cabe, o campo de orçamento chega ao `verificar` (em segundos =
  minutos × 60), e "Resultado por critério" aparece na tela e na aba "Prioridades" da planilha;
- os padrões do módulo: `TEMPO` = 1800, `TEMPO_ETAPA2` = 1800, `ORCAMENTO` = 3600; campo da tela
  com 60 min;
- os testes antigos da tela e de entrada rodam com os limites da v1.2.3 (600/180/20 min) e
  passam sem mudar esperado.

**Suíte completa ao final** (regressão `--todos`, `testes_entrada.py`, todos os casos da tela,
um por processo). Tag `v1.3.0` só se tudo passar.
