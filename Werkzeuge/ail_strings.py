#!/usr/bin/env python3
"""ail_strings.py - Zeichenketten eines AIL-Moduls (CONST) bytegleich machen.

Die Agenten haben Formatstrings meist als extern char D_<adr>[] eingebunden (Adresse im Original) und manchmal
Platzhalter-Literale ("2", "s1", ...) geschrieben. Für den Gesamtbau muss das Modul seine Strings selbst
enthalten, in der Reihenfolge des Originals.

  bericht MODUL   : Literale je Funktion gegen die Strings, die der Originalcode dieser Funktion anspricht
                    (LE-Fixups) - zeigt Platzhalter und falsche Strings.
  probe MODUL     : D_-Strings durch echte Literale ersetzen, Modul übersetzen, Code UND CONST gegen das
                    Original vergleichen. Ergebnis Analyse/ail_modul/MOD_<M>_STR.C
"""
import os, re, sys, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ail_modul as M  # noqa: E402
R = M.R; A = M.A; CB = M.CB
_s = importlib.util.spec_from_file_location('le_albion', os.path.join(HERE, 'le.py'))
LE = importlib.util.module_from_spec(_s); _s.loader.exec_module(LE)
EXE = LE.LE(os.path.join(R.PROJ, 'Original', 'MAIN.EXE'))
O7 = EXE.objbytes(7); B7 = 0x130000
BASIS = {o['nr']: o['basis'] for o in EXE.objs}
FX = {BASIS[s] + so: BASIS[t] + to for s, so, ty, t, to in EXE.fixups() if s == 1 and ty == 7}


def cstr(a):
    b = O7[a - B7:O7.index(b'\0', a - B7)]
    out = ''
    for x in b:
        c = chr(x)
        if c == '\n':
            out += '\\n'
        elif c == '\t':
            out += '\\t'
        elif c in '"\\':
            out += '\\' + c
        elif 32 <= x < 127:
            out += c
        else:
            out += '\\%03o' % x
    return '"' + out + '"', len(b) + 1


def const_bereich(text):
    """Strings des Moduls: alle D_13xxxx/14xxxx, die als char-Feld deklariert sind und auf eine Zeichenkette zeigen."""
    namen = set(re.findall(r'\bD_(1[34][0-9a-f]{4})\b', text))
    deklariert = set()
    for m in re.finditer(r'extern\s+(?:const\s+)?char\s+([^;]+);', text):
        for t in m.group(1).split(','):
            mm = re.match(r'\s*D_([0-9a-f]+)\s*\[\s*\]\s*$', t)
            if mm:
                deklariert.add(mm.group(1))
    # nur CONST/CONST2 (bis 0x1344c8): D_14xxxx liegt in _DATA (z. B. D_141218 = beschreibbarer Puffer "SAMPLE")
    return sorted(int(n, 16) for n in namen & deklariert if int(n, 16) < 0x1344c8)


def ersetze_strings(text, adressen):
    for a in adressen:
        lit, _ = cstr(a)
        text = re.sub(r'\bD_%x\b(?!\s*\[\s*\])' % a, lambda m: lit, text)
    # Deklarationen der ersetzten Namen entfernen (auch Sammeldeklarationen)
    weg = {'D_%x' % a for a in adressen}

    def dekl(m):
        teile = [t for t in m.group(2).split(',') if re.sub(r'\s*\[\s*\]\s*', '', t).strip() not in weg]
        return '' if not teile else m.group(1) + ','.join(teile) + ';'
    return re.sub(r'(extern\s+(?:const\s+)?char\s+)([^;]+);', dekl, text)


def bericht(blk):
    Mo = M.zusammensetzen(blk, laut=False)
    r = M.uebersetze(Mo)
    if r.get('fehler'):
        print(r['fehler'][-800:]); return
    E = M.abschnitte_messen(Mo, r)
    text = open(Mo['datei'], 'rb').read().decode('latin1')
    funk = {}
    for m in re.finditer(r'\n([A-Za-z_][\w \*]*?\b(\w+)\s*\([^;{)]*\)\s*)\{', text):
        funk[m.group(2).strip('_').lower()] = m.start()
    starts = sorted((p, n) for n, p in funk.items())
    print('Funktion                         Literale im Quelltext  |  Strings, die das Original dort anspricht')
    for nm, (o, L) in sorted(E['pos'].items(), key=lambda kv: kv[1][0]):
        if nm not in funk:
            continue
        p = funk[nm]; q = next((p2 for p2, n2 in starts if p2 > p), len(text))
        body = text[p:q]
        lits = re.findall(r'"((?:[^"\\]|\\.)*)"', body)
        if not lits:
            continue
        a0 = Mo['a0'] + o
        ziele = [FX[x] for x in sorted(FX) if a0 <= x < a0 + L and 0x132000 <= FX[x] < 0x134000]
        dn = {int(x, 16) for x in re.findall(r'\bD_(13[0-9a-f]{4})\b', body)}
        rest = [t for t in ziele if t not in dn]
        print(f'{nm[:32]:32} {lits}  |  ' + ', '.join(f'{t:#x} {cstr(t)[0][:40]}' for t in rest))


def probe(blk):
    Mo = M.zusammensetzen(blk, laut=False)
    text = open(Mo['datei'], 'rb').read().decode('latin1')
    adr = const_bereich(text)
    neu = ersetze_strings(text, adr)
    p = Mo['datei'].replace('.C', '_STR.C'); open(p, 'wb').write(neu.encode('latin1'))
    Mo['datei'] = p
    r = M.uebersetze(Mo)
    if r.get('fehler'):
        zl = [l for l in r['fehler'].splitlines() if re.search(r'Error!|\(\d+\)', l)]
        print('Übersetzungsfehler:\n' + '\n'.join(zl[:15])); return
    E = M.abschnitte_messen(Mo, r)
    print(f'Code: {sum(z["bytegleich"] for z in E["zeilen"])} von {len(E["zeilen"])} Abschnitten bytegleich am Platz')
    S = r.get('segmente', {})
    print('Segmente im OBJ:', {k: v['groesse'] for k, v in S.items()})
    c = S.get('CONST')
    if not c:
        print('kein CONST-Segment'); return
    d = bytes.fromhex(c['daten']); m = bytes.fromhex(c['maske'])
    lo = min(adr) if adr else 0
    # Anfang des Modul-CONST im Original: der erste String liegt evtl. hinter nicht referenzierten Bytes
    best = None
    for st in range(lo - 64, lo + 1):
        o = O7[st - B7:st - B7 + len(d)]
        gl = sum(1 for k in range(len(d)) if m[k] or d[k] == o[k])
        if best is None or gl > best[1]:
            best = (st, gl)
    st, gl = best
    o = O7[st - B7:st - B7 + len(d)]
    falsch = [k for k in range(len(d)) if not m[k] and d[k] != o[k]]
    print(f'CONST: {len(d)} B, bester Anfang im Original {st:#x}, gleich {gl}/{len(d)}, abweichend {len(falsch)}')
    zeig = 0
    for k in falsch:
        if zeig >= 12:
            break
        if zeig and k - zeig_k < 24:
            continue
        zeig += 1; zeig_k = k
        print(f'  {st + k:#x}: Original {O7[st + k - B7 - 8:st + k - B7 + 24]!r}\n          OBJ      {d[max(0, k - 8):k + 24]!r}')
    print('Datei:', os.path.relpath(p, R.PROJ))


if __name__ == '__main__':
    {'bericht': bericht, 'probe': probe}[sys.argv[1]](sys.argv[2].lower())
