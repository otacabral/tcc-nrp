# Relatório da sessão de 19/10/2026

Pedido da Orientação de 19/10 (itens 1 a 9). Nenhuma mudança de código de produto: `src/` não
foi alterado. Scripts novos só em `docs/diagnostico/` (leitura e contas, sem solver).

| Item | Situação |
|---|---|
| 1. Cronograma | feito: `DECISOES.md` ("2026-10-19 — Cronograma"), `CLAUDE.md`, `ESTADO_ATUAL.md`, `LEIA_PRIMEIRO.md`, `PASSAGEM.md` |
| 2. Opção B no DECISOES | feito: "2026-10-14 — Função objetivo por níveis escolhidos pelo gestor (opção B)", marcada MUDANÇA DE FORMULAÇÃO, implementação pendente |
| 3. Diagnóstico para a implementação | feito, abaixo. **Parado aí**: nada da opção B implementado |
| 4. Validação por restrição | feito: **tudo OK**, com controle positivo; seção proposta para o `NUMEROS_TCC.md` abaixo (não incluída) |
| 5. Limitações declaradas | feito: "2026-10-19 — Limitações declaradas: domingo no art. 67 e escala do art. 386", com a lista do que falta |
| 6. Orçamento configurável | registrado: "2026-10-19 — Orçamento por clique configurável, padrão 60 min" (implementação junto com a B) |
| 7. Diferenças INRC × ferramenta | feito: `docs/diferencas_inrc_ferramenta.md` |
| 8. Documentação para a Redação | feito: `docs/pesos_inrc.md`; contagem de variáveis (seção 8); especificação dos testes (seção 8) |
| 9. Ao final | este relatório; `PASSAGEM.md`; tag `v1.2.3` está no GitHub (seção 9) |

---

## 3. Diagnóstico para a implementação da opção B (só leitura)

### 3a. Como a etapa 1 combina hoje "pedidos" e "enfermeiro em posto de técnico"

**Pesos escalonados, numa resolução só.** `src/ferramenta.py`, função `pesos(inst)`:

- cada turno de enfermeiro em posto de técnico custa **1** (família `custo_atribuicao` do
  modelo, `src/modelo.py`, bloco "custo por atribuicao" de `_adicionar_flexiveis`);
- cada pedido de folga não atendido custa **W = (total de postos de técnico do horizonte) + 1**
  (o peso do pedido é trocado por W; entra na família `day_off_requests`). No caso da
  demonstração (rodada 1), **W = 286**.

Como W passa o máximo que a segunda parcela pode somar, negar um pedido nunca compensa. É uma
ordem lexicográfica de dois níveis feita por coeficientes. A chamada: `resolver_com_objetivo` →
`pesos` → `experimento_a.modelo_br(inst, custo)` → `modelo.construir(..., habilidade_rigida=True,
noite_antes_de_fds_livre=True, rigidas_legais=RIGIDAS_LEGAIS_BR, custo_atribuicao=custo)`. O
objetivo é `sum(m.parcela[f])` (`modelo.py`, fim de `_adicionar_flexiveis`). No contrato da
ferramenta (`instancia_br._contrato`) nenhuma outra flexível gera termo: as três legais são
rígidas, as demais estão desligadas ou com valor 1 (mínimos de dias/folgas seguidos = 1, que não
penalizam nada).

**A etapa 2 já é resolução em sequência.** `ferramenta.preparar_equilibrio`: desativa o objetivo
da etapa 1, prende-o como restrição (`m.total_no_otimo`: `== z` com prova, `<= z` sem prova,
P14) e minimiza a amplitude da fração do contrato. **Os dois mecanismos que a opção B pode usar
já existem no código**: coeficientes escalonados (etapa 1) e níveis em sequência com o valor
anterior preso (etapa 1 → etapa 2).

### 3b. Opções de gap do HiGHS

**Nenhuma é alterada pela ferramenta nem pelo modelo** (busca por `mip_rel_gap`, `mip_abs_gap`,
`mip_gap` em `src/` e `docs/`: zero ocorrências). Valem os padrões do HiGHS 1.15.1 (lidos do
`highspy` instalado em 19/10): `mip_rel_gap` = **1e-4** (0,01%), `mip_abs_gap` = **1e-6**;
`mip_feasibility_tolerance` = 1e-6; `primal_feasibility_tolerance` = 1e-7. A única opção
passada é o limite de tempo (`modelo.resolver`) e, nos experimentos, `log_file`.

