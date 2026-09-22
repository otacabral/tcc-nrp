# Nota para o projeto de redação — as três conferências do achado do contrato

**22/09/2026.** Resposta às três conferências pedidas. Duas estão fechadas, e a terceira não
foi feita porque, como está pedida, ela não é bem posta — está registrada como **P10** no
`PROPOSTAS.md`, aguardando validação.

**Antes das três, uma correção que muda a leitura do que mandei ontem.** Ela nasceu da
conferência 2: ao ir atrás da correlação de 0,89, achei o motivo dela, e o motivo desmonta a
frase que eu tinha escrito.

Tudo aqui sai de `docs/conferencia_contratos.py`, que lê as instâncias e o
`resultados/experimento_b.csv` já medido. Não resolve nada: é aritmética sobre o que já
existe, reproduzível em dois segundos.

---

## 0. Correção — `long01` e `long02` são a mesma instância com contratos diferentes

Eu escrevi na nota de ontem que as duas longas têm *"os mesmos 49 profissionais, com pedidos
e cobertura diferentes"*, e concluí que a correlação de 0,89 mostra que **a exposição é
propriedade da pessoa, não sorteio da instância**.

A segunda metade da frase está errada, e a conclusão cai junto. Comparei os dois arquivos
campo a campo:

| | `sprint01` x `sprint02` | `long01` x `long02` |
|---|---|---|
| habilidades, turnos, padrões | idênticos | idênticos |
| profissionais e seus contratos | idênticos | idênticos |
| **demanda de cobertura** | **idêntica** | **idêntica** |
| **pedidos individuais** | **idênticos** | **idênticos** |
| horizonte | idêntico | idêntico |
| parâmetros dos contratos | 6 diferenças | 11 diferenças |

**São idênticos em 8 de 8 campos.** A única coisa que muda dentro de cada par são os
parâmetros dos contratos. Não são duas realizações independentes do mesmo hospital: são o
mesmo hospital, o mesmo mês, os mesmos pedidos, com outra regra de contrato.

Então **0,89 não é replicação**. Duas medidas sobre o mesmo cenário têm de concordar; o
espanto seria se não concordassem. Retiro a frase "a exposição é propriedade da pessoa".

**O que entra no lugar é melhor.** O par vira um experimento controlado sobre regra de
contrato, com tudo o mais fixo — e regra de contrato é exatamente o objeto do trabalho,
enquanto "sorteio de instância" não era:

| | `long01` | `long02` | o que mudou |
|---|---|---|---|
| dias consecutivos, teto | 7 / 5 / 5 | **4 / 4 / 4** | apertou nos três contratos |
| piso de atribuições | 6 / 6 / 3 | **8 / 6 / 4** | subiu em dois |
| teto de atribuições | 16 / 12 / 5 | 16 / **11** / 5 | apertou no `75_time` |
| **Z\*** | 197 | **219** | +11% |
| **concentração inevitável** | 2,74× | **3,13×** | +14% |
| **margem de gestão** | 1,73× | **1,43×** | −17% |

A leitura: **apertar a regra de contrato, com a mesma demanda e os mesmos pedidos, aumenta o
custo total, aumenta a concentração inevitável e reduz a margem de gestão ao mesmo tempo.**
Mais penalidade, pior distribuída, e com menos espaço para escolher como distribuir. As três
se movem juntas e na direção ruim.

O par `sprint01`/`sprint02` tem o mesmo desenho e mexe menos: 6 diferenças em vez de 11, e as
medidas quase não se movem (Z\* 56 → 58; concentração 1,25 → 1,21; margem 2,57 → 2,57). Isso
é coerente — mudança pequena, efeito pequeno —, mas com dois pares não dá para afirmar
dose-resposta. É uma direção, não uma curva.

**E não são dois pares: são duas séries.** Fui conferir o lote *early* inteiro, e no nível do
XML bruto — hash de cada bloco, sem passar pelo `parser.py`, para a conferência não depender
do meu próprio código:

| bloco do XML | 10 `sprint_early` | 5 `long_early` |
|---|---|---|
| `<CoverRequirements>` | 1 versão | 1 versão |
| `<DayOffRequests>`, `<ShiftOffRequests>` | 1 versão | 1 versão |
| `<Employees>`, `<ShiftTypes>`, `<Skills>` | 1 versão | 1 versão |
| **`<Contracts>`** | **10 versões** | **5 versões** |

**O lote *early* não é um conjunto de 15 cenários. São dois cenários — um por track — com 10
e 5 variações de regra de contrato.** Todas com ótimo provado na Tabela 6 (LB = UB, gap 0).

Isso é um fato sobre o *benchmark*, não sobre o nosso modelo, e vale como observação
metodológica por si só: resultados médios sobre o lote *early* não são médias sobre cenários
independentes.

**Cuidado de escrita:** dois pares não são amostra, e cinco pontos também não são. A
afirmação segura hoje é sobre o par das longas, nomeando o que mudou. O que a série permite é
propor um desenho — está na **P11**.

