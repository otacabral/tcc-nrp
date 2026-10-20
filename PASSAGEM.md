# PASSAGEM — Orientação (ferramenta)

Atualizado em 20/10/2026. Lido primeiro pelo chat de Orientação; atualizado pelo Claude Code ao
fim de cada sessão (dele ou do chat).

## Onde paramos

- **3º bloco (19–20/10) feito, Partes 0 a 5** (`resultados/relatorio_2026-10-20.md`):
  pedidos e regras dos profissionais (tabela com importância por linha; turno fixo como "Só este
  turno"); máximo de dias seguidos do hospital (rígido, 1 a 6); tela limpa (sem Situação,
  rótulos Manhã/Tarde/Noite, numeração 1–5). Identidade com a v1.3.0: **243/243** depois de cada
  parte. Todos os testes rodados passaram; a Parte 3 (b) saiu diferente do esperado (abaixo).
- **Tag `v1.3.0` criada em 20/10. Versão citável: v1.3.0.** A `v1.4.0` ainda **não existe**:
  depende da suíte de fechamento, que é do Otávio.
- **Parte 3 (b), plantão de 12 h:** esperado "admite com 22"; saiu 22 inviável (provado) e
  escala legal com 23. Conta à mão: domingo só com turnos de 12 h ocupa 9 pessoas, que não podem
  trabalhar na segunda (36 h de descanso); a segunda pede 14; 22 − 9 = 13. **Consequência para o
  caso A: o quadro precisa cobrir a segunda-feira depois do fim de semana com plantão de 12 h.**
- `NUMEROS_TCC.md`: sem mudança neste bloco. Congelamento: **25/10**.
- Nada enviado ao GitHub desde 19/10.

## Próxima tarefa

**1. Otávio: suíte de fechamento da v1.4.0**, com o Claude Code e o Chrome fechados. No
PowerShell, da raiz, um comando por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    & "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v140.sh

Termina com "TUDO OK" ou "PARADO: ..." na última linha de
`resultados/v140_2026-10-20/suite/resumo.txt`. Se for interrompida (memória, queda), **retomar**
— pula o que já passou — com, um por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    $env:RETOMAR = "1"
    & "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v140.sh
    Remove-Item Env:RETOMAR

**Regra: se TUDO OK, tag v1.4.0** (marca a versão; um por linha):

    git tag -a v1.4.0 -m "v1.4.0: pedidos e regras dos profissionais, maximo de dias do hospital, tela"

Se "PARADO": não criar a tag; abrir o log indicado e trazer ao Claude Code.

**Envio ao GitHub** (quando quiser; envia os commits e as tags; um por linha):

    git push origin main
    git push origin v1.3.0
    git push origin v1.4.0

**2. Depois: caso realista A (Massens 2019)** com **24 pessoas (Anexo B inteiro)**, em **duas
rodadas**: (i) equipe fixa por turno ("Só este turno") em **Essencial**; (ii) rodízio livre (sem
as linhas). **Orçamento 60 min** cada. Antes, fazer a conta da segunda-feira depois do fim de
semana (Parte 3 b).

**3.** Caso B, orçamento 60 min. **4.** Sensibilidade com 2 ou 3 ordens de prioridade.
Congelamento dos números: **25/10**.

## Decisões da sessão de 19–20/10 (3º bloco)

- DECISOES: "Opção B: decisões 4 e 5" (5 aprovada; 4 substituída pela tela sem Situação);
  "Pedidos e regras por profissional" (MUDANÇA DE FORMULAÇÃO; revê 09/10); "Máximo de dias
  seguidos como regra do hospital"; "Tela orientada ao usuário". Testes da tela atualizados com
  registro: 1-2 (aba Prioridades) e opB-tela (Partes 2, 4 e 5).
- Leituras adotadas: relatório de 20/10, seção "Leituras adotadas" (9 itens).
- Achado: o avaliador oficial não pontua DayOn/ShiftOn (limite 0 no código do jar); a ferramenta
  só usa pedidos negativos, que ele pontua.

## Decisões da sessão de 19/10 (2º bloco)

- Opção B: níveis em sequência, fusão por coeficiente se o bloco fundido < 10.000; 1.800 s por
  nível e na etapa 2; orçamento 60 min editável; 13 critérios com campo, 3 "já garantido pela
  CLT"; habilidade alternativa e pedidos por turno/para trabalhar fora.
- Os testes da tela rodam com os limites da v1.2.3 (600/180/20 min); um teste confere os padrões
  novos.

## Decisões da sessão de 19/10 (1º bloco)

- Opção B registrada (aprovação do Ormeu, 14/10); orçamento configurável, padrão 60 min,
  registrado (implementar junto com a B; bateria, demonstração e números atuais ficam
  declarados "com orçamento de 20 min").
- Cronograma: ferramenta 19–25/10; números congelados em 25/10; só escrita 26/10–01/11;
  revisão do orientador 02–06/11; **entrega 06/11**. **P18 cortada.** P16 só se sobrar tempo.
- Limitações declaradas: domingo no art. 67 e art. 386; o contorno pelo pedido de folga depende
  da classificação na opção B.
- Documentos novos: `docs/diferencas_inrc_ferramenta.md`, `docs/pesos_inrc.md`.

## Decisões da sessão de 13/10

- **Art. 67 com horários editáveis** (`DECISOES.md`, 2026-10-13). Com turno editado na tela, a
  folga isolada podia dar menos de 24 h (N 23–07, folga, M 05–13 = 22 h) e a ferramenta
  entregava a escala como "admite escala legal".
  - (a) o modelo proíbe a folga isolada abaixo de 24 h (fonte única: o gerador de pares);
  - (b) se a conferência no relógio reprovar, erro em vermelho, sem escala, e a busca para;
  - a regra vale também com `--sem-descanso-clt`; o id do padrão segue `clt_36h_…`.
