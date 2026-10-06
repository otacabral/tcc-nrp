# Relatório de 05/10/2026 (f)

## Para o Otávio

- **Grau da proporção corrigido:** com pacientes informados, o alerta usa o grau do grupo de maior carga, como manda o Parecer, e diz qual usou. Na clínica, o grupo é o intermediário (84 h contra 32 h e 40 h), 33%.
- **Demonstração refeita pela tela**, com 10 enfermeiros + 20 técnicos e o 20/11 como feriado. Os três cortes saíram exatamente onde a conta, registrada antes, previu: 20 técnicos sem alerta, 19 com 1 alerta, 18 trava pela alternância.
- **Dois defeitos meus, achados e corrigidos.** O título "Modelo de entrada" do DECISOES tinha sido apagado numa edição. E um esperado de texto do `testes_entrada.py` não tinha sido atualizado depois da correção de plurais.
- **Decisão sua, P8 (nova):** o que fazer quando dois grupos de pacientes empatam em carga. Hoje a ferramenta avisa o empate e usa o maior percentual.
- `git pull` traz tudo.

---

## 1. Grau da proporção com graus misturados

**O que o Parecer diz.** Conferido no PDF oficial, Parecer Normativo nº 1/2024/COFEN, seção 3:

> "Quando houver diferentes tipos de cuidados em pacientes em um mesmo setor, a distribuição de profissionais por categoria deverá seguir o tipo de cuidado, cujo grupo de pacientes apresentar a maior carga de trabalho para assistência de Enfermagem."

Os dois exercícios resolvidos com dependência plena (Anexo II, Saúde Mental) usam a dependência discreta, 33%:
- **exercício 1:** carga por grupo de 210 h, 112,5 h e 112,5 h;
- **exercício 2:** 48 h, 30 h e 30 h.

O exercício de clínica médica fecha com a mesma leitura: mínimos 64 h, contra 48, 56 e 24 h.

Tudo está citado no DECISOES, entrada nova "2026-10-05 — Grau da proporção: o grupo de pacientes de maior carga", que corrige a leitura de 29/09.

**Na ferramenta** (`instancia_br.grau_do_alerta`):
- Com pacientes informados, vale o grupo de maior carga total, e o alerta diz qual grau usou e por quê.
- Sem pacientes, vale o campo da tela ("grau informado na tela").
- **Empate:** a regra não está decidida (P8). O alerta diz "empate de carga entre ..." e conta com o maior percentual, declarando isso.

**O modelo não mudou.** A função de 29/09 (`grau_de_maior_carga`) continua no caminho por pacientes de `construir`, que monta instâncias. Os 544 XML seguem idênticos byte a byte. Ficou registrada a divergência entre esse caminho (experimentos) e o alerta da tela.

**Esperado registrado antes** (commit `0618788`): clínica 32 / 84 / 40 h → intermediário. Deu intermediário, então não parei.

**Testes, um por processo:**
- 4b, novo (4b a 4e): OK, nos quatro casos — clínica, alta dependência mandando no campo, sem pacientes, empate.
- 4 (tela): OK; o alerta agora termina com "— grau informado na tela".
- `testes_entrada.py`: OK, depois de atualizar o esperado de texto ("1 turno(s)" → "1 turno"). Esse esperado tinha ficado velho desde a correção de plurais de 05/10, porque eu não rodei os testes de entrada depois dela.

## 2. A equipe e o 20/11

- **Equipe:** 10 enfermeiros (entram Ícaro Mendes e Júlia Freitas, 44 h) + 20 técnicos (saem Cíntia Zanetti e Diego Amaral, 44 h), 30 pessoas. Continuam 8 pessoas com 36 h.
- **20/11:** lançado como feriado, 1 + 4 nos dois turnos, igual ao 02/11.
- **Teste 7.4:** ficou congelado na equipe e nos feriados de 05/10, porque o esperado dele foi registrado sobre esses dados. Continua OK.

## 3. Conta registrada antes de rodar

Commit `ee7af24`, arquivo `docs/demonstracao/cortes_esperados.md`:

| Técnicos (quadro) | Esperado |
|---|---|
| 20 (30) | admite; **0 alertas**; enfermeiro em posto de técnico ≥ **24** |
| 19 (29) | admite; 1 alerta (QP completo 29,85); ≥ **36** |
| 18 (28) | **trava**; menor quadro viável **29**; diagnóstico **só "Alternância"**: ter 03/11–qua 04/11, 28 plantões, 27 pessoas. "Horas" não dispara: faltam 576 h de técnico, contra 660 h de folga dos enfermeiros |

## 4. As rodadas pela tela

Uma rodada por processo, com o Streamlit reiniciado entre elas. As capturas antigas da rodada 2 (21 e 20 técnicos) saíram da pasta e ficam no histórico do git.

