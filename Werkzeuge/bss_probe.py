#!/usr/bin/env python3
"""bss_probe.py - Lage der _BSS-Variablen einer Einheit unter Quellvarianten messen.
Watcom ordnet _BSS nicht nach der Reihenfolge im Quelltext, sondern über die Namen (Hash-artig); auch
unbenutzte Variablen verschieben alles. Hier werden Varianten der Quelle mit den Flags der Einheit übersetzt
und die PUBDEF-Offsets im _BSS des Moduls mit dem Original verglichen (ZIEL: Name -> Offset im Modul-_BSS,
aus daten_lage/Fixup-Zielen abgeleitet).
Aufruf: python3 Werkzeuge/bss_probe.py [EINHEIT ...]   Ergebnis: Analyse/bss_probe.txt"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import albion as A  # noqa: E402


def idx(L, t):
    return next(i for i, z in enumerate(L) if t in z)


def leer(L, t):
    i = idx(L, t); L[i] = b'\r' if L[i].endswith(b'\r') else b''
    return L


def setze(L, t, neu):
    i = idx(L, t); L[i] = neu + (b'\r' if L[i].endswith(b'\r') else b'')
    return L


def verschiebe(L, t, ziel, danach=False):   # Zeile t vor (oder nach) Zeile ziel; Zeilenzahl bleibt
    i = idx(L, t); z = L[i].rstrip(b'\r'); leer(L, t)
    j = idx(L, ziel) + (1 if danach else 0)
    L.insert(j, z + b'\r')
    k = next(k for k in range(j + 1, len(L)) if L[k].strip() == b'')
    del L[k]
    return L


def an_zeile(L, t, z):     # Zeile t vor Zeile Nr. z (1-basiert) einsetzen, alte Stelle leer, Zeilenzahl bleibt
    i = idx(L, t); zz = L[i].rstrip(b'\r'); leer(L, t)
    L.insert(z - 1, zz + b'\r'); del L[i + 1 if i + 1 > z - 1 else i]
    return L


def umbenennen(L, alt, neu):
    r = re.compile(rb'\b' + alt + rb'\b')
    return [r.sub(neu, z) for z in L]


GDP = b'static UNCHAR DOS_getcurrentdir_path[_MAX_PATH];'
NAMEN_GDP = ['DOS_GetCurrentDir_path', 'getcurrentdir_path', 'currentdir_path', 'DOS_currentdir_path', 'DOS_path',
             'path', 'cwd_path', 'DOS_cwd', 'DOS_getcurrentdir_buffer', 'getcurrentdir_buffer', 'DOS_CurrentDir',
             'DOS_currentdir', 'currentdir', 'curdir', 'DOS_curdir', 'BBDOS_currentdir', 'BBDOS_CurrentDirPath',
             'DOS_getcurrentdirpath', 'DOS_GetCurrentDirPath', 'DOS_getcurrentdir_str', 'pathbuffer', 'DOS_pathbuffer',
             'dirpath', 'DOS_dirpath', 'act_path', 'DOS_Path', 'DOS_PATH', 'getcwd_path', 'DOS_getcwd_path', 'DOS_actpath']
def block(L, a, b):        # Zeilen a..b (1-basiert, inkl.)
    return L[a - 1:b]


NAMEN_DEMO = ['Demo_flags', 'Demo_flag', 'Demo_mode', 'Demo_version', 'Demo', 'Demo_game', 'Demo_mode_flag', 'Is_demo',
              'Demo_version_flag', 'Albion_demo', 'DEMO_flag', 'Demo_on', 'Game_flags', 'Version_flags', 'Special_flags',
              'Program_flags', 'Albion_flags', 'Debug_flags', 'Mode_flags', 'Options', 'Game_options', 'Program_options',
              'Demo_status', 'Demo_active', 'Demo_switch', 'Demo_type', 'Game_mode', 'Program_mode', 'Albion_mode',
              'Version_type', 'Demo_nr', 'Demo_level', 'Restricted', 'Restricted_flag', 'Demo_restrictions',
              'Albion_version_flags', 'System_flags', 'Global_flags', 'Main_flags', 'Init_flags']
PROBEN_D0 = {u: ({}, [('D0 Quelle', lambda L: L)]) for u in ('XLOAD', 'BBEVENT', 'BBDSA', 'BBDOS', 'BBSYSTEM', 'BBERROR', 'BBBASMEM')}
XL = [b'XLD_ERROR_T XLD_Last_error;', b'static const UNCHAR *Library_ID = "XLD0";', b'static BOOLEAN XLD_Library_open = FALSE;',
      b'static BOOLEAN XLD_Batch_mode = FALSE;', b'static BOOLEAN XLD_Full_batch_mode = FALSE;', b'static SISHORT XLD_Library_ID;',
      b'static struct XLD_Library XLD_Library;', b'static UNLONG XLD_Subfile_lengths[MAX_SUBFILES];',
      b'static UNLONG XLD_Subfile_length;', b'static UNLONG XLD_Subfile_offset;', b'static UNLONG XLD_Batch_offset;',
      b'static struct Batch_load_data Batch_data_buffer[MAX_SUBFILES_PER_BATCH];']
PROBEN = {
    'BBSYSTEM': ({'_anker': 'intr_stack', 'save_int_regs': 0x1254, 'prev_int_09': 0x125a, 'prev_int_08': 0x1260, 'intmouse': 0x1266,
                  'inMouseInterrupt': 0x1268, 'msy': 0x126a, 'mouseevent': 0x1000, 'ticks': 0x11c8, 'regs': 0x11ac, 'sregs': 0x11d0}, [
        ('S0 Quelle (prev_int_9/8)', lambda L: L),
        ('S1 alte Namen prev_int_09/08', lambda L: umbenennen(umbenennen(L, b'prev_int_9', b'prev_int_09'), b'prev_int_8', b'prev_int_08'))]),
    'XLOAD': ({'XLD_Batch_data': 0, 'XLD_Library': 0x7d0, 'XLD_Subfile_lengths': 0x7d8, 'XLD_Batch_offset': 0x968,
               'XLD_Subfile_length': 0x96c, 'XLD_Subfile_offset': 0x970, 'XLD_Library_ID': 0x974, 'XLD_Last_error': 0x976},
              [('X0', lambda L: umbenennen(L, b'Batch_data_buffer', b'XLD_Batch_data'))]
              + [(f'N {n}', (lambda n: lambda L: umbenennen(umbenennen(L, b'Batch_data_buffer', b'XLD_Batch_data'), b'XLD_Batch_offset', n))(n)) for n in
                 [b'XLD_Batch_ofs', b'XLD_Batch_off', b'XLD_BatchOffset', b'XLD_batch_offset', b'XLD_Batch_Offset', b'XLD_Batch_file_offset', b'XLD_Batch_base', b'XLD_Batch_start_offset', b'XLD_Batch_seek', b'XLD_Batch_pointer', b'XLD_Batch_ptr', b'XLD_Batch_location', b'XLD_Batch_index', b'XLD_Current_offset', b'XLD_Batch_offs', b'XLD_Batch_adr', b'XLD_Batch_address', b'XLD_Batch_length_offset', b'XLD_Batch_Offs', b'XLD_Batch_pos_offset', b'Batch_ofs', b'XLD_First_offset', b'XLD_Start_offset', b'XLD_Batch_begin', b'XLD_Batch_first', b'XLD_Batch_offset2', b'XLD_BOffset', b'XLD_Batchoffset', b'XLD_Batch_off_set', b'XLD_Library_offset']
              ]),
    # GAME _BSS relativ zu _Screen (Original: Forbidden_Y nach Forbidden_X)
    'GAME': ({'_anker': 'Screen', 'Earth_object': 0xa0, 'Quit_program_flag': 0xa2, 'Screen_width': 0xa4, 'Forbidden_X': 0xa6,
              'Forbidden_Y': 0xa8, 'Screen_height': 0xaa, 'Loading_game': 0xac, 'Cheat_mode': 0xb0,
              'Restart_game_flag': 0xb2, 'Game_over_flag': 0xb4, 'Diagnostic_mode': 0xb6, 'Panel_Y': 0xb8}, [
        (f'N {n}', (lambda n: lambda L: [b'#define Demo_flags ' + n.encode() + b'\r'] + L)(n)) for n in NAMEN_DEMO] + [('ohne Definition', lambda L: [b'#define Demo_flags Load_game_nr\r'] + leer(L, b'UNSHORT Demo_flags = 0;')), ('ohne alles (Header-Zeile bleibt)', lambda L: leer(L, b'UNSHORT Demo_flags = 0;')), ('ohne Prototyp Init_saved', lambda L: leer(L, b'BOOLEAN Init_saved_XLD_library_check(void);'))] + [(f'+{k} extern-Attrappen', (lambda k: lambda L: [b''.join(b'extern int Probe_dummy%d;' % i for i in range(k)) + b'\r'] + L)(k)) for k in (1, 2, 3, 4, 8)] + [(f'+{k} Attrappen nach Includes', (lambda k: lambda L: setze(L, b'UNSHORT Demo_flags = 0;', b'UNSHORT Demo_flags = 0;' + b''.join(b'extern int Probe_dummy%d;' % i for i in range(k))))(k)) for k in (1, 2, 3)]),
    # BBDSA: im Original chain4lastreadselect vor chain4lastwriteselect (DSA_ASS: 0x152014/0x152015)
    'BBDSA': ({'_anker': 'chain4savereadselect', 'chain4savewriteselect': 1, 'chain4lastreadselect': 2, 'chain4lastwriteselect': 3,
               'chain4readselectok': 4, 'chain4writeselectok': 5}, [
        ('B0 Quelle', lambda L: L),
        ('B1 Zeilen getauscht', lambda L: verschiebe(L, b'UNBYTE chain4lastreadselect;', b'UNBYTE chain4lastwriteselect;')),
        ('B2 write ans Ende', lambda L: verschiebe(L, b'UNBYTE chain4lastwriteselect;', b'UNBYTE chain4readselectok;', danach=True))]
      + [(f'+{k} extern-Attrappen', (lambda k: lambda L: [b''.join(b'extern int Probe_dummy%d;' % i for i in range(k)) + b'\r'] + L)(k)) for k in (1, 2, 3, 4, 5, 6)]
      + [(f'E {n.decode()}', (lambda n: lambda L: setze(L, b'UNBYTE chain4lastwriteselect;', n + b' UNBYTE chain4lastwriteselect;'))(n)) for n in
         (b'void DSA_ASS_SaveCHAIN4Page(void);', b'extern void DSA_ASS_RestoreCHAIN4Page(void);', b'extern UNBYTE chain4select;', b'extern UNBYTE chain4lastselect;')]
      + [(f'+{k} Attrappen vor chain4', (lambda k: lambda L: setze(L, b'UNBYTE chain4lastwriteselect;', b''.join(b'extern int Probe_dummy%d;' % i for i in range(k)) + b'UNBYTE chain4lastwriteselect;'))(k)) for k in (1, 2, 3)]),
    # Original: statisches DOS_getcurrentdir_path (0x90) liegt VOR BBDOS_filenames (0x17f100 / 0x17f190)
    'BBDOS': ({'BBDOS_filenames': 0x90, 'BBDOS_FileHandleArray': 0x1990, 'errorfilenames': 0x1a58}, [
        ('D0 Quelle', lambda L: L),
        ('D2 nicht static', lambda L: setze(L, GDP, b'UNCHAR DOS_getcurrentdir_path[_MAX_PATH];')),
        ('D3 static in Funktion', lambda L: verschiebe(L, GDP, b'char *cwd;', danach=True)),
        ('D7 -bt=dos', ['-bt=dos']), ('D8 -bt=dos + static nach oben', ['-bt=dos', 'oben'])]),
}


def bss(obj):
    return sorted((o, n.lstrip('_')) for sg, o, n in A.pubs(obj) if sg == '_BSS')


def main():
    E = A.einheiten(); zeilen = []
    for unit in (sys.argv[1:] or list(PROBEN)):
        ziel, varianten = PROBEN.get(unit) or PROBEN_D0[unit]
        cfg = E[unit]; src = os.path.join(A.SRC, cfg['src'])
        text = open(src, 'rb').read()
        wd = os.path.join(A.PROJ, 'Bau', 'probe'); os.makedirs(wd, exist_ok=True)
        zeilen.append(f'##### {unit}  Ziel: ' + ' '.join(f'{n}@{o:#x}' if n != '_anker' else f'(rel. {o})' for n, o in ziel.items()))
        for name, f in varianten:
            p = os.path.join(wd, os.path.basename(src))
            cfg_ = cfg
            if f is None:
                cfg_ = dict(cfg, flags=[x for x in cfg['flags'] if x != '-d2']); f = lambda L: L
            elif isinstance(f, list):
                extra = [x for x in f if x.startswith('-')]
                cfg_ = dict(cfg, flags=cfg['flags'] + extra)
                f = (lambda L: verschiebe(L, GDP, b'/* Global variables */')) if 'oben' in f else (lambda L: L)
            try:
                open(p, 'wb').write(b'\n'.join(f(text.split(b'\n'))))
            except StopIteration:
                zeilen.append(f'{name}: Zeile nicht gefunden'); continue
            r = A.kompiliere(unit, cfg_, datei=p, mit_obj=True)
            if r.get('fehler') or not r.get('obj'):
                zeilen.append(f'{name}: FEHLER {str(r.get("fehler"))[-300:]}'); continue
            L = bss(r['obj']); d = {n: a for a, n in L}
            a0 = d.get(ziel.get('_anker'), 0) if '_anker' in ziel else 0
            t = sum(1 for n, o in ziel.items() if n != '_anker' and d.get(n, -99) - a0 == o)
            zeilen.append(f'{name}: {t}/{len([n for n in ziel if n != "_anker"])} gleich, _BSS {r["segmente"].get("_BSS", {}).get("groesse", 0):#x} B')
            zeilen.append('    Bau: ' + ' '.join(f'{n}@{a:#x}' for a, n in L))
    open(os.path.join(A.PROJ, 'Analyse', 'bss_probe.txt'), 'w').write('\n'.join(zeilen) + '\n')
    print('\n'.join(zeilen))


if __name__ == '__main__':
    main()
