# Relatório da sessão de 02–03/10/2026

## Para o Otávio

- **O bloco parou no item 1**, por falha de teste. Pela regra combinada, a P1 **não foi lançada**.
- Há duas falhas. Nas duas, o defeito está no **esperado** do teste e o código se mostrou correto. O motivo de cada uma está explicado abaixo, com a conta. Nenhum esperado foi alterado; a correção depende de você.
- A falha do 9c revelou uma questão de formulação, registrada como **P6** no PROPOSTAS.md. Ela pede decisão antes de relançar a P1.
- O sistema interrompeu a suíte de testes da tela por falta de memória, e eu não a relancei. Alguns testes ficaram sem rodar (lista abaixo).
- Para conferir em casa: `git pull` traz tudo deste relatório. Depois, com a .venv ativa, rode `python src\testes_ferramenta.py`, que é a suíte completa da tela e leva cerca de 15 min.

---

## 1. O que foi feito

### Monitor pendente

O monitor que restava era o `tail` do log da curva P1 antiga. Foi encerrado.

### Item 1 — carga por contrato (implementado; testes com falha)

**1b, como estava o teto antes.** O teto já valia sobre o horizonte, não por semana. Era uma restrição por profissional: soma das horas nos 28 dias ≤ 168 h (42 × 4), igual para todos. Não descontava férias.

**O que mudou:**

| Item | Implementação |
|---|---|
| a) | Carga semanal por profissional (30/36/40/44 h; padrão 44 h), numa tabela na tela de equipe. `Instancia.carga_semanal_h` |
| b), d) | Teto = carga × dias disponíveis ÷ 7, sobre o horizonte (`Instancia.horas_devidas`). Uma conta só, usada pelo teto do modelo, pela conferência e pelo denominador da fração |
| c) | A etapa 2 minimiza (maior − menor) da fração cumprida. Quem não tem dia disponível fica fora |
| e) | A CHS do QP é a média das cargas da equipe, e a tela mostra o valor usado |
| f) | Caminho por pacientes e Experimento A intactos, com 42 h |

**Como f) foi conferido.** Os **544 XML** saem idênticos byte a byte antes e depois. A conferência é o script novo `docs/conferencia_xml_experimentos.py`, que substitui a conferência avulsa dos 361 XML, que não estava no repositório. Pus a comparação à prova com um byte alterado numa cópia, e ela acusou a diferença.

**Consequências na ferramenta:**
- Quem a varredura do menor quadro acrescenta entra com 44 h.
- O piso e o diagnóstico da trava comparam a demanda com a soma dos tetos individuais.
- O `MaxNumAssignments` do XML passa a usar a maior carga: no modelo de 6 h, vai de 28 para 29.

### Item 2 — DECISOES.md

Entrada nova, **"2026-10-02 — Carga por contrato"**, vigente. Contém os itens a) a f), o argumento (as 42 h do 12×36 vêm da alternância; contratos heterogêneos aparecem em 30% dos estudos), os testes e as falhas.

### Item 3 — PROPOSTAS.md

- **P4** (amplitude com férias): marcada como **resolvida** pelo item 1c. Conferido no 9c: quem tem férias fica dentro da faixa dos demais.
- **P5** (teste de uso qualitativo com 1 ou 2 profissionais): **não executada, por decisão**; entra no texto como limitação declarada.
- **P6** (nova, achada no 9c): a amplitude da fração fica presa à separação entre enfermeiros e técnicos. Aguarda decisão.

### Item 4 — REENQUADRAMENTO_TCC1.md

**Não existe no repositório.** Nada foi anotado.

### Item 5 — P1

**Não lançada**, porque o bloco parou no item 1. Mesmo sem as falhas, a P6 pede o critério final da etapa 2 antes da P1.

---

## 2. O que parou e por quê

### Falha 1: teste 9c, metade (amplitude final ≤ 10 pp)

**O caso:** modelo de 8 h, 6 enfermeiros + 12 técnicos, todos com 44 h; Téc 1 de férias nos 14 primeiros dias. O esperado foi registrado antes de rodar.

**O que saiu:**
- Amplitude final de **27,3%**, provada ótima.
- A outra metade do teste acertou: Téc 1 ficou com 72 h de 88 h devidas, **81,8%**, dentro da faixa dos demais (63,6%–90,9%).

