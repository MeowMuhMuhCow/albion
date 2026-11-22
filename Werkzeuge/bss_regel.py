#!/usr/bin/env python3
"""bss_regel.py - Kleine Testquellen übersetzen, um Watcoms Reihenfolge im _BSS zu verstehen.
Aufruf: python3 Werkzeuge/bss_regel.py   Ergebnis: Analyse/bss_regel.txt"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import albion as A  # noqa: E402


def quelle(decls, uses):
    t = '\n'.join(decls) + '\n\nint f( void )\n{\n\tint r = 0;\n'
    t += ''.join(f'\tr += {u}[1];\n' for u in uses) + '\treturn r;\n}\n'
    return t.encode()


D = ['char aa[16];', 'char bb[16];', 'char cc[16];', 'static char ss[16];']
TESTS = [
    ('T9 Größen verschieden', ['char aa[16];', 'char bb[4096];', 'char cc[8];', 'static char ss[144];'], []),
    ('U1 extern cc vorab', ['extern char cc[];', 'char aa[16];', 'char bb[4096];', 'char cc[8];', 'static char ss[144];'], []),
    ('U2 static nach Funktion', ['char aa[16];', 'char bb[4096];', 'char cc[8];', 'int g(void){return aa[0];}', 'static char ss[144];'], ['ss']),
    ('U3 stdio vorab', ['#include <stdio.h>', 'char aa[16];', 'char bb[4096];', 'char cc[8];', 'static char ss[144];'], []),
    ('U4 BBDOS-Kopf', ['#include <BBDEF.H>', '#include <BBDOS.H>', 'char aa[16];', 'char bb[4096];', 'char cc[8];', 'static char ss[144];'], []),
    ('U5 BBDOS-Kopf + echte Namen', ['#include <BBDEF.H>', '#include <BBDOS.H>', 'char BBDOS_filenames[50][128];',
        'char errorfilenames[32][128];', 'static char DOS_getcurrentdir_path[144];'], []),
    ('U6 wie U5 ohne Kopf', ['char BBDOS_filenames[50][128];', 'char errorfilenames[32][128];', 'static char DOS_getcurrentdir_path[144];'], []),
    ('U7 viele Funktionen davor', [f'int fn{i}(int x){{return x+{i};}}' for i in range(60)] + ['char aa[16];', 'static char ss[144];'], []),
    ('U8 viele Globale', [f'char gv{i:02d}[4];' for i in range(60)] + ['static char ss[144];'], []),
]



def main():
    E = A.einheiten(); z = []
    wd = os.path.join(A.PROJ, 'Bau', 'probe'); os.makedirs(wd, exist_ok=True)
    for unit in ('BBDOS',):
        cfg = E[unit]; z.append(f'##### Flags von {unit}: {" ".join(cfg["flags"])}')
        for name, decls, uses in TESTS:
            p = os.path.join(wd, os.path.basename(cfg['src']))
            open(p, 'wb').write(quelle(decls, uses))
            r = A.kompiliere(unit, cfg, datei=p, mit_obj=True)
            if r.get('fehler') or not r.get('obj'):
                z.append(f'{name}: FEHLER {str(r.get("fehler"))[-200:]}'); continue
            L = sorted((o, n) for sg, o, n in A.pubs(r['obj']) if sg == '_BSS')
            z.append(f'{name}: ' + ' '.join(f'{n}@{o:#x}' for o, n in L))
    open(os.path.join(A.PROJ, 'Analyse', 'bss_regel.txt'), 'w').write('\n'.join(z) + '\n')
    print('\n'.join(z))


if __name__ == '__main__':
    main()
