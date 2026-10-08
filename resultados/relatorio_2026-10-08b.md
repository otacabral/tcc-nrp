# Relatório de 08/10/2026 (b) — registros da bateria (A) e implementação da P12 (B)

Máquina: i5-10210U, 12 GB, `appsi_highs` (HiGHS 1.15.1). Tempos são limite operacional, não
resultado.

## Para o Otávio

- **Parte A feita.** Propriedades 2 e 3: 96 derivados, 0 violações. **A escala com 17 do K4
  existe** (conferida); as falhas dele em 600 s e ~1.909 s são do solver. Nível 3 resorteado
  (40/30/30), commitado, **não rodado**: comandos no fim, com o Chrome fechado.
- **Parte B: P12 implementada, mas PARADA no B4.** Suíte com 15 de 16 OK; a falha é do **teste
  novo 12a**, que olhava a tabela errada da tela (a de turnos, não a escala). A escala da tela
  é idêntica à da planilha; o diagnóstico está abaixo.
- **Para decidir:** autorizar a correção do seletor do 12a (`at.dataframe[0]` →
  `at.dataframe[-1]`), sem mudar o esperado. Depois disso: demonstração refeita, P05/P08/K1,
  guia, capturas e tag `v1.1`.
- Nada de `modelo.py` nem `instancia_br.py` mudou; a regressão passou.


## Parte A — bateria: registros e decisões

### A1a — propriedades 2 e 3 (parte 3, rodada pelo Otávio em 08/10)

`python docs\diagnosticoateria_propriedades.py --resumo`, conferido de novo aqui:
**96 derivados, 88 ok, 8 inconclusivos, 0 violações.** Todas as escalas geradas passaram nas
conferências da propriedade 1 (cobertura, descanso no relógio, teto, férias). Etapa 2
desligada; veredito e menor quadro só dependem da etapa 1.

**Os 8 inconclusivos**, todos porque a **base** terminou "não decidido" (sem escala em 600 s):
sem veredito na base, nenhuma das propriedades tem o que comparar.

| Caso | Derivado | Base | Derivado deu |
|---|---|---|---|
| K3 | mais_pessoa | não decidido | admite, 17 (sem prova, gap 85,7%) |
| K3 | mais_posto | não decidido | não decidido |
| K3 | mais_ferias | não decidido | não decidido |
| K3 | embaralhado | não decidido | não decidido |
| K4 | mais_pessoa | não decidido | admite, 18 |
| K4 | mais_posto | não decidido | não decidido |
| K4 | mais_ferias | não decidido | não decidido |
| K4 | embaralhado | não decidido | não decidido |

### A1b — K3/mais_pessoa é a instância do K4?

**Não é idêntica.** O derivado `mais_pessoa` acrescenta um **técnico**: K3/mais_pessoa tem
**11 enfermeiros + 6 técnicos**, e o K4 tem **12 + 5**. Todo o resto é igual (demanda, turnos,
início, sem férias, pedidos nem cargas); só a pessoa "11" difere: técnico numa, enfermeiro na
outra.

**Mas a escala vale no K4**, e isso foi conferido, não só argumentado
(`docs/diagnostico/k4_dominancia.py`, esperado commitado antes em `57de0c4`; saída em
`resultados/bateria_2026-10-08/k4_dominancia/`):

```
etapa 1 de K3/mais_pessoa, 600 s: viavel | provado False | gap 0.857
K4: 12 enf + 5 tec
pessoas que diferem entre as duas instancias: ['11']
demanda identica: True | turnos identicos: True
conferir_rigidas no K4 (habilidade rigida): ok
descanso no relogio: cumpre {'menor_folga': 0.0, 'menor_semanal': 36.0, 'max_consec': 6}
acima do teto: ninguem
fora do dominio do modelo do K4: nenhuma
modelo da etapa 1 do K4 com a escala fixada: optimal | tem solucao True
```

