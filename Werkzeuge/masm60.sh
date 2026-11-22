#!/bin/bash
# masm60.sh (21.11.2026) - ML 6.0 und 6.0b aus den Disketten-Abbildern (Compiler/mASM60) holen, in DOSBox
# entpacken und die vier PCLIB-ASM-Dateien damit assemblieren. Dateinamen klein wie im Makefile
# (wmake übergibt sie klein, ML schreibt den Namen so ins OBJ). Vergleich gegen die Original-OBJs vom 05.11.95.
cd "$(dirname "$0")/.." || exit 1
set -o pipefail
Q="Compiler/mASM60"; W="Compiler/ML60"; DOSBOX="${DOSBOX:-$(wslpath -u 'C:\Program Files (x86)\GOG Galaxy\Games\Albion\DOSBOX\DOSBox.exe')}"
B60="$Q/Microsoft Macro Assembler 6.0 (3.5-720k)"; B60B="$Q/Microsoft Macro Assembler 6.0b (3.5-1.44m)"
for v in V60 V60B; do
  mkdir -p "$W/$v/PK"
  rm -rf "$W/$v/ASM" 2>/dev/null; mkdir -p "$W/$v/ASM"; cp -r Compiler/masm611/ASMTEST/PCLIB32 "$W/$v/ASM/" 
  find "$W/$v/ASM" -iname '*.OBJ' -o -iname '*.LOG' | while read -r f; do mv "$f" "$f.611"; done
done
python3 Werkzeuge/fat12.py extract "$B60/disk02.img" "$W/V60/PK" 'ML.E*' || exit 1
python3 Werkzeuge/fat12.py extract "$B60/disk02.img" "$W/V60/PK" 'MLX.EX$' || exit 1
python3 Werkzeuge/fat12.py extract "$B60/disk01.img" "$W/V60/PK" 'DECOMP.EXE' || exit 1
python3 Werkzeuge/fat12.py extract "$B60B/MS-DOS Utilities (016-045-057).img" "$W/V60B/PK" 'ML.E*' || exit 1
python3 Werkzeuge/fat12.py extract "$B60B/MS-DOS Utilities (016-045-057).img" "$W/V60B/PK" 'MLX.EX$' || exit 1
python3 Werkzeuge/fat12.py extract "$B60B/Setup (016-045-056).img" "$W/V60B/PK" 'DECOMP.EXE' || exit 1
WM="$(wslpath -w "$W")"; CONF="$W/ml60_dosbox.conf"
{
echo "[cpu]"; echo "cycles=max"; echo "[autoexec]"
echo "mount c \"$WM\""; echo "c:"
for v in V60 V60B; do
  echo "cd \\$v\\PK"
  for f in ML.EXE ML.ERR MLX.EXE; do b="${f%.*}"; e="${f##*.}"; echo "if not exist $f DECOMP $b.${e:0:2}\$ $f > NUL"; done
  echo "set PATH=C:\\$v\\PK"
  echo "ML > C:\\$v\\VERSION.TXT"
  echo "cd \\$v\\ASM\\PCLIB32\\SRC\\BBOPM"
  echo "ML /Zm /c /Cx /VM /FoOPM_ASS.OBJ opm_ass.asm > ML_OPM.LOG"
  echo "ML /Zm /c /Cx /VM /FoFNT_ASS.OBJ fnt_ass.asm > ML_FNT.LOG"
  echo "cd ..\\BBDSA"
  echo "ML /Zm /c /Cx /VM /FoDSA_ASS.OBJ dsa_ass.asm > ML_DSA.LOG"
  echo "ML /Zm /c /Cx /VM /FoDSA1210.OBJ DSA1210.ASM > ML_D12.LOG"
  echo "cd ..\\BBSYSTEM"
  echo "ML /Zm /c /Cx /VM /FoSYS_ASS.OBJ sys_ass.asm > ML_SYS.LOG"
done
echo "exit"
} > "$CONF"
sed -i 's/$/\r/' "$CONF"
echo "DOSBox startet (schließt sich selbst) ..."
"$DOSBOX" -conf "$(wslpath -w "$CONF")" || echo "DOSBox Rückgabe $?"
for v in V60 V60B; do
  echo "=== ML $v: $(tr -d '\r' < "$W/$v/VERSION.TXT" 2>/dev/null | head -2 | tr '\n' ' ')"
  python3 Werkzeuge/asm_vergleich.py "$W/$v/ASM/PCLIB32/SRC"
done | tee Analyse/masm_test_60.txt
