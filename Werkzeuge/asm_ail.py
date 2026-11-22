#!/usr/bin/env python3
"""asm_ail.py - Hand-Assembler-Teile von AIL 3.03 aus MAIN.EXE als MASM-6-Quelle zurückbauen und messen.

bauen BLOCK ENDE NAME : Original von BLOCK bis ENDE linear zerlegen (capstone) und als MASM-Quelle schreiben:
                        Sprungziele im Block -> Marken L_<adr>, Ziele außerhalb -> EXTRN F_<adr>,
                        Adressen mit LE-Fixup -> Symbole (Daten D_<adr>, eigener Code OFFSET L_<adr>).
                        Sprunglängen wie im Original (SHORT / NEAR PTR). Ergebnis src/AIL/ASM/<NAME>.ASM
vergleich BLOCK ENDE OBJ : ML-Ergebnis (_TEXT) gegen das Original, Fixups maskiert; zeigt die ersten Abweichungen
                        als Befehlspaar und zählt sie nach Art (Kodierungsvarianten sammeln).
"""
import os, re, sys, json, struct, collections
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.append(os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))  # omf.py; hinten, das
import le  # noqa: E402                                     # Toolkit hat ein eigenes le.py, gemeint ist Werkzeuge/le.py
import capstone  # noqa: E402

CB = 0x10000
FLAT = open(os.path.join(PROJ, 'Analyse', 'main_flat.bin'), 'rb').read()
CS = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32); CS.detail = True
SPRUNG = {'jmp', 'call', 'loop', 'loope', 'loopne', 'jecxz', 'jcxz'}
STRING = re.compile(r'^(rep[a-z]* )?(movs|stos|lods|scas|cmps|ins|outs)[bwd]\b')


def fixups():
    L = le.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE'))
    B = {o['nr']: o['basis'] for o in L.objs}
    return {B[s] + so: (ty, t, B[t] + to) for s, so, ty, t, to in L.fixups() if s in (1, 6)}


def _mit_obj6(flat):
    """Objekt 6 (ZOOM_CODE) an seiner Basis ins flache Abbild legen, 32-Bit-Fixups eingesetzt wie in main_flat.bin."""
    L = le.LE(os.path.join(PROJ, 'Original', 'MAIN.EXE'))
    B = {o['nr']: o['basis'] for o in L.objs}
    o6 = bytearray(L.objbytes(6))
    for s, so, ty, t, to in L.fixups():
        if s == 6 and ty == 7 and 0 <= so <= len(o6) - 4:
            o6[so:so + 4] = struct.pack('<I', B[t] + to)
    F = bytearray(flat); need = B[6] + len(o6) - CB
    F += bytes(max(0, need - len(F)))
    F[B[6] - CB:B[6] - CB + len(o6)] = o6
    return bytes(F)


FLAT = _mit_obj6(FLAT)


def hexm(v):
    """Zahl in MASM-Schreibweise."""
    s = '%x' % v
    return ('0' + s if s[0] in 'abcdef' else s) + 'h' if v > 9 else str(v)


def zahl(op):
    return re.sub(r'0x([0-9a-f]+)', lambda m: hexm(int(m.group(1), 16)), op)


def zerlegen(a0, a1):
    out = []; a = a0
    while a < a1:
        b = FLAT[a - CB:min(a1, a + 16) - CB]
        i = next(CS.disasm(b, a), None)
        if i is None:
            out.append(('db', a, FLAT[a - CB])); a += 1; continue
        out.append(('i', a, i)); a += i.size
    return out


REKURSIV = False


