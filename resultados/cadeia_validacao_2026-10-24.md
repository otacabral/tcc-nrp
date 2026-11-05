# Cadeia de validação até a v1.4.4 (24/10/2026)

> **Atualização de 05/11/2026:** o caso A passa a ter evidência direta na **v1.4.5** (rodadas de 05/11, entrada de 04/11; `NUMEROS_TCC.md` §15c, aprovada em 05/11). As linhas antigas do caso A (§15.1 e §15.2) ficam como histórico.

Pedido da Orientação (24/10). Só leitura: nada rodou para este arquivo. Para o texto dizer **em que
versão cada evidência rodou e por que ela vale na v1.4.4** — ou dizer que não vale. Onde a ligação
não existe, está escrito **"não coberto"**, sem inferência.

**Versões (tags):** v1.0.1 `a43f502` (06/10) · v1.1 `6b977a3` (09/10) · v1.2.3 `b6289dd` (13/10) ·
v1.3.0 `c9a3065` (20/10) · v1.4.0 `993dc70` (20/10) · v1.4.1 `da8467b` (20/10) · v1.4.2 `649aa13`
(21/10) · v1.4.3 `81f9ce8` (22/10) · **v1.4.4 `2988cd2`** (23/10; código `ed621a2`, sem mudança em
`src/` depois).

## Os elos que ligam versões (usados na tabela)

- **Identidade da entrada do solver** (XML da instância, LP da etapa 1 e LP da etapa 2, byte a
  byte, classificação padrão, sem solver): 81 casos — bateria P01–P18 e K1–K6 e as três rodadas da
  demonstração, com acréscimos de 0, 1 e 2 — = 243 arquivos, também com os pedidos como linhas da
  tabela. Passo a passo, **243/243** em cada elo: v1.2.3 × v1.3.0 (suíte de fechamento da v1.3.0,
  `resultados/opcao_b_2026-10-19/suite/resumo.txt`, `a1_comparar`, com controle) → v1.3.0 × v1.4.0
  (`resultados/v140_2026-10-20/suite/resumo.txt`) → v1.4.0 × v1.4.1 (`v141_2026-10-20`) → v1.4.1 ×
  v1.4.2 (`v142_2026-10-21`) → v1.4.2 × v1.4.4 (`v143_2026-10-23`). Mais **24/24** nas entradas da
  fase 2 (A36 livre e fixo, A11, B11, B36), v1.4.1 → v1.4.2 → v1.4.4.
- **Rodadas a2** (as rodadas registradas P01–P18 e demo 20/19/18 refeitas com a classificação padrão
  e os limites da v1.2.3, comparadas com o registrado em veredito, frase, menor quadro, tentativas,
  diagnóstico, prova, etapa 2 e falhas): **TUDO IGUAL** na v1.3.0, na v1.4.0, na v1.4.1 (admitida só a mudança
  registrada do P05: o 14 passa do solver à conta prévia) e na v1.4.2. Não rodaram na v1.4.4 (a
  suíte reduzida as dispensou porque a identidade cobre a entrada).
- **Regressão** (`src/regressao.py --todos`: ótimo provado, Tabela 6, objetivo = `avaliacao.py`,
  decomposição por profissional): passou em todas as suítes, inclusive a da v1.4.4
  (`resultados/v143_2026-10-23/suite/resumo.txt`, 37 de 37).
- **Segurança do piso** (`piso_pares.py --seguranca`): nenhum quadro viável registrado recusado pela
  conta prévia — em todas as rodadas registradas (bateria nível 1 e 2, nível 3, propriedades,
  demonstração, Parte 3); passou na v1.4.4.

## Restrições duras entre a bateria (07–09/10) e a v1.4.4

