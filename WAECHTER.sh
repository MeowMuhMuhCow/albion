#!/bin/bash
# WAECHTER.sh (22.11.2026) - führt Bauläufe aus, die über eine Auftragsdatei angestoßen werden.
# Einmal im WSL-Fenster starten, dann läuft er, bis das Fenster zu ist (Strg+C beendet ihn).
# Erlaubt sind NUR feste Befehle aus der Liste unten, nichts Beliebiges:
#   MORGEN        -> bash MORGEN.sh          (alle Stufen)
#   MORGEN <n>    -> bash MORGEN.sh <n>      (ab Stufe n, n = 1..10)
# Auftrag: Bau/auftrag/start (eine Zeile). Ausgabe: Bau/auftrag/log.txt, Ende: Bau/auftrag/fertig (Rückgabecode).
cd "$(dirname "$0")" || exit 1
set -o pipefail
A=Bau/auftrag; mkdir -p "$A"
printf '\033]0;%s\007' "Albion Wächter (wartet)"
echo "Albion-Wächter läuft ($(date +%H:%M)). Wartet auf $A/start ..."
while true; do
  if [ -f "$A/start" ]; then
    zeile="$(head -1 "$A/start" | tr -d '\r')"; mv -f "$A/start" "$A/laeuft"
    rm -f "$A/fertig"
    if [[ "$zeile" =~ ^MORGEN([[:space:]]+([0-9]|10))?$ ]]; then
      ab="${BASH_REMATCH[2]:-1}"
      printf '\033]0;%s\007' "Albion Wächter: MORGEN ab $ab"
      echo "$(date +%H:%M:%S) Auftrag: MORGEN ab Stufe $ab"
      bash MORGEN.sh "$ab" > "$A/log.txt" 2>&1; rc=$?
      tail -3 "$A/log.txt"
    else
      echo "$(date +%H:%M:%S) abgelehnt: '$zeile'" | tee "$A/log.txt"; rc=99
    fi
    echo "$rc $(date +%H:%M:%S)" > "$A/fertig"; mv -f "$A/laeuft" "$A/erledigt"
    printf '\033]0;%s\007' "Albion Wächter (wartet)"
    echo "$(date +%H:%M:%S) fertig (Rückgabe $rc), warte weiter ..."
  fi
  sleep 3
done
