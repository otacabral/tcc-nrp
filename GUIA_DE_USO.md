# Guia de uso — Escala de enfermagem

Este guia é para quem vai **usar** a ferramenta: enfermeira coordenadora, gestor de unidade,
quem monta a escala do mês. Não precisa saber programar.

---

## 1. O que a ferramenta faz

Você informa a unidade, a equipe e quantas pessoas precisa em cada turno. A ferramenta
devolve:

- **se a equipe dá conta** de uma escala que cumpre as regras de descanso da CLT;
- **a escala** de 28 dias, para baixar em planilha (.xlsx);
- **se não dá conta**, o motivo e o **menor quadro** com que daria;
- **alertas do COFEN** (Parecer Normativo nº 1/2024): proporção de enfermeiros e quadro de
  pessoal. Os alertas só avisam; não impedem a escala.

Entre todas as escalas legais, ela escolhe esta, nesta ordem:

1. a que atende o maior número de pedidos de folga;
2. a que põe menos enfermeiros cobrindo posto de técnico;
3. a que divide a carga de forma mais parecida entre colegas da mesma categoria.

As regras que **nunca** são quebradas:

- descanso entre turnos;
- descanso semanal;
- dias seguidos de trabalho;
- carga contratual de cada pessoa;
- férias e licenças.

## 2. O que a ferramenta **não** faz

- Não refaz a escala durante o mês por causa de faltas ou mudança de demanda.
- Não trata mais de uma unidade ao mesmo tempo, nem turnos partidos.
- Não calcula férias, ausências (IST), educação permanente nem enfermeiros gerenciais. Ela
  mostra o quadro da fórmula do COFEN, mas a escala cobre só a assistência.
- Não gera escala por mês civil: são sempre **28 dias, começando numa segunda-feira**.
- Não calcula custo de pessoal nem se liga a ponto eletrônico ou folha de pagamento.
- Quando a equipe não basta, não mostra onde faltaria gente. Ela informa só o menor quadro
  com que a escala fecha.
- Não trata habilidades além de enfermeiro e técnico.
- Não confere a virada de um período para o seguinte. Cada escala de 28 dias é feita
  sozinha.
- Não afirma conformidade jurídica. Os parâmetros do COFEN entram como valores declarados.

---

## 3. Como instalar no Windows

Você faz isto **uma vez só**.

**Passo 1 — Instale o Python.**
1. Entre em <https://www.python.org/downloads/> e baixe o Python 3.11 ou mais novo.
2. Na primeira tela do instalador, **marque "Add python.exe to PATH"** e clique em
   "Install Now".

**Passo 2 — Baixe a ferramenta.**
1. Entre em <https://github.com/otacabral/tcc-nrp>.
2. Clique no botão verde **"Code"** e depois em **"Download ZIP"**.
3. Descompacte o arquivo numa pasta, por exemplo `C:\escala`.

**Passo 3 — Prepare a pasta.**
1. Abra a pasta `C:\escala\tcc-nrp-main` no Explorador de Arquivos.
2. Clique na barra de endereço, digite `powershell` e aperte Enter. Abre uma janela azul ou
   preta.
3. Nessa janela, copie e cole os comandos abaixo, **um de cada vez**, apertando Enter depois
   de cada um:

```
python -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- O segundo comando pode pedir confirmação. Responda `S`.
- O último comando baixa os componentes e leva alguns minutos.

## 4. Como abrir

Toda vez que for usar:

1. Abra o PowerShell na pasta da ferramenta, como no Passo 3.
2. Digite os dois comandos abaixo:

```
.\.venv\Scripts\Activate.ps1
streamlit run src\app.py
```

O navegador abre sozinho na ferramenta. Se não abrir, digite `http://localhost:8501` na barra
de endereço.

**Para fechar:** feche a aba do navegador e, na janela do PowerShell, aperte `Ctrl + C`.

---

## 5. Como preencher

A tela é uma página só, de cima para baixo.

### 1. Configuração da unidade

- **Modelo de turnos.** Escolha um dos três:
  - 12×36: 7h–19h e 19h–7h;
  - 8 h em três turnos;
  - 6 h de dia mais noturno de 12 h.

  Na tabela logo abaixo você pode mudar o nome e o horário dos turnos, sempre em hora cheia.
- **Fim de semana.** Sábado e domingo, ou sexta a domingo.
- **Grau de dependência predominante.** Serve para o alerta da proporção de enfermeiros,
  **só quando você não informa os pacientes** no painel do COFEN. Com pacientes informados, a
  ferramenta usa o grau do grupo de pacientes de maior carga, como manda o Parecer, e diz qual
  usou.
