#!/usr/bin/env python3
"""ROUND-39: nirmmita_gun(count, size), the checked allocation.

  1. THE VALUES: count * size bytes, writable; 0 for a negative count, a size <= 0, and every
     product past 2^63 - 1 (2^61 + 1 cells of 8 bytes wraps to 8 under a plain multiply; 2^60
     cells wraps negative; MAX * MAX); 0 for count 0 (nirmmita(0) is 0). The largest product
     that fits (2^60 - 1 cells, 9.2e18 bytes) reaches mmap, which refuses it: 0.
  2. EXPRESSIONS: count and size are any expressions, a nested nirmmita_gun included; it works
     as a statement.
  3. --fail-alloc counts it like any allocation: the Nth is 0.
  4. ARITY: one or three arguments are refused, with no output (as for every builtin).
  5. THE ORDINARY PATH: a program without nirmmita_gun compiles exactly as before - checked by
     the guard, not here. A PE (.exe) program with nirmmita_gun compiles on Linux; running it
     needs Windows (Claude-to-Sarvam/evidence-r39/ ran it under Wine).
Linux only. No network.
usage: python3 -B tests/r39/test_nirmgun.py [--compiler PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

VALUES = '''mukhya() {
    vitti a = nirmmita_gun(4, 8)
    likha(a != 0)
    a[3] = 7
    likha(a[3])
    likha(nirmmita_gun(0 - 1, 8))
    likha(nirmmita_gun(4, 0))
    likha(nirmmita_gun(4, 0 - 8))
    likha(nirmmita_gun(2305843009213693953, 8))
    likha(nirmmita_gun(1152921504606846976, 8))
    likha(nirmmita_gun(9223372036854775807, 9223372036854775807))
    likha(nirmmita_gun(0 - 9223372036854775807, 0 - 1))
    likha(nirmmita_gun(0, 8))
    likha(nirmmita_gun(1152921504606846975, 8))
}
'''
VALUES_OUT = '1\n7\n0\n0\n0\n0\n0\n0\n0\n0\n0\n'

EXPRS = '''prakriya cells(n) {
    prati n * 2
}
mukhya() {
    vitti n = 3
    vitti b = nirmmita_gun(cells(n), n + 5)
    likha(b != 0)
    b[5] = 41
    likha(b[5] + 1)
    nirmmita_gun(1, 8)
    likha(nirmmita_gun(nirmmita_gun(1, 8) != 0, 16) != 0)
}
'''
EXPRS_OUT = '1\n42\n1\n'

FAULT = '''mukhya() {
    vitti a = nirmmita(8)
    vitti b = nirmmita_gun(2, 8)
    vitti c = nirmmita_gun(2, 8)
    likha(a == 0)
    likha(b == 0)
    likha(c == 0)
}
'''


def main(argv) -> int:
    comp = os.path.abspath(argv[argv.index('--compiler') + 1]) if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    work = Path(tempfile.mkdtemp(prefix='r39-nirmgun-'))
    passed = failed = 0

    def check(ok, what):
        nonlocal passed, failed
        if ok:
            passed += 1
        else:
            failed += 1
            print('FAIL', what)

    def build(text, out, extra=()):
        src = work / 'p.sm'
        src.write_text(text, encoding='utf-8')
        out.unlink(missing_ok=True)
        r = subprocess.run([comp, *extra, str(src), str(out)], capture_output=True, cwd=ROOT, timeout=60)
        return r.returncode == 0 and out.exists(), r.stdout.decode('utf-8', 'replace')

    def run(text, extra=()):
        ok, msg = build(text, work / 'p', extra)
        if not ok:
            return None, msg
        p = subprocess.run([str(work / 'p')], capture_output=True, timeout=20)
        return p.returncode, p.stdout.decode('utf-8', 'replace')

    got = run(VALUES)
    check(got == (0, VALUES_OUT), f'values: want {VALUES_OUT!r}, got {got!r}')
    got = run(EXPRS)
    check(got == (0, EXPRS_OUT), f'expressions: want {EXPRS_OUT!r}, got {got!r}')
    for n, want in ((1, '1\n0\n0\n'), (2, '0\n1\n0\n'), (3, '0\n0\n1\n'), (4, '0\n0\n0\n')):
        got = run(FAULT, ('--fail-alloc', str(n)))
        check(got == (0, want), f'--fail-alloc {n}: want {want!r}, got {got!r}')
    for bad in ('nirmmita_gun(8)', 'nirmmita_gun(8, 1, 2)', 'nirmmita_gun()'):
        ok, msg = build(f'mukhya() {{\n    likha({bad})\n}}\n', work / 'bad')
        check(not ok and 'Sutram Error' in msg, f'{bad} must be refused with no output: {msg[:80]!r}')
    ok, msg = build(VALUES, work / 'p.exe')
    check(ok and (work / 'p.exe').read_bytes()[:2] == b'MZ', f'a PE program with nirmmita_gun compiles: {msg[:80]!r}')
    print(f'r39 nirmmita_gun: {passed + failed} checks, {passed} passed, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
