# Textos da tela para o gestor — v1.4.3 (21/10/2026)

Para a revisão do Otávio, antes da suíte. Público: gestor de enfermagem usando a ferramenta pela
primeira vez. Só muda a redação; nenhuma conta, nenhum número. `modelo.py` e `instancia_br.py`
intocados. Decisão: `DECISOES.md`, "2026-10-21 — Textos para o gestor, tema claro e barra pelo
relógio". Esperado: `resultados/trava_clt_2026-10-21/ESPERADO.md` (acréscimo da noite).

**Exemplos do "?" conferidos pela contagem da ferramenta** (`prioridades.resultado`, que usa o
`avaliacao.py`), em escalas montadas à mão: 15 de 15 conferem (lista no ESPERADO). Dois ajustes de
exemplo: (1) máximo de dias seguidos, padrão 5 → "com máximo 5, trabalhar 6 dias seguidos gera 1
violação" (o texto pedido usava 4 e 5, que também confere); (2) os dois exemplos de fim de semana
valem para "sábado e domingo" (com "sexta a domingo" dão 2 e 4) e ganharam "(fim de semana de
sábado e domingo)". Máximo de turnos: o exemplo 12 → 14 fica (o padrão é 18, mas no 12×36 o campo
cai para o teto legal 14; o exemplo vale nos dois).

## Para a Redação: frases que o texto do TCC pode citar

| Antes | Depois |
|---|---|
| "Faltam N; o menor quadro viável é X." / "O quadro informado admite escala legal." / "Não há escala legal até N profissionais; o menor quadro viável está acima disso." | **sem mudança** |
| "Escala gerada; pode haver uma melhor (gap X%: distância máxima até a melhor possível)." | "Escala gerada; pode haver uma melhor: esta escala pode ser até X% pior que a melhor possível, e com mais tempo a ferramenta poderia melhorá-la." |
| "Sem resposta em T com N profissionais: o solver não achou escala nem provou que ela não existe." | "Sem resposta em T com N profissionais: a ferramenta não encontrou escala nem conseguiu mostrar que ela não existe." |
| "…Nenhuma conta simples explica… O solver provou que as regras juntas… não admitem escala com este quadro." | "…A busca completa mostrou que as regras juntas… não admitem escala com este quadro." |
| "…A conta prévia do menor quadro provou, sem o solver, que as regras juntas…" e "A conta prévia do menor quadro provou, sem o solver, que este quadro não tem escala legal." | "Uma conta feita antes de procurar a escala já mostra que as regras juntas…" e "Uma conta feita antes de procurar a escala já mostra que este número de pessoas não permite escala legal." |
| "Escala desta tela: a da etapa 2, com a carga equilibrada entre colegas." (e as variantes com "etapa 1") | "Esta escala tem a carga equilibrada entre colegas." (variantes na tabela abaixo) |

## Tela (`src/app.py`)

