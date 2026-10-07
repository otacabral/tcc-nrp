"""Parte A3c: o modelo da etapa 1 da ferramenta com UMA regra relaxada, sem mexer em src/.

As regras legais rigidas do modelo brasileiro sao tres familias (`modelo.RIGIDAS_LEGAIS_BR`):
`max_num_assignments`, `max_consecutive_working_days` e `unwanted_patterns`. Relaxar uma
delas = remontar o modelo com a familia FORA das rigidas: ela continua no modelo, mas
penalizada, como no INRC. O teto de horas e uma restricao propria (`carga_horaria`), que se
desativa.

O descanso SEMANAL nao tem restricao propria no modelo: ele vem do limite de 6 dias seguidos
(`max_consecutive_working_days`) e e conferido depois, no relogio. "sem descanso semanal" e
"sem limite de 6 dias" sao, no modelo, a mesma remocao.
"""

from __future__ import annotations

import modelo

REGRAS = {
    "sem_6_dias": "max_consecutive_working_days",     # = sem descanso semanal no modelo
    "sem_descanso_entre_turnos": "unwanted_patterns",
    "sem_max_atribuicoes": "max_num_assignments",
    "sem_teto_horas": None,
}


def montar(inst, custo, regra: str | None):
    rigidas = set(modelo.RIGIDAS_LEGAIS_BR)
    if regra and REGRAS[regra]:
        rigidas.discard(REGRAS[regra])
    m = modelo.construir(inst, flexiveis=True, habilidade_rigida=True,
                         noite_antes_de_fds_livre=True, rigidas_legais=frozenset(rigidas),
                         custo_atribuicao=custo)
    if regra == "sem_teto_horas" and hasattr(m, "carga_horaria"):
        m.carga_horaria.deactivate()
    return m
