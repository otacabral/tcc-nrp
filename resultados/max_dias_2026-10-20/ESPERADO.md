# Parte 4 (3º bloco, 20/10) — Máximo de dias seguidos do hospital: decisões e esperado

Registrado e commitado **antes** de implementar. Decisão: `DECISOES.md`, "2026-10-19 — Máximo de
dias seguidos como regra do hospital (rígida)".

## Decisões de implementação (registradas antes)
1. `Entrada.max_dias_seguidos` (padrão 6 = `MAX_CONSECUTIVOS_GENERICO`). `montar` o passa a
   `instancia_br.construir(..., max_consecutivos=...)`, que o leva ao contrato (máximo de dias
   seguidos, rígido) **e** ao gerador de pares (`pares_proibidos_por_horario`), como o 6 de hoje.
   Fora de 1–6 → erro de entrada ("acima da lei").
2. Tela: no grupo 2, no lugar da linha cinza "Máximo de dias seguidos de trabalho — já garantido
   pela CLT", um campo numérico (1 a 6, padrão 6) com a importância fixa "Obrigatória". Oculto
   quando o limite efetivo é 1 (só turnos de 12 h, o 12×36). Não entra no contador "k de n
   considerados" (não é critério da função objetivo).
3. "O diagnóstico usa o 4": `limite_efetivo` lê o contrato, então o piso aritmético
   (`piso_de_alternancia`: em qualquer janela de L + 1 dias, cada pessoa trabalha no máximo L) e o
   diagnóstico passam a usar o 4. **Leitura adotada:** não há mensagem de diagnóstico própria para
   L entre 2 e 5 (só a do 12×36); não acrescento uma, porque mudaria o texto de casos do padrão.

## Testes e esperado
- **Identidade:** padrão (campo 6, ou sem o campo) → entrada do solver idêntica à da v1.3.0:
  **243 de 243**.
- **Caso com 4.** Turnos M 7–13 e T 13–19 (6 h), demanda de técnicos M 6 e T 6 em todos os dias
  (12 postos/dia, 72 h/dia, 2.016 h em 28 dias), 0 enfermeiros, 14 técnicos.
  - Com **6**: piso = max(horas: 2.016 / 176 → 12; janela de 7 dias: ⌈7 × 12 / 6⌉ = **14**) = 14.
    Esperado: veredito "admite escala legal" com 14.
  - Com **4**: piso = ⌈5 × 12 / 4⌉ = **15** → o 14 é "inviável pela conta" (sem solver).
    Esperado: "Falta 1; o menor quadro viável é 15." (15 é atingível: 5 grupos de 3, cada grupo de
    folga num dia de cada 5; 12 trabalham por dia; ninguém passa de 4 seguidos).
    `limite_efetivo` = 4; nenhuma sequência maior que 4 na escala, contada fora do modelo
    (pela conferência no relógio e por contagem direta na escala).
  - Diagnóstico do 14 com 4: nenhuma conta simples dispara (horas e cada dia fecham) → o texto
    de "combinação de regras". *Observação registrada antes:* esse texto diz "O solver provou…",
    mas aqui quem provou foi o piso (sem solver) — imprecisão do texto que já existe no padrão
    (o piso com L = 6 também pode disparar); vai ao relatório, não é corrigida nesta parte.
- **Campo acima da lei:** 7 → erro de entrada.
