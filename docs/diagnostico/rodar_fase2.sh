#!/usr/bin/env bash
# Fase 2 (casos A e B), na v1.4.1, DEPOIS da tag: cinco rodadas, NA ORDEM, um processo por
# rodada (docs/diagnostico/fase2.py), classificacao padrao, orcamento 60 min por rodada, 1.800 s
# por nivel. Da raiz:
#
#   "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/rodar_fase2.sh
#
# Esperados: resultados/caso_a_2026-10-20/ESPERADO.md e caso_b_2026-10-20/ESPERADO.md.
# Saida em resultados/fase2_<data>/ (JSON e .txt por rodada, logs e resumo.txt). As rodadas de
# 11 h sao HIPOTESE DE SENSIBILIDADE — NAO REGRA DA FERRAMENTA (nome dos arquivos e primeira
# linha de cada saida). "Nao decidido" nao e falha; PARADO so por erro de codigo ou de entrada, ou
# por memoria: antes de cada rodada, menos de 3 GB livres -> "PARADO: menos de 3 GB livres".
# RETOMAR=1 pula o que ja esta no resumo com codigo 0 (pasta mais recente, ou a de FASE2_DATA).
# PULAR_SOLVER=1: teste do script — so monta as cinco entradas (sem solver).
set -u
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
if [ -z "${FASE2_DATA:-}" ] && [ "${RETOMAR:-0}" = 1 ]; then
    FASE2_DATA=$(ls -d resultados/fase2_* 2>/dev/null | sort | tail -1 | sed 's/.*fase2_//')
fi
OUT=resultados/fase2_${FASE2_DATA:-$(date +%Y-%m-%d)}
mkdir -p "$OUT"
RESUMO="$OUT/resumo.txt"
[ "${RETOMAR:-0}" = 1 ] || : > "$RESUMO"
export PYTHONIOENCODING=utf-8
MINIMO_GB=${MINIMO_GB:-3}   # so o teste do script muda isto (para ver o PARADO)
EXTRA=""
[ "${PULAR_SOLVER:-0}" = 1 ] && EXTRA="--montar"

para() { echo "PARADO: $1" | tee -a "$RESUMO"; exit 1; }

livre_gb() {   # memoria fisica livre do Windows, em GB (inteiro)
    local kb
    kb=$(powershell.exe -NoProfile -Command \
         "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory" | tr -dc '0-9')
    [ -n "$kb" ] || { echo -1; return; }
    echo $(( kb / 1024 / 1024 ))
}

roda() {   # roda <nome> <hipotese 0|1>
    local nome="$1" hip="$2" arq="$1"
    [ "$hip" = 1 ] && arq="HIPOTESE_SENSIBILIDADE_$1"
    if [ "${RETOMAR:-0}" = 1 ] && grep -q "^$nome | codigo 0 " "$RESUMO"; then return 0; fi
    local gb; gb=$(livre_gb)
    [ "$gb" -ge 0 ] || para "não consegui ler a memória livre do Windows"
    echo "$nome: memória livre ${gb} GB"
    [ "$gb" -ge "$MINIMO_GB" ] || para "menos de 3 GB livres (${gb} GB) antes de $nome"
    local t0; t0=$(date +%s)
    # a primeira linha do log das rodadas de 11 h e o ROTULO, escrito pelo fase2.py
    "$PY" docs/diagnostico/fase2.py "$nome" "$OUT" $EXTRA > "$OUT/$arq.log" 2>&1
    local cod=$?
    printf '%s | codigo %s | %s s | %s\n' "$nome" "$cod" "$(( $(date +%s) - t0 ))" \
        "$(grep -v '^DESCANSO_POR_TURNO ao fim' "$OUT/$arq.log" | tail -1)" | tee -a "$RESUMO"
    grep "^DESCANSO_POR_TURNO ao fim" "$OUT/$arq.log" | tail -1
    [ "$cod" -eq 0 ] || para "$nome: erro de código ou de entrada (ver $OUT/$arq.log)"
}

roda A36_livre 0
roda A36_fixo 0
roda A11_fixo 1
roda B11_livre 1
roda B36_livre 0
echo "DESCANSO_POR_TURNO num processo novo: $("$PY" -c "import sys; sys.path.insert(0, 'src'); import instancia_br as br; print(br.DESCANSO_POR_TURNO)")"
if [ "${PULAR_SOLVER:-0}" = 1 ]; then
    echo "TESTE DO SCRIPT OK (só montagem, sem solver)" | tee -a "$RESUMO"
else
    echo "TUDO OK" | tee -a "$RESUMO"
fi
