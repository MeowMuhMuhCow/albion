#!/usr/bin/env python3
"""ail_literale.py - Platzhalter-Strings der Agenten durch die echten Texte aus MAIN.EXE ersetzen.

Agenten haben in AIL-Funktionen oft Ersatztexte gleicher Länge geschrieben (strcpy(AIL_error, "1234567890...")),
weil für den Code nur die Länge zählt. Im Gesamtbau stehen diese Texte aber im CONST-Segment und verschieben bzw.
verfälschen die Daten. Hier wird für jeden String-Verweis im übersetzten Modul-OBJ die passende Stelle im Original
gesucht (Lage über die Funktion, in der der Verweis steht) und der Originaltext von dort gelesen. Weicht er ab,
wird das Literal in der Moduldatei ersetzt (Vorkommen in Dateireihenfolge = Verweise in Codereihenfolge).
Benutzt von bau_ail.py; einzeln: python3 Werkzeuge/ail_literale.py MODUL.C MODUL.OBJ  (nur Bericht)"""
import os, re, sys, struct, bisect, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
B7 = 0x130000


def seg_fixups(pfad):
    """OMF: Fixups mit Ziel SEGDEF: (Quellsegment, Offset, Zielsegment, Wert) - Wert = Displacement + Datenwert."""
    d = open(pfad, 'rb').read(); i = 0; ln = ['']; segs = ['']; out = []; last = None
    thr = {}
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
        elif t in (0xA0, 0xA1):
            s, j = idx(0); off = struct.unpack_from('<I' if t == 0xA1 else '<H', c, j)[0]
            j += 4 if t == 0xA1 else 2
            last = (segs[s], off, c[j:])
        elif t in (0x9C, 0x9D):
            j = 0
            while j < len(c):
                b = c[j]
                if not b & 0x80:
                    D = b & 0x40; meth = (b >> 2) & 7; num = b & 3; j += 1
                    v = None
                    if (D and meth < 3) or (not D and meth < 3):
                        v, j = idx(j)
                    elif D and meth == 3:
                        j += 2
                    if not D:
                        thr[num] = (meth, v)
                    continue
                loc = (b >> 2) & 0xF; doff = ((b & 3) << 8) | c[j + 1]; j += 2
                fd = c[j]; j += 1
                F = fd & 0x80; fm = (fd >> 4) & 7; T = fd & 8; P = fd & 4; tm = fd & 3
                if not F and fm < 3:
                    _, j = idx(j)
                if not T:
                    tv, j = idx(j); meth = tm
                else:
                    meth, tv = thr.get(tm, (None, None))
                disp = 0
                if not P:
                    disp = struct.unpack_from('<I' if t == 0x9D else '<H', c, j)[0]; j += 4 if t == 0x9D else 2
                if last and meth == 0 and tv is not None and tv < len(segs) and loc in (9, 13, 5):
                    roh = last[2][doff:doff + 4]
                    wert = disp + (struct.unpack('<I', roh)[0] if len(roh) == 4 else 0)
                    out.append((last[0], last[1] + doff, segs[tv], wert))
    return out


def cstr(b, k):
    e = b.find(b'\0', k)
    return b[k:e if e >= 0 else len(b)]


def c_literal(s):
    out = []
    for i, ch in enumerate(s):
        c = chr(ch)
        if c == '"':
            out.append('\\"')
        elif c == '\\':
            out.append('\\\\')
        elif c == '\n':
            out.append('\\n')
        elif c == '\r':
            out.append('\\r')
        elif c == '\t':
            out.append('\\t')
        elif 32 <= ch < 127:
            out.append(c)
        else:
            out.append('\\%03o' % ch)
    return '"' + ''.join(out) + '"'


def funktions_rumpf(text, adr):
    """(Anfang, Ende) des Rumpfs der Funktion zum AIL-Abschnitt adr in der Moduldatei (F_<adr> oder Zielname)."""
    import alias_bau as AB
    namen = [f'F_{adr:x}'] + [k for k, v in AB.ziel_namen().items() if v == adr]
    for nm in namen:
        m = re.search(r'\b' + re.escape(nm) + r'\s*\([^;{]*\)\s*\{', text, re.I)
        if m:
            i = m.end(); tiefe = 1
            while i < len(text) and tiefe:
                tiefe += {'{': 1, '}': -1}.get(text[i], 0); i += 1
            return (m.start(), i)
    return None


