"""Varredura das instancias do INRC-2010 (Sessao 1).

Percorre instancias/, valida cada XML contra docs/scheme_input.xsd e emite:

  docs/inventario_instancias.csv   uma linha por instancia
  docs/uso_elementos_opcionais.csv  elementos/atributos opcionais do XSD x instancias

Uso (na raiz do repositorio, com a .venv ativa):

    python src\\inspecionar.py

Os CSV usam ";" como separador e UTF-8 com BOM, para abrir direto no Excel
pt-BR. Em pandas: pd.read_csv(caminho, sep=";").

Este script e so de inspecao: nao e o parser. Nao cria dataclasses nem
interpreta semantica de restricao alem do necessario para contar.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

from lxml import etree

from parser import descobrir_instancias

RAIZ = Path(__file__).resolve().parents[1]
DIR_INSTANCIAS = RAIZ / "instancias"
XSD_ENTRADA = RAIZ / "docs" / "scheme_input.xsd"
CSV_INVENTARIO = RAIZ / "docs" / "inventario_instancias.csv"
CSV_OPCIONAIS = RAIZ / "docs" / "uso_elementos_opcionais.csv"

XS = "{http://www.w3.org/2001/XMLSchema}"
DIAS_SEMANA = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
               "Saturday", "Sunday")  # indice = date.weekday()

# Restricoes de contrato na ordem do XSD. Tipo "OnAndWeight" tem atributo on=
# e valor inteiro; tipo "WeightOnly" tem valor booleano e so weight=.
RESTRICOES_CONTRATO = [
    ("SingleAssignmentPerDay", "WeightOnly"),  # rigida, listada por completude
    ("MaxNumAssignments", "OnAndWeight"),
    ("MinNumAssignments", "OnAndWeight"),
    ("MaxConsecutiveWorkingDays", "OnAndWeight"),
    ("MinConsecutiveWorkingDays", "OnAndWeight"),
    ("MaxConsecutiveFreeDays", "OnAndWeight"),
    ("MinConsecutiveFreeDays", "OnAndWeight"),
    ("MaxConsecutiveWorkingWeekends", "OnAndWeight"),
    ("MinConsecutiveWorkingWeekends", "OnAndWeight"),
    ("MaxWorkingWeekendsInFourWeeks", "OnAndWeight"),
    ("CompleteWeekends", "WeightOnly"),
    ("IdenticalShiftTypesDuringWeekend", "WeightOnly"),
    ("NoNightShiftBeforeFreeWeekend", "WeightOnly"),
    ("TwoFreeDaysAfterNightShifts", "WeightOnly"),
    ("AlternativeSkillCategory", "WeightOnly"),
]


# A descoberta das instancias vive em parser.py (descobrir_instancias), para nao existir em
# duas versoes. Regra: track = 1o nivel, lote = 2o nivel, subpasta igual ao track = early.

# ---------------------------------------------------------------------------
# 2. Validacao
# ---------------------------------------------------------------------------

def carregar_esquema(xsd: Path) -> etree.XMLSchema:
    return etree.XMLSchema(etree.parse(str(xsd)))


def validar(esquema: etree.XMLSchema, doc: etree._ElementTree) -> tuple[bool, str]:
    ok = esquema.validate(doc)
    erros = " | ".join(f"l{e.line}: {e.message}" for e in esquema.error_log)
    return ok, erros


# ---------------------------------------------------------------------------
# 3. Extracao
# ---------------------------------------------------------------------------

def _txt(el, caminho, padrao=""):
    alvo = el.find(caminho)
    return alvo.text.strip() if alvo is not None and alvo.text else padrao


def _compacto(por_contrato: dict[str, str]) -> str:
    """Valor unico se todos os contratos concordam; senao 'c0=x|c1=y'."""
    valores = set(por_contrato.values())
    if len(valores) == 1:
        return valores.pop()
    return "|".join(f"c{k}={v}" for k, v in por_contrato.items())


def _fmt_counter(c: Counter | dict) -> str:
    return "|".join(f"{k}:{v}" for k, v in c.items())


def expandir_cobertura(raiz, inicio: date, fim: date) -> tuple[dict, list[str]]:
    """Demanda por (data, turno). DayOfWeekCover expandido para o horizonte;
    DateSpecificCover, se existir, sobrescreve a data (so para contagem)."""
    avisos = []
    por_dia_semana: dict[str, dict[str, int]] = defaultdict(dict)
    for dwc in raiz.iterfind("CoverRequirements/DayOfWeekCover"):
        dia = _txt(dwc, "Day")
        for cov in dwc.iterfind("Cover"):
            turno = _txt(cov, "Shift")
            pref = cov.find("Preferred")
            if pref is None:
                avisos.append(f"Cover sem Preferred em {dia}/{turno}")
            por_dia_semana[dia][turno] = int(pref.text) if pref is not None else 0

    por_data: dict[str, dict[str, int]] = defaultdict(dict)
    for dsc in raiz.iterfind("CoverRequirements/DateSpecificCover"):
        d = _txt(dsc, "Date")
        for cov in dsc.iterfind("Cover"):
            pref = cov.find("Preferred")
            por_data[d][_txt(cov, "Shift")] = int(pref.text) if pref is not None else 0

    demanda = {}
    d = inicio
    while d <= fim:
        cobertura = por_data.get(d.isoformat()) or por_dia_semana.get(DIAS_SEMANA[d.weekday()], {})
        for turno, qtd in cobertura.items():
            demanda[(d, turno)] = qtd
        d += timedelta(days=1)
    return demanda, avisos


def extrair(doc: etree._ElementTree) -> tuple[dict, list[str]]:
    r = doc.getroot()
    avisos: list[str] = []
    linha: dict[str, object] = {"id_xml": r.get("ID", "")}

    inicio = date.fromisoformat(_txt(r, "StartDate"))
    fim = date.fromisoformat(_txt(r, "EndDate"))
    linha["data_inicio"] = inicio.isoformat()
    linha["dia_semana_inicio"] = DIAS_SEMANA[inicio.weekday()]
    linha["dias"] = (fim - inicio).days + 1

    # --- Profissionais e habilidades
    empregados = r.findall("Employees/Employee")
    linha["n_profissionais"] = len(empregados)
    hab_declaradas = [s.text.strip() for s in r.iterfind("Skills/Skill")]
    prof_por_hab = Counter()
    combos = Counter()
    prof_por_contrato = Counter()
    for e in empregados:
        habs = sorted(s.text.strip() for s in e.iterfind("Skills/Skill"))
        prof_por_hab.update(habs)
        combos["+".join(habs) or "(nenhuma)"] += 1
        prof_por_contrato[_txt(e, "ContractID")] += 1
    linha["habilidades"] = "|".join(hab_declaradas)
    linha["prof_por_habilidade"] = _fmt_counter({h: prof_por_hab.get(h, 0) for h in hab_declaradas})
    linha["combinacoes_habilidade"] = _fmt_counter(dict(sorted(combos.items())))
    nao_declaradas = set(prof_por_hab) - set(hab_declaradas)
    if nao_declaradas:
        avisos.append(f"habilidade de profissional nao declarada: {sorted(nao_declaradas)}")

    # --- Turnos
    turnos = r.findall("ShiftTypes/Shift")
    linha["n_tipos_turno"] = len(turnos)
    linha["tipos_turno"] = "|".join(
        f"{t.get('ID')}({_txt(t, 'StartTime')[:5]}-{_txt(t, 'EndTime')[:5]})" for t in turnos)
    linha["habilidade_por_turno"] = "|".join(
        f"{t.get('ID')}:{'+'.join(s.text.strip() for s in t.iterfind('Skills/Skill')) or '-'}"
        for t in turnos)
    ids_turno = {t.get("ID") for t in turnos}

    # --- Padroes
    padroes = r.findall("Patterns/Pattern")
    linha["n_padroes"] = len(padroes)
    linha["padroes_def"] = " || ".join(
        f"{p.get('ID')}[w={p.get('weight', '')}]:" + "-".join(
            f"{_txt(pe, 'ShiftType')}@{_txt(pe, 'Day')}"
            for pe in p.iterfind("PatternEntries/PatternEntry"))
        for p in padroes)

    # --- Contratos
    contratos = r.findall("Contracts/Contract")
    linha["n_contratos"] = len(contratos)
    linha["contratos_desc"] = "|".join(f"{c.get('ID')}:{_txt(c, 'Description')}" for c in contratos)
    linha["prof_por_contrato"] = _fmt_counter(
        {c.get("ID"): prof_por_contrato.get(c.get("ID"), 0) for c in contratos})
    linha["weekend_definition"] = _compacto(
        {c.get("ID"): _txt(c, "WeekendDefinition", "ausente") for c in contratos})
    linha["unwanted_patterns"] = _compacto(
        {c.get("ID"): ",".join(p.text.strip() for p in c.iterfind("UnwantedPatterns/Pattern")) or "-"
         for c in contratos})

    for nome, tipo in RESTRICOES_CONTRATO:
        on, peso, valor = {}, {}, {}
        for c in contratos:
            cid = c.get("ID")
            el = c.find(nome)
            if el is None:
                on[cid] = peso[cid] = valor[cid] = "ausente"
                continue
            on[cid] = el.get("on", "-") if tipo == "OnAndWeight" else "-"
            peso[cid] = el.get("weight", "-")
            valor[cid] = (el.text or "").strip()
        if tipo == "OnAndWeight":
            linha[f"{nome}_on"] = _compacto(on)
        linha[f"{nome}_peso"] = _compacto(peso)
        linha[f"{nome}_valor"] = _compacto(valor)

    # --- Cobertura
    demanda, av = expandir_cobertura(r, inicio, fim)
    avisos += av
    linha["demanda_total"] = sum(demanda.values())
    por_turno = Counter()
    for (_, turno), q in demanda.items():
        por_turno[turno] += q
    linha["demanda_por_turno"] = _fmt_counter(por_turno)
    linha["capacidade_1_turno_dia"] = linha["n_profissionais"] * linha["dias"]
    turnos_cobertos = set(por_turno)
    if turnos_cobertos - ids_turno:
        avisos.append(f"cobertura cita turno inexistente: {sorted(turnos_cobertos - ids_turno)}")

    blocos_cov = Counter(ch.tag for ch in r.iterfind("CoverRequirements/*"))
    linha["blocos_cobertura"] = _fmt_counter(blocos_cov)
    tags_cover = Counter(ch.tag for ch in r.iterfind("CoverRequirements/*/Cover/*"))
    linha["tags_em_cover"] = "|".join(sorted(tags_cover))

    # --- Pedidos
    for bloco, item in (("DayOffRequests", "DayOff"), ("ShiftOffRequests", "ShiftOff"),
                        ("DayOnRequests", "DayOn"), ("ShiftOnRequests", "ShiftOn")):
        els = r.findall(f"{bloco}/{item}")
        linha[f"n_{item}"] = len(els)
        linha[f"pesos_{item}"] = "|".join(sorted({e.get("weight", "-") for e in els}, key=str))

    return linha, avisos


# ---------------------------------------------------------------------------
# 5. Elementos opcionais do esquema
# ---------------------------------------------------------------------------

def opcionais_do_xsd(xsd: Path) -> list[tuple[str, str, str]]:
    """(tipo, pai, nome) para todo elemento/atributo opcional do XSD.

    Elemento e opcional se tem minOccurs="0" ou esta dentro de um
    sequence/choice com minOccurs="0". Atributo e opcional se use != required.
    O pai e o elemento nomeado mais proximo; para complexTypes nomeados, todos
    os elementos que usam aquele tipo.
    """
    x = etree.parse(str(xsd)).getroot()
    usuarios_do_tipo = defaultdict(set)
    for el in x.iter(f"{XS}element"):
        if el.get("type") and el.get("name"):
            usuarios_do_tipo[el.get("type")].add(el.get("name"))

    def pais(no) -> set[str]:
        p = no.getparent()
        while p is not None:
            if p.tag == f"{XS}element" and p.get("name"):
                return {p.get("name")}
            if p.tag == f"{XS}complexType" and p.get("name"):
                return usuarios_do_tipo.get(p.get("name"), set())
            p = p.getparent()
        return set()

    def dentro_de_grupo_opcional(no) -> bool:
        p = no.getparent()
        while p is not None and p.tag != f"{XS}complexType":
            if p.tag in (f"{XS}sequence", f"{XS}choice") and p.get("minOccurs") == "0":
                return True
            p = p.getparent()
        return False

    itens = set()
    for el in x.iter(f"{XS}element"):
        nome = el.get("name")
        if not nome or el.getparent() is x:
            continue
        if el.get("minOccurs") == "0" or dentro_de_grupo_opcional(el):
            for pai in pais(el):
                itens.add(("elemento", pai, nome))
    for at in x.iter(f"{XS}attribute"):
        if at.get("use") != "required":
            for pai in pais(at):
                itens.add(("atributo", pai, at.get("name")))
    return sorted(itens, key=lambda t: (t[1], t[0], t[2]))


def usa(doc: etree._ElementTree, tipo: str, pai: str, nome: str) -> int:
    if tipo == "elemento":
        return len(doc.xpath(f"//{pai}/{nome}"))
    return len(doc.xpath(f"//{pai}[@{nome}]"))


def _lista_instancias(usadas: list[str], todas: list[str]) -> str:
    if not usadas:
        return "nenhuma"
    if len(usadas) == len(todas):
        return "todas"
    faltam = [i for i in todas if i not in usadas]
    if len(faltam) < len(usadas):
        return "todas exceto " + ",".join(faltam)
    return ",".join(usadas)


# ---------------------------------------------------------------------------
# Verificacoes obrigatorias
# ---------------------------------------------------------------------------

def verificar(linhas: list[dict]) -> list[str]:
    por_nome = {l["nome_literatura"]: l for l in linhas}
    falhas = []

    def conferir(inst, campo, esperado):
        obtido = por_nome.get(inst, {}).get(campo, "<instancia ausente>")
        status = "OK   " if str(obtido) == str(esperado) else "FALHA"
        print(f"  [{status}] {inst}.{campo} = {obtido} (esperado {esperado})")
        if status == "FALHA":
            falhas.append(f"{inst}.{campo}")

    l01 = por_nome.get("long_early01", {})
    hn = dict(kv.split(":") for kv in str(l01.get("prof_por_habilidade", "")).split("|") if kv)
    conferir("long_early01", "demanda_total", 740)
    conferir("long_early01", "n_profissionais", 49)
    print(f"  [{'OK   ' if hn.get('HeadNurse') == '6' else 'FALHA'}] "
          f"long_early01 HeadNurse = {hn.get('HeadNurse')} (esperado 6)")
    if hn.get("HeadNurse") != "6":
        falhas.append("long_early01.HeadNurse")

    for r in ("MaxConsecutiveWorkingWeekends", "MinConsecutiveWorkingWeekends",
              "MaxWorkingWeekendsInFourWeeks"):
        conferir("sprint_early01", f"{r}_on", "0")
    conferir("sprint_early01", "n_contratos", 4)
    return falhas


# ---------------------------------------------------------------------------

def main() -> int:
    esquema = carregar_esquema(XSD_ENTRADA)
    instancias, avisos_desc = descobrir_instancias(DIR_INSTANCIAS)
    print(f"{len(instancias)} instancias encontradas em {DIR_INSTANCIAS}")
    for a in avisos_desc:
        print(f"  aviso: {a}")

    opcionais = opcionais_do_xsd(XSD_ENTRADA)
    uso_opc: dict[tuple, list[str]] = {item: [] for item in opcionais}

    linhas, colunas = [], []
    for inst in instancias:
        doc = etree.parse(str(inst["caminho"]))
        ok, erros = validar(esquema, doc)
        dados, avisos = extrair(doc)
        linha = {k: v for k, v in inst.items() if k != "caminho"}
        linha.update({"xsd_valido": int(ok), "xsd_erros": erros})
        linha.update(dados)
        if dados["id_xml"] != Path(inst["arquivo"]).stem:
            avisos.append(f"ID do XML ({dados['id_xml']}) difere do nome do arquivo")
        linha["avisos"] = " | ".join(avisos)
        linhas.append(linha)
        for c in linha:
            if c not in colunas:
                colunas.append(c)
        for item in opcionais:
            if usa(doc, *item):
                uso_opc[item].append(inst["nome_literatura"])

    CSV_INVENTARIO.parent.mkdir(parents=True, exist_ok=True)
    with CSV_INVENTARIO.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=colunas, delimiter=";", restval="")
        w.writeheader()
        w.writerows(linhas)

    todas = [l["nome_literatura"] for l in linhas]
    with CSV_OPCIONAIS.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["tipo", "pai", "nome", "n_instancias", "de", "instancias"])
        for (tipo, pai, nome), usadas in uso_opc.items():
            w.writerow([tipo, pai, nome, len(usadas), len(todas), _lista_instancias(usadas, todas)])

    invalidas = [l["nome_literatura"] for l in linhas if not l["xsd_valido"]]
    print(f"\nValidacao XSD: {len(linhas) - len(invalidas)} validas, {len(invalidas)} invalidas")
    for l in linhas:
        if not l["xsd_valido"]:
            print(f"  {l['nome_literatura']}: {l['xsd_erros'][:300]}")
    com_aviso = [l for l in linhas if l["avisos"]]
    if com_aviso:
        print(f"\nAvisos de extracao ({len(com_aviso)} instancias):")
        for l in com_aviso:
            print(f"  {l['nome_literatura']}: {l['avisos']}")

    print(f"\nEscrito: {CSV_INVENTARIO.relative_to(RAIZ)} ({len(linhas)} linhas, {len(colunas)} colunas)")
    print(f"Escrito: {CSV_OPCIONAIS.relative_to(RAIZ)} ({len(opcionais)} itens opcionais)")

    print("\nVerificacoes obrigatorias:")
    falhas = verificar(linhas)
    if falhas:
        print(f"\n{len(falhas)} verificacao(oes) falharam: {falhas}")
        return 1
    print("\nTodas as verificacoes passaram.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
