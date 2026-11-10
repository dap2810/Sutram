#!/usr/bin/env python3
"""R173 (Sarvam ROUND-173 WS4): a mala declared in a chakra's own body, proven local, is made once.

Up to v317 `chakra j = 1 tak N { mala m[8] ... }` allocated the mala every pass and kept them all: 80 bytes a pass
(R168). From v318 the first pass allocates; every later pass with the same length finds it in a frame slot and
zeroes its numbers (a mala has no length to reset: every number is readable at once, so each pass must see zeros,
as from a new mala).

Proven local: the declaration is a statement of the loop's own body, the only one of its name, without an
initializer, and in the whole loop the name appears only as the base of an index (m[i], m[i] = v). Any other
appearance - a second name, an argument of a prakriya, nivartanam, a value put into a kosh or a mala - and the mala
is made every pass, as before: no program is newly refused, and no two rows can become one.

The witness is parimana(): each case is compiled with 1 pass and with 20. "once": the same number. "every pass":
more. Every program's sum is right only if each pass saw eight zeros before it wrote.

Usage: python3 tests/r173/test_chakra_mala.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0
POISON = -2401053089206453570


def check(ok, what):
    global checks, fails
    checks += 1
    print(('ok    ' if ok else 'FAIL  ') + what)
    fails += not ok


def loop(body, funcs='', pre='', post=''):
    return (funcs + 'mukhya() {\n    vitti s = 0\n' + pre + '    chakra j = 1 tak NPASS {\n' + body
            + '    }\n' + post + '    likha(s, " ", parimana(), "\\n")\n}\n')


Z = ''.join(f'        s = s + m[{i}]\n' for i in range(8))          # all eight read before any write
W = ''.join(f'        m[{i}] = j + {i}\n' for i in range(8))
USE = '        s = s + m[3]\n'
SUM = sum(j + 3 for j in range(1, 21))                              # 270: zeros read, then m[3] = j + 3

CASES = [
    ('plain', 'mala m[8], read, written, read', True, loop('        mala m[8]\n' + Z + W + USE), SUM),
    ('named-length', 'the length is a variable, the same every pass', True, loop('        mala m[n]\n' + Z + W + USE, pre='    vitti n = 8\n'), SUM),
    ('two', 'two mala in one body', True, loop('        mala m[8]\n        mala q[4]\n' + Z + W + '        q[0] = q[0] + m[3]\n        s = s + q[0]\n'), SUM),
    ('with-kosh', 'a mala and a kosh in one body', True, loop('        mala m[8]\n        kosh k[1]\n' + Z + W + '        kosh_kship(k, m[3])\n        s = s + k[0]\n'), SUM),
    ('agrim', 'agrim after the mala is written', True, loop('        mala m[8]\n' + Z + W + USE + '        yadi (j > 0) {\n            agrim\n        }\n        s = s + 1000000\n'), SUM),
    ('changing-length', 'a length that changes every pass: a new mala each time, as before', False,
     loop('        mala m[j + 7]\n' + Z + W + USE), SUM),
    ('alias', 'a second name: vitti a = m', False, loop('        mala m[8]\n' + Z + W + '        vitti a = m\n        s = s + a[3]\n'), SUM),
    ('to-prakriya', 'given to a prakriya', False,
     loop('        mala m[8]\n' + Z + W + '        s = s + teen(m)\n', funcs='prakriya teen(a) {\n    nivartanam a[3]\n}\n'), SUM),
    ('under-yadi', 'declared under a yadi', False,
     loop('        yadi (j > 0) {\n            mala m[8]\n' + (Z + W + USE).replace('        ', '            ') + '        }\n'), SUM),
    ('yavat', 'a yavat loop', False,
     'mukhya() {\n    vitti s = 0\n    vitti j = 1\n    yavat (j <= NPASS) {\n        mala m[8]\n' + Z + W + USE
     + '        j = j + 1\n    }\n    likha(s, " ", parimana(), "\\n")\n}\n', SUM),
]

# the rows stay their own: a mala put into a kosh every pass is NOT made once - five rows, five malas
ROWS = ('mukhya() {\n    kosh rows[1]\n    chakra j = 1 tak 5 {\n        mala m[2]\n        m[0] = j\n        m[1] = j * 10\n'
        '        kosh_kship(rows, m)\n    }\n    vitti p = rows[0]\n    vitti q = rows[2]\n    vitti r = rows[4]\n'
        '    likha(p[0] + p[1], " ", q[0] + q[1], " ", r[0] + r[1], "\\n")\n}\n')

RED = '''prakriya shabd(a, i) {
    nivartanam a[i]
}
prakriya nav() {
    vitti p = nirmmita(64)
    chakra i = 0 tak 7 {
        p[i] = %d
    }
    nivartanam p
}
prakriya akshat(a) {
    vitti bad = 0
    chakra i = 0 tak 7 {
        yadi (a[i] != %d) {
            bad = bad + 1
        }
    }
    nivartanam bad
}
mukhya() {
    vitti a = nav()
    vitti b = 0
    vitti s = 0
    vitti dirty = 0
    chakra j = 1 tak 1000000 {
        mala m[8]
        yadi (j == 1) {
            b = nav()
        }
        chakra i = 0 tak 7 {
            yadi (m[i] != 0) {
                dirty = dirty + 1
            }
            m[i] = j + i
        }
        s = s + m[7]
    }
    vitti bad = akshat(a) + akshat(b)
    yadi (shabd(a, 8) != 8) {
        bad = bad + 100
    }
    yadi (b - a != 144) {
        bad = bad + 1000
    }
    likha("bad ", bad, " dirty ", dirty, " held ", parimana())
    likha(" sum ", s, "\\n")
}
''' % (POISON, POISON)


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors='replace', timeout=600)
    return p.returncode, (p.stdout + p.stderr).strip()


def build(compiler, d, name, src):
    open(os.path.join(d, name + '.sm'), 'w').write(src)
    rc, out = run([compiler, name + '.sm', name + '.bin'], d)
    return rc == 0 and os.path.exists(os.path.join(d, name + '.bin')), out


def main():
    compiler = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        compiler = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    d = tempfile.mkdtemp(prefix='r173_')
    try:
        for name, what, once, src, want in CASES:
            held = {}
            for n in (1, 20):
                ok, out = build(compiler, d, f'{name}{n}', src.replace('NPASS', str(n)))
                if not ok:
                    check(False, f'{name}: compiles ({out[:90]})')
                    break
                rc, out = run([os.path.join(d, f'{name}{n}.bin')], d)
                parts = out.split()
                if rc != 0 or len(parts) != 2:
                    check(False, f'{name}: runs ({out[:90]}, exit {rc})')
                    break
                held[n] = (int(parts[0]), int(parts[1]))
            else:
                right = held[20][0] == want
                if once:
                    check(right and held[20][1] == held[1][1], f'{name}: {what} - made once: 20 passes hold {held[20][1]}, 1 pass holds {held[1][1]}; sum {held[20][0]}')
                else:
                    check(right and held[20][1] > held[1][1], f'{name}: {what} - made every pass, as before: 20 passes hold {held[20][1]}, 1 pass holds {held[1][1]}; sum {held[20][0]}')
        ok, out = build(compiler, d, 'rows', ROWS)
        rc, out = run([os.path.join(d, 'rows.bin')], d) if ok else (1, out)
        check(rc == 0 and out == '11 33 55', f'rows: a mala put into a kosh every pass - five rows stay five (printed {out[:40]!r})')
        ok, out = build(compiler, d, 'red', RED)
        rc, out = run([os.path.join(d, 'red.bin')], d) if ok else (1, out)
        check(rc == 0 and out.split() == ['bad', '0', 'dirty', '0', 'held', '208', 'sum', str(sum(j + 7 for j in range(1, 1000001)))],
              f'redzones: 64 bytes of 0xDEADBEEFCAFEBABE before the mala\'s length word and after its last number, 1,000,000 passes - both intact, the length word 8, every pass read eight zeros ({out[:70]!r})')
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'r173 chakra mala: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