| | Rodada 1: 10 + 20 = 30 | 19 técnicos (29) | 18 técnicos (28) |
|---|---|---|---|
| Veredito | "O quadro informado admite escala legal. Escala gerada." | idem | **"Falta 1; o menor quadro viável é 29. Escala gerada."** |
| Diagnóstico | — | — | **Alternância do plantão de 12 h** (texto abaixo) |
| Alertas do COFEN | **nenhum** | 1 (texto abaixo) | 1 (texto abaixo) |
| Quadro da escala | 30 | 29 | 29 (10 + 19) |
| Enfermeiro em posto de técnico | **24** (mínimo da conta: 24) | **36** (mínimo: 36) | 34 |
| Pedidos | "Todos os 6 pedidos de folga foram atendidos." | idem | idem |
| Contrato cumprido | 68%–100% | 82%–100% | 75%–100% |
| Diferença entre colegas, enf. · téc. | 1 plantão (12 h) · 0,6 plantão (6,9 h) | 0,2 plantão (2,3 h) · 0,6 plantão (6,9 h) | 0,9 plantão (10,2 h) · 0,6 plantão (6,8 h) |
| Horas não utilizadas, enf. · téc. | 432 h · 108 h | 288 h · 108 h | 312 h · 116 h |
| Diferença entre categorias | +24 pp | +14 pp | +16 pp |
| QP núcleo · completo | 26,08 · 30,00 | 25,96 · 29,85 | 25,82 · 29,70 |
| Descanso | cumpre (36 h; 36 h semanal; no máximo 1 dia seguido) | cumpre | cumpre |
| Pico de memória: servidor + solver · Chrome · roteiro | 301 · 569 · 58 MB | 309 · 600 · 58 MB | 331 · 580 · 59 MB |
| Menor memória livre | 2.638 MB | 2.757 MB | 2.958 MB |

**Texto exato do alerta, 19 técnicos:**
> Alerta COFEN (não impede a escala): quadro de 29 abaixo do QP completo do Parecer (29,85, com IST de 15%); o núcleo assistencial, sem IST, é 25,96

**Texto exato do alerta, 18 técnicos:**
> Alerta COFEN (não impede a escala): quadro de 28 abaixo do QP completo do Parecer (29,70, com IST de 15%); o núcleo assistencial, sem IST, é 25,82

**Diagnóstico na trava, 18 técnicos:**
> Por que não há escala legal com 28: Alternância do plantão de 12 h
>
> Com plantões de 12 h ninguém trabalha dois dias seguidos (a folga depois do plantão é de 36 h). ter 03/11 e qua 04/11 somam 28 plantões, que precisam de 28 pessoas diferentes; descontadas férias e licenças, 27 pessoas estão disponíveis em pelo menos um dos dois dias. Pela conta, falta pelo menos 1 pessoa.

**Comparação com a conta:** tudo igual, inclusive os textos dos alertas e do diagnóstico, palavra por palavra. Os turnos de enfermeiro em posto de técnico bateram com o mínimo da conta em 20 e 19.

**Outros pontos da tela:**
- O rótulo "Enfermeiro em posto de técnico" cabe sem cortar.
- A frase "Falta 1; ..." aparece duas vezes: no aviso amarelo e dentro da caixa do diagnóstico. É assim por desenho.
- No texto extraído da tela de 18 técnicos, "Todos os 6 pedidos..." aparece duas vezes, mas na captura aparece uma só. A repetição vem da página em atualização no momento da extração, não do que o usuário vê.

## 5. Defeitos achados e corrigidos

- **DECISOES.md:** o título "## Modelo de entrada" tinha sido apagado na edição da P7 (commit `7dc9bb9`). O modelo de entrada ficou grudado na seção da P7. Restaurei no commit `0618788`.
- **`testes_entrada.py`:** esperado de texto velho ("1 turno(s)"), da correção de plurais de 05/10. Atualizado; OK.

## 6. Commits

| Commit | Conteúdo |
|---|---|
| `0618788` | DECISOES (grau, com o Parecer citado), P8, esperados 4b–4e antes de implementar; título do DECISOES restaurado |
| o seguinte a ele | `grau_do_alerta`, esperado do `testes_entrada` |
| `ee7af24` | Equipe 10 + 20, 20/11, cortes esperados antes de rodar |
| `5a11be7` | Rodadas pela tela, guia, ESTADO |
| o seguinte | Este relatório |

---

## LEVAR PARA O PROJETO DE REDACAO

- **`DECISOES.md`:**
  - entrada nova "2026-10-05 — Grau da proporção: o grupo de pacientes de maior carga". Corrige a leitura de 29/09, cita a seção 3 do Parecer e os dois exercícios de Saúde Mental, e declara a divergência com o caminho por pacientes, que não muda;
  - título "Modelo de entrada" restaurado.
- **`PROPOSTAS.md`:** P8 nova, empate de carga entre grupos de pacientes. **Aguarda decisão.**
- **`ESTADO_ATUAL.md`:** nota de 05/10, 21h — demonstração refeita com a equipe 10 + 20; P8 em aberto.
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
