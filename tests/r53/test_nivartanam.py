#!/usr/bin/env python3
"""ROUND-53: `nivartanam` (निवर्तनम्, "returning") is the return keyword; `prati` (प्रति) stays as its alias.

The lexer maps all four spellings to the one token KW_NIVARTANAM, so the parser cannot tell which arrived:

  1. THE DECISIVE TEST: three programs written with `prati`, and the same three with `nivartanam`, compile to
     byte-identical binaries (a function value, recursion with several returns, and examples/249_r25_phal.sm with
     `prati siddhi(...)` / `prati dosh(...)`), and run to the same output.
  2. DEVANAGARI: `प्रति` and `निवर्तनम्` give the same binary, with and without --lang sanskrit, and the same binary
     as the Latin spelling.
  3. THE WORD: `निवर्तनम्` is the 27 bytes the owner confirmed, decoded from the compiler's own table
     (src/sutram_compiler.asm, kw_dev_nivartanam) - not typed from memory.
  4. IT IS A KEYWORD: `vitti nivartanam = 1` is refused, as `vitti prati = 1` is.

No network; writes only to a temporary directory.
usage: python3 -B tests/r53/test_nivartanam.py [--compiler ./sutram_compiler]
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
WORD = 'निवर्तनम्'

PROGRAMS = [
    'prakriya dviguna(n) {\n    prati n * 2\n}\nmukhya() {\n    likha(dviguna(21))\n}\n',
    ('prakriya kramgun(n) {\n    yadi (n <= 1) {\n        prati 1\n    }\n    prati n * kramgun(n - 1)\n}\n'
     'prakriya chinha(x) {\n    yadi (x < 0) { prati 0 - 1 }\n    yadi (x == 0) { prati 0 }\n    prati 1\n}\n'
     'mukhya() {\n    likha(kramgun(10))\n    likha(chinha(0 - 5))\n    likha(chinha(7))\n}\n'),
    (ROOT / 'examples' / '249_r25_phal.sm').read_text(encoding='utf-8'),
]


def main(argv) -> int:
    comp = argv[argv.index('--compiler') + 1] if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    with tempfile.TemporaryDirectory(prefix='r53-') as td:
        t = Path(td)

        def build(src, name, lang=None):
            p, b = t / f'{name}.sm', t / f'{name}.bin'
            p.write_text(src, encoding='utf-8')
            c = subprocess.run([comp] + (['--lang', lang] if lang else []) + [str(p), str(b)], capture_output=True,
                               timeout=60, cwd=ROOT)
            if c.returncode != 0 or not b.exists():
                return None, None
            r = subprocess.run([str(b)], capture_output=True, timeout=30)
            return b.read_bytes(), r.stdout

        # 1. the decisive test
        for i, src in enumerate(PROGRAMS, 1):
            n = len(re.findall(r'\bprati\b', src))
            a, ao = build(src, f'a{i}')
            b, bo = build(re.sub(r'\bprati\b', 'nivartanam', src), f'b{i}')
            check(a is not None and a == b and ao == bo,
                  f'program {i}: {n} returns written `prati` and `nivartanam` give the same binary '
                  f'({len(a) if a else "-"} B) and the same output')

        # 2. Devanagari
        dev = 'प्रक्रिया द्विगुण(न) {\n    प्रति न * 2।\n}\nमुख्य() {\n    लिख(द्विगुण(21))।\n}\n'
        lat, _ = build(PROGRAMS[0], 'lat')
        for lang in (None, 'sanskrit'):
            x, _ = build(dev, 'dx', lang)
            y, _ = build(dev.replace('प्रति', WORD), 'dy', lang)
            check(x is not None and x == y, f'Devanagari{" under --lang sanskrit" if lang else ""}: प्रति and {WORD} '
                  'give the same binary')
        x, _ = build(dev.replace('प्रति', WORD), 'dz')
        check(x is not None and x == lat, f'{WORD} and Latin nivartanam give the same binary')

        # 3. the word, from the compiler's own table
        asm = (ROOT / 'src' / 'sutram_compiler.asm').read_text(encoding='utf-8')
        m = re.search(r'kw_dev_nivartanam db ([0-9A-Fa-fx, ]+?), 0', asm)
        raw = bytes(int(v, 16) for v in m.group(1).split(',')) if m else b''
        check(raw.decode('utf-8', 'replace') == WORD and len(raw) == 27,
              f'kw_dev_nivartanam decodes to {raw.decode("utf-8", "replace")} ({len(raw)} bytes): the confirmed word')

        # 4. a keyword, not a name
        for word in ('nivartanam', 'prati'):
            r, _ = build(f'mukhya() {{\n    vitti {word} = 1\n    likha(1)\n}}\n', f'kw_{word}')
            check(r is None, f'`vitti {word} = 1` is refused: {word} is a keyword')

    print(f'r53 nivartanam: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