**Conclusão:** a escala com 17 existe no K4. "Sem escala em 600 s" (07/10), "sem escala em
~1.909 s" (08/10, interrompido) e K4/embaralhado sem escala em 600 s são **variação de
desempenho do solver na fronteira (camada solver), não defeito**.

### A2 — K3 e K4 longos: não rodam de novo (decisão do Otávio)

Registrado em `DECISOES.md` ("2026-10-08 — Bateria: K3/K4 longos não rodam de novo; nível 3
estratificado") e em `resultados/NUMEROS_TCC.md` (seção 11):
- K4: **"escala com 17 existe; o solver nem sempre a acha em 600 s (variação de desempenho na
  fronteira)"** — pela conferência do A1b, embora a instância de K3/mais_pessoa não seja a do
  K4;
- K3 (16): não determinado;
- **limitação:** casos de fronteira podem não ser decididos no tempo e na memória disponíveis.

### A3 — nível 3 resorteado, estratificado (NÃO rodado)

`docs/diagnostico/bateria_nivel3.py --gerar`, semente **20261008**; 495 candidatos sorteados
nas faixas do desenho até encher os estratos. Casos e esperados em
`docs/diagnostico/nivel3_casos_estratificado.json`, **commitados antes de rodar** (`b8ce2ae`).
Conferido sem solver: os 100 montam, o esperado gravado bate com a conta, a folga em horas da
instância bate com a da conta.

| Modelo | Folga clara | Fronteira | Inviável | Total |
|---|---|---|---|---|
| 12x36 | 9 | 14 | 7 | 30 |
| 8h | 26 | 2 | 9 | 37 |
| 6+12 | 5 | 14 | 14 | 33 |
| **Total** | **40** | **30** | **30** | **100** |

Ressalva: a folga clara saiu concentrada no 8 h (26 de 40), e a fronteira no 12×36 e no
6 h + 12 h. É o que as faixas produzem; não forcei equilíbrio por modelo.

O sorteio de 07/10 (semente 81026, `docs/diagnostico/nivel3_casos.json`) fica no repositório
como **descartado antes de rodar** (78 de 100 inviáveis). O script ainda o reproduz
(`sortear_07_10`), conferido.

`--lote`: um processo por caso, 15 min no máximo; esgotado, grava "não determinado (15 min)"
e segue; pula os casos que já têm resultado.

## B1 — tempo de um clique na demonstração da clínica, antes de implementar

Pelos registros existentes, sem rodar de novo: `docs/demonstracao/rodada*_memoria.txt`, que o
`rodar_rodada.sh` grava a cada ~10 s, do início do roteiro de capturas (servidor subindo,
digitação da entrada, clique, leitura do resultado) até o fim.

| Rodada | Técnicos (quadro) | Início | Fim | Rodada inteira |
|---|---|---|---|---|
| 1 | 20 (30) | 20:51:00 | 20:56:58 | 5 min 58 s |
| 2 | 19 (29) | 20:57:10 | 21:03:08 | 5 min 58 s |
| 2 | 18 (28) | 21:03:14 | 21:09:12 | 5 min 58 s |

O clique é parte da rodada, então **cada clique levou no máximo ~6 min**, abaixo dos 13 min
(20 min de orçamento ÷ 1,5). **O B2 não para.** Ressalva: é limite superior, não medição do
clique isolado. Os três intervalos idênticos sugerem que o roteiro esperou um tempo fixo
depois do resultado; o tempo do clique será medido de novo na demonstração refeita (B4).

## B2 — esperado, registrado e commitado ANTES de implementar

**a) Escala da etapa 1 na tela.**
- Assim que a etapa 1 acha a escala do quadro final, a tela mostra essa escala (a grade
  profissional × dia, no mesmo formato da aba Escala da planilha) com o aviso **"Escala pronta;
  equilibrando a carga entre colegas (até 3 min)."** Durante esse tempo **não há botão de
  planilha**, e a tela diz "A planilha fica disponível quando o equilíbrio terminar." (um
  clique num botão do Streamlit reexecuta a tela e interromperia o cálculo).
