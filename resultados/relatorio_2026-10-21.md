# Relatório de 21/10/2026 — fase 2 (casos A e B) e preferência de dias seguidos e de turnos

Pedido da Orientação de 21/10 (manhã), Partes 0 a 6. Sem push. DECISOES e esperado commitados
antes de implementar (`00f7726`). Tempo é limite operacional, nunca resultado: máquina Intel
i5-10210U, 11,8 GB de RAM, HiGHS 1.15.1 via `appsi_highs` (Pyomo 6.10.1), uma rodada por
configuração.

Versão das rodadas da fase 2: **v1.4.1** (`9afa334`, sem alterações locais em `src/`, conferido
pelo `fase2.py`). Suíte da v1.4.1: TUDO OK (`resultados/v141_2026-10-20/suite/resumo.txt`).

## Parte 0 — Fase 2 (resultados de `resultados/fase2_2026-10-21/`)

Classificação padrão, orçamento de 60 min por rodada, 1.800 s por nível e na etapa 2. Ordem:
A36_livre, A36_fixo, A11_fixo, B11_livre, B36_livre. `resumo.txt`: TUDO OK.

### Achado: a conferência do B11 no avaliador não tinha rodado

No B11_livre (89 pessoas) o avaliador oficial parou com `OutOfMemoryError: Java heap space` nas
duas chamadas (heap padrão da JVM nesta máquina, ~3 GB). O `validar._numero` leu como penalidade
o **43** do stack trace (`ScheduleEvaluator.java:43`), e o `fase2.py` registrou "sem violação de
dura" numa saída sem nenhuma linha de avaliação. **Conferência que não rodou entrou como
conferência aprovada.**

- **Reconferido** com `java -Xmx6g` (mesmo XML da instância e da escala, sem mexer na escala):
  saída detalhada completa, **nenhuma linha "Hard constraints"**, penalidade do avaliador
  **714**. Arquivos: `HIPOTESE_SENSIBILIDADE_B11_livre_escala_avaliador_Xmx6g.txt` e `..._p.txt`.
  Os originais ficam como estão (evidência).
- Nas outras três escalas a saída do avaliador está completa, e o número da saída curta (`-p`)
  bate com o da saída detalhada.
