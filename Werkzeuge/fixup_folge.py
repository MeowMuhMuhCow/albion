#!/usr/bin/env python3
"""fixup_folge.py - Krücke: Reihenfolge der LE-Fixup-Tabelle wie im Original (nur Satzrahmen der OBJs, keine Bytes).

Befund (22.11.2026): wlink 10.0 legt die Fixups jeder 4-KB-Seite in Blöcken zu 512 Byte ab; der neueste Block steht
in der Datei zuerst, innerhalb eines Blocks folgen die FIXUPP-Sätze in Einlesefolge, jeder Satz rückwärts. Die Folge
hängt also daran, wie der Compiler Code und Daten in LEDATA/FIXUPP-Sätze zerlegt. Diese Zerlegung richtet sich bei
-d2 nach den Debug-Sätzen (EXTDEF mit Typindex, $$TYPES/$$SYMBOLS), also nach Kopfdateien und Bau-Umgebung von
damals, nicht nach dem Programm. Hier wird die Zerlegung des Originals aus der Fixup-Tabelle von Original/MAIN.EXE
zurückgerechnet und die OBJ-Kopien in Bau/DOS/O werden an diesen Stellen neu in LEDATA/FIXUPP-Sätze geteilt.
Bytes, Fixup-Inhalte und Lage bleiben gleich; geändert wird nur, wo ein Satz endet.
Aufruf (nach einem ersten Link, braucht Bau/DOS/MAIN.MAP und MAIN.LNK): python3 Werkzeuge/fixup_folge.py
Rückgabe 0: nichts zu tun, 2: OBJs geändert (neu linken), 1: Fehler."""
import os, re, sys, struct, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
DOS = os.path.join(PROJ, 'Bau', 'DOS')
BLOCK = 512
BREITE = {0: 1, 1: 2, 2: 2, 3: 4, 4: 1, 5: 2, 9: 4, 11: 6, 13: 4}

_s = importlib.util.spec_from_file_location('le_ff', os.path.join(HERE, 'le.py'))
LE = importlib.util.module_from_spec(_s); _s.loader.exec_module(LE)


# ---------- Original: Seitenlisten -> Sätze ----------
def seitenlisten(E):
    """{(objekt, seite): [(groesse, [offsets])]} in Dateifolge"""
    d = E.d; res = {}
    for o in E.objs:
        for i in range(o['seiten']):
            pg = o['seite'] + i
            a = struct.unpack_from('<I', d, E.fpt + 4 * (pg - 1))[0]; b = struct.unpack_from('<I', d, E.fpt + 4 * pg)[0]
            j = E.frt + a; e = E.frt + b; L = []
            while j < e:
                st = j; src, flg = d[j], d[j + 1]; j += 2
                if src & 0x20:
                    cnt = d[j]; j += 1; offs = None
                else:
                    cnt = 1; offs = [struct.unpack_from('<h', d, j)[0]]; j += 2
                j += 2 if flg & 0x40 else 1
                if (src & 0xf) != 2:
                    j += 4 if flg & 0x10 else 2
                if offs is None:
                    offs = list(struct.unpack_from('<%dh' % cnt, d, j)); j += 2 * cnt
                L.append((j - st, offs))
            res[(o['nr'], i)] = L
    return res


def laeufe_gueltig(X):
    """Einlesefolge: absteigende Läufe, jeder Lauf ganz oberhalb des vorigen"""
    vor_max = None; cur = [X[0]]
    for v in X[1:]:
        if v > cur[-1]:
            if vor_max is not None and min(cur) <= vor_max:
                return False
            vor_max = max(cur); cur = [v]
        else:
            cur.append(v)
    return vor_max is None or min(cur) > vor_max


def zerlege(L, pruef=None, erste=False):
    """Blockgrenzen der Seitenliste finden; liefert die Einlesefolge (Liste der Offsets) oder None.
    pruef(X) -> bool prüft eine Einlesefolge; erste=True: erste Lösung, die nur die Blockregel erfüllt"""
    pruef = pruef or laeufe_gueltig
    s = [x[0] for x in L]; v = [x[1][0] for x in L]; n = len(L)
    if any(len(x[1]) != 1 for x in L):
        return None
    loes = []

    def rek(ende, vor_groesse, bloecke):
        if len(loes) > 1 or (erste and loes):
            return
        if ende == 0:
            # bloecke: zuerst gewählt = ältester (am Listenende); Einlesefolge = ältester zuerst
            X = [v[k] for st, en in bloecke for k in range(st, en)]
            if erste or pruef(X):
                loes.append(X)
            return
        g = 0
        for st in range(ende - 1, -1, -1):
            g += s[st]
            if g > BLOCK:
                break
            # älterer Block (zuletzt gewählt) muss voll sein: seine Größe + erster Eintrag dieses Blocks > BLOCK
            if vor_groesse is not None and vor_groesse + s[st] <= BLOCK:
                continue
            # dieser Block ist nicht der neueste -> er muss gegenüber dem nächstneueren voll sein (prüft der nächste Schritt)
            rek(st, g, bloecke + [(st, ende)])

    rek(n, None, [])
    return loes[0] if (len(loes) == 1 or (erste and loes)) else None


