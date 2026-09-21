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
- [x] src/instancia.py: dataclasses puras, sem Pyomo
- [x] src/parser.py: XML -> Instancia, respeitando on= e expandindo
      DayOfWeekCover para os dias do horizonte (com DateSpecificCover tendo
      precedencia) e conferindo integridade referencial
- [x] conferencia: long01 = 740 atribuicoes, 49 profissionais, 6 HeadNurse
- [x] conferencia: sprint01 com on="0" nas tres restricoes de fim de semana
- [x] conferencia cruzada: as 69 instancias batem com o inventario da Sessao 1
      em 9 campos cada

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

- [x] src/avaliacao.py: penalidade de uma escala em Python puro, restricao por
      restricao e profissional por profissional. Oraculo de semantica para a
      funcao objetivo, e decomposicao por profissional para o Experimento B
- [x] semantica das 13 flexiveis conferida contra o avaliador oficial: 207
      escalas nas 69 instancias, penalidade IDENTICA em todas, por profissional
      e por restricao. As 13 exercitaveis pelos dados foram exercitadas; as 6
      que ficaram com zero sao as que nenhuma instancia produz
- [x] achado: NoNightShiftBeforeFreeWeekend NAO e pontuada pelo avaliador. O
      campo e lido e nunca usado por nenhuma condicao. Implementa-la faria o
      modelo divergir em 44 das 69 instancias, medium_late05 inclusive
- [x] funcao objetivo no modelo.py, espelhando avaliacao.py. Montada por familia
      de restricao (m.parcela[familia]), o que permite comparar com avaliacao.py
      restricao por restricao quando divergir — e alimenta o Experimento B
- [x] teste de linearizacao: escala fixada no modelo, objetivo do modelo igual ao
      de avaliacao.py. Achou um erro real — o padrao de dia fixo penalizava uma
      vez por dia do fim de semana em vez de uma vez por semana
- [x] MARCO ANTECIPADO: sprint01 = 56, sprint02 = 58, long01 = 197, long02 = 219,
      todos com otimo provado e batendo no avaliador oficial
- [ ] medium_late05 = 107: nao fechou em 230s. Pela Tabela 3 do Santos, o CPLEX
      leva ~1h partindo de solucao gulosa. Rodar com limite maior
- [x] regressao da regra de ativacao: FEITA em 15/09, regra confirmada no
      avaliador por dois testes independentes. Ver DECISOES.md
- [x] AlternativeSkillCategory RESOLVIDA em 18/09: habilidade e flexivel com
      coeficiente na variavel de atribuicao. O item que mandava rodar as duas
      leituras contra o 197 foi REMOVIDO por nao distinguir as hipoteses; o
      motivo esta na entrada de 18/09 do DECISOES.md, para nao ser reaberto
- [ ] medir tempo ate provar otimalidade em long01 nos solvers disponiveis e
      escolher o dos experimentos -> entrada datada em DECISOES.md
- [x] MARCO: sprint01 = 56, long01 = 197
- [x] confirmacao independente: sprint02 = 58, long02 = 219
- [ ] cobertura ampla: medium_late05 = 107. E o alvo que exercita fins de semana
      consecutivos, turno noturno antes de fim de semana livre, habilidade
      alternativa e pesos diferentes de 1
- [x] implementadas, SEM conferencia externa possivel: maximo de fins de semana
      em quatro semanas e folgas apos noites, em avaliacao.py e modelo.py. Os
      pedidos "on" ja estavam. Inertes nos dados do INRC: sprint01 = 56 e
      long01 = 197 nao se alteraram depois de acrescenta-las. Marcar no texto
      como implementadas e nao validadas

## Semana 4 (30/09-06/10) - instancia brasileira

- [x] BLOQUEIO DA P5 DISSOLVIDO em 21/09: com perfil uniforme, cada janela de
      8 h e cada janela de 12 h pede os mesmos 8,81 profissionais, e o residuo
      e IDENTICO nos dois regimes (teto: 9 por janela, +2,16% nos dois). O piso
      aritmetico e 36 nos DOIS. A assimetria da P5 nao se coloca nesta
      instancia. Mantidas as duas instancias por regra e a conferencia de
      total de horas com tolerancia de um bloco. Historico abaixo:
- [x] BLOQUEIO: P5 do PROPOSTAS.md, a discretizacao da demanda em blocos de 12h.
      Medido em 18/09: nenhuma regra de arredondamento serve. Teto e maior resto
      caem os dois no TOPO da faixa admissivel do pico de 48h — 40 contra faixa
      [38,40] no total, 8 e 7 contra faixa [5,8] no chefe. As duas inflam o piso
      de efetivo do 12x36, que e o lado que o trabalho mede. Proposta: demanda
      por janela vira variavel inteira entre piso e teto, com o total por
      categoria fixado. Nada de instancia brasileira antes de fechar isso
