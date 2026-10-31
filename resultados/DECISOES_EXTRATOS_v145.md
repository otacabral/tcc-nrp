# Extratos do DECISOES.md (v1.4.5)

Extraído do DECISOES.md no commit 634eeb5, tag v1.4.5.

Cópia literal das entradas pedidas, na ordem pedida, cada uma do título até o separador; sem resumo nem reescrita. O título traz a data; o status está na própria entrada.

Fica de fora a nota de 31/10 na entrada do Caso A ("a transcrição passou a ser versionada em
resultados/caso_a_pratica_2026-10-23/", commit `aebd8d2`), porque é posterior à tag. Por isso o
caminho `D:\TCC\escrita\fontes\...` citado nessa entrada é o de antes da mudança.

---

## 2026-09-08 — Formulação: atribuição, não janelas

**Status: vigente**

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

**Status: vigente**

O elemento `<Preferred>` do XML **não** é preferência: é a demanda obrigatória.

Fonte: Haspeslagh, De Causmaecker, Stølevik e Schaerf, *First International Nurse
Rostering Competition 2010*, anais do PATAT 2010, p. 499–500. O texto declara a demanda
como restrição rígida e lista apenas duas restrições rígidas — cobrir toda a demanda e no
máximo um turno por enfermeira por dia.

Santos et al. (2016) modelam como igualdade (restrição 1). Consistente.

---

## 2026-09-29 — Especificação da ferramenta

**Status: vigente**

Especificação completa:
<https://claude.ai/code/artifact/ebfaeed9-a670-49d7-8f24-0067a43f2f04>. Decidida pelo
Otávio no projeto de redação; o orientador é informado na reunião. Fecha a P2.

**Título.** "Ferramenta de apoio à decisão para escalas de enfermagem baseada em Programação
Inteira: conformidade com o dimensionamento do COFEN e a legislação trabalhista".

**Objetivo.** Minimizar a penalidade total, que inclui os pedidos. Entre as escalas
empatadas, a de menor penalidade individual máxima (mecanismo do Experimento B).

**Entradas.**
- Pacientes por grau de dependência. O percentual de enfermeiros vem do grau de maior carga.
- Quadro por quantidade de enfermeiros e de técnicos; nomes opcionais.
- QP em duas parcelas; a escala é comparada ao núcleo sem IST, porque o IST cobre ausências
  que a escala não modela.
- Variação de demanda como razão fim de semana / dia útil, com o total de horas preservado.

**Regras.**
- Proporção de enfermeiros no quadro, com piso de 1 enfermeiro por turno.
- Carga de 42 h semanais.
- Início numa segunda-feira, horizonte de 28 dias.
- Indisponibilidade rígida para férias e licenças; pedidos continuam flexíveis.

**Configuração.**
- Opções avançadas recolhidas, e só depois de o formulário básico funcionar. Critério para
  uma opção entrar: o motor já suporta, não mexe na garantia legal, custa no máximo meio dia.
- Arquivo de configuração no formato INRC, para baixar e carregar, com validação (esquema e
  conferência de descanso) e resumo em português antes de resolver.

**Licença.** MIT.

---

## 2026-09-29 — Redesenho da ferramenta

**Status: vigente**

Decidido pelo Otávio no projeto de redação. Especificação completa no link registrado na P2
e na entrada "2026-09-29 — Especificação da ferramenta". **Regra central: a CLT é restrição —
trava a escala; o COFEN é alerta — nunca trava.**

**Configuração com turnos editáveis.** O usuário define os turnos por hora de início e
duração. Novo caminho de `instancia_br.construir(turnos=...)`; o caminho por pacientes
continua igual, e o Experimento A segue reproduzível.

**Demanda informada pelo usuário.** Generalista: enfermeiros e técnicos por turno, com
valores opcionais diferentes para o fim de semana. Específica: por data × turno × categoria,
partindo da generalista (um feriado, por exemplo). **Cobertura entre categorias (decidido em
29/09; antes "a confirmar"):** enfermeiro pode cobrir posto de técnico, como no caminho por
pacientes; técnico nunca cobre posto de enfermeiro. A saída informa quantos turnos de
enfermeiro foram usados em posto de técnico.

**CLT como trava, com diagnóstico do motivo.** *(Registro de 29/09, Etapa 5: o diagnóstico
ainda não estava implementado. Implementado na Etapa 7 — ver "Diagnóstico da trava" abaixo.)*
As regras de descanso deixam de ser escritas
à mão e passam a ser **geradas dos horários** (`pares_proibidos_por_horario`): para cada par
de turnos, o descanso medido no relógio é proibido abaixo de 11 h (art. 66), e abaixo de
36 h depois de turno de 12 h ou mais (art. 59-A). O gerador é a **fonte única** das regras de
descanso — padrões do XML e conferência das sequências saem dele. **Pares já proibidos pelo
limite de dias seguidos do contrato não são emitidos** (opção 1, decisão do Otávio): com o
descarte, a lista gerada é idêntica à escrita à mão nos dois regimes, e o modelo e o XML do
Experimento A não mudam — conferido em 361 XML, byte a byte. **A equivalência é garantida
por teste permanente** (`src/testes_entrada.py`): pares gerados sem descarte = pares com
descarte ∪ pares proibidos pelo limite de dias seguidos. Sem isso, o descarte poderia
esconder uma proibição. A conferência de descanso na escala também passa a tirar o exigido
do turno que termina, e vale para qualquer horário.

No caminho novo, o teto de 42 h/semana é **em horas**, rígido no modelo
(`Instancia.carga_maxima_h`), porque com turnos de durações diferentes contar turnos não
limita horas; e o limite de dias seguidos é 6 (art. 67, aproximado como no regime de 8 h) —
a alternância de quem faz turno de 12 h sai sozinha da regra das 36 h.

**COFEN como alerta** (`instancia_br.alertas_cofen`, que não mexe no modelo): proporção de
enfermeiros no quadro pelo grau predominante informado; turnos sem enfermeiro na demanda;
com pacientes informados, quadro abaixo do QP completo, mostrando também o núcleo. **No
caminho novo, o piso de 1 enfermeiro por turno deixa de ser cobertura rígida** — quem define
a demanda é o usuário — e vira alerta.

**Objetivo (Etapa 7, decisão do Otávio, 29/09).** Evitar enfermeiro em posto de técnico
quando não for necessário, com **pesos inteiros na mesma resolução**: cada turno de enfermeiro
em posto de técnico custa 1; cada pedido de folga não atendido custa W = (número máximo
possível de turnos de enfermeiro em posto de técnico) + 1, e o máximo possível é o total de
postos de técnico do horizonte. Como W passa tudo o que os postos de técnico podem somar,
negar um pedido nunca compensa: primeiro os pedidos, depois o enfermeiro em posto de técnico.
Sem pesos fracionários. Implementado em `ferramenta.pesos`; o modelo ganhou a família
`custo_atribuicao`, vazia no INRC. *Conferido:* no caso de 8 enfermeiros + 5 técnicos, a
contagem caiu de 66 (sem os pesos) para **35, que é o mínimo aritmético** (os técnicos dão
840 h para 1.120 h de posto de técnico), com os 3 pedidos atendidos nos dois casos.

**Equilíbrio ligado na ferramenta.** Com a penalidade da etapa 1 fixada no ótimo, a etapa 2
minimiza a penalidade individual máxima — o mecanismo do Experimento B, sobre o mesmo modelo
(`ferramenta.equilibrar`). Só roda com a etapa 1 ótima e penalidade maior que zero.
*Medido, afirmação fraca:* no 12×36 equivalente ao Experimento A, com 40 profissionais e 20
pedidos, a etapa 1 levou 56,9 s e a etapa 2 90,7 s de CPU (appsi_highs, na máquina do
Otávio); a maior penalidade individual caiu de 10 para 7.

**Diagnóstico da trava.** Quando o quadro informado não tem escala legal, a tela explica o
motivo pela conta mais simples que se aplica, nesta ordem: **horas** (demanda do período
acima de 42 h/semana × equipe); **alternância** do plantão de 12 h (dois dias seguidos somam
mais plantões que a equipe, com o par de dias); **categoria** (horas ou plantões de posto de
enfermeiro acima do que os enfermeiros cobrem); **dia específico** (numa data, descontadas as
férias, sobram menos pessoas que postos); **combinação de regras** (nenhuma conta explica; o
solver provou). Em todos, quantos faltam e o menor quadro viável. Implementado em
`ferramenta.diagnosticar`, só contas, sem solver. Na busca do menor quadro, cada tamanho é
tentado com a composição da regra e, se inviável, com todos os acréscimos como enfermeiros —
enfermeiro cobre tudo o que técnico cobre, então se essa também falha, nenhuma composição
daquele tamanho fecha. *Conferido:* um caso por motivo, com o motivo registrado antes de
rodar; os cinco acertaram, e o 39 do Experimento A cai em alternância.

**Funcionalidades congeladas em 10/10.** **A Etapa 4 (P1, curva de escalabilidade com
objetivo não trivial) passa para depois da Etapa 7.**

*Nota de 02/10 — carga mínima, verificação sem mudança no código.* No caminho de turnos
configurados, o contrato tem **MinNumAssignments desligada** (valor 0, peso 0): nenhuma carga
mínima, nem rígida nem penalizada. **MaxNumAssignments ligada**, valor 14 turnos = 168 h ÷
12 h (o turno mais curto do modelo), rígida por `RIGIDAS_LEGAIS_BR`; o teto que vale é o de
**horas**, 168 h no horizonte (`carga_maxima_h`), também rígido. O mínimo, se existisse,
seria contado em turnos, que é o que o formato do INRC sabe contar. Medido no 12×36
equivalente ao Experimento A, 40 profissionais (14 + 26), objetivo completo (pesos + etapa
de equilíbrio), appsi_highs: **menor carga 120 h, maior 168 h**, com e sem os 20 pedidos de
folga do teste 7.2. Sem pedidos, 22 pessoas ficam em 168 h e 7 em 120 h; média 153,6 h
(512 plantões × 12 h ÷ 40). A etapa de equilíbrio não iguala horas: ela minimiza a
penalidade individual máxima, e horas não são penalidade. Uma diferença de 48 h no mês
entre colegas do mesmo regime é o que pede decisão (carga mínima, ou equilíbrio de horas)
— ver `ESTADO_ATUAL.md`, seção 5.

*Nota de 02/10 — o limite de tempo nunca chegava ao HiGHS.* Pelo appsi, o
`LegacySolverInterface.solve` refaz `config.time_limit` a partir do argumento `timelimit`
da chamada, que tem padrão vazio; o limite que `modelo.resolver` gravava antes da chamada
era apagado. É a mesma armadilha já registrada no código para o `load_solution`. Corrigido
passando o limite na chamada; conferido no log do HiGHS ("Time limit reached" em 20,03 s com
limite de 20 s); regressão OK. **Os números registrados não mudam**: todas as resoluções
até aqui terminaram com resposta provada — a maior da curva de escalabilidade antiga levou
549 s, abaixo dos 900 s que se supunha valerem. O que muda é o comportamento: a tela agora
para em 600 s por resolução, em vez de poder rodar sem fim. Achado ao preparar a P1: o teste
rápido com "60 s por etapa" passou de 800 s de CPU.

*Nota de 02/10 — o que a tela diz quando o tempo esgota (decisão do Otávio).* Três desfechos
distintos: **(a)** ótimo provado → "Escala gerada."; **(b)** escala encontrada sem prova →
"Escala gerada; pode haver uma melhor", com o gap da etapa 1; **(c)** tempo esgotado sem
escala → "Não foi possível gerar a escala no tempo disponível." **Nunca "faltam N" em (c)**:
o diagnóstico de falta só aparece com prova de inviabilidade, pela conta ou pelo solver. Se
o quadro informado foi provado curto e o seguinte esgotou o tempo, a tela mostra o
diagnóstico do informado (provado) e diz que o menor quadro viável não foi determinado. Na
situação (b) a etapa 2 não roda (só roda sobre ótimo provado). *Defeito achado ao montar o
teste de (b):* parado no limite de tempo **com** escala, o appsi devolve `maxTimeLimit`, e
`experimento_a.classificar` só reconhecia "optimal" ou "feasible" — classificava como não
decidido e descartava uma escala legal. Corrigido com `modelo.tem_solucao`, que lê o valor
da melhor solução e não o nome do estado. Não afeta nenhum número registrado, porque até
02/10 o limite nunca chegava ao solver e toda resolução terminava com prova. *Testes*
(`src/testes_ferramenta.py`, 8a–8d, esperado registrado antes): os quatro acertaram. Os casos
(b) e (c) dependem da máquina — escolhidos por sondagem no log do HiGHS (no 40 com 20
pedidos, primeira escala aos ~17 s com gap 1,03%, prova aos ~43 s), limites de 25 s e 3 s.

*Nota de 02/10 — a etapa 2 passa a equilibrar HORAS (decisão do Otávio).* Com a penalidade
da etapa 1 fixada no ótimo, a etapa 2 minimiza a **amplitude de carga**: maior carga do
período menos a menor, em horas, sobre todos os profissionais (`ferramenta.preparar_equilibrio`).
A distribuição dos pedidos negados continua informada na tela (quantos, em quantas pessoas,
no máximo quantos por pessoa), mas não é otimizada. **O mecanismo é o do Experimento B** —
fixar o ótimo, otimizar um segundo critério — e o Experimento B continua válido como
demonstração; muda o critério que a ferramenta otimiza. A etapa 2 agora roda também com
penalidade zero, porque a carga pode estar desequilibrada sem pedido negado. *Medido no caso
de 40 profissionais (12×36, 14 + 26, 20 pedidos):* amplitude **72 h na escala da etapa 1 →
48 h**, com otimalidade provada; carga de 120 h a 168 h; 20 de 20 pedidos atendidos. A
amplitude de 48 h é **a menor possível com a penalidade da etapa 1 fixada**, e a conta mostra
por quê: fixado o ótimo, ficam fixos os 96 turnos de enfermeiro em posto de técnico. Os
enfermeiros fazem então 56 + 96 = 152 plantões, 10,86 por pessoa — ao menos um fica com 10
ou menos (120 h). Os técnicos fazem 456 − 96 = 360, mais que 26 × 13 = 338 — ao menos um
fica com 14 (168 h). Logo amplitude ≥ 48 h, e o solver a atinge. A diferença de 48 h da nota
anterior não era acaso da etapa 1: é consequência do objetivo (técnico em posto de técnico
antes de enfermeiro), e equilibrar horas não a remove.
*Afirmação fraca:* etapa 1 em 35,9 s e etapa 2 em 37,5 s de relógio (appsi_highs, Intel
i5-10210U, Windows 11). Questão aberta sobre quem tem férias: ver P4 do `PROPOSTAS.md`.

---

## 2026-10-02 — Carga por contrato

**Status: vigente**

Decidido pelo Otávio no projeto de redação, para o caminho de turnos configurados (a
ferramenta). Implementado em 02–03/10.

**a) Carga contratual por profissional.** Cada profissional tem carga contratual semanal de
30, 36, 40 ou 44 h, informada na tela de equipe. Padrão 44 h, o limite da Constituição
(art. 7º, XIII). `instancia_br.CARGA_CONTRATUAL_PADRAO`, `Instancia.carga_semanal_h`.

