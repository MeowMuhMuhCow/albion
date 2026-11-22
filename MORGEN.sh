#!/bin/bash
# MORGEN.sh (22.11.2026) - Albion Morgenlauf in einem Rutsch:
#  1 OBJs neu (MAIN/GAMETEXT/FONT/PCLIB geändert)   2 Daten-Karte   3 Code-Karte + Bilanz
#  4 neue AIL-Module messen (0xa9b04, 0xacde0, 0xaefd0)   5 AIL-OBJs bauen
#  6 Linkliste + WLINK in DOSBox (Probebau)   7 EXE-Vergleich
# Jede Stufe schreibt nach Analyse/morgen/<n>_<name>.txt, Übersicht in Analyse/morgen/ZUSAMMENFASSUNG.txt
# Aufruf: bash MORGEN.sh [ab-Stufe]
cd "$(dirname "$0")" || exit 1
set -o pipefail
printf '\033]0;%s\007' "Albion Morgenlauf"
AB="${1:-1}"
# Stufe 0 = nur Probe: Bau/auftrag/probe.sh ausfuehren (fuer Messungen zwischen den Laeufen)
if [ "$AB" = 0 ]; then printf '\033]0;%s\007' "Albion Probe"; bash Bau/auftrag/probe.sh; exit $?; fi
L="Analyse/morgen"; mkdir -p "$L"
Z="$L/ZUSAMMENFASSUNG.txt"; [ "$AB" = 1 ] && : > "$Z"
DOSBOX="${DOSBOX:-$(wslpath -u 'C:\Program Files (x86)\GOG Galaxy\Games\Albion\DOSBOX\DOSBox.exe')}"

stufe() {   # stufe NR NAME BEFEHL...
  local nr="$1" nm="$2"; shift 2
  [ "$nr" -lt "$AB" ] && return 0
  local f="$L/${nr}_${nm}.txt" t0=$SECONDS
  printf '\033]0;%s\007' "Albion Morgenlauf $nr/10 $nm"
  echo "=== Stufe $nr: $nm  ($(date +%H:%M:%S))"
  "$@" > "$f" 2>&1; local rc=$?
  tail -12 "$f"
  echo "--- Stufe $nr $nm: Rückgabe $rc, $((SECONDS - t0)) s" | tee -a "$Z"
  tail -6 "$f" | sed 's/^/    /' >> "$Z"
  return 0
}

ail_plan() {
  for b in 0xa9b04 0xacde0 0xae988 0xaefd0 0xb24b0; do
    echo "##### Modul $b"; python3 Werkzeuge/ail_modul.py "$b" --plan || echo "Rückgabe $?"
  done
}

asm_teile() {
  python3 Werkzeuge/ail_daten.py || return 1
  python3 Werkzeuge/alias_bau.py || return 1
  echo "--- AIL32/DMASND32 neu (öffentliche Einsprünge)"
  bash AIL_ASM.sh 0xac320 0xacd17 ail32 | tail -2
  bash AIL_ASM.sh 0xc2dec 0xc4f21 dmasnd32 rekursiv | tail -2
  echo "--- AIL-Datenmodule mit ML 6.0"
  local W="Compiler/ML60" CONF="Compiler/ML60/ail_daten_dosbox.conf" N
  for N in AILCD A9B04D AIL32D DMASNDD KEYD; do
    rm -f "$W/AIL/$N.OBJ"; cp "src/AIL/ASM/$N.ASM" "$W/AIL/$N.ASM" || return 1
  done
  {
    echo "[cpu]"; echo "cycles=max"; echo "[autoexec]"
    echo "mount c \"$(wslpath -w "$W")\""; echo "c:"
    echo "set PATH=C:\\V60\\PK"; echo "cd \\AIL"
    for N in AILCD A9B04D AIL32D DMASNDD KEYD; do echo "ML /c /Cx /Fo$N.OBJ $N.ASM > $N.LOG"; done
    echo "exit"
  } > "$CONF"
  sed -i 's/$/\r/' "$CONF"
  "$DOSBOX" -noconsole -conf "$(wslpath -w "$CONF")" || echo "DOSBox Rückgabe $?"
  for N in AILCD A9B04D AIL32D DMASNDD KEYD; do
    if [ -f "$W/AIL/$N.OBJ" ]; then echo "$N.OBJ ok"; A=--leer-byte; [ "$N" = KEYD ] && A=--leer-para; python3 Werkzeuge/omf_inl.py $A "$W/AIL/$N.OBJ" || return 1; else echo "$N: kein OBJ"; grep -i "error" "$W/AIL/$N.LOG" | head -5; fi
  done
}

