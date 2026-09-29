"""Testes das entradas da ferramenta (DECISOES.md, 29/09). Roda da raiz, com a .venv ativa:

    python src\\testes_entrada.py            # tudo, inclusive as resolucoes (~minutos)
    python src\\testes_entrada.py --rapido   # so o que nao chama o solver

O que se confere, e contra o que:

- **QP em duas parcelas**: o nucleo reproduz o `QP_ref` = 35,24 do Experimento A, pelo porte
  e pela entrada em pacientes.
- **Entrada por pacientes**: soma de pacientes x horas do grau; grau de maior carga; a mesma
  demanda que o caminho por porte, quando os pacientes dao o mesmo porte.
- **Razao fim de semana / dia util**: total de horas preservado em toda razao; a razao 20/29
  gera EXATAMENTE a demanda de `variacao = 1`, nos dois regimes e nas duas regras.
- **Reproducao do long01** (com solver): razao 20/29 exige 40 no 12x36 e 37 no de 8 h,
  com inviabilidade provada um abaixo — os numeros de `resultados/experimento_a.csv`.
- **Equipe por quantidade**: nomes padrao e informados, XML valido no esquema, conferencia
  da proporcao de enfermeiros.
- **Indisponibilidade** (com solver): a pessoa nao aparece nos dias bloqueados, as rigidas
  passam, e o descanso MEDIDO NO RELOGIO (`docs/conferencia_descanso_escala.py`, que nao usa
  lista de padroes) continua dentro do exigido.
"""

from __future__ import annotations

import sys
import tempfile
from datetime import timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "docs"))

import experimento_a as ea  # noqa: E402
import instancia_br as br  # noqa: E402
import modelo  # noqa: E402
from solucao import conferir_rigidas  # noqa: E402

FALHAS: list[str] = []


def confere(condicao: bool, mensagem: str) -> None:
    print(f"   {'ok   ' if condicao else 'FALHA'} {mensagem}")
    if not condicao:
        FALHAS.append(mensagem)


def teste_qp() -> None:
    print("QP em duas parcelas")
    nucleo, completo = br.quadro_pessoal(br.PORTE_HORAS / br.DIAS_HORIZONTE)
    confere(round(nucleo, 2) == 35.24, f"nucleo pelo porte = {nucleo:.4f} (esperado 35,24)")
    confere(abs(completo - nucleo * 1.15) < 1e-9, f"completo = nucleo x 1,15 = {completo:.2f}")
    confere(br.quadro_referencia() == nucleo, "quadro_referencia e o mesmo nucleo")
    pac = {"intermediario": br.PORTE_HORAS / br.DIAS_HORIZONTE / 6}
    n2, _ = br.quadro_pessoal(br.horas_por_dia(pac))
    confere(round(n2, 2) == 35.24, f"nucleo por pacientes ({pac['intermediario']:.2f} "
                                   f"intermediarios) = {n2:.4f}")


def teste_pacientes() -> None:
    print("entrada por pacientes")
    confere(br.horas_por_dia({"intermediario": 30, "intensivo": 4}) == 30 * 6 + 4 * 18,
            "30 intermediarios + 4 intensivos = 252 h/dia")
    confere(br.grau_de_maior_carga({"minimo": 10, "intermediario": 5}) == "intermediario",
            "minimo + intermediario -> intermediario")
    confere(br.grau_de_maior_carga({"alta": 3, "semi_intensivo": 1}) == "semi_intensivo",
            "alta + semi-intensivo (ambos 10 h) -> semi-intensivo, pela ordem do Parecer")
    confere(br.grau_de_maior_carga({"intensivo": 0, "minimo": 2}) == "minimo",
            "grau com zero pacientes nao conta")
    inst = br.construir(pacientes={"intermediario": 30, "intensivo": 4}, efetivo=50)
    horas = sum(q * br.REGIMES["12x36"][0][2] for q in inst.demanda.values())
    confere(inst.id.startswith("br_intensivo_"), f"grau derivado no id: {inst.id}")
    confere(horas >= 252 * 28, f"demanda entrega {horas} h >= {252 * 28} h (teto)")
    # pacientes que dao exatamente o porte do experimento -> a mesma demanda
    for regime in ("12x36", "8h"):
        a = br.construir(grau="intermediario", regime=regime)
        b = br.construir(regime=regime,
                         pacientes={"intermediario": br.PORTE_HORAS / br.DIAS_HORIZONTE / 6})
        confere(a.demanda == b.demanda, f"{regime}: pacientes equivalentes ao porte dao a "
                                        f"mesma demanda")


