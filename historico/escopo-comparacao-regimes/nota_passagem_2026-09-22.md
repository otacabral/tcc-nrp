# Nota de passagem — 22/09/2026

> **CORRIGIDA em 22/09, mais tarde.** A seção "O padrão se repetiu nas duas instâncias longas"
> afirma que `long01` e `long02` têm *"pedidos e cobertura diferentes"*, e conclui daí que a
> exposição é propriedade da pessoa. **As duas afirmações estão erradas:** as duas instâncias
> são idênticas em demanda, pedidos, profissionais, habilidades e turnos — só os contratos
> mudam. A correlação de 0,89 não é replicação. Ver
> `docs/nota_conferencias_contrato_2026-09-22.md`, seção 0, e a P11.

Consolida cinco rodadas do projeto de códigos que ainda não chegaram ao projeto de redação.
Cobre da chegada do Parecer COFEN até os primeiros resultados do Experimento B.

Cada item aponta onde está o registro completo. Esta nota é índice, não substituto.

---

## 1. Decisões registradas no `DECISOES.md`

**21/09 — Instância brasileira: parâmetros do Parecer Normativo COFEN nº 1/2024.**
Porte de 5.920 horas-profissional em 28 dias (= 211,43 h/dia, o mesmo invariante da P4);
perfil uniforme nas 24 h, dando 8,81 profissionais presentes em qualquer hora; carga semanal
de 42 h nos dois regimes; QP_ref = 35,24. Composição por categoria aplicada ao **quadro**, não
à cobertura da janela. A proporção profissional/paciente por turno **não é usada** — era da
Resolução 543/2017, revogada.

*Para o texto:* manter o porte fixo em todos os graus significa que a unidade representada
muda de tamanho — 52,9 pacientes no grau mínimo contra 11,7 no intensivo. O número nunca entra
no modelo, mas precisa estar declarado.

*Correção de enquadramento, feita nesta rodada:* o piso aritmético de 36 profissionais nos
dois regimes **não é resultado** — sai por construção, porque a carga semanal foi igualada.
A forma correta para a metodologia está na entrada.

**21/09 — Definição de viável, e limites legais como rígidos.**
> Viável = satisfaz a cobertura e todos os limites legais de jornada e descanso. As demais
> restrições flexíveis entram apenas na penalidade, objeto do Experimento B.

Implementado pela flag `rigidas_legais` no `modelo.py`. O XML emitido continua sendo instância
normal do INRC: a rigidez é opção de quem resolve, não propriedade do arquivo, e uma escala que
respeita os limites tem violação zero neles no avaliador oficial.

Descanso conferido por enumeração de todas as sequências que o contrato admite: **36 h** no
12×36 (exatamente o art. 59-A), **16 h** de interjornada e **24 h** de descanso semanal no de
8 h. As duas regras valem, e valem justas.

Achado que motivou a correção: `MaxConsecutiveWorkingDays = 1` **não bastava** no 12×36 — o
plantão noturno termina às 07:00 do dia seguinte e o diurno de dois dias depois começa às
07:00, dando 24 h e não 36. Corrigido por um padrão indesejado. *Consequência a observar na
análise:* a proibição tende a separar a equipe em turmas fixas de dia e de noite.

**21/09 — Experimento B: núcleo no INRC, e o que entra na penalidade comparada.**
Regra de restrição estrutural em três degraus; família de fins de semana **não** ligada; núcleo
do experimento migrado para as quatro instâncias do INRC com ótimo provado.

Verificação feita antes de qualquer otimização: a penalidade decompõe **exatamente** por
profissional (soma = Z\* nas quatro instâncias) e cada parcela individual bate com o avaliador
oficial nos 118 profissionais. **Todo número que o Experimento B reportar tem conferência
externa.**

**22/09 — Medida de dispersão: penalidade individual máxima.**
Com o total fixado em Z\*, reportar o **intervalo** que `max_n p_n` pode assumir entre as
escalas ótimas. Minimax no lado do mínimo; uma resolução por profissional no lado do máximo
(forma B), guardando o máximo de cada um.

*Argumento que vale para o capítulo de formulação:* fixar a soma em Z\* já garante que a escala
é ótima **e** que cada `p_n` é a penalidade real da pessoa. Cada folga é variável contínua
limitada por baixo pelo excesso que representa; exigir que a soma dê exatamente Z\* força a
escala a ser ótima (senão a soma dos limites passaria do mínimo) e cada folga a valer
exatamente o seu limite.

