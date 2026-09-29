# VIRADA DE ESCOPO — 24/09/2026

**Este arquivo substitui, no contexto ativo dos projetos, os seguintes documentos:**
`CONTEXTO_PROJETO.md`, `PROPOSTAS.md`, `PLANO.md` e as notas de passagem de 15/09, 18/09,
22/09 e 23/09. O `DECISOES.md` foi reclassificado como ativo, na raiz, em 29/09, com status
por entrada — ver item 5 do `ESTADO_ATUAL.md`.

Eles **não foram apagados** — continuam no repositório, em `historico/escopo-comparacao-regimes/`,
e no histórico do Git. Saíram do contexto porque descrevem um trabalho que mudou de objeto.
Tudo deles que continua valendo está reproduzido aqui.

**Enquanto a especificação da ferramenta não estiver pronta, nenhum arquivo de contexto deve
ser reescrito.** Notas novas sim; reescrita de contexto, não.

---

## 1. O que mudou

Em 24/09/2026, em reunião de orientação, o escopo do TCC mudou por decisão do orientador.

**Escopo anterior:** comparar o efeito do regime de jornada (8 horas contra 12×36) sobre o
efetivo necessário e sobre a distribuição de carga, em instância construída a partir de
parâmetros normativos brasileiros.

**Objeção do orientador:** tamanho de turno não caracteriza regime nacional; a comparação
equivale a comparar dois tipos de turno, e concluir qual é "melhor" é contribuição fina para
um TCC.

**Escopo atual:** entregar uma **ferramenta de apoio à decisão** que gera escalas de
enfermagem a partir dos parâmetros de dimensionamento do COFEN e da legislação trabalhista
brasileira, com motor de otimização validado contra benchmark internacional com ótimos
publicados.

**Enquadramento que sustenta o trabalho:** o dimensionamento normativo é calculado por
fórmula e a escala é montada manualmente, sem instrumento que garanta conformidade legal. A
ferramenta preenche essa lacuna; o modelo validado é a prova de que ela funciona.

**Pendência de novidade:** antes de afirmar que a ferramenta preenche lacuna, é preciso
levantar o que já existe (sistemas comerciais de escala de enfermagem no Brasil, o que
implementa o dimensionamento do COFEN). Coluna a acrescentar na planilha de triagem dos 110.

---

## 2. O que está pronto e continua valendo

### 2.1 Validação do motor

| Instância | Modelo | Publicado (Santos et al., 2016) | Avaliador oficial |
|---|---|---|---|
| `sprint01` | 56 | 56 | 56 |
| `sprint02` | 58 | 58 | 58 |
| `long01` | 197 | 197 | 197 |
| `long02` | 219 | 219 | 219 |

Todos com otimalidade provada. A semântica das 13 restrições flexíveis foi validada contra o
avaliador oficial **antes** de a função objetivo existir, em 207 escalas mais 36 adversárias,
comparando cada par profissional × restrição. As escalas de teste vieram de seis heurísticas
construtivas com vieses opostos, nenhuma do solver.

`src/regressao.py` é o portão: confere otimalidade declarada, valor publicado, espelho contra
`avaliacao.py` e decomposição por profissional. Nenhum experimento roda antes de passar.

Pendência: `medium_late05` = 107 não fechou no tempo de solver disponível.

### 2.2 Parâmetros normativos (Parecer Normativo COFEN nº 1/2024)

| Grau de dependência | Horas/paciente/24 h | Enfermeiros | Técnicos e auxiliares |
|---|---|---|---|
| Mínimo | 4 | 33% (mín. 1 por turno) | 67% |
| Intermediário | 6 | 33% (mín. 1 por turno) | 67% |
| Alta dependência | 10 | 36% | 64% |
| Semi-intensivo | 10 | 42% | 58% |
| Intensivo | 18 | 52% | 48% |

Percentual sobre o quadro total, cobertura de 24 h. Unidade com graus misturados segue o de
maior carga. **Não usar** as proporções profissional/paciente do tipo "1 para 6" — eram da
Resolução 543/2017, revogada, e não constam do Parecer.

Fórmula oficial de quadro de pessoal:
`QP = [Σ (pacientes × horas)] × DS × (1 + IST) / CHS`, com IST = 15% e CHS = carga horária
semanal contratual. **A fórmula não depende do regime de jornada.** O Parecer delega
explicitamente a montagem da escala ao setor.

Fora de escopo, declarado: IST de 15% (férias e ausências), 5% de educação permanente,
enfermeiros gerenciais, acréscimo de 10% por restrição de atividade.

Status jurídico: Resolução 543/2017 revogada em 12/03/2024; há decisões judiciais suspendendo
atos normativos sobre dimensionamento. Os parâmetros entram como **valores declarados, com
fonte e data de consulta**, nunca como exigência legal vigente.

### 2.3 Base legal da jornada

- Art. 7º, XIII da Constituição: 8 horas diárias, 44 semanais.
- Art. 59-A da CLT (Lei 13.467/2017): 12×36 por acordo individual escrito ou negociação
  coletiva. **Não é obrigatório** — é exceção autorizada.
- STF, ADI 5994: constitucionalidade do acordo individual. Sessão virtual de 23 a 30/06/2023,
  vencido o relator Marco Aurélio, acórdão redigido por Gilmar Mendes.
