#!/usr/bin/env python3
"""ail_richter.py - Richter für den Nachbau von AIL 3.03 Funktion für Funktion (Lauf E).

Jede Funktion (Adresse aus Richter/ail_funktionen.json) bekommt eine eigene C-Datei. Gemessen wird nur
diese eine Funktion gegen die Originalbytes an ihrer Adresse (Fixups maskiert). Ratsche: übernommen
wird nur, was besser ist. Angenommene Fassungen: src/AIL/REKO/F_<adr>.C, alte -> src_archiv/AIL_REKO/.

Befehle (immer aus dem Projektordner):
  liste [N] | naechste --id ID | zeigen --id ID | messen --id ID | abgeben --id ID [--ende] | freigeben --id ID | status
"""
import argparse, datetime as dt, difflib, json, os, re, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import albion as A  # noqa: E402

PROJ = A.PROJ; RD = A.RD
FUNK = os.path.join(RD, 'ail_funktionen.json')
ZUST = os.path.join(RD, 'ail_zustand.json')
BELEG = os.path.join(RD, 'ail_belegung.json')
MESS = os.path.join(RD, 'ail_messungen.jsonl')
REKO = os.path.join(A.SRC, 'AIL', 'REKO')
WORK = os.path.join(PROJ, 'work')
INC = 'C:\\WATCOM.10A\\H;C:\\AIL\\AIL_303;C:\\AIL\\REKO'
# Flags von AIL 3.03 sind nicht belegt; DLLLOAD (gleiche Bibliothek) passte mit -s. Gemessen wird mit allen,
# die beste Variante zählt und wird mitgeschrieben.
# Befund E04 (21.11.): Funktionen sind auf 16 Bytes ausgerichtet, das Füllmuster passt mit -4r (486-Padding).
# Gewonnen haben bisher nur diese fünf (Stand 19:11); die übrigen kosteten nur Zeit pro Messung.
FLAGSAETZE = [['-s'], ['-s', '-4r'], ['-s', '-oneatx', '-5r'], ['-s', '-oneatx', '-4r'], ['-s', '-ox', '-4r']]
CODE = open(A.FLAT, 'rb').read()
CB = A.CB


def jetzt():
    return dt.datetime.now().astimezone().isoformat(timespec='seconds')


def funktionen():
    return {f['adr']: f for f in A.jload(FUNK)['funktionen']}


def name_von(adr):
    return 'F_' + adr[2:].lower()


def ziel_name(text, adr):
    m = re.search(r'ZIELFUNKTION:\s*([A-Za-z_][A-Za-z0-9_]*)', text)
    return m.group(1) if m else name_von(adr)


def vorlage(f):
    n = name_von(f['adr'])
    return ('/*\r\n * AIL 3.03 - Nachbau der Funktion bei ' + f['adr'] + ' (' + str(f['laenge']) + ' Bytes)\r\n'
            ' * ZIELFUNKTION: ' + n + '\r\n */\r\n\r\n#include <stdlib.h>\r\n#include <string.h>\r\n#include <dos.h>\r\n'
            '#include <AIL.H>\r\n\r\nvoid cdecl ' + n + '(void)\r\n{\r\n}\r\n')


def namen():
    """Adresse -> Name für bekannte Funktionen (Anker der Karte, AIL-Funktionen)."""
    karte = A.jload(A.KARTE); E = A.einheiten(); m = {}
    comp = {}
    for s, e, u, i in karte['anker']:
        if u.startswith('#'):
            m[s + CB] = i.split(':')[1] if ':' in i else i
        else:
            if u not in comp:
                comp[u] = A.kompiliere(u, E[u])
            st = comp[u]['stuecke']
            m[s + CB] = st[i]['name'] if i < len(st) else f'{u}[{i}]'
    z = A.jload(ZUST, {})
    for adr in funktionen():
        m[int(adr, 16)] = z.get(adr, {}).get('name') or name_von(adr)
    return m


