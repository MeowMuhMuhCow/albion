#!/usr/bin/env python3
"""alias_bau.py - Offene Namen des Probebaus (MAIN.MAP: 'undefined reference') auf die echten Symbole abbilden.

Agenten haben fremde Funktionen und Variablen oft nach ihrer Adresse benannt (F_8c64d, D_13fc44) oder unter
eigenen Namen (XMI_flush_buffer, AIL_bkgnd_flag). Für jeden offenen Namen wird das Ziel im Original bestimmt
(aus dem Namen selbst oder per Mehrheit über die Fixups der OBJs, die ihn benutzen) und im Probebau das Symbol
gesucht, das genau dort liegt: Code über die Bytes am Ziel (eindeutige Fundstelle in Objekt 1), Daten über den
Versatz aus Analyse/daten_lage.txt. Ergebnis: Bau/alias.lnk (WLINK-Direktive 'ALIAS a=b'), Bericht Bau/alias.txt.
Wirkt beim nächsten Probebau. Aufruf: python3 Werkzeuge/alias_bau.py"""
import os, re, sys, json, bisect, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ail_daten as AD  # noqa: E402
LE = AD.LE
B7 = 0x130000


def main():
    mp = os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.MAP')
    txt = open(mp, 'rb').read().decode('latin1').replace('\r', '')
    offen = sorted(set(re.findall(r'Warning\(1028\): (\S+) is an undefined reference', txt)))
    kommt = set()                                         # werden von den AIL-Datenmodulen (ail_daten) definiert
    ad = os.path.join(PROJ, 'src', 'AIL', 'ASM')
    for f in ('AILCD.ASM', 'A9B04D.ASM', 'AIL32D.ASM', 'DMASNDD.ASM', 'KEYD.ASM'):
        if os.path.exists(os.path.join(ad, f)):
            for l in open(os.path.join(ad, f), encoding='latin1'):
                if l.strip().startswith('PUBLIC'):
                    kommt.update(x.strip() for x in l.strip()[6:].split(','))
    offen = [n for n in offen if n not in kommt]
    code, daten = {}, {}
    for l in txt.split('\n'):
        m = re.match(r'000([17]):([0-9a-f]{8})[ +*]+(\S+)', l)
        if m:
            (code if m.group(1) == '1' else daten).setdefault(int(m.group(2), 16), []).append(m.group(3))
    A = LE.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE')); Bx = LE.LE(os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.EXE'))
    x1 = bytes(A.objbytes(1)); y1 = bytes(Bx.objbytes(1))
    fx = {}                                               # Original: (obj, quelle) -> (zielobj, ziel)
    for s, so, ty, t, to in A.fixups():
        fx[(s, so)] = (t, to)
    fixstellen_b = set()
    for s, so, ty, t, to in Bx.fixups():
        if s == 1:
            fixstellen_b.update(range(so, so + 4))
    fixstellen_a = set()
    for (s, so) in fx:
        if s == 1:
            fixstellen_a.update(range(so, so + 4))
    # Stimmen: Name -> Ziel, aus allen OBJs mit bekannter Lage im Original
    stimmen = collections.defaultdict(collections.Counter)
    quellen = []
    d = os.path.join(PROJ, 'Bau', 'AIL')
    for f in sorted(os.listdir(d)):
        m = re.fullmatch(r'[MK]([0-9A-F]+)\.OBJ', f)
        if m:
            quellen.append((os.path.join(d, f), int(m.group(1), 16)))
    K = json.load(open(os.path.join(PROJ, 'Richter', 'karte.json')))
    u0 = {}
    for s, e, u, i in K['anker']:
        if not u.startswith('#'):
            u0[u.upper()] = min(u0.get(u.upper(), 10 ** 9), s)
    od = os.path.join(PROJ, 'Bau', 'OBJ')
    for f in sorted(os.listdir(od)) if os.path.isdir(od) else []:
        u = os.path.splitext(f)[0].upper()
        if u in u0:
            quellen.append((os.path.join(od, f), u0[u] + 0x10000))
    ml = os.path.join(PROJ, 'Compiler', 'ML60', 'AIL')
    for n, a0 in (('AIL32.OBJ', 0xac320), ('DMASND32.OBJ', 0xc2dec)):
        if os.path.exists(os.path.join(ml, n)):
            quellen.append((os.path.join(ml, n), a0))
    sys.path.append(os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
    import omf
    for p, a0 in quellen:
        try:
            mo = omf.parse(open(p, 'rb').read(), 0)
            text = next((bytes(s['data']) for s in mo['segs'].values() if s['name'] in ('_TEXT', 'CODE') and len(s['data'])), b'')
        except Exception:
            text = b''
        fstarts = funktionsanfaenge(p)
        for seg, off, n in AD.ext_fixups(p):
            if seg not in ('_TEXT', 'CODE'):
                continue
            q = a0 + off - 0x10000
            j = bisect.bisect_right([f[0] for f in fstarts], off) - 1
            if j >= 0:                                    # Lage über die Funktion, in der der Fixup steht
                q = fstarts[j][1] + (off - fstarts[j][0]) - 0x10000
            if (1, q) in fx:
                stimmen[n][fx[(1, q)]] += 1
            elif 0 < off <= len(text) and text[off - 1] in (0xE8, 0xE9) and q + 4 <= len(x1):
                # relativer Aufruf/Sprung: im Original ohne Fixup, Ziel aus den Originalbytes
                stimmen[n][(1, q + 4 + int.from_bytes(x1[q:q + 4], 'little', signed=True))] += 1
    # Datenversatz aus daten_lage
    dl = []
    p = os.path.join(PROJ, 'Analyse', 'daten_lage.txt')
    if os.path.exists(p):
        for l in open(p):
            m = re.match(r'(0x[0-9a-f]+)  Bau (0x[0-9a-f]+)', l)
            if m:
                dl.append((int(m.group(1), 16) - B7, int(m.group(2), 16) - B7))
    dl.sort(); dla = [a for a, b in dl]

    def ziel_von(n):
        m = re.fullmatch(r'_?([FD])_([0-9a-f]+)_?', n)
        if m:
            a = int(m.group(2), 16)
            return (7, a - B7) if a >= B7 else (1, a - 0x10000)
        c = stimmen.get(n)
        if c:
            (z, k), = c.most_common(1)
            return z
        return None

    # Modulversatz: Ladeliste (Onnn -> Original-Anfang) und MAIN.MAP (Onnn -> erstes Codesymbol im Bau)
    folge = {}
    ll = os.path.join(PROJ, 'Bau', 'link_liste.txt'); rf = json.load(open(os.path.join(PROJ, 'Bau', 'reihenfolge.json')))
    adr_von = {}
    for z in rf:
        if z.get('adr', '-') != '-':
            adr_von.setdefault((z['art'], z['name']), int(z['adr'], 16))
    for l in open(ll):
        f_ = l.split()
        if len(f_) >= 3 and f_[0].startswith('O') and (f_[1], f_[2]) in adr_von:
            folge[f_[0].split('.')[0]] = adr_von[(f_[1], f_[2])] - 0x10000
    erst = {}; cur = None
    for l in txt.split('\n'):
        m = re.match(r'Module: C:\\O\\(O\d+)\.OBJ', l)
        if m:
            cur = m.group(1); continue
        m = re.match(r'0001:([0-9a-f]{8})', l)
        if m and cur in folge:
            erst[cur] = min(erst.get(cur, 10 ** 9), int(m.group(1), 16))
    starts = sorted((folge[k], erst[k] - folge[k]) for k in erst)
    sa = [s for s, d in starts]

    def bau_modul(o):
        j = bisect.bisect_right(sa, o) - 1
        return o + starts[j][1] if j >= 0 else None

    def bau_code(o):
        b = bau_modul(o)
        if b is not None and b in code:
            return b
        roh = []
        for k in range(o, min(o + 48, len(x1))):
            roh.append(b'.' if k in fixstellen_a else re.escape(x1[k:k + 1]))
        pat = b''.join(roh)
        hits = [h.start() for h in re.finditer(pat, y1, re.S)]
        if not hits or len(hits) > 16:
            return None
        return min(hits, key=lambda h: abs(h - o))      # bei Mehrdeutigkeit die nächste Fundstelle (Verschiebung klein)

    def bau_daten(o):
        j = bisect.bisect_right(dla, o) - 1
        if j < 0:
            return None
        a, b = dl[j]
        return o + (b - a)

    zeilen = []; aliase = []
    for n in offen:
        z = ziel_von(n)
        if not z:
            zeilen.append(f'{n:32} ? (kein Ziel)'); continue
        obj, o = z
        if obj == 1:
            b = bau_code(o); kand = code.get(b, []) if b is not None else []
            if not [k for k in kand if k != n]:           # Abschnittsanfang eines AIL-Moduls: über den Namen der Zielfunktion
                zn = {v: k for k, v in ziel_namen().items() if not k.startswith('f_')}.get(o + 0x10000)
                if zn:
                    treffer = [(a_, s_) for a_, ss in code.items() for s_ in ss if s_.strip('_').lower() == zn]
                    if len(treffer) == 1:
                        b, kand = treffer[0][0], [treffer[0][1]]
        elif obj == 7:
            b = bau_daten(o); kand = daten.get(b, []) if b is not None else []
        else:
            b = None; kand = []
        kand = [k for k in kand if k != n]
        if kand:
            aliase.append((n, kand[0]))
            zeilen.append(f'{n:32} -> {kand[0]}  (Original Objekt {obj} {o:#x}, Bau {b:#x})')
        else:
            zeilen.append(f'{n:32} ? Original Objekt {obj} {o:#x}, Bau {b if b is None else hex(b)}: kein Symbol dort')
    # bisherige Aliase behalten (im letzten Bau aufgelöste Namen stehen nicht mehr als offen in der MAP)
    alt = {}
    pa = os.path.join(PROJ, 'Bau', 'alias.lnk')
    if os.path.exists(pa):
        for l in open(pa):
            m = re.match(r'ALIAS (\S+)=(\S+)', l.strip())
            if m:
                alt[m.group(1)] = m.group(2)
    neu_ = dict(aliase)
    definiert = {s for ss in code.values() for s in ss} | {s for ss in daten.values() for s in ss}
    for a, b in alt.items():
        if a not in neu_ and a not in definiert and a not in kommt:
            aliase.append((a, b))
    with open(os.path.join(PROJ, 'Bau', 'alias.lnk'), 'w', newline='\r\n') as f:
        for a, b in aliases_sortiert(aliase):
            f.write(f'ALIAS {a}={b}\n')
    open(os.path.join(PROJ, 'Bau', 'alias.txt'), 'w').write('\n'.join(zeilen) + '\n')
    print(f'offene Namen {len(offen)}, abgebildet {len(aliase)} -> Bau/alias.lnk, Bericht Bau/alias.txt')


_ZIEL = None


def ziel_namen():
    """Name der Zielfunktion je AIL-Abschnitt (klein, ohne _) -> Original-Adresse."""
    global _ZIEL
    if _ZIEL is None:
        _ZIEL = {}
        try:
            import ail_richter as R
            for adr in R.funktionen():
                p = os.path.join(R.REKO, R.name_von(adr).upper() + '.C')
                if os.path.exists(p):
                    tn = R.ziel_name(open(p, 'rb').read().decode('latin1'), adr)
                    _ZIEL[tn.strip('_').lower()] = int(adr, 16)
                _ZIEL[R.name_von(adr).strip('_').lower()] = int(adr, 16)
        except Exception as e:
            print('ziel_namen:', e)
    return _ZIEL


def funktionsanfaenge(pfad):
    """PUBDEFs im _TEXT eines AIL-OBJs: sortierte Liste (Offset, Original-Adresse) für Funktionen mit bekannter Lage."""
    import struct
    d = open(pfad, 'rb').read(); i = 0; ln = ['']; segs = ['']; out = []
    while i + 3 <= len(d):
        t = d[i]; L = struct.unpack_from('<H', d, i + 1)[0]; c = d[i + 3:i + 3 + L - 1]; i += 3 + L

        def idx(j):
            return ((c[j] & 0x7f) << 8 | c[j + 1], j + 2) if c[j] & 0x80 else (c[j], j + 1)
        if t == 0x96:
            j = 0
            while j < len(c):
                n = c[j]; ln.append(c[j + 1:j + 1 + n].decode('latin1')); j += 1 + n
        elif t in (0x98, 0x99):
            j = 1 + (4 if t == 0x99 else 2); sn, j = idx(j); segs.append(ln[sn])
        elif t in (0x90, 0x91, 0xB6, 0xB7):
            j = 0; _, j = idx(j); si, j = idx(j)
            if si == 0:
                j += 2
            while j < len(c):
                n = c[j]; nm = c[j + 1:j + 1 + n].decode('latin1'); j += 1 + n
                off = struct.unpack_from('<I' if t in (0x91, 0xB7) else '<H', c, j)[0]; j += 4 if t in (0x91, 0xB7) else 2
                _, j = idx(j)
                if 0 < si < len(segs) and segs[si] == '_TEXT':
                    k = nm.strip('_').lower()
                    m = re.fullmatch(r'f_([0-9a-f]+)', k)
                    a = int(m.group(1), 16) if m else ziel_namen().get(k)
                    if a:
                        out.append((off, a))
    return sorted(out)


def aliases_sortiert(a):
    return sorted(set(a))


if __name__ == '__main__':
    main()
