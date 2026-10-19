#!/usr/bin/env python3
"""Build the committed Windows binaries from this tree on Linux, reproducibly.

    python3 tools/cross_build_windows.py            # writes the binaries into the repo root
    python3 tools/cross_build_windows.py --check    # rebuilds in a temp dir, compares with the committed files

It follows windows/build-windows-native.ps1, windows/gui/build-gui.ps1 and
windows/native-installer/build-installer.ps1 step by step (same sources, same NASM defines,
same payload layout, same embedded SHA-256 table), with two differences that make the output
reproducible, so anyone can rebuild it and get the same SHA-256:

  * the PE linker gets --no-insert-timestamp (the Windows scripts embed the link time);
  * payload.zip is written with sorted entries and a fixed timestamp (Compress-Archive uses
    the file times).

The Windows-only steps of those scripts (running sutram.exe --version, hello.exe, and
Sutram-Setup.exe --self-test) cannot run here; that is what tools/accept-windows.ps1 is for.

Outputs (repo root): win/sutram.exe, sutram.exe (same file; the historical root copy),
sutram-ide-gui.exe, Sutram-Setup.exe, Sutram-Setup.sha256, and
build/windows/cross-build.json (tool versions, inputs, output hashes).
Needs: nasm, x86_64-w64-mingw32-ld (binutils-mingw-w64) and the mingw import libraries.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LD = shutil.which('x86_64-w64-mingw32-ld') or 'x86_64-w64-mingw32-ld'
MINGW_LIB = '/usr/x86_64-w64-mingw32/lib'
ZIP_TIME = (2026, 1, 1, 0, 0, 0)
OUTPUTS = ('win/sutram.exe', 'sutram.exe', 'sutram-ide-gui.exe', 'Sutram-Setup.exe', 'Sutram-Setup.sha256')


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd: list[str], cwd: Path) -> None:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f'FAILED: {" ".join(cmd)}\n{r.stdout}{r.stderr}')


def icon_include(ico_path: Path, incbin: str) -> str:
    """Port of Write-IconResourceInclude in windows/build-common.ps1 (same text, line for line)."""
    ico = ico_path.read_bytes()
    if len(ico) < 6 or struct.unpack_from('<H', ico, 0)[0] != 0 or struct.unpack_from('<H', ico, 2)[0] != 1:
        raise SystemExit(f'Not an ICO file: {ico_path}')
    count = struct.unpack_from('<H', ico, 4)[0]
    if not 1 <= count <= 32:
        raise SystemExit(f'Unexpected icon image count: {count}')
    L = [f'; generated from {incbin} by windows/build-common.ps1; do not edit',
         'section .rsrc rdata align=8', 'rsrc_root:', '    dd 0,0', '    dw 0,0,0,2',
         '    dd 3,(rsrc_icons-rsrc_root)|0x80000000', '    dd 14,(rsrc_group-rsrc_root)|0x80000000',
         'rsrc_icons:', '    dd 0,0', f'    dw 0,0,0,{count}']
    L += [f'    dd {i},(rsrc_icon_lang_{i}-rsrc_root)|0x80000000' for i in range(1, count + 1)]
    for i in range(1, count + 1):
        L += [f'rsrc_icon_lang_{i}:', '    dd 0,0', '    dw 0,0,0,1', f'    dd 0x0409,(rsrc_icon_data_{i}-rsrc_root)']
    L += ['rsrc_group:', '    dd 0,0', '    dw 0,0,0,1', '    dd 1,(rsrc_group_lang-rsrc_root)|0x80000000',
          'rsrc_group_lang:', '    dd 0,0', '    dw 0,0,0,1', '    dd 0x0409,(rsrc_group_data-rsrc_root)']
    for i in range(1, count + 1):
        e = 6 + 16 * (i - 1)
        size = struct.unpack_from('<I', ico, e + 8)[0]
        L += [f'rsrc_icon_data_{i}:', f'    dd rsrc_icon_bytes_{i} wrt ..imagebase,{size},0,0']
    L += ['rsrc_group_data:', '    dd rsrc_group_bytes wrt ..imagebase,rsrc_group_end-rsrc_group_bytes,0,0',
          'rsrc_group_bytes:', f'    dw 0,1,{count}']
    for i in range(1, count + 1):
        e = 6 + 16 * (i - 1)
        w, h, colors = ico[e], ico[e + 1], ico[e + 2]
        planes, bpp = struct.unpack_from('<HH', ico, e + 4)
        size = struct.unpack_from('<I', ico, e + 8)[0]
        L += [f'    db {w},{h},{colors},0', f'    dw {planes},{bpp}', f'    dd {size}', f'    dw {i}']
    L.append('rsrc_group_end:')
    for i in range(1, count + 1):
        e = 6 + 16 * (i - 1)
        size, off = struct.unpack_from('<II', ico, e + 8)
        if off + size > len(ico):
            raise SystemExit(f'Icon entry {i} exceeds the file')
        L += ['    align 8', f'rsrc_icon_bytes_{i}:', f'    incbin "{incbin}",{off},{size}']
    # WriteAllLines on Windows ends every line with CRLF
    return '\r\n'.join(L) + '\r\n'


def deterministic_zip(src: Path, dest: Path) -> None:
    files = sorted(p for p in src.rglob('*') if p.is_file())
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in files:
            info = zipfile.ZipInfo(p.relative_to(src).as_posix(), ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())


def build(out_root: Path) -> dict:
    work = out_root / 'build' / 'windows' / 'cross'
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    (out_root / 'win').mkdir(exist_ok=True)
    inc = str(ROOT) + '/'
    # 1. compiler: windows/build-windows-native.ps1
    run(['nasm', '-f', 'win64', '-dWINDOWS', '-I' + inc, 'src/r68_compiler_entry.asm', '-o', str(work / 'sutram.obj')], ROOT)
    run([LD, '-mi386pep', '--no-insert-timestamp', '--entry=_start', '-o', str(out_root / 'win/sutram.exe'), str(work / 'sutram.obj')], ROOT)
    shutil.copyfile(out_root / 'win/sutram.exe', out_root / 'sutram.exe')
    # 2. IDE: windows/gui/build-gui.ps1
    (work / 'r73_icon.inc').write_bytes(icon_include(ROOT / 'icons/sutram.ico', 'icons/sutram.ico').encode())
    objs = []
    for src in ('r67_gui_entry.asm', 'r66_indic_clusters.asm', 'r67_cluster_count.asm'):
        obj = work / (Path(src).stem + '.obj')
        run(['nasm', '-f', 'win64', '-dR73_ICON', '-I' + inc, '-I' + str(work) + '/', 'windows/gui/' + src, '-o', str(obj)], ROOT)
        objs.append(str(obj))
    run([LD, '-mi386pep', '--no-insert-timestamp', '--subsystem', 'windows', '--entry=_start', '-o',
         str(out_root / 'sutram-ide-gui.exe')] + objs + ['-L' + MINGW_LIB, '-lkernel32', '-lshell32', '-luser32', '-lgdi32'], ROOT)
    # 3. installer: windows/native-installer/build-installer.ps1
    stage = work / 'payload'
    for d in ('bin', 'win', 'assets'):
        (stage / d).mkdir(parents=True)
    for src, dst in (('win/sutram.exe', 'bin/sutram.exe'), ('win/sutram.exe', 'win/sutram.exe'),
                     ('sutram-ide-gui.exe', 'sutram-ide-gui.exe'), ('icons/sutram.ico', 'assets/sutram.ico'),
                     ('LICENSE.txt', 'LICENSE.txt'), ('README.md', 'README.md')):
        base = out_root if src.endswith('.exe') else ROOT
        shutil.copyfile(base / src, stage / dst)
    tracked = set(subprocess.run(['git', 'ls-files', 'lang', 'lib', 'examples', 'docs'], cwd=ROOT,
                                 capture_output=True, text=True).stdout.split())
    for folder in ('lang', 'lib', 'examples', 'docs'):
        for rel in sorted(t for t in tracked if t.startswith(folder + '/')):
            for dest in [Path(rel)] + ([Path(d) / rel for d in ('bin', 'win')] if folder in ('lib', 'lang') else []):
                (stage / dest).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, stage / dest)
    rows = sorted((p.relative_to(stage).as_posix().replace('/', '\\'), sha256(p)) for p in stage.rglob('*') if p.is_file())
    (stage / 'payload.manifest.sha256').write_bytes(''.join(f'{h} *{r}\r\n' for r, h in rows).encode())
    deterministic_zip(stage, work / 'payload.zip')
    for f in ('install-core.ps1', 'uninstall-core.ps1'):
        shutil.copyfile(ROOT / 'windows/native-installer' / f, work / f)
    shutil.copyfile(ROOT / 'LICENSE.txt', work / 'LICENSE.txt')
    lines = ['section .data']
    for f, n in (('payload.zip', 'payload'), ('install-core.ps1', 'install'), ('uninstall-core.ps1', 'uninst'), ('LICENSE.txt', 'license')):
        h = sha256(work / f).upper()
        lines.append(f'hash_{n}: db ' + ','.join('0x' + h[i:i + 2] for i in range(0, 64, 2)))
    lines.append('embedded_hash_table:')
    lines += [f'dq blob_{n},blob_{n}_end-blob_{n},hash_{n}' for n in ('payload', 'install', 'uninst', 'license')]
    lines.append('dq 0,0,0')
    (work / 'embedded_hashes.inc').write_bytes(('\r\n'.join(lines) + '\r\n').encode())
    run(['nasm', '-f', 'win64', '-dR73_ICON', '-I' + str(work) + '/', '-I' + inc,
         'windows/native-installer/sutram_wizard.asm', '-o', str(work / 'wizard.obj')], ROOT)
    run([LD, '-mi386pep', '--no-insert-timestamp', '--subsystem', 'windows', '--entry=_start', '-o',
         str(out_root / 'Sutram-Setup.exe'), str(work / 'wizard.obj'), '-L' + MINGW_LIB, '-lkernel32', '-lbcrypt'], ROOT)
    (out_root / 'Sutram-Setup.sha256').write_text(sha256(out_root / 'Sutram-Setup.exe') + ' *Sutram-Setup.exe\n', encoding='ascii')
    tool = lambda c: subprocess.run(c, capture_output=True, text=True).stdout.splitlines()[0]
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(['git', 'status', '--porcelain', '--', 'src', 'windows', 'win', 'lib', 'lang', 'icons'],
                                cwd=ROOT, capture_output=True, text=True).stdout.strip())
    report = {
        'tool': 'tools/cross_build_windows.py', 'git_commit': head, 'source_dirty': dirty,
        'nasm': tool(['nasm', '-v']), 'ld': tool([LD, '-v']),
        'outputs': {o: sha256(out_root / o) for o in OUTPUTS if o != 'Sutram-Setup.sha256'},
        'payload_zip_sha256': sha256(work / 'payload.zip'), 'payload_files': len(rows),
        'not_run_here': ['sutram.exe --version', 'hello.exe', 'Sutram-Setup.exe --self-test',
                         'everything in tools/accept-windows.ps1'],
    }
    (out_root / 'build' / 'windows' / 'cross-build.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--check', action='store_true', help='rebuild in a temp dir and compare with the committed files')
    a = ap.parse_args(argv)
    if not a.check:
        r = build(ROOT)
        for o, h in r['outputs'].items():
            print(f'{h}  {o}')
        return 0
    with tempfile.TemporaryDirectory() as t:
        r = build(Path(t))
        bad = 0
        for o, h in r['outputs'].items():
            here = sha256(ROOT / o) if (ROOT / o).is_file() else None
            state = 'MATCH' if here == h else f'DIFFERS (committed {here})'
            bad += here != h
            print(f'{h}  {o}  {state}')
        print('REPRODUCED' if not bad else f'NOT REPRODUCED: {bad} file(s) differ')
        return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