- **Correção de defeito** (`DECISOES.md`, "2026-10-21 — Correção de defeito: avaliador sem
  memória lido como 'sem violação'"): `validar._executar` falha alto (`AvaliadorIndisponivel`) se
  o código de saída não for 0 ou se aparecer "Exception in thread"; a JVM roda com `-Xmx6g`.
  Testado: B11 → 714, A36_livre → 288, e com `-Xmx64m` forçado → erro, não número.

### As cinco rodadas

| Rodada | Frase da ferramenta | Menor viável | Quem provou | Tempo total (limite operacional) | Avaliador oficial |
|---|---|---:|---|---|---|
| A36_livre | "Faltam 6; o menor quadro viável é 30. Escala gerada." | **30** (10 enf. + 20 téc.) | 24–29: **conta** prévia (sem solver); 30: solver (etapa 1 provada) | 1.813 s (etapa 1 em ~12 s; etapa 2 até o limite de 1.800 s) | **sem violação de dura**; penalidade INRC 288 |
| A36_fixo | "Faltam 6; o menor quadro viável é 30. Escala gerada." | **30** (10 + 20) | 24–29: conta; 30: solver (provado) | 1.807 s (etapa 1 em ~6 s) | **sem violação de dura**; 216 |
| A11_fixo — HIPÓTESE DE SENSIBILIDADE | "O quadro informado admite escala legal. Escala gerada." | 24 (4 + 20) | solver (provado) | 146 s | **sem violação de dura**; 96 |
| B11_livre — HIPÓTESE DE SENSIBILIDADE | "O quadro informado admite escala legal. Escala gerada; pode haver uma melhor (gap 100,0%…)." | 89 (15 + 74), viável **sem prova** | solver: achou escala, não provou o ótimo da etapa 1 | 3.602 s (etapa 1 até o limite de 1.800 s; etapa 2 sem melhora) | **sem violação de dura** só na reconferência com `-Xmx6g`; 714 |
| B36_livre | "Não há escala legal até 101 profissionais; o menor quadro viável está acima disso." | acima de 101 (piso 105) | 89–101: **conta**, sem solver | 0 s (nenhum solver) | — (sem escala) |

Detalhes que valem para o texto:
- **Descanso no relógio** (A36, A11, B11): conferência aprovada; menor descanso depois de D12 e
  de N = 36 h nas de 36 h; nas de 11 h, D12 → 12 h e N → 36 h. Essa conferência compartilha a
  premissa com o modelo (`descanso_exigido`); a da cobertura é externa (avaliador).
- **Diagnóstico** de A36 e B36: "Dois dias seguidos" — "A conta prévia do menor quadro provou, sem
  o solver…": A, dom 17/01 e seg 18/01, 17 + 11 = 28 contra 22 disponíveis (faltam ≥ 6); B, dom
  10/01 e seg 11/01, 65 + 40 = 105 contra 89 (faltam ≥ 16). Igual aos `ESPERADO.md` dos casos A e
  B ("Depois da Parte 7").
- **"Só este turno"** (A36_fixo e A11_fixo): 0 descumpridas, nas duas.
- **Alertas do COFEN**: A, 4 enfermeiros em 24 (o Parecer pede ≥ 8 no grau intermediário); B, 15
  em 89 (pede ≥ 30). Alerta, não regra.
- **Penalidade do avaliador** é a do INRC com os pesos que a ferramenta grava no XML; não é o
  objetivo da ferramenta e não compara rodadas. Vai ao texto só "sem violação de dura".

### Caso A: a composição do quadro de 30

- **10 enfermeiros + 20 técnicos.** A busca acrescentou os 6 como enfermeiros: a regra `equipe`
  (`ferramenta.equipe`) põe primeiro enfermeiros até max(⌈33% × 30⌉ = 10, o que a demanda de
  enfermeiro exige em horas), pela proporção do COFEN para o grau intermediário. Aqui a regra e a
  segunda composição ("acréscimos como enfermeiros") coincidem; só uma foi ao solver.
- **Enfermeiro em posto de técnico:** **13 turnos** no A36_livre (8 pessoas) e 14 no A36_fixo (8
  pessoas). Recontado fora da ferramenta, dos XMLs da instância e da escala (habilidades de cada
  pessoa × habilidade de cada turno): 13 e 14, iguais ao resultado por critério.

**Limitação declarada.** A busca do menor quadro tenta, em cada tamanho, só a composição da regra
`equipe` e "todos os acréscimos como enfermeiros". O **30 vale para qualquer composição**: a conta
prévia recusa 29 pelo total de pessoas (28 postos contra o que 29 pessoas, menos as 2 de férias,
podem cobrir), sem depender da mistura, e 30 tem escala. Mas **a composição de 10 + 20 não é ótimo
de custo**: outra mistura de 30 (menos enfermeiros) pode também ter escala, e não foi testada.

## Proposta para o `NUMEROS_TCC.md` — **NÃO GRAVADA; o Otávio aprova antes**

> ## 15. Casos realistas A e B (fase 2, 21/10/2026)
>
> Origem: `resultados/fase2_2026-10-21/` (JSON, `.txt`, XML da instância e da escala, saída do
> avaliador, `resumo.txt`). Comando: `docs/diagnostico/rodar_fase2.sh` (um processo por rodada,
> `docs/diagnostico/fase2.py`). Versão **v1.4.1** (`9afa334`). Entradas:
> `resultados/caso_a_2026-10-20/entrada.py` e `caso_b_2026-10-20/entrada.py` (Massens, 2019).
> Esperados commitados antes: os `ESPERADO.md` das duas pastas. Classificação padrão, orçamento
> 60 min, 1.800 s por nível e na etapa 2. **Afirmação fraca:** uma rodada por configuração;
> tempos são limite operacional (i5-10210U, 11,8 GB, HiGHS 1.15.1 via `appsi_highs`).
>
> | Valor | O que mede | Conferência | Ressalva |
> |---|---|---|---|
> | caso A, 36 h: **faltam 6; menor quadro viável 30** (turno fixo e rodízio livre) | 24–29 recusados pela conta prévia (dom 17 + seg 18/01: 17 + 11 = 28 postos contra 22 disponíveis); 30 com escala, etapa 1 provada | cobertura: **avaliador oficial, sem violação de dura**; descanso no relógio: menor 36 h depois de D12 e de N (compartilha a premissa com o modelo); conta à mão no `ESPERADO.md` (≥ 30) | o 30 vale para qualquer composição; a composição 10 enf. + 20 téc. é a da regra `equipe` (proporção do COFEN), **não ótimo de custo** |
> | caso A, 30 = 10 enf. + 20 téc.; **13 turnos** de enfermeiro em posto de técnico (rodízio livre; 14 no turno fixo) | composição e uso de enfermeiro em vaga de técnico na escala entregue | recontado dos XMLs, fora da ferramenta | a busca tenta só duas composições por tamanho |
> | caso B, 36 h: **não há escala legal até 101** | 89–101 recusados pela conta prévia (dom 10 + seg 11/01: 65 + 40 = 105 contra 89) | conta à mão no `ESPERADO.md` (≥ 105) | a busca vai até 89 + 12; o menor viável não foi determinado (≥ 105 pela conta, que é condição necessária) |
> | **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA:** com 11 h depois do D12 (`DESCANSO_POR_TURNO = {"D12": 11}`), A (turno fixo) admite 24, provado; B admite 89, **sem prova** (gap 100%) | o quanto a regra das 36 h depois do D12 pesa no quadro | avaliador oficial, sem violação de dura (B reconferido com `-Xmx6g`: na rodada, o avaliador tinha parado sem memória); descanso no relógio: D12 → 12 h | parâmetro de pesquisa, fora da tela; o texto não afirma que o hospital descumpre a lei ("a regra, como modelada, segue o art. 59-A") |

## Parte 1 — DECISOES (`00f7726`, antes do código)

- "2026-10-21 — Máximo de dias seguidos e máximo de turnos também como preferência" (MUDANÇA DE
  FORMULAÇÃO; revisa o item c de "2026-10-19 — Opção B"; a marca de revisão foi posta no item),
  com seis decisões de implementação: famílias próprias no contrato, fora do XML; padrão "Não
  considerar", limites padrão 5 e 18 (contrato 0 do `medium_late05`); limite usado =
  min(preferência, legal); no 12×36 a linha de dias some; contagem fora do modelo pelo
  `avaliacao.py`; testes da tela atualizados com registro.
- "2026-10-21 — Correção de defeito: avaliador sem memória lido como 'sem violação'".

## Parte 2 — `modelo.py` (e onde mais)

- `src/instancia.py`: `Contrato.pref_max_consecutive_working_days` e `pref_max_num_assignments`,
  `Flexivel.ausente()` por padrão, fora de `RESTRICOES` (não vão ao XML).
- `src/modelo.py`: duas famílias novas, com folga α e a mesma expressão do INRC —
  α ≥ Σ_{d=t..t+Lp} y − Lp (janela) e α ≥ Σ_d y − γp. Só existem quando ativas. As rígidas (máximo
  de dias seguidos, teto de turnos, teto de horas) não mudaram.
- `src/prioridades.py`: os critérios "max_dias_seguidos" e "max_turnos" deixam de ser "já
  garantido pela CLT" e apontam para as famílias novas; `limite_usado` = min(preferência, legal);
  máximo de violações como as outras famílias "máximo" (D − limite por pessoa); resultado por
  critério pelo `avaliacao.py` com a família INRC de mesma expressão no limite da preferência
  (`violacoes_preferencia`).

## Parte 3 — Tela (`src/app.py`)

- "Máximo de dias seguidos (preferência)", logo abaixo do campo rígido do hospital (que ficou como
  estava), com importância e limite; o limite não passa do máximo rígido informado. Oculta no
  12×36, como o campo rígido.
- "Máximo de turnos no período", com importância e limite; o limite não passa do teto legal de
  turnos do contrato (na tela padrão, 14). Padrão: "Não considerar".

## Parte 4 — Esperado e testes

Esperado: `resultados/preferencias_2026-10-21/ESPERADO.md` (commitado antes do código, com um
acréscimo a posteriori — ver (c)).

- **(b) controle — OK.** No P01: o padrão não tem família `pref_`; com dias 4 (Importante) o LP
  muda e contém `pref_max_consecutive_working_days`; com turnos 10, `pref_max_num_assignments`;
  acima do legal (9 dias, 999 turnos), as duas existem e o limite usado é o legal (6 dias, 22
  turnos).
- **(c) caso pequeno — o esperado de 56 estava errado; deu 96, e a contagem bate.** (c1) Lp = 4
  em Importante, rígida 6, 14 técnicos: "admite", provado, maior sequência 6 na escala e no
  relógio, descanso aprovado; violações acima de 4 contadas no script, das sequências da escala:
  **96 = 96** do resultado por critério. (c2) com turnos γp = 23 em Desejável: "em sequência, 2
  blocos", dias 96 = 96, turnos **14 = 14** (o esperado). **Erro do esperado:** a conta dos 56
  ignorou que a cobertura exige 2 folgas em todos os dias, e sequências 5-5-5-5-4 só põem folgas
  em 8 dias. A conta certa, feita **depois** de ver o resultado: 14 × 24 janelas de 5 dias, no
  máximo 2 × 120 quebradas por folgas → ≥ 96, e o solver atingiu e provou 96. Registrado no
  ESPERADO como acréscimo a posteriori; o teste passa a esperar 96 (coerência, não previsão).
- **(a) identidade 243/243** e **(d) regressão**: OK nesta sessão (Parte 5); a suíte do Otávio
  (`fechar_v142.sh`) refaz as duas.
- **(e) identidade na fase 2 — OK, sem solver:** 8 casos (A36_livre, A36_fixo e A11_fixo com
  acréscimos 0 e 6; B11_livre e B36_livre com 0), cada um com o `DESCANSO_POR_TURNO` da rodada:
  **24 de 24 arquivos idênticos** à v1.4.1. Conferido que a gravação da v1.4.1 usou o código do
  worktree (`codigo de D:\dev\tcc-nrp-v141`; o `Contrato` de lá não tem os campos novos).
- **Testes da tela** (rodados à parte, antes da suíte): pref-tela (novo), opB-d, opB-tela e opB-e
  — **todos OK**, com as atualizações registradas (opB-e: "admite/3 x admite/3" e "admite/13 x
  admite/13", com as duas preferências no Essencial). O pref-tela preenche a equipe antes de conferir o campo (sem
  equipe a instância não monta e não há teto) — ajuste do teste, registrado no ESPERADO.

## Parte 5 — Suíte da v1.4.2

- Worktree de leitura `D:\dev\tcc-nrp-v141` na tag v1.4.1 (criado nesta sessão).
- `docs/diagnostico/fechar_v142.sh`: o conteúdo do `fechar_v141.sh` com a identidade contra a
  v1.4.1, mais `pref_controle`, `pref_fase2_v141`/`_nova`/`_comparar`, `pref_caso_pequeno` e o
  teste de tela `pref-tela`. `RETOMAR=1` como nas anteriores.
- Teste sem solver (`PULAR_SOLVER=1 V142_DATA=teste_script`): **TESTE DO SCRIPT OK** —
  `id_comparar` e `id_comparar_regras` **243 de 243 idênticos** à v1.4.1 (é o (a), já visto
  aqui); `id_controle` muda (ok); `pref_controle` OK; `pref_fase2_comparar` 24 de 24 idênticos;
  `piso_seguranca`, `piso_controle` e `piso_casos` OK. `RETOMAR=1` pulou tudo e terminou em
  "TESTE DO SCRIPT OK". A pasta `resultados/v142_teste_script/` foi apagada.
- **(d) regressão**, rodada à parte nesta sessão: sprint01 56, sprint02 58, long01 197, long02
  219 — "regressao OK: otimo provado, Tabela 6".
- Testes da tela rodados à parte, antes da suíte: ver "Testes da tela" na Parte 4.

## Parte 6 — Registros

`MAPA_CODIGO.md` (arquivos novos e alterados) e `PASSAGEM.md` (próxima tarefa: suíte da v1.4.2,
com o RETOMAR) atualizados.

## Pendências com a Redação

- Números da fase 2 só depois de o Otávio aprovar a seção 15 proposta acima. A11 e B11 só como
  "HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA".
- O `GUIA_DE_USO.md` ainda não cita as duas preferências novas (linhas da tela "Máximo de dias
  seguidos (preferência)" e "Máximo de turnos no período" com campo e nível).
- A preferência não tem conferência no avaliador oficial (o XML só tem a versão rígida, com o
  limite legal); a contagem é do `avaliacao.py`.

## LEVAR PARA O CHAT DE ORIENTAÇÃO

- `resultados/relatorio_2026-10-21.md` (este): fase 2, achado do avaliador sem memória no B11
  (reconferido: 714, sem violação de dura), composição do quadro de 30 e limitação declarada,
  proposta da seção 15 do `NUMEROS_TCC.md` (não gravada), preferências implementadas e testadas.
- `DECISOES.md`: duas entradas novas de 21/10 (preferência de dias seguidos e de turnos; correção
  de defeito do avaliador sem memória) e a marca de revisão no item c de "2026-10-19 — Opção B".
- `resultados/preferencias_2026-10-21/ESPERADO.md`: esperado da v1.4.2, com o acréscimo a
  posteriori (o 56 do caso pequeno estava errado; 96, com a conta).
- `resultados/fase2_2026-10-21/`: resultados da fase 2 e a reconferência do B11 com `-Xmx6g`.
- `MAPA_CODIGO.md` e `PASSAGEM.md`: atualizados (próxima tarefa: suíte da v1.4.2).
- `NUMEROS_TCC.md`: **sem mudança** (a seção 15 espera a aprovação do Otávio).
