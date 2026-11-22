#!/bin/bash
# masm60_zoom.sh (21.11.2026) - Objekt 6 von MAIN.EXE: ZOOM.ASM (Rainer, ZOOMFUNC-Bibliothek) mit ML 6.0 assemblieren
# und gegen ZOOM.OBJ vom 12.10.95 vergleichen (dieses OBJ steckt byteweise in MAIN.EXE).
# Makefile 12.10.: ml /VM /Zm /c /Cx /Fo...ZOOM.OBJ ...ZOOM.ASM ; Includes absolut g:\PCLIB32\LIB\ASMINC\...
cd "$(dirname "$0")/.." || exit 1
set -o pipefail
W="Compiler/ML60"; R="Referenz_Horneman/horneman_albion/MS-DOS"
DOSBOX="${DOSBOX:-$(wslpath -u 'C:\Program Files (x86)\GOG Galaxy\Games\Albion\DOSBOX\DOSBox.exe')}"
[ -f "$W/V60/PK/ML.EXE" ] || { echo "erst bash Werkzeuge/masm60.sh"; exit 1; }
mkdir -p "$W/G/PCLIB32/LIB/ASMINC" "$W/ZOOM"
cp "$R/051195/PCLIB32/LIB/ASMINC/BBMACRO.INC" "$R/051195/PCLIB32/LIB/ASMINC/BBHARD.INC" "$W/G/PCLIB32/LIB/ASMINC/"
cp "$R/221195/ALBION/OUTSIDE/RAINER/SRC/ZOOMFUNC/ZOOM.ASM" "$W/ZOOM/ZOOM.ASM"
CONF="$W/zoom_dosbox.conf"
{
echo "[cpu]"; echo "cycles=max"; echo "[autoexec]"
echo "mount c \"$(wslpath -w "$W")\""; echo "mount g \"$(wslpath -w "$W/G")\""; echo "c:"
echo "set PATH=C:\\V60\\PK"
echo "cd \\ZOOM"
echo "ML /VM /Zm /c /Cx /FoZOOM.OBJ ZOOM.asm > ML_ZOOM.LOG"
echo "exit"
} > "$CONF"
sed -i 's/$/\r/' "$CONF"
"$DOSBOX" -conf "$(wslpath -w "$CONF")" || echo "DOSBox Rückgabe $?"
python3 - "$W/ZOOM/ZOOM.OBJ" "$R/121095/ALBION/SRC/ZOOMFUNC/OBJS/ZOOM.OBJ" "$W/ZOOM/ML_ZOOM.LOG" <<'PY'
import os, sys
sys.path.insert(0, 'Werkzeuge/byte-exact-decomp-toolkit/02_basis'); import omf
neu, alt, log = sys.argv[1:4]
if not os.path.exists(neu):
    print('kein OBJ:', open(log, errors='replace').read()[-500:] if os.path.exists(log) else '(kein Log)'); sys.exit(1)
a, b = open(neu, 'rb').read(), open(alt, 'rb').read()
sa = {s['name']: s for m in omf.modules(neu) for s in m['segs'].values()}
sb = {s['name']: s for m in omf.modules(alt) for s in m['segs'].values()}
for n in sorted(set(sa) | set(sb)):
    x, y = sa.get(n), sb.get(n)
    if not x or not y: print(n, 'nur in', 'neu' if x else 'alt'); continue
    print(f"{n}: {len(x['data'])}/{len(y['data'])} B, abweichend {sum(1 for k in range(min(len(x['data']), len(y['data']))) if x['data'][k] != y['data'][k])}")
print('ZOOM.OBJ:', 'IDENTISCH' if a == b else f'verschieden ({len(a)}/{len(b)} B)')
PY
