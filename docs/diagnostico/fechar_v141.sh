#!/usr/bin/env bash
# Fecha a v1.4.1 (Parte 7, 20/10: piso por pares de dias): o mesmo conteudo do fechar_v140.sh
# mais os testes da Parte 7, NA ORDEM, um processo por teste, parando na PRIMEIRA falha. Da raiz:
#
#   "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v141.sh
#
# Esperados: resultados/piso_pares_2026-10-20/ESPERADO.md (Parte 7) e os da v1.4.0
# (pedidos_2026-10-20/, max_dias_2026-10-20/, tela_2026-10-20/). A identidade e contra a v1.4.0,
# num worktree em ../tcc-nrp-v140 (git worktree add ../tcc-nrp-v140 v1.4.0).
# Saida em resultados/v141_<data>/suite/resumo.txt. RETOMAR=1 pula o que ja esta no resumo com
# codigo 0 e acrescenta ao resumo; retoma a pasta mais recente (ou a de V141_DATA).
set -u
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
if [ -z "${V141_DATA:-}" ] && [ "${RETOMAR:-0}" = 1 ]; then
    V141_DATA=$(ls -d resultados/v141_* 2>/dev/null | sort | tail -1 | sed 's/.*v141_//')
fi
DATA="${V141_DATA:-$(date +%Y-%m-%d)}"
RAIZ_SAIDA=resultados/v141_$DATA
OUT=$RAIZ_SAIDA/suite
mkdir -p "$OUT"
RESUMO="$OUT/resumo.txt"
[ "${RETOMAR:-0}" = 1 ] || : > "$RESUMO"
export PYTHONIOENCODING=utf-8
BASE="${TEMP:-/tmp}/v141_identidade"
V140=../tcc-nrp-v140

para() { echo "PARADO: $1" | tee -a "$RESUMO"; exit 1; }

roda() {   # roda <nome> <comando...>: grava o log, anota no resumo, para se falhar
    local nome="$1"; shift
    if [ "${RETOMAR:-0}" = 1 ] && grep -q "^$nome | codigo 0 " "$RESUMO"; then return 0; fi
    local t0; t0=$(date +%s)
    "$@" > "$OUT/$nome.log" 2>&1
    local cod=$?
    printf '%s | codigo %s | %s s | %s\n' "$nome" "$cod" "$(( $(date +%s) - t0 ))" \
        "$(tail -1 "$OUT/$nome.log")" | tee -a "$RESUMO"
    [ "$cod" -eq 0 ] || para "$nome falhou (ver $OUT/$nome.log)"
}

[ -d "$V140/docs/diagnostico" ] || para "falta o worktree da v1.4.0 em $V140 (git worktree add ../tcc-nrp-v140 v1.4.0)"
[ "${PULAR_SOLVER:-0}" = 1 ] && echo "(PULAR_SOLVER=1: teste do script, so os passos sem solver)"

# identidade da entrada do solver: v1.4.0 x arvore atual (sem linhas; e com os pedidos como
# linhas "Folga + dia, Essencial"), e o controle positivo. Os scripts de identidade ja estao na
# v1.4.0 (commitados), entao nada e copiado para o worktree.
[ "${RETOMAR:-0}" = 1 ] || rm -rf "$BASE"
roda id_gravar_v140 bash -c "cd $V140 && ../tcc-nrp/$PY docs/diagnostico/identidade_3bloco.py --gravar '$BASE/v140'"
roda id_gravar_nova "$PY" docs/diagnostico/identidade_3bloco.py --gravar "$BASE/nova"
roda id_gravar_regras "$PY" docs/diagnostico/identidade_3bloco.py --gravar "$BASE/regras" --regras
roda id_comparar "$PY" docs/diagnostico/identidade_opcao_b.py --comparar "$BASE/v140" "$BASE/nova"
roda id_comparar_regras "$PY" docs/diagnostico/identidade_opcao_b.py --comparar "$BASE/v140" "$BASE/regras"
roda id_controle "$PY" docs/diagnostico/identidade_3bloco.py --controle "$BASE/controle"

# Parte 7, sem solver: seguranca nas rodadas registradas, controle (Parte 3), casos A e B
export PISO_PARES_SAIDA=$RAIZ_SAIDA/piso_pares
roda piso_seguranca "$PY" docs/diagnostico/piso_pares.py --seguranca
roda piso_controle "$PY" docs/diagnostico/piso_pares.py --controle
roda piso_casos "$PY" docs/diagnostico/piso_pares.py --casos
[ "${PULAR_SOLVER:-0}" = 1 ] && { echo "TESTE DO SCRIPT OK (sem solver)" | tee -a "$RESUMO"; exit 0; }
# Parte 7, com solver (porte pequeno): o sorteio
roda piso_sorteio "$PY" docs/diagnostico/piso_pares.py --sorteio

roda regressao "$PY" src/regressao.py --todos
roda testes_entrada "$PY" src/testes_entrada.py
roda avaliador_pedidos "$PY" docs/diagnostico/pedidos_avaliador.py
for caso in ped-2 ped-3 ped-6 max-dias tela-limpa descanso-param \
            opB-padroes opB-d opB-b opB-c opB-e opB-tela \
            16 4b 7.4 9b-sem-teto 9c-tela 3 4 5 15 7.1 7.2 8 12 1-2 9 7.3; do
    roda "tela_$caso" "$PY" src/testes_ferramenta.py "$caso"
done

# (a2) rodadas com a classificacao padrao e os limites da v1.2.3, comparadas com o registrado;
# admitida so a mudanca registrada da Parte 7 (P05: 14 passa do solver a conta)
export A2_SAIDA=$RAIZ_SAIDA A2_PISO_PARES=1
for caso in P01 P02 P03 P04 P05 P06 P07 P08 P09 P10 P11 P12 P13 P14 P15 P16 P17 P18 \
            demo20 demo19 demo18; do
    roda "a2_$caso" "$PY" docs/diagnostico/identidade_opcao_b_rodadas.py "$caso"
done
roda a2_comparar "$PY" docs/diagnostico/identidade_opcao_b_rodadas.py --comparar
echo "TUDO OK" | tee -a "$RESUMO"