Consequência já registrada ("2026-10-09 — Condição das afirmações de ótimo provado"): com
objetivo inteiro, "ótimo" do HiGHS vale como ótimo inteiro quando 0,0001 × objetivo < 1, isto é,
**objetivo < 10.000**. Hoje, no caso da demonstração, o objetivo máximo possível é 6 × 286 + 285
= 2.001: a condição vale. Ver 3d para o que acontece com pesos escalonados em 3 ou 4 níveis.

### 3c. Os 13 critérios flexíveis: nome, parâmetro, uso no INRC, exposição na ferramenta

Numeração de Santos et al. (2016) e do `DECISOES.md` ("2026-09-18 — Restrição não pontuada…",
contagem das 13). "INRC" = instâncias, das 69, em que a família está ativa em pelo menos um
contrato (`resultados/censo_flexiveis_2026-10-19/censo.md`). Exposição: **existe** (já está na
tela), **adaptar** (a família existe no modelo; falta parâmetro na tela e ligar no contrato),
**novo** (exige mudança no modelo ou entrada nova).

**Pedidos e qualificação**

| # | XML | Nome proposto | Parâmetro | INRC | Ferramenta |
|---|---|---|---|---:|---|
| 12 | DayOffRequest / DayOnRequest | Pedido de folga no dia / Pedido para trabalhar no dia | profissional e data | 49 / 0 | folga: **existe** (pedidos da tela, peso W); trabalhar: **novo** na tela (a família `day_on_requests` existe; sem conferência externa, nenhuma instância a traz) |
| 13 | ShiftOffRequest / ShiftOnRequest | Pedido de folga num turno / para trabalhar num turno | profissional, data e turno | 49 / 0 | **novo** na tela; decidido como trabalho futuro em "2026-10-09 — Pedido por turno vira trabalho futuro" — se entrar na B, essa decisão muda |
| 10 | AlternativeSkillCategory | Profissional fora da sua habilidade | — | 18 | na ferramenta a habilidade é **rígida** (técnico nunca em posto de enfermeiro). A versão do INRC seria permitir isso com penalidade: contradiz uma regra rígida; **para a Orientação decidir** se entra. O análogo permitido, enfermeiro em posto de técnico, **existe** (`custo_atribuicao`, não é do INRC) |

**Sequências de trabalho e folga**

| # | XML | Nome proposto | Parâmetro | INRC | Ferramenta |
|---|---|---|---|---:|---|
| 2 | Max/MinConsecutiveWorkingDays | Máximo / mínimo de dias seguidos de trabalho | v (dias) | 69 / 69 | máximo: **rígido** (6, art. 67). Uma preferência mais apertada é **novo**: `rigidas_legais` endurece a família inteira, e o contrato tem um só valor por família — a versão suave precisa de família própria. Mínimo: **adaptar** (no contrato com v = 1, sem efeito) |
| 3 | Max/MinConsecutiveFreeDays | Máximo / mínimo de folgas seguidas | v (dias) | 69 / 69 | **adaptar** (máximo desligado; mínimo v = 1) |
| 11 | UnwantedPatterns | Sequência indesejada | o padrão (turnos/dias) | 57 | a família carrega as regras de descanso da CLT, rígidas. Padrão do gestor como preferência é **novo**: família própria (mesmo motivo do item 2) e entrada nova na tela para definir o padrão |

**Fins de semana**

| # | XML | Nome proposto | Parâmetro | INRC | Ferramenta |
|---|---|---|---|---:|---|
| 4 | Max/MinConsecutiveWorkingWeekends | Máximo / mínimo de fins de semana seguidos trabalhados | v | 49 / 41 | **adaptar** (desligadas no contrato; a definição de fim de semana já está na tela) |
| 5 | MaxWorkingWeekendsInFourWeeks | Máximo de fins de semana trabalhados em 4 semanas | v | 0 | **adaptar**; sem conferência externa possível (o avaliador não tem condição para ela; nenhuma instância a liga) |
| 6 | CompleteWeekends | Fim de semana completo (trabalha os dois dias ou nenhum) | — | 69 | **adaptar**. No 12×36, sábado e domingo seguidos são proibidos pelas 36 h: quem trabalha no fim de semana sempre viola (`RETORNO_ORMEU_14-10.md`, item 2) |
| 7 | IdenticalShiftTypesDuringWeekend | Mesmo turno nos dias do fim de semana | — | 69 | **adaptar**. Pela fórmula do modelo (`tam × u − dias com o turno`), no 12×36 quem trabalha um só dia do fim de semana também viola (lido do código, não rodado) |

