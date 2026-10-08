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

## Parte 2 — K4 (17) e K3 (16), só a etapa 1, 3.600 s

**Esperado registrado antes de rodar** (este parágrafo foi commitado antes do primeiro
solver): a conta independente **não prova escala** em nenhum dos dois — folga 1 em ocupados
por dia no K4 e 0 no K3 — e também **não prova inviabilidade** (nenhuma folga negativa).
Qualquer dos três desfechos é possível: escala achada, inviabilidade provada ou tempo esgotado.
O que separaria as camadas (C4): escala achada → a falha de 07/10 era de **solver** (tempo);
inviabilidade provada → a conta da bateria é frouxa demais para esta família, e o caso passa a
"inviável com prova".

Como roda: `docs/diagnostico/caso_parte_a.py etapa1 --enf N --tempo 3600 --log <arq>`, o
mesmo caminho da parte A (`ferramenta.montar` → `ferramenta.pesos` →
`experimento_a.modelo_br`), com a entrada idêntica à de K3/K4 (6 h + noturno de 12 h, M 2+1,
T 2+1, N 3+2, início 12/10/2026, grau intermediário, 5 técnicos). Um por vez, K4 primeiro,
nada mais rodando na máquina.
