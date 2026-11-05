# Rodadas de 05/11 (v1.4.5) — resultado automático

Gerado por `docs/diagnostico/caso_a_v145.py --relatorio`, só lendo os JSON desta pasta. O comentário contra o esperado está no `RELATORIO.md` da pasta de cima. **Tempo: limite operacional, não resultado** (máquina e solver em cada rodada).

## Resumo do mestre

```
05/11 01:47:00 | INÍCIO (primeira) — {'versao': 'v1.4.5-10-g46a7419', 'commit': '46a7419b0e787be3054c5b6fbf5fab6745291b17', 'src_alterado': False, 'diff_src_v145': False}
05/11 01:47:00 | A36_fixo_padrao: começando (memória livre 3215 MB)
05/11 01:53:46 | A36_fixo_padrao: código 0 | 406 s | A36_fixo_padrao: Faltam 5; o menor quadro viável é 28. Escala gerada. | menor viável 28 | avaliador: não | 394 s
05/11 01:53:46 | A36_livre_padrao: começando (memória livre 3831 MB)
05/11 02:53:58 | A36_livre_padrao: código 0 | 3613 s | A36_livre_padrao: Faltam 5; o menor quadro viável é 28. Escala gerada. | menor viável 28 | avaliador: não | 3601 s
05/11 02:53:58 | A36_fixo_class1: começando (memória livre 3707 MB)
05/11 02:54:21 | A36_fixo_class1: código 0 | 23 s | A36_fixo_class1: O quadro informado admite escala legal. Escala gerada. | menor viável 28 | avaliador: não | 11 s
05/11 02:54:22 | A36_fixo_class2: começando (memória livre 3777 MB)
05/11 02:55:10 | A36_fixo_class2: código 0 | 48 s | A36_fixo_class2: O quadro informado admite escala legal. Escala gerada. | menor viável 28 | avaliador: não | 37 s
05/11 02:55:10 | HIPOTESE_SENSIBILIDADE_A11_fixo_class1: começando (memória livre 3511 MB)
05/11 02:55:34 | HIPOTESE_SENSIBILIDADE_A11_fixo_class1: código 0 | 24 s | [HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA] HIPOTESE_SENSIBILIDADE_A11_fixo_class1: O quadro informado admite escala legal. Escala gerada. | menor viável 23 | avaliador: não | 13 s
05/11 02:55:34 | B36_livre: começando (memória livre 3684 MB)
05/11 02:55:36 | B36_livre: código 0 | 3 s | B36_livre: Não há escala legal até 101 profissionais; o menor quadro viável está acima disso. | menor viável None | avaliador: - | 0 s
05/11 02:55:36 | HIPOTESE_SENSIBILIDADE_B11_livre: começando (memória livre 3696 MB)
05/11 03:55:58 | HIPOTESE_SENSIBILIDADE_B11_livre: código 0 | 3621 s | [HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA] HIPOTESE_SENSIBILIDADE_B11_livre: O quadro informado admite escala legal. Escala gerada; pode haver uma melhor. | menor viável 89 | avaliador: não | 3602 s
```

## A36_fixo_padrao

- Versão `v1.4.5-10-g46a7419` (`46a7419`); `src/` alterado: não; diferente da v1.4.5: não.
- Máquina: Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz, 11,8 GB; HiGHS 1.15.1 (highspy, via Pyomo 6.10.1 appsi); avaliador Java -Xmx6g -Duser.timezone=UTC. Memória livre antes: 3108 MB; pico: 322 MB.
- Entrada: quadro 23 (4 + 19); classificação padrão; 33 linhas (Essencial).
- **Frase da tela:** "Faltam 5; o menor quadro viável é 28. Escala gerada."
- Frase vigente: Esta escala tem a carga equilibrada entre colegas.; equilíbrio: Equilíbrio entre colegas: o melhor possível.
- Piso (conta prévia): 28; menor viável: 28.
- Tentativas: 23 piso (conta); 24 piso (conta); 25 piso (conta); 26 piso (conta); 27 piso (conta); 28 viavel (solver, 9 + 19).
- Diagnóstico: Dois dias seguidos — Uma conta feita antes de procurar a escala já mostra que este número de pessoas não permite escala legal. dom 04/11 e seg 05/11: 17 postos na segunda + 10 no domingo em turnos que impedem a segunda (N, D12: depois deles, o descanso exigido não deixa trabalhar no dia seguinte); são 27 pessoas diferentes, e, descontadas férias e licenças, 22 pessoas estão disponíveis em pelo menos um dos dois dias. Pela conta, faltam pelo menos 5 pessoas.
- Etapa 2: ok; provada: True; maior amplitude etapa 1 → final: 0.5454545454545455 → 0.045454545454545414.
- Conferência de descanso no relógio: True; menor descanso (h): {'D12': 36.0, 'N': 36.0}.
- Avaliador oficial, restrição dura: não.
- Tempo total: 394.4 s (limite operacional; orçamento 3600 s).
- Erros depois do solver: nenhum.

| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do bloco: escala | Escala final |
|---|---:|---:|---|---:|---:|---:|
| Essencial | 1124 | 3.2 | sim | 2 | 2 | 2 |
| Importante | 980 | 1.6 | sim | 25 | 25 | 25 |

- Essencial: 2 violações — a melhor possível.
- Importante: 25 violações — a melhor possível.

| Critério | Importância | Violações (ferramenta) | Avaliador oficial, peso 1 |
|---|---|---:|---:|
| Pedido de folga no dia | Essencial | 0 | 0 |
| Pedidos e regras dos profissionais | Essencial | 2 | 2 |
| Enfermeiro em posto de técnico | Importante | 25 | sem conferência externa |

Conferência com peso 1 (critérios da classificação 2 ligados): Pedido de folga no dia 0; Máximo de fins de semana seguidos trabalhados 10; Pedidos e regras dos profissionais 2; Enfermeiro em posto de técnico 25; Máximo de folgas seguidas 29; Mínimo de turnos no período 11. Avaliador oficial por família: {'max_consecutive_working_weekends': 10, 'unwanted_patterns': 186, 'shift_off_requests': 2, 'max_consecutive_free_days': 29, 'min_num_assignments': 11}.

Quebras do turno fixo por profissional — pela ferramenta (nível, quantas): Téc 5595 (Essencial, 1); Téc 3602 (Essencial, 1). Medidas na escala, contra as 33 linhas da entrada (também na rodada sem linhas): Téc 3602 1; Téc 5595 1 (total 2).

Enfermeiro em posto de técnico: 4 da unidade **6**, acrescidos **19**. Por enfermeiro: Enf 4798 (unidade) 15 turnos, 5 em posto de técnico; Enf 4969 (unidade) 7 turnos, 0 em posto de técnico; Enf 5993 (unidade) 7 turnos, 0 em posto de técnico; Enf 6118 (unidade) 15 turnos, 1 em posto de técnico; Enf 5 (acrescido) 10 turnos, 4 em posto de técnico; Enf 6 (acrescido) 10 turnos, 3 em posto de técnico; Enf 7 (acrescido) 11 turnos, 3 em posto de técnico; Enf 8 (acrescido) 9 turnos, 3 em posto de técnico; Enf 9 (acrescido) 9 turnos, 6 em posto de técnico.

Por pessoa, avaliador oficial com peso 1 (férias: 6137 em 31/10–15/11, 5976 em 15/11–25/11):
- Máx. folgas seguidas (4): total 29; Enf 4969 3, Enf 5993 3, Enf 6 2, Enf 7 2, Téc 5976 7 (férias 15/11–25/11), Téc 6137 12 (férias 31/10–15/11). Inevitável pela conta do ESPERADO §4: 19 (Téc 6137 ≥ 12, Téc 5976 ≥ 7); evitável: 10.
- Mín. turnos (10): total 11; Enf 4969 3, Enf 5993 3, Enf 8 1, Enf 9 1, Téc 5976 2 (férias 15/11–25/11), Téc 6137 1 (férias 31/10–15/11). Inevitável pela conta do ESPERADO §4: 2 (Téc 5976 ≥ 2; o do 5976 só com a linha Só N cumprida); evitável: 9.

