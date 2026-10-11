# LEIA PRIMEIRO — mapa dos arquivos deste projeto

**Atualizado em 11/10/2026.** Este arquivo diz o que é cada arquivo do projeto de redação,
quais estão vigentes e em que ordem ler. Qualquer chat novo deve começar por aqui.

## Onde o trabalho está (11/10/2026)

- **Versão citável do TCC: v1.2.2** (tag `v1.2.2`, 11/10). Diferença para a v1.2.1: a
  correção de defeito de texto da P17 (abaixo), só no caminho sem prova; regressão e telas 8 e
  12 OK. A v1.2.1 (tag v1.2.1, commit `032dede`) tinha código idêntico ao da v1.2 (tag enviada
  em 09/10; `resumo.txt` do `fechar_v12` termina em "TUDO OK"), mais 23 arquivos de evidência
  citados pelo `NUMEROS_TCC.md` que estavam fora do git.
- A v1.2 acrescenta à v1.1: **P15** (alerta, não trava, quando o descanso semanal fica abaixo
  de 35 h — Súmula 110 do TST — ignorando as bordas do período), **P14 + P17** (a etapa 2
  equilibra a carga mesmo sem prova de ótimo, partindo da escala da etapa 1, sem nunca piorar).
- **P17 fechada (11/10): sem defeito, com limitação.** Nos casos sem prova, a etapa 2 não
  melhorou em nenhuma rodada registrada (Otávio, K5 e K6 em 09/10; K5 em 11/10, com as
  escalas gravadas e recontadas; e o teste 8b). A garantia (nunca piora a etapa 1) vale por
  construção. A tela passou a dizer, nesse caso, "a da etapa 1" (defeito de texto corrigido
  na v1.2.2). Números: `NUMEROS_TCC.md`, seção 13; decisão: `DECISOES.md`, "2026-10-10 — P17".
- **Validação encerrada em 09/10.** Até 16/10 (congelamento dos números), só correção de
  defeito, com esperado registrado antes. Texto do TCC de 09/10 a 25/10; melhorias de tela de
  26 a 29/10. Reorganização das pastas (P18, opção A) em 16–17/10.

## Dois avisos sobre as instruções do projeto

Se as instruções do projeto ainda tiverem estas referências, elas estão mortas:
- **`CONTEXTO_PROJETO_2_REDACAO.md` não existe.** O papel dele é deste arquivo, do
  `ESTADO_ATUAL.md` e do `VIRADA_ESCOPO_2026-09-24.md`.
- **O projeto "INRC 1 · Códigos" não existe mais.** O código roda no **Claude Code**, no
  repositório `D:\dev\tcc-nrp`, que nenhum chat acessa. A ponte são os arquivos abaixo.

## Ordem de leitura

1. **Este arquivo.**
2. **`ESTADO_ATUAL.md`** — onde o trabalho está e o que vem depois.
3. **`DECISOES.md`** — toda decisão de modelagem, com data, motivo e status. Vale o que a marca
   de status diz (vigente, superada, histórico). As entradas de 05/10 a 10/10 são as que mais
   pesam agora.
4. **`PROPOSTAS.md`** — propostas decididas, descartadas e trabalhos futuros (P3). P16 é a lista
   de melhorias de tela de 26-29/10; P18, a reorganização das pastas.
5. **`NUMEROS_TCC.md`** — todo número citável, com origem, comando, conferência e ressalva. É a
   fonte do capítulo de resultados. **Nenhum número vai ao texto sem estar aqui.**
6. **`VIRADA_ESCOPO_2026-09-24.md`** — o escopo atual (ferramenta, não comparação de regimes),
   parâmetros do Parecer COFEN e base legal.

## O que é cada arquivo

### Ponte com o Claude Code (vigentes, atualizados pelo Claude Code)

| Arquivo | Para quê |
|---|---|
| `LEIA_PRIMEIRO.md` | Este mapa |
| `ESTADO_ATUAL.md` | Onde o trabalho está e o que vem depois |
| `DECISOES.md` | Diário de decisões de modelagem e implementação |
| `PROPOSTAS.md` | O que espera decisão; trabalhos futuros (P3) |
| `NUMEROS_TCC.md` | Números citáveis com conferência |
| `GUIA_DE_USO.md` | Manual do usuário final (instalar, preencher, ler o resultado) |

### Relatórios de sessão do Claude Code (histórico; consulta pontual)

Cada sessão do Claude Code termina num relatório. Servem para saber **como** algo foi feito;
o que eles decidiram já está no `DECISOES.md` e no `NUMEROS_TCC.md`.