def original_saetze(modul=None):
    """rid {(objekt, absolute_offset): satz_id}; exakt {(objekt, absolute_offset): (seite, rang)} für Seiten, die
    sich nicht als Folge absteigender Läufe lesen lassen (z. B. MASM-Teile): dort wird die Einlesefolge genau nachgebaut"""
    E = LE.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE'))
    rid = {}; exakt = {}; rang = {}; folgen = {}; nicht = 0; genau = 0
    for (ob, pg), L in seitenlisten(E).items():
        if len(L) < 2:
            continue
        X = zerlege(L)
        if X is None and modul:
            def je_modul(X, ob=ob, pg=pg):
                g = {}
                for x in X:
                    g.setdefault(modul(ob, pg * E.pgsz + x), []).append(x)
                return all(laeufe_gueltig(v) for v in g.values())
            X = zerlege(L, je_modul)
        if X is None:
            X = zerlege(L, erste=True)
            if X is None:
                nicht += 1; continue
            folgen[(ob, pg)] = [pg * E.pgsz + x for x in X]
            genau += 1
            for r, x in enumerate(X):
                if x >= 0:                         # über die Seitengrenze ragende Fixups zählen auf ihrer Startseite
                    exakt[(ob, pg * E.pgsz + x)] = (pg, r); rang[(ob, pg * E.pgsz + x)] = (pg, r)
            continue
        folgen[(ob, pg)] = [pg * E.pgsz + x for x in X]
        k = 0; prev = None
        for r, x in enumerate(X):
            if prev is not None and x > prev:
                k += 1
            if x >= 0:
                rid[(ob, pg * E.pgsz + x)] = (pg, k); rang[(ob, pg * E.pgsz + x)] = (pg, r)
            prev = x
    return rid, exakt, rang, folgen, nicht, genau, E.pgsz


# ---------- Bau: Segmentlage der OBJs ----------
def saetze(d):
    i = 0
    while i < len(d):
        t = d[i]; l = struct.unpack_from('<H', d, i + 1)[0]
        yield i, t, d[i:i + 3 + l]
        i += 3 + l


def idx(c, j):
    if c[j] & 0x80:
        return ((c[j] & 0x7f) << 8) | c[j + 1], j + 2
    return c[j], j + 1


def easy(d):
    """Easy OMF-386 (COMENT-Klasse 0xAA): auch die 16-Bit-Satztypen tragen 32-Bit-Felder"""
    return any(t == 0x88 and len(rec) > 5 and rec[4] == 0xaa for _, t, rec in saetze(d))


def segdefs(d):
    E4 = easy(d)
    names = ['']; segs = [None]
    for _, t, rec in saetze(d):
        c = rec[3:-1]
        if t == 0x96:
            j = 0
            while j < len(c):
                n = c[j]; names.append(c[j + 1:j + 1 + n].decode('latin1')); j += 1 + n
        elif t in (0x98, 0x99):
            a = c[0] >> 5; j = 1 + (3 if a == 0 else 0); w = 4 if (t == 0x99 or E4) else 2
            ln = int.from_bytes(c[j:j + w], 'little')
            if t == 0x99 and c[0] & 2:
                ln = 1 << 32
            ni, _ = idx(c, j + w)
            segs.append((names[ni], a, ln))
    return segs


AUSR = {0: 1, 1: 1, 2: 2, 3: 16, 4: 256, 5: 4, 6: 4096}


