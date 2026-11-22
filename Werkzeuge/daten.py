#!/usr/bin/env python3
"""daten.py - Daten-Richter, erste Stufe: Wo liegen die Datensegmente aller Module in MAIN.EXE?

Quellen der Datensegmente: übersetzte Einheiten (albion.kompiliere hebt jetzt alle Segmente auf), die
benutzten Module der Fremdbibliotheken (CLIB3R, MATH387R, EMU387, 3DM) und die ASM-OBJs.
Jedes Segment wird maskiert (Fixups) und eindeutig in Objekt 7 bzw. 8 gesucht. Ergebnis:
Analyse/daten_karte.json, Analyse/daten_bericht.txt. Ändert nichts an src/ oder der Code-Karte.
Aufruf: python3 Werkzeuge/daten.py
"""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import albion as A  # noqa: E402
import le as LEm  # noqa: E402
import obj_abgleich as O  # noqa: E402
omf = A.omf
PROJ = A.PROJ
R = os.path.join(PROJ, 'Referenz_Horneman', 'horneman_albion', 'MS-DOS')
W = os.path.join(PROJ, 'Compiler', 'w100a', 'LIB386')
LIBS = {'CLIB': os.path.join(W, 'DOS', 'CLIB3R.LIB'), 'CLIB3R': os.path.join(W, 'DOS', 'CLIB3R.LIB'),
        'MATH387R': os.path.join(W, 'MATH387R.LIB'), 'EMU387': os.path.join(W, 'DOS', 'EMU387.LIB'),
        '3DM': os.path.join(R, '121095', 'ALBION', 'LIB', '3DM.LIB')}
ASMOBJ = [os.path.join(R, '051195', 'PCLIB32', 'SRC', d, 'OBJS', f) for d, f in
          (('BBOPM', 'OPM_ASS.OBJ'), ('BBOPM', 'FNT_ASS.OBJ'), ('BBDSA', 'DSA_ASS.OBJ'), ('BBSYSTEM', 'SYS_ASS.OBJ'))] + \
         [os.path.join(R, '121095', 'ALBION', 'SRC', 'ZOOMFUNC', 'OBJS', 'ZOOM.OBJ')]
LEER = ('_TEXT', '_BSS', 'STACK', 'OPM', 'FNT_CODE', 'DSA', 'SYS', 'ZOOM_CODE', 'BEGTEXT')
NICHT_GELINKT = ('SINTAB', 'TANTAB')     # gehören zu BBMTH, nicht gelinkt


def lib_module(pfad):
    d = open(pfad, 'rb').read(); out = {}
    for st in O.modul_starts(d):
        m = omf.parse(d, st); out[m['name'].lower()] = m
        out[os.path.splitext(os.path.basename(m['name'].replace('\\', '/')))[0].lower()] = m
    return out


def segs_aus_modul(m):
    return {s['name']: (bytes(s['data']), bytes(s['mask']), s.get('cls', '')) for s in m['segs'].values()
            if s['name'] not in LEER and len(s['data'])}


