#!/usr/bin/env python3
"""ail_modul.py - AIL-Funktionen eines Blocks zu EINER Moduldatei zusammensetzen und als Ganzes messen.

Grund: Watcom legt gleiche Funktionsenden innerhalb eines Moduls zusammen (Quersprünge, z. B. 20 AIL-Hüllen auf
0x8c62e). Das entsteht nur, wenn die Funktionen gemeinsam in einer Datei übersetzt werden.
Ablauf: Fassungen aus src/AIL/REKO in Adressreihenfolge, je Datei nur die eigenen Funktionen (Hilfskopien von
Funktionen anderer Abschnitte fallen weg), Deklarationen zusammengeführt, dann mit jedem Flagsatz übersetzt und
gegen den ganzen Block verglichen. Ergebnis: Analyse/ail_modul/MOD_<BLOCK>.C und Bericht. Ändert nichts am Stand,
außer mit --uebernehmen: dann werden Abschnitte, deren Funktionen im Modul an der richtigen Stelle bytegleich
sind, als GLEICH (modul) eingetragen.
Aufruf: python3 Werkzeuge/ail_modul.py 0x8bf0b [--uebernehmen]
"""
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ail_richter as R  # noqa: E402
A = R.A; CB = R.CB


# Module = Adressbereiche, die nachweislich EINE Quelldatei sind (Quersprünge zwischen ihren Abschnitten)
MODULE = {'0x8bf0b': (0x8bf0b, 0x91256),     # große AIL.C, 104 Quersprung-Kanten
          '0xb2643': (0xb2643, 0xb31d2),     # WAVESYN.C (Kanten b2ab9->b2a4d, b3154->b2ab9; b24b0->b2843 war Tabelle)
          # Nacht 22.11.: Modulgrenzen aus der Füllung vor 16-ausgerichteten Funktionen (Compiler-Füllbefehle =
          # gleiches Modul, reine Nullen = Linker = neues Modul); noch nicht gemessen
          '0xa9b04': (0xa9b04, 0xaa466),     # 9 Abschnitte, -s
          '0xacde0': (0xacde0, 0xae988),     # DIGPLAY-Bereich, -s -oneatx -4r (Funktionen 16-ausgerichtet)
          # 22.11. nachmittags: ab 0xae988 nicht mehr ausgerichtet, Texte "fmt "/"data"/"Creative"/"WAVE" ungepolstert
          # -> eigene Übersetzungseinheit (Datei-/VOC/WAV-Teil), andere Flags
          '0xae988': (0xae988, 0xaefd0),
          '0xaefd0': (0xaefd0, 0xb24b0),     # XMIDI.C (M06), -s -oneatx -4r
          # 0xb24b0 ruft F_af150, statt es einzubetten -> eigene Übersetzungseinheit (dann GANZER BLOCK GLEICH)
          '0xb24b0': (0xb24b0, 0xb2643)}
# XMI_flush_buffer/MDI_flush der Agenten = F_af150 (gleicher Rumpf, liegt vor den Aufrufern, wird mit -oe eingebettet)
HILFS_ALIAS = {'XMI_flush_buffer': 'F_af150', 'MDI_flush': 'F_af150'}
# Agenten-Hilfen, die im Original nur eingebettet vorkommen (kein eigener Code im Modul): als Makro
# Eingebettete Hilfen mit eigenem Rumpf: Watcom gibt die statische Funktion trotz Einbettung zusätzlich aus. Diese
# Kopie kommt in ein Segment der Klasse DEBSYM (WLINK übernimmt Debug-Klassen nicht ins Programm), danach code_seg().
HILFS_WEG = {'XMI_send_sysex', 'XMI_rewind_sequence'}
HILFS_MAKRO = {}
# 0xaf0f0 (Länge eines MIDI-Ereignisses) steht im Original als eigene Funktion UND eingebettet in F_b01f0: static
MODUL_STATISCH = {'0xaefd0': ['F_af0f0']}
UMDEUTEN = {'0xa9b04', '0xacde0', '0xae988', '0xaefd0', '0xb24b0'}           # Module, in denen abweichende Variablentypen per Makro gelten
MODUL_FLAGS = {'0xacde0': ('-s', '-oneatx', '-4r'), '0xaefd0': ('-s', '-oneatx', '-4r'), '0xa9b04': ('-s', '-4r'), '0xae988': ('-s', '-4r'), '0xb24b0': ('-s', '-oneatx', '-4r')}


ALIAS = {'D_1890fc': 'AIL_debugfile', 'D_189100': 'AIL_debug', 'D_189104': 'AIL_sys_debug', 'D_189110': 'AIL_indent'}


def modul_von(adr):
    a = int(adr, 16)
    return next((k for k, (lo, hi) in MODULE.items() if lo <= a < hi), None)


