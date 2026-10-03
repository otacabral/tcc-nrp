# Relatório da sessão de 03/10/2026 (tarde)

## Para o Otávio

- A P6 foi implementada como você decidiu: a etapa 2 equilibra **dentro** de cada categoria. A diferença entre categorias aparece à parte.
- A tela e a planilha ganharam um indicador novo: **horas de contrato não utilizadas** por categoria.
- **Todos os testes passaram.** O 9c bateu exatamente com a conta registrada antes de rodar, e os 544 XML continuam idênticos.
- **A P1 foi lançada** às 14:29, com o modelo final. Pode levar até cerca de 3 h. Nada a decidir agora.
- Para conferir em casa: `git pull`. Para rodar um teste da tela isolado: `python src\testes_ferramenta.py 9`, por exemplo.

---

## 1. O que mudou no código

| Item | Onde |
|---|---|
| A etapa 2 minimiza (maior − menor fração entre enfermeiros) + (o mesmo entre técnicos), com a etapa 1 fixada no ótimo | `ferramenta.preparar_equilibrio` |
| Categoria do profissional, por habilidade | `ferramenta.categoria`, `ENF`, `TEC` |
| Por categoria: faixa da fração, fração média, horas devidas, escaladas e **não utilizadas** | `ferramenta.por_categoria` |
| `amplitude` passa a ser o critério da etapa 2 (soma por categoria) | `ferramenta.amplitude` |
| Diferença entre categorias (fração média dos técnicos − dos enfermeiros), não otimizada | `ferramenta.diferenca_entre_categorias` |
| Tela: uma linha por categoria, a diferença entre categorias e a frase do equilíbrio reescrita | `src/app.py` |
| Planilha, aba Resumo: fração e horas não utilizadas por categoria, e a diferença | `ferramenta.planilha` |
| P1 grava amplitude e horas não utilizadas por categoria no CSV | `src/escalabilidade_objetivo.py` |
| Testes da tela rodam por nome, um por processo (`... testes_ferramenta.py 7.2`) | `src/testes_ferramenta.py` |

## 2. Esperados

Todos ficaram no commit `08603c6`, **antes** de qualquer teste rodar.

**9c, pelo critério por categoria (conta feita antes):**
- Enfermeiros cobrem o posto deles, 672 h ÷ 6 = 112 h cada (63,6%). Amplitude **0**.
- Técnicos cobrem 1.792 h. Téc 1 deve 88 h, com degraus de 9,09 pp; os outros devem 176 h, com degraus de 4,55 pp. Amplitude zero exigiria 23x = 224, que não tem solução inteira. O mínimo é então **1/22 = 4,55 pp**, e só é atingido com Téc 1 em 10 turnos (90,9%).
- Horas não utilizadas: **384 h** dos enfermeiros e **232 h** dos técnicos. Diferença entre categorias: **+24,9 pp**.

**Caso 5 da tela:** o esperado passou a ser ≥ 30, pela conta com 44 h (5 × 176 = 880 h para 1.120 h de posto de técnico; faltam 240 h = 30 turnos). Está anotado no teste que **foi corrigido depois de ver o resultado**, por ser aritmético. O texto do 7.1 também passou a dizer "mínimo 30", e a condição dele não mudou.

**9b sem teto:** foi preciso desligar dois limites, não um.
- O teto de horas.
- O `MaxNumAssignments`, que no 12×36 vale floor(176/12) = 14 e é rígido. Se só o teto de horas saísse, ele continuaria parando em 14.

Também não basta olhar a escala da ferramenta: a demanda dá 12,8 plantões por pessoa, então ninguém precisa passar de 14. Por isso o teste **maximiza** os plantões de Téc 1. O esperado é 14.

## 3. Resultados