def main():
    le = LEm.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE'))
    o7, o8 = le.objbytes(7), le.objbytes(8)
    b7, b8 = le.objs[6]['basis'], le.objs[7]['basis']
    quellen = []                                   # (herkunft, name, segment, daten, maske)
    E = A.einheiten()
    for u, cfg in E.items():
        r = A.kompiliere(u, cfg)
        for sn, sg in (r.get('segmente') or {}).items():
            if sn in LEER or sn.startswith('$$') or not sg['daten'] or u in NICHT_GELINKT:
                continue                     # $$TYPES/$$SYMBOLS = Debug-Infos, landen nicht im Programm
            quellen.append(('C', u, sn, bytes.fromhex(sg['daten']), bytes.fromhex(sg['maske'])))
    fremd = A.jload(os.path.join(PROJ, 'Analyse', 'fremd_anker.json'), {})
    cache = {}
    gesehen = set()
    for k in fremd:
        teile = k.split(':')
        lib = teile[0]
        if lib not in LIBS or len(teile) < 2:
            continue
        if lib not in cache:
            cache[lib] = lib_module(LIBS[lib])
        m = cache[lib].get(teile[1].lower())
        if m is None or (lib, m['name']) in gesehen:
            continue
        gesehen.add((lib, m['name']))
        for sn, (d, mk, cls) in segs_aus_modul(m).items():
            quellen.append((lib, m['name'], sn, d, mk))
    for p in ASMOBJ:
        for m in omf.modules(p):
            for sn, (d, mk, cls) in segs_aus_modul(m).items():
                quellen.append(('ASM', os.path.basename(p), sn, d, mk))
    treffer = []; nicht = []; mehrfach = []
    for her, nm, sn, d, mk in quellen:
        h7 = A.finde(o7, d, mk); h8 = A.finde(o8, d, mk)
        if len(h7) + len(h8) == 1:
            obj, off = (7, h7[0]) if h7 else (8, h8[0])
            treffer.append({'herkunft': her, 'modul': nm, 'segment': sn, 'objekt': obj, 'off': off, 'n': len(d)})
        elif len(h7) + len(h8) > 1:
            mehrfach.append((her, nm, sn, len(d)))
        else:
            nicht.append((her, nm, sn, len(d)))
    # Stufe 2: Lage vorhersagen. wlink legt je Klasse (CONST, CONST2, _DATA) die Segmente in Linkreihenfolge
    # hintereinander; die Linkreihenfolge steht in der Code-Karte (erste Fundstelle je Modul).
    karte = A.jload(A.KARTE); reihe = []
    for st_, en_, u, i in karte['anker']:
        key = (u[1:] if u.startswith('#') else 'C', (i.split(':')[1] if u.startswith('#') and ':' in str(i) else u))
        if key not in reihe:
            reihe.append(key)
    idx = {k: n for n, k in enumerate(reihe)}
    fest = {(t['herkunft'], t['modul'].lower() if t['herkunft'] != 'C' else t['modul'], t['segment']): t for t in treffer if t['objekt'] == 7}
    nah = []
    for klasse in ('CONST', 'CONST2', '_DATA'):
        folge = sorted([q for q in quellen if q[2] == klasse and q[0] != 'ASM'],
                       key=lambda q: idx.get((q[0] if q[0] != 'CLIB3R' else 'CLIB', q[1] if q[0] == 'C' else q[1].lower()), 10 ** 6))
        pos = None
        for her, nm, sn, d, mk in folge:
            k = (her, nm.lower() if her != 'C' else nm, sn)
            if k in fest:
                pos = fest[k]['off'] + fest[k]['n']; continue
            if pos is None:
                continue
            best = None
            for al in (1, 2, 4, 8, 16):
                p0 = (pos + al - 1) // al * al
                if p0 + len(d) > len(o7):
                    continue
                diff = sum(1 for j in range(len(d)) if not mk[j] and o7[p0 + j] != d[j])
                if best is None or diff < best[0]:
                    best = (diff, p0)
            if best and best[0] <= 0.3 * len(d):
                nah.append({'herkunft': her, 'modul': nm, 'segment': sn, 'off': best[1], 'n': len(d), 'abweichend': best[0]})
                treffer.append({'herkunft': her, 'modul': nm, 'segment': sn, 'objekt': 7, 'off': best[1], 'n': len(d), 'nah': best[0]})
                nicht[:] = [x for x in nicht if not (x[0] == her and x[1] == nm and x[2] == sn)]
                pos = best[1] + len(d)
            else:
                pos = None
    gleich_nah = sum(x['n'] - x['abweichend'] for x in nah)

    def abdeckung(obj, groesse):
        iv = sorted((t['off'], t['off'] + t['n']) for t in treffer if t['objekt'] == obj)
        bel = 0; pos = 0; luecken = []
        for a, b in iv:
            if a > pos:
                luecken.append((pos, a))
            bel += max(0, b - max(a, pos)); pos = max(pos, b)
        if pos < groesse:
            luecken.append((pos, groesse))
        return bel, luecken
    zeilen = []
    for obj, data, basis in ((7, o7, b7), (8, o8, b8)):
        # Datei-Inhalt: hinter dem letzten Nicht-Null-Byte beginnt BSS (nur Nullen)
        ende = len(data.rstrip(b'\0'))
        bel, luecken = abdeckung(obj, ende)
        echt = [(a, b) for a, b in luecken if any(data[a:b])]
        zeilen.append(f'Objekt {obj}: {len(data)} B, davon mit Inhalt bis {ende:#x}; durch Segmente belegt {bel} B '
                      f'({100 * bel / max(ende, 1):.1f} %); Lücken mit Nicht-Null-Bytes: {len(echt)}, zusammen {sum(b - a for a, b in echt)} B')
        for a, b in sorted(echt, key=lambda x: -(x[1] - x[0]))[:15]:
            vor = max((t for t in treffer if t['objekt'] == obj and t['off'] + t['n'] <= a), key=lambda t: t['off'], default=None)
            zeilen.append(f'   {basis + a:#x}  {b - a:>7} B  nach {vor["herkunft"] + ":" + vor["modul"] + ":" + vor["segment"] if vor else "-"}')
    st = collections.Counter(); sb = collections.Counter()
    for t in treffer:
        st[t['herkunft']] += 1; sb[t['herkunft']] += t['n']
    zeilen.append(f'Nach Lage zugeordnet (Stufe 2): {len(nah)} Segmente, {sum(x["n"] for x in nah)} B, davon gleich {gleich_nah} B, '
                  f'abweichend {sum(x["abweichend"] for x in nah)} B in {sum(1 for x in nah if x["abweichend"])} Segmenten')
    for x in sorted(nah, key=lambda x: -x['abweichend'])[:20]:
        if x['abweichend']:
            zeilen.append(f'   {x["herkunft"]}:{x["modul"]}:{x["segment"]} bei {0x130000 + x["off"]:#x}: {x["abweichend"]} von {x["n"]} B anders')
    zeilen.append('Gefunden je Herkunft: ' + ', '.join(f'{k} {st[k]} Segmente/{sb[k]} B' for k in st))
    zeilen.append(f'Nicht gefunden: {len(nicht)} Segmente, {sum(x[3] for x in nicht)} B; mehrdeutig: {len(mehrfach)} Segmente, {sum(x[3] for x in mehrfach)} B')
    for x in sorted(nicht, key=lambda x: -x[3])[:25]:
        zeilen.append(f'   nicht gefunden: {x[0]}:{x[1]}:{x[2]} {x[3]} B')
    A.jsave(os.path.join(PROJ, 'Analyse', 'daten_karte.json'), {'treffer': treffer, 'nicht': nicht, 'mehrfach': mehrfach, 'nah': nah})
    open(os.path.join(PROJ, 'Analyse', 'daten_bericht.txt'), 'w', encoding='utf-8').write('\n'.join(zeilen) + '\n')
    print('\n'.join(zeilen))


if __name__ == '__main__':
    main()
