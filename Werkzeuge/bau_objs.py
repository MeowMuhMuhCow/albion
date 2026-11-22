#!/usr/bin/env python3
"""bau_objs.py - Gesamtbau Schritt 1: alle C-Einheiten (albion_einheiten.json) mit ihren Flags übersetzen und die
OBJ-Dateien nach Bau/OBJ/<EINHEIT>.OBJ legen. Parallel (4 Prozesse). Protokoll: Bau/objs.txt
Aufruf: python3 Werkzeuge/bau_objs.py [N_PROZESSE]"""
import os, sys, shutil
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import albion as A  # noqa: E402
ZIEL = os.path.join(A.PROJ, 'Bau', 'OBJ')


def eins(args):
    u, cfg = args
    r = A.kompiliere(u, cfg, mit_obj=True)
    if r.get('fehler') or not r.get('obj'):
        return u, False, (r.get('fehler') or 'kein OBJ')[-300:]
    shutil.copyfile(r['obj'], os.path.join(ZIEL, u.upper() + '.OBJ'))
    return u, True, f"{sum(len(s['daten']) // 2 for s in r['stuecke'])} B Code"


if __name__ == '__main__':
    os.makedirs(ZIEL, exist_ok=True)
    E = A.einheiten(); n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with Pool(n) as p:
        erg = p.map(eins, list(E.items()), chunksize=1)
    ok = [e for e in erg if e[1]]; schlecht = [e for e in erg if not e[1]]
    with open(os.path.join(A.PROJ, 'Bau', 'objs.txt'), 'w') as f:
        for u, g, t in erg:
            f.write(f"{u:12} {'OK ' if g else 'FEHLER'} {t}\n")
    print(f'{len(ok)} von {len(erg)} Einheiten als OBJ in Bau/OBJ' + (f', Fehler: {[e[0] for e in schlecht]}' if schlecht else ''))