---

## 1. Conferência 2 — correlação dentro de cada grupo de contrato

Feita. Os números:

| Contrato | Teto | n | Máx. médio `long01` | Máx. médio `long02` | **r intragrupo** |
|---|---|---|---|---|---|
| `fulltime` | 16 | 25 | 6,20 | 3,48 | 0,533 |
| `75_time` | 12 / 11 | 10 | 9,30 | 6,80 | 0,812 |
| `50_percent` | 5 | 14 | 15,79 | 13,57 | 0,574 |
| global | | 49 | | | 0,892 |

Correlação dos desvios em torno da média do próprio contrato: **r = 0,551**. Variância do
máximo explicada só pelo contrato: **R² = 0,714** no `long01` e **0,835** no `long02`.

**Resposta: o contrato explica a maior parte, mas não tudo, e o que sobra é estrutural.**
Tirado o contrato, ainda restam 0,55 de correlação entre as duas instâncias. Como a demanda
e os pedidos são idênticos (seção 0), esse resíduo não pode vir de sorteio — vem de algum
atributo estável da pessoa dentro do contrato dela.

**Achei qual, e é o segundo eixo:** a habilidade. Nas longas o turno `DH` exige `HeadNurse`,
há 48 turnos `DH` no mês e apenas 6 pessoas habilitadas — 8 por pessoa, enquanto a média
geral é de 15,1 turnos por pessoa no mês. Dentro do mesmo contrato:

| Contrato | HeadNurse (n=2) | demais | HeadNurse (n=2) | demais |
|---|---|---|---|---|
| | *`long01`* | | *`long02`* | |
| `fulltime` (teto 16) | 5,50 | 6,26 | 3,50 | 3,48 |
| `75_time` (teto 12/11) | 11,50 | 8,75 | 7,00 | 6,75 |
| `50_percent` (teto 5) | **19,00** | 15,25 | **18,50** | 12,75 |

O efeito só aparece onde o teto é baixo, e é grande lá: quem acumula habilidade escassa **e**
contrato parcial é o mais exposto dos dois lados. Os dois maiores máximos das duas instâncias
são os profissionais 4 e 5 — `50_percent` e `HeadNurse`. No `fulltime` o efeito some, porque
sobra teto para absorver os `DH` sem violar nada.

**Para o texto:** a exposição tem dois eixos, contrato e habilidade, e eles se multiplicam em
vez de somar. Habilidade escassa sozinha não expõe (veja o `fulltime`); teto baixo sozinho
expõe; os dois juntos expõem mais que a soma. Isso é mais forte do que a tabela de contratos
sozinha, e a evidência é a mesma medição — não custou resolução nova.

---

## 2. Conferência 3 — contratos das sprints

Feita. A hipótese era: a diferença de concentração entre sprints (1,2×) e longas (2,7× e
3,1×) vem de heterogeneidade de contrato, não de tamanho.

| | N | contratos | tetos | amplitude | teto mais baixo |
|---|---|---|---|---|---|
| `sprint01` | 10 | 4 | 16, 12, 9, 8 | 2,0× | 8 (29% do horizonte) |
| `sprint02` | 10 | 4 | 16, 12, 8, 8 | 2,0× | 8 |
| `long01` | 49 | 3 | 16, 12, 5 | **3,2×** | **5 (18%), com 14 das 49 pessoas** |
| `long02` | 49 | 3 | 16, 11, 5 | **3,2×** | 5 |

**Resposta: a hipótese vai na direção certa, mas "heterogeneidade" não é a palavra exata.**
As sprints têm *mais* contratos distintos (4 contra 3). O que as longas têm é uma **cauda
baixa**: um contrato de teto 5 com 29% das pessoas dentro. Nas sprints o contrato mais
apertado é 8 de 28 dias e pega 20% das pessoas. A conta que importa é onde está o piso, e
quanta gente está nele — não quantos contratos existem.

E as duas coisas continuam confundidas, porque `sprint` e `long` diferem em pessoas, demanda,
habilidades e contratos ao mesmo tempo. O que dá para afirmar é o que a tabela mostra, sem
atribuir causa ao tamanho nem à contagem de contratos.

---

## 3. Conferência 1 — não fiz, e explico

O pedido foi aplicar a decomposição por família às escalas de máximo, com a regra: dominada
por excesso de atribuições → afirmação encolhe; espalhada → achado mais geral.

**O problema:** a resolução que maximiza `p_n` fixa o total em Z\* e maximiza a *soma* das
parcelas da pessoa. Não fixa de que famílias essa soma é feita. Entre as escalas ótimas em
que `p_n` vale 19, umas podem ter 19 de excesso de jornada e outras 10 de excesso e 9 de dias
consecutivos. O solver devolve uma, e a escolha é desempate — a mesma coisa que o Experimento
B foi desenhado para não reportar, repetida um nível abaixo. E há motivo para achar que o
caso não é degenerado: **nas quatro instâncias todo peso vale 1**, então trocar uma violação
de uma família por uma de outra custa exatamente o mesmo, e o solver é indiferente.

