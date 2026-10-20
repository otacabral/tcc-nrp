# PASSAGEM — Orientação (ferramenta)

Atualizado em 20/10/2026 (tarde). Lido primeiro pelo chat de Orientação; atualizado pelo Claude Code ao
fim de cada sessão (dele ou do chat).

## Onde paramos

- **Versão citável: v1.4.0** (suíte TUDO OK em `resultados/v140_2026-10-20/suite/resumo.txt`; tag
  criada e enviada pelo Otávio com main e v1.3.0). A tag v1.4.0 não se mexe.
- **Sessão de 20/10 (tarde), Partes 0, 1 e 7 a 11** (`resultados/relatorio_2026-10-20c.md`):
  - Parte 0: o `git status` já estava limpo; nada a descartar. O `pedidos_avaliador.py` (e o
    `validar.py`) regravam em CRLF — só registrado.
  - Parte 1: DECISOES "a posteriori: fundamento das 36 h para qualquer plantão de 12 h ou mais".
  - **Parte 7 — piso por pares de dias (vira v1.4.1)**: a ferramenta recusa sem solver os quadros
    que dois dias seguidos já provam insuficientes. Caso A (36 h): piso 18 → **30**; caso B (36 h):
    68 → **105**, veredito "Não há escala legal até 101…" pela conta, sem solver. Sob D12 = 11 h a
    conta não recusa nem A (24) nem B (89). Nenhum quadro viável recusado em 224 rodadas
    registradas; sorteio pequeno 40/40 (semente 20261020). Entrada do solver 243/243 idêntica à
    v1.4.0.
  - Parte 8: `fechar_v141.sh` pronto e testado sem solver. Parte 9: `rodar_fase2.sh` pronto e
    testado sem solver; ESPERADO de A e B atualizados. Parte 10: MAPA_CODIGO.
- **A v1.4.1 ainda não existe**: depende da suíte, que é do Otávio.
- `NUMEROS_TCC.md`: sem mudança. Congelamento dos números: **25/10**.
- Nada enviado ao GitHub nesta sessão.

## Próxima tarefa

**1. Otávio: suíte de fechamento da v1.4.1.** Com o Claude Code e o Chrome fechados. No
PowerShell, da raiz, um comando por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    & "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v141.sh

Termina com "TUDO OK" ou "PARADO: ..." na última linha de
`resultados/v141_<data>/suite/resumo.txt` (a data do dia em que começou). Se for interrompida
(memória, queda), **retomar** — pula o que já passou e continua na mesma pasta —, um por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    $env:RETOMAR = "1"
    & "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v141.sh
    Remove-Item Env:RETOMAR

Diferença esperada e já admitida: na a2, o P05 tem o quadro 14 recusado pela conta (antes, pelo
solver). Qualquer outra diferença é falha.

**2. Se TUDO OK: tag v1.4.1 e envio** (um por linha; a tag marca a versão, o push manda os
commits e a tag ao GitHub):

    git tag -a v1.4.1 -m "v1.4.1: piso por pares de dias"
    git push origin main
    git push origin v1.4.1

Se "PARADO": não criar a tag; abrir o log indicado e trazer ao Claude Code.

**3. Depois da tag: fase 2** (cinco rodadas, até 60 min cada; termina com "TUDO OK" ou
"PARADO: ..." em `resultados/fase2_<data>/resumo.txt`). Um por linha:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    & "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/rodar_fase2.sh

Retomar, se interrompida:

    cd D:\dev\tcc-nrp
    .\.venv\Scripts\Activate.ps1
    $env:RETOMAR = "1"
    & "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/rodar_fase2.sh
    Remove-Item Env:RETOMAR

Ordem: A36_livre, A36_fixo, A11_fixo, B11_livre, B36_livre. As de 11 h saem como
`HIPOTESE_SENSIBILIDADE_*` — hipótese de sensibilidade, não regra da ferramenta. Antes de cada
rodada o script lê a memória livre; abaixo de 3 GB, para ("PARADO: menos de 3 GB livres") —
fechar programas e retomar. "Não decidido" não é falha. Esperados: os `ESPERADO.md` de
`resultados/caso_a_2026-10-20/` e `caso_b_2026-10-20/` (seção "Depois da Parte 7").

