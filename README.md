# Albion (Blue Byte, 1995) – bytegleiche Rekonstruktion von MAIN.EXE

Rekonstruierter C-Quelltext von **Albion** (Blue Byte Software, 1995/96), aus dem sich das Hauptprogramm **`MAIN.EXE`** der heutigen GOG-Fassung **bytegleich** bauen lässt.

Man übersetzt den Quelltext mit dem historischen **Watcom C 10.0a**, assembliert die Assemblerteile mit **MASM 6.0** und bindet mit **wlink 10.0**. Heraus kommt eine `MAIN.EXE`, die in **allen 1.109.655 Bytes** mit dem Original übereinstimmt.

| Kennzahl | Wert |
|---|---|
| **Zieldatei** | `MAIN.EXE` (GOG-Fassung von *Albion*) |
| **Größe** | `1.109.655` Bytes |
| **MD5** | `c4171d5eb0ebd36b132e081f8362a075` |
| **Compiler** | Watcom C 10.0a `wcc386`, Debug-Build: `-w1 -d2 -od -5r` (schnelle Module `-ox`) |
| **Assembler / Linker** | MASM 6.0 (`ml /c /Cx`), Watcom wlink 10.0, DOS/4GW |
| **Übersetzungseinheiten** | 109 C-Einheiten (Spiel und Blue-Byte-Bibliothek PCLIB32), dazu Assemblerteile und Watcom-Laufzeit |
| **Funktionen** | rund 2.170 in `MAIN.EXE`, fast alle mit Originalnamen; jede mit Funktionskopf (Zweck, Eingaben, Rückgabe), Übersicht in [`KATALOG.md`](KATALOG.md) |
| **Übereinstimmung** | 100 %: alle 8 LE-Objekte, Kopf und Fixup-Tabelle; md5 gleich, auch bei einem Bau ohne Zwischenspeicher |