Uma só mudou: **o art. 67 com horários editáveis** (`DECISOES.md`, "2026-10-13 — Art. 67 com
horários editáveis"; v1.2.3) — o gerador de pares passou a proibir a folga isolada de menos de 24 h,
e a escala que reprova na conferência do relógio deixou de ser entregue. **Para a bateria, nenhum
par novo:** conferido byte a byte em 13/10 nos 96 XML do caminho por turnos (bateria P e K,
demonstração, casos de diagnóstico, os três modelos prontos) e nos 544 XML da grade dos
experimentos, antes × depois, idênticos; o nível 3 e os derivados das propriedades usam os horários
dos modelos prontos, cobertos pelo argumento registrado (toda folga isolada ≥ 24 h nesses horários),
**não pela conferência byte a byte**. As outras mudanças até a v1.4.4 não alteram o problema na
classificação padrão: o campo do hospital (padrão 6, igual ao de antes; depois removido), o
`DESCANSO_POR_TURNO` (vazio por padrão), as famílias de preferência (só existem quando ligadas) —
todas cobertas pela identidade de 243. Mudaram também, sem ser restrição: a etapa 2 sem prova (P14,
09/10) e a partida da etapa 2 (P17, 09/10), o piso por pares (v1.4.1), a divisão do tempo (22/10) e a
P20 (23/10).

**Parte da bateria que deixa de valer como evidência direta da v1.4.4:** nenhuma por mudança de
restrição dura. Deixam de valer como evidência direta, por outros motivos: os **números de etapa 2**
da bateria (rodada antes da P14 e da P17) e os **desfechos limitados pelo tempo** (K3, K4, os 7 não
decididos do nível 3), porque o tempo por resolução mudou (600 s antes; divisão proporcional do
orçamento hoje).

## Tabela

| Evidência | Seção do NUMEROS_TCC | Versão/commit em que rodou | O que mudou depois no modelo ou nas restrições (DECISOES) | O que liga à v1.4.4 | O que NÃO fica coberto |
|---|---|---|---|---|---|
| 4 ótimos = Tabela 6 (56, 58, 197, 219), provados | §1 | primeira vez antes de 06/10; avaliador oficial reconfirmado em 06/10 (v1.0.1, `validar.py` corrigido); **refeito em toda suíte** | caminho do INRC: `modelo.py` só ganhou a partida da etapa 2 (P17, 09/10; não é restrição) e as famílias de preferência (21/10, só quando ligadas — o parser do INRC nunca as liga); `avaliacao.py` e `parser.py` sem mudança desde 06/10 | **regressão na v1.4.4** (`v143_2026-10-23/suite/resumo.txt`: ótimo provado, Tabela 6, espelho do `avaliacao.py`, decomposição) — evidência direta | o **avaliador oficial** não rodou nas escalas da v1.4.4 (a regressão confere com o `avaliacao.py`, que foi conferido contra o avaliador); identidade byte a byte do LP do INRC entre versões: **não coberto** (só os 81 casos brasileiros) |
| medium_late05: 224 sem prova (alvo de validação) | §1 | 06/10 (v1.0.1) | idem | refeito na v1.4.4 em 23/10 (sensibilidade, HiGHS 3.600 s, 1 thread): **224**, avaliador oficial 224 (seção "Comportamento computacional: HiGHS × SCIP") | condição diferente da de 06/10 (limite e threads); uma rodada |
| Validação por restrição nos 4 ótimos (duras = 0; avaliador × modelo por tipo e por profissional; controle de 20 escalas) | §14 | árvore de 19/10, depois da v1.2.3 e antes da v1.3.0 (esperado `8d20313`, controle `d44daef`); sem solver, sobre as 4 escalas ótimas gravadas | idem §1 (nenhuma restrição do INRC mudou; `avaliacao.py` igual) | regressão na v1.4.4: objetivo = `avaliacao.py` e decomposição por profissional, nas escalas que ela acha | a comparação **por tipo com o avaliador oficial** e o controle de 20 escalas **não foram refeitos na v1.4.4**; valem sobre a semântica (inalterada), não como execução da v1.4.4 |
| Bateria nível 1 e 2 (P01–P18, K1–K6): 24 casos, 0 falhas; 3 de 3 inviáveis pela conta | §11 | 07/10, entre a v1.0.1 e a v1.1 (esperados `62bbf4d`) | art. 67 (13/10): **nenhum par novo** nesses casos (XML byte a byte, 13/10); o resto não muda o problema no padrão | P01–P18: **a2 = TUDO IGUAL na v1.4.2** (`v142_2026-10-21/suite/resumo.txt`) + identidade 243/243 v1.4.2 × v1.4.4; K1–K6: identidade da entrada v1.2.3 → v1.4.4 (os 81 casos incluem K1–K6) | **K1–K6 não foram refeitos** depois de 07/10: a entrada é a mesma, o desfecho não foi reexecutado; K3 e K4 (não decididos no tempo) e os números de etapa 2: **não coberto** na v1.4.4 (o tempo e a etapa 2 mudaram); identidade do LP entre 07/10 e a v1.2.3: **não coberto** (só o XML foi comparado em 13/10) |
| Bateria — propriedades 2 e 3 (96 derivados, 0 violações) e K4/dominância | §11 | 08/10, entre a v1.0.1 e a v1.1 (`ff54b2b`, `57de0c4`); só etapa 1, 600 s | art. 67: sem par novo pelo argumento registrado (horários dos modelos prontos), **sem conferência byte a byte** | segurança do piso na v1.4.4 (nenhum quadro viável registrado recusado pela conta) | os derivados **não estão** nos 81 casos da identidade e **não foram refeitos**: **não coberto** como evidência direta da v1.4.4 |
| Bateria nível 3 (100 casos sorteados; 0 falhas; 7 não decididos no 6 h + 12 h) | §11 | 09/10, entre a v1.0.1 e a v1.1/v1.2 (`b8ce2ae`); só etapa 1, 600 s | idem propriedades | segurança do piso na v1.4.4 | **não estão** nos 81 casos e **não foram refeitos**: **não coberto**; os 7 não decididos dependem do tempo, que mudou |
| Conferência do descanso no relógio (`docs/conferencia_descanso_escala.py`: 11 h, 36 h, folga isolada ≥ 24 h, 6 dias seguidos) | transversal (§8, §9, §11, §15) | desde 23/09; obrigatória na entrega da escala desde 13/10 (v1.2.3, "segunda proteção") | 09/10 (P15: alerta de 35 h, sem bordas — medida a mais, não muda a reprovação); 20/10 (`DESCANSO_POR_TURNO`, vazio por padrão = a regra de sempre) | roda em toda escala entregue pela v1.4.4; teste 16 (escala que reprova não é entregue) na suíte da v1.4.4; testes de tela com "descanso cumpre" na mesma suíte | **compartilha a premissa com o modelo** (a mesma `descanso_exigido`): confere a aritmética e a coerência com o gerador, **não a leitura legal**; descanso nas bordas do horizonte: **não coberto** |
| Identidade 243/243 (com e sem linhas) e 24/24 | elo, não seção | cada suíte da v1.3.0 à v1.4.4 (a da v1.3.0 contra a v1.2.3) | — (é o próprio elo) | `v143_2026-10-23/suite/resumo.txt` (`id_comparar`, `id_comparar_regras`, `pref_fase2_comparar`) | prova a **entrada** do solver na **classificação padrão**, não a saída; **não coberto:** classificações não padrão (critérios de folga, preferências), a P20 (só age depois de nível sem prova com critério de folga), a divisão do tempo (o tempo não entra no LP), entradas fora dos 81 + 8 casos |
| **Histórico (substituída pela §15c em 05/11; entrada antiga):** Caso A, fase 2 (A36 livre e fixo: faltam 6, menor viável 30; A11 admite 24; B11 admite 89 sem prova; B36 sem escala até 101) | §15.1 (histórico) | 21/10, **v1.4.1** (`9afa334`); 1.800 s por nível e na etapa 2, orçamento 60 min | v1.4.2 e v1.4.3 (sem efeito no padrão; identidade); divisão do tempo (22/10); P20 (23/10; sem efeito: a classificação padrão não tem critério de folga) | identidade **24/24** das entradas da fase 2 v1.4.1 → v1.4.2 → v1.4.4; os quadros recusados pela conta (A 24–29, B 89–101) e os provados (A 30, A11 24) não dependem do tempo | os desfechos **sem prova** (B11) e a etapa 2 dependem do tempo, que mudou: **não coberto** na v1.4.4; as rodadas da fase 2 não foram refeitas na v1.4.4 |
| **Histórico (substituída pela §15c em 05/11; entrada antiga):** Caso A pela prática (A11 24 ordem 1; A36 30 ordens 1 e 2) | §15.2 (histórico) | 24/10, **v1.4.4** (commit da rodada `ce0f6d9`; `src/` = `ed621a2`) | — (rodou na versão citável) | evidência direta: rodou na v1.4.4; avaliador oficial nas três escalas (dura e por critério) | uma rodada por ordem; etapa 2 do A36 ordem 1 sem prova (não afeta os níveis de prioridade, todos provados); "enfermeiro em posto de técnico" sem conferência externa |
| Caso A com a entrada de 04/11 (A36 com e sem linhas: faltam 5, menor viável 28; classificação 2 × 1 no 28; inevitável 19 folgas seguidas; A11 admite 23, provado; B36 sem escala até 101; B11 admite 89 sem prova) | §15c (aprovada em 05/11) | 05/11/2026, **v1.4.5** (`src/` idêntico à tag `634eeb5`, conferido e gravado em cada JSON; rodadas no commit `ebaf663`, fechamento em `8c14ca5` e `17eb5cf`) | — (rodou na versão citável) | **evidência direta na v1.4.5**: esperado sem solver commitado antes (`b39dd13`); avaliador oficial nas 6 escalas (sem violação de dura; por critério com peso 1 no caso A), com o Java em UTC (horário de verão de 04/11/2018; saída idêntica nas instâncias de 2027 com e sem a opção); descanso no relógio; quebras das linhas recontadas fora da ferramenta | uma rodada por configuração; sem prova: etapa 2 do A36_livre_padrao e o B11 inteiro (dependem do tempo); 11 h é hipótese de sensibilidade; "enfermeiro em posto de técnico" conferido só pela cota à mão (≥ 15), sem avaliador externo |

## Para o texto, em uma frase por evidência

- §1 e regressão: refeitos na v1.4.4 (Tabela 6 e espelho do `avaliacao.py`).
- §14: rodou em 19/10 sobre a mesma semântica do INRC, que não mudou até a v1.4.4; a comparação com o
  avaliador oficial por tipo não foi refeita.
- §11: nenhuma restrição dura mudou para os casos da bateria (art. 67 conferido em 13/10, sem par
  novo); P01–P18 e a demonstração foram refeitos até a v1.4.2 com desfechos iguais, e a v1.4.4 recebe
  a mesma entrada; K1–K6, propriedades e nível 3 não foram refeitos depois de 07–09/10.
- §15.2: rodou na v1.4.4. **Histórico** desde 05/11: o caso A no texto vem da §15c.
- §15c (05/11): rodou na v1.4.5 com a entrada de 04/11 (janela real do Anexo B, férias reais); evidência direta, com o avaliador oficial nas escalas; a §15.1 e a §15.2 ficam como histórico.

## Elo v1.4.4 × v1.4.5 (30/10/2026, PENDENTE DE APROVAÇÃO)

Acrescentado em 30/10. A v1.4.5 está no branch `v1.4.5-minmax`, sem merge nem tag até o ok do
Otávio. A mudança é só da etapa 2, que passa da soma das amplitudes para o min-max (`DECISOES.md`,
"2026-10-30 — Etapa 2 por min-max (v1.4.5)"). Origem: `resultados/v145_2026-10-30/suite/resumo.txt`
(TUDO OK; 19 passos com código 0 na primeira rodada, 27 com o complemento de 30–31/10), com o worktree da v1.4.4 (`e91aa05`) em `../tcc-nrp-v144`.

- **Identidade da entrada do solver**, nos mesmos 81 casos: o XML e o LP da etapa 1 são idênticos
  byte a byte (162 de 162). Os 81 LPs da etapa 2 diferem **só** no objetivo, na variável
  `amplitude` e nas restrições `amplitude_constraints`, uma por categoria presente. A conferência é
  `docs/diagnostico/identidade_v145.py`, que lê o LP como conteúdo, porque o Pyomo reordena termos
  e limites quando aparece uma variável nova.
- **Controle da conferência** (`identidade_v145.py --controle`): quatro defeitos plantados numa
  cópia de um LP da etapa 2, os quatro pegos. Os defeitos foram um coeficiente de restrição antiga
  mudado, uma restrição de amplitude faltando, um limite de `f_max` mudado e um termo a mais no
  objetivo.
- **Regressão** (`src/regressao.py --todos`): passou, idêntica (56, 58, 197, 219 provados = Tabela
  6). Os testes das entradas também passaram, e os testes da ferramenta que passam pela etapa 2
  foram 9 (com 9c e 9d), 9c-tela, 8, 12, p20, pref-tela e opB-*.

**Nota:** os resultados que dependem da etapa 2 foram medidos na v1.4.4 (ou antes), com a soma.
Estão marcados no `NUMEROS_TCC.md` como *medido na v1.4.4 (etapa 2 pela soma)*. O XML e a etapa 1
não mudam, então as evidências que só dependem deles continuam ligadas pela identidade acima.
