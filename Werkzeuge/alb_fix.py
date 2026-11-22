#!/usr/bin/env python3
"""alb_fix.py - Bugfixes fuer Albion MAIN.EXE als kleiner Binaerpatch.

Arbeitet nur auf einer Kopie: liest MAIN.EXE (muss die GOG-Fassung sein, md5 wird geprueft)
und schreibt eine neue Datei. Die Eingabedatei wird nie veraendert.

    python3 alb_fix.py MAIN.EXE MAIN_FIX.EXE            alle Fixes
    python3 alb_fix.py MAIN.EXE MAIN_FIX.EXE --liste    nur anzeigen

Jeder Fix entspricht einem Schalter im Quelltext (#ifdef ALB_FIX_...), siehe BUGFIXES.md.
"""
import hashlib, os, sys

ORIGINAL_MD5 = 'c4171d5eb0ebd36b132e081f8362a075'

# (Schalter, Beschreibung, [(Dateioffset, neue Bytes), ...])
# Die Eingabe wird ueber die md5 geprueft, deshalb stehen hier nur die neuen Bytes.
_BERSERKER_WERT = bytes.fromhex('31d2668b55f0' '8d441202' 'bb03000000' '99' 'f7fb' '909090')
_BERSERKER_SCHADEN = bytes.fromhex('8d441202' 'bb03000000' '99' 'f7fb' '909090')
FIXES = [
    ('ALB_FIX_AUTOMAP_TRAPS',
     'Automap: Fallensymbole nur mit dem Zauber zeigen (fehlendes break in Insert_automap_events, AUTOMAP.C). '
     'Der bedingte Sprung "keine Fallen zeigen" springt jetzt ans Ende des case statt in default.',
     [(0x7c4eb, bytes([0x3c]))]),
    ('ALB_FIX_BERSERKER',
     'Berserker: Werte nach Ende des Effekts exakt zuruecksetzen (Remove_temporary_effect, COMBAT.C). '
     'Statt v*100/150 wird (2v+2)/3 gerechnet, ungerade Werte verlieren keinen Punkt mehr. '
     'Betrifft Staerke, Nahkampf, Fernkampf, kritischer Treffer und Schaden.',
     [(0x69c56, _BERSERKER_WERT), (0x69c8f, _BERSERKER_WERT), (0x69ccb, _BERSERKER_WERT),
      (0x69d0a, _BERSERKER_WERT), (0x69d50, _BERSERKER_SCHADEN)]),
]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--liste' in sys.argv:
        for s, t, stellen in FIXES:
            print('%-24s %d Stelle(n), %d Byte(s)  %s' % (s, len(stellen), sum(len(n) for o, n in stellen), t))
        return 0
    if len(args) != 2:
        print(__doc__)
        return 1
    quelle, ziel = args
    if os.path.abspath(quelle) == os.path.abspath(ziel):
        print('Fehler: Ziel muss eine andere Datei sein als die Quelle.')
        return 1
    daten = bytearray(open(quelle, 'rb').read())
    md5 = hashlib.md5(daten).hexdigest()
    if md5 != ORIGINAL_MD5:
        print('Fehler: %s ist nicht die erwartete MAIN.EXE (md5 %s, erwartet %s).' % (quelle, md5, ORIGINAL_MD5))
        return 1
    for s, t, stellen in FIXES:
        for o, neu in stellen:
            daten[o:o + len(neu)] = neu
        print('angewendet: %s' % s)
    open(ziel, 'wb').write(daten)
    print('geschrieben: %s (md5 %s)' % (ziel, hashlib.md5(daten).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
