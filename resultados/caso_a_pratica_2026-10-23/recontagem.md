# Caso A — recontagem independente da escala real (23/10/2026)

Fonte: `D:\TCC\escrita\fontes\transcricao_anexoB_massens.csv` (24 linhas, 26/10 a 25/11/2018); leituras da ficha (corrigida pela Orientação em 23/10); contagem pelo `avaliacao.py` (noturno na véspera: contador da ferramenta, que o avaliacao.py não pontua). Borda e férias pela **leitura C** (Orientação, 23/10, a posteriori): bloco que toca a borda do mês conta nos critérios de máximo e sai nos de mínimo; bloco que toca as férias sai sempre. Totais de turnos só sem férias. Calendário conferido: todo P das linhas diurnas cai em sábado ou domingo (27/10/2018 é sábado).

| Critério (limite padrão) | Na recontagem (avaliacao.py) | Pessoas com violação | Ficha (Orientação) | Mesmo lado? |
|---|---|---:|---|---|
| Máx. dias seguidos, preferência (5) | violado: 30 violação(ões) | 9 (dia 9) | violado | sim |
| Mín. dias seguidos (3) | violado: 302 violação(ões) | 16 (dia 5, noite_A 5, noite_B 6) | violado | sim |
| Máx. folgas seguidas (4) | nunca: 0 violação(ões) | 0 (—) | nunca | sim |
| Mín. folgas seguidas (3) | violado: 371 violação(ões) | 24 (dia 13, noite_A 5, noite_B 6) | violado | sim |
| Máx. fins de semana seguidos (3) | violado: 26 violação(ões) | 14 (dia 9, noite_A 3, noite_B 2) | violado | sim |
| Mín. fins de semana seguidos (2) | nunca: 0 violação(ões) | 0 (—) | nunca | sim |
| Fins de semana em 4 semanas (2) | violado: 63 violação(ões) | 19 (dia 9, noite_A 4, noite_B 6) | violado | sim |
| Fim de semana completo | violado: 93 violação(ões) | 21 (dia 10, noite_A 5, noite_B 6) | violado | sim |
| Mesmo turno no fim de semana | violado: 93 violação(ões) | 21 (dia 10, noite_A 5, noite_B 6) | violado | sim |
| Máx. turnos, preferência (18) | violado: 68 violação(ões) | 12 (dia 12) | violado | sim |
| Mín. turnos (10) | nunca: 0 violação(ões) | 0 (—) | nunca | sim |
| Noturno na véspera de fim de semana livre | violado: 4 violação(ões) | 4 (noite_A 1, noite_B 3) | violado | sim |
| Duas folgas depois de noites | violado: 137 violação(ões) | 11 (noite_A 5, noite_B 6) | violado | sim |

**Os 13 critérios contáveis ficam do mesmo lado da ficha.**

## Histórico: as três leituras da borda (23/10)

A primeira recontagem usou a regra então escrita na ficha (leitura A: tirar todo bloco que toca a
borda do mês ou as férias) e pôs o máx. fins de semana seguidos do outro lado da ficha, porque os
diurnos trabalham os 5 fins de semana do mês (um bloco que toca as duas bordas). A Orientação
decidiu pela leitura C (DECISOES.md, "2026-10-23 — Caso A", a posteriori), com motivo independente
do resultado: na borda do mês, nos critérios de máximo, o bloco conta (se já passa do limite dentro
do mês, a violação é certa) e, nos de mínimo, sai (pode continuar fora da imagem); o bloco que toca
as férias sai sempre (o fim das férias não se lê na imagem — o que descarta a B).

| Leitura | Máx. fins de semana seguidos | Máx. folgas seguidas | Reproduz a ficha? |
|---|---|---|---|
| A — tirar todo bloco que toca a borda ou as férias | nunca | nunca | não (máx. fins de semana) |
| B — nos de máximo, contar os blocos de borda e também os que tocam as férias; nos de mínimo, tirar | violado (26, em 14 pessoas) | violado (1: o 5976, 5 dias sem trabalho de 21 a 25/11, logo depois das férias de 15 a 20/11) | não (máx. folgas) |
| C — nos de máximo, contar o bloco de borda do mês; nos de mínimo, tirar; o que toca as férias, sempre tirar | violado | nunca | sim |

"Mesmo turno no fim de semana": pela semântica do `avaliacao.py`/avaliador oficial, quem trabalha um
só dia do fim de semana viola; a ficha (que dizia "sem ocorrência") foi corrigida pela Orientação;
a classificação continua Não considerar, agora por evidência.