- **Início.** Tem de ser uma **segunda-feira**. A escala cobre 28 dias a partir dela.

### 2. Equipe

- **Enfermeiros** e **Técnicos e auxiliares.** Quantas pessoas de cada categoria.
- **Nomes (opcional).** Um nome por linha. Sem nomes, aparecem "Enf 1", "Téc 1" etc.
- **Carga semanal.** Para cada pessoa, 30, 36, 40 ou 44 h. O padrão é 44 h. A carga vale
  sobre o período inteiro, não semana a semana, e já desconta férias.
- **Férias e licenças.** Clique na linha vazia da tabela para acrescentar uma linha. Escolha a
  pessoa e as datas de início e fim. Nesses dias a pessoa **não** é escalada.
- **Pedidos de folga.** Mesma coisa: a pessoa e o dia. A ferramenta tenta atender, mas um
  pedido nunca impede a escala.

### 3. Demanda

- Para cada turno, quantos **enfermeiros** e quantos **técnicos** precisam estar trabalhando.
- Marque **"Fim de semana com demanda própria"** se o fim de semana pede outro número.
- **Demanda específica por data** (feriados, eventos): abra a seção e mude só os dias
  diferentes. A tabela já vem preenchida com a demanda acima.

### 4. Conferir com o COFEN (opcional)

- Informe a **média diária de pacientes** em cada grau de dependência.
- A ferramenta calcula o quadro de pessoal do Parecer e compara com a sua equipe. Isso não
  muda a escala.

Ao final, clique em **"Gerar escala"**. Uma barra mostra o andamento.

**Quanto tempo leva:**
- cada quadro testado leva até 10 minutos para a escala e até 3 minutos para equilibrar a
  carga;
- se a equipe não bastar, a ferramenta testa quadros maiores, até 12 pessoas a mais.

---

## 6. Como ler o resultado

### O veredito: três desfechos

| O que aparece | O que quer dizer |
|---|---|
| **"O quadro informado admite escala legal. Escala gerada."** (verde) | A equipe dá conta. A escala está pronta. |
| **"Falta 1; o menor quadro viável é 29. Escala gerada."** (amarelo) | A equipe informada não dá conta. A escala mostrada é a do menor quadro que dá. A ferramenta acrescenta as pessoas e diz quantas. |
| **"Não foi possível gerar a escala no tempo disponível."** (vermelho) | A ferramenta não achou escala no tempo. Isso **não** prova que falta gente; pode ser só tempo. Tente de novo ou simplifique a entrada. |

**"Pode haver uma melhor (gap ...)".** Às vezes aparece depois de "Escala gerada". A escala é
legal, mas o tempo acabou antes de provar que é a melhor. O gap é a distância máxima até a
melhor possível.

### Alertas do COFEN (em vermelho)

Começam com "Alerta COFEN (não impede a escala)". Exemplos:

- "8 enfermeiros em 30 profissionais; o Parecer pede ao menos 33% no grau intermediário, isto
  é, 10";
- "quadro de 28 abaixo do QP completo do Parecer".

A escala continua valendo. Os alertas são para a sua decisão.

### Por que não há escala legal (o diagnóstico)

Quando falta gente, aparece uma caixa com **todos os motivos simples** que explicam a falta,
cada um com os números. Cada motivo, sozinho, já prova que não há escala:

| Motivo | Exemplo do que quer dizer |
|---|---|
| **Horas** | As horas de técnico passam do que os técnicos podem trabalhar mais a folga dos enfermeiros. O limite de cada pessoa é a carga contratual nos dias disponíveis e, no 12×36, a alternância: no máximo um plantão a cada dois dias. |
| **Alternância do plantão de 12 h** | Ninguém faz dois plantões de 12 h em dias seguidos. Por isso, dois dias seguidos precisam de pessoas diferentes, e quem está de férias nos dois dias não conta. |
| **Categoria** | Faltam enfermeiros para os postos que só enfermeiro cobre (em horas, ou num par de dias seguidos). |
| **Dia específico** | Num dia, com férias e licenças, sobram menos pessoas do que postos. |
| **Combinação de regras** | Nenhuma conta simples explica. As regras juntas (descanso, dias seguidos, férias) é que impedem. |

### Os números do resultado

