# MAIN.EXE md5-gleich – 22.11.2026

`Bau/DOS/MAIN.EXE` = `Original/MAIN.EXE`, 1 109 655 Bytes, md5 `c4171d5eb0ebd36b132e081f8362a075`.
Ein kompletter Lauf (`MORGEN 1`, Stufen 1–10) baut sie reproduzierbar aus Quellen, Bibliotheken und Werkzeugen.
Auch mit leerem OBJ-Cache (alles neu übersetzt, 18:20) kommt dieselbe md5 heraus.

## Krücken (für das Paper offenlegen)

| Krücke | Wo | Warum |
|---|---|---|
| Namen `prev_int_9/8`, `XLD_Batch_data/ptr`, `Demo_flags` | BBSYSTEM.C, XLOAD.C, GAME.C | Watcom ordnet _BSS über die Namen; die echten Namen sind nicht bekannt |
| Zusätzliche `extern void _DSA_ASS_FLASH( void );` vor `chain4lastwriteselect` | BBDSA.C | BSS-Reihenfolge; die Deklaration ändert keinen Code |
| INL_TEXT-Kopien leeren | omf_inl.entfernen, bau_ail | Watcom gibt eingebettete statische Funktionen zusätzlich aus |
| 0xb24b0 als eigene Einheit, Watcom-Füllung `8d 40 00 8b c9` am Ende von 0xaefd0 | ail_modul, omf_inl.auffuellen | b24b0 ruft F_af150, statt es einzubetten |
| Leere _TEXT der AIL-Datenmodule auf Byte (KEYD: PARA) | omf_inl.leer_byte, MORGEN.sh | die Datenmodule sind eine Aufteilung von uns, im Original lagen die Daten in den AIL-Modulen |
| 27 Füllbytes aus dem Original | fuellbytes.py | Reste aus dem Compiler-Speicher des damaligen Baurechners, kein Programminhalt |
| Satzgrenzen der OBJs nach dem Original | fixup_folge.py | Reihenfolge der LE-Fixup-Tabelle; hängt an Debug-Sätzen und Bauumgebung, keine Bytes |

## Was wirklich gefunden wurde (keine Krücke)

- Linkfolge leerer, ausgerichteter Segmente (ZOOM, OPM_ASS, FNT_ASS, STDMOUSP, KEYD, 3DM data, stinit, seg386, environ, umaskval, heapmod, ___argc, minreal)
- Quellfehler der Rekonstruktion: GAME.C (Aufrufe vertauscht), BBEVENT (Tastaturaufrufe), AIL_preference-Indizes, Notentabelle, XFTYPES-Flags, Sprache ENGLISH
- wlink-Modell der Fixup-Tabelle: Blöcke zu 512 B je Seite, neuester zuerst, FIXUPP-Sätze rückwärts
