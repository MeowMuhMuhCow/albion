#!/usr/bin/env python3
"""ail_daten.py - Daten der AIL-Teile als eigene kleine ASM-Module (ML 6.0), die in der Ladefolge direkt hinter dem
Modul stehen, zu dem die Daten im Original gehören. Die Agenten-Quellen kennen ihre Variablen nur als extern.

Blöcke (Original-Adressen, aus den Verweisen des AIL-Codes und den Nachbarsegmenten bestimmt, 22.11.2026):
  AILCD    hinter AIL.C (0x8bf0b):  _DATA 0x13ff00-0x13ff04, _BSS 0x1890fc-0x189140
  A9B04D   hinter 0xa9b04:         _DATA 0x14032c-0x140334 (AIL_bkgnd_flag, AIL_locked)
  AIL32D   hinter AIL32:           _DATA 0x1405dc-0x1412b0 (auch die Daten von 0xacde0/0xaefd0/0xb2643, dort steht
                                   keine eigene Definition), _BSS 0x199440-0x199880
  KEYD     hinter FNT_ASS:         _DATA 0x13ff24-0x13ffa4 (pressedkeytab)
  DMASNDD  hinter DMASND32:        _DATA 0x143e64-0x143e84 (Endmarke D_143e84 = Anfang 3DM:data)
Jede angesprochene Adresse bekommt eine öffentliche Marke D_<adr> und _D_<adr> (C-Seite), dazu die AIL-Namen aus
ail_modul.ALIAS. Ausgabe: src/AIL/ASM/<NAME>.ASM
Aufruf: python3 Werkzeuge/ail_daten.py"""
import os, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
_s = importlib.util.spec_from_file_location('le_albion', os.path.join(HERE, 'le.py'))
LE = importlib.util.module_from_spec(_s); _s.loader.exec_module(LE)

B7 = 0x130000
CODE = [(0x8bf0b, 0x91256), (0xa9b04, 0xaa466), (0xac31a, 0xacd17), (0xacde0, 0xaefd0), (0xaefd0, 0xb2643),
        (0xb2643, 0xb31d2), (0xc2de9, 0xc4f21)]
ALIAS = {0x1890fc: 'AIL_debugfile', 0x189100: 'AIL_debug', 0x189104: 'AIL_sys_debug', 0x189110: 'AIL_indent',
         0x13ff24: 'pressedkeytab'}
MODULE = {
    'AILCD': [('DATA', 0x13ff00, 0x13ff04), ('BSS', 0x1890fc, 0x189140)],
    # BSS 0x199600 = __OpenStreams (stinit), 0x199604-0x199628 = localtim (struct tm): Bibliothek, nicht AIL
    # 0x1995e8-0x199600 = static IO_PARMS IO (F_aa22f) im C-Modul selbst -> A9B04D steht VOR dem Modul
    'A9B04D': [('DATA', 0x14032c, 0x140334), ('BSS', 0x199440, 0x1995e8)],
    'AIL32D': [('DATA', 0x1405dc, 0x1412b0), ('BSS', 0x199628, 0x199880)],
    'DMASNDD': [('DATA', 0x143e64, 0x143e84)],   # 0x143e5c/60 = environ (_environ/__env_mask, setenvp)
    # Tastaturtabelle (128 B, liest BBSYSTEM und der Krümel 0x88b83): im Original hinter den BBOPM-Daten, vor rand
    'KEYD': [('DATA', 0x13ff24, 0x13ffa4)],
}
ENDMARKEN = {'DMASNDD': [0x143e84]}
EXTRA_MARKEN = {'KEYD': [0x13ff24]}


def ext_fixups(pfad):
    """OMF: (Segmentname, Offset, Externname) für jeden Fixup, dessen Ziel ein EXTDEF ist."""
    import struct
    d = open(pfad, 'rb').read(); i = 0; ln = ['']; segs = ['']; ext = ['']; out = []; last = None
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
        elif t in (0x8C, 0xB4):
            j = 0
            while j < len(c):
                n = c[j]; ext.append(c[j + 1:j + 1 + n].decode('latin1')); j += 1 + n
                _, j = idx(j)
        elif t in (0xA0, 0xA1):
            s, j = idx(0); off = struct.unpack_from('<I' if t == 0xA1 else '<H', c, j)[0]; last = (segs[s], off)
        elif t in (0x9C, 0x9D):
            j = 0; thr = {}
            while j < len(c):
                b = c[j]
                if not b & 0x80:                          # THREAD
                    meth = (b >> 2) & 7; D = b & 0x40; num = b & 3; j += 1
                    if meth < 3:
                        v, j = idx(j)
                    else:
                        v = None
                    if not D:
                        thr[('T', num)] = (meth, v)
                    continue
                doff = ((b & 3) << 8) | c[j + 1]; j += 2
                fd = c[j]; j += 1
                F = fd & 0x80; fm = (fd >> 4) & 7; T = fd & 8; P = fd & 4; tm = fd & 3
                if not F:
                    if fm < 3:
                        _, j = idx(j)
                if not T:
                    tv, j = idx(j); meth = tm
                else:
                    meth, tv = thr.get(('T', tm), (None, None))
                if not P:
                    j += 4 if t == 0x9D else 2
                if last and meth in (2, 6) and tv is not None and tv < len(ext):
                    out.append((last[0], last[1] + doff, ext[tv]))
    return out