def teile(text):
    """C-Text in oberste Einheiten zerlegen: ('pp', zeile) | ('decl', text) | ('func', name, text)."""
    t = re.sub(r'/\*.*?\*/', ' ', text, flags=re.S); t = re.sub(r'//[^\n]*', ' ', t)
    out = []; i = 0; n = len(t); start = 0; tiefe = 0
    while i < n:
        c = t[i]
        if tiefe == 0 and c == '#' and (i == 0 or t[i - 1] == '\n' or t[start:i].strip() == ''):
            j = i
            while True:                                   # Fortsetzungszeilen (\ am Zeilenende) gehören dazu
                k = t.find('\n', j); k = n if k < 0 else k
                if t[j:k].rstrip().endswith('\\') and k < n:
                    j = k + 1; continue
                break
            out.append(('pp', t[i:k].strip())); i = k + 1; start = i; continue
        if c in '"\'':
            q = c; i += 1
            while i < n and t[i] != q:
                i += 2 if t[i] == '\\' else 1
            i += 1; continue
        if c == '{':
            tiefe += 1
        elif c == '}':
            tiefe -= 1
            if tiefe == 0:
                k = i + 1
                while k < n and t[k] in ' \t\r\n':
                    k += 1
                kopf = t[start:t.find('{', start)]
                if (k >= n or t[k] != ';') and re.search(r'\)\s*$', kopf.strip()) and '=' not in kopf:
                    m = re.search(r'(\w+)\s*\([^()]*(\([^()]*\)[^()]*)*\)\s*$', kopf.strip())
                    out.append(('func', m.group(1) if m else '?', t[start:i + 1].strip())); i += 1; start = i; continue
        elif c == ';' and tiefe == 0:
            s = t[start:i + 1].strip()
            if s:
                out.append(('decl', s))
            i += 1; start = i; continue
        i += 1
    return out


def dis(b, mask):
    import capstone
    cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    out = []
    for i in cs.disasm(bytes(b), 0):
        op = i.op_str; m = any(mask[i.address:i.address + i.size])
        if (i.mnemonic == 'call' or i.mnemonic.startswith('j') or i.mnemonic.startswith('loop')) and (op.startswith('0x') or m):
            op = 'REL'
        elif m:
            op = re.sub(r'0x[0-9a-f]+|(?<![\w.])\d+(?![\w.])', 'X', op)
        out.append(i.mnemonic + ' ' + op)
    return out


def name_der_decl(d):
    d2 = re.sub(r'__based\s*\((?:[^()]|\([^()]*\))*\)', ' ', re.sub(r'\s+', ' ', d))   # __based(__segname("_CODE"))
    while True:                                   # Körper { ... } (auch verschachtelt) entfernen: Member-Namen und
        d3 = re.sub(r'\{[^{}]*\}', ' ', d2)       # Funktionszeiger darin sind nicht der deklarierte Name
        if d3 == d2:
            break
        d2 = d3
    d2 = re.sub(r'\s+', ' ', d2)
    mf = re.match(r'\s*typedef\b.*?\(\s*(?:\w+\s+)*\*\s*(\w+)\s*\)\s*\(', d2)
    if mf:
        return mf.group(1)
    m = re.search(r'(\w+)\s*(\[[^\]]*\])?\s*(=.*)?;$', d2) if '(' not in d2 else re.search(r'(\w+)\s*\(', d2)
    return m.group(1) if m else d2


def tag_defs(s):
    """Alle struct/union-Definitionen 'struct TAG { ... }' in s: [(art, tag, start, ende)] (ende hinter '}')."""
    out = []
    for m in re.finditer(r'\b(struct|union)\s+(\w+)\s*\{', s):
        i = m.end(); d = 1
        while i < len(s) and d:
            d += {'{': 1, '}': -1}.get(s[i], 0); i += 1
        out.append((m.group(1), m.group(2), m.start(), i))
    return out


def tag_koerper(s, st, en):
    return re.sub(r'\s+', ' ', s[s.index('{', st):en]).strip()


