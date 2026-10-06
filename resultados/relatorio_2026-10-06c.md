# Relatório de 06/10/2026 (c)

## Para o Otávio

- **Padrão das 36 h:** a opção (a) foi registrada no DECISOES, e a P13 está fechada no histórico.
- **`validar.py` corrigido.** Os defeitos estavam lá desde 15/09, mas nenhum resultado registrado passou por ele, porque ele nunca conseguia devolver um número. As cinco conferências agora dão 56, 58, 197, 219 e 224, como esperado.
- **`medium_late05` descrito** para comparar com a instância da demonstração (item 3).
- **P9 registrada:** não fechar o `medium_late05` antes de 04/11; vai para trabalhos futuros.
- Nada a executar. `git pull` traz tudo.

## Item 1 — Padrão das 36 h: FEITO

- **DECISOES.md**, entrada nova "2026-10-06 — Padrão das 36 h fica no XML (opção (a) da P13)". Ela diz que é uma decisão registrada em 06/10 sobre um comportamento que o código já aplicava antes de 23/09.
  - Motivo: a (b) alteraria os 544 XML e exigiria refazer os experimentos.
  - Nas instâncias brasileiras, as 36 h são conferidas por medição direta do descanso, não pelo avaliador.
- **P13**, no `historico/escopo-comparacao-regimes/PROPOSTAS.md`: status "FECHADA em 06/10", com apontamento para a entrada.
- Commit `f020e74`.

## Item 2 — `src/validar.py`: FEITO

### a) Antes de corrigir

**Desde quando:** os dois defeitos estão no arquivo desde a criação. `git blame` mostra as linhas 33–34, 56 e 94 todas no commit `603d1f7` (15/09, "Sessão 3: encanamento validado no avaliador oficial"), sem mudança depois. Os defeitos:
1. classpath só com o `evaluator.jar` (linha 56): `NoClassDefFoundError: org/dom4j/DocumentException`;
2. `-p` depois dos arquivos (linha 94): "Syntax error". O README já avisava desde 15/09 que o `-p` tem de vir antes.

Um terceiro ponto apareceu ao testar: caminho absoluto com contrabarra é recusado pelo avaliador ("Invalid file path").

**Algum resultado registrado como conferido pelo avaliador passou por ele? Não.** Por isso não parei.
- O número do avaliador é lido só da chamada com `-p`. Quebrada, ela sai `None` ("não interpretado"), e o script acusa FALHA. **O `validar.py` nunca pôde devolver um número**, nem certo nem errado.
- Nenhum script do repositório importa o `validar.py`. Os que gravam conferências chamam o Java direto, do jeito certo (`-cp avaliador/*`, sem `-p` depois dos arquivos):
  - `src/experimento_a.py` (linha 196);
  - `docs/conferencia_piso_forcado.py` (linha 58);
  - `docs/conferencia_padrao_avaliador.py` (linha 61).
- **Única origem não documentada:** a coluna `avaliador_oficial` do `resultados/consolidado.csv` (commit `4fde6c3`, 18/09), com 56, 58, 197, 219 e 716. Nenhum script a escreve, e o `validar.py`, como estava, não teria produzido esses números.
- Hoje, em 06/10, os quatro primeiros foram reconfirmados pelo `validar.py` corrigido (abaixo).

### b) Esperado

Registrado e commitado antes de corrigir (commit `f020e74`): 56, 58, 197, 219 nas escalas ótimas da regressão (`resultados/*_completo.xml`, de 22/09) e 224 na do `medium_late05`.

### c) Correção e conferências

Correção como no README:
- classpath `avaliador/*`;
- `-p` antes dos arquivos;
- caminhos com barra normal.

Commit `e9e0da4`. Registrado no DECISOES como correção de defeito.

| Instância | Escala | Avaliador | Modelo | Resultado |
|---|---|---|---|---|
| sprint01 | `resultados/sprint01_completo.xml` | 56 | 56 | OK |
| sprint02 | `resultados/sprint02_completo.xml` | 58 | 58 | OK |
| long01 | `resultados/long01_completo.xml` | 197 | 197 | OK |
| long02 | `resultados/long02_completo.xml` | 219 | 219 | OK |
| medium_late05 | `resultados/medium_late05_2026-10-06/medium_late05_escala.xml` (caminho absoluto com contrabarra, de propósito) | 224 | 224 | OK |

