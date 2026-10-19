#!/usr/bin/env bash
# Fecha a v1.3.0 (19/10, opcao B): portao, entradas, identidade com a v1.2.3, testes novos e a
# suite da tela, NA ORDEM, um processo por teste, parando na PRIMEIRA falha. Da raiz:
#
#   "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v130.sh
#
# Esperado: resultados/opcao_b_2026-10-19/ESPERADO.md. Resumo em
# resultados/opcao_b_2026-10-19/suite/resumo.txt. A identidade (a1) precisa da v1.2.3 num
# worktree em ../tcc-nrp-v123 (git worktree add ../tcc-nrp-v123 v1.2.3).
#
# Retomar depois de uma interrupcao (19/10: a suite foi derrubada por falta de memoria depois do
# caso 9c-tela): RETOMAR=1 pula o que ja esta no resumo com codigo 0 e acrescenta ao resumo.
set -u
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
OUT=resultados/opcao_b_2026-10-19/suite
mkdir -p "$OUT"
RESUMO="$OUT/resumo.txt"
[ "${RETOMAR:-0}" = 1 ] || : > "$RESUMO"
export PYTHONIOENCODING=utf-8
BASE="${TEMP:-/tmp}/opcao_b_identidade"

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

# (a1) identidade da entrada do solver: v1.2.3 x arvore atual, e o controle positivo
[ "${RETOMAR:-0}" = 1 ] || rm -rf "$BASE"
cp docs/diagnostico/identidade_opcao_b.py ../tcc-nrp-v123/docs/diagnostico/
roda a1_gravar_v123 bash -c "cd ../tcc-nrp-v123 && ../tcc-nrp/$PY docs/diagnostico/identidade_opcao_b.py --gravar '$BASE/v123'"
roda a1_gravar_nova "$PY" docs/diagnostico/identidade_opcao_b.py --gravar "$BASE/nova"
roda a1_comparar "$PY" docs/diagnostico/identidade_opcao_b.py --comparar "$BASE/v123" "$BASE/nova"
roda a1_controle "$PY" docs/diagnostico/identidade_opcao_b.py --controle "$BASE/controle"

roda regressao "$PY" src/regressao.py --todos
roda testes_entrada "$PY" src/testes_entrada.py
for caso in opB-padroes opB-d opB-b opB-c opB-e opB-tela; do
    roda "tela_$caso" "$PY" src/testes_ferramenta.py "$caso"
done
for caso in 16 4b 7.4 9b-sem-teto 9c-tela 3 4 5 15 7.1 7.2 8 12 1-2 9 7.3; do
    roda "tela_$caso" "$PY" src/testes_ferramenta.py "$caso"
done

# (a2) rodadas com a classificacao padrao e os limites da v1.2.3
for caso in P01 P02 P03 P04 P05 P06 P07 P08 P09 P10 P11 P12 P13 P14 P15 P16 P17 P18 \
            demo20 demo19 demo18; do
    roda "a2_$caso" "$PY" docs/diagnostico/identidade_opcao_b_rodadas.py "$caso"
done
roda a2_comparar "$PY" docs/diagnostico/identidade_opcao_b_rodadas.py --comparar
echo "TUDO OK" | tee -a "$RESUMO"