- Quando a etapa 2 termina, a tela é atualizada: a grade provisória some, o resultado normal
  aparece, e uma linha diz qual escala vale: **"Escala desta tela: a da etapa 2, com a carga
  equilibrada entre colegas."**, ou **"Escala desta tela: a da etapa 1; o equilíbrio de carga
  não terminou no tempo."**, ou, se a etapa 2 não rodou, **"Escala desta tela: a da etapa 1;
  o equilíbrio de carga não rodou."**
- A planilha baixada é sempre a escala da tela: a grade da tela continua sendo lida da própria
  planilha, como hoje.
- Teste: pela ferramenta, o aviso da escala da etapa 1 chega antes do início da etapa 2, com
  uma escala que passa na conferência de descanso; pela tela, a linha "Escala desta tela" e a
  grade igual à da planilha, célula a célula, e igual à `r.escala`.

**b) Progresso.** A barra mostra a fase e o limite de tempo dela:
- "Conta: piso aritmético e alertas do COFEN";
- "Quadro informado, N profissionais: etapa 1 (procurando escala legal), até 10 min";
- "Busca do menor quadro, N profissionais: etapa 1 (procurando escala legal), até 10 min"
  (com "— 2ª composição: acréscimos como enfermeiros" quando for a segunda candidata);
- "Busca do menor quadro, N profissionais: inviável pela conta, sem solver";
- "Escala pronta com N profissionais: etapa 2 (equilibrando a carga entre colegas), até 3 min".
Cada mensagem termina com "· orçamento do clique: 20 min".
**Tempo decorrido ao vivo: não implementado.** Exige atualizar a tela enquanto o solver roda,
isto é, rodar o solver em outra thread (ou processo) e a tela num laço de espera. Fica como
proposta no relatório.

**c) Mensagens de falha.** "o solver falhou" deixa de existir na tela.
- Tempo esgotado sem escala no quadro informado: **"Sem resposta em 10 min com N
  profissionais: o solver não achou escala nem provou que ela não existe."**
- Quadro informado provado insuficiente e um quadro maior sem resposta: **"O quadro informado
  é insuficiente. Sem resposta em 10 min com N profissionais: o menor quadro viável não foi
  determinado."**
- Erro técnico: **"Erro técnico ao resolver com N profissionais; detalhes no console."** (com
  "O quadro informado é insuficiente. " antes, se for o caso). O console mostra a exceção
  inteira (traceback).
- Em "Como o veredito foi obtido": "sem resposta em 10 min — nem provado inviável" e "erro
  técnico ao resolver; detalhes no console".
- O tempo sai do limite usado: "10 min" com o limite da tela; nos testes que o encurtam, o
  valor encurtado (ex.: "3 s").

**d) Orçamento de 20 min por clique.**
- Cada resolução recebe como limite o menor entre o seu (600 s ou 180 s) e o que resta do
  orçamento; acabado o orçamento, a busca para.
- Se o quadro informado já foi provado insuficiente: **"O quadro informado é insuficiente; o
  menor quadro viável não foi determinado em 20 min."** Nunca "faltam N" sem prova.
- Se o orçamento acabar no próprio quadro informado: a mensagem do item c, com o tempo que
  ele teve.
- O orçamento não muda nenhum resultado em que o clique leve menos de 20 min.
- Teste com orçamento reduzido (3 s) no caso 8d (39 provado curto pela conta, 40 sem resposta):
  tela com "O quadro informado é insuficiente; o menor quadro viável não foi determinado em
  3 s.", diagnóstico de alternância e nenhum "Falta".

**e) Demonstração da clínica (20/19/18 técnicos).** Mesmos números, vereditos e textos de
diagnóstico de 05/10 (`resultados/relatorio_2026-10-05f.md`): 20 admite sem alerta; 19 admite
com o alerta de QP; 18 "Falta 1; o menor quadro viável é 29", diagnóstico "Alternância do
plantão de 12 h". Só mudam os textos de progresso, a linha nova "Escala desta tela" e os do
item c.

