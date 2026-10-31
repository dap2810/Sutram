#!/usr/bin/env python3
"""Exercise NaN and ordered floating comparisons against an independent oracle.

Usage: python tests/r159_float_compare/test_float_compare.py path/to/compiler
The output suffix selects PE: on Windows the test writes .exe programs, elsewhere native ELF
(R90, Claude: so it also runs on Linux).
"""
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
# z = +inf by repeated multiplication, and NaN = inf - inf: no division by zero, which is
# an error since v280 (R90; ChatGPT's follow-up noted the dependency).
INF = 'dasham z = 10.0\n vitti i = 0\n yavat (i < 400) {\n  z = z * 10.0\n  i = i + 1\n }'
OPS = ('==', '!=', '<', '<=', '>', '>=')
CASES = (
    ('less', 'dasham x = 2.0\n dasham y = 3.0', 'x', 'y', (0, 1, 1, 1, 0, 0)),
    ('greater', 'dasham x = 3.0\n dasham y = 2.0', 'x', 'y', (0, 1, 0, 0, 1, 1)),
    ('equal', 'dasham x = 2.0\n dasham y = 2.0', 'x', 'y', (1, 0, 0, 1, 0, 1)),
    ('signed_zero', 'dasham x = 0.0\n dasham y = 0.0 - x', 'x', 'y', (1, 0, 0, 1, 0, 1)),
    ('nan_left', INF + '\n dasham x = z - z\n dasham y = 5.0', 'x', 'y', (0, 1, 0, 0, 0, 0)),
    ('nan_right', INF + '\n dasham x = 5.0\n dasham y = z - z', 'x', 'y', (0, 1, 0, 0, 0, 0)),
    ('nan_both', INF + '\n dasham x = z - z\n dasham y = z - z', 'x', 'y', (0, 1, 0, 0, 0, 0)),
    ('nan_literal', INF + '\n dasham x = z - z', 'x', '5.0', (0, 1, 0, 0, 0, 0)),
    ('nan_mixed', INF + '\n dasham x = z - z', '5', 'x', (0, 1, 0, 0, 0, 0)),
    ('infinity', INF + '\n dasham x = z\n dasham y = 5.0', 'x', 'y', (0, 1, 0, 0, 1, 1)),
)

def main():
    compiler = pathlib.Path(sys.argv[1]).resolve()
    failures = 0
    with tempfile.TemporaryDirectory(prefix='sutram-r159-', dir=ROOT.parent) as tmp:
        for name, decl, lhs, rhs, expected in CASES:
            source = pathlib.Path(tmp) / (name + '.sm')
            binary = pathlib.Path(tmp) / (name + ('.exe' if os.name == 'nt' else ''))
            body = '\n'.join(' likha(%s %s %s)' % (lhs, op, rhs) for op in OPS)
            source.write_text('mukhya() {\n ' + decl + '\n' + body + '\n}\n', encoding='utf-8')
            c = subprocess.run([str(compiler), str(source), str(binary)], cwd=ROOT,
                               capture_output=True, text=True, timeout=15)
            if c.returncode != 0 or not binary.exists():
                print('FAIL', name, 'compile', c.returncode, c.stdout, c.stderr)
                failures += 1
                continue
            r = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
            want = ''.join(str(x) + '\n' for x in expected)
            ok = r.returncode == 0 and r.stdout == want and not r.stderr
            print('PASS' if ok else 'FAIL', name, 'exit', r.returncode,
                  'stdout', repr(r.stdout), 'stderr', repr(r.stderr))
            failures += not ok
    print('r159 float comparison:', len(CASES) - failures, 'pass,', failures, 'fail')
    return int(bool(failures))

if __name__ == '__main__':
    sys.exit(main())