## Item 3 — `medium_late05`, lido do arquivo: FEITO

**Equipe e horizonte:**
- **30 profissionais**, **28 dias** (01/01/2010 a 28/01/2010).
- **Contratos:** `fulltime` (15 pessoas), `75_time` (10) e `50_percent` (5). Um quarto contrato, `night`, não tem ninguém.
- **Habilidades:** 27 só `Nurse`; 3 com `HeadNurse` e `Nurse`.
- **Pedidos de folga:** 390, sendo 300 por turno e 90 por dia.

**5 tipos de turno**, todos de 8 h:

| Turno | Horário | Habilidade |
|---|---|---|
| E | 06:30–14:30 | Nurse |
| D | 08:30–16:30 | Nurse |
| DH | 08:30–16:30 | HeadNurse |
| L | 14:30–22:30 | Nurse |
| N | 22:30–06:30 | Nurse |

**Restrições flexíveis ativas, com peso, por contrato** (valor entre parênteses quando há). Fim de semana = sábado e domingo nos quatro contratos.

| Restrição | fulltime | 75_time | 50_percent | peso |
|---|---|---|---|---|
| máximo de atribuições | 18 | 14 | 8 | 3 |
| mínimo de atribuições | 10 | 6 | 4 | 3 |
| máximo de dias seguidos de trabalho | 5 | 4 | 4 | 4 |
| mínimo de dias seguidos de trabalho | 3 | 2 | 3 | 4 |
| máximo de folgas seguidas | 4 | 5 | 6 | 7 |
| mínimo de folgas seguidas | 2 | 3 | 4 | 3 |
| máximo de fins de semana seguidos trabalhados | 3 | 3 | 3 | 5 |
| mínimo de fins de semana seguidos trabalhados | 2 | 2 | 2 | 5 |
| fim de semana completo | sim | sim | sim | 10 |
| mesmo turno no fim de semana | sim | sim | sim | 10 |
| sem noturno antes de fim de semana livre | sim | sim | sim | 10 |
| habilidade alternativa | sim | sim | sim | 10 |
| padrões indesejados | 7 | 7 | 7 | 1 cada |
| um turno por dia | sim | sim | sim | 1 |

- **Ressalva:** "sem noturno antes de fim de semana livre" está ligada, mas fica fora do objetivo do modelo, porque o avaliador oficial não a pontua (decisão de 18/09).
- Ao todo, 15.320 variáveis e 13.060 restrições no modelo.

**Para comparar com a demonstração, que é outra coisa:**
- a clínica tem 30 pessoas em 12×36, com 2 turnos de 12 h;
- regras da CLT **rígidas** (descanso entre turnos e semanal, alternância);
- carga contratual em horas;
- só os pedidos de folga são flexíveis.

No `medium_late05`, quase tudo é flexível e tem peso.

## Item 4 — P9: FEITO

**`PROPOSTAS.md`**, P9 nova, "fechar o `medium_late05`": decidida, não executar antes de 04/11.
- **Motivo:** o gap vem do limite inferior fraco (63 contra 107). Fechar exigiria formulação reforçada ou solver comercial.
- **A validação já se apoia** nos 4 ótimos provados e na concordância em 224.
- Entrou na P3 como trabalho futuro.
- Commit `ec05f46`.

---

## LEVAR PARA O PROJETO DE REDACAO

- **`DECISOES.md`**:
  - entrada nova "Padrão das 36 h fica no XML (opção (a) da P13)";
  - entrada nova "Correção de defeito: `src/validar.py` não conseguia chamar o avaliador", com o defeito, a verificação de que nenhum resultado passou por ele, o esperado e o resultado (56, 58, 197, 219, 224).
- **`PROPOSTAS.md`**:
  - P9 nova (fechar o `medium_late05`: não executar; vai para trabalhos futuros);
  - P3 com o item "Fechar o `medium_late05`".
- **`historico/escopo-comparacao-regimes/PROPOSTAS.md`**: P13 fechada, com apontamento para o DECISOES.
- `ESTADO_ATUAL.md` e `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
