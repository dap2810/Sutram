#!/usr/bin/env python3
"""ROUND-46: --debug made usable, and a wrong answer found with it.

  --debug=<name>[,<name>...]   only these names are shown; a line with none of them in scope is not printed
  --debug=...@N  /  @N-M        only statements on lines N.. (or N..M) print; the rest still count
  at the end of mukhya          [shodhan] samapti, vakya: <statements run>, then every scalar in scope
                                (locals, and now module-level vitti too)

  1. WATCH: --debug=yoga prints yoga alone, and no line where it is not yet declared.
  2. RANGE: --debug=n,r@2-3 traces only the function's two lines, every call.
  3. THE SUMMARY: the count is the number of statements of the file that ran (17, counted by hand), and the final
     scalars follow.
  4. MODULE VITTI: a module-level vitti is shown in the trace and the summary, with its updated value.
  5. MALFORMED: --debug=, --debug=a, --debug=,a, --debug=@, --debug=@5-2, --debug=x@3y each give the usage and
     write nothing.
  7. R49: the flags repeat, in any order: --debug=yoga --debug=i --debug-from=11 is --debug=yoga,i@11; a
     malformed --debug-from is the usage; the environment is still read after the extra flags are dropped.
  6. A WRONG ANSWER IS FINDABLE: madhava_sin with the sign error that survives every library proof
     (PROJECT-MASTER; here line 10 is `y = y - pi2` where it should be `y + pi2`). The program prints a wrong
     sin(-4.0) - 0.757068 for 0.756802, off in the fourth digit. Compiled with --debug=y@5-12 the trace shows y
     = -4.000000 before line 10 and y = -10.283185 at line 12: outside [-pi, pi], the first wrong value, made
     by line 10. With the sign corrected, the same trace shows y = 2.283185 and the program prints 0.756802.

No network; writes only to a temporary directory.
usage: python3 -B tests/r46/test_debug_usable.py [--compiler ./sutram_compiler]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

PROG = ('prakriya dviguna(n) {\n'          # 1
        '    vitti r = n * 2\n'             # 2
        '    nivartanam r\n'                     # 3
        '}\n'                               # 4
        '\n'                                # 5
        'mukhya() {\n'                      # 6
        '    vitti yoga = 0\n'              # 7
        '    vitti i = 1\n'                 # 8
        '    dasham ardha = 0.5\n'          # 9
        '    yavat (i <= 3) {\n'            # 10
        '        yoga = yoga + dviguna(i)\n'  # 11
        '        i = i + 1\n'               # 12
        '    }\n'                           # 13
        '    likha(yoga)\n'                 # 14
        '}\n')

SIN = ('prakriya sin_galat(dasham x) {\n'                  # 1
       '    dasham pi2 = 6.283185307179586\n'               # 2
       '    dasham pi = 3.141592653589793\n'                # 3
       '    vitti k = x / pi2\n'                            # 4
       '    dasham y = x - k * pi2\n'                       # 5
       '    yadi (y > pi) {\n'                              # 6
       '        y = y - pi2\n'                              # 7
       '    }\n'                                            # 8
       '    yadi (y < 0.0 - pi) {\n'                        # 9
       '        y = y SIGN pi2\n'                           # 10
       '    }\n'                                            # 11
       '    dasham s = y\n'                                 # 12
       '    dasham t = y\n'                                 # 13
       '    vitti n = 1\n'                                  # 14
       '    yavat (n < 16) {\n'                             # 15
       '        t = 0.0 - t * y * y / ((2.0 * n) * (2.0 * n + 1.0))\n'  # 16
       '        s = s + t\n'                                # 17
       '        n = n + 1\n'                                # 18
       '    }\n'                                            # 19
       '    nivartanam s\n'                                      # 20
       '}\n'                                                # 21
       'mukhya() {\n'                                       # 22
       '    likha(sin_galat(0.0 - 4.0))\n'                  # 23
       '}\n')


def main(argv) -> int:
    comp = argv[argv.index('--compiler') + 1] if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    comp = str(Path(comp).resolve())
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)
        return ok

    with tempfile.TemporaryDirectory(prefix='r46-') as td:
        t = Path(td)

        def build(src, flag='--debug'):
            p, b = t / 'p.sm', t / 'p.bin'
            p.write_text(src, encoding='utf-8')
            if b.exists():
                b.unlink()
            c = subprocess.run([comp] + ([flag] if flag else []) + [str(p), str(b)], capture_output=True,
                               timeout=60, cwd=ROOT)
            if c.returncode != 0 or not b.exists():
                return None, (c.stdout + c.stderr).decode('utf-8', 'replace')
            r = subprocess.run([str(b)], capture_output=True, timeout=30)
            return r.returncode, r.stdout.decode('utf-8', 'replace')

        # 1. watch
        rc, out = build(PROG, '--debug=yoga')
        heads = [l for l in out.splitlines() if l.startswith('[shodhan] pankti')] if rc == 0 else []
        check(rc == 0 and heads[:1] == ['[shodhan] pankti 8'] and 'samapti' in out,
              f'--debug=yoga: the first line printed is 8, after yoga is declared (got {heads[:2]})')
        # in the summary every scalar is shown, so check the trace part alone
        trace = out.split('[shodhan] samapti')[0] if rc == 0 else ''
        check(rc == 0 and {l.split('=')[0].strip() for l in trace.splitlines() if l.startswith('    ')} == {'yoga'},
              '--debug=yoga: the trace names no other variable')

        # 2. range
        rc, out = build(PROG, '--debug=n,r@2-3')
        trace = out.split('[shodhan] samapti')[0] if rc == 0 else ''
        want = ''.join(f'[shodhan] pankti 2\n    n = {n}\n[shodhan] pankti 3\n    n = {n}\n    r = {2 * n}\n'
                       for n in (1, 2, 3)) + '12\n'
        check(rc == 0 and trace == want, f'--debug=n,r@2-3: the function\'s two lines, each of 3 calls '
              f'(got {trace!r:.160})')

        # 3. the summary
        rc, out = build(PROG)
        summary = out[out.index('[shodhan] samapti'):] if rc == 0 and '\n12\n[shodhan] samapti' in out else ''
        check(summary == '[shodhan] samapti, vakya: 17\n    yoga = 12\n    i = 4\n    ardha = 0.500000\n',
              f'summary: 17 statements ran - lines 7-10 once (4), 11-12 per pass (6), 2-3 per call (6), 14 (1) - '
              f'then the final scalars (got {summary!r})')

        # 4. a module-level vitti
        rc, out = build('vitti ginti = 5\nmukhya() {\n    vitti x = 1\n    ginti = ginti + x\n    likha(ginti)\n}\n')
        want = ('[shodhan] pankti 3\n    ginti = 5\n[shodhan] pankti 4\n    x = 1\n    ginti = 5\n'
                '[shodhan] pankti 5\n    x = 1\n    ginti = 6\n6\n'
                '[shodhan] samapti, vakya: 3\n    x = 1\n    ginti = 6\n')
        check(rc == 0 and out == want, f'a module-level vitti: in the trace and the summary (got {out!r:.200})')

        # 5. malformed specs: the usage, nothing written
        (t / 'x.sm').write_text('mukhya() {\n    likha(1)\n}\n', encoding='utf-8')
        for spec in ('--debug=', '--debug=a,', '--debug=,a', '--debug=@', '--debug=@5-2', '--debug=x@3y'):
            before = set(os.listdir(t))
            c = subprocess.run([comp, spec, 'x.sm', 'x.bin'], capture_output=True, timeout=30, cwd=t)
            check(set(os.listdir(t)) == before, f'malformed {spec}: the usage, nothing written (exit {c.returncode})')

        # 7. R49: repeated flags in any order, and --debug-from=<N>
        def trace_of(*flags):
            pp, bb = t / 'p.sm', t / 'p.bin'
            pp.write_text(PROG, encoding='utf-8')
            if bb.exists():
                bb.unlink()
            c = subprocess.run([comp, *flags, str(pp), str(bb)], capture_output=True, timeout=60, cwd=ROOT)
            if c.returncode != 0 or not bb.exists():
                return None
            o = subprocess.run([str(bb)], capture_output=True, timeout=30).stdout.decode('utf-8', 'replace')
            return o.split('[shodhan] samapti')[0]
        one = trace_of('--debug=yoga,i@11-14')
        check(one is not None and one == trace_of('--debug=yoga', '--debug=i', '--debug-from=11', '--debug=@11-14')
              and one == trace_of('--debug=i@11-14', '--debug=yoga'),
              'R49: --debug=yoga --debug=i --debug-from=11 ... is the same trace as --debug=yoga,i@11-14, in any order')
        two = trace_of('--debug-from=14')
        check(two is not None and two == trace_of('--debug=@14') and two.startswith('[shodhan] pankti 14\n'),
              f'R49: --debug-from=14 is --debug=@14 (got {two!r:.60})')
        for spec in ('--debug-from=', '--debug-from=x', '--debug-from=0'):
            before = set(os.listdir(t))
            c = subprocess.run([comp, '--debug=yoga', spec, 'x.sm', 'x.bin'], capture_output=True, timeout=30, cwd=t)
            check(set(os.listdir(t)) == before, f'R49: malformed {spec} after --debug=yoga: the usage, nothing written')
        (t / 'dv.sm').write_text('मुख्य()\n    वित्ति योग = 4।\n    लिख(योग)।\n', encoding='utf-8')
        c = subprocess.run([comp, '--debug=योग', '--debug', '--debug-from=3', 'dv.sm', 'dv.bin'], capture_output=True,
                           timeout=30, cwd=t, env={**os.environ, 'SUTRAM_LANG': 'sanskrit'})
        out = subprocess.run([str(t / 'dv.bin')], capture_output=True, timeout=30).stdout.decode() if c.returncode == 0 else ''
        check(out.startswith('[shodhan] pankti 3\n    योग = 4\n4\n'), 'R49: after two flags are dropped the environment is '
              f'still read (SUTRAM_LANG=sanskrit compiles Devanagari) (got {out!r:.60})')

        # 6. a wrong answer, found
        bad = SIN.replace('SIGN', '-')
        good = SIN.replace('SIGN', '+')
        rc, out = build(bad, None)
        check(rc == 0 and out == '0.757068\n', f'the sign error gives a wrong sin(-4.0): {out.strip()!r} '
              f'(true: 0.756802)')
        rc, out = build(bad, '--debug=y@5-12')
        want = ('[shodhan] pankti 6\n    y = -4.000000\n[shodhan] pankti 9\n    y = -4.000000\n'
                '[shodhan] pankti 10\n    y = -4.000000\n[shodhan] pankti 12\n    y = -10.283185\n0.757068\n')
        trace = out.split('[shodhan] samapti')[0] if rc == 0 else ''
        check(trace == want, 'the trace finds it: y = -4.000000 before line 10, y = -10.283185 (outside [-pi, pi]) '
              f'at line 12 - line 10 made the first wrong value (got {trace!r:.200})')
        rc, out = build(good, '--debug=y@5-12')
        trace = out.split('[shodhan] samapti')[0] if rc == 0 else ''
        check('    y = 2.283185\n' in trace and trace.endswith('0.756802\n'),
              f'with the sign corrected: y = 2.283185 and sin(-4.0) = 0.756802 (got {trace[-60:]!r})')

    print(f'r46 debug usable: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
