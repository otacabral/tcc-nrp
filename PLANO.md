# Plano de execucao

Checklist operacional. O porque de cada etapa esta em CONTEXTO_PROJETO.md
(secoes 11 e 12). Aqui ficam as tarefas.

Congelamento numerico: 14/10/2026. Entrega: 04/11/2026.

## Semana 1 (ate 15/09) - encanamento validado

Sessao 1 - varredura
- [x] src/inspecionar.py: percorre as 69 instancias (60 da competicao + 9 do
      lote hint), valida contra docs/scheme_input.xsd, emite
      docs/inventario_instancias.csv e docs/uso_elementos_opcionais.csv
- [x] ler a tabela; achados para DECISOES.md ou PROPOSTAS.md
      (correcoes e regra de ativacao em DECISOES.md; P1 e P2 registradas em
      PROPOSTAS.md e validadas em 15/09)

Fora de sessao, fazer assim que possivel
- [ ] solicitar licenca academica de Gurobi ou CPLEX. Prazo incerto e nao
      depende de mim; nada trava se nao sair. Atencao: a versao do gurobipy
      instalada por pip vem com licenca limitada a modelos pequenos, que nao
      resolve long01

Sessao 2 - parser
- [ ] src/instancia.py: dataclasses puras, sem Pyomo
- [ ] src/parser.py: XML -> Instancia, respeitando on= e expandindo
      DayOfWeekCover para os dias do horizonte
- [ ] conferencia: long01 = 740 atribuicoes, 49 profissionais, 6 HeadNurse
- [ ] conferencia: sprint01 com on="0" nas tres restricoes de fim de semana

Sessao 3 - encanamento
- [x] src/modelo.py: apenas as duas rigidas, com solver como parametro e flag
      --habilidade-livre
- [x] src/solucao.py: escreve XML, valida contra docs/scheme_solution.xsd,
      confere as duas rigidas antes de chamar o avaliador
- [x] src/validar.py: chama o avaliador, compara com o objetivo interno
- [x] dependencias do avaliador resolvidas: dom4j, jaxen e jaxb-api em
      avaliador/ (o evaluator.jar nao as embute; jaxb saiu do JDK no Java 11).
      O -p tem de vir ANTES dos arquivos. Ver README.md
- [x] MARCO: sprint01 aprovada como viavel pelo avaliador oficial (penalidade
      294 no modelo minimo, que ainda nao tem funcao objetivo)
- [x] varredura completa: as 69 instancias montadas, resolvidas, escala viavel,
      XML validado no esquema e ACEITO pelo avaliador oficial

## Semanas 2-3 (ate 29/09) - modelo completo

- [ ] ativar as 13 flexiveis UMA POR VEZ, conferindo no avaliador a cada uma
      (modo sem -p detalha violacoes por profissional e aponta a divergencia)
- [x] regressao da regra de ativacao: FEITA em 15/09, regra confirmada no
      avaliador por dois testes independentes. Ver DECISOES.md
- [ ] resolver AlternativeSkillCategory: flag no codigo (ja existe:
      --habilidade-livre), duas rodadas contra long01 = 197, so uma bate ->
      entrada datada em DECISOES.md. ATENCAO: o avaliador NAO arbitra isso, ele
      e indiferente a habilidade quando a flag esta em false. Quem arbitra e o
      197 da Tabela 6, entao o teste so roda com a funcao objetivo completa
- [ ] medir tempo ate provar otimalidade em long01 nos solvers disponiveis e
      escolher o dos experimentos -> entrada datada em DECISOES.md
- [ ] MARCO: sprint01 = 56, long01 = 197
- [ ] confirmacao independente: sprint02 = 58, long02 = 219
- [ ] cobertura ampla: medium_late05 = 107. E o alvo que exercita fins de semana
      consecutivos, turno noturno antes de fim de semana livre, habilidade
      alternativa e pesos diferentes de 1
- [ ] implementar tambem, SEM conferencia externa possivel: maximo de fins de
      semana em quatro semanas, folgas apos noites, pedidos "on" de dia e turno.
      Marcar no texto como implementados e nao validados

## Semana 4 (30/09-06/10) - instancia brasileira

- [ ] src/instancia_br.py: constroi Instancia em codigo, serializa para XML
      oficial, valida contra o esquema antes de resolver
- [ ] desagregacao enfermeiro/tecnico via tipo de turno por horario x categoria
- [ ] regime 12x36 como MaxConsecutiveWorkingDays = 1
- [ ] efetivo parametrizavel (e resultado no Experimento A, nao parametro)
- [ ] grau de dependencia assistencial em tres niveis

## Semana 5 (07-13/10) - experimentos

- [ ] src/experimentos.py, saida em resultados/consolidado.csv
- [ ] Experimento A: efetivo minimo viavel em 8h e em 12x36
- [ ] Experimento B: penalidade total e distribuicao (maxima individual,
      amplitude, dispersao)
- [ ] pesos identicos entre configuracoes; instancias pequenas o bastante
      para PROVAR otimalidade

## 14/10 - congelamento

- [ ] git tag -a congelamento-2026-10-14 -m "Resultados congelados"
- [ ] git push --tags
- [ ] a partir daqui, apenas texto

## Convencoes de codigo

src/ tem seis arquivos com fronteira definida:

| Arquivo | Papel |
|---|---|
| instancia.py | dataclasses puras, zero Pyomo |
| parser.py | XML -> Instancia |
| modelo.py | Instancia -> modelo Pyomo |
| solucao.py | solucao Pyomo -> XML do avaliador |
| validar.py | invoca o avaliador e compara objetivos |
| experimentos.py | Experimentos A e B |

Regra: modelo.py consome apenas Instancia, nunca XML. E o que permite a
instancia brasileira entrar sem tocar no modelo.

Descoberta de instancias: track e o primeiro nivel de diretorio, lote e o
segundo. Subpasta com o mesmo nome do track = lote early. Ignorar __MACOSX
e arquivos iniciados por "._" (residuo AppleDouble com extensao .xml falsa).

Mapeamento para a Tabela 6 de Santos et al.: long01.xml = long_early01.
