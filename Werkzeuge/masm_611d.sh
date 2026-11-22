#!/bin/bash
# masm_611d.sh (21.11.2026) - MASM 6.11d aus 6.11 + Microsoft-Patch (Compiler/masm611/PATCH/ML611D.EXE) bauen
# und die vier PCLIB-ASM-Dateien damit assemblieren. Grund: ML 6.11 kodiert Register-Register-Befehle anders
# (38 statt 3A) als die Original-OBJs. 6.11 bleibt unverändert in BIN, 6.11d entsteht in M611D/BIN.
cd "$(dirname "$0")/.." || exit 1
set -o pipefail
M="Compiler/masm611"; DOSBOX="${DOSBOX:-$(wslpath -u 'C:\Program Files (x86)\GOG Galaxy\Games\Albion\DOSBOX\DOSBox.exe')}"
[ -f "$M/BIN/ML.EXE" ] || { echo "erst bash Werkzeuge/masm_einrichten.sh"; exit 1; }
mkdir -p "$M/M611D/BIN"
# DSA_ASS vom 12.10. zusätzlich (05.11. ergibt 1 Byte mehr als das Original-OBJ)
cp "Referenz_Horneman/horneman_albion/MS-DOS/121095/PCLIB32/SRC/BBDSA/DSA_ASS.ASM" "$M/ASMTEST/PCLIB32/SRC/BBDSA/DSA1210.ASM"
if [ ! -f "$M/M611D/GEPATCHT" ]; then
  cp "$M/BIN/ML.EXE" "$M/BIN/ML.ERR" "$M/BIN/DOSXNT.EXE" "$M/BIN/DOSXNT.386" "$M/M611D/BIN/"
  cp "$M/PATCH611D/PATCH.EXE" "$M/PATCH611D/PATCH.RTD" "$M/PATCH611D/PATCH.RTP" "$M/M611D/"
fi
WM="$(wslpath -w "$M")"; CONF="$M/masm611d_dosbox.conf"
cat > "$CONF" <<KONF
[cpu]
cycles=max
[autoexec]
mount c "$WM"
c:
cd \\M611D
if not exist GEPATCHT PATCH
if not exist GEPATCHT echo ok > GEPATCHT
set PATH=C:\\M611D\\BIN
ML > C:\\M611D\\VERSION.TXT
cd \\ASMTEST\\PCLIB32\\SRC\\BBOPM
ML /Zm /c /Cx /VM /FoOPM_ASS.OBJ OPM_ASS.ASM > ML_OPM.LOG
ML /Zm /c /Cx /VM /FoFNT_ASS.OBJ FNT_ASS.ASM > ML_FNT.LOG
cd ..\\BBDSA
ML /Zm /c /Cx /VM /FoDSA_ASS.OBJ DSA_ASS.ASM > ML_DSA.LOG
ML /Zm /c /Cx /VM /FoDSA1210.OBJ DSA1210.ASM > ML_D12.LOG
cd ..\\BBSYSTEM
ML /Zm /c /Cx /VM /FoSYS_ASS.OBJ SYS_ASS.ASM > ML_SYS.LOG
exit
KONF
sed -i 's/$/\r/' "$CONF"
echo "DOSBox startet: zuerst läuft der Microsoft-Patch sichtbar (Fragen dort mit j/y beantworten), dann assembliert es."
"$DOSBOX" -conf "$(wslpath -w "$CONF")" || echo "DOSBox Rückgabe $?"
echo "ML-Version:"; tr -d '\r' < "$M/M611D/VERSION.TXT" | head -3
python3 Werkzeuge/asm_vergleich.py | tee Analyse/masm_test_611d.txt
