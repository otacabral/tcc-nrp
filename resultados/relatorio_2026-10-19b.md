# Relatório da sessão de 19/10/2026 — 2º bloco: implementação da opção B

Pedido da Orientação (2º bloco de 19/10), decisões aprovadas pelo Otávio. Esperado registrado
e commitado antes de implementar: `resultados/opcao_b_2026-10-19/ESPERADO.md` (commit
`a9822da`; implementação no `5a445ec`).

**Estado: implementada; suíte de fechamento INTERROMPIDA pelo sistema, por falta de memória,
depois de 17 passos, todos OK. Tag `v1.3.0` NÃO criada** — a regra é tag só com tudo passando.

## 0. NUMEROS_TCC.md

Seção 14 (validação por restrição nos 4 ótimos) incluída, como aprovada.

## 1. DECISOES.md

"2026-10-19 — Opção B: mecanismo, tempo e critérios expostos", MUDANÇA DE FORMULAÇÃO, com os
itens (a)–(c) da Orientação e **sete decisões de implementação registradas antes de
implementar**. Duas pedem atenção da Orientação:
- **"a CLT prevalece"**: com as três famílias legais sem campo, nenhum limite exposto pode ser
  "mais frouxo que a lei"; a situação ficou para o limite que **contradiz** a lei (mínimo de dias
  seguidos acima do que o descanso admite — 1 no 12×36 —; mínimo de turnos acima do teto legal);
- **limites padrão** dos critérios com parâmetro: os do contrato 0 do `medium_late05`; fins de
  semana em 4 semanas = 2, sem fonte.

## 2. O que mudou no código

- `src/prioridades.py` (novo): catálogo dos 16 critérios (13 com campo, 3 "já garantido pela
  CLT"), máximo de violações (as fórmulas do censo de 19/10 — o censo passou a chamar esta
  função; saída do censo idêntica byte a byte), plano de fusão (< 10.000), situação, resultado
  por critério.
- `src/ferramenta.py`: `modelo_etapa1` (pesos = coeficiente do nível no bloco), níveis em
  sequência com o anterior preso (`<=`, partindo da escala anterior), `TEMPO` = `TEMPO_ETAPA2` =
  1.800 s, `ORCAMENTO` = 60 min, `Entrada.prioridades`, `Resultado.criterios`, aba
  "Prioridades" na planilha. O caminho usado vai ao console e a `info["caminho"]`.
- `src/app.py`: tabela "Prioridades da escala" (4 grupos; o 1 aberto; contador "k de n
  considerados"; Importância, Limite, Situação; uma linha de ajuda por critério, com exemplo;
  ⓘ nos sem conferência externa), "Restaurar padrão", aviso de mesmo nível, campo de orçamento
  (minutos, padrão 60), "Resultado por critério".
- `src/solucao.py`: contagem do noturno antes de fim de semana livre também por pessoa (a de
  antes passa a somá-la).
- `GUIA_DE_USO.md`: seção das prioridades e do orçamento; as três menções a "20 min" (e as de
  10 e 3 min) atualizadas; a planilha com quatro abas.
- `src/modelo.py` e `src/instancia_br.py`: **não mudaram**.

## 3. Testes — resultado

Suíte `docs/diagnostico/fechar_v130.sh` (um processo por teste; `resultados/opcao_b_2026-10-19/
suite/resumo.txt`):

| Passo | Resultado |
|---|---|
| (a1) entrada do solver, v1.2.3 × atual, classificação padrão | **243 de 243 idênticos** (81 casos: bateria P01–P18 e K1–K6, as três rodadas da demonstração, acréscimos 0, 1 e 2; XML da instância, LP da etapa 1, LP da etapa 2). Controle positivo: uma suave ligada muda o LP — **ok** |
| regressão `--todos` | **OK** (56, 58, 197, 219 = Tabela 6) |
| `testes_entrada.py` | **OK** (inclui as partes com solver: `long01` 40 viável, indisponibilidade) |
| opB-padroes | **OK**: 1.800 s, 1.800 s, 3.600 s; campo da tela abre em 60 |
| opB-d (situação) | **OK**: "a CLT prevalece" (mínimo de dias seguidos 2 e mínimo de turnos 20 no 12×36), "nunca será atendido" (fim de semana completo e mesmo turno no 12×36), "já garantido pela CLT" (3 linhas), "ok" no 8 h. **Rodada pequena**: mesmo turno no fim de semana = **8** e fim de semana completo = **8**, como a conta — confirma o que o relatório 3c tinha lido do código |
| opB-b (sequência = definição) | **OK**: **(0, 1, 14)** pelo caminho fundido, pelo caminho em sequência forçado (3 blocos, todos provados) e pela definição resolvida à parte; resultado por critério (0/0, 1/1, 14/2); invertida (0, 1, 14) |
| opB-c (fusão) | **OK**: padrão = 1 bloco {pedido 286, enfermeiro 1}, máximo 2.001; suaves no Desejável = 2 blocos ({286, 1} máx. 2.001 e 11 suaves com peso 1, máx. 5.010). Rodada da demonstração com as suaves no Desejável: "em sequência, 2 blocos"; bloco de cima **24, provado** (0 pedido negado, 24 enfermeiros em posto de técnico — o mesmo da demonstração); bloco Desejável 2.201 **sem prova** em 600 s (gap 28,0%); escala cumpre o descanso |
| opB-e (Essencial não trava) | **OK**: caso pequeno admite 3 = padrão; caso 5 admite 13 = padrão; as duas em sequência (2 blocos), escalas cumprem o descanso |
| opB-tela | **OK**: grupos e contadores, padrão, restaurar, aviso de mesmo nível, orçamento padrão não vai (None) e 2 min chega como 120 s, resultado na tela = aba Prioridades da planilha |
| tela antigos: 16, 4b, 7.4, 9b-sem-teto, 9c-tela | **OK** |
| tela antigos: 3, 4, 5, 15, 7.1, 7.2, 8, 12, 1-2, 9, 7.3 | **NÃO RODARAM** (interrupção durante o 3) |
| (a2) bateria P01–P18 e demonstração (600/180/20 min) | **NÃO RODOU** na suíte. Só o P04, à mão, antes: igual ao registrado |

**Interrupção.** Às ~18h00, durante o caso 3 da tela, o Claude Code encerrou a suíte porque o
sistema estava com pouca memória (aviso do próprio Claude Code: não é falha do comando). O
processo órfão do caso 3 foi encerrado; memória livre depois: ~2 GB. Pela regra recebida, a
suíte **não foi relançada** sem pedido.

**Para retomar** (pula o que já passou e acrescenta ao resumo):

    RETOMAR=1 "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v130.sh

Precisa do worktree da v1.2.3 em `../tcc-nrp-v123` (existe) e, de preferência, com o Chrome e
outros programas fechados. Faltam ~11 casos da tela (os mais longos, como 7.2, 8 e 12, levam
minutos cada) e o (a2) (~1 h).

## 4. Pendências

- Retomar a suíte; se passar, tag `v1.3.0` (comando no PASSAGEM).
- Levar à Orientação as duas leituras de implementação acima.
- Observação do opB-c para o texto: com as suaves no Desejável, o bloco Desejável da
  demonstração não provou o ótimo em 600 s (gap 28%). Com o padrão novo (1.800 s), não medido.
  Tempo é limite operacional, não resultado.
- Nada enviado ao GitHub. Falta enviar: os commits de 19/10 (1º e 2º blocos). Comando:
  `git push origin main`; a tag `v1.3.0` só depois de criada.