**f) Bateria.** P05 (faltam 1, menor 15), P08 (admite, 12) e K1 (admite, 16) com o mesmo
veredito e o mesmo menor quadro de 07/10.

**Testes afetados:** 8c e 8d (texto do tempo esgotado). Os demais testes da tela não leem os
textos que mudam.

## B3 — implementação (só `src/ferramenta.py` e `src/app.py`)

`modelo.py` e `instancia_br.py` **não mudaram** (`git diff --stat`: só os dois arquivos da tela
em `src/`). O item adicional da P12 (tetos do diagnóstico no piso) **não** foi implementado.

- `ferramenta.ORCAMENTO = 20 * 60`, lido na chamada. Em `verificar`, cada resolução recebe
  `min(limite, o que resta do orçamento)`; acabado, a busca para (tentativa "orcamento").
- `Resultado.parada` = (motivo, quadro, segundos que a resolução teve); `Resultado.frase()`
  monta os textos do item c e do d a partir dela. "Faltam N" continua só com prova.
- `Resultado.frase_vigente()`: a linha "Escala desta tela: …".
- `resolver_com_objetivo(..., aviso, prazo)`: avisa "escala_etapa1" e "etapa2" antes da etapa
  2, e corta o limite da etapa 2 pelo orçamento.
- `resolver`: com exceção do solver, além da linha "[ERRO] …", imprime o traceback.
- `ferramenta.grade(inst, escala)`: a grade profissional × dia saiu de dentro de `planilha`
  para uma função só, que a planilha e a tela provisória usam.
- `verificar` manda à barra a fase, o quadro, o limite da fase e o orçamento.
- `app.py`: área provisória com a escala da etapa 1 (sem botão de planilha), apagada quando o
  resultado final chega; linha "Escala desta tela"; textos novos em "Como o veredito foi
  obtido" (o "o solver falhou" saiu).

**Tempo decorrido ao vivo: não feito (proposta).** O Streamlit só redesenha a tela quando o
script chama um elemento; durante o `solve` do HiGHS o script está parado dentro do solver.
Para um relógio ao vivo, o solver teria de rodar em outra thread (ou processo) e a tela num
laço que atualiza a barra a cada segundo até ele terminar. Não é mudança de modelo, mas muda a
forma de execução, o tratamento de erro e o consumo de memória; fica para decisão.

## B4 — testes, um por processo — **PARADO: 1 falha, no teste novo 12a**

**Esperados de texto atualizados e commitados antes** (`3caa14f`). **Controle:** o caso 8 com
os esperados **antigos** contra o código novo **falha** no 8c e no 8d, e a tela mostra
exatamente os textos novos (`resultados/suite_2026-10-08/controle_8_esperado_antigo.log`).

Suíte (`bash docs/diagnostico/suite_p12.sh`; logs em `resultados/suite_2026-10-08/`):

| Teste | Código | Tempo | Resultado |
|---|---|---|---|
| regressão `--todos` | 0 | 59 s | OK (56, 58, 197, 219; espelho; decomposição) |
| testes_entrada | 0 | 8 s | OK |
| **tela 12 (novo)** | **1** | 377 s | **1 falha** (abaixo); 12c e 12d OK |
| tela 8 (8a–8d, textos novos) | 0 | 222 s | OK |
| tela 1-2 | 0 | 389 s | OK |
| tela 3 | 0 | 188 s | OK |
| tela 4 | 0 | 184 s | OK |
| tela 4b | 0 | 2 s | OK |
| tela 5 | 0 | 187 s | OK |
| tela 7.1 | 0 | 186 s | OK |
| tela 7.2 | 0 | 213 s | OK |
| tela 7.3 | 0 | 926 s | OK |
| tela 7.4 | 0 | 2 s | OK |
| tela 9 | 0 | 490 s | OK |
| tela 9b-sem-teto | 0 | 11 s | OK |
| tela 9c-tela | 0 | 25 s | OK |