| Antes | Depois | Onde aparece |
|---|---|---|
| "A CLT trava a escala; o COFEN só alerta. Horizonte de 28 dias, começando numa segunda-feira." | "A escala sempre cumpre a CLT; as recomendações do COFEN aparecem como alerta, sem impedir a escala. O período é de 28 dias, começando numa segunda-feira." | legenda sob o título |
| "?" dos turnos: "Edite os horários ou acrescente uma linha para um turno novo (ex.: D12, 7 a 19). As regras de descanso da CLT saem dos horários: 11 h entre turnos, 36 h depois de turno de 12 h, e toda folga isolada de pelo menos 24 h." | "Edite os horários ou acrescente uma linha para um turno novo (ex.: D12, das 7 às 19). A ferramenta tira dos horários as regras de descanso da CLT: 11 h entre um turno e outro, 36 h depois de um plantão de 12 h, e pelo menos 24 h em toda folga de um dia só." | 1. Configuração, "?" da tabela de turnos |
| "Carga contratual semanal de cada profissional (padrão 44 h)." | "Horas por semana do contrato de cada profissional (padrão 44 h)." | 2. Equipe, legenda da carga |
| "?": "O teto vale sobre o período, não por semana (no 12×36 há semanas de 48 h e de 36 h), e desconta férias e licenças. 44 h é o limite da Constituição." | texto da Parte 2 ("Horas por semana do contrato desta pessoa (padrão 44 h, o máximo da Constituição). A ferramenta não confere semana a semana: … desde que o total do mês não passe de 176 h.") — 44 × 28 ÷ 7 = 176 conferido | 2. Equipe, "?" da carga |
| "Férias e licenças — nesses dias a pessoa não é escalada (regra rígida)." | "Férias e licenças: nesses dias a pessoa nunca é escalada." | 2. Equipe |
| "Média diária de pacientes. Serve só para comparar o quadro com o QP do Parecer; não muda a escala." | "Média de pacientes por dia em cada grau de dependência. Serve só para comparar a equipe com o quadro recomendado pelo Parecer do COFEN; não muda a escala." | painel "Conferir com o COFEN" |
| "?" de "4. Prioridades da escala": "Os de nível Essencial vêm antes de todos os outros; … as regras da CLT continuam rígidas e valem antes de tudo." | texto da Parte 3 ("Aqui você diz o que é mais importante para a sua equipe. … qualquer que seja a sua classificação.") | 4. Prioridades, "?" |
| (sem ajuda) | "Restaurar padrão" ganha "?": "Volta à classificação inicial: enfermeiro em posto de técnico Importante; os outros critérios, Não considerar." | botão "Restaurar padrão" |
| linha pequena sob cada critério (ex.: "Evita folga isolada.") | **apagada**; a explicação toda vai para o "?" | 4. Prioridades, cada critério |
| "ⓘ Sem conferência externa: nenhuma instância do benchmark INRC a usa ou o avaliador oficial não a pontua." | "ⓘ Sem conferência externa: este critério não pôde ser conferido contra o banco de testes internacional usado para validar a ferramenta (INRC-2010); a contagem é só da ferramenta." | "?" de fins de semana em 4 semanas, noturno na véspera, duas folgas depois de noites |
| "Todos os critérios considerados estão no nível X: entre eles há compensação — uma violação de um vale o mesmo que uma de outro." | "Todos os critérios considerados estão no nível X: entre eles, uma violação de um vale o mesmo que uma de outro, e a ferramenta pode trocar uma pela outra." | aviso de mesmo nível |
| "Orçamento do clique (minutos)"; "?": "Tempo máximo de um clique em "Gerar escala". Esgotado, a ferramenta para e mostra só o que foi provado." | "Tempo máximo para gerar a escala (minutos)" (mesma key `orcamento`); "?" da Parte 5 | campo acima de "Gerar escala" |
| "preparando" | "Preparando" | barra |
| "Entrada inválida: …" | "Dados incompletos ou inválidos: …" | erro antes do cálculo |
| "Escala pronta; equilibrando a carga entre colegas (até T)." | "Escala encontrada; equilibrando a carga entre colegas (até T)." | escala provisória |
| (sem legenda) | "QP: quadro de pessoal recomendado pelo Parecer do COFEN. IST: índice de segurança técnica, a margem de 15% para férias e ausências que a escala não cobre." (só quando há alerta com QP ou IST; o texto do alerta vem de `instancia_br`, fora do escopo) | sob os alertas do COFEN |
| métrica "Conferência de descanso" sem "?" | "?": "A escala foi medida no relógio, turno a turno: descanso entre turnos, descanso semanal e dias seguidos, como manda a CLT." | 5. Resultado, métricas |
| "…em relação aos enfermeiros. Ela não é otimizada: vem da demanda…" | "…em relação aos enfermeiros. A ferramenta não tenta igualar isso: vem da demanda…" | 5. Resultado, diferença entre categorias |
| "Equilíbrio de carga dentro de cada categoria, entre as escalas de mesmo custo." / "…que não pioram o valor da etapa 1 (a etapa 1 não provou o ótimo)." | "Equilíbrio de carga dentro de cada categoria, sem piorar nenhum critério da classificação." / "…sem piorar a escala encontrada (que pode não ser a melhor possível)." | 5. Resultado |
| "Equilíbrio de carga: não rodou: o orçamento do clique acabou" / "…não melhorou o equilíbrio no tempo; fica a escala da etapa 1" / "…sem resposta (S); fica a escala da etapa 1" / "…nao rodou" | "Equilíbrio de carga: não foi feito: o tempo máximo acabou" / "…não foi possível equilibrar mais no tempo disponível; fica a escala encontrada" / "…sem resposta no tempo disponível; fica a escala encontrada" (com erro: "erro técnico ao equilibrar; fica a escala encontrada") / "…não foi feito" (o valor guardado não muda) | 5. Resultado |
| "CHS usada no QP: X h por semana, a média das cargas contratuais da equipe." | "Horas semanais usadas na conta do COFEN (CHS, carga horária semanal): X h, a média dos contratos da equipe." | 5. Resultado, painel COFEN |
| "QP núcleo assistencial"; "?": "Horas por dia × 7 / CHS (X h)." | "Quadro recomendado pelo COFEN, só assistência (QP)"; "?": "Horas de cuidado por dia × 7 ÷ horas semanais (X h)." | idem |
| "QP completo (IST 15%)"; "?": "Núcleo × 1,15. O IST cobre férias e ausências que a escala não modela." | "Quadro recomendado pelo COFEN, com 15% para ausências (QP com IST)"; "?": "O quadro só assistência × 1,15. A margem (IST, índice de segurança técnica) cobre férias e ausências que a escala não modela." | idem |
| "Como o veredito foi obtido" | "Como o resultado foi obtido" | 5. Resultado, painel |
| "inviável pela aritmética — horas ou alternância de plantões não cobrem a demanda" | "não basta, pela conta: as horas ou a alternância de plantões não cobrem a demanda" | idem, cada tentativa |
| "inviável, provado pelo solver" | "não há escala que cumpra a lei com este número (a busca completa mostrou)" | idem |
| "viável — escala encontrada e conferida" | "escala encontrada e conferida" | idem |
| "sem resposta em T — nem provado inviável" | "sem resposta em T: a ferramenta não encontrou escala nem mostrou que ela não existe" | idem |
| "erro técnico ao resolver; detalhes no console" | "erro técnico ao calcular; detalhes no console" | idem |
| "não testado: o orçamento do clique acabou" | "não testado: o tempo máximo acabou" | idem |

