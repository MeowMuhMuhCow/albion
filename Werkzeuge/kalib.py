#!/usr/bin/env python3
"""kalib.py - Eichung: Hornemans .C mit emuliertem WCC386 10.0a uebersetzen und gegen seine .OBJ vergleichen."""
import os, sys, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
import omf
from emu100a import Emu100a, DEFAULT_EXE
EXE = os.environ.get('WCC386_EXE') or (os.path.join(HERE, 'w100a', 'BINB', 'WCC386.EXE') if os.path.exists(os.path.join(HERE, 'w100a', 'BINB', 'WCC386.EXE')) else DEFAULT_EXE)

def segs(path):
    out = {}
    for m in omf.modules(path):
        for s in m['segs'].values():
            out[(s['name'], s['cls'])] = (bytes(s['data']), bytes(s['mask']))
        for c in m['comdats']:
            out[('COMDAT:' + c['name'], 'CODE')] = (bytes(c['data']), bytes(c['mask']))
    return out

def cmp(a, b):
    res = {}
    for k in set(a) | set(b):
        if k not in a or k not in b:
            res[k] = 'fehlt'; continue
        da, ma = a[k]; db, mb = b[k]
        if da == db and ma == mb: res[k] = 'GLEICH'
        elif len(da) != len(db): res[k] = f'laenge {len(da)}/{len(db)}'
        else:
            n = sum(1 for x, y, p, q in zip(da, db, ma, mb) if (x != y and not p and not q) or p != q)
            res[k] = f'{n} Bytes anders'
    return res

def main(root, objdir, srcglob, flags, inc):
    srcs = {os.path.splitext(os.path.basename(p))[0].upper(): p for p in glob.glob(os.path.join(root, srcglob), recursive=True)}
    rows = []
    for o in sorted(glob.glob(os.path.join(root, objdir, '*.OBJ'))):
        st = os.path.splitext(os.path.basename(o))[0].upper()
        if st not in srcs: continue
        rel = os.path.relpath(srcs[st], root).replace('/', '\\')
        out = os.path.join(root, '_KALIB.OBJ')
        if os.path.exists(out): os.remove(out)
        env = {'PATH': 'C:\\', 'INCLUDE': inc, 'WATCOM': 'C:\\WATCOM.10A'}
        e = Emu100a(root, [rel] + flags + ['-zq', '-fo=_KALIB.OBJ'], exe=EXE, env=env)
        code, dt = e.run()
        if not os.path.exists(out):
            rows.append((st, 'KOMPILIERFEHLER', e.out.decode('latin1')[-300:], e.fault)); continue
        r = cmp(segs(o), segs(out))
        code_ok = all(v == 'GLEICH' for (n, c), v in r.items() if c == 'CODE')
        all_ok = all(v == 'GLEICH' for v in r.values())
        rows.append((st, 'ALLES GLEICH' if all_ok else ('CODE GLEICH' if code_ok else 'ANDERS'), {f'{n}/{c}': v for (n, c), v in r.items() if v != 'GLEICH'}, round(dt, 2)))
    return rows

if __name__ == '__main__':
    cfg = json.loads(sys.argv[1])
    rows = main(**cfg)
    from collections import Counter
    print(Counter(r[1] for r in rows))
    for r in rows: print(r)
