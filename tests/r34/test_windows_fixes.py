#!/usr/bin/env python3
"""ROUND-34: regressions for the defects the real Windows run found.

  1. MANY RUNTIME CALLS: every call a Windows program makes into its runtime (each likha, each
     read, each allocation) was recorded in a 256-entry table with no bound check; a program
     with more overran it and the compiler crashed (a 200-likha program: exit 139, a broken
     .exe). Programs with 100, 200 and 250 likha, and the object of the 250 one, must compile;
     on Windows they also run and print every line. On Linux the same code path is reached by
     compiling to a .exe (the Linux compiler writes a PE for that name), so this runs there too.
  2. THE OBJECT OF IT: --object of the 250-likha program (Windows: SUTRAMO2) links and runs.
No network. Writes only to a temporary directory.
usage: python -B tests/r34/test_windows_fixes.py [--compiler PATH] [--linker PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
WIN = os.name == 'nt'


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def main(argv) -> int:
    comp = arg(argv, '--compiler', str(ROOT / ('sutram.exe' if WIN else 'sutram_compiler')))
    link = arg(argv, '--linker', str(ROOT / ('sutram-link.exe' if WIN else 'sutram-link')))
    fails = checks = 0

    def check(ok, what):
        nonlocal fails, checks
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    with tempfile.TemporaryDirectory(prefix='r34f-') as td:
        t = Path(td)
        for n in (100, 200, 250):
            src = t / f'p{n}.sm'
            src.write_text('mukhya() {\n' + ''.join(f'    likha({i})\n' for i in range(n)) + '}\n', newline='\n')
            exe = t / f'p{n}.exe'
            r = subprocess.run([comp, str(src), str(exe)], capture_output=True, timeout=120)
            ok = r.returncode == 0 and exe.exists() and exe.read_bytes()[:2] == b'MZ'
            if ok and WIN:
                p = subprocess.run([str(exe)], capture_output=True, timeout=20)
                ok = p.returncode == 0 and p.stdout.replace(b'\r\n', b'\n') == ''.join(f'{i}\n' for i in range(n)).encode()
            check(ok, f'{n} likha: compiles to a PE (exit {r.returncode})' + (' and prints all of them' if WIN else ''))
        if WIN:
            o = subprocess.run([comp, '--object', str(t / 'p250.sm'), str(t / 'p250.smo')], capture_output=True, timeout=120)
            ok = o.returncode == 0 and (t / 'p250.smo').read_bytes()[:8] == b'SUTRAMO2'
            if ok:
                l = subprocess.run([link, str(t / 'l250.exe'), str(t / 'p250.smo')], capture_output=True, timeout=60)
                ok = l.returncode == 0 and (t / 'l250.exe').read_bytes() == (t / 'p250.exe').read_bytes()
            check(ok, '250 likha through --object + sutram-link: byte-identical to the direct compile')
    print('r34 windows fixes: %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