def teste_razao() -> None:
    print("razao fim de semana / dia util")
    for r in (0.0, 0.25, 20 / 29, 0.9, 1.0):
        perfil = br.perfil_continuo(razao_fds=r)
        confere(abs(sum(perfil.values()) - br.PORTE_HORAS) < 1e-6,
                f"razao {r:.3f}: total {sum(perfil.values()):.4f} h preservado")
    perfil = br.perfil_continuo(razao_fds=20 / 29)
    seg, sab = perfil[0], perfil[5 * 24]
    confere(abs(sab / seg - 20 / 29) < 1e-12, f"razao efetiva sabado/segunda = {sab / seg:.4f}")
    for regime in ("12x36", "8h"):
        for regra in ("teto", "maior_resto"):
            a = br.construir(grau="intermediario", regime=regime, regra=regra, variacao=1.0)
            b = br.construir(grau="intermediario", regime=regime, regra=regra,
                             razao_fds=20 / 29)
            confere(a.demanda == b.demanda,
                    f"{regime}/{regra}: razao 20/29 = variacao 1 (demanda identica)")
    confere(br.construir(razao_fds=1.0).demanda == br.construir().demanda,
            "razao 1 (padrao da ferramenta) = demanda plana")


def teste_equipe() -> None:
    print("equipe por quantidade")
    inst = br.construir(n_enfermeiros=13, n_tecnicos=25)
    nomes = [p.nome for p in inst.profissionais.values()]
    confere(nomes[:2] == ["Enf 1", "Enf 2"] and nomes[13] == "Téc 1" and len(nomes) == 38,
            f"nomes padrao: {nomes[0]}..{nomes[12]}, {nomes[13]}..{nomes[-1]}")
    confere(sum(1 for p in inst.profissionais.values() if br.HABILIDADE_ENF in p.habilidades)
            == 13, "13 com a habilidade de enfermeiro")
    confere(br.conferir_composicao(inst, "intermediario") == [],
            "13 de 38 cumpre os 33% do intermediario")
    pouco = br.construir(n_enfermeiros=5, n_tecnicos=33)
    confere(len(br.conferir_composicao(pouco, "intermediario")) == 1,
            f"5 de 38 e acusado: {br.conferir_composicao(pouco, 'intermediario')}")
    dada = br.construir(n_enfermeiros=2, n_tecnicos=1, nomes_enfermeiros=["Ana", "Bia"],
                        nomes_tecnicos=["Caio"])
    confere([p.nome for p in dada.profissionais.values()] == ["Ana", "Bia", "Caio"],
            "nomes informados")
    with tempfile.TemporaryDirectory() as tmp:
        caminho = br.escrever_xml(inst, Path(tmp) / "equipe.xml")
        confere(br.validar_xsd(caminho) == [], "XML com nomes acentuados valido no esquema")


def teste_descanso_semanal() -> None:
    """A medicao do art. 67 contra escalas montadas a mao, com resposta conhecida de antemao.

    Existe porque em 29/09 todas as escalas de 8 h deram EXATAMENTE 24 h — no limite. Valor
    no limite em todas e o tipo de coisa que pode ser a medicao presa num numero, e nao a
    escala; so caso com resposta sabida separa as duas coisas.
    """
    from conferencia_descanso_escala import _inicio_fim, descanso_semanal, medir
    print("descanso semanal medido no relogio (escalas montadas a mao)")
    inst = br.construir(regime="8h", efetivo=1)
    dia = lambda k: inst.inicio + timedelta(days=k)  # noqa: E731
    # M = 07-15, N = 23-07. Em cada caso, o maior descanso da semana 1 foi calculado a mao e
    # registrado ANTES de rodar (29/09, regra do descanso medido inteiro). O turno da segunda
    # da semana 2 (dia 7) fecha o descanso, para ele nao correr ate o fim do horizonte.
    casos = [
        # nenhum dia sem turno na semana: nao ha descanso que conte -> 0 h, reprova
        ("7 manhas seguidas", [(dia(k), "M") for k in range(8)], 0.0),
        # sab 15:00 -> seg (semana 2) 07:00 = 40 h
        ("manha de seg a sab, domingo livre, manha na seg seguinte",
         [(dia(k), "M") for k in range(6)] + [(dia(7), "M")], 40.0),
        # a noite de sabado termina dom 07:00; a da segunda seguinte comeca 23:00 = 40 h.
        # Com o recorte na segunda 00:00 (regra anterior) dava 23 h e reprovava escala legal.
        ("6 noites de seg a sab, noite na seg seguinte",
         [(dia(k), "N") for k in range(6)] + [(dia(7), "N")], 40.0),
        # a noite de quarta termina qui 07:00; quinta livre; manha de sexta 07:00 = 24 h
        ("noites seg-qua, quinta livre, manhas sex-seg",
         [(dia(k), "N") for k in (0, 1, 2)] + [(dia(k), "M") for k in (4, 5, 6, 7)], 24.0),
    ]
    for rotulo, turnos, esperado in casos:
        blocos = [_inicio_fim(inst, d, t) for d, t in sorted(turnos)]
        semana1 = descanso_semanal(inst, blocos)[0][1]
        confere(abs(semana1 - esperado) < 1e-9,
                f"{rotulo}: semana 1 = {semana1:.1f} h (esperado {esperado:.0f} h)")
        # e o `medir`, que e o que as conferencias usam, tem de devolver o mesmo pior caso
        r = medir(inst, [(d, "0", t) for d, t in turnos])
        confere((r["menor_semanal"] < 24) == (esperado < 24),
                f"{rotulo}: medir {'reprova' if r['menor_semanal'] < 24 else 'aprova'} "
                f"({r['menor_semanal']:.1f} h)")
    # borda aberta (29/09): folga no ULTIMO domingo, depois de noites de segunda a sabado. O
    # descanso vai de dom 07:00 ao fim do horizonte (17 h) e continua no periodo seguinte;
    # conta como cumprido. Esperado registrado antes de rodar: semana 4 = inf, aprova.
    turnos = [(dia(k), "N") for k in range(21, 27)]
    blocos = [_inicio_fim(inst, d, t) for d, t in turnos]
    semana4 = descanso_semanal(inst, blocos)[3][1]
    confere(semana4 == float("inf"),
            f"folga no ultimo domingo: semana 4 = {semana4} (esperado inf, borda aberta)")