def kompiliere_datei(adr, pfad, flags, inc=None):
    cfg = {'src': 'AIL/REKO/' + name_von(adr).upper() + '.C', 'flags': flags, 'inc': inc or INC}
    return A.kompiliere('AILREKO', cfg, pfad)


# Abschnitte in einem Modul aus ail_modul.MODULE werden im ganzen Modul gemessen (Quersprünge)


def messe(adr, pfad):
    f = funktionen()[adr]; a = int(adr, 16) - CB - f.get('vor', 0); n = f['laenge'] + f.get('vor', 0)   # vor: switch-Tabelle
    import ail_modul
    if ail_modul.modul_von(adr):
        text = open(pfad, 'rb').read().decode('latin1')
        for pat in A.VERBOTEN:
            if re.search(pat, text, re.I):
                return {'fehler': f'Pförtner: verbotenes Konstrukt ({pat})'}
        import ail_modul
        return ail_modul.modul_messe(adr, pfad, tag='_' + adr[2:])
    orig = CODE[a:a + n]
    text = open(pfad, 'rb').read().decode('latin1')
    for pat in A.VERBOTEN:
        if re.search(pat, text, re.I):
            return {'fehler': f'Pförtner: verbotenes Konstrukt ({pat})'}
    zn = ziel_name(text, adr).strip('_').lower()
    best = None; fehler = None
    for fl in f.get('flagsaetze') or FLAGSAETZE:          # Krümel-Aufgaben bringen eigene Flags/Includes mit
        r = kompiliere_datei(adr, pfad, fl, f.get('inc'))
        if r.get('fehler'):
            fehler = r['fehler']; continue
        if not any(s['name'].strip('_').lower() == zn for s in r['stuecke']):
            fehler = f'Zielfunktion {zn} nicht gefunden (Stücke: {[s["name"] for s in r["stuecke"]]})'; continue
        # Gemessen wird der GANZE Code der Datei: ein Abschnitt kann mehrere Funktionen enthalten
        # (Grenzen stammen nur aus direkten Aufrufen). Befund E02/E03/E05, 21.11. abends.
        d = b''.join(bytes.fromhex(s['daten']) for s in r['stuecke'])
        m = b''.join(bytes.fromhex(s['maske']) for s in r['stuecke'])
        tb = f.get('tabelle')
        if tb and f.get('vor', 0) > tb:
            # switch-Tabelle vor der Funktion, dahinter Ausrichtung auf die Funktionsadresse. Im OBJ fehlt diese
            # Füllung (andere Lage), der Linker setzt sie. Darum Füllbytes des Originals einsetzen und maskieren.
            fz = f['vor'] - tb
            if d[tb:tb + fz] != CODE[a + tb:a + tb + fz]:
                d = d[:tb] + CODE[a + tb:a + tb + fz] + d[tb:]; m = m[:tb] + b'\x01' * fz + m[tb:]
        # Fenster: der Datei-Code darf über mehrere Abschnitte reichen (Befund E02/E03/E05). Das Fenster endet am
        # Ende des letzten Abschnitts, den er berührt. Dahinter fehlende Füllbytes (< 16, Ende auf 16 ausgerichtet,
        # nur nop/lea/mov) gehören zur Ausrichtung der NÄCHSTEN Funktion und zählen nicht als Abweichung.
        ende = fenster_ende(a + CB, len(d)) - CB
        orig = CODE[a:ende]
        tail = CODE[a + len(d):ende] if len(d) <= ende - a else b''
        fuell = len(d) <= ende - a and len(tail) < 16 and ende % 16 == 0 and \
            (all(x.split()[0] in ('nop', 'lea', 'mov') for x in A.dis(tail)) or tail == bytes(len(tail)))   # Linker füllt Modulenden mit 00
        gleich = A.passt(CODE, a, d, m) and (len(d) == ende - a or fuell)
        quer = False
        if not gleich:
            quer = quersprung(a, f['laenge'], d, m)
            gleich = quer
        rr = 0 if gleich else A.rest(A.dis(orig, base=a + CB), A.dis(d, m, base=a + CB))
        if rr == 0 and not gleich:
            rr = 1                                   # Befehle gleich, Bytes nicht (Länge/Kodierung)
        k = {'rest': rr, 'gleich': gleich, 'flags': fl, 'laenge': len(d), 'orig_laenge': f['laenge'] if quer else ende - a,
             'abschnitte': [adr] if quer else abschnitte(a + CB, ende + CB), 'fuellbytes': len(tail) if gleich and not quer else 0,
             'quersprung': quer}
        if best is None or rr < best['rest']:
            best = k
        if gleich:
            break
    return best or {'fehler': (fehler or 'kein Ergebnis')[-800:]}


