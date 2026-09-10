# Diário de decisões — TCC NRP

Registro datado de decisões de modelagem e implementação. Matéria-prima dos capítulos de
formulação e de experimentos.

**Regra:** toda decisão não óbvia entra aqui no momento em que é tomada, com data, o que
foi decidido e por quê. Três linhas bastam. Perguntas abertas ficam na seção final até
serem resolvidas — e então viram entrada datada.

---

## 2026-09-08 — Formulação: atribuição, não janelas

Adotada codificação por atribuição (`x[n,s,d]`) com restrições explícitas de janela
deslizante para dias consecutivos.

Não adotadas as variáveis `w[n,d1,d2]` / `r[n,d1,d2]` nem as tabelas σ/τ de Santos et al.
(2016). Aquelas construções servem ao objetivo do artigo original — fortalecer o limite
dual por planos de corte. Este trabalho não persegue desempenho algorítmico, e a
codificação por atribuição permite adaptação direta ao 12×36 e à desagregação por
categoria profissional.

Semântica das restrições (2 rígidas, 13 flexíveis) tomada integralmente de Santos et al.

---

## 2026-09-08 — Cobertura é restrição rígida de igualdade

O elemento `<Preferred>` do XML **não** é preferência: é a demanda obrigatória.

Fonte: Haspeslagh, De Causmaecker, Stølevik e Schaerf, *First International Nurse
Rostering Competition 2010*, anais do PATAT 2010, p. 499–500. O texto declara a demanda
como restrição rígida e lista apenas duas restrições rígidas — cobrir toda a demanda e no
máximo um turno por enfermeira por dia.

Santos et al. (2016) modelam como igualdade (restrição 1). Consistente.

---

## 2026-09-08 — Atributo `on=` deve ser respeitado pelo parser

Cada restrição flexível traz `on="0"` ou `on="1"` indicando se está ativa na instância.
Restrição com `on="0"` não deve entrar no modelo.

Verificado em `sprint01`: os quatro contratos desligam `MaxConsecutiveWorkingWeekends`,
`MinConsecutiveWorkingWeekends` e `MaxWorkingWeekendsInFourWeeks`.

Ignorar isso faz o valor objetivo divergir do avaliador oficial — e o sintoma parece bug
de modelo, não de leitura.

Nota adicional: o formato já prever ativação por restrição é argumento a favor do
experimento de variantes — ligar e desligar regra é mecanismo nativo do benchmark.

---

## 2026-09-08 — Cobertura vem por dia da semana

`CoverRequirements` traz `DayOfWeekCover` (7 blocos, um por dia da semana), não por data.
O parser expande para os dias do horizonte.

Nas instâncias inspecionadas existe apenas `<Preferred>`; não há `<Minimum>` nem
`<Maximum>`.

---

## 2026-09-08 — Desagregação por categoria: via tipo de turno

O elemento `<Cover>` aceita apenas `<Shift>` e `<Preferred>` — não aceita `<Skill>`.
A habilidade está pregada no **tipo de turno**.

Em `long01`: o turno `DH` tem horário idêntico ao `D` (08:30–16:30) mas exige `HeadNurse`,
e a cobertura pede 2 de `DH` nos dias úteis. Isso expressa composição de equipe.

Consequência para a instância brasileira: a desagregação enfermeiro/técnico se faz criando
um tipo de turno por par horário×categoria, dentro do esquema oficial. **Não** exige
extensão do formato — o avaliador continua aplicável.

Ressalva a registrar no texto: a cobertura resulta em contagem fixa por categoria, não em
"ao menos 1 das N de um pool comum".

Nota: apenas 6 dos 49 profissionais de `long01` têm a habilidade `HeadNurse`.

---

## 2026-09-08 — 12×36 modelado como MaxConsecutiveWorkingDays = 1

Alternância estrita (12h trabalho, 36h descanso) implica não trabalhar dois dias
consecutivos, o que dá 14 plantões em 28 dias.

Confere com a realidade legal: o art. 59-A da CLT permite o regime; a lei não fixa carga
semanal, e a jurisprudência entende alternância entre semanas de 36h e 48h, média de ~42h
semanais e ~15 plantões por mês.

Logo **não** é necessário um `MaxNumAssignments` reduzido em separado — a alternância já é
a restrição correta.

Ressalva a registrar no texto: é aproximação em granularidade de dia, não representação
exata das 36 horas de descanso. O avaliador valida o código, não a fidelidade desta
representação.

Verificar antes de citar: PEC 221/19 e projeto do governo discutem limitar a média a 40h
semanais. Citar com data de consulta.

---

## 2026-09-08 — 12×36 é inviável no efetivo original: vira Experimento A

