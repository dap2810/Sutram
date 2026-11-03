#!/usr/bin/env python3
"""R116: the sixteen library contracts (ChatGPT R189), each at its boundaries.

Every case is one small program: it calls one function once and prints the result. A success case must print
the exact value (Python is the oracle for the arithmetic) and exit 0; a refusal case must print nothing on
stdout from the call, write exactly the spec's diagnostic on stderr, and exit 1. Status rows (9, 15, 16) check
their return value and their output cells instead. Last line: "r116 contracts: N checks, M failed".
"""
import math, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPILER = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
    else os.path.join(ROOT, 'sutram_compiler')
MIN, MAX = -2**63, 2**63 - 1
MSG = {
    'dvigun': 'Sutram truti [E_ATIPRAVAH]: dvigun: dvigunitam phalam purnanka-seemam atikramati; n -4611686018427387904 tah 4611686018427387903 paryantam bhavet.',
    'trigun': 'Sutram truti [E_ATIPRAVAH]: trigun: trigunitam phalam purnanka-seemam atikramati; n -3074457345618258602 tah 3074457345618258602 paryantam bhavet.',
    'vardh': 'Sutram truti [E_ATIPRAVAH]: vardh: ekena vardhitam phalam purnanka-seemam atikramati; n 9223372036854775807 tah nyunam bhavet.',
    'nirapeksh_mulya': 'Sutram truti [E_PHALA_SEEMA]: nirapeksh_mulya: nirapeksha-mulyam 9223372036854775808; purnankasya adhikatamam mulyam 9223372036854775807.',
    'mahattam_samapavartak': 'Sutram truti [E_PHALA_SEEMA]: mahattam_samapavartak: mahattama-samapavartakah 9223372036854775808; purnankasya adhikatamam mulyam 9223372036854775807.',
    'viparyay_ank': 'Sutram truti [E_PHALA_SEEMA]: viparyay_ank: viparita-ankasya mulyam purnanke na dharyate; seema -9223372036854775808 tah 9223372036854775807 paryantam.',
    'ganita_nirapeksh': 'Sutram truti [E_PHALA_SEEMA]: ganita_nirapeksh: nirapeksha-mulyam 9223372036854775808; purnankasya adhikatamam mulyam 9223372036854775807.',
    'brahmagupta_kshetr': 'Sutram truti [E_ATIPRAVAH]: brahmagupta_kshetr: kshetraphalam purnanka-seemam atikramati; adhikatamam mulyam 9223372036854775807.',
    'brihat_ank_tak_laghu': 'Sutram truti [E_PHALA_SEEMA]: brihat_ank_tak_laghu: ankasya mulyam purnanke na dharyate; adhikatamam mulyam 9223372036854775807.',
    'adish_gunan': 'Sutram truti [E_AKARA_ASAMYA]: adish_gunan: dvi-koshayoh dirghate asamane; samane dirghate apekshite.',
    'bindu_gunan': 'Sutram truti [E_AKARA_ASAMYA]: bindu_gunan: dvi-koshayoh dirghate asamane; samane dirghate apekshite.',
}
INV = 'Sutram truti [E_MULYA_AYOGYA]: {f}: dattam mulyam ayogyam; kriyayah niyaman parikshatam.'


def lit(v):
    """A Sutram expression for any i64 (MIN cannot be written as a literal)."""
    return '((0 - 9223372036854775807) - 1)' if v == MIN else (str(v) if v >= 0 else f'(0 - {-v})')


