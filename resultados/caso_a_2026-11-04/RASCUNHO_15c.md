# RASCUNHO — proposta de seção 15c do `NUMEROS_TCC.md` (NÃO APROVADO)

> Rascunho de 05/11/2026. **Não está no `NUMEROS_TCC.md`** e não vale como número citável até o
> ok do Otávio com a Orientação. Cobre as 7 rodadas.

## 15c. Caso A com a entrada de 04/11 (janela real do Anexo B, férias reais) na v1.4.5 (05/11/2026)

Decisão e esperado commitados antes: `DECISOES.md`, "2026-11-04 — Caso A: entrada revista…" (itens
a–g) e "2026-11-05 — Limitações declaradas"; `resultados/caso_a_2026-11-04/ESPERADO.md`. Resultado:
`RELATORIO.md` e `rodadas/` na mesma pasta. Versão **v1.4.5** (`src/` idêntico à tag `634eeb5`).
Comando: `python docs\diagnostico\caso_a_v145.py --rodar`. Orçamento 60 min por rodada; uma rodada
por configuração.

**Ressalvas obrigatórias:**
- janela 29/10–25/11/2018, sem ajuste de demanda nos feriados de 02 e 15/11; equipe de 23 (o 4309
  como técnico de noite é decisão do Otávio; o 6089 fora); a conta dá o mesmo menor quadro (28) com
  22, 23 ou 24 (`ESPERADO.md` §2);
- 9 + 19 é a composição da regra `equipe` (33%, grau intermediário), **não ótimo de custo**;
- limites dos critérios: padrões da ferramenta, não calibrados;
- tempo só como **limite operacional** (i5-10210U, 11,8 GB, HiGHS 1.15.1 via appsi);
- avaliador oficial rodado com o Java em UTC (o horário de verão de 04/11/2018 quebra a contagem de
  dias do avaliador no fuso de São Paulo; saída idêntica nas instâncias antigas com e sem a opção);
- a penalidade total do avaliador não vai ao texto; vai "sem violação de restrição dura";
- 11 h depois do D12 é **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA**.

| Valor | O que mede | Conferência | Ressalva |
|---|---|---|---|
| caso A, 36 h: **faltam 5; menor quadro viável 28** (com as 33 linhas e sem elas) | 23–27 recusados pela conta prévia (dom 04 + seg 05/11: 17 + 10 = 27 postos contra 22 disponíveis); 28 com escala, etapa 1 provada | avaliador oficial, sem violação de dura; descanso no relógio: menor 36 h depois de D12 e N; conta à mão no `ESPERADO.md` (≥ 28) | a recusa de 23–27 vale para qualquer composição; a escala no 28 é com 9 + 19, que não é ótimo de custo |
| no 28, sem linhas: **15 turnos** de enfermeiro em posto de técnico, provado (= a cota inferior da conta, ≥ 15) | quanto a falta de técnicos nos pares dom + seg obriga a usar enfermeiro em vaga de técnico | cota à mão no `ESPERADO.md` §4; recontado da escala | com as linhas no Essencial, 25 |
| linhas "Só este turno" no Essencial: **mínimo de 2 quebras**, provado (padrão e classificação 1) | o quanto o turno fixo da prática cabe no quadro de 28 | quebras recontadas fora da ferramenta, iguais pessoa a pessoa | quem quebra muda com a classificação |
| classificação 2 × 1 no 28: fins de semana seguidos acima de 3 **0 × 13**; quebras das linhas **15 × 2** | o efeito da classificação; direções previstas no `ESPERADO.md` §3 | as duas com prova em todos os níveis; contagem com peso 1 fora da ferramenta | uma rodada por configuração |
| violação inevitável só no máximo de folgas seguidas: **19** (6137: 12; 5976: 7), atingida exatamente nas classificações 1 e 2 | o que as férias impõem | conta à mão no `ESPERADO.md` §4 | o mínimo de turnos **não** é inevitável: a classificação 2 dá 0 (5976 à custa da linha "Só N") |
| **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA:** com 11 h depois do D12, A (turno fixo, classificação 1) **admite 23, provado**; 14 quebras das linhas no Essencial, 0 enfermeiro em posto de técnico | o quanto a regra das 36 h depois do D12 pesa no quadro (28 × 23) | avaliador oficial, sem violação de dura; descanso no relógio: D12 → 12 h; conta à mão (22 contra 22) | parâmetro de pesquisa, fora da tela |
| caso B, 36 h: **não há escala legal até 101** (igual a 15.1) | 89–101 recusados pela conta (105 contra 89) | conta à mão no `ESPERADO.md` §5 | só a janela mudou; o menor viável não foi determinado |
| **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA:** com 11 h depois do D12, B (rodízio livre) **admite 89, sem prova** (0 e 1 violação, limite inferior 0); os mesmos valores da v1.4.1 (15.1) | o quanto a regra das 36 h depois do D12 pesa no caso B | avaliador oficial (`-Xmx6g`), sem violação de dura, na própria rodada; descanso no relógio: D12 → 12 h | parâmetro de pesquisa, fora da tela; sem prova no orçamento de 60 min |
