#!/usr/bin/env python3
"""exe_vergleich.py - gebaute MAIN.EXE gegen das Original: Datei, MZ-Stub, LE-Objekte (Größe, Bytes), Fixups.
Aufruf: python3 Werkzeuge/exe_vergleich.py [Bau/DOS/MAIN.EXE]"""
import os, sys, hashlib, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
_s = importlib.util.spec_from_file_location('le_albion', os.path.join(HERE, 'le.py'))
LE = importlib.util.module_from_spec(_s); _s.loader.exec_module(LE)


def main():
    neu_p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.EXE')
    alt_p = os.path.join(PROJ, 'Original', 'MAIN.EXE')
    a, b = open(alt_p, 'rb').read(), open(neu_p, 'rb').read()
    print(f'Datei: Original {len(a)} B md5 {hashlib.md5(a).hexdigest()}, Bau {len(b)} B md5 {hashlib.md5(b).hexdigest()}'
          + ('  *** IDENTISCH ***' if a == b else ''))
    if a == b:
        return
    A, Bn = LE.LE(alt_p), LE.LE(neu_p)
    print(f'LE-Kopf bei {A.L:#x} / {Bn.L:#x}; Stub gleich: {a[:A.L] == b[:Bn.L]}')
    fa, fb = {}, {}
    for s, so, ty, t, to in A.fixups():
        fa.setdefault(s, set()).add((so, ty, t, to))
    for s, so, ty, t, to in Bn.fixups():
        fb.setdefault(s, set()).add((so, ty, t, to))
    for oa, ob in zip(A.objs, Bn.objs):
        x, y = A.objbytes(oa['nr']), Bn.objbytes(ob['nr'])
        n = min(len(x), len(y)); diff = [k for k in range(n) if x[k] != y[k]]
        fx = fa.get(oa['nr'], set()); fy = fb.get(ob['nr'], set())
        stellen = set()                                   # Fixup-Stellen (4 Byte) beider Dateien ausblenden
        for so, *_ in fx | fy:
            stellen.update(range(so, so + 4))
        roh = [k for k in diff if k not in stellen]
        print(f"Objekt {oa['nr']}: Basis {oa['basis']:#x}/{ob['basis']:#x} Größe {oa['groesse']}/{ob['groesse']} "
              f"Flags {oa['flags']:#x}/{ob['flags']:#x}; Bytes abweichend {len(diff)}"
              + (f" (erste bei {oa['basis'] + diff[0]:#x})" if diff else '')
              + f"; ohne Fixup-Stellen {len(roh)}" + (f" (erste bei {oa['basis'] + roh[0]:#x})" if roh else '')
              + f"; Fixups {len(fx)}/{len(fy)}, nur Original {len(fx - fy)}, nur Bau {len(fy - fx)}")
    if len(A.objs) != len(Bn.objs):
        print(f'Objektzahl {len(A.objs)}/{len(Bn.objs)}')


if __name__ == '__main__':
    main()
