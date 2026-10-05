# Estado atual — ponto de partida para qualquer sessão

**Atualizado em 03/10/2026.** Este arquivo existe para responder, em uma leitura, *onde o
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
| **10/10/2026** | **Congelamento das funcionalidades.** Depois disso, nenhuma função nova entra na ferramenta. |
| **14/10/2026** | **Congelamento de resultado numérico.** Depois disso, nenhum número novo entra. |
| **04/11/2026** | **Entrega.** |

Em 02/10: oito dias até o congelamento das funcionalidades, doze até o de resultado numérico e cerca de cinco semanas até a entrega.

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

**A interface existe** (02/10): `src/app.py`, em Streamlit — `streamlit run srcpp.py`.
É a casca de `src/ferramenta.py`. Tem, na ordem da especificação:

- configuração da unidade: modelo de turnos editável (início e duração), definição de fim de
  semana, grau de dependência;
- equipe: enfermeiros e técnicos por quantidade, nomes opcionais, férias e licenças
  (rígidas), pedidos de folga (flexíveis);
- demanda por turno, geral (com valores próprios para o fim de semana) e por data;
- conferência com o COFEN, que só alerta e nunca trava;
- alertas em vermelho no resultado;
- diagnóstico da trava: quando o quadro não tem escala legal, o motivo e o menor quadro
  viável;
- escala conferida na conferência de descanso e planilha `.xlsx` para baixar.

Testes ponta a ponta pela tela em `src/testes_ferramenta.py`; testes das entradas em
`src/testes_entrada.py`.

As três funções que nasceram como experimento estão dentro dela: `experimento_a.py` (o quadro
admite escala legal?), `docs/conferencia_descanso_escala.py` (a escala é legal?) e
`experimentos.py` (a mais equilibrada entre as de mesmo custo).

## 5. O que está pendente, em ordem

**Concluído: Etapas 1 a 7** da especificação (ver `DECISOES.md`, entradas de 29/09:
"Especificação da ferramenta", "Ajustes da Etapa 2" e "Redesenho da ferramenta"). Licença
MIT decidida e no repositório; `DECISOES.md` de volta à raiz como arquivo ativo.

**Pendente, nesta ordem:**

1. **P1 — curva de escalabilidade com objetivo não trivial** (Etapa 4). Será lançada depois
   do item 1 do próximo bloco (carga por contrato, equilíbrio por fração do contrato), com o
   modelo final. A rodada de 02/10 foi preliminar e não é resultado. Ver `PROPOSTAS.md`, P1.
   *Atualização de 05/10:* rodou em 03/10 pelo caminho da ferramenta. A prova fecha até
   N = 80; em 120 fica sem prova (gap 3,2%), em 200 sem escala em 900 s. Ressalva: a etapa 2
   é degenerada em todos os tamanhos (demanda = 14N, todos em 168 h). Proposta em aberto na
   P1 sobre medir a etapa 2 numa instância com folga. *05/10, tarde:* rodada com folga feita
   (demanda de 40/60/80, equipe +10%): etapa 1 provada nos três; a etapa 2 acha a escala final
   entre 18 e 81 s e não prova em 900 s, mas a conta mostra que ela já é ótima. Pendente:
   decidir o limite da etapa 2 na tela.
2. ~~**Decisão sobre carga mínima.**~~ Respondida em 02/10 pela decisão "Carga por contrato"
   (`DECISOES.md`): carga contratual por profissional, teto nos dias disponíveis, equilíbrio
   pela fração do contrato cumprida. Implementada em 03/10. **Em aberto, P6:** a amplitude da
   fração fica presa à separação entre enfermeiros e técnicos (teste 9c); decidir o critério
   final da etapa 2 antes de relançar a P1.
   *Atualização de 03/10:* P6 resolvida — a etapa 2 equilibra dentro de cada categoria
   (`DECISOES.md`, "Carga por contrato", itens g e h); suíte completa OK. *Correção de 03/10:* a
   P1 lançada às 14:29 morreu às 14:30 (instâncias do caminho antigo sem carga contratual);
   passa a medir o caminho da ferramenta — ver `PROPOSTAS.md`, P1, e
   `resultados/relatorio_2026-10-03c.md`.
3. **Acabamento visual mínimo** na tela: concordância e textos soltos ("isto e" sem acento,
   "1 dias").
4. **Arquivo de configuração** (pacote INRC + complemento). Menor prioridade: se não estiver
   pronto em 10/10, vira trabalho futuro.

**Dívida menor, sem prazo:**

- **Destino de quatro notas do escopo anterior** em `docs/`:
  `nota_conferencias_contrato_2026-09-22.md`, `nota_intervalo_individual_2026-09-22.md`,
  `nota_piso_forcado_2026-09-22.md`, `para_orientacao_2026-09-23.md`. Vão para `historico/`
  ou ficam como metodologia ativa? Não decidido.
- **O `README.md` tem três links mortos** para arquivos que foram para `historico/`.

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
