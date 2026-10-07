# Bateria de entradas variadas — desenho

**Desenhado em 07/10/2026. NÃO RODADO.** Só roda depois que a parte A do diagnóstico estiver resolvida, e por decisão do Otávio (`DECISOES.md`, "2026-10-06 — Cronograma": semana de testes de 08 a 12/10).

Os casos e o esperado de cada um saem de `docs/diagnostico/bateria_desenho.py`, que só faz conta, sem solver.

---

## C1. Áreas editáveis da tela

Levantadas de `src/app.py`; a chave do campo entre parênteses.

| # | Área | Campo na tela | O que varia |
|---|---|---|---|
| 1 | modelo de turnos | "Modelo de turnos" (`modelo`) | 12×36; 8 h em três turnos; 6 h de dia + noturno de 12 h |
| 2 | horários | tabela de turnos (`turnos_<modelo>`) | nome, início e fim, em hora cheia; linhas a mais ou a menos |
| 3 | definição de fim de semana | "Fim de semana" (`fds`) | sábado e domingo; sexta a domingo |
| 4 | início | "Início (segunda-feira)" (`inicio`) | qualquer segunda; atravessar mês ou ano |
| 5 | composição | "Enfermeiros", "Técnicos e auxiliares" (`n_enf`, `n_tec`) | quantidades, inclusive 0 técnicos |
| 6 | nomes | "Nomes (opcional)" (`nomes_enf`, `nomes_tec`) | com e sem; acento; nome repetido |
| 7 | cargas | tabela de carga semanal (`cargas_<n>`) | 30, 36, 40, 44 h por pessoa |
| 8 | férias e licenças | tabela "Férias e licenças" (`indisp`) | pessoa, de, até |
| 9 | pedidos de folga | tabela "Pedidos de folga" (`pedidos`) | pessoa, data |
| 10 | demanda por turno | `g_<turno>_enf`, `g_<turno>_tec` | enfermeiros e técnicos por turno |
| 11 | fim de semana próprio | caixa "Fim de semana com demanda própria" (`com_fds`) e `f_<turno>_enf/tec` | outra demanda no fim de semana |
| 12 | grade por data | "Demanda específica por data" (`especifica_…`) | feriados, eventos; dia a dia |
| 13 | pacientes | "Conferir com o COFEN" (`pac_<grau>`) | pacientes por grau; graus misturados; empate de carga |
| 14 | grau | "Grau de dependência predominante" (`grau`) | 5 graus; só vale sem pacientes |

## C2. Três níveis

### Nível 1 — cobertura por pares (18 casos)

Cada caso edita de 6 a 7 áreas. Os 18 juntos cobrem os **91 pares** das 14 áreas, conferido pelo gerador ("faltam: []"). O esperado vem da conta independente, que só dá condições necessárias:

1. **horas:** demanda do período contra a soma de (carga × dias disponíveis ÷ 7), no total e só para enfermeiros;
2. **ocupados por dia:** o descanso entre turnos é medido dos horários (36 h depois de turno de 12 h ou mais; 11 h nos demais). Se um turno impede todos os do dia seguinte, quem o fez na véspera não trabalha hoje. Então os postos de hoje mais os desses turnos da véspera têm de caber nas pessoas disponíveis. O mesmo vale só para enfermeiros.

"GERA ESCALA (esperado)" é expectativa, não prova. Um "sem escala" nesses casos é exatamente o que a bateria quer achar.

| Caso | Áreas editadas | Modelo | Equipe | Esperado pela conta | Folgas (h; h enf.; ocupados/dia; ocupados/dia enf.) |
|---|---|---|---|---|---|
| P01 | composição, fds_def, horários, início, modelo, nomes | 8h | 5+9 | GERA ESCALA (esperado) | 448; 208; 5; 2 |
| P02 | cargas, demanda, fds_própria, férias, modelo, pedidos | 6+12 | 6+6 | GERA ESCALA (esperado) | 676; 308; 3; 1 |
| P03 | cargas, grade_data, grau, horários, modelo, pacientes | 12x36 | 5+10 | GERA ESCALA (esperado) | 576; 192; 3; 1 |
| P04 | composição, fds_def, férias, grade_data, grau, pedidos | 8h | 8+6 | GERA ESCALA (esperado) | 387; 736; 4; 5 |
| P05 | cargas, demanda, férias, início, nomes, pacientes | 12x36 | 4+10 | **INVIÁVEL pela conta** | 6; −18; −1; −1 |
| P06 | composição, fds_própria, grau, horários, início, pedidos | 6+12 | 10+4 | GERA ESCALA (esperado) | 832; 752; 4; 4 |
| P07 | fds_própria, férias, grade_data, modelo, nomes, pacientes | 8h | 5+8 | GERA ESCALA (esperado) | 264; 208; 3; 2 |
| P08 | cargas, composição, demanda, fds_def, grade_data, pacientes | 12x36 | 8+4 | GERA ESCALA (esperado) | 692; 660; 3; 3 |
| P09 | demanda, férias, grau, horários, início, nomes | 8h | 6+9 | GERA ESCALA (esperado) | 760; 384; 5; 3 |
| P10 | composição, fds_def, férias, horários, pacientes, pedidos | 6+12 | 12+4 | GERA ESCALA (esperado) | 1092; 1104; 5; 6 |
| P11 | cargas, fds_def, fds_própria, grade_data, grau, nomes | 12x36 | 4+9 | **INVIÁVEL pela conta** | 216; 32; −1; 0 |
| P12 | composição, demanda, grade_data, início, modelo, pedidos | 8h | 7+6 | GERA ESCALA (esperado) | 952; 560; 7; 4 |
| P13 | cargas, fds_própria, férias, horários, início, pacientes | 12x36 | 5+9 | GERA ESCALA (esperado) | 328; 176; 1; 1 |
| P14 | cargas, composição, demanda, grau, nomes, pedidos | 6+12 | 11+5 | GERA ESCALA (esperado) | 1048; 872; 6; 5 |
| P15 | demanda, fds_def, início, modelo, pacientes, pedidos | 6+12 | 10+5 | GERA ESCALA (esperado) | 960; 584; 5; 3 |
| P16 | composição, fds_própria, férias, grau, horários, nomes, pedidos | 8h | 9+7 | GERA ESCALA (esperado) | 884; 868; 6; 5 |
| P17 | cargas, demanda, fds_def, grade_data, início, modelo, pacientes | 12x36 | 5+10 | GERA ESCALA (esperado) | 236; 208; 1; 1 |
| P18 | demanda, fds_própria, férias, grade_data, grau, horários, nomes | 6+12 | 12+5 | GERA ESCALA (esperado) | 1256; 1092; 5; 5 |

