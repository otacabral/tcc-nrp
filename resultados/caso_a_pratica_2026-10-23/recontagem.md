# Caso A — recontagem independente da escala real (23/10/2026)

Fonte: `D:\TCC\escrita\fontes\transcricao_anexoB_massens.csv` (24 linhas, 26/10 a 25/11/2018); leituras da ficha; contagem pelo `avaliacao.py` (noturno na véspera: contador da ferramenta, que o avaliacao.py não pontua). Sequências só em blocos inteiros (bordas e férias fora); totais de turnos só sem férias. Calendário conferido: todo P das linhas diurnas cai em sábado ou domingo.

| Critério (limite padrão) | Na recontagem (avaliacao.py) | Pessoas com violação | Ficha (Orientação) | Mesmo lado? |
|---|---|---:|---|---|
| Máx. dias seguidos, preferência (5) | violado: 30 violação(ões) | 9 (dia 9) | violado | sim |
| Mín. dias seguidos (3) | violado: 302 violação(ões) | 16 (dia 5, noite_A 5, noite_B 6) | violado | sim |
| Máx. folgas seguidas (4) | nunca: 0 violação(ões) | 0 (—) | nunca | sim |
| Mín. folgas seguidas (3) | violado: 371 violação(ões) | 24 (dia 13, noite_A 5, noite_B 6) | violado | sim |
| Máx. fins de semana seguidos (3) | nunca: 0 violação(ões) | 0 (—) | violado | **NÃO** |
| Mín. fins de semana seguidos (2) | nunca: 0 violação(ões) | 0 (—) | nunca | sim |
| Fins de semana em 4 semanas (2) | violado: 63 violação(ões) | 19 (dia 9, noite_A 4, noite_B 6) | violado | sim |
| Fim de semana completo | violado: 93 violação(ões) | 21 (dia 10, noite_A 5, noite_B 6) | violado | sim |
| Mesmo turno no fim de semana | sem ocorrência: 93 violação(ões) | 21 (dia 10, noite_A 5, noite_B 6) | sem ocorrência | sim |
| Máx. turnos, preferência (18) | violado: 68 violação(ões) | 12 (dia 12) | violado | sim |
| Mín. turnos (10) | nunca: 0 violação(ões) | 0 (—) | nunca | sim |
| Noturno na véspera de fim de semana livre | violado: 4 violação(ões) | 4 (noite_A 1, noite_B 3) | violado | sim |
| Duas folgas depois de noites | violado: 137 violação(ões) | 11 (noite_A 5, noite_B 6) | violado | sim |

**PARAR: mudaram de lado: Máx. fins de semana seguidos (3)** (levar à Orientação).

## Por que o critério mudou de lado (diagnóstico, 23/10) — para a Orientação

**Máx. fins de semana seguidos (3).** Os diurnos trabalham os 5 fins de semana do mês (`XXXXX`):
um bloco único, que toca as duas bordas do mês. A recontagem acima tirou **todo** bloco que toca
borda ou férias, como diz a regra da ficha, e por isso não sobrou nenhuma violação. A ficha conta
"diurnos 5 de 5" como violado.

Três leituras da regra da borda, todas com o `avaliacao.py`:

| Leitura | Máx. fins de semana seguidos | Máx. folgas seguidas | Reproduz a ficha? |
|---|---|---|---|
| A — tirar todo bloco que toca a borda do mês ou as férias (a recontagem acima) | **nunca** | nunca | não (máx. fins de semana) |
| B — nos critérios de **máximo**, contar também os blocos de borda (um bloco que já passa do limite dentro do mês é violação certa: o que vem antes ou depois só o alonga); nos de mínimo, tirar | violado (26, em 14 pessoas: 9 diurnos, 5 noturnos) | **violado (1)**: o 5976 (noite_A) tem 5 dias sem trabalho de 21 a 25/11, logo depois das férias (15 a 20/11) e até o fim do mês | não (máx. folgas) |
| C — como B, mas tirando os blocos que tocam as **férias** (a borda do mês conta para máximo; as férias não) | violado | nunca (o bloco do 5976 toca as férias) | **sim**, em todos os critérios |

A leitura C reproduz a ficha inteira, mas é uma leitura construída por mim depois de ver a
diferença — não está escrita na ficha. Decisão da Orientação.

Fins de semana trabalhados (X), por pessoa, fora das férias (f = fim de semana com férias):
diurnos `XXXXX` (9), 6137 `X-fXX`; linhas em branco (6118, 4798, 6089) `-----`; noite_A 4969
`XXXXX`, 4158 `X-XXX`, 5595 `XXXXX`, 5976 `XXXf-`, 5337 `XXXX-`; noite_B 5993 `XXXXX`, 4178 `XXXX-`,
5923 `XX-XX`, 4789 `XXX-X`, 4309 `--XXX`, 3602 `X-XXX`.

**Mesmo turno no fim de semana — outra diferença, sem efeito na classificação.** A ficha diz "sem
ocorrência (ninguém trabalha os dois dias)". Pela semântica do `avaliacao.py` (conferida contra o
avaliador oficial), quem trabalha só um dia do fim de semana **viola** o critério (o turno usado não
cobre todos os dias do fim de semana): 93 violações, em 21 pessoas. A classificação não muda (violado
→ Não considerar; sem ocorrência → padrão, que também é Não considerar), mas a frase da ficha
precisa de ajuste. A tabela acima ainda mostra "sem ocorrência" porque o script trata esse critério
pela leitura da ficha (nenhum fim de semana com os dois dias trabalhados); a contagem pelo
`avaliacao.py` é a da coluna "violação(ões)".

Os outros 10 critérios (todos menos o máx. fins de semana seguidos, o máx. folgas seguidas e o
mesmo turno no fim de semana) ficam do mesmo lado da ficha nas três leituras.
