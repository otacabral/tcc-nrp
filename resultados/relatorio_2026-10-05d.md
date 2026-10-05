# Relatório de 05/10/2026 (d)

## Para o Otávio

- **Demonstração pela tela concluída**, sem falta de memória: três rodadas (30 pessoas, 21 técnicos, 20 técnicos), com capturas e planilhas em `docs/demonstracao/`. Os cortes saíram exatamente onde a conta, registrada antes, previa.
- **Testes da tela afetados pelos textos: todos OK**, com os números idênticos aos de 03/10. O 9c deixou de exigir prova e passou.
- **Arquivo de configuração** registrado como trabalho futuro. Os links mortos do README foram corrigidos.
- **Decisão sua (P7, nova):** na trava com 20 técnicos, a ferramenta diz "combinação de regras", mas uma conta simples explica a trava. Melhorar isso é funcionalidade nova, e o congelamento é em 10/10.
- `git pull` traz tudo.

---

## 1. Teste 9c sem exigir prova

- **Esperado registrado antes de rodar** (commit `7f32730`): a amplitude atinge o piso de `08603c6` — enfermeiros 0, técnicos 4,55 pp; tela "nenhuma (0 h)" e "1 plantão (8 h)". Já não se exige prova. O motivo está anotado no teste: a prova dentro de 180 s depende da carga da máquina (146,9 s rodando sozinho; falhou com outro processo junto).
- **9c-tela, novo.** A etapa 2 é encurtada para 20 s, para terminar sem prova com certeza. Nem a tela nem a planilha podem dizer "provado".
- **Resultado:** o 9 inteiro passou. O 9c atingiu o piso e, desta vez, também provou dentro do limite; a prova agora é só informativa. O 9c-tela passou: a etapa 2 terminou sem prova, nenhum "provado" apareceu na tela nem na planilha, e a linha da diferença entre colegas apareceu.
- **DECISOES.md:** adendo ao item i da entrada "Carga por contrato".

## 2. Testes da tela afetados pela correção dos textos

- **a) O teste lê o texto?** Os esperados de texto já tinham sido atualizados no commit `9d81c5f`, junto com a correção e antes de qualquer rodada. Para conferir, voltei o caso 4 ao esperado antigo ("isto e, 7") só na cópia de trabalho e rodei. **Falhou**, mostrando o texto novo. Depois restaurei o arquivo.
- **b)** Os esperados já estavam commitados antes de rodar (`9d81c5f`).
- **c)** Rodados um por processo: 1-2, 4, 7.3 e 8. **Todos OK.**
- **d) Números idênticos aos de 03/10:**
  - tentativas e menores quadros viáveis: 40; 16; 40; 24; 15; 5;
  - horas do diagnóstico: 2.688/2.464 h e 672/528 h;
  - 8b: gap 1,03%, com 20 de 20 pedidos.

  Só o texto mudou.
- **ESTADO_ATUAL.md, item 3:** registrado e concluído.

## 3. Demonstração pela tela

### a) Dias especiais

Declarados no roteiro (`caso_clinica_medica.py`):

- **02/11 (Finados, segunda, primeiro dia):** feriado, 1 + 4 em cada turno.
- **15/11 (domingo):** feriado. Só o turno do dia muda, de 1 + 5 para 1 + 4.
- **20/11 (sexta):** lançado como **dia útil**. É feriado nacional desde 2024 (Lei 14.759/2023), e o caso não o tratou como feriado, ao contrário dos outros dois. Ficou declarado; mudar alteraria os números.
- **Primeiro dia:** sem continuidade com o período anterior (P3, trabalho futuro).

### b, d) As rodadas

Uma por processo, com o Streamlit reiniciado entre elas (`rodar_rodada.sh`):

| | Rodada 1: 8 + 22 = 30 | 21 técnicos (29) | 20 técnicos (28) |
|---|---|---|---|
| Veredito | "O quadro informado admite escala legal. Escala gerada." | idem | **"Falta 1; o menor quadro viável é 29. Escala gerada."** |
| Diagnóstico | — | — | **"Combinação de regras"** |
| Alertas do COFEN | 1: 8 enfermeiros em 30, pede 10 | 2: proporção; quadro abaixo do QP completo (30,05) | 2: proporção; abaixo do QP completo (30,10) |
| Quadro da escala | 30 | 29 | 29 (9 + 20) |
| Enf. em posto de técnico | 4 | **13** | **27** |
| Pedidos atendidos | 6 de 6 | 6 de 6 | 6 de 6 |
| Contrato cumprido | 75%–100% | 82%–100% | 82%–100% |
| Diferença entre colegas, enf. · téc. | 0,5 plantão (6,4 h) · 1,5 plantão (18,4 h) | 1 plantão (12 h) · 0,6 plantão (6,9 h) | 1 plantão (12 h) · 0,6 plantão (6,9 h) |
| Horas não utilizadas, enf. · téc. | 308 h · 184 h | 200 h · 116 h | 208 h · 108 h |
| Diferença entre categorias | +19 pp | +13 pp | +11 pp |
| QP núcleo · completo | 26,08 · 30,00 | 26,13 · 30,05 | 26,18 · 30,10 |
| Descanso | cumpre (36 h entre turnos, 36 h semanal, no máximo 1 dia seguido) | cumpre | cumpre |
| Pico de memória: servidor + solver · Chrome · roteiro | 302 · 598 · 59 MB | 466 · 595 · 59 MB | 297 · 611 · 58 MB |
| Menor memória livre do Windows | 646 MB | 1.525 MB | 2.926 MB |