Aritmética sobre `long01`:

| | |
|---|---|
| Demanda total no horizonte (28 dias) | 740 atribuições |
| Profissionais | 49 |
| Capacidade sem limite de dias consecutivos | 49 × 28 = 1.372 → 54% de utilização |
| Capacidade com máx. 1 dia consecutivo | 49 × 14 = 686 → **108% de utilização** |

Passa de 100%: a instância seria **inviável nas restrições rígidas**, sem solução alguma.

Consequência para o desenho: o comparativo não pode manter o efetivo constante. O efetivo
passa a ser **resultado**, não parâmetro fixo.

**Experimento A** — qual o efetivo mínimo viável sob cada regime, para a mesma cobertura?
Estimativa preliminar: ~90 a 100 profissionais sob 12×36, contra 49. É medida de
viabilidade, portanto independente do algoritmo de resolução.

**Experimento B** — com o efetivo dimensionado em cada regime, comparar penalidade total e
sua distribuição entre profissionais.

Dado prático útil ao dimensionamento: no 12×36, 4 profissionais cobrem um posto 24/7.

---

## 2026-09-08 — Convenção do turno noturno

O turno `N` do INRC já atravessa a meia-noite (22:30 → 06:30) e a documentação oficial o
trata como pertencente a um dia; as restrições de dias consecutivos operam em dias.

Adotar a mesma convenção para o plantão noturno de 12h da instância brasileira, e citar a
fonte. Não inventar convenção própria.

---

## 2026-09-08 — Limites do que as medições sustentam

Custo computacional é propriedade da tripla (formulação, algoritmo, instância), não da
instância. Um branch-and-price sobre formulação por padrões pode inverter o ranking.

Afirmações **fortes** (propriedade da instância, independentes do algoritmo):
viabilidade / inviabilidade; valor ótimo comprovado; distribuição da penalidade no ótimo.

Afirmações **médias** (propriedade da formulação): número de variáveis e restrições; valor
do relaxamento linear na raiz; gap de integralidade inicial.

Afirmações **fracas** (dependem do algoritmo): tempo até o ótimo, nós explorados, gap ao
fim de um limite de tempo. Reportar como observação com escopo declarado.

Decorrências operacionais: manter instâncias pequenas o suficiente para provar
otimalidade; usar pesos idênticos entre configurações comparadas; preferir medidas
normalizadas a totais absolutos.

---

## Perguntas abertas

### A habilidade é restrição rígida ou flexível?

`AlternativeSkillCategory` varia de forma independente entre instâncias:

| Arquivo | Valor |
|---|---|
| long01, sprint01, sprint_hidden01, sprint_late01 | `weight="0"` → false |
| long_late01 | `weight="10"` → **true** |
| sprint_hint01 | `weight="10"` → false |

Leitura provável, **não confirmada**: `true` = categoria alternativa permitida mas
penalizada; `false` = não permitida (restrição de domínio). O peso 10 com `false` no
`hint01` seria valor residual não lido.

**Método de resolução, custo zero:** `long_early01` tem ótimo comprovado em 197 (Tabela 6
de Santos et al., 2016). As duas leituras geram modelos diferentes — se `false` = proibido,
o ótimo é ≥ 197; se `false` = livre, é ≤ 197. Só uma dá exatamente 197.

Implementar a habilidade como *flag* no código e rodar as duas versões. Resolve-se na
própria validação do Passo 3.

Alternativa: o relatório técnico da competição (CODeS/Technical Report/2010/1, citado nos
anais do PATAT 2010) traz a descrição formal das restrições e resolveria a questão
diretamente.

### Grau de dependência assistencial da instância brasileira

Não está em base pública — é classificação clínica, não cadastral. Decisão: tratar como
**parâmetro experimental** (mínimo, intermediário, intensivo) em vez de suposição fixa.
A confirmar com o orientador.

### Status jurídico do arcabouço normativo de dimensionamento

A Resolução COFEN 543/2017 foi revogada e há decisões judiciais que suspenderam resoluções
sobre dimensionamento; o Parecer Normativo COFEN nº 1/2024 foi aprovado nos limites das
liminares em vigor.

Verificar status atual em fonte primária, com data de consulta, antes de redigir o capítulo
de fundamentação. As conclusões do trabalho devem ser formuladas de modo a **não depender**
da vigência da norma — a norma é origem declarada dos parâmetros, não fundamento das
conclusões.

---

## Modelo de entrada

```
## AAAA-MM-DD — Título curto da decisão

O que foi decidido, em uma ou duas frases.

Por quê. Se houver fonte, citar.

Ressalva ou consequência, se houver.
```