| Relatório | Assunto |
|---|---|
| `relatorio_2026-10-06c.md` | Padrão das 36 h, correção do `validar.py`, caracterização do `medium_late05` |
| `relatorio_2026-10-06d.md` | Tag v1.0.1 |
| `relatorio_2026-10-06f.md` | Diagnóstico do caso 15+5 (não era defeito); material de estudo; desenho da bateria |
| `relatorio_2026-10-07a.md` | Bateria nível 1 + K1–K6: 24 casos, zero falhas |
| `relatorio_2026-10-08a.md` | K4 longo (queda por memória); propriedades 2 e 3; nível 3 preparado |
| `relatorio_2026-10-08b.md` | P12 (progresso na tela, limite de 20 min); feriado de 20/11 achado |
| `relatorio_2026-10-09a.md` | Demonstração refeita; v1.1; nível 3: 100 casos, zero falhas |
| `relatorio_2026-10-09b.md` | P15 (alerta de 35 h) e P14 |
| `relatorio_2026-10-09c.md` | P17 (etapa 2 partindo da etapa 1); pedido por turno (trabalho futuro); tolerância do HiGHS; comandos da v1.2 |
| `relatorio_2026-10-10a.md` | P17: leitura do código (sem defeito) e esperado da rodada do K5; v1.2.1 (23 arquivos de evidência versionados); P18 decidida |
| `relatorio_2026-10-11a.md` | P17 fechada (K5 sem melhora, recontagem = ferramenta); defeito de texto corrigido; v1.2.2; cronograma do texto (09–25/10) |
| `resumo.txt` | Saída do `fechar_v12.sh`: tudo OK, base da tag v1.2 |
| `p17_otavio.log`, `p17_K5.log`, `p17_K6.log` | Logs da P17 nos três casos difíceis: etapa 2 sem melhora sobre a etapa 1; diagnóstico aberto em 10/10 (rodada do K5, `DECISOES.md`) |

**Duplicatas no projeto de redação:** `relatorio_2026-10-07a.md` e `relatorio_2026-10-09a.md`
aparecem duas vezes cada. Vale a cópia **mais recente** (enviada em 09/10, 19:15); a mais
antiga pode ser apagada.

### Apoio da bateria e da demonstração

| Arquivo | Para quê |
|---|---|
| `bateria_entradas.md` | Desenho da bateria (14 áreas da tela, 3 níveis, 6 propriedades, camadas de falha) |
| `cortes_esperados.md` | A conta registrada antes de rodar a demonstração da clínica (20/19/18 técnicos) |

### Referência técnica (do repositório; podem estar desatualizados)

| Arquivo | Situação |
|---|---|
| `MAPA_CODIGO.md` | Inventário do código de 28/09. **Desatualizado** (fala em escalabilidade "rodando agora"); o papel de cada arquivo ainda vale |
| `CLAUDE.md` | Regras de trabalho do Claude Code no repositório |
| `README.md`, `requirements.txt` | Apresentação e bibliotecas do repositório |
| `formato_instancias.md` | Formato XML das instâncias do INRC |

### Escopo e TCC 1

| Arquivo | Para quê |
|---|---|
| `VIRADA_ESCOPO_2026-09-24.md` | Escopo atual, parâmetros do Parecer, base legal |
| `REENQUADRAMENTO_TCC1.md` | O que no TCC 1 contradiz o escopo atual. Escrito antes da virada de 24/09; o cabeçalho diz o que foi superado (título, objetivo, ordem de execução) e o que vale |
| `TCC parte I .pdf` | TCC 1 entregue, para escopo abandonado (estudo de caso em hospital) |

### Fontes e literatura

| Arquivo | Para quê |
|---|---|
| `Parecer-Normativo-1-2024.pdf` | Fonte primária do COFEN (QP, percentuais, graus misturados) |
| `Informe-Estrategico-…12X36.pdf`, `RT Informa - N. 20…12x36.pdf` | ADI 5994: acordo individual no 12×36 |
| `s1047901415946.pdf` | Artigo de referência (conferir na ficha antes de citar) |
| `00_Triagem_Etapa1.xlsx`, `Analise_Base_Literatura_NRP.docx` | Triagem e síntese da literatura de NRP para o referencial |

## Como a ferramenta funciona, em uma linha por peça

`app.py` (tela) → `ferramenta.py` (comanda: conta, etapa 1, etapa 2, busca do menor quadro,
diagnóstico, planilha) → `instancia_br.py` (aplica CLT e COFEN e preenche o formato de
`instancia.py`) → `modelo.py` (escreve o modelo em Pyomo) → HiGHS (resolve) → conferência
independente fora do modelo (descanso medido no relógio) → planilha. O mesmo modelo, lido do
INRC por `parser.py`, reproduz os ótimos publicados (`regressao.py`): é isso que valida o motor.

O briefing completo (validações, perguntas de banca, limitações):
<https://claude.ai/code/artifact/1d045bdf-f8bd-40d1-a96d-effdcf888696>