> **Wichtig:** Dieses Repository enthält **keine Spieldaten**, **keine `MAIN.EXE`**, **keinen Compiler** und **nicht** die Rekonstruktion der Miles-Soundbibliothek AIL 3.03 (fremder, kommerzieller Code). Zum Nachbauen braucht man eine eigene legale Kopie von *Albion* (z. B. von [GOG.com](https://www.gog.com/en/game/albion)). Siehe [`RECHTE.md`](RECHTE.md).

---

## Herkunft des Quelltexts

Grundlage sind die Quelltext-Schnappschüsse, die **Jurie Horneman** (Albion-Entwickler bei Blue Byte) veröffentlicht hat: [github.com/jhorneman/albion](https://github.com/jhorneman/albion). Nach seinem Hinweis sind sie unvollständig und lassen sich so nicht zum fertigen Spiel bauen.

Ausgangspunkt war der Stand vom 22.11.1995. Fehlende Module kamen aus den Schnappschüssen vom 05.11. und 12.10.1995. Danach wurde der Quelltext Funktion für Funktion so lange ergänzt und korrigiert, bis jede Funktion, jede Variable und jede Tabelle mit der ausgelieferten Fassung übereinstimmt. Der fertige Code ist ein **Debug-Build** ohne Debug-Info in der EXE.

Einige Befunde unterwegs:
- **GAME.C:** Zwei Init-Aufrufe standen vertauscht.
- **BBEVENT:** Statt der Tastaturroutinen wurde `SYSTEM_SystemTask` aufgerufen.
- **XFTYPES:** Die Tabelle enthielt ein Flag, das es in dieser Fassung noch nicht gab.
- **Sprache:** Voreingestellt ist Englisch.

## Aufbau

| Ordner / Datei | Inhalt |
|---|---|
| `src/ALBION/` | Spiel: `SRC/` (Module), `LIB/` (Kopfdateien), `OUTSIDE/` (Fremdteile, z. B. `ZOOM.ASM`) |
| `src/PCLIB32/` | Blue-Byte-Bibliothek PCLIB32 (Speicher, Grafik/OPM, DSA, Ereignisse, DOS, System) |
| `KATALOG.md` | Funktionskatalog: was jede Quelldatei im Spiel macht und was jede Funktion tut |
| `Werkzeuge/` | Bauwerkzeuge (Python, Shell), Linkfolge, OMF-/LE-Werkzeuge |
| `MORGEN.sh` | kompletter Bau in 10 Stufen (OBJs, Daten, Karte, AIL, Assembler, wlink, Vergleich) |
| `WAECHTER.sh` | startet Bauläufe über eine Auftragsdatei (`Bau/auftrag/start`) |
| `Analyse/MD5_MEILENSTEIN.md` | Abschlussbericht: was echte Befunde sind und was Krücken |
| `Analyse/NACHT_LOG.md` | Arbeitsprotokoll |
| `Analyse/ERSTE_BILANZ.md` | erste Messung und Eichung des Compilers |

## Funktionen verstehen

Jede Funktion hat im Quelltext einen Kopf im Stil von Blue Byte:

```c
/*
 ******************************************************************************
 * #FUNCTION HEADER BEGIN#
 * NAME      : Do_Chest
 * FUNCTION  : Enter Chest screen.
 * INPUTS    : UNSHORT Locked_percentage - Locked percentage (100 = cannot
 *              be picked).
 *             ...
 * RESULT    : UNSHORT : Chest status (see CHEST.H).
 * #FUNCTION HEADER END#
 */
```

Rund 2.090 dieser Köpfe sind Originale der Entwickler. Für die übrigen knapp 180 Funktionen gab es keinen Kopf. Sie haben bei der Rekonstruktion einen bekommen, erkennbar an `AUTHOR : - (no original header; written for the reconstruction)`.

[`KATALOG.md`](KATALOG.md) fasst alles zusammen: je Quelldatei ein Satz, was das Modul im Spiel macht, und darunter alle Funktionen mit Zweck und Zeilennummer.

**Warum manchmal `#line` hinter einem Kopf steht:** Viele Module übergeben mit Makros wie `Error()` die Zeilennummer (`__LINE__`) an die Fehlerbehandlung, und diese Zahl landet in der EXE. Ein neuer Kommentarblock würde alle folgenden Nummern verschieben und `MAIN.EXE` wäre nicht mehr bytegleich. Die `#line`-Zeile stellt die Originalnummerierung wieder her.

## Krücken (offengelegt)

Nicht jedes Byte der Datei folgt aus dem Programm. Wo der Bau Hilfe braucht, ist das hier ausgewiesen:

| Krücke | Warum |
|---|---|
| Einige Variablennamen sind gewählt (`prev_int_9/8`, `XLD_Batch_data/ptr`, `Demo_flags`), dazu eine zusätzliche `extern`-Deklaration in `BBDSA.C` | Watcom ordnet nicht initialisierte Variablen über ihre Namen. Die echten Namen sind nicht bekannt |
| 27 Füllbytes aus dem Original (`Werkzeuge/fuellbytes.py`) | Der Compiler füllte Ausrichtungslücken mit Resten aus seinem Speicher. Das ist kein Programminhalt |
| Satzgrenzen der OBJs nach dem Original (`Werkzeuge/fixup_folge.py`) | Bestimmt nur die Reihenfolge der Fixup-Tabelle in der EXE, keine Bytes. Ursache sind Debug-Sätze und die damalige Bauumgebung |
| Kleinere OMF-Nacharbeiten (`Werkzeuge/omf_inl.py`) | betreffen nur die AIL-Teile |

Zur Fixup-Tabelle: wlink legt die Fixups jeder 4-KB-Seite in Blöcken zu 512 Byte ab. Der neueste Block steht zuerst, und jeder FIXUPP-Satz landet darin rückwärts. Daraus lässt sich die damalige Aufteilung der Objektdateien aus der Original-EXE zurückrechnen.

## Selbst bauen

Der Bau läuft unter **WSL** (Linux unter Windows) mit **DOSBox**. Das ist die aus der GOG-Installation; der Pfad lässt sich über die Variable `DOSBOX` setzen. Gebraucht werden:

1. **Eigene `MAIN.EXE`** aus der GOG-Installation nach `Original/MAIN.EXE` kopieren (siehe [`Original/HIER_MAIN_EXE_REIN.txt`](Original/HIER_MAIN_EXE_REIN.txt)).
2. **Watcom C/C++ 10.0a**: die 10.0-CD mit Patchlevel A. `Werkzeuge/watcom_apatch.py` wendet den Patch ohne DOS an, das Ergebnis kommt nach `Compiler/w100a/` (siehe [`Compiler/HIER_COMPILER_REIN.txt`](Compiler/HIER_COMPILER_REIN.txt)).
3. **MASM 6.0**, eingerichtet mit `Werkzeuge/masm60.sh` nach `Compiler/ML60/`.
4. **Horneman-Schnappschüsse** nach `Referenz_Horneman/horneman_albion/` klonen ([jhorneman/albion](https://github.com/jhorneman/albion)). Daraus kommen Referenz-OBJs und Bibliotheksstände.
5. **Byte-exact Decomp Toolkit** nach `Werkzeuge/byte-exact-decomp-toolkit/` klonen ([MeowMuhMuhCow/byte-exact-decomp-toolkit](https://github.com/MeowMuhMuhCow/byte-exact-decomp-toolkit)). Daraus kommen der Compiler-Emulator und die OMF/LE-Grundlagen.
6. Python 3 mit `unicorn` und `capstone` (`Werkzeuge/python_pakete.sh`).

Dann:

```bash
bash MORGEN.sh        # alle Stufen; Ergebnis Bau/DOS/MAIN.EXE, Vergleich in Analyse/morgen/8_exe.txt
```

**Einschränkung:** Die AIL-3.03-Teile (Miles Sound System) sind nicht enthalten, weil sie fremder Code sind. Ohne sie scheitern die AIL-Stufen 4 und 5, und das Ergebnis ist nicht vollständig. Den Spiel- und Bibliotheksteil kann man trotzdem übersetzen und Funktion für Funktion gegen das Original prüfen.

## Dank

- **Jurie Horneman** für die Veröffentlichung der Albion-Schnappschüsse, ohne die es diese Arbeit nicht gäbe.
- Dem **Albion-Team von Blue Byte** (1994–1996).
- Die Methode dahinter ist im Byte-exact Decomp Toolkit beschrieben; Albion ist nach der Nordlandtrilogie der zweite Fall.

MooMoo, November 2026.
