# Caso A pela prática e sensibilidade (2 ordens) — esperado

Registrado e commitado **antes** de rodar. Decisão: `DECISOES.md`, "2026-10-23 — Caso A:
classificação dos critérios pela escala real e sensibilidade (2 ordens)". Código: v1.4.4 (nada em
`src/` muda). Recontagem da escala real (sem solver, já feita): `recontagem.md` — com a leitura C,
os 13 critérios contáveis do mesmo lado da ficha.

## Rodadas e frase esperada
1. **A11_fixo com 24**, **HIPÓTESE DE SENSIBILIDADE — NÃO REGRA DA FERRAMENTA**, ordem 1:
   "O quadro informado admite escala legal" (como em 21/10).
2. **A36_fixo com 30** (10 enf. + 20 téc., a composição que a busca achou em 21/10), **ordem 1**:
   "O quadro informado admite escala legal" (o 30 já foi mostrado viável em 21/10, e critério nunca
   torna a escala impossível).
3. **A36_fixo com 30, ordem 2**: idem.

Nas três: **avaliador oficial sem violação de restrição dura.**

## Ordem 2 × ordem 1 (A36_fixo, 30)
Só se os níveis envolvidos tiverem **prova**:
- violações de máx. fins de semana seguidos na ordem 2 **≤** ordem 1 (avaliadas nas duas escalas com
  o critério ligado);
- descumprimentos de "Só este turno" na ordem 2 **≥** ordem 1.

Sem prova: relatar o que saiu, **sem afirmar direção**.

## Violações por critério
Não previstas (exploratório). O relatório traz: a frase da tela, a prova por nível, as violações
por critério (contagem da ferramenta e avaliador oficial onde ele pontua; "sem conferência externa"
onde não), os descumprimentos de "Só este turno" por profissional (separando os 4 enfermeiros da
unidade dos 6 acrescidos) e o tempo como limite operacional (máquina e solver).
