"""Leitura das instancias do INRC-2010: XML -> Instancia.

Uso como biblioteca:

    from parser import ler_instancia, descobrir_instancias
    inst = ler_instancia("instancias/long/long/long01.xml")

Uso como conferencia (na raiz do repositorio, com a .venv ativa):

    python src\\parser.py

Roda as conferencias obrigatorias do PLANO.md e compara, instancia por instancia, o que o
parser leu com o que a varredura da Sessao 1 registrou em docs/inventario_instancias.csv.
As duas leituras foram escritas em separado, entao divergencia entre elas aponta erro em uma
das duas.

O que este modulo decide, e por que (ver DECISOES.md):

- restricao flexivel conta se estiver ligada e com peso > 0; nas restricoes sem atributo
  `on=`, o conteudo booleano e o interruptor;
- `<Preferred>` e demanda obrigatoria, nao preferencia;
- `DayOfWeekCover` e expandido para as datas do horizonte, e `DateSpecificCover` tem
  precedencia sobre ele;
- pedidos com peso 0 sao lidos e preservados; quem filtra e `Instancia.pedidos_ativos`.
"""

from __future__ import annotations

import csv
import re
import sys
from datetime import date, time
from pathlib import Path

from lxml import etree

from instancia import (
    DIAS_SEMANA,
    RESTRICOES,
    Contrato,
    EntradaPadrao,
    Flexivel,
    Instancia,
    Padrao,
    Pedido,
    Profissional,
    Turno,
)

RAIZ = Path(__file__).resolve().parents[1]
DIR_INSTANCIAS = RAIZ / "instancias"
XSD_ENTRADA = RAIZ / "docs" / "scheme_input.xsd"
CSV_INVENTARIO = RAIZ / "docs" / "inventario_instancias.csv"

LOTES_VALIDOS = ("early", "late", "hidden", "hint")

# nome do elemento no XML -> nome do atributo em Contrato
ELEMENTO_DE = {
    "SingleAssignmentPerDay": "single_assignment_per_day",
    "MaxNumAssignments": "max_num_assignments",
    "MinNumAssignments": "min_num_assignments",
    "MaxConsecutiveWorkingDays": "max_consecutive_working_days",
    "MinConsecutiveWorkingDays": "min_consecutive_working_days",
    "MaxConsecutiveFreeDays": "max_consecutive_free_days",
    "MinConsecutiveFreeDays": "min_consecutive_free_days",
    "MaxConsecutiveWorkingWeekends": "max_consecutive_working_weekends",
    "MinConsecutiveWorkingWeekends": "min_consecutive_working_weekends",
    "MaxWorkingWeekendsInFourWeeks": "max_working_weekends_in_four_weeks",
    "CompleteWeekends": "complete_weekends",
    "IdenticalShiftTypesDuringWeekend": "identical_shift_types_during_weekend",
    "NoNightShiftBeforeFreeWeekend": "no_night_shift_before_free_weekend",
    "TwoFreeDaysAfterNightShifts": "two_free_days_after_night_shifts",
    "AlternativeSkillCategory": "alternative_skill_category",
}


# ---------------------------------------------------------------------------
# Descoberta dos arquivos
# ---------------------------------------------------------------------------

def descobrir_instancias(dir_instancias: Path = DIR_INSTANCIAS) -> tuple[list[dict], list[str]]:
    """Lista as instancias com track e lote derivados dos diretorios.

    track = 1o nivel abaixo de instancias/; lote = 2o nivel. Subpasta com o mesmo nome do
    track = lote "early"; as demais seguem <track>_<lote>_xml. Niveis extras abaixo do 2o
    (sprint_hidden_xml/sprint_hidden_xml/) sao tolerados. Ignora __MACOSX e arquivos
    iniciados por "._" (residuo AppleDouble com extensao .xml falsa). O lote tambem e
    derivado do nome do arquivo, e as duas leituras sao conferidas.

    Devolve (instancias, avisos). Cada instancia e um dict com track, lote, numero,
    nome_literatura (o nome usado na Tabela 6 de Santos et al.), arquivo e caminho.
    """
    achados, avisos = [], []
    for caminho in sorted(dir_instancias.rglob("*.xml")):
        rel = caminho.relative_to(dir_instancias)
        if "__MACOSX" in rel.parts or caminho.name.startswith("._"):
            continue
        if len(rel.parts) < 3:
            avisos.append(f"fora da estrutura track/lote: {rel.as_posix()}")
            continue

        track, pasta_lote = rel.parts[0], rel.parts[1]
        if pasta_lote == track:
            lote = "early"
        else:
            lote = re.sub(rf"^{re.escape(track)}_", "", pasta_lote)
            lote = re.sub(r"_xml$", "", lote)
        if lote not in LOTES_VALIDOS:
            avisos.append(f"lote desconhecido '{lote}': {rel.as_posix()}")

        m = re.fullmatch(r"([a-z]+)(?:_([a-z]+))?(\d+)", caminho.stem)
        if not m:
            avisos.append(f"nome fora do padrao: {rel.as_posix()}")
            numero, lote_nome, track_nome = "", "?", "?"
        else:
            track_nome, lote_nome, numero = m.group(1), m.group(2) or "early", m.group(3)
        if (track_nome, lote_nome) != (track, lote):
            avisos.append(f"pasta diz {track}/{lote}, nome diz "
                          f"{track_nome}/{lote_nome}: {rel.as_posix()}")
        if len(rel.parts) > 3:
            avisos.append(f"nivel extra de diretorio (tolerado): {rel.as_posix()}")

        achados.append({
            "track": track,
            "lote": lote,
            "numero": numero,
            "nome_literatura": f"{track}_{lote}{numero}",
            "arquivo": rel.as_posix(),
            "caminho": caminho,
        })
    return achados, avisos


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------