def run(src, d):
    p = os.path.join(d, 't.sm')
    b = os.path.join(d, 't.bin')
    open(p, 'w', encoding='utf-8').write(src)
    if os.path.exists(b):
        os.remove(b)
    c = subprocess.run([COMPILER, p, b], capture_output=True, text=True, cwd=ROOT)
    if c.returncode != 0:
        return ('compile', c.returncode, c.stdout + c.stderr, '')
    r = subprocess.run([b], capture_output=True, text=True, timeout=20)
    return ('run', r.returncode, r.stdout, r.stderr)


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    with tempfile.TemporaryDirectory() as d:
        def call(mod, expr, setup=''):
            return run(f'yoj {mod}\n\nmukhya() {{\n{setup}    likha({expr})\n}}\n', d)

        def ok(mod, f, args, want, setup=''):
            k, rc, out, err = call(mod, f'{f}({", ".join(args)})', setup)
            good = k == 'run' and rc == 0 and out.strip() == str(want) and err == ''
            check(good, f'{f}({", ".join(args)}) = {want}' + ('' if good else f'  [got {k} {rc} {out.strip()!r} {err.strip()!r}]'))

        def refused(mod, f, args, msg, setup=''):
            k, rc, out, err = call(mod, f'{f}({", ".join(args)})', setup)
            good = k == 'run' and rc == 1 and out == '' and err == msg + '\n'
            check(good, f'{f}({", ".join(args)}) refused' + ('' if good else f'  [got {k} {rc} {out.strip()!r} {err.strip()!r}]'))

        # 1-3
        for n in (-2**62, 2**62 - 1, 0, -1, 12345):
            ok('ganit', 'dvigun', [lit(n)], 2 * n)
        for n in (-2**62 - 1, 2**62, MAX, MIN):
            refused('ganit', 'dvigun', [lit(n)], MSG['dvigun'])
        for n in (-3074457345618258602, 3074457345618258602, 7):
            ok('ganit', 'trigun', [lit(n)], 3 * n)
        for n in (-3074457345618258603, 3074457345618258603, MAX, MIN):
            refused('ganit', 'trigun', [lit(n)], MSG['trigun'])
        for n in (MAX - 1, MIN, -1):
            ok('ganit', 'vardh', [lit(n)], n + 1)
        refused('ganit', 'vardh', [lit(MAX)], MSG['vardh'])
        # 4, 7
        for f, mod in (('nirapeksh_mulya', 'ganit'), ('ganita_nirapeksh', 'ganita')):
            for n in (MIN + 1, MAX, -5, 0):
                ok(mod, f, [lit(n)], abs(n))
            refused(mod, f, [lit(MIN)], MSG[f])
        # 5
        for a, b in ((MIN, 2), (2, MIN), (MIN, 3), (MIN, MIN + 1), (MIN, 6), (-6, 4), (0, 0), (12, -18), (MAX, MAX), (MIN, -1)):
            ok('ganit', 'mahattam_samapavartak', [lit(a), lit(b)], math.gcd(a, b))
        for a, b in ((MIN, 0), (0, MIN), (MIN, MIN)):
            refused('ganit', 'mahattam_samapavartak', [lit(a), lit(b)], MSG['mahattam_samapavartak'])
        # 6
        def rev(n):
            r = int(str(abs(n))[::-1])
            return -r if n < 0 else r
        for n in (1000, -1000, 7085774586302733229, -8085774586302733229, 0, 123, -123, 1000000000000000009, 7463847412, MAX, MIN, 1000000000000000019):
            ok('ank', 'viparyay_ank', [lit(n)], rev(n))
        for n in (8085774586302733229, -9085774586302733229, 1000000000000000039, -1000000000000000039):
            refused('ank', 'viparyay_ank', [lit(n)], MSG['viparyay_ank'])
        # 10: digits least-significant first, one byte per 8-byte cell
        def digits(ds):
            s = f'    vitti a = nirmmita({max(1, len(ds)) * 8})\n'
            for i, dg in enumerate(ds):
                s += f'    likh8(a + {i * 8}, {dg})\n'
            return s
        for v in (MAX, 0, 1, 922337203685477580):
            ds = [int(c) for c in str(v)][::-1]
            ok('brihat', 'brihat_ank_tak_laghu', ['a', str(len(ds))], v, digits(ds))
        ok('brihat', 'brihat_ank_tak_laghu', ['a', '0'], 0, digits([]))
        ok('brihat', 'brihat_ank_tak_laghu', ['a', '4'], 12, digits([2, 1, 0, 0]))     # leading zeros allowed
        for ds in ([int(c) for c in str(MAX + 1)][::-1], [int(c) for c in str(10**19)][::-1]):
            refused('brihat', 'brihat_ank_tak_laghu', ['a', str(len(ds))], MSG['brihat_ank_tak_laghu'], digits(ds))
        refused('brihat', 'brihat_ank_tak_laghu', ['a', '2'], INV.format(f='brihat_ank_tak_laghu'), digits([1, 10]))
        refused('brihat', 'brihat_ank_tak_laghu', ['a', '0 - 1'], INV.format(f='brihat_ank_tak_laghu'), digits([1]))
        # 13, 14
        def koshes(u, v):
            s = '    kosh dasham u[4]\n    kosh dasham v[4]\n'
            s += ''.join(f'    kosh_kship(u, {x})\n' for x in u) + ''.join(f'    kosh_kship(v, {x})\n' for x in v)
            return s
        for f, mod in (('adish_gunan', 'samanvaya'), ('bindu_gunan', 'sankhyiki')):
            ok(mod, f, ['u', 'v'], '8.500000', koshes(['2.5', '1.5'], ['2.5', '1.5']))
            ok(mod, f, ['u', 'v'], '0.000000', koshes([], []))
            ok(mod, f, ['u', 'u'], '8.500000', koshes(['2.5', '1.5'], []))
            refused(mod, f, ['u', 'v'], MSG[f], koshes(['5.0', '6.0', '7.0'], ['5.0', '6.0']))
        # 8: exact, against Python's isqrt
        def area(a, b, c, dd):
            t = a + b + c + dd
            return math.isqrt((t - 2 * a) * (t - 2 * b) * (t - 2 * c) * (t - 2 * dd)) // 4
        for sides in ((1, 1, 2, 3), (2, 3, 4, 0), (3, 3, 3, 3), (1, 1, 1, 3), (1, 2, 3, 0), (MAX, MAX, 1, 1),
                      (3037000499,) * 4, (2**40 + 7, 2**41 - 3, 2**40, 2**39 + 11), (MAX, MAX, MAX // 2, MAX // 2 + 1)):
            want = area(*sides)
            if want <= MAX:
                ok('ganita', 'brahmagupta_kshetr', [lit(x) for x in sides], want)
        for sides in ((MAX,) * 4, (3037000500,) * 4, (MAX, MAX, MAX, 0)):
            refused('ganita', 'brahmagupta_kshetr', [lit(x) for x in sides], MSG['brahmagupta_kshetr'])
        for sides in ((-1, 2, 2, 2), (2, 0, 2, 2), (2, 2, 2, -1), (1, 2, 10, 3), (1, 1, 10, 0), (0, 0, 0, 0)):
            refused('ganita', 'brahmagupta_kshetr', [lit(x) for x in sides], INV.format(f='brahmagupta_kshetr'))

        # 9: status; nothing printed; the destination cleared on failure, untouched on a bad descriptor
        def se(ds, base, n, pre=7):
            setup = f'    vitti d = nirmmita({max(1, len(ds)) * 8})\n' + ''.join(f'    d[{i}] = {v}\n' for i, v in enumerate(ds))
            setup += f'    vitti x = nirmmita({max(1, n) * 8})\n' + ''.join(f'    x[{i}] = {pre}\n' for i in range(max(1, n)))
            prog = f'yoj aadhar\n\nmukhya() {{\n{setup}    likha(brihat_ank_se(d, {len(ds)}, {base}, x, {n}))\n'
            prog += ''.join(f'    likha(x[{i}])\n' for i in range(max(1, n))) + '}\n'
            k, rc, out, err = run(prog, d)
            return k == 'run' and rc == 0 and err == '', out.split()
        for ds, base, n, want in (([9, 9], 10, 2, ['1', '9', '9']), ([1, 0, 0], 10, 2, ['0', '0', '0']),
                                  ([0, 0, 1, 2], 10, 2, ['1', '2', '1']), ([1, 10], 10, 2, ['0', '0', '0']),
                                  ([], 10, 2, ['1', '0', '0']), ([1, 1, 1, 1], 2, 2, ['1', '5', '1']),
                                  ([15, 15], 16, 3, ['1', '5', '5', '2']), ([1], 1, 2, ['0', '7', '7']),
                                  ([1], 17, 2, ['0', '7', '7']), ([1], 10, 0, ['0', '7'])):
            good, out = se(ds, base, n)
            check(good and out == want, f'brihat_ank_se({ds}, base {base}, n {n}) -> {want}' + ('' if good and out == want else f'  [got {good} {out}]'))

        # 12: exact or saturated, never refused
        for a, b in ((2**62, 2**62), (MIN, MIN), (MIN, MAX), (5, 4), (0, MAX), (MIN + 2, MAX), (-2**62 - 1, -2**62 - 1),
                     (0, 4294967296), (2**62, 2**62 + 1), (-5, 5), (MAX, MAX)):
            want = 0 if b < a else max(MIN, min(MAX, (a + b) * (b - a + 1) // 2))
            ok('sadhan', 'yog_seema', [lit(a), lit(b)], want)

        # 15: 1 sorted; 0 with the cells unchanged when the scratch is refused (a length of 2^60 cells)
        prog = ('yoj suchi\n\nmukhya() {\n    vitti l = suchi_srij(4)\n    suchi_khip(l, 3)\n    suchi_khip(l, 1)\n'
                '    suchi_khip(l, 2)\n    likha(suchi_shreni(l))\n    likha(suchi_grah(l, 0))\n    likha(suchi_grah(l, 2))\n'
                '    vitti e = suchi_srij(1)\n    likha(suchi_shreni(e))\n    vitti c = l[2]\n    c[0] = 9\n'
                '    l[0] = 1152921504606846976\n    likha(suchi_shreni(l))\n    likha(c[0])\n    likha(c[1])\n}\n')
        k, rc, out, err = run(prog, d)
        check(k == 'run' and rc == 0 and err == '' and out.split() == ['1', '1', '3', '1', '0', '9', '2'],
              f'suchi_shreni: sorted 1, empty 1, refused scratch 0 with cells unchanged  [{out.split()} {err!r}]')

        # 16: status; leading zeros never fail
        def vd(text):
            cells = ''.join(f'    b[{i}] = {ord(ch)}\n' for i, ch in enumerate(text))
            prog = (f'yoj vakyank\n\nmukhya() {{\n    vitti b = nirmmita({max(1, len(text)) * 8})\n{cells}'
                    f'    vitti ok = nirmmita(8)\n    dasham v = varna_tak_dashm(b, {len(text)}, ok)\n    likha(v * 100000000000000000000.0)\n    likha(ok[0])\n}}\n')
            k, rc, out, err = run(prog, d)
            return k == 'run' and rc == 0 and err == '', out.split()
        for text, want in (('00000000000000000001', ['1.000000e+20', '1']),
                           ('0.00000000000000000001', ['1.000000', '1']), ('0000', ['0.000000', '1']),
                           ('1x', ['0.000000', '0']), ('1e999', ['0.000000', '0']), ('9e308', ['0.000000', '0']),
                           ('1e-999', ['0.000000', '1']), ('0e99999999999999999999', ['0.000000', '1']),
                           ('000000000000000000000000000002.5', ['2.500000e+20', '1'])):
            good, out = vd(text)
            check(good and out == want, f'varna_tak_dashm({text!r}) -> {want}' + ('' if good and out == want else f'  [got {good} {out}]'))

        # the compiler fix this needed: string literals of 127 bytes or more (v295: a crash, or nothing or the wrong text printed)
        for n in (125, 126, 127, 128, 255, 256, 300, 1000, 5000):
            prog = 'mukhya() {\n    likha("' + 'x' * n + '")\n    vitti s = "' + 'y' * n + '"\n    shabda(s)\n    likha_rup("' + 'z' * n + '", 7)\n}\n'
            k, rc, out, err = run(prog, d)
            want = 'x' * n + 'y' * n + 'z' * n + '7'
            check(k == 'run' and rc == 0 and out.replace('\n', '') == want, f'a {n}-byte string literal, three ways' + ('' if k == 'run' and out.replace('\n', '') == want else f'  [got {k} {rc} {len(out)}]'))
    print(f'r116 contracts: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