def zerlegen_rekursiv(a0, a1, FX=None):
    """Code/Daten trennen: Befehle nur dort, wo Ausführung hinkommt (Einstiege: Abschnittsanfänge mit Aufrufern,
    Einträge von Sprungtabellen = Läufe von Fixup-Dwords im Block mit Ziel im Block). Rest = Daten (dd/db)."""
    FX = FX if FX is not None else fixups()
    tab = {s for s, (ty, tob, t) in FX.items() if a0 <= s < a1 and ty == 7}
    ein = set()
    for s in tab:
        if s + 4 in tab or s - 4 in tab:                 # Tabelle von Adressen
            t = FX[s][2]
            if FX[s][1] == 1 and a0 <= t < a1:
                ein.add(t)
    F_ = json.load(open(os.path.join(PROJ, 'Richter', 'ail_funktionen.json')))['funktionen']
    for f in F_:
        a = int(f['adr'], 16)
        if a0 <= a < a1 and 'call' in f.get('herkunft', []):
            ein.add(a)
    code = {}; arbeit = sorted(ein)
    while arbeit:
        a = arbeit.pop()
        while a0 <= a < a1 and a not in code:
            i = next(CS.disasm(FLAT[a - CB:min(a1, a + 16) - CB], a), None)
            if i is None or any(a < s < a + i.size for s in tab):
                break
            code[a] = i
            mn = i.mnemonic
            if (mn in SPRUNG or mn.startswith('j')) and i.op_str.startswith('0x'):
                t = int(i.op_str, 16)
                if a0 <= t < a1:
                    arbeit.append(t)
            if mn in ('ret', 'retf', 'iret', 'iretd', 'jmp', 'ljmp', 'hlt') or mn.startswith('ret'):
                break
            a += i.size
    ziele = {t for (ty, tob, t) in FX.values() if a0 <= t < a1}
    for i in code.values():
        if (i.mnemonic in SPRUNG or i.mnemonic.startswith('j')) and i.op_str.startswith('0x'):
            ziele.add(int(i.op_str, 16))
    out = []; a = a0
    while a < a1:
        if a in code:
            out.append(('i', a, code[a])); a += code[a].size; continue
        if a in tab and a + 4 <= a1 and not any(a + k in code for k in (1, 2, 3)):
            out.append(('dd', a, FX[a])); a += 4; continue
        b = a + 1
        while b < a1 and b not in code and b not in tab and b not in ziele and b - a < 16:
            b += 1
        out.append(('db', a, FLAT[a - CB:b - CB])); a = b
    return out


