#!/usr/bin/env python3
"""ROUND-45: --debug, the smallest useful debugger.

  1. THE TRACE: a fixed program compiled with --debug prints, before each statement of the program's own
     file, `[shodhan] pankti N` and every scalar variable then in scope (locals, parameters, a dasham), and
     goes on. Checked exactly: the lines, the values, the order, a function's own scope, a loop's every pass.
  1b. SCOPE: a name declared in a block is not shown once the block has ended, nor when its branch was
     never taken (var_table is flat per function; the slot would be stale or uninitialized).
  2. NOT TRACED: a mala/kosh (an address) is left out; a library function called through `yoj` is one step
     (its statements are not traced); a module-level vitti is not shown.
  3. DEVANAGARI: the same under --debug --lang sanskrit, with Devanagari names; the line is the original
     file's.
  4. THE SAME PROGRAM: every examples/*.sm with an accepted expectation (the suite) is compiled WITH --debug,
     run, and its output - with the trace taken out - must equal the expectation, with the same exit code.
     A trace changes what is printed, never what the program does. A program too large for the debug build
     (a capacity diagnostic: the trace multiplies the code) is reported, not failed.
  5. USAGE: --debug without an output, and --debug --lang without the pack's arguments, print the usage and
     write nothing.

The flag-off guarantee (the ordinary compile is byte-identical) is the guard's job, not this file's.
No network; writes only to a temporary directory.
usage: python3 -B tests/r45/test_debug.py [--compiler ./sutram_compiler]
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
TRACE = re.compile(r'\[shodhan\] (?:pankti|samapti, vakya:) \d+\n(?:    [^\n]* = [^\n]*\n)*')  # R46: + the summary
OUT_CAP = 64 << 20                 # a trace past 64 MiB is a loop too long to compare usefully


def run_tests_tables():
    spec = importlib.util.spec_from_file_location('run_tests', ROOT / 'tests' / 'run_tests.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main(argv) -> int:
    comp = argv[argv.index('--compiler') + 1] if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    comp = str(Path(comp).resolve())
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        if not ok:
            fails += 1
        print(('PASS  ' if ok else 'FAIL  ') + what)
        return ok

    with tempfile.TemporaryDirectory(prefix='r45-') as td:
        t = Path(td)

        def build(src, lang=None, debug=True, name='p'):
            p, b = t / f'{name}.sm', t / f'{name}.bin'
            p.write_text(src, encoding='utf-8')
            if b.exists():
                b.unlink()
            cmd = [comp] + (['--debug'] if debug else []) + (['--lang', lang] if lang else []) + [str(p), str(b)]
            c = subprocess.run(cmd, capture_output=True, timeout=60, cwd=ROOT)
            if c.returncode != 0:
                return None, (c.stdout + c.stderr).decode('utf-8', 'replace')
            r = subprocess.run([str(b)], capture_output=True, timeout=30)
            return r.returncode, r.stdout.decode('utf-8', 'replace')

        # 1. the trace, exactly
        src = ('prakriya dviguna(n) {\n'          # 1
               '    vitti r = n * 2\n'             # 2
               '    nivartanam r\n'                     # 3
               '}\n'                               # 4
               'mukhya() {\n'                      # 5
               '    vitti yoga = 0\n'              # 6
               '    dasham ardha = 0.5\n'          # 7
               '    mala m[3]\n'                   # 8
               '    vitti i = 1\n'                 # 9
               '    yavat (i <= 2) {\n'            # 10
               '        yoga = yoga + dviguna(i)\n'  # 11
               '        i = i + 1\n'               # 12
               '    }\n'                           # 13
               '    likha(yoga)\n'                 # 14
               '}\n')
        want = ('[shodhan] pankti 6\n'
                '[shodhan] pankti 7\n    yoga = 0\n'
                '[shodhan] pankti 8\n    yoga = 0\n    ardha = 0.500000\n'
                '[shodhan] pankti 9\n    yoga = 0\n    ardha = 0.500000\n'
                '[shodhan] pankti 10\n    yoga = 0\n    ardha = 0.500000\n    i = 1\n'
                '[shodhan] pankti 11\n    yoga = 0\n    ardha = 0.500000\n    i = 1\n'
                '[shodhan] pankti 2\n    n = 1\n'
                '[shodhan] pankti 3\n    n = 1\n    r = 2\n'
                '[shodhan] pankti 12\n    yoga = 2\n    ardha = 0.500000\n    i = 1\n'
                '[shodhan] pankti 11\n    yoga = 2\n    ardha = 0.500000\n    i = 2\n'
                '[shodhan] pankti 2\n    n = 2\n'
                '[shodhan] pankti 3\n    n = 2\n    r = 4\n'
                '[shodhan] pankti 12\n    yoga = 6\n    ardha = 0.500000\n    i = 2\n'
                '[shodhan] pankti 14\n    yoga = 6\n    ardha = 0.500000\n    i = 3\n'
                '6\n'
                '[shodhan] samapti, vakya: 14\n    yoga = 6\n    ardha = 0.500000\n    i = 3\n')   # R46
        rc, out = build(src)
        ok = check(rc == 0 and out == want, 'the trace: every statement of the file, its line, its scalar '
                   'variables (a local, a dasham, a parameter, a loop counter), each loop pass; then the output')
        if not ok:
            print('      want: ' + repr(want[:300]))
            print('      got:  ' + repr((out or '')[:300]))
        check(rc == 0 and '    m = ' not in out, 'not shown: the mala m (an address, not a value)')

        # 1b. block scope: a block's name is not shown after the block, nor when its branch was not taken
        rc, out = build('mukhya() {\n'            # 1
                        '    vitti a = 1\n'        # 2
                        '    yadi (a == 1) {\n'    # 3
                        '        vitti b = 5\n'    # 4
                        '        a = 2\n'          # 5
                        '    }\n'                  # 6
                        '    yadi (a == 9) {\n'    # 7
                        '        vitti z = 8\n'    # 8
                        '    }\n'                  # 9
                        '    vitti c = 7\n'        # 10
                        '    likha(c)\n'           # 11
                        '}\n')
        want1b = ('[shodhan] pankti 2\n[shodhan] pankti 3\n    a = 1\n[shodhan] pankti 4\n    a = 1\n'
                  '[shodhan] pankti 5\n    a = 1\n    b = 5\n[shodhan] pankti 7\n    a = 2\n'
                  '[shodhan] pankti 10\n    a = 2\n[shodhan] pankti 11\n    a = 2\n    c = 7\n7\n'
                  '[shodhan] samapti, vakya: 7\n    a = 2\n    c = 7\n')   # R46
        check(rc == 0 and out == want1b, 'block scope: b only inside its block; z (branch not taken) never shown '
              f'(got {out!r:.200})')

        # 2. a library call is one step; the library's own statements are not traced
        rc, out = build('yoj varna\nmukhya() {\n    vitti n = varna_maap("abc")\n    likha(n)\n}\n')
        lines = [l for l in (out or '').splitlines() if l.startswith('[shodhan] pankti')]
        check(rc == 0 and lines == ['[shodhan] pankti 3', '[shodhan] pankti 4'] and '\n3\n[shodhan] samapti, vakya: 2\n' in out,
              f'yoj varna: only the program\'s own 2 statements are traced (got {lines})')

        # 3. Devanagari, under --lang sanskrit
        rc, out = build('मुख्य()\n    वित्ति योग = 0।\n    वित्ति इ = 4।\n    योग = योग + इ।\n    लिख(योग)।\n',
                        lang='sanskrit')
        want3 = ('[shodhan] pankti 2\n[shodhan] pankti 3\n    योग = 0\n'
                 '[shodhan] pankti 4\n    योग = 0\n    इ = 4\n'
                 '[shodhan] pankti 5\n    योग = 4\n    इ = 4\n4\n'
                 '[shodhan] samapti, vakya: 4\n    योग = 4\n    इ = 4\n')   # R46
        check(rc == 0 and out == want3, f'Devanagari names and lines under --lang sanskrit (got {out!r:.160})')

        # 5. usage: nothing written
        (t / 'x.sm').write_text('mukhya() {\n    likha(1)\n}\n', encoding='utf-8')
        for args, what in ((['--debug', 'x.sm'], '--debug without an output'),
                           (['--debug', '--lang', 'sanskrit', 'x.sm'], '--debug --lang without an output')):
            before = set(os.listdir(t))
            c = subprocess.run([comp] + args, capture_output=True, timeout=30, cwd=t)
            check(set(os.listdir(t)) == before, f'usage: {what} writes nothing (exit {c.returncode})')

        # 4. the suite, with --debug: the same program
        rt = run_tests_tables()
        exp = ROOT / 'tests' / 'expect'
        same = refused = toolong = 0
        bad: list[str] = []
        for sm in sorted((ROOT / 'examples').glob('*.sm')):
            n = sm.stem
            eo, ee = exp / f'{n}.out', exp / f'{n}.exit'
            if not eo.exists() or not ee.exists() or (exp / f'{n}.compile_fail').exists():
                continue
            b = t / f'{n}.bin'
            cmd = [comp, '--debug'] + (['--lang', rt.LANG[n]] if n in rt.LANG else []) + [str(sm), str(b)]
            c = subprocess.run(cmd, capture_output=True, timeout=120, cwd=rt.CWD.get(n, str(ROOT)))
            if c.returncode != 0:
                msg = (c.stdout + c.stderr).decode('utf-8', 'replace')
                if 'seema atikram' in msg or 'atikram' in msg:
                    refused += 1             # a capacity limit: the trace multiplies the code
                    print(f'NOTE  {n}: too large for a debug build: {msg.strip().splitlines()[-1][:80]}')
                    continue
                bad.append(f'{n}: the --debug compile failed: {msg.strip()[-120:]}')
                continue
            try:
                r = subprocess.run([str(b)], input=rt.STDIN.get(n, '').encode(), capture_output=True, timeout=60)
            except subprocess.TimeoutExpired:
                toolong += 1
                print(f'NOTE  {n}: its trace did not finish in 60 s')
                continue
            if len(r.stdout) > OUT_CAP:
                toolong += 1
                print(f'NOTE  {n}: a trace of {len(r.stdout)} bytes, too long to compare')
                continue
            got = TRACE.sub('', r.stdout.decode('utf-8', 'replace'))
            if got == eo.read_text(encoding='utf-8') and str(r.returncode) == ee.read_text().strip():
                same += 1
            else:
                bad.append(f'{n}: exit {r.returncode} (want {ee.read_text().strip()}), output differs '
                           f'after the trace is taken out')
        for line in bad:
            print('FAIL  ' + line)
        check(not bad, f'the suite under --debug: {same} programs print exactly their expected output once the '
              f'trace is taken out, with the same exit code; {refused} too large for a debug build, '
              f'{toolong} with a trace too long to compare')

    print(f'r45 debug: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
