# v1.4.3 (21/10) — a trava do máximo de dias seguidos é só a da CLT: esperado

Registrado e commitado **antes** de implementar e de rodar. Decisão: `DECISOES.md`, "2026-10-21 —
Máximo de dias seguidos: a trava é só a da CLT; a regra do hospital é preferência".

## Escopo da mudança (registrado antes)
- `src/modelo.py` e `src/instancia_br.py`: **não mudam**. Se for preciso tocar neles, paro e
  levo ao Otávio.
- `src/ferramenta.py`: `Entrada.max_dias_seguidos` sai; `montar` passa
  `max_consecutivos=br.MAX_CONSECUTIVOS_GENERICO` (6), o valor padrão que o campo tinha.
- `src/app.py`: sai a linha rígida do hospital (chave `max_dias`); o teto dos campos de dias
  seguidos (preferência e mínimo) passa a ser o legal (6); ajuda da preferência com o texto
  pedido.
- `src/prioridades.py`: só texto (ajuda, resumo, comentários). Nenhuma conta muda.

## (a) Identidade, classificação padrão: 243 de 243
`identidade_3bloco.py --gravar` na v1.4.2 (worktree `../tcc-nrp-v142`, tag `v1.4.2` = commit
74659bc) e na árvore nova, sem linhas e com os pedidos como linhas; `identidade_opcao_b.py
--comparar`: **243 arquivos, 243 idênticos** nas duas comparações; o controle positivo (uma linha
a mais no LP) acusa diferença. Motivo: nenhuma das 81 entradas usava o campo (todas no 6 padrão),
e `montar` passa o mesmo 6.

## (b) Identidade nas entradas da fase 2: 24 de 24
`preferencias.py --gravar-fase2` com `--raiz ../tcc-nrp-v142` e na árvore nova: **24 de 24
idênticos**. As instâncias gravadas da fase 2 têm `MaxConsecutiveWorkingDays` = 6 (conferido nos
quatro `*_instancia.xml` de `resultados/fase2_2026-10-21/`).

## (c) Regressão: 56, 58, 197, 219
`python src\regressao.py --todos` sem mudança (o caminho do INRC não passa por `ferramenta`).

## (d) Teste `max-dias` reescrito para a preferência
**O que deixa de valer** (era trava): "7 → erro de entrada (art. 67)" pela `Entrada`, e o caso
"hospital = 4 → Falta 1; o menor quadro viável é 15", com `limite_efetivo` = 4, piso 15 e o 14
recusado pela conta. Não há mais como pedir à ferramenta uma trava abaixo da lei.

**O que o substitui.** Mesma base: turnos M 7–13 e T 13–19, técnicos M 6 e T 6 todos os dias, 0
enfermeiros, 28 dias.
1. `Entrada` não tem mais `max_dias_seguidos` (passar o campo é erro de tipo).
2. Com 14 técnicos: `limite_efetivo` = 6 e piso = 14 (janela de 7 dias: ⌈7 × 12 / 6⌉).
3. **Preferência de dias seguidos = 4 no Essencial, 14 técnicos.** Esperado: "O quadro informado
   admite escala legal. Escala gerada.", menor viável 14, provado; maior sequência na escala ≤ 6
   (contada direto e no relógio), descanso ok; violações da preferência **contadas pelo script fora
   do modelo = "Resultado por critério" = 96**. Conta: com 12 postos por dia e 14 pessoas, há
   exatamente 2 folgas por dia; 14 × 24 = 336 janelas de 5 dias, no máximo 2 × 120 = 240
   quebradas, logo ≥ 96 (cota de 21/10, `resultados/preferencias_2026-10-21/ESPERADO.md`,
   acréscimo 1). O 96 é atingível (o caso c1, com a preferência no Importante, provou 96); no
   Essencial o bloco dela é minimizado primeiro, então o ótimo dela é o mesmo 96.
4. **Preferência 9 (acima da lei)** no back end: limite usado 6 (`pr.limite_usado`), nunca
   violada — já coberto pelo `preferencias.py --controle` ("acima"), que roda na suíte.