**Sobre os números:**
- A rodada 1 pela tela deu os mesmos números da execução sem tela da tarde.
- Os picos de memória vêm do Windows (`PeakWorkingSetSize`), lidos antes de fechar o navegador.
- O pico do servidor inclui o solver, que roda dentro dele.

### c) Conta registrada antes da rodada 2, e a comparação

A conta ficou no commit `8d90ece`, antes da rodada 2: `docs/demonstracao/cortes_esperados.md`, gerada por `conta_cortes.py`, sem solver e sem as contas da ferramenta.

| Transição | Esperado pela conta | Saiu |
|---|---|---|
| Escala limpa → com alerta e enfermeiro em posto de técnico | "Limpa" não ocorre de 22 para baixo. O alerta de proporção existe em todo quadro de 25 ou mais. Com 22, a conta de horas não obriga enfermeiro em posto de técnico (sobram 12 h), mas não proíbe | com 22: 1 alerta e 4 turnos (outras regras obrigaram) |
| Mais alertas e mais enfermeiros em posto de técnico | 21: 2 alertas, ≥ 13 turnos | 21: 2 alertas, **13** |
| Trava pela CLT | **20**: horas (faltam 324 h de técnico contra 312 h de folga dos enfermeiros, com o teto pela alternância de 168 h) e par 03–04/11 (28 plantões para 27 disponíveis, com Karen de férias). Menor quadro viável **29**. Diagnóstico da ferramenta: "combinação de regras" | 20: trava, **29**, "Combinação de regras", 27 turnos na escala de 29 (mínimo da conta: 27) |

**Achado (P7, aguardando decisão).** O diagnóstico da ferramenta diz "combinação de regras" porque:
- a regra de alternância compara o par de dias com o quadro inteiro, sem descontar férias;
- a regra de horas usa o teto do contrato (176 h), não o da alternância (168 h), e não separa as horas de técnico.

A conta simples explica a trava. A proposta é corrigir as duas regras; é mudança de funcionalidade, então fica para sua decisão.

**Outros pontos que a tela mostrou** (só texto; não corrigi, porque não estavam no pedido):
- a frase "Pedidos de folga negados: 0, em 0 profissionais; no máximo 0 por pessoa" aparece mesmo quando todos foram atendidos;
- o rótulo "Turnos de enfermeiro em posto de técnico" sai cortado na largura de 1.400 px.

## 4. Arquivo de configuração

- **DECISOES.md:** entrada nova "2026-10-05 — Arquivo de configuração vira trabalho futuro", vigente. Altera a adição da especificação de 29/09; o motivo é o congelamento em 10/10 e a prioridade da demonstração.
- **PROPOSTAS.md:** acrescentado à P3.
- **ESTADO_ATUAL.md:** item 4 riscado.
- **Código parcial:** **nenhum**. Continuam o `instancia_br.escrever_xml` e o `parser.py`, que são anteriores e servem aos experimentos e ao avaliador oficial.

## 5. README

Restavam duas referências mortas ao `CONTEXTO_PROJETO.md`; agora apontam para `historico/escopo-comparacao-regimes/`. A terceira das contadas antes, ao `DECISOES.md`, já valia desde que ele voltou à raiz em 29/09. A lista de documentos passou a incluir os arquivos ativos.

## 6. Commits

| Commit | Conteúdo |
|---|---|
| `7f32730` | 9c sem exigir prova e 9c-tela, com esperados antes de rodar; adendo no DECISOES |
| `36c3335` | Arquivo de configuração como trabalho futuro; README |
| `8d90ece` | Dias especiais declarados; cortes esperados antes da rodada 2; P7 |
| `5b8975f` | Testes de texto OK; registro de pico de memória |
| `0ab97bb` | Rodada 1 pela tela |
| o seguinte | Rodada 2 pela tela, resultado ao lado do esperado, guia, ESTADO_ATUAL, este relatório |

---

## LEVAR PARA O PROJETO DE REDACAO

- **`DECISOES.md`**:
  - adendo ao item i de "Carga por contrato": o 9c não exige prova; o teste novo 9c-tela garante que nada diga "provado" sem prova;
  - entrada nova "2026-10-05 — Arquivo de configuração vira trabalho futuro", alterando a especificação de 29/09.
- **`PROPOSTAS.md`**:
  - P3 ganha o arquivo de configuração;
  - **P7 nova**: o diagnóstico da trava diz "combinação" quando uma conta simples explica (férias no par de dias; teto pela alternância). **Aguarda decisão.**
- **`ESTADO_ATUAL.md`**: item 3 (testes de texto concluídos), item 4 riscado, links do README corrigidos, demonstração concluída.
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
