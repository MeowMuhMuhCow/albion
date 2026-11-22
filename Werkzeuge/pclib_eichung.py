#!/usr/bin/env python3
"""pclib_eichung.py - Flags der PCLIB bestimmen: Quellen 05.11.95 mit Kandidaten-Flags uebersetzen und
gegen die fertigen OBJs aus demselben Snapshot (SRC/*/OBJS) vergleichen. Nur lesend fuer src/ und Karte;
uebersetzt in src/_K/K<pid> wie der Richter. Ergebnis: Analyse/pclib/eichung.tsv und Zusammenfassung.

Aufruf: python3 Werkzeuge/pclib_eichung.py [--prozesse 4]
"""
import json, os, sys, time
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import albion  # noqa: E402
sys.path.insert(0, os.path.join(HERE, 'byte-exact-decomp-toolkit', '02_basis'))
import omf  # noqa: E402

PROJ = albion.PROJ
SNAP = os.path.join(PROJ, 'Referenz_Horneman', 'horneman_albion', 'MS-DOS', '051195', 'PCLIB32', 'SRC')
AUS = os.path.join(PROJ, 'Analyse', 'pclib')

SAETZE = {
    'AKTUELL': None,                                                     # Flags aus albion_einheiten.json
    'OPT0511': ['-5r', '-od', '-d2', '-w1', '-dDEBUG', '-dBYTEPIXEL'],   # PCLIB OPTIONS 05.11.95
    'OPT2211': ['-wx', '-d2', '-od', '-5r', '-dBYTEPIXEL'],              # PCLIB OPTIONS 22.11.95
    'INT0511': ['-5r', '-omlet', '-w3', '-s', '-dWORDPIXEL'],           # Compiler_Options_int 05.11.95 (BBSYSTEM)
    'INT2211': ['-5r', '-omlet', '-wx', '-s', '-dBYTEPIXEL'],           # Compiler_Options_int 22.11.95
    'MEM_D2':  ['-d2', '-od', '-5r', '-dDEBUG'],                        # BBMEM-Makefile
    'MEM_D0':  ['-d0', '-od', '-5r', '-dDEBUG'],
}
# Einheit -> (Quelle im Snapshot, OBJ im Snapshot)
PAARE = {
    'BBDSA': ('BBDSA/BBDSA.C', 'BBDSA/OBJS/BBDSA.OBJ'),
    'BBLBM': ('BBLBM/BBLBM.C', 'BBLBM/OBJS/BBLBM.OBJ'),
    'BBTGA': ('BBLBM/BBTGA.C', 'BBLBM/OBJS.HI/BBTGA.OBJ'),
    'BBMEM': ('BBMEM/BBMEM.C', 'BBMEM/OBJS/BBMEM.OBJ'),
    'BBMEMALO': ('BBMEM/BBMEMALO.C', 'BBMEM/OBJS/BBMEMALO.OBJ'),
    'BBMEMCHK': ('BBMEM/BBMEMCHK.C', 'BBMEM/OBJS/BBMEMCHK.OBJ'),
    'BBMEMVAR': ('BBMEM/BBMEMVAR.C', 'BBMEM/OBJS/BBMEMVAR.OBJ'),
    'BBMTH': ('BBMTH/BBMTH.C', 'BBMTH/OBJS/BBMTH.OBJ'),
    'SINTAB': ('BBMTH/SINTAB.C', 'BBMTH/OBJS/SINTAB.OBJ'),
    'TANTAB': ('BBMTH/TANTAB.C', 'BBMTH/OBJS/TANTAB.OBJ'),
    'BBOPM': ('BBOPM/BBOPM.C', 'BBOPM/OBJS/BBOPM.OBJ'),
    'BBSYSTEM': ('BBSYSTEM/BBSYSTEM.C', 'BBSYSTEM/OBJS/BBSYSTEM.OBJ'),
    'KEYINTRN': ('BBSYSTEM/KEYINTRN.C', 'BBSYSTEM/OBJS/KEYINTRN.OBJ'),
    'STDMOUSP': ('BBSYSTEM/STDMOUSP.C', 'BBSYSTEM/OBJS/STDMOUSP.OBJ'),
}


def obj_text(p):
    for m in omf.modules(p):
        for s in m['segs'].values():
            if s['name'] == '_TEXT':
                return bytes(s['data']), bytes(s['mask'])
    return b'', b''


def vergleich(a, am, b, bm):
    if len(a) != len(b):
        return None
    return sum(1 for k in range(len(a)) if not am[k] and not bm[k] and a[k] != b[k])


def job(arg):
    u, satz = arg
    E = albion.einheiten(); cfg = dict(E[u])
    if SAETZE[satz] is not None:
        cfg['flags'] = SAETZE[satz]
    q, o = PAARE[u]
    t0 = time.time()
    try:
        r = albion.kompiliere(u, cfg, os.path.join(SNAP, q))
    except Exception as ex:
        return (u, satz, 'ABSTURZ', repr(ex)[:80], 0, 0, time.time() - t0)
    if r.get('fehler'):
        return (u, satz, 'FEHLER', r['fehler'].strip().splitlines()[-1][:80] if r['fehler'].strip() else '?', 0, 0, time.time() - t0)
    a = b''.join(bytes.fromhex(s['daten']) for s in r['stuecke'])
    am = b''.join(bytes.fromhex(s['maske']) for s in r['stuecke'])
    b, bm = obj_text(os.path.join(SNAP, o))
    d = vergleich(a, am, b, bm)
    status = 'GLEICH' if d == 0 else ('LAENGE' if d is None else 'ABW')
    return (u, satz, status, '' if d is None else str(d), len(a), len(b), time.time() - t0)


def main():
    n = int(sys.argv[sys.argv.index('--prozesse') + 1]) if '--prozesse' in sys.argv else 4
    os.makedirs(AUS, exist_ok=True)
    jobs = [(u, s) for u in PAARE for s in SAETZE]
    out = os.path.join(AUS, 'eichung.tsv')
    erg = []
    with open(out, 'w', encoding='utf-8') as f:
        f.write('einheit\tsatz\tstatus\tabweichende_bytes\tlaenge_wir\tlaenge_obj\tsekunden\n')
        with Pool(n) as p:
            for i, r in enumerate(p.imap_unordered(job, jobs), 1):
                erg.append(r)
                f.write('\t'.join(str(x) if not isinstance(x, float) else f'{x:.1f}' for x in r) + '\n'); f.flush()
                print(f'[{i}/{len(jobs)}] {r[0]:9} {r[1]:8} {r[2]:7} {r[3]:>6}  ({r[4]}/{r[5]} B, {r[6]:.0f} s)', flush=True)
    print('\nZusammenfassung (bester Flagsatz je Einheit):')
    for u in PAARE:
        rs = [r for r in erg if r[0] == u]
        gl = [r[1] for r in rs if r[2] == 'GLEICH']
        if gl:
            print(f'  {u:9} GLEICH mit {", ".join(gl)}')
        else:
            ab = sorted((int(r[3]), r[1]) for r in rs if r[2] == 'ABW')
            print(f'  {u:9} kein GLEICH' + (f', am nächsten {ab[0][1]} ({ab[0][0]} Bytes)' if ab else ', nur Längenabweichung/Fehler'))
    print(f'\nTabelle: {out}')


if __name__ == '__main__':
    main()