**b) O teto vale sobre o horizonte, não por semana**: carga × 4 semanas. O 12×36 tem semanas
de 48 h compensadas por semanas de 36 h (CLT, art. 59-A); um teto semanal o tornaria ilegal.
*Como estava antes (verificado em 02/10):* o teto já era sobre o horizonte — uma restrição por
profissional, soma das horas nos 28 dias ≤ 168 h (42 × 4), igual para todos — mas não
descontava férias.

**c) A etapa 2 minimiza (maior − menor) da FRAÇÃO cumprida**: horas trabalhadas ÷ horas
devidas, com horas devidas = carga semanal × dias disponíveis ÷ 7. Quem tem 44 h e 14 dias
de férias deve 88 h, não 176 h. Resolve a P4 (amplitude distorcida por férias). Quem não tem
dia disponível no período fica fora da fração. Substitui a etapa 2 por horas da nota de 02/10
na entrada "Redesenho"; o mecanismo continua o do Experimento B.
*Marca de revisão em 30/10/2026:* o critério de minimização muda de **soma das amplitudes por categoria** para **min-max (máxima das amplitudes)**. Ver "2026-10-30 — Etapa 2 por min-max (v1.4.5)".

**d) O teto também usa os dias disponíveis** — é a mesma conta das horas devidas,
`Instancia.horas_devidas`, que serve ao teto rígido (`modelo.py`), à conferência
(`solucao.conferir_rigidas`) e ao denominador da fração. Uma conta só, para os três não
divergirem.

**e) O painel do COFEN usa como CHS a média das cargas contratuais da equipe**, e a tela
mostra o valor usado (`instancia_br.chs`).

**f) O caminho por pacientes e o Experimento A ficam intactos**, com 42 h como hipótese
declarada. *Conferido:* 544 XML do caminho dos experimentos e do caminho por pacientes (5
graus × 2 regimes × 2 regras × efetivos 36–44 × 3 variações, mais 4 por pacientes) saem
idênticos byte a byte antes e depois (`docs/conferencia_xml_experimentos.py`). A comparação
foi posta à prova com um byte alterado numa cópia, e acusou. A conferência avulsa dos 361 XML
de 29/09 não ficou no repositório; esta a substitui.

**Argumento.** As 42 h do 12×36 decorrem da alternância — 14 plantões de 12 h em 28 dias são
168 h, ou 42 h por semana —, não de um teto. Fixar 42 h para todo contrato confunde
consequência do regime com regra. E o levantamento do projeto de redação aponta contratos
heterogêneos em só 30% dos estudos: tratar a carga como dado do contrato, e não como
constante, é o que o caso real pede.

**Consequências na ferramenta.** Quem a varredura do menor quadro acrescenta entra com 44 h.
O piso e o diagnóstico da trava passam a comparar as horas da demanda com a soma dos tetos
individuais (carga nos dias disponíveis), e dizem "faltam pelo menos k de 44 h".
`MaxNumAssignments` do XML fica com a maior carga no horizonte inteiro ÷ turno mais curto —
nunca mais apertado que as horas de ninguém (no modelo de 6 h: 29, antes 28).

**Testes** (`src/testes_ferramenta.py`, `casos_carga`, esperado registrado antes, 03/10):
- **9a, acertou:** em equipe mista 30/44 h, a maior carga entre os de 30 h foi 112 h (teto
  120 h) e entre os de 44 h, 168 h (teto 176 h); rígidas OK.
- **9b, acertou, com ressalva registrada antes de rodar:** no 12×36 com 44 h, ninguém passa
  de 14 plantões. Mas o teto de 176 h também para em 14 (15 plantões dariam 180 h), então o
  teste não separa alternância de teto.
- **9c, metade acertou:** quem tem 14 dias de férias ficou com 72 h de 88 h devidas,
  81,8%, dentro da faixa dos demais (63,6%–90,9%). Em horas, ficaria em 72 h contra 112–160 h.
