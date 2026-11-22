#!/usr/bin/env python3
"""fuellbytes.py - Krücke: Füllbytes hinter Zeichenketten und Variablen (Ausrichtung in CONST/_DATA) aus dem Original.

Warum: Watcom 10.0a füllt bis zur nächsten 2/4-Byte-Grenze mit dem, was gerade in seinem Puffer bzw. im nicht
gelöschten Speicher steht (im Bau z. B. Bruchstücke des eben gelesenen Quelltexts, "fmt", "cha", " );"). Im Original
stehen dort Reste aus dem damaligen Bauvorgang ("xt", "_n ", "id In", 0x10 ...). Das hängt am Speicherzustand des
Bau-Rechners und an der verlorenen Quelle der AIL-Module, nicht am Programm. Darum werden genau diese Stellen in der
Kopie des OBJs (Bau/DOS/O) aus Original/MAIN.EXE übernommen; Quellen und OBJ-Cache bleiben unverändert.
Sicherung: die Bytes rings um jede Stelle (ohne die Füllbytes selbst) müssen im OBJ und im Original gleich sein,
sonst Abbruch (dann hat sich die Lage verschoben und die Tabelle passt nicht mehr).
Aufruf: aus bau_link.py (fuellen(pfad, quelle)); python3 Werkzeuge/fuellbytes.py zeigt die Tabelle"""
import os, struct, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)

# Quelle des OBJs (Bau-relativ) -> [(Segment, Offset im Segment des Moduls, Adresse im Original, Anzahl Füllbytes)]
FUELL = {
    'OBJ/BBSYSTEM.OBJ': [('CONST', 0x1f, 0x13271f, 1),            # hinter "SYSTEM_Init: Cannot init EVENT"
                         ('_DATA', 0x12, 0x13fdda, 2),            # hinter BBSYS_LibraryName "BBSYS Library"
                         ('_DATA', 0x1d, 0x13fde5, 3)],           # hinter SYSTEM_Library_Status (1 Byte)
    'AIL/MACDE0.OBJ': [('CONST', 0x2b, 0x133c23, 1), ('CONST', 0x52, 0x133c4a, 2), ('CONST', 0x6a, 0x133c62, 2),
                       ('CONST', 0x8e, 0x133c86, 2)],
    'AIL/MAEFD0.OBJ': [('CONST', 0x05, 0x133e0d, 3), ('CONST', 0x0d, 0x133e15, 3), ('CONST', 0x15, 0x133e1d, 3),
                       ('CONST', 0x5e, 0x133e66, 2), ('CONST', 0x76, 0x133e7e, 2), ('CONST', 0xc2, 0x133eca, 2),
                       ('CONST', 0x17d, 0x133f85, 2)],
}
RAND = 6


def _orig7():
    s = importlib.util.spec_from_file_location('le_fb', os.path.join(HERE, 'le.py'))
    LE = importlib.util.module_from_spec(s); s.loader.exec_module(LE)
    E = LE.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE'))
    return E.objbytes(7), {o['nr']: o['basis'] for o in E.objs}[7]


def _saetze(d):
    i = 0
    while i < len(d):
        t = d[i]; l = struct.unpack_from('<H', d, i + 1)[0]
        yield i, t, d[i:i + 3 + l]
        i += 3 + l


def _bild(d):
    """Segmentnamen je Index und Lage der LEDATA-Bytes: {seg: {offset: dateiposition}}"""
    names = ['']; segs = [None]; lage = {}
    for pos, t, rec in _saetze(d):
        c = rec[3:-1]
        if t == 0x96:
            j = 0
            while j < len(c):
                n = c[j]; names.append(c[j + 1:j + 1 + n].decode('latin1')); j += 1 + n
        elif t in (0x98, 0x99):
            a = c[0] >> 5; k = 1 + (3 if a == 0 else 0) + (4 if t == 0x99 else 2); segs.append(names[c[k]])
        elif t in (0xa0, 0xa1):
            si = c[0]; w = 4 if t == 0xa1 else 2; off = int.from_bytes(c[1:1 + w], 'little'); k0 = pos + 3 + 1 + w
            m = lage.setdefault(segs[si], {})
            for k in range(len(c) - 1 - w):
                m[off + k] = (k0 + k, pos)
    return lage


def fuellen(pfad, quelle):
    tab = FUELL.get(quelle.replace('\\', '/').split('Bau/')[-1])
    if not tab:
        return None
    o7, b7 = _orig7()
    d = bytearray(open(pfad, 'rb').read()); lage = _bild(bytes(d)); geaendert = set(); n = 0
    fuell = {(sg, off + i) for sg, off, _, k in tab for i in range(k)}
    for seg, off, adr, k in tab:
        m = lage.get(seg, {}); x = adr - b7
        for r in list(range(off - RAND, off)) + list(range(off + k, off + k + RAND)):
            if (seg, r) not in fuell and r in m and d[m[r][0]] != o7[x + r - off]:
                raise ValueError(f'{quelle} {seg}+{r:#x}: Umgebung passt nicht zum Original bei {adr + r - off:#x}')
        for i in range(k):
            if off + i not in m:
                raise ValueError(f'{quelle} {seg}+{off + i:#x}: nicht in LEDATA')
            fp, rp = m[off + i]
            if d[fp] != o7[x + i]:
                d[fp] = o7[x + i]; geaendert.add(rp); n += 1
    for rp in geaendert:                                       # Prüfsummen der geänderten Sätze
        l = struct.unpack_from('<H', d, rp + 1)[0]
        d[rp + 2 + l] = (-sum(d[rp:rp + 2 + l])) & 0xff
    open(pfad, 'wb').write(bytes(d))
    return f'{quelle}: {n} Füllbytes aus dem Original'


if __name__ == '__main__':
    for q, t in FUELL.items():
        print(q, [(s, hex(o), hex(a), k) for s, o, a, k in t])
