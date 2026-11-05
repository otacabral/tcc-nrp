# Caso A (entrada de 04/11) e caso B na v1.4.5 — esperado, ANTES das rodadas (05/11/2026)

Decisão: `DECISOES.md`, "2026-11-04 — Caso A: entrada revista pela leitura independente do Anexo B;
rodadas na v1.4.5". Entrada: `entrada.py` nesta pasta (caso A) e
`resultados/caso_b_2026-11-04/entrada.py` (caso B: a de 20/10 com a janela a). Tudo **sem solver**:
as contas abaixo saem de `ferramenta.piso`, `ferramenta.pares_de_dias` e `ferramenta.equipe`
chamados na entrada nova (`docs/diagnostico/caso_a_v145.py --esperado` refaz as tabelas), e
foram conferidas à mão pela conta escrita aqui. Premissa compartilhada: a conta usa a mesma regra
de descanso do modelo (`descanso_exigido`); confere a aritmética, não a regra.

## 1. Conta prévia do caso A, 23 pessoas, regra de 36 h (a regra da ferramenta)

Turnos que impedem qualquer turno no dia seguinte (36 h depois de turno de 12 h): **N e D12**.
Pessoas disponíveis em pelo menos um dos dois dias: 23 menos quem está de férias nos dois dias.

| Par (d, d+1) | Postos em d+1 | Postos de d em N ou D12 | Pessoas diferentes | Disponíveis | Excesso |
|---|---:|---:|---:|---:|---:|
| **dom 04/11 + seg 05/11** | M 6 + T 6 + N 5 = **17** | D12 5 + N 5 = **10** | **27** | 22 (6137 de férias) | **5** |
| dom 11/11 + seg 12/11 | 17 | 10 | 27 | 22 (6137) | 5 |
| dom 18/11 + seg 19/11 | 17 | 10 | 27 | 22 (5976) | 5 |
| dia útil + dia útil (ex.: qua 31/10 + qui 01/11) | 17 | N 5 | 22 | 22 | 0 |
| sáb + dom | D12 5 + N 5 = 10 | N 5 + D12 5 = 10 | 20 | 22 ou 23 | < 0 |

- **Par crítico: domingo + segunda** (três vezes no mês, empatados; a ferramenta cita o primeiro,
  04/11 e 05/11). Excesso 5 → **menor quadro ≥ 23 + 5 = 28**. Confere com o esperado pela
  Orientação: 17 + 10 = 27 pessoas diferentes contra 22 disponíveis.
- **Motivo da tela: "Dois dias seguidos"** (`PARES`), conferido sem solver: *"dom 04/11 e seg 05/11:
  17 postos na segunda + 10 no domingo em turnos que impedem a segunda (N, D12 …); são 27 pessoas
  diferentes, e, descontadas férias e licenças, 22 pessoas estão disponíveis em pelo menos um dos
  dois dias. Pela conta, faltam pelo menos 5 pessoas."* Não é a tarde com férias nem a categoria:
  só enfermeiros, o pior par dá 3 + 1 = 4 contra 4 (excesso 0); horas: 3.600 h demandadas contra
  3.878 h de teto (não aperta); alternância (limite efetivo 6): 18.
- **Composição no 28** (`ferramenta.equipe`, grau intermediário, 33%): **9 enfermeiros + 19
  técnicos** — os 5 acrescentados são enfermeiros (`ceil(0,33 × 28) = 10`, limitado a 4 + 5 = 9).
  Como os acréscimos já são todos enfermeiros, a varredura não tem segunda tentativa no 28. No 29:
  10 + 19; no 30: 10 + 20.
- **Esperado da rodada 1** (A36 com e sem linhas, classificação padrão): tentativas de 23 a 27 pela
  **conta**; o 28 vai ao solver. Se o 28 tiver escala: **"Faltam 5; o menor quadro viável é 28."**
  O desfecho no 28 **não tem esperado**: no 28 os três pares domingo + segunda ficam justos (27
  contra 27), ou seja, cada pessoa disponível trabalha num dos turnos contados desses pares. As
  linhas "Só este turno" não mudam a viabilidade (são preferência, não regra rígida): **se as duas
  rodadas decidirem, o menor quadro é o mesmo com e sem linhas.**

