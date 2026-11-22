#!/usr/bin/env python3
"""albion.py - Richter, Karte, Arbeitsliste und Übernahme (Ratsche) für Q 007 Albion.

Grundidee
  MAIN.EXE ist eine lückenlose Folge von Übersetzungseinheiten (keine Füllbytes zwischen Modulen).
  Jedes Funktionsstück (Public bis nächstes Public), das bytegleich (Fixups maskiert) genau einmal im
  Bild steht, ist ein ANKER. Was zwischen Ankern liegt, ist eine LÜCKE. Die Karte (Richter/karte.json)
  legt einmalig fest, welche Stücke welcher Einheiten in welcher Lücke liegen. Sie ist danach gefroren.
  Gemessen wird eine Lücke, indem die übersetzten Stücke aneinandergehängt und mit dem Original-Bereich
  verglichen werden: GLEICH oder Rest = Zahl abweichender Befehle.

Befehle (alle aus dem Projektordner Q 007 Albion):
  python3 Werkzeuge/albion.py karte              Karte neu aufbauen (nur Hauptsitzung!)
  python3 Werkzeuge/albion.py bilanz             alle Lücken messen, Zustand + Fortschritt schreiben
  python3 Werkzeuge/albion.py status             wer arbeitet woran, Gesamtstand, letzte Log-Zeilen
  python3 Werkzeuge/albion.py liste [N]          offene C-Lücken, kleinster Rest zuerst
  python3 Werkzeuge/albion.py naechste --id A01  nächste freie Lücke holen (sperrt ihre Einheiten), Arbeitskopie anlegen
  python3 Werkzeuge/albion.py zeigen --id A01    Original-Assembler vs. eigene Übersetzung der Lücke
  python3 Werkzeuge/albion.py messen --id A01    Arbeitskopie messen (ändert nichts)
  python3 Werkzeuge/albion.py abgeben --id A01   Ratsche: übernehmen, wenn besser und nichts schlechter
  python3 Werkzeuge/albion.py freigeben --id A01 Sperre lösen ohne Übernahme
"""
import argparse, datetime as dt, difflib, fcntl, hashlib, json, os, re, shutil, struct, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.environ.get('ALBION_PROJ') or os.path.normpath(os.path.join(HERE, '..'))
SRC = os.path.join(PROJ, 'src')
RD = os.path.join(PROJ, 'Richter')
KARTE = os.path.join(RD, 'karte.json')
ZUSTAND = os.path.join(RD, 'zustand.json')
CACHE = os.path.join(RD, 'cache')
SPERREN = os.path.join(RD, 'sperren')
MESSLOG = os.path.join(RD, 'messungen.jsonl')
WORK = os.path.join(PROJ, 'work')
EINHEITEN = os.path.join(HERE, 'albion_einheiten.json')
FLAT = os.path.join(PROJ, 'Analyse', 'main_flat.bin')
CB = 0x10000
for p in (os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'), HERE):
    sys.path.insert(0, p)
import omf                       # noqa: E402
from emu100a import Emu100a, DEFAULT_EXE   # noqa: E402

EXE = os.environ.get('WCC386_EXE') or DEFAULT_EXE
VERBOTEN = [r'\b_?_asm\b', r'\b_emit\b', r'#\s*pragma\s+aux\b[^\n]*=\s*\\?\s*0x', r'__declspec\s*\(\s*naked']


def now():
    return dt.datetime.now().astimezone().isoformat(timespec='seconds')


def jload(p, default=None):
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else default


def jsave(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + '.tmp'
    json.dump(o, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    os.replace(tmp, p)


class Lock:
    # Sperrdateien auf der Linux-Seite (flock auf dem Windows-Laufwerk ist unter WSL nicht verlässlich)
    def __init__(self, name):
        d = os.environ.get('ALBION_LOCKDIR', '/tmp/albion_locks')
        os.makedirs(d, exist_ok=True)
        self.f = open(os.path.join(d, name + '.lock'), 'w')

    def __enter__(self):
        fcntl.flock(self.f, fcntl.LOCK_EX)

    def __exit__(self, *a):
        fcntl.flock(self.f, fcntl.LOCK_UN)


# ------------------------------------------------------------------ Übersetzen
def pubs(path):
    d = open(path, 'rb').read(); i = 0; segs = [None]; ln = ['']; out = []
    while i < len(d):
        t = d[i]; l = struct.unpack_from('<H', d, i + 1)[0]; c = d[i + 3:i + 2 + l]; i += 3 + l
        if t == 0x96:
            j = 0
            while j < len(c):
                n = c[j]; ln.append(c[j + 1:j + 1 + n].decode('latin1')); j += 1 + n
        elif t in (0x98, 0x99):
            j = 1 + (3 if (c[0] >> 5) == 0 else 0) + (4 if t == 0x99 else 2)
            sn, j = omf.idx(c, j); segs.append(ln[sn])
        elif t in (0x90, 0x91, 0xB6, 0xB7):
            g, j = omf.idx(c, 0); s, j = omf.idx(c, j)
            if s == 0:
                j += 2
            while j < len(c):
                n = c[j]; nm = c[j + 1:j + 1 + n].decode('latin1'); j += 1 + n
                off = struct.unpack_from('<I' if t & 1 else '<H', c, j)[0]; j += 4 if t & 1 else 2
                _, j = omf.idx(c, j)
                out.append((segs[s] if s < len(segs) else '?', off, nm))
        elif t in (0x8A, 0x8B):
            break
    return out


_HSTAND = None


def header_stand():
    """Pruefsumme ueber alle Header unter src/ (ohne _K). Gehoert in den Cache-Schluessel:
    sonst bleiben nach einer Header-Aenderung alte Uebersetzungen im Cache stehen."""
    global _HSTAND
    if _HSTAND is None:
        h = hashlib.sha1()
        for wurzel, dirs, files in os.walk(SRC):
            dirs[:] = sorted(d for d in dirs if d != '_K')
            for f in sorted(files):
                if f.lower().endswith(('.h', '.inc', '.g')):
                    p = os.path.join(wurzel, f)
                    h.update(os.path.relpath(p, SRC).lower().encode()); h.update(open(p, 'rb').read())
        _HSTAND = h.digest()
    return _HSTAND


def kompiliere(unit, cfg, datei=None, mit_obj=False):
    """Übersetzt eine Einheit (optional aus einer Arbeitskopie). Ergebnis: Stücke mit Daten und Maske.
    mit_obj: das OBJ wird im Cache aufgehoben (Schlüssel.obj, Pfad in out['obj']) - für den Gesamtbau."""
    src_rel = cfg['src']
    datei = datei or os.path.join(SRC, src_rel)
    text = open(datei, 'rb').read()
    # Albion-Quellen mit dem Originalpfad aufrufen: __FILE__ steht als "g:\albion\src\...c" in CONST (43 Dateien)
    orig = ('g:\\' + src_rel.replace('/', '\\').lower()) if src_rel.upper().startswith('ALBION/SRC/') else None
    if src_rel.upper().startswith('PCLIB32/SRC/'):      # PCLIB: im Quellordner mit kleinem Dateinamen ("bbbasmem.c")
        orig = os.path.basename(src_rel).lower()
    key = hashlib.sha1(text + json.dumps(cfg, sort_keys=True).encode() + b'bt=dos' + open(EXE, 'rb').read(64) + header_stand()
                       + (orig.encode() if orig else b'')
                       + (b'uhr=1996-07-25T12:39:09' if b'__DATE__' in text or b'__TIME__' in text else b'')).hexdigest()
    cp = os.path.join(CACHE, key + '.json')
    c = jload(cp)
    cobj = os.path.join(CACHE, key + '.obj')
    if c and ('segmente' in c or c.get('fehler')) and (not mit_obj or c.get('fehler') or os.path.exists(cobj)):
        if os.path.exists(cobj):
            c['obj'] = cobj
        return c
    wid = 'K%d' % os.getpid()
    wdir = os.path.join(SRC, '_K', wid)
    os.makedirs(wdir, exist_ok=True)
    tmp = os.path.join(wdir, os.path.basename(src_rel))
    open(tmp, 'wb').write(text)
    obj = os.path.join(wdir, 'OUT.OBJ')
    if os.path.exists(obj):
        os.remove(obj)
    d = os.path.dirname(src_rel).replace('/', '\\')
    # -bt=dos: der Compiler läuft hier als NT-Programm und setzte sonst __NT__ (stdlib.h: _MAX_PATH 260 statt 144,
    # andere Symbolmenge -> andere _BSS-Reihenfolge). Blue Byte übersetzte unter DOS (22.11.2026, BBDOS-Fund).
    fl = cfg['flags'] + ([] if any(x.startswith('-bt') for x in cfg['flags']) else ['-bt=dos'])
    e = Emu100a(SRC, [orig or 'C:\\_K\\%s\\%s' % (wid, os.path.basename(src_rel))] + fl + ['-zq', '-fo=C:\\_K\\%s\\OUT.OBJ' % wid],
                exe=EXE, env={'PATH': 'C:\\', 'INCLUDE': cfg['inc'], 'WATCOM': 'C:\\WATCOM.10A'})
    e.cwd = d
    if orig:
        e.alias = {(orig[2:] if orig[1:2] == ':' else orig).lower(): tmp}
    code, dts = e.run()
    out = {'fehler': None, 'stuecke': []}
    if not os.path.exists(obj):
        out['fehler'] = e.out.decode('latin1')[-1500:] or (e.fault or 'kein OBJ')
    else:
        t = None; out['segmente'] = {}
        for m in omf.modules(obj):
            for s in m['segs'].values():
                if s['name'] == '_TEXT':
                    t = s
                # alle Segmente mit Inhalt aufheben (Daten-Richter: CONST, CONST2, _DATA ...; _BSS nur Größe)
                ein = out['segmente'].setdefault(s['name'], {'klasse': s.get('cls', ''), 'daten': '', 'maske': '', 'groesse': 0})
                ein['groesse'] += len(s['data'])
                if s['name'] not in ('_TEXT', '_BSS', 'STACK'):
                    ein['daten'] += bytes(s['data']).hex(); ein['maske'] += bytes(s['mask']).hex()
        P = sorted({(o, n) for sg, o, n in pubs(obj) if sg == '_TEXT'})
        if t is not None and P:
            if P[0][0] != 0:
                P.insert(0, (0, '$vor_' + P[0][1]))
            n = len(t['data'])
            for k, (o, nm) in enumerate(P):
                e_ = P[k + 1][0] if k + 1 < len(P) else n
                out['stuecke'].append({'name': nm, 'daten': bytes(t['data'][o:e_]).hex(), 'maske': bytes(t['mask'][o:e_]).hex()})
        out['warnungen'] = e.out.decode('latin1')[-600:]
    os.makedirs(CACHE, exist_ok=True)
    if os.path.exists(obj):
        shutil.copyfile(obj, cobj); out['obj'] = cobj
    json.dump(out, open(cp, 'w'))
    return out


# ------------------------------------------------------------------ Vergleich
def finde(code, data, mask):
    best = (0, 0); st = None
    for k in range(len(data) + 1):
        if k < len(data) and not mask[k]:
            if st is None:
                st = k
        else:
            if st is not None and k - st > best[1] - best[0]:
                best = (st, k)
            st = None
    a, b = best
    if b - a < 6:
        return []
    anc = bytes(data[a:b]); hits = []; p = code.find(anc)
    while p >= 0 and len(hits) < 3:
        base = p - a
        if base >= 0 and base + len(data) <= len(code) and all(mask[k] or code[base + k] == data[k] for k in range(len(data))):
            hits.append(base)
        p = code.find(anc, p + 1)
    return hits


def passt(code, off, data, mask):
    return off + len(data) <= len(code) and all(mask[k] or code[off + k] == data[k] for k in range(len(data)))


_cs = None


def dis(b, mask=None, base=0):
    global _cs
    if _cs is None:
        import capstone
        _cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    out = []
    for i in _cs.disasm(bytes(b), base):
        op = i.op_str
        rel = i.address - base
        if (i.mnemonic == 'call' or i.mnemonic.startswith('j') or i.mnemonic.startswith('loop')) and \
                (op.startswith('0x') or (mask is not None and any(mask[rel:rel + i.size]))):
            op = 'REL'
        elif mask is not None and any(mask[rel:rel + i.size]):
            op = re.sub(r'0x[0-9a-f]+', 'X', op)
        out.append(i.mnemonic + ' ' + op)
    return out


def rest(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != 'equal')


# ------------------------------------------------------------------ Karte
def einheiten():
    return json.load(open(EINHEITEN, encoding='utf-8'))


def baue_karte(a=None):
    code = open(FLAT, 'rb').read()
    E = einheiten()
    comp = {u: kompiliere(u, c) for u, c in E.items()}
    anker = []                                    # (start, ende, einheit, idx)
    for u, r in comp.items():
        for i, s in enumerate(r['stuecke']):
            h = finde(code, bytes.fromhex(s['daten']), bytes.fromhex(s['maske']))
            if len(h) == 1:
                anker.append((h[0], h[0] + len(bytes.fromhex(s['daten'])), u, i))
    fremd = jload(os.path.join(PROJ, 'Analyse', 'fremd_anker.json'), {})   # CLIB, 3DM, ASM aus Bibliotheken
    for nm, (adr, n, herkunft) in fremd.items():
        anker.append((adr - CB, adr - CB + n, '#' + herkunft, nm))
    anker.sort()
    # Überlappungen entfernen (zweiter Treffer im selben Bereich ist verdächtig)
    sauber = []
    for x in anker:
        if sauber and x[0] < sauber[-1][1]:
            continue
        sauber.append(x)
    anker = sauber
    # Reihenfolge der Einheiten im Bild (nach erstem Anker), anker-lose Einheiten nach Link-Reihenfolge
    erst = {}
    for s, e, u, i in anker:
        if not u.startswith('#'):
            erst.setdefault(u, s)
    linkfolge = [u for u in E if u not in erst]
    # Lücken
    luecken = []
    pos = 0
    N = len(code)
    grenzen = [(s, e, u, i) for s, e, u, i in anker]
    for k, (s, e, u, i) in enumerate(grenzen + [(N, N, None, None)]):
        if s > pos:
            luecken.append({'start': pos, 'ende': s, 'vor': grenzen[k - 1][2:] if k else None, 'nach': (u, i) if u else None})
        pos = max(pos, e)
    ank = {}
    for s, e, u, i in anker:
        if not u.startswith('#'):
            ank.setdefault(u, {})[i] = s
    # Stücke den Lücken zuordnen
    for L in luecken:
        L['teile'] = []
    def luecke_bei(adr):
        for j, L in enumerate(luecken):
            if L['start'] == adr:
                return j
        return None
    def luecke_vor(adr):
        for j, L in enumerate(luecken):
            if L['ende'] == adr:
                return j
        return None
    rest_units = []
    for u, r in comp.items():
        st = r['stuecke']
        A = ank.get(u, {})
        if not A:
            rest_units.append(u); continue
        idx = sorted(A)
        # führende Stücke
        if idx[0] > 0:
            j = luecke_vor(A[idx[0]])
            if j is not None:
                luecken[j].setdefault('kopf', []).append([u, list(range(0, idx[0]))])
        for a_, b_ in zip(idx, idx[1:]):
            if b_ > a_ + 1:
                j = luecke_bei(A[a_] + len(bytes.fromhex(st[a_]['daten'])))
                if j is not None:
                    luecken[j]['teile'].append([u, list(range(a_ + 1, b_))])
        if idx[-1] < len(st) - 1:
            j = luecke_bei(A[idx[-1]] + len(bytes.fromhex(st[idx[-1]]['daten'])))
            if j is not None:
                luecken[j].setdefault('schwanz', []).append([u, list(range(idx[-1] + 1, len(st)))])
    for L in luecken:                 # Reihenfolge: Schwanz der Einheit davor, (anker-lose), Kopf der Einheit danach
        L['teile'] = L.get('schwanz', []) + L['teile'] + L.get('kopf', [])
        L.pop('schwanz', None); L.pop('kopf', None)
    for u in rest_units:              # anker-lose Einheiten: nach Link-Nachbarn einsortieren
        names = list(E)
        k = names.index(u)
        prev = next((names[x] for x in range(k - 1, -1, -1) if names[x] in ank), None)
        nxt = next((names[x] for x in range(k + 1, len(names)) if names[x] in ank), None)
        cand = None
        for j, L in enumerate(luecken):
            if prev and L['vor'] and L['vor'][0] == prev:
                cand = j; break
            if nxt and L['nach'] and L['nach'][0] == nxt:
                cand = j
        if cand is not None and comp[u]['stuecke']:
            L = luecken[cand]
            # nach dem Schwanz von prev einfügen
            pos_ins = 0
            for q, (uu, ii) in enumerate(L['teile']):
                if uu == prev:
                    pos_ins = q + 1
            L['teile'].insert(pos_ins, [u, list(range(len(comp[u]['stuecke'])))])
    for j, L in enumerate(luecken):
        L['id'] = 'L%04d' % j
        L['groesse'] = L['ende'] - L['start']
        L['typ'] = 'C' if L['teile'] else 'unbekannt'
    karte = {'erstellt': now(), 'flat_sha1': hashlib.sha1(code).hexdigest(), 'anker': [[s, e, u, i] for s, e, u, i in anker],
             'luecken': luecken, 'einheiten': list(E)}
    jsave(KARTE, karte)
    print(f'Karte: {len(anker)} Anker, {len(luecken)} Lücken, davon C {sum(1 for L in luecken if L["typ"]=="C")}, '
          f'Bytes in Lücken {sum(L["groesse"] for L in luecken)}')
    return karte


# ------------------------------------------------------------------ Messen
def messe_luecke(L, comp, code):
    data = bytearray(); mask = bytearray(); fehler = []
    for u, idxs in L['teile']:
        r = comp[u]
        if r.get('fehler'):
            fehler.append(u); continue
        for i in idxs:
            if i < len(r['stuecke']):
                data += bytes.fromhex(r['stuecke'][i]['daten']); mask += bytes.fromhex(r['stuecke'][i]['maske'])
    orig = code[L['start']:L['ende']]
    if fehler:
        return {'status': 'FEHLER', 'rest': None, 'fehler': fehler, 'laenge': len(data)}
    if len(data) == len(orig) and passt(code, L['start'], data, mask):
        return {'status': 'GLEICH', 'rest': 0, 'laenge': len(data)}
    a = dis(orig, base=L['start'] + CB); b = dis(data, mask, base=L['start'] + CB)
    return {'status': 'offen', 'rest': rest(a, b), 'laenge': len(data), 'orig_befehle': len(a)}


def anker_ok(u, comp_u, karte, code):
    """Alle Anker der Einheit müssen an ihrer Adresse gleich bleiben."""
    bad = []
    for s, e, uu, i in karte['anker']:
        if uu != u:
            continue
        st = comp_u['stuecke']
        if comp_u.get('fehler') or i >= len(st) or not passt(code, s, bytes.fromhex(st[i]['daten']), bytes.fromhex(st[i]['maske'])) \
                or len(st[i]['daten']) // 2 != e - s:
            bad.append(i)
    return bad


def bilanz(a=None, wer='Richter', wie='Bilanz'):
    karte = jload(KARTE); code = open(FLAT, 'rb').read(); E = einheiten()
    comp = {u: kompiliere(u, c) for u, c in E.items()}
    z = {'zeit': now(), 'luecken': {}}
    for L in karte['luecken']:
        if L['typ'] != 'C':
            continue
        z['luecken'][L['id']] = messe_luecke(L, comp, code)
    jsave(ZUSTAND, z)
    schreibe_fortschritt(karte, z, comp, wer, wie)
    off = [v for v in z['luecken'].values() if v['status'] != 'GLEICH']
    print(f"C-Lücken {len(z['luecken'])}: GLEICH {len(z['luecken'])-len(off)}, offen {len(off)}, Rest gesamt {sum(v['rest'] or 0 for v in off)}")
    return z


def schreibe_fortschritt(karte, z, comp, wer, wie):
    """Funktionsstände im Format von fortschritt.py ('stand'), dann fortschritt.py aufrufen."""
    E = einheiten()
    funcs = {u: [] for u in E}
    adr = {}
    for s, e, u, i in karte['anker']:
        if not u.startswith('#'):
            adr[(u, i)] = s + CB
    status = {}
    for L in karte['luecken']:
        m = z['luecken'].get(L['id'])
        for u, idxs in L['teile']:
            for i in idxs:
                status[(u, i)] = 'GLEICH' if m and m['status'] == 'GLEICH' else 'anders'
    mods = {}
    for u, cfg in E.items():
        st = comp[u].get('stuecke', [])
        mods[u] = {'snap': cfg.get('quelle', 'src'), 'grp': cfg.get('gruppe', 'alb'), 'flags': ' '.join(cfg['flags']),
                   'funcs': [[s['name'], len(s['daten']) // 2, 'GLEICH' if (u, i) in adr else status.get((u, i), 'anders'),
                              adr.get((u, i))] for i, s in enumerate(st)]}
    p = os.path.join(RD, 'stand_module.json')
    jsave(p, mods)
    import subprocess
    subprocess.run([sys.executable, os.path.join(HERE, 'fortschritt.py'), 'stand', '--module', p, '--wer', wer, '--wie', wie],
                   env=dict(os.environ, ALBION_PROJ=PROJ))


# ------------------------------------------------------------------ Arbeitsliste / Agenten
def offene(z, karte):
    L = {x['id']: x for x in karte['luecken']}
    return sorted([(v['rest'] if v['rest'] is not None else 10 ** 6, k) for k, v in z['luecken'].items() if v['status'] != 'GLEICH'],
                  key=lambda t: (t[0], L[t[1]]['groesse']))


def cmd_liste(a):
    karte = jload(KARTE); z = jload(ZUSTAND); n = int(a.n or 30)
    L = {x['id']: x for x in karte['luecken']}
    gesperrt = set(os.listdir(SPERREN)) if os.path.isdir(SPERREN) else set()
    for r, k in offene(z, karte)[:n]:
        x = L[k]; us = sorted({u for u, _ in x['teile']})
        print(f"{k}  Rest {r:>5}  {x['groesse']:>6} B  {hex(x['start']+CB)}  {'+'.join(us)}"
              f"{'  [gesperrt]' if any(u + '.lock' in gesperrt for u in us) else ''}")


def stuecknamen(L, comp):
    return [(u, [comp[u]['stuecke'][i]['name'] for i in idxs if i < len(comp[u]['stuecke'])]) for u, idxs in L['teile']]


def cmd_naechste(a):
    os.makedirs(SPERREN, exist_ok=True)
    with Lock('verteiler'):
        karte = jload(KARTE); z = jload(ZUSTAND); E = einheiten()
        Lm = {x['id']: x for x in karte['luecken']}
        besetzt = {f[:-5] for f in os.listdir(SPERREN)}
        versucht = jload(os.path.join(RD, 'versucht.json'), {})
        wahl = None
        for r, k in offene(z, karte):
            us = {u for u, _ in Lm[k]['teile']}
            if us & besetzt or r >= 10 ** 6:
                continue
            if versucht.get(k, {}).get('rest') == r and versucht[k].get('n', 0) >= 3:
                continue          # Kreislauf der Frische: dreimal ohne Fortschritt -> erst andere
            wahl = k; break
        if not wahl:
            print('KEINE FREIE LÜCKE'); return
        L = Lm[wahl]
        us = sorted({u for u, _ in L['teile']})
        for u in us:
            open(os.path.join(SPERREN, u + '.lock'), 'w').write(json.dumps({'id': a.id, 'luecke': wahl, 'seit': now()}))
        wd = os.path.join(WORK, a.id)
        os.makedirs(os.path.join(wd, 'entwuerfe'), exist_ok=True)
        for u in us:
            shutil.copy(os.path.join(SRC, E[u]['src']), os.path.join(wd, os.path.basename(E[u]['src'])))
        jsave(os.path.join(wd, 'auftrag.json'), {'id': a.id, 'luecke': wahl, 'einheiten': us, 'start': now(),
                                                 'rest_start': z['luecken'][wahl]['rest']})
    comp = {u: kompiliere(u, E[u]) for u in us}
    print(f"LÜCKE {wahl}: Rest {z['luecken'][wahl]['rest']}, {L['groesse']} Bytes ab {hex(L['start']+CB)}")
    for u, ns in stuecknamen(L, comp):
        print(f"  Einheit {u} ({E[u]['src']}), Flags {' '.join(E[u]['flags'])}: Funktionen {', '.join(ns)}")
    print(f"Arbeitskopien: work/{a.id}/  (nur die genannten Funktionen ändern)")
    print(f"Weiter: python3 Werkzeuge/albion.py zeigen --id {a.id}")
    vers = versucht.setdefault(wahl, {}); vers['n'] = vers.get('n', 0) + (1 if vers.get('rest') == z['luecken'][wahl]['rest'] else 0)
    vers['rest'] = z['luecken'][wahl]['rest']; jsave(os.path.join(RD, 'versucht.json'), versucht)


def _auftrag(a):
    wd = os.path.join(WORK, a.id)
    au = jload(os.path.join(wd, 'auftrag.json'))
    if not au:
        sys.exit(f'Kein Auftrag für {a.id}. Erst: albion.py naechste --id {a.id}')
    return wd, au


def _comp_mit_arbeitskopie(wd, au, E):
    comp = {}
    for u in au['einheiten']:
        comp[u] = kompiliere(u, E[u], os.path.join(wd, os.path.basename(E[u]['src'])))
    return comp


def cmd_zeigen(a):
    wd, au = _auftrag(a); karte = jload(KARTE); E = einheiten(); code = open(FLAT, 'rb').read()
    L = next(x for x in karte['luecken'] if x['id'] == au['luecke'])
    comp_all = {u: kompiliere(u, E[u]) for u in E}
    comp_all.update(_comp_mit_arbeitskopie(wd, au, E))
    data = bytearray(); mask = bytearray()
    for u, idxs in L['teile']:
        for i in idxs:
            s = comp_all[u]['stuecke'][i] if i < len(comp_all[u].get('stuecke', [])) else None
            if s:
                data += bytes.fromhex(s['daten']); mask += bytes.fromhex(s['maske'])
    A = dis(code[L['start']:L['ende']], base=L['start'] + CB); B = dis(data, mask, base=L['start'] + CB)
    print(f"=== {au['luecke']}  ORIGINAL ({len(A)} Befehle)  vs  EIGENE ÜBERSETZUNG ({len(B)} Befehle), Rest {rest(A, B)}")
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            n = i2 - i1
            for x in A[i1:i1 + 2]:
                print('    ' + x)
            if n > 4:
                print(f'    ... {n-4} gleiche Befehle ...')
            for x in A[max(i1 + 2, i2 - 2):i2]:
                print('    ' + x)
        else:
            for x in A[i1:i2]:
                print('  - ' + x)
            for x in B[j1:j2]:
                print('  + ' + x)
    print("(- = Original MAIN.EXE, + = eigene Übersetzung; X = Adresse/Fixup, REL = relativer Sprung/Aufruf)")


def _messe_kandidat(wd, au):
    karte = jload(KARTE); E = einheiten(); code = open(FLAT, 'rb').read()
    comp = {u: kompiliere(u, E[u]) for u in E}
    neu = _comp_mit_arbeitskopie(wd, au, E)
    for u, r in neu.items():
        if r.get('fehler'):
            return {'fehler': f'{u}: {r["fehler"]}'}
    comp.update(neu)
    res = {'luecken': {}, 'anker_verloren': {}}
    for L in karte['luecken']:
        if L['typ'] == 'C' and any(u in neu for u, _ in L['teile']):
            res['luecken'][L['id']] = messe_luecke(L, comp, code)
    for u in neu:
        bad = anker_ok(u, comp[u], karte, code)
        if bad:
            res['anker_verloren'][u] = bad
    return res


def pfoertner(wd, au, E):
    probleme = []
    for u in au['einheiten']:
        neu = open(os.path.join(wd, os.path.basename(E[u]['src'])), encoding='latin1').read()
        alt = open(os.path.join(SRC, E[u]['src']), encoding='latin1').read()
        for pat in VERBOTEN:
            if len(re.findall(pat, neu, re.I)) > len(re.findall(pat, alt, re.I)):
                probleme.append(f'{u}: verbotenes Konstrukt ({pat})')
    return probleme


def cmd_messen(a):
    wd, au = _auftrag(a); z = jload(ZUSTAND); t0 = time.time()
    E = einheiten()
    pf = pfoertner(wd, au, E)
    res = _messe_kandidat(wd, au)
    if 'fehler' in res:
        print('KOMPILIERFEHLER\n' + res['fehler']); return
    for k, v in res['luecken'].items():
        alt = z['luecken'].get(k, {})
        print(f"{k}: {v['status']} Rest {v['rest']} (vorher {alt.get('status')} Rest {alt.get('rest')})")
    if res['anker_verloren']:
        print('ACHTUNG: bisher gleiche Stücke würden verloren gehen:', res['anker_verloren'])
    if pf:
        print('PFÖRTNER:', pf)
    with open(MESSLOG, 'a') as f:
        f.write(json.dumps({'zeit': now(), 'id': a.id, 'luecke': au['luecke'], 'ergebnis': res, 'dauer_s': round(time.time() - t0, 2)}) + '\n')
    # Entwurf archivieren
    n = len(os.listdir(os.path.join(wd, 'entwuerfe')))
    for u in au['einheiten']:
        shutil.copy(os.path.join(wd, os.path.basename(E[u]['src'])), os.path.join(wd, 'entwuerfe', f'v{n+1:03d}_{os.path.basename(E[u]["src"])}'))


def cmd_abgeben(a):
    wd, au = _auftrag(a); t0 = time.time(); E = einheiten()
    with Lock('uebernahme'):
        z = jload(ZUSTAND)
        pf = pfoertner(wd, au, E)
        res = _messe_kandidat(wd, au)
        grund = None
        if 'fehler' in res:
            grund = 'Kompilierfehler'
        elif pf:
            grund = 'Pförtner: ' + '; '.join(pf)
        elif res['anker_verloren']:
            grund = 'Anker verloren: ' + json.dumps(res['anker_verloren'])
        else:
            schlechter = [k for k, v in res['luecken'].items() if z['luecken'][k]['status'] == 'GLEICH' and v['status'] != 'GLEICH'
                          or (v['rest'] is not None and z['luecken'][k]['rest'] is not None and v['rest'] > z['luecken'][k]['rest'])]
            besser = [k for k, v in res['luecken'].items() if (v['status'] == 'GLEICH' and z['luecken'][k]['status'] != 'GLEICH')
                      or (v['rest'] is not None and z['luecken'][k]['rest'] is not None and v['rest'] < z['luecken'][k]['rest'])]
            if schlechter:
                grund = 'schlechter in ' + ', '.join(schlechter)
            elif not besser:
                grund = 'keine Verbesserung'
        ok = grund is None
        ziel = au['luecke']; vorher = z['luecken'][ziel]; nachher = res.get('luecken', {}).get(ziel, {})
        if ok:
            ts = time.strftime('%Y%m%d_%H%M%S')
            for u in au['einheiten']:
                s = os.path.join(SRC, E[u]['src'])
                arch = os.path.join(PROJ, 'src_archiv', u)
                os.makedirs(arch, exist_ok=True)
                shutil.copy(s, os.path.join(arch, f'{ts}_{a.id}_{os.path.basename(s)}'))
                neu = open(os.path.join(wd, os.path.basename(s)), 'rb').read()
                if b'\r\n' in open(s, 'rb').read():          # Originaltreue: Zeilenenden wie im Original (CRLF)
                    neu = neu.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
                open(s, 'wb').write(neu)
            for k, v in res['luecken'].items():
                z['luecken'][k] = v
            z['zeit'] = now()
            jsave(ZUSTAND, z)
        wer = os.environ.get('AGENT_WER', 'Agent'); modell = os.environ.get('AGENT_MODELL', os.environ.get('AGY_MODELL', ''))
        sys.path.insert(0, HERE)
        os.environ['ALBION_PROJ'] = PROJ
        import fortschritt as F
        F.ereignis(wer=f'{wer} {a.id}', modell=modell, was='Übernahme ' + ('angenommen' if ok else 'abgelehnt'),
                   wie='albion.py abgeben (Richter + Ratsche)', einheit='+'.join(au['einheiten']), funktion=ziel,
                   start=au['start'], dauer_s=round(time.time() - dt.datetime.fromisoformat(au['start']).timestamp()),
                   erfolg='ja' if ok and nachher.get('status') == 'GLEICH' else ('teilweise' if ok else 'nein'),
                   vorher=f"{vorher['status']} Rest {vorher['rest']}", nachher=f"{nachher.get('status')} Rest {nachher.get('rest')}" if nachher else '',
                   notiz=grund or '')
    if ok:
        print(f'ÜBERNOMMEN: {ziel} {vorher["status"]} Rest {vorher["rest"]} -> {nachher.get("status")} Rest {nachher.get("rest")}')
        if any(v['status'] == 'GLEICH' for v in res['luecken'].values()):
            karte = jload(KARTE); comp = {u: kompiliere(u, c) for u, c in E.items()}
            schreibe_fortschritt(karte, z, comp, f'{wer} {a.id}', 'Übernahme')
    else:
        print('ABGELEHNT:', grund)
    if ok or a.ende:
        cmd_freigeben(a)


def cmd_freigeben(a):
    wd = os.path.join(WORK, a.id); au = jload(os.path.join(wd, 'auftrag.json'))
    if au:
        for u in au['einheiten']:
            p = os.path.join(SPERREN, u + '.lock')
            if os.path.exists(p):
                os.remove(p)
        os.rename(os.path.join(wd, 'auftrag.json'), os.path.join(wd, f'auftrag_{au["luecke"]}_erledigt.json'))
    print('freigegeben')


def cmd_status(a):
    """Kurzübersicht: wer arbeitet woran, Gesamtstand, letzte Log-Zeilen."""
    karte = jload(KARTE); z = jload(ZUSTAND)
    Lm = {x['id']: x for x in karte['luecken']}
    v = z['luecken'].values()
    g = sum(1 for x in v if x['status'] == 'GLEICH')
    print(f"Stand {z['zeit'][:16]}:  C-Lücken GLEICH {g} von {len(z['luecken'])}   offener Rest {sum(x['rest'] or 0 for x in v if x['status'] != 'GLEICH')} Befehle")
    print()
    print('Agent  Lücke  Einheit(en)            Rest jetzt  seit')
    for d in sorted(os.listdir(WORK)) if os.path.isdir(WORK) else []:
        au = jload(os.path.join(WORK, d, 'auftrag.json'))
        fertig = len([f for f in os.listdir(os.path.join(WORK, d)) if f.endswith('_erledigt.json')])
        if au and 'luecke' not in au:            # Auftrag eines anderen Richters (z. B. ail_richter.py)
            print(f"{d:6} {au.get('funktion', '?')}  AIL"); continue
        if au:
            r = z['luecken'].get(au['luecke'], {}).get('rest')
            print(f"{d:6} {au['luecke']}  {'+'.join(au['einheiten']):22} {str(r):>10}  {au['start'][11:16]}   (erledigt: {fertig})")
        else:
            print(f"{d:6} -      (sucht/fertig)                                (erledigt: {fertig})")
    if os.path.exists(os.path.join(PROJ, 'LOG.md')):
        print('\nLetzte Einträge LOG.md:')
        for l in open(os.path.join(PROJ, 'LOG.md'), encoding='utf-8').read().splitlines()[-8:]:
            print('  ' + l)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('karte'); sp.add_parser('bilanz'); sp.add_parser('status')
    l = sp.add_parser('liste'); l.add_argument('n', nargs='?')
    for c in ('naechste', 'zeigen', 'messen', 'abgeben', 'freigeben'):
        p = sp.add_parser(c); p.add_argument('--id', required=True)
        if c == 'abgeben':
            p.add_argument('--ende', action='store_true', help='auch bei Ablehnung freigeben')
    a = ap.parse_args()
    {'karte': baue_karte, 'bilanz': bilanz, 'status': cmd_status, 'liste': cmd_liste, 'naechste': cmd_naechste, 'zeigen': cmd_zeigen,
     'messen': cmd_messen, 'abgeben': cmd_abgeben, 'freigeben': cmd_freigeben}[a.cmd](a)


if __name__ == '__main__':
    main()
