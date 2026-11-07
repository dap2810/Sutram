#!/usr/bin/env python3
"""tools/build_installer_linux.py - R128: build Sutram-Setup.exe on Linux, step for step as
windows/native-installer/build-installer.ps1 does on Windows.

The PowerShell script is the reference; this is its port, so the installer's payload can be brought to the
compiler's version without a Windows machine (docs/INSTALLER-REBUILD.md). The same steps, in the same order:

  1. stage the payload: win/sutram.exe as bin/ and win/, sutram-link.exe, sutram-ide-gui.exe, the icon,
     LICENSE.txt, README.md; lang/ lib/ examples/ docs/; lang/ and lib/ again under bin/ and win/;
  2. payload.manifest.sha256 - "<sha256> *<path>" for every staged file, paths with backslashes, as
     Get-ChildItem's FullName gives them on Windows (install-core.ps1's Verify-Payload checks every line);
  3. payload.zip - deflate, entry names with backslashes, as Windows PowerShell 5.1's Compress-Archive
     writes them (the v243 payload has them; Expand-Archive takes them);
  4. embedded_hashes.inc - the SHA-256 of payload.zip, install-core.ps1, uninstall-core.ps1, LICENSE.txt;
  5. r73_icon.inc - the icon as a PE resource (build-common.ps1's Write-IconResourceInclude, ported);
  6. nasm -f win64 -dR73_ICON sutram_wizard.asm; ld -mi386pep --subsystem windows (kernel32, bcrypt);
  7. Sutram-Setup.exe --self-test (under Wine 64 here), then Sutram-Setup.sha256 = "<sha256> *Sutram-Setup.exe".

Both builders normalise declared UTF-8 text payloads to LF before hashing. Payload file bytes and
manifest order/newlines are platform-independent. ZIP metadata/compression and the linked wizard may
still differ: ZIP times are the files' modification times; the link uses platform import libraries.
Usage: python3 tools/build_installer_linux.py [--work DIR] [--wine PATH]   (from the repo root)
Last line: "SETUP PASS ..." or "SETUP FAIL ...".
"""
import argparse
import hashlib
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NI = os.path.join(ROOT, 'windows', 'native-installer')


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def normalize_payload_text(path):
    """Match build-installer.ps1; preserve every byte outside declared text files."""
    if os.path.splitext(path)[1].lower() in {'.md', '.html', '.txt', '.out', '.exit'}:
        with open(path, 'rb') as f:
            raw = f.read()
        raw.decode('utf-8', errors='strict')
        if b'\r\n' in raw:
            with open(path, 'wb') as f:
                f.write(raw.replace(b'\r\n', b'\n'))


def assert_pe64(path):
    b = open(path, 'rb').read()
    if len(b) < 512 or b[:2] != b'MZ':
        raise SystemExit(f'SETUP FAIL not an MZ executable: {path}')
    pe = struct.unpack_from('<i', b, 60)[0]
    if b[pe:pe + 4] != b'PE\0\0' or struct.unpack_from('<H', b, pe + 4)[0] != 0x8664 \
            or struct.unpack_from('<H', b, pe + 24)[0] != 0x20B:
        raise SystemExit(f'SETUP FAIL not a PE32+ AMD64 executable: {path}')


