#!/usr/bin/env python3
"""asm_vergleich.py - selbst assemblierte PCLIB-OBJs (Compiler/masm611/ASMTEST) gegen die Original-OBJs vom 05.11.95."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
import omf  # noqa: E402
T = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJ, 'Compiler', 'masm611', 'ASMTEST', 'PCLIB32', 'SRC')
O = os.path.join(PROJ, 'Referenz_Horneman', 'horneman_albion', 'MS-DOS', '051195', 'PCLIB32', 'SRC')
for d, f, fa in (('BBOPM', 'OPM_ASS', 'OPM_ASS'), ('BBOPM', 'FNT_ASS', 'FNT_ASS'), ('BBDSA', 'DSA_ASS', 'DSA_ASS'), ('BBDSA', 'DSA1210', 'DSA_ASS'), ('BBSYSTEM', 'SYS_ASS', 'SYS_ASS')):
    neu = os.path.join(T, d, f + '.OBJ'); alt = os.path.join(O, d, 'OBJS', fa + '.OBJ')
    if f == 'DSA1210' and not os.path.exists(neu):
        continue
    log = os.path.join(T, d, 'ML_' + f[:3] + '.LOG')
    if not os.path.exists(neu):
        print(f'{f}: kein OBJ erzeugt.', open(log, errors='replace').read()[-400:] if os.path.exists(log) else '(kein Log)'); continue
    a, b = open(neu, 'rb').read(), open(alt, 'rb').read()
    sa = {s['name']: s for m in omf.modules(neu) for s in m['segs'].values()}
    sb = {s['name']: s for m in omf.modules(alt) for s in m['segs'].values()}
    teile = []
    for n in sorted(set(sa) | set(sb)):
        x, y = sa.get(n), sb.get(n)
        if not x or not y:
            teile.append(f'{n}: nur in {"neu" if x else "alt"}'); continue
        diff = sum(1 for k in range(min(len(x['data']), len(y['data']))) if x['data'][k] != y['data'][k])
        teile.append(f'{n} {len(x["data"])}/{len(y["data"])} B, abweichend {diff}')
    print(f'{f}: Datei {"IDENTISCH" if a == b else "verschieden"} ({len(a)}/{len(b)} B); ' + '; '.join(teile))
