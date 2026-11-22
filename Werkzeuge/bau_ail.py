#!/usr/bin/env python3
"""bau_ail.py - Gesamtbau Schritt 3: AIL-C als OBJ-Dateien (Bau/AIL/), ein OBJ je Modul aus ail_modul.MODULE und
eines je übrigem Abschnitt (Krümel 0x88b83 usw.). Strings: D_-Verweise werden durch die echten Literale ersetzt
(ail_strings), damit CONST im OBJ steckt. Je Modul werden die Flagsätze probiert; genommen wird der mit den meisten
bytegleichen Abschnitten (bei MODUL_FLAGS zuerst der dort eingetragene). Bericht: Bau/ail.txt
Aufruf: python3 Werkzeuge/bau_ail.py"""
import os, re, sys, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ail_modul as M  # noqa: E402
import ail_strings as S  # noqa: E402
R = M.R; A = M.A
ZIEL = os.path.join(A.PROJ, 'Bau', 'AIL')
# 0xaefd0 und 0xb24b0 waren im Original eine Einheit; b24b0 steht getrennt (ruft F_af150 statt es einzubetten), darum
# fehlt am Ende von aefd0 Watcoms Füllung vor der 16-Byte-Grenze (8d 40 00 8b c9 bei 0xb24ab)
FUELLEN = {'0xaefd0'}
STRING_NAMEN = {'digits': 0x133b00}                    # A9B04: "0123456789ABCDEF"[j]


def modul(blk, zeilen):
    Mo = M.zusammensetzen(blk, laut=False)
    text = open(Mo['datei'], 'rb').read().decode('latin1')
    text = S.ersetze_strings(text, S.const_bereich(text))
    # Umdeute-Makros für Variablen, die eben durch ihr Literal ersetzt wurden (#define "SAMPLE" ...), fallen weg
    text = re.sub(r'(?m)^#\s*(?:define|undef)\s+"[^\r\n]*\r?\n', '', text)
    # Namen, unter denen Agenten String-Literale des Originals ansprechen (Literal steht im CONST des Moduls)
    for nm_, adr_ in STRING_NAMEN.items():
        if re.search(r'\b' + nm_ + r'\b', text):
            lit, _ = S.cstr(adr_)
            text = re.sub(r'extern\s+(?:const\s+)?char\s+' + nm_ + r'\s*\[\s*\]\s*;', '', text)
            text = re.sub(r'\b' + nm_ + r'\b', lit, text)
    p = Mo['datei'].replace('.C', '_BAU.C'); open(p, 'wb').write(text.encode('latin1')); Mo['datei'] = p
    versuche = []
    erst = M.MODUL_FLAGS.get(blk)
    for fl in ([list(erst)] if erst else []) + [f for f in R.FLAGSAETZE if list(f) != list(erst or [])]:
        cfg = {'src': 'AIL/REKO/MOD_' + blk[2:].upper() + '.C', 'flags': list(fl), 'inc': R.INC}
        r = A.kompiliere('AILMOD', cfg, p, mit_obj=True)
        if r.get('fehler'):
            versuche.append((-1, fl, None, r['fehler'].splitlines()[-1][:120] if r['fehler'] else '')); continue
        E = M.abschnitte_messen(Mo, r)
        n = sum(z['bytegleich'] for z in E['zeilen'])
        versuche.append((n, fl, r.get('obj'), f"{n}/{len(E['zeilen'])} bytegleich, Länge {len(E['dd'])}/{len(Mo['orig'])}"))
        if n == len(E['zeilen']):
            break
    best = max(versuche, key=lambda v: v[0])
    for v in versuche:
        zeilen.append(f"  {blk} {' '.join(v[1]):22} {v[3]}")
    # Platzhalter-Strings der Agenten durch die Originaltexte ersetzen (ail_literale), mit dem besten Flagsatz neu
    if best[2]:
        try:
            import ail_literale as L
            text2, ber = L.korrigieren(text, best[2])
        except Exception as e:
            text2, ber = text, [f'Literale: Fehler {e}']
        zeilen += ['  ' + l for l in ber]
        if text2 != text:
            p2 = Mo['datei'].replace('_BAU.C', '_LIT.C'); open(p2, 'wb').write(text2.encode('latin1'))
            cfg = {'src': 'AIL/REKO/MOD_' + blk[2:].upper() + '.C', 'flags': list(best[1]), 'inc': R.INC}
            r = A.kompiliere('AILMOD', cfg, p2, mit_obj=True)
            if not r.get('fehler'):
                Mo2 = dict(Mo); Mo2['datei'] = p2
                E = M.abschnitte_messen(Mo2, r)
                n = sum(z['bytegleich'] for z in E['zeilen'])
                zeilen.append(f"  {blk} mit Originaltexten: {n}/{len(E['zeilen'])} bytegleich, Länge {len(E['dd'])}/{len(Mo['orig'])}")
                if n >= best[0]:
                    best = (n, best[1], r.get('obj'), f"{n}/{len(E['zeilen'])} bytegleich, Länge {len(E['dd'])}/{len(Mo['orig'])}, Originaltexte")
            else:
                zeilen.append(f"  {blk} mit Originaltexten: FEHLER {r['fehler'].splitlines()[-1][:100]}")
    if best[2]:
        ziel_ = os.path.join(ZIEL, 'M' + blk[2:].upper() + '.OBJ')
        shutil.copyfile(best[2], ziel_)
        import omf_inl                              # eingebettete Hilfen: zusätzliche Kopie (INL_TEXT) aus dem OBJ
        neu_, ber_ = omf_inl.entfernen(open(ziel_, 'rb').read())
        if not ber_.startswith('kein'):
            open(ziel_, 'wb').write(neu_); zeilen.append(f'  {blk}: {ber_}')
        if blk in FUELLEN:                          # Krücke: Compiler-Füllung am Ende der abgetrennten Einheit
            neu_, ber_ = omf_inl.auffuellen(open(ziel_, 'rb').read())
            open(ziel_, 'wb').write(neu_); zeilen.append(f'  {blk}: {ber_}')
        zeilen.append(f"  -> {blk}: {' '.join(best[1])} ({best[3]})")
    return best


