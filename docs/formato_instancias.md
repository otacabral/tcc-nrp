# O formato das instâncias do INRC-2010

Documento descritivo: o que é uma instância da competição, como o arquivo está organizado,
o que o formato faz de maneira contraintuitiva e qual é o perfil das 69 instâncias da pasta
`instancias/`.

Serve de matéria-prima para a seção do TCC que descreve os dados. **Não contém decisões de
modelagem** — essas ficam em `DECISOES.md`, e as que aguardam validação, em `PROPOSTAS.md`.
Aqui só entra o que é fato verificável no arquivo ou na documentação oficial.

Duas fontes:

- HASPESLAGH, S.; DE CAUSMAECKER, P.; STØLEVIK, M.; SCHAERF, A. *First International Nurse
  Rostering Competition 2010*. 5 maio 2010. Referida abaixo como "documentação oficial", com
  a seção entre parênteses. Cópia em `docs/nrpcompetition_description.pdf`.
- Varredura das 69 instâncias por `src/inspecionar.py`, 15/09/2026. Resultados em
  `docs/inventario_instancias.csv` e `docs/uso_elementos_opcionais.csv`.

---

## 1. O que é uma instância

Cada arquivo XML é um problema completo de escala: quem são os profissionais, quantos dias,
quantas pessoas precisam estar em cada turno e quais regras valem para cada um. Resolver
`long01.xml` significa montar uma escala de 28 dias para 49 profissionais que atenda toda a
demanda e desagrade o mínimo possível.

O documento oficial descreve o problema como a escala de **uma ala de hospital** (seção 2.1).
Cada instância também vem em formato texto, com o mesmo conteúdo; a solução pode ser
entregue em qualquer um dos dois.

## 2. Os blocos do arquivo

Raiz `SchedulingPeriod`, com dez blocos em ordem fixa. Os que importam:

**`StartDate` / `EndDate`** — o horizonte. Nas 69 instâncias são sempre 28 dias.

**`Skills`** — as habilidades existentes. No máximo duas: `Nurse` e `HeadNurse`.

**`ShiftTypes`** — os turnos, com horário e habilidade exigida. Em `long01`:

| ID | Horário | Habilidade |
|---|---|---|
| `E` | 06:30–14:30 | Nurse |
| `L` | 14:30–22:30 | Nurse |
| `D` | 08:30–16:30 | Nurse |
| `N` | 22:30–06:30 | Nurse |
| `DH` | 08:30–16:30 | HeadNurse |

`D` e `DH` têm horário idêntico e habilidade diferente. Isso não é acaso — ver a seção 4.

**`Patterns`** — sequências indesejadas, cada uma com peso. Uma entrada do padrão pode ser um
turno específico, `Any` (qualquer turno) ou `None` (folga), e pode valer para qualquer dia ou
para um dia da semana. Exemplo de `long01`: o padrão 2 é `None@Friday – Any@Saturday –
Any@Sunday`, isto é, folga na sexta seguida de trabalho no fim de semana.

**`Contracts`** — os pacotes de regras. Cada profissional segue exatamente um contrato. Cada
regra é uma linha com valor, ativação e peso:

```xml
<MaxConsecutiveWorkingDays on="1" weight="1">7</MaxConsecutiveWorkingDays>
```

No máximo 7 dias seguidos de trabalho; a regra vale nesta instância; cada dia de excesso
custa 1 ponto.

**`Employees`** — cada pessoa, com contrato e habilidades.

**`CoverRequirements`** — a demanda, por **dia da semana** (`DayOfWeekCover`, sete blocos),
não por data. O parser expande para as datas do horizonte.

**`DayOffRequests` / `ShiftOffRequests`** — pedidos individuais, cada um com peso.

## 3. Como o problema é pontuado

Duas restrições rígidas, e só duas (documentação oficial, 2.2.1):

1. toda a demanda deve ser coberta;
2. no máximo um turno por profissional por dia.

Todo o resto é flexível: pode ser violado, a um custo. O valor de uma escala é a soma das
penalidades, e o objetivo é minimizá-la. O apêndice A da documentação traz o pseudocódigo do
avaliador: cada penalidade é `custo × distância`, onde o custo é o peso declarado no arquivo
e a distância é o tamanho da violação — dias além do máximo, por exemplo. Restrições lógicas,
que só podem estar satisfeitas ou não, custam uma vez o peso.

Quando a Tabela 6 de Santos et al. (2016) diz que `long01` vale 197, significa: existe escala
que cobre toda a demanda com 197 pontos de penalidade, e nenhuma consegue menos.

O avaliador oficial da competição é um programa Java que lê a instância e a escala e devolve
esse número. É a única conferência externa disponível no trabalho.

## 4. Quatro particularidades do formato

**A habilidade está pregada no tipo de turno.** O bloco `<Cover>` aceita apenas o turno e a
quantidade; não existe elemento `<Skill>` na cobertura. Para exigir composição de equipe, a
competição cria um turno por par horário × habilidade — é o caso do `DH` de `long01`, mesmo
horário do `D`, exigindo `HeadNurse`, com cobertura própria de 2 nos dias úteis.

**`<Preferred>` é demanda obrigatória, não preferência.** O nome engana. A documentação
oficial declara a cobertura como restrição rígida (2.2.1), e Santos et al. modelam como
igualdade.

**O booleano das restrições sem `on=` faz o papel do interruptor.** No formato texto (3.1.2),
essas restrições aparecem como `CompleteWeekends (on|weight) (<boolean>|<int>)`: o campo que
no XML é o conteúdo do elemento chama-se, no texto, `on`. Portanto conteúdo `false` é
restrição desligada.

