# TCC - Nurse Rostering Problem (INRC-2010)

Modelo de programacao inteira mista para o Nurse Rostering Problem, usando as
instancias da First International Nurse Rostering Competition (2010).

Stack: Python, Pyomo, HiGHS. Avaliador oficial em Java.

O solver e parametro da chamada, nao do modelo. HiGHS e o padrao, por nao exigir
licenca; Gurobi ou CPLEX entram nos experimentos se a licenca academica sair, sem
reescrever o modelo. Ver CONTEXTO_PROJETO.md, secao 8.

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

## Ferramenta (tela)

    streamlit run src\app.py

Abre no navegador. Esqueleto de 29/09: formulario basico, veredito do quadro,
escala e planilha para baixar.

## Avaliador oficial

O `evaluator.jar` distribuido pela competicao NAO declara `Main-Class` no
manifesto, entao `java -jar` falha com "no main manifest attribute". Ele tambem
NAO embute as dependencias. Sao tres, e sem elas o avaliador morre com
`NoClassDefFoundError`:

| Jar | Para que | Onde baixar |
|---|---|---|
| dom4j 1.6.1 ou 2.x | leitura do XML | Maven Central: `dom4j/dom4j` |
| jaxen 1.2.0 | XPath do dom4j (`selectSingleNode`) | Maven Central: `jaxen/jaxen` |
| jaxb-api 2.3.1 | `javax.xml.bind.DatatypeConverter`, removido do JDK a partir do Java 11 | Maven Central: `javax.xml.bind/jaxb-api` |

Baixar os tres e colocar em `avaliador/`, ao lado do `evaluator.jar`. Com eles la,
o curinga do classpath resolve tudo:

    java -cp "avaliador\*" dds.nrp.core.evaluation.ScheduleEvaluator instancia.xml solucao.xml

Opcoes:

- `-h` imprime a ajuda
- `-p` imprime apenas o valor da penalidade, sem as violacoes detalhadas.
  **Tem de vir antes dos arquivos** — o `main` so reconhece `-p` como primeiro
  argumento; depois dos arquivos ele responde "Syntax error"

O `src/validar.py` monta esse comando sozinho e avisa qual dependencia falta.

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

## Licenca

MIT. Ver `LICENSE`.