def einzeln(adr, zeilen):
    f = R.funktionen()[adr]; z = A.jload(R.ZUST, {}).get(adr, {})
    p = os.path.join(R.REKO, R.name_von(adr).upper() + '.C')
    fl = z.get('flags') or (f.get('flagsaetze') or [['-s']])[0]
    r = A.kompiliere('AILREKO', {'src': 'AIL/REKO/' + os.path.basename(p), 'flags': list(fl), 'inc': f.get('inc') or R.INC}, p, mit_obj=True)
    if r.get('fehler') or not r.get('obj'):
        zeilen.append(f'  {adr}: FEHLER'); return
    shutil.copyfile(r['obj'], os.path.join(ZIEL, 'K' + adr[2:].upper() + '.OBJ'))
    zeilen.append(f"  {adr}: {' '.join(fl)} -> K{adr[2:].upper()}.OBJ")


def main():
    os.makedirs(ZIEL, exist_ok=True)
    folge = json.load(open(os.path.join(A.PROJ, 'Bau', 'reihenfolge.json')))
    zeilen = []
    gemacht = set()
    for z in folge:
        if z['art'] == 'AILMOD' or (z['art'] == 'AILREKO' and M.modul_von(z['name'])):
            blk = z['name'] if z['art'] == 'AILMOD' else M.modul_von(z['name'])
            if blk not in gemacht:
                gemacht.add(blk); modul(blk, zeilen)
        elif z['art'] == 'AILREKO':
            einzeln(z['name'], zeilen)
    open(os.path.join(A.PROJ, 'Bau', 'ail.txt'), 'w').write('\n'.join(zeilen) + '\n')
    print('\n'.join(l for l in zeilen if l.startswith('  ->') or 'FEHLER' in l or 'Literale' in l or 'Originaltexten' in l))


if __name__ == '__main__':
    main()
