# Nota para o projeto de redação — o Experimento A fechou

**23/09/2026.** O Experimento A rodou nas vinte células e está **fechado dos dois lados**.
Este é o resultado do objetivo geral, e ele é negativo. Vale a pena ler até o fim antes de
decidir o que fazer com isso, porque a explicação mecânica é mais interessante que o número.

Reprodução: `python src\experimento_a.py --todos`. Saída em `resultados/experimento_a.csv`,
escalas e relatórios do avaliador em `resultados/experimento_a/`.

---

## 1. O resultado

Vinte células: 5 graus de dependência × 2 regimes × 2 regras de reagregação. Em **todas**:

| | |
|---|---|
| efetivo 35 | **inviável, com inviabilidade provada pelo solver** |
| efetivo 36 | **viável, com escala exibida** |
| conferência no avaliador oficial | **`ok` nas vinte** — zero violação nas três famílias que aqui são rígidas |
| intervalo | **[36, 36]** |
| distância ao piso de capacidade | **0,0%** |

Não é "36 basta": é **36 é o mínimo**, demonstrado nos dois sentidos. A sonda em 35 serve a
duas coisas ao mesmo tempo — fecha o intervalo por baixo e testa o modelo contra a aritmética
de capacidade. Se 35 tivesse dado viável, o modelo estaria errado, não o regime.

## 2. Por que dá zero — e por que isso é resultado, não ausência de resultado

Os dois regimes entregam **a mesma capacidade por pessoa em horas**, porque o teto legal é o
mesmo:

| regime | plantões em 28 dias | duração | horas | por semana |
|---|---|---|---|---|
| 12x36 | 14 | 12 h | 168 | **42 h** |
| 8 h | 21 | 8 h | 168 | **42 h** |

5.920 h ÷ 168 h = **35,24 pessoas**, que é exatamente o `QP_ref` do Parecer COFEN. O mínimo
viável é o teto disso: 36.

A frase para o texto não é "a distância é zero". É esta:

> **O que determina o efetivo é o teto de 42 h semanais, igual nos dois regimes por lei. As
> regras de descanso da CLT não chegam a apertar: em nenhum dos dois regimes elas forçam
> alguém a trabalhar menos que o teto de horas.**

E isso não era óbvio antes de medir, principalmente no 12x36, onde as 36 h de descanso após o
plantão noturno poderiam ter forçado dias ociosos. Não forçaram: a alternância um-sim-um-não
dá exatamente 14 plantões em 28 dias — exatamente o teto — e satisfaz o descanso por
construção. No de 8 h, 21 dias de trabalho e 7 de folga sobram para o descanso semanal.

Dito de outro jeito: **o modelo reproduz o QP do Parecer e demonstra que as regras de
descanso não acrescentam nada a ele.** Isso é uma validação do dimensionamento normativo por
um caminho independente do que o Parecer usou, e é defensável como resultado.

## 3. As ressalvas, e uma delas encolheu

**Uniformidade da demanda.** Nas células `teto` a demanda é rigorosamente uniforme e a
capacidade iguala a demanda exatamente — a instância pede um empacotamento perfeito, e existe
um. É o caso mais fácil possível.

**Mas as células `maior_resto` não são uniformes** (7 e 8 profissionais alternando conforme o
dia) e têm folga de 11 plantões, e dão o mesmo 36. É teste fraco de robustez, porque a
não-uniformidade é pequena, mas não é nulo. A ressalva que escrevi ontem era maior do que
devia.

**A uniformidade não é descuido.** O Parecer não fornece curva horária, e o perfil contínuo
virou primitiva do gerador justamente para não inventar repartição — é a decisão da P5, que
custou três revisões. Inventar um pico diurno para fazer a distância aparecer seria reabrir
aquilo pela porta dos fundos.

**O que o experimento não diz nada sobre:** qualidade da distribuição. Dois regimes com o
mesmo efetivo podem tratar as pessoas de maneiras muito diferentes. Isso é o Experimento B.

## 4. Um achado sobre o modelo, não sobre o regime

O 12x36 é **muito mais caro de resolver**: mediana de 23,9 s de CPU contra 5,0 s no de 8 h,
com pico de 59,9 s. Mesma pergunta, mesma resposta, cinco vezes a busca. A alternância rígida
corta o espaço de solução de um jeito que o solver sente.

Cabe numa frase do capítulo de método, e é honesto: o custo computacional dos dois regimes é
assimétrico mesmo quando a resposta não é.

## 5. O que precisa de decisão

Está na **P12**, com o raciocínio completo. Em resumo:

1. **Aceitar o zero como resultado negativo**, com a ressalva da uniformidade declarada em
   voz alta, e escrever a seção 2 acima como o achado. É o que eu recomendaria.
2. **Para onde vai a comparação entre regimes**, já que A responde "não muda o efetivo". A
   candidata natural é rodar o **Experimento B na instância brasileira**, efetivo fixo em 36,
   comparando a distribuição da penalidade entre os dois regimes. É exatamente o desenho que
   vocês pediram ao recusar a P11 — um parâmetro por vez, na instância brasileira — mas
   contraria a decisão de 21/09, que restringiu o B ao INRC porque a pergunta não dependia de
   regime. Agora depende, por um motivo que não existia então: **A voltou nulo.**

Não implementei a segunda. É mudança de escopo e precisa passar por vocês.