def lage(objs):
    """{(obj, segname): (objekt, offset)} über die Segmenttabelle der MAIN.MAP und die Linkfolge"""
    seg_start = {}
    for l in open(os.path.join(DOS, 'MAIN.MAP'), errors='replace'):
        m = re.match(r'(\S+)\s+\S+\s+(?:\S+\s+)?(000\d):([0-9a-f]{8})\s+([0-9a-f]{8})\s*$', l)
        if m and m.group(1) not in seg_start:
            seg_start[m.group(1)] = (int(m.group(2)), int(m.group(3), 16))
    pos = dict(seg_start); out = {}
    for p in objs:
        for sg in segdefs(open(p, 'rb').read())[1:]:
            name, a, ln = sg
            if name not in pos:
                continue
            ob, o = pos[name]; al = AUSR.get(a, 1)
            o = (o + al - 1) // al * al
            out[(p, name)] = (ob, o); pos[name] = (ob, o + ln)
    return out


def pubs_pruefen(objs, L):
    """Lage gegen die Symbole der MAP prüfen (PUBDEF-Offsets)"""
    sym = {}
    for l in open(os.path.join(DOS, 'MAIN.MAP'), errors='replace'):
        m = re.match(r'(000\d):([0-9a-f]{8})[\s*+]+(\S+)', l)
        if m:
            sym[m.group(3)] = (int(m.group(1)), int(m.group(2), 16))
    falsch = 0; gut = 0
    for p in objs:
        d = open(p, 'rb').read(); segs = segdefs(d); E4 = easy(d)
        for _, t, rec in saetze(d):
            if t not in (0x90, 0x91):
                continue
            c = rec[3:-1]; gi, j = idx(c, 0); si, j = idx(c, j)
            if si == 0 or segs[si][0] == '_BSS':
                continue
            w = 4 if (t == 0x91 or E4) else 2
            while j < len(c):
                n = c[j]; nm = c[j + 1:j + 1 + n].decode('latin1'); j += 1 + n
                off = int.from_bytes(c[j:j + w], 'little'); j += w
                if j < len(c):
                    _, j = idx(c, j)
                key = (p, segs[si][0])
                if nm in sym and key in L:
                    ob, o = L[key]
                    if sym[nm] == (ob, o + off):
                        gut += 1
                    else:
                        falsch += 1
    return gut, falsch


# ---------- Neuaufteilung ----------
def zerlegen_obj(d):
    """LEDATA/FIXUPP je Segment: {seg: {'stuecke': [(off, bytes)], 'fix': [(abs_loc, breite, subrec_bytes, satznr)],
    'li': bool, 'letzter': dateiposition, 'saetze': [dateipositionen]}}"""
    segs = segdefs(d); info = {}; aktuell = None; nr = 0; E4 = easy(d)
    for pos, t, rec in saetze(d):
        c = rec[3:-1]
        if t in (0xa0, 0xa1):
            si, j = idx(c, 0); w = 4 if (t == 0xa1 or E4) else 2
            off = int.from_bytes(c[j:j + w], 'little')
            I = info.setdefault(si, {'stuecke': [], 'fix': [], 'li': False, 'saetze': [], 'typ': t, 'e4': E4})
            I['stuecke'].append((off, c[j + w:])); I['saetze'].append(pos); I['letzter'] = pos
            aktuell = (si, off)
        elif t in (0xa2, 0xa3):
            si, _ = idx(c, 0)
            I = info.setdefault(si, {'stuecke': [], 'fix': [], 'li': False, 'saetze': [], 'typ': t}); I['li'] = True
            aktuell = None
        elif t in (0x9c, 0x9d):
            nr += 1
            if aktuell is None:
                continue
            si, base = aktuell; I = info[si]; I['saetze'].append(pos)
            j = 0
            while j < len(c):
                b = c[j]
                if not (b & 0x80):
                    I['thread'] = True
                    meth = (b >> 2) & 7; j += 1
                    if meth < 4:
                        _, j = idx(c, j)
                    continue
                st = j; loc = ((b & 3) << 8) | c[j + 1]; typ = (b >> 2) & 0xf; j += 2
                fd = c[j]; j += 1
                if not (fd & 0x80) and ((fd >> 4) & 7) < 3:
                    _, j = idx(c, j)
                if not (fd & 0x08):
                    _, j = idx(c, j)
                if not ((fd >> 2) & 1):
                    j += 4 if (t == 0x9d or E4) else 2
                I['fix'].append((base + loc, BREITE.get(typ, 4), c[st:j], nr, t))
        else:
            if t not in (0x94, 0x95, 0x88):            # LINNUM/COMENT ändern die Zuordnung nicht
                aktuell = aktuell if t in (0x8c, 0xb4) else None
    return segs, info


def pruefsumme(b):
    return b + bytes([(-sum(b)) & 0xff])


def satz(t, body):
    return pruefsumme(bytes([t]) + (len(body) + 1).to_bytes(2, 'little') + body)


