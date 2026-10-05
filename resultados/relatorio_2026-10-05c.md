# Relatório de 05/10/2026 (c) — Partes A, B e C

## Para o Otávio

- **Parte A pronta.** O limite da etapa 2 na tela ficou em **180 s**. Na tela, a etapa 2 agora mostra a diferença de carga entre colegas em vez do gap. A P1 foi marcada como concluída. Testes e regressão OK.
- **Parte B parou:** o computador interrompeu a rodada pela tela por **falta de memória** (só 1,1 GB livres de 12 GB). Pela regra, não relancei. Os dados e o roteiro estão prontos e a captura da tela preenchida saiu. Os números da demonstração existem, rodados pelo mesmo motor sem a tela.
- **Parte C pronta:** textos da tela corrigidos, `GUIA_DE_USO.md` e figuras em `resultados/figuras/`.
- **O que você precisa fazer:** fechar programas pesados (abas do navegador, VS Code) e me pedir para relançar a rodada pela tela. Depois, rodar de novo os testes da tela que leem os textos corrigidos (lista no item 3.3).
- `git pull` traz tudo.

---

## 1. Parte A — limite e exibição da etapa 2

| Item | O que foi feito |
|---|---|
| 1. Limite da etapa 2 | max(120 s; 1,5 × 81,1 s = 121,7 s), arredondado para cima ao minuto: **180 s** (`ferramenta.TEMPO_ETAPA2`). A etapa 1 continua com 600 s. A etapa 2 usa o menor dos dois, porque os testes encurtam o limite da etapa 1 |
| 2. Exibição | Na tela e na planilha, a etapa 2 deixa de mostrar o gap. No lugar, aparece a **diferença máxima de carga entre colegas** por categoria, em plantões e horas ("1 plantão (8 h)"). O gap fica só para a etapa 1 |
| 3. P3 | Acrescentado: "parar a etapa 2 ao atingir o piso aritmético da amplitude", simples só com contrato e turno homogêneos e sem indisponibilidade |
| 4. P1 | Registrada a rodada com folga, com a leitura que você ditou. **Status: CONCLUÍDA** |

**Como a diferença entre colegas é calculada** (decisão de implementação, registrada no `DECISOES.md`, item i):
- para cada pessoa, horas escaladas − (fração média da categoria × horas devidas dela);
- o resultado é o maior desses valores menos o menor;
- com contrato e disponibilidade iguais, é a diferença de horas entre quem mais e quem menos trabalhou;
- com férias ou contratos diferentes, não pune quem deve menos horas.

No 9c, o esperado foi registrado antes de rodar: técnicos "1 plantão (8 h)" e enfermeiros "nenhuma (0 h)". **Acertou.**

**Testes (um por processo):**

| Teste | Resultado |
|---|---|
| 9 (9a–9d) | **Na primeira rodada, falhou só a parte "provado" do 9c**: a amplitude veio certa (4,55%), mas a etapa 2 não provou em 180 s. Eu estava instalando um pacote (Playwright) ao mesmo tempo. **Rodado de novo sozinho, passou inteiro**, com prova em 146,9 s. Fica a fragilidade: a folga até o limite é de 33 s nesta máquina |
| 7.2 | OK; etapa 2 em 181 s, sem prova (34,1 → 13,6 pp) |
| 8a–8d | OK |
| 1–2 | OK |
| `regressao.py --todos` | OK: 56, 58, 197, 219 = Tabela 6 |

Commit `579e47e`, enviado.

## 2. Parte B — demonstração de uso

### 2.1 O caso

Os dados ficam num lugar só: `docs/demonstracao/caso_clinica_medica.py`.

- **Unidade:** clínica médica, 12×36, de 02/11/2026 a 29/11/2026.
- **Equipe:** 8 enfermeiros e 22 técnicos, nomes fictícios. Oito pessoas com contrato de 36 h, o resto com 44 h.
- **Demanda:**
  - dias úteis: dia 2 + 6, noite 1 + 5 (enfermeiros + técnicos);
  - fim de semana: dia 1 + 5, noite 1 + 4;
  - feriados de 02/11 e 15/11: 1 + 4 nos dois turnos.