**Noturno e carga**

| # | XML | Nome proposto | Parâmetro | INRC | Ferramenta |
|---|---|---|---|---:|---|
| 1 | Max/MinNumAssignments | Máximo / mínimo de turnos no período | v (turnos) | 69 / 69 | máximo: **rígido** (teto legal; com turnos de durações diferentes o teto que vale é o de horas, `carga_horaria`). Preferência mais apertada: **novo** (família própria). Mínimo: **adaptar** (desligado); conversa com a etapa 2 (equilíbrio pela fração do contrato) |
| 8 | NoNightShiftBeforeFreeWeekend | Noturno na véspera de fim de semana livre | — | 44 | **adaptar** (o modelo da ferramenta já a liga, `noite_antes_de_fds_livre=True`; falta ligar no contrato). Sem conferência externa: o avaliador não a pontua |
| 9 | TwoFreeDaysAfterNightShifts | Duas folgas depois de noites | — (fixo em 2) | 0 | **adaptar**; sem conferência externa possível (elemento ausente nas 69) |

### 3d. Limite superior de violações por instância (tamanho dos coeficientes)

Unidades de excesso, peso 1 (como a opção B conta), somadas sobre os profissionais. Limites
**válidos, não justos** (servem para dimensionar). Fórmulas e valor por instância:
`resultados/censo_flexiveis_2026-10-19/censo.csv` (69 instâncias × 19 famílias). D = dias,
F = fins de semana, v = parâmetro.

| Família | Limite por profissional | Maior nas 69 (instância) | Caso da demonstração¹ |
|---|---|---:|---:|
| máximo de turnos | D − v | 862 (long_early04) | 240 |
| mínimo de turnos | v | 400 (long_hint01) | 300 |
| máximo de dias seguidos | D − v | 1.197 (long_hint02) | 690 |
| mínimo de dias seguidos | (v − 1) × ⌈D/2⌉ | 1.302 (long_late05) | 840 |
| máximo de folgas seguidas | D − v | 1.180 (long_hint01) | 720 |
| mínimo de folgas seguidas | (v − 1) × ⌈D/2⌉ | 1.330 (medium_hidden01) | 840 |
| máximo de fins de semana seguidos | F − v | 115 (long_hidden05) | 30 |
| mínimo de fins de semana seguidos | (v − 1) × ⌈F/2⌉ | 60 (long_hint01) | 60 |
| fins de semana em 4 semanas | (F − 3) × (4 − v) | 0 (desligada nas 69) | 0 |
| fim de semana completo | pior padrão por fim de semana (enumerado) | 560 (long_hidden03) | 120 |
| mesmo turno no fim de semana | pior combinação por fim de semana (enumerada) | 880 (long_hidden03) | 240 |
| noturno antes de fim de semana livre | F | 200 (long_hidden01) | 120 |
| duas folgas após noites | 2 × D (frouxo) | 0 (ausente nas 69) | 0 |
| habilidade alternativa | D (quem não tem todas) | 1.344 (long_hidden01) | 560 |
| sequências indesejadas | posições em que o padrão casa | 10.950 (long_hidden01) | — |
| pedidos de folga (dia / turno) | nº de pedidos | 490 / 310 | 6 (dia) |
| enfermeiro em posto de técnico | postos de técnico do horizonte | — (não é do INRC) | 285 |

¹ Caso da demonstração (30 profissionais, 28 dias, 4 fins de semana), com as suaves do INRC
ligadas **com os parâmetros do contrato 0 do `medium_late05`**, só para dar ordem de grandeza —
inclui famílias que na ferramenta são rígidas (máximos) ou impossíveis (habilidade). Soma das
suaves do INRC: **4.760**.

**O que isso diz sobre pesos escalonados** (conta, não decisão). Três níveis no caso da
demonstração — Essencial = pedidos (≤ 6), Importante = enfermeiro em posto de técnico (≤ 285),
Desejável = todas as suaves do INRC (≤ 4.760):

