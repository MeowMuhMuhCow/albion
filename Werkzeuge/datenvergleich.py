#!/usr/bin/env python3
"""datenvergleich.py - ein Datensegment einer Einheit (Bau/OBJ/<EINHEIT>.OBJ) gegen Objekt 7 von MAIN.EXE.
Zeigt die abweichenden Stellen mit Kontext und dem nächsten öffentlichen Symbol davor (zum Finden in der Quelle).
Reines Python, kein Compiler. Aufruf: python3 Werkzeuge/datenvergleich.py EINHEIT SEGMENT [ADRESSE]"""
import os, sys, struct, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.append(os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
import omf  # noqa: E402
_s = importlib.util.spec_from_file_location('le_albion', os.path.join(HERE, 'le.py'))
LE = importlib.util.module_from_spec(_s); _s.loader.exec_module(LE)
EXE = LE.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE'))
O7 = EXE.objbytes(7); B7 = 0x130000
FX7 = set()
for s, so, ty, t, to in EXE.fixups():
    if s == 7 and ty == 7:
        FX7.update(range(so, so + 4))


def pubs(p):
    d = open(p, 'rb').read(); i = 0; out = []; segs = []; lnames = []
    while i < len(d):
        t = d[i]; L = struct.unpack_from('<H', d, i + 1)[0]; r = d[i + 3:i + 3 + L - 1]
        if t == 0x96:
            j = 0
            while j < len(r):
                n = r[j]; lnames.append(r[j + 1:j + 1 + n].decode('latin1')); j += 1 + n
        elif t in (0x98, 0x99):
            j = 1 + (4 if t == 0x99 else 2); ni = r[j]
            segs.append(lnames[ni - 1] if ni <= len(lnames) else '?')
        elif t in (0x90, 0x91):
            j = 0; gi = r[j]; j += 1
            if gi & 0x80: j += 1
            si = r[j]; j += 1
            if si == 0: j += 2
            while j < len(r):
                n = r[j]; nm = r[j + 1:j + 1 + n].decode('latin1'); j += 1 + n
                off = struct.unpack_from('<I' if t == 0x91 else '<H', r, j)[0]; j += 4 if t == 0x91 else 2
                ti = r[j]; j += 1
                if ti & 0x80: j += 1
                out.append((segs[si - 1] if 0 < si <= len(segs) else '?', off, nm))
        i += 3 + L
    return out


def lage(einheit, seg):
    K = json.load(open(os.path.join(PROJ, 'Analyse', 'daten_karte.json')))
    for t in K['treffer']:
        if t['herkunft'] == 'C' and t['modul'] == einheit and t['segment'] == seg and t.get('objekt', 7) == 7:
            return B7 + t['off']
    return None


def main():
    u, sg = sys.argv[1].upper(), sys.argv[2]
    p = os.path.join(PROJ, 'Bau', 'OBJ', u + '.OBJ')
    S = {s['name']: s for m in omf.modules(p) for s in m['segs'].values()}
    d, mk = bytes(S[sg]['data']), bytes(S[sg]['mask'])
    a = int(sys.argv[3], 16) if len(sys.argv) > 3 else lage(u, sg)
    if a is None:
        print('Lage unbekannt - Adresse angeben'); return
    o = O7[a - B7:a - B7 + len(d)]
    ab = [k for k in range(len(d)) if not mk[k] and (a - B7 + k) not in FX7 and d[k] != o[k]]
    P = sorted((off, nm) for s, off, nm in pubs(p) if s == sg)
    print(f'{u} {sg}: {len(d)} B bei {a:#x}, abweichend {len(ab)}')
    laeufe = []
    for k in ab:
        if laeufe and k - laeufe[-1][1] <= 6:
            laeufe[-1][1] = k
        else:
            laeufe.append([k, k])
    for x, y in laeufe[:40]:
        sym = max((pp for pp in P if pp[0] <= x), default=(0, '-'))
        print(f'  +{x:#06x} ({a + x:#x}) {y - x + 1:4} B  nach {sym[1]}+{x - sym[0]:#x}')
        print(f'      EXE {o[max(0, x - 8):y + 9]!r}\n      OBJ {d[max(0, x - 8):y + 9]!r}')


if __name__ == '__main__':
    main()
