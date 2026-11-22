# Erste Bilanz – 21.11.2026

## Emulator (Schritt 1)

`Werkzeuge/emu100a.py`: WCC386 10.0a (CF-Image aus `Compiler/w100a/BINB`) im Unicorn-Emulator, Mechanik von `emu106`. Int-21h-Stub 0x2FED3, Exit 0x2FED1. Etwa 0,05–3 s pro Modul.

## Eichung gegen Hornemans OBJs (Snapshot 12.10.95, `ALBION/LIB`)

| Flags | Ergebnis |
|---|---|
| `-w1 -d0 -ox -5r` | 13 Module **vollständig gleich** (alle Segmente) |
| `-w1 -d2 -od -5r` | 64 Module **Code gleich**. Nur die Debug-Typinfo ist um 25 Bytes je Pfad länger (andere Include-Pfade) |
| Rest | 2 Module ohne Header (`DLL.H`, AIL 3.03) |

77 von 79 Modulen sind bytegleich. Der Emulator ist damit **bewiesen**.

## Bilanz Snapshot 22.11.95 gegen MAIN.EXE

**Überraschung:** Die ausgelieferte MAIN.EXE ist ein **Debug-Build ohne Debug-Info im EXE**.
- Normale Module: `wcc386 -w1 -d2 -od -5r`
- „Schnelle“ Module (`Fast_compiler`): `wcc386 -w1 -d2 -ox -5r` → 2D_DISPL, FASTFLC, FINDCOL, FLC, GFXFUNC, SCROLL, SORT
- `-d2` verändert den Code gegenüber `-d0`. Das Production-Flag `-d0 -ox` aus dem Makefile passt **nicht**.

| Teil | Module | komplett gleich | Funktionsstücke gleich | Bytes gleich |
|---|---|---|---|---|
| Spiel (`ALBION/SRC`) | 54 | 10 | 736 / 999 (73,7 %) | 241 890 / 301 923 (80,1 %) |
| PCLIB32 (C-Teile) | 7 | 0 | 76 / 110 (69,1 %) | 13 266 / 23 077 (57,5 %) |
| **Gesamt** | 61 | 10 | **812 / 1 109 (73,2 %)** | **255 156 / 325 000 (78,5 %)** |

„Stück“ = Code von einem Public bis zum nächsten. Statische Funktionen hängen am vorigen Public. Fixup-Bytes sind maskiert, und das Stück muss genau einmal im Bild vorkommen.

## Noch nicht erfasst

- Module, die im Snapshot 22.11.95 fehlen (ANIMATE … XFTYPES, siehe stand.md): aus 05.11./12.10. nehmen
- PCLIB32 BBSYSTEM: Symbol `CHAIN4` fehlt (Header-Stand)
- MAIN, MUSIC: `DLL.H` und der AIL-3.03-Header fehlen. Von DLLLOAD gibt es nur ein OBJ (`PROJECT/SWAPALIA/LIB/DLLLOAD.OBJ`)
- Miles AIL 3.03 (Sound-Bibliothek, fremder Code) ist in MAIN.EXE gelinkt, eine Quelle haben wir nicht
- 9 Assembler-Dateien (MASM)
- Watcom-CLIB: 118 Module bereits exakt (aus der Lib, keine Rekonstruktion nötig)
