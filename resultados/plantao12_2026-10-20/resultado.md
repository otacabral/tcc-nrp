# Parte 3 — plantão de 12 h no fim de semana: resultado (20/10/2026)

Esperado: `ESPERADO.md` nesta pasta. Orçamento 20 min; HiGHS 1.15.1. Tempo é limite operacional, não resultado.

- (a) aceita o 4º turno e a demanda 0: sim
- (b) veredito: Falta 1; o menor quadro viável é 23. Escala gerada. (tentativas [(22, 'inviavel', 4, 18), (23, 'viavel', 5, 18)]; caminho fundido; provado True; gap 0.0)
- (c) depois de um D12, menor descanso até o turno seguinte da mesma pessoa: 36.0 h; abaixo de 36 h: 0 []
- (d) conferência de descanso: cumpre (menor entre turnos 12 h; máximo de dias seguidos 6)
- (e) D12 em dia útil: 0 (D12 no fim de semana: 40)
- enfermeiro em posto de técnico: 15; contrato cumprido 17%–92%
- FALHOU

## Análise (depois de rodar)

**(b) não saiu como o esperado:** o esperado era "admite com 22"; a ferramenta provou o 22
inviável (solver, ótimo provado) e entregou escala legal com **23** ("Falta 1"). A conta de horas
do esperado (3.024 h contra 3.872 h) não via a trava, que é de **dias**, não de horas. Conta à mão
que a explica sozinha:
- todo turno de domingo é de 12 h (D12 5 + N 4 = **9** pessoas), e depois de turno de 12 h vêm 36 h
  de descanso: **ninguém que trabalhou domingo trabalha segunda**;
- segunda pede M 5 + T 5 + N 4 = **14** pessoas;
- com 22, sobram 22 − 9 = **13** para a segunda → falta 1. Com 23, sobram 14.

O diagnóstico da tela não tem conta para isso (a alternância do 12×36 só é testada quando
*todos* os turnos são de 12 h), por isso o caso não mostra "por que" além do resultado do solver.
Fica como observação: a mesma conta vale para qualquer segunda depois de um domingo só com
plantões de 12 h — é o que o caso A precisa saber ao escolher o quadro.

**`pares_proibidos_por_horario` trata certo o D12 entre turnos de 6 h:** a lista gerada é a da
conta à mão (ESPERADO.md), e a medição na escala (c) confirma: o menor descanso depois de um D12
foi exatamente 36 h (sábado 19h → segunda 7h), nenhum abaixo.

(a), (c), (d), (e): como o esperado.
