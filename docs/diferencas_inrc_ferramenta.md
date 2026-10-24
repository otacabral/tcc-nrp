# Diferenças: Santos et al. (2016) × modelo INRC × ferramenta

Criado em 19/10/2026 (sessão de 19/10, item 7), para o comparativo pedido pelo orientador em
14/10. **Só documentação**: nada aqui muda o código nem número.

**A defesa já registrada.** A semântica das restrições é tomada integralmente de Santos et al.
(2016); muda só a codificação (atribuição `x[n,s,d]` em vez das janelas `w`/`r` e das tabelas
σ/τ); a equivalência está provada pelo avaliador oficial, que é independente do modelo — os
quatro ótimos da Tabela 6 reproduzidos e, desde 19/10, conferidos restrição por restrição e
profissional por profissional (`resultados/validacao_restricoes_2026-10-19/`).

**O que não se afirma.** Eficiência. Santos et al. provaram o ótimo do `medium_late05` (107) e
nós não (224, sem prova, 3.600 s; `NUMEROS_TCC.md`). Menos variáveis não é prova de resolver
mais rápido. O ganho defensável é **adaptabilidade**: regra nova = uma desigualdade sobre `x` e
`y`, sem recalcular custo de bloco (σ, τ, ψ).

**Fontes de cada coluna.** "Por quê": entrada do `DECISOES.md` com data e título; sem registro,
"motivo não registrado". "Tamanho": medido por `docs/diagnostico/tamanho_modelos.py`
(`resultados/tamanho_modelos_2026-10-19/tamanho.csv`) quando há número; senão, o efeito
qualitativo. A formulação de Santos foi lida pelo fichamento da Redação (`D:\TCC\escrita\fontes\
fichamentos\Camada 4 ...\santos.md`, SA16-019 a SA16-033, conferido na versão publicada em
13/10). *Conferido no artigo em 24/10 (chat de Orientação; antes aqui: "conferir no artigo antes
de citar números de Santos"):* Santos et al. (2016), Ann Oper Res 239:225–251, seções 3.1–3.2,
p. 228–230 — Π = todos os pares (d1, d2) com d1 ≤ d2; w e r indexadas por enfermeiro e janela
('O(n × d²) variables w and r'); y por fim de semana; z por par de fins de semana (i1 ≤ i2). A conta
x + y + w + r + z refeita só pela definição do artigo bate nas cinco linhas da tabela de tamanho
(`NUMEROS_TCC.md`, seção 15b, aprovada em 24/10). "Com a opção B": se a
diferença some, fica ou muda quando a função objetivo por níveis for implementada
(`DECISOES.md`, "2026-10-14 — Função objetivo por níveis escolhidos pelo gestor (opção B)").

---

## (a) Santos et al. (2016) × modelo INRC — semântica igual, codificação diferente

Motivo geral: `DECISOES.md`, "2026-09-08 — Formulação: atribuição, não janelas" (as janelas
servem ao objetivo do artigo, fortalecer o limite dual por planos de corte; este trabalho não
persegue desempenho algorítmico, e a atribuição adapta direto ao 12×36 e à categoria).

**Tamanho, pela definição** (só `x`, `y`, `w`, `r`, `z` de Santos; as folgas α dependem das
suaves ativas e não foram contadas, então a coluna de Santos é limite **inferior**):

| Instância | Nosso: variáveis | Nosso: restrições | Santos: x + y + w + r + z | dos quais w + r |
|---|---:|---:|---:|---:|
| sprint01 (10 enf., 4 turnos, 28 dias) | 2.978 | 2.450 | ≥ 9.380 | 8.120 |
| sprint02 | 2.992 | 2.464 | ≥ 9.380 | 8.120 |
| long01 (49 enf., 5 turnos) | 15.029 | 10.857 | ≥ 47.334 | 39.788 |
| long02 | 15.120 | 10.948 | ≥ 47.334 | 39.788 |
| medium_late05 (30 enf., 5 turnos) | 15.320 | 13.060 | ≥ 28.980 | 24.360 |

(28 dias → 406 janelas por enfermeiro: 28 × 29 / 2. Confere com a estimativa de 14/10.) As
restrições de Santos não foram contadas: dependem das suaves ativas e da enumeração de σ/τ.

| O que muda | Santos et al. (2016) | Modelo INRC (`modelo.construir`, padrões) | Por quê | Efeito no tamanho |
|---|---|---|---|---|
| Dias seguidos de trabalho e de folga (máx./mín.) | janelas `w[n,d1,d2]`, `r[n,d1,d2]` para todo par d1 ≤ d2, custo pré-calculado σ/τ por bloco; restrições (5)–(9) | `y[n,d]` + janela deslizante de L+1 dias (máximo) e um indicador por (início, tamanho de bloco curto) (mínimo) | "2026-09-08 — Formulação: atribuição, não janelas"; convenções de contagem em "2026-09-18 — Função objetivo: uma folga por violação, não por termo" | nosso: N × D de `y` + folgas por janela; Santos: 2 × N × D(D+1)/2 só de `w`/`r` |
| Fins de semana seguidos (máx./mín.) | `z[n,i1,i2]` por par de fins de semana, custo ψ; (18)–(20) | `wk` por fim de semana + janela deslizante / indicadores | idem, 08/09 | pequeno nos dois (4 fins de semana) |
| Turnos idênticos no fim de semana | folga α⁹ por par de dias e por turno, (14)–(15) | uma variável `u` por (fim de semana, turno), penalidade tam × u − dias com o turno | motivo não registrado (só a convenção geral de 18/09) | ordem de grandeza igual |
| Fim de semana completo | dentro de σ (blocos) | variáveis de início de bloco `cw` por dia do fim de semana | "2026-09-08 — Formulação" | pequeno |
| Padrões indesejados | (16) por padrão de turnos e (17) por padrão de dias, com dias virtuais negativos | uma folga por ocorrência; o padrão "livre no dia fixo e trabalha num dos seguintes" vale **uma** violação por semana (vários limites na mesma folga) | "2026-09-18 — Função objetivo: uma folga por violação" (no `long02` isto valia 16 pontos: 221 × 219) | uma folga por posição em que o padrão pode casar |
| Turno noturno antes de fim de semana livre | restrição (13), com α⁸ na função objetivo | **fora da função objetivo nas instâncias do INRC** (implementada, peso zero) | "2026-09-18 — Restrição não pontuada pelo avaliador fica fora da função objetivo" (o avaliador oficial não a pontua; ligada em 44 das 69 instâncias) | menos folgas |
| Folgas após noites | (12), com parâmetro γ⁶ de dias de descanso | número de folgas fixo em 2 (o elemento do XML é booleano) | "2026-09-15 — Escopo: implementar as 13 flexíveis" | nenhuma instância a exercita |
| Habilidade alternativa; pedidos de turno | coeficiente ν em `x` | coeficiente em `x` | "2026-09-18 — Habilidade é restrição flexível" (igual a Santos) | **igual** |
| Cobertura; um turno por dia | (1) igualdade; (2) | igualdade, também onde a demanda não é declarada; ≤ 1 | "2026-09-08 — Cobertura é restrição rígida de igualdade"; "2026-09-15 — Cobertura: igualdade também onde a demanda não é declarada" | **igual** |
| Planos de corte (clique, Window cuts) e heurística MPH | parte do método do artigo | não usados; só o HiGHS com as opções padrão | "2026-09-08 — Formulação" (o objeto é o modelo) | — |

---

## (b) Modelo INRC × ferramenta

**Tamanho, no caso da demonstração** (30 profissionais, 4 tipos de turno, 28 dias; cada linha
liga **só uma** diferença a partir do modelo nos padrões do INRC):

| Modelo | Variáveis | Restrições |
|---|---:|---:|
| caso da demonstração com `construir()` nos padrões do INRC | 20.970 | 18.592 |
| + só habilidade rígida | 11.810 | 10.552 |
| + só limites legais rígidos (`RIGIDAS_LEGAIS_BR`) | 4.200 | 18.592 |
| + só custo de enfermeiro em posto de técnico | 20.970 | 18.592 |
| **ferramenta** (`experimento_a.modelo_br`, todas juntas) | **3.080** | **10.552** |

Leitura: o limite legal rígido tira as folgas (a mesma expressão vira restrição, sem variável);
a habilidade rígida tira as atribuições de técnico a posto de enfermeiro e, com elas, as
restrições de padrão que as envolvem. O custo de enfermeiro em posto de técnico é só
coeficiente: não muda o tamanho.

| O que muda | Por quê (DECISOES.md) | Efeito no tamanho | Com a opção B |
|---|---|---|---|
| Teto de atribuições, dias seguidos e padrões indesejados (interjornada 11 h, 36 h após 12 h, folga isolada ≥ 24 h) passam de penalizados a **rígidos** | "2026-09-21 — Definição de viável, e limites legais como rígidos" (motivo atual: a ferramenta promete escala legal); "2026-10-13 — Art. 67 com horários editáveis" | −16.770 variáveis (folgas) no caso da demonstração; restrições iguais | **fica** (a CLT continua dura). **Muda** se uma dessas três famílias for oferecida também como preferência: `rigidas_legais` endurece a família inteira, então a versão suave precisaria de família própria |
| Habilidade **rígida**: técnico nunca em posto de enfermeiro (o enfermeiro tem as duas habilidades e cobre os dois postos) | "2026-09-18 — Habilidade é restrição flexível, não restrição de domínio" (versão rígida reservada à instância brasileira) | −9.160 variáveis e −8.040 restrições no caso da demonstração | **fica** |
| **Enfermeiro em posto de técnico** custa 1 por turno (família `custo_atribuicao`, ausente no INRC) | "2026-09-29 — Redesenho da ferramenta" (item Objetivo) | nenhum (coeficiente) | **muda**: vira critério classificável (padrão: Importante) |
| **Pesos** da função objetivo: pedido de folga custa W = (postos de técnico do horizonte) + 1, em vez do peso do XML | "2026-09-29 — Redesenho da ferramenta" (item Objetivo) | nenhum | **some**: substituído pela classificação por níveis (o padrão reproduz a ordem atual) |
| Suaves do INRC **desligadas** no contrato da ferramenta (fins de semana, mínimo de dias seguidos, folgas seguidas, turnos idênticos etc.) | **motivo não registrado** (é a pergunta do orientador em 14/10) | menos folgas | **muda**: passam a ser critérios classificáveis; "Não considerar" reproduz o atual |
| Noturno antes de fim de semana livre **ligável** (`noite_antes_de_fds_livre=True`), mas desligado no contrato | "2026-09-18 — Restrição não pontuada pelo avaliador..." (volta a valer na instância brasileira) | nenhum hoje | **muda**: critério classificável; sem conferência externa possível (o avaliador não a pontua) |
| **Teto de horas** por profissional (carga contratual nos dias disponíveis), rígido | "2026-10-02 — Carga por contrato" | + N restrições | **fica** |
| **Férias e licenças** rígidas (variáveis fixadas em zero) | "2026-09-29 — Especificação da ferramenta" / "Redesenho" | variáveis fixadas | **fica** |
| **Turnos configuráveis** (início e duração), demanda por turno e categoria, posto de enfermeiro como tipo de turno próprio | "2026-09-08 — Desagregação por categoria: via tipo de turno"; "2026-09-29 — Redesenho da ferramenta" | depende do número de turnos | **fica** |
| **Etapa 2**: segunda resolução que fixa o valor da etapa 1 (= ou ≤) e minimiza a amplitude da fração do contrato cumprida dentro de cada categoria | "2026-10-02 — Carga por contrato" (itens g–i); P14 e P17 (09 e 10/10) | + 2 variáveis e 2N restrições por categoria na etapa 2 | **fica**, como último passo fixo |
| Limite de tempo por resolução (600 s / 180 s), orçamento por clique, escala sem prova entregue com o gap | "2026-10-08 — P12 aprovada"; "2026-10-09 — P14"; "2026-10-09 — P17" | — | **muda**: orçamento vira parâmetro, padrão 60 min ("2026-10-19 — Orçamento por clique configurável") |
| Conferência de descanso **no relógio**, fora do modelo; escala reprovada não é entregue | "2026-10-13 — Art. 67 com horários editáveis" | — (fora do modelo) | **fica** |
| COFEN como **alerta**, fora do modelo | "2026-09-29 — Redesenho da ferramenta" | — | **fica** |
