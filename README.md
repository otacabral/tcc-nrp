# TCC - Nurse Rostering Problem (INRC-2010)

Modelo de programacao inteira mista para o Nurse Rostering Problem, usando as
instancias da First International Nurse Rostering Competition (2010).

Stack: Python, Pyomo, HiGHS. Avaliador oficial em Java.

## Estrutura

- `src/` - codigo
- `instancias/` - instancias INRC-2010 (nao versionado, ver Download)
- `avaliador/` - avaliador oficial (nao versionado, ver Download)
- `docs/` - esquemas XSD e descricao da competicao
- `resultados/` - saidas dos experimentos (so o consolidado e versionado)

## Download dos dados

Instancias, avaliador e esquemas XSD nao entram no repositorio por serem
publicos e grandes. Baixar de:

https://watt.cs.kuleuven.be/basic-page/first-international-nurse-rostering-competition

- zip de instancias -> descompactar o conteudo em `instancias/`
- `evaluator.jar` -> `avaliador/`
- `scheme_input.xsd` e `scheme_solution.xsd` -> `docs/` (ja versionados)

## Ambiente

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt

Java: JDK 21 ou superior (testado com Temurin 25). Necessario apenas para
executar o avaliador oficial.

## Avaliador oficial

O `evaluator.jar` distribuido pela competicao NAO declara `Main-Class` no
manifesto, entao `java -jar` falha com "no main manifest attribute".
Executar via classpath, indicando a classe principal:

    java -cp avaliador\evaluator.jar dds.nrp.core.evaluation.ScheduleEvaluator instancia.xml solucao.xml

Opcoes:

- `-h` imprime a ajuda
- `-p` imprime apenas o valor da penalidade, sem as violacoes detalhadas

Sem `-p`, a saida detalha as violacoes, o que permite identificar qual
restricao e qual profissional divergem do modelo. E o modo usado na
validacao incremental.

A solucao pode ser xml ou txt. Usamos XML, por ter contrato verificavel
em `docs/scheme_solution.xsd`.

## Regra de validacao

Nenhum resultado numerico e considerado valido sem conferencia no avaliador
oficial ou contra a Tabela 6 de Santos et al. (2016).

## Documentos do projeto

- `CONTEXTO_PROJETO.md` - escopo e pipeline
- `DECISOES.md` - decisoes de modelagem tomadas
- `PROPOSTAS.md` - sugestoes que aguardam validacao
