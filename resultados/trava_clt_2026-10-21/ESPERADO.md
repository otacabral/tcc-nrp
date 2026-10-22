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