- **9c, a outra metade falhou:** amplitude final de 27,3% contra ≤ 10 pp esperados. **O erro
  é do esperado**, e a conta mostra por quê. Com a penalidade da etapa 1 fixada em zero,
  enfermeiro não ocupa posto de técnico. Os enfermeiros cobrem exatamente o posto de
  enfermeiro (63,6% cada), e os técnicos não cabem abaixo de 90,9%; o mínimo é 27,3 pp, e o
  solver o provou.
- **9d, acertou:** o equilíbrio por fração reduziu a amplitude de 45,5% para 27,3%.

**Esperados antigos que a carga de 44 h desatualizou (03/10, não corrigidos — parado por
regra).** O caso 5 da tela e o 7.1 esperavam ≥ 35 turnos de enfermeiro em posto de técnico,
"mínimo aritmético" calculado com 42 h: 5 técnicos × 168 h = 840 h para 1.120 h de posto. Com
o padrão de 44 h, os técnicos dão 5 × 176 = 880 h, faltam 240 h = **30 turnos**, e o solver deu
exatamente 30 — o caso 5 falha (≥ 35), o 7.1 passa (sua condição é ≤ 35), mas o texto dele
ainda diz "mínimo aritmético 35". Ambos precisam do esperado refeito com 44 h.

**Suíte de 03/10:** `regressao.py --todos` OK (os 4 ótimos da Tabela 6); `testes_entrada.py`
completo OK; testes da tela: casos 1–4 OK, caso 5 FALHA (acima), 7.1 OK; a suíte foi
interrompida pelo sistema por falta de memória durante o 7.2 — 7.2, 7.3 e 8a–8d **não
rodaram** depois da carga por contrato. Os testes 9a–9d rodaram à parte (acima).

**O que a falha do 9c revela: decisão em aberto, P6 do `PROPOSTAS.md`.** Com enfermeiros
dedicados ao posto de enfermeiro, a amplitude da fração fica presa à razão entre posto de
enfermeiro e posto de técnico, não às férias. A P1 não foi relançada: o bloco parou aqui por
regra.

**g) Adendo de 03/10 — a etapa 2 equilibra DENTRO de cada categoria (P6 decidida pelo
Otávio).** Substitui o critério do item c) quanto ao alcance: a etapa 2, com a etapa 1 fixada
no ótimo, minimiza (maior − menor fração entre enfermeiros) + (maior − menor fração entre
técnicos). A fração continua a do item c). A diferença ENTRE categorias não é otimizada: vem
da demanda de cada posto frente ao tamanho de cada categoria, e a tela e a planilha a mostram
à parte (fração média dos técnicos − fração média dos enfermeiros, em pontos percentuais).
`ferramenta.preparar_equilibrio`, `ferramenta.por_categoria`. Motivo: a amplitude da equipe
inteira media a razão entre os postos, não a justiça entre colegas que fazem o mesmo trabalho
(P6).

**h) Indicador novo, sem mudança no modelo: horas de contrato não utilizadas por
categoria** = horas contratadas nos dias disponíveis − horas escaladas. Na tela (uma linha por
categoria, com a faixa da fração) e na planilha (aba Resumo).

**Esperados corrigidos ou novos (03/10).**
- **9c**, refeito pelo critério por categoria, com a conta registrada ANTES de rodar (commit
  `08603c6`): enfermeiros cobrem 672 h ÷ 6 = 112 h cada, amplitude 0; técnicos cobrem
  1.792 h, e como 23x = 224 não tem inteiro, a amplitude mínima é 1/22 = 4,55 pp, atingida só
  com Téc 1 em 10 turnos (90,9%). **Acertou em tudo:** enfermeiros 0, técnicos 4,55 pp,
  provado; Téc 1 em 90,9%, dentro da faixa dos técnicos (86,4%–90,9%); horas não utilizadas
  384 h (enfermeiros) e 232 h (técnicos); diferença entre categorias +24,9 pp, como na conta.
- **9d:** o critério caiu de 36,4 pp na escala da etapa 1 para 4,5 pp, provado.
- **Caso 5 da tela:** esperado refeito para ≥ 30, pela conta com o padrão de 44 h (5 × 176 =
  880 h para 1.120 h de posto de técnico, faltam 240 h = 30 turnos). **Corrigido depois de ver o
  resultado (30)** — admitido por ser aritmético e independente do solver. O texto do 7.1
  também passou a dizer "mínimo aritmético 30"; a condição do 7.1 (≤ 40) não mudou. Ambos
  deram 30.
- **9b-sem-teto**, variante nova, esperado registrado antes: desligados o teto de horas E o
  `MaxNumAssignments` (que no 12×36 é floor(176/12) = 14 e é rígido — desligar só o teto de
  horas deixaria esse limite parando em 14), maximizou-se o número de plantões de Téc 1.
  **Deu 14, provado ótimo.** Quem limita é a alternância (regra das 36 h), não o teto.

**Suíte completa de 03/10, depois do adendo (um teste por processo, por memória):** tela 1–5,
7.1, 7.2, 7.3, 8a–8d, 9a–9d e 9b-sem-teto OK; `regressao.py --todos` OK (56, 58, 197, 219 =
Tabela 6); `testes_entrada.py` OK; 544 XML idênticos byte a byte ao commit `cec3d8e`.
Observação, não resultado: no 7.2 (40 profissionais, 20 pedidos) a etapa 2 por categoria
parou no limite de 600 s sem provar (amplitude 34,1 → 13,6 pp); no 9c provou em 111 s.
Máquina: i5-10210U, 12 GB, Windows 11, HiGHS 1.15.1 via appsi.

**i) Adendo de 05/10 — limite e exibição da etapa 2 (decisão do Otávio).**
- **Limite da etapa 2 na tela: 180 s** = max(120 s; 1,5 × 81,1 s), arredondado para cima ao
  minuto; 81,1 s é o tempo em que a etapa 2 do caso de 88 profissionais da rodada com folga
  chegou a 90% da redução final (`PROPOSTAS.md`, P1). A etapa 1 continua com 600 s. A etapa 2
  usa o menor dos dois limites (os testes encurtam o da etapa 1). `ferramenta.TEMPO_ETAPA2`.
- **A etapa 2 não mostra gap.** Na tela e na planilha mostra a **diferença máxima de carga
  entre colegas dentro de cada categoria**, em plantões e em horas ("1 plantão (12 h)"). O gap
  continua só para a etapa 1.
- **Definição (decisão de implementação, não óbvia):** o desvio de cada profissional em relação à
  sua parte justa — horas trabalhadas − (fração média da categoria × suas horas devidas) —,
  maior menos menor. Com contrato e disponibilidade iguais, é a diferença de horas entre quem
  mais e quem menos trabalhou. Com férias ou contratos diferentes, não pune quem deve menos
  horas (o mesmo cuidado da P4). Em plantões só quando todos os turnos têm a mesma duração;
  senão, só horas. `ferramenta.por_categoria`, `ferramenta.fmt_diferenca`. No 9c, esperado
  registrado antes: técnicos "1 plantão (8 h)", enfermeiros "nenhuma (0 h)".
- **Adendo de 05/10 ao item i — o teste 9c não exige prova (decisão do Otávio).** A prova de
  ótimo da etapa 2 dentro dos 180 s depende da carga da máquina: 146,9 s rodando sozinho;
  falhou em 05/10 com outro processo rodando junto. O 9c passa a conferir que a amplitude
  atingiu o piso da conta registrado no commit `08603c6` (enfermeiros 0, técnicos 4,55 pp;
  tela "nenhuma (0 h)" e "1 plantão (8 h)"), sem exigir prova. Teste novo, 9c-tela: com a
  etapa 2 encurtada para 20 s, para que termine sem prova, nem a tela nem a planilha podem
  dizer "provado".

---

## 2026-10-05 — Diagnóstico da trava: teto pela alternância e férias no par

**Status: vigente**

Decidido pelo Otávio em 05/10 (fecha a P7). **Correção do diagnóstico da trava**
(`ferramenta.diagnosticar`); o modelo e o objetivo não mudam. O diagnóstico só afirma
condições NECESSÁRIAS: cada motivo que ele mostra é uma conta que, sozinha, prova que não há
escala.

**a) Teto de cada pessoa** (`ferramenta.teto_horas`) = o menor entre a carga contratual nos dias
disponíveis e, quando ninguém pode trabalhar dois dias seguidos (12×36), a duração do turno
mais longo × a soma, por bloco de dias disponíveis seguidos, de ceil(tamanho / 2). É limite
superior válido: num bloco de b dias sem dois seguidos cabem no máximo ceil(b / 2) plantões.
Com 44 h e o horizonte inteiro no 12×36: 168 h (14 plantões), não 176 h.

**b) Duas condições por categoria**, com o enfermeiro podendo cobrir posto de técnico:
- *horas*: primeiro os enfermeiros (horas do posto de enfermeiro contra os tetos deles — se
  falta, motivo "Categoria"); depois os técnicos (horas do posto de técnico contra os tetos dos
  técnicos mais a folga dos enfermeiros — se falta, motivo "Horas");
- *par de dias seguidos no 12×36*: os plantões do par contra as pessoas disponíveis em pelo
  menos um dos dois dias, descontando férias e licenças (motivo "Alternância"); e o mesmo só
  para enfermeiros e posto de enfermeiro (motivo "Categoria"), quando o par geral não dispara.

O diagnóstico mostra **todos** os motivos que disparam, cada um com os números; o título junta
os nomes. A ordem: horas, par, dia específico; "combinação de regras" só quando nenhum dispara.

