#!/bin/bash
# ail_diag.sh - für die festgefahrenen AIL-Familien (Rest 14/15, gleiche Muster) den Vergleich Original/eigene
# Übersetzung in eine Datei schreiben, damit die gemeinsame Ursache gefunden werden kann. Nur lesend.
cd "$(dirname "$0")/.." || exit 1
OUT=Analyse/ail_diag.txt; : > "$OUT"
for adr in 0x8cb2e 0x8c3d8 0x8f179 0x90cde 0x8d4ef 0x8f01f 0x911bf 0x8cf4c; do
  python3 - "$adr" >> "$OUT" 2>&1 <<'PY'
import sys, os, json
sys.path.insert(0, 'Werkzeuge'); import ail_richter as R
adr = sys.argv[1]; p = os.path.join(R.REKO, R.name_von(adr).upper() + '.C')
os.makedirs('work/DIAG', exist_ok=True)
json.dump({'id': 'DIAG', 'funktion': adr, 'laenge': R.funktionen()[adr]['laenge'], 'datei': p, 'start': R.jetzt()}, open('work/DIAG/auftrag.json', 'w'))
print('#' * 30, adr, '#' * 30)
print(open(p, encoding='latin1').read() if os.path.exists(p) else '(keine Datei)')
class X: id = 'DIAG'
R.cmd_zeigen(X())
PY
done
rm -f work/DIAG/auftrag.json
echo "fertig: $OUT ($(wc -l < "$OUT") Zeilen)"
