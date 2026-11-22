#!/usr/bin/env python3
"""daten_lage.py - Wo liegen die Daten im Probebau gegenüber dem Original? (CONST, _DATA und _BSS)

Für jede Funktion mit Karten-Anker werden die Fixups ins Datenobjekt (7) an derselben Stelle in Original und Bau
verglichen. Jedes Ziel bekommt den Namen des nächstkleineren Datensymbols aus MAIN.MAP. Ergebnis je Zieladresse
(Original-Offset in Objekt 7): Bau-Offset und Verschiebung. Wo sich die Verschiebung ändert, fehlt oder überzählt
etwas im Bau. Reines Python.
Aufruf: python3 Werkzeuge/daten_lage.py   -> Analyse/daten_lage.txt"""
import os, re, sys, bisect, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import aufruf_vergleich as AV  # noqa: E402
LE = AV.LE


def daten_syms(pfad):
    out = []; mod = None
    for l in open(pfad, 'rb').read().decode('latin1').replace('\r', '').split('\n'):
        m = re.match(r'Module: (\S+?)\((.*)\)\s*$', l)
        if m:
            mod = os.path.splitext(os.path.basename(m.group(2).replace('\\', '/')))[0]; continue
        m = re.match(r'0007:([0-9a-f]{8})[ +*]+(\S+)', l)
        if m:
            out.append((int(m.group(1), 16), m.group(2), mod))
    out.sort()
    return out


def main():
    A = LE.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE')); B = LE.LE(os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.EXE'))
    an, lib0 = AV.karte(); P = AV.bau_map(os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.MAP'))
    # dieselbe Nummern-Eichung wie in aufruf_vergleich
    alen = {k: e - s for s, e, k in an}
    bl = {}
    for j, (a, k, n) in enumerate(P):
        if k[0] != 'LIB' and j + 1 < len(P):
            bl[k] = P[j + 1][0] - a
    dver = {}
    for u in {k[0] for k in bl}:
        dver[u] = max(range(-4, 5), key=lambda d: sum(1 for (uu, i), L in bl.items() if uu == u and alen.get((u, i + d)) == L))
    key2bau = {}
    for a, k, n in P:
        if k[0] != 'LIB':
            key2bau[(k[0], k[1] + dver.get(k[0], 0))] = a
    fa = {}; fb = {}
    for s, so, ty, t, to in A.fixups():
        if s == 1 and t == 7:
            fa[so] = to
    for s, so, ty, t, to in B.fixups():
        if s == 1 and t == 7:
            fb[so] = to
    DS = daten_syms(os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.MAP')); da = [d[0] for d in DS]
    ziele = {}                                            # orig-Offset -> Counter(bau-Offset)
    wer = collections.defaultdict(set)
    for s, e, k in an:
        if k[0] == 'LIB' or k not in key2bau:
            continue
        b0 = key2bau[k]
        for so in range(s, e):
            if so in fa and (b0 + so - s) in fb:
                ziele.setdefault(fa[so], collections.Counter())[fb[b0 + so - s]] += 1
                wer[fa[so]].add(k[0])
    zeilen = []; alt = None; spruenge = []
    for o in sorted(ziele):
        b, n = ziele[o].most_common(1)[0]
        j = bisect.bisect_right(da, b) - 1
        nm = f'{DS[j][1]}+{b - DS[j][0]:#x} [{DS[j][2]}]' if j >= 0 else '?'
        d = b - o
        if d != alt:
            spruenge.append((o, alt, d, nm)); alt = d
        zeilen.append(f'{o + 0x130000:#x}  Bau {b + 0x130000:#x}  Versatz {d:+#x}  {nm}  (aus {",".join(sorted(wer[o]))[:60]})'
                      + ('  MEHRDEUTIG' if len(ziele[o]) > 1 else ''))
    with open(os.path.join(PROJ, 'Analyse', 'daten_lage.txt'), 'w') as f:
        f.write(f'{len(ziele)} Datenziele aus Funktionen mit Anker; Sprünge der Verschiebung: {len(spruenge)}\n\n')
        for o, a_, d, nm in spruenge:
            f.write(f'  ab {o + 0x130000:#x}: Versatz {a_ if a_ is None else hex(a_)} -> {d:+#x}  ({nm})\n')
        f.write('\n' + '\n'.join(zeilen) + '\n')
    print(f'{len(ziele)} Datenziele, {len(spruenge)} Versatzsprünge -> Analyse/daten_lage.txt')
    for o, a_, d, nm in spruenge[:25]:
        print(f'  ab {o + 0x130000:#x}: {a_ if a_ is None else hex(a_)} -> {d:+#x}  ({nm})')


if __name__ == '__main__':
    main()
