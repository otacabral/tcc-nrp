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
- **Grau de dependência predominante.** É o grau da maioria dos pacientes. Serve para o
  alerta da proporção de enfermeiros.
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

Quando falta gente, aparece uma caixa com **o motivo mais simples** que explica a falta:

| Motivo | Exemplo do que quer dizer |
|---|---|
| **Horas** | As horas da demanda passam do que a equipe pode trabalhar pelos contratos. |
| **Alternância do plantão de 12 h** | Ninguém faz dois plantões de 12 h em dias seguidos. Por isso, dois dias seguidos precisam de pessoas diferentes. |
| **Categoria** | Faltam enfermeiros para os postos que só enfermeiro cobre. |
| **Dia específico** | Num dia, com férias e licenças, sobram menos pessoas do que postos. |
| **Combinação de regras** | Nenhuma conta simples explica. As regras juntas (descanso, dias seguidos, férias) é que impedem. |

### Os números do resultado

| Na tela | O que é |
|---|---|
| Quadro da escala | Quantas pessoas a escala usa. |
| Turnos de enfermeiro em posto de técnico | Quantas vezes um enfermeiro cobriu vaga de técnico. |
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
- 8 enfermeiros e 22 técnicos, 30 pessoas. Nomes fictícios.
- 8 pessoas com contrato de 36 h; o resto com 44 h.
- Férias: Carla Nunes de 16 a 29/11; Karen Dias de 02 a 15/11.
- Seis pedidos de folga.

**A demanda.**
- Dias úteis: de dia, 2 enfermeiros e 6 técnicos; à noite, 1 e 5.
- Fim de semana: de dia, 1 e 5; à noite, 1 e 4.
- Feriados (02/11, Finados; 15/11, Proclamação da República): 1 enfermeiro e 4 técnicos em
  cada turno.

**Pacientes (painel do COFEN).** 8 de cuidado mínimo, 14 intermediários e 4 de alta
dependência.

**Rodada 1 — a equipe de 30.**
- Veredito: **"O quadro informado admite escala legal. Escala gerada."**
- Um alerta do COFEN: 8 enfermeiros em 30, quando o Parecer pede 10 no grau intermediário.
- Todos os 6 pedidos de folga atendidos.
- 4 turnos de enfermeiro em posto de técnico.
- Conferência de descanso: cumpre.
- Diferença máxima de carga entre colegas: 0,5 plantão (6,4 h) entre enfermeiros e
  1,5 plantão (18,4 h) entre técnicos.
- Horas de contrato não utilizadas: 308 h dos enfermeiros e 184 h dos técnicos.

**Rodada 2 — a mesma unidade com 20 técnicos (28 pessoas).**
- Veredito: **"Falta 1; o menor quadro viável é 29."** O 29º profissional entra como
  enfermeiro.
- Diagnóstico: **combinação de regras**. Pela conta simples, 28 pessoas bastariam. As regras
  juntas — descanso, dias seguidos e as duas férias — é que impedem.
- Os alertas do COFEN passam a ser dois: a proporção de enfermeiros e o quadro abaixo do QP
  completo do Parecer.

> **Situação deste exemplo em 05/10/2026.** Os números acima vêm do mesmo motor da tela, rodado
> por `docs/demonstracao/caso_clinica_medica.py`, com os mesmos dados. A rodada pela tela,
> com capturas e planilha, foi interrompida pelo computador por falta de memória. A captura da
> tela preenchida está em `docs/demonstracao/rodada1_entrada.png`. A diferença de carga entre
> colegas pode variar um pouco de uma rodada para outra, porque o equilíbrio tem tempo
> limitado.