def quersprung(a, n, d, m):
    """Watcom legt gleiche Funktionsenden innerhalb EINES Moduls zusammen: das Original springt per jmp in das Ende
    einer anderen Funktion (z. B. 20 AIL-Hüllen auf 0x8c62e). Eine einzeln übersetzte Funktion kann das nicht und
    schreibt das Ende aus. Abgleich Befehl für Befehl: jeder jmp des Originals auf ein Ziel AUSSERHALB des Abschnitts
    darf bei uns durch die ausgeschriebenen Befehle am Sprungziel (bis einschließlich ret) ersetzt sein; alles andere
    muss bytegleich sein. Gilt dann als GLEICH (mit Quersprung); endgültiger Beweis beim Zusammensetzen des Moduls."""
    import capstone
    cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    io = idd = 0; benutzt = False
    ins = list(cs.disasm(CODE[a:a + n], a + CB))
    for k, i in enumerate(ins):
        off = i.address - (a + CB)
        if off != io:
            return False
        if i.mnemonic == 'jmp' and i.op_str.startswith('0x') and not (a + CB <= int(i.op_str, 16) < a + CB + n):
            t = int(i.op_str, 16) - CB; L = 0
            for x in cs.disasm(CODE[t:t + 64], t + CB):
                L += x.size
                if x.mnemonic == 'ret':
                    break
            else:
                return False
            if idd + L > len(d) or not A.passt(CODE, t, d[idd:idd + L], m[idd:idd + L]):
                return False
            io += i.size; idd += L; benutzt = True
            continue
        if idd + i.size > len(d) or not A.passt(CODE, a + io, d[idd:idd + i.size], m[idd:idd + i.size]):
            # Rest des Originals nur Füllbytes und unser Code zu Ende?
            if idd == len(d) and all(x.mnemonic in ('nop', 'lea', 'mov') for x in ins[k:]):
                return benutzt
            return False
        io += i.size; idd += i.size
    return benutzt and idd == len(d)


def fenster_ende(adr, laenge):
    """Ende des letzten Abschnitts, den [adr, adr+laenge) berührt (mindestens der eigene)."""
    ende = adr
    for f in sorted(funktionen().values(), key=lambda f: int(f['adr'], 16)):
        s = int(f['adr'], 16); e = s + f['laenge']
        if s >= adr and s < adr + max(laenge, 1):
            ende = max(ende, e)
    return ende


def abschnitte(von, bis):
    return [k for k, f in funktionen().items() if von <= int(k, 16) < bis]


def markiere_mit(z, haupt, r, wer):
    """Bei GLEICH über mehrere Abschnitte: die mitabgedeckten Abschnitte ebenfalls GLEICH setzen."""
    for k in r.get('abschnitte', []):
        if k != haupt and z.get(k, {}).get('status') != 'GLEICH':
            z[k] = {'status': 'GLEICH', 'rest': 0, 'in': haupt, 'wer': wer, 'zeit': jetzt(), 'flags': r['flags'],
                    'name': z.get(k, {}).get('name') or ('enthalten in ' + haupt)}


