#!/usr/bin/env python3
"""ROUND-25: the error type - siddhi, dosh, prasar - the rules and the edges.

The working program is examples/249_r25_phal.sm (golden in tests/expect, run by
the suite). This pins each rule: a failure propagates through every level, a
phal-prakriya must be called under prasar, prasar only on such a call and only
in a phal-prakriya or mukhya, every prati in one is siddhi or dosh, the end of
one is siddhi(0), and in mukhya a failure is the exit status.

Runs the Linux compiler. No network.
usage: python3 -B tests/r25/test_phal.py [--compiler PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

F = 'prakriya f(a) {\n    yadi (a) {\n        prati dosh(3)\n    }\n    prati siddhi(a + 1)\n}\n'
# (name, source, expect): ('out', text, exit) or ('compile-fail', text)
CASES = [
    ('success and failure through three levels',
     'prakriya bhaj(a, b) {\n    yadi (b == 0) {\n        prati dosh(7)\n    }\n    prati siddhi(a / b)\n}\n'
     'prakriya ek(a, b) {\n    vitti q = prasar bhaj(a, b)\n    prati siddhi(q + 1)\n}\n'
     'prakriya dvi(a, b, c) {\n    vitti x = prasar ek(a, b)\n    vitti y = prasar ek(x, c)\n    prati siddhi(x * 100 + y)\n}\n'
     'mukhya() {\n    likha(prasar dvi(20, 2, 3))\n    likha(prasar dvi(20, 0, 3))\n    likha(999)\n}\n',
     ('out', '1104\n', 7)),
    ('a failure stops a later step: the deeper call is not made',
     'prakriya g(a) {\n    likha(a)\n    prati siddhi(a)\n}\n'
     'prakriya h(a) {\n    yadi (a > 1) {\n        prati dosh(4)\n    }\n    vitti x = prasar g(a)\n    prati siddhi(x)\n}\n'
     'mukhya() {\n    likha(prasar h(1))\n    likha(prasar h(2))\n}\n',
     ('out', '1\n1\n', 4)),
    ('recursion', 'prakriya gin(n) {\n    yadi (n == 0) {\n        prati siddhi(0)\n    }\n    vitti r = prasar gin(n - 1)\n    prati siddhi(r + n)\n}\n'
     'mukhya() {\n    likha(prasar gin(10))\n}\n', ('out', '55\n', 0)),
    ('a method that is a phal-prakriya',
     'rachana B = { x }\nprakriya B.ghata(swa, d) {\n    yadi (swa.x < d) {\n        prati dosh(swa.x)\n    }\n'
     '    swa.x = swa.x - d\n    prati siddhi(swa.x)\n}\n'
     'mukhya() {\n    vitti b = nirmmita(8)\n    b.x = 10\n    likha(prasar b.ghata(4))\n    likha(prasar b.ghata(7))\n}\n',
     ('out', '6\n', 6)),
    ('the end of a phal-prakriya is siddhi(0)',
     'prakriya z(a) {\n    yadi (a) {\n        prati dosh(9)\n    }\n}\nmukhya() {\n    likha(prasar z(0))\n    likha(prasar z(1))\n}\n',
     ('out', '0\n', 9)),
    ('prati dosh(c) in mukhya exits with c',
     'mukhya() {\n    likha(1)\n    prati dosh(42)\n}\n', ('out', '1\n', 42)),
    ('prasar inside an argument of a prasar call',
     F + 'mukhya() {\n    likha(prasar f(prasar f(0) - 1))\n}\n', ('out', '1\n', 0)),
    ('a call without prasar', F + 'mukhya() {\n    likha(f(0))\n}\n',
     ('compile-fail', 'Sutram Error: phal-prakriya prasar vina ahuta')),
    ('a statement call without prasar', F + 'mukhya() {\n    f(0)\n}\n',
     ('compile-fail', 'Sutram Error: phal-prakriya prasar vina ahuta')),
    ('a call inside prasar\'s arguments without prasar', F + 'mukhya() {\n    likha(prasar f(f(0)))\n}\n',
     ('compile-fail', 'Sutram Error: phal-prakriya prasar vina ahuta')),
    ('prasar on a plain prakriya', 'prakriya g(a) {\n    prati a\n}\nmukhya() {\n    likha(prasar g(1))\n}\n',
     ('compile-fail', 'Sutram Error: prasar: phal-prakriya-ahvanam apekshitam')),
    ('prasar on something that is not a call', 'mukhya() {\n    vitti x = 1\n    likha(prasar x)\n}\n',
     ('compile-fail', 'Sutram Error: prasar: phal-prakriya-ahvanam apekshitam')),
    ('prasar in a plain prakriya', F + 'prakriya h(a) {\n    prati prasar f(a)\n}\nmukhya() {\n    likha(h(1))\n}\n',
     ('compile-fail', 'Sutram Error: prasar kevalam phal-prakriya-madhye mukhya-madhye va')),
    ('a plain prati in a phal-prakriya',
     'prakriya k(a) {\n    yadi (a) {\n        prati dosh(1)\n    }\n    prati a\n}\nmukhya() {\n    likha(prasar k(0))\n}\n',
     ('compile-fail', 'Sutram Error: phal-prakriya: prati siddhi va dosh bhavet')),
]


def main(argv) -> int:
    comp = os.path.abspath(argv[argv.index('--compiler') + 1]) if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    fails = 0
    with tempfile.TemporaryDirectory() as td:
        src, out = Path(td, 'p.sm'), Path(td, 'p.bin')
        for name, text, want in CASES:
            src.write_text(text, encoding='utf-8')
            if out.exists():
                out.unlink()
            c = subprocess.run([comp, str(src), str(out)], capture_output=True, timeout=60, cwd=td)
            msg = (c.stdout + c.stderr).decode('utf-8', 'replace')
            if want[0] == 'compile-fail':
                ok = c.returncode == 1 and want[1] in msg and not out.exists()
                why = 'compile exit %d: %s' % (c.returncode, msg.strip()[-80:])
            elif c.returncode != 0:
                ok, why = False, 'did not compile: ' + msg.strip()[-80:]
            else:
                r = subprocess.run([str(out)], capture_output=True, timeout=20)
                got = r.stdout.decode('utf-8', 'replace')
                ok = got == want[1] and r.returncode == want[2]
                why = 'printed %r, exit %d' % (got, r.returncode)
            print('%s  %-60s %s' % ('PASS' if ok else 'FAIL', name, '' if ok else why))
            fails += not ok
    print('r25 phal: %d checks, %d failed' % (len(CASES), fails))
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
