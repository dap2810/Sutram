#!/usr/bin/env python3
"""Float-division zero guard; pass the compiler path as argv[1]. Writes .exe programs on
Windows and native ELF elsewhere (R90, Claude: so it also runs on Linux)."""
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
CASES = (
    ('positive_zero', 'dasham a = 5.0\n dasham b = 0.0\n likha(a / b)', 1, 'E_SHUNYA_BHAJAN'),
    ('negative_zero', 'dasham a = 5.0\n dasham b = -0.0\n likha(a / b)', 1, 'E_SHUNYA_BHAJAN'),
    ('zero_zero', 'dasham a = 0.0\n dasham b = 0.0\n likha(a / b)', 1, 'E_SHUNYA_BHAJAN'),
    ('literal_zero', 'likha(5.0 / 0.0)', 1, 'E_SHUNYA_BHAJAN'),
    ('self_update', 'dasham a = 5.0\n dasham b = 0.0\n a = a / b\n likha(a)', 1, 'E_SHUNYA_BHAJAN'),
    ('destination', 'dasham a = 5.0\n dasham b = 0.0\n dasham c = 0.0\n c = a / b\n likha(c)', 1, 'E_SHUNYA_BHAJAN'),
    ('compound', 'dasham a = 5.0\n dasham b = 0.0\n a /= b\n likha(a)', 1, 'E_SHUNYA_BHAJAN'),
    ('nonzero', 'dasham a = 5.0\n dasham b = 2.0\n likha(a / b)', 0, '2.500000\n'),
)

def main():
    compiler = pathlib.Path(sys.argv[1]).resolve()
    failures = 0
    with tempfile.TemporaryDirectory(prefix='sutram-r159-div-', dir=ROOT.parent) as tmp:
        for name, body, status, expected in CASES:
            source = pathlib.Path(tmp) / (name + '.sm')
            binary = pathlib.Path(tmp) / (name + ('.exe' if os.name == 'nt' else ''))
            source.write_text('mukhya() {\n ' + body + '\n}\n', encoding='utf-8')
            c = subprocess.run([str(compiler), str(source), str(binary)], cwd=ROOT,
                               capture_output=True, text=True, timeout=15)
            if c.returncode or not binary.exists():
                print('FAIL', name, 'compile', c.returncode, repr(c.stdout), repr(c.stderr))
                failures += 1
                continue
            run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
            ok = run.returncode == status and expected in run.stdout and not run.stderr
            print('PASS' if ok else 'FAIL', name, 'exit', run.returncode, 'stdout', repr(run.stdout))
            failures += not ok
    print('r159 float division:', len(CASES) - failures, 'pass,', failures, 'fail')
    return int(bool(failures))

if __name__ == '__main__':
    sys.exit(main())
