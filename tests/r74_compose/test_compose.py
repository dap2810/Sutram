#!/usr/bin/env python3
"""R74: the memory model as a whole - five compositions, each with a number.

    python3 -B tests/r74_compose/test_compose.py --compiler ./sutram_compiler

  1. c1_kosh_outside: a block in a loop pushes 1,000,000 values into a kosh declared outside it.
     The kosh keeps every value (length, sum, first, last); the scratch is released: peak RSS
     below 16 MB (the kosh itself is 8 MB), against above 48 MB for the control without the block.
  2. c2_param: a prakriya given a scratch pointer returns the sum of its data (10): allowed and
     right. One that returns the pointer plus 8 compiles too - the stated blind spot, pinned.
  3. c3_siblings: two sibling blocks, 1,000,000 times: the second never sees the first's data
     (dirty = 0) and memory stays flat (below 4 MB).
  4. c4_100mb: a 100 MB block, every page written, twenty times: correct (190) and peak RSS
     below 120 MB (twenty passes reuse the same 100 MB). c4_too_big: 1,200 MB in one block
     stops with `kshetra purnam - mandapa-smritih samapta`, exit 1.
  5. c5_recursion: a block in a prakriya recursing 1,000 deep, 1,000 times: every frame's buffer
     intact after its callees return (sum 500500000), peak RSS below 8 MB; the control above 32 MB.
  6. c6_adjacent: the scratch allocator's own writes (the cursor, the zeroing) stay inside each block,
     for every size 1..200 - the part of the redirect the guard-page build cannot see.
Linux ELF only. Last line: `r74 compose: N checks, M failed`.
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MB = 1024
CASES = [  # name, expected output lines, exit, rss test
    ('c1_kosh_outside', ['1000000', '1499998500000', '0 2999997'], 0, lambda r: r < 16 * MB),
    ('c1_kosh_outside_control', ['1000000', '1499998500000', '0 2999997'], 0, lambda r: r > 48 * MB),
    ('c2_param', ['8', '10'], 0, None),
    ('c3_siblings', ['0', '500000500000'], 0, lambda r: r < 4 * MB),
    ('c4_100mb', ['190'], 0, lambda r: r < 120 * MB),
    ('c4_too_big', ['Sutram Error: kshetra purnam - mandapa-smritih samapta'], 1, None),
    ('c5_recursion', ['500500000'], 0, lambda r: r < 8 * MB),
    ('c5_recursion_control', ['500500000'], 0, lambda r: r > 32 * MB),
    ('c6_adjacent', ['0'], 0, None),
]


def main():
    comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
        else os.path.join(ROOT, 'sutram_compiler')
    work = tempfile.mkdtemp()
    checks = failed = 0
    for name, want, code, rss_ok in CASES:
        out = os.path.join(work, name)
        c = subprocess.run([comp, os.path.join(HERE, name + '.sm'), out], cwd=ROOT, capture_output=True, text=True)
        checks += 1
        if c.returncode != 0:
            failed += 1
            print(f'FAIL  {name}: did not compile: {(c.stdout + c.stderr).strip()[-120:]}')
            continue
        r = subprocess.run(['/usr/bin/time', '-f', '%M', out], capture_output=True, text=True, timeout=120)
        rss = int(r.stderr.strip().split('\n')[-1])
        got = [l.strip() for l in r.stdout.split('\n') if l.strip()]
        ok = got == want and r.returncode == code and (rss_ok is None or rss_ok(rss))
        failed += not ok
        print(('PASS' if ok else 'FAIL') + f'  {name}: output {" / ".join(got)!s}, exit {r.returncode}, peak RSS {rss} KB')
    print(f'r74 compose: {checks} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
