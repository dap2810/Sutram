#!/usr/bin/env python3
"""ROUND-82: a kosh made inside a mandapa lives as long as the block.

Each case is a program and what it must do: print exactly OUT and exit 0, or stop with E_KOSH_MANDAPA
(exit 1) after printing what came before;
or (R107) be refused when compiled. Last line: `r82 kosh-mandapa: N checks, M failed`.

usage: python3 -B tests/r82_kosh_mandapa/test_kosh_mandapa.py [--compiler PATH]
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CASES = [
    ('a kosh in a block, grown and read through a prakriya, a value returned',
     'prakriya padh(kosh k, i) {\n    nivartanam k[i]\n}\nprakriya yog_karo(n) {\n    vitti s = 0\n    mandapa {\n        kosh k[2]\n        vitti i = 1\n        yavat (i <= n) {\n            kosh_push(k, i * i)\n            i = i + 1\n        }\n        s = padh(k, 0) + padh(k, n - 1) + kosh_len(k)\n    }\n    nivartanam s\n}\nmukhya() {\n    likha(yog_karo(10))\n}\n',
     '111\n', 0),
    ('a kosh outside any block beside one inside',
     'prakriya padh(kosh k, i) {\n    nivartanam k[i]\n}\nmukhya() {\n    kosh bahar[2]\n    kosh_push(bahar, 7)\n    vitti s = 0\n    mandapa {\n        kosh k[2]\n        kosh_push(k, 1)\n        s = padh(k, 0) + padh(bahar, 0)\n    }\n    likha(s + padh(bahar, 0))\n}\n',
     '15\n', 0),
    ('recursion: a live kosh passed down five levels, each with a block kosh of its own',
     'prakriya padh(kosh k, i) {\n    nivartanam k[i]\n}\nprakriya gahra(kosh k, d) {\n    yadi (d == 0) { nivartanam padh(k, 0) }\n    vitti s = 0\n    mandapa {\n        kosh m[2]\n        kosh_push(m, d)\n        s = gahra(k, d - 1) + padh(m, 0) + gahra(m, 0)\n    }\n    nivartanam s\n}\nmukhya() {\n    vitti s = 0\n    mandapa {\n        kosh k[2]\n        kosh_push(k, 100)\n        s = gahra(k, 5)\n    }\n    likha(s)\n}\n',
     '130\n', 0),
    ('kosh dasham in a block',
     'prakriya padh(kosh dasham k, i) {\n    nivartanam k[i]\n}\nmukhya() {\n    dasham s = 0.0\n    mandapa {\n        kosh dasham k[1]\n        kosh_push(k, 1.5)\n        kosh_push(k, 2.25)\n        s = padh(k, 0) + padh(k, 1)\n    }\n    likha(s)\n}\n',
     '3.750000\n', 0),
    ('read after its block ended: refused, naming its block (R107: the kosh leaves through a prakriya, which the compiler cannot see)',
     'prakriya rakh(kosh k) {\n    nivartanam k\n}\nprakriya padh(kosh k, i) {\n    nivartanam k[i]\n}\nmukhya() {\n    kosh bahar[1]\n    mandapa {\n        kosh k[4]\n        kosh_push(k, 11)\n        kosh_push(k, 22)\n        likha(padh(k, 1))\n        bahar = rakh(k)\n    }\n    likha(padh(bahar, 0))\n}\n',
     'pankti 9 mandape', 1),
    ('left by krama out of a loop, read after: refused (R107: the kosh leaves through a prakriya, which the compiler cannot see)',
     'prakriya rakh(kosh k) {\n    nivartanam k\n}\nprakriya padh(kosh k, i) {\n    nivartanam k[i]\n}\nmukhya() {\n    kosh bahar[1]\n    vitti i = 0\n    yavat (i < 3) {\n        mandapa {\n            kosh k[2]\n            kosh_push(k, i)\n            bahar = rakh(k)\n            krama\n        }\n    }\n    likha(padh(bahar, 0))\n}\n',
     'pankti 11 mandape', 1),
    ('an inner block ended, the outer still running: refused (R107: the kosh leaves through a prakriya, which the compiler cannot see)',
     'prakriya rakh(kosh k) {\n    nivartanam k\n}\nprakriya padh(kosh k, i) {\n    nivartanam k[i]\n}\nmukhya() {\n    mandapa {\n        kosh bahar[1]\n        mandapa {\n            kosh k[2]\n            kosh_push(k, 4)\n            bahar = rakh(k)\n            likha(padh(bahar, 0))\n        }\n        likha(padh(bahar, 0))\n    }\n}\n',
     'pankti 10 mandape', 1),
    ('the same block in the next loop iteration (same slot, new generation): refused (R107: the kosh leaves through a prakriya, which the compiler cannot see)',
     'prakriya rakh(kosh k) {\n    nivartanam k\n}\nprakriya padh(kosh k, i) {\n    nivartanam k[i]\n}\nmukhya() {\n    kosh pichhla[1]\n    mandapa {\n        kosh z[1]\n        kosh_push(z, 9)\n        pichhla = rakh(z)\n    }\n    vitti i = 0\n    yavat (i < 3) {\n        mandapa {\n            kosh k[2]\n            kosh_push(k, i * 10)\n            likha(padh(k, 0))\n            yadi (i > 0) {\n                likha(padh(pichhla, 0))\n            }\n            pichhla = rakh(k)\n        }\n        i = i + 1\n    }\n}\n',
     'pankti 16 mandape', 1),
    ('a sibling block (another slot): refused (R107: the kosh leaves through a prakriya, which the compiler cannot see)',
     'prakriya rakh(kosh k) {\n    nivartanam k\n}\nprakriya padh(kosh k, i) {\n    nivartanam k[i]\n}\nmukhya() {\n    kosh pichhla[1]\n    mandapa {\n        kosh z[1]\n        kosh_push(z, 9)\n        pichhla = rakh(z)\n    }\n    mandapa {\n        kosh y[1]\n        kosh_push(y, 8)\n        likha(padh(y, 0))\n        likha(padh(pichhla, 0))\n    }\n}\n',
     'pankti 9 mandape', 1),
    # R107 (v289): the forms the compiler sees are refused when compiled - E_KOSH_MANDAPA, nothing is built
    ('R107: stored in a variable declared outside the block: refused at compile time',
     'mukhya() {\n    vitti bahar = 0\n    mandapa {\n        kosh k[4]\n        bahar = k\n    }\n}\n',
     'bahya-vittau', 2),
    ('R107: written into memory (kosh_push of the kosh itself): refused at compile time',
     'mukhya() {\n    kosh bahar[1]\n    mandapa {\n        kosh k[4]\n        kosh_push(bahar, k)\n    }\n}\n',
     'smritau', 2),
    ('R107: returned from inside its block: refused at compile time',
     'prakriya f() {\n    mandapa {\n        kosh k[4]\n        nivartanam k\n    }\n    nivartanam 0\n}\nmukhya() {\n    likha(f())\n}\n',
     'nivartanam', 2),
]


def main(argv):
    comp = os.path.abspath(argv[argv.index('--compiler') + 1]) if '--compiler' in argv else \
        os.path.join(ROOT, 'sutram_compiler')
    tmp = tempfile.mkdtemp(prefix='r82-')
    checks = failed = 0
    for why, src, want, code in CASES:
        sp, bp = os.path.join(tmp, 'p.sm'), os.path.join(tmp, 'p.bin')
        open(sp, 'w').write(src)
        if os.path.exists(bp):
            os.remove(bp)
        c = subprocess.run([comp, sp, bp], capture_output=True, text=True, timeout=60, cwd=ROOT)
        checks += 1
        if code == 2:               # R107: refused when compiled, with E_KOSH_MANDAPA and the form
            msg = c.stdout + c.stderr
            if not (c.returncode == 1 and not os.path.exists(bp) and 'E_KOSH_MANDAPA' in msg and want in msg):
                failed += 1; print(f'FAIL  {why}: exit {c.returncode}, {msg.strip()[:120]!r}')
            continue
        if c.returncode != 0 or not os.path.exists(bp):
            failed += 1; print(f'FAIL  {why}: did not compile: ' + (c.stdout + c.stderr).strip()[:100]); continue
        r = subprocess.run([bp], capture_output=True, text=True, timeout=20)
        if code == 0:
            ok = r.stdout == want and r.returncode == 0
        else:                       # want: the block's line, as the message names it
            ok = r.returncode == 1 and 'E_KOSH_MANDAPA' in r.stdout and want in r.stdout
        if not ok:
            failed += 1; print(f'FAIL  {why}: exit {r.returncode}, printed {r.stdout[:120]!r}')
    print(f'r82 kosh-mandapa: {checks} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
