#!/usr/bin/env python3
"""ROUND-30: a module-level `vitti` in an object, and shared across separately compiled modules.

  1. SHARED STATE: in tests/r30/proj, two modules both `yoj` r30_ganak, which holds two
     vitti. Built separately, the program prints what the one-pass compile prints, and
     each vitti is defined (as the symbol "vitti:<name>") in exactly one object - its own
     module's. The root object holds only the root's own vitti.
  2. ONE COPY OF THE BYTES: a program with a module-level vitti, compiled with --object and
     linked alone, is byte-identical to the direct compile (also in tests/r28's identity).
  3. THE REFUSAL: a library object (no mukhya) compiled with plain --object refuses a vitti
     with an initializer - no mukhya of its own would run it. Without an initializer it is
     accepted.
Linux only. No network.
usage: python3 -B tests/r30/test_vitti.py [--compiler PATH] [--linker PATH]
"""
from __future__ import annotations

import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def arg(argv, flag, default):
    return os.path.abspath(argv[argv.index(flag) + 1]) if flag in argv else default


def symbols(path):
    data = open(path, 'rb').read()
    code, nsym, _ = struct.unpack_from('<3Q', data, 8)
    pos, names = 32 + code, []
    for _ in range(nsym):
        _off, ln = struct.unpack_from('<2Q', data, pos)
        names.append(data[pos + 16:pos + 16 + ln].decode())
        pos += 16 + ln
    return names


def main(argv) -> int:
    comp = arg(argv, '--compiler', str(ROOT / 'sutram_compiler'))
    link = arg(argv, '--linker', str(ROOT / 'sutram-link'))
    fails = checks = 0

    def check(ok, what):
        nonlocal fails, checks
        checks += 1
        if not ok:
            fails += 1
            print('FAIL', what)

    os.chdir(ROOT)
    t = Path(tempfile.mkdtemp(prefix='r30-'))
    # 1. shared state
    src = 'tests/r30/proj/main.sm'
    d = subprocess.run([comp, src, str(t / 'd.bin')], capture_output=True)
    b = subprocess.run([sys.executable, '-B', 'tools/sutram_build.py', '--compiler', comp, '--linker', link,
                        '--keep', str(t / 'k'), src, '-o', str(t / 's.bin')], capture_output=True)
    check(d.returncode == 0 and b.returncode == 0, f'build: {d.stdout[-120:]!r} {b.stdout[-120:]!r} {b.stderr[-120:]!r}')
    if d.returncode == 0 and b.returncode == 0:
        one = subprocess.run([str(t / 'd.bin')], capture_output=True, timeout=10)
        sep = subprocess.run([str(t / 's.bin')], capture_output=True, timeout=10)
        check(one.stdout == b'1\n11\n12\n112\n7\n' and (sep.returncode, sep.stdout) == (one.returncode, one.stdout),
              f'output {one.stdout!r} vs {sep.stdout!r}')
        defs = {}
        for o in sorted(os.listdir(t / 'k')):
            for s in symbols(t / 'k' / o):
                defs.setdefault(s, []).append(o)
        g = defs.get('vitti:ganak', [])
        check(len(g) == 1 and g[0].endswith('r30_ganak.smlib.smo'), f'vitti:ganak in one object: {g}')
        check(len(defs.get('vitti:prarambha', [])) == 1, f'vitti:prarambha in one object: {defs.get("vitti:prarambha")}')
        check(symbols(t / 'k' / '000-main.sm.smo') == ['mukhya', 'vitti:mula'],
              f'the root holds only its own vitti: {symbols(t / "k" / "000-main.sm.smo")}')
        print('shared state: 4 modules, one ganak; the separate build prints what the one-pass compile prints')
    # 2. the same bytes
    (t / 'g.sm').write_text('vitti G = 5\nmukhya() {\n    G = G * 3\n    likha(G)\n}\n')
    subprocess.run([comp, '--object', str(t / 'g.sm'), str(t / 'g.smo')], capture_output=True)
    subprocess.run([comp, str(t / 'g.sm'), str(t / 'gd.bin')], capture_output=True)
    l = subprocess.run([link, str(t / 'gl.bin'), str(t / 'g.smo')], capture_output=True)
    check(l.returncode == 0 and (t / 'gl.bin').read_bytes() == (t / 'gd.bin').read_bytes(), 'vitti: --object + link = direct')
    print('the same bytes: a program with a vitti, --object and linked alone, is the direct compile')
    # 3. the refusal
    (t / 'li.sm').write_text('vitti G = 5\nprakriya g() {\n    nivartanam G\n}\n')
    r = subprocess.run([comp, '--object', str(t / 'li.sm'), str(t / 'li.smo')], capture_output=True)
    check(r.returncode == 1 and b'vastu-patre ghatak-star vitti asamarthita' in r.stdout, f'refusal {r.stdout!r}')
    (t / 'ln.sm').write_text('vitti G\nprakriya g() {\n    nivartanam G\n}\n')
    r = subprocess.run([comp, '--object', str(t / 'ln.sm'), str(t / 'ln.smo')], capture_output=True)
    check(r.returncode == 0 and 'vitti:G' in symbols(t / 'ln.smo'), f'no initializer: accepted {r.stdout!r}')
    print('the refusal: an initialized vitti in a library object; without an initializer it is held')
    print(f'r30 vitti: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
