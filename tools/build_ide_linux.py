#!/usr/bin/env python3
"""tools/build_ide_linux.py - R131: build sutram-ide-gui.exe on Linux, as windows/gui/build-gui.ps1 does on Windows.

The same steps: the icon resource include (build-common.ps1's Write-IconResourceInclude, the port in
tools/build_installer_linux.py), nasm -f win64 -dR73_ICON for r67_gui_entry.asm, r66_indic_clusters.asm and
r67_cluster_count.asm, then ld -mi386pep --subsystem windows --entry=_start with kernel32, shell32, user32, gdi32
(mingw's import libraries here). Usage: python3 tools/build_ide_linux.py [--out PATH] [--work DIR]
Rendering and interaction still require the Windows desktop acceptance test.
"""
import argparse, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from build_installer_linux import icon_include, assert_pe64  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(ROOT, 'sutram-ide-gui.exe'))
    ap.add_argument('--work')
    a = ap.parse_args()
    work = a.work or tempfile.mkdtemp(prefix='sutram-ide-')
    os.makedirs(work, exist_ok=True)
    icon_include(os.path.join(ROOT, 'icons', 'sutram.ico'), os.path.join(work, 'r73_icon.inc'), 'icons/sutram.ico')
    objs = []
    for src in ('r67_gui_entry.asm', 'r66_indic_clusters.asm', 'r67_cluster_count.asm'):
        obj = os.path.join(work, src[:-4] + '.obj')
        r = subprocess.run(['nasm', '-f', 'win64', '-dR73_ICON', f'-I{ROOT}/', f'-I{work}/', 'windows/gui/' + src, '-o', obj],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit('IDE FAIL nasm ' + src + ': ' + (r.stdout + r.stderr)[-800:])
        objs.append(obj)
    r = subprocess.run(['x86_64-w64-mingw32-ld', '-mi386pep', '--subsystem', 'windows', '--entry=_start', '-o', a.out] + objs +
                       ['-L/usr/x86_64-w64-mingw32/lib', '-lkernel32', '-lshell32', '-luser32', '-lgdi32'],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('IDE FAIL ld: ' + (r.stdout + r.stderr)[-800:])
    assert_pe64(a.out)
    print(f'IDE PASS: built {a.out} ({os.path.getsize(a.out)} bytes). Rendering and interaction still need the Windows desktop test.')


if __name__ == '__main__':
    main()