wlink_dosbox() {
  python3 Werkzeuge/bau_liste.py | tail -2 || return 1
  python3 Werkzeuge/bau_link.py --probe || return 1
  dosbox_link || return 1
  # Krücke: Satzrahmen der OBJs wie im Original (Reihenfolge der LE-Fixup-Tabelle), dann neu linken
  python3 Werkzeuge/fixup_folge.py | tail -4; local rc=${PIPESTATUS[0]}
  if [ "$rc" = 2 ]; then echo "--- neu linken (Fixup-Folge)"; dosbox_link || return 1
  elif [ "$rc" != 0 ]; then echo "fixup_folge Rückgabe $rc"; return 1; fi
}

dosbox_link() {
  local D="Bau/DOS" W="Compiler/w100a" CONF="Bau/DOS/wlink_dosbox.conf"
  rm -f "$D/MAIN.EXE" "$D/MAIN.MAP" "$D/WLINK.LOG"
  {
    echo "[cpu]"; echo "cycles=max"; echo "[dos]"; echo "files=200"; echo "[autoexec]"
    echo "mount c \"$(wslpath -w "$D")\""
    echo "mount w \"$(wslpath -w "$W")\""
    echo "c:"
    echo "set WATCOM=W:\\"
    echo "set PATH=W:\\BINB;W:\\BIN"
    echo "set DOS4G=QUIET"
    echo "WLINK @C:\\MAIN.LNK > C:\\WLINK.LOG"
    echo "exit"
  } > "$CONF"
  sed -i 's/$/\r/' "$CONF"
  echo "DOSBox startet WLINK (schließt sich selbst) ..."
  "$DOSBOX" -noconsole -conf "$(wslpath -w "$CONF")" || echo "DOSBox Rückgabe $?"
  echo "--- WLINK.LOG (Fehler/Warnungen)"
  grep -i "error\|warning\|undefined\|cannot" "$D/WLINK.LOG" | head -40
  echo "--- Ende WLINK.LOG"; tail -8 "$D/WLINK.LOG"
  echo "--- fehlende OBJs"; grep -c '^FEHLT' Bau/link_liste.txt; grep '^FEHLT' Bau/link_liste.txt | head -20
  [ -f "$D/MAIN.EXE" ] && ls -l "$D/MAIN.EXE" || { echo "keine MAIN.EXE"; return 1; }
}

stufe 1 objs     python3 Werkzeuge/bau_objs.py 4
stufe 2 daten    python3 Werkzeuge/daten.py
stufe 3 karte    bash -c 'python3 Werkzeuge/albion.py karte && python3 Werkzeuge/albion.py bilanz'
stufe 4 ailplan  ail_plan
stufe 5 ailobjs  python3 Werkzeuge/bau_ail.py
stufe 6 asm      asm_teile
stufe 7 wlink    wlink_dosbox
stufe 8 exe      bash -c 'if [ -f Bau/DOS/MAIN.EXE ]; then python3 Werkzeuge/exe_vergleich.py; else echo "keine MAIN.EXE, kein Vergleich"; exit 1; fi'
stufe 9 aufrufe  bash -c 'if [ -f Bau/DOS/MAIN.EXE ]; then python3 Werkzeuge/aufruf_vergleich.py && head -40 Analyse/aufruf_vergleich.txt; else exit 1; fi'
stufe 10 datenlage bash -c 'if [ -f Bau/DOS/MAIN.EXE ]; then python3 Werkzeuge/daten_lage.py; else exit 1; fi'
printf '\033]0;%s\007' "Albion Morgenlauf fertig"
echo; echo "=== fertig $(date +%H:%M). Übersicht: $Z"
cat "$Z"