def teste_reproducao_long01(tempo: int) -> None:
    """SE NAO REPRODUZIR, o resto nao vale: a instrucao e parar e relatar."""
    print("reproducao do long01 pela razao 20/29 (com solver)")
    esperado = {"12x36": 40, "8h": 37}
    for regime, minimo in esperado.items():
        abaixo, _, _ = ea.tentar("intermediario", regime, "teto", minimo - 1, ea.modelo.SOLVER_PADRAO,
                                 tempo, razao_fds=20 / 29)
        no_minimo, inst, escala = ea.tentar("intermediario", regime, "teto", minimo,
                                            ea.modelo.SOLVER_PADRAO, tempo, razao_fds=20 / 29)
        confere(abaixo == ea.INVIAVEL, f"{regime}: efetivo {minimo - 1} {abaixo}")
        confere(no_minimo == ea.VIAVEL, f"{regime}: efetivo {minimo} {no_minimo}")
        if escala:
            confere(conferir_rigidas(inst, escala) == [], f"{regime}: rigidas da escala ok")
            _descanso(inst, escala, regime)


def _descanso(inst, escala, rotulo) -> None:
    from conferencia_descanso_escala import medir, regime_da_instancia
    r = medir(inst, escala)
    exigido = br.DESCANSO_EXIGIDO[regime_da_instancia(inst)]
    limite = inst.contratos["0"].max_consecutive_working_days.valor
    confere(r["menor_geral"] >= exigido,
            f"{rotulo}: descanso minimo medido {r['menor_geral']:.0f} h >= {exigido} h")
    confere(r["max_consec"] <= limite,
            f"{rotulo}: dias seguidos {r['max_consec']} <= {limite}")
    from conferencia_descanso_escala import fmt_semanal
    confere(r["menor_semanal"] >= 24,
            f"{rotulo}: descanso semanal medido {fmt_semanal(r['menor_semanal'])} >= 24 h "
            f"(pior: profissional, semana = {r['pior_semanal']})")


def teste_indisponibilidade(tempo: int) -> None:
    print("indisponibilidade rigida (com solver)")
    for regime, efetivo in (("12x36", 38), ("8h", 38)):
        inicio = br.primeira_segunda()
        bloqueio = [("Enf 1", inicio + timedelta(days=3), inicio + timedelta(days=9)),
                    ("Téc 4", inicio + timedelta(days=20), inicio + timedelta(days=40))]
        veredito, inst, escala = ea.tentar(
            "intermediario", regime, "teto", efetivo, modelo.SOLVER_PADRAO, tempo,
            n_enfermeiros=13, n_tecnicos=efetivo - 13, indisponibilidades=bloqueio)
        confere(len(inst.indisponiveis) == 7 + 8,
                f"{regime}: 7 dias de Enf 1 + 8 de Téc 4 (recortado no fim do horizonte)")
        confere(veredito == ea.VIAVEL, f"{regime}: efetivo {efetivo} com bloqueio {veredito}")
        if not escala:
            continue
        escalados = {(n, d) for d, n, _ in escala}
        confere(not (escalados & inst.indisponiveis),
                f"{regime}: ninguem escalado em dia indisponivel")
        confere(conferir_rigidas(inst, escala) == [], f"{regime}: rigidas da escala ok")
        _descanso(inst, escala, regime)


def main() -> int:
    rapido = "--rapido" in sys.argv
    teste_qp()
    teste_pacientes()
    teste_razao()
    teste_equipe()
    teste_descanso_semanal()
    if not rapido:
        teste_reproducao_long01(tempo=600)
        if FALHAS:
            print("\nA REPRODUCAO FALHOU OU HA FALHA ANTERIOR: parando antes da indisponibilidade.")
        else:
            teste_indisponibilidade(tempo=600)
    print()
    if FALHAS:
        print(f"{len(FALHAS)} FALHA(S):")
        for f in FALHAS:
            print(f"   {f}")
        return 1
    print("testes das entradas OK" + (" (sem as resolucoes)" if rapido else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
