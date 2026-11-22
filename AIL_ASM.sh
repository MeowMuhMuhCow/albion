#!/bin/bash
# AIL_ASM.sh (22.11.2026) - AIL-Hand-Assembler aus dem Original zurückbauen, mit ML 6.0 (DOSBox) assemblieren
# und gegen MAIN.EXE vergleichen. Aufruf: bash AIL_ASM.sh [BLOCK ENDE NAME]   (Standard: AIL32 0xac31a..0xacd17)
cd "$(dirname "$0")" || exit 1
set -o pipefail
printf '\033]0;%s\007' "AIL ASM ${3:-ail32}"
B="${1:-0xac31a}"; E="${2:-0xacd17}"; N="${3:-ail32}"; NU="${N^^}"
W="Compiler/ML60"; DOSBOX="${DOSBOX:-$(wslpath -u 'C:\Program Files (x86)\GOG Galaxy\Games\Albion\DOSBOX\DOSBox.exe')}"
python3 Werkzeuge/asm_ail.py bauen "$B" "$E" "$N" ${4:-} || exit 1
mkdir -p "$W/AIL"
[ -f "$W/AIL/$NU.OBJ" ] && mv -f "$W/AIL/$NU.OBJ" "$W/AIL/$NU.OBJ.alt"
Q="src/AIL/ASM/$NU.ASM"; [ "$N" = "zoom" ] && Q="src/ZOOMFUNC/ZOOM.ASM"
cp "$Q" "$W/AIL/$N.asm" || exit 1
WM="$(wslpath -w "$W")"; CONF="$W/ail_asm_dosbox.conf"
{
echo "[cpu]"; echo "cycles=max"; echo "[autoexec]"
echo "mount c \"$WM\""; echo "c:"
echo "set PATH=C:\\V60\\PK"
echo "cd \\AIL"
echo "ML /c /Cx /Fo$N.obj $N.asm > $NU.LOG"
echo "exit"
} > "$CONF"
sed -i 's/$/\r/' "$CONF"
echo "DOSBox startet (schließt sich selbst) ..."
"$DOSBOX" -noconsole -conf "$(wslpath -w "$CONF")" || echo "DOSBox Rückgabe $?"
mkdir -p Analyse/asm_ail
{
echo "=== ML 6.0: $N ($B..$E)"
grep -i "error\|warning" "$W/AIL/$NU.LOG" | head -25
if [ -f "$W/AIL/$NU.OBJ" ]; then python3 Werkzeuge/asm_ail.py vergleich "$B" "$E" "$W/AIL/$NU.OBJ" ${4:-}; else echo "kein OBJ"; tail -15 "$W/AIL/$NU.LOG"; fi
} 2>&1 | tee "Analyse/asm_ail/$N.txt"