- coeficientes: Desejável 1; Importante 4.761; Essencial 4.760 + 4.761 × 285 + 1 = **1.361.646**;
- objetivo máximo ≈ 6 × 1.361.646 + 285 × 4.761 + 4.760 ≈ **9,5 milhões**;
- com o `mip_rel_gap` padrão (1e-4), o HiGHS declara ótimo com folga absoluta de até 0,0001 ×
  objetivo: com **um** pedido negado (objetivo ≈ 1,36 milhão) são ~136 unidades — mais que uma
  violação do nível Desejável. A ordem entre níveis continua garantida pelos coeficientes, mas
  **o ótimo dentro dos níveis de baixo deixa de ser provado**. A condição de 09/10 (objetivo <
  10.000) falha. Pesos escalonados com 3 ou 4 níveis exigiriam fixar `mip_rel_gap` = 0 (e
  `mip_abs_gap` < 1), com custo de tempo não medido; e a razão de ~10⁶ entre coeficientes
  encosta nas tolerâncias de viabilidade (1e-6/1e-7). **Não testado; é conta.**
- em sequência (um nível por resolução, o anterior preso como restrição, como a etapa 2 já
  faz), cada objetivo é o de um nível só: no caso acima, ≤ 4.760 < 10.000, e a condição de
  09/10 vale com o gap padrão. Custo: uma resolução por nível não vazio, todas dentro do mesmo
  orçamento (3e).
- **Conferência que compartilha premissa:** os limites saem das mesmas fórmulas de contagem que
  o modelo usa (excesso por janela/bloco). Servem para dimensionar coeficientes, não para
  validar nada.

### 3e. Orçamento de 20 min por clique (P12)

**Onde mora.** `src/ferramenta.py`, constante de módulo `ORCAMENTO = 20 * 60`, lida na chamada
por `verificar(..., orcamento=None)` (os testes a encurtam: teste 12d, `fe.ORCAMENTO = 3`). A
tela (`src/app.py`) chama `fe.verificar(entrada, progresso=..., aviso=...)` sem passar
`orcamento`. Os outros limites: `TEMPO = 600` (etapa 1, por resolução) e `TEMPO_ETAPA2 = 180`.

**Como se reparte: não há cota por fase.** É um prazo único (`prazo = time.time() + orcamento`)
consumido em sequência:

1. conta (piso aritmético, alertas do COFEN) — sem solver;
2. quadro informado: etapa 1 com `min(600 s, o que resta)`;
3. se o quadro tem escala: etapa 2 com `min(180 s, limite da etapa 1, o que resta)`
   (`resolver_com_objetivo`); a busca termina;
4. se não tem: busca do menor quadro — para cada quadro acima, uma ou duas composições
   (a da regra e "acréscimos como enfermeiros"), cada uma com etapa 1 de `min(600 s, o que
   resta)`; no primeiro viável, a etapa 2 como em 3;
5. resta < 1 s → para (`ORCAMENTO_ESGOTADO`), mostra só o que foi provado.

**O que precisa mudar para virar parâmetro (item 6):**

- `app.py`: um campo (minutos, padrão 60) e `orcamento=campo × 60` na chamada de `verificar`.
  `verificar` já recebe o parâmetro; nada muda no motor;
- `ORCAMENTO` passa a 60 × 60 (ou fica 20 × 60 e só a tela muda o padrão — decidir);
- textos: o sufixo da barra ("orçamento do clique: …") e a frase "o menor quadro viável não foi
  determinado em …" já usam o valor da chamada (`fmt_tempo(orcamento)`); o `GUIA_DE_USO.md`
  diz "20 min" literalmente em três lugares (linhas 155, 173, 188);
