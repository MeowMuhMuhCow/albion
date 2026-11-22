#!/usr/bin/env python3
"""emu100a.py - Watcom C 10.0a (BINB/WCC386.EXE, CF-Image) im Unicorn-Emulator.

Gleiche Mechanik wie emu106.py aus dem Toolkit; nur Stub-/Exit-Adressen und das Programm sind anders.
  Watcom 10.0a WCC386.EXE (CF size 0x8209C, entry 0x2FE00): int-21h-Stub 0x2FED3, Exit-retf 0x2FED1.

Aufruf: python3 emu100a.py --root DIR [--exe PFAD] -- DATEI.C -5r -ox -d0 -zq
"""
import argparse, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.join(HERE, 'byte-exact-decomp-toolkit', '01_werkzeugkette'),
          os.path.join(HERE, '..', 'Werkzeuge', 'byte-exact-decomp-toolkit', '01_werkzeugkette'),
          os.path.join(HERE, 'tk01')):
    if os.path.isdir(p):
        sys.path.insert(0, p)
import emu106
from emu106 import Emu106

STUB_100A, EXIT_100A = 0x2FED3, 0x2FED1
DEFAULT_EXE = os.path.normpath(os.path.join(HERE, '..', 'Compiler', 'w100a', 'BINB', 'WCC386.EXE'))


class Emu100a(Emu106):
    def __init__(self, root, args, exe=DEFAULT_EXE, env=None, fill=None):
        super().__init__(root, args, exe=exe, env=env, fill=fill, stub=STUB_100A, exit=EXIT_100A)

    def host(self, dos, create=False):
        # wie Emu106.host, zusaetzlich '..' (relative Includes wie ..\..\lib\asminc\X.H)
        p = dos.replace('/', '\\')
        al = getattr(self, 'alias', None)       # feste Umleitungen: Originalpfad (fuer __FILE__) -> Arbeitsdatei
        if al:
            k = (p[2:] if len(p) >= 2 and p[1] == ':' else p).lower()
            if k in al:
                return al[k]
        if len(p) >= 2 and p[1] == ':':
            p = p[2:]
        raw = p.split('\\') if p.startswith('\\') else (self.cwd.split('\\') if self.cwd else []) + p.split('\\')
        parts = []
        for x in raw:
            if not x or x == '.':
                continue
            if x == '..':
                if parts:
                    parts.pop()
                continue
            parts.append(x)
        cur = self.root
        for i, x in enumerate(parts):
            try:
                names = os.listdir(cur)
            except OSError:
                return None
            hit = [n for n in names if n.lower() == x.lower()]
            if hit:
                cur = os.path.join(cur, hit[0])
            elif create and i == len(parts) - 1:
                cur = os.path.join(cur, x.upper())
            else:
                return None
        return cur

    # Uhr des Bau-Rechners: __DATE__/__TIME__ in VERSION.C stehen in MAIN.EXE als "Jul 25 1996" "12:39:09"
    def dos_2A(self, al):
        self.w(emu106.X.UC_X86_REG_ECX, 1996)
        self.w(emu106.X.UC_X86_REG_EDX, (7 << 8) | 25)
        self.w(emu106.X.UC_X86_REG_EAX, 4)          # Donnerstag
        self.cf(0)

    def dos_2C(self, al):
        self.w(emu106.X.UC_X86_REG_ECX, (12 << 8) | 39)
        self.w(emu106.X.UC_X86_REG_EDX, 9 << 8)
        self.cf(0)

    def dos_3D(self, al):
        # nicht vorhandene Datei: DOS-Fehler 2 statt Python-Ausnahme (WCC386 prueft so alte .ERR-Dateien)
        p = self.host(self.cstr(self.r(emu106.X.UC_X86_REG_EDX)))
        if p is None or os.path.isdir(p) or not os.path.exists(p):
            return self.err(2)
        self.ok(self._open(p, 'r+b' if al & 3 else 'rb'))


def compile_c(root, src, flags, exe=DEFAULT_EXE, include='C:\\H'):
    env = {'PATH': 'C:\\', 'INCLUDE': include, 'WATCOM': 'C:\\'}
    e = Emu100a(root, [src] + flags + ['-zq'], exe=exe, env=env)
    code, dt = e.run()
    return code, dt, e.out.decode('latin-1').replace('\r', ''), e.fault


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--exe', default=DEFAULT_EXE)
    ap.add_argument('--trace', action='store_true')
    ap.add_argument('args', nargs='*')
    a = ap.parse_args()
    e = Emu100a(a.root, a.args, exe=a.exe, env={'PATH': 'C:\\', 'INCLUDE': 'C:\\H', 'WATCOM': 'C:\\'})
    e.trace = a.trace
    code, dt = e.run()
    sys.stdout.write(e.out.decode('latin-1').replace('\r', ''))
    print('[emu100a] Exit %s, %.2f s%s' % (code, dt, (', ' + e.fault) if e.fault else ''), file=sys.stderr)
    sys.exit(0 if code == 0 else 1)


if __name__ == '__main__':
    main()