**Por que o esperado está errado** (diagnóstico rodado só para leitura):
1. A penalidade da etapa 1 é zero, com 0 turno de enfermeiro em posto de técnico. Fixado esse ótimo, nenhum enfermeiro pode ir para posto de técnico.
2. Os 6 enfermeiros cobrem exatamente as 672 h de posto de enfermeiro: 112 h cada, **63,6%**.
3. Os técnicos cobrem **1.792 h**; o esperado usou 1.680, uma conta errada minha. Com 11 técnicos em ≤ 152 h, somariam no máximo 11 × 152 + 88 = 1.760 h < 1.792. Logo alguém chega a 160 h, **90,9%**.
4. Amplitude mínima = 90,9 − 63,6 = **27,3 pp**, exatamente o valor provado pelo solver.

O esperado tratou a equipe como um grupo só, com média de 80%. **O código está certo; o esperado, não.** O que isso revela vai além do teste: com enfermeiros dedicados ao próprio posto, a amplitude mede a diferença entre categorias, não a justiça entre colegas. É a **P6**, com três saídas; a minha recomendação é equilibrar dentro de cada categoria.

### Falha 2: caso 5 da tela (≥ 35 turnos de enfermeiro em posto de técnico)

**O que saiu:** **30** turnos.

**Por que o esperado está desatualizado:**
- O esperado foi calculado com 42 h: 5 técnicos × 168 h = 840 h para 1.120 h de posto de técnico, logo 35 turnos.
- Com o padrão de 44 h, os técnicos dão 5 × 176 = 880 h. Faltam 240 h = **30 turnos**, e o solver deu exatamente 30.
- O 7.1 passa, porque sua condição é ≤ 35, mas o texto dele ainda diz "mínimo aritmético 35".
- **Os dois precisam do esperado refeito com 44 h.** É consequência direta da decisão de 44 h como padrão.

### Interrupção por memória

O sistema interrompeu a suíte da tela durante o teste 7.2, por falta de memória na máquina. A instrução que recebi foi não relançar sem pedido seu.

**Não rodaram depois da carga por contrato:**
- **7.2** (caso de 40 com 20 pedidos);
- **7.3** (os cinco diagnósticos);
- **8a–8d** (os três desfechos de tempo).

---

## 3. Números

| Conferência | Resultado |
|---|---|
| `regressao.py --todos` | **OK.** sprint01 56, sprint02 58, long01 197, long02 219 = Tabela 6 |
| `testes_entrada.py` (completo) | **OK** |
| XML do caminho dos experimentos (544) | **idênticos** byte a byte |
| Tela 1–4 | OK |
| Tela 5 | **FALHA:** 30 contra ≥ 35 (esperado de 42 h) |
| Tela 7.1 | OK (texto desatualizado) |
| Tela 7.2, 7.3, 8a–8d | **não rodaram** (memória) |
| 9a, equipe mista 30/44 h | OK: maior carga 112 h entre os de 30 h (teto 120 h) e 168 h entre os de 44 h (teto 176 h); rígidas OK |
| 9b, 12×36 com 44 h | OK: no máximo 14 plantões. Ressalva registrada antes de rodar: o teto de 176 h também para em 14, então o teste não separa alternância de teto |
| 9c, férias | Metade OK: Téc 1 com 81,8%, dentro de 63,6%–90,9%. Metade **FALHA:** amplitude 27,3% contra ≤ 10 pp (esperado errado) |
| 9d, equilíbrio reduz amplitude | OK: 45,5% → 27,3%, provado; etapa 2 em 57,6 s |

**Máquina:** Intel Core i5-10210U (4 núcleos, 8 threads), 12 GB, Windows 11, Python 3.11.9, HiGHS 1.15.1 via appsi. O tempo de 57,6 s é limite operacional, não resultado.

---

## 4. Commits

| Commit | Conteúdo | Enviado |
|---|---|---|
| `cbac3b3` | Carga por contrato: código, tabela na tela, conferência dos 544 XML | sim, neste push |
| `a389478` | Registros dos itens 2–3, testes 9a–9d, anotação das falhas | sim, neste push |
| este | Este relatório (`git add -f`, porque `resultados/` é ignorado pelo git) | sim |

---

## LEVAR PARA O PROJETO DE REDACAO

- **`DECISOES.md`**: entrada nova "2026-10-02 — Carga por contrato" (vigente), com os itens a) a f), o argumento, os testes, as duas falhas de esperado e o estado da suíte.
- **`PROPOSTAS.md`**:
  - P4 marcada como resolvida pelo item 1c.
  - P5 nova: teste de uso qualitativo, não executado, limitação declarada.
  - P6 nova: a amplitude da fração fica presa à separação enfermeiro/técnico. **Decisão necessária antes da P1.**
- **`ESTADO_ATUAL.md`**: data de 03/10. A pendência "carga mínima" foi respondida pela carga por contrato, e a P6 fica em aberto antes de relançar a P1.
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
