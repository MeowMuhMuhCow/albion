#!/usr/bin/env python3
"""bau_liste.py - Gesamtbau Schritt 2: Modulreihenfolge für wlink und Bibliotheksmodule als einzelne OBJs.

Das Original wurde mit FILE {Albion-OBJs} LIBRARY {...} gelinkt; wlink legt die Module in der Reihenfolge ab, in der
es sie lädt. Diese Ladefolge ist in MAIN.EXE als Code-Reihenfolge sichtbar (Richter/karte.json). Geben wir wlink alle
Module als FILE genau in dieser Reihenfolge, ergibt sich dieselbe Ablage für Code UND Daten (je Klasse in Ladefolge).

Ergebnis:
  Bau/reihenfolge.json  - Liste der Module mit Art und Herkunft
  Bau/reihenfolge.txt   - lesbar
  Bau/LIBOBJ/*.OBJ      - Module aus CLIB3R, MATH387R, EMU387, 3DM (Rohbytes aus den LIB-Dateien, unverändert)
Reines Python. Aufruf: python3 Werkzeuge/bau_liste.py
"""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.append(os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
import omf  # noqa: E402

R = os.path.join(PROJ, 'Referenz_Horneman', 'horneman_albion', 'MS-DOS')
W = os.path.join(PROJ, 'Compiler', 'w100a', 'LIB386')
LIBS = {'CLIB': os.path.join(W, 'DOS', 'CLIB3R.LIB'), 'CLIB3R': os.path.join(W, 'DOS', 'CLIB3R.LIB'),
        'MATH387R': os.path.join(W, 'MATH387R.LIB'), 'EMU387': os.path.join(W, 'DOS', 'EMU387.LIB'),
        '3DM': os.path.join(R, '121095', 'ALBION', 'LIB', '3DM.LIB')}
CB = 0x10000
NICHT_GELINKT = ('KEYINTRN', 'SINTAB', 'TANTAB')     # ihre Daten kommen in MAIN.EXE nicht vor
# Bereiche ohne Karten-Anker und woraus sie gebaut werden
AIL_MODULE = {0x8bf0b: ('AILMOD', '0x8bf0b'), 0xb2643: ('AILMOD', '0xb2643')}
ASM = {0xac31a: ('ASM', 'AIL32'), 0xc2de9: ('ASM', 'DMASND32')}
# getrennte LE-Objekte 2..6 (eigene Segmentklassen): hinter der Einheit, zu der sie gehören
# Reihenfolge der eigenen Codesegmente im Original: OPM, DSA, SYS, FNT_CODE, ZOOM_CODE (LE-Objekte 2..6). DSA_ASS und
# SYS_ASS haben weder _TEXT noch _DATA, ihre Stelle in der Liste bestimmt nur die Segmentfolge.
# OPM_ASS, FNT_ASS und ZOOM haben ein leeres DWORD-_TEXT (DSA_ASS/SYS_ASS gar keins). Im Original stehen sie zwischen
# initargv (Ende 0xb3462) und vsprintf (0xb3464): genau 2 Füllbytes. Segmentfolge OPM, DSA, SYS, FNT_CODE, ZOOM_CODE bleibt.
ASM_HINTER = {'CLIB:initargv': ['OPM_ASS', 'DSA_ASS', 'SYS_ASS', 'FNT_ASS', 'ZOOM']}
# Reine Datenmodule der Bibliotheken, die daten.py nicht sucht (keine Code-Anker): (Offset in Objekt 7, Herkunft, Modul)
CODE_FEST = {'CLIB:remove': 0x9532b, 'CLIB:errno': 0x9535a, 'CLIB:gtpid': 0xac0d4, 'CLIB:nmemneed': 0xc2186,
             'MATH387R:matherr': 0xd0486, 'CLIB:crwd386': 0xaadf6, 'CLIB:ljmphdl': 0xabdcb, 'CLIB:save8087': 0xcf2b5,
             'MATH387R:__mtherr': 0xcff68, 'EMU387:386inite': 0x94ee6}
# 22.11. nachmittags: __mtherr (jmp matherr) liegt bei 0xcff68 vor iobaddr (_RWD_matherr im Original zeigt dorthin); die beiden
# jmp-Stummel hinter fchop (0x94ee6/0x94eeb, nach __sys_init/fini_387_emulator) sind EMU387:386inite (XI/YI-Einträge).
# Reine Datenmodule der Bibliothek, deren Daten nur Nullen sind (Bytesuche unmöglich), von Hand nach den Fixup-Zielen
# im Original: argcv386 (__argc/__argv, 8 B) liegt bei 0x13ff0c direkt hinter cstrt386 (initargv schreibt dorthin)
DATEN_FEST = {'CLIB:argcv386': [('_DATA', 0x0ff0c, 8)],
              'CLIB:_8087386': [('_DATA', 0x10030, 2)],   # __8087/__real87: dosinite schreibt 0x140030/31
              'CLIB:umaskval': [('_DATA', 0x13e4c, 4)],   # open: xor eax,[0x143e4c]
              'CLIB:environ': [('_DATA', 0x13e5c, 8)],    # setenvp schreibt 0x143e5c/60
              'CLIB:amblksiz': [('_DATA', 0x16f94, 4)]}   # cinit: mov [0x146f94],8000h
DATEN_EXTRA = [(0x13e84, '3DM', 'data'), (0x0ff04, 'CLIB', 'cstrt386'),
               (0x10420, 'CLIB', 'ljmphdl'),   # Zeiger auf Code 0xabdcb (Fixup-Wert, darum nicht gefunden), vor STDMOUSP
               (0x13e54, 'CLIB', 'noefgfmt'), (0x16f80, 'CLIB', 'hook387'), (0x16f90, 'CLIB', 'heapen'),   # Bezugspunkte (Daten mit Fixups)
               # Lage der AIL-Daten (ail_daten.py) als Bezugspunkte für reine Datenmodule
               (0x0ff00, 'C', '0x8bf0b'), (0x1032c, 'C', '0xa9b04'), (0x105dc, 'C', 'AIL32'), (0x13e5c, 'C', 'DMASND32'),
               (0x02acc, 'C', '0x8bf0b'), (0x03b00, 'C', '0xa9b04'), (0x03bf8, 'C', '0xacde0'), (0x03d64, 'C', '0xae988'), (0x03e08, 'C', '0xaefd0'),
               (0x04050, 'C', '0xb2643')]               # CONST der AIL-Module (Strings)
# BSS: errno vor iob (__ClosedStreams 0x196d1c), stinit (__OpenStreams 0x199600) direkt vor localtim (0x199604)
# KEYD (pressedkeytab): im Original ein Datenmodul mit leerem PARA-_TEXT zwischen TEXTDISP und rand
# (Code: 4 Nullbytes 0x9431c-0x94320; Daten: 0x13ff24 hinter BBOPM, vor rand 0x13ffa4); PARA setzt MORGEN.sh per omf_inl
ASMDATA_VOR = {'A9B04D'}   # vor dem Besitzer: dessen eigenes _BSS (static IO in F_aa22f) liegt im Original dahinter
MODUL_NACH = [('CLIB:fltused', 'CLIB:argcv386'), ('CLIB:_8087386', 'EMU387:386inite'), ('CLIB:iob', 'CLIB:errno'),
              # stinit (leeres WORD-_TEXT): Füllbyte 0xabecb vor seterrno; seterrno/fseek/chktty ohne Daten/BSS/XI
              ('CLIB:stinit', 'CLIB:allocfp'),
              # STDMOUSP (nur Daten, _BSS leer aber PARA-ausgerichtet): BSS-seitig hinter localtim, sonst 4-8 B Lücke im BSS
              # Code: leeres PARA-_TEXT = die 6 Nullbytes 0xac31a-0xac320 vor AIL32; _DATA/_BSS dazwischen alle leer
              ('STDMOUSP', 'CLIB:d_setvec'),
              # 3DM data (_SineData, leeres PARA-_TEXT): Code-Füllung 0xc4f65-0xc4f70 vor poly32, nicht hinter environ
              # (dort 15 B zuviel); stricmp/cinit haben keine Daten, die Datenlage bleibt
              ('3DM:data', 'CLIB:cinit'),
              # Datenfolge im Original: umaskval 0x143e4c vor enterdb (___WD_Present 0x143e50); environ 0x143e5c vor den
              # DMASND32-Daten (0x143e64). Beide ohne Code (environ: leeres WORD-_TEXT, 0xc2de9 -> 0xc2dea, DMASND32 bleibt
              # bei 0xc2dec), XI-Folge unverändert
              ('CLIB:umaskval', 'CLIB:stack386'), ('CLIB:environ', 'CLIB:setvbuf'),
              # reine BSS-Module, die wlink sonst erst am Ende aus clib3r.lib nachzieht (dann hinten im BSS):
              # heapmod (___nheap_clean 0x1a5e41) vor gmtime, ___argc (0x1a5e68) vor hook387, minreal (0x1a5ef0) vor 3dm_3
              ('CLIB:heapmod', 'CLIB:hugeval'), ('CLIB:___argc', 'EMU387:emu387'), ('CLIB:minreal', 'CLIB:setenvp'),
              # seg386 (__DOSseg__, leeres WORD-_TEXT/_DATA): sonst am Ende nachgezogen -> 1 Füllbyte hinter frexp (Objekt 1
              # 788186 statt 788185 B). Vor argcv386 (WORD/DWORD) gesetzt, ändert es nichts.
              ('CLIB:seg386', 'CLIB:cstrt386')]
# AIL-Datenmodule (ail_daten.py, ML 6.0) direkt hinter ihrem Besitzer: (Name, (Art, Name des Besitzers))
ASMDATA = [('AILCD', ('AILMOD', '0x8bf0b')), ('A9B04D', ('AILREKO', '0xa9b04')), ('AIL32D', ('ASM', 'AIL32')),
           ('DMASNDD', ('ASM', 'DMASND32')), ('KEYD', ('C', 'TEXTDISP'))]          # _SineData (4104 B), gebraucht von poly32/dng32/graph32


def lib_module(pfad):
    d = open(pfad, 'rb').read(); out = {}
    psz = int.from_bytes(d[1:3], 'little') + 3 if d[0] == 0xF0 else None
    i = psz or 0
    while i < len(d):
        if d[i] == 0xF1:
            break
        if d[i] != 0x80:
            i += 1; continue
        m = omf.parse(d, i)
        roh = d[i:m['end']]
        for k in (m['name'].lower(), os.path.splitext(os.path.basename(m['name'].replace('\\', '/')))[0].lower()):
            out.setdefault(k, (m['name'], roh))
        i = m['end']
        if psz:
            i = (i + psz - 1) // psz * psz
    return out


def nachzuegler():
    """Bibliotheksmodule, die WLINK im letzten Probebau selbst aus den LIBs gezogen hat (MAIN.MAP: 'lib386'). Sie
    fehlen in der Karte (keine oder nur winzige Code-Anker), landen so aber am Ende der Ladefolge. Hier wird ihr Code
    in Objekt 1 und ihre Daten in Objekt 7 des Originals gesucht (Fixup-Stellen maskiert, nur eindeutige Treffer).
    Ergebnis wird in Bau/nachzuegler.json gesammelt (bleibt über Läufe erhalten)."""
    import re as _re, importlib.util as _iu
    pf = os.path.join(PROJ, 'Bau', 'nachzuegler.json')
    alt = json.load(open(pf)) if os.path.exists(pf) else {}
    mp = os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.MAP')
    if not os.path.exists(mp):
        return alt
    _s = _iu.spec_from_file_location('le_albion', os.path.join(HERE, 'le.py'))
    LEm = _iu.module_from_spec(_s); _s.loader.exec_module(LEm)
    E = LEm.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE')); o1 = bytes(E.objbytes(1)); o7 = bytes(E.objbytes(7))
    libname = {'clib3r.lib': 'CLIB', 'math387r.lib': 'MATH387R', 'emu387.lib': 'EMU387'}
    # Mehrdeutige Treffer eingrenzen: Code nur in Karten-Lücken (unbekannt), Daten nur außerhalb gefundener Segmente
    K_ = json.load(open(os.path.join(PROJ, 'Richter', 'karte.json')))
    luecken = [(l['start'], l['ende']) for l in K_['luecken'] if l['typ'] == 'unbekannt']
    belegt_anker = sorted((s, e) for s, e, u, i in K_['anker'])
    DK_ = json.load(open(os.path.join(PROJ, 'Analyse', 'daten_karte.json')))
    belegt = [(t_['off'], t_['off'] + t_['n']) for t_ in DK_['treffer'] if t_.get('objekt', 7) == 7 and 'nah' not in t_]

    def frei_code(x, n):
        return any(lo <= x and x + n <= hi for lo, hi in luecken) or not any(lo < x + n and x < hi for lo, hi in belegt_anker)

    def frei_daten(x, n):
        return not any(lo < x + n and x < hi for lo, hi in belegt)
    cache = {}
    for l in open(mp, 'rb').read().decode('latin1').replace('\r', '').split('\n'):
        m = _re.match(r'Module: .*?([\w]+\.lib)\((\w+)\)', l, _re.I)
        if not m or m.group(1).lower() not in libname:
            continue
        lib = libname[m.group(1).lower()]; mod = m.group(2).lower(); key = f'{lib}:{mod}'
        if key in alt:
            continue
        if lib not in cache:
            cache[lib] = lib_module(LIBS[lib])
        hit = cache[lib].get(mod)
        if not hit:
            alt[key] = {'fehlt': True}; continue
        mo = omf.parse(hit[1], 0)
        info = {'code': None, 'daten': []}
        for s in mo['segs'].values():
            d = bytes(s['data']); n = len(d)
            if n == 0 or s['cls'].upper() == 'BSS':
                continue
            pat = b''.join(b'.' if (s['mask'][k] or not s['has'][k]) else _re.escape(d[k:k + 1]) for k in range(n))
            ziel = o1 if s['cls'].upper() == 'CODE' else o7
            treffer = [x.start() for x in _re.finditer(pat, ziel, _re.S)]
            if len(treffer) > 1:
                treffer = [x for x in treffer if (frei_code if s['cls'].upper() == 'CODE' else frei_daten)(x, n)]
            if len(treffer) != 1 or sum(1 for k in range(n) if not s['mask'][k] and s['has'][k]) < 2:
                info.setdefault('unklar', []).append((s['name'], n, len(treffer))); continue
            if s['cls'].upper() == 'CODE':
                info['code'] = treffer[0] + CB
            else:
                info['daten'].append((s['name'], treffer[0], n))
        alt[key] = info
    # Winzige Stummel, die mehrfach passen, von Hand den Karten-Lücken zugeordnet (22.11.2026): remove = jmp unlnk,
    # errno = zwei 'mov eax,ofs / ret', gtpid = 'mov eax,[..] / ret', nmemneed/matherr = 'xor eax,eax / ret' (matherr
    # bei den Mathe-Modulen), 1-Byte-'ret'-Module in die drei 1-Byte-Lücken (Bytes gleich, Reihenfolge geschätzt),
    # __mtherr = erster der beiden jmp-Stummel hinter fchop (beide springen nach dosinite, geschätzt).
    for key, ca in CODE_FEST.items():
        if key in alt and (not alt[key].get('code') or alt[key].get('von_hand')):
            alt[key]['code'] = ca; alt[key]['von_hand'] = True
    for key, dl in DATEN_FEST.items():
        if key in alt and not alt[key].get('code') and (not alt[key].get('daten') or alt[key].get('von_hand')):
            alt[key]['daten'] = [list(x) for x in dl]; alt[key]['von_hand'] = True
    json.dump(alt, open(pf, 'w'), indent=1)
    return alt


def main():
    K = json.load(open(os.path.join(PROJ, 'Richter', 'karte.json')))
    F = json.load(open(os.path.join(PROJ, 'Richter', 'ail_funktionen.json')))['funktionen']
    DK = json.load(open(os.path.join(PROJ, 'Analyse', 'daten_karte.json')))
    ail = sorted((int(f['adr'], 16) - f.get('vor', 0), f) for f in F if f.get('art') != 'kruemel')   # 0x88b83 (BLEV_Check/Init_keyboard) steckt jetzt in BBEVENT.C
    folge = []

    def neu(art, name, adr, **kw):
        if folge and folge[-1]['art'] == art and folge[-1]['name'] == name:
            return
        folge.append(dict(art=art, name=name, adr=hex(adr), **kw))

    A_ = sorted(K['anker'] + [[l['start'], l['ende'], '?', l['id']] for l in K['luecken'] if l['typ'] == 'unbekannt'])
    for s, e, u, i in A_:
        a = s + CB
        if u == '?':
            if e - s <= 16 and not any(a <= x < e + CB for x, _ in ail):
                continue                                   # Füllbytes zwischen Bibliotheksmodulen
            if a in ASM:
                neu(*ASM[a], a); continue
            if a == 0x45963:
                continue                                   # steckt jetzt in GAMETEXT.C (HLC_Him2)
            for x, f in ail:
                if a <= x < e + CB:
                    lo = 0x8bf0b if 0x8bf0b <= x < 0x91256 else (0xb2643 if 0xb2643 <= x < 0xb31d2 else None)
                    if lo:
                        neu(*AIL_MODULE[lo], lo)
                    elif f.get('art') == 'asm':
                        continue                           # gehört zu AIL32/DMASND32 (oben) oder ist Füllung
                    elif f['adr'] == '0xacd17':
                        continue                           # CLIB-Module getenv..time, kommen über die Karte
                    else:
                        neu('AILREKO', f['adr'], x, flags=f.get('flags'))
            if not any(a <= x < e + CB for x, _ in ail) and a not in ASM and a < 0xd06d9:
                neu('UNBEKANNT', f'{a:#x}', a, groesse=e - s)
            continue
        if u.startswith('#'):
            lib, mod = str(i).split(':')[0], str(i).split(':')[1]
            if str(i).endswith(':BEGTEXT'):
                continue                                   # BEGTEXT (cstrt386) legt wlink per Klasse ohnehin nach vorn
            neu('LIB', f'{lib}:{mod}', a)
        else:
            neu('C', u, a)
    NZ = nachzuegler()
    for key, info in sorted(NZ.items()):
        if info.get('code'):
            ca = info['code']
            folge[:] = [z for z in folge if not (z['art'] == 'UNBEKANNT' and int(z['adr'], 16) <= ca < int(z['adr'], 16) + z.get('groesse', 1))]
            k = next((i_ for i_, z in enumerate(folge) if z['adr'] != '-' and int(z['adr'], 16) > ca), len(folge))
            folge.insert(k, dict(art='LIB', name=key, adr=hex(ca)))
    # Ein C-Modul liegt im Original am Stück: mehrfach vorkommende Einheiten (durch Lücken zwischen ihren Ankern
    # unterbrochen) auf das erste Auftreten zusammenziehen, die ASM-OBJs dahinter (ASM_HINTER) erst danach einsetzen.
    gesehen_c = set(); f2 = []
    for z in folge:
        if z['art'] == 'C':
            if z['name'] in gesehen_c:
                continue
            gesehen_c.add(z['name'])
        f2.append(z)
    folge[:] = f2
    for u_, xs in ASM_HINTER.items():
        k = next((i_ for i_, z in enumerate(folge) if z['art'] in ('C', 'LIB') and z['name'] == u_), None)
        for x in reversed(xs):
            if k is not None and not any(z['name'] == x for z in folge):
                folge.insert(k + 1, dict(art='ASMOBJ', name=x, adr='-'))
    # reine Daten-Module der Bibliotheken (ohne Code): hinter das Modul, dessen Daten davor liegen
    code_mods = {z['name'] for z in folge}
    nz_daten = [(min(d[1] for d in info['daten']), key.split(':')[0], key.split(':')[1]) for key, info in NZ.items()
                if not info.get('code') and info.get('daten')]
    dpos = sorted([(t['off'], t['herkunft'], t['modul']) for t in DK['treffer'] if t.get('objekt', 7) == 7] + DATEN_EXTRA + nz_daten)
    for i_, (off, her, mod) in enumerate(dpos):
        if her == 'ASM' or mod in NICHT_GELINKT:
            continue
        key = f'{her}:{mod.lower()}' if her != 'C' else mod
        if key in code_mods:
            continue
        vor = next((f'{h}:{m.lower()}' if h not in ('C',) else m for o_, h, m in reversed(dpos[:i_])
                    if (f'{h}:{m.lower()}' if h != 'C' else m) in code_mods), None)
        pos = next((k for k, z in enumerate(folge) if z['name'] == vor), len(folge) - 1)
        folge.insert(pos + 1, dict(art='LIB' if her != 'C' else 'C', name=key, adr='-', nur_daten=True)); code_mods.add(key)
    # Module, deren Lage nur die XI/YI-Tabellen (Init/Exit-Reihenfolge) festlegen: Original-XI = stk386, argcv386,
    # fltused (__setEFGfmt), 386inite, _8087386 (__init_8087), stinit, environ (__setenvp); YI = 386inite, stinit.
    for key, nach in MODUL_NACH:
        alt_ = next((z for z in folge if z['name'] == key), None)
        if alt_:
            folge.remove(alt_)
        k = next((i_ for i_, z in enumerate(folge) if z['name'] == nach), None)
        if k is not None:
            folge.insert(k + 1, alt_ or dict(art='LIB', name=key, adr='-', nur_daten=True))
    for nm, (art, besitzer) in ASMDATA:
        k = next((i_ for i_, z in enumerate(folge) if z['art'] == art and z['name'] == besitzer), None)
        if k is not None:
            folge.insert(k + (0 if nm in ASMDATA_VOR else 1), dict(art='ASMDATA', name=nm, adr='-'))
    # Bibliotheksmodule extrahieren
    od = os.path.join(PROJ, 'Bau', 'LIBOBJ'); os.makedirs(od, exist_ok=True)
    cache = {}; fehlt = []; n = 0
    for z in folge:
        if z['art'] != 'LIB':
            continue
        lib, mod = z['name'].split(':')
        lib = 'CLIB' if lib == 'CLIB3R' else lib
        if lib not in cache:
            cache[lib] = lib_module(LIBS[lib])
        hit = cache[lib].get(mod.lower())
        if not hit:
            fehlt.append(z['name']); continue
        n += 1; kurz = f'L{n:03d}.OBJ'
        open(os.path.join(od, kurz), 'wb').write(hit[1])
        z['obj'] = 'LIBOBJ/' + kurz; z['modulname'] = hit[0]
    json.dump(folge, open(os.path.join(PROJ, 'Bau', 'reihenfolge.json'), 'w'), indent=1)
    with open(os.path.join(PROJ, 'Bau', 'reihenfolge.txt'), 'w') as f:
        for k, z in enumerate(folge):
            f.write(f"{k:4} {z['adr']:>9} {z['art']:9} {z['name']}{'  ' + z.get('obj', '') if z.get('obj') else ''}"
                    f"{'  (nur Daten)' if z.get('nur_daten') else ''}\n")
    from collections import Counter
    print(f"{len(folge)} Module: {dict(Counter(z['art'] for z in folge))}; Bibliotheksmodule extrahiert {n}, fehlen {fehlt}")


if __name__ == '__main__':
    main()