def _txt(el, caminho: str, padrao: str = "") -> str:
    alvo = el.find(caminho)
    return alvo.text.strip() if alvo is not None and alvo.text else padrao


def _hora(texto: str) -> time:
    h, m, s = (int(p) for p in texto.split(":"))
    return time(h, m, s)


def _flexivel(contrato_el, elemento: str) -> Flexivel:
    """Le uma restricao flexivel preservando o dado bruto.

    Nas restricoes do tipo OnAndWeight o interruptor e o atributo `on=` e o conteudo e o
    limite numerico. Nas do tipo WeightOnly nao ha atributo `on=`: o interruptor e o proprio
    conteudo booleano, conforme o formato texto da documentacao oficial, secao 3.1.2, que
    descreve esses elementos como `(on|weight) (<boolean>|<int>)`.
    """
    el = contrato_el.find(elemento)
    if el is None:
        return Flexivel.ausente()
    peso = int(el.get("weight", 0))
    conteudo = (el.text or "").strip()
    if el.get("on") is not None:
        return Flexivel(presente=True, ligada=el.get("on") in ("1", "true"),
                        peso=peso, valor=int(conteudo) if conteudo else None)
    return Flexivel(presente=True, ligada=conteudo == "true", peso=peso, valor=None)


def _cobertura(raiz, inicio: date, fim: date) -> dict[tuple[date, str], int]:
    """Expande a cobertura para as datas do horizonte.

    `DayOfWeekCover` traz 7 blocos, um por dia da semana. `DateSpecificCover` tem
    precedencia sobre ele (documentacao oficial, secao 3.1) — nenhuma instancia do INRC usa
    esse bloco, mas o esquema permite e a instancia brasileira pode precisar.
    """
    por_dia_semana: dict[str, dict[str, int]] = {}
    for bloco in raiz.iterfind("CoverRequirements/DayOfWeekCover"):
        dia = _txt(bloco, "Day")
        por_dia_semana.setdefault(dia, {})
        for cov in bloco.iterfind("Cover"):
            pref = cov.find("Preferred")
            por_dia_semana[dia][_txt(cov, "Shift")] = int(pref.text) if pref is not None else 0

    por_data: dict[str, dict[str, int]] = {}
    for bloco in raiz.iterfind("CoverRequirements/DateSpecificCover"):
        d = _txt(bloco, "Date")
        por_data.setdefault(d, {})
        for cov in bloco.iterfind("Cover"):
            pref = cov.find("Preferred")
            por_data[d][_txt(cov, "Shift")] = int(pref.text) if pref is not None else 0

    demanda: dict[tuple[date, str], int] = {}
    dia = inicio
    while dia <= fim:
        especifica = por_data.get(dia.isoformat())
        cobertura = especifica if especifica is not None else por_dia_semana.get(
            DIAS_SEMANA[dia.weekday()], {})
        for turno, qtd in cobertura.items():
            demanda[(dia, turno)] = qtd
        dia += __import__("datetime").timedelta(days=1)
    return demanda


def _pedidos(raiz) -> tuple[Pedido, ...]:
    pedidos = []
    blocos = (
        ("DayOffRequests/DayOff", "folga_dia", False),
        ("ShiftOffRequests/ShiftOff", "folga_turno", True),
        ("DayOnRequests/DayOn", "trabalho_dia", False),
        ("ShiftOnRequests/ShiftOn", "trabalho_turno", True),
    )
    for caminho, tipo, com_turno in blocos:
        for el in raiz.iterfind(caminho):
            pedidos.append(Pedido(
                tipo=tipo,
                profissional=_txt(el, "EmployeeID"),
                data=date.fromisoformat(_txt(el, "Date")),
                peso=int(el.get("weight", 0)),
                turno=_txt(el, "ShiftTypeID") if com_turno else None,
            ))
    return tuple(pedidos)


