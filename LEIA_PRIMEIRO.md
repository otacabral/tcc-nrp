# LEIA PRIMEIRO — mapa da pasta para os chats

**Atualizado em 11/10/2026** (reescrito na reorganização dos chats). Este arquivo diz o que é
cada arquivo de `D:\dev\tcc-nrp`, quais estão vigentes e em que ordem ler.

## Como os chats usam esta pasta

- Os chats **leem esta pasta direto**, no disco. Não há mais cópias no Projeto do claude.ai
  nem upload: a verdade está aqui.
- **Chat de Orientação:** só leitura.
- **Chat de Redação:** lê esta pasta e escreve só em `D:\TCC\escrita`.
- **Claude Code:** é o único que escreve nesta pasta. Ao fim de cada sessão, atualiza o
  `PASSAGEM.md` e commita.

## Onde o trabalho está (11/10/2026)

- **Versão citável do TCC: v1.2.2** (tag `v1.2.2`, 11/10). Diferença para a v1.2.1: a
  correção de defeito de texto da P17, só no caminho sem prova; regressão e telas 8 e 12 OK. A
  v1.2.1 (tag `v1.2.1`, commit `032dede`) tinha código idêntico ao da v1.2, mais 23 arquivos
  de evidência citados pelo `NUMEROS_TCC.md` que estavam fora do git.
- A v1.2 acrescenta à v1.1: **P15** (alerta, não trava, quando o descanso semanal fica abaixo
  de 35 h — Súmula 110 do TST — ignorando as bordas do período), **P14 + P17** (a etapa 2
  equilibra a carga mesmo sem prova de ótimo, partindo da escala da etapa 1, sem nunca piorar).
- **P17 fechada (11/10): sem defeito, com limitação.** Nos limites da tela, a etapa 2 não
  melhorou em nenhuma das 5 resoluções sem prova. No diagnóstico de 11/10 (só teste), o K5 com
  30 min em vez de 3 achou escala bem mais equilibrada com a mesma penalidade (diferença entre
  colegas 42 → 12 h e 30 → 12 h), só aos ~29 min; a quebra de simetria não ajudou em 3 min. A
  limitação é de tempo, não de alcance; a ferramenta não muda. Trabalho futuro: `PROPOSTAS.md`,
  P19. Números: `resultados/NUMEROS_TCC.md`, seção 13.