def korrigieren(text, obj, laut=False):
    """Gibt (neuer_text, bericht_zeilen) zurück."""
    sys.path.append(os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
    import omf
    import alias_bau as AB
    _s = importlib.util.spec_from_file_location('le_albion', os.path.join(HERE, 'le.py'))
    LE = importlib.util.module_from_spec(_s); _s.loader.exec_module(LE)
    E = LE.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE')); o7 = bytes(E.objbytes(7))
    fx = {so + 0x10000: to + B7 for s, so, ty, t, to in E.fixups() if s == 1 and t == 7}
    mo = omf.parse(open(obj, 'rb').read(), 0)
    const = next((bytes(s['data']) for s in mo['segs'].values() if s['name'] == 'CONST'), b'')
    fs = AB.funktionsanfaenge(obj); fo = [f[0] for f in fs]
    refs = collections.defaultdict(list)                  # unser Text -> [(Codeoffset, Originaltext)]
    bericht = []
    for seg, off, ziel, k in seg_fixups(obj):
        if seg != '_TEXT' or ziel != 'CONST' or k >= len(const):
            continue
        j = bisect.bisect_right(fo, off) - 1
        if j < 0:
            continue
        q = fs[j][1] + off - fs[j][0]
        if q not in fx:
            continue
        sb = cstr(const, k); so_ = cstr(o7, fx[q] - B7)
        refs[sb].append((off, so_, fs[j][1]))
    neu = text; n_ersetzt = 0
    for sb, lst in refs.items():
        lst.sort()
        if all(x[1] == sb for x in lst):
            continue
        lit = c_literal(sb)
        stellen = [m.start() for m in re.finditer(re.escape(lit), neu)]
        ziele = [x[1] for x in lst]
        if len(set(ziele)) == 1:
            ersatz = [ziele[0]] * len(stellen)
        elif len(stellen) == len(ziele):
            ersatz = ziele
        else:
            # je Funktion zuordnen: Vorkommen im Rumpf der Funktion (Dateireihenfolge) = ihre Verweise (Codereihenfolge)
            ersatz = [None] * len(stellen)
            for a_f in sorted({x[2] for x in lst}):
                rumpf = funktions_rumpf(neu, a_f)
                if not rumpf:
                    continue
                st_f = [i_ for i_, s_ in enumerate(stellen) if rumpf[0] <= s_ < rumpf[1]]
                zi_f = [x[1] for x in lst if x[2] == a_f]
                if len(st_f) == len(zi_f) or len(set(zi_f)) == 1:
                    for n_, i_ in enumerate(st_f):
                        ersatz[i_] = zi_f[min(n_, len(zi_f) - 1)]
            if not any(ersatz):
                bericht.append(f'  {lit[:40]}: {len(stellen)} Vorkommen, {len(ziele)} Verweise mit verschiedenen Zielen - übersprungen')
                continue
            ersatz = [e if e is not None else sb for e in ersatz]
        teile = re.split('(' + re.escape(lit) + ')', neu)
        z = 0
        for i_ in range(1, len(teile), 2):
            if z < len(ersatz):
                teile[i_] = c_literal(ersatz[z]); z += 1
        neu = ''.join(teile); n_ersetzt += z
        bericht.append(f'  {lit[:40]} -> {c_literal(ersatz[0])[:60]}' + (f' (+{len(ersatz) - 1} weitere)' if len(ersatz) > 1 else ''))
    bericht.insert(0, f'Literale: {n_ersetzt} Vorkommen ersetzt')
    if laut:
        print('\n'.join(bericht))
    return neu, bericht


if __name__ == '__main__':
    t = open(sys.argv[1], 'rb').read().decode('latin1')
    korrigieren(t, sys.argv[2], laut=True)