| Teste | Resultado |
|---|---|
| Tela 1–2, 3, 4 | OK |
| Tela 5 | **OK**: 30 (≥ 30) |
| 7.1 | OK: 30 turnos, pedidos 3/3, W = 141 |
| 7.2 | OK (só relata). Etapa 1 provada, penalidade 96, pedidos 20/20. Etapa 2: critério 34,1 → 13,6 pp, **sem prova**, parou no limite de 600 s |
| 7.3 | OK, os cinco diagnósticos |
| 8a–8d | OK |
| 9a | OK: 112 h (teto 120 h) e 168 h (teto 176 h) |
| 9b | OK: 14 plantões |
| **9b sem teto** | **OK: máximo de 14, provado.** Quem limita é a alternância, não o teto |
| **9c** | **OK em tudo**: enfermeiros 63,6%–63,6% (0); técnicos 86,4%–90,9% (4,55 pp, provado); Téc 1 com 80 h de 88 h = 90,9%; não utilizadas 384 h / 232 h; +24,9 pp entre categorias |
| 9d | OK: 36,4 → 4,5 pp, provado (etapa 2 em 111 s) |
| `regressao.py --todos` | OK: 56, 58, 197, 219 = Tabela 6 |
| `testes_entrada.py` | OK |
| 544 XML | idênticos byte a byte ao commit `cec3d8e` (0 diferentes) |

**Resultado idêntico, visto com o critério do CLAUDE.md.** Os 544 XML iguais não são alarme: a mudança está só na etapa 2, que não entra na escrita do XML. Já a mudança de critério alterou os números onde devia alterar: 9c, 9d e 7.2 deram valores diferentes dos de 03/10 de manhã.

**Ponto de atenção para a P1, não resultado.** No 7.2, a etapa 2 por categoria não provou em 600 s, com 40 pessoas e 20 pedidos. A P1 vai medir isso com 900 s.

Os tempos são limite operacional, não resultado. Máquina: Intel Core i5-10210U, 12 GB, Windows 11, Python 3.11.9, HiGHS 1.15.1 via appsi.

## 4. P1

Lançada às **14:29 de 03/10** (PID 22292): `python src\escalabilidade_objetivo.py --tempo 900`, em segundo plano.
- Log: `resultados\escalabilidade_objetivo\p1_2026-10-03.log`.
- Log do HiGHS por etapa: `highs_N<n>_etapa<k>.log`.
- CSV: `resultados\escalabilidade_objetivo.csv`.

Registra por tamanho:
- tempo até a primeira escala legal, lido do log do HiGHS;
- estado, tempo e resultado de cada etapa;
- gap e se provou a otimalidade;
- conferência de descanso medida e rígidas;
- máquina.

Tamanhos: 36, 40, 60, 80, 120 e 200. São no máximo 2 × 900 s por tamanho, cerca de 3 h. **O resultado ainda não foi lido.** A leitura fica para a próxima sessão.

## 5. Commits

| Commit | Conteúdo |
|---|---|
| `08603c6` | Código da P6, indicador novo, esperados registrados antes de rodar |
| o seguinte | Registros (DECISOES, PROPOSTAS, ESTADO_ATUAL), resultado no docstring dos testes, este relatório (`git add -f`) |

---

## LEVAR PARA O PROJETO DE REDACAO

- **`DECISOES.md`**, entrada "2026-10-02 — Carga por contrato", com adendo (sem reescrever o que havia):
  - item g): a etapa 2 equilibra dentro de cada categoria, e a diferença entre categorias é mostrada à parte;
  - item h): indicador de horas de contrato não utilizadas;
  - esperados refeitos (9c, caso 5, 9b sem teto) e seus resultados;
  - suíte completa OK.
- **`PROPOSTAS.md`**:
  - P6 marcada como **RESOLVIDA** (saída 1, decisão do Otávio, implementada e testada);
  - P1 anotada como lançada às 14:29 de 03/10 com o modelo final, resultado pendente.
- **`ESTADO_ATUAL.md`**: nota de atualização no item 2 do pendente (P6 resolvida, suíte OK, P1 lançada).
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
