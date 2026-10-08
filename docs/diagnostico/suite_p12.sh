#!/usr/bin/env bash
# Suite completa depois da P12 (08/10), um teste por processo, como a de 06/10.
#
#   bash docs/diagnostico/suite_p12.sh            # da raiz, com a .venv
#
# Cada teste grava resultados/suite_2026-10-08/<nome>.log; o resumo (codigo de saida, tempo,
# ultima linha) vai para resultados/suite_2026-10-08/resumo.txt. Feche o Chrome antes.
set -u
PY=.venv/Scripts/python.exe
OUT=resultados/suite_2026-10-08
mkdir -p "$OUT"
RESUMO="$OUT/resumo.txt"

roda() {   # roda <nome> <comando...>
    local nome="$1"; shift
    local t0=$(date +%s)
    "$@" > "$OUT/$nome.log" 2>&1
    local cod=$?
    local dt=$(( $(date +%s) - t0 ))
    printf '%s | codigo %s | %s s | %s\n' "$nome" "$cod" "$dt" "$(tail -1 "$OUT/$nome.log")" \
        | tee -a "$RESUMO"
}

roda regressao "$PY" src/regressao.py --todos
roda testes_entrada "$PY" src/testes_entrada.py
for caso in 12 8 1-2 3 4 4b 5 7.1 7.2 7.3 7.4 9 9b-sem-teto 9c-tela; do
    roda "tela_$caso" "$PY" src/testes_ferramenta.py "$caso"
done
