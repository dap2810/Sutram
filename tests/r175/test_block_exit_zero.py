#!/usr/bin/env python3
"""R175 (Sarvam ROUND-175 WS2): memory a mandapa gives up is zero before an ordinary nirmmita can be handed it.

The defect (found R172, in v315): the field is 1 GiB; a block's nirmmita takes from its top, growing down, and
goes back when the block ends; an ordinary nirmmita takes from the bottom, growing up, is bounded by where the
block's side is NOW, and is not zeroed - memory never used arrives zeroed. So once a block had used the top
600 MB and ended, an ordinary nirmmita(600000000) reached 126 MB of what the block wrote and read it:
15,782,272 words of the block's data in a buffer the reference calls zeroed.

From v320 every way out of a block zeroes what the block took before the cursor goes back.

Each case: a block takes nirmmita(600000000) and writes 77 into its lowest 15,782,272 words - exactly the part an
ordinary 600 MB buffer will reach - and is left one way; then nirmmita(600000000) outside any block, whose words
59,217,728 .. 74,999,999 are those same bytes, is read before it is written. Every word must be 0.
The ways out: the block's last line, krama, agrim, nivartanam with a value, nivartanam without one, a failure
passed on by prasar, and a nested block left through its outer block's nivartanam.
Each program touches about 600 MB; they run one after another.

Usage: python3 tests/r175/test_block_exit_zero.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0
FILL = ('vitti p = nirmmita(600000000)\nchakra i = 0 tak 15782271 {\n    p[i] = 77\n}\n')
READ = ('    vitti q = nirmmita(600000000)\n    vitti n = 0\n    chakra i = 59217728 tak 74999999 {\n        yadi (q[i] != 0) {\n            n = n + 1\n        }\n    }\n'
        '    likha(n, "\\n")\n')


def ind(text, n):
    return ''.join(' ' * n + l + '\n' for l in text.strip('\n').split('\n'))


CASES = [
    ('end', "the block's last line", 'mukhya() {\n    mandapa {\n' + ind(FILL, 8) + '    }\n' + READ + '}\n'),
    ('krama', 'krama', 'mukhya() {\n    chakra j = 1 tak 3 {\n        mandapa {\n' + ind(FILL, 12) + '            krama\n        }\n    }\n' + READ + '}\n'),
    ('agrim', 'agrim', 'mukhya() {\n    chakra j = 1 tak 1 {\n        mandapa {\n' + ind(FILL, 12) + '            agrim\n        }\n    }\n' + READ + '}\n'),
    ('nivartanam', 'nivartanam with a value',
     'prakriya kar() {\n    mandapa {\n' + ind(FILL, 8) + '        nivartanam p[0]\n    }\n    nivartanam 0\n}\nmukhya() {\n    vitti z = kar()\n' + READ + '}\n'),
    ('nivartanam-bare', 'nivartanam without a value',
     'prakriya kar() {\n    mandapa {\n' + ind(FILL, 8) + '        nivartanam\n    }\n}\nmukhya() {\n    kar()\n' + READ + '}\n'),
    ('prasar', 'a failure passed on by prasar',
     'prakriya vifal() {\n    nivartanam dosh(7)\n}\nprakriya kar() {\n    mandapa {\n' + ind(FILL, 8)
     + '        vitti x = prasar vifal()\n        nivartanam siddhi(x)\n    }\n    nivartanam siddhi(0)\n}\n'
       'mukhya() {\n    vitti f = 0\n    yadi dosh (e = kar()) {\n        f = e\n    }\n' + READ + '}\n'),
    ('nested', "an inner block left through the outer block's nivartanam",
     'prakriya kar() {\n    mandapa {\n        vitti t = nirmmita(64)\n        mandapa {\n' + ind(FILL, 12)
     + '            nivartanam p[0]\n        }\n    }\n    nivartanam 0\n}\nmukhya() {\n    vitti z = kar()\n' + READ + '}\n'),
]

SMALL = ('mukhya() {\n    vitti bad = 0\n    chakra j = 1 tak 100000 {\n        mandapa {\n            vitti t = nirmmita(64)\n'
         '            chakra i = 0 tak 7 {\n                yadi (t[i] != 0) {\n                    bad = bad + 1\n                }\n                t[i] = j\n            }\n        }\n    }\n'
         '    likha(bad, "\\n")\n}\n')


def check(ok, what):
    global checks, fails
    checks += 1
    print(('ok    ' if ok else 'FAIL  ') + what)
    fails += not ok


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors='replace', timeout=900)
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    compiler = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        compiler = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    d = tempfile.mkdtemp(prefix='r175z_')
    try:
        for name, what, src in CASES + [('small', '', SMALL)]:
            open(os.path.join(d, name + '.sm'), 'w').write(src)
            rc, out = run([compiler, name + '.sm', name + '.bin'], d)
            if rc != 0 or not os.path.exists(os.path.join(d, name + '.bin')):
                check(False, f'{name}: compiles ({out[:100]})')
                continue
            rc, out = run([os.path.join(d, name + '.bin')], d)
            os.remove(os.path.join(d, name + '.bin'))
            if name == 'small':
                check(rc == 0 and out == '0', f'small: 100,000 blocks, each reading its nirmmita(64) before writing it - words that were not 0: {out[:40]}')
            else:
                check(rc == 0 and out == '0', f'{name}: the block left by {what} - an ordinary nirmmita over the same bytes reads {out[:40]} words that are not 0 (of 15,782,272)')
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'r175 block exit zero: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