def bauen(a0, a1, name):
    FX = fixups(); Z = zerlegen_rekursiv(a0, a1, FX) if REKURSIV else zerlegen(a0, a1)
    marken, ext_f, ext_d = set(), set(), set()
    zeilen = []
    import bisect
    anf = sorted(k[1] for k in Z)

    def marke(t):
        """Ziel im Block. Liegt es mitten in einem Befehl (selbstverändernder Code: Platzhalter 9999h, die zur
        Laufzeit gepatcht werden), dann Marke am Befehlsanfang plus Abstand."""
        s_ = anf[bisect.bisect_right(anf, t) - 1]
        marken.add(s_)
        return f'L_{s_:x}' if s_ == t else f'L_{s_:x}+{t - s_}'

    for k in Z:
        if k[0] == 'db':
            bb = k[2] if isinstance(k[2], (bytes, bytearray)) else bytes([k[2]])
            zeilen.append((k[1], 'db ' + ','.join(hexm(x) for x in bb))); continue
        if k[0] == 'dd':
            ty, tob, t = k[2]
            sym = marke(t) if tob == 1 and a0 <= t < a1 else (f'F_{t:x}' if tob == 1 else f'D_{t:x}')
            (ext_f if tob == 1 and not (a0 <= t < a1) else ext_d if tob != 1 else set()).add(t)
            zeilen.append((k[1], f'dd OFFSET {sym}')); continue
        _, a, i = k
        mn, op = i.mnemonic, i.op_str
        fx = {o: FX[a + o] for o in range(i.size) if a + o in FX}
        if mn in SPRUNG or mn.startswith('j'):
            if op.startswith('0x') and not fx:
                t = int(op, 16)
                if a0 <= t < a1:
                    ziel = marke(t)
                else:
                    ext_f.add(t); ziel = f'F_{t:x}'
                if mn == 'call':
                    zeilen.append((a, f'call {ziel}')); continue
                if mn.startswith('loop') or mn in ('jecxz', 'jcxz'):
                    zeilen.append((a, f'{mn} {ziel}')); continue
                art = 'SHORT ' if i.size == 2 else 'NEAR PTR '
                zeilen.append((a, f'{mn} {art}{ziel}')); continue
        if STRING.match(mn + ' '):
            zeilen.append((a, mn)); continue
        # mov Speicher <-> Segmentregister ohne 66h-Präfix: ML setzt bei WORD PTR ein 66h davor (Lauf 2, 0xac368)
        if mn == 'mov' and re.search(r'\b[cdefgs]s\b', op) and 'word ptr' in op and i.prefix[2] != 0x66:
            op = op.replace('word ptr', 'dword ptr')
        # 16-Bit-Fernrücksprung (66h CBh) im 32-Bit-Code: dafür hat MASM kein Kürzel, im Quelltext steht db 66h vor retf
        if mn in ('retf', 'lret') and i.prefix[2] == 0x66:
            zeilen.append((a, 'db 66h')); zeilen.append((None, 'retf ' + zahl(op) if op else 'retf')); continue
        # xchg reg,reg (86/87 C0-FF): ML legt den ERSTEN Operanden ins reg-Feld, der Disassembler nennt ihn zuerst
        # als r/m. Darum Operanden tauschen (dmasnd32 Lauf 3: 86 C4 statt 86 E0).
        if mn == 'xchg' and i.bytes[i.size - 2] in (0x86, 0x87) and i.bytes[i.size - 1] >= 0xc0 and ',' in op:
            x_, y_ = [t.strip() for t in op.split(',')]
            op = f'{y_}, {x_}'
        if mn == 'pushal':
            mn = 'pushad'
        if mn == 'popal':
            mn = 'popad'
        # Adressen mit Fixup durch Symbole ersetzen
        for o, (ty, tob, ziel) in fx.items():
            if ty != 7:
                continue
            wert = struct.unpack_from('<I', FLAT, a + o - CB)[0]
            if tob == 1 and a0 <= ziel < a1:
                sym = marke(ziel)
            elif tob == 1:
                ext_f.add(ziel); sym = f'F_{ziel:x}'
            else:
                ext_d.add(ziel); sym = f'D_{ziel:x}'
            hx = '0x%x' % wert
            if f'[{hx}]' in op or re.search(r'[+\-] ' + hx + r'\]', op):
                op = op.replace(f'[{hx}]', f'[{sym}]').replace(f'+ {hx}]', f'+ {sym}]')
            else:
                op = re.sub(r'(?<![\w\[])' + hx + r'\b', 'OFFSET ' + sym, op)
        op = zahl(op).replace(' + ', '+').replace(' - ', '-').replace(' * ', '*')
        # [reg+reg] ohne Faktor: ML 6.0 wählt Basis/Index selbst (ZOOM: [ecx+ebp] -> SIB 0Dh statt 29h).
        # Der Disassembler nennt die Basis zuerst; mit *1 ist der zweite Register eindeutig der Index.
        op = re.sub(r'\[(e[a-z]{2})\+(e[a-z]{2})(?=[\]+\-])', r'[\1+\2*1', op)
        zeilen.append((a, f'{mn} {op}'.rstrip()))
    if name.lower() == 'zoom':
        return zoom_schreiben(a0, a1, name, zeilen, marken, ext_f, ext_d)
    txt = ['; AIL 3.03 - Hand-Assembler-Teil, aus MAIN.EXE zurückgebaut (Werkzeuge/asm_ail.py).',
           f'; Bereich {a0:#x} bis {a1:#x}. Bezeichner F_/D_/L_ = Adressen im Original.',
           '', '        .386', '        .MODEL FLAT', '']
    for t in sorted(ext_f):
        txt.append(f'        EXTRN F_{t:x}:NEAR')
    for t in sorted(ext_d):
        txt.append(f'        EXTRN D_{t:x}:BYTE')
    # Einsprünge, die C-Module unter Adressnamen rufen (F_xxx, _F_xxx, F_xxx_ = cdecl/watcall): offene Namen des
    # letzten Probebaus (MAIN.MAP) im Block bekommen hier ihre öffentliche Marke. Ändert keine Bytes.
    einsprung = {}
    mp = os.path.join(PROJ, 'Bau', 'DOS', 'MAIN.MAP')
    starts = {a for a, _ in zeilen}
    if os.path.exists(mp):
        for n in set(re.findall(r'Warning\(1028\): (\S+) is an undefined reference', open(mp, 'rb').read().decode('latin1'))):
            m = re.fullmatch(r'_?F_([0-9a-f]+)_?', n)
            if m and a0 <= int(m.group(1), 16) < a1 and int(m.group(1), 16) in starts:
                einsprung.setdefault(int(m.group(1), 16), set()).add(n)
    al = os.path.join(PROJ, 'Bau', 'alias.txt')         # weitere Namen, die alias_bau im Block verortet hat
    if os.path.exists(al):
        for l in open(al):
            m = re.match(r'(\S+)\s+\? Original Objekt 1 (0x[0-9a-f]+)', l)
            if m:
                a_ = int(m.group(2), 16) + 0x10000
                if a0 <= a_ < a1 and a_ in starts:
                    einsprung.setdefault(a_, set()).add(m.group(1))
    # Die Warnungen stehen nur in einer MAIN.MAP, in der der Block fehlte: gefundene Einsprünge darum dauerhaft merken
    # (sonst fehlen sie im übernächsten Bau wieder, weil der letzte Bau sie ja aufgelöst hatte)
    gm = os.path.join(PROJ, 'Bau', f'asm_einsprung_{name}.json')
    alt = json.load(open(gm)) if os.path.exists(gm) else {}
    for k, ns in alt.items():
        if a0 <= int(k, 16) < a1 and int(k, 16) in starts:
            einsprung.setdefault(int(k, 16), set()).update(ns)
    json.dump({hex(k): sorted(v) for k, v in sorted(einsprung.items())}, open(gm, 'w'), indent=1)
    for a in sorted(einsprung):
        txt.append('        PUBLIC ' + ', '.join(sorted(einsprung[a])))
    txt += ['', '        .CODE', '']
    for a, z in zeilen:
        if a in marken:
            txt.append(f'L_{a:x}:')
        for n in sorted(einsprung.get(a, ())):
            txt.append(f'{n} LABEL NEAR')
        txt.append(f'        {z}')
    txt += ['', '        END', '']
    d = os.path.join(PROJ, 'src', 'AIL', 'ASM'); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name.upper() + '.ASM')
    open(p, 'wb').write('\r\n'.join(txt).encode('latin1'))
    print(f'{name}: {len(zeilen)} Befehle, {len(marken)} Marken, {len(ext_f)} externe Funktionen, {len(ext_d)} Datenziele -> '
          f'{os.path.relpath(p, PROJ)}')


