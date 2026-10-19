# Estado atual — ponto de partida para qualquer sessão

**Atualizado em 11/10/2026; datas atualizadas em 19/10** (notas de 10 e 11/10 abaixo; o corpo, das seções 1 a 7, é de 03/10 com
atualizações datadas). Este arquivo existe para responder, em uma leitura, *onde o
trabalho está*. É o primeiro que qualquer assistente — Claude Code aqui no repositório ou o
chat de Orientação ou de Redação, que leem esta pasta direto — deve ler (os chats começam
pelo `PASSAGEM.md`).

Ele não substitui nada. O escopo está em `VIRADA_ESCOPO_2026-09-24.md`, o protocolo de
trabalho em `CLAUDE.md`, o inventário de código em `MAPA_CODIGO.md`, as decisões de modelagem
em `DECISOES.md`. Este arquivo diz **em que ponto
estamos** e **o que vem depois**.

> **06/10/2026 — FERRAMENTA FECHADA, v1.0** (tag `v1.0` no commit desta nota). Suíte completa
> final de 06/10, um teste por processo: 17 de 17 OK — `regressao.py --todos` (56, 58, 197,
> 219 = Tabela 6), `testes_entrada.py`, todos os testes da tela (1–5, 4b, 7.1–7.4, 8a–8d,
> 9a–9d, 9b-sem-teto, 9c-tela) e os 544 XML idênticos byte a byte. Tempos e picos de memória
> em `resultados/suite_2026-10-06/` e no `resultados/relatorio_2026-10-06a.md`. Funcionalidades
> congeladas desde 05/10; daqui em diante, só correção de defeito, com esperado registrado
> antes. Inventário dos números citáveis: `resultados/NUMEROS_TCC.md`.
>
> **06/10/2026 — v1.0.1: VERSÃO CITÁVEL DO TCC.** Tag `v1.0.1` no commit desta nota. Diferença
> para a `v1.0`: a correção de defeito do `src/validar.py` (classpath `avaliador/*`, `-p` antes
> dos arquivos, barra normal; `DECISOES.md`, "Correção de defeito: `src/validar.py`"), com as
> cinco conferências refeitas no avaliador oficial (56, 58, 197, 219 e 224). A suíte não foi
> rodada de novo: nenhum teste usa o `validar.py`.
>
> **09/10/2026 — v1.1: VERSÃO CITÁVEL DO TCC** (tag `v1.1` no commit desta nota; substitui a
> `v1.0.1` como versão citável). Diferenças:
> - **P12** (`DECISOES.md`, "2026-10-08 — P12 aprovada"): a escala da etapa 1 aparece na tela
>   enquanto a etapa 2 equilibra a carga; a barra diz a fase e o limite dela; "o solver falhou"
>   virou "sem resposta em 10 min com N profissionais" ou "erro técnico …"; orçamento de 20 min
>   por clique. Nenhuma regra, modelo ou número mudou (`modelo.py` e `instancia_br.py` intactos).
> - **Suíte de 08/10**, um teste por processo: 16 de 16 OK (regressão, entradas, tela 1–9c e o
>   teste novo 12), depois da correção de um defeito do teste 12a; P05, P08 e K1 da bateria
>   iguais a 07/10 (`resultados/relatorio_2026-10-08b.md`).
> - **Demonstração refeita em 09/10** com o roteiro corrigido (o feriado de 20/11 entrava em
>   24/11 desde 05/10; `DECISOES.md`, "2026-10-08 — Demonstração: feriado de 20/11 digitado em
>   24/11"): conferidor independente da entrada OK nas três rodadas; vereditos, cortes e todos
>   os números da seção 9 do `NUMEROS_TCC.md` iguais (`resultados/relatorio_2026-10-09a.md`).
> - **Bateria** (07–08/10): níveis 1 e 2 e propriedades 2 e 3 sem violação; a escala com 17
>   do K4 existe (o solver nem sempre a acha em 600 s). Nível 3 estratificado: ver o relatório
>   de 09/10.
>
> **09/10/2026 (tarde) — VALIDAÇÃO ENCERRADA; próxima frente, o texto** (`DECISOES.md`,
> "2026-10-09 — Encerramento da validação"). Entraram a **P15** (alerta de descanso semanal
> abaixo de 35 h, sem as bordas do horizonte) e a **P14** (etapa 2 também sem prova, sem piorar o
> valor da etapa 1). A versão citável passa a ser a **`v1.2`** quando a suíte da parte B fechar:
> em 09/10 ela foi interrompida por falta de memória (ver `resultados/relatorio_2026-10-09b.md`).
> Até 16/10, só correção de defeito, com esperado registrado antes. Melhorias de tela para 26 a
> 29/10: P16. Candidata em aberto: P17 (warm start da etapa 2).
>
> **09/10/2026 (noite) — v1.2: VERSÃO CITÁVEL DO TCC** (tag `v1.2` no commit `04f3156`, enviada
> ao GitHub; substitui a `v1.1`; registrado em 10/10). O `docs/diagnostico/fechar_v12.sh` terminou
> às 18:33 de 09/10 com **"TUDO OK"** (`resultados/fechar_v12/resumo.txt`), na ordem e parando na
> primeira falha: regressão dos 4 ótimos (56, 58, 197, 219 = Tabela 6), testes de entrada, P17 no
> caso do Otávio, K5 e K6 (seis conferências OK), P08/P05/K1 iguais a 07/10, suíte da tela (15
> testes) e a demonstração pelas três rodadas, com o conferidor da planilha OK em cada uma e os
> números iguais (24/36/34 enfermeiros em posto de técnico, 6 de 6 pedidos). Entram na `v1.2`: P15
> (alerta), P14 e P17. A P17 deixou de ser candidata: está implementada e conferida.
>
> **10/10/2026 — v1.2.1: VERSÃO CITÁVEL DO TCC** (tag `v1.2.1` no commit desta nota; substitui a
> `v1.2`, que não foi movida). **Código idêntico ao da `v1.2`** (diff de `src/` vazio). Diferença:
> a evidência citada pelo `NUMEROS_TCC.md` que estava fora do git (23 arquivos, 286,5 KB: CSVs e
> logs da P1, CSVs dos experimentos A e B, as quatro escalas ótimas `*_completo.xml` com as saídas
> do avaliador, os três logs do HiGHS da condição de ótimo e os `p17_*.json`) passou a ser
> versionada. Lista gerada e conferida por `docs/diagnostico/citados_fora_do_git.py`, que depois
> do add dá **0 arquivos fora do git**. Em andamento: o diagnóstico da P17 (`DECISOES.md`,
> "2026-10-10 — P17: etapa 2 sem melhora nos três casos difíceis").
>
> **11/10/2026 — v1.2.2: VERSÃO CITÁVEL DO TCC** (tag `v1.2.2` no commit desta nota; substitui a
> `v1.2.1`). **P17 fechada, sem defeito** (`DECISOES.md`, "2026-10-10 — P17"): na rodada do K5
> de 11/10, com as escalas gravadas, a etapa 2 não melhorou a partida (0,4091) em 180 s, 0
> células diferentes, recontagem independente igual à ferramenta (`NUMEROS_TCC.md`, seção 13).
> **Correção de defeito de texto**, só no caminho sem prova: sem melhora do critério, a tela
> mostra a escala da etapa 1 e diz isso. Regressão (56, 58, 197, 219) e telas 8 e 12 OK
> (`resultados/v122_2026-10-11/`). Cronograma: texto do TCC de 09 a 25/10 (`DECISOES.md`,
> "2026-10-09 — Texto do TCC antecipado para 09/10").
>
> **13/10/2026 — v1.2.3: VERSÃO CITÁVEL DO TCC** (tag `v1.2.3` no commit desta nota; substitui a
> `v1.2.2`). **Correção de defeito: art. 67 com horários editáveis** (`DECISOES.md`,
> "2026-10-13 — Art. 67 com horários editáveis"; `resultados/relatorio_2026-10-13a.md`). (a) o
> gerador de pares proíbe a folga isolada abaixo de 24 h; (b) escala que reprova na conferência
> de descanso não é entregue (erro explícito na tela). Nenhum número muda: 544 + 96 XML
> idênticos byte a byte; regressão = Tabela 6; suíte da tela completa OK.

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
| ~~10/10/2026~~ **05/10/2026** | **Congelamento das funcionalidades — antecipado para 05/10** (decisão do Otávio, `DECISOES.md`, "2026-10-05 — Congelamento das funcionalidades antecipado"). Até 10/10 só entra correção de defeito, com esperado registrado antes. Nenhuma função nova. |
| 08–12/10/2026 | **Semana de testes**: diagnóstico e bateria de entradas variadas (`DECISOES.md`, "2026-10-06 — Cronograma"). |
| ~~14/10/2026~~ **16/10/2026** | **Congelamento de resultado numérico — adiado para 16/10** (decisão do Otávio, 06/10), para acomodar a semana de testes. Até lá, fechamento técnico (suíte, demonstração refeita se preciso, `v1.1`) e só correção de defeito, com esperado registrado antes. Depois, nenhum número novo entra. |
| ~~13–25/10/2026~~ **09–25/10/2026** | Texto do TCC, antecipado para 09/10 (`DECISOES.md`, "2026-10-09 — Texto do TCC antecipado para 09/10"). |
| 26–29/10/2026 | Melhoria de tela e textos de ajuda, com o rascunho com o orientador — sem mudar comportamento nem número; capturas finais refeitas no fim. |
| 19–25/10/2026 | *Cronograma de 19/10* (`DECISOES.md`, "2026-10-19 — Cronograma"): modificações na ferramenta (opção B, orçamento configurável). **Números congelados em 25/10** (substitui 16/10). |
| 26/10–01/11/2026 | Só escrita. 02–06/11: revisão do orientador. P18 cortada; P16 só se sobrar tempo. |
| ~~04/11/2026~~ **06/11/2026** | **Entrega** (adiada em 19/10). |

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
   *05/10:* corrigidos ("isto é", grau com acento, "Falta 1", plurais). Os testes da tela que
   leem esses textos (1–2, 4, 7.3, 8) ainda não rodaram depois da correção, por falta de
   memória; os textos foram conferidos sem solver.
   *05/10, noite:* **testes rodados, um por processo, todos OK** (1–2, 4, 7.3, 8a–8d). Antes,
   o caso 4 rodou com o esperado antigo ("isto e, 7") e FALHOU — o teste lê o texto. Os
   esperados de texto estavam atualizados desde o commit `9d81c5f`, antes de rodar. Os
   números saíram idênticos aos de 03/10: tentativas e menores quadros viáveis (40, 16, 40,
   24, 15, 5), horas do diagnóstico (2.688/2.464 h, 672/528 h), gap do 8b 1,03% com 20/20
   pedidos. Concluído.

*Demonstração de uso pela tela — concluída em 05/10 (noite).* Três rodadas, uma por processo,
com o Streamlit reiniciado entre elas: 30 pessoas (admite), 21 técnicos (admite, 13 turnos de
enfermeiro em posto de técnico), 20 técnicos (trava: "Falta 1; o menor quadro viável é 29",
diagnóstico "Combinação de regras"). Os cortes saíram onde a conta, registrada antes, previu
(`docs/demonstracao/cortes_esperados.md`). Capturas e planilhas em `docs/demonstracao/`. A
conta mostrou que o diagnóstico podia ter dado um motivo simples: P7, aguardando decisão.

*05/10, 20h:* **P7 implementada** (diagnóstico com teto pela alternância e férias no par;
`DECISOES.md`, "2026-10-05 — Diagnóstico da trava"); testes de diagnóstico e de texto OK.
**Demonstração a refazer, PARADA por regra:** o alerta da rodada de 30 pessoas é de proporção
de enfermeiros (8, o Parecer pede 10); a equipe da rodada 1 será ajustada por decisão do
Otávio, e só então entram o 20/11 como feriado e as três rodadas de novo. Ver
`resultados/relatorio_2026-10-05e.md`.

*05/10, 21h:* **demonstração refeita** com a equipe decidida (10 enfermeiros + 20 técnicos) e o
20/11 como feriado; alerta de proporção pelo grupo de pacientes de maior carga (`DECISOES.md`,
"2026-10-05 — Grau da proporção"). Os três cortes saíram onde a conta, registrada antes,
previu: 20 técnicos sem alerta, 19 com o alerta de QP, 18 trava pela alternância (menor quadro
viável 29). Ver `resultados/relatorio_2026-10-05f.md`. ~~Em aberto: P8~~ — *decidida em 05/10*: mantém o comportamento atual (avisa o empate, usa o maior percentual).

*Atualização de 05/10 (noite):* **P1 concluída** (`PROPOSTAS.md`); limite da etapa 2 na tela =
180 s, e a etapa 2 mostra a diferença de carga entre colegas no lugar do gap (`DECISOES.md`,
"Carga por contrato", item i). **Demonstração de uso pela tela: interrompida** pelo sistema por
falta de memória durante a rodada 1 (*depois concluída na noite de 05/10, ver acima*) (`docs/demonstracao/`; dados e roteiro prontos, só a captura
da entrada da rodada 1 saiu). Guia do usuário em `GUIA_DE_USO.md`; figuras do capítulo de
resultados em `resultados/figuras/` (`src/figuras_tcc.py`).
4. ~~**Arquivo de configuração** (pacote INRC + complemento). Menor prioridade: se não estiver
   pronto em 10/10, vira trabalho futuro.~~ *05/10:* saiu do TCC e virou trabalho futuro, por
   decisão do Otávio — ver `DECISOES.md`, "2026-10-05 — Arquivo de configuração vira trabalho
   futuro", e `PROPOSTAS.md`, P3. Não há código parcial dele.

**Dívida menor, sem prazo:**

- ~~**Destino de quatro notas do escopo anterior** em `docs/`:
  `nota_conferencias_contrato_2026-09-22.md`, `nota_intervalo_individual_2026-09-22.md`,
  `nota_piso_forcado_2026-09-22.md`, `para_orientacao_2026-09-23.md`. Vão para `historico/`
  ou ficam como metodologia ativa? Não decidido.~~
  *06/10:* decidido — as quatro **ficam em `docs/` como metodologia ativa** (`DECISOES.md`,
  "2026-10-06 — Notas de 22 e 23/09 ficam em docs/").
- ~~**O `README.md` tem três links mortos** para arquivos que foram para `historico/`.~~
  *05/10:* corrigido. Restavam duas referências ao `CONTEXTO_PROJETO.md`, que agora apontam
  para `historico/`; a terceira, ao `DECISOES.md`, já valia desde que ele voltou à raiz em
  29/09. A lista de documentos do README passou a incluir os arquivos ativos.

## 6. O que este repositório aprendeu errando

Está em `CLAUDE.md`, mas vale repetir porque é o critério mais útil que saiu do trabalho:

- **Conferência que compartilha premissa com o que confere não confere nada.**
- **Lista duplicada é o defeito** — o mesmo conjunto existia em três lugares e corrigir dois
  não mudou nada.
- **Resultado idêntico depois de uma correção é sinal de alarme**, não de estabilidade.

## 7. Como os ambientes se dividem (reescrita em 11/10)

**Claude Code, aqui no repositório**: código, experimentos, conferências, organização de
arquivos. É o **único que escreve** nesta pasta. Ao fim de cada sessão, atualiza o
`PASSAGEM.md` e commita.

**Chat de Orientação**: escopo, decisões, especificação da ferramenta. **Lê esta pasta direto**
(`D:\dev	cc-nrp`), só leitura. Começa pelo `PASSAGEM.md`.

**Chat de Redação**: texto do TCC. Lê esta pasta direto e escreve só em `D:\TCC\escrita`.

Não há mais upload: as cópias no Projeto do claude.ai foram aposentadas em 11/10, e a verdade
está no disco.

**Quem decide (regra de 29/09/2026).** Decisões de escopo e de formulação são tomadas pelo
Otávio com o chat de Orientação e registradas como decisões no `DECISOES.md` pelo Claude Code.
Não esperam validação do orientador; ele é informado na reunião.

**Os arquivos-ponte**: `PASSAGEM.md` (onde paramos e próxima tarefa), `LEIA_PRIMEIRO.md` (mapa
da pasta para os chats), este, `DECISOES.md`, `PROPOSTAS.md`, `resultados/NUMEROS_TCC.md` e
`VIRADA_ESCOPO_2026-09-24.md`. O bloco "LEVAR PARA O CHAT DE ORIENTAÇÃO", no fim de cada
resposta do Claude Code, diz o que mudou e o que reler. Decisão registrada aqui que o chat não
relê vira capítulo escrito com decisão superada.
