#!/usr/bin/env python3
"""bilanz.py - erste Bilanz: Snapshot-Quellen mit emuliertem WCC386 10.0a uebersetzen und Funktionen in MAIN.EXE suchen.

Pro Modul: _TEXT wird an PUBDEF-Grenzen in Stuecke geteilt (statische Funktionen haengen am vorigen Public).
Jedes Stueck wird mit Fixup-Maske im flachen Bild von MAIN.EXE gesucht (eindeutiger Treffer = GLEICH).
"""
import os, sys, glob, json, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
import omf
from emu100a import Emu100a, DEFAULT_EXE
EXE = os.environ.get('WCC386_EXE') or (os.path.join(HERE, 'w100a', 'BINB', 'WCC386.EXE') if os.path.exists(os.path.join(HERE, 'w100a', 'BINB', 'WCC386.EXE')) else DEFAULT_EXE)

def pubs(path):
    d = open(path, 'rb').read(); i = 0; segs = [None]; ln = ['']; out = []
    while i < len(d):
        t = d[i]; l = struct.unpack_from('<H', d, i + 1)[0]; c = d[i + 3:i + 2 + l]; i += 3 + l
        if t == 0x96:
            j = 0
            while j < len(c): n = c[j]; ln.append(c[j + 1:j + 1 + n].decode('latin1')); j += 1 + n
        elif t in (0x98, 0x99):
            j = 1 + (3 if (c[0] >> 5) == 0 else 0) + (4 if t == 0x99 else 2)
            sn, j = omf.idx(c, j); segs.append(ln[sn])
        elif t in (0x90, 0x91, 0xB6, 0xB7):
            g, j = omf.idx(c, 0); s, j = omf.idx(c, j)
            if s == 0: j += 2
            while j < len(c):
                n = c[j]; nm = c[j + 1:j + 1 + n].decode('latin1'); j += 1 + n
                off = struct.unpack_from('<I' if t & 1 else '<H', c, j)[0]; j += 4 if t & 1 else 2
                ti, j = omf.idx(c, j)
                out.append((segs[s] if s < len(segs) else '?', off, nm))
        elif t == 0x8A or t == 0x8B:
            break
    return out

def find(code, data, mask):
    best = (0, 0); st = None
    for k in range(len(data) + 1):
        if k < len(data) and not mask[k]:
            if st is None: st = k
        else:
            if st is not None and k - st > best[1] - best[0]: best = (st, k)
            st = None
    a, b = best
    if b - a < 6: return []
    anc = bytes(data[a:b]); hits = []; p = code.find(anc)
    while p >= 0 and len(hits) < 3:
        base = p - a
        if base >= 0 and base + len(data) <= len(code) and all(mask[k] or code[base + k] == data[k] for k in range(len(data))):
            hits.append(base)
        p = code.find(anc, p + 1)
    return hits

def run(cfg):
    code = open(cfg['flat'], 'rb').read()
    root = cfg['root']; res = {}
    for src in sorted(glob.glob(os.path.join(root, cfg['srcglob']), recursive=True)):
        st = os.path.splitext(os.path.basename(src))[0].upper()
        rel = os.path.relpath(src, root).replace('/', '\\')
        out = os.path.join(root, '_B.OBJ')
        if os.path.exists(out): os.remove(out)
        d, _, fname = rel.rpartition('\\')
        e = Emu100a(root, [fname] + cfg['flags'] + ['-zq', '-fo=C:\\_B.OBJ'], exe=EXE,
                    env={'PATH': 'C:\\', 'INCLUDE': cfg['inc'], 'WATCOM': 'C:\\WATCOM.10A'})
        e.cwd = d
        e.run()
        if not os.path.exists(out):
            res[st] = {'fehler': e.out.decode('latin1')[-200:]}; continue
        text = None
        for m in omf.modules(out):
            for s in m['segs'].values():
                if s['name'] == '_TEXT': text = s
        P = sorted({(o, n) for sg, o, n in pubs(out) if sg == '_TEXT'})
        if text is None or not P:
            res[st] = {'leer': True}; continue
        n = len(text['data']); fn = []
        if P[0][0] != 0: P.insert(0, (0, '(vor erstem Public)'))
        for k, (o, nm) in enumerate(P):
            e_ = P[k + 1][0] if k + 1 < len(P) else n
            h = find(code, text['data'][o:e_], text['mask'][o:e_])
            fn.append((nm, e_ - o, 'GLEICH' if len(h) == 1 else ('mehrdeutig' if h else 'anders'), h[0] + 0x10000 if len(h) == 1 else None))
        res[st] = {'bytes': n, 'funcs': fn}
    return res

if __name__ == '__main__':
    cfg = json.loads(sys.argv[1]); r = run(cfg)
    json.dump(r, open(cfg['out'], 'w'), indent=1)
    nf = sum(len(v.get('funcs', [])) for v in r.values()); ng = sum(1 for v in r.values() for f in v.get('funcs', []) if f[2] == 'GLEICH')
    bf = sum(f[1] for v in r.values() for f in v.get('funcs', [])); bg = sum(f[1] for v in r.values() for f in v.get('funcs', []) if f[2] == 'GLEICH')
    print(f'Module {len(r)}, Stuecke {nf}, GLEICH {ng} ({100*ng/max(nf,1):.1f} %), Bytes {bg}/{bf} ({100*bg/max(bf,1):.1f} %)')
    for k, v in r.items():
        if 'funcs' not in v: print(k, v)