def zusammensetzen(blk, ersetze=None, laut=True, tag=''):
    """Moduldatei bauen. ersetze = {adr: pfad}: diese Abschnitte aus einer Arbeitsdatei statt aus src/AIL/REKO."""
    ersetze = ersetze or {}
    say = print if laut else (lambda *a, **k: None)
    F = R.funktionen(); z = A.jload(R.ZUST, {})
    lo, hi = MODULE[blk]
    ab = sorted([f for f in F.values() if lo <= int(f['adr'], 16) < hi and f.get('art', 'c') in ('c', 'system')],
                key=lambda f: int(f['adr'], 16))
    eigen = {}
    for f in ab:
        p = ersetze.get(f['adr']) or os.path.join(R.REKO, R.name_von(f['adr']).upper() + '.C')
        tn = R.ziel_name(open(p, 'rb').read().decode('latin1'), f['adr']) if os.path.exists(p) else R.name_von(f['adr'])
        for nm in (tn, R.name_von(f['adr'])):
            eigen[nm.strip('_').lower()] = f['adr']
    pp, decls, dnamen, funcs, konflikte = [], [], {}, [], []
    fehlend = []; verworfen = []; hilfen = {}
    # Vorlauf: typedefs, die in verschiedenen Dateien verschieden aussehen (Agenten haben sich private Sichten
    # auf dieselbe Struktur gebaut). Je Datei umbenennen (NAME_<adr>), sonst übersetzt das Modul nicht. Der Name
    # ändert keinen Code. Die häufigste Fassung bleibt zusätzlich unter dem Originalnamen für globale Deklarationen.
    tdv = {}
    for f in ab:
        p = ersetze.get(f['adr']) or os.path.join(R.REKO, R.name_von(f['adr']).upper() + '.C')
        if os.path.exists(p):
            for x in teile(open(p, 'rb').read().decode('latin1')):
                if x[0] == 'decl' and re.match(r'\s*typedef\b', x[1]):
                    v = tdv.setdefault(name_der_decl(x[1]), {}).setdefault(re.sub(r'\s+', ' ', x[1]), [0, x[1], set()])
                    v[0] += 1; v[2].add(f['adr'])
    tdkonf = {n: v for n, v in tdv.items() if len(v) > 1}
    # struct/union-Tags: Agenten definieren dieselbe Struktur in vielen Dateien (oft gleich, manchmal anders). Ein Tag
    # darf im Modul nur EINMAL definiert sein: die häufigste Fassung kommt einmal global nach vorn, Dateien mit dieser
    # Fassung verweisen nur noch darauf ('struct TAG'), Dateien mit einer anderen Fassung bekommen TAG_<adr>.
    tgv = {}
    for f in ab:
        p = ersetze.get(f['adr']) or os.path.join(R.REKO, R.name_von(f['adr']).upper() + '.C')
        if os.path.exists(p):
            for x in teile(open(p, 'rb').read().decode('latin1')):
                if x[0] == 'decl':
                    for art_, tg, st, en in tag_defs(x[1]):
                        v = tgv.setdefault((art_, tg), {}).setdefault(tag_koerper(x[1], st, en), [0, set()])
                        v[0] += 1; v[1].add(f['adr'])
    tgmehr = {k: v for k, v in tgv.items() if sum(w[0] for w in v.values()) > 1}
    tghaupt = {k: max(v.items(), key=lambda kv: kv[1][0])[0] for k, v in tgmehr.items()}
    tgdone = set(); dvar = {}; packmap = {}
    htd = {}                                          # AIL.H: typedef struct TAG [*]NAME;
    _h = os.path.join(R.PROJ, 'src', 'AIL', 'AIL_303', 'AIL.H')
    if os.path.exists(_h):
        for m in re.finditer(r'typedef\s+(struct|union)\s+(\w+)\s*(\*?)\s*(\w+)\s*;', open(_h, 'rb').read().decode('latin1')):
            htd.setdefault((m.group(1), m.group(2)), []).append((m.group(3), m.group(4)))
    for (art_, tg), v in tgmehr.items():
        if len(v) > 1:
            say(f'  {art_} {tg}: {len(v)} Fassungen, Abweichler je Datei umbenannt')
    for n, v in tdkonf.items():
        haupt = max(v.values(), key=lambda w: w[0])[1]
        dnamen[n] = {'global': [10 ** 6, haupt]}; decls.append(n)
        say(f'  typedef {n}: {len(v)} Fassungen, je Datei umbenannt')
    for f in ab:
        p = ersetze.get(f['adr']) or os.path.join(R.REKO, R.name_von(f['adr']).upper() + '.C')
        if not os.path.exists(p):
            fehlend.append(f['adr']); continue
        text_ = open(p, 'rb').read().decode('latin1')
        # Gleiche Variable, verschiedene Namen (D_<adr> gegen AIL_-Name): im Modul MUSS es ein Symbol sein, sonst sind
        # gleiche Funktionsenden für Watcom verschieden und der Quersprung bleibt aus (0x8f10c, 22.11.).
        for alt_, neu_ in ALIAS.items():
            text_ = re.sub(r'\b' + alt_ + r'\b', neu_, text_)
        text_ = re.sub(r'\b(struct|union|enum)\s+', r'\1 ', text_)
        meine = {}                                        # (art, tag) -> 'haupt' | 'eigen' für Tags dieser Datei
        for x in teile(text_):
            if x[0] == 'decl':
                for art_, tg, st, en in tag_defs(x[1]):
                    if (art_, tg) in tgmehr:
                        meine[(art_, tg)] = 'haupt' if tag_koerper(x[1], st, en) == tghaupt[(art_, tg)] else 'eigen'
        kopf_td = []
        for (art_, tg), w in meine.items():
            if w == 'eigen':
                sfx = f'_{f["adr"][2:]}'
                text_ = re.sub(r'\b' + art_ + r' ' + tg + r'\b', f'{art_} {tg}{sfx}', text_)
                # Typnamen, die auf diesen Tag zeigen, gehören in dieser Datei ebenfalls zur eigenen Fassung
                for st_, hn in htd.get((art_, tg), []):
                    text_ = re.sub(r'(?<!struct )(?<!union )\b' + hn + r'\b', hn + sfx, text_)
                    kopf_td.append(('decl', f'typedef {art_} {tg}{sfx} {st_}{hn}{sfx};'))
                for x in teile(text_):
                    if x[0] == 'decl' and x[1].lstrip().startswith('typedef') and f'{art_} {tg}{sfx}' in x[1]:
                        hn = name_der_decl(x[1])
                        if hn not in tdkonf and not hn.endswith(sfx):
                            text_ = re.sub(r'(?<!struct )(?<!union )\b' + hn + r'\b', hn + sfx, text_)
        for n, v in tdkonf.items():
            if any(f['adr'] in w[2] for w in v.values()):
                text_ = re.sub(r'(?<!struct )(?<!union )(?<!enum )\b' + n + r'\b', f'{n}_{f["adr"][2:]}', text_)
        T = kopf_td + teile(text_)
        T2 = []
        for x in T:                                       # Haupt-Fassungen: Körper weg, nur Verweis 'struct TAG'
            if x[0] == 'decl':
                s_ = x[1]
                vorab = []
                for art_, tg, st, en in reversed(tag_defs(s_)):
                    if meine.get((art_, tg)) == 'haupt':
                        if (art_, tg) not in tgdone:      # erste Haupt-Fassung: als eigene Tag-Definition davor
                            tgdone.add((art_, tg)); vorab.insert(0, ('decl', f'{art_} {tg} ' + s_[s_.index('{', st):en] + ';'))
                        s_ = s_[:st] + f'{art_} {tg}' + s_[en:]
                T2 += vorab
                if re.fullmatch(r'\s*(struct|union)\s+\w+\s*;\s*', s_):
                    continue                              # reine Tag-Definition: steht schon davor
                x = ('decl', s_)
            T2.append(x)
        T = T2
        tn = R.ziel_name(open(p, 'rb').read().decode('latin1'), f['adr']).strip('_').lower()
        # Der Abschnitt beginnt mit seiner Zielfunktion: was in der Datei VOR ihr definiert ist, sind Hilfskopien
        ziel_i = next((k for k, x in enumerate(T) if x[0] == 'func' and x[1].strip('_').lower() in (tn, R.name_von(f['adr']).lower())), None)
        if blk in UMDEUTEN and ziel_i is not None:      # Hilfskopien merken (eingesetzt, wenn sonst nirgends definiert)
            for k, x in enumerate(T):
                if x[0] == 'func' and k < ziel_i:
                    hilfen.setdefault(x[1], (f['adr'], x[2]))
        T = [x for k, x in enumerate(T) if x[0] != 'func' or (ziel_i is not None and k >= ziel_i)]
        lokal = []                                        # #define der Datei: gelten nur für ihre eigenen Funktionen
        pack_jetzt = None
        for x in T:
            if x[0] == 'pp':
                mp = re.match(r'#\s*pragma\s+pack\s*\(\s*(\d*)\s*\)', x[1])
                if mp and blk in UMDEUTEN:
                    pack_jetzt = mp.group(1) or None      # gilt für die folgenden Deklarationen DIESER Datei
                    continue
                if blk in UMDEUTEN and re.match(r'#\s*pragma\s+code_seg\b', x[1]):
                    continue                              # Agenten-Kniff (Hilfsfunktionen auslagern), im Modul sinnlos
                if blk in UMDEUTEN and re.match(r'#\s*pragma\s+intrinsic\b', x[1]):
                    continue                              # wirkt im Modul (Watcom übersetzt verzögert) auch auf frühere
                                                          # Funktionen: 0xa9c7d bekam strcpy eingebettet (+21 B)
                if x[1].startswith('#include'):
                    if x[1] not in pp:
                        pp.append(x[1])
                else:
                    lokal.append(x[1])
            elif x[0] == 'decl':
                if re.match(r'\s*void\s*\*\s*ref_[0-9a-f]+\s*=\s*\(\s*void\s*\*\s*\)\s*F_[0-9a-f]+\s*;', x[1]):
                    continue                      # Agenten-Kniff (statische Funktion "benutzt" halten): im Modul 4 B _DATA zuviel
                mt = re.match(r'\s*(struct|union)\s+(\w+)\s*\{', x[1])
                nm = f'tag:{mt.group(1)}:{mt.group(2)}' if mt and x[1].rstrip().endswith('};') else name_der_decl(x[1])
                norm = re.sub(r'\s+', ' ', x[1])
                if pack_jetzt:
                    packmap[norm] = pack_jetzt
                if nm not in dnamen:
                    dnamen[nm] = {}; decls.append(nm)          # Reihenfolge nach erstem Auftreten
                v = dnamen[nm].setdefault(norm, [0, x[1]])
                dvar.setdefault(nm, {}).setdefault(norm, set()).add(f['adr'])
                w_ = 10 if z.get(f['adr'], {}).get('status') == 'GLEICH' else 1   # GLEICHe Dateien wiegen 10fach
                if blk in UMDEUTEN:   # dazu nach Codegröße: Umdeute-Makros (*(T *)&X) hemmen Watcoms Einbetten (-oe) im
                    w_ *= max(1, f['laenge'])   # großen Abschnitt (0xb01b0: F_af0f0 wurde nicht mehr eingebettet)
                v[0] += w_
            else:
                nm = x[1].strip('_').lower()
                if nm in eigen and eigen[nm] != f['adr']:
                    continue                      # Hilfskopie einer Funktion aus einem anderen Abschnitt
                if any(nm == g[0] for g in funcs):
                    continue
                # Hinter der Zielfunktion nur, was wirklich in diesen Abschnitt gehört: echte AIL_-Namen oder F_<adr>
                # innerhalb des Abschnitts. Platzhalter, Abstandshalter und Kopien fremder Funktionen (mid_fn, fn2,
                # F_spacer1, F_last_4arg, F_8d402 …) haben Agenten nur fürs Messfenster beigelegt.
                if nm not in (tn, R.name_von(f['adr']).lower()):
                    mh = re.fullmatch(r'f_([0-9a-f]+)', nm)
                    a_ = int(f['adr'], 16)
                    drin = (nm.startswith('ail_') and nm not in eigen) or (mh and a_ < int(mh.group(1), 16) < a_ + f['laenge'])
                    if not drin:
                        if blk in UMDEUTEN:
                            hilfen.setdefault(x[1], (f['adr'], x[2]))
                        verworfen.append((f['adr'], nm, x[2])); continue
                vor = '\r\n'.join(lokal) + '\r\n' if lokal and not any(g[1] == f['adr'] for g in funcs) else ''
                funcs.append((nm, f['adr'], vor + x[2]))
        if lokal and any(g[1] == f['adr'] for g in funcs):
            namen = [re.match(r'#\s*define\s+(\w+)', l).group(1) for l in lokal if re.match(r'#\s*define\s+(\w+)', l)]
            if namen:
                i_ = max(k for k, g in enumerate(funcs) if g[1] == f['adr'])
                g = funcs[i_]; funcs[i_] = (g[0], g[1], g[2] + '\r\n' + '\r\n'.join('#undef ' + n for n in namen))
    # Statische Hilfsfunktionen der Agenten (XMI_flush_buffer, MDI_flush ...), die ein Abschnitt aufruft, die aber
    # nirgends sonst definiert sind: im Original stehen sie im Modul (meist eingebettet, -oe). Ohne sie bleibt der
    # Aufruf offen (watcall-Name, WLINK: undefined) und der Aufrufer wird anders übersetzt. Vor den ersten Aufrufer.
    # Hilfen, die im Original ein vorhandener Abschnitt sind (gleicher Rumpf): Aufruf auf ihn umlenken
    for hn, ziel in HILFS_ALIAS.items():
        pat = re.compile(r'\b' + hn + r'\s*\(')
        for k, g in enumerate(funcs):
            if pat.search(g[2]) and g[0] != hn.lower():
                funcs[k] = (g[0], g[1], f'#define {hn}(m) {ziel}((void *)(m))\r\n' + g[2] + f'\r\n#undef {hn}')
        hilfen.pop(hn, None)
    for hn, (args, rumpf) in HILFS_MAKRO.items():   # im Original eingebettet und nicht als eigene Funktion vorhanden
        pat = re.compile(r'\b' + hn + r'\s*\(')
        for k, g in enumerate(funcs):
            if pat.search(g[2]) and g[0] != hn.lower():
                funcs[k] = (g[0], g[1], f'#define {hn}({args}) {rumpf}\r\n' + g[2] + f'\r\n#undef {hn}')
        hilfen.pop(hn, None)
    for hn, (hadr, htxt) in hilfen.items():
        hk = hn.strip('_').lower()
        if hk in {g[0] for g in funcs} or hk in eigen:
            continue
        pat = re.compile(r'\b' + re.escape(hn) + r'\s*\(')
        users = [k for k, g in enumerate(funcs) if g[0] != hk and pat.search(g[2])]
        if not users:
            continue
        txt = htxt if re.match(r'\s*static\b', htxt) else 'static ' + htxt.lstrip()
        if hn in HILFS_WEG:
            txt = '#pragma code_seg("INL_TEXT")\r\n' + txt + '\r\n#pragma code_seg()'

        funcs.insert(users[0], (hk, funcs[users[0]][1], txt))
        say(f'  Hilfsfunktion {hn} (aus {hadr}) vor {funcs[users[0] + 1][0]} eingesetzt')
    # Mehrere Fassungen derselben Deklaration: die häufigste gewinnt (Mehrheit der Dateien), Abweichler melden
    gewaehlt = []
    for nm in decls:
        fass = sorted(dnamen[nm].items(), key=lambda kv: -kv[1][0])
        defin = [kv for kv in fass if '=' in kv[0] and not kv[0].lstrip().startswith('extern')]
        if defin:                                   # eine Definition im Modul schlägt alle extern-Deklarationen
            fass = defin + [kv for kv in fass if kv not in defin]
            gewaehlt.append(defin[0][1][1]); continue
        gewaehlt.append(fass[0][1][1])
        if len(fass) > 1:
            konflikte.append((nm, ' | '.join(f'{k} ({v[0]})' for k, v in fass)[:200]))
    decls = gewaehlt
    # Variablen, die eine Datei mit anderem Typ deklariert als die Mehrheit (extern LONG D_x gegen extern SEQ *D_x):
    # für die Funktionen dieser Datei per Makro auf ihren eigenen Typ umdeuten, *(T *)&D_x erzeugt denselben Code.
    gew = {name_der_decl(x): re.sub(r'\s+', ' ', x) for x in decls}
    for nm, fv in dvar.items():
        if nm not in gew or nm.startswith('tag:') or blk not in UMDEUTEN:
            continue
        for norm, adrs in fv.items():
            if norm == gew[nm] or norm.lstrip().startswith('typedef') or re.match(r'\s*(struct|union|enum)\b[^;]*\{', norm):
                continue
            fp = re.search(r'\b' + nm + r'\s*\(', norm)
            if fp and (nm.strip('_').lower() in {g[0] for g in funcs} or not re.search(r'\b' + nm + r'\s*\([^()]*\)\s*;\s*$', norm)):
                continue                                  # im Modul definiert (Definition gilt) oder unklar
            if fp:                                        # nur der Rückgabetyp ändert den Code des Aufrufers
                rt = lambda s: re.sub(r'\b(extern|cdecl|__cdecl)\b|\s+', '', s[:re.search(r'\b' + nm + r'\s*\(', s).start()])
                r1, r2 = rt(norm), rt(gew[nm])
                if r1 == r2 or ('*' in r1 and '*' in r2):
                    continue
            if not fp and ('=' in norm or ',' in re.sub(r'\([^()]*\)|\[[^\]]*\]', '', norm)):
                continue                                  # Definition oder Mehrfach-Deklaration: nicht umdeuten
            for a_ in adrs:
                tn = f'T_{nm}_{a_[2:]}'
                if fp:                                    # fremde Funktion mit anderem Prototyp: Aufruf über Zeigertyp
                    k_ = re.sub(r'^\s*extern\s+', '', norm)
                    k_ = re.sub(r'\b((?:__)?cdecl\s+)?' + nm + r'\s*\(', lambda m: f'({m.group(1) or ""}*{tn})(', k_, count=1)
                    td = 'typedef ' + k_
                    ks = [k for k, g in enumerate(funcs) if g[1] == a_]
                    if not ks:
                        continue
                    g = funcs[ks[0]]; funcs[ks[0]] = (g[0], g[1], f'{td}\r\n#define {nm} (({tn}){nm})\r\n' + g[2])
                    g = funcs[ks[-1]]; funcs[ks[-1]] = (g[0], g[1], g[2] + f'\r\n#undef {nm}')
                    say(f'  Funktion {nm}: Abschnitt {a_} mit eigenem Prototyp ({norm[:60]})')
                    continue
                td = 'typedef ' + re.sub(r'\b' + nm + r'\b', tn, re.sub(r'^\s*extern\s+', '', norm), count=1)
                ks = [k for k, g in enumerate(funcs) if g[1] == a_]
                if not ks:
                    continue
                g = funcs[ks[0]]; funcs[ks[0]] = (g[0], g[1], f'{td}\r\n#define {nm} (*({tn} *)&{nm})\r\n' + g[2])
                g = funcs[ks[-1]]; funcs[ks[-1]] = (g[0], g[1], g[2] + f'\r\n#undef {nm}')
                say(f'  Variable {nm}: Abschnitt {a_} mit eigenem Typ ({norm[:60]})')
    # Funktionsdefinitionen schlagen extern-Deklarationen derselben Variablen/Funktion nicht; static-Konflikte melden
    # Für Funktionen, die im Modul definiert sind, gilt der Kopf der Definition (sie wurde einzeln GLEICH gemessen):
    # deren extern-Deklarationen fallen weg, an ihre Stelle tritt ein Prototyp aus der Definition.
    def kopf(t):
        z, weiter = [], False                     # Präprozessorzeilen samt \-Fortsetzungen überspringen
        for l in t.split('\n'):
            if weiter or l.lstrip().startswith('#'):
                weiter = l.rstrip().endswith('\\'); continue
            z.append(l)
        t2 = re.sub(r'/\*.*?\*/', ' ', '\n'.join(z), flags=re.S)
        t2 = re.sub(r'//[^\n]*', ' ', t2)
        h = t2[:t2.find('{')]
        return re.sub(r'\s+', ' ', h[h.rfind(';') + 1:]).strip()   # vorangestellte typedefs (Umdeutung) nicht mitnehmen
    fnamen = {g[0] for g in funcs}
    abw = []
    for x in decls:
        nm = name_der_decl(x).strip('_').lower()         # Funktionsnamen sind normalisiert (klein, ohne _)
        if nm in fnamen and '(' in x:
            g = next(g for g in funcs if g[0] == nm)
            a = re.sub(r'\s+', ' ', x).replace('extern ', '').rstrip(';').strip(); b = kopf(g[2])
            if re.sub(r'\b(cdecl|__cdecl)\b ?', '', a) != re.sub(r'\b(cdecl|__cdecl)\b ?', '', b) or ('cdecl' in a) != ('cdecl' in b):
                abw.append((nm, a, b))
    decls = [x for x in decls if not (name_der_decl(x).strip('_').lower() in fnamen and '(' in x)]
    protos = [kopf(g[2]) + ';' for g in funcs]
    gesehen = set(fnamen)
    for adr_, nm_, t_ in verworfen:
        if nm_ not in gesehen:
            gesehen.add(nm_); k_ = re.sub(r'^\s*static\s+', '', kopf(t_))
            protos.append('extern ' + k_ + ';')
    if verworfen:
        say(f'  Beigaben verworfen ({len(verworfen)}): ' + ', '.join(f'{nm_}@{adr_}' for adr_, nm_, _ in verworfen)[:900])
    if abw:
        say(f'  Prototypen: {len(abw)} extern-Deklarationen weichen von der Definition ab (Definition gilt):')
        for nm, a, b in abw[:12]:
            say(f'    {nm}: extern "{a}"  /  Def "{b}"')
    typ = [x for x in decls if re.match(r'\s*(typedef|struct|union|enum)\b', x)]
    rest = [x for x in decls if x not in typ]
    def gepackt(x):                                       # #pragma pack der Herkunftsdatei um die Deklaration legen
        n_ = packmap.get(re.sub(r'\s+', ' ', x))
        return f'#pragma pack({n_})\r\n{x}\r\n#pragma pack()' if n_ else x
    typ = [gepackt(x) for x in typ]
    text = ('\r\n'.join(pp) + '\r\n\r\n' + '\r\n'.join(typ) + '\r\n\r\n' + '\r\n'.join(protos) + '\r\n\r\n'
            + '\r\n'.join(rest) + '\r\n\r\n'
            + '\r\n\r\n'.join(g[2] for g in funcs) + '\r\n')
    d = os.path.join(R.PROJ, 'Analyse', 'ail_modul'); os.makedirs(d, exist_ok=True)
    for nm_ in MODUL_STATISCH.get(blk, ()):     # im Original statisch (eingebettet UND ausgegeben), Agenten: global
        text = re.sub(r'(?m)^(?!static )([A-Za-z_][^\n;{]*\b' + nm_ + r'\s*\()', r'static \1', text)
    datei = os.path.join(d, f'MOD_{blk[2:].upper()}{tag}.C'); open(datei, 'w', encoding='latin1', newline='').write(text)
    a0 = int(ab[0]['adr'], 16); a1 = max(int(f['adr'], 16) + f['laenge'] for f in ab)
    orig = R.CODE[a0 - CB:a1 - CB]
    say(f'Block {blk}: {len(ab)} Abschnitte, {a1 - a0} B, {len(funcs)} Funktionen zusammengesetzt, fehlend {fehlend}, '
          f'abweichende Deklarationen {len(konflikte)} (Mehrheit gilt)')
    for nm, t in konflikte[:15]:
        say(f'    {nm}: {t}')
    return {'blk': blk, 'datei': datei, 'ab': ab, 'eigen': eigen, 'a0': a0, 'a1': a1, 'orig': orig}