- A afirmação de 29/09 "o modelo garante o art. 67 por construção" ficou marcada como
  superada (vale só para os horários dos modelos prontos).
- P16, item novo (pedido da Orientação): veredito próprio para a escala reprovada na
  conferência, no lugar de "nao_decidido"; mesma frase e mesmo comportamento. Prioridade
  baixa; janela de 26–29/10.

## Decisões das sessões de 09 a 11/10

- v1.2.1: evidência citada versionada.
- v1.2.2: frase da tela quando a etapa 2 não melhora (caminho sem prova).
- Texto do TCC antecipado para 09/10.
- P17: diagnóstico só como teste, sem mexer na ferramenta. Resultado:
  - A (1800 s): melhora;
  - B (simetria, 180 s): sem melhora.
- P18 opção A; P19 registrada, com (d) "busca longa"; item novo na P16.
- 11/10, reorganização dos chats:
  - `PASSAGEM.md` criado;
  - `CLAUDE.md`, `LEIA_PRIMEIRO.md` e a seção 7 do `ESTADO_ATUAL.md` reescritos;
  - bloco final das respostas: "LEVAR PARA O CHAT DE ORIENTAÇÃO";
  - congelamento dos números em 16/10.

## Pendências com a Redação

- **3º bloco (20/10):** `GUIA_DE_USO.md` com a tabela "Pedidos e regras dos profissionais", o
  máximo de dias seguidos do hospital e a tela sem Situação; o texto não pode mais citar a coluna
  Situação nem "já garantido pela CLT" na tela. Fins de semana em 4 semanas = 2 é **valor de
  exemplo, sem fonte (suposição declarada)**, nunca valor do INRC. Nota para o texto: com nível
  sem prova, a prioridade entre níveis só é garantida nos provados. O avaliador oficial não
  pontua DayOn/ShiftOn (relatório de 20/10) — pode ir como limitação do benchmark.

- **Opção B (19/10, 2º bloco):** a função objetivo da ferramenta passa a ser por níveis
  escolhidos pelo gestor; o `GUIA_DE_USO.md` tem a seção nova; os números de antes ficam
  declarados "orçamento 20 min, 600 s / 180 s". Ainda sem tag (suíte incompleta).
- **19/10, prontos para leitura:** `docs/diferencas_inrc_ferramenta.md` (comparativo pedido
  pelo orientador; sem afirmar eficiência), `docs/pesos_inrc.md` (o INRC não tem um conjunto
  único de pesos: 41 instâncias só com peso 1, 28 com 1 a 10, e um 31 no `medium_late05`) e a
  especificação dos testes (`resultados/relatorio_2026-10-19.md`, seção 8; versões de Pyomo,
  Streamlit e Java das rodadas antigas não foram registradas).
- **Contagem de Santos:** x + y + w + r + z pela definição, sem as folgas α (limite inferior),
  tirada do fichamento; **conferir no artigo antes de ir ao texto**.
- **Validação por restrição:** os números só vão ao texto depois de o Otávio aprovar a seção 14
  proposta para o `NUMEROS_TCC.md`.
- **Limitações (19/10):** domingo no art. 67 e art. 386 registrados no `DECISOES.md`; o que
  falta (trabalho futuro? jurisprudência?) está listado lá.

- **Art. 67 (13/10):** onde o texto disser que o modelo garante o descanso semanal "por
  construção" ou pelos horários, trocar pela regra explícita: toda folga isolada ≥ 24 h, mais
  no máximo 6 dias seguidos (`DECISOES.md`, "2026-10-13 — Art. 67 com horários editáveis"). E
  a segunda proteção: escala que reprova na conferência no relógio não é entregue.

- **Seção 2.4.3:** gap de otimalidade, heurísticas primais no solver, HiGHS e por que ele
  (ferramenta gratuita). Fontes a conferir.
  - Material pronto: `DECISOES.md`, P17 item d, nota "para o referencial (2.4.3) e o método".
  - O que tem: o que é o sub-MIP do HiGHS 1.15.1; as três heurísticas que o usam (RENS, RINS,
    rootReducedCost); quando disparam; as opções `mip_heuristic_*` com os padrões.
  - Tudo com arquivo e linha na tag `v1.15.1` do ERGO-Code/HiGHS.
  - "Foi o RINS no K5" é inferência pelo código, não observação.
- **Limitação da P17:** números só da seção 13 do `NUMEROS_TCC.md`.
- **207 escalas heurísticas + 36 adversárias (18/09):** nem o script nem as escalas existem.
  - Busca feita em todo o histórico do git, nos arquivos apagados, em `historico/` e no disco.
  - Os números ficam como **registro histórico** (`DECISOES.md`, 18/09). **Não citar no
    capítulo de resultados** (`NUMEROS_TCC.md`, seção 1).
  - O método (conferir a semântica fora do modelo antes da função objetivo) pode ser descrito;
    a contagem não vai como resultado.

## Cronograma

- 19–25/10: modificações na ferramenta (opção B em 19/10; 3º bloco em 19–20/10; caso realista A a seguir).
- 20/10: reunião com o orientador.
- **Números congelados: 25/10** (substitui 16/10).
- 26/10–01/11: só escrita. 02–06/11: revisão do orientador.
- **Entrega: 06/11** (substitui 04/11).
- P18: cortada. P16: só se sobrar tempo.
