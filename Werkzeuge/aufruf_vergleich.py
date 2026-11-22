#!/usr/bin/env python3
"""aufruf_vergleich.py - Wer ruft wen? Direkte Aufrufe (E8 rel32) im Original gegen den Probebau.

Die Karte vergleicht Funktionen mit maskierten Sprungzielen (REL). Ein Aufruf der falschen Funktion bleibt dort
unsichtbar. Hier wird jedes Ziel auf (Einheit, Nr. der öffentlichen Funktion, Abstand) abgebildet:
Original über die Karten-Anker, Bau über MAIN.MAP (öffentliche Funktionen je Modul in Adressfolge = Anker-Nr.).
Bibliotheksmodule über ihren Modulnamen. Reines Python.
Aufruf: python3 Werkzeuge/aufruf_vergleich.py   -> Analyse/aufruf_vergleich.txt"""
import os, re, sys, json, bisect, importlib.util, collections
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
_s = importlib.util.spec_from_file_location('le_albion', os.path.join(HERE, 'le.py'))
LE = importlib.util.module_from_spec(_s); _s.loader.exec_module(LE)


def karte():
    K = json.load(open(os.path.join(PROJ, 'Richter', 'karte.json')))
    an = []
    for s, e, u, i in K['anker']:
        if u.startswith('#'):
            key = ('LIB', str(i).split(':')[1].lower())
        else:
            key = (u.upper(), i)
        an.append((s, e, key))
    an.sort()
    lib0 = {}
    for s, e, k in an:
        if k[0] == 'LIB':
            lib0[k] = min(lib0.get(k, s), s)
    return an, lib0


def bau_map(pfad):
    mods = []; cur = None
    for l in open(pfad, 'rb').read().decode('latin1').replace('\r', '').split('\n'):
        m = re.match(r'Module: (\S+?)\((.*)\)\s*$', l)
        if m:
            q = m.group(2); n = os.path.splitext(os.path.basename(q.replace('\\', '/')))[0]
            cur = {'quelle': q, 'name': n, 'syms': []}; mods.append(cur); continue
        m = re.match(r'0001:([0-9a-f]{8})[ +*]+(\S+)', l)
        if m and cur is not None:
            cur['syms'].append((int(m.group(1), 16), m.group(2)))
    punkte = []                                           # (adresse, key, name)
    for md in mods:
        syms = sorted(md['syms'])
        if not syms:
            continue
        c_quelle = md['quelle'].upper().endswith('.C')
        for k, (a, n) in enumerate(syms):
            if c_quelle:
                punkte.append((a, (md['name'].upper(), k), n))
        if not c_quelle:
            punkte.append((syms[0][0], ('LIB', md['name'].lower()), syms[0][1]))
    punkte.sort()
    return punkte


def main():
    A = LE.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE')); B = LE.LE(os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.EXE'))
    x, y = A.objbytes(1), B.objbytes(1)
    an, lib0 = karte(); P = bau_map(os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.MAP'))
    nr_basis = {}
    for s, e, k in an:
        if k[0] != 'LIB':
            nr_basis[k[0]] = min(nr_basis.get(k[0], 10 ** 9), k[1])
    # Nummern eichen: je Einheit die Verschiebung d (Karten-Nr. = Bau-Nr. + d), bei der die Stücklängen am besten
    # übereinstimmen (Karte: Anker-Länge, Bau: Abstand zur nächsten öffentlichen Funktion)
    alen = {k: e - s for s, e, k in an}
    bl = {}
    for j, (a, k, n) in enumerate(P):
        if k[0] != 'LIB' and j + 1 < len(P):
            bl[k] = P[j + 1][0] - a
    dver = {}
    for u in {k[0] for k in bl}:
        best = max(range(-4, 5), key=lambda d: sum(1 for (uu, i), L in bl.items() if uu == u and alen.get((u, i + d)) == L))
        dver[u] = best
    P2 = []
    for a, k, n in P:
        if k[0] != 'LIB':
            k = (k[0], k[1] + dver.get(k[0], 0))
        P2.append((a, k, n))
    P = P2
    pa = [p[0] for p in P]
    starts = [a[0] for a in an]
    key2bau = {k: a for a, k, n in P}

    def orig_ziel(t):
        j = bisect.bisect_right(starts, t) - 1
        if j < 0 or not (an[j][0] <= t < an[j][1]):
            return None
        s, e, k = an[j]
        return (k, t - (lib0[k] if k[0] == 'LIB' else s))

    def bau_ziel(t):
        j = bisect.bisect_right(pa, t) - 1
        if j < 0:
            return None
        a, k, n = P[j]
        return (k, t - a, n)

    erg = []; nicht = 0; geprueft = 0
    for s, e, k in an:
        if k[0] == 'LIB' or k not in key2bau:
            continue
        b0 = key2bau[k]
        for p in range(s, e - 4):
            if x[p] != 0xE8:
                continue
            q = b0 + (p - s)
            if q + 5 > len(y) or y[q] != 0xE8:
                continue
            ta = p + 5 + int.from_bytes(x[p + 1:p + 5], 'little', signed=True)
            tb = q + 5 + int.from_bytes(y[q + 1:q + 5], 'little', signed=True)
            zo, zb = orig_ziel(ta), bau_ziel(tb)
            if zo is None or zb is None:
                nicht += 1; continue
            geprueft += 1
            if zo[0] != zb[0] or zo[1] != zb[1]:
                erg.append((k, p, zo, zb))
    # Bibliotheken: Anker beginnen nicht immer am Modulanfang -> häufigste Verschiebung je Modul abziehen
    lv = collections.defaultdict(collections.Counter)
    for k, p, zo, zb in erg:
        if zo[0] == zb[0] and zo[0][0] == 'LIB':
            lv[zo[0]][zo[1] - zb[1]] += 1
    lvm = {m: c.most_common(1)[0][0] for m, c in lv.items()}
    erg = [r for r in erg if not (r[2][0] == r[3][0] and r[2][0][0] == 'LIB' and r[2][1] - r[3][1] == lvm[r[2][0]])]
    with open(os.path.join(PROJ, 'Analyse', 'aufruf_vergleich.txt'), 'w') as f:
        f.write(f'Geprüfte Aufrufe {geprueft}, nicht zuordenbar {nicht}, abweichend {len(erg)}\n')
        jeEinheit = collections.Counter(k[0] for k, *_ in erg)
        f.write('Abweichend je Einheit: ' + ', '.join(f'{u} {n}' for u, n in jeEinheit.most_common()) + '\n\n')
        for k, p, zo, zb in erg:
            f.write(f'{k[0]}#{k[1]} bei {p + 0x10000:#x}: Original ruft {zo[0][0]}#{zo[0][1]}+{zo[1]:#x}, '
                    f'Bau ruft {zb[0][0]}#{zb[0][1]}+{zb[1]:#x} ({zb[2]})\n')
    print(f'Geprüfte Aufrufe {geprueft}, nicht zuordenbar {nicht}, abweichend {len(erg)} -> Analyse/aufruf_vergleich.txt')


if __name__ == '__main__':
    main()