---

## 2. Resultados medidos

**As quatro instâncias fecharam.**

| Instância | Z\* | N | Média Z\*/N | Mín | Máx | Concentração inevitável | Margem de gestão | Tempo |
|---|---|---|---|---|---|---|---|---|
| `sprint01` | 56 | 10 | 5,60 | 7 | 18 | 1,2× | 2,6× | 6 min |
| `sprint02` | 58 | 10 | 5,80 | 7 | 18 | 1,2× | 2,6× | 5 min |
| `long01` | 197 | 49 | 4,02 | 11 | 19 | 2,7× | 1,7× | 69 min |
| `long02` | 219 | 49 | 4,47 | 14 | 20 | **3,1×** | **1,4×** | 193 min |

O tempo do `long02` é o de parede **menos 36.036 s de suspensão da máquina** — a tampa do
notebook foi fechada no meio da rodada. **Uma das 51 resoluções ficou sem tempo medido**, e a
ressalva está na coluna `observacao` do resumo. Os valores calculados não são afetados: a
suspensão congela o processo, não corrompe conta.

Perfil por profissional em `resultados/experimento_b.csv`; resumo em
`resultados/experimento_b_resumo.csv`.

**Desfecho: largo.** O critério de penalidade total **não determina** a distribuição entre
pessoas. Escolher entre escalas ótimas é decisão de gestão que o modelo não toma sozinho.

**No lote early todos os pesos valem 1**, então penalidade é **contagem de violações**. A frase
do texto fica concreta: *no `sprint01`, entre todas as escalas de custo mínimo, o profissional
mais sobrecarregado sofre de 7 a 18 violações; a escolha entre elas não altera o custo total,
mas muda em mais de duas vezes a carga de quem sai pior.*

### Correção: a leitura relativa estava com o denominador errado

A versão anterior desta nota dividia a amplitude por Z\* — 20% nas sprints, 4% no `long01` — e
concluía que quanto maior a instância, mais determinada fica a distribuição. **Está errado.**
Dividir pelo total encolhe mecanicamente quando N cresce: com 49 pessoas a fatia de qualquer
uma sobre o total é necessariamente menor que com 10. A queda era aritmética, não propriedade
do problema. **O percentual sobre Z\* sai do texto.**

O denominador certo é a média por profissional, Z\*/N — o que cada um receberia numa divisão
perfeitamente igual. Conferido:

| Instância | Média Z\*/N | Concentração inevitável | Margem de gestão |
|---|---|---|---|
| `sprint01` | 5,60 | 1,2× a média | 2,6× |
| `sprint02` | 5,80 | 1,2× a média | 2,6× |
| `long01` | 4,02 | **2,7× a média** | 1,7× |

São **duas grandezas distintas**, e o texto precisa das duas:

- **concentração inevitável** = mínimo do máximo ÷ média. Quanto a pessoa mais sobrecarregada
  carrega mesmo na escala ótima **mais equilibrada**. Nenhuma escolha evita.
- **margem de gestão** = máximo do máximo ÷ mínimo do máximo. Quanto a escolha entre escalas
  ótimas muda a carga de quem sai pior. É o espaço de decisão que o custo total deixa.

Na escala certa a leitura inverte: no `long01` há **menos** margem de escolha (1,7× contra
2,6×) e **mais** concentração que nenhuma escolha evita (2,7× contra 1,2×). Nem "mais
determinada" nem "menos" — são coisas diferentes, e a frase anterior juntava as duas.

**A generalização por tamanho sai do texto.** São três instâncias, e `sprint` e `long` diferem
em muito mais que o número de profissionais — contratos, habilidades, pedidos. Não dá para
atribuir a diferença ao tamanho.

*Isto responde a decisão 2: reportar em violações e em múltiplos da média.* As duas razões já
saem calculadas no `experimento_b_resumo.csv`.

### O padrão se repetiu nas duas instâncias longas, e tem explicação

`long01` e `long02` têm **os mesmos 49 profissionais** — mesmos contratos, mesmas habilidades —
com pedidos e cobertura diferentes. Os perfis de máximo das duas têm **correlação 0,89**, e
5 dos 8 menores e 6 dos 8 maiores são as mesmas pessoas. A exposição de cada um a ser
sobrecarregado não é sorteio da instância: é propriedade da pessoa.

