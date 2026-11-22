#!/usr/bin/env python3
"""omf_inl.py - Hilfscode-Segment INL_TEXT aus einem Watcom-OBJ entfernen (Länge 0, Byte-Ausrichtung, ohne Daten).

Warum: Einige Hilfsfunktionen stehen im Original nur eingebettet im Aufrufer (Watcom -oe). Watcom gibt eine statische
Funktion trotz Einbettung zusätzlich als eigene Funktion aus. ail_modul legt diese Kopie per
#pragma code_seg("INL_TEXT") in ein eigenes Segment; hier wird es geleert, damit es im Programm keinen Platz belegt.
Sicherheitsprüfungen: kein Fixup zielt auf INL_TEXT (sonst würde die Kopie noch gebraucht), keine THREAD-Unterdatensätze
in den gestrichenen FIXUPP-Sätzen. Sonst Abbruch mit Fehler, das OBJ bleibt unverändert.
Aufruf: python3 Werkzeuge/omf_inl.py EIN.OBJ AUS.OBJ"""
import struct, sys


def saetze(d):
    i = 0
    while i < len(d):
        t = d[i]; l = struct.unpack_from('<H', d, i + 1)[0]
        yield t, d[i:i + 3 + l]
        i += 3 + l


def idx(c, j):
    if c[j] & 0x80:
        return ((c[j] & 0x7f) << 8) | c[j + 1], j + 2
    return c[j], j + 1


def pruefsumme(rec):
    body = rec[:-1]
    return body + bytes([(-sum(body)) & 0xff])


def fixup_ziele(c, rec32):
    """Ziel-Segmentindizes aller FIXUP-Unterdatensätze (nur explizite Ziele) und ob THREADs vorkommen."""
    j = 0; ziele = []; threads = False
    while j < len(c):
        b = c[j]
        if not (b & 0x80):                         # THREAD
            threads = True
            meth = (b >> 2) & 7; j += 1
            if meth < 4:
                _, j = idx(c, j)
            continue
        j += 2                                     # locat
        fd = c[j]; j += 1
        f_thread = fd & 0x80; frame = (fd >> 4) & 7
        t_thread = fd & 0x08; tgt = fd & 3; p = (fd >> 2) & 1
        if not f_thread and frame < 3:
            _, j = idx(c, j)
        if not t_thread:
            ti, j = idx(c, j)
            if tgt == 0:
                ziele.append(ti)
        if not p:
            j += 4 if rec32 else 2
    return ziele, threads


def entfernen(d, segname='INL_TEXT'):
    lnames = ['']; segs = [None]; inl = None
    for t, rec in saetze(d):
        c = rec[3:-1]
        if t == 0x96:
            j = 0
            while j < len(c):
                n = c[j]; lnames.append(c[j + 1:j + 1 + n].decode('latin1')); j += 1 + n
        elif t in (0x98, 0x99):
            a = c[0] >> 5; j = 1 + (3 if a == 0 else 0) + (4 if t == 0x99 else 2)
            ni, _ = idx(c, j); segs.append(lnames[ni])
            if lnames[ni] == segname:
                inl = len(segs) - 1
    if inl is None:
        return d, 'kein ' + segname
    out = []; segnr = 0; weg_daten = False; n_weg = 0
    for t, rec in saetze(d):
        c = rec[3:-1]
        if t in (0x98, 0x99):
            segnr += 1
            if segnr == inl:
                a = c[0] >> 5; j = 1 + (3 if a == 0 else 0)
                nc = bytes([(c[0] & 0x1f) | (1 << 5)]) + c[1:j] + (b'\0\0\0\0' if t == 0x99 else b'\0\0') + c[j + (4 if t == 0x99 else 2):]
                rec = pruefsumme(rec[:3] + nc + b'\0')
            out.append(rec); weg_daten = False; continue
        if t in (0xa0, 0xa1, 0xa2, 0xa3):            # LEDATA/LIDATA
            si, _ = idx(c, 0)
            weg_daten = (si == inl)
            if weg_daten:
                n_weg += 1; continue
            out.append(rec); continue
        if t in (0x9c, 0x9d):
            ziele, threads = fixup_ziele(c, t == 0x9d)
            if weg_daten:
                if threads:
                    raise ValueError('THREAD in gestrichenem FIXUPP')
                continue
            if inl in ziele:
                raise ValueError(f'Fixup zielt auf {segname}: Kopie wird noch gebraucht')
            out.append(rec); continue
        weg_daten = False
        out.append(rec)
    return b''.join(out), f'{segname} geleert ({n_weg} Datensätze)'