def neu_aufteilen(d, si, I, grenzen, schluessel=None):
    """Segment si mit Stückanfängen 'grenzen' (sortiert, inkl. Start) neu schreiben; Rest des OBJs bleibt"""
    bild = {}
    for off, b in I['stuecke']:
        for k, x in enumerate(b):
            bild[off + k] = x
    lo, hi = min(bild), max(bild) + 1
    if len(bild) != hi - lo:
        raise ValueError('Lücke im Segmentbild')
    ends = grenzen[1:] + [hi]; neu = b''
    sib = bytes([si]) if si < 0x80 else bytes([0x80 | (si >> 8), si & 0xff])
    fixe = sorted(I['fix'], key=lambda f: f[0])
    paare = list(zip(grenzen, ends))
    if schluessel:
        paare.sort(key=lambda ae: schluessel(ae[0], ae[1]))
    for a, e in paare:
        daten = bytes(bild[k] for k in range(a, e))
        neu += satz(I['typ'], sib + a.to_bytes(4 if (I['typ'] == 0xa1 or I.get('e4')) else 2, 'little') + daten)
        sub = b''; t_ = 0x9c
        for loc, w, raw, _, t in fixe:
            if a <= loc < e:
                r = loc - a
                if r > 1023:
                    raise ValueError('Stück zu lang')
                sub += bytes([(raw[0] & 0xfc) | (r >> 8), r & 0xff]) + raw[2:]; t_ = t
        if sub:
            neu += satz(t_, sub)
    # alte LEDATA/FIXUPP des Segments streichen, neue an die Stelle des letzten LEDATA
    weg = set(I['saetze']); out = []
    for pos, t, rec in saetze(d):
        if pos == I['letzter']:
            out.append(neu)
        elif pos in weg:
            continue
        else:
            out.append(rec)
    return b''.join(out)


def plane(I, ob, base, rid, pgsz):
    """Neue Stückgrenzen oder None (nichts zu tun / nicht möglich)"""
    fixe = sorted(I['fix'], key=lambda f: f[0])
    bild_lo = min(o for o, _ in I['stuecke']); bild_hi = max(o + len(b) for o, b in I['stuecke'])
    le = [(f[0], f[1], f[3]) for f in fixe if (ob, base + f[0]) in rid]
    if len(le) < 2:
        return None
    gleich = []; trennen = []; aendern = False
    for (a, wa, ra), (b, wb, rb) in zip(le, le[1:]):
        pa, pb = rid[(ob, base + a)], rid[(ob, base + b)]
        if pa[0] != pb[0]:
            continue                                   # verschiedene Seiten: egal
        so = pa == pb; su = ra == rb
        if so != su:
            aendern = True
        (gleich if so else trennen).append((a, wa, b))
    if not aendern:
        return None
    verboten = set()
    for loc, w, *_ in fixe:
        verboten.update(range(loc + 1, loc + w))
    for a, wa, b in gleich:
        verboten.update(range(a + 1, b + 1))
    grenzen = {bild_lo}
    for a, wa, b in trennen:
        p = next((q for q in range(b, a + wa - 1, -1) if q not in verboten), None)
        if p is None:
            raise ValueError(f'keine Grenze zwischen {a:#x} und {b:#x}')
        grenzen.add(p)
    g = sorted(grenzen)
    # Länge begrenzen (Offsets im FIXUPP 10 Bit)
    k = 0
    while True:
        g = sorted(g); ends = g[1:] + [bild_hi]
        lang = next(((a, e) for a, e in zip(g, ends) if e - a > 1000), None)
        if not lang:
            break
        a, e = lang
        p = next((q for q in range(a + 1000, a, -1) if q not in verboten), None)
        if p is None:
            raise ValueError('Stück zu lang, keine erlaubte Grenze')
        g.append(p); k += 1
    return sorted(g)


def topo(knoten, ob, folgen, rang):
    """Einlesefolge für die Fixups eines Segments, die alle Seitenfolgen zugleich erfüllt (über Seitengrenzen ragende
    Fixups stehen in zwei Seiten)"""
    import heapq
    nach = {k: set() for k in knoten}; vor = {k: 0 for k in knoten}
    for (o_, pg), F_ in folgen.items():
        if o_ != ob:
            continue
        kette = [a for a in F_ if a in nach]
        for a, b in zip(kette, kette[1:]):
            if b not in nach[a]:
                nach[a].add(b); vor[b] += 1
    h = [(rang.get((ob, k), (1 << 30, 0)), k) for k in knoten if vor[k] == 0]; heapq.heapify(h); out = {}
    while h:
        _, k = heapq.heappop(h); out[k] = len(out)
        for b in nach[k]:
            vor[b] -= 1
            if vor[b] == 0:
                heapq.heappush(h, (rang.get((ob, b), (1 << 30, 0)), b))
    if len(out) != len(knoten):
        raise ValueError('Seitenfolgen widersprechen sich')
    return out


