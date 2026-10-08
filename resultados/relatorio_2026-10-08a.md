# Relatório de 08/10/2026 (a) — bateria: K3/K4 com 3.600 s, propriedades 2 e 3, nível 3

*Escrito parte a parte, numa sessão sem supervisão (madrugada de 07 para 08/10). Cada parte
foi commitada e enviada ao fim. Travas: nada em `src/` nem nos testes; scripts só em
`docs/diagnostico/`.*

Máquina: i5-10210U, `appsi_highs` (HiGHS 1.15.1). Tempos são limite operacional, não
resultado.

## Parte 1 — correções e conferência dos esperados

**1a.** `docs/bateria_entradas.md`: a nota de 07/10 dizia "níveis 2 e 3 ainda não rodados".
O nível 2 (K1–K6) rodou. Corrigida para o que faltava de fato: propriedades 2 e 3 da C3 e
nível 3. A correção fica marcada na própria nota.

**1b.** Os esperados usados na rodada de 07/10 são os do commit `545bae9`:
- `docs/diagnostico/bateria_desenho.py` tem um único commit (`62bbf4d`, 07/10 00:47), anterior
  a `545bae9`; sem diferença no arquivo de trabalho. Modificado pela última vez às 00:46 de
  07/10; a rodada começou às ~21:02 do mesmo dia.
- Rodado de novo agora, o gerador reproduz a tabela de `docs/bateria_entradas.md` em
  `545bae9`: P01–P18 com caso, modelo, equipe, esperado e as quatro folgas idênticos (a tabela
  do documento só tem acentos, que o script não usa); K1–K6 com o mesmo veredito e as mesmas
  folgas citadas na tabela do nível 2.
- O esperado gravado em cada JSON da rodada é calculado pelo mesmo arquivo, na hora.

**Nenhum caso muda; todos contam como teste.**