def leer_byte(d, segname='_TEXT', ausr=1):
    """Leeres Segment (Länge 0) auf Byte-Ausrichtung setzen. Für die AIL-Datenmodule (ail_daten.py): .MODEL FLAT legt dort
    ein leeres _TEXT mit DWORD-Ausrichtung an, das im Code Füllbytes erzeugt, die es im Original nicht gibt (dort lagen
    diese Daten in den AIL-Modulen selbst). Nicht leere Segmente bleiben unverändert (Fehler)."""
    lnames = ['']; out = []; n = 0
    for t, rec in saetze(d):
        c = rec[3:-1]
        if t == 0x96:
            j = 0
            while j < len(c):
                k = c[j]; lnames.append(c[j + 1:j + 1 + k].decode('latin1')); j += 1 + k
        elif t in (0x98, 0x99):
            a = c[0] >> 5; j = 1 + (3 if a == 0 else 0); w = 4 if t == 0x99 else 2
            ni, _ = idx(c, j + w)
            if lnames[ni] == segname:
                if any(c[j:j + w]) or (c[0] & 0x02):
                    raise ValueError(f'{segname} ist nicht leer')
                rec = pruefsumme(rec[:3] + bytes([(c[0] & 0x1f) | (ausr << 5)]) + c[1:] + b'\0'); n += 1
        out.append(rec)
    return b''.join(out), f'{segname}: {n} leere Segmente auf ' + {1: 'Byte', 3: 'PARA'}.get(ausr, str(ausr)) + '-Ausrichtung'


# Füllbefehle, mit denen Watcom innerhalb einer Übersetzungseinheit bis zur nächsten 16-Byte-Grenze auffüllt (-ot)
WATCOM_FUELL = {5: bytes.fromhex('8d40008bc9')}


def auffuellen(d, segname='_TEXT', grenze=16):
    """_TEXT am Ende mit Watcoms Füllbefehlen bis zur nächsten Grenze verlängern. Für Abschnitte, die im Original in
    derselben Übersetzungseinheit wie der folgende Code lagen (0xaefd0/0xb24b0): dort füllte der Compiler, im Bau ist
    die Einheit getrennt und der Linker füllt mit Nullen. Unbekannte Fülllänge: Fehler."""
    lnames = ['']; segs = [None]; ziel = None; laenge = None
    for t, rec in saetze(d):
        c = rec[3:-1]
        if t == 0x96:
            j = 0
            while j < len(c):
                k = c[j]; lnames.append(c[j + 1:j + 1 + k].decode('latin1')); j += 1 + k
        elif t in (0x98, 0x99):
            a = c[0] >> 5; j = 1 + (3 if a == 0 else 0); w = 4 if t == 0x99 else 2
            ni, _ = idx(c, j + w); segs.append(lnames[ni])
            if lnames[ni] == segname:
                ziel = len(segs) - 1; laenge = int.from_bytes(c[j:j + w], 'little')
    if ziel is None:
        raise ValueError('kein ' + segname)
    n = (-laenge) % grenze
    if n == 0:
        return d, f'{segname} schon ausgerichtet'
    if n not in WATCOM_FUELL:
        raise ValueError(f'Fülllänge {n} unbekannt')
    out = []; segnr = 0
    for t, rec in saetze(d):
        c = rec[3:-1]
        if t in (0x98, 0x99):
            segnr += 1
            if segnr == ziel:
                if t != 0x99:
                    raise ValueError('16-Bit-SEGDEF')
                a = c[0] >> 5; j = 1 + (3 if a == 0 else 0)
                rec = pruefsumme(rec[:3] + c[:j] + (laenge + n).to_bytes(4, 'little') + c[j + 4:] + b'\0')
        if t in (0x8a, 0x8b):                                  # MODEND: Fülldaten davor
            si = bytes([ziel]) if ziel < 0x80 else bytes([0x80 | (ziel >> 8), ziel & 0xff])
            body = si + laenge.to_bytes(4, 'little') + WATCOM_FUELL[n]
            out.append(pruefsumme(bytes([0xa1]) + (len(body) + 1).to_bytes(2, 'little') + body + b'\0'))
        out.append(rec)
    return b''.join(out), f'{segname} um {n} B Watcom-Füllung auf {laenge + n} verlängert'


if __name__ == '__main__':
    if sys.argv[1] in ('--leer-byte', '--leer-para'):                  # omf_inl.py --leer-byte DATEI.OBJ [SEGMENT]  (an Ort und Stelle)
        d = open(sys.argv[2], 'rb').read()
        neu, ber = leer_byte(d, sys.argv[3] if len(sys.argv) > 3 else '_TEXT', 3 if sys.argv[1] == '--leer-para' else 1)
        open(sys.argv[2], 'wb').write(neu)
        print(sys.argv[2].split('/')[-1], ber); sys.exit(0)
    d = open(sys.argv[1], 'rb').read()
    neu, ber = entfernen(d)
    open(sys.argv[2], 'wb').write(neu)
    print(ber)
