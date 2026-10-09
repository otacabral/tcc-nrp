# Relatório de 09/10/2026 (b) — P15, P14, tempo-limite, encerramento da validação

Máquina: Intel Core i5-10210U, 12 GB, Windows 11, `appsi_highs` (HiGHS 1.15.1). Tempos são
limite operacional, não resultado.

## Para o Otávio

- **P15 (alerta de 35 h): feita.** O seu "31 h" era da borda do início do período; o alerta e o
  indicador agora ignoram as bordas (decisão sua). Teste 15 OK.
- **P14 (etapa 2 sem prova): feita**; suíte da tela inteira OK, regressão OK, P05/P08/K1
  iguais. Mas a etapa 2 só entregou escala em 1 de 4 casos sem prova (o K5): proposta P17
  (partir da escala da etapa 1), não implementada.
- **Falta a demonstração (B2a):** não rodou por falta de memória (2 GB livres). **A tag `v1.2`
  não foi criada.** Comandos no fim.
- **Tempo-limite (C):** 93% das resoluções da bateria provam antes de 600 s; os 7% restantes são
  da família de fronteira do 6 h + 12 h.
- **Para decidir:** a P17.


## Parte A — P15: alerta de descanso semanal abaixo de 35 h

### A0 — achado antes de implementar: o "31 h" do caso de teste é da borda do horizonte

O caso de teste do Otávio (09/10) rodado pelo código atual (`docs/diagnostico/caso_otavio_0910.py
rodar`; saída em `resultados/p14_p15_2026-10-09/otavio_antes.log`) reproduz o que ele viu:
escala sem prova (gap 17,5%), 57 enfermeiros em posto de técnico, contrato cumprido de 51% a
92%, descanso semanal mínimo 31 h, etapa 2 não rodou.

Por pessoa e por semana (`… semanal`; `otavio_antes_semanal.log`): **só 1 profissional fica
abaixo de 35 h — Téc 5, 31 h — e os 31 h são o descanso da borda inicial**, de 00:00 de
segunda 12/10 (o começo do horizonte, sem saber o que veio antes) até o M de terça às 7h. Nas
outras semanas o Téc 5 tem 42, 42 e 36 h. No meio do mês, o mínimo da escala é 36 h.

**Decisão do Otávio (09/10):** o alerta de 35 h **ignora as bordas** (o descanso que começa
no início do período e o que chega ao fim); o teste da P15 usa outro caso, montado para ter
um descanso real abaixo de 35 h; a trava de 24 h continua como está. O indicador "descanso
semanal mínimo" da tela passa a seguir a mesma regra, se isso não afetar teste ou número
registrado — **não afeta**: os testes leem o `menor_semanal` do `medir`, que é o da trava e
não muda; o valor exibido não é lido por nenhum teste nem registrado no `NUMEROS_TCC.md`; e,
pela conta, nas três planilhas da demonstração o mínimo sem bordas é 36 h, igual ao exibido
hoje. **Feito: o indicador segue a regra do alerta.**

### A2 — esperado, registrado e commitado ANTES de implementar

Conta independente, feita antes, sem o código novo (um laço próprio sobre as escalas):
caso do Otávio, mínimo sem bordas **36 h**, ninguém abaixo de 35 h; demonstração, **36 h** nas
três rodadas, sem e com bordas.

Os casos e o que se espera estão no docstring de `src/testes_ferramenta.py` (casos 15a–15d):
- **15a** (montado a mão, 8 h): `medir` (a trava, com bordas) dá 31 h, como hoje; sem bordas,
  32 h; alerta com **1 profissional, 32 h**, citando a Súmula 110;
- **15b** (demonstração, 12×36): sem alerta; mínimo sem bordas ≥ 35 h;
- **15c** (caso do Otávio, escala de hoje): sem alerta; mínimo sem bordas 36 h; `medir` 31 h;
- **15d** (tela): o indicador mostra o mínimo sem bordas; o alerta aparece em amarelo.

