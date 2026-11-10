#!/usr/bin/env python3
"""R175 (Sarvam ROUND-175 WS1): a proven-local kosh or mala is made once wherever it is declared in a loop.

v317 / v318 made it once only when the declaration was a statement of a chakra's own body. From v319 the
declaration may also be under a yadi or an anya, in a plain block or in a mandapa inside the loop, at any depth, and
the loop may be a yavat. Not reached: a declaration in a loop inside the loop - that loop has its own entry, and
the kosh is made once each time it starts.

The rule is the same whitelist (the name, in the whole loop, only as an index base or as the kosh a kosh_* built-in
other than kosh_ksham works on; a mala only as an index base). New in v319: the name may be declared more than once
in the loop - a yadi and its anya - and each declaration has its own slot; a declaration that never runs makes
nothing; a kosh reused inside a mandapa gets this pass's block generation in its header (R82).

The witness is parimana(): each case is compiled with 20 passes and with 40. "once": the same number. "every pass":
more. Every sum is right only if each pass began with an empty kosh / a zeroed mala.

Usage: python3 tests/r175/test_nested_made_once.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0


def check(ok, what):
    global checks, fails
    checks += 1
    print(('ok    ' if ok else 'FAIL  ') + what)
    fails += not ok


def chakra(body, funcs=''):
    return funcs + 'mukhya() {\n    vitti s = 0\n    chakra j = 1 tak NPASS {\n' + body + '    }\n    likha(s, " ", parimana(), "\\n")\n}\n'


def yavat(body):
    return 'mukhya() {\n    vitti s = 0\n    vitti j = 1\n    yavat (j <= NPASS) {\n' + body + '        j = j + 1\n    }\n    likha(s, " ", parimana(), "\\n")\n}\n'


def ind(text, n):
    return ''.join(' ' * n + l + '\n' for l in text.strip('\n').split('\n'))


KOSH = 'kosh k[1]\nkosh_kship(k, j)\nkosh_kship(k, 2)\ns = s + k[0] + kosh_gan(k)'        # j + 2 a pass
MALA = 'mala m[4]\ns = s + m[0] + m[3]\nm[0] = j\nm[3] = 1\ns = s + m[0] + m[3]'            # j + 1 a pass


def total(per, n=40, when=lambda j: True):
    return sum(per(j) for j in range(1, n + 1) if when(j))


K = lambda j: j + 2
M = lambda j: j + 1

# (name, what, made once?, source, the sum at 40 passes)
CASES = [
    ('kosh-yadi', 'a kosh under a yadi', True, chakra('        yadi (j > 0) {\n' + ind(KOSH, 12) + '        }\n'), total(K)),
    ('kosh-yadi-sometimes', 'a kosh under a yadi that runs every third pass', True,
     chakra('        yadi (j % 3 == 0) {\n' + ind(KOSH, 12) + '        }\n'), total(K, when=lambda j: j % 3 == 0)),
    ('kosh-anya', 'a kosh under an anya', True,
     chakra('        yadi (j % 2 == 0) {\n            s = s + 0\n        } anya {\n' + ind(KOSH, 12) + '        }\n'), total(K, when=lambda j: j % 2 == 1)),
    ('kosh-both-branches', 'the same name declared in a yadi and in its anya (two capacities): one each', True,
     chakra('        yadi (j % 2 == 0) {\n            kosh t[10]\n            kosh_kship(t, j)\n            s = s + t[0] + kosh_gan(t)\n        } anya {\n'
            '            kosh t[20]\n            kosh_kship(t, j)\n            kosh_kship(t, j)\n            s = s + t[1] + kosh_gan(t)\n        }\n'),
     total(lambda j: j + 1, when=lambda j: j % 2 == 0) + total(lambda j: j + 2, when=lambda j: j % 2 == 1)),
    ('kosh-deep', 'a kosh under a yadi under a yadi', True,
     chakra('        yadi (j > 0) {\n            yadi (j > 1) {\n' + ind(KOSH, 16) + '            }\n        }\n'), total(K, when=lambda j: j > 1)),
    ('kosh-mandapa', 'a kosh in a mandapa inside the loop', True, chakra('        mandapa {\n' + ind(KOSH, 12) + '        }\n'), total(K)),
    ('kosh-mandapa-yadi', 'a kosh under a yadi in a mandapa inside the loop, the block also taking scratch', True,
     chakra('        mandapa {\n            vitti t = nirmmita(256)\n            t[0] = j\n            yadi (t[0] > 0) {\n' + ind(KOSH, 16) + '            }\n        }\n'), total(K)),
    ('mala-yadi', 'a mala under a yadi', True, chakra('        yadi (j > 0) {\n' + ind(MALA, 12) + '        }\n'), total(M)),
    ('mala-mandapa', 'a mala in a mandapa inside the loop', True, chakra('        mandapa {\n' + ind(MALA, 12) + '        }\n'), total(M)),
    ('yavat-kosh', 'a kosh in a yavat loop', True, yavat(ind(KOSH, 8)), total(K)),
    ('yavat-mala-yadi', 'a mala under a yadi in a yavat loop', True, yavat('        yadi (j > 0) {\n' + ind(MALA, 12) + '        }\n'), total(M)),
    ('yadi-alias', 'under a yadi, but given a second name', False,
     chakra('        yadi (j > 0) {\n            kosh k[1]\n            kosh_kship(k, j)\n            vitti a = k\n            s = s + a[0]\n        }\n'), total(lambda j: j)),
    ('mandapa-to-prakriya', 'in a mandapa, but given to a prakriya', False,
     chakra('        mandapa {\n            kosh k[1]\n            kosh_kship(k, j)\n            s = s + dekh(k)\n        }\n',
            funcs='prakriya dekh(kosh q) {\n    nivartanam q[0]\n}\n'), total(lambda j: j)),
]

NEVER = chakra('        yadi (j > 1000000) {\n            kosh k[100]\n            kosh_kship(k, j)\n            mala m[100]\n            s = s + k[0] + m[0]\n        }\n')
INNER = ('mukhya() {\n    vitti s = 0\n    chakra a = 1 tak NOUT {\n        vitti i = 1\n        yavat (i <= NIN) {\n            yadi (i > 0) {\n'
         '                kosh k[1]\n                kosh_kship(k, i)\n                s = s + k[0]\n            }\n            i = i + 1\n        }\n    }\n'
         '    likha(s, " ", parimana(), "\\n")\n}\n')

# the R82 stamp: a kosh made once inside a mandapa carries the generation of the block it is in NOW.
# Layout with R82: 64 bytes at a, then the descriptor's header: a[8] line, a[9] the block's slot, a[10] generation.
STAMP = '''prakriya shabd(a, i) {
    nivartanam a[i]
}
prakriya nav() {
    vitti p = nirmmita(64)
    nivartanam p
}
mukhya() {
    vitti a = nav()
    vitti g1 = 0
    vitti g2 = 0
    vitti slot1 = 0
    vitti ek = 0
    vitti s = 0
    chakra j = 1 tak 3 {
        mandapa {
            kosh k[1]
            kosh_kship(k, j)
            s = s + k[0] + kosh_gan(k)
            yadi (j == 1) {
                g1 = shabd(a, 10)
                slot1 = shabd(a, 9)
            }
            yadi (j == 3) {
                g2 = shabd(a, 10)
                yadi (shabd(a, 9) == slot1) {
                    ek = 1
                }
            }
        }
    }
    vitti changed = 0
    yadi (g1 != g2) {
        changed = 1
    }
    vitti live = 0
    yadi (g1 != 0) {
        live = 1
    }
    likha(s, " ", changed, " ", live)
    likha(" ", ek, " ", parimana(), "\\n")
}
'''


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors='replace', timeout=600)
    return p.returncode, (p.stdout + p.stderr).strip()


def held(compiler, d, name, src):
    open(os.path.join(d, name + '.sm'), 'w').write(src)
    rc, out = run([compiler, name + '.sm', name + '.bin'], d)
    if rc != 0 or not os.path.exists(os.path.join(d, name + '.bin')):
        return None, 'does not compile: ' + out[:90]
    rc, out = run([os.path.join(d, name + '.bin')], d)
    parts = out.split()
    if rc != 0 or len(parts) < 2:
        return None, f'exit {rc}: {out[:90]}'
    return [int(x) for x in parts], ''


def main():
    compiler = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        compiler = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    d = tempfile.mkdtemp(prefix='r175_')
    try:
        for name, what, once, src, want in CASES:
            h20, e1 = held(compiler, d, name + '20', src.replace('NPASS', '20'))
            h40, e2 = held(compiler, d, name + '40', src.replace('NPASS', '40'))
            if h20 is None or h40 is None:
                check(False, f'{name}: {e1 or e2}')
                continue
            right = h40[0] == want
            if once:
                check(right and h40[1] == h20[1] > 0, f'{name}: {what} - made once: 40 passes hold {h40[1]}, 20 hold {h20[1]}; sum {h40[0]}')
            else:
                check(right and h40[1] > h20[1], f'{name}: {what} - made every pass, as before: 40 passes hold {h40[1]}, 20 hold {h20[1]}; sum {h40[0]}')
        h, e = held(compiler, d, 'never', NEVER.replace('NPASS', '40'))
        check(h == [0, 0], f'never: a kosh and a mala under a yadi that never runs are never made - the program holds {h[1] if h else e}')
        a, e1 = held(compiler, d, 'inner_a', INNER.replace('NOUT', '20').replace('NIN', '20'))
        b, e2 = held(compiler, d, 'inner_b', INNER.replace('NOUT', '20').replace('NIN', '1'))
        c, e3 = held(compiler, d, 'inner_c', INNER.replace('NOUT', '1').replace('NIN', '1'))
        check(bool(a and b and c) and a[1] == b[1] == 20 * c[1] > 0 and a[0] == 20 * 210,
              f'inner loop: a kosh in a yavat inside a chakra is made once for each time the yavat starts - 20 x 20 passes hold {a and a[1]}, 20 x 1 hold {b and b[1]}, 1 x 1 holds {c and c[1]}')
        h, e = held(compiler, d, 'stamp', STAMP)
        check(h is not None and h[:4] == [9, 1, 1, 1] and h[4] == 64 + 64,
              f'stamp: a kosh made once inside a mandapa carries this pass\'s block generation - sum, changed, live, same slot, held: {h or e}')
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'r175 nested made once: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