def uebersetze(M, fl=None):
    fl = fl or MODUL_FLAGS.get(M['blk'], ('-s',))
    cfg = {'src': 'AIL/REKO/MOD_' + M['blk'][2:].upper() + '.C', 'flags': list(fl), 'inc': R.INC}
    return A.kompiliere('AILMOD', cfg, M['datei'])


def abschnitte_messen(M, r):
    """Je Abschnitt: Lage im übersetzten Modul und Rest (Befehle ohne Sprung-/Aufrufziele; die hängen am Lageplan).
    Ein Abschnitt reicht im Modul von seiner Zielfunktion bis zur Zielfunktion des nächsten Abschnitts."""
    ab, eigen, a0, orig = M['ab'], M['eigen'], M['a0'], M['orig']
    dd = b''.join(bytes.fromhex(s['daten']) for s in r['stuecke']); mm = b''.join(bytes.fromhex(s['maske']) for s in r['stuecke'])
    off = 0; pos = {}
    for s in r['stuecke']:
        L_ = len(s['daten']) // 2; pos[s['name'].strip('_').lower()] = (off, L_); off += L_
    adr2nm = {}
    for n_, a_ in eigen.items():
        if n_ in pos:
            adr2nm[a_] = n_
    starts = [(f, pos[adr2nm[f['adr']]][0]) for f in ab if f['adr'] in adr2nm]
    zeilen = []
    for f in ab:
        soll = int(f['adr'], 16) - a0; nm = adr2nm.get(f['adr'])
        if nm is None:
            zeilen.append({'adr': f['adr'], 'soll': soll, 'soll_l': f['laenge'], 'name': None, 'ist': None, 'ist_l': 0,
                           'rest': f['laenge'], 'gleich': False, 'bytegleich': False, 'da': [], 'db': []}); continue
        o = pos[nm][0]
        o2 = next((st for f2, st in starts if int(f2['adr'], 16) > int(f['adr'], 16)), len(dd))
        ist_b, ist_m = dd[o:o2], mm[o:o2]
        soll_b = orig[soll:soll + f['laenge']]
        m2 = ist_m[:len(soll_b)] + bytes(max(0, len(soll_b) - len(ist_m)))
        da, db = dis(ist_b, ist_m), dis(soll_b, m2)
        rst = A.rest(da, db)
        zeilen.append({'adr': f['adr'], 'soll': soll, 'soll_l': f['laenge'], 'name': nm, 'ist': o, 'ist_l': o2 - o, 'rest': rst,
                       'gleich': rst == 0 and o2 - o == f['laenge'],
                       'bytegleich': o2 - o == f['laenge'] and A.passt(R.CODE, a0 - CB + soll, ist_b, ist_m), 'da': da, 'db': db})
    fremd = [n_ for n_ in pos if n_ not in adr2nm.values()]
    return {'zeilen': zeilen, 'dd': dd, 'mm': mm, 'pos': pos, 'fremd': fremd}


