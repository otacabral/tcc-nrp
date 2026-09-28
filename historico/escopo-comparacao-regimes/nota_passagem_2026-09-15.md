# Nota de passagem para o projeto de redação — 15/09/2026

Primeira sincronização desde a abertura do projeto de códigos. Cobre as Sessões 1 a 3:
varredura das instâncias, parser e encanamento validado no avaliador oficial.

Subir junto com esta nota: `CONTEXTO_PROJETO.md`, `DECISOES.md`, `PROPOSTAS.md`,
`PLANO.md` e `docs/formato_instancias.md`.

---

## 1. Correções no que já estava lá

Coisas que o projeto de redação pode ter tomado como verdadeiras e não são.

| Onde | Estava | Está |
|---|---|---|
| CONTEXTO §7 | só o lote *hint* usa pesos diferenciados | só o lote *early* usa pesos 0/1; *late*, *hidden* e *hint* usam de 3 a 10, e 31 em três `medium` |
| CONTEXTO §7 | 60 instâncias | 69 arquivos: as 60 da competição mais 9 do lote *hint*, que não têm referência na Tabela 6 |
| DECISOES, pergunta aberta | `AlternativeSkillCategory = false` significaria habilidade proibida | para o avaliador, significa **sem penalidade nenhuma**; não há checagem rígida de habilidade em lugar algum do código dele |
| DECISOES, mesma pergunta | a dúvida se resolveria no avaliador, no Passo 3 | o avaliador é indiferente e aceita as duas leituras; quem arbitra é o 197 da Tabela 6 |
| CONTEXTO §8 | HiGHS como solver | HiGHS no desenvolvimento e validação; comercial nos experimentos se a licença sair; escolha por medição na semana 3 |

## 2. Decisões novas, prontas para virar texto

Todas com data e justificativa no `DECISOES.md`.

- **Regra de ativação de restrição flexível** (15/09) — uma restrição entra no modelo se
  estiver ligada e com peso maior que zero; nas restrições sem atributo `on=`, o conteúdo
  booleano é o interruptor. Confirmada por três evidências independentes: dois testes no
  avaliador oficial e o código-fonte dele, que vem dentro do `evaluator.jar`.
- **Cobertura como igualdade, inclusive onde a demanda não é declarada** (15/09) — turno não
  listado num dia tem demanda zero, e ninguém pode ser alocado nele.
- **Quinto alvo de validação: `medium_late05` = 107** (15/09) — os quatro alvos anteriores
  são todos do lote *early*, que desliga quatro restrições flexíveis e usa peso 1 em todas.
  Validar só neles prova 8 das 13 restrições.
- **Escopo: implementar as 13 flexíveis** (15/09), inclusive as três que nenhuma instância
  exercita, com ressalva explícita de que são implementadas e não validadas.

## 3. Material descritivo novo

`docs/formato_instancias.md` — descrição do formato das instâncias e perfil das 69. É
matéria-prima direta da seção que descreve os dados. Não contém decisão nenhuma, e não deve
mudar mais.

Dois inventários em CSV sustentam as afirmações dele: `docs/inventario_instancias.csv`
(uma linha por instância, 78 colunas) e `docs/uso_elementos_opcionais.csv`.

## 4. O que ainda está em aberto — não escrever capítulo sobre isso

- **O que `AlternativeSkillCategory = false` significa para o modelo.** Resolve-se nas
  semanas 2-3, rodando as duas leituras contra `long01` = 197.
- **Fim de semana incompleto no horizonte.** Não ocorre nas 69 instâncias do INRC; vira
  questão na instância brasileira, conforme a data de início escolhida.
- **Hierarquia de habilidade na instância brasileira.** No INRC ninguém tem `HeadNurse` sem
  ter `Nurse` — a habilidade é acumulativa. Se enfermeiro cobre posto de técnico, ou se as
  categorias são disjuntas, é decisão a tomar com o orientador.
- **Grau de dependência assistencial** e **status jurídico das normas de dimensionamento**,
  que já estavam abertas.

## 5. Estado do cronograma

Semana 1 fechada com atraso de poucos dias: parser pronto e escala aceita como viável pelo
avaliador oficial nas 69 instâncias. A função objetivo ainda não existe — o modelo tem
apenas as duas restrições rígidas. Próximo marco: `sprint01` = 56 e `long01` = 197, com as
13 flexíveis ativadas uma a uma.

Nenhum resultado numérico deste projeto pode ser citado no texto ainda. Os números que
apareceram até aqui (294 em `sprint01`, 1517 em `long01`) são de um modelo sem função
objetivo e servem só como prova de que o encanamento funciona.
