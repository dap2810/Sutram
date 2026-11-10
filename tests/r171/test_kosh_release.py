#!/usr/bin/env python3
"""R171 (Sarvam ROUND-171): one narrow case - a kosh proven local to its mandapa gives its region back.

A kosh whose capacity reaches 64 KiB (from its 4,097th element) keeps its elements in a region of its own
(mmap / VirtualAlloc, 64 MiB of address space). Up to v316 that region stayed for the program's life when the
kosh's block ended. From v317 it is given back (munmap / VirtualFree) at these ways out of the block - its last
line, krama, agrim, nivartanam (not a failure passed on by prasar: that way out keeps it) - when the kosh is

  1  declared as a statement of the block's own body (not under a yadi or a loop inside it),
  2  the only declaration of its name in the block,
  3  added to in the block (kosh_kship / kosh_yuj: nothing else grows a kosh), and
  4  named in the block only as the base of an index (k[i], k[i] = v) or as the kosh a kosh_* built-in works on.

Any other use - `vitti a = k`, k given to a prakriya, anything the check does not know - and it is not reclaimed:
it behaves as in v316. The compiler already refuses returning it, storing it and assigning it outward
(E_KOSH_MANDAPA); those lines are checked here as still refused.

How a release is seen without tracing system calls: parimana() counts a region kosh by its capacity, and a release
takes that capacity back. Each case prints parimana() at its end. BASE is what the v316 compiler's program prints
(recorded once, ROUND-171); the test requires  printed == BASE - RELEASED x REGION  where REGION is the capacity in
bytes at the block's end (65,536 for 4,097 elements, 131,072 for 9,000). RELEASED = 0 is "as v316".
The descriptor and the elements left in the arena are NOT given back: BASE - RELEASED x REGION is never 0.

And once against the operating system (Linux only): with the address space limited to 8 GiB, 1,000 passes of the
proven-local case finish (v316: stopped in pass 112), and the same loop with a second name stops as it did.

Usage: python3 tests/r171/test_kosh_release.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
N = 20
checks = fails = 0


def check(ok, what):
    global checks, fails
    checks += 1
    if ok:
        print('ok    ' + what)
    else:
        fails += 1
        print('FAIL  ' + what)


def grow(name='k', n=4097, ind=12):
    p = ' ' * ind
    return f'{p}chakra i = 1 tak {n} {{\n{p}    kosh_kship({name}, i)\n{p}}}\n'


def prog(body, pre='', funcs=''):
    return (funcs + 'mukhya() {\n    vitti s = 0\n' + pre + f'    chakra j = 1 tak {N} {{\n' + body
            + '    }\n    likha(s, " ", parimana(), "\\n")\n}\n')


def fn(body_of_kar, calls=N):
    return ('prakriya kar(j) {\n' + body_of_kar + '    nivartanam 0\n}\nmukhya() {\n    vitti s = 0\n'
            + f'    chakra j = 1 tak {calls} {{\n        s = s + kar(j)\n    }}\n    likha(s, " ", parimana(), "\\n")\n}}\n')


M = '        mandapa {\n'
E = '        }\n'
K = '            kosh k[1]\n'
G = grow()
R = 65536

# (name, what, released, region bytes, v316's output "s parimana", source)
CASES = [
    ('plain', 'declared in the block, pushed to, indexed', N, R, '81940 1967360',
     prog(M + K + G + '            s = s + k[4096]\n' + E)),
    ('no-block', 'no mandapa: no place where it is known dead', 0, R, '81940 1966720',
     prog('        kosh k[1]\n' + grow(ind=8) + '        s = s + k[4096]\n')),
    ('outer', 'declared outside the block (condition 1)', 0, R, '20000 294944',
     prog(M + grow(n=1000) + '            s = s + k[999]\n' + E, pre='    kosh k[1]\n')),
    ('alias', 'a second name: vitti a = k', 0, R, '81940 1967360',
     prog(M + K + G + '            vitti a = k\n            s = s + a[4096]\n' + E)),
    ('to-prakriya', 'given to a prakriya (even one that only reads it)', 0, R, '81940 1967360',
     prog(M + K + G + '            s = s + dekh(k)\n' + E, funcs='prakriya dekh(kosh q) {\n    nivartanam q[4096]\n}\n')),
    ('under-yadi', 'declared under a yadi inside the block, not in its own body', 0, R, '81940 1967360',
     prog(M + '            yadi (j > 0) {\n                kosh k[1]\n' + grow(ind=16) + '                s = s + k[4096]\n            }\n' + E)),
    ('never-pushed', 'nothing is added to it: it cannot have a region, no code for it', 0, R, '20 2560',
     prog(M + '            kosh k[8]\n            s = s + kosh_gan(k) + 1\n' + E)),
    ('small', 'proven local but small: the check runs, there is no region to give back', 0, R, '210 1280',
     prog(M + K + '            kosh_kship(k, j)\n            s = s + k[0]\n' + E)),
    ('krama', 'krama out of the block', 1, R, '4097 98368',
     prog(M + K + G + '            s = s + k[4096]\n            krama\n' + E)),
    ('agrim', 'agrim out of the block', N, R, '81940 1967360',
     prog(M + K + G + '            s = s + k[4096]\n            yadi (j > 0) {\n                agrim\n            }\n            s = s + 1000000\n' + E)),
    ('nivartanam', 'nivartanam of a value read from it', N, R, '163880 1967360',
     fn('    mandapa {\n        kosh k[1]\n' + grow(ind=8) + '        nivartanam k[4096] + kosh_gan(k)\n    }\n')),
    ('early-nivartanam', 'a nivartanam before the declaration (nothing to release) and one after', N // 2, R, '40980 983680',
     fn('    mandapa {\n        yadi (j % 2 == 0) {\n            nivartanam 1\n        }\n        kosh k[1]\n' + grow(ind=8)
        + '        yadi (j > 0) {\n            nivartanam k[4096]\n        }\n    }\n')),
    ('two', 'two kosh in one block', 2 * N, R, '81960 3934720',
     prog(M + K + '            kosh m[1]\n' + G + grow('m') + '            s = s + k[4096] + m[0]\n' + E)),
    ('nested', 'a block in a block, one kosh each', 2 * N, R, '163880 3934720',
     prog(M + K + G + '            mandapa {\n                kosh m[1]\n' + grow('m', ind=16) + '                s = s + m[4096]\n            }\n            s = s + k[4096]\n' + E)),
    ('krama-two-deep', 'krama leaving two blocks at once', 2, R, '8194 196736',
     prog(M + K + G + '            mandapa {\n                kosh m[1]\n' + grow('m', ind=16) + '                s = s + m[4096] + k[4096]\n                krama\n            }\n' + E)),
    ('long-block', 'a block of fifteen statements', N, R, '82240 1967360',
     prog(M + ''.join(f'            vitti a{i} = {i}\n' for i in range(1, 10)) + K + G
          + '            s = s + k[4096] + a9\n            s = s + a1\n            s = s + a2\n            s = s + a3\n' + E)),
    ('every-builtin', 'every kosh_* built-in on it', N, R, '327780 1967360',
     prog(M + K + G + '            vitti z = kosh_iksh(k) + kosh_apanay(k) + kosh_ksham(k) + kosh_rikt(k) + kosh_hri(k)\n'
          '            kosh_yuj(k, 3)\n            kosh_shodh(k)\n            kosh_kship(k, z)\n            k[0] = k[0] + 1\n            s = s + k[0] + kosh_gan(k)\n' + E)),
    ('dasham', 'a kosh of dasham', N, R, '81940 1967360',
     prog(M + '            kosh dasham k[1]\n' + G + '            s = s + kosh_gan(k)\n' + E)),
    ('parimita', 'mandapa parimita', N, R, '81940 1967360',
     prog('        mandapa parimita 100000 {\n' + K + G + '            s = s + k[4096]\n' + E)),
    ('grown-twice', '9,000 elements: the growth path frees the first region, the block the second', N, 2 * R, '180000 3278080',
     prog(M + K + grow(n=9000) + '            s = s + k[8999]\n' + E)),
    ('inner-krama', 'krama out of a loop inside the block (the block is not left)', N, R, '81940 1967360',
     prog(M + K + '            chakra i = 1 tak 9000 {\n                kosh_kship(k, i)\n                yadi (i == 4097) {\n                    krama\n                }\n            }\n            s = s + k[4096]\n' + E)),
    ('same-name-twice', 'the same name in two blocks, one after the other', 2 * N, R, '163880 3934720',
     prog(M + K + G + '            s = s + k[4096]\n' + E + M + K + G + '            s = s + k[4096]\n' + E)),
    ('recursion', 'a prakriya that calls itself from inside the block: five live at once', 5, R, '20485 491840',
     'prakriya gahan(n) {\n    vitti r = 0\n    mandapa {\n        kosh k[1]\n' + grow(ind=8)
     + '        yadi (n > 1) {\n            r = gahan(n - 1)\n        }\n        r = r + k[4096]\n    }\n    nivartanam r\n}\n'
       'mukhya() {\n    likha(gahan(5), " ", parimana(), "\\n")\n}\n'),
    ('prasar', 'ten returns give it back; ten failures passed on by prasar do not (kept, as v316)', 10, R, '70 40970 1967360',
     'prakriya failure(c)\n    yadi (c == 1)\n        nivartanam dosh(7)\n    nivartanam siddhi(c * 10)\n'
     'prakriya attempt(c)\n    mandapa\n        kosh k[1]\n        chakra i = 1 tak 4097\n            kosh_kship(k, i)\n'
     '        vitti x = prasar failure(c)\n        nivartanam siddhi(x + k[4096])\n    nivartanam siddhi(0)\n'
     'mukhya()\n    vitti j = 0\n    vitti fails = 0\n    vitti sum = 0\n    yavat (j < 20)\n'
     '        yadi dosh (q = attempt(j % 2))\n            fails = fails + q\n        anya\n            sum = sum + q\n'
     '        j = j + 1\n    likha(fails, " ", sum, " ", parimana(), "\\n")\n'),
]

REFUSED = [
    ('returned', 'nivartanam k (condition 3)',
     fn('    mandapa {\n        kosh k[1]\n' + grow(ind=8) + '        nivartanam k\n    }\n')),
    ('pushed', 'kosh_kship(o, k) (condition 4)',
     prog(M + K + '            kosh o[1]\n' + G + '            kosh_kship(o, k)\n' + E)),
    ('stored', 'o[1] = k (condition 4)',
     prog(M + K + '            mala o[4]\n' + G + '            o[1] = k\n' + E)),
]

LOOP = ('mukhya() {\n    vitti s = 0\n    chakra j = 1 tak 1000 {\n        mandapa {\n            kosh k[1]\n'
        + grow() + 'USE        }\n    }\n    likha(s, "\\n")\n}\n')


def run(cmd, cwd, limit=None):
    pre = None
    if limit:
        import resource
        pre = lambda: resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors='replace', timeout=300, preexec_fn=pre)
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    compiler = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        compiler = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    record = '--record' in sys.argv          # print what this compiler's programs print (to record BASE)
    d = tempfile.mkdtemp(prefix='r171_')
    try:
        for name, what, released, region, base, src in CASES:
            open(os.path.join(d, name + '.sm'), 'w').write(src)
            rc, out = run([compiler, name + '.sm', name + '.bin'], d)
            if rc != 0 or not os.path.exists(os.path.join(d, name + '.bin')):
                check(False, f'{name}: compiles ({out[:80]})')
                continue
            rc, out = run([os.path.join(d, name + '.bin')], d)
            if record:
                print(f'RECORD {name} {out!r}')
                continue
            s0, p0 = base.rsplit(' ', 1)
            want = f'{s0} {int(p0) - released * region}'
            check(rc == 0 and out == want,
                  f'{name}: {what} - {released} region(s) given back' + ('' if out == want else f' (printed {out[:60]!r}, wanted {want!r})'))
        for name, what, src in REFUSED:
            open(os.path.join(d, name + '.sm'), 'w').write(src)
            rc, out = run([compiler, name + '.sm', name + '.bin'], d)
            check(rc != 0 and 'E_KOSH_MANDAPA' in out and not os.path.exists(os.path.join(d, name + '.bin')),
                  f'{name}: {what} is still refused when compiled (E_KOSH_MANDAPA)')
        if record:
            return 0
        if not sys.platform.startswith('linux'):
            print('NOT RUN  the 8 GiB address-space limit - Linux only (RLIMIT_AS)')
        else:
            lim = 8 << 30
            for name, use, finishes in (('limit-local', '            s = s + k[4096]\n', True),
                                        ('limit-alias', '            vitti a = k\n            s = s + a[4096]\n', False)):
                open(os.path.join(d, name + '.sm'), 'w').write(LOOP.replace('USE', use))
                rc, out = run([compiler, name + '.sm', name + '.bin'], d)
                rc, out = run([os.path.join(d, name + '.bin')], d, limit=lim)
                if finishes:
                    check(rc == 0 and out == '4097000', f'{name}: 1,000 passes finish with the address space limited to 8 GiB ({out[:50]!r}, exit {rc})')
                else:
                    check(rc == 1 and 'kosh vardhayitum' in out, f'{name}: with a second name it is not reclaimed - the same loop stops under 8 GiB, as in v316 (exit {rc})')
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'r171 kosh release: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
