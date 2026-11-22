#!/usr/bin/env python3
"""fortschritt.py - vollständiges Fortschritts-Tracking für Q 007 Albion.

Ablage (Ordner Fortschritt/ im Projekt):
  ereignisse.jsonl   append-only: wer, was, wie, wann, wie lange, mit welchem Erfolg
  funktionen.tsv     aktueller Stand je Funktionsstück (Einheit, Name, Adresse, Größe, Status, Quelle, Flags, seit, durch)
  einheiten.tsv      aktueller Stand je Übersetzungseinheit
  segmente.tsv       Abdeckung je Objekt/Segment von MAIN.EXE
  FORTSCHRITT.md     erzeugte Übersicht (Gesamt, Gruppen, Segmente, Ablauf, letzte Ereignisse, offene Einheiten)

Befehle:
  fortschritt.py ereignis --wer Agent --modell "Modell" --was "..." --wie "..." [--einheit X] [--funktion F]
                          [--start ISO] [--ende ISO] [--dauer S] [--erfolg ja|nein|teilweise] [--vorher ..] [--nachher ..] [--notiz ..]
  fortschritt.py stand --module stand_module.json [--clib clib_treffer.json] --wer .. --wie ..
        übernimmt Messergebnisse; jede Statusänderung einer Funktion wird automatisch als Ereignis protokolliert
  fortschritt.py bericht
"""
import argparse, csv, datetime as dt, json, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.environ.get('ALBION_PROJ') or os.path.normpath(os.path.join(HERE, '..'))
FD = os.path.join(PROJ, 'Fortschritt')
EV = os.path.join(FD, 'ereignisse.jsonl')
FN = os.path.join(FD, 'funktionen.tsv')
EH = os.path.join(FD, 'einheiten.tsv')
SG = os.path.join(FD, 'segmente.tsv')
MD = os.path.join(FD, 'FORTSCHRITT.md')
EXE = os.path.join(PROJ, 'Original', 'MAIN.EXE')
FCOLS = ['einheit', 'gruppe', 'funktion', 'adresse', 'groesse', 'status', 'quelle', 'flags', 'seit', 'durch']


def now():
    return dt.datetime.now().astimezone().isoformat(timespec='seconds')


