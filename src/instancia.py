"""Estruturas de dados de uma instancia do NRP. Sem Pyomo, sem XML.

Fronteira do projeto (PLANO.md): `modelo.py` consome apenas `Instancia`, nunca XML.
E o que permite a instancia brasileira entrar sem tocar no modelo.

Nomes dos atributos de restricao: mantidos iguais aos do esquema oficial, em snake_case
(`max_consecutive_working_days` e nao `max_dias_consecutivos`). O objetivo e rastreabilidade
— o mesmo nome aparece no XML, na documentacao da competicao e em Santos et al. (2016).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, timedelta

# indice = date.weekday(): 0 = segunda
DIAS_SEMANA = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# Os quatro valores admitidos pelo esquema, em indices de date.weekday()
DEFINICAO_FIM_DE_SEMANA = {
    "SaturdaySunday": (5, 6),
    "FridaySaturdaySunday": (4, 5, 6),
    "FridaySaturdaySundayMonday": (4, 5, 6, 0),
    "SaturdaySundayMonday": (5, 6, 0),
}

# Restricoes flexiveis de contrato, na ordem do esquema. O valor diz se a restricao tem
# limite numerico (OnAndWeight) ou e apenas logica (WeightOnly).
RESTRICOES = {
    "single_assignment_per_day": "logica",
    "max_num_assignments": "valor",
    "min_num_assignments": "valor",
    "max_consecutive_working_days": "valor",
    "min_consecutive_working_days": "valor",
    "max_consecutive_free_days": "valor",
    "min_consecutive_free_days": "valor",
    "max_consecutive_working_weekends": "valor",
    "min_consecutive_working_weekends": "valor",
    "max_working_weekends_in_four_weeks": "valor",
    "complete_weekends": "logica",
    "identical_shift_types_during_weekend": "logica",
    "no_night_shift_before_free_weekend": "logica",
    "two_free_days_after_night_shifts": "logica",
    "alternative_skill_category": "logica",
}


@dataclass(frozen=True)
class Flexivel:
    """Uma restricao flexivel de contrato, como lida do arquivo.

    `ligada` e o interruptor: o atributo `on=` nas restricoes que o tem, e o proprio
    conteudo booleano nas que so tem peso (ver DECISOES.md, 2026-09-15). Os campos guardam
    o dado bruto; `ativa` aplica a regra de ativacao adotada.
    """

    presente: bool
    ligada: bool
    peso: int
    valor: int | None = None

    @property
    def ativa(self) -> bool:
        """A restricao entra no modelo?

        Regra adotada em 2026-09-15: ligada E com peso maior que zero. O peso 0 anula a
        parcela por construcao no avaliador (apendice A da documentacao oficial), entao
        incluir a restricao nao mudaria o valor objetivo — so o tamanho do modelo.
        """
        return self.presente and self.ligada and self.peso > 0

    @classmethod
    def ausente(cls) -> "Flexivel":
        return cls(presente=False, ligada=False, peso=0, valor=None)


@dataclass(frozen=True)
class Turno:
    id: str
    inicio: time
    fim: time
    descricao: str
    habilidades: frozenset[str]

    @property
    def noturno(self) -> bool:
        """Atravessa a meia-noite. No INRC, o turno N vai de 22:30 a 06:30."""
        return self.fim <= self.inicio


@dataclass(frozen=True)
class EntradaPadrao:
    turno: str  # ID de turno, "Any" (qualquer turno) ou "None" (folga)
    dia: str    # "Any" ou nome do dia da semana


@dataclass(frozen=True)
class Padrao:
    """Sequencia indesejada. O peso esta no padrao, nao no contrato que o referencia."""

    id: str
    peso: int
    entradas: tuple[EntradaPadrao, ...]

    @property
    def tamanho(self) -> int:
        return len(self.entradas)

    @property
    def em_dia_fixo(self) -> bool:
        return any(e.dia != "Any" for e in self.entradas)


@dataclass(frozen=True)
class Contrato:
    id: str
    descricao: str
    weekend_definition: str
    padroes_indesejados: tuple[str, ...]
    single_assignment_per_day: Flexivel
    max_num_assignments: Flexivel
    min_num_assignments: Flexivel
    max_consecutive_working_days: Flexivel
    min_consecutive_working_days: Flexivel
    max_consecutive_free_days: Flexivel
    min_consecutive_free_days: Flexivel
    max_consecutive_working_weekends: Flexivel
    min_consecutive_working_weekends: Flexivel
    max_working_weekends_in_four_weeks: Flexivel
    complete_weekends: Flexivel
    identical_shift_types_during_weekend: Flexivel
    no_night_shift_before_free_weekend: Flexivel
    two_free_days_after_night_shifts: Flexivel
    alternative_skill_category: Flexivel

    @property
    def dias_fim_de_semana(self) -> tuple[int, ...]:
        return DEFINICAO_FIM_DE_SEMANA[self.weekend_definition]

    def restricoes(self) -> dict[str, Flexivel]:
        return {nome: getattr(self, nome) for nome in RESTRICOES}

    def ativas(self) -> dict[str, Flexivel]:
        return {n: r for n, r in self.restricoes().items() if r.ativa}


@dataclass(frozen=True)
class Profissional:
    id: str
    nome: str
    contrato: str
    habilidades: frozenset[str]


@dataclass(frozen=True)
class Pedido:
    """Pedido individual. Peso 0 existe nos dados e nao penaliza nada."""

    tipo: str  # folga_dia | folga_turno | trabalho_dia | trabalho_turno
    profissional: str
    data: date
    peso: int
    turno: str | None = None


@dataclass(frozen=True)
class FimDeSemana:
    """Um fim de semana do horizonte, ja recortado pelo inicio e fim do periodo."""

    indice: int
    datas: tuple[date, ...]
    completo: bool


@dataclass(frozen=True)
class Instancia:
    id: str
    arquivo: str
    inicio: date
    fim: date
    habilidades: tuple[str, ...]
    turnos: dict[str, Turno]
    padroes: dict[str, Padrao]
    contratos: dict[str, Contrato]
    profissionais: dict[str, Profissional]
    demanda: dict[tuple[date, str], int]   # (data, turno) -> quantidade exigida
    pedidos: tuple[Pedido, ...]
    # (profissional, dia) em que a pessoa nao pode ser escalada: ferias, licenca. RIGIDO, e
    # fora do formato do INRC — o parser nunca preenche, so a instancia brasileira.
    indisponiveis: frozenset[tuple[str, date]] = frozenset()

    # --- horizonte

    @property
    def dias(self) -> tuple[date, ...]:
        n = (self.fim - self.inicio).days + 1
        return tuple(self.inicio + timedelta(days=i) for i in range(n))

    @property
    def n_dias(self) -> int:
        return (self.fim - self.inicio).days + 1

    def indice(self, dia: date) -> int:
        """Posicao do dia no horizonte, contando de 0."""
        return (dia - self.inicio).days

    # --- demanda

    @property
    def demanda_total(self) -> int:
        return sum(self.demanda.values())

    def demanda_de(self, dia: date, turno: str) -> int:
        return self.demanda.get((dia, turno), 0)

    # --- habilidades

    def habilitados(self, turno: str) -> tuple[str, ...]:
        """Profissionais que tem todas as habilidades exigidas pelo turno."""
        exigidas = self.turnos[turno].habilidades
        return tuple(p.id for p in self.profissionais.values() if exigidas <= p.habilidades)

    def contrato_de(self, profissional: str) -> Contrato:
        return self.contratos[self.profissionais[profissional].contrato]

    # --- fins de semana

    def fins_de_semana(self, contrato: str) -> tuple[FimDeSemana, ...]:
        """Fins de semana do horizonte, segundo a definicao do contrato.

        Blocos maximos de dias consecutivos cujo dia da semana pertence a definicao. Um
        bloco recortado pelo inicio ou fim do horizonte vem com `completo=False` — o que
        fazer com fim de semana incompleto e decisao de modelagem, nao de leitura, e por
        isso fica para `modelo.py`. Nas 69 instancias do INRC nao ocorre.
        """
        dias_fds = set(self.contratos[contrato].dias_fim_de_semana)
        blocos, atual = [], []
        for d in self.dias:
            if d.weekday() in dias_fds:
                atual.append(d)
            elif atual:
                blocos.append(tuple(atual))
                atual = []
        if atual:
            blocos.append(tuple(atual))
        esperado = len(dias_fds)
        return tuple(
            FimDeSemana(indice=i, datas=b, completo=len(b) == esperado)
            for i, b in enumerate(blocos)
        )

    # --- pedidos

    @property
    def pedidos_ativos(self) -> tuple[Pedido, ...]:
        return tuple(p for p in self.pedidos if p.peso > 0)

    def pedidos_de(self, profissional: str) -> tuple[Pedido, ...]:
        return tuple(p for p in self.pedidos_ativos if p.profissional == profissional)

    # --- conferencia rapida

    def resumo(self) -> str:
        hab = {h: sum(1 for p in self.profissionais.values() if h in p.habilidades)
               for h in self.habilidades}
        return (f"{self.id}: {self.n_dias} dias ({self.inicio} a {self.fim}), "
                f"{len(self.profissionais)} profissionais, {len(self.turnos)} turnos, "
                f"{len(self.contratos)} contratos, {len(self.padroes)} padroes, "
                f"demanda {self.demanda_total}, habilidades "
                + ", ".join(f"{h}={n}" for h, n in hab.items())
                + f", pedidos {len(self.pedidos_ativos)} ativos de {len(self.pedidos)}")