**A explicação é o contrato, e é mecânica:**

| Contrato | Teto de atribuições | Pessoas | Máximo médio (`long01`) | Faixa |
|---|---|---|---|---|
| `fulltime` | 16 | 25 | **6,2** | 0–11 |
| `75_time` | 12 | 10 | 9,3 | 5–14 |
| `50_percent` | 5 | 14 | **15,8** | 9–19 |

**Quanto menor o teto de jornada, maior a penalidade que a escolha entre escalas ótimas pode
impor à pessoa.** Faz sentido: a cobertura tem de ser coberta por alguém, e empurrar um
contrato parcial para mais um turno estoura o teto dele imediatamente. O integral absorve dez
turnos extras antes de violar o mesmo limite.

*Para o texto, com cuidado:* a afirmação defensável é mecânica — teto menor, violação mais
fácil. Não extrapolar para poder de barganha ou vulnerabilidade contratual sem outra evidência.

### O profissional 28: explicação encontrada, e ele deixa de ser o caso

No `long01` o máximo dele é zero, o que é invariância *provada*: máximo zero e penalidade
nunca negativa implicam zero em toda escala ótima. **No `long02` o máximo dele é 1** — ou seja,
o zero exato era da instância, não da pessoa.

O que sobrevive, e é melhor: ele é um `fulltime`, o contrato de maior teto, e fica no extremo
baixo da faixa desse contrato (0–11) nas duas instâncias. **A frase para o texto é sobre a
tabela de contratos acima, não sobre ele.** O caso individual vira ilustração, não achado.

**Cuidado ao escrever:** a coluna de máximos **não pode ser somada**. Dá 469 contra Z\* = 197
no `long01` e 345 contra 219 no `long02` — cada máximo vem de uma escala ótima diferente.

**Sobre tamanho de instância, a ressalva continua valendo.** As duas sprints concordam entre si
(1,2× e 2,6×) e as duas longas concordam entre si (2,7–3,1× e 1,4–1,7×), mas `sprint` e `long`
diferem em contratos, habilidades e pedidos, não só no número de pessoas. O que se pode afirmar
é que o padrão é **consistente dentro de cada track**, não que decorre do tamanho.

---

## 3. Propostas — todas validadas; o que resta é redação

**Nenhuma proposta está aguardando validação.** Os três status que estavam parados no
`PROPOSTAS.md` foram corrigidos em 22/09: **P5** dissolvida (não bloqueia mais nada; o que
sobra é achado de metodologia), **P6** validada, **P7.4** resolvida.