**Esperado registrado antes de rodar** (`src/testes_ferramenta.py`, 7.3 e 7.4): na clínica da
demonstração com 20 técnicos, "Horas" (324 h contra 312 h) e "Alternância" (ter 03/11 e qua
04/11: 28 plantões, 27 pessoas); com 21, nenhum; o caso "combinação" do 7.3 passa a "Categoria"
(672 h contra 667,4 h) e "Alternância" (sáb 09 e dom 10/01, 4 plantões para 3 pessoas) — motivo
mais específico e verdadeiro; os outros quatro mantêm o motivo.

**Fica igual:** `ferramenta.piso` (que decide se um quadro vai ao solver) continua com a conta
antiga; trocá-la mudaria quais quadros o solver tenta. Não pedido.

---

## 2026-10-09 — Condição das afirmações de ótimo provado: tolerância do HiGHS

**Status: vigente.** Decidido pelo Otávio em 09/10. Nada muda no código.

O HiGHS declara "ótimo" com gap relativo de até 0,01%. Como os objetivos da etapa 1 são
inteiros, a prova vale como ótimo inteiro quando 0,0001 × objetivo < 1 — o que vale em todos os
resultados registrados, exceto na P1 de 03/10 com N = 40, 60 e 80; nesses três, o log mostra
limite inferior igual ao objetivo (gap 0 exato). Registrado no `NUMEROS_TCC.md` como condição
das afirmações de ótimo; conferência em `resultados/relatorio_2026-10-09c.md`.

---

## 2026-10-13 — Art. 67 com horários editáveis

**Status: vigente.** Correção de defeito antes do congelamento (16/10). Decisão do Otávio:
correção (a) + (b). Esperado registrado e commitado antes de implementar
(`resultados/relatorio_2026-10-13a.md`). Supera, na entrada "2026-09-29 — Ajustes da Etapa 2",
a afirmação "o modelo garante o art. 67 por construção" (marcada lá, sem apagar).

**Defeito.** Com turnos editados na tela, o art. 67 (24 h de descanso semanal) não era
garantido pelo modelo. N 23–07, folga, M 05–13 = 22 h: passa nas 11 h e não era proibido. A
conferência no relógio (`medir`/`cumpre`) reprovava, mas a ferramenta entregava a escala com
"admite escala legal", só com a métrica "NÃO CUMPRE", e a busca do menor quadro a contava como
viável. O argumento de 29/09 (pior caso noite → folga → manhã = 24 h) só vale para os horários
dos modelos prontos.

**(a) Regra no modelo.** `instancia_br.pares_proibidos_por_horario` (fonte única) proíbe também
(s, 2, t) quando 48 + início de t − (início de s + duração de s) < 24 h. Critério conservador:
**toda** folga isolada dá ao menos 24 h; com no máximo 6 dias seguidos, toda janela de 7 dias
tem um dia sem turno, logo há ao menos um descanso de 24 h por semana. Salto 3 não precisa: com
dois dias livres o descanso é ≥ 72 − (23 + 24) = 25 h (início ≤ 23 h, duração ≤ 24 h, limites
de `_validar_turnos`); conferido por enumeração em `testes_entrada.py`. A regra vale com ou sem
`interjornada` (o `--sem-descanso-clt` continua desligando só as 11 h), como o limite de 6 dias.
O id do padrão de salto 2 continua `clt_36h_…` (nome histórico; trocar mudaria os XML).

**(b) Segunda proteção na ferramenta.** Se `cumpre()` reprovar a escala achada, ela não é
entregue: veredito "não decidido", sem escala nem planilha, a busca do menor quadro para ali
(a escala não conta como viável e o quadro não foi provado inviável), e a tela mostra em
vermelho "A escala encontrada não cumpre a conferência de descanso (art. 67): <medida>. Não use
esta escala." O artigo entre parênteses acompanha o que reprovou (art. 66 ou 59-A para o
intervalo entre turnos, art. 67 para o semanal e os dias seguidos). Com (a), não deve
acontecer; teste 16 de `testes_ferramenta.py` (escala montada à mão que reprova).

**Efeito nos números: nenhum.** Os modelos prontos (12×36, 8 h em três turnos, 6 h + noturno
12 h), os regimes do caminho por pacientes e todo caso da bateria e dos testes com horários
próprios dão no mínimo 24 h na folga isolada: nenhum par novo. Conferido byte a byte: os 544
XML da grade dos experimentos e os 96 XML do caminho por turnos (bateria P e K, demonstração,
casos de diagnóstico, os três modelos), antes × depois, idênticos. Controle positivo: o XML do
caso 23–07 + 05–13 muda (ganha o padrão N, folga, M).

---

## 2026-10-14 — Função objetivo por níveis escolhidos pelo gestor (opção B)

**Status: vigente — MUDANÇA DE FORMULAÇÃO da função objetivo da ferramenta. Implementação:
pendente** (bloco seguinte da Orientação). Aprovada pelo Prof. Ormeu em 14/10/2026, 19h58
(mensagem e áudio do Otávio); registrada em 19/10 a pedido da Orientação.

**Decisão.** O gestor classifica cada critério — pedidos de folga, enfermeiro em posto de
técnico e as suaves do INRC — em **Essencial / Importante / Desejável / Não considerar**. A
otimização é **lexicográfica entre níveis**; dentro do nível, **peso 1 por violação**; empate =
mesmo nível. **Padrão = a ferramenta atual**: pedidos de folga Essencial; enfermeiro em posto de
técnico Importante; demais Não considerar. O equilíbrio de carga (etapa 2) continua como último
passo fixo, depois dos níveis.

**Motivo** (Otávio, 14/10, 18h; texto em `D:\TCC\escrita\RETORNO_ORMEU_14-10.md`, seção
"Justificativa da opção B"). Peso é informação de **quantidade** ("um pedido negado vale 7 fins
de semana incompletos"), que ninguém sabe justificar — nem o INRC, cujos pesos variam por
instância (todas as suaves com peso 1 em `sprint01` e `long01`; de 3 a 10 em `medium_late05` (restrições dos contratos atribuídos; padrões e pedidos com peso 1 —
precisão de 26/10)).
A descrição oficial da competição (`docs/nrpcompetition_description.pdf`, seção 2.2) chama a
divisão entre duras e suaves de "rather arbitrary" e diz que unidades diferentes dão pesos
diferentes. Ordem é informação de **prioridade** ("o pedido importa mais que o fim de semana
completo"), que o gestor responde com segurança; a otimização por níveis usa só essa
informação. **Custo declarado:** sem compensação entre níveis (é o significado de
"Essencial"); compensação possível dentro do nível (empate).

**Relação com o que existe.** A ferramenta já é um caso particular: a etapa 1 combina pedidos
(peso W) e enfermeiro em posto de técnico (peso 1) com W maior que o máximo possível da segunda
parcela ("2026-09-29 — Redesenho da ferramenta", item Objetivo; `ferramenta.pesos`). A opção B
generaliza essa ordem fixa para uma ordem escolhida. Nada é superado enquanto não for
implementada; depois, a entrada de 29/09 passa a descrever o caso padrão.

**Teste obrigatório da implementação:** com a classificação padrão, XML, números e textos
idênticos aos da `v1.2.3`.

Diagnóstico para a implementação (como a etapa 1 combina hoje os critérios, gap do HiGHS, os 13
critérios, limites superiores, orçamento): `resultados/relatorio_2026-10-19.md`, item 3.

---

## 2026-10-19 — Limitações declaradas: domingo no art. 67 e escala do art. 386

**Status: vigente.** Pendentes desde 13/10; registradas em 19/10 a pedido da Orientação. Fontes:
"2026-10-13 — Art. 67 com horários editáveis" (acima) e, só leitura, o fichamento da CLT da
Redação (`D:\TCC\escrita\fontes\fichamentos\Camada 7 - Contexto Brasileiro e Hospitalar\clt.md`,
CLT-003 e CLT-004) e `D:\TCC\escrita\REUNIAO_ORMEU_14-10.md`, item 5.

**(a) Domingo no art. 67.** O art. 67 assegura 24 h consecutivas de descanso semanal que,
"salvo motivo de conveniência pública ou necessidade imperiosa do serviço, deverá coincidir
com o domingo, no todo ou em parte" (CLT-003). A ferramenta garante as 24 h (toda folga isolada
≥ 24 h e no máximo 6 dias seguidos, entrada de 13/10) e as mede no relógio, mas **não impõe que
o descanso caia no domingo**, nem com que frequência.

**(b) Art. 386.** "Havendo trabalho aos domingos, será organizada uma escala de revezamento
quinzenal, que favoreça o repouso dominical" (CLT-004; o artigo está no capítulo da proteção do
trabalho da mulher). A ferramenta **não recebe o sexo dos profissionais** (decisão do trabalho)
e **não impõe essa escala**.

**Contorno pelo gestor, e do que ele depende.** O gestor pode pedir folga no domingo para quem
precisar, como pedido de folga. Isso é **forma de uso, não cumprimento da lei**: o pedido é
critério flexível. Hoje ele tem prioridade sobre enfermeiro em posto de técnico (peso W), mas
pode ser negado quando a cobertura e as regras de descanso não o comportam. **Com a opção B, o
contorno depende da classificação**: com pedidos em Essencial (o padrão), só perdem para as
regras rígidas; em nível mais baixo, podem perder também para os critérios dos níveis acima;
em "Não considerar", o contorno deixa de existir.

**O que falta registrar (não inventado aqui):** se o domingo e o art. 386 vão como trabalho
futuro (o fichamento CLT-004 sugere a 6.3, "como hipótese"); a frequência mínima de domingos
livres que a jurisprudência ou norma aplicável exigiria para o art. 67 (não pesquisada); e se a
jurisprudência sobre o art. 386 (o fichamento cita o RE 1.403.904 do STF) entra no texto — o
fichamento proíbe citá-la sem o acórdão lido.