MEHRFACH = 3     # so viele Agenten dürfen parallel an derselben Funktion arbeiten (Wettlauf, Endspurt 22.11.)
STOPP = 12       # Stoppregel: Versuche ohne Gewinn je Funktion (vorher 6)


def belegt_von(b, adr):
    return [k for k in b if k.split('@')[0] == adr]


def lade_beleg():
    return A.jload(BELEG, {})


def cmd_liste(a):
    F = funktionen(); z = A.jload(ZUST, {}); b = lade_beleg()
    offen = [f for f in F.values() if z.get(f['adr'], {}).get('status') != 'GLEICH']
    offen.sort(key=lambda f: (f.get('art') in ('asm', 'system'), z.get(f['adr'], {}).get('rest', 10 ** 6), f['laenge']))
    g = len(F) - len(offen)
    C_ = [f for f in F.values() if f.get('art') not in ('asm', 'system', 'kruemel')]
    gC = [f for f in C_ if z.get(f['adr'], {}).get('status') == 'GLEICH']
    print(f'AIL in C: {len(gC)} von {len(C_)} Funktionen GLEICH, {sum(f["laenge"] for f in gC)} von {sum(f["laenge"] for f in C_)} B'
          f'   (Hand-ASM: {sum(1 for f in F.values() if f.get("art") in ("asm", "system"))} Funktionen, Krümel: {sum(1 for f in F.values() if f.get("art") == "kruemel")})')
    for f in offen[:int(a.n or 20)]:
        s = z.get(f['adr'], {})
        art = {'asm': '[Hand-ASM, später MASM]', 'system': '[System, nicht an Agenten]'}.get(f.get('art'), '')
        if s.get('filter_n', 0) >= 2:
            art = '[2x Filter, nicht an Agenten]'
        print(f"  {f['adr']}  {f['laenge']:>5} B  Rest {str(s.get('rest', '-')):>5}  {s.get('name', '')}  {('belegt ' + b[f['adr']]['id']) if f['adr'] in b else ''} {art}")


def cmd_naechste(a):
    F = funktionen()
    with A.Lock('ail_vergabe'):
        z = A.jload(ZUST, {}); b = lade_beleg()
        for adr, x in list(b.items()):
            if x['id'] == a.id:
                print(f'{a.id} hat schon {adr}. Erst abgeben oder freigeben.'); return
        kand = [f for f in F.values() if z.get(f['adr'], {}).get('status') != 'GLEICH' and len(belegt_von(b, f['adr'])) < MEHRFACH
                and f.get('art') not in ('asm', 'system')  # Hand-Assembler: später mit MASM, nicht in C
                and z.get(f['adr'], {}).get('filter_n', 0) < 2   # zweimal am Modellfilter gescheitert
                and z.get(f['adr'], {}).get('versuche_ohne_gewinn', 0) < STOPP]   # Stoppregel
        if not kand:
            print('KEINE FREIE FUNKTION'); return
        # kleine zuerst, große (>= 1500 B) zuletzt; schon angefangene mit kleinem Rest vor neuen
        kand.sort(key=lambda f: (len(belegt_von(b, f['adr'])), f['laenge'] >= 1500, z.get(f['adr'], {}).get('rest', 10 ** 6) if f['adr'] in z else 10 ** 5 + f['laenge']))
        f = kand[0]
        schl = f['adr'] if f['adr'] not in b else f"{f['adr']}@{a.id}"   # weitere Agenten an derselben Funktion
        b[schl] = {'id': a.id, 'start': jetzt()}; A.jsave(BELEG, b)
    wd = os.path.join(WORK, a.id); os.makedirs(os.path.join(wd, 'entwuerfe'), exist_ok=True)
    datei = os.path.join(wd, name_von(f['adr']).upper() + '.C')
    alt = os.path.join(REKO, name_von(f['adr']).upper() + '.C')
    # Ab dem 3. Fehlschlag Neubau statt Flicken: blind von der Vorlage aus (Blind-Mischen-Methode)
    blind = z.get(f['adr'], {}).get('versuche_ohne_gewinn', 0) >= 3
    if os.path.exists(alt) and not blind:
        shutil.copy2(alt, datei)
    else:
        open(datei, 'w', newline='').write(vorlage(f))
    # Schwestern: bis zu 5 schon gleiche Funktionen ähnlicher Länge (±15 %) als Vorlage
    sw = sorted((abs(g['laenge'] - f['laenge']), g['adr']) for g in F.values()
                if z.get(g['adr'], {}).get('status') == 'GLEICH' and not z[g['adr']].get('in')
                and abs(g['laenge'] - f['laenge']) <= 0.15 * f['laenge'] and g['laenge'] >= 24)[:5]
    schwestern = [os.path.relpath(os.path.join(REKO, name_von(a_).upper() + '.C'), PROJ) for _, a_ in sw]
    A.jsave(os.path.join(wd, 'auftrag.json'), {'id': a.id, 'funktion': f['adr'], 'laenge': f['laenge'], 'datei': datei,
                                               'start': jetzt(), 'rest_start': z.get(f['adr'], {}).get('rest'),
                                               'neubau': blind, 'schwestern': schwestern})
    print(f"FUNKTION {f['adr']} ({f['laenge']} Bytes), Arbeitsdatei {os.path.relpath(datei, PROJ)}"
          + ('  [NEUBAU: frühere Fassungen nicht ansehen, frisch aus dem Assembler]' if blind else ''))
    if schwestern:
        print('Schwestern (schon GLEICH, ähnliche Länge, als Vorlage ansehen):', ', '.join(schwestern))
    print('Weiter mit: python3 Werkzeuge/ail_richter.py zeigen --id', a.id)