def plane_exakt(I, ob, base, rang, folgen):
    """Jeder LE-Fixup in eigenem Stück; Stücke in der Einlesefolge des Originals (Seite, Rang)"""
    fixe = sorted(I['fix'], key=lambda f: f[0])
    lo = min(o for o, _ in I['stuecke']); hi = max(o + len(b) for o, b in I['stuecke'])
    le = [f for f in fixe if (ob, base + f[0]) in rang]
    verboten = set()
    for loc, w, *_ in fixe:
        verboten.update(range(loc + 1, loc + w))
    g = {lo}; ende_vor = lo
    for f in le:
        p = next((q for q in range(f[0], ende_vor - 1, -1) if q not in verboten), None)
        if p is None:
            raise ValueError(f'keine Grenze vor {f[0]:#x}')
        g.add(p); ende_vor = f[0] + f[1]
    g = sorted(g)
    while True:
        ends = g[1:] + [hi]
        lang = next(((a, e) for a, e in zip(g, ends) if e - a > 1000), None)
        if not lang:
            break
        a, e = lang
        p = next((q for q in range(a + 1000, a, -1) if q not in verboten), None)
        if p is None:
            raise ValueError('Stück zu lang')
        g = sorted(g + [p])
    reihe = topo({base + f[0] for f in le}, ob, folgen, rang)
    lepos = {f[0]: (reihe[base + f[0]],) for f in le}

    def schluessel(a, e):
        r = [lepos[x] for x in lepos if a <= x < e]
        if len(r) > 1:
            raise ValueError('zwei LE-Fixups in einem Stück')
        return (1,) + r[0] if r else (0, a)
    return g, schluessel


def main():
    lnk = [l.strip() for l in open(os.path.join(DOS, 'MAIN.LNK'))]
    objs = [os.path.join(DOS, 'O', l.split('\\')[-1]) for l in lnk if l.upper().startswith('FILE ')]
    L = lage(objs)
    bereiche = []
    for p in objs:
        for sg in segdefs(open(p, 'rb').read())[1:]:
            if (p, sg[0]) in L and sg[2]:
                ob, o = L[(p, sg[0])]; bereiche.append((ob, o, o + sg[2], p))

    def modul(ob, a):
        return next((p for o_, lo, hi, p in bereiche if o_ == ob and lo <= a < hi), None)
    rid, exakt, rang, folgen, nicht, genau, pgsz = original_saetze(modul)
    gut, falsch = pubs_pruefen(objs, L)
    print(f'Original: {len(rid)} Fixups Sätzen zugeordnet, {genau} Seiten genau nachzubauen, {nicht} nicht zerlegbar; '
          f'Lageprüfung {gut} gut, {falsch} falsch')
    if falsch:
        print('Lage stimmt nicht - Abbruch'); return 1
    geaendert = 0
    for p in objs:
        d = open(p, 'rb').read()
        segs, info = zerlegen_obj(d)
        for si in sorted(info):
            I = info[si]; name = segs[si][0]
            if I['li'] or I.get('thread') or (p, name) not in L or not I['fix']:
                continue
            ob, base = L[(p, name)]
            try:
                if any((ob, base + f[0]) in exakt for f in I['fix']):
                    g, sch = plane_exakt(I, ob, base, rang, folgen)
                    d = neu_aufteilen(d, si, I, g, sch)
                    segs, info = zerlegen_obj(d); geaendert += 1
                    print(f'  {os.path.basename(p)} {name}: genau nachgebaut, {len(g)} Stücke'); continue
                g = plane(I, ob, base, rid, pgsz)
                if g is None:
                    continue
                d = neu_aufteilen(d, si, I, g)
                segs, info = zerlegen_obj(d)
                geaendert += 1
                print(f'  {os.path.basename(p)} {name}: neu in {len(g)} Stücke geteilt')
            except ValueError as e:
                print(f'  {os.path.basename(p)} {name}: {e}')
        open(p, 'wb').write(d)
    print(f'{geaendert} Segmente neu aufgeteilt')
    return 2 if geaendert else 0


if __name__ == '__main__':
    sys.exit(main())
