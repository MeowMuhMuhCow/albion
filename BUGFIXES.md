# Bugfixes

Der Quelltext baut ohne weitere Angaben die unveränderte, bytegleiche `MAIN.EXE`. Jeder Bugfix liegt hinter einem eigenen Schalter (`#ifdef ALB_FIX_...`) und ist damit standardmäßig aus.

Wer die Fixes spielen will, braucht dafür keinen neuen Bau. Er wendet sie als kleinen Patch auf eine **Kopie** seiner `MAIN.EXE` an:

```bash
python3 Werkzeuge/alb_fix.py MAIN.EXE MAIN_FIX.EXE
```

Das Werkzeug prüft zuerst, ob die Eingabe die GOG-Fassung ist (md5), und schreibt dann eine neue Datei. Die Eingabe bleibt unverändert. Danach `MAIN_FIX.EXE` im Spielordner unter dem Namen `MAIN.EXE` verwenden, das Original vorher sichern.

| Schalter | Datei | Fehler | Fix | Patch |
|---|---|---|---|---|
| `ALB_FIX_AUTOMAP_TRAPS` | `src/ALBION/SRC/AUTOMAP.C`, `Insert_automap_events` | Im `case TRAP_AUTO_ICON` fehlt `break;`. Fallen aus Kartenereignissen erscheinen deshalb immer auf der Automap, auch ohne den Zauber, der Fallen sichtbar machen soll. Bei Fallen an Figuren (`Insert_automap_NPCs`) ist dieselbe Regel richtig umgesetzt. | `break;` nach dem Eintragen | 1 Byte: Der Sprung „Fallen nicht zeigen“ führt ans Ende des `case` statt nach `default`. Mit Zauber wird das Symbol wie bisher eingetragen (zweimal an dieselbe Stelle, ohne Wirkung). |

Hinweis zu `#line`: Der Fix steht in einer Datei, die über `Error()` Zeilennummern in die EXE schreibt. Die `#line`-Zeile hinter dem Schalter stellt die Originalzählung wieder her, deshalb bleibt der Bau ohne Schalter bytegleich.