def ereignis(**k):
    os.makedirs(FD, exist_ok=True)
    e = {'zeit': now()}
    e.update({a: b for a, b in k.items() if b not in (None, '')})
    # mehrere Agenten schreiben gleichzeitig: Sperre ausserhalb des Windows-Laufwerks, eine Zeile in einem Schreibvorgang
    import fcntl
    os.makedirs(os.environ.get('ALBION_LOCKDIR', '/tmp/albion_locks'), exist_ok=True)
    with open(os.path.join(os.environ.get('ALBION_LOCKDIR', '/tmp/albion_locks'), 'ereignisse.lock'), 'w') as sp:
        fcntl.flock(sp, fcntl.LOCK_EX)
        fd = os.open(EV, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            os.write(fd, (json.dumps(e, ensure_ascii=False) + '\n').encode('utf-8'))
        finally:
            os.close(fd)
    return e


def lade_ev():
    if not os.path.exists(EV):
        return []
    out = []
    for l in open(EV, encoding='utf-8'):
        if l.strip():
            try:
                out.append(json.loads(l))
            except ValueError:
                print('fortschritt: kaputte Zeile in ereignisse.jsonl übersprungen', file=sys.stderr)
    return out


def lade_tsv(p):
    if not os.path.exists(p):
        return []
    return list(csv.DictReader(open(p, encoding='utf-8'), delimiter='\t'))


def schreibe_tsv(p, rows, cols):
    with open(p, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter='\t', extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)


def le_objekte():
    d = open(EXE, 'rb').read()
    L = d.find(b'LE\0\0', 0x2000)
    u = lambda o: struct.unpack_from('<I', d, L + o)[0]
    objs = []
    for k in range(u(0x44)):
        vs, ba, fl, pi, pc, _ = struct.unpack_from('<6I', d, L + u(0x40) + 24 * k)
        objs.append({'nr': k + 1, 'basis': ba, 'groesse': vs, 'typ': 'Code' if fl & 4 else 'Daten'})
    return objs


GRUPPE = {'alb': 'Spiel', 'pcl': 'PCLIB32', 'ail': 'AIL (Miles)'}


def cmd_stand(a):
    alt = {(r['einheit'], r['funktion']): r for r in lade_tsv(FN)}
    mods = json.load(open(a.module))
    neu = {}
    for m, v in mods.items():
        for nm, size, st, adr in v['funcs']:
            k = (m, nm)
            o = alt.get(k)
            r = {'einheit': m, 'gruppe': GRUPPE.get(v.get('grp'), v.get('grp', '?')), 'funktion': nm,
                 'adresse': '%#x' % adr if adr else '', 'groesse': size, 'status': st,
                 'quelle': {'r221': 'Snapshot 22.11.95', 'r051': 'Snapshot 05.11.95', 'r121': 'Snapshot 12.10.95'}.get(v['snap'], v['snap']),
                 'flags': v['flags']}
            if o and o['status'] == st:
                r['seit'], r['durch'] = o['seit'], o['durch']
            else:
                r['seit'], r['durch'] = now(), a.wer + ' / ' + a.wie
                if o:   # echte Statusänderung -> Ereignis
                    ereignis(wer=a.wer, modell=a.modell, was='Statusänderung Funktion', wie=a.wie, einheit=m,
                             funktion=nm, vorher=o['status'], nachher=st,
                             erfolg='ja' if st == 'GLEICH' else ('nein' if o['status'] == 'GLEICH' else 'teilweise'))
            neu[k] = r
    if a.clib:
        for nm, info in json.load(open(a.clib)).items():
            k = ('CLIB3R', nm)
            o = alt.get(k)
            r = {'einheit': 'CLIB3R', 'gruppe': 'Watcom-CLIB 10.0a', 'funktion': nm, 'adresse': info.get('adresse', ''),
                 'groesse': info['groesse'], 'status': info['status'], 'quelle': 'LIB386/DOS/CLIB3R.LIB (10.0a)', 'flags': '-',
                 'seit': o['seit'] if o and o['status'] == info['status'] else now(),
                 'durch': o['durch'] if o and o['status'] == info['status'] else a.wer + ' / Bibliotheksabgleich'}
            neu[k] = r
    for k, o in alt.items():          # nichts verlieren: nicht mehr gemessene Zeilen bleiben stehen
        neu.setdefault(k, o)
    rows = sorted(neu.values(), key=lambda r: (r['gruppe'], r['einheit'], int(r['adresse'], 16) if r['adresse'] else 1 << 40))
    schreibe_tsv(FN, rows, FCOLS)
    # Einheiten
    eh = {}
    for r in rows:
        e = eh.setdefault(r['einheit'], {'einheit': r['einheit'], 'gruppe': r['gruppe'], 'quelle': r['quelle'], 'flags': r['flags'],
                                          'funktionen': 0, 'gleich': 0, 'bytes': 0, 'bytes_gleich': 0})
        e['funktionen'] += 1
        e['bytes'] += int(r['groesse'])
        if r['status'] == 'GLEICH':
            e['gleich'] += 1
            e['bytes_gleich'] += int(r['groesse'])
    for e in eh.values():
        e['anteil'] = '%.1f %%' % (100 * e['bytes_gleich'] / max(e['bytes'], 1))
        e['status'] = 'KOMPLETT' if e['gleich'] == e['funktionen'] else ('offen' if e['gleich'] else 'nicht begonnen')
    schreibe_tsv(EH, sorted(eh.values(), key=lambda e: (e['gruppe'], e['einheit'])),
                 ['einheit', 'gruppe', 'quelle', 'flags', 'funktionen', 'gleich', 'bytes', 'bytes_gleich', 'anteil', 'status'])
    # Segmente
    objs = le_objekte()
    cover = {o['nr']: bytearray(o['groesse']) for o in objs}
    for r in rows:
        if r['status'] == 'GLEICH' and r['adresse']:
            ad, n = int(r['adresse'], 16), int(r['groesse'])
            for o in objs:
                if o['basis'] <= ad < o['basis'] + o['groesse']:
                    s = ad - o['basis']
                    cover[o['nr']][s:s + n] = b'\1' * min(n, o['groesse'] - s)
    srows = []
    for o in objs:
        c = sum(cover[o['nr']])
        srows.append({'objekt': o['nr'], 'typ': o['typ'], 'basis': '%#x' % o['basis'], 'groesse': o['groesse'],
                      'bytegleich_belegt': c, 'anteil': '%.1f %%' % (100 * c / max(o['groesse'], 1))})
    schreibe_tsv(SG, srows, ['objekt', 'typ', 'basis', 'groesse', 'bytegleich_belegt', 'anteil'])
    ereignis(wer=a.wer, modell=a.modell, was='Stand übernommen', wie=a.wie, dauer_s=a.dauer, erfolg='ja',
             nachher='%d/%d Funktionsstücke GLEICH' % (sum(1 for r in rows if r['status'] == 'GLEICH'), len(rows)))
    bericht()


def bericht():
    rows = lade_tsv(FN)
    eh = lade_tsv(EH)
    sg = lade_tsv(SG)
    ev = lade_ev()
    L = ['# Fortschritt Q 007 Albion', '', f'Erzeugt: {now()} · Quelle: `Fortschritt/*.tsv`, `ereignisse.jsonl`', '']
    nf = len(rows); ng = sum(1 for r in rows if r['status'] == 'GLEICH')
    nb = sum(int(r['groesse']) for r in rows); nbg = sum(int(r['groesse']) for r in rows if r['status'] == 'GLEICH')
    L += ['## Gesamt', '', '| Funktionsstücke GLEICH | Bytes GLEICH | Einheiten komplett |', '|---|---|---|',
          f'| {ng} / {nf} ({100*ng/max(nf,1):.1f} %) | {nbg} / {nb} ({100*nbg/max(nb,1):.1f} %) | '
          f'{sum(1 for e in eh if e["status"]=="KOMPLETT")} / {len(eh)} |', '']
    L += ['## Nach Gruppe', '', '| Gruppe | Einheiten | komplett | Stücke GLEICH | Bytes GLEICH |', '|---|---|---|---|---|']
    for g in sorted({e['gruppe'] for e in eh}):
        E = [e for e in eh if e['gruppe'] == g]
        f = sum(int(e['funktionen']) for e in E); fg = sum(int(e['gleich']) for e in E)
        b = sum(int(e['bytes']) for e in E); bg = sum(int(e['bytes_gleich']) for e in E)
        L.append(f'| {g} | {len(E)} | {sum(1 for e in E if e["status"]=="KOMPLETT")} | {fg}/{f} ({100*fg/max(f,1):.1f} %) | {bg}/{b} ({100*bg/max(b,1):.1f} %) |')
    L += ['', '## Segmente von MAIN.EXE (bytegleich belegte Bytes)', '', '| Objekt | Typ | Basis | Größe | belegt | Anteil |', '|---|---|---|---|---|---|']
    for s in sg:
        L.append(f'| {s["objekt"]} | {s["typ"]} | {s["basis"]} | {s["groesse"]} | {s["bytegleich_belegt"]} | {s["anteil"]} |')
    L += ['', 'Hinweis: Datensegmente werden erst beim Gesamtbau gemessen, bis dahin 0 %.', '']
    L += ['## Ablauf (wer · was · wie · wann · wie lange · Erfolg)', '',
          '| Zeit | Wer | Was | Wie | Dauer | Erfolg | Ergebnis |', '|---|---|---|---|---|---|---|']
    for e in [x for x in ev if x.get('was') != 'Statusänderung Funktion'][-40:]:
        d = e.get('dauer_s')
        ds = '' if d in (None, '') else (f'{float(d):.0f} s' if float(d) < 120 else f'{float(d)/60:.1f} min')
        wer = e.get('wer', '') + (f' ({e["modell"]})' if e.get('modell') else '')
        L.append(f'| {e.get("start", e["zeit"])[:16]} | {wer} | {e.get("was","")} | {e.get("wie","")} | {ds} | {e.get("erfolg","")} | {e.get("nachher","")} |')
    ch = [x for x in ev if x.get('was') == 'Statusänderung Funktion']
    L += ['', f'## Statusänderungen einzelner Funktionen ({len(ch)} insgesamt, letzte 25)', '',
          '| Zeit | Einheit | Funktion | vorher → nachher | wer / wie |', '|---|---|---|---|---|']
    for e in ch[-25:]:
        L.append(f'| {e["zeit"][:16]} | {e.get("einheit","")} | {e.get("funktion","")} | {e.get("vorher","")} → {e.get("nachher","")} | {e.get("wer","")} / {e.get("wie","")} |')
    L += ['', '## Offene Einheiten (größter offener Rest zuerst)', '', '| Einheit | Gruppe | Stücke | Bytes offen | Quelle | Flags |', '|---|---|---|---|---|---|']
    op = sorted([e for e in eh if e['status'] != 'KOMPLETT'], key=lambda e: -(int(e['bytes']) - int(e['bytes_gleich'])))
    for e in op[:40]:
        L.append(f'| {e["einheit"]} | {e["gruppe"]} | {e["gleich"]}/{e["funktionen"]} | {int(e["bytes"])-int(e["bytes_gleich"])} | {e["quelle"]} | {e["flags"]} |')
    os.makedirs(FD, exist_ok=True)
    open(MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(f'{ng}/{nf} Stücke GLEICH, {nbg}/{nb} Bytes -> {MD}')


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    e = sp.add_parser('ereignis')
    for k in ('wer', 'modell', 'was', 'wie', 'einheit', 'funktion', 'start', 'ende', 'dauer', 'erfolg', 'vorher', 'nachher', 'notiz'):
        e.add_argument('--' + k)
    s = sp.add_parser('stand')
    s.add_argument('--module', required=True)
    s.add_argument('--clib')
    s.add_argument('--wer', default='Agent')
    s.add_argument('--modell', default='')
    s.add_argument('--wie', default='Messung')
    s.add_argument('--dauer')
    sp.add_parser('bericht')
    a = ap.parse_args()
    if a.cmd == 'ereignis':
        k = {x: getattr(a, x) for x in ('wer', 'modell', 'was', 'wie', 'einheit', 'funktion', 'start', 'ende', 'erfolg', 'vorher', 'nachher', 'notiz')}
        k['dauer_s'] = a.dauer
        print(ereignis(**k))
        bericht()
    elif a.cmd == 'stand':
        cmd_stand(a)
    else:
        bericht()


if __name__ == '__main__':
    main()