def _au(a):
    au = A.jload(os.path.join(WORK, a.id, 'auftrag.json'))
    if not au:
        sys.exit(f'{a.id}: kein Auftrag, erst naechste')
    return au


def cmd_zeigen(a):
    au = _au(a); adr = au['funktion']; f = funktionen()[adr]; o = int(adr, 16) - CB - f.get('vor', 0)
    nm = namen()
    def anm(op):
        for h in re.findall(r'0x[0-9a-f]+', op):
            v = int(h, 16)
            if v in nm:
                op = op.replace(h, f'{h} <{nm[v]}>')
            elif 0x130000 <= v < 0x1b2000:
                op = op.replace(h, f'{h} <DATEN>')
        return op
    import capstone
    cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    print(f'=== Original {adr}, {f["laenge"]} Bytes ===' + (f'\nHINWEIS: {f["notiz"]}' if f.get('notiz') else ''))
    for i in cs.disasm(CODE[o:o + f['laenge'] + f.get('vor', 0)], o + CB):
        print(f'  {i.address:#x}:  {i.mnemonic:7} {anm(i.op_str)}')
    # Aufrufer (vorberechnet in Richter/ail_aufrufer.json) - hilft beim Benennen über die Quellen von SOUND/MAIN
    print('\n=== Aufrufer ===')
    R = A.jload(os.path.join(RD, 'ail_aufrufer.json'), {}).get(adr.lower(), [])
    E = A.einheiten()
    for q, wo in R[:20]:
        m = re.match(r'(\w+)\[(\d+)\]$', wo)
        if m and m.group(1) in E:
            st = A.kompiliere(m.group(1), E[m.group(1)])['stuecke']
            i = int(m.group(2)); wo = f"{m.group(1)}: {st[i]['name'] if i < len(st) else wo}  (Quelle {E[m.group(1)]['src']})"
        print(f'  {q}  in {wo}')
    if not R:
        print('  (keine direkten Aufrufe, evtl. über Funktionszeiger)')
    r = messe(adr, au['datei'])
    if 'fehler' in r:
        print('\n=== eigene Übersetzung: FEHLER ===\n' + r['fehler']); return
    if r.get('modul'):
        print(f"\n=== Vergleich IM MODUL {r['modul']} (- Original, + dein Abschnitt im zusammengesetzten Modul): "
              f"Rest {r['rest']}, Länge {r['laenge']} von {r['orig_laenge']} ===")
        print('  (Sprung-/Aufrufziele stehen als REL und zählen nicht; X = Adresse mit Fixup)')
        for l in difflib.unified_diff(r['db'], r['da'], lineterm='', n=2):
            if not l.startswith(('---', '+++')):
                print('  ' + l)
        return
    fl = r['flags']; rr = kompiliere_datei(adr, au['datei'], fl, f.get('inc'))
    d = b''.join(bytes.fromhex(s['daten']) for s in rr['stuecke'])
    m = b''.join(bytes.fromhex(s['maske']) for s in rr['stuecke'])
    e_ = fenster_ende(o + CB, len(d)) - CB
    A_ = A.dis(CODE[o:e_], base=o + CB); B_ = A.dis(d, m, base=o + CB)
    print(f'\n=== Vergleich (- Original, + eigene Übersetzung, Flags {" ".join(fl) or "(Standard)"}): Rest {r["rest"]} ===')
    for l in difflib.unified_diff(A_, B_, lineterm='', n=2):
        if not l.startswith(('---', '+++')):
            print('  ' + l)