## A36_livre_padrao

- Versão `v1.4.5-10-g46a7419` (`46a7419`); `src/` alterado: não; diferente da v1.4.5: não.
- Máquina: Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz, 11,8 GB; HiGHS 1.15.1 (highspy, via Pyomo 6.10.1 appsi); avaliador Java -Xmx6g -Duser.timezone=UTC. Memória livre antes: 3723 MB; pico: 698 MB.
- Entrada: quadro 23 (4 + 19); classificação padrão; 0 linhas.
- **Frase da tela:** "Faltam 5; o menor quadro viável é 28. Escala gerada."
- Frase vigente: Esta escala tem a carga equilibrada entre colegas.; equilíbrio: Equilíbrio entre colegas: pode haver uma escala mais equilibrada.
- Piso (conta prévia): 28; menor viável: 28.
- Tentativas: 23 piso (conta); 24 piso (conta); 25 piso (conta); 26 piso (conta); 27 piso (conta); 28 viavel (solver, 9 + 19).
- Diagnóstico: Dois dias seguidos — Uma conta feita antes de procurar a escala já mostra que este número de pessoas não permite escala legal. dom 04/11 e seg 05/11: 17 postos na segunda + 10 no domingo em turnos que impedem a segunda (N, D12: depois deles, o descanso exigido não deixa trabalhar no dia seguinte); são 27 pessoas diferentes, e, descontadas férias e licenças, 22 pessoas estão disponíveis em pelo menos um dos dois dias. Pela conta, faltam pelo menos 5 pessoas.
- Etapa 2: ok; provada: False; maior amplitude etapa 1 → final: 0.4772727272727272 → 0.03409090909090917.
- Conferência de descanso no relógio: True; menor descanso (h): {'D12': 36.0, 'N': 36.0}.
- Avaliador oficial, restrição dura: não.
- Tempo total: 3600.7 s (limite operacional; orçamento 3600 s).
- Erros depois do solver: nenhum.

| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do bloco: escala | Escala final |
|---|---:|---:|---|---:|---:|---:|
| Essencial + Importante | 1799 | 23.5 | sim | 15 | 15 | 15 |

- Essencial e Importante: 0 e 15 violações — a melhor possível.

| Critério | Importância | Violações (ferramenta) | Avaliador oficial, peso 1 |
|---|---|---:|---:|
| Pedido de folga no dia | Essencial | 0 | 0 |
| Enfermeiro em posto de técnico | Importante | 15 | sem conferência externa |

Conferência com peso 1 (critérios da classificação 2 ligados): Pedido de folga no dia 0; Máximo de fins de semana seguidos trabalhados 17; Enfermeiro em posto de técnico 15; Máximo de folgas seguidas 29; Mínimo de turnos no período 11. Avaliador oficial por família: {'max_consecutive_working_weekends': 17, 'unwanted_patterns': 204, 'max_consecutive_free_days': 29, 'min_num_assignments': 11}.

Quebras do turno fixo por profissional — pela ferramenta (nível, quantas): nenhuma. Medidas na escala, contra as 33 linhas da entrada (também na rodada sem linhas): Enf 4798 6; Enf 4969 8; Enf 5993 6; Enf 6118 7; Téc 3602 7; Téc 4158 1; Téc 4178 11; Téc 4309 15; Téc 4789 15; Téc 5337 12; Téc 5595 11; Téc 5697 14; Téc 5762 9; Téc 5923 23; Téc 5976 10; Téc 6003 11; Téc 6017 12; Téc 6052 12; Téc 6137 6; Téc 6187 14; Téc 6209 8; Téc 6262 12; Téc 6271 9 (total 239).