def strafe(zl):
    """Kennzahl eines Abschnitts im Modul: Befehlsrest + Längenabweichung."""
    return zl['rest'] + abs(zl['ist_l'] - zl['soll_l'])


def modul_messe(adr, pfad=None, tag=''):
    """Für ail_richter: Abschnitt adr im ganzen Modul messen (Arbeitsdatei pfad statt REKO-Fassung)."""
    blk = modul_von(adr)
    M = zusammensetzen(blk, {adr: pfad} if pfad else None, laut=False, tag=tag)
    r = uebersetze(M)
    if r.get('fehler'):
        zl = [l for l in r['fehler'].splitlines() if re.search(r'Error!|\(\d+\)', l)]
        return {'fehler': 'Modul übersetzt nicht:\n' + '\n'.join(zl[:12])[-1500:]}
    E = abschnitte_messen(M, r)
    z_ = next(z for z in E['zeilen'] if z['adr'] == adr)
    gesamt = sum(strafe(z) for z in E['zeilen'])
    return {'rest': strafe(z_), 'gleich': z_['gleich'], 'flags': ['-s'], 'laenge': z_['ist_l'], 'orig_laenge': z_['soll_l'],
            'abschnitte': [adr], 'modul': blk, 'modul_gesamt': gesamt, 'modul_gleich': sum(z['gleich'] for z in E['zeilen']),
            'zeilen': [{k: v for k, v in z.items() if k not in ('da', 'db')} for z in E['zeilen']], 'da': z_['da'], 'db': z_['db']}


