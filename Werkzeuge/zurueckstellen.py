#!/usr/bin/env python3
"""zurueckstellen.py - Luecken, die kein Agent loesen kann, in versucht.json sperren (nach Adresse, nicht ID).
Aufruf: python3 Werkzeuge/zurueckstellen.py ADRESSE[:NOTIZ] ...   (Adresse im Code, z. B. 0x61c26)"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
PROJ = os.path.dirname(HERE)
K = json.load(open(os.path.join(PROJ, 'Richter', 'karte.json'), encoding='utf-8'))
Z = json.load(open(os.path.join(PROJ, 'Richter', 'zustand.json'), encoding='utf-8'))
p = os.path.join(PROJ, 'Richter', 'versucht.json')
V = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}
for arg in sys.argv[1:]:
    adr, _, notiz = arg.partition(':'); a = int(adr, 16) - 0x10000
    for L in K['luecken']:
        if L['start'] <= a < max(L['ende'], L['start'] + 1):
            V[L['id']] = {'n': 3, 'rest': Z['luecken'].get(L['id'], {}).get('rest'), 'notiz': 'zurückgestellt: ' + (notiz or 'siehe HINWEISE')}
            print('zurückgestellt', L['id'], hex(L['start'] + 0x10000), notiz)
json.dump(V, open(p + '.neu', 'w', encoding='utf-8'), indent=1, ensure_ascii=False); os.replace(p + '.neu', p)