## Critérios: o "?" (`src/prioridades.py`, campo `ajuda`)

| Critério | Antes | Depois |
|---|---|---|
| Enfermeiro em posto de técnico | "Turno em que um enfermeiro cobre vaga de técnico. Ex.: faltam técnicos no sábado e um enfermeiro cobre: 1 violação." | "Conta quantas vezes um enfermeiro precisou cobrir a vaga de um técnico. Ex.: faltou técnico no sábado e um enfermeiro cobriu: 1 violação. Classifique alto se quiser poupar os enfermeiros." |
| Máximo de dias seguidos (preferência) | "A lei trava em 6 (art. 67); a regra do seu hospital vai aqui, como preferência; no Essencial ela pesa acima de tudo o que é Importante ou Desejável. Ex.: com preferência 4, cinco dias seguidos contam 1 violação; mais de 6 nunca acontece." | "Quantos dias seguidos de trabalho a sua unidade aceita no máximo. A lei já proíbe mais de 6, e isso é sempre cumprido; aqui vai a regra do seu hospital, abaixo disso. Ex.: com máximo 5, trabalhar 6 dias seguidos gera 1 violação. Se for uma regra firme do hospital, marque Essencial. (Não aparece no 12×36, em que ninguém trabalha dois dias seguidos.)" |
| Mínimo de dias seguidos | "Evita dia de trabalho isolado. Ex.: com mínimo 3, trabalhar só na terça, entre folgas, conta 2 violações." | "Evita dia de trabalho isolado entre folgas. Ex.: com mínimo 3, trabalhar só na terça, com folga na segunda e na quarta, gera 2 violações (faltaram 2 dias para o mínimo)." |
| Máximo de folgas seguidas | "…seis folgas seguidas contam 2 violações." | "Evita folgas longas demais. Ex.: com máximo 4, seis folgas seguidas geram 2 violações." |
| Mínimo de folgas seguidas | "Evita folga isolada. Ex.: com mínimo 3, uma folga isolada conta 2 violações." | "Evita folga de um dia só. Ex.: com mínimo 3, uma folga isolada gera 2 violações." |
| Máximo de fins de semana seguidos | "Ex.: com máximo 3, quatro fins de semana seguidos trabalhados contam 1 violação." | "Limita quantos fins de semana seguidos a mesma pessoa trabalha. Ex.: com máximo 3, trabalhar 4 fins de semana seguidos gera 1 violação." |
| Mínimo de fins de semana seguidos | "Evita fim de semana trabalhado isolado. Ex.: com mínimo 2, um fim de semana trabalhado entre dois livres conta 1 violação." | "Evita trabalhar um fim de semana isolado. Ex.: com mínimo 2, trabalhar um fim de semana com folga no anterior e no seguinte gera 1 violação." |
| Fins de semana em 4 semanas | "Ex.: com máximo 2, três fins de semana trabalhados em quatro semanas contam 1 violação. O 2 do campo é valor de exemplo, sem fonte (suposição declarada)." | "Limita quantos dos fins de semana do mês a mesma pessoa trabalha. Ex.: com máximo 2, trabalhar 3 gera 1 violação. O 2 é só um exemplo: ajuste à regra da sua unidade." |
| Fim de semana completo | "Trabalha os dias do fim de semana todos ou nenhum. Ex.: trabalhar só no sábado conta 1 violação." | "Quem trabalha no fim de semana trabalha o fim de semana inteiro. Ex. (fim de semana de sábado e domingo): trabalhar só no sábado gera 1 violação. No 12×36 isso não é possível (ninguém trabalha dois dias seguidos)." |
| Mesmo turno no fim de semana | "…Ex.: diurno no sábado e noturno no domingo contam 2 violações." | "Quem trabalha no fim de semana faz o mesmo turno em todos os dias dele. Ex. (fim de semana de sábado e domingo): diurno no sábado e noturno no domingo geram 2 violações." |
| Máximo de turnos no período | "Preferência do hospital, abaixo do teto obrigatório (a carga contratual nos dias disponíveis continua valendo). Ex.: com máximo 18, quem fez 20 turnos conta 2 violações. O campo não passa do teto legal de turnos." | "Quantos turnos no mês a sua unidade aceita no máximo por pessoa. As horas do contrato já são sempre respeitadas; use isto se a unidade quiser um limite mais baixo. Ex.: com máximo 12, quem fizer 14 turnos gera 2 violações." |
| Mínimo de turnos no período | "Ex.: com mínimo 10, quem fez 8 turnos conta 2 violações." | "Quantos turnos no mês cada pessoa deve fazer, no mínimo. Ex.: com mínimo 10, quem fizer 8 gera 2 violações." |
| Noturno na véspera de fim de semana livre | "Ex.: noturno na sexta e o fim de semana livre: 1 violação." | "Evita plantão noturno na sexta quando a pessoa folga no fim de semana (ela passaria o sábado dormindo). Ex.: noturno na sexta e fim de semana livre: 1 violação." |
| Duas folgas depois de noites | "Depois de uma sequência de noturnos, dois dias de folga. Ex.: noturno na segunda e trabalho na quarta: 1 violação." | "Depois de uma sequência de plantões noturnos, dois dias de folga antes de voltar. Ex.: noturno na segunda e trabalho na quarta: 1 violação." |

