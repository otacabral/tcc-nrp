# Relatório de 05/10/2026 (e)

## Para o Otávio

- **Parei antes do item 3, pela sua regra:** o alerta da rodada de 30 pessoas é de **proporção de enfermeiros** (8, quando o Parecer pede 10). A equipe da rodada 1 depende da sua decisão. Os itens 3 (20/11) e 4 (refazer a demonstração) não foram feitos.
- **P7 implementada:** na trava, o diagnóstico agora mostra os motivos simples com os números. Para 20 técnicos: horas (324 h contra 312 h) e par 03–04/11 (28 plantões para 27 pessoas).
- **Textos corrigidos:** "Todos os 6 pedidos de folga foram atendidos."; o rótulo virou "Enfermeiro em posto de técnico".
- **O 20/11 foi escolha do roteiro.** A ferramenta não tem lista de feriados.
- **Decisão sua:** a equipe da rodada 1. Veja também a observação sobre o grau usado no alerta (item 0).

---

## 0. Antes de mexer

### a) Os alertas do COFEN

A conta foi refeita agora pela ferramenta, sem solver, e bate com a tela de 05d.

**Rodada de 30 pessoas, 1 alerta:**
> Alerta COFEN (não impede a escala): 8 enfermeiros em 30 profissionais; o Parecer pede ao menos 33% no grau intermediário, isto é, 10

- Conta: ceil(0,33 × 30) = ceil(9,9) = 10 enfermeiros exigidos; a equipe tem 8.
- O percentual vem do grau escolhido na tela, "Intermediário" (33%).

**21 técnicos (29 pessoas), 2 alertas:**
> 8 enfermeiros em 29 profissionais; o Parecer pede ao menos 33% no grau intermediário, isto é, 10

> quadro de 29 abaixo do QP completo do Parecer (30,05, com IST de 15%); o núcleo assistencial, sem IST, é 26,13

- Proporção: ceil(0,33 × 29) = ceil(9,57) = 10.
- QP:
  - horas por dia = 8 × 4 + 14 × 6 + 4 × 10 = 156 h;
  - CHS = média das cargas = (21 × 44 + 8 × 36) ÷ 29 = 41,79 h;
  - núcleo = 156 × 7 ÷ 41,79 = 26,13;
  - completo = núcleo × 1,15 = 30,05;
  - 29 < 30,05, por isso o alerta.

**20 técnicos (28 pessoas), 2 alertas:** os mesmos dois, com 28.
- Proporção: ceil(9,24) = 10.
- QP: CHS = (20 × 44 + 288) ÷ 28 = 41,71 h; núcleo 26,18; completo 30,10.

**Por que a rodada de 30 não tem o alerta de QP:** CHS = (22 × 44 + 8 × 36) ÷ 30 = 41,87 h; núcleo 26,08; completo 29,995, que a tela arredonda para 30,00. Como 30 ≥ 29,995, não há alerta.

**Como o alerta de 30 é de proporção de enfermeiros, parei antes do item 3.**

**Observação para a sua decisão sobre a equipe:**
- O alerta de proporção usa o **grau escolhido na tela** ("Intermediário", 33%).
- O caso tem 4 pacientes de **alta dependência**. A regra de 29/09 para graus misturados (`DECISOES.md`, "Ajustes da Etapa 2", `grau_de_maior_carga`) manda usar o maior percentual entre os graus presentes: alta dependência, **36%**.
- Por essa regra, o mínimo seria ceil(0,36 × 30) = **11** enfermeiros, não 10.
- Hoje a tela não aplica a regra de 29/09 ao alerta quando há pacientes informados; usa o grau do campo. Não mexi. É uma inconsistência entre a tela e a decisão de 29/09: escolha o critério ao ajustar a equipe.

### b) Por que o 20/11 entrou como dia útil

**Foi escolha do roteiro, não lista da ferramenta.** A ferramenta não tem lista de feriados embutida: feriado é demanda específica por data, lançada pelo usuário. O roteiro `docs/demonstracao/caso_clinica_medica.py` lista só 02/11 e 15/11 em `FERIADOS`. Portanto o item 3 é "reconfigurar o roteiro", não corrigir a ferramenta. Parado junto com o 4.

## 1. P7 — diagnóstico da trava

**Esperado registrado e commitado antes de implementar e rodar** (commit `7dc9bb9`):
- testes 7.3 e 7.4;
- entrada nova no DECISOES;
- P7 marcada como decidida.

**Implementação** (commit `bf089d9`), sem mexer no modelo nem no objetivo:
- `ferramenta.teto_horas`: o menor entre a carga contratual nos dias disponíveis e, no 12×36, turno mais longo × Σ ceil(bloco ÷ 2) por bloco de dias disponíveis. É limite superior: na escala real da rodada 1 de 05/10, ninguém passou dele (conferido no 7.4c).
- `ferramenta.motivos_da_trava` lista todos os motivos simples que disparam, nesta ordem:
  - **horas**: primeiro enfermeiros contra os tetos deles (motivo "Categoria"); depois técnicos contra os tetos deles mais a folga dos enfermeiros (motivo "Horas");
  - **par de dias seguidos no 12×36**: plantões do par contra as pessoas disponíveis em pelo menos um dos dois dias (motivo "Alternância"); se esse não disparar, o mesmo só para enfermeiros (motivo "Categoria");
  - **dia específico**.