**Nada muda no modelo, na escala nem nos números**: o alerta e o indicador só leem a escala
pronta.

### A3 — implementação

- `docs/conferencia_descanso_escala.py`: `descanso_semanal(..., sem_bordas=False)` — com
  `sem_bordas=True`, pula o descanso que começa no início do horizonte ou chega ao fim; a
  semana sem descanso interno vale None. `semanal_sem_bordas(inst, escala)`: o mínimo por
  profissional. Sem o parâmetro, a função é a de antes (a trava de 24 h não muda).
- `src/ferramenta.py`: `SEMANAL_ALERTA_H = 35`; `alertas_descanso(inst, escala)` (o texto
  inteiro, com o prefixo "Alerta de descanso semanal (não impede a escala)"); o resultado
  ganha `alertas_descanso` e `conformidade["menor_semanal_interno"]`; a planilha mostra o
  mínimo sem bordas e o alerta.
- `src/app.py`: o alerta em amarelo (`st.warning`), depois dos alertas do COFEN; a linha do
  descanso mostra o mínimo sem bordas.
- `modelo.py` e `instancia_br.py`: intactos.

**Testes** (um processo cada; `resultados/suite_2026-10-09/`):
- `testes_ferramenta.py 15`: **código 0**, todos os itens ok — 15a (`medir` 31 h; sem bordas
  32/64/None; 1 profissional, 32 h), 15b (as três rodadas: sem alerta, 36 h), 15c (caso do
  Otávio: sem alerta, 36 h; `medir` 31 h), 15d (indicador sem bordas na tela; alerta em amarelo).
- `testes_entrada.py`: **código 0** (a medida da trava, com bordas, inalterada).

Efeito registrado: nas escalas de **8 h** o alerta tende a aparecer de verdade (no caso 5 da
tela, mínimo sem bordas de 24 h: sair às 23h e voltar às 7h do dia seguinte ao da folga dá
32 h). Os testes antigos leem erros e sucessos, não avisos — exceto o 8b, que é 12×36. A suíte
completa roda na parte B.

### A4 — guia

`GUIA_DE_USO.md`: o alerta na lista do que a ferramenta devolve; seção nova "Trava e alerta: a
diferença" (lei trava; norma técnica e custo alertam); seção "Alerta de descanso semanal", com
a Súmula 110, o exemplo das 32 h no 8 h e o que não conta (as bordas); o indicador na tabela
dos números.

## Parte B — P14: etapa 2 também sem prova

### B2 — esperado, registrado e commitado ANTES de implementar

Registro: `DECISOES.md`, "2026-10-09 — P14", com a regra (penalidade da etapa 2 ≤ valor da
etapa 1 no caminho sem prova; `=` ótimo no caminho provado, como antes) e a **salvaguarda**: no
caminho sem prova, se a etapa 2 devolver escala com critério de equilíbrio pior que o da etapa
1, fica a da etapa 1. **"Antes" = a escala da etapa 1 da mesma rodada**, porque a etapa 1 sem
prova para no limite de tempo e não acha a mesma escala a cada execução.

- **a) Demonstração da clínica** (20/19/18 técnicos), refeita pela tela com o conferidor:
  idêntica à de 09/10 (lá a etapa 1 prova o ótimo; o caminho provado não muda).
- **b) Caso do Otávio** e **c) K5 e K6**: `docs/diagnostico/p14_conferir.py` (as cinco
  conferências estão no cabeçalho): a etapa 2 roda; enfermeiro em posto de técnico ≤ o da etapa
  1; diferença máxima de carga entre colegas, em cada categoria, ≤ a da etapa 1; descanso e
  rígidas conferidos; pedidos ≥ os da etapa 1.
- **d) P05, P08, K1:** mesmo veredito e mesmo menor quadro de 07/10.
- **Teste 8b** (esperado refeito no docstring, antes): o equilíbrio deixa de dizer "não rodou";
  a linha "Escala desta tela" diz "sobre uma escala sem prova de ótimo" (ou "a da etapa 1", se a
  etapa 2 não entregar escala); os 20 pedidos continuam atendidos.