| Na tela | O que é |
|---|---|
| Quadro da escala | Quantas pessoas a escala usa. |
| Enfermeiro em posto de técnico | Quantos turnos um enfermeiro cobriu em vaga de técnico. |
| Pedidos de folga atendidos | Quantos dos pedidos foram atendidos. |
| Contrato cumprido (mín.–máx.) | Quanto do contrato cada pessoa cumpre: horas escaladas ÷ horas contratadas nos dias em que está disponível. |
| Conferência de descanso | "cumpre" quer dizer que a escala foi medida no relógio e respeita os descansos da CLT. |
| Diferença máxima de carga entre colegas | Por categoria. Por exemplo, "1 plantão (12 h)": entre dois colegas da mesma categoria, a diferença de carga é de no máximo um plantão, já descontadas férias e contratos diferentes. |
| Horas de contrato não utilizadas | Por categoria: horas contratadas menos horas escaladas. |
| Diferença entre categorias | Quanto, em média, técnicos e enfermeiros cumprem do contrato. A ferramenta não tenta igualar isso: depende de quantos postos de cada categoria a demanda pede. |

### A planilha

Clique em **"Baixar planilha (.xlsx)"**. Ela tem três abas:

- **Escala:** uma linha por pessoa e uma coluna por dia.
  - O código é o turno.
  - Turno com **asterisco** (`D*`, `N*`) é posto de enfermeiro.
  - "indisp." é férias ou licença.
- **Resumo:** o veredito e todos os números acima.
- **Legenda:** horário de cada código.

---

## 7. Um exemplo completo

Os dados estão em `docs/demonstracao/caso_clinica_medica.py`.

**A unidade.** Clínica médica com plantões de 12×36 (7h–19h e 19h–7h). Escala de
**02/11/2026** a 29/11/2026.

**A equipe.**
- 10 enfermeiros e 20 técnicos, 30 pessoas — a proporção 33/67 do Parecer no grau
  intermediário. Nomes fictícios.
- 8 pessoas com contrato de 36 h; o resto com 44 h.
- Férias: Carla Nunes de 16 a 29/11; Karen Dias de 02 a 15/11.
- Seis pedidos de folga.

**A demanda.**
- Dias úteis: de dia, 2 enfermeiros e 6 técnicos; à noite, 1 e 5.
- Fim de semana: de dia, 1 e 5; à noite, 1 e 4.
- Feriados (02/11, Finados; 15/11, Proclamação da República; 20/11, Consciência Negra):
  1 enfermeiro e 4 técnicos em cada turno.

**Pacientes (painel do COFEN).** 8 de cuidado mínimo, 14 intermediários e 4 de alta
dependência. O grupo de maior carga é o intermediário (14 × 6 h = 84 h por dia, contra 32 h e
40 h), e é ele que vale para a proporção de enfermeiros.

**Rodada 1 — a equipe de 30.**
- Veredito: **"O quadro informado admite escala legal. Escala gerada."**
- Nenhum alerta do COFEN.
- Todos os 6 pedidos de folga atendidos.
- 24 turnos de enfermeiro em posto de técnico: os técnicos não dão conta de todos os postos
  de técnico, e os enfermeiros cobrem a diferença.
- Conferência de descanso: cumpre.
- Diferença máxima de carga entre colegas: 1 plantão (12 h) entre enfermeiros e
  0,6 plantão (6,9 h) entre técnicos.
- Horas de contrato não utilizadas: 432 h dos enfermeiros e 108 h dos técnicos.

**Rodada 2 — a mesma unidade com técnicos a menos.**

| Técnicos (quadro) | Veredito na tela | Enf. em posto de técnico | Alertas do COFEN |
|---|---|---|---|
| 19 (29) | "O quadro informado admite escala legal. Escala gerada." | 36 | 1: quadro abaixo do QP completo (29,85) |
| 18 (28) | **"Falta 1; o menor quadro viável é 29. Escala gerada."** | 34 (na escala de 29, com 10 enfermeiros e 19 técnicos) | 1: quadro abaixo do QP completo (29,70) |

Com 18 técnicos, a caixa do diagnóstico diz:

> **Por que não há escala legal com 28: Alternância do plantão de 12 h.** Com plantões de 12 h
> ninguém trabalha dois dias seguidos (a folga depois do plantão é de 36 h). ter 03/11 e qua
> 04/11 somam 28 plantões, que precisam de 28 pessoas diferentes; descontadas férias e
> licenças, 27 pessoas estão disponíveis em pelo menos um dos dois dias. Pela conta, falta pelo
> menos 1 pessoa.

As capturas da tela e as planilhas estão em `docs/demonstracao/`:
- `rodada1_*`;
- `rodada2_19tec_*`;
- `rodada2_18tec_*`.

Também estão lá o roteiro que preenche a tela e a conta feita antes de rodar,
`cortes_esperados.md`.