**P6 — o que falta é só do lado do texto.** Com o perfil contínuo como primitivo, a instância
brasileira deixa de ser derivada do benchmark e passa a ser construída a partir da norma, com o
`long01` só como referência de porte — 5.920 h. Pendente: reescrita do específico 2,
reformulação do gap ("construir instância a partir de parâmetros normativos calibrada a um
benchmark", não "reparametrizar um benchmark") e menção na delimitação 1.4 de que a instância é
sintética.

**P7.4 — as duas reclassificações, para o capítulo de método.**
`complete_weekends` e `identical_shift_types_during_weekend` são **estruturais** e saem da
penalidade comparada. A conta do primeiro: sob 12×36 ninguém pode trabalhar sábado e domingo,
então todo profissional que trabalha um dia de fim de semana viola a restrição — 144 de
penalidade inevitável só no braço do 12×36, com o efetivo inteiro violando toda semana.

Aplicado o critério corrigido, sobra só a família de pedidos de folga — e a família de fins de
semana está **desligada** nos três contratos do `long01`, logo não há peso a herdar. Foi essa
constatação que levou o núcleo do Experimento B para as instâncias do INRC, onde a penalidade
é a do próprio benchmark e não precisa ser inventada.

---

## 4. As duas conferências pedidas, feitas em 22/09

**Os perfis das duas sprints são diferentes.** Não rodou nada duas vezes. Os dois perfis
divergem em **6 dos 10 profissionais**, e a soma de cada um bate com o seu próprio Z\* — 56 e
58. A coincidência nos três números agregados é real: mesma composição de contratos (4+2+2+2) e
exatamente 15 pedidos por profissional nas duas.

**O zero do profissional 28 NÃO é trivial.** A hipótese era que ele tivesse contrato quase sem
restrições e nenhum pedido. É o contrário:

| | profissional 28 |
|---|---|
| contrato | 0, `fulltime` — o mais restrito, **9 restrições ativas** |
| pedidos ativos | **15**, exatamente a média e o mínimo da instância (todos os 49 têm 15) |
| habilidades | `Nurse`, como a maioria |

Ele tem a mesma exposição que os outros 24 do contrato 0. A explicação trivial está descartada.

**Mas ainda não há explicação positiva, e por isso ele não deve ir para o texto ainda.**
Procurei no perfil de pedidos: o profissional 0 é o gêmeo estatístico dele — mesmo contrato,
mesmos 10 pedidos de dia e 5 de turno, mesmos 2 pedidos em fim de semana, mesma carga média nos
dias pedidos (27,8) — e tem máximo **8**, não 0. A diferença tem de estar nas datas específicas
e na interação com os pedidos dos demais, o que a estatística agregada não mostra.

Ele também não é isolado: há uma cauda de máximos muito baixos (0, 2, 3, 3) contra um teto de
19. A pergunta certa talvez não seja "por que o 28 é zero" e sim "o que caracteriza a cauda".

---

## 5. O que precisa de decisão

1. **Intervalo por pessoa — RESPONDIDA em 22/09, e implementada.** Recomendação aceita: sim nas
   sprints (minutos), no `long01` só com a máquina livre. A flag `--por-pessoa` já existe no
   `experimentos.py` e acrescenta a coluna `pena_minima_entre_otimos`. Falta rodar.
2. ~~Reportar amplitude absoluta ou relativa~~ — **respondida**: violações e múltiplos da média;
   o percentual sobre Z\* sai. Ver a correção na seção 2.
3. ~~P6 e P7.4~~ — **validadas em 21/09**; os status no `PROPOSTAS.md` foram atualizados, junto
   com o da P5, que estava dizendo "aguardando validação" e "bloqueia a instância brasileira"
   quando já tinha sido dissolvida.

---

## 6. Erros meus declarados nestas rodadas

- **Datas no futuro.** Entradas do P3 estavam datadas 22/09 quando ainda era 18/09. Corrigidas
  em todos os arquivos.
- **Enquadramento do piso 36.** Eu havia registrado como pré-resultado; é controle de desenho,
  sai por construção. Corrigido.
- **Sobrescrita do CSV.** A opção `--alvo` que eu acrescentei escrevia por cima em vez de
  mesclar, e rodar o `long01` apagou as duas sprints do arquivo. Corrigido, e as linhas foram
  restauradas a partir da cópia lida antes da sobrescrita — são os mesmos números que a máquina
  imprimiu. Sem a correção, o `long02` teria apagado os 69 minutos do `long01`.
- **Leitura apressada do perfil.** Eu falei em "profissionais sem margem" olhando quem tem
  máximo igual ao valor na escala minimax. Isso só mostra que aquela escala põe a pessoa no teto
  dela; o piso pessoal pode ser mais baixo. Apenas o profissional 28 tem invariância demonstrada.
- **Denominador da leitura relativa.** Dividi a amplitude por Z\* e concluí que instâncias
  maiores são mais determinadas. O denominador encolhe sozinho quando N cresce; a conclusão era
  artefato aritmético. Corrigido na seção 2, e na escala certa a leitura inverte.
- **Três status parados no `PROPOSTAS.md`.** P5, P6 e P7.4 continuavam como "aguardando
  validação" depois de decididas. Corrigidos.
- **Estimativa da forma A.** Prometi minutos; passou de 9 sem terminar. Contei as resoluções e
  esqueci de pensar na dificuldade de cada uma — uma conta com 49 variáveis de escolha pode ser
  pior que 49 contas simples. A conta continua correta, só não é rápida.

---

## 7. Código novo

| Arquivo | Papel |
|---|---|
| `src/instancia_br.py` | perfil assistencial contínuo → `Instancia` → XML oficial validado |
| `src/regressao.py` | confere os 4 alvos em 4 dimensões; portão de toda alteração no modelo |
| `src/experimentos.py` | Experimento B: intervalo da penalidade individual máxima |
| `docs/medicao_sobreposicao.py` | evidência da P5 revisão 3, sobreposição nas 69 instâncias |

`modelo.py` ganhou a flag `rigidas_legais` e a expressão `m.pena[n]`, a penalidade decomposta
por profissional ao lado da decomposição por família.

Quatro instâncias brasileiras emitidas e válidas no esquema oficial, em `instancias/br/`.
