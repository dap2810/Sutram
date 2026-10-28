#!/usr/bin/env python3
"""ROUND-54: Muse's nivartanam migration of lib/ and examples/, and the expanded-source limit it needed.

  1. THE LIMIT: the expanded source (the program plus every `yoj`) may be 128 KiB (R54; it was 64 KiB).
     tests/stdlib/r11_sets_lists - six modules, about 66 KiB once lib/ says nivartanam - compiles and prints
     its expected output. A program of ~8 KB with two modules of ~59 KB each (about 126 KB in all) compiles
     and runs; with a third module (about 148 KB) it is refused with `vistarit srot seema atikram`, and
     nothing is written.
  2. DEVANAGARI: a migrated example (examples/41_recursion.sm, six returns) written with nivartanam, प्रति
     and निवर्तनम्, compiled under --lang sanskrit, gives one identical executable, which prints the
     example's expected output. The alias still works after the migration.
  3. THE COUNT: no `prati` (as a word) is left in the code of lib/*.smlib, examples/**/*.sm and
     examples/lib/*.smlib. A comment may still name it (examples/256 explains the keyword).

No network; writes only to a temporary directory.
usage: python3 -B tests/r54/test_r54.py [--compiler ./sutram_compiler]
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
WORD = re.compile(r'\bprati\b')


def pad(n: int) -> str:
    return ''.join(f'# {"x" * 76}\n' for _ in range(n // 80))


def main(argv) -> int:
    comp = argv[argv.index('--compiler') + 1] if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    comp = str(Path(comp).resolve())
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    with tempfile.TemporaryDirectory(prefix='r54-') as td:
        t = Path(td)

        def build(src: Path, out: Path, *flags):
            c = subprocess.run([comp, *flags, str(src), str(out)], capture_output=True, timeout=60, cwd=src.parent)
            return c.returncode, (c.stdout + c.stderr).decode('utf-8', 'replace')

        def run(b: Path) -> str:
            return subprocess.run([str(b)], capture_output=True, timeout=30).stdout.decode('utf-8', 'replace')

        # 1. the limit
        sm = ROOT / 'tests' / 'stdlib' / 'r11_sets_lists.sm'
        c = subprocess.run([comp, str(sm), str(t / 'r11.bin')], capture_output=True, timeout=60, cwd=ROOT)
        got = run(t / 'r11.bin') if c.returncode == 0 else None
        check(got == (ROOT / 'tests' / 'stdlib' / 'r11_sets_lists.out').read_text(encoding='utf-8'),
              'r11_sets_lists (six modules, > 64 KiB expanded) compiles and prints its expected output')
        (t / 'lib').mkdir()
        (t / 'lib' / 'm1.smlib').write_text(pad(60000) + 'prakriya ek() {\n    nivartanam 1\n}\n', encoding='utf-8')
        (t / 'lib' / 'm2.smlib').write_text(pad(60000) + 'prakriya dvi() {\n    nivartanam 2\n}\n', encoding='utf-8')
        (t / 'lib' / 'm3.smlib').write_text(pad(30000) + 'prakriya tri() {\n    nivartanam 3\n}\n', encoding='utf-8')
        (t / 'a.sm').write_text('yoj m1\nyoj m2\n' + pad(8000) + 'mukhya() {\n    likha(ek() + dvi())\n}\n',
                                encoding='utf-8')
        (t / 'b.sm').write_text('yoj m1\nyoj m2\nyoj m3\nmukhya() {\n    likha(ek() + dvi() + tri())\n}\n',
                                encoding='utf-8')
        size = sum((t / p).stat().st_size for p in ('a.sm', 'lib/m1.smlib', 'lib/m2.smlib'))
        rc, msg = build(t / 'a.sm', t / 'a.bin')
        check(rc == 0 and run(t / 'a.bin') == '3\n', f'a program and two modules, {size} bytes in all (> 64 KiB, '
              f'< 128 KiB), compiles and prints 3 (got rc={rc} {msg.strip()[-60:]!r})')
        rc, msg = build(t / 'b.sm', t / 'b.bin')
        check(rc != 0 and 'vistarit srot seema atikram' in msg and not (t / 'b.bin').exists(),
              f'with a third module (> 128 KiB) it is refused with the limit message and nothing is written '
              f'(got rc={rc} {msg.strip()[-60:]!r})')

        # 2. Devanagari: the alias still works after the migration
        src = (ROOT / 'examples' / '41_recursion.sm').read_text(encoding='utf-8')
        want = (ROOT / 'tests' / 'expect' / '41_recursion.out').read_text(encoding='utf-8')
        bins = {}
        for tag, word in (('nivartanam', 'nivartanam'), ('prati-deva', 'प्रति'), ('nivartanam-deva', 'निवर्तनम्')):
            p = t / f'{tag}.sm'
            p.write_text(src.replace('nivartanam', word), encoding='utf-8')
            rc, msg = build(p, t / f'{tag}.bin', '--lang', 'sanskrit')
            bins[tag] = (t / f'{tag}.bin').read_bytes() if rc == 0 else None
            check(rc == 0 and run(t / f'{tag}.bin') == want,
                  f'41_recursion with {word} under --lang sanskrit prints its expected output')
        check(src.count('nivartanam') == 6 and None not in bins.values() and len(set(bins.values())) == 1,
              'the three spellings give one identical executable')

    # 3. the count
    left = []
    files = sorted((ROOT / 'lib').glob('*.smlib')) + sorted((ROOT / 'examples').glob('**/*.sm')) + \
        sorted((ROOT / 'examples' / 'lib').glob('*.smlib'))
    for f in files:
        for n, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
            code = line.split('#', 1)[0]
            if WORD.search(code):
                left.append(f'{f.relative_to(ROOT)}:{n}')
    check(not left, f'no prati left in the code of {len(files)} lib/ and examples/ files (left: {left[:5]})')

    print(f'r54 nivartanam migration: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
