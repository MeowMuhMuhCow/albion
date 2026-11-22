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

# (Schalter, Beschreibung, Dateioffset, Byte vorher, Byte nachher)
FIXES = [
    ('ALB_FIX_AUTOMAP_TRAPS',
     'Automap: Fallensymbole nur mit dem Zauber zeigen (fehlendes break in Insert_automap_events, AUTOMAP.C). '
     'Der bedingte Sprung "keine Fallen zeigen" springt jetzt ans Ende des case statt in default.',
     0x7c4eb, 0x1e, 0x3c),
]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--liste' in sys.argv:
        for s, t, o, a, b in FIXES:
            print('%-24s Offset 0x%06x  %02x -> %02x  %s' % (s, o, a, b, t))
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
    for s, t, o, a, b in FIXES:
        if daten[o] != a:
            print('Fehler: unerwartetes Byte bei 0x%x fuer %s.' % (o, s))
            return 1
        daten[o] = b
        print('angewendet: %s' % s)
    open(ziel, 'wb').write(daten)
    print('geschrieben: %s (md5 %s)' % (ziel, hashlib.md5(daten).hexdigest()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