Enfermeiro em posto de técnico: 4 da unidade **5**, acrescidos **10**. Por enfermeiro: Enf 4798 (unidade) 8 turnos, 1 em posto de técnico; Enf 4969 (unidade) 10 turnos, 2 em posto de técnico; Enf 5993 (unidade) 9 turnos, 1 em posto de técnico; Enf 6118 (unidade) 10 turnos, 1 em posto de técnico; Enf 5 (acrescido) 8 turnos, 2 em posto de técnico; Enf 6 (acrescido) 10 turnos, 3 em posto de técnico; Enf 7 (acrescido) 9 turnos, 1 em posto de técnico; Enf 8 (acrescido) 9 turnos, 1 em posto de técnico; Enf 9 (acrescido) 10 turnos, 3 em posto de técnico.

Por pessoa, avaliador oficial com peso 1 (férias: 6137 em 31/10–15/11, 5976 em 15/11–25/11):
- Máx. folgas seguidas (4): total 29; Enf 4798 2, Enf 5 2, Enf 5993 1, Enf 6118 1, Enf 8 2, Enf 9 1, Téc 5976 7 (férias 15/11–25/11), Téc 6137 13 (férias 31/10–15/11). Inevitável pela conta do ESPERADO §4: 19 (Téc 6137 ≥ 12, Téc 5976 ≥ 7); evitável: 10.
- Mín. turnos (10): total 11; Enf 4798 2, Enf 5 2, Enf 5993 1, Enf 7 1, Enf 8 1, Téc 6137 4 (férias 31/10–15/11). Inevitável pela conta do ESPERADO §4: 0 (Téc 5976 ≥ 2; o do 5976 só com a linha Só N cumprida); evitável: 11.

## A36_fixo_class1

- Versão `v1.4.5-10-g46a7419` (`46a7419`); `src/` alterado: não; diferente da v1.4.5: não.
- Máquina: Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz, 11,8 GB; HiGHS 1.15.1 (highspy, via Pyomo 6.10.1 appsi); avaliador Java -Xmx6g -Duser.timezone=UTC. Memória livre antes: 3732 MB; pico: 180 MB.
- Entrada: quadro 28 (9 + 19); classificação 1; 33 linhas (Essencial); quadro e composição da rodada 1: 28 (9 + 19), lidos de A36_fixo_padrao.
- **Frase da tela:** "O quadro informado admite escala legal. Escala gerada."
- Frase vigente: Esta escala tem a carga equilibrada entre colegas.; equilíbrio: Equilíbrio entre colegas: o melhor possível.
- Piso (conta prévia): 18; menor viável: 28.
- Tentativas: 28 viavel (solver, 9 + 19).
- Diagnóstico: None — —
- Etapa 2: ok; provada: True; maior amplitude etapa 1 → final: 0.4090909090909091 → 0.30681818181818177.
- Conferência de descanso no relógio: True; menor descanso (h): {'D12': 36.0, 'N': 36.0}.
- Avaliador oficial, restrição dura: não.
- Tempo total: 10.8 s (limite operacional; orçamento 3600 s).
- Erros depois do solver: nenhum.

| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do bloco: escala | Escala final |
|---|---:|---:|---|---:|---:|---:|
| Essencial | 1124 | 3.4 | sim | 2 | 2 | 2 |
| Importante | 980 | 2.5 | sim | 45 | 45 | 45 |

- Essencial: 2 violações — a melhor possível.
- Importante: 45 violações — a melhor possível.

| Critério | Importância | Violações (ferramenta) | Avaliador oficial, peso 1 |
|---|---|---:|---:|
| Pedido de folga no dia | Essencial | 0 | 0 |
| Pedidos e regras dos profissionais | Essencial | 2 | 2 |
| Enfermeiro em posto de técnico | Importante | 25 | sem conferência externa |
| Máximo de folgas seguidas | Importante | 19 | 19 |
| Mínimo de turnos no período | Importante | 1 | 1 |

Conferência com peso 1 (critérios da classificação 2 ligados): Pedido de folga no dia 0; Máximo de fins de semana seguidos trabalhados 13; Pedidos e regras dos profissionais 2; Enfermeiro em posto de técnico 25; Máximo de folgas seguidas 19; Mínimo de turnos no período 1. Avaliador oficial por família: {'max_consecutive_working_weekends': 13, 'unwanted_patterns': 138, 'shift_off_requests': 2, 'max_consecutive_free_days': 19, 'min_num_assignments': 1}.

