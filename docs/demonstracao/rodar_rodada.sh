#!/usr/bin/env bash
# Uma rodada da demonstracao pela tela, num processo so, com o Streamlit reiniciado:
#   bash docs/demonstracao/rodar_rodada.sh rodada1
#   bash docs/demonstracao/rodar_rodada.sh rodada2_21tec --tec 21
# Sobe o servidor, roda o roteiro de capturas, registra a memoria livre do Windows a cada
# 10 s (vigia) e derruba o servidor no fim. Saida em docs/demonstracao/<rodada>_tela.txt e
# <rodada>_memoria.txt.
set -u
cd "$(dirname "$0")/../.."
NOME="$1"; shift
OUT="docs/demonstracao/${NOME}_tela.txt"
MEM="docs/demonstracao/${NOME}_memoria.txt"
export PYTHONIOENCODING=utf-8

.venv/Scripts/python.exe -m streamlit run src/app.py --server.headless true \
    --server.port 8599 --browser.gatherUsageStats false > /dev/null 2>&1 &
for _ in $(seq 1 60); do
    curl -s -o /dev/null -w "%{http_code}" http://localhost:8599/ | grep -q 200 && break
    sleep 1
done

( while true; do
    echo "$(date +%H:%M:%S) livre_MB=$(powershell -NoProfile -Command '[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1KB)')"
    sleep 10
  done ) > "$MEM" &
VIGIA=$!

.venv/Scripts/python.exe -u docs/demonstracao/capturas.py "$NOME" "$@" > "$OUT" 2>&1
STATUS=$?

kill $VIGIA 2>/dev/null
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe' AND CommandLine LIKE '%streamlit run%8599%'\" | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force }"
# conferidor independente da entrada (08/10): a planilha baixada contra os dados DECLARADOS
# do caso — cobertura dia a dia, rigidas, descanso no relogio, teto e ferias
if [ $STATUS -eq 0 ]; then
    .venv/Scripts/python.exe docs/demonstracao/conferir_planilhas.py "$NOME" >> "$OUT" 2>&1
    STATUS=$?
fi
echo "status $STATUS" >> "$OUT"
echo "menor memoria livre: $(sort -t= -k2 -n "$MEM" | head -1)" >> "$OUT"
exit $STATUS