- **Férias:** Carla Nunes de 16 a 29/11; Karen Dias de 02 a 15/11.
- **Pedidos de folga:** 6.
- **COFEN:** 8 pacientes de cuidado mínimo, 14 intermediários e 4 de alta dependência.

### 2.2 Dimensionamento

Rodado sem a tela, pelo mesmo motor, com `caso_clinica_medica.py`:

| Equipe | Veredito | Diagnóstico | Alertas do COFEN |
|---|---|---|---|
| 8 + 22 = 30 (**rodada 1**) | **admite escala legal** | — | 1: 8 enfermeiros em 30, o Parecer pede 10 |
| 8 + 21 = 29 | admite escala legal | — | 2: proporção; quadro abaixo do QP completo (30,05) |
| 8 + 20 = 28 (**rodada 2**) | **falta 1; menor quadro viável 29** (9 + 20) | **combinação de regras** (o piso aritmético é 28; o solver provou 28 inviável) | 2: proporção; quadro abaixo do QP completo (30,10) |

**Rodada 1, números:**
- pedidos de folga atendidos: 6 de 6;
- turnos de enfermeiro em posto de técnico: 4;
- contrato cumprido: de 75% a 100%;
- diferença entre colegas: enfermeiros 0,5 plantão (6,4 h); técnicos 1,5 plantão (18,4 h);
- horas de contrato não utilizadas: 308 h dos enfermeiros e 184 h dos técnicos;
- descanso: cumpre;
- etapa 1 com ótimo provado; etapa 2 parou no limite de 180 s.

**Rodada 2, números da escala com 29:**
- pedidos: 6 de 6;
- turnos de enfermeiro em posto de técnico: 27;
- diferença entre colegas: enfermeiros 1 plantão (12 h); técnicos 0,6 plantão (6,9 h);
- horas não utilizadas: 208 h dos enfermeiros e 108 h dos técnicos;
- descanso: cumpre.

Estes números são de uma execução sem tela. **Não são os números "que aparecem na tela"** pedidos no item 5. A diferença entre colegas pode variar entre execuções, porque a etapa 2 roda com tempo limitado.

### 2.3 Pela tela — PARADO

**O roteiro** (`docs/demonstracao/capturas.py`) abre a tela no Chrome via Playwright e digita os dados do caso como um usuário faria:
- datas segmentadas;
- cargas escolhidas na lista da célula e conferidas lendo a célula depois;
- férias e pedidos em linhas novas;
- os feriados colados na grade de demanda por data;
- painel do COFEN.

Para funcionar, precisei contornar a tela, que perde o foco a cada atualização: o roteiro clica de novo e confere se o editor abriu.

**Pré-teste:** a tela preenchida foi conferida por captura e saiu certa: datas, nomes, cargas, férias, pedidos, demanda, feriados e COFEN.

**A rodada 1 completa foi interrompida pelo sistema por falta de memória.** Pela instrução, não relancei.
- Saiu só `docs/demonstracao/rodada1_entrada.png`, a tela preenchida antes de gerar.
- Na captura, as cargas visíveis estão certas, e as férias e os pedidos também. As linhas de Gabriela e Heitor não aparecem, mas cada carga foi conferida pelo roteiro lendo a célula depois de editar.
- **Faltam:** a captura do resultado da rodada 1, a planilha da rodada 1 e as duas capturas da rodada 2.

Encerrei o servidor do Streamlit que eu tinha aberto.

**Para relançar**, com memória livre:

```
streamlit run src\app.py --server.headless true --server.port 8599
python docs\demonstracao\capturas.py rodada1
python docs\demonstracao\capturas.py rodada2 --tec 20
```

O primeiro comando fica rodando numa janela; os outros dois vão em outra janela, com a .venv ativa. Cada rodada leva uns 10 min, a maior parte no preenchimento.

## 3. Parte C

### 3.1 Item 7 — textos da tela

Nada mudou no layout. Corrigido:

| Antes | Depois |
|---|---|
| "no grau intermediario, isto e, 10" | "no grau intermediário, isto é, 10" |
| "Faltam 1; o menor quadro viável é 40" | "Falta 1; ..." (com 2 ou mais, "Faltam") |
| "no máximo 1 dias seguidos" | "no máximo 1 dia seguido" |
| "faltam pelo menos 1 enfermeiro(s)" e similares no diagnóstico | "falta pelo menos 1 enfermeiro" / "faltam pelo menos 2 profissionais" |
| "N turno(s) sem enfermeiro", "em N profissional(is)" | plural certo |
| planilha: grau "intermediario" | "intermediário" |

As formas no singular e no plural saem de uma função só, `instancia_br.plural`.

**Testes que acompanham o texto:**
- o 2 espera "Falta 1";
- o 4 espera "isto é, 7";
- o 8c e o 8d procuravam a ausência de "Faltam". Com "Falta 1" no singular, essa busca passaria sem querer. Agora procuram "Falta", que pega as duas formas.

### 3.2 Item 9 — figuras

`src/figuras_tcc.py` gera tudo em `resultados/figuras/` a partir dos CSVs, sem número digitado à mão:
- `tab_p1_curva` (.csv, .md);
- `tab_p1_folga` (.csv, .md);
- `fig_p1_tempos_etapa1.png`;
- `fig_folga_amplitude.png`;
- `fig_folga_tempo_etapa2.png`;
- `legendas.md`.

As legendas descrevem a figura e dão a origem: arquivo, data de gravação, máquina tirada do log da rodada e solver tirado do CSV. O log do HiGHS não traz a versão, então a legenda diz "highspy 1.15.1 instalado ao gerar esta figura".

O `matplotlib==3.11.2` entrou no `requirements.txt`.

### 3.3 Conferências depois da Parte C

| Conferência | Resultado |
|---|---|
| 544 XML | idênticos byte a byte |
| Textos novos, conferidos sem solver | alerta do caso 4 com "isto é, 7" e "intermediário"; "Falta 1" / "Faltam 2"; os cinco diagnósticos contêm os trechos que o 7.3 espera |
| Testes da tela 1–2, 4, 7.3 e 8 depois da correção dos textos | **não rodaram**: 1,1 GB livres, e os testes com solver já tinham sido interrompidos. **Pendente** |
| `regressao.py` | não precisa: o modelo não mudou na Parte C. Rodou depois da Parte A |

### 3.4 Item 8 — guia de uso

`GUIA_DE_USO.md` na raiz, com link no README. Tem:
- o que a ferramenta faz e não faz (a lista do "não faz" vem da especificação);
- instalação no Windows passo a passo;
- como abrir;
- cada seção da tela;
- os três desfechos, os alertas do COFEN, os cinco motivos do diagnóstico, os números e a planilha;
- o exemplo da clínica médica.

O exemplo usa os números da execução sem tela, e o guia diz isso explicitamente. Quando a rodada pela tela sair, os números e as capturas entram lá.

## 4. Commits

| Commit | Conteúdo |
|---|---|
| `579e47e` | Parte A |
| `9d81c5f` | Parte C (textos, figuras) e scripts da demonstração |
| o seguinte | Guia, README, ESTADO_ATUAL, captura da entrada da rodada 1, este relatório |

---

## LEVAR PARA O PROJETO DE REDACAO

- **`PROPOSTAS.md`**:
  - P1 marcada como **CONCLUÍDA**, com a leitura da rodada com folga: a melhor escala sai cedo, o resto do tempo vai na prova, e a amplitude coincide com o piso aritmético (conta feita depois; é explicação, não previsão). Limite da etapa 2 em 180 s.
  - P3: trabalho futuro novo, parar a etapa 2 no piso aritmético.
- **`DECISOES.md`**, "Carga por contrato", **item i)** novo:
  - limite da etapa 2 em 180 s;
  - a etapa 2 sem gap, com a diferença de carga entre colegas;
  - a definição dessa diferença.
- **`ESTADO_ATUAL.md`**: notas de 05/10 — P1 concluída, demonstração interrompida, textos corrigidos com testes pendentes, guia e figuras.
- `VIRADA_ESCOPO_2026-09-24.md`: sem mudança.
