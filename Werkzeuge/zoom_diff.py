#!/usr/bin/env python3
"""zoom_diff.py - ZOOM.OBJ (12.10.95, steckt in MAIN.EXE) gegen das aus ZOOM.ASM (22.11.95) mit ML 6.0 gebaute OBJ.
Zeigt, welche Befehlsblöcke dem späteren Quelltext fehlen oder anders sind, und beide ZOOM_DATA-Inhalte.
Ergebnis: Analyse/zoom_diff.txt"""
import os, sys, difflib
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.append(os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
import omf, capstone  # noqa: E402
ALT = os.path.join(PROJ, 'Referenz_Horneman/horneman_albion/MS-DOS/121095/ALBION/SRC/ZOOMFUNC/OBJS/ZOOM.OBJ')
NEU = os.path.join(PROJ, 'Compiler/ML60/ZOOM/ZOOM.OBJ')
cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)


def seg(p, n):
    return next(s for m in omf.modules(p) for s in m['segs'].values() if s['name'] == n)


def dis(s):
    d, m = bytes(s['data']), bytes(s['mask']); out = []
    for i in cs.disasm(d, 0):
        op = i.op_str
        if i.mnemonic.startswith('j') or i.mnemonic in ('call', 'loop'):
            op = 'REL'
        elif any(m[i.address:i.address + i.size]):
            op = 'FIX:' + op
        out.append((i.address, f'{i.mnemonic} {op}', d[i.address:i.address + i.size].hex()))
    return out


a, b = dis(seg(ALT, 'ZOOM_CODE')), dis(seg(NEU, 'ZOOM_CODE'))
sm = difflib.SequenceMatcher(None, [x[1] for x in a], [x[1] for x in b], autojunk=False)
with open(os.path.join(PROJ, 'Analyse', 'zoom_diff.txt'), 'w') as f:
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            f.write(f'= {i2 - i1} Befehle gleich (alt {a[i1][0]:#x}, neu {b[j1][0]:#x})\n'); continue
        f.write(f'{tag}: alt {i1}-{i2}, neu {j1}-{j2}\n')
        for x in a[i1:i2]:
            f.write(f'  - {x[0]:#06x} {x[2]:16} {x[1]}\n')
        for x in b[j1:j2]:
            f.write(f'  + {x[0]:#06x} {x[2]:16} {x[1]}\n')
    for n in ('ZOOM_DATA',):
        f.write(f'\n{n} alt: {bytes(seg(ALT, n)["data"]).hex(" ")}\n{n} neu: {bytes(seg(NEU, n)["data"]).hex(" ")}\n')
print(open(os.path.join(PROJ, 'Analyse', 'zoom_diff.txt')).read()[:3000])
