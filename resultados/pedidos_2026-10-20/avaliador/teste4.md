# Teste 4 — pedidos da tabela no avaliador oficial (20/10/2026)

Caso 2b + "Folga, d2" de A + "Folga, d4, turno T" de C; pedidos gerados: 2 DayOff, 80 ShiftOff (peso 1). XSD da instância: válido. Escala da ferramenta: fundido, provado True. Semente 20261020; 9 perturbadas, 3 trocas cada.

Colunas: penalidade dos pedidos (DayOff + ShiftOff) somada nos profissionais. A coluna do modelo vem das expressões do próprio modelo (`m.pena_familia`, x fixado) — não é conferência independente do modelo. **Premissa compartilhada pelas quatro colunas:** a lista de pedidos gerada pela tradução da tabela; o teste não confere a tradução (conferida nos testes 2 e 3, à mão).

| Escala | Avaliador (pedidos) | Modelo (pedidos) | avaliacao.py (pedidos) | Ferramenta (descumpridos) | Profissionais com diferença |
|---|---:|---:|---:|---:|---:|
| ferramenta | 4 | 4 | 4 | 4 | 0 |
| perturbada1 | 6 | 6 | 6 | 6 | 0 |
| perturbada2 | 7 | 7 | 7 | 7 | 0 |
| perturbada3 | 9 | 9 | 9 | 9 | 0 |
| perturbada4 | 6 | 6 | 6 | 6 | 0 |
| perturbada5 | 9 | 9 | 9 | 9 | 0 |
| perturbada6 | 6 | 6 | 6 | 6 | 0 |
| perturbada7 | 4 | 4 | 4 | 4 | 0 |
| perturbada8 | 6 | 6 | 6 | 6 | 0 |
| perturbada9 | 7 | 7 | 7 | 7 | 0 |

TUDO OK
