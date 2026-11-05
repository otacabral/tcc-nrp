# Relatório das rodadas da v1.4.5 — caso A (entrada de 04/11) e caso B (05/11/2026, madrugada)

Decisão: `DECISOES.md`, "2026-11-04 — Caso A: entrada revista…; rodadas na v1.4.5" (itens a–g) e
"2026-11-05 — Limitações declaradas". Esperado commitado antes de rodar: `ESPERADO.md` (`b39dd13`).
Script: `docs/diagnostico/caso_a_v145.py --rodar` (`34810ad`), um processo por rodada, lançado
desacoplado às 01:47 de 05/11. Versão **v1.4.5** (`src/` idêntico à tag `634eeb5`: o próprio script
confere e grava `src_alterado: false`, `diff_src_v145: false` em cada JSON). Resultados brutos:
`rodadas/` (um `.json`, `.log`, XML da instância e da escala e saída do avaliador por rodada;
`resumo.txt`; `resultado_automatico.md`, escrito pelo script no fim).

**Máquina e solver (tempo só como limite operacional, nunca como resultado):** Intel i5-10210U,
11,8 GB, Windows 11, Python 3.11.9, HiGHS 1.15.1 (highspy, via Pyomo 6.10.1 appsi); avaliador
oficial em Java com `-Xmx6g` e `-Duser.timezone=UTC` (ver §0). Orçamento da tela: 60 min por rodada.

**Estado deste relatório:** **7 de 7 rodadas completas**, código 0 em todas, nenhuma PARADA por
memória. O mestre escreveu "FIM" às 03:55:58 de 05/11. Só o vigia em segundo plano da sessão do
Claude Code caiu, encerrado pelo sistema por falta de memória da máquina. O mestre rodava
desacoplado e não foi afetado.

## 0. Achado: o avaliador oficial quebra nesta janela de 2018 (horário de verão)

- Sintoma: `ArrayIndexOutOfBoundsException: Index 216 out of bounds for length 216` em
  `Schedule.<init>`, na escala de 28 dias a partir de 29/10/2018.
- Causa: o JVM roda no fuso do Windows (America/Sao_Paulo). O horário de verão de 2018 começou à
  0 h de **04/11/2018**, e essa meia-noite não existe no fuso. A conta de dias do avaliador perde
  um dia.
- Contorno: `JAVA_TOOL_OPTIONS=-Duser.timezone=UTC`, posto **só no ambiente do script**.
  `src/validar.py` não mudou.
- Controle (não compartilha premissa: compara a saída do próprio avaliador):
  - nas instâncias antigas de 2027 (sem horário de verão), a saída é **idêntica byte a byte** com e
    sem a opção (md5 em `A11_fixo_24_ordem1` e `A36_fixo_30_ordem2_conferencia`);
  - a leitura da penalidade continua certa com a linha extra "Picked up JAVA_TOOL_OPTIONS" na saída.
- **Pendência (decisão do Otávio):** defeito latente para qualquer janela com data de início do
  horário de verão brasileiro (até 2018). Corrigir `src/validar.py` é mudança em `src/`, não feita.

## 1. Rodada 1 — A36, classificação padrão, com e sem as linhas

| | Esperado (`ESPERADO.md` §1) | A36_fixo_padrao (33 linhas, Essencial) | A36_livre_padrao (sem linhas) |
|---|---|---|---|
| Frase da tela | "Faltam 5; o menor quadro viável é 28" se o 28 tiver escala | **"Faltam 5; o menor quadro viável é 28. Escala gerada."** | **igual** |
| Tentativas 23–27 | pela conta (piso 28) | piso, quem provou: conta | igual |
| Motivo | "Dois dias seguidos", dom 04/11 + seg 05/11, 27 contra 22 | **igual, palavra por palavra** | igual |
| Composição no 28 | 9 enf. + 19 téc., sem 2ª tentativa | **9 + 19**, primeira tentativa | igual |
| Mesmo menor quadro com e sem linhas | sim | **28 = 28** ✔ | |
| Etapa 1 | sem esperado | Essencial **2**, provado; Importante **25**, provado | Essencial + Importante (fundido) **0 e 15**, provado |
| Etapa 2 (min-max) | sem esperado | ok, **provada** | ok, **sem prova** (orçamento esgotado; "pode haver uma escala mais equilibrada") |
| Avaliador oficial | — | **sem violação de restrição dura** | **sem violação de restrição dura** |
| Descanso no relógio | ≥ 36 h depois de N e D12 | menor 36 h (D12 e N) | menor 36 h (D12 e N) |
| Tempo (operacional) | — | 394 s | 3.601 s (a etapa 2 usou o orçamento) |