def validar_xsd(caminho: Path | str) -> list[str]:
    """Valida contra docs/scheme_input.xsd. Lista vazia = valido."""
    esquema = etree.XMLSchema(etree.parse(str(XSD_ENTRADA)))
    doc = etree.parse(str(caminho))
    if esquema.validate(doc):
        return []
    return [f"l{e.line}: {e.message}" for e in esquema.error_log]


def ler_instancia(caminho: Path | str, validar: bool = True) -> Instancia:
    """Le um XML do INRC-2010 e devolve a Instancia correspondente."""
    caminho = Path(caminho)
    if validar:
        erros = validar_xsd(caminho)
        if erros:
            raise ValueError(f"{caminho.name} nao valida contra o esquema: {erros[:3]}")

    r = etree.parse(str(caminho)).getroot()
    inicio = date.fromisoformat(_txt(r, "StartDate"))
    fim = date.fromisoformat(_txt(r, "EndDate"))

    turnos = {}
    for el in r.iterfind("ShiftTypes/Shift"):
        turnos[el.get("ID")] = Turno(
            id=el.get("ID"),
            inicio=_hora(_txt(el, "StartTime")),
            fim=_hora(_txt(el, "EndTime")),
            descricao=_txt(el, "Description"),
            habilidades=frozenset(s.text.strip() for s in el.iterfind("Skills/Skill")),
        )

    padroes = {}
    for el in r.iterfind("Patterns/Pattern"):
        padroes[el.get("ID")] = Padrao(
            id=el.get("ID"),
            peso=int(el.get("weight", 0)),
            entradas=tuple(
                EntradaPadrao(turno=_txt(e, "ShiftType"), dia=_txt(e, "Day"))
                for e in el.iterfind("PatternEntries/PatternEntry")),
        )

    contratos = {}
    for el in r.iterfind("Contracts/Contract"):
        flexiveis = {attr: _flexivel(el, elemento) for elemento, attr in ELEMENTO_DE.items()}
        contratos[el.get("ID")] = Contrato(
            id=el.get("ID"),
            descricao=_txt(el, "Description"),
            weekend_definition=_txt(el, "WeekendDefinition", "SaturdaySunday"),
            padroes_indesejados=tuple(
                p.text.strip() for p in el.iterfind("UnwantedPatterns/Pattern")),
            **flexiveis,
        )

    profissionais = {}
    for el in r.iterfind("Employees/Employee"):
        profissionais[el.get("ID")] = Profissional(
            id=el.get("ID"),
            nome=_txt(el, "Name"),
            contrato=_txt(el, "ContractID"),
            habilidades=frozenset(s.text.strip() for s in el.iterfind("Skills/Skill")),
        )

    inst = Instancia(
        id=r.get("ID", caminho.stem),
        arquivo=caminho.name,
        inicio=inicio,
        fim=fim,
        habilidades=tuple(s.text.strip() for s in r.iterfind("Skills/Skill")),
        turnos=turnos,
        padroes=padroes,
        contratos=contratos,
        profissionais=profissionais,
        demanda=_cobertura(r, inicio, fim),
        pedidos=_pedidos(r),
    )
    _conferir_integridade(inst)
    return inst


def _conferir_integridade(inst: Instancia) -> None:
    """Referencias cruzadas que o XSD nao verifica. Falha cedo e com mensagem clara."""
    for (_, turno) in inst.demanda:
        if turno not in inst.turnos:
            raise ValueError(f"{inst.id}: cobertura cita turno inexistente '{turno}'")
    for p in inst.profissionais.values():
        if p.contrato not in inst.contratos:
            raise ValueError(f"{inst.id}: profissional {p.id} cita contrato inexistente")
        if not p.habilidades <= set(inst.habilidades):
            raise ValueError(f"{inst.id}: profissional {p.id} tem habilidade nao declarada")
    for c in inst.contratos.values():
        for pid in c.padroes_indesejados:
            if pid not in inst.padroes:
                raise ValueError(f"{inst.id}: contrato {c.id} cita padrao inexistente '{pid}'")
    for ped in inst.pedidos:
        if ped.profissional not in inst.profissionais:
            raise ValueError(f"{inst.id}: pedido de profissional inexistente")
        if ped.turno is not None and ped.turno not in inst.turnos:
            raise ValueError(f"{inst.id}: pedido cita turno inexistente '{ped.turno}'")
        if not (inst.inicio <= ped.data <= inst.fim):
            raise ValueError(f"{inst.id}: pedido fora do horizonte ({ped.data})")


# ---------------------------------------------------------------------------
# Conferencia
# ---------------------------------------------------------------------------

