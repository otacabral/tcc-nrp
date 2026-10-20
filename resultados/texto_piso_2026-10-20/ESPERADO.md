# Ajuste de texto: diagnóstico "combinação" quando quem provou foi a conta prévia (20/10)

Registrado e commitado **antes** de mexer. Item 7 das leituras adotadas do relatório de 20/10.

## O que muda (só texto)
`ferramenta.diagnosticar` ganha o parâmetro `por_conta` (padrão False). `verificar` passa
`por_conta=True` quando a primeira tentativa (o quadro informado) foi recusada pelo **piso**
("piso" em `r.tentativas[0]`), e False quando foi o solver. Só o texto do motivo "combinação"
muda nesse caso:
- solver (como hoje, **sem mudança**): "Nenhuma conta simples explica: horas, alternância,
  categoria e cada dia fecham separados. O solver provou que as regras juntas — descanso entre
  turnos, dias seguidos, férias e licenças — não admitem escala com este quadro."
- conta prévia (novo): "… fecham separados. A conta prévia do menor quadro provou, sem o solver,
  que as regras juntas — … — não admitem escala com este quadro."
Os motivos com conta simples (horas, alternância, categoria, dia) não mudam. Lógica nova: nenhuma
(a informação "piso" já existe em `r.tentativas`). Entrada do solver: não muda.

## Esperado (sem solver)
- Caso da Parte 4 com máximo 4 (14 técnicos, M 6 + T 6), `verificar(margem=0)`: tentativa
  (14, "piso"); diagnóstico "combinacao" com "A conta prévia do menor quadro provou" e **sem**
  "O solver provou". Sem chamada ao solver (margem 0, o 14 cai no piso).
- `diagnosticar(inst)` sem o parâmetro: o texto de hoje, idêntico byte a byte.
- Nenhum teste existente confere a frase (busca em `src/testes_*.py` e `docs/`); o teste
  `max-dias` ganha as duas conferências acima (acréscimo, registrado no DECISOES; roda na suíte).
- Identidade da entrada do solver com a v1.3.0: 243/243 (sem solver).
