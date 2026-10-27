#!/usr/bin/env python3
"""ROUND-43: a keyword is never matched inside a longer word.

`prati` is `return`; `vartani_pratilip` must be an ordinary name. The lexer reads a whole word first
(ASCII letters, digits, `_`, and every 3-byte UTF-8 scalar - so a Devanagari letter, a combining vowel sign,
anusvara or virama are all part of the word) and only then compares the complete word with the keyword
table. These cases pin that, generated from lang/sanskrit.lang so a keyword added later is tested too:

  1. WS1: a prakriya named vartani_pratilip, called, returns its value.
  2. every Latin keyword K (column 2 of lang/sanskrit.lang): K+letter, K+_, K+digit and K+Devanagari letter
     are ordinary names (vitti NAME = 41; likha(NAME + 1) prints 42).
  3. every Devanagari keyword D (column 1), under --lang sanskrit: D + a Devanagari letter, a letter+virama,
     anusvara, a vowel sign, a Latin letter, _, a Devanagari digit and an ASCII digit are ordinary names.
  4. CONTROLS, so the test can fail: the keyword ITSELF as a name is refused (vitti prati = 1 does not
     compile), in both scripts. Without these a lexer that recognised no keyword at all would pass.

A candidate name that is itself a keyword (शब्द + म् = शब्दम्, a builtin alias) is skipped in 2-3: it is a
keyword, not a prefix case.
No network; writes only to a temporary directory.
usage: python3 -B tests/r43/test_keyword_boundary.py [--compiler ./sutram_compiler]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

LATIN_SUFFIXES = (('x', 'letter'), ('_y', 'underscore'), ('2', 'digit'), ('क', 'Devanagari letter'))
DEVA_SUFFIXES = (('क', 'letter'), ('म्', 'letter+virama'), ('ं', 'anusvara'), ('ि', 'vowel sign'),
                 ('X', 'Latin letter'), ('_य', 'underscore'), ('२', 'Devanagari digit'), ('7', 'ASCII digit'))


def keywords():
    deva, latin = [], []
    for line in (ROOT / 'lang' / 'sanskrit.lang').read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        d, lat = line.split()[:2]
        deva.append(d)
        latin.append(lat)
    return sorted(set(deva)), sorted(set(latin))


def main(argv) -> int:
    comp = argv[argv.index('--compiler') + 1] if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    deva, latin = keywords()
    checks = fails = 0

    with tempfile.TemporaryDirectory(prefix='r43-') as td:
        t = Path(td)

        def build_run(src: str, lang: str | None):
            p, b = t / 'p.sm', t / 'p.bin'
            p.write_text(src, encoding='utf-8')
            if b.exists():
                b.unlink()
            cmd = [comp] + (['--lang', lang] if lang else []) + [str(p), str(b)]
            c = subprocess.run(cmd, capture_output=True, timeout=30)
            if c.returncode != 0:
                return None, (c.stdout + c.stderr).decode('utf-8', 'replace')
            r = subprocess.run([str(b)], capture_output=True, timeout=10)
            return r.returncode, r.stdout.decode('utf-8', 'replace').strip()

        def check(ok: bool, what: str):
            nonlocal checks, fails
            checks += 1
            if not ok:
                fails += 1
                print('FAIL  ' + what)

        # 1. the case the round is about
        rc, out = build_run('prakriya vartani_pratilip(a)\n    prati a + 1\n\nmukhya()\n'
                            '    likha(vartani_pratilip(8))\n', None)
        check(rc == 0 and out == '9', f'WS1: prakriya vartani_pratilip(8) returns 9 (got rc={rc} {out!r:.80})')
        if fails == 0:
            print('PASS  WS1: a prakriya named vartani_pratilip compiles, is called, returns 9')

        # 2. every Latin keyword followed by a word character
        n0 = fails
        for k in latin:
            for suf, tag in LATIN_SUFFIXES:
                name = k + suf
                if name in latin:
                    continue
                rc, out = build_run(f'mukhya()\n    vitti {name} = 41\n    likha({name} + 1)\n', None)
                check(rc == 0 and out == '42', f'latin {k} + {tag}: {name} is a name (got rc={rc} {out!r:.80})')
        if fails == n0:
            print(f'PASS  {len(latin)} Latin keywords x {len(LATIN_SUFFIXES)} continuations: each is an ordinary name')

        # 3. every Devanagari keyword followed by a word character, under --lang sanskrit
        n0 = fails
        for d in deva:
            for suf, tag in DEVA_SUFFIXES:
                name = d + suf
                if name in deva:
                    continue
                rc, out = build_run(f'मुख्य()\n    वित्ति {name} = 41।\n    लिख({name} + 1)।\n', 'sanskrit')
                check(rc == 0 and out == '42', f'deva {d} + {tag}: {name} is a name (got rc={rc} {out!r:.80})')
        if fails == n0:
            print(f'PASS  {len(deva)} Devanagari keywords x {len(DEVA_SUFFIXES)} continuations: each is an ordinary name')

        # 4. controls: the keyword itself is NOT a name
        n0 = fails
        for k in ('prati', 'yadi', 'mukhya', 'vitti', 'kosh'):
            rc, out = build_run(f'mukhya()\n    vitti {k} = 41\n    likha(1)\n', None)
            check(rc is None, f'control: the keyword {k} itself is refused as a name (it compiled)')
        for d in ('प्रतियाति', 'यदि', 'कोश', 'प॰'):
            rc, out = build_run(f'मुख्य()\n    वित्ति {d} = 41।\n    लिख(1)।\n', 'sanskrit')
            check(rc is None, f'control: the keyword {d} itself is refused as a name (it compiled)')
        if fails == n0:
            print('PASS  controls: 9 keywords, Latin and Devanagari, are each refused as a name')

    print(f'r43 keyword boundary: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
