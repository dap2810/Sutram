#!/usr/bin/env python3
"""R172 (Sarvam ROUND-172 WS2, WS4): a kosh declared in a chakra's own body, never escaping, is made once.

Up to v316 `chakra j = 1 tak N { kosh k[1] ... }` allocated a new descriptor and buffer every pass and kept all
of them: 48 bytes a pass (R168). From v317 the first pass allocates; every later pass finds the descriptor in a
frame slot and sets its length to 0. The descriptor's layout is unchanged; nothing is zeroed.

Part 1 - which kosh are made once (parimana() is the witness; the test calibrates itself, no recorded numbers):
each case is compiled twice, with 1 pass and with 20. "once": the 20-pass program holds exactly what the 1-pass
program holds. "every pass": it holds more (as v316). Each program also prints a sum that is right only if every
pass saw an empty kosh.

Part 2 - the redzones (the design's own test, WS4): 64 bytes of 0xDEADBEEFCAFEBABE immediately before the
descriptor's first word (d-16) and immediately after its first allocation, then 1,000,000 passes, nested chakra,
a chakra in a mandapa, growth to 20,000,000 elements in each of three passes. After each phase every redzone word
is read back and d-16 (length), d-8 (capacity), d (elements), d+8 (region size) are compared with exact values.
An address-space limit (Linux, RLIMIT_AS) then makes the growth fail: the program must stop with the kosh message
and exit 1, redzones of the finished phases already reported intact.

Usage: python3 tests/r172/test_chakra_kosh.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0
POISON = -2401053089206453570            # 0xDEADBEEFCAFEBABE as a signed 64-bit number


def check(ok, what):
    global checks, fails
    checks += 1
    if ok:
        print('ok    ' + what)
    else:
        fails += 1
        print('FAIL  ' + what)


def loop(body, funcs='', pre='', n='NPASS'):
    return (funcs + 'mukhya() {\n    vitti s = 0\n' + pre + f'    chakra j = 1 tak {n} {{\n' + body
            + '    }\n    likha(s, " ", parimana(), "\\n")\n}\n')


K = '        kosh k[1]\n'
P = '        kosh_kship(k, j)\n'
U = '        s = s + k[0] + kosh_gan(k)\n'
G100 = '        chakra i = 1 tak 100 {\n            kosh_kship(k, i)\n        }\n'
G4097 = '        chakra i = 1 tak 4097 {\n            kosh_kship(k, i)\n        }\n'

# (name, what, made once?, source with NPASS, the sum for 20 passes)
CASES = [
    ('plain', 'declared in the body, pushed to, read', True, loop(K + P + U), 230),
    ('dasham', 'a kosh of dasham', True, loop('        kosh dasham k[1]\n' + P + '        s = s + kosh_gan(k)\n'), 20),
    ('grown', 'grown to 100 every pass', True, loop(K + G100 + '        s = s + k[99] + kosh_gan(k)\n'), 4000),
    ('region', 'grown to 4,097 every pass (a region: one, kept, not one a pass)', True, loop(K + G4097 + '        s = s + k[4096] + kosh_gan(k)\n'), 163880),
    ('capacity', 'a declared capacity that changes every pass', True, loop('        kosh k[j]\n' + P + U), 230),
    ('agrim', 'agrim after the declaration', True, loop(K + P + U + '        yadi (j > 0) {\n            agrim\n        }\n        s = s + 1000000\n'), 230),
    ('builtins', 'kosh_hri, kosh_iksh, kosh_apanay, kosh_rikt, kosh_shodh, kosh_yuj, k[i] = v', True,
     loop(K + P + '        kosh_yuj(k, 5)\n        kosh_kship(k, 6)\n        k[0] = k[0] + 1\n'
          '        s = s + kosh_iksh(k) + kosh_hri(k) + kosh_apanay(k) + kosh_rikt(k) + kosh_gan(k)\n        kosh_shodh(k)\n        s = s + kosh_gan(k)\n'), 20 * 14 + 210),
    ('two', 'two kosh in one body', True, loop(K + '        kosh m[1]\n' + P + '        kosh_kship(m, 3)\n' + U + '        s = s + m[0]\n'), 290),
    ('in-prakriya', 'the chakra is in a prakriya', True,
     'prakriya kar(n) {\n    vitti s = 0\n    chakra j = 1 tak n {\n' + K + P + U + '    }\n    nivartanam s\n}\n'
     'mukhya() {\n    likha(kar(NPASS), " ", parimana(), "\\n")\n}\n', 230),
    ('nivartanam', 'nivartanam out of the loop with the kosh alive (nothing to undo)', True,
     'prakriya kar(n) {\n    chakra j = 1 tak n {\n' + K + P + '        yadi (j == n) {\n            nivartanam k[0] + kosh_gan(k)\n        }\n    }\n    nivartanam 0\n}\n'
     'mukhya() {\n    likha(kar(NPASS), " ", parimana(), "\\n")\n}\n', 21),
    ('in-mandapa', 'the chakra is inside a mandapa', True,
     'mukhya() {\n    vitti s = 0\n    mandapa {\n        vitti b = nirmmita(64)\n        chakra j = 1 tak NPASS {\n    ' + K + '    ' + P + '    ' + U + '        }\n    }\n    likha(s, " ", parimana(), "\\n")\n}\n', 230),
    ('alias', 'a second name: vitti a = k', False, loop(K + P + '        vitti a = k\n        s = s + a[0] + kosh_gan(k)\n'), 230),
    ('to-prakriya', 'given to a prakriya (even one that only reads it)', False,
     loop(K + P + '        s = s + dekh(k) + kosh_gan(k)\n', funcs='prakriya dekh(kosh q) {\n    nivartanam q[0]\n}\n'), 230),
    ('slice', 'a slice of it given to a prakriya', False,
     loop(K + P + '        s = s + pratham(k[0:1]) + kosh_gan(k)\n', funcs='prakriya pratham(vibhag v) {\n    nivartanam v[0]\n}\n'), 230),
    ('ksham', 'kosh_ksham: the capacity would show the reuse', False, loop(K + P + '        s = s + k[0] + kosh_ksham(k)\n'), 230),
    ('under-yadi', 'declared under a yadi in the body (made once from v319, R175)', True,
     loop('        yadi (j > 0) {\n            kosh k[1]\n            kosh_kship(k, j)\n            s = s + k[0] + kosh_gan(k)\n        }\n'), 230),
    ('yavat', 'a yavat loop (made once from v319, R175)', True,
     'mukhya() {\n    vitti s = 0\n    vitti j = 1\n    yavat (j <= NPASS) {\n' + K + P + U + '        j = j + 1\n    }\n    likha(s, " ", parimana(), "\\n")\n}\n', 230),
    ('mandapa-in-chakra', 'declared in a mandapa inside the chakra (made once from v319, R175)', True,
     loop('        mandapa {\n            kosh k[1]\n            kosh_kship(k, j)\n            s = s + k[0] + kosh_gan(k)\n        }\n'), 230),
]

# nested: the inner loop's kosh is made once for each time the inner loop is entered (20), not 400 times
NESTED = loop('        chakra i = 1 tak NIN {\n            kosh k[1]\n            kosh_kship(k, i)\n            s = s + k[0] + kosh_gan(k)\n        }\n', n='NOUT')

RED_FUNCS = '''prakriya shabd(a, i) {
    nivartanam a[i]
}
prakriya bhar(a) {
    chakra i = 0 tak 7 {
        a[i] = %d
    }
    nivartanam 0
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
prakriya nav() {
    vitti p = nirmmita(64)
    vitti z = bhar(p)
    nivartanam p
}
prakriya varnan(a, off, len, cap, el, reg) {
    vitti bad = 0
    yadi (a[8 + off] != len) {
        bad = bad + 100
    }
    yadi (a[9 + off] != cap) {
        bad = bad + 1000
    }
    yadi (a[10 + off] != el) {
        bad = bad + 10000
    }
    yadi (a[11 + off] != reg) {
        bad = bad + 100000
    }
    nivartanam bad
}
''' % (POISON, POISON)


def red_phase(name, n, off, inner, growth, len_, cap, el, reg, wrap=('', '')):
    """One phase as a prakriya: redzone A, the loop (B is made right after the kosh's first allocation), the check.
    el: 'first' = the elements where the first allocation put them, 'same' = wherever pass 1 left them."""
    ind = '        '
    body = (f'{ind}kosh k[1]\n{ind}yadi (j == 1) {{\n{ind}    b = nav()\n{ind}}}\n'
            + growth + f'{ind}s = s + kosh_gan(k)\n'
            + f'{ind}yadi (j == 1) {{\n{ind}    e1 = shabd(a, {10 + off})\n{ind}}}\n'
            + f'{ind}yadi (shabd(a, {10 + off}) != e1) {{\n{ind}    moved = moved + 1\n{ind}}}\n')
    el_expr = {'first': f'a + {96 + 8 * off}', 'same': 'e1'}[el]
    return (f'prakriya {name}() {{\n    vitti a = nav()\n    vitti z = 0\n    vitti b = 0\n    vitti s = 0\n'
            f'    vitti e1 = 0\n    vitti moved = 0\n{wrap[0]}    chakra j = 1 tak {n} {{\n{inner[0]}{body}{inner[1]}    }}\n{wrap[1]}'
            f'    z = akshat(a) + akshat(b) + varnan(a, {off}, {len_}, {cap}, {el_expr}, {reg})\n'
            f'    likha("phase ", {name[1:]}, " bad ", z, "\\n")\n'
            f'    likha("  passes sum ", s, " moved ", moved, "\\n")\n    nivartanam z\n}}\n')


def redzone_program(off, big):
    g1 = '        kosh_kship(k, j)\n'
    g5 = '        chakra i = 1 tak 5 {\n            kosh_kship(k, i)\n        }\n'
    gbig = f'        chakra i = 1 tak {big} {{\n            kosh_kship(k, i)\n        }}\n'
    cap, reg = 1, 0                      # as r127_emit_grow: doubling; a region from 64 KiB of capacity, of
    while cap < big:                     # max(2 x the new bytes, 64 MiB); a capacity that fits the region stays in it
        cap *= 2
        if cap * 8 >= 65536 and reg < cap * 8:
            reg = max(2 * cap * 8, 64 << 20)
    src = RED_FUNCS
    src += red_phase('p1', 1000000, off, ('', ''), g1, 1, 1, 'first', 0)
    src += red_phase('p2', 1000, off, ('', '        chakra q = 1 tak 1000 {\n            kosh m[1]\n            kosh_kship(m, q)\n            s = s + m[0]\n        }\n'), g5, 5, 8, 'same', 0)
    if off:
        src += red_phase('p3', 100000, off, ('', ''), g5, 5, 8, 'same', 0,
                         wrap=('    mandapa {\n    vitti t = nirmmita(4096)\n', '    }\n'))
    src += red_phase('p4', 3, off, ('', ''), gbig, big, cap, 'same', reg)
    calls = ''.join(f'    bad = bad + {p}()\n' for p in (['p1', 'p2'] + (['p3'] if off else []) + ['p4']))
    return src + 'mukhya() {\n    vitti bad = 0\n' + calls + '    likha("redzones bad ", bad, " held ", parimana(), "\\n")\n}\n'


def run(cmd, cwd, limit=None):
    pre = None
    if limit:
        import resource
        pre = lambda: resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors='replace', timeout=900, preexec_fn=pre)
    return p.returncode, (p.stdout + p.stderr).strip()


def build(compiler, d, name, src):
    open(os.path.join(d, name + '.sm'), 'w').write(src)
    rc, out = run([compiler, name + '.sm', name + '.bin'], d)
    return rc == 0 and os.path.exists(os.path.join(d, name + '.bin')), out


def main():
    compiler = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        compiler = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    d = tempfile.mkdtemp(prefix='r172_')
    try:
        for name, what, once, src, want_sum in CASES:
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
                right = held[20][0] == want_sum
                if once:
                    check(right and held[20][1] == held[1][1],
                          f'{name}: {what} - made once: 20 passes hold {held[20][1]}, 1 pass holds {held[1][1]}; sum {held[20][0]}')
                else:
                    check(right and held[20][1] > held[1][1],
                          f'{name}: {what} - made every pass, as before: 20 passes hold {held[20][1]}, 1 pass holds {held[1][1]}; sum {held[20][0]}')
        held = {}
        for o, i in ((1, 1), (20, 20), (20, 1)):
            ok, out = build(compiler, d, f'nested{o}_{i}', NESTED.replace('NOUT', str(o)).replace('NIN', str(i)))
            rc, out = run([os.path.join(d, f'nested{o}_{i}.bin')], d) if ok else (1, out)
            held[(o, i)] = int(out.split()[1]) if rc == 0 and len(out.split()) == 2 else -1
        check(held[(20, 20)] == held[(20, 1)] == 20 * held[(1, 1)] > 0,
              f'nested: a kosh in an inner chakra is made once for each entry to the inner loop - 20 x 20 passes hold {held[(20, 20)]}, 20 x 1 hold {held[(20, 1)]}, 1 x 1 holds {held[(1, 1)]}')

        for off, label in ((0, 'no kosh in a mandapa in the program: a 32-byte descriptor'),
                           (3, 'a chakra inside a mandapa: the 56-byte descriptor (R82)')):
            ok, out = build(compiler, d, f'red{off}', redzone_program(off, 20000000))
            if not ok:
                check(False, f'redzones ({label}): compiles ({out[:120]})')
                continue
            rc, out = run([os.path.join(d, f'red{off}.bin')], d)
            lines = out.split('\n')
            phases = [l for l in lines if l.startswith('phase ')]
            want = 4 if off else 3
            check(rc == 0 and len(phases) == want and all(l.endswith(' bad 0') for l in phases) and any(l.startswith('redzones bad 0 ') for l in lines),
                  f'redzones ({label}): {want} phases, every redzone word intact, d-16 d-8 d d+8 exact ({"; ".join(phases)[:150]})')
            check(all(l.endswith(' moved 0') for l in lines if l.startswith('  passes')),
                  f'redzones ({label}): after pass 1 the elements never move - every pass uses the same buffer')
        if not sys.platform.startswith('linux'):
            print('NOT RUN  the out-of-memory refusal under an address-space limit - Linux only (RLIMIT_AS)')
        else:
            ok, out = build(compiler, d, 'oom', redzone_program(0, 20000000))
            rc, out = run([os.path.join(d, 'oom.bin')], d, limit=(1 << 30) + (200 << 20))
            lines = out.split('\n')
            check(rc == 1 and 'kosh vardhayitum smritih na labdha' in out and 'phase 1 bad 0' in lines and 'phase 2 bad 0' in lines and not any(l.startswith('phase 4') for l in lines),
                  f'out of memory: with 1.2 GiB of address space the growth to 20,000,000 is refused with the kosh message, exit 1, after phases 1 and 2 reported intact (exit {rc})')
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'r172 chakra kosh: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