Sensibilidade com 2 ou 3 ordens de critérios: **sem proposta até a decisão do Otávio**.
Congelamento dos números: **25/10**.

## Worktrees de leitura (D:\dev)

`D:\dev\tcc-nrp-v123`, `D:\dev\tcc-nrp-v130` e `D:\dev\tcc-nrp-v140` são **worktrees de leitura**
(cópias da v1.2.3, v1.3.0 e v1.4.0 para as conferências de identidade). Ninguém trabalha nelas;
o Claude Code só abre `D:\dev\tcc-nrp`. As da v1.2.3 e v1.3.0 têm cópias de scripts de identidade
deixadas pelas suítes antigas, por isso o `--force`. Para removê-las **depois da entrega**, da
raiz, um por linha:

    cd D:\dev\tcc-nrp
    git worktree remove --force ..\tcc-nrp-v123
    git worktree remove --force ..\tcc-nrp-v130
    git worktree remove --force ..\tcc-nrp-v140

(apaga só as pastas; as tags e o histórico ficam).

## Decisões de 20/10 (tarde)

- DECISOES "2026-10-20 — a posteriori: fundamento das 36 h para qualquer plantão de 12 h ou mais"
  (art. 59 e 59-A; justificativa nova; convenção coletiva não lida; o texto não afirma
  descumprimento: "a regra, como modelada, segue o art. 59-A").
- DECISOES "2026-10-20 — Piso por pares de dias (v1.4.1)".
- Leitura registrada: técnico nunca cobre posto de enfermeiro (habilidade rígida; o critério
  "habilidade alternativa" não entra no modelo da ferramenta); por isso a conta só de
  enfermeiros existe e a só de técnicos não.
- Item extra (só leitura): 53 quadros provados inviáveis pelo solver nas rodadas registradas; a
  conta nova recusa 34. As contas do diagnóstico (horas por categoria, dia específico,
  alternância com férias) não entram no piso — registrado, **sem proposta** (decisão da
  Orientação).

## Decisões de 20/10 (Parte 6)

- DECISOES "2026-10-20 — a posteriori: descanso depois do D12 como parâmetro de pesquisa": o
  produto mantém 36 h; `DESCANSO_POR_TURNO` (vazio por padrão, fora da tela) só para experimento
  rotulado. Testado: padrão 243/243 com a v1.3.0; D12 = 11 h libera D12 → M no dia seguinte, a noite
  continua 36 h; o relógio acompanha o gerador. O texto não afirma que o hospital descumpre a lei.

## Decisões de 20/10 (fase 1 do caso A)

- Diagnóstico "combinação": "A conta prévia do menor quadro provou…" quando foi o piso
  (`DECISOES.md`, 2026-10-20). Entrada do solver idêntica (243/243).
- Achado de leitura: a regra das 36 h vale por **duração** (≥ 12 h), registrada em "2026-09-29 —
  Redesenho da ferramenta" com base no art. 59-A; **não há motivo registrado** para aplicá-la a um
  plantão de 12 h avulso (D12) fora do regime 12×36. Não é editável sem código.

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

- **20/10 (tarde):** (1) fundamento das 36 h: a frase admitida é "a regra, como modelada, segue o
  art. 59-A" — nunca "o hospital descumpre"; a convenção coletiva do caso não foi lida. (2) Na
  v1.4.1 o diagnóstico tem o motivo novo "Dois dias seguidos" (a conta da segunda-feira depois
  do fim de semana com plantão de 12 h); o `GUIA_DE_USO.md` ainda não o cita. (3) A conta prévia
  é condição necessária e compartilha a regra de descanso com o modelo: confere a aritmética,
  não a lei. Números da fase 2 só depois das rodadas.

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