ZOOM_PUBLIC = {56: '_ZOOMFUNC_DESTCLIPX0', 60: '_ZOOMFUNC_DESTCLIPY0', 64: '_ZOOMFUNC_DESTCLIPX1', 68: '_ZOOMFUNC_DESTCLIPY1'}


def zoom_schreiben(a0, a1, name, zeilen, marken, ext_f, ext_d):
    """ZOOM.ASM (Stand 12.10.95) als vollständiges Modul: ZOOM_CODE + ZOOM_DATA (84 B) wie in der Quelle vom 22.11.95."""
    lo, hi = min(ext_d), max(ext_d)
    basis = next(b for b in range(lo - lo % 16, lo - 96, -16) if hi < b + 84)
    nam = {basis + o: n for o, n in ZOOM_PUBLIC.items()}
    txt = ['; ZOOM.ASM (ZOOMFUNC-Bibliothek), Stand 12.10.95 wie in MAIN.EXE - aus dem Programm zurückgebaut',
           '; (Werkzeuge/asm_ail.py). Die erhaltene Quelle vom 22.11.95 ist eine spätere, umgebaute Fassung.',
           '; Rahmen (Segmente, Namen der öffentlichen Symbole) aus dieser Quelle. L_/D_ = Adressen im Original.',
           '', '        .386p', '        ASSUME DS:ZOOM_DATA', '        .MODEL FLAT', '',
           '        PUBLIC _ZOOM_BLOCK_'] + [f'        PUBLIC {n}' for n in ZOOM_PUBLIC.values()]
    for t in sorted(ext_f):
        txt.append(f'        EXTRN F_{t:x}:NEAR')
    txt += ['', "ZOOM_CODE SEGMENT PARA USE32 'CODE'", '_ZOOM_BLOCK_:']
    for a, z in zeilen:
        if a in marken:
            txt.append(f'L_{a:x}:')
        for t in ext_d:
            z = re.sub(r'\bD_%x\b' % t, nam.get(t, f'D_{t:x}'), z)
        txt.append(f'        {z}')
    txt += ['ZOOM_CODE ENDS', '', "ZOOM_DATA SEGMENT PARA USE32 'DATA'"]
    for o in range(84):
        a = basis + o
        if a in ext_d or a in nam:
            txt.append(f'{nam.get(a, "D_%x" % a)} LABEL BYTE')
        txt.append('        DB ?')
    txt += ['ZOOM_DATA ENDS', '', '        END', '']
    d = os.path.join(PROJ, 'src', 'ZOOMFUNC'); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, 'ZOOM.ASM')
    open(p, 'wb').write('\r\n'.join(txt).encode('latin1'))
    print(f'zoom: {len(zeilen)} Befehle, ZOOM_DATA ab {basis:#x}, {len(ext_d)} Datenziele -> {os.path.relpath(p, PROJ)}')


