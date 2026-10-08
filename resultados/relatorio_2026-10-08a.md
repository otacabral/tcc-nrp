# Relatório de 08/10/2026 (a) — bateria: K3/K4 com 3.600 s, propriedades 2 e 3, nível 3

*Escrito parte a parte, numa sessão sem supervisão (madrugada de 07 para 08/10). Cada parte
foi commitada e enviada ao fim. Travas: nada em `src/` nem nos testes; scripts só em
`docs/diagnostico/`.*

Máquina: i5-10210U, `appsi_highs` (HiGHS 1.15.1). Tempos são limite operacional, não
resultado.

## Para o Otávio

- **Parte 1 feita:** nota corrigida; os esperados da rodada de 07/10 são os de `545bae9`, e
  nenhum caso perde valor.
- **Parte 2 interrompida pelo sistema, por falta de memória.** O K4 rodou ~1.909 s **sem achar
  escala** e foi morto; o K3 não rodou.
- **Partes 3 e 4 prontas e registradas, mas não rodadas.** Com 1,2 GB livres, relançar
  arriscava outra queda. Os 96 derivados e os 100 casos do nível 3 (semente 81026) montam sem
  erro; foram conferidos sem solver.
- **Para decidir:** as faixas do nível 3 fazem 78 de 100 casos nascerem inviáveis (ver parte 4).
- **Para executar:** feche o Chrome e rode os comandos do fim, um bloco por vez.

| Parte | Status | Falhas | Commit |
|---|---|---|---|
| 1. Correções | feita | — | `3ef7da2` |
| 2. K4 e K3, 3.600 s | **interrompida** (memória); K4 sem escala em ~1.909 s; K3 não rodou | nenhuma achada; inconclusivo | `dddd3dd` (esperado), `ff54b2b` |
| 3. Monotonia e ordem | script e derivados conferidos; **não rodada** | — | `ff54b2b` |
| 4. Nível 3 | 100 casos sorteados e commitados; **não rodada** | — | `ff54b2b` |

**Falhas por camada (C4):** nenhuma falha nova. Segue em aberto o achado de 07/10 (K3/K4 sem
escala), agora com K4 também sem escala em ~1.909 s: camada **solver ou modelo**, não
determinada.

## Parte 1 — correções e conferência dos esperados

**1a.** `docs/bateria_entradas.md`: a nota de 07/10 dizia "níveis 2 e 3 ainda não rodados".
O nível 2 (K1–K6) rodou. Corrigida para o que faltava de fato: propriedades 2 e 3 da C3 e
nível 3. A correção fica marcada na própria nota.

**1b.** Os esperados usados na rodada de 07/10 são os do commit `545bae9`:
- `docs/diagnostico/bateria_desenho.py` tem um único commit (`62bbf4d`, 07/10 00:47), anterior
  a `545bae9`; sem diferença no arquivo de trabalho. Modificado pela última vez às 00:46 de
  07/10; a rodada começou às ~21:02 do mesmo dia.
- Rodado de novo agora, o gerador reproduz a tabela de `docs/bateria_entradas.md` em
  `545bae9`: P01–P18 com caso, modelo, equipe, esperado e as quatro folgas idênticos (a tabela
  do documento só tem acentos, que o script não usa); K1–K6 com o mesmo veredito e as mesmas
  folgas citadas na tabela do nível 2.
- O esperado gravado em cada JSON da rodada é calculado pelo mesmo arquivo, na hora.

**Nenhum caso muda; todos contam como teste.**

## Parte 2 — K4 (17) e K3 (16), só a etapa 1, 3.600 s

**Esperado registrado antes de rodar** (este parágrafo foi commitado antes do primeiro
solver): a conta independente **não prova escala** em nenhum dos dois — folga 1 em ocupados
por dia no K4 e 0 no K3 — e também **não prova inviabilidade** (nenhuma folga negativa).
Qualquer dos três desfechos é possível: escala achada, inviabilidade provada ou tempo esgotado.
O que separaria as camadas (C4): escala achada → a falha de 07/10 era de **solver** (tempo);
inviabilidade provada → a conta da bateria é frouxa demais para esta família, e o caso passa a
"inviável com prova".

Como roda: `docs/diagnostico/caso_parte_a.py etapa1 --enf N --tempo 3600 --log <arq>`, o
mesmo caminho da parte A (`ferramenta.montar` → `ferramenta.pesos` →
`experimento_a.modelo_br`), com a entrada idêntica à de K3/K4 (6 h + noturno de 12 h, M 2+1,
T 2+1, N 3+2, início 12/10/2026, grau intermediário, 5 técnicos). Um por vez, K4 primeiro,
nada mais rodando na máquina.

### Resultado da parte 2 — INTERROMPIDA pelo sistema, por falta de memória

- **K4 (12 + 5):** começou às 22:46:14. O Claude Code matou o processo por **memória
  crítica no sistema** por volta dos **1.909 s** (último registro do log do HiGHS). Até ali:
  **nenhuma escala** (BestSol = inf), limite inferior 15,25, 0,06% da árvore explorada.
  Inconclusivo: não achou escala nem provou inviabilidade.
- **K3 (11 + 5): não rodou.** O laço foi morto junto.
- Depois da interrupção, a máquina tinha 1,2 GB livres de 11,8 GB (o Chrome aberto ocupava
  mais de 2 GB). **Não relancei**: a regra do sistema é não reiniciar sozinho com memória curta.