Nomes dos critérios (a coluna "Critério") não mudaram.

## Mensagens da ferramenta (`src/ferramenta.py`)

| Antes | Depois | Onde aparece |
|---|---|---|
| "Escala gerada; pode haver uma melhor (gap X: distância máxima até a melhor possível)." | "Escala gerada; pode haver uma melhor: esta escala pode ser até X pior que a melhor possível, e com mais tempo a ferramenta poderia melhorá-la." | frase do resultado (aviso amarelo) e planilha |
| "Sem resposta em T com N profissionais: o solver não achou escala nem provou que ela não existe." | "Sem resposta em T com N profissionais: a ferramenta não encontrou escala nem conseguiu mostrar que ela não existe." | frase do resultado (erro) |
| "Escala desta tela: a da etapa 1. O equilíbrio de carga não achou, no tempo disponível, escala mais equilibrada sem piorar o resultado da etapa 1." | "Esta é a escala encontrada: no tempo disponível, não foi possível equilibrar mais a carga entre colegas sem piorar o resultado." | 5. Resultado, linha da escala vigente |
| "Escala desta tela: a da etapa 2, com a carga equilibrada entre colegas, sobre uma escala sem prova de ótimo: o equilíbrio não deixou piorar o valor achado pela etapa 1." | "Esta escala tem a carga equilibrada entre colegas, sem piorar o resultado da escala encontrada (que pode não ser a melhor possível)." | idem |
| "Escala desta tela: a da etapa 2, com a carga equilibrada entre colegas." | "Esta escala tem a carga equilibrada entre colegas." | idem |
| "Escala desta tela: a da etapa 1; o equilíbrio não achou escala mais equilibrada no tempo." | "Esta é a escala encontrada: não foi possível equilibrar mais a carga entre colegas no tempo disponível." | idem |
| "Escala desta tela: a da etapa 1; o equilíbrio de carga não rodou." | "Esta é a escala encontrada: o equilíbrio de carga entre colegas não foi feito." | idem |
| "Escala desta tela: a da etapa 1; o equilíbrio de carga não terminou no tempo." | "Esta é a escala encontrada: o equilíbrio de carga entre colegas não terminou no tempo." | idem |
| "A conta prévia do menor quadro provou, sem o solver, que este quadro não tem escala legal." | "Uma conta feita antes de procurar a escala já mostra que este número de pessoas não permite escala legal." | diagnóstico "Dois dias seguidos" |
| "A conta prévia do menor quadro provou, sem o solver, que" / "O solver provou que" (…as regras juntas…) | "Uma conta feita antes de procurar a escala já mostra que" / "A busca completa mostrou que" | diagnóstico "Combinação de regras" |
| "Conta: piso aritmético e alertas do COFEN · orçamento do clique: T" | "Conferindo as contas de horas e os alertas do COFEN · tempo máximo: T" | texto da barra |
| "…N profissionais: inviável pela conta, sem solver" | "…N profissionais: pela conta, não basta (sem precisar procurar escala)" | texto da barra |
| "…N profissionais: etapa 1 (procurando escala legal), até T — 2ª composição: acréscimos como enfermeiros" | "…N profissionais: procurando uma escala que cumpra a lei (até T) — 2ª tentativa: as pessoas a mais como enfermeiros" | texto da barra |
| "Escala pronta com N profissionais: etapa 2 (equilibrando a carga entre colegas), até T" | "Escala encontrada com N profissionais; equilibrando a carga entre colegas (até T)" | texto da barra |
| "…A Súmula 110 do TST (e a OJ 355 da SDI-1) manda pagar…" | "…A Súmula 110 do TST, o Tribunal Superior do Trabalho (e a sua Orientação Jurisprudencial 355, OJ 355 da SDI-1), manda pagar…" | alerta de descanso semanal |
| planilha "Veredito" | "Resultado" | planilha, aba Resumo |
| planilha "Diferença entre categorias na fração média (técnicos − enfermeiros; não otimizada)" — "+N pp" | "…(técnicos − enfermeiros; a ferramenta não tenta igualar)" — "+N pontos percentuais" | planilha, aba Resumo |
| planilha "CHS do QP (média das cargas contratuais)" / "QP núcleo assistencial (sem IST)" / "QP completo (com IST de 15%)" | "Horas semanais da conta do COFEN (CHS, carga horária semanal: média dos contratos da equipe)" / "Quadro recomendado pelo COFEN, só assistência (QP sem IST)" / "Quadro recomendado pelo COFEN, com 15% para férias e ausências (QP com IST, índice de segurança técnica)" | planilha, aba Resumo |
| coluna "Nível" | "Importância" | tabela "Resultado por critério" e aba Prioridades da planilha |

