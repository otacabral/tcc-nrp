# Parte 5 (3º bloco, 20/10) — Limpeza da tela: decisões e esperado

Registrado e commitado **antes** de implementar. Decisão: `DECISOES.md`, "2026-10-19 — Tela
orientada ao usuário". Nenhum número muda.

## Decisões de implementação (registradas antes)
1. **Numeração.** Títulos: "1. Configuração da unidade", "2. Equipe", "3. Demanda", o expansor
   "Conferir com o COFEN (opcional) — pacientes por grau" no mesmo lugar e **sem** o "4.",
   "4. Prioridades da escala", "5. Resultado".
2. **Rótulos dos turnos.** A tabela de turnos mostra "Manhã", "Tarde", "Noite" (12×36: "Dia",
   "Noite"). O código interno continua M, T, N, D: rótulo padrão → código por um mapa fixo
   (Manhã→M, Tarde→T, Noite→N, Dia→D); nome digitado fora do mapa (ex.: "D12") é o próprio
   código. Assim `Entrada.turnos`, o XML e o LP **não mudam**. As chaves dos campos de demanda
   continuam pelo código (`g_M_enf` …); o rótulo vai no texto do campo. A grade da escala e a
   legenda continuam com as siglas. Na tabela de pedidos, a coluna Turno mostra os rótulos e grava
   o código.
3. **Graus:** "Alta dependência (10 h; 36% enfermeiros)" e "Semi-intensivo (10 h; 42%
   enfermeiros)", na seção 1 e no expansor do COFEN (valores do Parecer COFEN 1/2024, já em
   `instancia_br.GRAUS`: 0,36 e 0,42).
4. **"(fds)" → "(fim de semana)"** nos campos de demanda do fim de semana.
5. **Prioridades:** sem a coluna Situação; sem as linhas "Sequências indesejadas" e "Máximo de
   turnos no período" (as regras ficam no back end); no 12×36 (só turnos de 12 h) ficam ocultas
   "Fim de semana completo", "Mesmo turno no fim de semana" e "Mínimo de dias seguidos de
   trabalho". **Leitura adotada:** critério oculto vale como "Não considerar" (não entra na
   classificação enviada), mesmo que tenha sido escolhido antes de trocar o modelo de turnos.
   Limites presos pela lei: "Mínimo de dias seguidos" ≤ máximo de dias seguidos (6, ou o do
   hospital); "Mínimo de turnos no período" ≤ teto legal de turnos do contrato.
6. **Explicações.** Cada critério ganha uma descrição de uma linha (`Criterio.resumo`) na tela e
   o texto longo (a ajuda de hoje, com exemplo) no "?" (`help`). Fins de semana em 4 semanas: a
   ajuda diz "valor de exemplo, sem fonte (suposição declarada)" (Parte 1a). Saem os parágrafos
   explicativos das seções 2 (carga contratual) e 4 (prioridades); o texto vai ao `help` e ao
   `GUIA_DE_USO.md`. Mensagens de resultado não mudam.

## Esperado
- **Identidade:** entrada do solver idêntica à da v1.3.0: **243 de 243** (a tela não entra nesse
  teste; ele prova que nada da Parte 5 tocou o back end).
- **Tela** (teste novo `tela-limpa`, AppTest): cabeçalhos na ordem 1–5; expansor do COFEN sem
  "4."; rótulos dos graus; nenhum texto "(fds)"; nenhuma "Situação" nem "já garantido pela CLT";
  no 12×36, os três critérios ocultos e no 8 h visíveis; a tabela de turnos com "Manhã", "Tarde",
  "Noite" no 8 h e "Dia", "Noite" no 12×36; uma rodada do caso 5 pela tela dá o mesmo veredito e
  os mesmos indicadores de antes (texto de resultado inalterado).
- **Testes antigos da tela que conferem texto removido:** só o opB-tela (contadores dos grupos
  no 12×36: "0 de 2" e "0 de 3"; linhas cinza: 0). Atualização registrada no DECISOES, como a do
  1-2. Os demais (16, 4b, 7.4, 9b, 9c, 3, 4, 5, 15, 7.1, 7.2, 8, 12, 1-2, 9, 7.3, opB-*, ped-*,
  max-dias) passam sem mudança; ficam para a suíte de fechamento, com o Claude Code fechado. Aqui
  rodam os rápidos que passam pela tela (opB-tela, tela-limpa, 16, 4b, 7.4, 9c-tela).
