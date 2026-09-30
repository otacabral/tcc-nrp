# Estado atual — ponto de partida para qualquer sessão

**Atualizado em 29/09/2026.** Este arquivo existe para responder, em uma leitura, *onde o
trabalho está*. É o primeiro que qualquer assistente — Claude Code aqui no repositório ou o
chat de orientação/redação — deve ler.

Ele não substitui nada. O escopo está em `VIRADA_ESCOPO_2026-09-24.md`, o protocolo de
trabalho em `CLAUDE.md`, o inventário de código em `MAPA_CODIGO.md`, as decisões de modelagem
em `DECISOES.md`. Este arquivo diz **em que ponto
estamos** e **o que vem depois**.

---

## 1. O que é o trabalho, em três frases

TCC de Engenharia de Produção (CEFET-RJ). Uma **ferramenta gratuita de apoio à decisão** que
gera escalas de enfermagem a partir dos parâmetros de dimensionamento do COFEN (Parecer
Normativo nº 1/2024) e da legislação trabalhista brasileira. O motor de otimização é validado
contra o benchmark INRC-2010, que tem ótimos publicados — é isso que autoriza dizer que a
ferramenta está correta.

**O objeto do trabalho é o modelo, não o algoritmo.** Sem metaheurística, sem geração de
colunas. Warm start heurístico só como partida, e só se a escala exigir.

## 2. Datas

| Data | O quê |
|---|---|
| 24/09/2026 | Virada de escopo (comparação de regimes → ferramenta). Feita. |
| **14/10/2026** | **Congelamento de resultado numérico.** Depois disso, nenhum número novo entra. |
| **04/11/2026** | **Entrega.** |

Restam cerca de duas semanas até o congelamento e cinco até a entrega.

## 3. O que está fechado

Tudo abaixo é reproduzível por um comando no repositório. Nenhum destes números vale sem
conferência no avaliador oficial ou contra a Tabela 6 de Santos et al. (2016) — todos passaram
por uma das duas, exceto onde anotado.

**O motor está validado.** `python src\regressao.py` roda 4 instâncias × 4 conferências e
reproduz os quatro ótimos publicados da Tabela 6. É o portão: roda antes de qualquer alteração
no modelo entrar.

**Efetivo mínimo com demanda constante: 36 pessoas, nos dois regimes, em 20 de 20 células.**
Fechado dos dois lados — 35 é inviável com prova do solver, 36 tem escala exibida e aprovada
pelo avaliador. A explicação é aritmética: 5.920 h ÷ 168 h = 35,24, que é o próprio quadro de
referência do Parecer.

**Com demanda variando entre dias, os regimes se separam.** A forma da variação foi medida na
instância `long01` do benchmark (29 atribuições por dia útil contra 20 no fim de semana), não
arbitrada, e preserva o total de horas. O 12×36 passa a exigir 40 pessoas contra 37–38 do
regime de 8 h. O mecanismo é demonstrável sem resolver nada: no 12×36 ninguém trabalha dois
dias seguidos, logo o efetivo tem de cobrir a *soma* de dois dias consecutivos.

**A curva de escalabilidade fecha até 200 profissionais.** Seis tamanhos (36, 40, 60, 80, 120,
200), otimalidade provada em 6 de 6, 549 s no maior. **Ressalva grande, registrada em
`PROPOSTAS.md` como P1:** na instância brasileira o objetivo é degenerado (ótimo = zero), então
a curva mediu *viabilidade*, não otimização. Com objetivo de verdade a curva pode ser outra.

**Achado metodológico sobre o avaliador oficial (P13 do escopo anterior).** O avaliador lê o
padrão das 36 h como *(noturno, folga, folga)*: depois de uma entrada "folga" em posição não
inicial, ele ignora o tipo de turno das entradas seguintes. Isso gera 116 cobranças fantasma
contra 0 violações reais. Não contamina nada: varri os 59 arquivos do INRC, 304 padrões,
**nenhum** com esse formato. O que está demonstrado é *comportamento*, não código — não li o
fonte do avaliador.

**Piso aritmético do custo.** Como a cobertura é igualdade, o total de atribuições é fixo; o
excesso sobre a soma dos tetos existe em toda escala viável. Responde por 54–61% do ótimo nas
instâncias *sprint* e 73–81% nas *long*.

## 4. Onde está o código

Detalhe arquivo por arquivo em `MAPA_CODIGO.md`. O resumo que importa:

**O motor está pronto.** `modelo.py` + `instancia.py` + `instancia_br.py` + `solucao.py`.