- Art. 66 da CLT: 11 horas entre jornadas. Art. 67: 24 horas de descanso semanal.
- Aritmética do regime: 14 plantões de 12 h = 21 plantões de 8 h = 168 h em 28 dias = 42 h
  semanais. Sem fonte para "média de 42 h" como regra jurídica — é aritmética, e deve ser
  apresentada assim.

### 2.4 Decisões de modelagem em vigor

- Formulação por atribuição, variável binária `x[n,s,d]`, com janelas deslizantes explícitas.
  Divergência declarada de Santos et al., que usa variáveis de janela.
- Cobertura é **igualdade rígida**, inclusive onde a demanda não é declarada (demanda ausente
  = zero, atribuição proibida).
- Habilidade é restrição **flexível**, com coeficiente na variável de atribuição. Versão
  rígida existe como opção declarada.
- 12×36 = no máximo 1 dia consecutivo de trabalho **mais** a sequência proibida
  (noturno, folga, diurno), sem a qual o descanso cai para 24 h.
- Regime de 8 horas: três proibições de interjornada e no máximo 6 dias consecutivos.
- Limites legais são **rígidos** no modelo, via flag, e o XML continua instância normal do
  INRC.
- **Definição de viável:** satisfaz a cobertura e todos os limites legais de jornada e
  descanso; as demais restrições entram apenas na penalidade.
- Uma restrição do INRC (turno noturno antes de fim de semana livre) fica **fora da função
  objetivo**: o avaliador oficial não a pontua.
- Duas restrições (máximo de fins de semana em quatro semanas; folgas após noites) estão
  implementadas mas **não são exercitadas por nenhuma instância** — sem conferência externa
  possível.
- Tempo de resolução é **afirmação fraca**: nunca vai ao texto como resultado, só como limite
  operacional com máquina e solver nomeados.
- **Novo em 25/09:** o escopo passa a admitir solução inicial heurística para warm start do
  solver, revertendo em parte a exclusão de matheurística decidida em 08/09. A heurística
  entra como partida — solução inicial e corte superior —, nunca substituindo a prova de
  otimalidade. Só será implementada se a curva de escalabilidade mostrar faixa em que a prova
  não fecha.

### 2.5 Instância brasileira

Nasce de **perfil assistencial contínuo** derivado da norma, não de conversão do `long01`. Os
dois regimes são recortados do mesmo perfil, pela mesma regra. Porte: **5.920 horas-profissional
em 28 dias = 211,4 h/dia**, calibrado pela `long01`.

Requisito do gerador: o perfil contínuo deve vir da necessidade assistencial hora a hora,
nunca de blocos de 8 ou 12 horas — senão o regime daquele tamanho ganha resíduo zero de graça.
Há conferência automática para isso.

---

## 3. Resultados obtidos, e onde eles passam a servir

Deixam de ser o resultado central do trabalho. Passam a ser **validação e demonstração de uso
da ferramenta**.

**Experimento A.** Com demanda constante, 36 profissionais nos dois regimes, em 20
combinações, com 35 provado inviável e 36 com escala aprovada pelo avaliador. O número
coincide com o quadro da fórmula do Parecer (5.920 ÷ 168 = 35,24). **Serve como conferência
independente de que a tradução da norma está correta.**

Com demanda variando entre dias úteis e fins de semana (forma medida no `long01`: 29 contra
20 atribuições), os regimes se separam: 12×36 exige 40, contra 38 e 37 no de 8 horas. **Serve
para mostrar que a ferramenta detecta quando o quadro da fórmula não admite escala viável** —
que é o caso de uso principal. Mecanismo: no 12×36 ninguém trabalha dois dias seguidos, logo
o efetivo cobre a soma de dois dias, não a média.

Ressalva: um grau de dependência, uma regra de arredondamento, uma forma de variação.

**Experimento B.** Entre escalas de mesmo custo ótimo, o profissional mais penalizado recebe
de 7 a 18 violações (`sprint01`), de 11 a 19 (`long01`), de 14 a 20 (`long02`). Custo mínimo
**não** determina distribuição. **Serve como base de uma função da ferramenta:** entre as
escalas de custo ótimo, escolher a mais equilibrada em vez de aceitar a que o solver devolveu
por acaso. O mecanismo já está implementado.

**Achados metodológicos que sobrevivem para o texto:** a reagregação de turnos sobrepostos em
janelas disjuntas (65 de 69 instâncias, com grupo de controle); o piso forçado (73% a 81% do
ótimo das instâncias grandes é excesso de atribuição decidido por subtração); o lote *early*
ser dois cenários com variações de contrato, não 15 cenários independentes; e o comportamento
do avaliador oficial com o padrão das 36 h.

---

## 4. O que virou histórico

- A comparação entre regimes de jornada como **tese central** do trabalho.
- O título e o objetivo geral formulados em 21/09.
- O plano de trabalho até 04/11 anterior a 24/09.
- As propostas P10, P11 e P13 na forma em que estavam pendentes.

---

## 5. Próximos passos

1. **Especificação da ferramenta** — o que entra, o que sai, o que ela não faz. É o documento
   que destrava todo o resto. Em elaboração no projeto de redação.
2. **Curva de escalabilidade do método exato** — instâncias com 40, 60, 80, 120 e 200
   profissionais, registrando se o solver prova otimalidade, o valor e o gap. Decide se
   heurística de warm start é necessária. Em execução no projeto de códigos.
3. Depois da especificação: contexto novo dos dois projetos, triagem do que sobrevive das 22
   decisões e 13 propostas, e plano até 04/11.

Entrega: **04/11/2026**. Congelamento de resultado numérico: **14/10/2026**.
