# Validação por restrição nos 4 ótimos — ESPERADO (registrado antes de rodar, 19/10/2026)

Pedido do orientador (14/10): não basta o valor bater; mostrar que a escala cumpre as
restrições. Sem solver: só leitura das escalas salvas e das saídas do avaliador oficial já
versionadas (v1.2.1), mais contas.

## Fontes

| Instância | Escala | Saída do avaliador | Tabela 6 |
|---|---|---|---|
| sprint01 | `resultados/sprint01_completo.xml` | `resultados/sprint01_completo_avaliador.txt` | 56 |
| sprint02 | `resultados/sprint02_completo.xml` | `resultados/sprint02_completo_avaliador.txt` | 58 |
| long01 | `resultados/long01_completo.xml` | `resultados/long01_completo_avaliador.txt` | 197 |
| long02 | `resultados/long02_completo.xml` | `resultados/long02_completo_avaliador.txt` | 219 |

## Conferências e valor esperado

0. **A saída do avaliador é desta escala.** A grade "Schedule" impressa pelo avaliador,
   célula a célula, é a escala do XML. Esperado: idêntica nas 4.
1. **Duras = 0.**
   - avaliador: nenhuma linha "Hard constraints violation" nem "Error!" (o avaliador só checa
     cobertura: "Coverage exceeded" e "Not all shifts are assigned"). Esperado: 0 nas 4.
   - um turno por profissional por dia, contado direto no XML da escala (sem o parser do
     projeto). Esperado: 0 nas 4.
   - `solucao.conferir_rigidas` (código do projeto). Esperado: 0 nas 4.
   - restrições do modelo Pyomo com x fixado na escala (cobertura, um turno por dia e as
     auxiliares). Esperado: 0 violadas nas 4.
2. **Penalidade por tipo de restrição, avaliador × modelo.** Soma por tipo = **56, 58, 197,
   219**; diferença avaliador × modelo = **0 em todas as linhas**. Também × `avaliacao.py`:
   diferença 0.
3. **A mesma conferência por profissional** (e por profissional × tipo). Diferença = **0 em
   todas as linhas**.

## O que cada coluna é (declarado antes)

- **Avaliador**: o avaliador oficial da competição (Java, `avaliador/evaluator.jar`), lido das
  saídas salvas. Árbitro externo: não compartilha código nem premissa com o projeto.
- **Modelo**: as expressões do próprio modelo Pyomo (`m.parcela[família]`,
  `m.pena_familia[n, família]`), avaliadas com x fixado na escala e as auxiliares no menor
  valor admissível (o que a minimização escolhe). **É o mesmo código que gera o valor da
  função objetivo** — esta coluna não é conferência independente do modelo; a independência
  está toda na coluna do avaliador.
- **avaliacao.py**: a semântica em Python puro. Compartilha a premissa de interpretação com o
  modelo (o modelo lineariza o `avaliacao.py`); por isso não conta como conferência do modelo,
  só como terceira coluna.
- **Mapa rótulo do avaliador → família do modelo**: escrito à mão no script. É premissa do
  script; um rótulo sem mapa faz o script falhar, não passar.
