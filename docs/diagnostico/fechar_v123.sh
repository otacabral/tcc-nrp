#!/usr/bin/env bash
# Fecha a v1.2.3 (13/10, art. 67 com horarios editaveis): portao, entradas e a suite da tela,
# NA ORDEM, um processo por teste, parando na PRIMEIRA falha. Da raiz, com o Chrome fechado:
#
#   "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v123.sh
#
# Resumo em resultados/art67_2026-10-13/resumo.txt. Esperado: resultados/relatorio_2026-10-13a.md.
set -u
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
OUT=resultados/art67_2026-10-13
mkdir -p "$OUT"
RESUMO="$OUT/resumo.txt"
: > "$RESUMO"
export PYTHONIOENCODING=utf-8

para() { echo "PARADO: $1" | tee -a "$RESUMO"; exit 1; }

roda() {   # roda <nome> <comando...>: grava o log, anota no resumo, para se falhar
    local nome="$1"; shift
    local t0; t0=$(date +%s)
    "$@" > "$OUT/$nome.log" 2>&1
    local cod=$?
    printf '%s | codigo %s | %s s | %s\n' "$nome" "$cod" "$(( $(date +%s) - t0 ))" \
        "$(tail -1 "$OUT/$nome.log")" | tee -a "$RESUMO"
    [ "$cod" -eq 0 ] || para "$nome falhou (ver $OUT/$nome.log)"
}

roda regressao "$PY" src/regressao.py --todos
roda testes_entrada "$PY" src/testes_entrada.py
for caso in 16 4b 7.4 9b-sem-teto 9c-tela 3 4 5 15 7.1 7.2 8 12 1-2 9 7.3; do
    roda "tela_$caso" "$PY" src/testes_ferramenta.py "$caso"
done
echo "TUDO OK" | tee -a "$RESUMO"
