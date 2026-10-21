#!/usr/bin/env python3
"""ROUND-23: function values, methods and slices - the edges.

The three working programs are examples 246-248 (goldens in tests/expect, run
by the suite). This test pins what those do not show: each documented error,
each runtime bounds check, and the choices stated in R23-0x:

  * a bare prakriya name is a value; an undefined name is still an error;
  * a call through a variable is indirect, but a prakriya of the same name wins;
  * a method is found by its name; none, or two rachanas with it, is an error;
  * a slice is checked when made (0 <= lo <= hi <= length) and when indexed;
  * a slice of a raw pointer, a non-array to a vibhag parameter, and returning a
    slice are compile errors.

Runs the Linux compiler. No network.
usage: python3 -B tests/r23/test_capabilities.py [--compiler PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

ARR = 'mukhya() {\n    mala a[4]\n    a[0] = 1\n    a[1] = 2\n    a[2] = 3\n    a[3] = 4\n'
# (name, source, expect): expect is ('out', text) for a program that runs and
# prints text, ('run-fail', text) for one that compiles and stops at run time
# with text, ('compile-fail', text) for one the compiler refuses with text.
CASES = [
    ('function value: passed, stored, returned',
     'prakriya f(a) {\n    prati a * 2\n}\nprakriya h(a) {\n    prati a * 3\n}\n'
     'prakriya chuno(k) {\n    yadi (k) {\n        prati h\n    }\n    prati f\n}\n'
     'prakriya lagu(g, x) {\n    prati g(x)\n}\n'
     'mukhya() {\n    vitti c = chuno(1)\n    likha(c(5))\n    likha(lagu(f, 5))\n    likha(lagu(chuno(0), 6))\n}\n',
     ('out', '15\n10\n12\n')),
    ('function value through a mala',
     'prakriya f(a) {\n    prati a + 1\n}\nmukhya() {\n    mala t[1]\n    t[0] = f\n    vitti c = t[0]\n    likha(c(41))\n}\n',
     ('out', '42\n')),
    ('the same function is the same value',
     'prakriya f(a) {\n    prati a\n}\nprakriya h(a) {\n    prati a\n}\n'
     'mukhya() {\n    vitti x = f\n    likha(x == f)\n    likha(x == h)\n}\n',
     ('out', '1\n0\n')),
    ('a prakriya wins over a parameter of its name',
     'prakriya f(a) {\n    prati a + 1\n}\nprakriya g(f) {\n    prati f(10)\n}\nmukhya() {\n    likha(g(5))\n}\n',
     ('out', '11\n')),
    ('an undefined name is still an error',
     'mukhya() {\n    vitti g = nahi_hai\n    likha(g)\n}\n',
     ('compile-fail', "[E_UNDEFINED_NAME]: agyat naam 'nahi_hai'")),
    ('calling an undefined name is still an error',
     'mukhya() {\n    likha(nahi_hai(1))\n}\n',
     ('compile-fail', 'agyat prakriya: nahi_hai')),
    ('a method changes its object',
     'rachana B = { x }\nprakriya B.badha(swa, d) {\n    swa.x = swa.x + d\n    prati swa.x\n}\n'
     'mukhya() {\n    vitti b = nirmmita(8)\n    b.x = 1\n    likha(b.badha(4))\n    likha(b.x)\n}\n',
     ('out', '5\n5\n')),
    ('no such method',
     'rachana B = { x }\nmukhya() {\n    vitti b = nirmmita(8)\n    likha(b.nahi())\n}\n',
     ('compile-fail', "[E_UNKNOWN_FIELD]: agyat kshetra 'nahi'")),
    ('a method name in two rachanas',
     'rachana A = { x }\nrachana B = { y }\nprakriya A.m(p) {\n    prati 1\n}\nprakriya B.m(p) {\n    prati 2\n}\n'
     'mukhya() {\n    vitti b = nirmmita(8)\n    likha(b.m())\n}\n',
     ('compile-fail', "[E_AMBIGUOUS_FIELD]: kshetra 'm'")),
    ('a method of an undeclared rachana',
     'prakriya Nahi.m(p) {\n    prati 1\n}\nmukhya() {\n    likha(1)\n}\n',
     ('compile-fail', "[E_UNDEFINED_NAME]: agyat naam 'Nahi'")),
    ('... and its hint names the rachana (R24)',
     'prakriya Nahi.m(p) {\n    prati 1\n}\nmukhya() {\n    likha(1)\n}\n',
     ('compile-fail', 'Sanket: vidheh purvam ghoshana avashyaki: rachana Nahi = ...')),
    ('a method call with the wrong number of arguments',
     'rachana A = { x }\nprakriya A.m(p, q) {\n    prati q\n}\nmukhya() {\n    vitti b = nirmmita(8)\n    likha(b.m())\n}\n',
     ('compile-fail', "[E_ARITY]: 'A.m' ityasmai 1 tarkah dattah; hastakshare 2")),
    ('slices: views, writes, omitted bounds',
     ARR + '    vitti s = a[1:4]\n    s[0] = 20\n    likha(a[1])\n    likha(pankti_len(s))\n'
     '    vitti t = s[1:]\n    likha(t[0])\n    likha(pankti_len(a[:2]))\n    likha(pankti_len(a[4:]))\n}\n',
     ('out', '20\n3\n3\n2\n0\n')),
    ('a slice index past its length',
     ARR + '    vitti s = a[1:3]\n    likha(s[2])\n}\n', ('run-fail', 'Sutram Error: mala ank seema atikram')),
    ('a slice write past its length',
     ARR + '    vitti s = a[0:2]\n    s[2] = 9\n}\n', ('run-fail', 'Sutram Error: mala ank seema atikram')),
    ('hi past the array',
     ARR + '    vitti s = a[2:5]\n}\n', ('run-fail', 'Sutram Error: mala ank seema atikram')),
    ('lo after hi',
     ARR + '    vitti s = a[3:2]\n}\n', ('run-fail', 'Sutram Error: mala ank seema atikram')),
    ('a negative lo',
     ARR + '    vitti s = a[0 - 1:2]\n}\n', ('run-fail', 'Sutram Error: mala ank seema atikram')),
    ('a sub-slice past its slice',
     ARR + '    vitti s = a[0:2]\n    vitti t = s[1:3]\n}\n', ('run-fail', 'Sutram Error: mala ank seema atikram')),
    ('a slice of a raw pointer',
     'mukhya() {\n    vitti p = nirmmita(32)\n    vitti s = p[0:2]\n}\n',
     ('compile-fail', 'Sutram Error: vibhag: mala, kosh va vibhag apekshita')),
    ('a number to a vibhag parameter',
     'prakriya f(vibhag s) {\n    prati s[0]\n}\nmukhya() {\n    likha(f(5))\n}\n',
     ('compile-fail', 'Sutram Error: vibhag: mala, kosh va vibhag apekshita')),
    ('returning a slice',
     'prakriya f(vibhag s) {\n    prati s\n}\nmukhya() {\n    mala a[2]\n    likha(f(a))\n}\n',
     ('compile-fail', 'Sutram Error: vibhag prakriyayah na pratyarpaniyah')),
    ('a whole kosh to a vibhag parameter, and a kosh slice',
     'prakriya yog(vibhag s) {\n    vitti t = 0\n    chakra i = 0 tak pankti_len(s) - 1 {\n        t = t + s[i]\n    }\n    prati t\n}\n'
     'mukhya() {\n    kosh k[1]\n    kosh_push(k, 1)\n    kosh_push(k, 2)\n    kosh_push(k, 3)\n    likha(yog(k))\n    likha(yog(k[1:]))\n}\n',
     ('out', '6\n5\n')),
]


def main(argv) -> int:
    comp = os.path.abspath(argv[argv.index('--compiler') + 1]) if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    fails = 0
    with tempfile.TemporaryDirectory() as td:
        src, out = Path(td, 'p.sm'), Path(td, 'p.bin')
        for name, text, (kind, want) in CASES:
            src.write_text(text, encoding='utf-8')
            if out.exists():
                out.unlink()
            c = subprocess.run([comp, str(src), str(out)], capture_output=True, timeout=60, cwd=td)
            msg = (c.stdout + c.stderr).decode('utf-8', 'replace')
            if kind == 'compile-fail':
                ok = c.returncode == 1 and want in msg and not out.exists()
                why = 'compile exit %d' % c.returncode
            elif c.returncode != 0:
                ok, why = False, 'did not compile: ' + msg.strip().splitlines()[-1][:80] if msg.strip() else 'did not compile'
            else:
                r = subprocess.run([str(out)], capture_output=True, timeout=20)
                got = r.stdout.decode('utf-8', 'replace')
                if kind == 'out':
                    ok, why = (r.returncode == 0 and got == want), 'printed %r' % got
                else:
                    ok, why = (r.returncode == 1 and want in got), 'exit %d, %r' % (r.returncode, got[-60:])
            print('%s  %-58s %s' % ('PASS' if ok else 'FAIL', name, '' if ok else why))
            fails += not ok
    print('r23 capabilities: %d checks, %d failed' % (len(CASES), fails))
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
