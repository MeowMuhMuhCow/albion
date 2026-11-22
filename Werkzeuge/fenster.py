#!/usr/bin/env python3
"""fenster.py - Fortschrittsanzeige fuer den Luecken-Lauf, erneuert sich jede Minute.

Liest nur: Richter/karte.json, Richter/zustand.json, work/*/auftrag.json, LOG.md.
Schreibt nur: Fortschritt/fenster_verlauf.tsv (Zeit, GLEICH, Rest) fuer die Geschwindigkeit.
Aufruf: python3 Werkzeuge/fenster.py [--takt 60]
"""
import argparse, datetime as dt, json, os, re, shutil, sys, time

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZUSTAND = os.path.join(PROJ, 'Richter', 'zustand.json')
WORK = os.path.join(PROJ, 'work')
LOG = os.path.join(PROJ, 'LOG.md')
VERLAUF = os.path.join(PROJ, 'Fortschritt', 'fenster_verlauf.tsv')
EREIGNISSE = os.path.join(PROJ, 'Fortschritt', 'ereignisse.jsonl')
MESSUNGEN = os.path.join(PROJ, 'Richter', 'messungen.jsonl')

G, R, Y, C, B, D, N = '\033[32m', '\033[31m', '\033[33m', '\033[36m', '\033[1m', '\033[2m', '\033[0m'
SPARK = ' ▁▂▃▄▅▆▇█'


def jload(p):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return None