## O que ficou como estava, e por quê
- Alertas do COFEN ("quadro de N abaixo do QP completo do Parecer (X, com IST de 15%); o núcleo
  assistencial, sem IST, é Y"; "N turnos sem enfermeiro na demanda"): o texto é de
  `instancia_br.alertas_cofen`, fora do escopo. A tela ganhou a legenda que explica QP e IST.
- Mensagens de erro de dado (ex.: "máximo de dias seguidos … use de 1 a 6"): vêm de
  `instancia_br`; ficam.
- "Erro técnico ao resolver com N profissionais; detalhes no console." — frase do resultado
  conferida literalmente pelo teste 12c; caso raro, para quem dá suporte. Fica.
- Rótulos dos graus ("Alta dependência (10 h; 36% enfermeiros)"), cabeçalhos e o painel
  "Conferir com o COFEN (opcional) — pacientes por grau": conferidos literalmente pelo
  `tela-limpa` e já claros. Ficam.
- Nomes dos critérios, "Essencial/Importante/Desejável/Não considerar", tipos "Folga / Só este
  turno": ficam.

## Barra pelo relógio: medição (21/10, antes da suíte)

Caso 5 (8 h em três turnos, 8 enfermeiros + 5 técnicos), 3 vezes pela tela (cálculo na thread de
trabalho, com a barra) e 3 vezes com `fe.verificar` direto (sem a barra). Notebook i5-10210U,
HiGHS 1.15.1. O caso 5 chega ao limite de tempo da etapa 2 (180 s neste teste); por isso os
tempos são quase iguais e o número vale só como limite operacional desta máquina.

| | Rodada 1 | Rodada 2 | Rodada 3 |
|---|---:|---:|---:|
| Cálculo com a barra (s) | 184,3 | 184,3 | 184,3 |
| Cálculo sem a barra (s) | 184,5 | 184,8 | 184,7 |
| Clique inteiro pela tela, com os ~3 s do fechamento da barra (s) | 188,8 | 188,0 | 187,8 |

Resultado igual nas 6 rodadas: frase, menor quadro, tentativas, resultado por critério e escala
("O quadro informado admite escala legal. Escala gerada."). Script:
`medir_barra.py` (rascunho da sessão, fora do repositório).

---

## Acréscimo de 22/10: tempo dividido, resultado por nível, seção 5 enxuta

Decisão: `DECISOES.md`, "2026-10-22 — Divisão proporcional do tempo máximo; resultado por nível;
seção 5 enxuta". Só redação e arrumação; nenhuma conta muda.

### Para a Redação: frase citável que muda

| Antes | Depois |
|---|---|
| "Escala gerada; pode haver uma melhor: esta escala pode ser até X pior que a melhor possível, e com mais tempo a ferramenta poderia melhorá-la." (texto de 21/10; até 21/10 de manhã, "…(gap X: distância máxima até a melhor possível).") | "Escala gerada; pode haver uma melhor." — o quanto pode melhorar vai para as frases por nível |
| "Faltam N; o menor quadro viável é X." / "O quadro informado admite escala legal." / "Não há escala legal até N…" | **sem mudança** |

### Tela e mensagens

| Antes | Depois | Onde aparece |
|---|---|---|
| (não havia) | "<Nível>: N violações — a melhor possível." / "<Nível>: N violações. Nenhuma escala tem menos de M." / "<Nível>: N violações. Não deu tempo de saber quanto dá para melhorar." / "<Nível>: não deu tempo de otimizar; a escala mantém o resultado dos níveis acima." / bloco fundido: "Essencial e Importante: A e B violações. Nenhuma escala tem menos de M no nível Essencial." (ou "No nível Essencial, é a melhor possível; nos outros, pode haver melhor.") | 5. Resultado, acima das linhas de cada nível na tabela "Resultado por critério" |
| (não havia) | "Equilíbrio entre colegas: o melhor possível." / "Equilíbrio entre colegas: pode haver uma escala mais equilibrada." | 5. Resultado, abaixo das tabelas |
| uma tabela "Resultado por critério" | uma tabela por nível (ou bloco), cada uma com a sua frase acima | 5. Resultado |
| "?" do tempo máximo: "…avisa se ainda poderia existir uma melhor. Padrão: 60 minutos. Equipes grandes podem precisar de mais tempo." | "…avisa se ainda poderia existir uma melhor. Metade do tempo vai para atender as suas prioridades, na ordem Essencial, Importante, Desejável; a outra metade, para equilibrar a carga entre colegas. Se uma parte terminar antes, o tempo que sobrou passa para as próximas. Padrão: 60 minutos. Equipes grandes podem precisar de mais tempo." | campo "Tempo máximo para gerar a escala" |
| "Alerta de descanso semanal (não impede a escala): N profissionais têm descanso semanal abaixo de 35 h (o menor: X h). A Súmula 110 do TST, o Tribunal Superior do Trabalho (e a sua Orientação Jurisprudencial 355, OJ 355 da SDI-1), manda pagar como extras… Não conta o descanso que encosta no início ou no fim do período…" | "Atenção (não impede a escala): N profissionais têm menos de 35 h de descanso em volta da folga semanal (o menor: X h). Pela regra do TST, as horas que faltam para 35 h são pagas como hora extra." + legenda "Por que 35 h?" com o fundamento completo no "?" (o texto mora em `ferramenta.alertas_descanso`, dentro do escopo; feito lá) | 5. Resultado (amarelo) e planilha |
| "Diferença entre categorias: técnicos cumprem em média −38 pontos percentuais do contrato em relação aos enfermeiros. A ferramenta não tenta igualar isso: vem da demanda…" | "Os técnicos usam, em média, 38 pontos percentuais a menos do contrato que os enfermeiros. Isso vem da demanda de cada turno, não da escala." (ou "a mais"; com 0: "Técnicos e enfermeiros usam, em média, a mesma parte do contrato.") | Detalhes da escala |
| "Descanso mínimo entre turnos 16 h · descanso semanal 32 h · no máximo 4 dias seguidos" | "Menor descanso entre turnos: 16 h · menor descanso semanal: 32 h · maior sequência de trabalho na escala: 4 dias" | Detalhes da escala |
| legendas soltas entre os números e a tabela (escala vigente, descanso, enfermeiros/técnicos, diferença entre categorias, equilíbrio, pedidos, descumpridos) | dentro do painel "Detalhes da escala", fechado por padrão | 5. Resultado |
| "Pedidos de folga atendidos: 0 de 0" | "sem pedidos" (quando não há pedidos) | métrica e planilha |
| "sem resposta em 30 min: a ferramenta não encontrou escala…" (o 30 min era o limite fixo por resolução) | "sem resposta no tempo disponível: a ferramenta não encontrou escala nem mostrou que ela não existe" | painel "Como o resultado foi obtido" |