def main():
    blk = sys.argv[1].lower(); ueb = '--uebernehmen' in sys.argv
    M = zusammensetzen(blk)
    ab, eigen, a0, a1, orig, datei = M['ab'], M['eigen'], M['a0'], M['a1'], M['orig'], M['datei']
    bester = None
    FL = ([list(MODUL_FLAGS[blk])] if blk in MODUL_FLAGS else []) + [f for f in R.FLAGSAETZE if list(f) != list(MODUL_FLAGS.get(blk, ()))]
    for fl in (FL[:1] if '--schnell' in sys.argv else FL):   # erster = Kandidat (MODUL_FLAGS, sonst -s)
        cfg = {'src': 'AIL/REKO/MOD_' + blk[2:].upper() + '.C', 'flags': fl, 'inc': R.INC}
        r = A.kompiliere('AILMOD', cfg, datei)
        if r.get('fehler'):
            zl = r['fehler'].splitlines()
            fz = [l for l in zl if 'Error' in l]
            print(f'  Flags {" ".join(fl):22} FEHLER {fz[0][-150:] if fz else r["fehler"][-150:]}')
            if fl is FL[0]:                     # Einmal ausführlich: Fehler- und Hinweiszeilen mit Zeilennummer
                for l in [l for l in zl if re.search(r'Error!|Note!|Warning!|\(\d+\)', l)][:12]:
                    print('      ' + l.strip()[-220:])
                if fz and all(l in r['fehler'] for l in fz[:1]):
                    print('  (Übersetzungsfehler hängt nicht an den Flags, Rest übersprungen)'); break
            continue
        dd = b''.join(bytes.fromhex(s['daten']) for s in r['stuecke']); mm = b''.join(bytes.fromhex(s['maske']) for s in r['stuecke'])
        off = 0; pos = {}
        for s in r['stuecke']:
            pos[s['name'].strip('_').lower()] = (off, len(bytes.fromhex(s['daten']))); off += len(bytes.fromhex(s['daten']))
        erste = next((k for k in range(min(len(dd), len(orig))) if not mm[k] and dd[k] != orig[k]), None)
        gl = []
        for f in ab:
            nm = next((n for n, adr in eigen.items() if adr == f['adr'] and n in pos), None)
            if nm is None:
                continue
            o, L = pos[nm]; soll = int(f['adr'], 16) - a0
            if o == soll and A.passt(R.CODE, a0 - CB + o, dd[o:o + L], mm[o:o + L]):
                gl.append(f['adr'])
        ganz = len(dd) == len(orig) and erste is None
        if '--plan' in sys.argv and fl is FL[0]:   # Lageplan: Soll-Abschnitt gegen Ist-Funktion im Modul
            E = abschnitte_messen(M, r)
            print('      Abschnitt  soll-Off soll-L | Funktion          ist-Off  ist-L  Drift  Rest  gleich')
            for zl in E['zeilen']:
                if zl['name'] is None:
                    print(f'      {zl["adr"]:9} {zl["soll"]:8} {zl["soll_l"]:6} | (nicht im Modul)'); continue
                print(f'      {zl["adr"]:9} {zl["soll"]:8} {zl["soll_l"]:6} | {zl["name"][:16]:16} {zl["ist"]:8} {zl["ist_l"]:6} '
                      f'{zl["ist"] - zl["soll"]:6} {zl["rest"]:5}  {"ja" if zl["bytegleich"] else ("~" if zl["gleich"] else "")}')
                if '--diff' in sys.argv and zl['adr'] in sys.argv[sys.argv.index('--diff') + 1:]:
                    import difflib
                    print(f'        --- {zl["adr"]} ist / +++ soll')
                    for l in list(difflib.unified_diff(zl['da'], zl['db'], 'ist', 'soll', n=2, lineterm=''))[2:int(os.environ.get('DIFF_ZEILEN', '82'))]:
                        print('        ' + l)
            Z = E['zeilen']
            print(f'      Abschnitte: {len(Z)}, gleich im Modul (Befehle und Länge): {sum(z["gleich"] for z in Z)}, '
                  f'bytegleich am Platz: {sum(z["bytegleich"] for z in Z)}, Gesamtstrafe: {sum(strafe(z) for z in Z)}')
            print(f'      Funktionen im Modul ohne eigenen Abschnitt ({len(E["fremd"])}): '
                  + ', '.join(f'{n_}({E["pos"][n_][1]})' for n_ in E['fremd'])[:1500])
            if '--stand' in sys.argv:                     # Modulmessung als Stand eintragen (Ratsche startet neu)
                with A.Lock('ail_uebernahme'):
                    zz = A.jload(R.ZUST, {}); n_g = n_o = 0
                    for zl in Z:
                        e = zz.setdefault(zl['adr'], {})
                        e.update({'status': 'GLEICH' if zl['gleich'] else 'offen', 'rest': 0 if zl['gleich'] else strafe(zl),
                                  'modul': blk, 'flags': ['-s'], 'zeit': R.jetzt(), 'versuche_ohne_gewinn': 0,
                                  'einzeln': e.get('einzeln', {'status': e.get('status'), 'rest': e.get('rest')})})
                        n_g += zl['gleich']; n_o += not zl['gleich']
                    A.jsave(R.ZUST, zz)
                print(f'      STAND: {n_g} Abschnitte GLEICH im Modul, {n_o} offen (Rest = Modulstrafe), Ratsche neu gesetzt')
        print(f'  Flags {" ".join(fl):22} Länge {len(dd)}/{len(orig)}, erste Abweichung bei {hex(a0 + erste) if erste is not None else "-"}, '
              f'Funktionen an richtiger Stelle gleich: {len(gl)} von {len(ab)}{"  GANZER BLOCK GLEICH" if ganz else ""}')
        if bester is None or len(gl) > len(bester[1]):
            bester = (fl, gl)
    if ueb and bester and bester[1]:
        with A.Lock('ail_uebernahme'):
            z = A.jload(R.ZUST, {}); n = 0
            for adr in bester[1]:
                if z.get(adr, {}).get('status') != 'GLEICH':
                    e = z.setdefault(adr, {}); e.update({'status': 'GLEICH', 'rest': 0, 'modul': blk, 'flags': bester[0],
                                                         'wer': 'ail_modul', 'zeit': R.jetzt()}); n += 1
            A.jsave(R.ZUST, z)
        print(f'{n} Abschnitte als GLEICH (im Modul) eingetragen')
    print('Moduldatei:', os.path.relpath(datei, R.PROJ))


if __name__ == '__main__':
    main()