- [x] REQUISITO ANTI-TAUTOLOGIA, antes de qualquer codigo: o perfil continuo
      tem de vir da necessidade assistencial HORA A HORA (horas de enfermagem por
      paciente em 24 h, do dimensionamento normativo), NUNCA de blocos de 8 h nem
      de 12 h. Montado como "manha, tarde, noite", o braco de 8 h nasce com
      residuo zero de graca e a assimetria volta embutida no primitivo, invisivel
- [x] conferencia do gerador: reagregar o perfil emitido nos DOIS tamanhos de
      janela e verificar que nenhum dos dois da residuo zero. Residuo zero em
      qualquer um deles reprova o perfil — e sintoma de que o primitivo foi
      construido naquele tamanho (e o que acontece nas 4 instancias de controle)
- [x] src/instancia_br.py: o PRIMITIVO e o perfil assistencial horario continuo,
      nao a demanda ja em blocos. Os dois regimes (8h e 12x36) sao emitidos a
      partir dele pela mesma regra, o que torna a comparacao simetrica por
      construcao. Medido em 18/09: o long01 nao permite essa simetria porque
      seus turnos se sobrepoem (D e DH cruzam a fronteira das 14:30) e o perfil
      continuo de origem dele nao existe
- [x] src/instancia_br.py: serializa para XML oficial, valida contra o esquema
      antes de resolver. Emitir DUAS instancias, uma por teto e outra por maior
      resto por categoria, que sao as duas pontas do intervalo reportado
- [x] REQUISITO do gerador: as duas instancias emitidas saem do MESMO perfil
      continuo e diferem SO na regra de reagregacao. Se nascerem de perfis
      diferentes, o par deixa de medir o efeito da regra. Conferencia: os dois
      XML tem de ter o mesmo total de horas antes do arredondamento
- [x] desagregacao enfermeiro/tecnico via tipo de turno por horario x categoria
- [x] regime 12x36 como MaxConsecutiveWorkingDays = 1 (COM FURO: ver P7.2,
      o plantao noturno so ganha 24 h de descanso, nao 36)
- [x] efetivo parametrizavel (e resultado no Experimento A, nao parametro)
- [x] composicao por categoria e grau de dependencia como PARAMETROS DE ENTRADA
      da funcao construtora, varridos nos experimentos, nao fixados no codigo
      (decisao de 18/09; e o que torna o objetivo especifico 5 reprodutivel)
- [x] regra de discretizacao da demanda como PARAMETRO do gerador (fixa por regra
      ou variavel em faixa), pelo mesmo motivo dos outros dois
- [x] conferencia obrigatoria: horas-profissional da instancia nova x 5.920 h do
      long01, POR CATEGORIA, com tolerancia de um bloco de 12 h por categoria.
      A tolerancia e necessaria: 5.920 nao e divisivel por 12 (= 493,33 blocos)

- [x] P7.1, P7.2 e P7.3 VALIDADAS e implementadas em 21/09. Descanso conferido
      por enumeracao: 36 h no 12x36, 16 h de interjornada e 24 h de descanso
      semanal no de 8 h. Ver DECISOES.md, entrada "Definicao de viavel"
- [ ] BLOQUEIO DO EXPERIMENTO B: P7.4 revisada. Aplicado o criterio, sobra so a
      familia de pedidos de folga — e a instancia brasileira nao tem pedidos,
      entao a penalidade seria zero nos dois bracos. complete_weekends e
      identical_shift_types_during_weekend estavam na lista de ENTRA e sao
      estruturais; a familia de fins de semana esta OFF nos tres contratos do
      long01, logo nao ha peso a herdar. Ver PROPOSTAS.md, P7.4 revisao
- [ ] emitir as instancias dos 5 graus x 2 regimes x 2 regras depois que a P7
      fechar, e versionar em instancias/br/

## Semana 5 (07-13/10) - experimentos

- [ ] src/experimentos.py, saida em resultados/consolidado.csv
- [ ] Experimento A: efetivo minimo viavel em 8h e em 12x36, a horas de
      assistencia constantes. Reportar a DISTANCIA PERCENTUAL entre o piso
      aritmetico e o minimo viavel em cada regime, nao o numero absoluto.
      O efetivo de 8h e recalculado, nao e os 49 do long01
- [ ] Experimento A: reportar INTERVALO, nao ponto. A comparacao entre regimes
      se faz com o intervalo inteiro, nunca com a ponta que mais favorece
- [ ] declarar no texto: na categoria do chefe o intervalo e 60% da grandeza,
      logo o Experimento A nao sustenta afirmacao quantitativa ali. Sobra a
      qualitativa, que e o achado