Trecho final do log do HiGHS (`resultados/bateria_2026-10-08/parte2/highs_17.log`):

```
        Nodes      |    B&B Tree     |            Objective Bounds              |  Dynamic Constraints |       Work
Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time
     13268    1825      1238   0.06%   15.25           inf                  inf     7741    436   9995     4991k  1899.9s
     13308    1825      1240   0.06%   15.25           inf                  inf     7552    387   9402     5016k  1908.9s
```

Leitura: em 1.909 s, o HiGHS não achou nenhuma escala para 17 pessoas. Com 20 (parte A),
achou em 0,4 s. O limite inferior (15,25) é do **objetivo**, não da viabilidade: ele não
diz nada sobre a escala existir. **Camada: solver ou modelo, ainda não determinada.**

Para relançar (com o Chrome fechado), um de cada vez:

```
.\.venv\Scripts\Activate.ps1
python docs\diagnostico\caso_parte_a.py etapa1 --enf 12 --tec 5 --tempo 3600 --log resultados\bateria_2026-10-08\parte2\highs_17.log
python docs\diagnostico\caso_parte_a.py etapa1 --enf 11 --tec 5 --tempo 3600 --log resultados\bateria_2026-10-08\parte2\highs_16.log
```

## Parte 3 — propriedades 2 e 3: SCRIPT PRONTO, NÃO RODADA

Não rodada pela mesma falta de memória (são 96 resoluções; o sistema acabara de matar a
parte 2). Script: `docs/diagnostico/bateria_propriedades.py`, commitado antes de qualquer
solver. **A etapa 2 é desligada no script** (troca de `ferramenta.equilibrar`, sem tocar em
`src/`), porque veredito e menor quadro saem só da etapa 1; o cabeçalho do script declara
isso, os quatro derivados e o que se exige de cada um. A base de comparação são os JSON de
07/10.

Conferido sem solver: os 96 derivados (24 casos × 4) montam, e cada um muda só o que devia:
- `mais_pessoa`: +1 pessoa, +176 h de teto, demanda igual;
- `mais_posto`: demanda + a duração de um turno, teto igual;
- `mais_ferias`: +1 dia indisponível, teto − carga/7 do profissional "0";
- `embaralhado` (semente 20261008 + índice do caso): mesma demanda, mesmo teto, mesmas
  cargas (no P04 o teto difere na 13ª casa decimal, só pela ordem da soma).

## Parte 4 — nível 3: CASOS SORTEADOS E REGISTRADOS, NÃO RODADA

Não rodada pelo mesmo motivo. Os **100 casos estão sorteados e commitados antes de qualquer
solver**: semente **81026**, `docs/diagnostico/nivel3_casos.json`, script
`docs/diagnostico/bateria_nivel3.py` (as faixas e o que o desenho não fixava estão no
cabeçalho). Conferido sem solver: os 100 montam sem erro de entrada, e a folga em horas da
instância bate com a da conta nos 100.

**Como saiu o sorteio, pela conta:**

| Modelo | Gera escala (esperado) | Fronteira | Inviável pela conta |
|---|---|---|---|
| 12x36 | 3 | 2 | 28 |
| 6+12 | 3 | 2 | 24 |
| 8h | 11 | 1 | 26 |
| **Total** | **17** | **5** | **78** |

**Ponto para decidir antes de rodar:** com as faixas do desenho (1 a 2 enfermeiros e 0 a 4
técnicos por turno, contra 3 a 8 enfermeiros e 2 a 12 técnicos), 78 de 100 casos já nascem
inviáveis pela conta. O lote vai exercitar muito o "faltam N" e o diagnóstico, e pouco a
propriedade 5 (folga clara), que só vale nos 17. Não mudei as faixas: são as do desenho, e
mudá-las é mudança de desenho experimental.

## Para rodar o que faltou (feche o Chrome antes)

No PowerShell, na pasta do repositório. Antes de tudo, `.\.venv\Scripts\Activate.ps1`.

**Parte 2** (um de cada vez, até 1 h cada): os dois comandos da seção da parte 2.

**Parte 3:** primeiro o menor caso, até o fim; depois o resto (até ~3 h):

```
python docs\diagnostico\bateria_propriedades.py P08 mais_pessoa
foreach ($c in "P01","P02","P03","P04","P05","P06","P07","P08","P09","P10","P11","P12","P13","P14","P15","P16","P17","P18","K1","K2","K3","K4","K5","K6") { foreach ($v in "mais_pessoa","mais_posto","mais_ferias","embaralhado") { if (-not (Test-Path "resultados\bateria_2026-10-08\parte3\${c}_$v.json")) { python docs\diagnostico\bateria_propriedades.py $c $v } } }
python docs\diagnostico\bateria_propriedades.py --resumo
```

**Parte 4:** primeiro um caso, depois o resto:

```
python docs\diagnostico\bateria_nivel3.py N001
1..100 | ForEach-Object { $n = "N{0:D3}" -f $_; if (-not (Test-Path "resultados\bateria_2026-10-08\parte4\$n.json")) { python docs\diagnostico\bateria_nivel3.py $n } }
python docs\diagnostico\bateria_nivel3.py --resumo
```

O laço pula os casos que já têm resultado gravado: se cair no meio, é só rodar de novo.

**Commit**, depois de cada parte (o `-f` porque `resultados/` é ignorada pelo git):

```
git add -f resultados/bateria_2026-10-08 resultados/relatorio_2026-10-08a.md
git commit -m "Bateria 08/10: parte N rodada"
git push
```
