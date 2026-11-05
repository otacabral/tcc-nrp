# Caso A — recontagem da escala real com a transcrição v2 (05/11/2026)

Fonte: `resultados/caso_a_2026-11-04/transcricao_anexoB_massens_v2.csv`. É a v1 (`resultados/caso_a_pratica_2026-10-23/transcricao_anexoB_massens.csv`) com a faixa de férias completa, conferida pelo Otávio na p. 70: o 6137 de 31/10 a 15/11 (16 dias) e o 5976 de 15/11 a 25/11 (11 dias). Quinze células passaram de branco para FERIAS; nenhuma célula com registro mudou. Janela de 31 dias, 26/10 a 25/11, como antes. Mesmas leituras, mesma leitura C e mesmas 21 linhas com registro do `recontagem.md` de 26/10 (ficam fora: 6118, 4798, 6089). Decisão: `DECISOES.md`, "2026-11-04 — Caso A: entrada revista". Regra: violado → Não considerar; nunca violado, com ocorrência → Importante; sem ocorrência testável → sem evidência → padrão.

O que conta como ocorrência testável (o que a leitura C deixa contar):
- sequências de dias, de folgas e de fins de semana: os blocos dentro da janela da leitura C (nos de
  mínimo, sem o primeiro e o último bloco de cada trecho; nos de máximo, sem o bloco que toca as
  férias); blocos de trabalho nos critérios de trabalho, blocos de folga nos de folga;
- fim de semana completo e mesmo turno: fins de semana com algum dia trabalhado, fora das férias;
- fins de semana em 4 semanas (limite 2): trechos com pelo menos 3 fins de semana inteiros;
- noturno na véspera: fins de semana livres com a sexta no trecho;
- duas folgas depois de noites: sequências de noites com os 2 dias seguintes no trecho;
- máximo e mínimo de turnos: pessoas sem férias.

| Critério (limite padrão) | Ocorrências testáveis | Violações (avaliacao.py) | Pessoas com violação | Lado | Esperado (classificação g) | Mesmo lado? |
|---|---:|---:|---:|---|---|---|
| Máx. dias seguidos, preferência (5) | 211 | 30 | 9 (dia 9) | violado | violado | sim |
| Mín. dias seguidos (3) | 188 | 302 | 16 (dia 5, noite_A 5, noite_B 6) | violado | violado | sim |
| Máx. folgas seguidas (4) | 208 | 0 | 0 (—) | nunca violado | nunca violado | sim |
| Mín. folgas seguidas (3) | 190 | 359 | 21 (dia 10, noite_A 5, noite_B 6) | violado | violado | sim |
| Máx. fins de semana seguidos (3) | 23 | 26 | 14 (dia 9, noite_A 3, noite_B 2) | violado | violado | sim |
| Mín. fins de semana seguidos (2) | 0 | 0 | 0 (—) | sem evidência | sem evidência | sim |
| Fins de semana em 4 semanas (2) | 20 | 63 | 19 (dia 9, noite_A 4, noite_B 6) | violado | violado | sim |
| Fim de semana completo | 93 | 93 | 21 (dia 10, noite_A 5, noite_B 6) | violado | violado | sim |
| Mesmo turno no fim de semana | 93 | 93 | 21 (dia 10, noite_A 5, noite_B 6) | violado | violado | sim |
| Máx. turnos, preferência (18) | 19 | 59 | 9 (dia 9) | violado | violado | sim |
| Mín. turnos (10) | 19 | 0 | 0 (—) | nunca violado | nunca violado | sim |
| Noturno na véspera de fim de semana livre | 8 | 4 | 4 (noite_A 1, noite_B 3) | violado | violado | sim |
| Duas folgas depois de noites | 146 | 137 | 11 (noite_A 5, noite_B 6) | violado | violado | sim |

**Os lados dão a classificação g)**: o mínimo de fins de semana seguidos fica sem evidência (padrão: Não considerar), e o resto fica do mesmo lado da ficha.
