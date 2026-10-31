#!/usr/bin/env python3
"""Exact-only float-to-integer guard; argv[1] is the compiler. Writes .exe programs on Windows,
native ELF elsewhere (R92, Claude: so it runs on Linux too; NaN and infinity come from overflow,
since dividing a dasham by zero is an error from v280)."""
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
INF = 'dasham z = 10.0\n vitti n = 0\n yavat (n < 400) {\n  z = z * 10.0\n  n = n + 1\n }'
CASES = (
    ('fraction_decl', '', 'dasham d = 3.7\n vitti i = d\n likha(i)', 1, 'E_DASHAM_VITTI'),
    ('fraction_assign', '', 'dasham d = 0.0 - 3.7\n vitti i = 0\n i = d\n likha(i)', 1, 'E_DASHAM_VITTI'),
    ('integer_value', '', 'dasham d = 3.0\n vitti i = d\n likha(i)', 0, '3\n'),
    ('negative_integer', '', 'dasham d = 0.0 - 3.0\n vitti i = d\n likha(i)', 0, '-3\n'),
    ('push', '', 'dasham d = 2.9\n kosh k[1]\n kosh_push(k, d)\n likha(k[0])', 1, 'E_DASHAM_VITTI'),
    ('index', '', 'dasham d = 2.9\n kosh k[1]\n kosh_push(k, 1)\n k[0] = d\n likha(k[0])', 1, 'E_DASHAM_VITTI'),
    ('arg', 'prakriya f(i) { nivartanam i }\n', 'dasham d = 2.9\n likha(f(d))', 1, 'E_DASHAM_VITTI'),
    ('main_return', '', 'dasham d = 2.9\n nivartanam d', 1, 'E_DASHAM_VITTI'),
    ('negative_zero', '', 'dasham d = -0.0\n vitti i = d\n likha(i)', 0, '0\n'),
    ('nan', '', INF + '\n dasham d = z - z\n vitti i = d\n likha(i)', 1, 'E_DASHAM_VITTI'),
    ('infinity', '', INF + '\n dasham d = z\n vitti i = d\n likha(i)', 1, 'E_DASHAM_VITTI'),
    ('plus_limit', '', 'dasham d = 9223372036854775808.0\n vitti i = d\n likha(i)', 1, 'E_DASHAM_VITTI'),
    ('min_exact', '', 'vitti m = -9223372036854775808\n dasham d = m\n vitti i = d\n likha(i)', 0, '-9223372036854775808\n'),
)

def main():
    compiler = pathlib.Path(sys.argv[1]).resolve()
    failed = 0
    with tempfile.TemporaryDirectory(prefix='sutram-r161-', dir=ROOT.parent) as tmp:
        for name, prefix, body, status, expected in CASES:
            source = pathlib.Path(tmp) / (name + '.sm')
            binary = pathlib.Path(tmp) / (name + ('.exe' if os.name == 'nt' else ''))
            source.write_text(prefix + 'mukhya() {\n ' + body + '\n}\n', encoding='utf-8')
            c = subprocess.run([str(compiler), str(source), str(binary)], cwd=ROOT,
                               capture_output=True, text=True, timeout=15)
            if c.returncode or not binary.exists():
                ok = False
                print('FAIL', name, 'compile', c.returncode, repr(c.stdout), repr(c.stderr))
            else:
                run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
                ok = run.returncode == status and (run.stdout == expected if status == 0 else expected in run.stdout) and not run.stderr
                print('PASS' if ok else 'FAIL', name, 'run', run.returncode, repr(run.stdout))
            failed += not ok
    print('r161 runtime narrowing:', len(CASES) - failed, 'pass,', failed, 'fail')
    return int(bool(failed))

if __name__ == '__main__':
    sys.exit(main())
