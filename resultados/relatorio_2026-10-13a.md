# Relatório 13/10/2026 (a) — Art. 67 com horários editáveis: esperado

Correção de defeito antes do congelamento (16/10). Decisão do Otávio: correção (a) + (b).
**Este bloco "Esperado" foi registrado e commitado ANTES de qualquer mudança em `src/`.**

## O defeito

Com turnos editados na tela, o art. 67 (descanso semanal de 24 h) não é garantido pelo modelo.
Exemplo: N 23–07, folga, M 05–13 = 22 h. Passa nas 11 h (art. 66) e não é proibido. A
conferência no relógio (`medir`/`cumpre`) reprova, mas a ferramenta entrega a escala com o
veredito "admite escala legal", só com a métrica "NÃO CUMPRE", e a busca do menor quadro a conta
como viável. O argumento de 29/09 ("pior caso noite → folga → manhã = 24 h", `DECISOES.md`,
"o modelo garante o art. 67 por construção") vale só para os horários dos modelos prontos.

## A correção

**(a)** `instancia_br.pares_proibidos_por_horario`: além das 11 h / 36 h, proibir (s, 2, t)
quando 48 + ini_t − (ini_s + dur_s) < 24 (art. 67, critério conservador: toda folga isolada dá
≥ 24 h; com no máximo 6 dias seguidos, toda janela de 7 dias tem um dia sem turno, e portanto
há ao menos um descanso de 24 h por semana). Mesma fonte única.

k = 3 não precisa: o menor descanso com dois dias livres no meio é
72 + ini_t − (ini_s + dur_s) ≥ 72 + 0 − (23 + 24) = **25 h** (início ≤ 23 h, duração ≤ 24 h,
limites de `_validar_turnos`). Conferido por enumeração de todo início 0–23, duração 1–24 e
início seguinte 0–23: mínimo 25 h.

**(b)** `ferramenta`/`app`: se `cumpre()` reprovar, o veredito não é "admite escala legal", a
tela mostra erro explícito ("A escala encontrada não cumpre a conferência de descanso
(art. 67): <medida>. Não use esta escala.") e a busca do menor quadro não a conta como viável.
Segunda proteção: com (a), não deve acontecer.

## Esperado

1. **Modelos prontos e regimes do caminho por pacientes: nenhum par novo.** Conta feita em
   13/10 com o código atual (script no scratchpad, k = 2, dia do meio livre):
   - 12×36 (D 7–19, N 19–7): menor N → D = 24 h (já proibido pelas 36 h); nenhum par novo.
   - 8 h em três turnos (7–15–23): menor N → M = 24 h; nenhum par novo.
   - 6 h + noturno 12 h (7–13–19): menor N → M = 24 h (já proibido pelas 36 h); nenhum.
   - Regimes `8h` e `12x36` de `instancia_br.REGIMES` (caminho por pacientes): nenhum.

   Logo: os 544 XML idênticos byte a byte; regressão 56/58/197/219 = Tabela 6 (INRC-2010 não
   passa pelo gerador); demonstração e números do `NUMEROS_TCC.md` inalterados.

2. **Caso 23–07 + 05–13.** Antes (medido em 13/10 com o código atual): pares proibidos =
   {(N, 1, M)} só; (N, 2, M) não proibido; a sequência N → folga → M dá **22 h**. Depois:
   (N, 2, M) proibido, e o menor intervalo admitido com o dia do meio livre (k = 2) é ≥ 24 h
   (N → N 40 h, M → M 40 h, M → N 58 h).

3. **Casos da bateria e dos testes com horários próprios** (levantados por busca de toda tupla
   de horários em `src/` e `docs/`, em 13/10):

   | Caso | Horários | Par novo? |
   |---|---|---|
   | P01, P16 (bateria) | 8 h: 6–14, 14–22, 22–6 | não (N → M = 24 h) |
   | P03 | 12×36: 8–20, 20–8 | não (N → D = 24 h, já proibido) |
   | P06, P18 | 6+12: 6–12, 12–18, 18–6 | não (N → M = 24 h, já proibido) |
   | P13 | 12×36: 6–18, 18–6 | não |
   | P09, P10 e demais P/K | horários dos modelos prontos | não |
   | `testes_entrada.py`, turnos mistos | M 7 (6 h), T 13 (6 h), N 19 (12 h) | não; o teste de lista exata continua igual |
   | `testes_ferramenta.py`, demonstração, `caso_otavio_0910`, `caso_parte_a`, `escalabilidade_objetivo`, `brinquedo` | modelos prontos | não |
   | nível 3 da bateria | horários dos modelos (sorteia só demanda, equipe, férias) | não |

   **Nenhum caso ganha par novo; nada é refeito; nenhum número citável muda.**

4. **Teste novo de (b)** (`testes_ferramenta.py`, caso "16"): escala montada à mão que reprova
   — turnos N 23–07 e M 05–13, uma pessoa no ciclo N, folga, M ao longo dos 28 dias (toda
   folga isolada entre N e M: 22 h) — entregue no lugar da resolução:
   - `verificar`: veredito **não** é "admite"; `r.escala` vazia (sem grade, sem planilha);
     a frase contém "não cumpre a conferência de descanso (art. 67)", "22 h" e "Não use esta
     escala"; a tentativa fica registrada como reprovada, não como viável;
   - pela tela: a frase aparece como `st.error`; nenhum "admite escala legal" e nenhum botão
     de planilha.

   E o teste de (a) em `testes_entrada.py`: (N, 2, M) proibido no caso 23–07 + 05–13, e
   `conferir_descanso` com esses turnos dá k = 2 mínimo ≥ 24 h.

## Ordem

esperado (este commit) → regressão → (a) → (b) → testes → suíte da tela afetada → tag v1.2.3.

## Resultado

(preenchido depois da implementação, abaixo)
