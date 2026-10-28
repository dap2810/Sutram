#!/usr/bin/env python3
"""ROUND-52: four additions; no existing program's output changes.

  1. likha WITH UP TO SIX VALUES: likha("x = ", x, ", y = ", y) prints `x = 42, y = 7` and a newline. Each value
     but the last prints as lkhb (a number, no newline) or likha (a string literal); the last as likha, so the line
     ends the way likha(a, b) ends it. Three values take this form only when the first is a string literal: every
     three-argument call in the tree passes 1 or an fd first and stays a raw write. Seven values are refused.
  2. lkhb ON A DASHAM prints the number (2.500000), not its IEEE-754 bits (4612811918334230528).
  3. THE yoj HINT: a call to a library prakriya without its `yoj` prints, after `agyat prakriya: <name>`, the line
     `  Sanket: '<name>' '<module>' ghatake asti; 'yoj <module>' iti likhatu` - in the ordinary compile and in
     --check. A name in no module gets no hint.
  4. arabhya ... paryantam: `chakra i = a arabhya b paryantam` compiles to the same binary as `chakra i = a tak b`;
     neither word is reserved; `arabhya` without `paryantam` is a grammar error.

No network; writes only to a temporary directory.
usage: python3 -B tests/r52/test_r52.py [--compiler ./sutram_compiler]
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def main(argv) -> int:
    comp = argv[argv.index('--compiler') + 1] if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    with tempfile.TemporaryDirectory(prefix='r52-') as td:
        t = Path(td)

        def build(src, name='p', check_mode=False):
            p, b = t / f'{name}.sm', t / f'{name}.bin'
            p.write_text(src, encoding='utf-8')
            if b.exists():
                b.unlink()
            cmd = [comp, '--check', str(p)] if check_mode else [comp, str(p), str(b)]
            c = subprocess.run(cmd, capture_output=True, timeout=60, cwd=ROOT)
            msg = (c.stdout + c.stderr).decode('utf-8', 'replace')
            if check_mode or c.returncode != 0 or not b.exists():
                return None, msg, None
            r = subprocess.run([str(b)], capture_output=True, timeout=30)
            return r.stdout.decode('utf-8', 'replace'), msg, b.read_bytes()

        # 1. likha with up to six values
        out, _, _ = build('mukhya() {\n    vitti x = 42\n    vitti y = 7\n    dasham d = 2.5\n'
                          '    likha("x = ", x, ", y = ", y)\n'
                          '    likha("d = ", d, " and x+y = ", x + y)\n'
                          '    likha("a", "b", "c", "d", "e", 6)\n'
                          '    likha("three: ", x, "!\\n")\n'
                          '    likha(x, " ", y, "\\n")\n'
                          '    likha("two: ", x)\n'
                          '    likha(1, "raw\\n", 4)\n}\n')
        want = 'x = 42, y = 7\nd = 2.500000 and x+y = 49\nabcde6\nthree: 42!\n42 7\ntwo: 42\nraw\n'
        check(out == want, f'likha with 3 to 6 values prints one line; likha(a, b) and the raw 3-argument write are '
              f'unchanged (got {out!r})')
        out, msg, _ = build('mukhya() {\n    likha("a", 1, "b", 2, "c", 3, "d")\n}\n')
        check(out is None, 'likha with seven values is refused')

        # 2. lkhb on a dasham
        out, _, _ = build('mukhya() {\n    dasham d = 2.5\n    lkhb(d)\n    likha("|\\n")\n    lkhb(0.0 - 1.25)\n'
                          '    likha("|\\n")\n    lkhb(7)\n    likha("|\\n")\n}\n')
        check(out == '2.500000|\n-1.250000|\n7|\n', f'lkhb prints a dasham as a number, no newline; an integer as '
              f'before (got {out!r})')

        # 3. the yoj hint
        prog = 'mukhya() {\n    mala a[8]\n    brihat_yuj(a, a, a, 8)\n}\n'
        hint = "  Sanket: 'brihat_yuj' 'brihat' ghatake asti; 'yoj brihat' iti likhatu\n"
        _, msg, _ = build(prog)
        check(msg.startswith('Sutram Error: agyat prakriya: brihat_yuj\n' + hint),
              f'the yoj hint after agyat prakriya (got {msg!r:.160})')
        _, msg, _ = build(prog, check_mode=True)
        check(hint in msg, '--check prints the same hint')
        _, msg, _ = build('mukhya() {\n    nahi_asti(1)\n}\n')
        check('agyat prakriya: nahi_asti' in msg and 'Sanket' not in msg, 'a name in no module: no hint')
        out, _, _ = build('yoj brihat\n' + prog.replace('brihat_yuj(a, a, a, 8)', 'likha(brihat_yuj(a, a, a, 8))'))
        check(out is not None, 'with `yoj brihat` the same call compiles')

        # 4. arabhya ... paryantam
        a, _, ab = build('mukhya() {\n    chakra i = 0 tak 4 {\n        likha(i)\n    }\n}\n', 'a')
        b, _, bb = build('mukhya() {\n    chakra i = 0 arabhya 4 paryantam {\n        likha(i)\n    }\n}\n', 'b')
        check(ab is not None and ab == bb and a == '0\n1\n2\n3\n4\n',
              'chakra i = 0 arabhya 4 paryantam: the same binary as chakra i = 0 tak 4')
        out, _, _ = build('mukhya() {\n    vitti arabhya = 2\n    vitti paryantam = 5\n'
                          '    chakra i = arabhya arabhya paryantam paryantam {\n        likha(i)\n    }\n}\n')
        check(out == '2\n3\n4\n5\n', f'arabhya and paryantam are not reserved: names, even inside the loop '
              f'(got {out!r})')
        out, msg, _ = build('mukhya() {\n    chakra i = 0 arabhya 4 {\n        likha(i)\n    }\n}\n')
        check(out is None and 'vyakaran' in msg, 'arabhya without paryantam is a grammar error')

    print(f'r52: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
