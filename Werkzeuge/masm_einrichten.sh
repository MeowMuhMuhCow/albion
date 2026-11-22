#!/bin/bash
# masm_einrichten.sh (21.11.2026) - MASM 6.11 aus den Disketten entpacken (DECOMP in DOSBox) und
# (wie im Makefile: ml /Zm /c /Cx /VM /Fo... Datei; /VM kennt ML 6.11 nicht und verschluckt das nächste Argument)
# die vier PCLIB-ASM-Dateien vom 05.11.95 probehalber assemblieren. DOSBox aus dem GOG-Ordner wird nur
# AUSGEFÜHRT, dort wird nichts geschrieben. Ergebnis: Compiler/masm611/BIN, Analyse/masm_test.txt
cd "$(dirname "$0")/.." || exit 1
set -o pipefail
M="Compiler/masm611"; S="Referenz_Horneman/horneman_albion/MS-DOS/051195/PCLIB32"
DOSBOX="${DOSBOX:-$(wslpath -u 'C:\Program Files (x86)\GOG Galaxy\Games\Albion\DOSBOX\DOSBox.exe')}"
[ -x "$DOSBOX" ] || { echo "DOSBox nicht gefunden: $DOSBOX"; exit 1; }
mkdir -p "$M/BIN" "$M/ASMTEST/PCLIB32/LIB/ASMINC" "$M/ASMTEST/PCLIB32/SRC/BBOPM" "$M/ASMTEST/PCLIB32/SRC/BBDSA" "$M/ASMTEST/PCLIB32/SRC/BBSYSTEM"
cp "$S/LIB/ASMINC/BBMACRO.INC" "$S/LIB/ASMINC/BBHARD.INC" "$M/ASMTEST/PCLIB32/LIB/ASMINC/"
cp "$S/SRC/BBOPM/OPM_ASS.ASM" "$S/SRC/BBOPM/FNT_ASS.ASM" "$M/ASMTEST/PCLIB32/SRC/BBOPM/"
cp "$S/SRC/BBDSA/DSA_ASS.ASM" "$M/ASMTEST/PCLIB32/SRC/BBDSA/"
cp "$S/SRC/BBSYSTEM/SYS_ASS.ASM" "$M/ASMTEST/PCLIB32/SRC/BBSYSTEM/"
WM="$(wslpath -w "$M")"
CONF="$M/masm_dosbox.conf"
cat > "$CONF" <<KONF
[cpu]
cycles=max
[autoexec]
mount c "$WM"
c:
if not exist BIN\\ML.EXE DISK1\\DECOMP DISK1\\BIN\\ML.EX\$ BIN\\ML.EXE > BIN\\ENTP1.LOG
if not exist BIN\\ML.ERR DISK1\\DECOMP DISK1\\BIN\\ML.ER\$ BIN\\ML.ERR > BIN\\ENTP2.LOG
if not exist BIN\\DOSXNT.EXE DISK1\\DECOMP DISK1\\BIN\\DOSXNT.EX\$ BIN\\DOSXNT.EXE > BIN\\ENTP3.LOG
if not exist BIN\\DOSXNT.386 DISK1\\DECOMP DISK1\\BIN\\DOSXNT.38\$ BIN\\DOSXNT.386 > BIN\\ENTP4.LOG
set PATH=C:\\BIN
cd \\ASMTEST\\PCLIB32\\SRC\\BBOPM
ML /Zm /c /Cx /VM /FoOPM_ASS.OBJ OPM_ASS.ASM > ML_OPM.LOG
ML /Zm /c /Cx /VM /FoFNT_ASS.OBJ FNT_ASS.ASM > ML_FNT.LOG
cd ..\\BBDSA
ML /Zm /c /Cx /VM /FoDSA_ASS.OBJ DSA_ASS.ASM > ML_DSA.LOG
cd ..\\BBSYSTEM
ML /Zm /c /Cx /VM /FoSYS_ASS.OBJ SYS_ASS.ASM > ML_SYS.LOG
exit
KONF
sed -i 's/$/\r/' "$CONF"
echo "DOSBox startet (Fenster geht nach dem Lauf von selbst zu) ..."
"$DOSBOX" -conf "$(wslpath -w "$CONF")" || echo "DOSBox Rückgabe $?"
ls -la "$M/BIN"
python3 Werkzeuge/asm_vergleich.py | tee Analyse/masm_test.txt