### Sob a hipótese de 11 h depois do D12 — HIPÓTESE DE SENSIBILIDADE, NÃO REGRA DA FERRAMENTA

`DESCANSO_POR_TURNO = {"D12": 11}`: só a N impede o dia seguinte. Domingo + segunda: 17 + N 5 =
**22** contra 22 → excesso **0**; todos os pares de dia útil também dão 22 contra 22. **A conta não
recusa o 23** (o piso fica em 18, o da alternância). O desfecho com 23 é do solver; **não tem
esperado** (todos os pares justos: se o 23 tiver escala, ela usa cada pessoa disponível em todo
par de dias, sem folga).

## 2. Sensibilidade da conta prévia (sem solver), regra de 36 h

| Equipe | Plantão diurno de fim de semana | Par crítico | Pessoas diferentes | Disponíveis | Excesso | Menor quadro ≥ |
|---|---|---|---:|---:|---:|---:|
| 22 (sem o 4309) | 0 enf. + 5 téc. | dom + seg | 27 | 21 | 6 | **28** |
| 22 | 1 enf. + 5 téc. | dom + seg | 28 | 21 | 7 | **29** |
| **23** | **0 + 5** | dom + seg | 27 | 22 | 5 | **28** |
| 23 | 1 + 5 | dom + seg | 28 | 22 | 6 | **29** |
| 24 (com o 6089 como técnico) | 0 + 5 | dom + seg | 27 | 23 | 4 | **28** |
| 24 | 1 + 5 | dom + seg | 28 | 23 | 5 | **29** |

- O **menor quadro da conta não depende da equipe** (22, 23 ou 24): quem a busca acrescenta não
  tem férias, então cada pessoa a menos na equipe é uma a mais que falta. A equipe só muda o
  "faltam". O enfermeiro no plantão de fim de semana soma 1 ao domingo e ao quadro.
- Com 1 enfermeiro no plantão, a conta só de enfermeiros também recusa: 3 + 2 = 5 contra 4
  (excesso 1); a do total (6) domina.
- Com 22 a equipe tem 32 linhas (o 4309 sai com a dele); com 24, 33 (o 6089 não tem linha).

## 3. Direções esperadas, classificação 2 × classificação 1 (mesmo quadro e composição)

- **Máximo de fins de semana seguidos (3): classificação 2 ≤ classificação 1.** Na 2 ele é
  Essencial; na 1, Não considerar. Comparação na conferência com peso 1, em que os dois são
  contados.
- **Violações das linhas "Só este turno": classificação 2 ≥ classificação 1.** Na 1 as linhas são
  Essencial; na 2 caem para Desejável, abaixo de tudo o que é considerado.
- As duas direções **só valem com prova** nos níveis envolvidos (Essencial nas duas rodadas e, na
  2, o Desejável). Sem prova, a diferença pode vir do tempo, não da classificação.

## 4. Violações inevitáveis (as férias contam como dias livres; não reduzem o mínimo de turnos)

Pela semântica do INRC, dia de férias é dia sem trabalho, e o bloco de folga encostado na borda
do horizonte conta (`avaliacao._folgas_consecutivas`; `modelo.py`, folgas consecutivas).

| Critério | 6137 (férias 31/10–15/11, 16 dias; 12 disponíveis) | 5976 (férias 15/11–25/11, 11 dias; 17 disponíveis) | Total inevitável |
|---|---|---|---:|
| Máximo de folgas seguidas (4) | ≥ 16 − 4 = **12** (em qualquer escala) | ≥ 11 − 4 = **7** (em qualquer escala; o bloco toca o fim da janela) | **≥ 19** |
| Mínimo de turnos (10) | **0**: dá para chegar a 10 cumprindo as linhas (abaixo) | **≥ 2 enquanto a linha "Só N" for cumprida**: teto 44 × 17 / 7 = 106,9 h → no máximo 8 noites de 12 h (96 h) | **≥ 2** (com as linhas cumpridas) |

