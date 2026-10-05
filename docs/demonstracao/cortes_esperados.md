# Rodada 2 da demonstração — cortes esperados pela conta

**Registrado em 05/10/2026, ANTES de rodar a rodada 2 pela tela.** Conta sem solver e sem as
contas da ferramenta: `python docs\demonstracao\conta_cortes.py` (o método está no docstring).
Técnicos retirados do fim da lista do caso; enfermeiros fixos em 8.

| técnicos | total | horas posto téc. | tetos dos téc. | enf. em posto téc. (mín.) | folga dos enf. | pior par de dias (demanda / disponíveis) | alertas COFEN | trava pela conta |
|---|---|---|---|---|---|---|---|---|
| 22 | 30 | 3456 h | 3468 h | 0 | 312 h | 03/11–04/11: 28 / 29 | 1 | não |
| 21 | 29 | 3456 h | 3300 h | 13 | 312 h | 03/11–04/11: 28 / 28 | 2 | não |
| 20 | 28 | 3456 h | 3132 h | 27 | 312 h | 03/11–04/11: 28 / 27 | 2 | horas, dois dias seguidos |
| 19 | 27 | 3456 h | 2988 h | 39 | 312 h | 03/11–04/11: 28 / 26 | 2 | horas, dois dias seguidos |
| 18 | 26 | 3456 h | 2844 h | 51 | 312 h | 03/11–04/11: 28 / 25 | 2 | horas, dois dias seguidos |
| 17 | 25 | 3456 h | 2700 h | 63 | 312 h | 03/11–04/11: 28 / 24 | 2 | horas, dois dias seguidos |

"Enf. em posto téc. (mín.)" é o mínimo que a conta de horas obriga; o solver pode precisar de
mais (outras regras somam). "Trava pela conta" = alguma das contas já mostra que não há escala.

## Transições esperadas

| Transição | Corte esperado pela conta |
|---|---|
| escala limpa (sem alerta do COFEN, sem enfermeiro em posto de técnico) | **não ocorre** de 22 técnicos para baixo: o alerta de proporção (8 enfermeiros, quando o Parecer pede ceil(33% do quadro)) existe em todo quadro de 25 ou mais pessoas, e com 16 técnicos ou menos (quadro de 24) a escala já trava |
| escala com alerta do COFEN e enfermeiros em posto de técnico | **22 técnicos** (rodada 1): 1 alerta (proporção); a conta de horas não obriga enfermeiro em posto de técnico (sobram 12 h), mas não proíbe. **21 técnicos**: 2 alertas (proporção e quadro abaixo do QP completo); pelo menos **13** turnos de enfermeiro em posto de técnico |
| trava pela CLT | **20 técnicos** (28 pessoas), por duas contas: (a) horas — faltam 324 h de técnico, contra 312 h de folga dos enfermeiros, contando o teto pela alternância (14 plantões = 168 h, não 176 h); (b) par 03–04/11 — 28 plantões para 27 pessoas disponíveis, porque Karen Dias está de férias. **Menor quadro viável esperado: 29** (com 1 a mais, o par fica 28/28, e a folga cobre a falta) |

## O que a ferramenta deve mostrar na trava

O diagnóstico da ferramenta, calculado por ela só com contas (`ferramenta.diagnosticar`,
rodado agora sem solver), dá **"combinação de regras"** nos três cortes. A conta acima explica
a trava de 20 por motivos simples que o diagnóstico da ferramenta não vê:

- a regra de alternância do diagnóstico compara a soma de dois dias com o quadro inteiro, sem
  descontar quem está de férias num dos dois dias;
- a regra de horas usa o teto do contrato (176 h), não o teto da alternância do 12×36
  (168 h), e não separa as horas de técnico.

Esperado na tela, para 20 técnicos: **"Falta 1; o menor quadro viável é 29"**, diagnóstico
**"Combinação de regras"**. Melhorar o diagnóstico é mudança de funcionalidade: vai como
proposta, não implementada.

**Já se sabia de antes** (execução sem tela de 05/10, pelo mesmo motor; declarado aqui para não
parecer previsão): 22 admite com 4 turnos de enfermeiro em posto de técnico; 21 admite com 13;
20 trava, com "combinação de regras" e menor quadro viável de 29 (9 + 20).