def cmd_messen(a):
    au = _au(a); r = messe(au['funktion'], au['datei'])
    wd = os.path.join(WORK, a.id, 'entwuerfe'); n = len(os.listdir(wd)) + 1
    shutil.copy2(au['datei'], os.path.join(wd, f'v{n:03d}_' + os.path.basename(au['datei'])))
    with open(MESS, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'zeit': jetzt(), 'id': a.id, 'funktion': au['funktion'],
                            'ergebnis': {k: v for k, v in r.items() if k not in ('zeilen', 'da', 'db')}}) + '\n')
    if 'fehler' in r:
        print('FEHLER:\n' + r['fehler']); return
    z = A.jload(ZUST, {}).get(au['funktion'], {})
    if z.get('status') == 'GLEICH':
        print(f"HINWEIS: {au['funktion']} ist inzwischen GLEICH (anderer Agent war schneller). Beende mit: abgeben --ende")
    if len(r.get('abschnitte', [])) > 1:
        print(f"Hinweis: dein Code reicht über {len(r['abschnitte'])} Abschnitte ({', '.join(r['abschnitte'])}); gemessen wird bis {hex(int(au['funktion'], 16) + r['orig_laenge'])}.")
    if r.get('modul'):
        print(f"Modul {r['modul']}: Gesamtstrafe {r['modul_gesamt']}, Abschnitte gleich im Modul {r['modul_gleich']} von {len(r['zeilen'])}")
    print(f"{au['funktion']}: {'GLEICH' if r['gleich'] else 'Rest ' + str(r['rest'])} (Länge {r['laenge']} von {r['orig_laenge']}, "
          f"Flags {' '.join(r['flags']) or '(Standard)'}); bisher bester Rest: {z.get('rest', '-')}")