Quebras do turno fixo por profissional — pela ferramenta (nível, quantas): Téc 5976 (Essencial, 1); Téc 3602 (Essencial, 1). Medidas na escala, contra as 33 linhas da entrada (também na rodada sem linhas): Téc 3602 1; Téc 5976 1 (total 2).

Enfermeiro em posto de técnico: 4 da unidade **1**, acrescidos **24**. Por enfermeiro: Enf 4798 (unidade) 11 turnos, 1 em posto de técnico; Enf 4969 (unidade) 10 turnos, 0 em posto de técnico; Enf 5993 (unidade) 10 turnos, 0 em posto de técnico; Enf 6118 (unidade) 11 turnos, 0 em posto de técnico; Enf 5 (acrescido) 10 turnos, 8 em posto de técnico; Enf 6 (acrescido) 10 turnos, 4 em posto de técnico; Enf 7 (acrescido) 10 turnos, 4 em posto de técnico; Enf 8 (acrescido) 11 turnos, 5 em posto de técnico; Enf 9 (acrescido) 10 turnos, 3 em posto de técnico.

Por pessoa, avaliador oficial com peso 1 (férias: 6137 em 31/10–15/11, 5976 em 15/11–25/11):
- Máx. folgas seguidas (4): total 19; Téc 5976 7 (férias 15/11–25/11), Téc 6137 12 (férias 31/10–15/11). Inevitável pela conta do ESPERADO §4: 19 (Téc 6137 ≥ 12, Téc 5976 ≥ 7); evitável: 0.
- Mín. turnos (10): total 1; Téc 5976 1 (férias 15/11–25/11). Inevitável pela conta do ESPERADO §4: 1 (Téc 5976 ≥ 2; o do 5976 só com a linha Só N cumprida); evitável: 0.

## A36_fixo_class2

- Versão `v1.4.5-10-g46a7419` (`46a7419`); `src/` alterado: não; diferente da v1.4.5: não.
- Máquina: Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz, 11,8 GB; HiGHS 1.15.1 (highspy, via Pyomo 6.10.1 appsi); avaliador Java -Xmx6g -Duser.timezone=UTC. Memória livre antes: 3723 MB; pico: 219 MB.
- Entrada: quadro 28 (9 + 19); classificação 2; 33 linhas (Desejável); quadro e composição da rodada 1: 28 (9 + 19), lidos de A36_fixo_padrao.
- **Frase da tela:** "O quadro informado admite escala legal. Escala gerada."
- Frase vigente: Esta escala tem a carga equilibrada entre colegas.; equilíbrio: Equilíbrio entre colegas: o melhor possível.
- Piso (conta prévia): 18; menor viável: 28.
- Tentativas: 28 viavel (solver, 9 + 19).
- Diagnóstico: None — —
- Etapa 2: ok; provada: True; maior amplitude etapa 1 → final: 0.27272727272727265 → 0.27272727272727265.
- Conferência de descanso no relógio: True; menor descanso (h): {'D12': 36.0, 'N': 36.0}.
- Avaliador oficial, restrição dura: não.
- Tempo total: 36.8 s (limite operacional; orçamento 3600 s).
- Erros depois do solver: nenhum.

| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do bloco: escala | Escala final |
|---|---:|---:|---|---:|---:|---:|
| Essencial | 899 | 5.6 | sim | 0 | 0 | 0 |
| Importante | 718 | 15.6 | sim | 41 | 41 | 41 |
| Desejável | 596 | 6.1 | sim | 15 | 15 | 15 |

- Essencial: 0 violações — a melhor possível.
- Importante: 41 violações — a melhor possível.
- Desejável: 15 violações — a melhor possível.

| Critério | Importância | Violações (ferramenta) | Avaliador oficial, peso 1 |
|---|---|---:|---:|
| Pedido de folga no dia | Essencial | 0 | 0 |
| Máximo de fins de semana seguidos trabalhados | Essencial | 0 | 0 |
| Enfermeiro em posto de técnico | Importante | 22 | sem conferência externa |
| Máximo de folgas seguidas | Importante | 19 | 19 |
| Mínimo de turnos no período | Importante | 0 | 0 |
| Pedidos e regras dos profissionais | Desejável | 15 | 15 |

