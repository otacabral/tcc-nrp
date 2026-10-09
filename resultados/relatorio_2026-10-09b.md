# Relatório de 09/10/2026 (b) — P15, P14, tempo-limite, encerramento da validação

Máquina: Intel Core i5-10210U, 12 GB, Windows 11, `appsi_highs` (HiGHS 1.15.1). Tempos são
limite operacional, não resultado.

<!-- PARA_O_OTAVIO -->

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
