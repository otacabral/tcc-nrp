# P20 (23/10) — prender o valor verdadeiro depois de um nível sem prova: esperado

Registrado e commitado **antes** de implementar e de rodar. Decisão: `DECISOES.md`, "2026-10-23 —
P20 aprovada: trava pelo valor verdadeiro depois de nível sem prova".

## Implementação (registrada antes)
- Novo `ferramenta._apertar(m, limite)`: com o objetivo do nível ainda ativo, fixa as atribuições
  `m.x` da escala carregada (0/1, arredondadas), resolve de novo — só folgas e auxiliares livres; o
  `y` sai do `x` por igualdade — e solta o `x`. Devolve o valor verdadeiro do nível e deixa todas
  as variáveis com as folgas no mínimo que a escala exige. Limite: o menor entre 60 s e o que resta
  do prazo (no mínimo 1 s).
- Em `_niveis_em_sequencia`, ao fechar um bloco **sem prova**: z = `_apertar`; a trava do bloco
  (`expr ≤ z`) usa esse z; o bloco seguinte parte dessas variáveis (já apertadas). Com prova,
  nada muda.
- Em `resolver_com_objetivo`: a etapa 2 (penalidade ≤ z, P14) usa o z apertado quando a etapa 1
  não provou (caminho de um bloco e último bloco do caminho em sequência). Com prova, nada muda.
- Se o aperto falhar (sem resposta ou erro), fica o valor do modelo, como antes, e isso é
  registrado em `info["partes"]` (`aperto`).
- `info["partes"]` ganha, por bloco sem prova, `valor_modelo` (o de antes) e `valor` (o apertado).

## Esperado
1. **Identidade inalterada:** 243/243 (sem e com linhas) e 24/24 contra a v1.4.2 — a primeira
   resolução de cada nível e o LP enviados não mudam (o aperto é uma resolução a mais, depois).
2. **Teste novo `p20`** (`src/testes_ferramenta.py`): caso 5 (8 h em três turnos, 8 enf. + 5 téc.,
   M e T 1 + 2, N 1 + 1), critérios de folga ligados — todas as suaves no Essencial
   (`_todas_suaves`), enfermeiro em posto de técnico no Importante, pedido de folga no Essencial —,
   blocos separados (`LIMITE_FUSAO = 0`) e prazo curto (tempo máximo de 30 s, sem teto por
   resolução), para o bloco Essencial terminar **sem prova** (o "todas as suaves no Essencial"
   desse caso não prova em minutos: teste opB-e).
   - (a) o bloco Essencial termina sem prova e com escala;
   - (b) o valor preso (`partes[0]["valor"]`) = a contagem verdadeira do Essencial na escala do fim
     do bloco, recalculada **fora do modelo** (`prioridades.resultado`, Σ coeficiente × violações
     dos critérios do bloco);
   - (c) `valor_modelo` ≥ `valor` (o aperto nunca sobe o número); se forem iguais, o teste diz
     que as folgas já estavam justas nessa rodada (o mecanismo não foi exercitado, o que não é
     falha);
   - (d) **o nível de cima não piora:** na escala final (depois do Importante e da etapa 2), a
     contagem verdadeira do Essencial ≤ o valor preso;
   - (e) a escala final cumpre o descanso (conferência no relógio).
3. **Testes rápidos da opção B, sem mudança:** opB-b (os três níveis provam: nada muda), opB-d,
   opB-padroes, max-dias, pref-tela, e a conta do tempo (`tempo_proporcional.py --conta`).