Conferência com peso 1 (critérios da classificação 2 ligados): Pedido de folga no dia 0; Máximo de fins de semana seguidos trabalhados 0; Enfermeiro em posto de técnico 22; Máximo de folgas seguidas 19; Mínimo de turnos no período 0; Pedidos e regras dos profissionais 15. Avaliador oficial por família: {'unwanted_patterns': 192, 'shift_off_requests': 15, 'max_consecutive_free_days': 19}.

Quebras do turno fixo por profissional — pela ferramenta (nível, quantas): Enf 6118 (Desejável, 2); Enf 4798 (Desejável, 2); Téc 4158 (Desejável, 1); Téc 5976 (Desejável, 4); Téc 4178 (Desejável, 1); Téc 5923 (Desejável, 2); Téc 4789 (Desejável, 1); Téc 3602 (Desejável, 1); Téc 4309 (Desejável, 1). Medidas na escala, contra as 33 linhas da entrada (também na rodada sem linhas): Enf 4798 2; Enf 6118 2; Téc 3602 1; Téc 4158 1; Téc 4178 1; Téc 4309 1; Téc 4789 1; Téc 5923 2; Téc 5976 4 (total 15).

Enfermeiro em posto de técnico: 4 da unidade **8**, acrescidos **14**. Por enfermeiro: Enf 4798 (unidade) 10 turnos, 4 em posto de técnico; Enf 4969 (unidade) 10 turnos, 0 em posto de técnico; Enf 5993 (unidade) 10 turnos, 2 em posto de técnico; Enf 6118 (unidade) 10 turnos, 2 em posto de técnico; Enf 5 (acrescido) 10 turnos, 2 em posto de técnico; Enf 6 (acrescido) 10 turnos, 4 em posto de técnico; Enf 7 (acrescido) 10 turnos, 2 em posto de técnico; Enf 8 (acrescido) 10 turnos, 3 em posto de técnico; Enf 9 (acrescido) 10 turnos, 3 em posto de técnico.

Por pessoa, avaliador oficial com peso 1 (férias: 6137 em 31/10–15/11, 5976 em 15/11–25/11):
- Máx. folgas seguidas (4): total 19; Téc 5976 7 (férias 15/11–25/11), Téc 6137 12 (férias 31/10–15/11). Inevitável pela conta do ESPERADO §4: 19 (Téc 6137 ≥ 12, Téc 5976 ≥ 7); evitável: 0.
- Mín. turnos (10): total 0; nenhuma. Inevitável pela conta do ESPERADO §4: 0 (Téc 5976 ≥ 2; o do 5976 só com a linha Só N cumprida); evitável: 0.

## HIPOTESE_SENSIBILIDADE_A11_fixo_class1 — HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA

- Versão `v1.4.5-10-g46a7419` (`46a7419`); `src/` alterado: não; diferente da v1.4.5: não.
- Máquina: Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz, 11,8 GB; HiGHS 1.15.1 (highspy, via Pyomo 6.10.1 appsi); avaliador Java -Xmx6g -Duser.timezone=UTC. Memória livre antes: 3487 MB; pico: 153 MB.
- Entrada: quadro 23 (4 + 19); classificação 1; 33 linhas (Essencial).
- **Frase da tela:** "O quadro informado admite escala legal. Escala gerada."
- Frase vigente: Esta escala tem a carga equilibrada entre colegas.; equilíbrio: Equilíbrio entre colegas: o melhor possível.
- Piso (conta prévia): 18; menor viável: 23.
- Tentativas: 23 viavel (solver, 4 + 19).
- Diagnóstico: None — —
- Etapa 2: ok; provada: True; maior amplitude etapa 1 → final: 0.2727272727272728 → 0.2727272727272728.
- Conferência de descanso no relógio: True; menor descanso (h): {'D12': 12.0, 'N': 36.0}.
- Avaliador oficial, restrição dura: não.
- Tempo total: 13.4 s (limite operacional; orçamento 3600 s).
- Erros depois do solver: nenhum.

| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do bloco: escala | Escala final |
|---|---:|---:|---|---:|---:|---:|
| Essencial | 1124 | 4.2 | sim | 14 | 14 | 14 |
| Importante | 980 | 4.0 | sim | 19 | 19 | 19 |

- Essencial: 14 violações — a melhor possível.
- Importante: 19 violações — a melhor possível.

| Critério | Importância | Violações (ferramenta) | Avaliador oficial, peso 1 |
|---|---|---:|---:|
| Pedido de folga no dia | Essencial | 0 | 0 |
| Pedidos e regras dos profissionais | Essencial | 14 | 14 |
| Enfermeiro em posto de técnico | Importante | 0 | sem conferência externa |
| Máximo de folgas seguidas | Importante | 19 | 19 |
| Mínimo de turnos no período | Importante | 0 | 0 |

Conferência com peso 1 (critérios da classificação 1 ligados): Pedido de folga no dia 0; Pedidos e regras dos profissionais 14; Enfermeiro em posto de técnico 0; Máximo de folgas seguidas 19; Mínimo de turnos no período 0. Avaliador oficial por família: {'max_consecutive_free_days': 19, 'shift_off_requests': 14, 'unwanted_patterns': 12}.

Quebras do turno fixo por profissional — pela ferramenta (nível, quantas): Téc 5976 (Essencial, 4); Téc 4178 (Essencial, 10). Medidas na escala, contra as 33 linhas da entrada (também na rodada sem linhas): Téc 4178 10; Téc 5976 4 (total 14).

Enfermeiro em posto de técnico: 4 da unidade **0**, acrescidos **0**. Por enfermeiro: Enf 4798 (unidade) 20 turnos, 0 em posto de técnico; Enf 4969 (unidade) 14 turnos, 0 em posto de técnico; Enf 5993 (unidade) 14 turnos, 0 em posto de técnico; Enf 6118 (unidade) 20 turnos, 0 em posto de técnico.

Por pessoa, avaliador oficial com peso 1 (férias: 6137 em 31/10–15/11, 5976 em 15/11–25/11):
- Máx. folgas seguidas (4): total 19; Téc 5976 7 (férias 15/11–25/11), Téc 6137 12 (férias 31/10–15/11). Inevitável pela conta do ESPERADO §4: 19 (Téc 6137 ≥ 12, Téc 5976 ≥ 7); evitável: 0.
- Mín. turnos (10): total 0; nenhuma. Inevitável pela conta do ESPERADO §4: 0 (Téc 5976 ≥ 2; o do 5976 só com a linha Só N cumprida); evitável: 0.

## B36_livre

- Versão `v1.4.5-10-g46a7419` (`46a7419`); `src/` alterado: não; diferente da v1.4.5: não.
- Máquina: Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz, 11,8 GB; HiGHS 1.15.1 (highspy, via Pyomo 6.10.1 appsi); avaliador Java -Xmx6g -Duser.timezone=UTC. Memória livre antes: 3668 MB; pico: 47 MB.
- Entrada: quadro 89 (15 + 74); classificação padrão; 0 linhas.
- **Frase da tela:** "Não há escala legal até 101 profissionais; o menor quadro viável está acima disso."
- Frase vigente: None; equilíbrio: None
- Piso (conta prévia): 105; menor viável: None.
- Tentativas: 89 piso (conta); 90 piso (conta); 91 piso (conta); 92 piso (conta); 93 piso (conta); 94 piso (conta); 95 piso (conta); 96 piso (conta); 97 piso (conta); 98 piso (conta); 99 piso (conta); 100 piso (conta); 101 piso (conta).
- Diagnóstico: Dois dias seguidos — Uma conta feita antes de procurar a escala já mostra que este número de pessoas não permite escala legal. dom 04/11 e seg 05/11: 65 postos na segunda + 40 no domingo em turnos que impedem a segunda (N, D12: depois deles, o descanso exigido não deixa trabalhar no dia seguinte); são 105 pessoas diferentes, e, descontadas férias e licenças, 89 pessoas estão disponíveis em pelo menos um dos dois dias. Pela conta, faltam pelo menos 16 pessoas.
- Etapa 2: None; provada: None; maior amplitude etapa 1 → final: None → None.
- Conferência de descanso no relógio: None; menor descanso (h): None.
- Avaliador oficial, restrição dura: — (sem escala).
- Tempo total: 0.0 s (limite operacional; orçamento 3600 s).
- Erros depois do solver: nenhum.