5. **Cobertura do texto da conta prévia**, que só o `max-dias` testava: 13 técnicos, a lei (6).
   Piso 14 > 13 → "Falta 1; o menor quadro viável é 14. Escala gerada."; primeira tentativa
   (13, "piso"); diagnóstico `combinacao` com "A conta prévia do menor quadro provou" e sem "O
   solver provou"; `diagnosticar` sem o parâmetro dá "O solver provou que". Conferido sem solver
   antes de registrar: `limite_efetivo` 6, piso 14, diagnóstico `combinacao` com o texto da conta.
   O 14 é viável (o caso antigo com 6 admitia 14).
6. **Tela (no `pref-tela`):** no modelo de 8 h não existe campo com a chave `max_dias`; a linha
   "Máximo de dias seguidos (preferência)" aparece com campo de limite de máximo **6**; a ajuda da
   linha contém "a lei trava em 6". No 12×36, a linha continua oculta (como antes).

## (e) Números do `NUMEROS_TCC.md` e da fase 2 que usaram o campo do hospital ≠ 6
Esperado: **nenhum**. Conferido antes de registrar: o `NUMEROS_TCC.md` só cita "dias seguidos"
na linha das penalidades do INRC (56, 58, 197, 219), que não passa pela ferramenta; nenhum
script de `docs/diagnostico/` nem da demonstração passa `max_dias_seguidos` à `Entrada`; as
instâncias da fase 2 têm 6. O único uso de valor ≠ 6 foi o teste `max-dias` (4 e 7), citado em
`resultados/max_dias_2026-10-20/ESPERADO.md` e no `relatorio_2026-10-20.md` — registros de
teste, não números do TCC.

## (f) Testes do piso que usavam L do hospital ≠ 6
- `piso_pares.py --seguranca / --controle / --casos / --sorteio`: **nenhum** usa (as entradas vêm
  das baterias, da demonstração, da Parte 3 e do sorteio, todas com o 6). Não mudam.
- `piso_pares.py --tela` (não roda na suíte) colhia duas entradas do `max-dias` (L = 6 e L = 4),
  sem diferença entre piso antigo e novo. A de L = 4 deixa de existir; no lugar entram as do
  `max-dias` novo (14 com preferência; 13 com a lei).
- O piso com L = 4 (⌈5 × 12 / 4⌉ = 15) e o `limite_efetivo` = 4 deixam de ser testados pela
  ferramenta: com a entrada atual, `limite_efetivo` só vale 6 ou 1 (12×36). `piso_de_alternancia`
  continua genérico em L.

## Suíte reduzida: `docs/diagnostico/fechar_v143.sh`
Identidade contra a v1.4.2 em `../tcc-nrp-v142`; RETOMAR=1; um processo por teste; para na
primeira falha.

| Passo | Por quê | Tempo (v1.4.2, i5-10210U, HiGHS 1.15.1) |
|---|---|---|
| identidade 243 (sem linhas e com linhas) + controle | (a) | ~2,5 min |
| `preferencias.py --controle`, fase 2 v1.4.2 × nova | (b) e o limite acima da lei | ~0,5 min |
| `piso_pares.py --seguranca --controle --casos` | (f) | < 0,1 min |
| `preferencias.py --caso-pequeno` | usa a preferência de dias (4) | < 0,1 min |
| `regressao.py --todos` | (c) | ~1 min |
| `testes_entrada.py` | testes de entrada | < 0,2 min |
| tela `pref-tela` | campo removido e teto 6 da preferência (item 6) | < 0,2 min |
| tela `max-dias` | reescrito (d) | ~0,5 min (estimado) |
| tela `opB-d` | situação da preferência de dias ("ok"), que lê o limite efetivo | < 0,1 min |
| tela `opB-tela` | conferia que o campo do hospital não aparece no 12×36 | ~5 min |
| tela `opB-c` | plano com a preferência de dias (limite 5, máximo 690) | ~14 min |
| tela `opB-e` | todas as suaves, inclusive a de dias, no Essencial | ~35 min |

