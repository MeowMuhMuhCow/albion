# Rechtliche Hinweise & Lizenz

## 1. Was dieses Repository enthält – und was nicht

Dieses Repository ist ein **nicht-kommerzielles Forschungs-, Dokumentations- und Erhaltungsprojekt** (Software-Archäologie: bytegleiche Rekonstruktion eines historischen Programms).

**Nicht enthalten** (und per `.gitignore` ausgeschlossen):
- **Keine Original-Spieldateien:** keine `MAIN.EXE`, keine Spieldaten, Grafiken, Musik oder Videos von *Albion*.
- **Kein Compiler:** weder Watcom C/C++ 10.0a (Programme, Kopfdateien, Bibliotheken) noch MASM, noch der DOS/4GW-Extender.
- **Keine Miles-Soundbibliothek:** Die Rekonstruktion der in `MAIN.EXE` gebundenen AIL 3.03 (RAD Game Tools / Miles Design) ist fremder, kommerzieller Code und fehlt bewusst.
- **Keine Kopie der Horneman-Schnappschüsse** als eigener Ordner (sie werden nur verlinkt).

Zum Nachbauen braucht man eine **eigene, rechtmäßig erworbene Kopie** von *Albion* (z. B. über [GOG.com](https://www.gog.com/en/game/albion)).

## 2. Rechte am Originalspiel

- *Albion* wurde 1994–1996 von **Blue Byte Software** entwickelt. Die Rechte liegen nach Angabe von Jurie Horneman bei **Ubisoft Entertainment SA**.
- Der Quelltext in `src/` beruht auf den von Jurie Horneman veröffentlichten Schnappschüssen ([github.com/jhorneman/albion](https://github.com/jhorneman/albion)) und wurde für die bytegleiche Rekonstruktion ergänzt und korrigiert. **Für diesen Spielcode werden keinerlei Rechte beansprucht**, und dieses Dokument erteilt dafür keine Lizenz.
- Dieses Projekt steht in keiner Verbindung zu Ubisoft oder Blue Byte. Wenn die Rechteinhaber es wünschen, wird es entfernt.

## 3. Lizenz der eigenen Werkzeuge

Die für dieses Projekt neu geschriebenen Skripte in `Werkzeuge/` sowie `MORGEN.sh`, `WAECHTER.sh` und `AIL_ASM.sh` stehen unter der **MIT-Lizenz** (siehe [`Werkzeuge/LICENSE`](Werkzeuge/LICENSE)).