Os parâmetros exatos de cada caso (horários, cargas, férias, demanda) estão no gerador. Antes de rodar, cada caso vira uma `Entrada` da ferramenta com esses mesmos valores.

### Nível 2 — casos de resposta conhecida

| Caso | Esperado pela conta | Por quê |
|---|---|---|
| K1 folga clara (8 h, 6 + 10, 1 + 1 por turno) | GERA ESCALA | folga de 10 pessoas por dia |
| K2 inviável pela conta (12×36, 3 + 6, 1 + 3 por turno) | INVIÁVEL: faltam horas e pessoas | horas −1.104; ocupados por dia −7 |
| K3 parte A com 16 (11 + 5) | **FRONTEIRA** | ocupados por dia: folga 0 |
| K4 parte A com 17 (12 + 5) | GERA ESCALA (esperado) | folga 1 |
| K5 parte A com 18 (13 + 5) | GERA ESCALA (esperado) | folga 2 |
| K6 parte A com 20 (15 + 5): o caso do Otávio | GERA ESCALA (esperado) | folga 4; existe escala construída à mão e aceita pelo modelo (`docs/diagnostico/escala_construida.py`, 07/10) |

### Nível 3 — lote aleatório (cerca de 200 casos pequenos)

- **Sorteio:** semente registrada no gerador antes de rodar.
- **O que se sorteia, em faixas pequenas** para cada caso caber em poucos minutos:
  - modelo (os 3);
  - fim de semana;
  - início (uma segunda entre 10/2026 e 03/2027);
  - de 3 a 8 enfermeiros e de 2 a 12 técnicos;
  - cargas (30/36/40/44 h, com 70% em 44 h);
  - de 0 a 2 períodos de férias de até 10 dias;
  - de 0 a 6 pedidos;
  - demanda de 1 a 2 enfermeiros e de 0 a 4 técnicos por turno;
  - fim de semana próprio em 30% dos casos;
  - de 0 a 2 datas editadas na grade;
  - pacientes em 40% dos casos.
- **Conferido só pelas propriedades automáticas** (C3). Sem esperado caso a caso, além da conta.
- **Limite por caso:** o da tela, 600 s e 180 s. Os casos que esgotarem o tempo são listados à parte.

## C3. Propriedades automáticas (valem para todo caso)

1. **Toda escala passa na conferência independente da CLT:** descanso medido no relógio a partir dos horários, entre turnos, semanal e em dias seguidos (`docs/conferencia_descanso_escala.py`), e `solucao.conferir_rigidas`.
2. **Monotonia:**
   - mais gente nunca piora: o menor quadro viável não sobe ao acrescentar uma pessoa;
   - mais demanda ou mais férias nunca melhora.

   Verifica-se em pares de casos derivados: o mesmo caso com +1 pessoa, +1 posto e +1 dia de férias.
3. **Ordem não importa:** embaralhar a ordem dos profissionais (e dos nomes) não muda o veredito nem o menor quadro viável.
4. **Honestidade da tela:**
   - nunca "provado" sem prova;
   - nunca "faltam N" sem prova de inviabilidade do quadro informado (pela conta ou pelo solver).

   Lido no texto da tela (AppTest) e da planilha.
5. **Folga clara não termina sem escala:** caso pequeno com folga de pelo menos 2 em todas as contas da conta independente não pode acabar em "não foi possível gerar a escala no tempo disponível".
6. **Coerência com a conta:** se a conta independente diz INVIÁVEL, a ferramenta não pode gerar escala para o quadro informado. Se gerar, há defeito na conta ou no modelo.

## C4. Classificação de cada falha futura

Toda falha que a bateria achar recebe uma camada, antes de qualquer correção:

| Camada | O que é | Exemplo de sintoma |
|---|---|---|
| **tradução da entrada** | `ferramenta.montar` / `instancia_br.construir`: a tela pede uma coisa e a instância diz outra | horário editado que não chega aos pares proibidos; feriado que não vira demanda |
| **modelo** | `src/modelo.py`: restrição a mais, a menos ou errada | escala construída à mão que a conferência aprova e o modelo recusa |
| **orquestração** | piso, etapas, busca do menor quadro, leitura do estado do solver (`ferramenta.verificar`, `resolver`, `experimento_a.classificar`) | "o solver falhou" quando houve só tempo esgotado; busca que para cedo demais |
| **solver** | HiGHS: não acha escala que existe, ou não prova, dentro do tempo | log sem solução viável com escala viável conhecida |
| **apresentação** | `src/app.py`, textos e números da tela e da planilha | texto que diz o contrário do veredito; número sem unidade |

Cada falha entra no relatório com: caso, camada, arquivo e linha, proposta de correção e esperado. A correção só entra com esperado registrado antes (`DECISOES.md`, E3).