**A cobertura por data específica tem precedência.** A documentação (3.1) determina que
`DateSpecificCover` prevalece sobre `DayOfWeekCover`. Nenhuma instância do INRC usa esse
bloco, mas é o mecanismo oficial para demanda diferenciada em datas — feriados, por exemplo.

O turno noturno, por fim, atravessa a meia-noite (`N`, 22:30–06:30) e a documentação o trata
como pertencente a um dia; as restrições de dias consecutivos operam em dias.

## 5. Nomenclatura e contagem

Três tracks, nomeados a partir de provas olímpicas e definidos pelo tempo de resolução
concedido na competição: `sprint` (segundos), `medium` (minutos) e `long` (horas). Quatro
lotes, que são **momentos de divulgação**, não classes de dificuldade (Regra 7): *early*,
divulgado na abertura; *late*, duas semanas antes do fim; *hidden*, guardado para testar os
finalistas; e *hint*, exemplos avulsos que a documentação sequer menciona.

A pasta tem **69 arquivos**: as 60 instâncias da competição mais 9 do lote *hint*, três por
track. Santos et al. reportam as 60; as *hint* não têm valor de referência na Tabela 6.

Os arquivos do lote *early* não trazem sufixo: o que a literatura chama de `long_early01` é o
`long01.xml`. A coluna `nome_literatura` do inventário faz esse mapeamento.

## 6. Perfil das 69 instâncias

Horizonte de 28 dias em todas. Os lotes *early*, *late* e *hint* começam numa sexta
(2010-01-01); as *hidden* começam numa terça — o parser precisa derivar o dia da semana da
data, nunca supor.

| Track | Lote | n | Profissionais | Turnos | Contratos | Padrões | Demanda total | Habilidades |
|---|---|---|---|---|---|---|---|---|
| long | early | 5 | 49 | 5 | 3 | 3 | 740 | Nurse, HeadNurse |
| long | late | 5 | 50 | 5 | 3–4 | 9 | 740–752 | Nurse, HeadNurse |
| long | hidden | 5 | 50 | 5 | 3–4 | 9 | 632–752 | Nurse, HeadNurse |
| long | hint | 3 | 50 | 5 | 3 | 7–9 | 740 | Nurse, HeadNurse |
| medium | early | 5 | 31 | 4 | 4 | 0 | 608 | Nurse |
| medium | late | 5 | 30 | 4–5 | 3–4 | 0–7 | 416–452 | Nurse (e HeadNurse em `late05`) |
| medium | hidden | 5 | 30 | 5 | 4 | 9 | 440–488 | Nurse, HeadNurse |
| medium | hint | 3 | 30 | 4 | 3–4 | 7 | 428 | Nurse |
| sprint | early | 10 | 10 | 4 | 4 | 3 | 152 | Nurse |
| sprint | late | 10 | 10 | 3–4 | 3 | 0–8 | 144–160 | Nurse |
| sprint | hidden | 10 | 10 | 3–4 | 3 | 4–8 | 136–168 | Nurse |
| sprint | hint | 3 | 10 | 4 | 3 | 0–8 | 152 | Nurse |

Outras observações da varredura:

- **Pesos.** Apenas o lote *early* usa pesos uniformes 0/1. Os lotes *late*, *hidden* e *hint*
  usam pesos diferenciados por restrição — 3, 4, 5, 7 e 10, e 31 em três instâncias `medium`.
- **Habilidade é acumulativa.** Nenhum profissional, em nenhuma instância, tem `HeadNurse`
  sem ter também `Nurse`. Quem é chefe pode cobrir qualquer turno; o inverso não vale. Em
  `long01`, 6 dos 49; nas *late* e *hint*, 4 de 50; nas *hidden*, 2 de 50.
- **Pedidos.** Vinte instâncias não têm nenhum pedido de folga. Algumas trazem pedidos com
  peso 0, que não penalizam nada.
- **Instâncias irmãs.** As cinco *early* de um mesmo track compartilham profissionais, turnos
  e cobertura; diferem nos parâmetros dos contratos e nos pedidos. É o que explica `long01`
  valer 197 e `long02`, 219.
- **Utilização.** A razão entre demanda total e capacidade (profissionais × dias) fica entre
  0,45 e 0,60, exceto nas `medium_early`, que chegam a 0,70.

## 7. O que o esquema permite e as instâncias não usam

Relevante para o gerador da instância brasileira: tudo o que está abaixo é válido no esquema
oficial, então o avaliador aceita, mas não há exemplo no benchmark.

| Elemento | Uso nas 69 |
|---|---|
| `DateSpecificCover` | nenhuma |
| `DayOnRequests` / `ShiftOnRequests` (pedidos para trabalhar) | nenhuma |
| `TwoFreeDaysAfterNightShifts` | nenhuma |
| `OrganisationID` | nenhuma |
| `MaxWorkingWeekendsInFourWeeks` | presente em todas, porém `on="0"` em todos os 235 contratos |

Já presentes em todas as instâncias, embora opcionais no esquema: todos os demais elementos
de contrato, `WeekendDefinition`, `UnwantedPatterns`, as habilidades, o nome do profissional
e a descrição do turno. `Contract/Description` é obrigatório no esquema.

A definição de fim de semana admite quatro valores (`SaturdaySunday`,
`FridaySaturdaySunday`, `FridaySaturdaySundayMonday`, `SaturdaySundayMonday`); o benchmark só
usa os dois primeiros, e o segundo aparece apenas nos lotes *late*, *hidden* e *hint*.

Inventário completo, instância por instância, em `docs/uso_elementos_opcionais.csv`.
