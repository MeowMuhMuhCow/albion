#!/usr/bin/env python3
"""obj_abgleich.py - fertige OBJ/LIB-Module (z. B. PCLIB 12.10.95) gegen MAIN.EXE abgleichen, nur lesend.

Je Modul: _TEXT an den Publics zerlegen, jedes Stueck maskiert (Fixups) im Codeobjekt suchen.
Aufruf: python3 Werkzeuge/obj_abgleich.py DATEI.OBJ|DATEI.LIB ... [--json AUSGABE]
"""
import json, os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
import omf  # noqa: E402

PROJ = os.path.dirname(HERE)
FLAT = os.path.join(PROJ, 'Analyse', 'main_flat.bin')
KARTE = os.path.join(PROJ, 'Richter', 'karte.json')
CB = 0x10000


def modul_starts(d):
    i, out = 0, []
    psz = struct.unpack('<H', d[1:3])[0] + 3 if d[0] == 0xF0 else None
    if psz:
        i = psz
    while i < len(d):
        if d[i] == 0xF1:
            break
        if d[i] != 0x80:
            i += 1
            continue
        out.append(i)
        m = omf.parse(d, i)
        i = m['end']
        if psz:
            i = ((i + psz - 1) // psz) * psz
    return out


def pubs_ab(d, i):
    segs = [None]; ln = ['']; out = []
    while i < len(d):
        t = d[i]; l = struct.unpack_from('<H', d, i + 1)[0]; c = d[i + 3:i + 2 + l]; i += 3 + l
        if t == 0x96:
            j = 0
            while j < len(c):
                n = c[j]; ln.append(c[j + 1:j + 1 + n].decode('latin1')); j += 1 + n
        elif t in (0x98, 0x99):
            j = 1 + (3 if (c[0] >> 5) == 0 else 0) + (4 if t == 0x99 else 2)
            sn, j = omf.idx(c, j); segs.append(ln[sn])
        elif t in (0x90, 0x91):
            g, j = omf.idx(c, 0); s, j = omf.idx(c, j)
            if s == 0:
                j += 2
            while j < len(c):
                n = c[j]; nm = c[j + 1:j + 1 + n].decode('latin1'); j += 1 + n
                off = struct.unpack_from('<I' if t & 1 else '<H', c, j)[0]; j += 4 if t & 1 else 2
                _, j = omf.idx(c, j)
                out.append((segs[s] if s < len(segs) else '?', off, nm))
        elif t in (0x8A, 0x8B):
            break
    return out


def finde(code, data, mask):
    best = (0, 0); st = None
    for k in range(len(data) + 1):
        if k < len(data) and not mask[k]:
            if st is None:
                st = k
        else:
            if st is not None and k - st > best[1] - best[0]:
                best = (st, k)
            st = None
    a, b = best
    if b - a < 6:
        return []
    anc = bytes(data[a:b]); hits = []; p = code.find(anc)
    while p >= 0 and len(hits) < 3:
        base = p - a
        if 0 <= base and base + len(data) <= len(code) and all(mask[k] or code[base + k] == data[k] for k in range(len(data))):
            hits.append(base)
        p = code.find(anc, p + 1)
    return hits


def luecke_von(karte, off):
    for L in karte['luecken']:
        if L['start'] <= off < L['ende']:
            return L['id']
    return None


def main():
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    jout = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    if jout in args:
        args.remove(jout)
    code = open(FLAT, 'rb').read()
    karte = json.load(open(KARTE, encoding='utf-8'))
    ergebnis = {}
    for pfad in args:
        d = open(pfad, 'rb').read()
        for st in modul_starts(d):
            m = omf.parse(d, st)
            t = next((s for s in m['segs'].values() if s['name'] == '_TEXT'), None)
            if t is None or not len(t['data']):
                continue
            P = sorted({(o, n) for sg, o, n in pubs_ab(d, st) if sg == '_TEXT'})
            if not P or P[0][0] != 0:
                P.insert(0, (0, '$anfang'))
            n = len(t['data']); gef = 0; stuecke = []
            for k, (o, nm) in enumerate(P):
                e = P[k + 1][0] if k + 1 < len(P) else n
                h = finde(code, t['data'][o:e], t['mask'][o:e])
                if len(h) == 1:
                    gef += e - o
                stuecke.append({'name': nm, 'off': o, 'n': e - o, 'treffer': [hex(x + CB) for x in h],
                                'luecke': luecke_von(karte, h[0]) if len(h) == 1 else None})
            ganz = finde(code, t['data'], t['mask'])
            name = os.path.basename(pfad) + ':' + m['name']
            ergebnis[name] = {'text': n, 'gefunden': gef, 'ganz': [hex(x + CB) for x in ganz], 'stuecke': stuecke}
            ls = sorted({s['luecke'] for s in stuecke if s['luecke']})
            print(f"{name:40} _TEXT {n:6}  gefunden {gef:6} ({100 * gef / n:5.1f} %)  ganz {'ja ' + ergebnis[name]['ganz'][0] if len(ganz) == 1 else 'nein'}  Lücken {','.join(ls) or '-'}")
    if jout:
        json.dump(ergebnis, open(jout, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