**Esperado cumprido nas duas** (frase, motivo, composição, mesmo menor quadro, sem dura).

## 2. Rodada 2 — A36 no 28 (9 + 19, lido da rodada 1), classificação 1 × classificação 2

Classificação 1: Essencial = pedido de folga + linhas; Importante = enfermeiro em posto de técnico,
máximo de folgas seguidas (4), mínimo de turnos (10). Classificação 2 = a 1 com o máximo de fins de
semana seguidos (3) no Essencial e as linhas no Desejável (decisão g).

| Por nível (valor da ferramenta) | A36_fixo_class1 | A36_fixo_class2 |
|---|---|---|
| Frase | "O quadro informado admite escala legal. Escala gerada." | igual |
| Essencial | **2**, provado | **0**, provado |
| Importante | **45**, provado | **41**, provado |
| Desejável | — | **15**, provado |
| Etapa 2 | ok, provada | ok, provada |
| Avaliador oficial | sem violação de dura | sem violação de dura |
| Descanso no relógio | menor 36 h | menor 36 h |
| Tempo (operacional) | 11 s | 37 s |

Por critério, contado com peso 1 (todos os critérios das duas classificações, inclusive os que a
rodada não considera; total e pessoas atingidas):

| Critério | padrão fixo | padrão livre | class. 1 | class. 2 |
|---|---|---|---|---|
| Pedido de folga no dia | 0 | 0 | 0 | 0 |
| Linhas "Só este turno" (quebras) | **2** (5595, 3602) | — (sem linhas) | **2** (5976, 3602) | **15** (9 pessoas) |
| Máx. fins de semana seguidos (3) | 10 (10) | 17 (17) | **13** (13) | **0** |
| Enfermeiro em posto de técnico | 25 | 15 | 25 | 22 |
| Máx. folgas seguidas (4) | 29 (6) | 29 (8) | **19** (2) | **19** (2) |
| Mín. turnos (10) | 11 (6) | 11 (6) | 1 (1: 5976) | **0** |

As quebras das linhas foram recontadas fora da ferramenta (`medir_escala`, contra as 33 linhas da
entrada) e coincidem pessoa a pessoa com as da tela nas três rodadas com linhas.

**Direções (`ESPERADO.md` §3), as duas com prova em todos os níveis envolvidos:**
- máximo de fins de semana seguidos: classificação 2 (**0**) ≤ classificação 1 (**13**) ✔;
- quebras das linhas: classificação 2 (**15**) ≥ classificação 1 (**2**) ✔.

## 3. Inevitável × evitável (`ESPERADO.md` §4)

| Critério | Inevitável pela conta | O que as rodadas deram |
|---|---|---|
| Máx. folgas seguidas | 6137 ≥ 12; 5976 ≥ 7; total ≥ 19 | 6137 = 12 (padrão fixo, class. 1, class. 2) e 13 (livre); 5976 = 7 nas 4. Class. 1 e 2: **19, exatamente o inevitável** (o resto é evitável e some quando o critério é considerado) |
| Mín. turnos, 6137 | 0 | class. 1 e 2: **0** (6137 cumpre as linhas dele e faz 10 turnos) → confirma a divergência registrada: **não é inevitável** |
| Mín. turnos, 5976 | ≥ 2 só com a linha "Só N" cumprida | padrão fixo (linha dele cumprida): **2** ✔; class. 1 (linha quebrada 1 vez): **1**; class. 2 (4 quebras) e livre (sem linha): **0** → confirma: **evitável à custa da linha** |
| Linhas "Só este turno" | sem esperado | o mínimo no Essencial é **2**, provado, com e sem o mínimo de turnos no Importante (as pessoas mudam: 5595 + 3602 no padrão, 5976 + 3602 na class. 1) |

Logo, **o pedido dizia que 6137 e 5976 violam o mínimo de turnos "em qualquer escala"; as
rodadas mostram escala provada sem nenhuma violação de mínimo de turnos (class. 2)**. O inevitável
é só o das folgas seguidas, 19.

**Enfermeiro em posto de técnico** (cota inferior da conta, ≥ 15 no 28 com 19 técnicos): padrão
livre **15, exatamente a cota** (provado); padrão fixo 25 e class. 1 25, class. 2 22 (as linhas e os
outros critérios custam vagas). Divisão unidade × acrescidos (os 4 da unidade × os 5 enfermeiros
acrescidos pela busca):

