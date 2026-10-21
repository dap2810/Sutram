#!/usr/bin/env python3
"""ROUND-30 proposal (branch claude/round-30-yoj-scan, NOT on main): where `yoj` is an import.

Before: the compiler's import pass found `yoj` at any byte outside a comment - inside a
string literal, and at the end of a longer name. So `likha("yoj bogus")` failed with
E_MODULE_MISSING, `likha("yoj ganit ")` silently compiled ganit's source INTO the string,
and `vitti sanyoj = 4` failed. tools/sutram_build.py copied the same rule (ChatGPT R96).
After: not inside a string (the lexer's rule, escapes included), not after a letter, digit,
`_` or non-ASCII byte. Each case: the compile, its output, and the builder's graph.
usage: python3 -B tests/r30/test_yoj_scan.py [--compiler PATH]
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import sutram_build  # noqa: E402

CASES = [  # (source, expected stdout, expected builder names)
    ('mukhya() {\n    likha("yoj bogus")\n}\n', b'yoj bogus', []),
    ('mukhya() {\n    likha("yoj ganit ")\n}\n', b'yoj ganit ', []),
    ('mukhya() {\n    likha("a \\" yoj ganit ")\n    likha("|")\n}\n', b'a " yoj ganit |', []),
    ('mukhya() {\n    vitti sanyoj = 4\n    likha(sanyoj + 1)\n}\n', b'5\n', []),
    ('# yoj bogus\nyoj ganit\nmukhya() {\n    likha(vargit(3))\n}\n', b'9\n', ['ganit']),
]


def main(argv):
    comp = os.path.abspath(argv[argv.index('--compiler') + 1]) if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    os.chdir(ROOT)
    t = Path(tempfile.mkdtemp(prefix='r30-scan-'))
    fails = 0
    for k, (src, out, names) in enumerate(CASES):
        f, exe = t / f'c{k}.sm', t / f'c{k}.bin'
        f.write_text(src)
        r = subprocess.run([comp, str(f), str(exe)], capture_output=True)
        got = subprocess.run([str(exe)], capture_output=True).stdout if r.returncode == 0 else r.stdout
        g = sutram_build.yoj_names(src.encode())
        ok = r.returncode == 0 and got == out and g == names
        fails += not ok
        print('PASS' if ok else 'FAIL', repr(src.split('\n')[-3 if k < 4 else 1])[:50], got[:40], g)
    print(f'r30 yoj scan: {len(CASES)} cases, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