- **Validação encerrada em 09/10.** *Cronograma de 19/10* (`DECISOES.md`, "2026-10-19 —
  Cronograma"): 19 a 25/10, modificações na ferramenta (opção B, orçamento configurável);
  congelamento dos números em **25/10**; 26/10 a 01/11, só escrita; 02 a 06/11, revisão do
  orientador; entrega **06/11**. P18 cortada; P16 só se sobrar tempo.

## Ordem de leitura

1. **`PASSAGEM.md`** — onde a última sessão parou, próxima tarefa, pendências com a Redação.
2. **Este arquivo.**
3. **`ESTADO_ATUAL.md`** — onde o trabalho está e o que vem depois, com mais detalhe.
4. **`DECISOES.md`** — toda decisão de modelagem, com data, motivo e status. Vale o que a marca
   de status diz (vigente, superada, histórico). As entradas de 05/10 em diante são as que mais
   pesam agora.
5. **`PROPOSTAS.md`** — propostas decididas, descartadas e trabalhos futuros (P3, P19). P16 é a
   lista de melhorias de tela de 26-29/10; P18, a reorganização das pastas.
6. **`resultados/NUMEROS_TCC.md`** — todo número citável, com origem, comando, conferência e
   ressalva. É a fonte do capítulo de resultados. **Nenhum número vai ao texto sem estar aqui.**
7. **`VIRADA_ESCOPO_2026-09-24.md`** — o escopo atual (ferramenta, não comparação de regimes),
   parâmetros do Parecer COFEN e base legal.

## O que é cada arquivo

### Arquivos-ponte (vigentes, mantidos pelo Claude Code)

| Arquivo | Para quê |
|---|---|
| `PASSAGEM.md` | Passagem entre sessões: onde paramos, próxima tarefa, decisões, pendências com a Redação |
| `LEIA_PRIMEIRO.md` | Este mapa |
| `ESTADO_ATUAL.md` | Onde o trabalho está e o que vem depois |
| `DECISOES.md` | Diário de decisões de modelagem e implementação |
| `PROPOSTAS.md` | O que espera decisão; trabalhos futuros (P3, P19) |
| `resultados/NUMEROS_TCC.md` | Números citáveis com conferência |
| `VIRADA_ESCOPO_2026-09-24.md` | Escopo atual, parâmetros do Parecer, base legal |
| `GUIA_DE_USO.md` | Manual do usuário final (instalar, preencher, ler o resultado) |

### Relatórios de sessão do Claude Code (`resultados/`; histórico, consulta pontual)

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
| `relatorio_2026-10-11b.md` | Diagnóstico da etapa 2 no K5: 30 min melhora (0,4091 → 0,1364), simetria não; P19; item novo da P16 |
| `relatorio_2026-10-11c.md` | Reorganização dos chats; Sub-MIP do HiGHS; busca das 207 + 36 escalas de 18/09 |
| `fechar_v12/resumo.txt` | Saída do `fechar_v12.sh`: tudo OK, base da tag v1.2 |
| `fechar_v12/p17_otavio.log`, `p17_K5.log`, `p17_K6.log` | Logs da P17 nos três casos difíceis (09/10) |

### Apoio da bateria e da demonstração

| Arquivo | Para quê |
|---|---|
| `docs/bateria_entradas.md` | Desenho da bateria (14 áreas da tela, 3 níveis, 6 propriedades, camadas de falha) |
| `docs/demonstracao/cortes_esperados.md` | A conta registrada antes de rodar a demonstração da clínica (20/19/18 técnicos) |

### Referência técnica (podem estar desatualizados)

| Arquivo | Situação |
|---|---|
| `MAPA_CODIGO.md` | Inventário do código de 28/09. **Desatualizado** (fala em escalabilidade "rodando agora"); o papel de cada arquivo ainda vale |
| `CLAUDE.md` | Regras de trabalho do Claude Code nesta pasta |
| `README.md`, `requirements.txt` | Apresentação e bibliotecas do repositório |
| `docs/formato_instancias.md` | Formato XML das instâncias do INRC |
| `historico/escopo-comparacao-regimes/` | Documentos do escopo anterior (comparação de regimes): consulta, não referência ativa |

### Fora desta pasta (em `D:\TCC`)

| Arquivo | Onde |
|---|---|
| `Parecer-Normativo-1-2024.pdf` (fonte primária do COFEN) | `D:\TCC\acervo\normas\` |
| `Informe-Estrategico-…12X36.pdf`, `RT Informa - N. 20…12x36.pdf` (ADI 5994, acordo individual no 12×36) | `D:\TCC\acervo\normas\` |
| `00_Triagem_Etapa1.xlsx`, `Analise_Base_Literatura_NRP.docx` (triagem e síntese da literatura de NRP) | `D:\TCC\acervo\revisao_sistematica\artigos e analises\` |
| Literatura por camada (fundamentos, NRP, MILP, solvers…) | `D:\TCC\acervo\literatura\Fontes NRP\` |
| `REENQUADRAMENTO_TCC1.md` (o que no TCC 1 contradiz o escopo atual) | `D:\TCC\escrita\fontes\` |
| `TCC parte I .pdf` (TCC 1 entregue, escopo abandonado) | `D:\TCC\arquivo_morto\TCC1\01. seções em desenvolvimento\` |
| Santos et al. (2016), Ann Oper Res 239:225–251 (artigo de referência; no Projeto, `s1047901415946.pdf`) | `D:\TCCcervo\literatura\Fontes NRP\Camada 4 - Modelos IP e MILP para NRP (nucleo do trabalho)\Santos et al. (2016) - publicado.pdf` (achado pelo md5 em 13/10) |

## Como a ferramenta funciona, em uma linha por peça

`app.py` (tela) → `ferramenta.py` (comanda: conta, etapa 1, etapa 2, busca do menor quadro,
diagnóstico, planilha) → `instancia_br.py` (aplica CLT e COFEN e preenche o formato de
`instancia.py`) → `modelo.py` (escreve o modelo em Pyomo) → HiGHS (resolve) → conferência
independente fora do modelo (descanso medido no relógio) → planilha. O mesmo modelo, lido do
INRC por `parser.py`, reproduz os ótimos publicados (`regressao.py`): é isso que valida o motor.

O briefing completo (validações, perguntas de banca, limitações):
<https://claude.ai/code/artifact/1d045bdf-f8bd-40d1-a96d-effdcf888696>