| | padrão fixo | padrão livre | class. 1 | class. 2 |
|---|---|---|---|---|
| Os 4 da unidade | 6 | 5 | 1 | 8 |
| Os 5 acrescidos | 19 | 10 | 24 | 14 |

## 4. Etapa 2

Provada em padrão fixo, class. 1 e class. 2; **sem prova** no padrão livre (orçamento de 60 min
esgotado na etapa 2; a etapa 1 estava provada). Amplitude final (maior entre categorias): 0,045
(padrão fixo), 0,034 (livre), 0,307 (class. 1), 0,273 (class. 2).

## 5. Rodada 3 — HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA: A11, classificação 1, 23 pessoas

| | Esperado (`ESPERADO.md` §1, 11 h) | HIPOTESE_SENSIBILIDADE_A11_fixo_class1 |
|---|---|---|
| Conta prévia | não recusa o 23 (22 contra 22; piso 18) | piso 18; o 23 foi ao solver |
| Frase | sem esperado | **"O quadro informado admite escala legal. Escala gerada."** (4 + 19) |
| Essencial | sem esperado | **14**, provado (linhas: 5976 4 quebras, 4178 10) |
| Importante | sem esperado | **19**, provado = enfermeiro em posto de técnico **0** (cota 0 ✔) + folgas seguidas **19** (exatamente o inevitável ✔) + mínimo de turnos **0** |
| Etapa 2 | sem esperado | ok, provada |
| Avaliador | — | sem violação de dura |
| Descanso no relógio | D12 → 12 h (a hipótese), N → 36 h | menor 12 h depois de D12, 36 h depois de N ✔ |
| Tempo (operacional) | — | 13 s |

Fins de semana seguidos não entram na classificação 1 nem na contagem desta rodada (o script conta
os critérios da classificação 1 para a A11). Quebras recontadas fora da ferramenta: iguais.

## 6. Rodada 4 — caso B

- **B36_livre:** **"Não há escala legal até 101 profissionais; o menor quadro viável está acima
  disso."**, as 13 tentativas pela conta, 3 s, sem solver ✔ (igual ao esperado e a 21/10). Sem
  escala, sem avaliador.
- **HIPOTESE_SENSIBILIDADE_B11_livre** (HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA), sem
  esperado (`ESPERADO.md` §5: a conta não recusa o 89; piso 68):

| | v1.4.5 (05/11, esta rodada) | v1.4.1 (21/10, `NUMEROS_TCC.md` 15.1) |
|---|---|---|
| Frase | **"O quadro informado admite escala legal. Escala gerada; pode haver uma melhor."** | "… Escala gerada; pode haver uma melhor (gap 100,0%…)." |
| Quadro | 89 (15 enf. + 74 téc.) | 89 (15 + 74) |
| Essencial + Importante (fundido) | **0 e 1**, **sem prova** (limite inferior 0; gap 100%) | 0 e 1, sem prova (gap 100%) |
| Etapa 2 | ok, sem prova ("pode haver uma escala mais equilibrada") | — (etapa 2 pela soma, na v1.4.1) |
| Avaliador oficial (`-Xmx6g`) | **sem violação de dura**, na própria rodada | sem violação de dura, só na reconferência com `-Xmx6g` (na rodada, sem memória) |
| Descanso no relógio | D12 → 12 h, N → 36 h | D12 → 12 h |
| Tempo (operacional) | 3.602 s (etapa 1 até o limite de 1.800 s) | 3.602 s |

  **Mesmos valores da v1.4.1, e de novo sem prova.** A única violação no Importante é 1 turno de
  enfermeiro em posto de técnico. O limite inferior que o solver tem é 0, então a prova não fecha
  neste orçamento. Rodada sem as 33 linhas e sem contagem por critério com peso 1 (só o caso A
  tem conferência por classificação).

## 7. Dúvidas e escolhas (leitura conservadora)

- Vigia do Claude Code encerrado por memória: não religado (o próprio Claude Code pede para não
  religar sozinho). O mestre não depende dele e chegou ao FIM.
- Avaliador em UTC: nota no `DECISOES.md`, entrada "2026-11-04 — Caso A…", de 05/11.
- Os números da §1–§3 **não vão ao `NUMEROS_TCC.md`**: ficam no rascunho `RASCUNHO_15c.md`, pendente
  do ok do Otávio.
- A penalidade total do avaliador não vai ao texto (pesos do INRC gravados no XML); vai "sem
  violação de restrição dura".
