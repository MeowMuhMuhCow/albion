#!/usr/bin/env python3
"""fat12.py - Dateien aus Disketten-Abbildern (FAT12/16) lesen. list BILD | extract BILD ZIELORDNER [MUSTER]"""
import struct, sys, os, fnmatch


class FAT:
    def __init__(self, p):
        self.d = d = open(p, 'rb').read()
        self.bps, self.spc, self.res, self.nf, self.nroot = struct.unpack_from('<HBHBH', d, 11)
        ts = struct.unpack_from('<H', d, 19)[0] or struct.unpack_from('<I', d, 32)[0]
        self.spf = struct.unpack_from('<H', d, 22)[0]
        self.fat = d[self.res * self.bps:(self.res + self.spf) * self.bps]
        self.root = (self.res + self.nf * self.spf) * self.bps
        self.data = self.root + self.nroot * 32
        ncl = (ts - self.data // self.bps) // self.spc
        self.f12 = ncl < 4085

    def nxt(self, c):
        if self.f12:
            v = struct.unpack_from('<H', self.fat, c * 3 // 2)[0]
            return v >> 4 if c & 1 else v & 0xfff
        return struct.unpack_from('<H', self.fat, c * 2)[0]

    def kette(self, c, n=None):
        out = b''; ende = 0xff8 if self.f12 else 0xfff8; cs = self.bps * self.spc
        while 2 <= c < ende:
            o = self.data + (c - 2) * cs; out += self.d[o:o + cs]; c = self.nxt(c)
        return out if n is None else out[:n]

    def eintraege(self, raw):
        for i in range(0, len(raw), 32):
            e = raw[i:i + 32]
            if not e or e[0] == 0:
                break
            if e[0] == 0xe5 or e[11] == 0x0f or e[11] & 8:
                continue
            name = e[0:8].decode('latin1').rstrip() + ('.' + e[8:11].decode('latin1').rstrip() if e[8:11].strip() else '')
            yield name, e[11], struct.unpack_from('<H', e, 26)[0], struct.unpack_from('<I', e, 28)[0]

    def alle(self, raw=None, pfad=''):
        raw = raw if raw is not None else self.d[self.root:self.data]
        for name, attr, cl, n in self.eintraege(raw):
            if name in ('.', '..'):
                continue
            if attr & 0x10:
                yield from self.alle(self.kette(cl), pfad + name + '/')
            else:
                yield pfad + name, cl, n


def main():
    cmd, bild = sys.argv[1], sys.argv[2]; f = FAT(bild)
    if cmd == 'list':
        for p, cl, n in f.alle():
            print(f'{n:>8}  {p}')
    else:
        ziel = sys.argv[3]; muster = sys.argv[4] if len(sys.argv) > 4 else '*'
        for p, cl, n in f.alle():
            if fnmatch.fnmatch(p.upper(), muster.upper()):
                q = os.path.join(ziel, p); os.makedirs(os.path.dirname(q) or '.', exist_ok=True)
                open(q, 'wb').write(f.kette(cl, n)); print('entpackt', p)


if __name__ == '__main__':
    main()