## HIPOTESE_SENSIBILIDADE_B11_livre — HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA

- Versão `v1.4.5-10-g46a7419` (`46a7419`); `src/` alterado: não; diferente da v1.4.5: não.
- Máquina: Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz, 11,8 GB; HiGHS 1.15.1 (highspy, via Pyomo 6.10.1 appsi); avaliador Java -Xmx6g -Duser.timezone=UTC. Memória livre antes: 3676 MB; pico: 739 MB.
- Entrada: quadro 89 (15 + 74); classificação padrão; 0 linhas.
- **Frase da tela:** "O quadro informado admite escala legal. Escala gerada; pode haver uma melhor."
- Frase vigente: Esta escala tem a carga equilibrada entre colegas, sem piorar o resultado da escala encontrada (que pode não ser a melhor possível).; equilíbrio: Equilíbrio entre colegas: pode haver uma escala mais equilibrada.
- Piso (conta prévia): 68; menor viável: 89.
- Tentativas: 89 viavel (solver, 15 + 74).
- Diagnóstico: None — —
- Etapa 2: ok; provada: False; maior amplitude etapa 1 → final: 0.375 → 0.06818181818181823.
- Conferência de descanso no relógio: True; menor descanso (h): {'D12': 12.0, 'N': 36.0}.
- Avaliador oficial, restrição dura: não.
- Tempo total: 3602.5 s (limite operacional; orçamento 3600 s).
- Erros depois do solver: nenhum.

| Nível (bloco) | Limite (s) | Tempo (s) | Prova | Fim do bloco: modelo | Fim do bloco: escala | Escala final |
|---|---:|---:|---|---:|---:|---:|
| Essencial + Importante | 1799 | 1800.8 | não | 1 | 1 | 1 |

- Essencial e Importante: 0 e 1 violação. Não deu tempo de saber quanto dá para melhorar.

| Critério | Importância | Violações (ferramenta) | Avaliador oficial, peso 1 |
|---|---|---:|---:|
| Pedido de folga no dia | Essencial | 0 | sem conferência externa |
| Enfermeiro em posto de técnico | Importante | 1 | sem conferência externa |

Quebras do turno fixo por profissional — pela ferramenta (nível, quantas): nenhuma. Medidas na escala, contra as 33 linhas da entrada (também na rodada sem linhas): nenhuma (total 0).

Enfermeiro em posto de técnico: 4 da unidade **0**, acrescidos **1**. Por enfermeiro: Enf 1 (acrescido) 13 turnos, 0 em posto de técnico; Enf 10 (acrescido) 17 turnos, 1 em posto de técnico; Enf 11 (acrescido) 16 turnos, 0 em posto de técnico; Enf 12 (acrescido) 14 turnos, 0 em posto de técnico; Enf 13 (acrescido) 16 turnos, 0 em posto de técnico; Enf 14 (acrescido) 18 turnos, 0 em posto de técnico; Enf 15 (acrescido) 17 turnos, 0 em posto de técnico; Enf 2 (acrescido) 18 turnos, 0 em posto de técnico; Enf 3 (acrescido) 11 turnos, 0 em posto de técnico; Enf 4 (acrescido) 15 turnos, 0 em posto de técnico; Enf 5 (acrescido) 16 turnos, 0 em posto de técnico; Enf 6 (acrescido) 17 turnos, 0 em posto de técnico; Enf 7 (acrescido) 14 turnos, 0 em posto de técnico; Enf 8 (acrescido) 15 turnos, 0 em posto de técnico; Enf 9 (acrescido) 16 turnos, 0 em posto de técnico.