- [ ] Experimento B: penalidade total e distribuicao (maxima individual,
      amplitude, dispersao). TRES resolucoes por celula: o otimo Z*, depois Z*
      fixado com a dispersao minimizada e maximizada. Reportar a amplitude
- [ ] pesos identicos entre configuracoes; instancias pequenas o bastante
      para PROVAR otimalidade

## Dependencias externas a este projeto

- [ ] coluna na planilha de triagem dos 110 sobre reagregacao de turnos
      sobrepostos em janelas disjuntas. Ate ela existir, a frase "a literatura
      nao discute esse passo" fica SUSPENSA: sem denominador e "nao achei".
      O achado pode ser apresentado sem essa frase — ele tem denominador
      proprio (65 de 69 instancias) e grupo de controle (as 4 sem sobreposicao)
- [ ] ENQUADRAMENTO no texto: a inversao (12x36 distorcendo menos que 8 h) e
      achado SOBRE O BENCHMARK, nao sobre regimes de jornada. Nas 4 instancias
      sem sobreposicao a intuicao ingenua esta certa: 12 h custa ~19%, 8 h custa
      zero. A inversao so existe onde ha sobreposicao, e existe porque ela
      penaliza o arranjo de 8 h. Escrito de outro jeito, a banca le que o
      trabalho mostrou o 12x36 discretizando melhor. Nao mostrou
- [ ] o achado da reagregacao e METODOLOGIA, nao resultado. Cabe numa subsecao
      do capitulo de dados. Esta FECHADO: nao abrir medicao nova sobre ele
- [ ] TERMO no texto: "reagregacao de turnos sobrepostos em janelas disjuntas",
      nunca "discretizacao" como nome do efeito. Nas instancias sem
      sobreposicao o residuo em janelas de 8 h e zero, e chamar de
      discretizacao generica convida a pergunta com a resposta errada
- [x] FECHADO em 21/09: Parecer Normativo COFEN 1/2024. Os parametros estao na
      entrada de 21/09 do DECISOES.md. Historico do portao, mantido porque
      explica o desenho: as fontes NAO alimentam a instancia, elas a
      constituem. O portao FICOU MAIS
      ESTREITO em 18/09: com o perfil assistencial continuo como primitivo do
      gerador (P5 revisao 2), as fontes nao alimentam mais a instancia — elas a
      constituem. Sem fontes nao ha primitivo; sem primitivo nao ha instancia,
      nem Experimento A, nem B
- [ ] reescrita do objetivo especifico 2 no projeto de redacao: a instancia
      passa a ser construida a partir de perfil assistencial derivado de
      parametros normativos, calibrada para o porte de uma instancia do
      benchmark. PORTE = total de horas-profissional no horizonte = 5.920 h do
      long01, que e o proprio invariante da P4. Ver P6 do PROPOSTAS.md
- [ ] no projeto de redacao, junto com o especifico 2: reformular o gap (nao e
      "reparametrizar um benchmark", e "construir instancia a partir de
      parametros normativos calibrada a um benchmark") e dizer na delimitacao
      1.4 que a instancia e SINTETICA, para nao ser lida como estudo de caso

## 14/10 - congelamento

- [ ] git tag -a congelamento-2026-10-14 -m "Resultados congelados"
- [ ] git push --tags
- [ ] a partir daqui, apenas texto

## Convencoes de codigo

src/ tem fronteira definida por arquivo:

| Arquivo | Papel |
|---|---|
| instancia.py | dataclasses puras, zero Pyomo |
| parser.py | XML -> Instancia; tambem a descoberta dos arquivos |
| avaliacao.py | penalidade de uma escala em Python puro, por restricao e por profissional |
| modelo.py | Instancia -> modelo Pyomo |
| solucao.py | solucao Pyomo -> XML do avaliador |
| validar.py | invoca o avaliador e compara objetivos |
| inspecionar.py | varredura das instancias, emite os inventarios em docs/ |
| instancia_br.py | perfil assistencial continuo -> Instancia -> XML oficial |
| experimentos.py | Experimentos A e B (a fazer) |

avaliacao.py nao estava no plano original. Entrou na semana 2 com duas funcoes: fixar a
semantica das flexiveis contra o avaliador antes de a funcao objetivo existir, e decompor a
penalidade por profissional, que e o que o Experimento B pede e o modelo nao da.

Regra: modelo.py consome apenas Instancia, nunca XML. E o que permite a
instancia brasileira entrar sem tocar no modelo.

Descoberta de instancias: track e o primeiro nivel de diretorio, lote e o
segundo. Subpasta com o mesmo nome do track = lote early. Ignorar __MACOSX
e arquivos iniciados por "._" (residuo AppleDouble com extensao .xml falsa).

Mapeamento para a Tabela 6 de Santos et al.: long01.xml = long_early01.
