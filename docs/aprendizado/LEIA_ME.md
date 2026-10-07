# Material de estudo do código — para quem não programa

Conteúdo da pasta `docs/aprendizado/`:

- **este arquivo:**
  - B1, o que o código faz e o que não faz com o solver;
  - B3, o modelo da instância de brinquedo, linha a linha;
  - B4, como ler o log do HiGHS;
- `PASSEIO_DE_UM_CLIQUE.md` (B5): o caminho de um clique em "Gerar escala" até a planilha;
- `brinquedo.py` (B2): monta a instância de brinquedo pelo mesmo caminho da tela, grava o modelo em `.lp` e roda o HiGHS com log;
- `brinquedo.lp`, `brinquedo_highs.log`, `brinquedo_inviavel_highs.log`: o que o script gerou.

---

## B1. O que o código faz (e não faz) com o solver

Conferido na `v1.0.1`.

**(a) Não existe warm start nem heurística de partida.** A primeira escala vem do próprio HiGHS. `src/modelo.py`, função `resolver` (linhas 464–520), só faz três coisas:
- cria o solver: `pyo.SolverFactory(solver)`, com `appsi_highs` por padrão (`SOLVER_PADRAO`, linha 30);
- passa o limite de tempo;
- passa o arquivo de log.

Nenhum valor inicial é dado às variáveis. Nenhum script do repositório usa "warm start": a palavra só aparece em comentários de `src/escalabilidade.py`, que discutem se valeria a pena tê-lo. No log do HiGHS, a letra no começo da linha mostra qual heurística dele achou a escala; por exemplo, `J` (*feasibility jump*), `L` (busca local num sub-problema), `T` (nó da árvore). Veja a B4.

**(b) O HiGHS roda com os parâmetros padrão, exceto dois:**
- o **tempo-limite** (`opt.config.time_limit` e o argumento `timelimit` da chamada, linhas 478–508);
- o **arquivo de log** (`opt.options["log_file"]`, linha 498).

Não há ajuste de threads, semente, estratégia de busca ou tolerância.

**(c) Tolerância de gap: a padrão do HiGHS**, gap relativo de **0,01%** (`mip_rel_gap` = 1e-4). O próprio log a imprime, por exemplo em `resultados/diagnostico_2026-10-07/A3a_15mais5_3600s.log`, linha 213: `Gap 0% (tolerance: 0.01%)`. "Ótimo provado", na ferramenta, quer dizer gap ≤ 0,01%.

**(d) A tag `v1.0.1` existe** e aponta para o commit `35a9cd178311f8c67678bd7b0322f7136e6bf630` (`35a9cd1`). A `v1.0` aponta para `c64dcf9`.

*(B3 e B4 vêm a seguir, depois que a instância de brinquedo rodar.)*
