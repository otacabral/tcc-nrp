#!/usr/bin/env bash
# Fecha a v1.4.0 (3o bloco, 19-20/10: pedidos e regras dos profissionais, maximo de dias seguidos
# do hospital, limpeza da tela): identidade com a v1.3.0, portao, entradas, testes novos e a
# suite da tela, NA ORDEM, um processo por teste, parando na PRIMEIRA falha. Da raiz:
#
#   "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v140.sh
#
# Esperados: resultados/pedidos_2026-10-20/, max_dias_2026-10-20/, tela_2026-10-20/ (ESPERADO.md).
# Resumo em resultados/v140_2026-10-20/suite/resumo.txt. A identidade precisa da v1.3.0 num
# worktree em ../tcc-nrp-v130 (git worktree add ../tcc-nrp-v130 v1.3.0).
# RETOMAR=1 pula o que ja esta no resumo com codigo 0 e acrescenta ao resumo.
set -u
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
OUT=resultados/v140_2026-10-20/suite
mkdir -p "$OUT"
RESUMO="$OUT/resumo.txt"
[ "${RETOMAR:-0}" = 1 ] || : > "$RESUMO"
export PYTHONIOENCODING=utf-8
BASE="${TEMP:-/tmp}/v140_identidade"

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

# identidade da entrada do solver: v1.3.0 x arvore atual (sem linhas; e com os pedidos como
# linhas "Folga + dia, Essencial"), e o controle positivo
[ "${RETOMAR:-0}" = 1 ] || rm -rf "$BASE"
cp docs/diagnostico/identidade_opcao_b.py docs/diagnostico/identidade_3bloco.py \
   ../tcc-nrp-v130/docs/diagnostico/
roda id_gravar_v130 bash -c "cd ../tcc-nrp-v130 && ../tcc-nrp/$PY docs/diagnostico/identidade_3bloco.py --gravar '$BASE/v130'"
roda id_gravar_nova "$PY" docs/diagnostico/identidade_3bloco.py --gravar "$BASE/nova"
roda id_gravar_regras "$PY" docs/diagnostico/identidade_3bloco.py --gravar "$BASE/regras" --regras
roda id_comparar "$PY" docs/diagnostico/identidade_opcao_b.py --comparar "$BASE/v130" "$BASE/nova"
roda id_comparar_regras "$PY" docs/diagnostico/identidade_opcao_b.py --comparar "$BASE/v130" "$BASE/regras"
roda id_controle "$PY" docs/diagnostico/identidade_3bloco.py --controle "$BASE/controle"

roda regressao "$PY" src/regressao.py --todos
roda testes_entrada "$PY" src/testes_entrada.py
roda avaliador_pedidos "$PY" docs/diagnostico/pedidos_avaliador.py
for caso in ped-2 ped-3 ped-6 max-dias tela-limpa \
            opB-padroes opB-d opB-b opB-c opB-e opB-tela \
            16 4b 7.4 9b-sem-teto 9c-tela 3 4 5 15 7.1 7.2 8 12 1-2 9 7.3; do
    roda "tela_$caso" "$PY" src/testes_ferramenta.py "$caso"
done

# (a2) rodadas com a classificacao padrao e os limites da v1.2.3, comparadas com o registrado
export A2_SAIDA=resultados/v140_2026-10-20
for caso in P01 P02 P03 P04 P05 P06 P07 P08 P09 P10 P11 P12 P13 P14 P15 P16 P17 P18 \
            demo20 demo19 demo18; do
    roda "a2_$caso" "$PY" docs/diagnostico/identidade_opcao_b_rodadas.py "$caso"
done
roda a2_comparar "$PY" docs/diagnostico/identidade_opcao_b_rodadas.py --comparar
echo "TUDO OK" | tee -a "$RESUMO"
