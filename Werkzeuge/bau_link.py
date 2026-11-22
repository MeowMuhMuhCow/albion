#!/usr/bin/env python3
"""bau_link.py - Gesamtbau Schritt 4: alle OBJs nach Bau/DOS/O/Onnn.OBJ (8.3-Namen) und Linkdatei Bau/DOS/MAIN.LNK
in der Ladefolge aus Bau/reihenfolge.json. Linker-Optionen wie im Makefile (SYSTEM DOS4G, CASEEXACT, NOREDEFS,
STACK=16K). OPTION UNDEFSOK nur für den Probebau (AIL-Variablen fehlen noch). Ablauf in DOSBox: BAU_LINK.sh
Aufruf: python3 Werkzeuge/bau_link.py [--probe]"""
import os, sys, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
B = os.path.join(PROJ, 'Bau')
ML = os.path.join(PROJ, 'Compiler', 'ML60')
ASMOBJ = {'OPM_ASS': 'V60/ASM/PCLIB32/SRC/BBOPM/OPM_ASS.OBJ', 'FNT_ASS': 'V60/ASM/PCLIB32/SRC/BBOPM/FNT_ASS.OBJ',
          'DSA_ASS': 'V60/ASM/PCLIB32/SRC/BBDSA/DSA_ASS.OBJ', 'SYS_ASS': 'V60/ASM/PCLIB32/SRC/BBSYSTEM/SYS_ASS.OBJ',
          'ZOOM': 'AIL/ZOOM.OBJ'}
ASM = {'AIL32': 'AIL/AIL32.OBJ', 'DMASND32': 'AIL/DMASND32.OBJ'}


def main():
    import ail_modul as M
    folge = json.load(open(os.path.join(B, 'reihenfolge.json')))
    od = os.path.join(B, 'DOS', 'O'); os.makedirs(od, exist_ok=True)
    liste = []; fehlt = []; gesehen = set()
    for z in folge:
        art, nm = z['art'], z['name']
        if art == 'C':
            q = os.path.join(B, 'OBJ', nm.upper() + '.OBJ')
        elif art == 'LIB':
            q = os.path.join(B, z['obj']) if z.get('obj') else None
        elif art == 'ASMOBJ':
            q = os.path.join(ML, ASMOBJ[nm])
        elif art == 'ASM':
            q = os.path.join(ML, ASM[nm])
        elif art == 'ASMDATA':
            q = os.path.join(ML, 'AIL', nm + '.OBJ')
        elif art in ('AILMOD', 'AILREKO'):
            blk = nm if art == 'AILMOD' else M.modul_von(nm)
            if blk:
                if blk in gesehen:
                    continue
                gesehen.add(blk); q = os.path.join(B, 'AIL', 'M' + blk[2:].upper() + '.OBJ')
            else:
                q = os.path.join(B, 'AIL', 'K' + nm[2:].upper() + '.OBJ')
        else:
            fehlt.append(f"{art} {nm}"); continue
        if not q or not os.path.exists(q):
            fehlt.append(f"{art} {nm} ({os.path.relpath(q, PROJ) if q else '-'})"); continue
        k = f'O{len(liste) + 1:03d}.OBJ'
        shutil.copyfile(q, os.path.join(od, k)); liste.append((k, art, nm, os.path.relpath(q, PROJ)))
        import fuellbytes                                 # Krücke: Füllbytes aus dem Original (siehe fuellbytes.py)
        ber_ = fuellbytes.fuellen(os.path.join(od, k), os.path.relpath(q, PROJ))
        if ber_:
            print(ber_)
    zeilen = ['SYSTEM DOS4G', 'OPTION CASEEXACT', 'OPTION NOREDEFS', 'OPTION STACK=16K', 'OPTION MAP=C:\\MAIN.MAP',
              'NAME C:\\MAIN.EXE']
    if '--probe' in sys.argv:
        zeilen.insert(4, 'OPTION UNDEFSOK')
    zeilen += [f'FILE C:\\O\\{k}' for k, *_ in liste]
    al = os.path.join(B, 'alias.lnk')                   # Namen der Agenten auf echte Symbole (alias_bau.py)
    if os.path.exists(al):
        zeilen += [l.strip() for l in open(al) if l.strip()]
    open(os.path.join(B, 'DOS', 'MAIN.LNK'), 'w', newline='\r\n').write('\n'.join(zeilen) + '\n')
    with open(os.path.join(B, 'link_liste.txt'), 'w') as f:
        for k, art, nm, q in liste:
            f.write(f'{k} {art:8} {nm:24} {q}\n')
        for x in fehlt:
            f.write(f'FEHLT {x}\n')
    print(f'{len(liste)} OBJs in Bau/DOS/O, Linkdatei Bau/DOS/MAIN.LNK' + (f'; fehlen {len(fehlt)}: {fehlt[:8]}' if fehlt else ''))


if __name__ == '__main__':
    main()