def cmd_abgeben(a):
    au = _au(a); adr = au['funktion']
    with A.Lock('ail_uebernahme'):
        r = messe(adr, au['datei']); z = A.jload(ZUST, {}); alt = z.get(adr, {})
        ok = 'fehler' not in r and (alt.get('rest') is None or r['rest'] < alt['rest'])
        if r.get('modul') and 'fehler' not in r:
            # Im Modul hängen Abschnitte zusammen (Quersprünge): angenommen wird, was die Gesamtstrafe senkt,
            # oder den eigenen Abschnitt verbessert, ohne dass die Gesamtstrafe steigt.
            import ail_modul
            vor = ail_modul.modul_messe(adr, None, tag='_basis')
            vg = vor.get('modul_gesamt', 10 ** 9)
            ok = r['modul_gesamt'] < vg or (ok and r['modul_gesamt'] <= vg)
            print(f"Modul: Gesamtstrafe vorher {vg}, mit deiner Fassung {r['modul_gesamt']}")
        if ok:
            ziel = os.path.join(REKO, name_von(adr).upper() + '.C')
            if os.path.exists(ziel):
                d = os.path.join(PROJ, 'src_archiv', 'AIL_REKO'); os.makedirs(d, exist_ok=True)
                shutil.copy2(ziel, os.path.join(d, time.strftime('%Y%m%d_%H%M%S_') + a.id + '_' + os.path.basename(ziel)))
            b = open(au['datei'], 'rb').read()
            b = re.sub(rb'(?<!\r)\n', b'\r\n', b)             # Zeilenenden CRLF wie die übrigen Quellen
            open(ziel, 'wb').write(b)
            text = b.decode('latin1')
            z[adr] = {'status': 'GLEICH' if r['gleich'] else 'offen', 'rest': r['rest'], 'flags': r['flags'],
                      'name': ziel_name(text, adr), 'wer': a.id, 'zeit': jetzt(), 'versuche_ohne_gewinn': 0,
                      'quersprung': r.get('quersprung', False)}
            if r['gleich'] and not r.get('modul'):
                markiere_mit(z, adr, r, a.id)
            if r.get('modul'):                          # Nachbarn im Modul mitziehen (sie hängen am selben Lageplan)
                for zl in r['zeilen']:
                    e = z.setdefault(zl['adr'], {})
                    if zl['adr'] != adr:
                        e.update({'status': 'GLEICH' if zl['gleich'] else 'offen',
                                  'rest': 0 if zl['gleich'] else zl['rest'] + abs(zl['ist_l'] - zl['soll_l'])})
                z[adr]['modul'] = r['modul']
        else:
            alt['versuche_ohne_gewinn'] = alt.get('versuche_ohne_gewinn', 0) + 1
            alt.setdefault('rest', r.get('rest')); alt.setdefault('status', 'offen'); z[adr] = alt
        A.jsave(ZUST, z)
        if ok and r['gleich'] or a.ende or not ok:
            b2 = lade_beleg()
            for k in [k for k, v in b2.items() if v['id'] == a.id]:
                b2.pop(k)
            A.jsave(BELEG, b2)
            erl = os.path.join(WORK, a.id, f'auftrag_{adr}_erledigt.json')
            shutil.move(os.path.join(WORK, a.id, 'auftrag.json'), erl)
    try:
        import fortschritt as F
        F.ereignis(wer=f"{os.environ.get('AGENT_WER', 'Agent')} {a.id}", modell=os.environ.get('AGENT_MODELL', ''),
                   was='AIL-Übernahme ' + ('angenommen' if ok else 'abgelehnt'), wie='ail_richter.py abgeben (Ratsche)',
                   einheit='AIL', funktion=adr, start=au['start'], erfolg='ja' if ok and r.get('gleich') else ('teilweise' if ok else 'nein'),
                   vorher=f"Rest {alt.get('rest') if not ok else au.get('rest_start')}", nachher=f"Rest {r.get('rest', 'Fehler')}")
    except Exception as ex:
        print('Hinweis: Fortschritt nicht geschrieben:', ex)
    if 'fehler' in r:
        print('ABGELEHNT, Fehler:\n' + r['fehler'])
    else:
        print(f"{'ÜBERNOMMEN' if ok else 'ABGELEHNT (nicht besser)'}: {adr} Rest {r['rest']}{' GLEICH' if r['gleich'] else ''}"
              + ('' if (ok and r['gleich']) or a.ende or not ok else ' - Funktion bleibt bei dir, weiter verbessern oder --ende'))


