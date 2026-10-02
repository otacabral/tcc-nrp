"""Escala -> XML de solucao do avaliador oficial, e conferencia das duas rigidas.

Sem Pyomo: este modulo trabalha com a escala ja extraida, uma sequencia de
(data, profissional, turno). Isso permite conferir e escrever solucao vinda de qualquer
lugar — do modelo, de um arquivo, ou da escala trivial usada em teste.

Uso como conferencia (na raiz do repositorio, com a .venv ativa):

    python src\\solucao.py

Monta uma escala viavel trivial — sem otimizacao nenhuma, so cobrindo a demanda — para
`sprint01` e `sprint_hidden06`, confere as duas rigidas, escreve os XML em resultados/ e
valida contra docs/scheme_solution.xsd. Serve para testar o escritor sem depender do solver,
e para ter um arquivo pronto para rodar no avaliador oficial.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

from lxml import etree

from instancia import Instancia
from parser import ler_instancia

RAIZ = Path(__file__).resolve().parents[1]
XSD_SOLUCAO = RAIZ / "docs" / "scheme_solution.xsd"
DIR_RESULTADOS = RAIZ / "resultados"

Atribuicao = tuple[date, str, str]  # (data, profissional, turno)


def _chave(identificador: str):
    return (0, int(identificador)) if identificador.isdigit() else (1, identificador)


# ---------------------------------------------------------------------------
# Conferencia das duas rigidas
# ---------------------------------------------------------------------------

def conferir_rigidas(inst: Instancia, escala: list[Atribuicao] | tuple[Atribuicao, ...],
                     habilidade_rigida: bool = True) -> list[str]:
    """Lista os problemas da escala. Lista vazia = escala viavel.

    Confere as duas rigidas da competicao mais a integridade dos identificadores. A
    habilidade entra como conferencia separada, governada pela flag, porque se ela e
    restricao de dominio ou penalidade e pergunta aberta (DECISOES.md).

    Rodar isto antes de chamar o avaliador economiza tempo: escala invalida e rejeitada
    aqui, com mensagem em portugues, em vez de virar erro do Java.
    """
    problemas: list[str] = []
    atribuido: dict[tuple[date, str], int] = {}
    cobertura: dict[tuple[date, str], int] = {}

    for (d, n, s) in escala:
        if n not in inst.profissionais:
            problemas.append(f"profissional inexistente: {n}")
            continue
        if s not in inst.turnos:
            problemas.append(f"turno inexistente: {s}")
            continue
        if not (inst.inicio <= d <= inst.fim):
            problemas.append(f"atribuicao fora do horizonte: {d}")
            continue
        if (n, d) in inst.indisponiveis:
            problemas.append(f"{n} escalado em {d}, dia em que esta indisponivel")
        atribuido[(d, n)] = atribuido.get((d, n), 0) + 1
        cobertura[(d, s)] = cobertura.get((d, s), 0) + 1
        if habilidade_rigida and not inst.turnos[s].habilidades <= inst.profissionais[n].habilidades:
            problemas.append(f"{n} nao tem a habilidade exigida por {s} ({d})")

    # (I) cobertura exata
    for d in inst.dias:
        for s in inst.turnos:
            exigido, alocado = inst.demanda_de(d, s), cobertura.get((d, s), 0)
            if alocado != exigido:
                problemas.append(f"cobertura {d} turno {s}: {alocado} alocados, {exigido} exigidos")

    # (II) um turno por profissional por dia
    for (d, n), quantidade in atribuido.items():
        if quantidade > 1:
            problemas.append(f"{n} tem {quantidade} turnos em {d}")

    # teto de horas no horizonte, por profissional, quando a instancia declara carga
    # contratual (turnos configurados): as horas contratadas nos dias disponiveis
    if inst.carga_semanal_h is not None:
        horas: dict[str, float] = {}
        for (d, n, s) in escala:
            if n in inst.profissionais and s in inst.turnos:
                horas[n] = horas.get(n, 0.0) + inst.turnos[s].duracao_h
        for n, h in horas.items():
            teto = inst.horas_devidas(n)
            if h > teto + 1e-6:
                problemas.append(f"{n} com {h:g} h no periodo, acima do teto de "
                                 f"{teto:g} h")

    return problemas


# ---------------------------------------------------------------------------
# XML de solucao
# ---------------------------------------------------------------------------

def escrever_xml(inst: Instancia, escala: list[Atribuicao] | tuple[Atribuicao, ...],
                 caminho: Path | str, competidor: str = "TCC-CEFET",
                 penalidade: int = 0, validar: bool = True) -> Path:
    """Escreve a escala no formato de solucao da competicao.

    `penalidade` e o valor que o modelo calculou. No modelo minimo nao ha funcao objetivo,
    entao vai 0 — o avaliador calcula o proprio numero de qualquer forma, e e a comparacao
    entre os dois que valida o modelo a partir da semana 2.
    """
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    raiz = etree.Element("Solution")
    etree.SubElement(raiz, "SchedulingPeriodID").text = inst.id
    etree.SubElement(raiz, "Competitor").text = competidor
    etree.SubElement(raiz, "SoftConstraintsPenalty").text = str(int(penalidade))
    for (d, n, s) in sorted(escala, key=lambda a: (a[0], _chave(a[1]), a[2])):
        el = etree.SubElement(raiz, "Assignment")
        etree.SubElement(el, "Date").text = d.isoformat()
        etree.SubElement(el, "Employee").text = n
        etree.SubElement(el, "ShiftType").text = s

    arvore = etree.ElementTree(raiz)
    etree.indent(arvore, space="  ")
    arvore.write(str(caminho), encoding="utf-8", xml_declaration=True, pretty_print=True)

    if validar:
        erros = validar_xsd(caminho)
        if erros:
            raise ValueError(f"solucao escrita nao valida contra o esquema: {erros[:3]}")
    return caminho


def validar_xsd(caminho: Path | str) -> list[str]:
    """Valida contra docs/scheme_solution.xsd. Lista vazia = valido."""
    esquema = etree.XMLSchema(etree.parse(str(XSD_SOLUCAO)))
    doc = etree.parse(str(caminho))
    if esquema.validate(doc):
        return []
    return [f"l{e.line}: {e.message}" for e in esquema.error_log]


def ler_xml(caminho: Path | str) -> tuple[str, int, tuple[Atribuicao, ...]]:
    """Le um XML de solucao. Devolve (id da instancia, penalidade declarada, escala)."""
    raiz = etree.parse(str(caminho)).getroot()
    escala = tuple(
        (date.fromisoformat(el.findtext("Date")), el.findtext("Employee"), el.findtext("ShiftType"))
        for el in raiz.iterfind("Assignment"))
    return raiz.findtext("SchedulingPeriodID"), int(raiz.findtext("SoftConstraintsPenalty")), escala


# ---------------------------------------------------------------------------
# Escala trivial: fixture de teste, nao faz parte do modelo
# ---------------------------------------------------------------------------

def escala_trivial(inst: Instancia) -> tuple[Atribuicao, ...]:
    """Escala viavel construida por atribuicao direta, sem otimizacao.

    NAO e o modelo, e nao pretende ser boa: serve para testar o escritor de XML e para ter
    um arquivo com que exercitar o avaliador oficial antes do modelo estar pronto. Percorre
    os dias, atende os turnos mais restritos primeiro e distribui entre quem esta livre no
    dia, girando o ponto de partida para nao sobrecarregar sempre os mesmos.
    """
    escala: list[Atribuicao] = []
    ordem_turnos = sorted(inst.turnos, key=lambda s: len(inst.habilitados(s)))
    for i, d in enumerate(inst.dias):
        ocupados: set[str] = set()
        for s in ordem_turnos:
            exigido = inst.demanda_de(d, s)
            if not exigido:
                continue
            candidatos = [n for n in inst.habilitados(s) if n not in ocupados]
            if len(candidatos) < exigido:
                raise ValueError(f"{inst.id}: {d} turno {s} sem gente suficiente "
                                 f"({len(candidatos)} livres, {exigido} exigidos)")
            giro = i % len(candidatos)
            escolhidos = (candidatos[giro:] + candidatos[:giro])[:exigido]
            for n in escolhidos:
                escala.append((d, n, s))
                ocupados.add(n)
    return tuple(escala)


def noites_antes_de_fim_de_semana_livre(inst: Instancia,
                                        escala: tuple[Atribuicao, ...]) -> int:
    """Quantas vezes a escala poe alguem em turno noturno na vespera de um fim de semana
    que essa pessoa tem livre.

    E a situacao que a restricao `NoNightShiftBeforeFreeWeekend` penaliza. Serve para saber
    se um teste no avaliador tem o que medir: se este numero for zero, a ausencia de
    penalidade no avaliador nao prova nada.
    """
    por_pessoa: dict[str, dict[date, str]] = {}
    for (d, n, s) in escala:
        por_pessoa.setdefault(n, {})[d] = s
    noturnos = {s for s, t in inst.turnos.items() if t.noturno}

    ocorrencias = 0
    for n, dias_trabalhados in por_pessoa.items():
        for fds in inst.fins_de_semana(inst.profissionais[n].contrato):
            if any(d in dias_trabalhados for d in fds.datas):
                continue  # fim de semana trabalhado
            vespera = fds.datas[0] - timedelta(days=1)
            if dias_trabalhados.get(vespera) in noturnos:
                ocorrencias += 1
    return ocorrencias


# ---------------------------------------------------------------------------

ALVOS_TESTE = {
    "sprint01": "instancias/sprint/sprint/sprint01.xml",
    "sprint_hidden06": "instancias/sprint/sprint_hidden_xml/sprint_hidden_xml/sprint_hidden06.xml",
}


def main() -> int:
    falhas = 0
    for nome, relativo in ALVOS_TESTE.items():
        inst = ler_instancia(RAIZ / relativo)
        escala = escala_trivial(inst)
        problemas = conferir_rigidas(inst, escala)
        destino = DIR_RESULTADOS / f"{nome}_escala_trivial.xml"
        print(f"{nome}: {len(escala)} atribuicoes para demanda de {inst.demanda_total}")
        if problemas:
            falhas += 1
            print(f"  [FALHA] {len(problemas)} problema(s): {problemas[:3]}")
            continue
        print("  [OK   ] as duas rigidas conferem")
        escrever_xml(inst, escala, destino, penalidade=0, validar=True)
        print(f"  [OK   ] escrito e validado contra o esquema: {destino.relative_to(RAIZ)}")
        lido = ler_xml(destino)
        if lido[2] != tuple(sorted(escala, key=lambda a: (a[0], _chave(a[1]), a[2]))):
            falhas += 1
            print("  [FALHA] releitura do XML nao reproduz a escala")
        else:
            print("  [OK   ] releitura do XML reproduz a escala")
        if nome == "sprint_hidden06":
            n = noites_antes_de_fim_de_semana_livre(inst, escala)
            print(f"  noites na vespera de fim de semana livre: {n} "
                  f"({'teste do avaliador tem o que medir' if n else 'NAO serve de teste'})")

    print("\nTodas as conferencias passaram." if not falhas else f"\n{falhas} falha(s).")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