**Total estimado: ~1 h.** Não rodam: as rodadas a2 e os testes da tela que não tocam no campo nem
na preferência de dias (ped-*, tela-limpa, descanso-param, opB-padroes, opB-b, 16, 4b, 7.x, 9x,
3, 4, 5, 15, 8, 12, 1-2, 9) — a identidade os cobre.

Esperado de todos os passos não reescritos: o mesmo resultado da suíte da v1.4.2
(`resultados/v142_2026-10-21/suite/resumo.txt`).

---

## Acréscimo de 21/10 (noite), registrado ANTES de implementar: textos para o gestor, tema claro, barra pelo relógio

Pedido do Otávio (v1.4.3, continuação). A suíte da v1.4.3 foi cancelada antes do fim; roda uma
só, depois destas mudanças e da revisão dele.

**Escopo:** `src/app.py`; só os TEXTOS de `src/prioridades.py` e de `src/ferramenta.py`; novo
`.streamlit/config.toml`; os testes que conferem esses textos. `modelo.py`, `instancia_br.py` e
as contas de `ferramenta.py` e `prioridades.py` não mudam. Os alertas do COFEN são escritos em
`instancia_br.alertas_cofen` (fora do escopo): o texto deles fica; a tela ganha, logo abaixo, uma
legenda que explica QP e IST.

**Esperado:**
1. **Identidade inalterada:** 243/243 (sem linhas e com linhas) e 24/24 (fase 2) contra a v1.4.2.
   Texto não entra no LP nem no XML.
2. **Exemplos do "?" conferidos contra a contagem da ferramenta** (`prioridades.resultado`, que
   usa o `avaliacao.py`), em escalas montadas à mão, ANTES de registrar: todos os 14 conferem
   (máximo de dias 5 → 6 seguidos = 1, e 4 → 5 = 1; mínimo de dias 3, só a terça = 2; máximo de
   folgas 4, seis = 2; mínimo de folgas 3, isolada = 2; máximo de fins de semana 3, quatro = 1;
   mínimo 2, isolado = 1; 4 semanas, máximo 2, três = 1; fim de semana completo, só o sábado = 1;
   mesmo turno, diurno no sábado e noturno no domingo = 2; máximo de turnos 12, 14 = 2; mínimo
   10, 8 = 2; noturno na sexta com fim de semana livre = 1; noturno na segunda e trabalho na
   quarta = 1; enfermeiro em posto de técnico, um turno = 1). Achado: os dois exemplos de fim de
   semana valem para "sábado e domingo"; com "sexta a domingo" dão 2 e 4. O texto ganha
   "(fim de semana de sábado e domingo)" — corrige o exemplo, não a conta.
   Ajuste de número pedido ("se o limite padrão for outro"): máximo de dias seguidos, padrão 5 →
   exemplo "com máximo 5, trabalhar 6 dias seguidos gera 1 violação". Máximo de turnos: o padrão
   é 18, mas no 12×36 o campo cai para o teto legal 14; o exemplo 12 → 14 vale nos dois e fica.
