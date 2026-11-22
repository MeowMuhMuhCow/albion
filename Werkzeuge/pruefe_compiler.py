#!/usr/bin/env python3
"""pruefe_compiler.py - prueft, ob in Compiler/ Watcom 10.0a und MASM liegen, und vergleicht mit MAIN.EXE.

Aufruf (aus dem Projektordner Q 007 Albion):  python3 Werkzeuge/pruefe_compiler.py
Ergebnis: Konsole + logs/compiler_pruefung.log. Entpackt aus ISOs/ZIPs nach Compiler/_entpackt/<name>/.
"""
import os, re, sys, subprocess, zipfile, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CDIR = os.path.join(ROOT, 'Compiler')
OUT = os.path.join(CDIR, '_entpackt')
LOG = os.path.join(ROOT, 'logs', 'compiler_pruefung.log')
ISO = os.path.join(ROOT, 'Werkzeuge', 'byte-exact-decomp-toolkit', '01_werkzeugkette', 'iso.py')
WANT = ['wcc386.exe', 'wlink.exe', 'wlib.exe', 'clib3r.lib', 'math3r.lib', 'math387r.lib', 'stdio.h', 'ml.exe']
lines = []

def say(s=''):
    print(s); lines.append(s)

def strings(path, pat):
    try:
        d = open(path, 'rb').read()
    except OSError:
        return []
    return sorted({m.decode('latin1') for m in re.findall(rb'[ -~]{6,}', d) if re.search(pat, m, re.I)})

say(f'== Compiler-Pruefung {datetime.datetime.now().isoformat(timespec="seconds")}')
os.makedirs(OUT, exist_ok=True)
for fn in sorted(os.listdir(CDIR)):
    p = os.path.join(CDIR, fn)
    base = os.path.splitext(fn)[0]
    if fn.lower().endswith('.iso'):
        say(f'ISO: {fn}')
        ls = subprocess.run([sys.executable, ISO, p, 'ls'], capture_output=True, text=True).stdout.splitlines()
        hits = [l for l in ls if os.path.basename(l.strip().split()[-1] if l.strip() else '').lower() in WANT]
        say(f'  {len(ls)} Eintraege, davon gesuchte Dateien: {len(hits)}')
        for h in hits[:20]: say('   ' + h.strip())
        dst = os.path.join(OUT, base)
        if not os.path.isdir(dst):
            subprocess.run([sys.executable, ISO, p, 'x', dst, 'binw', 'lib386', '/h/', 'binnt', 'bin/'], capture_output=True)
    elif fn.lower().endswith('.zip'):
        say(f'ZIP: {fn}')
        dst = os.path.join(OUT, base)
        if not os.path.isdir(dst):
            zipfile.ZipFile(p).extractall(dst)

found = {}
for r, _, fs in os.walk(CDIR):
    for f in fs:
        k = f.lower()
        if k in WANT:
            found.setdefault(k, []).append(os.path.join(r, f))
say('\nGefundene Dateien:')
for k in WANT:
    say(f'  {k:13s} ' + (found[k][0].replace(ROOT + os.sep, '') + (f'  (+{len(found[k])-1} weitere)' if len(found[k]) > 1 else '') if k in found else 'FEHLT'))

main = os.path.join(ROOT, 'Original', 'MAIN.EXE')
rt_main = strings(main, rb'C/C\+\+32 Run-Time system')
say('\nMAIN.EXE Runtime:  ' + (rt_main[0] if rt_main else '?'))
for p in found.get('clib3r.lib', []):
    rt = strings(p, rb'C/C\+\+32 Run-Time system')
    ok = any(x.lstrip('vx') in m for x in rt for m in rt_main) or any(m.lstrip('vx') in x for x in rt for m in rt_main)
    say(f'CLIB3R  {p.replace(ROOT + os.sep, "")}: {rt[:1]}  -> {"PASST" if ok else "anders"}')
for p in found.get('wcc386.exe', []):
    say(f'WCC386  {p.replace(ROOT + os.sep, "")}: ' + ' | '.join(strings(p, rb'(Version|10\.[0-9]a?\b)')[:4]))
for p in found.get('ml.exe', []):
    say(f'ML      {p.replace(ROOT + os.sep, "")}: ' + ' | '.join(strings(p, rb'Macro Assembler|Version 6')[:3]))

os.makedirs(os.path.dirname(LOG), exist_ok=True)
open(LOG, 'a', encoding='utf-8').write('\n'.join(lines) + '\n\n')
say(f'\nLog: {LOG}')
