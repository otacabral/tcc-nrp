# Parte 6 — descanso depois do D12 como parâmetro de pesquisa: implementação e esperado

Registrado e commitado **antes** de implementar. Decisão: `DECISOES.md`, "2026-10-20 — a
posteriori: descanso depois do D12 como parâmetro de pesquisa". **Hipótese de sensibilidade, não
regra da ferramenta.**

## Implementação (o menor desvio)
- `instancia_br.py`: as constantes (`INTERJORNADA` 11, `POS_TURNO_LONGO` 36, `TURNO_LONGO` 12)
  continuam e passam a ser o **padrão**; entra `DESCANSO_POR_TURNO: dict[str, int] = {}` (código
  do turno → horas de descanso exigidas depois dele). `descanso_exigido(duracao_h, turno=None)`
  devolve o valor do dicionário se o turno estiver nele (a variante de enfermeiro, `<código>E`,
  usa o valor do código), senão a regra de hoje. Vazio = comportamento atual.
- `pares_proibidos_por_horario` passa o código do turno; `conferencia_descanso_escala.medir`
  também. Mesma fonte para os dois. Nada na tela nem na `Entrada`.
- `interjornada=False` (o `--sem-descanso-clt`) continua desligando só os turnos cujo exigido é
  11 h — com D12 = 11 h, o D12 entra nessa regra, como os demais turnos de 11 h.
- Regra de parada: se exigir mais do que isso, não fazer e registrar como limitação.

## Esperado
1. **Padrão:** entrada do solver **243/243** idêntica à v1.3.0.
2. **Caso pequeno à mão** (modelo M 7–13, T 13–19, N 19–7, D12 7–19; 1 técnico; 7 dias a partir
   de uma segunda; demanda só nos dias indicados; resolvido pelo solver, caso mínimo):
   - D12 no d1 e M no d2 (descanso 7h−19h = **12 h**): padrão (36 h) → **inviável**; D12 = 11 h →
     **viável**.
   - N no d1 e M no d2 (0 h): **inviável** nos dois.
   - N no d1 e M no d3 (24 h): **inviável** nos dois (a noite de 12 h continua com 36 h).
3. **Gerador:** (D12, 1, M) está na lista no padrão e **não está** com D12 = 11 h; (N, 1, M) e
   (N, 2, M) estão nos dois.
4. **Conferência no relógio acompanha o parâmetro:** a escala "D12 no d1, M no d2" (montada à
   mão) **reprova** em `cumpre` no padrão (falta de 24 h, exigido 36 h, artigo 59-A em
   `reprovacao`) e **cumpre** com D12 = 11 h. A escala "N no d1, M no d3" reprova nos dois.
5. Com o dicionário restaurado ao fim do teste, o padrão volta (o teste confere).

Premissa compartilhada: o gerador e a conferência leem a mesma `descanso_exigido` — por
desenho; o teste 2 (solver) e o 4 (relógio) conferem que os dois a seguem, não que 11 h é a
leitura certa da lei.