def vergleich(a0, a1, obj):
    import omf
    segs = [s for m in omf.modules(obj) for s in m['segs'].values() if s['name'] in ('_TEXT', 'CODE', 'ZOOM_CODE')]
    segs.sort(key=lambda s: -len(s['data']))      # .MODEL FLAT legt ein leeres _TEXT an: das größte Codesegment zählt
    if not segs:
        print('kein _TEXT im OBJ'); return
    d, m = bytes(segs[0]['data']), bytes(segs[0]['mask'])
    orig = FLAT[a0 - CB:a1 - CB]
    print(f'Länge {len(d)}/{len(orig)}')
    Z = {a: i for t, a, i in (zerlegen_rekursiv(a0, a1) if REKURSIV else zerlegen(a0, a1)) if t == 'i'}
    arten = collections.Counter(); bsp = []
    for a, i in sorted(Z.items()):
        o = a - a0
        if o + i.size > len(d):
            break
        x, y = d[o:o + i.size], orig[o:o + i.size]
        if any(x[k] != y[k] and not m[o + k] for k in range(i.size)):
            w = next(CS.disasm(d[o:o + 16], a), None)
            art = f'{i.mnemonic} {i.op_str}'.split(',')[0][:24]
            arten[i.mnemonic] += 1
            if len(bsp) < 25:
                bsp.append(f'  {a:#x}: Original {y.hex():16} {i.mnemonic} {i.op_str} | ML {x.hex():16} '
                           f'{w.mnemonic + " " + w.op_str if w else "?"}')
            if w is None or w.size != i.size:
                bsp.append('  (Länge weicht ab, danach verschoben - weiter mit dem nächsten Lauf)'); break
    gleich = len(d) == len(orig) and all(m[k] or d[k] == orig[k] for k in range(len(d)))
    nb = [k for k in range(min(len(d), len(orig))) if not m[k] and d[k] != orig[k]]
    print(f'abweichende Bytes (maskiert verglichen): {len(nb)}' + (f', erste bei {a0 + nb[0]:#x}' if nb else ''))
    print('GLEICH' if gleich else f'abweichende Befehle nach Art: {dict(arten.most_common())}')
    print('\n'.join(bsp))


if __name__ == '__main__':
    c = sys.argv[1]; a0, a1 = int(sys.argv[2], 16), int(sys.argv[3], 16)
    REKURSIV = 'rekursiv' in sys.argv[5:]
    bauen(a0, a1, sys.argv[4]) if c == 'bauen' else vergleich(a0, a1, sys.argv[4])