def cmd_nachmessen(a):
    """Alle Fassungen in src/AIL/REKO neu messen (z. B. nach neuen Flagsätzen) und Stand verbessern."""
    F = funktionen(); besser = 0
    for adr in sorted(F):
        p = os.path.join(REKO, name_von(adr).upper() + '.C')
        if not os.path.exists(p):
            continue
        with A.Lock('ail_uebernahme'):
            z = A.jload(ZUST, {}); alt = z.get(adr, {})
            if alt.get('status') == 'GLEICH':
                continue
            r = messe(adr, p)
            if 'fehler' not in r and (alt.get('rest') is None or r['rest'] < alt['rest']):
                alt.update({'status': 'GLEICH' if r['gleich'] else 'offen', 'rest': r['rest'], 'flags': r['flags'],
                            'quersprung': r.get('quersprung', False),
                            'zeit': jetzt(), 'wer': (alt.get('wer') or '') + '+nachmessen'})
                z[adr] = alt
                if r['gleich']:
                    markiere_mit(z, adr, r, 'nachmessen')
                A.jsave(ZUST, z); besser += 1
                print(f"{adr}: Rest {r['rest']}{' GLEICH' if r['gleich'] else ''}{' (mit Quersprung)' if r.get('quersprung') else ''} (Flags {' '.join(r['flags'])})")
    print(f'{besser} Funktionen verbessert')
    cmd_liste(argparse.Namespace(n=0))


def cmd_abgebrochen(a):
    """Sitzung eines Agenten ist abgebrochen (z. B. Modellfilter): Funktion freigeben und mitzählen."""
    with A.Lock('ail_vergabe'):
        b = lade_beleg(); z = A.jload(ZUST, {})
        for adr in [k for k, v in b.items() if v['id'] == a.id]:
            b.pop(adr); adr = adr.split('@')[0]; e = z.setdefault(adr, {'status': 'offen'}); e['filter_n'] = e.get('filter_n', 0) + 1
            print(f'{a.id}: {adr} freigegeben, Abbrüche dort: {e["filter_n"]}')
        A.jsave(BELEG, b); A.jsave(ZUST, z)
    p = os.path.join(WORK, a.id, 'auftrag.json')
    if os.path.exists(p):
        shutil.move(p, p.replace('auftrag.json', f'auftrag_abgebrochen_{int(time.time())}.json'))


def cmd_entsperren(a):
    with A.Lock('ail_uebernahme'):
        z = A.jload(ZUST, {}); n = 0
        for v in z.values():
            if v.get('versuche_ohne_gewinn', 0):
                v['versuche_ohne_gewinn'] = 0; n += 1
        A.jsave(ZUST, z)
    print(n, 'Funktionen wieder freigegeben')


def cmd_freigeben(a):
    with A.Lock('ail_vergabe'):
        b = lade_beleg()
        for adr in [k for k, v in b.items() if v['id'] == a.id]:
            b.pop(adr); print('freigegeben', adr)
        A.jsave(BELEG, b)
    p = os.path.join(WORK, a.id, 'auftrag.json')
    if os.path.exists(p):
        shutil.move(p, p.replace('auftrag.json', f'auftrag_freigegeben_{int(time.time())}.json'))


def cmd_status(a):
    cmd_liste(argparse.Namespace(n=0))
    for adr, x in lade_beleg().items():
        print(f"  {x['id']}: {adr} seit {x['start'][11:16]}")


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    l = sp.add_parser('liste'); l.add_argument('n', nargs='?')
    sp.add_parser('status'); sp.add_parser('nachmessen'); sp.add_parser('entsperren')
    for c in ('naechste', 'zeigen', 'messen', 'abgeben', 'freigeben', 'abgebrochen'):
        p = sp.add_parser(c); p.add_argument('--id', required=True)
        if c == 'abgeben':
            p.add_argument('--ende', action='store_true')
    a = ap.parse_args()
    {'liste': cmd_liste, 'status': cmd_status, 'naechste': cmd_naechste, 'zeigen': cmd_zeigen, 'messen': cmd_messen,
     'abgeben': cmd_abgeben, 'freigeben': cmd_freigeben, 'nachmessen': cmd_nachmessen, 'entsperren': cmd_entsperren, 'abgebrochen': cmd_abgebrochen}[a.cmd](a)


if __name__ == '__main__':
    main()
