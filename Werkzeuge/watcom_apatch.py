#!/usr/bin/env python3
"""watcom_apatch.py - wendet das Watcom-10.0a-Patchlevel (A_LEVEL/APPLYA.BAT + PTCH*.A/.C) ohne DOS an.

Format nach Open Watcom bld/bdiff/c/dopatch.c (CMD_DIFFS=0, CMD_SAMES=1, CMD_DONE=2, CMD_HOLES=3,
CMD_ITER_HOLES=4, Pruefsumme = Bytesumme der neuen Datei, 32 Bit).

Aufruf: python3 watcom_apatch.py <WATCOM-Basisbaum 10.0> <A_LEVEL-Ordner> <Zielbaum 10.0a>
Der Basisbaum bleibt unveraendert; der Zielbaum wird als Kopie angelegt und dort gepatcht.
"""
import os, re, shutil, struct, sys

SIG_END, EOF_CHAR = 0x0d, 0x1a


def apply(old: bytes, pat: bytes):
    i = pat.index(bytes([EOF_CHAR])) + 1
    j = pat.index(b'\0', i)
    name = pat[i:j].decode('latin1'); i = j + 1
    old_size, new_size, checksum = struct.unpack_from('<3I', pat, i); i += 12
    new = bytearray(new_size)
    holes = []
    while True:
        cmd = pat[i]; i += 1
        if cmd == 2:
            break
        if cmd == 0:                                   # DIFFS: neue Bytes
            off, size = struct.unpack_from('<2I', pat, i); i += 8
            new[off:off + size] = pat[i:i + size]; i += size
        elif cmd == 1:                                 # SAMES: aus alter Datei kopieren
            off, ooff, size = struct.unpack_from('<3I', pat, i); i += 12
            new[off:off + size] = old[ooff:ooff + size]
        elif cmd == 4:                                 # ITER_HOLES
            off, diff, iters, incr = struct.unpack_from('<4I', pat, i); i += 16
            i += 1                                     # ch (unbenutzt)
            for _ in range(iters):
                holes.append((off, diff)); off += incr
        elif cmd == 3:                                 # HOLES
            off, diff = struct.unpack_from('<2I', pat, i); i += 8
            while True:
                holes.append((off, diff))
                nx = pat[i]; i += 1
                if nx == 0:
                    break
                if nx & 0x80 == 0:
                    off += nx & 0x7f
                elif nx & 0x40 == 0:
                    off += ((nx & 0x3f) << 8) + pat[i]; i += 1
                else:
                    off += ((nx & 0x3f) << 16) + (pat[i] << 8) + pat[i + 1]; i += 2
        else:
            raise ValueError(f'unbekanntes Kommando {cmd} bei {i - 1}')
    for off, diff in sorted(holes):
        v = struct.unpack_from('<I', new, off)[0]
        struct.pack_into('<I', new, off, (v + diff) & 0xFFFFFFFF)
    ok = (sum(new) & 0xFFFFFFFF) == checksum
    return name, old_size, bytes(new), checksum, ok


def main():
    base, alevel, dst = sys.argv[1:4]
    if not os.path.isdir(dst):
        shutil.copytree(base, dst)
    bat = open(os.path.join(alevel, 'APPLYA.BAT'), 'rb').read().decode('latin1')
    pairs = []
    for m in re.finditer(r'if exist %1\\(\S+) if exist (\S+) bpatch', bat, re.I):
        p = (m.group(1).replace('\\', '/'), m.group(2))
        if p not in pairs:
            pairs.append(p)
    stats = {'gepatcht': 0, 'schon_neu': 0, 'fehlt': 0, 'falsch': 0}
    log = []
    for rel, pf in pairs:
        tgt = None
        for cand in (rel, rel.upper(), rel.lower()):
            t = os.path.join(dst, cand)
            if os.path.exists(t):
                tgt = t; break
        if tgt is None:
            # Gross/Kleinschreibung pro Pfadteil aufloesen
            cur = dst
            for part in rel.split('/'):
                hit = [x for x in os.listdir(cur) if x.lower() == part.lower()] if os.path.isdir(cur) else []
                if not hit:
                    cur = None; break
                cur = os.path.join(cur, hit[0])
            tgt = cur
        pfp = os.path.join(alevel, pf.upper()) if os.path.exists(os.path.join(alevel, pf.upper())) else os.path.join(alevel, pf)
        if tgt is None or not os.path.exists(pfp):
            stats['fehlt'] += 1; continue
        old = open(tgt, 'rb').read()
        pat = open(pfp, 'rb').read()
        i = pat.index(bytes([EOF_CHAR])) + 1
        i = pat.index(b'\0', i) + 1
        old_size, new_size, chk = struct.unpack_from('<3I', pat, i)
        if len(old) != old_size:
            if len(old) == new_size and (sum(old) & 0xFFFFFFFF) == chk:
                stats['schon_neu'] += 1; continue
            stats['falsch'] += 1; log.append(f'GROESSE {rel} ({pf}): {len(old)} != {old_size}'); continue
        try:
            name, old_size, new, chk, ok = apply(old, pat)
        except Exception as e:
            stats['falsch'] += 1; log.append(f'FEHLER {rel} ({pf}): {e}'); continue
        if not ok:
            stats['falsch'] += 1; log.append(f'PRUEFSUMME {rel} ({pf})'); continue
        open(tgt, 'wb').write(new)
        stats['gepatcht'] += 1
        log.append(f'ok {rel} <- {pf}')
    print(stats)
    for l in log:
        if not l.startswith('ok'):
            print(l)
    open(os.path.join(dst, 'APATCH.LOG'), 'w').write('\n'.join(log) + '\n' + repr(stats) + '\n')


if __name__ == '__main__':
    main()