3. **Testes da tela que conferem textos que mudam** (atualizados com registro, como no precedente
   do 1-2):
   - `8` (8b: aviso "pode haver uma melhor (gap" → frase nova do gap; linha da escala vigente;
     ausência de "Equilíbrio de carga: não rodou" → da frase nova; 8c: "o solver não achou
     escala nem provou que ela não existe" → frase nova);
   - `12` (linha da escala vigente: "Escala desta tela: a da etapa 2…" → frase nova);
   - `opB-tela` (coluna "Nível" da tabela "Resultado por critério" → "Importância");
   - `pref-tela` (a ajuda da preferência de dias passa ao texto da Parte 4);
   - `max-dias` (diagnóstico: "A conta prévia do menor quadro provou" e "O solver provou que" →
     frases novas).
   Continuam valendo sem mudança, e os textos novos são escritos para isso: `4` (alerta começa
   com "Alerta COFEN (não impede a escala)"), `9c-tela` (nenhum texto com "provad"), `tela-limpa`
   (cabeçalhos, rótulos do COFEN e dos graus; nenhum "Situação", "já garantido", "(fds)"), `9`
   ("Diferença máxima de carga entre colegas"), `15` ("Súmula 110"), `16` ("não cumpre a
   conferência de descanso (art. 67)"), `7.3` e `7.4` (trechos dos diagnósticos), opB-tela
   ("Todos os critérios considerados estão no nível Importante").
4. **Frases que o TCC cita** ("Faltam N; o menor quadro viável é X", "O quadro informado admite
   escala legal", "Não há escala legal até N"): não mudam. Muda o complemento de "Escala gerada;
   pode haver uma melhor (gap X: …)", porque "gap" é proibido; a lista antiga → nova vai para a
   Redação no `resultados/textos_tela_2026-10-21.md`.
5. **Barra pelo relógio** (Parte 7). Plano: o cálculo (`fe.verificar`) roda numa thread de
   trabalho, sem chamar o Streamlit; a thread do script (a de sempre) espera por ela em passos de
   até 1 s e atualiza a barra (fração = decorrido ÷ tempo máximo, no máximo 99%) e o texto da
   parte em que está; a escala provisória é desenhada pela thread do script. Assim nenhuma
   chamada do Streamlit sai da thread do script e não é preciso `add_script_run_ctx`. Ao terminar
   antes do limite, a barra completa até 100% em ~3 s. Se a thread de trabalho não funcionar nos
   testes da tela ou no navegador, plano B (a barra anda pelas partes, pula para 100% no fim).
   **A barra não muda veredito nem número:** o mesmo caso rodado direto e pela thread dá o mesmo
   resultado; o tempo do cálculo com e sem a barra é medido e relatado (o ~3 s de fechamento da
   barra é depois do cálculo).
6. **Testes da tela que passam pela barra:** todos os que clicam em "Gerar escala". Os que rodam
   na suíte reduzida: `8`, `12`, `opB-tela`, mais os que conferem textos (lista do item 3) e o `4`
   (alerta COFEN) e o `9c-tela` (nenhum "provad").

**Complemento (Parte 9, antes da suíte): testes da tela no `fechar_v143.sh`**, na ordem:
pref-tela, max-dias, opB-d, 16, 4b, 7.4, 9c-tela, 4, 5, 15, 8, 12, opB-tela, tela-limpa, opB-c,
opB-e. Motivos: campo removido ou preferência de dias (pref-tela, max-dias, opB-d, opB-tela,
opB-c, opB-e); textos que mudaram (8, 12, opB-tela, pref-tela, max-dias); textos que os novos não
podem quebrar (4, 9c-tela, tela-limpa, 15, 16, 7.4, 4b); passam pela barra clicando em "Gerar
escala" (os anteriores que usam a tela, mais o 5). Ficam de fora: a2, 1-2, 3, 7.1, 7.2, 7.3, 9,
9b-sem-teto, ped-*, descanso-param, opB-padroes, opB-b (a identidade cobre o problema enviado ao
solver; a barra é a mesma em todos os cliques e já passa por 12 testes). Tempo estimado (tempos
da v1.4.2, i5-10210U, HiGHS 1.15.1, mais ~3 s por clique do fechamento da barra): ~1 h 30.
Esperado: todos OK, com os resultados da v1.4.2. Já rodados nesta sessão com o código novo, antes
da suíte: pref-tela, max-dias, 9c-tela, 16, 4b, 7.4, opB-d, 8, 12, opB-tela, 4, 15, tela-limpa —
todos OK; identidade sem solver 243/243 (sem linhas e com linhas) e 24/24.

---

## Acréscimo de 22/10, registrado ANTES de implementar: divisão proporcional do tempo máximo e resultado por nível

Pedido do Otávio (v1.4.3, acréscimo de 22/10). A suíte da v1.4.3 ainda não rodou; roda uma só,
depois disto e da revisão dele.

**Escopo:** `src/ferramenta.py` (distribuição do tempo e textos do resultado) e `src/app.py`
(textos e arrumação da seção 5). `modelo.py`, `instancia_br.py` e o que vai ao solver não mudam.

**Regra (parâmetro de projeto, sem calibração).** Etapa 1 : etapa 2 = 50 : 50; dentro da etapa 1,
Essencial : Importante : Desejável = 50 : 30 : 20. No início de cada parte k:
`tempo_k = tempo que resta × peso_k ÷ (soma dos pesos das partes que ainda faltam, incluindo k)`.

*Leitura adotada (Claude Code; levar ao Otávio):* os pesos do pedido são 0,25 / 0,15 / 0,10 /
0,50 com os três níveis. Com nível vazio, a leitura literal ("nível vazio não entra", e os outros
pesos ficam como estão) daria, no padrão fundido Essencial+Importante, 0,40 : 0,50 → 26,7 + 33,3
min a 60 min, e não os 30 + 30 que o item 6 pede. Para os dois valerem juntos, **a etapa 1 fica
sempre com 50%, e os 50 : 30 : 20 se dividem entre os níveis presentes**: Essencial+Importante
fundidos = 0,50 (80/80 da etapa 1); com os três separados, 0,25 / 0,15 / 0,10 (o mesmo do pedido).

**(a) Identidade inalterada:** 243/243 e 24/24 contra a v1.4.2 — o tempo não entra no LP nem no XML.

**(b) Divisão no início (minutos; antes de qualquer sobra):**

| Níveis | Pesos (etapa 1 … ; etapa 2) | 20 min | 60 min | 120 min |
|---|---|---|---|---|
| 1 nível, ou bloco fundido (o padrão) | 0,50 ; 0,50 | 10 + 10 | **30 + 30** | 60 + 60 |
| 2 separados: Essencial, Importante | 0,3125 / 0,1875 ; 0,50 | 6,2 / 3,8 + 10 | 18,8 / 11,2 + 30 | 37,5 / 22,5 + 60 |
| 2 separados: Essencial, Desejável | 0,357 / 0,143 ; 0,50 | 7,1 / 2,9 + 10 | 21,4 / 8,6 + 30 | 42,9 / 17,1 + 60 |
| 2 separados: Importante, Desejável | 0,30 / 0,20 ; 0,50 | 6,0 / 4,0 + 10 | 18,0 / 12,0 + 30 | 36,0 / 24,0 + 60 |
| 3 separados | 0,25 / 0,15 / 0,10 ; 0,50 | 5 / 3 / 2 + 10 | 15 / 9 / 6 + 30 | 30 / 18 / 12 + 60 |
| 3 níveis, Essencial+Importante fundidos, Desejável à parte | 0,40 / 0,10 ; 0,50 | 8 / 2 + 10 | 24 / 6 + 30 | 48 / 12 + 60 |

Padrão a 60 min = **30 + 30**, igual ao de hoje (1.800 s + 1.800 s).

**(c) Conta, sem solver** (60 min, 3 níveis separados), feita pela função da ferramenta com
tempos gastos simulados: início 15 / 9 / 6 / 30; Essencial prova em 2 min → Importante 11,6
(58 × 0,15 ÷ 0,75); se o Importante usa tudo → Desejável 7,7, etapa 2 38,7; se o Desejável prova
em 1 min → etapa 2 45,4. Conferido antes de registrar com a mesma fórmula.

**(d) Caso pequeno com solver, 3 níveis separados, tempo curto** (`docs/diagnostico/
tempo_proporcional.py --caso`; o mesmo caso do teste de 40 com 20 pedidos, em que a primeira
escala aparece perto dos 17 s nesta máquina): tempo máximo de 60 s. Esperado: o Essencial
recebe 15 s; se acabar sem escala, a **proteção da primeira escala** roda de novo com todo o tempo
que resta (recomeça: sem escala não há de onde partir — custo declarado) e a escala sai; cada
parte seguinte recebe `resta × peso ÷ soma`, com a sobra de quem terminou antes; a soma dos
limites não passa do tempo máximo. A escala é entregue e cumpre o descanso. Com tempo máximo
de 10 min, sem proteção (o Essencial acha a escala na sua fatia), a sobra passa adiante: limite
de cada parte > a fatia do início quando a anterior termina antes. O script imprime limite e
tempo gasto de cada parte.

**(e) Testes que dependem do tempo ou do texto do resultado, e o que pode mudar:**
- `TEMPO` e `TEMPO_ETAPA2` passam a `None` na ferramenta (sem teto fixo); ficam como **teto
  opcional, só para os testes** (que os põem em 600 / 180 / 20 min, ou 25 s e 3 s no teste 8).
  Com teto, a proteção da primeira escala continua, mas a cadeia inteira da primeira resolução
  não passa do teto. `resolver_com_objetivo(inst, tempo)` chamado sem `prazo` (testes ped e
  descanso-param, `pedidos_avaliador.py`) usa o teto por resolução, como antes.
- `opB-padroes`: conferia `(TEMPO, TEMPO_ETAPA2, ORCAMENTO) == (1800, 1800, 3600)` → passa a
  `(None, None, 3600)` (atualizado com registro).
- `8`: 8a/8c/8d sem mudança (teto do teste); 8b: o aviso passa de "…pode haver uma melhor: esta
  escala pode ser até X pior…" a "…Escala gerada; pode haver uma melhor." (o gap sai da frase e
  vai para as frases por nível).
- `12`: 12d (tempo máximo 3 s) continua "o menor quadro viável não foi determinado em 3 s": o
  Essencial recebe 1 s, e a proteção usa os ~2 s restantes.
- `opB-tela`: a tabela "Resultado por critério" passa a uma tabela por nível (ou bloco), cada uma
  com a sua frase acima; a conferência passa a "as tabelas juntas = `r.criterios`".
- `opB-b`, `opB-c`, `opB-e`: com mais de um bloco, cada nível recebe a sua fatia em vez de 600 s;
  no caso pequeno (opB-b) os três provam em segundos (sem mudança esperada); no opB-c, o bloco
  Desejável recebe menos tempo — o teste confere caminho, escala e descanso, não prova.
- `15`: o alerta curto não traz mais "Súmula 110" (vai para o "?"); 15d: a linha do descanso
  passa a "menor descanso semanal: …".
- `9c-tela`: nenhum texto novo contém "provad"; a etapa 2 continua presa nos 20 s do teste.
- Rodadas a2 (fora da suíte): com os tetos 600/180/20 min, o caminho fundido recebe 600 s, como
  antes; os campos "frase" das rodadas sem prova passariam a "pode haver uma melhor." sem o gap.

**(f) NUMEROS_TCC:** não muda. Os números foram medidos com os limites antigos (600 s, 180 s,
20 min até a v1.2.3; 1.800 s por resolução depois), declarados no próprio arquivo.

**Resultado por nível (texto):** provado → "<Nível>: N violações — a melhor possível."; sem prova
com limite útil → "<Nível>: N violações. Nenhuma escala tem menos de M." (M = limite inferior do
solver, arredondado para cima; nunca acima de N); sem limite útil → "…Não deu tempo de saber
quanto dá para melhorar."; não rodou → "<Nível>: não deu tempo de otimizar; a escala mantém o
resultado dos níveis acima."; bloco fundido → uma frase para o bloco. *Decisão de implementação
(não óbvia):* num bloco fundido o objetivo do solver soma os níveis com coeficientes (o de cima =
máximo do resto do bloco + 1), e o limite inferior não é contagem de violações. O M do bloco é
dado só para o nível de cima: M = ⌈(limite − (coef − 1)) ÷ coef⌉, porque o resto do bloco vale no
máximo coef − 1. Etapa 2: "Equilíbrio entre colegas: o melhor possível." / "…pode haver uma
escala mais equilibrada." As três frases do TCC não mudam.

**Parte extra (seção 5):** alerta de descanso semanal em uma linha (o texto mora em
`ferramenta.alertas_descanso`, dentro do escopo; o fundamento vai para o "?"); diferença entre
categorias sem número negativo; "maior sequência de trabalho na escala: N dias", "menor descanso
entre turnos", "menor descanso semanal"; legendas num expander "Detalhes da escala", fechado;
"sem pedidos" no lugar de "0 de 0"; frases por nível junto da tabela.

**Rodado em 22/10 com o código novo, antes da suíte** (i5-10210U, HiGHS 1.15.1):
- Sem solver: identidade 243/243 (sem e com linhas) e 24/24; `tempo_proporcional.py --conta` OK
  (tabela, 15/9/6/30, 11,6 / 7,7 / 38,7 / 45,4, frases por nível).
- Testes da tela: opB-padroes, pref-tela, max-dias, 16, 4b, 7.4, opB-d, opB-b, 12, opB-tela, 15
  OK; 8 OK depois do ajuste abaixo; 9c-tela, ver abaixo.
- **Ajuste a posteriori no 8a (não previsto acima):** a conferência procurava "pode haver" em
  qualquer texto; a frase nova da etapa 2 ("Equilíbrio entre colegas: pode haver uma escala mais
  equilibrada.") também tem essas palavras. O esperado registrado do 8a (docstring do teste) é
  "nenhum 'pode haver uma melhor'"; a conferência passou a procurar isso. Mesmo precedente do 1-2.
- **9c-tela:** falhou uma vez com a máquina carregada (Chrome aberto; a etapa 2 não achou escala
  nos 20 s do teste) e passou na v1.4.2 com a mesma carga. Investigado (pedido do Otávio): o
  limite da etapa 2 nesse teste é **20 s nas duas regras** (medido no mesmo caso por
  `fe.verificar`, com os ajustes do teste: v1.4.2 — etapa 1 limite 600 s, gastou 2,0 s; etapa 2
  limite 20 s, gastou 20,5 s; nova — etapa 1 limite 599 s, gastou 1,4 s; etapa 2 limite 20 s,
  gastou 20,4 s). A regra nova dá 0,5 do que resta (~600 s) e o teto do teste corta em 20 s.
  Sem carga (Chrome fechado), duas rodadas em cada versão: v1.4.2 25 s e 26 s, nova 29 s e 29 s
  (os ~3 s a mais são o fechamento da barra), todas OK. Leitura: o teste é sensível à carga da
  máquina (20 s para a etapa 2 achar uma escala do zero, porque a etapa 1 prova o ótimo); a falha
  sob carga não vem da mudança de tempo. O teste fica como está.
- **(d) caso com solver:** sem carga, (d1) caso pequeno: as três partes provam em menos de 1 s,
  a sobra passa adiante (Importante 11 s > 9 s, Desejável 9 s > 6 s); (d2) 40 com 20 pedidos,
  60 s: o Essencial provou em 8,6 s (a proteção não disparou), o Importante saiu com "112
  violações. Nenhuma escala tem menos de 96."; (d3) mesmo caso, 600 s: tudo provado, Importante
  96 — o mesmo 96 que o limite de (d2) dava, o que confere a frase. Com a máquina carregada
  (Chrome aberto), a mesma (d2) mostrou a **proteção**: o Essencial esgotou os seus 14 s sem
  escala, rodou de novo com os 42 s que restavam e provou em 34,7 s; depois, Importante e etapa 2
  receberam 1 s e o HiGHS passou do limite em alguns segundos (6,1 s com limite de 1 s; total
  ~62 s). Por isso a conferência do tempo gasto tem folga de 15 s. Quando a proteção dispara, os
  níveis de baixo podem ficar com quase nada — é a regra pedida (a primeira escala vem primeiro).
- **Conferências do script corrigidas antes de registrar o resultado:** a primeira versão
  conferia "soma dos limites ≤ tempo máximo", o que está errado (cada limite é calculado no início
  da parte, sobre o que resta; quem termina antes deixa a soma passar do máximo) — passou a
  conferir o tempo **gasto**; e a conferência da sobra passou a valer só sem proteção.