**Três coisas que nasceram como experimento já são funções da ferramenta, sem interface:**
`experimento_a.py` ("o quadro que a fórmula do COFEN dá admite escala legal?"),
`docs/conferencia_descanso_escala.py` ("esta escala é legal?" — é o relatório de conformidade),
`experimentos.py` ("me dê a escala mais equilibrada entre as de mesmo custo").

**O que falta é a casca**: entrada que não seja código Python, apresentação da escala em
formato legível por gestor, e o relatório de conformidade como saída de produto.

## 5. O que está pendente, em ordem

### Bloqueia tudo

**1. ~~A especificação da ferramenta.~~ — RESOLVIDO em 29/09.** Decidida, ver
`DECISOES.md`, "2026-09-29 — Especificação da ferramenta". Registro original, abaixo.

Está sendo escrita no projeto de redação. Sem ela não dá
para começar a interface, e a reescrita dos arquivos de contexto está congelada esperando por
ela. **É o caminho crítico.** Enquanto ela não sai, o trabalho de código é organização e
dívida.

### Esperando decisão

**2. ~~P1 — repetir a curva de escalabilidade com objetivo não trivial.~~ — RESOLVIDO em
29/09.** Desbloqueada; executa depois da Etapa 7 (ver DECISOES 2026-09-29, Redesenho). Registro original, abaixo.

Registrado em
`PROPOSTAS.md`, aguardando validação. Custo: ~20 min de máquina. Só faz sentido depois da
especificação, porque é ela que define o objetivo.

**3. ~~Licença.~~ — RESOLVIDO em 29/09.** MIT; arquivo `LICENSE` na raiz. Registro
original, abaixo.

Uma ferramenta que se propõe gratuita e não declara licença é juridicamente
inutilizável por quem a receber. Precisa de decisão — provavelmente MIT ou GPL. Questão para a
orientação.

**4. Destino de quatro notas do escopo anterior** em `docs/`:
`nota_conferencias_contrato_2026-09-22.md`, `nota_intervalo_individual_2026-09-22.md`,
`nota_piso_forcado_2026-09-22.md`, `para_orientacao_2026-09-23.md`. Vão para `historico/` ou
ficam como metodologia ativa? Não decidido.

**5. ~~`DECISOES.md` está em `historico/`, e isso é um risco.~~ — RESOLVIDO em 29/09.** O
arquivo voltou à raiz como ativo, com marca de status em cada entrada e em cada pergunta
aberta. É **exceção declarada** à regra da VIRADA de não reescrever contexto antes da
especificação: só movimentação e marcação, sem alteração do texto das entradas. A correção
das linhas 3 e 4 da `VIRADA_ESCOPO_2026-09-24.md`, que apontavam o `DECISOES.md` como
substituído, faz parte da mesma exceção. Registro original do problema, abaixo.

O arquivo foi para o histórico
junto com o escopo anterior, mas boa parte do que está nele são **decisões de modelagem que
sobrevivem à virada**: cobertura como igualdade, os limites legais rígidos, o piso aritmético,
o achado do avaliador. Pelo `CLAUDE.md`, `historico/` é "consulta, não referência ativa" — ou
seja, uma sessão nova pode não olhar. Decisão a tomar: separar as decisões que continuam
valendo, ou reclassificar o arquivo.

### Dívida menor

**6. O `README.md` tem três links mortos** para arquivos que foram para `historico/`. Reescrita
adiada de propósito: o README vai ter de mudar de qualquer jeito quando a especificação sair.

## 6. O que este repositório aprendeu errando

Está em `CLAUDE.md`, mas vale repetir porque é o critério mais útil que saiu do trabalho:

- **Conferência que compartilha premissa com o que confere não confere nada.**
- **Lista duplicada é o defeito** — o mesmo conjunto existia em três lugares e corrigir dois
  não mudou nada.
- **Resultado idêntico depois de uma correção é sinal de alarme**, não de estabilidade.

## 7. Como os dois ambientes se dividem

**Claude Code, aqui no repositório**: código, experimentos, conferências, organização de
arquivos. Lê estes arquivos sozinho — não precisa que nada seja colado.

**Chat de orientação / redação**: escopo, decisões, especificação da ferramenta, texto do TCC.
Não tem acesso a esta pasta. Recebe os arquivos por upload.

**Quem decide (regra de 29/09/2026).** Decisões de escopo e de formulação são tomadas pelo
Otávio no projeto de redação e registradas como decisões no `DECISOES.md`. Não esperam
validação do orientador; ele é informado na reunião.

**A ponte são quatro arquivos**: este, `VIRADA_ESCOPO_2026-09-24.md`, `PROPOSTAS.md` e
`DECISOES.md`. Decisão registrada de um lado que não chega ao outro vira capítulo escrito com
decisão superada.