Raciocínio completo e a alternativa em **P10**, no `PROPOSTAS.md`. Em resumo: perguntar em
forma de intervalo (mínimo e máximo da parcela de uma família, sujeito a total = Z\* **e**
`p_n` = máximo conhecido), e só para quem detém o máximo. São 8 a 12 resoluções, dezenas de
minutos.

**Uma parte da conferência 1, no entanto, se responde sem resolver nada — e essa parte é
sólida.** A cobertura entra como igualdade, então o total de atribuições de qualquer escala
viável é exatamente a demanda `D`. Se `D` passa da soma dos tetos `C`, os `D − C` excedentes
existem em **toda** escala viável, e como o peso é 1 isso é piso para Z\*:

| | D | soma dos tetos | excesso forçado | Z\* | **piso/Z\*** |
|---|---|---|---|---|---|
| `sprint01` | 152 | 122 | 30 | 56 | **54%** |
| `sprint02` | 152 | 120 | 32 | 58 | **55%** |
| `long01` | 740 | 590 | 150 | 197 | **76%** |
| `long02` | 740 | 580 | 160 | 219 | **73%** |

**No total, a resposta à conferência 1 é sim: a penalidade é dominada por excesso de
atribuição — por aritmética, não por propriedade do ótimo.** Três quartos de Z\* nas longas
já estão decididos antes de qualquer escala existir. Isso é forte e é grátis: não depende de
solver, de versão nem de semente.

E o piso não vale só nas quatro. Aplicado ao lote *early* inteiro, contra a Tabela 6:

| track | instâncias | excesso forçado E | Z\* (Tabela 6) | **E/Z\*** |
|---|---|---|---|---|
| `sprint_early` | 10 | 28 a 34 | 51 a 59 | **54% a 61%** |
| `long_early` | 5 | 150 a 230 | 197 a 303 | **73% a 81%** |

Quinze instâncias, ótimo provado em todas, e a fração forçada fica numa faixa estreita dentro
de cada track. O número da esquerda sai de uma subtração sobre o arquivo; o da direita custou
o estado da arte de 2016. **Cuidado:** são 10 e 5 pontos, as faixas são estreitas porque a
demanda é a mesma dentro do track, e isso não se estende a `late` ou `hidden` sem conferir.

**O que esse piso não explica é a concentração.** Aplicando o mesmo raciocínio ao máximo
individual — o menor `t` tal que a demanda ainda caiba se ninguém passar de `teto + t` — dá 3,
4, 4 e 4 nas quatro instâncias, contra máximos mínimos medidos de 7, 7, 11 e 14. O teto
sozinho explica menos da metade. **O resto vem do acoplamento**: empurrar alguém para além do
teto também estoura dias consecutivos, fins de semana e padrões. É por isso que a composição
por família interessa, e é por isso que vale a pena fazê-la bem posta em vez de rápido.

---

## 4. O que mudou no código

- `modelo.py`: `m.pena_familia[n, f]` — a decomposição cruzada (profissional × família), ao
  lado das duas que já existiam. Não entra em restrição nem no objetivo; é leitura depois de
  resolver, e sai de graça das mesmas resoluções.
- `regressao.py`: mais uma conferência — a grade tem de fechar nos dois sentidos,
  `Σ_f pena_familia[n,f] = pena[n]` e `Σ_n pena_familia[n,f] = parcela[f]`. Se fechar só num,
  alguma parcela foi contada no profissional errado.
- `experimentos.py`: grava `resultados/experimento_b_composicao.csv` com a coluna `escala`
  (`minimax` ou `maximo_proprio`), para que fique explícito que é leitura de uma escala e não
  propriedade do conjunto. **Nenhuma resolução nova.**
- `docs/conferencia_contratos.py`: tudo desta nota, sem Pyomo.

Nada disso muda o modelo nem os resultados já medidos. A regressão dos quatro alvos precisa
passar antes de qualquer rodada nova — é o portão de sempre.

---

## 5. O que peço de decisão

1. **P10** — medir a composição em forma de intervalo (8 a 12 resoluções) ou aceitar a
   leitura de uma escala testemunha, com o texto dizendo que é isso?
2. **A correção da seção 0 precisa entrar antes de qualquer frase sobre replicação.** Se algum
   capítulo já usa "a exposição é propriedade da pessoa", tem de sair.
3. **P11 — rodar o Experimento B na série `long_early` inteira** (faltam `long03`, `long04`
   e `long05`), transformando a tabela da seção 0 em resultado com cinco pontos em vez de
   dois. Custo estimado: 6 a 10 horas de máquina, em rodadas separadas. É desenho
   experimental novo — não faço sem validação.

Nas três, o que eu recomendaria: **2 é correção e entra já; 1 e 3 podem esperar** o
Experimento A, que é o resultado central e ainda não rodou.
