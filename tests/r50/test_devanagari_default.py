#!/usr/bin/env python3
"""ROUND-50: Devanagari Sanskrit needs no flag (W1), and prati has one Devanagari form (W2).

  1. A program in Devanagari - every keyword and builtin from lang/sanskrit.lang - compiles
     with no --lang and no SUTRAM_LANG, to the same bytes as the same program in Latin.
  2. Only the KEYWORDS come by default: the compile prints no pack banner and the default
     messages, exactly as for a Latin program.
  3. prati: प्रति is the keyword; the old spellings प्रतियाति, प्रत्यायति and प॰ are not
     (each is now an ordinary, undeclared name).
  4. A named pack is used alone, as before: --lang sanskrit gives the same program, with the
     banner; --lang gujarati does not take the Sanskrit Devanagari words.
Linux only. No network.
usage: python3 -B tests/r50/test_devanagari_default.py [--compiler PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

LATIN = '''prakriya yog(a, b) {
    vitti s = a + b
    prati s
}
mukhya() {
    vitti x = 5
    yadi (x > 3) {
        likha(yog(x, 10))
    } anya {
        likha(0)
    }
    vitti i = 0
    yavat (i < 2) {
        likha(i)
        i = i + 1
    }
}
'''
DEVA = '''प्रक्रिया yog(a, b) {
    वित्ति s = a + b
    प्रति s
}
मुख्य() {
    वित्ति x = 5
    यदि (x > 3) {
        लिख(yog(x, 10))
    } अन्यत्र {
        लिख(0)
    }
    वित्ति i = 0
    यावत् (i < 2) {
        लिख(i)
        i = i + 1
    }
}
'''


def main(argv) -> int:
    comp = os.path.abspath(argv[argv.index('--compiler') + 1]) if '--compiler' in argv else str(ROOT / 'sutram_compiler')
    work = Path(tempfile.mkdtemp(prefix='r50-deva-'))
    env = {k: v for k, v in os.environ.items() if k != 'SUTRAM_LANG'}
    passed = failed = 0

    def check(ok, what):
        nonlocal passed, failed
        if ok:
            passed += 1
        else:
            failed += 1
            print('FAIL', what)

    def build(text, name, extra=()):
        src, exe = work / (name + '.sm'), work / name
        src.write_text(text, encoding='utf-8')
        exe.unlink(missing_ok=True)
        r = subprocess.run([comp, *extra, str(src), str(exe)], capture_output=True, cwd=ROOT, env=env, timeout=60)
        return (exe.read_bytes() if exe.exists() else None), r.stdout.decode('utf-8', 'replace')

    lat, lat_msg = build(LATIN, 'lat')
    deva, deva_msg = build(DEVA, 'deva')
    check(lat is not None, f'the Latin program compiles: {lat_msg!r}')
    check(deva is not None and deva == lat, f'the Devanagari program, no flag, gives the Latin bytes: {deva_msg!r}')
    check(deva_msg == lat_msg and 'Siddh' in deva_msg,
          f'no flag: no banner, the default message: {deva_msg!r} vs {lat_msg!r}')
    out = subprocess.run([str(work / 'deva')], capture_output=True).stdout if deva else b''
    check(out == b'15\n0\n1\n', f'the Devanagari program runs: {out!r}')

    for old in ('प्रतियाति', 'प्रत्यायति', 'प॰'):
        exe, msg = build(DEVA.replace('प्रति s', f'{old} s'), 'old')
        check(exe is None and 'E_UNDEFINED_NAME' in msg, f'{old} is no longer a keyword: {msg[:90]!r}')

    sa, sa_msg = build(DEVA, 'sa', ('--lang', 'sanskrit'))
    check(sa == lat and 'sanskrit' in sa_msg, f'--lang sanskrit: the same bytes, with the banner: {sa_msg[:60]!r}')
    gu, gu_msg = build(DEVA, 'gu', ('--lang', 'gujarati'))
    check(gu is None, '--lang gujarati is used alone: it does not take the Sanskrit Devanagari words')

    print(f'r50 devanagari default: {passed + failed} checks, {passed} passed, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
