# Passeio guiado: de um clique em "Gerar escala" até a planilha

Para quem **não programa**. Cada passo diz onde está (arquivo e função), o que entra, o que sai e por que existe. Linhas conferidas na `v1.0.1` (commit `35a9cd1`).

---

## 1. O clique

**`src/app.py`, linha 182** (`st.button("Gerar escala")`). A tela é um formulário do Streamlit. Quando você clica, o Streamlit roda o arquivo `app.py` de novo, de cima a baixo, sabendo que o botão foi apertado.

- **Entra:** tudo o que está nos campos (turnos, equipe, cargas, férias, pedidos, demanda, pacientes).
- **Sai:** um pacote único com esses dados, a `Entrada` (`src/ferramenta.py`, classe `Entrada`, linha ~68).
- **Por que existe:** separa a tela da conta. A tela só junta os dados; quem decide é a `ferramenta.py`.

## 2. Conferir a entrada antes de gastar tempo

**`app.py`, linhas 186–207** → **`ferramenta.montar`** (linha 187). Monta a instância uma vez, só para ver se a entrada faz sentido: turno repetido, nome que não existe, data fora do mês, início que não cai numa segunda.

- **Sai:** a instância, ou uma mensagem vermelha "Entrada inválida: …".
- **Por que existe:** um erro de digitação aparece em um segundo, e não depois de minutos de cálculo.

## 3. A barra de progresso e a chamada principal

**`app.py`, linhas 209–213**: cria a barra (`st.progress`) e chama **`ferramenta.verificar`** (linha 618), que faz todo o trabalho. A cada quadro testado, `verificar` atualiza a barra com "testando quadro de N profissionais" (linha 639).

**Durante o cálculo a tela mostra só essa barra e essa frase.** Não há relógio nem estimativa de quanto falta; isso é a proposta P12.

## 4. O que `verificar` calcula antes do solver

**`ferramenta.verificar`, linhas 618–635:**
- **alertas do COFEN** (`instancia_br.alertas_cofen`): proporção de enfermeiros e quadro de pessoal. Só avisam;
- **CHS e QP** do Parecer, se houver pacientes;
- **o piso** (`ferramenta.piso`, linha 230): o menor quadro que a aritmética admite, por horas e, no 12×36, pela soma de dois dias seguidos.

**Por que existe:** quadro abaixo do piso é inviável **por conta**. Não vale gastar solver com ele.

## 5. A busca do menor quadro

**Linhas 637–664.** Começa no quadro informado e sobe de um em um, até **12 acima** (`MARGEM`, linha 50). Para cada tamanho:

1. **Abaixo do piso:** marca "inviável pela aritmética" e passa ao próximo, sem solver (linha 640).
2. **Monta até duas equipes candidatas** (linhas 643–648):
   - a composição da regra (`ferramenta.equipe`: primeiro enfermeiros, até o que os postos de enfermeiro e a proporção pedem; depois técnicos);
   - se a primeira for inviável, a mesma com todos os acréscimos como enfermeiros. Enfermeiro cobre tudo o que técnico cobre: se nem essa fecha, nenhuma composição daquele tamanho fecha.
3. **Resolve cada candidata** com `resolver_com_objetivo` (passo 6).
4. **Viável** → para a busca; esse é o menor quadro.
5. **Inviável provado** → tenta a próxima candidata ou o próximo tamanho.
6. **Sem resposta no tempo, ou erro** → **para a busca** (linha 663): sem prova, não dá para dizer que um quadro maior é o menor.

**Resoluções por tamanho:** no máximo 2 candidatas, cada uma com a etapa 1 e, se a etapa 1 provar o ótimo, a etapa 2.

**Quando a busca para:**
- no primeiro quadro viável;
- no primeiro "sem resposta" ou erro;
- ou depois de 13 tamanhos (o informado e mais 12).

**Tempo máximo teórico de um clique** (contas sobre os limites, não medição): cada etapa 1 pode levar até 600 s e cada etapa 2 até 180 s.
- O pior caso são 13 tamanhos com duas candidatas cada, todas provadas inviáveis perto do limite: 13 × 2 × 600 s = 15.600 s.
- Somando 600 + 180 s do quadro final, dá cerca de **16.400 s, uns 4 h 30 min**.
- Na prática a busca para muito antes, porque a prova de inviabilidade costuma ser rápida ou o primeiro "sem resposta" encerra.

## 6. Uma resolução: as duas etapas

**`ferramenta.resolver_com_objetivo`, linhas 442–481.**

**Etapa 1** (`pesos`, linha 277, e `experimento_a.modelo_br`):
- monta o modelo com as regras da CLT **rígidas**;
- o objetivo é: cada pedido de folga negado custa W, cada turno de enfermeiro em posto de técnico custa 1. W é maior que a soma de todos os postos de técnico, então negar pedido nunca compensa;
- resolve com o HiGHS (`ferramenta.resolver`, linha 297; `modelo.resolver`), com limite de **600 s** (`TEMPO`).

**Etapa 2** (`equilibrar`, linha 319):
- só roda se a etapa 1 provou o ótimo;
- fixa a penalidade nesse ótimo e minimiza a diferença de carga entre colegas da mesma categoria;
- limite de **180 s** (`TEMPO_ETAPA2`, linha 465).

**O veredito de cada resolução** sai do estado do solver (`experimento_a.classificar`):
- "inviável" com prova;
- "viável", com escala (provada ótima ou não);
- "indeterminado", sem escala no tempo;
- "erro", quando o solver levantou exceção ou disse que tinha escala mas não a entregou. Na tela aparece como "o solver falhou".

## 7. Conferir a escala por fora

**`verificar`, linhas 655–660**: com escala na mão, `ferramenta.medir` e `cumpre` medem o descanso **no relógio**, a partir dos horários: entre turnos, semanal, dias seguidos. É a conferência independente (`docs/conferencia_descanso_escala.py`), que não confia nas listas do modelo.

`ferramenta.indicadores` calcula os números da tela (pedidos atendidos, enfermeiro em posto de técnico, frações do contrato, horas não utilizadas).

## 8. Se faltou gente: o diagnóstico

**Linha 666** → **`ferramenta.diagnosticar`** (linha 594). Se o quadro informado foi provado inviável, pela conta ou pelo solver, procura **todas as contas simples** que provam isso (`motivos_da_trava`): horas, alternância do 12×36, categoria, dia específico. Se nenhuma explica, mostra "combinação de regras".

## 9. A tela mostra o resultado

**`app.py`, linhas 215–298**, nesta ordem:
- o veredito (verde, amarelo ou vermelho, conforme `Resultado.frase`);
- a caixa do diagnóstico;
- os alertas do COFEN;
- os números;
- a linha da diferença entre colegas;
- os pedidos;
- o QP;
- "Como o veredito foi obtido": a lista de quadros tentados e o veredito de cada um.

## 10. A planilha

**`app.py`, linhas 299–300** → **`ferramenta.planilha`** (linha 686). Monta o `.xlsx` com três abas:
- **Escala:** profissional × dia; `*` = posto de enfermeiro; "indisp." = férias;
- **Resumo:** veredito e números;
- **Legenda:** horário de cada código.

O botão "Baixar planilha (.xlsx)" entrega o arquivo.
