# Mapa do código — o que é cada arquivo e o que serve à ferramenta

**28/09/2026.** Escrito depois da virada de escopo de 24/09, para responder a uma pergunta
simples: *destes treze arquivos, quais são a ferramenta e quais são o trabalho anterior?*

Não é triagem de decisões — essa sai no projeto de redação depois da especificação. É
inventário de código.

**A descoberta ao montar o mapa:** duas coisas que nasceram como experimento **já são funções
da ferramenta**, só que sem interface. Estão marcadas com ⭐ abaixo.

---

## Núcleo — vira produto

| Arquivo | O que faz |
|---|---|
| `src/instancia.py` | As estruturas de dados: turno, contrato, profissional, padrão, demanda. Sem Pyomo, sem XML. É a fronteira que permite a instância brasileira entrar sem tocar no modelo. |
| `src/modelo.py` | **O motor.** Monta o problema de programação inteira: 2 restrições rígidas, 13 flexíveis, limites legais endurecíveis por flag. É o que a interface vai chamar. |
| `src/instancia_br.py` | **A tradução da norma.** Parecer COFEN + CLT → instância resolvível. Recebe grau de dependência, porte, regime, efetivo e devolve o problema montado. Na ferramenta, isto é a camada que fica atrás do formulário. |
| `src/solucao.py` | Escreve a escala produzida e valida contra o esquema. É a saída. |
| `src/tabela.py` | Gravação de CSV por mesclagem, com testes próprios. Utilitário. |
| `src/testes_entrada.py` | Testes das entradas da ferramenta (29/09): pacientes, QP em duas parcelas, razão fim de semana/dia útil, equipe por quantidade, indisponibilidade. Reproduz 40 e 37 do Experimento A pela razão 20/29. `--rapido` pula o solver. |

## Já são funções da ferramenta, sem interface

| Arquivo | A função que ele é |
|---|---|
| ⭐ `src/experimento_a.py` | *"O quadro que a fórmula do COFEN dá admite escala legal?"* Varre o efetivo, prova inviabilidade abaixo do mínimo e exibe escala acima. **É o caso de uso principal da ferramenta** — o gestor calcula o quadro pela fórmula e quer saber se ele fecha. |
| ⭐ `docs/conferencia_descanso_escala.py` | *"Esta escala é legal?"* Mede o descanso real entre plantões a partir dos horários, sem depender de padrão nem de avaliador. **É o relatório de conformidade** que o usuário precisa ver junto com a escala. |
| ⭐ `src/experimentos.py` | Entre escalas de mesmo custo ótimo, mede quanto a carga individual pode variar. **É a base do "me dê a escala mais equilibrada"** em vez de aceitar a que o solver devolveu por acaso. |

## Validação — a prova de que o motor funciona

Não entram no produto, mas sustentam o capítulo que diz que ele está correto. Não apagar.

| Arquivo | O que faz |
|---|---|
| `src/regressao.py` | **O portão.** 4 instâncias × 4 conferências. Roda antes de qualquer alteração no modelo entrar. Continua valendo no escopo novo. |
| `src/avaliacao.py` | Reimplementação da penalidade em Python puro. É o oráculo: existe para o modelo ter com quem discordar. |
| `src/validar.py` | Chama o avaliador oficial da competição (Java) e compara. |
| `src/parser.py` | Lê o XML do INRC. Necessário para a validação; e se a ferramenta um dia importar instâncias, é por aqui. |
| `src/inspecionar.py` | Varredura das 69 instâncias do benchmark. Serviu ao levantamento inicial; consulta. |

## Rodando agora

| Arquivo | O que faz |
|---|---|
| `src/escalabilidade.py` | Curva 40–200 profissionais: até que tamanho a prova fecha. Decide se o warm start heurístico é necessário. |

## Escopo anterior — referência, não produto

Ficam em `docs/`. Produziram achados que vão ao texto como metodologia.

| Arquivo | O que produziu |
|---|---|
| `docs/conferencia_padrao_avaliador.py` | A demonstração de que o avaliador oficial lê o padrão das 36 h como (noturno, folga, folga). |
| `docs/conferencia_contratos.py` | O piso forçado e a descoberta de que o lote *early* é um cenário por track, não 15 independentes. |
| `docs/conferencia_piso_forcado.py` | As duas declarações que sustentam o piso aritmético. |
| `docs/medicao_conversao_12h.py`, `docs/medicao_sobreposicao.py` | A reagregação de turnos sobrepostos (P5). |

Os documentos do escopo anterior estão em `historico/escopo-comparacao-regimes/`, exceto o
`DECISOES.md`, que voltou à raiz como arquivo ativo em 29/09.

---

## O que isso sugere para a construção da ferramenta

O motor está pronto e validado. O que **não** existe é: camada de entrada que não seja código
Python, apresentação da escala em formato legível por gestor, e o relatório de conformidade
como saída de produto em vez de saída de terminal.

Ou seja — a parte difícil já passou. O que falta é a casca. Isso é uma boa notícia para o
prazo, e é o que a especificação precisa delimitar.

**Uma pendência de risco que a especificação vai ter de encarar:** o tempo de resolução. O
`experimento_a.py` leva de 1 a 43 segundos por tentativa de efetivo, e a curva de
escalabilidade está medindo o que acontece com 200 profissionais. Uma interface web que faz o
usuário esperar não é a mesma coisa que um script que roda no terminal.