Os 544 XML não foram comparados: o caminho que os gera não passa por `ferramenta.py` nem
`app.py`, e `instancia_br.py`/`modelo.py` não mudaram.

**A falha.** No 12a, o item "grade da tela = grade da planilha" falhou. Os outros itens do 12a
passaram: avisos na ordem certa (`escala_etapa1` antes de `etapa2`), escala da etapa 1 cumpre
o descanso, linha "Escala desta tela: a da etapa 2, …" coerente com a etapa 2 ("ok"),
planilha = `r.escala` célula a célula.

**Diagnóstico (só leitura, sem mexer no teste nem no código;**
`resultados/suite_2026-10-08/diagnostico_12a*.log`**):** o teste compara com
`at.dataframe[0]`, mas a tela tem **6** tabelas, e a 0 é a **tabela de turnos** da configuração
(Nome, Início, Fim). A escala é a **última** (a 5; 13 × 30). Comparada a ela: **tela =
`fe.grade` = planilha lida de volta, célula a célula, 0 diferenças.**

**Camada:** o próprio **teste** (seletor da tabela), não a ferramenta. **Proposta de correção,
não aplicada (regra: parar e relatar, sem ajustar):** no 12a, trocar `at.dataframe[0]` por
`at.dataframe[-1]`, ou pela tabela cuja primeira coluna é "Categoria". O esperado não muda:
"grade da tela = grade da planilha". **Esperado da correção:** o 12a passa inteiro.

**Não rodados, por causa da parada:** B2e (demonstração refeita pela tela, com as conferências
de descanso), B2f (P05, P08, K1), B5 (guia, capturas, `ESTADO_ATUAL.md`, tag `v1.1`). Já estão
prontos para rodar: `docs/demonstracao/capturas.py` agora mede o tempo do clique e fotografa a
tela de "equilibrando"; `docs/diagnostico/bateria_rodar.py` aceita `--saida` (para não
sobrescrever 07/10).

## B6 — registros

- **P3 (trabalho futuro):** "Recuperar o resultado na tela quando a conexão do navegador cai
  durante o cálculo" — acrescentado ao `PROPOSTAS.md` (commit `6a40925`).
- **Hipótese da parte A do diagnóstico:** os erros do Otávio na tela em 06/10 e 07/10 vieram de
  **queda de conexão do navegador** (console do Streamlit com `ConnectionResetError` WinError
  10054, sem nenhuma linha "[ERRO]" e sem queda do processo), não do modelo. Sustentação: pelo
  caminho da tela, sem navegador, o caso 15 + 5 gera escala (parte A, 07/10; K6 em 07/10).
  **Continua hipótese:** a captura da tela de 06/10 não existe.

## Comandos

**Commit** (feito nesta sessão; para referência):

```
git add src/app.py src/ferramenta.py docs/demonstracao/capturas.py docs/diagnostico/bateria_rodar.py docs/diagnostico/suite_p12.sh
git add -f resultados/suite_2026-10-08 resultados/relatorio_2026-10-08b.md
git commit -m "P12 implementada; suite 15/16, falha no seletor do teste 12a"
git push
```

**Nível 3, de madrugada.** **Feche o Chrome antes** (em 08/10 a falta de memória matou o K4).
No PowerShell, na raiz do repositório:

```
.\.venv\Scripts\Activate.ps1
python docs\diagnostico\bateria_nivel3.py N001
python docs\diagnostico\bateria_nivel3.py --lote
python docs\diagnostico\bateria_nivel3.py --resumo > resultados\bateria_2026-10-08\nivel3_resumo.md
git add -f resultados/bateria_2026-10-08
git commit -m "Nivel 3 rodado"
git push
```

O lote usa o código atual de `src/`, já com a P12; com cada caso limitado a 15 min, o
orçamento de 20 min do clique nunca é atingido. O `--lote` pula os casos que já têm resultado: se cair, é só rodar de novo. Cada caso tem no
máximo 15 min; o lote inteiro, no pior caso, 25 h, mas a maioria dos casos leva segundos ou
poucos minutos.
