#!/usr/bin/env bash
# Conferencias da P14 e suite completa (09/10), um processo por teste. Da raiz, com a .venv;
# feche o Chrome antes. O P08 roda antes, sozinho (regra de 03/10).
#
#   bash docs/diagnostico/suite_p14.sh
#
# Resumo em resultados/suite_2026-10-09/resumo.txt (codigo, tempo, ultima linha).
set -u
PY=.venv/Scripts/python.exe
OUT=resultados/suite_2026-10-09
B=resultados/bateria_2026-10-09/p14
mkdir -p "$OUT" "$B"
export PYTHONIOENCODING=utf-8
RESUMO="$OUT/resumo.txt"

roda() {   # roda <log> <comando...>
    local log="$1"; shift
    local t0=$(date +%s)
    "$@" > "$log" 2>&1
    local cod=$?
    printf '%s | codigo %s | %s s | %s\n' "$(basename "$log" .log)" "$cod" \
        "$(( $(date +%s) - t0 ))" "$(tail -1 "$log")" | tee -a "$RESUMO"
}

# B2d: mesmo veredito e menor quadro de 07/10
for c in P05 K1; do
    roda "$B/$c.log" "$PY" docs/diagnostico/bateria_rodar.py "$c" --saida "$B"
done
# B2b e B2c: a etapa 2 roda sem prova, sem piorar
for c in otavio K5 K6; do
    roda "$OUT/p14_$c.log" "$PY" docs/diagnostico/p14_conferir.py "$c"
done
# suite da tela e o portao
roda "$OUT/regressao.log" "$PY" src/regressao.py --todos
for caso in 8 15 12 1-2 3 4 4b 5 7.1 7.2 7.3 7.4 9 9b-sem-teto 9c-tela; do
    roda "$OUT/tela_$caso.log" "$PY" src/testes_ferramenta.py "$caso"
done
# B2a: demonstracao pela tela, com o conferidor
for r in "rodada1" "rodada2_19tec --tec 19" "rodada2_18tec --tec 18"; do
    nome=${r%% *}
    t0=$(date +%s)
    bash docs/demonstracao/rodar_rodada.sh $r
    printf 'demo_%s | codigo %s | %s s | %s\n' "$nome" "$?" "$(( $(date +%s) - t0 ))" \
        "$(grep 'planilhas da demonstracao' docs/demonstracao/${nome}_tela.txt)" | tee -a "$RESUMO"
done
