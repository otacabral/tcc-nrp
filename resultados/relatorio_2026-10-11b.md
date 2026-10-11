# Relatório de 11/10/2026 (b): diagnóstico da etapa 2 no K5 (só teste), P19, P16, 8b

Máquina: Intel Core i5-10210U, 12 GB, Windows 11, `appsi_highs` (HiGHS 1.15.1). Tempos são
limite operacional, não resultado. **Nada mudou em `src/`, na ferramenta nem na `v1.2.2`.**

## Para o Otávio

- **Diagnóstico da etapa 2 no K5:** script e esperado commitados antes (`195cf9b`). Os dois
  testes curtos (60 s) rodaram até o fim, todas as conferências OK, sem melhora.
- **Para executar:** as duas rodadas de verdade, A (1.800 s) e B (180 s). Comandos no fim.
- **Registrado:** P19 nova (trabalho futuro, com duas opções descartadas), item novo na P16 e o
  8b na seção 13 do `NUMEROS_TCC.md` (total: 5 de 5 resoluções sem prova, nenhuma melhora).
- **Commit e push feitos.** Os resultados de A e B entram depois das rodadas.

## 1. Diagnóstico da etapa 2 no K5 (só teste)

Script: `docs/diagnostico/p17_etapa2_variantes.py`. O esperado está no cabeçalho e no
`DECISOES.md` ("2026-10-10 — P17", item d), commit `195cf9b`, antes de qualquer rodada.

**Como o script monta a partida:**
- usa as funções da ferramenta: `montar`, `pesos`, `modelo_br` e
  `preparar_equilibrio(..., exato=False)`;
- **fixa** os `x` na escala gravada da etapa 1 e resolve a etapa 1, para as variáveis auxiliares
  ganharem valor coerente com essa escala;
- confere que o objetivo dá 21, solta os `x`, troca o objetivo pelo da etapa 2 (penalidade ≤ 21)
  e resolve com `partida=True`.

**Na variante B:**
- grupos de idênticos achados pelo script: 13 enfermeiros e 5 técnicos;
- 16 restrições de ordem (12 + 4);
- partida renumerada por horas decrescentes dentro de cada grupo;
- a escala final é devolvida à numeração original e conferida na instância original.

**Testes curtos, 60 s, rodados até o fim** (`resultados/p17_variantes_2026-10-11/A_teste/` e
`B_teste/`). O veredito deles não vale como resultado:

| | A (teste) | B (teste) |
|---|---|---|
| partida aceita no log | 0,4091 | 0,4091 |
| melhoras na tabela do log | nenhuma | nenhuma |
| fim | primal 0,4091; dual ~1e-14; gap 100%; 616 nós | primal 0,4091; dual ~3e-14; gap 100%; 790 nós |
| penalidade final (recontada) | 21 | 21 |
| diferença entre colegas (h), enf. / téc. | 42 / 30 | 42 / 30 |
| conferências | todas OK | todas OK, inclusive a 5 (desfeita a renumeração) |

**Rodadas de verdade (A, 1.800 s; B, 180 s): pendentes.** Comandos no fim.

## 2. P19 nova: equilíbrio nos casos de fronteira (trabalho futuro)

- **(a) Quebra de simetria.** O resultado da rodada 1B entra quando ela rodar.
- **(b) Equilíbrio como faixa, por bissecção.**
- **(c) Troca explícita para o gestor:** uma piora limitada da etapa 1 em troca de equilíbrio.
- **Descartadas, com motivo:**
  - retirar a etapa 2: perde 9d 36,4 → 4,5 pp e, na rodada com folga, 34,1/20,5/27,3 → 13,6 pp;
  - pôr o equilíbrio como prioridade da etapa 1: subordina o COFEN, leva o limite inferior ~0
    para a etapa 1 e invalida a bateria.

## 3. P16, item novo

No caminho **com prova** sem melhora, a linha passa a ser "O equilíbrio de carga não reduziu a
diferença entre colegas em relação à etapa 1." Caso ainda não observado. Não mexer antes de 26/10.

## 4. `NUMEROS_TCC.md`, seção 13

- **O 8b não estava lá; acrescentado.** Critério 0,3409 → 0,3409, 25 s.
- **Conferência que ele de fato teve:** o teste conferiu, sobre os indicadores da ferramenta, que
  o critério final é igual ao da etapa 1 e que a linha bate. **SEM RECONTAGEM INDEPENDENTE**: a
  escala não foi gravada.
- **Linha de total:** 5 de 5 resoluções sem prova, nenhuma melhora.

## Para rodar: as duas rodadas do diagnóstico

Feche o Chrome, este terminal do Claude Code e qualquer Streamlit aberto. No PowerShell, na pasta
do repositório:

```
cd D:\dev\tcc-nrp
.\.venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING = "utf-8"
(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
```

O último número é a memória livre em GB. Se for **menor que 3**, feche mais programas.

```
python docs\diagnostico\p17_etapa2_variantes.py B
python docs\diagnostico\p17_etapa2_variantes.py A
```

- **B primeiro** (~4 min), depois **A** (~31 min).
- A última linha de cada uma diz "SEM MELHORA" ou "MELHORA", e "CONFERENCIAS OK" ou
  "CONFERENCIA FALHOU".
- Saída em `resultados\p17_variantes_2026-10-11\B\` e `...\A\`.
- Se aparecer "CONFERENCIA FALHOU" ou "PARADO", não rode a outra: me traga a saída.
