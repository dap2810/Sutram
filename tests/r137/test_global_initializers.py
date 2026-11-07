#!/usr/bin/env python3
"""Validate expression entry points that bypass gen_stmt, on native Windows or Linux."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MAKE = 'prakriya make_kosh() { kosh k[1] kosh_kship(k, 7) nivartanam k }\n'
OPS = ['+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=', '&', '|', '^', '&&', '||', '<<', '>>']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    cases = []
    for op in OPS:
        for scope in ('global', 'local'):
            decl = f'vitti leaked = make_kosh() {op} zero\n'
            body = 'likha(leaked)'
            source = 'vitti zero = 0\n' + MAKE
            source += decl + f'mukhya() {{ {body} }}\n' if scope == 'global' else f'mukhya() {{ {decl}{body} }}\n'
            cases.append((f'{scope} {op}', source, 'E_KOSH_GANIT'))
    cases += [
        ('scalar global calls', (ROOT / 'tests/r56_check/initializer_calls.sm').read_text(encoding='utf8'), '17\n6\n'),
        ('global conditional kosh arithmetic', 'vitti zero = 0\n' + MAKE +
         'vitti leaked = (zero ? make_kosh() : make_kosh()) + zero\nmukhya() { likha(leaked) }\n', 'E_KOSH_GANIT'),
        ('direct global kosh', MAKE + 'vitti leaked = make_kosh()\nmukhya() { likha(1) }\n', 'E_KOSH_DVARA'),
        ('global scope ignores local string', 'vitti a = 8\nvitti b = a + 1\nmukhya() { vitti a = "hello" likha(b) }\n', '9\n'),
    ]
    for scope in ('global', 'local'):
        source = MAKE + 'prakriya scalar() { nivartanam 2 }\nvitti zero = 0\n'
        decl = 'vitti leaked = (make_kosh() + zero) + scalar()\n'
        source += decl + 'mukhya() { likha(leaked) }\n' if scope == 'global' else 'mukhya() { ' + decl + 'likha(leaked) }\n'
        cases.append((f'{scope} nested expression with return analysis', source, 'E_KOSH_GANIT'))
    rows = []
    with tempfile.TemporaryDirectory(prefix='sutram-global-') as tmp:
        for i, (name, source, expected) in enumerate(cases):
            sm, exe = Path(tmp) / f'{i}.sm', Path(tmp) / f'{i}.exe'
            sm.write_text(source, encoding='utf8')
            command = [str(args.compiler.resolve()), str(sm), str(exe)]
            cp = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            row = dict(name=name, source=source, command=command, exit=cp.returncode,
                       stdout=cp.stdout, stderr=cp.stderr, output_exists=exe.exists(), expected=expected)
            if expected.startswith('E_'):
                row['pass'] = cp.returncode != 0 and not exe.exists() and f'[{expected}]' in cp.stdout + cp.stderr
            else:
                row['pass'] = False
                if cp.returncode == 0 and exe.exists():
                    run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
                    row['run'] = dict(exit=run.returncode, stdout=run.stdout, stderr=run.stderr)
                    row['pass'] = run.returncode == 0 and run.stdout == expected and not run.stderr
            rows.append(row)
            print(('PASS ' if row['pass'] else 'FAIL ') + name)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(rows, indent=2) + '\n', encoding='utf8')
    failures = sum(not row['pass'] for row in rows)
    print(f'global initializer validation: {len(rows)} checks, {failures} failed')
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