def log_zeilen():
    """LOG.md -> Liste (datetime, zeile, angenommen, rest_weniger). Uhrzeiten ohne Datum: Tageswechsel erkennen."""
    try:
        zeilen = open(LOG, encoding='utf-8', errors='replace').read().splitlines()
    except OSError:
        return []
    heute = dt.date.today()
    roh = []
    for z in zeilen:
        m = re.match(r'\s*(\d\d):(\d\d)\s', z)
        if m:
            roh.append((int(m.group(1)) * 60 + int(m.group(2)), z))
    # rueckwaerts: letzte Zeile ist heute, Sprung nach vorn heisst Vortag
    out, tag, letzt = [], heute, None
    for mins, z in reversed(roh):
        if letzt is not None and mins > letzt + 60:
            tag -= dt.timedelta(days=1)
        letzt = mins
        t = dt.datetime.combine(tag, dt.time(mins // 60, mins % 60))
        ja = 'übernommen ja' in z
        nein = 'übernommen nein' in z or 'abgelehnt' in z
        weniger = sum(max(0, int(a) - int(b)) for a, b in re.findall(r'(\d+)\s*->\s*(\d+)', z)) if ja else 0
        out.append((t, z, ja, nein, weniger))
    out.reverse()
    return out


def richter_ereignisse():
    """Abgaben laut Richter (ereignisse.jsonl) -> Liste (zeit, angenommen, abgelehnt, rest_weniger).
    Zaehlt nach dem Richter, nicht nach den Agentenzeilen in LOG.md (die koennen sich verschreiben)."""
    out = []
    try:
        f = open(EREIGNISSE, encoding='utf-8', errors='replace')
    except OSError:
        return out
    for z in f:
        try:
            e = json.loads(z)
        except Exception:
            continue
        was = e.get('was', '')
        was = was.replace('AIL-Übernahme', 'Übernahme')     # AIL-Lauf zählt mit
        if was not in ('Übernahme angenommen', 'Übernahme abgelehnt'):
            continue
        try:
            t = dt.datetime.fromisoformat(e['zeit']).replace(tzinfo=None)
        except Exception:
            continue
        zahl = lambda x: int(m.group(1)) if (m := re.search(r'Rest (\d+)', x or '')) else None
        a, b = zahl(e.get('vorher')), zahl(e.get('nachher'))
        weniger = max(0, a - b) if a is not None and b is not None else 0
        out.append((t, was == 'Übernahme angenommen', was == 'Übernahme abgelehnt', weniger))
    return out


def verlauf_schreiben(jetzt, gleich, rest):
    os.makedirs(os.path.dirname(VERLAUF), exist_ok=True)
    neu = not os.path.exists(VERLAUF)
    with open(VERLAUF, 'a', encoding='utf-8') as f:
        if neu:
            f.write('zeit\tgleich\trest\n')
        f.write(f'{jetzt:%Y-%m-%dT%H:%M}\t{gleich}\t{rest}\n')


def verlauf_lesen():
    v = []
    try:
        for z in open(VERLAUF, encoding='utf-8').read().splitlines()[1:]:
            t, g, r = z.split('\t')
            v.append((dt.datetime.fromisoformat(t), int(g), int(r)))
    except Exception:
        pass
    return v


def balken(anteil, breite):
    voll = int(anteil * breite)
    return G + '█' * voll + D + '░' * (breite - voll) + N


def dauer(h):
    if h is None or h != h or h < 0:
        return '–'
    if h < 1:
        return f'{h * 60:.0f} min'
    return f'{h:.1f} h' if h < 48 else f'{h / 24:.1f} Tage'


def zeichne():
    breite = max(60, min(shutil.get_terminal_size((100, 40)).columns, 120))
    z = jload(ZUSTAND) or {'luecken': {}, 'zeit': '?'}
    v = list(z['luecken'].values())
    n = len(v) or 1
    gleich = sum(1 for x in v if x.get('status') == 'GLEICH')
    rest = sum(x.get('rest') or 0 for x in v if x.get('status') != 'GLEICH')
    L = log_zeilen()
    jetzt = dt.datetime.now()
    # Log-Uhrzeiten sind Ortszeit der Agenten; Versatz zur eigenen Uhr aus dem Aenderungszeitpunkt von LOG.md
    if L:
        mt = dt.datetime.fromtimestamp(os.path.getmtime(LOG))
        jetzt += dt.timedelta(hours=round((L[-1][0] - mt).total_seconds() / 3600))
    verlauf_schreiben(jetzt, gleich, rest)
    VL = verlauf_lesen()
    RE = richter_ereignisse()

    def seit(minuten):
        grenze = jetzt - dt.timedelta(minutes=minuten)
        e = [x for x in RE if x[0] >= grenze]
        return sum(1 for x in e if x[1]), sum(1 for x in e if x[2]), sum(x[3] for x in e)

    o = []
    o.append(f'{B}{C} Q 007 Albion – Lücken-Lauf{N}   {D}{jetzt:%d.%m.%Y %H:%M:%S}, Richterstand {z["zeit"][11:16]}{N}')
    o.append('')
    o.append(f' C-Lücken GLEICH  {B}{gleich}{N} von {n}   {balken(gleich / n, breite - 40)} {100 * gleich / n:5.1f} %')
    o.append(f' offener Rest     {B}{rest}{N} Befehle in {n - gleich} Lücken')
    fa = jload(os.path.join(PROJ, 'Richter', 'ail_funktionen.json')); za = jload(os.path.join(PROJ, 'Richter', 'ail_zustand.json')) or {}
    if fa:
        alle = fa['funktionen']
        F = [f for f in alle if f.get('art') not in ('asm', 'system', 'kruemel')]          # AIL in C
        H = [f for f in alle if f.get('art') in ('asm', 'system')]                         # Hand-Assembler
        K = [f for f in alle if f.get('art') == 'kruemel']
        gl = lambda f: za.get(f['adr'], {}).get('status') == 'GLEICH'
        gb = sum(f['laenge'] for f in F if gl(f)); ga = sum(1 for f in F if gl(f)); tb = sum(f['laenge'] for f in F) or 1
        o.append(f' AIL in C GLEICH  {B}{ga}{N} von {len(F)} Funktionen   {balken(gb / tb, breite - 54)} {gb} von {tb} B')
        o.append(f' {D}AIL Hand-ASM: {len(H)} Funktionen, {sum(f["laenge"] for f in H)} B (später MASM)   '
                 f'Krümel: {sum(1 for f in K if gl(f))} von {len(K)} GLEICH{N}')
    o.append('')
    o.append(f' {B}Tempo laut Richter{N} Übernahmen   Ablehnungen   Rest weg')
    for m, name in ((10, 'letzte 10 min'), (30, 'letzte 30 min'), (60, 'letzte Stunde'), (24 * 60, 'heute/24 h')):
        a, b, w = seit(m)
        o.append(f'   {name:14} {G}{a:>10}{N}   {R}{b:>11}{N}   {w:>8}')
    # Hochrechnung aus dem Rest-Abbau laut Richter (Abgaben der letzten Stunde); ein Kartenneubau zaehlt nicht mit
    _, _, weg60 = seit(60)
    if fa:                                      # AIL: Tempo in Funktionen und Bytes
        g60 = [f for f in F if za.get(f['adr'], {}).get('status') == 'GLEICH' and
               dt.datetime.fromisoformat(za[f['adr']]['zeit']).replace(tzinfo=None) >= jetzt - dt.timedelta(minutes=60)]
        if g60:
            offen_b = tb - gb; b60 = sum(f['laenge'] for f in g60)
            eta = (f'bei dem Tempo fertig in {dauer(offen_b / b60)}' if gb >= 0.2 * tb else
                   'Hochrechnung erst ab 20 % der Bytes (bisher fast nur Kleinstfunktionen)')
            o.append(f'   AIL: {len(g60)} Funktionen ({b60} B) GLEICH in der letzten Stunde, {eta}')
    if weg60 > 0 and rest > 300:
        eta = rest / weg60
        o.append(f'   Rest-Abbau laut Richter: {weg60} Befehle in der letzten Stunde, bei dem Tempo fertig in {dauer(eta)} {D}(grob, die großen Lücken kommen zuletzt){N}')
    o.append('')
    # Sparkline: Uebernahmen je 10 min, letzte 3 h
    eimer = [0] * 18
    for t, ja, _, _ in RE:
        k = int((jetzt - t).total_seconds() // 600)
        if ja and 0 <= k < 18:
            eimer[17 - k] += 1
    mx = max(eimer) or 1
    spark = ''.join(SPARK[min(8, round(8 * e / mx))] if e else D + '·' + N + G for e in eimer)
    o.append(f' Übernahmen je 10 min, letzte 3 h:  {G}{spark}{N}  {D}(max {max(eimer)}){N}')
    o.append('')
    # Agenten: Messungen zeigen, dass gearbeitet wird, auch wenn noch nichts abgegeben ist
    mess = {}
    try:
        for zm in open(MESSUNGEN, encoding='utf-8', errors='replace'):
            try:
                m = json.loads(zm)
            except ValueError:
                continue
            t = dt.datetime.fromisoformat(m['zeit']).replace(tzinfo=None)
            r = m.get('ergebnis', {}).get('luecken', {}).get(m.get('luecke'), {}).get('rest')
            e = mess.setdefault(m.get('id'), {'n': {}, 'zeit': None, 'rest': None})
            e['n'][m.get('luecke')] = e['n'].get(m.get('luecke'), 0) + 1
            e['zeit'], e['rest'] = t, r
    except OSError:
        pass
    ail_mess = {}
    try:
        for zm in open(os.path.join(PROJ, 'Richter', 'ail_messungen.jsonl'), encoding='utf-8', errors='replace'):
            try:
                m = json.loads(zm)
            except ValueError:
                continue
            e = ail_mess.setdefault(m.get('id'), {'n': {}})
            e['n'][m.get('funktion')] = e['n'].get(m.get('funktion'), 0) + 1
            e['funktion'] = m.get('funktion'); e['rest'] = m.get('ergebnis', {}).get('rest')
            t = dt.datetime.fromisoformat(m['zeit']).replace(tzinfo=None)
            if m.get('id') in mess:
                mess[m['id']]['zeit'] = max(mess[m['id']]['zeit'] or t, t)
            else:
                mess[m['id']] = {'n': {}, 'zeit': t, 'rest': None}
    except OSError:
        pass
    letzte_zeit = {}
    for t, zl, *_ in L:
        m = re.match(r'\s*\d\d:\d\d\s+(\S+)', zl)
        if m:
            letzte_zeit[m.group(1)] = t
    zeilen = []
    for d in sorted(os.listdir(WORK)) if os.path.isdir(WORK) else []:
        p = os.path.join(WORK, d)
        if not os.path.isdir(p):
            continue
        fertig = len([f for f in os.listdir(p) if f.endswith('_erledigt.json')])
        au = jload(os.path.join(p, 'auftrag.json'))
        me = mess.get(d, {})
        akt = max([x for x in (letzte_zeit.get(d), me.get('zeit')) if x], default=None)
        still = (jetzt - akt).total_seconds() / 60 if akt else None
        if not au and (still is None or still > 30):
            continue                       # abgeschlossene Läufe ausblenden
        farbe = '' if still is None or still < 20 else (Y if still < 45 else R)
        lzs = f'{farbe}vor {still:.0f} min{N}' if still is not None else '–'
        if au and 'funktion' in au:              # AIL-Lauf (ail_richter.py)
            am = ail_mess.get(d, {}); r = am.get('rest') if am.get('funktion') == au['funktion'] else None
            zeilen.append(f' {d:6} {au["funktion"][2:]:>6} {"AIL " + str(au.get("laenge", "")) + " B":18} {str(r if r is not None else "-"):>6} {am.get("n", {}).get(au["funktion"], 0):>6}  {au["start"][11:16]}  {fertig:>8}  {lzs}')
        elif au:
            r = me.get('rest') if me.get('zeit') and me['zeit'] >= dt.datetime.fromisoformat(au['start']).replace(tzinfo=None) else None
            r = r if r is not None else z['luecken'].get(au['luecke'], {}).get('rest')
            nm = me.get('n', {}).get(au['luecke'], 0)
            zeilen.append(f' {d:6} {au["luecke"]}  {"+".join(au["einheiten"])[:18]:18} {str(r):>6} {nm:>6}  {au["start"][11:16]}  {fertig:>8}  {lzs}')
        else:
            zeilen.append(f' {d:6} -      {D}(sucht/fertig){N}                                  {fertig:>8}  {lzs}')
    o.append(f' {B}Agent  Lücke  Einheit(en)          Rest  Mess.  seit   erledigt  zuletzt aktiv{N}')
    o.extend(zeilen or [f' {D}(kein Agent aktiv){N}'])
    o.append('')
    o.append(f' {B}Zuletzt{N}')
    for t, zl, ja, nein, _ in L[-12:]:
        farbe = G if ja else (R if nein else '')
        o.append(f'  {farbe}{zl[:breite - 3]}{N}')
    fertig_alle = [zl for _, zl, *_ in L if 'ABGESCHLOSSEN' in zl]
    if fertig_alle:
        o.append('')
        o.append(f' {Y}Abgeschlossen: {", ".join(x.split()[2] if len(x.split()) > 2 else x for x in fertig_alle)}{N}')
    return '\n'.join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--takt', type=int, default=60)
    ap.add_argument('--einmal', action='store_true')
    a = ap.parse_args()
    while True:
        try:
            bild = zeichne()
        except Exception as ex:
            bild = f'Fehler beim Lesen: {ex!r} (nächster Versuch in {a.takt} s)'
        sys.stdout.write('\033[H\033[2J\033[3J' + bild + f'\n\n {D}erneuert alle {a.takt} s, Strg+C beendet{N}\n')
        sys.stdout.flush()
        if a.einmal:
            break
        time.sleep(a.takt)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