def _conferir_obrigatorias(por_nome: dict[str, Instancia]) -> list[str]:
    """As duas conferencias fixadas no PLANO.md para a Sessao 2."""
    falhas = []

    def ok(condicao: bool, descricao: str) -> None:
        print(f"  [{'OK   ' if condicao else 'FALHA'}] {descricao}")
        if not condicao:
            falhas.append(descricao)

    l01 = por_nome["long_early01"]
    chefes = sum(1 for p in l01.profissionais.values() if "HeadNurse" in p.habilidades)
    ok(l01.demanda_total == 740, f"long01: 740 atribuicoes de demanda (lido {l01.demanda_total})")
    ok(len(l01.profissionais) == 49, f"long01: 49 profissionais (lido {len(l01.profissionais)})")
    ok(chefes == 6, f"long01: 6 profissionais com HeadNurse (lido {chefes})")

    s01 = por_nome["sprint_early01"]
    desligadas = ("max_consecutive_working_weekends", "min_consecutive_working_weekends",
                  "max_working_weekends_in_four_weeks")
    for nome in desligadas:
        fora = [c.id for c in s01.contratos.values() if getattr(c, nome).ligada]
        ok(len(s01.contratos) == 4 and not fora,
           f"sprint01: {nome} desligada nos 4 contratos"
           + (f" (ligada em {fora})" if fora else ""))
    return falhas


def _conferir_contra_inventario(instancias: list[dict],
                                lidas: dict[str, Instancia]) -> list[str]:
    """Compara o parser com a varredura da Sessao 1, instancia por instancia."""
    if not CSV_INVENTARIO.exists():
        print(f"  inventario ausente ({CSV_INVENTARIO.name}); rode src/inspecionar.py antes")
        return []
    with CSV_INVENTARIO.open(encoding="utf-8-sig", newline="") as f:
        inventario = {l["nome_literatura"]: l for l in csv.DictReader(f, delimiter=";")}

    divergencias = []
    for inst in instancias:
        nome = inst["nome_literatura"]
        lida, esperado = lidas[nome], inventario.get(nome)
        if esperado is None:
            divergencias.append(f"{nome}: ausente do inventario")
            continue
        chefes = sum(1 for p in lida.profissionais.values() if "HeadNurse" in p.habilidades)
        hab = dict(kv.split(":") for kv in esperado["prof_por_habilidade"].split("|") if kv)
        comparacoes = {
            "n_profissionais": (len(lida.profissionais), int(esperado["n_profissionais"])),
            "n_tipos_turno": (len(lida.turnos), int(esperado["n_tipos_turno"])),
            "n_contratos": (len(lida.contratos), int(esperado["n_contratos"])),
            "n_padroes": (len(lida.padroes), int(esperado["n_padroes"])),
            "demanda_total": (lida.demanda_total, int(esperado["demanda_total"])),
            "dias": (lida.n_dias, int(esperado["dias"])),
            "HeadNurse": (chefes, int(hab.get("HeadNurse", 0))),
            "n_DayOff": (sum(1 for p in lida.pedidos if p.tipo == "folga_dia"),
                         int(esperado["n_DayOff"])),
            "n_ShiftOff": (sum(1 for p in lida.pedidos if p.tipo == "folga_turno"),
                           int(esperado["n_ShiftOff"])),
        }
        for campo, (obtido, previsto) in comparacoes.items():
            if obtido != previsto:
                divergencias.append(f"{nome}.{campo}: parser {obtido} x inventario {previsto}")
    return divergencias


def main() -> int:
    instancias, avisos = descobrir_instancias()
    print(f"{len(instancias)} instancias encontradas")
    for a in avisos:
        if "nivel extra" not in a:
            print(f"  aviso: {a}")

    lidas: dict[str, Instancia] = {}
    for inst in instancias:
        lidas[inst["nome_literatura"]] = ler_instancia(inst["caminho"], validar=True)
    print(f"{len(lidas)} instancias lidas e validadas contra o esquema\n")

    print("Conferencias obrigatorias (PLANO.md, Sessao 2):")
    falhas = _conferir_obrigatorias(lidas)

    print("\nConferencia cruzada contra docs/inventario_instancias.csv:")
    divergencias = _conferir_contra_inventario(instancias, lidas)
    if divergencias:
        for d in divergencias[:20]:
            print(f"  DIVERGENCIA {d}")
    else:
        print(f"  [OK   ] as {len(lidas)} instancias batem em 9 campos cada")

    incompletos = [(n, fs) for n, i in lidas.items() for c in i.contratos
                   for fs in i.fins_de_semana(c) if not fs.completo]
    print(f"\nFins de semana incompletos no horizonte: {len(incompletos)}"
          + ("" if not incompletos else f" -> {incompletos[:3]}"))

    print("\n" + lidas["long_early01"].resumo())
    print(lidas["sprint_early01"].resumo())

    total = len(falhas) + len(divergencias)
    print("\nTodas as conferencias passaram." if not total
          else f"\n{total} conferencia(s) falharam.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
