# Relatório de 08/10/2026 (b) — registros da bateria (A) e implementação da P12 (B)

Máquina: i5-10210U, 12 GB, `appsi_highs` (HiGHS 1.15.1). Tempos são limite operacional, não
resultado.

<!-- PARA_O_OTAVIO -->

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
