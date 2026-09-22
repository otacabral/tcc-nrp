# Nota para o projeto de redação — o piso forçado, declarado

**22/09/2026.** As duas declarações pedidas antes de o piso forçado virar texto. **As duas
passam**, e a primeira passou de um jeito melhor do que eu esperava: quem responde é o
avaliador oficial, não o meu código.

Reprodução: `python docs\conferencia_piso_forcado.py`. Saídas cruas do avaliador em
`resultados/conferencia_piso/`.

---

## Declaração 1 — a violação de teto é contada por atribuição excedente

**Confirmada, diretamente pelo avaliador oficial.** Não precisou de teste construído: ele
imprime `excess` e `cost` em campos separados, por profissional. Nas escalas ótimas que já
temos gravadas:

```
Maximum number of assignments: excess = 13 , pos = 111, cost = 13
```

`cost = excess` em **todas** as linhas das quatro instâncias, com excessos de até 13. Se
fosse binária por profissional em violação, o custo seria 1 em todas elas. É por atribuição.

*(Registro de método: a primeira tentativa montava escalas artificiais com `teto + k` dias
para ver o custo crescer. Não funciona — o avaliador aborta antes de calcular as flexíveis
quando a cobertura não fecha. O caminho certo era ler o que ele já imprime.)*

## Declaração 2 — `MaxNumAssignments` ativo em todos os contratos das quinze

**Confirmada.** Contrato a contrato, com a regra de ativação do projeto (ligada **e** peso
> 0):

| | contratos | com teto ativo | pessoas sem teto |
|---|---|---|---|
| 10 `sprint_early` | 4 cada | 4 cada | 0 |
| 5 `long_early` | 3 cada | 3 cada | 0 |

Nenhum profissional das quinze instâncias está num contrato sem teto. E os **pesos**: o
conjunto de pesos distintos de `MaxNumAssignments` no lote inteiro é `{1}`. Isso importa
tanto quanto a ativação — é o peso 1 que faz cada atribuição excedente valer exatamente uma
unidade de penalidade e permite somar excessos e custos na mesma moeda. Se algum peso fosse
diferente, o piso passaria a ser `Σ peso × excesso` e a tabela de E/Z\* teria de ser refeita.

## O que apareceu junto, e é mais forte que as duas

A conferência incluía uma verificação da própria desigualdade: a soma dos excessos que o
avaliador reporta nas escalas ótimas tem de ser **≥ D − C**. O resultado:

| | soma dos excessos (avaliador) | D − C | profissionais abaixo do próprio teto |
|---|---|---|---|
| `sprint01` | 30 | 30 | **0** |
| `sprint02` | 32 | 32 | **0** |
| `long01` | 150 | 150 | **0** |
| `long02` | 160 | 160 | **0** |

Não é só `≥`: é **igualdade exata nas quatro**. E a igualdade só acontece numa condição, que
conferi direto na escala contando atribuições: **ninguém trabalha menos que o próprio teto**.

A frase que isso autoriza, e vale a pena escrever com esse cuidado: *no ótimo, o teto de
jornada deixa de funcionar como teto e passa a funcionar como piso.* Todo profissional
trabalha pelo menos o seu limite contratual, e o excedente forçado se distribui por cima
disso.

**O que é invariante e o que não é.** Invariante: qualquer escala em que alguém trabalhe
abaixo do próprio teto paga **estritamente mais** que `D − C` nessa família — isso é
aritmética, vale para toda escala viável. Não invariante: que o ótimo de fato tenha todo
mundo no teto ou acima. Isso é propriedade das quatro escalas ótimas que temos, medida, não
demonstrada. O texto pode afirmar a primeira como teorema de uma linha e a segunda como
observação nas quatro instâncias — não as duas no mesmo tom.

## Conclusão

O piso forçado está declarado e pode virar texto:

| | D | soma dos tetos | excesso forçado | Z\* | E/Z\* |
|---|---|---|---|---|---|
| 10 `sprint_early` | 152 | 118 a 124 | 28 a 34 | 51 a 59 | **54% a 61%** |
| 5 `long_early` | 740 | 510 a 590 | 150 a 230 | 197 a 303 | **73% a 81%** |

Com as ressalvas que já estavam: as faixas são estreitas porque a demanda é a mesma dentro do
track, são 10 e 5 pontos, e nada disso se estende a `late` ou `hidden` sem conferir.
