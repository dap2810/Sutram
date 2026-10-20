#!/usr/bin/env python3
"""ROUND-17 D4: the operator precedence the compiler implements is the documented
table (docs/LANGUAGE-REFERENCE.md s3), checked pair by pair.

For every ordered pair (A, B) of the 16 binary operators, and every A with
itself, it finds (seeded, so the program is the same every run) values x, y, z
for which (x A y) B z and x A (y B z) differ, prints `likha(x A y B z)` without
parentheses, compiles the program, and checks each printed value against the
one the table predicts: A binds first when its level is higher, or equal and
to the left (every binary operator is left-associative; the ternary is not
tested here).

usage: python3 -B tools/check_precedence.py [--compiler ./sutram_compiler]
Prints "246 pairs tested; 0 disagree" and exits 0, or lists the pairs and exits 1.
"""
import itertools
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import fuzz_valid as fv  # noqa: E402

OPS = ['||', '&&', '|', '^', '&', '==', '!=', '<', '>', '<=', '>=', '<<', '>>', '+', '-', '*', '/', '%']


def ev(a, op, b):
    if op in ('/', '%') and b == 0:
        return None
    if op in ('<<', '>>') and not 0 <= b <= 63:
        return None
    return fv.binop(op, a, b)


def main(argv):
    comp = os.path.abspath(argv[argv.index('--compiler') + 1] if '--compiler' in argv else ROOT / 'sutram_compiler')
    rng = random.Random(17)
    lines, meta = [], []
    for A, B in list(itertools.permutations(OPS, 2)) + [(A, A) for A in OPS]:
        for _ in range(4000):
            x, y, z = [rng.randint(-6, 9) for _ in range(3)]
            l1 = ev(x, A, y); l = None if l1 is None else ev(l1, B, z)
            r1 = ev(y, B, z); r = None if r1 is None else ev(x, A, r1)
            if l is not None and r is not None and l != r:
                lines.append('    likha(%d %s %d %s %d)' % (x, A, y, B, z)); meta.append((A, B, l, r)); break
    got = []
    with tempfile.TemporaryDirectory() as td:
        sm, bn = Path(td, 'p.sm'), Path(td, 'p.bin')
        for i in range(0, len(lines), 60):          # a block holds a limited number of statements
            sm.write_text('mukhya() {\n' + '\n'.join(lines[i:i + 60]) + '\n}\n')
            c = subprocess.run([comp, str(sm), str(bn)], capture_output=True, text=True)
            if c.returncode != 0:
                print('the pair program does not compile:', c.stdout[:200]); return 1
            got += subprocess.run([str(bn)], capture_output=True, text=True).stdout.split()
    bad = []
    for (A, B, l, r), o, src in zip(meta, got, lines):
        o = int(o)
        want = 'left' if fv.PREC[A] >= fv.PREC[B] else 'right'
        have = 'left' if o == l else 'right' if o == r else 'neither(%d)' % o
        if have != want:
            bad.append('%-3s %-3s table says %s, compiler gives %s: %s' % (A, B, want, have, src.strip()))
    print('%d pairs tested; %d disagree with the documented table' % (len(meta), len(bad)))
    for b in bad:
        print(b)
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
