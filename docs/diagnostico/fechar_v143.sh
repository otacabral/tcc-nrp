#!/usr/bin/env bash
# Fecha a v1.4.3 (21/10: a trava do maximo de dias seguidos e so a da CLT; a regra do hospital e
# preferencia; textos da tela para o gestor, tema claro e barra pelo relogio). Suite REDUZIDA (DECISOES.md, "2026-10-21 — Maximo de dias seguidos: a trava e so a
# da CLT"): a mudanca e so de entrada e tela, modelo e solver intocados, e a identidade prova que o
# problema enviado ao solver nao mudou. Um processo por teste, NA ORDEM, parando na PRIMEIRA
# falha. Da raiz:
#
#   "C:/Program Files/Git/bin/bash.exe" docs/diagnostico/fechar_v143.sh
#
# Esperado: resultados/trava_clt_2026-10-21/ESPERADO.md (lista dos passos e o motivo de cada um).
# A identidade e contra a v1.4.2, num worktree em ../tcc-nrp-v142 (git worktree add
# ../tcc-nrp-v142 v1.4.2). Saida em resultados/v143_<data>/suite/resumo.txt. RETOMAR=1 pula o que
# ja esta no resumo com codigo 0 e acrescenta ao resumo; retoma a pasta mais recente (ou a de
# V143_DATA). PULAR_SOLVER=1: teste do script, so os passos sem solver.
set -u
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
if [ -z "${V143_DATA:-}" ] && [ "${RETOMAR:-0}" = 1 ]; then
    V143_DATA=$(ls -d resultados/v143_* 2>/dev/null | sort | tail -1 | sed 's/.*v143_//')
fi
DATA="${V143_DATA:-$(date +%Y-%m-%d)}"
RAIZ_SAIDA=resultados/v143_$DATA
OUT=$RAIZ_SAIDA/suite
mkdir -p "$OUT"
RESUMO="$OUT/resumo.txt"
[ "${RETOMAR:-0}" = 1 ] || : > "$RESUMO"
export PYTHONIOENCODING=utf-8
BASE="${TEMP:-/tmp}/v143_identidade"
V142=../tcc-nrp-v142

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

[ -d "$V142/docs/diagnostico" ] || para "falta o worktree da v1.4.2 em $V142 (git worktree add ../tcc-nrp-v142 v1.4.2)"
[ "${PULAR_SOLVER:-0}" = 1 ] && echo "(PULAR_SOLVER=1: teste do script, so os passos sem solver)"

# (a) identidade da entrada do solver: v1.4.2 x arvore atual (sem linhas; e com os pedidos como
# linhas "Folga + dia, Essencial"), e o controle positivo
[ "${RETOMAR:-0}" = 1 ] || rm -rf "$BASE"
roda id_gravar_v142 bash -c "cd $V142 && ../tcc-nrp/$PY docs/diagnostico/identidade_3bloco.py --gravar '$BASE/v142'"
roda id_gravar_nova "$PY" docs/diagnostico/identidade_3bloco.py --gravar "$BASE/nova"
roda id_gravar_regras "$PY" docs/diagnostico/identidade_3bloco.py --gravar "$BASE/regras" --regras
roda id_comparar "$PY" docs/diagnostico/identidade_opcao_b.py --comparar "$BASE/v142" "$BASE/nova"
roda id_comparar_regras "$PY" docs/diagnostico/identidade_opcao_b.py --comparar "$BASE/v142" "$BASE/regras"
roda id_controle "$PY" docs/diagnostico/identidade_3bloco.py --controle "$BASE/controle"

# (b) preferencias, sem solver: controle (inclui o limite acima da lei) e identidade nas entradas
# da fase 2 (o preferencias.py grava com o codigo do worktree por --raiz)
roda pref_controle "$PY" docs/diagnostico/preferencias.py --controle "$BASE/pref_controle"
roda pref_fase2_v142 "$PY" docs/diagnostico/preferencias.py --gravar-fase2 "$BASE/fase2_v142" --raiz "$V142"
roda pref_fase2_nova "$PY" docs/diagnostico/preferencias.py --gravar-fase2 "$BASE/fase2_nova"
roda pref_fase2_comparar "$PY" docs/diagnostico/identidade_opcao_b.py --comparar "$BASE/fase2_v142" "$BASE/fase2_nova"

# (f) piso, sem solver: seguranca nas rodadas registradas, controle (Parte 3), casos A e B
export PISO_PARES_SAIDA=$RAIZ_SAIDA/piso_pares
roda piso_seguranca "$PY" docs/diagnostico/piso_pares.py --seguranca
roda piso_controle "$PY" docs/diagnostico/piso_pares.py --controle
roda piso_casos "$PY" docs/diagnostico/piso_pares.py --casos
[ "${PULAR_SOLVER:-0}" = 1 ] && { echo "TESTE DO SCRIPT OK (sem solver)" | tee -a "$RESUMO"; exit 0; }

# com solver: o caso pequeno das preferencias (usa a de dias seguidos), (c) o portao, as entradas
roda pref_caso_pequeno "$PY" docs/diagnostico/preferencias.py --caso-pequeno
roda regressao "$PY" src/regressao.py --todos
roda testes_entrada "$PY" src/testes_entrada.py
# testes da tela (motivo de cada um no ESPERADO): os que usam o campo removido ou a preferencia
# de dias (pref-tela, max-dias, opB-d, opB-tela, opB-c, opB-e); os que conferem textos que
# mudaram em 21/10 (8, 12, opB-tela, pref-tela, max-dias) ou que os textos novos nao podem
# quebrar (4, 9c-tela, tela-limpa, 15, 16, 7.4, 4b); e os que passam pela barra nova clicando em
# "Gerar escala" (todos os anteriores que usam a tela, mais o 5). Os longos por ultimo.
for caso in pref-tela max-dias opB-d 16 4b 7.4 9c-tela 4 5 15 8 12 opB-tela tela-limpa \
            opB-c opB-e; do
    roda "tela_$caso" "$PY" src/testes_ferramenta.py "$caso"
done
echo "TUDO OK" | tee -a "$RESUMO"
