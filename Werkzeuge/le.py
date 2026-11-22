#!/usr/bin/env python3
"""le.py - LE-Executable (DOS/4GW) lesen: Objekte, Seiten, Fixups. Nur lesend.

Fixups werden als Liste (quellobjekt, quelloffset, typ, zielobjekt, zieloffset) geliefert.
typ: 7 = 32-Bit-Offset (absolut), 8 = 32-Bit relativ (call/jmp rel32), 2/3/5/6 = Selektor/16 Bit/48 Bit.
Aufruf: python3 Werkzeuge/le.py [EXE]   -> Übersicht
"""
import struct, sys, os, collections


class LE:
    def __init__(self, pfad):
        d = self.d = open(pfad, 'rb').read()
        self.L = L = struct.unpack_from('<I', d, 0x3c)[0]
        assert d[L:L + 2] == b'LE', 'kein LE'
        u = lambda o: struct.unpack_from('<I', d, L + o)[0]
        self.pgsz, self.lastpg, self.npages = u(0x28), u(0x2c), u(0x14)
        self.datapages = u(0x80)
        ot, nobj = L + u(0x40), u(0x44)
        self.objs = []
        for k in range(nobj):
            vs, base, fl, pti, pc, _ = struct.unpack_from('<6I', d, ot + 24 * k)
            self.objs.append({'nr': k + 1, 'groesse': vs, 'basis': base, 'flags': fl, 'seite': pti, 'seiten': pc})
        self.fpt = L + u(0x68)      # fixup page table
        self.frt = L + u(0x6c)      # fixup record table

    def seite_von(self, obj, off):
        o = self.objs[obj - 1]
        return o['seite'] + off // self.pgsz

    def objbytes(self, nr):
        o = self.objs[nr - 1]; out = b''
        for p in range(o['seite'] - 1, o['seite'] - 1 + o['seiten']):
            n = self.lastpg if p == self.npages - 1 else self.pgsz
            out += self.d[self.datapages + p * self.pgsz:self.datapages + p * self.pgsz + n]
        return out[:o['groesse']] + b'\0' * max(0, o['groesse'] - len(out))

    def fixups(self):
        d = self.d; out = []
        for o in self.objs:
            for i in range(o['seiten']):
                pg = o['seite'] + i                       # 1-basiert
                a = struct.unpack_from('<I', d, self.fpt + 4 * (pg - 1))[0]
                b = struct.unpack_from('<I', d, self.fpt + 4 * pg)[0]
                j = self.frt + a; e = self.frt + b
                while j < e:
                    src, flg = d[j], d[j + 1]; j += 2
                    if src & 0x20:
                        cnt = d[j]; j += 1
                        offs = None
                    else:
                        cnt = 1
                        offs = [struct.unpack_from('<h', d, j)[0]]; j += 2
                    ziel = flg & 3
                    if ziel != 0:
                        raise ValueError(f'Fixup-Zieltyp {ziel} (Import/Eintrag) nicht unterstützt')
                    if flg & 0x40:
                        tobj = struct.unpack_from('<H', d, j)[0]; j += 2
                    else:
                        tobj = d[j]; j += 1
                    styp = src & 0xf
                    if styp == 2:                          # nur Selektor
                        toff = 0
                    elif flg & 0x10:
                        toff = struct.unpack_from('<I', d, j)[0]; j += 4
                    else:
                        toff = struct.unpack_from('<H', d, j)[0]; j += 2
                    if offs is None:
                        offs = list(struct.unpack_from('<%dh' % cnt, d, j)); j += 2 * cnt
                    for so in offs:
                        out.append((o['nr'], i * self.pgsz + so, styp, tobj, toff))
        return out


def main():
    exe = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Original', 'MAIN.EXE')
    le = LE(exe)
    for o in le.objs:
        print(f"Objekt {o['nr']}: Basis {o['basis']:#x}, {o['groesse']} B, Flags {o['flags']:#x}")
    F = le.fixups()
    c = collections.Counter((s, t, ty) for s, _, ty, t, _ in F)
    print(len(F), 'Fixups'); [print(' ', k, v) for k, v in sorted(c.items())]


if __name__ == '__main__':
    main()
