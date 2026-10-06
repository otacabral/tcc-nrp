# Relatório de 05/10/2026 (g)

## Para o Otávio

- **P8 registrada como decidida:** no empate de carga, a ferramenta avisa e usa o maior percentual. É escolha da ferramenta, não regra do Parecer. Não houve mudança de código.
- **A divergência do caminho por pacientes não afeta nenhum resultado** (item 2). Ficou registrado no DECISOES.
- **Congelamento das funcionalidades antecipado para 05/10.** Até 10/10, só correção de defeito, com o esperado registrado antes.
- Nada a executar. `git pull` traz os registros.

## 1. P8

Entrada nova no DECISOES: "2026-10-05 — Empate de carga entre grupos de pacientes (fecha a P8)". A P8 está marcada como decidida no PROPOSTAS. O código não mudou; o teste do empate continua sendo o 4e.

## 2. Divergência do caminho por pacientes

Verificado sem alterar nada.

**a) Os 4 XML.** São os de `pacientes_*` da conferência (`docs/conferencia_xml_experimentos.py`): 8 h e 12×36, com e sem razão de fim de semana.
- **Os 4 têm graus misturados:** 10 pacientes de cuidado mínimo e 12 intermediários.
- **Em nenhum as duas leituras dão percentual diferente.**
  - Leitura de 29/09 (`grau_de_maior_carga`): intermediário, 33%. Os dois graus empatam em 33%, e a ordem da tabela desempata.
  - Leitura de 05/10 (`grau_do_alerta`): intermediário, 33%, pela carga (72 h contra 40 h).
- Mesmo grau e mesmo percentual.

**b) Números que vão ao texto.** Nenhum vem do caminho por pacientes:
- o Experimento A monta cada instância com um grau só (`experimento_a.py`, `br.construir(grau=...)`);
- a escalabilidade usa `grau="intermediario"`;
- a P1 e a demonstração usam o caminho de turnos configurados;
- as tabelas e figuras de `resultados/figuras/` saem dos CSVs da P1.

O caminho por pacientes só aparece nos 4 XML da conferência e nos testes de entrada.

Como nenhum número muda, ficou registrado no DECISOES, na entrada "2026-10-05 — Grau da proporção": a divergência existe e não afeta resultado.

## 3. Congelamento

- **DECISOES:** entrada nova "2026-10-05 — Congelamento das funcionalidades antecipado para 05/10".
- **ESTADO_ATUAL, seção 2 (datas):** 10/10 riscado e trocado por 05/10, com a regra (só correção de defeito, com esperado registrado antes).
- O congelamento de resultado numérico (14/10) e a entrega (04/11) não mudaram.

---

## LEVAR PARA O PROJETO DE REDACAO

- **`DECISOES.md`**:
  - entrada nova "Empate de carga entre grupos de pacientes", que fecha a P8;
  - entrada nova "Congelamento das funcionalidades antecipado para 05/10";
  - na entrada "Grau da proporção", parágrafo novo: a divergência com o caminho por pacientes não afeta resultado.
- **`PROPOSTAS.md`**: P8 marcada como decidida.
- **`ESTADO_ATUAL.md`**: seção 2 com o congelamento em 05/10; P8 marcada como decidida.
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