def benannte(E):
    """Namen der Variablen in den AIL-Modul-OBJs (Bau/AIL/*.OBJ) -> Original-Adresse, per Mehrheit über die Stellen,
    an denen das OBJ im Original liegt (Modulanfang + Offset im _TEXT)."""
    import collections, re as _re
    fx = {so + 0x10000: to + B7 for s, so, ty, t, to in E.fixups() if s == 1 and t == 7}
    stimmen = collections.defaultdict(collections.Counter)
    d = os.path.join(PROJ, 'Bau', 'AIL')
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        m = _re.fullmatch(r'[MK]([0-9A-F]+)\.OBJ', f)
        if not m:
            continue
        a0 = int(m.group(1), 16)
        try:                                              # Lage über die Funktion, in der der Fixup steht
            import alias_bau as AB, bisect
            fs = AB.funktionsanfaenge(os.path.join(d, f)); fo = [x[0] for x in fs]
        except Exception:
            fs, fo = [], []
        for seg, off, n in ext_fixups(os.path.join(d, f)):
            if seg != '_TEXT':
                continue
            q = a0 + off
            if fo:
                j = bisect.bisect_right(fo, off) - 1
                if j >= 0:
                    q = fs[j][1] + off - fs[j][0]
            if q in fx:
                stimmen[n.lstrip('_')][fx[q]] += 1
    code = set()                                          # im letzten Probebau als Code definierte Namen: keine Daten
    mp = os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.MAP')
    if os.path.exists(mp):
        for l in open(mp, 'rb').read().decode('latin1').split('\n'):
            mm = _re.match(r'0001:[0-9a-f]{8}[ +*]+(\S+)', l)
            if mm:
                code.add(mm.group(1).lstrip('_'))
    out = []
    for n, c in stimmen.items():
        if n in code:
            continue
        (a, k), = c.most_common(1)
        if k >= 2 or len(c) == 1:
            out.append((a, n))
    return out


def main():
    E = LE.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE')); o7 = bytes(E.objbytes(7))
    ziele = set(); innen = {}
    for s, so, ty, t, to in E.fixups():
        if t == 7 and s == 1 and any(lo <= so + 0x10000 < hi for lo, hi in CODE):
            ziele.add(to + B7)
        if s == 7:
            innen[so + B7] = (t, to)
    namen = {a: [n] for a, n in ALIAS.items()}
    for a, n in benannte(E):
        if n not in namen.get(a, []) and not n.startswith('D_'):
            namen.setdefault(a, []).append(n)
    od = os.path.join(PROJ, 'src', 'AIL', 'ASM'); os.makedirs(od, exist_ok=True)
    for name, bloecke in MODULE.items():
        marken = sorted(set([a for a in ziele if any(lo <= a < hi for _, lo, hi in bloecke)] + ENDMARKEN.get(name, [])
                            + EXTRA_MARKEN.get(name, [])))
        pub = []
        for a in marken:
            pub += [f'D_{a:x}', f'_D_{a:x}'] + [f'_{n}' for n in namen.get(a, [])]
        z = [f'; AIL 3.03 - Daten aus MAIN.EXE ({name}), erzeugt von Werkzeuge/ail_daten.py.',
             '; Marken D_<adr> = Adressen im Original.', '', '        .386', '        .MODEL FLAT', '']
        for k in range(0, len(pub), 6):
            z.append('        PUBLIC ' + ', '.join(pub[k:k + 6]))
        z.append('')
        for art, lo, hi in bloecke:
            z.append('        .DATA' if art == 'DATA' else '        .DATA?')
            ms = [a for a in marken if lo <= a < hi or (a == hi and a in ENDMARKEN.get(name, []))]
            p = lo
            for a in sorted(set(ms + [hi])):
                if a > p:
                    if art == 'BSS':
                        z.append(f'        db {a - p} dup(?)')
                    else:
                        roh = o7[p - B7:a - B7]
                        if any(q in innen for q in range(p, a)):
                            print(f'{name}: Zeiger im Datenblock {p:#x}-{a:#x}, nicht unterstützt'); sys.exit(1)
                        if not any(roh):
                            z.append(f'        db {a - p} dup(0)')
                        else:
                            for k in range(0, len(roh), 16):
                                z.append('        db ' + ', '.join(f'0{b:02x}h' for b in roh[k:k + 16]))
                    p = a
                if a in marken and (a < hi or a in ENDMARKEN.get(name, [])):
                    z.append(f'D_{a:x} LABEL BYTE')
                    z.append(f'_D_{a:x} LABEL BYTE')
                    for n in namen.get(a, []):
                        z.append(f'_{n} LABEL BYTE')
            z.append('')
        z.append('        END')
        open(os.path.join(od, name + '.ASM'), 'w', newline='\r\n').write('\n'.join(z) + '\n')
        print(f'{name}: {len(marken)} Marken, ' + ', '.join(f'{art} {hi - lo} B' for art, lo, hi in bloecke))


if __name__ == '__main__':
    main()