---

## 2026-10-19 — Opção B: mecanismo, tempo e critérios expostos

**Status: vigente — MUDANÇA DE FORMULAÇÃO** (complementa "2026-10-14 — Função objetivo por
níveis escolhidos pelo gestor (opção B)"). Decisões da Orientação sobre o
`resultados/relatorio_2026-10-19.md`, seção 3, aprovadas pelo Otávio em 19/10 (2º bloco).

**(a) Mecanismo.** Níveis resolvidos **em sequência**, cada nível com o valor do anterior preso
como restrição (o mesmo mecanismo da etapa 2). **Regra de fusão:** níveis vizinhos são
resolvidos juntos por coeficiente (W = máximo do bloco de baixo + 1) somente se o objetivo
máximo do bloco fundido for **< 10.000** (condição de "2026-10-09 — Condição das afirmações de
ótimo provado"); caso contrário, resolução separada. Máximos por nível: as fórmulas do censo de
19/10 (relatório, 3d). Motivo: com pesos escalonados em 3 níveis o coeficiente chega a ~1,36
milhão e o gap padrão deixa de provar os níveis de baixo. Com a classificação padrão (pedidos ≤
6 × 286 + enfermeiro em posto de técnico ≤ 285 = 2.001), a fusão reproduz o caminho atual.

*(22/10: o limite por resolução foi revisto — ver "2026-10-22 — Divisão proporcional do tempo
máximo"; o texto abaixo fica como registro.)*
**(b) Tempo.** Orçamento por clique **60 min** (campo na tela, em minutos). Limite por
resolução: **1.800 s em cada nível da etapa 1 e 1.800 s na etapa 2**, sempre min(limite, o que
resta). Motivo: P17, o K5 melhorou a etapa 2 aos ~29 min com 1.800 s (`NUMEROS_TCC.md`, seção
13). A bateria, a demonstração e os números atuais continuam válidos, declarados "orçamento 20
min, 600 s / 180 s"; não rodam de novo.

**(c) Critérios na tela** (numeração de Santos et al.):
- **expostos:** 1 mínimo de turnos; 2 mínimo de dias seguidos; 3 máximo e mínimo de folgas
  seguidas; 4 máximo e mínimo de fins de semana seguidos; 5 fins de semana em 4 semanas; 6 fim
  de semana completo; 7 mesmo turno no fim de semana; 8 noturno antes de fim de semana livre;
  9 duas folgas após noites; e os que já existem (pedido de folga no dia; enfermeiro em posto de
  técnico);
- **"já garantido pela CLT"**, na tabela, sem campo de preferência: máximo de dias seguidos;
  máximo de turnos; sequências indesejadas. Preferência mais apertada = trabalho futuro (exige
  família própria no modelo); *(REVISADO em 21/10 para o máximo de dias seguidos e o máximo de
  turnos por "2026-10-21 — Máximo de dias seguidos e máximo de turnos também como preferência";
  sequências indesejadas continuam só rígidas)*
- **fora:** habilidade alternativa (contradiz a habilidade rígida); pedidos por turno e pedidos
  para trabalhar (trabalho futuro, mantida "2026-10-09 — Pedido por turno vira trabalho
  futuro");
- **sem conferência externa** (ⓘ na ajuda): fins de semana em 4 semanas; duas folgas após
  noites; noturno antes de fim de semana livre (o avaliador não a pontua).

**Decisões de implementação (Claude Code, 19/10; não óbvias, registradas antes de
implementar):**
1. **Peso dentro do bloco = coeficiente do nível.** Cada família considerada entra no contrato
   (ou nos pedidos, ou no custo por atribuição) com peso igual ao coeficiente do seu nível no
   bloco; num bloco de um nível só, peso 1. Assim a função objetivo do bloco é a soma das
   parcelas das suas famílias, e o modelo (`modelo.py`) não muda. Famílias não consideradas
   ficam como hoje no contrato (desligadas), para o XML da instância não mudar com o padrão.
2. **Máximo de "enfermeiro em posto de técnico"** = total de postos de técnico do horizonte, e
   de "pedido de folga" = número de pedidos — os mesmos da `ferramenta.pesos` de hoje (é o que
   faz W = 286 na demonstração).
3. **Nível resolvido sem prova:** o nível seguinte prende "≤ valor achado" (como a P14) e parte
   da escala achada (como a P17). A escala é "sem prova" se algum nível não provou; o gap
   mostrado é o do primeiro nível sem prova.
4. **Situação, calculada antes de resolver** *(SUBSTITUÍDA em 19/10 por "2026-10-19 — Tela orientada ao usuário": a coluna sai da tela)*:
   - "a CLT prevalece": o limite pedido vai além do que a lei permite no regime — mínimo de dias
     seguidos acima do máximo de dias seguidos que as regras de descanso admitem (1 no 12×36, 6
     nos demais); mínimo de turnos acima do teto legal de turnos do contrato. O critério continua
     valendo; a escala sai legal e a preferência fica sem atender onde a lei impede;
   - "nunca será atendido neste regime": fim de semana completo e mesmo turno no fim de semana
     quando ninguém pode trabalhar dois dias seguidos (12×36) e o fim de semana tem demanda — quem
     trabalha no fim de semana trabalha um dia só e viola;
   - "já garantido pela CLT": as três linhas sem campo;
   - "ok": os demais.
   *Leitura do pedido da Orientação ("limite mais frouxo que a lei"):* com as três famílias
   legais sem campo, nenhum limite exposto pode ser "mais frouxo" que a lei; a situação "a CLT
   prevalece" ficou para o limite que **contradiz** a lei. Levar à Orientação.
5. **Limite padrão de cada critério com parâmetro**, quando o gestor o liga: os valores do
   contrato 0 do `medium_late05` (mínimo de turnos 10; mínimo de dias seguidos 3; máximo de
   folgas seguidas 4; mínimo de folgas seguidas 3; máximo de fins de semana seguidos 3; mínimo 2).
   Fins de semana em 4 semanas: 2 (nenhuma instância do INRC liga; valor de exemplo, sem fonte).
   O gestor edita.
6. **Resultado por critério:** contado na escala final, fora do modelo, por `avaliacao.py`
   (excesso por família) e, para o noturno antes de fim de semana livre, que o `avaliacao.py` não
   pontua, por `solucao.noites_antes_de_fim_de_semana_livre`; enfermeiro em posto de técnico e
   pedidos, pela contagem que a tela já usa (`ferramenta.indicadores`).
7. **Os testes da tela rodam com os limites da v1.2.3** (600 s / 180 s / 20 min): verificam
   comportamento, não limite. Um teste confere os padrões novos (1.800 s, 1.800 s, 60 min) e que
   o campo da tela chega ao `verificar`.

**Defeito do teste 1-2, corrigido com autorização do Otávio (19/10).** Na suíte de fechamento
da v1.3.0, o caso 1-2 falhou só no item "planilha abre": ele exigia as abas `["Escala",
"Resumo", "Legenda"]`, e a planilha trouxe `['Escala', 'Resumo', 'Legenda', 'Prioridades']`.
Causa: o teste é anterior à opção B, que acrescenta a aba "Prioridades" — acréscimo previsto
no esperado registrado e commitado antes de implementar (`resultados/opcao_b_2026-10-19/
ESPERADO.md`, linha 37: "as abas Escala, Resumo e Legenda não mudam; entra a aba
'Prioridades'"). A ferramenta estava certa; o teste ficou desatualizado. Correção: a
conferência, que era conjunta (abas **e** `max_row` da aba Escala = 41), foi separada em duas
— abas == `["Escala", "Resumo", "Legenda", "Prioridades"]` e `wb["Escala"].max_row == 41` —,
porque com a condição conjunta não se sabia se a segunda parte tinha passado. Nada mais mudou
no teste nem na ferramenta.

---

## 2026-10-19 — Pedidos e regras por profissional; revisa 2026-10-09 (Pedido por turno vira trabalho futuro)

**Status: vigente — MUDANÇA DE FORMULAÇÃO** (extensão da opção B). Decisão do Otávio, 19/10,
validada pela Orientação; registrada antes de implementar (20/10).

**Por quê.** Hospitais brasileiros costumam ter equipes fixas por turno (caso Massens 2019:
equipes de manhã, tarde e noite fixas) e profissionais com pedidos de dia e de turno. A
ferramenta precisa distinguir **regra do hospital** de **desejo do profissional**.

**O que muda.**
- Uma tabela "Pedidos e regras dos profissionais": Profissional | Dia (em branco = todos os
  dias) | Turno (em branco = o dia todo) | Tipo ∈ {Folga, Só este turno} | Importância ∈
  {Essencial, Importante, Desejável}. Linha sem dia e sem turno é inválida.
- **A importância fica na linha, não no critério:** o mesmo tipo pode ser regra do hospital
  (Essencial) ou desejo do profissional (Desejável); quem distingue é o gestor. Padrão de linha
  nova: Folga com dia e sem turno → Essencial (= v1.3.0); as demais → Desejável.
- **Tradução, sempre para pedidos negativos já validados** (`DayOffRequest` / `ShiftOffRequest`
  do INRC):
  - Folga + dia → folga no dia;
  - Folga + dia + turno → folga naquele turno daquele dia;
  - Folga + turno → folga naquele turno em todos os dias;
  - Só este turno (+ dia opcional) → folga em todos os outros turnos no(s) dia(s); várias linhas
    "Só este turno" da mesma pessoa e dia se somam (Manhã e D12 = pode Manhã ou D12).
- **Função objetivo:** cada linha pertence ao nível da sua Importância. Violação =
  profissional-dia-turno trabalhado contra a linha; para folga no dia, a unidade que o motor já
  usa (profissional-dia trabalhado), para preservar a identidade. Se várias linhas proíbem o
  mesmo profissional-dia-turno, conta **uma** violação, no nível mais alto entre elas. Peso 1 por
  violação dentro do nível. Entra no plano de níveis e na regra de fusão como os critérios
  existentes; o máximo de violações de cada nível vem das linhas da tabela.
- **Em Essencial nada é rígido:** a tela informa quantos pedidos foram descumpridos e de quem.
  Cobertura e CLT continuam rígidas.
- A tabela de Prioridades deixa de ter a linha "Pedido de folga no dia" (a importância é coluna
  da tabela de pedidos). No grupo 1 ("Pedidos e qualificação") ficam a tabela de pedidos e a
  linha "Enfermeiro em posto de técnico".
- Sem linhas na tabela, nada muda (nível vazio não gera resolução).

**Teste opB-tela atualizado com autorização prévia do pedido (20/10)**, como no precedente do
teste 1-2: com a linha "Pedido de folga no dia" fora da tabela de Prioridades, o grupo 1 passa
de "2 de 2" para "1 de 1 considerados", a conferência da importância padrão deixa de incluir
`pedido_folga` (não há mais campo), e o aviso de mesmo nível é provocado pondo "mínimo de folgas
seguidas" em Importante (antes, o pedido de folga em Importante). Acrescentada a conferência de
que a tabela "Pedidos e regras dos profissionais" aparece no grupo 1. O texto de resultado não
mudou. O critério `pedido_folga` continua no back end (caminho antigo, `Entrada.pedidos`) e na
linha "Pedido de folga no dia" do resultado por critério, que fica 0 quando só há a tabela nova.

**Motivo da revisão de 09/10.** (i) A tolerância do solver deixou de ser problema: com os níveis
em sequência (opção B), a prioridade entre níveis vem da sequência, não de pesos escalonados, e
só se fundem níveis cujo bloco fica abaixo de 10.000; (ii) o motor já suporta
`folga_turno`, validado pelas quatro instâncias da regressão (50 ou 245 pedidos de turno cada).
A entrada "2026-10-09 — Pedido por turno vira trabalho futuro" fica marcada como revista.

---

## 2026-10-20 — a posteriori: fundamento das 36 h para qualquer plantão de 12 h ou mais

**Status: vigente. Registro A POSTERIORI — justificativa nova, não era o motivo registrado em
29/09.** Pedido da Orientação, 20/10 (tarde). Sem mudança de código.

**Justificativa (do Otávio).** O art. 59 da CLT limita a jornada diária a 8 h, mais até 2 h
extras. O art. 59-A admite 12 h seguidas como **exceção**, por acordo individual escrito ou
convenção/acordo coletivo, e vincula essa exceção a 36 h ininterruptas de descanso. Logo, um
turno de 12 h ou mais só cabe dentro do desenho do art. 59-A, e a regra da ferramenta — 36 h
depois de todo turno com duração ≥ 12 h, sem olhar se o turno é noturno nem se o regime da
unidade é 12×36 — segue esse desenho. É a leitura que sustenta a decisão de manter as 36 h no
produto ("2026-10-20 — a posteriori: descanso depois do D12 como parâmetro de pesquisa").

**Declarações.**
- (a) É **justificativa nova**: o registro de 29/09 ("Redesenho da ferramenta") cita o art. 59-A
  mas não discute o plantão de 12 h avulso; este texto não reescreve o motivo daquela data.
- (b) A **convenção coletiva** do hospital do caso **não foi lida**. Ela pode prever outro arranjo
  (compensação, banco de horas); a ferramenta não a conhece.
- (c) O texto **nunca afirma que o hospital descumpre a lei**. A frase admitida é: "a regra, como
  modelada, segue o art. 59-A". A sensibilidade com D12 = 11 h continua rotulada como hipótese,
  não regra da ferramenta.

**Nota de 26/10 (correção de citação; raciocínio e código não mudam):** o limite de 8 h diárias é
do art. 58 da CLT (CLT-005); o art. 59 admite o acréscimo de até 2 h extras (CLT-006), conferidos
no Planalto em 26/10. O texto de 20/10 fica como está.

---

## 2026-10-20 — Piso por pares de dias (v1.4.1)

**Status: vigente.** Pedido da Orientação, 20/10 (tarde, Parte 7). Esperado em
`resultados/piso_pares_2026-10-20/ESPERADO.md` (`946e38c`), código em `0b1defe`.

**Decisão.** O piso da ferramenta (`ferramenta.piso`, que decide quais quadros vão ao solver)
ganha uma condição necessária: em cada par de dias seguidos, postos do segundo dia + postos do
primeiro em turnos que **bloqueiam o segundo inteiro** ≤ pessoas disponíveis em ao menos um dos
dois (férias descontadas); também só com enfermeiros (técnico não cobre posto de enfermeiro:
habilidade rígida). "Bloqueia" sai dos pares do gerador (`pares_proibidos_por_horario`), nunca
de "duração ≥ 12 h" fixo: acompanha horários editados e o `DESCANSO_POR_TURNO`. O diagnóstico
ganha o motivo "Dois dias seguidos" ("A conta prévia do menor quadro provou…", com o par e os
números); a "alternância" do 12×36 fica como estava.

**Por quê.** Sem ela, a conta prévia dava 18 (caso A) e 68 (caso B), e cada quadro abaixo do
mínimo gastava orçamento do solver; com ela, 30 e 105 (o B fica todo recusado pela conta até 101).

**Ressalvas.** A entrada do solver não muda (243/243 idênticos à v1.4.0). Mudam só tentativas
antes provadas pelo solver, que passam à conta (na suíte: P05, 14; demo18, 28; tela 7.3, 4). A
conta compartilha a regra de descanso com o modelo: confere a aritmética e a coerência, não a
leitura legal. Testes: `resultados/relatorio_2026-10-20c.md`, Parte 7.

---

## 2026-10-21 — Máximo de dias seguidos: a trava é só a da CLT; a regra do hospital é preferência

**Status: vigente — mudança de ENTRADA e TELA, não de formulação** (revisa "2026-10-19 — Máximo de
dias seguidos como regra do hospital (rígida)"). Pedido do Otávio, 21/10; registrada antes de
implementar. Versão v1.4.3.

**Decisão.** O máximo de dias seguidos rígido passa a ser **só o da lei**: 6 (art. 67; no 12×36, a
regra das 36 h já impede dois dias seguidos). O campo rígido do hospital (v1.4.0) sai da tela e da
`Entrada`. A vontade do hospital entra pela preferência de dias seguidos (v1.4.2), critério
classificável, com o limite do campo preso ao legal.

**Por quê (Otávio, 21/10).** Em toda a ferramenta a vontade do hospital é critério classificável:
na tabela de pedidos, regra do hospital = Essencial, que não é rígido. O campo rígido do hospital
era a única exceção. Regra da ferramenta: **duro = lei ou físico** (cobertura, CLT, horas do
contrato, férias); **tudo o que o hospital quer é critério classificável**. Quem quiser que a regra
do hospital pese quase como trava põe a preferência de dias seguidos no Essencial, acima de tudo o
que é Importante ou Desejável.

**O que muda e o que não muda.**
- `src/modelo.py` e `src/instancia_br.py` **intocados**. A trava continua sendo a mesma restrição
  do contrato (`max_consecutive_working_days`), agora sempre com o valor legal. `instancia_br`
  continua aceitando `max_consecutivos` de 1 a 6 (o caminho dos experimentos e testes de entrada o
  usam); só a ferramenta deixa de passar outro valor que não o 6.
- `src/ferramenta.py`: `Entrada.max_dias_seguidos` sai; `montar` passa o legal
  (`MAX_CONSECUTIVOS_GENERICO`). Com o padrão de antes (6), a entrada enviada ao solver é a mesma —
  é o que a identidade confere.
- `src/app.py`: a linha "Máximo de dias seguidos de trabalho — Obrigatória" sai; o limite máximo dos
  campos de dias seguidos (preferência e mínimo) passa a ser o legal. Ajuda da linha da preferência:
  "a lei trava em 6; a regra do seu hospital vai aqui, como preferência; no Essencial ela pesa acima
  de tudo o que é Importante ou Desejável".
- `src/prioridades.py`: **só texto** (ajuda e resumo da linha, que apontavam para "o campo acima", e
  dois comentários). `limite_usado` = min(preferência, legal) fica como está: o "legal" lido do
  contrato agora é sempre a lei.
- **Consequência:** um hospital com regra de 4 dias deixa de receber "Falta N" por causa dela. A
  escala sai com o quadro que a lei admite, e as sequências acima de 4 aparecem no "Resultado por
  critério". É a mesma lógica dos pedidos: preferência nunca torna a escala impossível.

**Suíte reduzida (v1.4.3), justificativa.** A mudança é só de entrada e tela; modelo e solver estão
intocados. A identidade (243/243 na classificação padrão e 24/24 nas entradas da fase 2, byte a
byte contra a v1.4.2) prova que o problema enviado ao solver não mudou nos casos em que o campo
estava no padrão — e nenhum teste fora do `max-dias` usava outro valor. Por isso não rodam as
rodadas a2 nem os testes da tela que não tocam no campo nem na preferência de dias: a identidade
os cobre. Rodam: identidade, regressão dos 4 ótimos, testes de entrada, piso (segurança, controle,
casos), o caso pequeno das preferências e os testes da tela que usam o campo removido ou a
preferência de dias (lista e motivo em `resultados/trava_clt_2026-10-21/ESPERADO.md`).

**Teste max-dias reescrito (registrado antes):** o caso "hospital = 4 → Falta 1; o menor quadro
viável é 15" era trava e deixa de existir. Substituem-no: (i) a preferência 4 no Essencial com 14
técnicos — escala sai com 14, violações contadas fora do modelo = resultado por critério; (ii) para
não perder a cobertura do texto "A conta prévia do menor quadro provou" (só o max-dias o testava),
o mesmo caso com 13 técnicos e a lei (6): piso pela janela de 7 dias = 14 → "Falta 1; o menor
quadro viável é 14".

---

## 2026-10-22 — Divisão proporcional do tempo máximo; resultado por nível; seção 5 enxuta

**Status: vigente — mudança de PARÂMETRO DE PROJETO (tempo) e de TELA, não de formulação**
(v1.4.3, acréscimo; revisa o item b de "2026-10-19 — Opção B: mecanismo, tempo e critérios
expostos"). Pedido do Otávio, 21–22/10; esperado registrado antes
(`resultados/trava_clt_2026-10-21/ESPERADO.md`, acréscimo de 22/10).

**Problema.** Cada resolução recebia min(1.800 s, o que resta). Com 20 min a etapa 2 podia não
rodar; com 3 níveis separados, o nível 3 e a etapa 2 ficavam sem tempo; com 120 min cada parte
seguia presa em 30 min. O campo da tela não se comportava como o gestor espera.

**Regra (parâmetro de projeto, sem calibração; sensibilidade só se o orientador pedir).**
Etapa 1 : etapa 2 = 50 : 50; dentro da etapa 1, Essencial : Importante : Desejável = 50 : 30 : 20.
Níveis fundidos num bloco somam os pesos; nível vazio não entra. No início de cada parte k:

    tempo_k = tempo que resta × peso_k ÷ (soma dos pesos das partes que ainda faltam, incluindo k)

A sobra de quem termina antes passa adiante, redividida na mesma proporção. Vale sobre o tempo
que resta em cada quadro tentado: quadros recusados pela conta prévia não gastam tempo;
tentativas sem escala gastam. **Proteção da primeira escala:** a primeira resolução do quadro
recebe a sua fatia; se ela acabar sem escala, segue com todo o tempo que resta. Os níveis
seguintes e a etapa 2 partem da escala anterior. Sem teto fixo de 1.800 s.

**Decisões de implementação (Claude Code, 22/10; não óbvias):**
1. **Leitura dos pesos com nível vazio.** A leitura literal ("nível vazio não entra", os outros
   pesos como estão) daria, no padrão fundido Essencial+Importante a 60 min, 0,40 : 0,50 → 26,7 +
   33,3 min, e não os 30 + 30 que o pedido manda conferir. Adotado: **a etapa 1 fica sempre com
   50%**, e os 50 : 30 : 20 se dividem entre os níveis presentes. Com os três níveis separados dá
   0,25 / 0,15 / 0,10 / 0,50, como no pedido; o padrão dá 30 + 30. Levado ao Otávio.
2. **Proteção = resolver de novo.** O HiGHS, pelo Pyomo, não aceita "pare no tempo t se já houver
   escala; senão continue". A proteção roda a resolução de novo com o tempo que resta,
   recomeçando do zero (sem escala não há de onde partir). Custo declarado: o tempo da fatia é
   gasto duas vezes no pior caso.
3. **`TEMPO` e `TEMPO_ETAPA2` viram teto opcional, só para os testes** (`None` no produto). Os
   testes os põem em 600 / 180 s (ou 25 s e 3 s no teste 8) para encurtar as rodadas; com teto,
   a cadeia da primeira resolução (com a proteção) também não passa dele. Chamada direta de
   `resolver_com_objetivo` sem prazo usa o teto por resolução, como antes.
4. **Resultado por nível, em vez de um gap só.** Provado: "<Nível>: N violações — a melhor
   possível."; sem prova: "… Nenhuma escala tem menos de M." (M = limite inferior do solver,
   arredondado para cima, nunca acima de N), ou "Não deu tempo de saber quanto dá para melhorar"
   se o limite for 0; não rodou: "não deu tempo de otimizar; a escala mantém o resultado dos
   níveis acima". **Bloco fundido:** o objetivo soma os níveis com coeficientes (o de cima =
   máximo do resto do bloco + 1), e o limite inferior não é contagem de violações. O M é dado só
   para o nível de cima, M = ⌈(limite − (coef − 1)) ÷ coef⌉, porque o resto do bloco vale no
   máximo coef − 1. A frase principal perde o gap ("Escala gerada; pode haver uma melhor."). As
   três frases citadas no TCC não mudam.
5. **Defeito corrigido de passagem:** em `_niveis_em_sequencia`, o resultado "provado" de cada
   bloco era guardado no nome `p`, o mesmo da classificação que `expressao_pedidos` lê no bloco
   seguinte. Com pedido sem nível (caminho antigo), linhas na tabela de pedidos e dois blocos ou
   mais, isso daria erro de tipo. Renomeado (`prova`). Nos casos que funcionavam, nada muda no que
   vai ao solver.

**Seção "5. Resultado" enxuta (só texto e arrumação):** alerta de descanso semanal em uma linha
(o texto mora em `ferramenta.alertas_descanso`; o fundamento — Súmula 110, OJ 355, 24 + 11 = 35 h,
bordas — vai para o "?"); diferença entre categorias sem número negativo ("a menos" / "a mais");
"maior sequência de trabalho na escala", "menor descanso entre turnos", "menor descanso
semanal" (medidas, não regras); legendas num painel "Detalhes da escala", fechado; "sem pedidos"
no lugar de "0 de 0"; uma frase por nível acima das linhas daquele nível na tabela "Resultado
por critério"; "Equilíbrio entre colegas: o melhor possível / pode haver uma escala mais
equilibrada".

**NUMEROS_TCC não muda:** os números foram medidos com os limites antigos, declarados no arquivo.

---

## 2026-10-23 — P20 aprovada: trava pelo valor verdadeiro depois de nível sem prova

**Status: vigente — mudança de IMPLEMENTAÇÃO do mecanismo de níveis (o modelo não muda).**
Aprovada pelo Otávio em 23/10, depois do diagnóstico "2026-10-22 — Anomalia do medium_late05
(HiGHS): folgas soltas na solução sem prova"; `PROPOSTAS.md`, P20. Registrada antes de
implementar; esperado em `resultados/p20_2026-10-23/ESPERADO.md`.

**Decisão.** Ao fechar um nível **sem prova**, a trava f_k ≤ valor usa o valor **recalculado na
escala** — as folgas e auxiliares apertadas ao mínimo que a escala exige —, e não o valor do
modelo no ponto entregue pelo solver. A escala de partida do nível seguinte vai com as folgas
recalculadas, para não violar a nova trava. Vale também para a trava da etapa 2 (penalidade ≤ z,
P14). Nível com prova: nada muda.

**Como (decisão de implementação, Claude Code):** fixar as atribuições `x` da escala, resolver de
novo só as folgas e auxiliares (o objetivo do nível continua o mesmo; `y` sai de `x` por
igualdade), soltar o `x`. É o próprio modelo que dá o mínimo — a mesma semântica, sem uma segunda
contagem que pudesse divergir. Limite do aperto: min(60 s, o que resta), no mínimo 1 s; se falhar,
fica o valor do modelo (como antes) e isso é registrado. O LP enviado na primeira resolução de cada
nível não muda — a identidade 243/243 e 24/24 tem de continuar valendo.

**Por quê.** Com folgas soltas, a trava fica frouxa e o que vem depois pode piorar a contagem
verdadeira de um nível acima — o contrário do que a opção B e a P14 prometem ("sem piorar").

**Suíte:** não roda agora (fica para sexta à noite, decisão do Otávio); rodam o teste novo e os
testes rápidos da opção B.

---

## 2026-10-23 — Caso A: classificação dos critérios pela escala real e sensibilidade (2 ordens)

**Status: vigente — DESENHO EXPERIMENTAL registrado ANTES de rodar** (Orientação, 23/10). Código
congelado na v1.4.4: nada em `src/` muda. Esperado: `resultados/caso_a_pratica_2026-10-23/
ESPERADO.md`. Script: `docs/diagnostico/caso_a_pratica.py`.

**Base.** `D:\TCC\escrita\fontes\FICHA_CASO_REALISTA.md`, seção "Contagem na escala real
(23/10/2026)" (corrigida pela Orientação em 23/10), e a transcrição célula a célula da p. 70 de
Massens (2019), `D:\TCC\escrita\fontes\transcricao_anexoB_massens.csv` (24 linhas, 26/10 a
25/11). **Regra de classificação:** violado em alguma ocorrência → Não considerar; nunca violado,
com ocorrência → Importante; sem evidência → padrão da ferramenta; Essencial só para regra
declarada na fonte (turno fixo). **Limites = os padrões da ferramenta, não calibrados ao
hospital.** A contagem é sobre a escala do hospital no formato do INRC; não afirma descumprimento
de lei.

**Recontagem independente** (`caso_a_pratica.py --recontar`; `recontagem.md`): lê o CSV com as
leituras da ficha e conta cada critério com o `avaliacao.py` (o noturno na véspera, com o contador
da ferramenta, que o `avaliacao.py` não pontua), sem reaproveitar o script do chat. Calendário: a
transcrição não marca o fim de semana; os P das linhas diurnas só fecham com 27/10 num sábado
(2018; 02/11 sexta e 15/11 quinta são as duas colunas sombreadas fora do fim de semana) — o script
confere. **Resultado, com a leitura C abaixo: os 13 critérios contáveis ficam do mesmo lado da
ficha.**

**Leitura da borda — a posteriori, 23/10 (leitura C).** Ressalva: formulada **depois** de a
recontagem expor a divergência entre a regra escrita na ficha (tirar todo bloco de borda) e a
contagem da ficha (que, nos fins de semana, contou os blocos de borda). Motivo, independente do
resultado:
- **borda do mês:** nos critérios de **máximo**, o bloco conta (se já passa do limite dentro do mês,
  a violação é certa, qualquer que seja o resto); nos de **mínimo**, sai (pode continuar fora da
  imagem);
- **férias:** o bloco que toca as férias **sai sempre** (o fim das férias não se lê na imagem; o
  branco de 21 a 25/11 do 5976 pode ser continuação). Isso descarta a leitura B.

As três leituras e o que cada uma dava (com o `avaliacao.py`):

| Leitura | Máx. fins de semana seguidos | Máx. folgas seguidas | Reproduz a ficha? |
|---|---|---|---|
| A — tirar todo bloco que toca a borda do mês ou as férias (a regra antes escrita na ficha) | nunca violado | nunca violado | não |
| B — nos de máximo, contar os blocos de borda e os que tocam as férias; nos de mínimo, tirar | violado (26, em 14 pessoas) | violado (1: o 5976, 21 a 25/11, logo depois das férias) | não |
| **C** — nos de máximo, contar o bloco de borda do mês; nos de mínimo, tirar; o que toca as férias, sempre tirar | violado | nunca violado | sim |

**"Mesmo turno no fim de semana":** vale a semântica do `avaliacao.py`/avaliador oficial (trabalhar
um só dia do fim de semana já viola: 93 violações, 21 pessoas). A ficha foi corrigida pela
Orientação (dizia "sem ocorrência"). Classificação: Não considerar, agora por evidência.

**Linhas contadas — a posteriori, 26/10** (Orientação). Na contagem da escala real (a evidência para
classificar os critérios) entram **só as linhas do Anexo B com pelo menos um registro: 21 de 24**.
Ficam fora as três linhas sem nenhum registro: **6118 e 4798** (enfermeiros diurnos) e **6089**
(integral). Motivo: linha vazia não mostra prática; pela leitura "dia útil em branco = trabalho", ela
viraria trabalho em todo dia útil, e o vazio no fim de semana só seria folga por suposição. Apoio: no
Apêndice A de Massens (escala recriada pelo algoritmo do autor), o enfermeiro diurno faz plantão de
supervisão em alguns fins de semana (fichamento MAS-014, `D:\TCC\escrita\fontes\fichamentos\Camada 7
...\massens.md`). **A entrada do caso não muda:** o caso continua com 24 pessoas, e as rodadas de 21
e 24/10 continuam valendo. A Orientação conferiu à mão que os três critérios nunca violados (máx.
folgas seguidas 4, mín. fins de semana seguidos 2, mín. turnos 10) continuam nunca violados sem as
três linhas; recontagem com as 21 linhas em `recontagem.md` (a de 24 linhas fica como histórico).
Se algum critério mudasse de lado, a regra era parar e levar à Orientação.

**As duas ordens:**
- **Ordem 1 (a prática):** Essencial = as linhas "Só este turno" da A36_fixo (29 linhas); Importante =
  máx. folgas seguidas (4), mín. fins de semana seguidos (2), mín. turnos (10) e enfermeiro em posto
  de técnico; todo o resto, Não considerar (pedido de folga: não há pedidos).
- **Ordem 2:** máx. fins de semana seguidos (3) no Essencial; as linhas "Só este turno" no
  Desejável; o resto igual à ordem 1.

**Rodadas (3):**
1. A11_fixo com 24 (4 enfermeiros + 20 técnicos), **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA
   FERRAMENTA** (`DESCANSO_POR_TURNO = {"D12": 11}`), ordem 1;
2. A36_fixo com 30 — 10 enfermeiros (os 4 da unidade: 6118, 4798, 4969 e 5993, mais 6 acrescidos
   pela regra `equipe`, Enf 5 a Enf 10) + 20 técnicos, a composição que a busca achou em 21/10
   (informada direto; conferido sem solver que a instância é a mesma que a busca montou) —, ordem 1;
3. A36_fixo com 30, ordem 2.

**Regras:** orçamento padrão de 60 min por rodada (regra de tempo da v1.4.3, com a P20); uma rodada
por processo; ≥ 3 GB livres antes de cada uma (registrado); suspensão do Windows desativada; na
ordem acima, a A11 primeiro e até o fim (regra de 03/10); retomada pula o que já tem resultado. Se
a noite der problema, a ordem 2 é a primeira a sair. Os resultados separam os 4 enfermeiros da
unidade dos 6 acrescidos.

**Conferência:** avaliador oficial nas três escalas (restrição dura). Por critério, a contagem da
ferramenta comparada com o avaliador oficial numa instância com os critérios da ordem ligados e
peso 1, onde o avaliador pontua; onde não pontua (enfermeiro em posto de técnico), "sem conferência
externa". Máx. fins de semana seguidos nas **duas** escalas do A36, avaliado com o avaliador numa
instância com o critério ligado (a ordem 1 não o tem ligado).

**Números** só vão ao `NUMEROS_TCC.md` depois da aprovação do Otávio. **Afirmação fraca:** um setor,
um mês, uma rodada por ordem; tempo como limite operacional (máquina e solver nomeados).

---

## 2026-10-26 — Limitações declaradas: duração diária do turno e limite semanal de horas

**Status: vigente — declaração, sem mudança de código** (Orientação, 26/10).

**O que a v1.4.4 aceita.** Turnos com início de 0 a 23 h e duração de 1 a 24 h, em hora cheia
(validação dos turnos em `instancia_br.py`, `_validar_turnos`; duração por `ferramenta.duracao`).
Carga contratual de 30, 36, 40 ou 44 h por semana (`instancia_br.CARGAS_CONTRATUAIS`), com o teto
sobre o horizonte, não por semana ("2026-10-02 — Carga por contrato", item b, motivo registrado lá:
o 12×36 tem semanas de 48 h compensadas por semanas de 36 h).

**O que não é verificado:**
- a **duração máxima diária do turno** (CLT, arts. 58, 59 e 59-A): um turno de 1 a 24 h é aceito;
- um **limite semanal de horas**.

Para a duração do turno **não há motivo registrado**; é **limitação declarada a posteriori**. Para
o limite semanal, o motivo é o do item b de 02/10.

**Frase admitida no texto:** "A ferramenta não verifica a duração máxima diária do turno, que aceita
de 1 a 24 h, nem um limite semanal de horas; a carga contratual é limitada no horizonte de 28 dias."

---

## 2026-10-30 — Etapa 2 por min-max (v1.4.5)

**Status: vigente — MUDANÇA DE FORMULAÇÃO (só a etapa 2)**

Pedido do Prof. Ormeu em 30/10/2026; aprovado pelo Otávio em 30/10/2026; validado pela Orientação.

**Motivo:** a soma das amplitudes não controla como a amplitude se divide entre as categorias (13 + 1 empata com 7 + 7). O min-max força a escolha equilibrada: 7 + 7 é melhor que 13 + 1 ou 14 + 0, porque max(7, 7) = 7 < max(13, 1) = 13 e < max(14, 0) = 14. Referência: Guéret, Prins e Sevaux, *Applications of optimization with Xpress-MP*, seção 2.10.1, "Minimax objective functions".

**Mudança técnica:**
1. Adiciona variável real `t ≥ 0` no modelo da etapa 2.
2. Para cada categoria presente (enfermeiros, técnicos): `t ≥ φmax_g − φmin_g`.
3. Objetivo da etapa 2: `min t` (substitui `min Σ_g (φmax_g − φmin_g)`).
4. Sem critério de desempate: escalas com a mesma maior amplitude empatam — 7 + 0 e 7 + 7 valem 7 (limitação declarada).

**Onde a SOMA das amplitudes decide algo, passa a valer a MAIOR das duas:**
- Escolha entre a escala da etapa 1 e a da etapa 2 quando não há prova (P17): antes `amplitude_etapa2 < soma_etapa1`, agora `max_amplitude_etapa2 < max_amplitude_etapa1`.
- Estado que gera a frase do equilíbrio na tela: mesma mudança.
- As exibições **por categoria** (diferença entre colegas, horas não utilizadas, planilha) **não mudam**. O teste 9c, com min-max, confere a maior amplitude (4,55 pp dos técnicos), e a amplitude dos enfermeiros pode subir de 0 sem custo — não é exigido que fique em 0.

**Não muda:** etapa 1, restrições duras e suaves, divisão do tempo, conferência de descanso, diagnóstico, limite inferior do quadro, caminho do INRC (regressão), textos da tela fora da frase do equilíbrio.

**Suíte:** identidade v1.4.4 × v1.4.5 (XML e LP etapa 1 idênticos; LP etapa 2 diferente só no objetivo e linhas de `t`), regressão (56, 58, 197, 219 idênticos), testes de entrada, testes da ferramenta que passam pela etapa 2 (9, 9c, 9c-tela, 9d, p20, 8, 12, opB-*, pref-tela se existirem) e conferidores (p14, p17) se rodarem.

*Nota de 30/10/2026 (Otávio, com a Orientação), registrada antes de mudar a conferência:* o item 3
do `docs/diagnostico/p14_conferir.py` passa a ser **"a maior amplitude da fração cumprida (critério
da etapa 2) é ≤ a da escala da etapa 1"**. Antes era "diferença máxima de carga entre colegas, em
cada categoria, ≤ a da escala da etapa 1". Motivo: o min-max garante só a maior; a categoria
menor pode subir (limitação já declarada no item 4 acima), e nem a soma garantia o item 3 por
categoria. O p14 continua fora da suíte, porque os casos dependem do tempo; o caminho sem prova
fica coberto pelos testes 8 e 9c-tela.
