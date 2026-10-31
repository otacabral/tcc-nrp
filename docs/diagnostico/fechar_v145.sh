#!/usr/bin/env bash
# Fecha a v1.4.5 (30/10: etapa 2 por min-max; DECISOES.md, "2026-10-30 — Etapa 2 por min-max
# (v1.4.5)"). Um processo por teste, NA ORDEM, parando na PRIMEIRA falha. Da raiz:
#
#   "C:/Program Files/Git/bin/bash.exe" docs/diagnostico/fechar_v145.sh
#
# A identidade e contra a v1.4.4, num worktree em ../tcc-nrp-v144 (git worktree add
# ../tcc-nrp-v144 v1.4.4): XML e LP da etapa 1 identicos; LP da etapa 2 diferente so no objetivo,
# na variavel `amplitude` e nas restricoes `amplitude_constraints` (identidade_v145.py, que le o
# LP como conteudo porque o Pyomo reordena termos e limites). Saida em
# resultados/v145_<data>/suite/resumo.txt. RETOMAR=1 pula o que ja esta no resumo com codigo 0.
# PULAR_SOLVER=1: teste do script, so os passos sem solver.
#
# Fora da suite: p14_conferir.py (os casos dependem do tempo; o item 3 passou em 30/10 a "maior
# amplitude <= etapa 1", nota no DECISOES; o caminho sem prova fica nos testes 8 e 9c-tela) e a
# escalabilidade (fora da v1.4.5). E p17_frase_conferir.py: falha igual na v1.4.4 (saida
# identica), porque espera os textos da tela anteriores a v1.4.3 (704cb6a, 22/10); a escolha da
# frase continua coberta pelos testes 8 e 12.
set -u
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
if [ -z "${V145_DATA:-}" ] && [ "${RETOMAR:-0}" = 1 ]; then
    V145_DATA=$(ls -d resultados/v145_* 2>/dev/null | sort | tail -1 | sed 's/.*v145_//')
fi
DATA="${V145_DATA:-$(date +%Y-%m-%d)}"
OUT=resultados/v145_$DATA/suite
mkdir -p "$OUT"
RESUMO="$OUT/resumo.txt"
[ "${RETOMAR:-0}" = 1 ] || : > "$RESUMO"
export PYTHONIOENCODING=utf-8
BASE="${TEMP:-/tmp}/v145_identidade_suite"
V144=../tcc-nrp-v144

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

[ -d "$V144/docs/diagnostico" ] || para "falta o worktree da v1.4.4 em $V144 (git worktree add ../tcc-nrp-v144 v1.4.4)"
[ "${PULAR_SOLVER:-0}" = 1 ] && echo "(PULAR_SOLVER=1: teste do script, so os passos sem solver)"

# (a) identidade da entrada do solver, v1.4.4 x arvore atual, e os controles
[ "${RETOMAR:-0}" = 1 ] || rm -rf "$BASE"
roda id_gravar_v144 bash -c "cd $V144 && ../tcc-nrp/$PY docs/diagnostico/identidade_3bloco.py --gravar '$BASE/v144'"
roda id_gravar_nova "$PY" docs/diagnostico/identidade_3bloco.py --gravar "$BASE/nova"
roda id_comparar "$PY" docs/diagnostico/identidade_v145.py "$BASE/v144" "$BASE/nova"
roda id_controle_comparador "$PY" docs/diagnostico/identidade_v145.py --controle "$BASE/v144" "$BASE/nova"
roda id_controle "$PY" docs/diagnostico/identidade_3bloco.py --controle "$BASE/controle"
[ "${PULAR_SOLVER:-0}" = 1 ] && { echo "TESTE DO SCRIPT OK (sem solver)" | tee -a "$RESUMO"; exit 0; }

# (c) o portao e as entradas
roda regressao "$PY" src/regressao.py --todos
roda testes_entrada "$PY" src/testes_entrada.py
# (d) testes da ferramenta que passam pela etapa 2 (lista do DECISOES de 30/10); 9 inclui 9c e 9d.
# Os longos por ultimo.
for caso in p20 opB-d opB-padroes opB-b 9 9c-tela 8 12 pref-tela opB-tela opB-c opB-e; do
    roda "tela_$caso" "$PY" src/testes_ferramenta.py "$caso"
done
echo "TUDO OK" | tee -a "$RESUMO"