- **Textos novos:** "Escala desta tela: a da etapa 2, com a carga equilibrada entre colegas,
  sobre uma escala sem prova de ótimo: o equilíbrio não deixou piorar o valor achado pela
  etapa 1."; "Escala desta tela: a da etapa 1; o equilíbrio não achou escala mais equilibrada
  no tempo." (salvaguarda); legenda do equilíbrio: "entre as escalas que não pioram o valor da
  etapa 1 (a etapa 1 não provou o ótimo)".

### B3 — implementação

- `src/ferramenta.py`: `preparar_equilibrio(m, inst, z, exato=True)` e `equilibrar(...,
  exato=True)` — com `exato=False`, a restrição da etapa 2 é penalidade ≤ z (no lugar de = z);
  `resolver_com_objetivo` roda a etapa 2 também sem prova (`exato=provado`), guarda os
  indicadores da escala da etapa 1 em `info["etapa1"]` e aplica a salvaguarda no caminho sem
  prova; `Resultado.frase_vigente` com os dois textos novos.
- `src/app.py`: só a legenda do equilíbrio ("entre as escalas que não pioram o valor da etapa 1
  (a etapa 1 não provou o ótimo)").
- `docs/diagnostico/bateria_propriedades.py`: a troca da etapa 2 usada pelos scripts da bateria
  passou a aceitar o parâmetro novo (sem isso, os próximos usos quebrariam).
- `modelo.py` e `instancia_br.py`: intactos.

### B4 — testes: suíte da tela completa; **demonstração (B2a) não rodou, por memória**

`bash docs/diagnostico/suite_p14.sh` (um processo por teste; `resultados/suite_2026-10-09/`).
O P08 rodou antes, sozinho: admite, 12, sem falhas.

| Teste | Resultado |
|---|---|
| **B2d** P05 / P08 / K1 | faltam 1, menor 15 / admite, 12 / admite, 16 — **iguais a 07/10**, sem falhas |
| **B2b** caso do Otávio | **P14 OK** nas cinco conferências; mas a etapa 2 **não achou escala** em 180 s ("sem resposta") e ficou a da etapa 1 (57 enf. em posto de técnico; 51–92%; diferença 60 h / 24 h) |
| **B2c** K5 | **P14 OK**; a etapa 2 **entregou** escala: enf. em posto 21 = 21; diferença entre enfermeiros 42 h → **36 h**, técnicos 30 h = 30 h; contrato mínimo 68% → **72%** |
| **B2c** K6 | **P14 OK**; etapa 2 sem resposta em 180 s; ficou a da etapa 1 |
| regressão `--todos` | OK (56, 58, 197, 219) |
| tela 8 (com o 8b refeito) | OK; no 8b a etapa 2 rodou e também ficou sem resposta (limite de 25 s); 20 de 20 pedidos |
| tela 15 | OK |
| tela 12, 1-2, 3, 4, 4b, 5, 7.1, 7.2, 7.3, 7.4, 9, 9b-sem-teto, 9c-tela | **todos OK** (código 0) |
| **B2a** demonstração pela tela | **não rodou** (memória) |

**O que aconteceu com a memória.** No teste 12, o Claude Code encerrou, por memória crítica, o
processo que acompanhava a suíte (0,8 GB livres depois). O script, porém, **continuou sozinho**
(não foi relançado) e terminou todos os testes da tela, com sucesso. Antes da demonstração — que
abre um Chrome (~560 MB) e precisou de ~2,7 GB livres em 09/10 —, um vigia mediu **2.015 MB
livres**, abaixo do mínimo combinado de 3 GB, e encerrou o script: a demonstração **não
começou** (os arquivos dela continuam os da madrugada de 09/10). O teste 4, que confere que há
um só alerta vermelho, passou com o alerta novo de descanso (amarelo) presente.

**Estado da parte B:** a suíte da tela inteira e a regressão passaram; B2b, B2c e B2d passaram;
**falta só o B2a** (demonstração idêntica). **Sem ele, a parte B não fecha e a tag `v1.2` não foi
criada.** Pela conta, a demonstração não deveria mudar: nas três rodadas a etapa 1 prova o
ótimo, e o caminho provado não mudou. Mas é afirmação a conferir, não conferida.

**Achado da P14: a etapa 2 sem prova quase nunca entrega escala no tempo.** Em 4 resoluções sem
prova (caso do Otávio, K5, K6, 8b), só o K5 entregou. Causa provável: a etapa 2 não parte da
escala da etapa 1 (o código não usa warm start, `relatorio_2026-10-06f.md`, parte B1); com a
restrição "penalidade ≤ valor da etapa 1", achar a primeira escala é tão difícil quanto foi
chegar àquele valor na etapa 1 (no caso do Otávio, 600 s). As conferências passam porque, sem
escala nova, fica a da etapa 1 — o comportamento é correto, mas o ganho é raro. **Proposta
P17, registrada e não implementada:** dar à etapa 2 a escala da etapa 1 como solução inicial
(warm start "só como partida", admitido pelo `CLAUDE.md`), o que garante escala na etapa 2 e
torna desnecessária a salvaguarda.

## Parte C — o tempo-limite de 600 s da etapa 1 (só leitura, sem solver)

`python docs\diagnostico\analise_tempo_limite.py`; saída completa em
`resultados/p14_p15_2026-10-09/analise_tempo_limite.md`.

**Limite do pedido: a bateria não gravou o log do HiGHS.** As rodadas de 07/10 e das partes 3 e
4 passaram pelo caminho da tela (`ferramenta.verificar`), que não pede o log do solver; os
`.log` delas só têm as mensagens do script. Sem o log não há tempo até a primeira solução nem
até a última melhora. Logs do HiGHS existem só para 10 resoluções (parte A do diagnóstico,
07/10, e o K4 de 08/10). Por isso a análise tem duas partes.

**1. Os 10 logs do HiGHS** (todos do modelo 6 h + noturno de 12 h):

| Log | O que é | 1ª solução | Última melhora | Fim | Status | Gap final |
|---|---|---|---|---|---|---|
| `A3a_15mais5_3600s` | K6 (15 + 5), limite 3.600 s | 0 s | **826 s** | 1.077 s | ótimo provado | 0% |
| `A3b_22` | 22 pessoas, 600 s | 0 s | 305 s | 600 s | tempo esgotado | 16,7% |
| `A3b_24` | 24 pessoas, 600 s | 0 s | 160 s | 600 s | tempo esgotado | 21,1% |
| `A3b_26` | 26 pessoas, 600 s | 0 s | 358 s | 414 s | ótimo provado | 0% |
| `A3c_*` (4) | modelos relaxados (sem uma regra cada), 600 s | 0 s | 66 a 277 s | 600 s | tempo esgotado | 10,5% a 30% |
| `inviavel_16_10mais6` | prova de inviabilidade | — | — | 15 s | inviável | — |
| `highs_17` | K4 (12 + 5), interrompido por memória | nenhuma | — | ~1.909 s | sem relatório | — |

No K6 com 3.600 s: aos 600 s a melhor escala valia **19**; a última melhora, para o ótimo
**18**, veio aos **826 s** (um turno de enfermeiro em posto de técnico a menos). Nos que pararam
nos 600 s, a "última melhora" observada é censurada: não se sabe se haveria outra depois.

**2. A bateria** (161 resoluções da etapa 1 que se isolam: o caso admite o quadro informado na
primeira tentativa; 07/10, propriedades de 08/10, nível 3 de 09/10). Quando há prova, a última
melhora acontece antes dela, então o tempo da prova é um limite superior da última melhora:

| Modelo | Estrato | Resoluções | Com prova | Tempo até a prova: mediana / máximo | Sem prova (600 s) |
|---|---|---|---|---|---|
| 12×36 | folga clara | 9 | 9 | 1 / 2 s | 0 |
| 12×36 | fronteira | 11 | 11 | 1 / 6 s | 0 |
| 12×36 | níveis 1–2 e derivados | 21 | 21 | 2 / 9 s | 0 |
| 6 h + 12 h | folga clara | 5 | 5 | 1 / 4 s | 0 |
| 6 h + 12 h | fronteira | 10 | 10 | 3 / 29 s | 0 |
| 6 h + 12 h | níveis 1–2 e derivados | 42 | 30 | 2 / 274 s | **12** (K3–K6 e derivados) |
| 8 h | folga clara | 26 | 26 | 1 / 5 s | 0 |
| 8 h | fronteira | 2 | 2 | 1 / 1 s | 0 |
| 8 h | níveis 1–2 e derivados | 35 | 35 | 1 / 5 s | 0 |

**Conclusão, em uma frase:** os 600 s cobrem a última melhora em **93% das resoluções da
bateria (149 de 161), que provaram o ótimo antes do limite (no máximo em 274 s)**; nos 7%
restantes — todos da família de fronteira do 6 h + noturno de 12 h (K3 a K6 e derivados) — a
última melhora é desconhecida, e o único log longo dessa família (o K6) mostra que ela veio aos
826 s, depois dos 600 s.

**Afirmação fraca:** depende da máquina (i5-10210U), do solver (HiGHS 1.15.1 via `appsi_highs`,
parâmetros padrão) e das instâncias da bateria (até 20 pessoas, 28 dias). Vai ao texto como
justificativa operacional do limite, não como resultado.

## Parte D — registros

- **D1.** `DECISOES.md`, "2026-10-09 — Encerramento da validação; próxima frente, o texto"; nota
  no `ESTADO_ATUAL.md`. A tag `v1.2` **ainda não foi criada**: depende de a suíte da parte B
  fechar (ver B4).
- **D2.** P3 (trabalhos futuros): "Mostrar a melhor escala encontrada durante a busca da etapa
  1, antes do fim do tempo-limite" — exige o solver em paralelo, como o relógio ao vivo.
- **D3.** P16 (`PROPOSTAS.md`): a lista de melhorias de tela para 26 a 29/10 — "sem pedidos de
  folga" no lugar de "0 de 0"; gap em unidades do problema; separar "o seu quadro" da "escala
  sugerida".
- **Novo, da parte B:** P17 (`PROPOSTAS.md`), warm start da etapa 2 com a escala da etapa 1 —
  candidata, não implementada.

## Comandos

Tudo desta sessão já foi commitado e enviado (`b6fc3f7` … `c49e9cb`). Para fechar a parte B
e criar a `v1.2`, com o Chrome fechado e, de preferência, sem o Claude Code aberto (ele ocupava
~870 MB), no PowerShell, na raiz:

```
.\.venv\Scripts\Activate.ps1
& "C:Program FilesGitbinbash.exe" docs/demonstracao/rodar_rodada.sh rodada1
& "C:Program FilesGitbinbash.exe" docs/demonstracao/rodar_rodada.sh rodada2_19tec --tec 19
& "C:Program FilesGitbinbash.exe" docs/demonstracao/rodar_rodada.sh rodada2_18tec --tec 18
```

Cada rodada termina com a linha "planilhas da demonstracao: OK" no fim de
`docs/demonstracao/<rodada>_tela.txt`. Os números têm de bater com a seção 9 do `NUMEROS_TCC.md`
(24, 36, 34; 6 de 6). Se baterem:

```
git add docs/demonstracao
git commit -m "B2a: demonstracao identica com a P14"
git tag -a v1.2 -m "v1.2: P15 e P14; validacao encerrada"
git push origin main --tags
```

Se algo não bater, não crie a tag: me traga o `_tela.txt` da rodada.