- `diagnosticar` devolve (motivo principal, texto com um parágrafo por motivo, lista de motivos). O título da caixa junta os nomes, por exemplo "Horas · Alternância do plantão de 12 h".
- `ferramenta.piso`, que decide se um quadro vai ao solver, **não mudou**, porque isso mudaria quais quadros o solver tenta. Está registrado no DECISOES.

**Resultados, um teste por processo:**

| Teste | Resultado |
|---|---|
| 7.4a, clínica com 20 técnicos (feriados 02 e 15/11) | **Horas** + **Alternância**. Texto: "...20 técnicos trabalham no máximo 3132 h: faltam 324 h, que só enfermeiro pode cobrir. Depois do posto de enfermeiro, os enfermeiros têm 312 h de folga..." e "ter 03/11 e qua 04/11 somam 28 plantões...; descontadas férias e licenças, 27 pessoas estão disponíveis em pelo menos um dos dois dias" |
| 7.4b, com 21 técnicos | nenhum motivo dispara |
| 7.4c, tetos | Ana Ribeiro 168 h; Karen Dias 84 h; Gabriela Pires 144 h. Ninguém acima do teto na escala da rodada 1 |
| 7.3 | horas, alternância, categoria e dia **mantêm o motivo** e o menor quadro viável (16, 40, 24, 15). O antigo "combinação" passou a **Categoria** (672 h contra 667 h) + **Alternância** (sáb 09/01 e dom 10/01: 4 plantões para 3 pessoas), com menor quadro viável 5, como registrado antes. Nenhum motivo falso: todos os casos têm o quadro informado provado inviável |
| 1-2, 8 (8a–8d) | OK; diagnóstico de alternância com o texto novo |
| `regressao.py --todos` | OK: 56 / 58 / 197 / 219 |

**Defeito achado e corrigido no caminho.** A edição de textos de 05/10 (commit `9d81c5f`) tinha deixado a função `_faltam` definida duas vezes, porque a marca de seção que usei para inseri-la aparece duas vezes no arquivo. Era inofensivo, já que as duas cópias eram iguais, mas é exatamente o padrão "lista duplicada" do CLAUDE.md. Ficou uma só.

## 2. Textos

| Antes | Depois | Teste |
|---|---|---|
| "Pedidos de folga negados: 0, em 0 profissionais; no máximo 0 por pessoa." | "Todos os 20 pedidos de folga foram atendidos." (com um pedido só: "O pedido de folga foi atendido.") | 8b: OK |
| rótulo "Turnos de enfermeiro em posto de técnico" (cortado) | "Enfermeiro em posto de técnico", com a explicação "Turnos em que um enfermeiro cobriu vaga de técnico." na ajuda | 5: OK |

A planilha mantém o rótulo longo, porque lá não corta.

**Ainda não conferido em captura:** o rótulo novo cabe sem cortar na tela de 1.400 px. Isso fica para as capturas do item 4.

## 3 e 4. Parados

Não foram feitos, pela regra do item 0. Quando você decidir a equipe da rodada 1:
1. lanço o 20/11 como feriado no roteiro (igual ao 02/11);
2. refaço e commito a conta das transições (`conta_cortes.py`, `cortes_esperados.md`);
3. refaço as três rodadas, uma por processo.

O guia (`GUIA_DE_USO.md`) já foi ajustado: a tabela dos motivos explica as contas novas, e o exemplo avisa que as capturas de 05/10 mostram o diagnóstico antigo.

## 5. Commits

| Commit | Conteúdo |
|---|---|
| `7dc9bb9` | Esperados (7.3, 7.4, 5, 8b), DECISOES, P7 decidida, antes de implementar e rodar |
| `bf089d9` | Implementação da P7, textos, `_faltam` duplicada removida |
| o seguinte | Guia, ESTADO_ATUAL, este relatório |

---

## LEVAR PARA O PROJETO DE REDACAO

- **`DECISOES.md`**: entrada nova "2026-10-05 — Diagnóstico da trava: teto pela alternância e férias no par". Vigente; fecha a P7. É correção do diagnóstico, sem mudar modelo nem objetivo; o `piso` ficou igual.
- **`PROPOSTAS.md`**: P7 marcada como DECIDIDA.
- **`ESTADO_ATUAL.md`**: nota de 05/10, 20h — P7 feita; demonstração parada à espera da decisão sobre a equipe.
- **Para decidir no projeto de redação:**
  - a equipe da rodada 1, que hoje tem 8 enfermeiros, quando o Parecer pede 10;
  - qual grau vale para o alerta de proporção quando há pacientes de graus misturados: o do campo da tela (hoje) ou o maior percentual (regra de 29/09).
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