- **com o teste obrigatório da opção B** ("classificação padrão → textos idênticos aos da
  v1.2.3"): se o padrão do orçamento for 60 min, esses textos mudam de propósito. O teste de
  identidade tem de rodar com o orçamento em 20 min, ou o esperado registra a troca antes;
- **atenção:** com 60 min de orçamento, cada resolução continua limitada a 600 s (etapa 1) e
  180 s (etapa 2). O orçamento maior serve à busca do menor quadro e às resoluções em sequência
  da opção B, **não dá mais tempo a uma resolução difícil**. A P17 mostrou que o caso K5 só
  melhorou a etapa 2 aos ~29 min (`NUMEROS_TCC.md`, seção 13). Se a intenção do orientador for
  dar mais tempo a uma resolução, `TEMPO`/`TEMPO_ETAPA2` também precisam de decisão.

---

## 4. Validação por restrição nos 4 ótimos

Esperado commitado antes (`8d20313`; adendo do controle, `d44daef`):
`resultados/validacao_restricoes_2026-10-19/ESPERADO.md`. Resultado: `tabela.md`,
`por_tipo.csv`, `por_profissional.csv` (mesma pasta). Comando:
`python docs\diagnostico\validacao_restricoes.py` (sem solver).

| Instância | Tabela 6 | Avaliador | Soma por tipo, avaliador | Soma por tipo, modelo | Duras (avaliador / XML / `conferir_rigidas` / modelo) | Tipos com diferença | Profissionais com diferença |
|---|---:|---:|---:|---:|---|---:|---:|
| sprint01 | 56 | 56 | 56 | 56 | 0 / 0 / 0 / 0 | 0 | 0 de 10 |
| sprint02 | 58 | 58 | 58 | 58 | 0 / 0 / 0 / 0 | 0 | 0 de 10 |
| long01 | 197 | 197 | 197 | 197 | 0 / 0 / 0 / 0 | 0 | 0 de 49 |
| long02 | 219 | 219 | 219 | 219 | 0 / 0 / 0 / 0 | 0 | 0 de 49 |

Igual ao esperado em todas as linhas, inclusive profissional × tipo (0 células com diferença).
A grade impressa pelo avaliador é, célula a célula, a escala do XML nas quatro.

**O que cada coluna é (dito antes de rodar):**
- **Avaliador**: o avaliador oficial (Java), das saídas salvas. É a única coluna independente.
- **Modelo**: as expressões do próprio modelo (`m.parcela`, `m.pena_familia`), com x fixado na
  escala. **É o mesmo código que gera o valor da função objetivo.** A coluna mostra que o
  modelo atribui a cada tipo e a cada profissional exatamente o que o avaliador cobra; não é
  conferência independente do modelo.
- `avaliacao.py`: terceira coluna, também 0 de diferença. **Compartilha premissa com o modelo**
  (o modelo lineariza o `avaliacao.py`): não confere o modelo.
- O mapa rótulo do avaliador → família do modelo é premissa do script, escrito à mão; rótulo
  sem mapa faz o script falhar.

**Controle positivo** (resultado idêntico pede controle). `python
docs\diagnostico\validacao_restricoes_controle.py`, semente 20261019: 5 escalas perturbadas por
instância (8 trocas que preservam cobertura e um-turno-por-dia), 20 no total.
- (c1) comparadas com a saída do avaliador da escala **original**, a conferência acusou
  diferença nas 20 (grade ≠ XML; 4 a 9 tipos com diferença);
- (c2) reavaliadas pelo avaliador oficial (java, nesta sessão): duras 0 nas 20; penalidade de
  69 a 250, sempre ≥ Tabela 6; **avaliador = modelo** em todos os tipos e em todas as células
  profissional × tipo. As perturbadas exercitam 11 tipos de violação (as ótimas, 6), entre
  eles fim de semana completo (58 ocorrências), mesmo turno no fim de semana (74), pedido de
  folga no turno (13) e mínimo de turnos (1).
- **Achado do controle:** o primeiro mapa de rótulos não tinha "Incomplete working weekends" e
  "Identical shifttypes during weekend" (grafia do avaliador, que não aparecem nas quatro
  escalas ótimas). O script parou com "rótulo sem mapa", como devia; os dois foram acrescentados
  e as duas rodadas refeitas. A rodada principal deu o mesmo antes e depois.

Fica fora: o `medium_late05` (não reproduz o ótimo; 224 já conferido no avaliador em 06/10) e
as famílias que nenhuma das 4 instâncias liga (noturno antes de fim de semana livre, fins de
semana seguidos, habilidade alternativa).

**Seção proposta para o `NUMEROS_TCC.md` (NÃO incluída; aguarda aprovação):**

> ### 14. Validação por restrição nos 4 ótimos (19/10/2026)
>
> | Número | O que é | Arquivo | Comando | Conferência | Ressalva |
> |---|---|---|---|---|---|
> | duras = **0** nas 4 escalas ótimas (56, 58, 197, 219) | cobertura pelo avaliador oficial; um turno por dia contado no XML; `conferir_rigidas`; restrições do modelo com x fixado | `resultados/validacao_restricoes_2026-10-19/tabela.md` | `python docs\diagnostico\validacao_restricoes.py` | avaliador oficial (saídas de `resultados/<inst>_completo_avaliador.txt`) | o avaliador só checa cobertura; um-turno-por-dia vem da contagem no XML |
> | penalidade por tipo, avaliador × modelo: diferença **0** em todos os tipos; somas **56, 58, 197, 219** | 6 tipos com custo nas 4 escalas (máximo de turnos, dias seguidos, mínimos de dias e de folgas seguidos, pedido de folga, padrão indesejado) | idem, `por_tipo.csv` | idem | avaliador oficial | a coluna "modelo" é o próprio código da função objetivo, com x fixado; a independência está no avaliador |
> | diferença **0** por profissional (10, 10, 49, 49) e por profissional × tipo | | `por_profissional.csv` | idem | avaliador oficial | idem |
> | controle: 20 escalas perturbadas (penalidade 69–250), avaliador = modelo em todos os tipos e células; a conferência acusa as 20 contra a saída da original | | `controle/controle.md` | `python docs\diagnostico\validacao_restricoes_controle.py` | avaliador oficial, rodado em 19/10 | perturbações aleatórias, semente 20261019; 11 tipos de violação exercitados |
>
> Substitui, como evidência de restrições, as 207 + 36 escalas de 18/09 (perdidas; seção 1).

---

## 5. Limitações declaradas

Registradas no `DECISOES.md`, "2026-10-19 — Limitações declaradas: domingo no art. 67 e escala
do art. 386", com o contorno pelo pedido de folga e a dependência da classificação na opção B.
**Falta (listado lá, não inventado):** se vão como trabalho futuro; a frequência de domingos
livres que valeria para o art. 67 (não pesquisada); se a jurisprudência do art. 386 entra (o
fichamento proíbe citar o RE 1.403.904 sem o acórdão lido).

## 6. Orçamento configurável

Registrado (`DECISOES.md`, "2026-10-19 — Orçamento por clique configurável, padrão 60 min").
Não implementado: vai junto com a opção B. Pontos técnicos em 3e.

## 7. Diferenças INRC × ferramenta

`docs/diferencas_inrc_ferramenta.md`: (a) Santos × modelo INRC, 10 linhas, com tamanho pela
definição; (b) modelo INRC × ferramenta, 13 linhas, com o efeito de cada opção medido no caso
da demonstração (de 20.970 variáveis e 18.592 restrições nos padrões do INRC para 3.080 e
10.552 na ferramenta; quem mais reduz são os limites legais rígidos, que tiram as folgas).
Uma linha sem motivo registrado no `DECISOES.md`: **por que as suaves do INRC estão desligadas
no contrato da ferramenta** — é a pergunta do orientador em 14/10. Duas com motivo só parcial
(turnos idênticos no fim de semana e a escolha das quatro instâncias *early* como alvos).

## 8. Documentação para a Redação

**`docs/pesos_inrc.md`**: censo dos pesos nas 69 instâncias. 41 usam só peso 1 (todas as
*early*, inclusive as 4 de validação); 28 usam pesos de 1 a 10; o `medium_late05` tem também
um **31** (contrato 3, mínimo de folgas seguidas = 10; conferido no XML cru).

**Contagem de variáveis e restrições** (`python docs\diagnostico\tamanho_modelos.py`,
`resultados/tamanho_modelos_2026-10-19/tamanho.csv`): tabela em
`docs/diferencas_inrc_ferramenta.md`, parte (a). A de Santos é pela definição das variáveis
(x, y, w, r, z), lida no fichamento da Redação, sem as folgas α: **limite inferior**, a
conferir no artigo (sem leitor de PDF nesta máquina; o fichamento foi conferido na versão
publicada em 13/10). Confirma a estimativa de 406 janelas de trabalho e 406 de folga por
enfermeiro em 28 dias. O nosso `medium_late05` dá 15.320 variáveis e 13.060 restrições, igual
ao `NUMEROS_TCC.md`. **Sem afirmar eficiência.**

**Especificação dos testes.**

*Hardware:* Intel Core i5-10210U (4 núcleos, 8 threads), 12 GB, Windows 11 Home Single
Language 10.0.26200 (`NUMEROS_TCC.md`, linha 22, e o ambiente desta sessão).

*Software, versões lidas em 19/10:* Python 3.11.9; Pyomo 6.10.1; highspy (HiGHS) 1.15.1 via
`appsi_highs`; Streamlit 1.64.0; pandas 3.0.6; openpyxl 3.1.5; lxml 6.1.3; Java OpenJDK 25.0.4.1
(Temurin) para o avaliador oficial (`evaluator.jar` de 2014, com dom4j 1.6.1, jaxen 1.2.0,
jaxb-api 2.3.1). **Registrado na época** só Python 3.11.9 e HiGHS 1.15.1 (`NUMEROS_TCC.md`);
as versões de Pyomo, Streamlit, pandas e Java nas rodadas de 02 a 13/10 **não foram
registradas** — as de hoje valem para hoje.

*Critério de escolha de cada teste:*

| Teste | Critério | Onde está registrado |
|---|---|---|
| Regressão: 4 ótimos (56, 58, 197, 219) | instâncias com ótimo **provado** na Tabela 6 de Santos et al.; reproduzir o ótimo e o avaliador | escolha das quatro *early*: **não registrada** no `DECISOES.md` ativo; a limitação (só exercitam 8 das 13) está em "2026-09-15 — Quinto alvo" |
| `medium_late05` | cobertura: exercita todas as flexíveis ligadas em alguma instância, duas habilidades, pesos de 1 a 10, ótimo provado (gap 0) | "2026-09-15 — Quinto alvo de validação" |
| Validação por restrição (19/10) | as 4 escalas ótimas + 20 perturbadas (controle; semente fixa) | `ESPERADO.md` de 19/10 |
| `testes_entrada.py` | cada entrada da ferramenta contra um valor conhecido: QP do Experimento A, razão 20/29 do `long01`, os números de `experimento_a.csv` | docstring de `src/testes_entrada.py` |
| Tela, casos 1–5 | 1: célula v1 do Experimento A (resultado conhecido); 2: piso de alternância (um abaixo); 3: modelo 6 h + 12 h; 4: alerta de composição; 5: enfermeiro em posto de técnico com conta aritmética | docstring de `src/testes_ferramenta.py` |
| Tela, 8a–8d | os três desfechos do tempo; limites (25 s, 3 s) escolhidos por **sondagem no log do HiGHS em 02/10** — dependem da máquina | idem |
| Tela, 12, 15, 16 | um por decisão: P12 (progresso, erro, orçamento), P15 (alerta de 35 h, caso montado à mão), art. 67 (escala montada que reprova) | idem; relatórios 08b, 09b, 13a |
| Bateria (níveis 1–3, propriedades) | cobrir as áreas editáveis da tela levantadas de `app.py`, mais monotonia e ordem; testa **correção**, não representatividade | `docs/bateria_entradas.md`; `bateria_desenho.py` |
| Demonstração (10 enf. + 20 téc., 12×36, nov./2026) | proporção 33/67 do Parecer no grau intermediário; cortes 20/19/18 técnicos previstos pela conta antes de rodar | `docs/demonstracao/caso_clinica_medica.py`; `cortes_esperados.md`; decisão do Otávio de 05/10 |
| Escalabilidade (P1) | tamanhos 36 a 200; depois, com folga de equipe | `PROPOSTAS.md`, P1 |

---

## 9. Ao final

- **Tag `v1.2.3` no GitHub: sim.** `git ls-remote --tags origin v1.2.3` →
  `b6289dd…`, o mesmo objeto da tag local (aponta para o commit `7006624`). O `main` do GitHub
  está em `6a6cda7` (início desta sessão); os commits de hoje **não foram enviados** — o push é
  do Otávio.
- `PASSAGEM.md` atualizado; próxima tarefa = implementação da opção B, depois da decisão da
  Orientação sobre 3d (pesos escalonados × sequência) e 3e (orçamento × limites por resolução).
- Commits da sessão: `8d20313` (decisões + esperado), `d44daef` (esperado do controle),
  `341298a` (validação), `4bfac9c` e o seguinte (censo e tamanhos), e o do fechamento.