def icon_include(ico_path, out_path, incbin_path):
    ico = open(ico_path, 'rb').read()
    if len(ico) < 6 or struct.unpack_from('<H', ico, 0)[0] != 0 or struct.unpack_from('<H', ico, 2)[0] != 1:
        raise SystemExit(f'SETUP FAIL not an ICO file: {ico_path}')
    count = struct.unpack_from('<H', ico, 4)[0]
    if not 1 <= count <= 32:
        raise SystemExit(f'SETUP FAIL unexpected icon image count: {count}')
    inc = [f'; generated from {incbin_path} by windows/build-common.ps1; do not edit',
           'section .rsrc rdata align=8', 'rsrc_root:', '    dd 0,0', '    dw 0,0,0,2',
           '    dd 3,(rsrc_icons-rsrc_root)|0x80000000', '    dd 14,(rsrc_group-rsrc_root)|0x80000000',
           'rsrc_icons:', '    dd 0,0', f'    dw 0,0,0,{count}']
    inc += [f'    dd {i},(rsrc_icon_lang_{i}-rsrc_root)|0x80000000' for i in range(1, count + 1)]
    for i in range(1, count + 1):
        inc += [f'rsrc_icon_lang_{i}:', '    dd 0,0', '    dw 0,0,0,1', f'    dd 0x0409,(rsrc_icon_data_{i}-rsrc_root)']
    inc += ['rsrc_group:', '    dd 0,0', '    dw 0,0,0,1', '    dd 1,(rsrc_group_lang-rsrc_root)|0x80000000',
            'rsrc_group_lang:', '    dd 0,0', '    dw 0,0,0,1', '    dd 0x0409,(rsrc_group_data-rsrc_root)']
    for i in range(1, count + 1):
        e = 6 + 16 * (i - 1)
        size = struct.unpack_from('<I', ico, e + 8)[0]
        inc += [f'rsrc_icon_data_{i}:', f'    dd rsrc_icon_bytes_{i} wrt ..imagebase,{size},0,0']
    inc += ['rsrc_group_data:', '    dd rsrc_group_bytes wrt ..imagebase,rsrc_group_end-rsrc_group_bytes,0,0',
            'rsrc_group_bytes:', f'    dw 0,1,{count}']
    for i in range(1, count + 1):
        e = 6 + 16 * (i - 1)
        w, h, colors = ico[e], ico[e + 1], ico[e + 2]
        planes, bpp = struct.unpack_from('<HH', ico, e + 4)
        size = struct.unpack_from('<I', ico, e + 8)[0]
        inc += [f'    db {w},{h},{colors},0', f'    dw {planes},{bpp}', f'    dd {size}', f'    dw {i}']
    inc.append('rsrc_group_end:')
    for i in range(1, count + 1):
        e = 6 + 16 * (i - 1)
        size, off = struct.unpack_from('<II', ico, e + 8)
        if off + size > len(ico):
            raise SystemExit(f'SETUP FAIL icon entry {i} exceeds the file')
        inc += ['    align 8', f'rsrc_icon_bytes_{i}:', f'    incbin "{incbin_path}",{off},{size}']
    open(out_path, 'w', encoding='utf-8', newline='\r\n').write('\n'.join(inc) + '\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work')
    ap.add_argument('--wine', default='/usr/lib/wine/wine64')
    ap.add_argument('--payload-only', action='store_true', help='build and verify payload inputs without linking a wizard')
    a = ap.parse_args()
    work = a.work or tempfile.mkdtemp(prefix='sutram-setup-')
    stage = os.path.join(work, 'payload')
    if os.path.exists(stage):
        raise SystemExit(f'SETUP FAIL {stage} exists; give an empty --work')
    for d in ('bin', 'win', 'assets'):
        os.makedirs(os.path.join(stage, d))
    for src, dst in (('win/sutram.exe', 'bin/sutram.exe'), ('win/sutram.exe', 'win/sutram.exe'),
                     ('sutram-link.exe', 'bin/sutram-link.exe'), ('sutram-ide-gui.exe', 'sutram-ide-gui.exe'),
                     ('icons/sutram.ico', 'assets/sutram.ico'), ('LICENSE.txt', 'LICENSE.txt'), ('README.md', 'README.md')):
        s = os.path.join(ROOT, src)
        if not os.path.isfile(s):
            raise SystemExit(f'SETUP FAIL missing payload input: {s}')
        if s.endswith('.exe'):
            assert_pe64(s)
        shutil.copy2(s, os.path.join(stage, dst))
    for folder in ('lang', 'lib', 'examples', 'docs'):
        shutil.copytree(os.path.join(ROOT, folder), os.path.join(stage, folder), ignore=shutil.ignore_patterns('__pycache__'))
    for dest in ('bin', 'win'):
        for folder in ('lib', 'lang'):
            shutil.copytree(os.path.join(ROOT, folder), os.path.join(stage, dest, folder), dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('__pycache__'))
    files = []
    for dp, _, fs in os.walk(stage):
        for f in fs:
            normalize_payload_text(os.path.join(dp, f))
            files.append(os.path.relpath(os.path.join(dp, f), stage))
    files.sort(key=lambda r: r.replace('/', '\\').lower())
    rows = [f'{sha(os.path.join(stage, r))} *{r.replace("/", chr(92))}' for r in files]
    open(os.path.join(stage, 'payload.manifest.sha256'), 'w', encoding='utf-8', newline='\r\n').write('\n'.join(rows) + '\n')
    files.append('payload.manifest.sha256')
    zpath = os.path.join(work, 'payload.zip')
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for r in sorted(files, key=lambda r: r.replace('/', '\\').lower()):
            z.write(os.path.join(stage, r), r.replace('/', '\\'))
    if a.payload_only:
        print(f'PAYLOAD PASS: {len(files) - 1} files; manifest {sha(os.path.join(stage, "payload.manifest.sha256"))}; {zpath}')
        return
    for f in ('install-core.ps1', 'uninstall-core.ps1'):
        shutil.copy2(os.path.join(NI, f), work)
    shutil.copy2(os.path.join(ROOT, 'LICENSE.txt'), work)
    lines = ['section .data']
    for f, name in (('payload.zip', 'payload'), ('install-core.ps1', 'install'), ('uninstall-core.ps1', 'uninst'),
                    ('LICENSE.txt', 'license')):
        h = sha(os.path.join(work, f)).upper()
        lines.append(f'hash_{name}: db ' + ','.join('0x' + h[i:i + 2] for i in range(0, 64, 2)))
    lines.append('embedded_hash_table:')
    lines += [f'dq blob_{n},blob_{n}_end-blob_{n},hash_{n}' for n in ('payload', 'install', 'uninst', 'license')]
    lines.append('dq 0,0,0')
    open(os.path.join(work, 'embedded_hashes.inc'), 'w', encoding='utf-8', newline='\r\n').write('\n'.join(lines) + '\n')
    icon_include(os.path.join(ROOT, 'icons', 'sutram.ico'), os.path.join(work, 'r73_icon.inc'), 'icons/sutram.ico')
    obj = os.path.join(work, 'wizard.obj')
    r = subprocess.run(['nasm', '-f', 'win64', '-dR73_ICON', f'-I{work}/', f'-I{ROOT}/', os.path.join(NI, 'sutram_wizard.asm'),
                        '-o', obj], cwd=work, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('SETUP FAIL nasm: ' + (r.stdout + r.stderr)[-600:])
    out = os.path.join(ROOT, 'Sutram-Setup.exe')
    r = subprocess.run(['x86_64-w64-mingw32-ld', '-mi386pep', '--subsystem', 'windows', '--entry=_start', '-o', out, obj,
                        '-L/usr/x86_64-w64-mingw32/lib', '-lkernel32', '-lbcrypt'], cwd=work, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('SETUP FAIL ld: ' + (r.stdout + r.stderr)[-600:])
    assert_pe64(out)
    b = open(out, 'rb').read()
    pe = struct.unpack_from('<i', b, 60)[0]
    rva, size = struct.unpack_from('<II', b, pe + 24 + 112 + 16)
    if rva == 0 or size < 64:
        raise SystemExit(f'SETUP FAIL no resource directory in {out}; the icon resource was not linked')
    print(f'Installer icon: resource directory RVA {rva}, {size} bytes')
    if os.path.exists(a.wine):
        st = subprocess.run([a.wine, out, '--self-test'], cwd=work, capture_output=True, timeout=300,
                            env=dict(os.environ, WINEDEBUG='-all'))
        print(f'self-test (Wine 64): exit {st.returncode} {(st.stdout + st.stderr).decode("latin-1").strip()[:300]}')
        if st.returncode:
            raise SystemExit('SETUP FAIL --self-test')
    else:
        print('NOT RUN self-test: no Wine here')
    h = sha(out)
    open(os.path.join(ROOT, 'Sutram-Setup.sha256'), 'w', encoding='ascii', newline='\n').write(f'{h} *Sutram-Setup.exe\n')
    print(f'payload: {len(files)} files, {os.path.getsize(zpath)} bytes zipped; Sutram-Setup.exe {len(b)} bytes, sha256 {h}')
    print(f'SETUP PASS: built {out}; staging kept at {work}')


if __name__ == '__main__':
    main()