- **Divergência com o pedido, registrada:** o pedido diz que 6137 e 5976 violam o mínimo de turnos
  "em qualquer escala". A conta não confirma para nenhum dos dois:
  - **6137** (técnico da tarde, linhas T e D12; T só em dia útil e D12 só no fim de semana, pela
    demanda): T em 29 e 30/10, T em 16/11, D12 em 17/11, T de 19 a 23/11 e D12 em 24/11 dão
    **10 turnos**, 72 h ≤ 75,4 h de teto, no máximo 6 dias seguidos (19–24/11), com as 36 h depois
    de cada D12 (sáb 17/11 → seg 19/11; sáb 24/11 → nada no domingo) e 12 h entre a T de sexta e o
    D12 de sábado. Logo, **0 inevitável**;
  - **5976**: o mínimo só é inevitável **com a linha "Só N" cumprida**. Com turnos de 6 h fora da
    linha, 10 turnos cabem nas 106,9 h. Nas rodadas com as linhas no Essencial (padrão, 1 e a de
    11 h), as linhas vêm antes do mínimo de turnos (Importante); o esperado é **≥ 2** se o nível
    Essencial fechar sem quebrar a linha dele. Na classificação 2 (linhas no Desejável, mínimo de
    turnos no Importante), pode ser evitado à custa da linha.
  - Escolha (conservadora): o relatório separa como inevitável só o que a conta prova (≥ 12 e
    ≥ 7 nas folgas seguidas; ≥ 2 do 5976 no mínimo de turnos, condicionado à linha cumprida), e
    mostra o resto como evitável, pessoa a pessoa.
- **Enfermeiro em posto de técnico (cota inferior pela conta, não inevitável de uma pessoa):** no
  28 e no 29 (19 técnicos), em cada um dos três pares domingo + segunda, os postos de técnico pedem
  14 + 9 = 23 pessoas diferentes e há 18 técnicos disponíveis → **≥ 5 por par, ≥ 15 no mês**. No 30
  (20 técnicos): ≥ 4 por par, ≥ 12. Sob a hipótese de 11 h, com 23: 14 + 4 = 18 contra 18 → cota 0.

## 5. Caso B na v1.4.5 (89; mesma entrada de 20/10, com a janela a)

Sem férias no caso B: só os dias da semana importam, e 29/10/2018 e 04/01/2027 são segundas. A conta
saiu **igual à de 20/10**:

- **B36:** domingo + segunda: 65 + 40 = 105 contra 89 → **piso 105 > 89 + 12 = 101**. Esperado:
  as 13 tentativas (89 a 101) pela **conta**, em segundos, sem solver, e a frase **"Não há escala
  legal até 101 profissionais; o menor quadro viável está acima disso."** (igual a 21/10). Sem
  escala: sem avaliador.
- **B11 (hipótese de sensibilidade, não regra da ferramenta):** 65 + 19 = 84 ≤ 89 (excesso −5);
  piso 68. A conta não recusa o 89; o desfecho é do solver, **sem esperado** (em 21/10, na v1.4.1,
  achou escala sem prova em 3.600 s). Avaliador com `-Xmx6g` (`src/validar.py`, `MEMORIA_JAVA`).

## 6. O que não tem esperado

- Valores por nível e por critério, em todas as rodadas;
- a etapa 2 (min-max, v1.4.5): status e amplitude;
- o desfecho no 28 (36 h) e no 23 (11 h), e se o solver prova cada nível no tempo.

## 7. O que não se refaz

**A bateria HiGHS × SCIP não é refeita:** a regra de troca de 22/10 não se reabre, o INRC não
mudou e a etapa 1 é idêntica na v1.4.5 (`identidade_v145.py`: 162 XML e LPs da etapa 1 iguais). A
seção fica como está, declarada como rodada anterior, com a entrada de 21/10.
