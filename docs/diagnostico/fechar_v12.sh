#!/usr/bin/env bash
# Fecha a v1.2 (09/10): tudo o que falta conferir da P14 e da P17, NA ORDEM, um processo por
# teste, parando na PRIMEIRA falha. Da raiz do repositorio, com o Chrome fechado:
#
#   "C:\Program Files\Git\bin\bash.exe" docs/diagnostico/fechar_v12.sh
#
# Resumo em resultados/fechar_v12/resumo.txt. A tag NAO e criada aqui: se terminar com
# "TUDO OK", os comandos da tag estao no fim do resultados/relatorio_2026-10-09c.md.
set -u
cd "$(dirname "$0")/../.."
PY=.venv/Scripts/python.exe
OUT=resultados/fechar_v12
mkdir -p "$OUT"
RESUMO="$OUT/resumo.txt"
: > "$RESUMO"
export PYTHONIOENCODING=utf-8

livre_mb() { powershell -NoProfile -Command '[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1KB)'; }

para() { echo "PARADO: $1" | tee -a "$RESUMO"; exit 1; }

memoria() {
    local l; l=$(livre_mb)
    echo "memoria livre: ${l} MB" | tee -a "$RESUMO"
    [ "$l" -ge 3072 ] || para "memoria livre abaixo de 3 GB antes de $1; feche programas e rode de novo"
}

roda() {   # roda <nome> <comando...>: grava o log, anota no resumo, para se falhar
    local nome="$1"; shift
    local t0; t0=$(date +%s)
    "$@" > "$OUT/$nome.log" 2>&1
    local cod=$?
    printf '%s | codigo %s | %s s | %s\n' "$nome" "$cod" "$(( $(date +%s) - t0 ))" \
        "$(tail -1 "$OUT/$nome.log")" | tee -a "$RESUMO"
    [ "$cod" -eq 0 ] || para "$nome falhou (ver $OUT/$nome.log)"
}

memoria "comecar"
# 1. o portao, obrigatorio antes de tudo (condicao do Otavio para a P17)
roda regressao "$PY" src/regressao.py --todos
roda testes_entrada "$PY" src/testes_entrada.py
# 2. P17: a etapa 2 sem prova parte da escala da etapa 1 e sempre entrega escala
for c in otavio K5 K6; do
    roda "p17_$c" "$PY" docs/diagnostico/p14_conferir.py "$c" --p17
done
# 3. P05, P08, K1: mesmo veredito e mesmo menor quadro de 07/10
for c in P08 P05 K1; do
    roda "bateria_$c" "$PY" docs/diagnostico/bateria_rodar.py "$c" --saida "$OUT/bateria"
done
roda bateria_comparar "$PY" - <<'PYEOF'
import json, sys
ok = True
for c in ("P08", "P05", "K1"):
    a = json.load(open(f"resultados/bateria_2026-10-07/{c}.json", encoding="utf-8"))
    b = json.load(open(f"resultados/fechar_v12/bateria/{c}.json", encoding="utf-8"))
    igual = (a["veredito"], a["menor_viavel"]) == (b["veredito"], b["menor_viavel"]) and not b["falhas"]
    ok &= igual
    print(c, "07/10:", a["veredito"], a["menor_viavel"], "| agora:", b["veredito"], b["menor_viavel"], "| falhas:", b["falhas"], "| igual" if igual else "| DIFERENTE")
print("bateria igual a 07/10" if ok else "BATERIA DIFERENTE")
sys.exit(0 if ok else 1)
PYEOF
# 4. a suite da tela inteira
for caso in 8 15 12 1-2 3 4 4b 5 7.1 7.2 7.3 7.4 9 9b-sem-teto 9c-tela; do
    roda "tela_$caso" "$PY" src/testes_ferramenta.py "$caso"
done
# 5. B2a da P14: a demonstracao pela tela, identica (o conferidor roda no fim de cada rodada)
for r in "rodada1" "rodada2_19tec --tec 19" "rodada2_18tec --tec 18"; do
    nome=${r%% *}
    memoria "a demonstracao ($nome)"
    roda "demo_$nome" bash docs/demonstracao/rodar_rodada.sh $r
    grep -q "planilhas da demonstracao: OK" "docs/demonstracao/${nome}_tela.txt" \
        || para "conferidor da demonstracao falhou em $nome"
done
roda demo_comparar "$PY" - <<'PYEOF'
import sys
import pandas as pd
esperado = {"rodada1": ("O quadro informado admite escala legal. Escala gerada.", 24),
            "rodada2_19tec": ("O quadro informado admite escala legal. Escala gerada.", 36),
            "rodada2_18tec": ("Falta 1; o menor quadro viável é 29. Escala gerada.", 34)}
ok = True
for r, (veredito, posto) in esperado.items():
    t = pd.read_excel(f"docs/demonstracao/{r}_escala.xlsx", sheet_name="Resumo")
    v = dict(zip(t["Item"], t["Valor"]))
    igual = (v["Veredito"] == veredito and int(v["Turnos de enfermeiro em posto de técnico"]) == posto
             and v["Pedidos de folga atendidos"] == "6 de 6")
    ok &= igual
    print(r, v["Veredito"], "|", v["Turnos de enfermeiro em posto de técnico"], "|",
          v["Pedidos de folga atendidos"], "| igual" if igual else "| DIFERENTE")
print("demonstracao igual" if ok else "DEMONSTRACAO DIFERENTE")
sys.exit(0 if ok else 1)
PYEOF
echo "TUDO OK: pode criar a tag v1.2 (comandos no fim do relatorio 09c)" | tee -a "$RESUMO"
