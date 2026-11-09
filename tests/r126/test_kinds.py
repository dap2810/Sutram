#!/usr/bin/env python3
"""R126: a name keeps one kind; a kosh leaves its tracking only through doors that keep the kind.

v300's kosh_vars / array_vars were set from a bare name only, never cleared and blind to control flow, so a
name could be compiled as one kind and hold another (R125: two SIGSEGVs and a silent read past a kosh's
length). From v301 every binding of a name in a prakriya - declaration, assignment, parameter, chakra
variable - must give the kind its first one gave (E_VITTI_PRAKAR), and a kosh cannot become a raw number
by a cell, a field, a global, an untyped parameter, a raw builtin, ?: or k + 0 (E_KOSH_DVARA, E_KOSH_GANIT).
A prakriya that returns a kosh parameter or a kosh it declares, by its own name on every nivartanam, gives
its caller a kosh: the caller's name is marked and checked.

Each REFUSED case must be refused at compile time with its code and write no output file; each RUNS case
compiles and prints what it should (ELF here; with --pe and Wine 64 also as a PE, NOT RUN without Wine).
Last line: "r126 kinds: N checks, M failed".
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPILER = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
    else os.path.join(ROOT, 'sutram_compiler')
WINE = '/usr/lib/wine/wine64'
K = '    kosh k[8]\n    kosh_kship(k, 41)\n'

REFUSED = [  # (what, program, the code that must be in the message)
    ('t2: a kosh name given a raw buffer', 'mukhya() {\n' + K + '    vitti a = k\n    a = nirmmita(64)\n    likha(a[0])\n}\n', 'E_VITTI_PRAKAR'),
    ('t3: a raw name given a kosh in one branch', 'mukhya() {\n' + K + '    vitti a = nirmmita(64)\n    vitti x = grahan()\n'
     '    yadi (x == 1) {\n        a = k\n    }\n    likha(a[0])\n}\n', 'E_VITTI_PRAKAR'),
    ('t4: a mala name given a kosh', 'mukhya() {\n    mala m[2]\n' + K + '    vitti a = m\n    a = k\n    likha(a[5])\n}\n', 'E_VITTI_PRAKAR'),
    ('the inverse: a kosh name given a mala', 'mukhya() {\n    mala m[2]\n' + K + '    vitti a = k\n    a = m\n}\n', 'E_VITTI_PRAKAR'),
    ('a number, then a kosh', 'mukhya() {\n' + K + '    vitti a = 0\n    a = k\n    likha(a[0])\n}\n', 'E_VITTI_PRAKAR'),
    ('no initial value, then a kosh (already refused: a vitti needs a value)', 'mukhya() {\n' + K
     + '    vitti a\n    a = k\n}\n', 'E_MULYA_VINA'),
    ('a kosh given inside a loop that may not run', 'mukhya() {\n' + K + '    vitti a = nirmmita(8)\n'
     '    chakra i = 1 tak grahan() {\n        a = k\n    }\n    likha(a[0])\n}\n', 'E_VITTI_PRAKAR'),
    ('a kosh, then a mala-kosh of the other element kind', 'mukhya() {\n' + K + '    kosh dasham d[2]\n'
     '    vitti a = k\n    a = d\n}\n', 'E_VITTI_PRAKAR'),
    ('two sibling blocks, two kinds', 'mukhya() {\n' + K + '    mandapa {\n        vitti a = k\n    }\n'
     '    mandapa {\n        vitti a = nirmmita(8)\n    }\n}\n', 'E_VITTI_PRAKAR'),
    ('an untyped parameter given a kosh', 'prakriya f(a) {\n    kosh k[2]\n    a = k\n    nivartanam 0\n}\n'
     'mukhya() {\n    likha(f(0))\n}\n', 'E_VITTI_PRAKAR'),
    ('a chakra counter that is a kosh', 'mukhya() {\n' + K + '    chakra k = 1 tak 3 {\n        likha(k)\n    }\n}\n', 'E_VITTI_PRAKAR'),
    ('t6: a kosh stored in a mala cell', 'mukhya() {\n    mala m[2]\n' + K + '    m[0] = k\n}\n', 'E_KOSH_DVARA'),
    ('a kosh stored in a rachana field', 'rachana B = { x }\nmukhya() {\n    vitti b = nirmmita(8)\n' + K
     + '    b.x = k\n}\n', 'E_KOSH_DVARA'),
    ('a kosh stored in a module vitti', 'vitti g = 0\nmukhya() {\n' + K + '    g = k\n}\n', 'E_KOSH_DVARA'),
    ('a kosh passed to an untyped parameter', 'prakriya f(a) {\n    nivartanam a[0]\n}\nmukhya() {\n' + K
     + '    likha(f(k))\n}\n', 'E_KOSH_DVARA'),
    ('a kosh passed through a function value', 'prakriya f(a) {\n    nivartanam 0\n}\nmukhya() {\n' + K
     + '    vitti g = f\n    likha(g(k))\n}\n', 'E_KOSH_DVARA'),
    ('a kosh as pad8\'s address', 'mukhya() {\n' + K + '    likha(pad8(k))\n}\n', 'E_KOSH_DVARA'),
    ('a kosh as likh8\'s value', 'mukhya() {\n' + K + '    vitti p = nirmmita(8)\n    likh8(p, k)\n}\n', 'E_KOSH_DVARA'),
    ('a kosh as kosh_kship\'s value (a kosh in a kosh)', 'mukhya() {\n' + K + '    kosh j[2]\n    kosh_kship(j, k)\n}\n', 'E_KOSH_DVARA'),
    ('a kosh printed as a number', 'mukhya() {\n' + K + '    likha(k)\n}\n', 'E_KOSH_DVARA'),
    ('a kosh in ?:', 'mukhya() {\n' + K + '    kosh j[2]\n    vitti a = grahan() ? k : j\n}\n', 'E_KOSH_DVARA'),
    ('t5: k + 0', 'mukhya() {\n' + K + '    vitti a = k + 0\n    likha(a[5])\n}\n', 'E_KOSH_GANIT'),
    ('k - 0', 'mukhya() {\n' + K + '    vitti a = k - 0\n}\n', 'E_KOSH_GANIT'),
    ('k * 1', 'mukhya() {\n' + K + '    vitti a = k * 1\n}\n', 'E_KOSH_GANIT'),
    ('a prakriya returning a second name of its kosh', 'prakriya f(kosh k) {\n    vitti b = k\n    nivartanam b\n}\n'
     'mukhya() {\n' + K + '    vitti a = f(k)\n}\n', 'E_KOSH_DVARA'),
    ('a prakriya that returns a kosh on one path only', 'prakriya f(kosh k, x) {\n    yadi (x == 1) {\n'
     '        nivartanam k\n    }\n    nivartanam 0\n}\nmukhya() {\n' + K + '    vitti a = f(k, 1)\n}\n', 'E_KOSH_DVARA'),
    ('a kosh as a phal-prakriya\'s siddhi value', 'prakriya f(kosh k) {\n    nivartanam siddhi(k)\n}\nmukhya() {\n' + K
     + '    yadi dosh (q = f(k)) {\n        likha(0)\n    } anya {\n        likha(q[5])\n    }\n}\n', 'E_KOSH_DVARA'),
    ('a kosh as a dosh code', 'prakriya f(kosh k) {\n    nivartanam dosh(k)\n}\nmukhya() {\n' + K
     + '    vitti q = 0\n    yadi dosh (q = f(k)) {\n        likha(1)\n    }\n}\n', 'E_KOSH_DVARA'),
    ('a kosh-returning prakriya\'s result into a number', 'prakriya f(kosh k) {\n    nivartanam k\n}\n'
     'mukhya() {\n' + K + '    vitti a = 0\n    a = f(k)\n}\n', 'E_VITTI_PRAKAR'),
]

RUNS = [  # (what, program, stdin, stdout, exit)
    ('vitti a = k: a is the kosh', 'mukhya() {\n' + K + '    vitti a = k\n    likha(a[0])\n    kosh_kship(a, 7)\n'
     '    likha(kosh_gan(k))\n}\n', '', '41\n2\n', 0),
    ('a kosh alias is bounds-checked', 'mukhya() {\n' + K + '    vitti a = k\n    likha(a[5])\n}\n', '',
     'Sutram truti: mala ank seema atikram\n', 1),
    ('vitti a = (k), and a chain b = a', 'mukhya() {\n' + K + '    vitti a = (k)\n    vitti b = a\n    b = k\n'
     '    likha(b[0])\n}\n', '', '41\n', 0),
    ('a = a and a = k again: the same kind', 'mukhya() {\n' + K + '    kosh j[2]\n    kosh_kship(j, 5)\n'
     '    vitti a = k\n    a = a\n    a = j\n    likha(a[0])\n}\n', '', '5\n', 0),
    ('a prakriya returning its kosh parameter: the result is a checked kosh',
     'prakriya f(kosh k) {\n    nivartanam k\n}\nmukhya() {\n' + K + '    vitti a = f(k)\n    likha(a[0])\n'
     '    likha(kosh_gan(a))\n    likha(a[5])\n}\n', '', '41\n1\nSutram truti: mala ank seema atikram\n', 1),
    ('a prakriya returning a kosh it declares', 'prakriya nava() {\n    kosh j[4]\n    kosh_kship(j, 9)\n'
     '    nivartanam j\n}\nmukhya() {\n    vitti a = nava()\n    likha(a[0])\n    likha(kosh_gan(a))\n}\n', '', '9\n1\n', 0),
    ('a chain of returns: g returns f(k), f returns k', 'prakriya f(kosh k) {\n    nivartanam k\n}\n'
     'prakriya g(kosh k) {\n    nivartanam f(k)\n}\nmukhya() {\n' + K + '    vitti a = g(k)\n    likha(a[0])\n}\n',
     '', '41\n', 0),
    ('a recursive prakriya returning its kosh', 'prakriya f(kosh k, n) {\n    yadi (n == 0) {\n'
     '        nivartanam k\n    }\n    nivartanam f(k, n - 1)\n}\nmukhya() {\n' + K + '    vitti a = f(k, 3)\n'
     '    likha(a[0])\n}\n', '', '41\n', 0),
    ('a kosh to a kosh parameter, a dasham kosh to a dasham one', 'prakriya s(kosh k) {\n    nivartanam k[0]\n}\n'
     'prakriya d(kosh dasham k) {\n    nivartanam k[0]\n}\nmukhya() {\n' + K + '    kosh dasham e[2]\n'
     '    kosh_kship(e, 2.5)\n    likha(s(k))\n    likha(d(e))\n}\n', '', '41\n2.500000\n', 0),
    ('a mala alias and a mala to an untyped parameter (unchanged)', 'prakriya f(a) {\n    nivartanam a[1]\n}\n'
     'mukhya() {\n    mala m[3]\n    m[1] = 6\n    vitti b = m\n    likha(b[1])\n    likha(f(m))\n}\n', '', '6\n6\n', 0),
    ('a slice alias', 'mukhya() {\n    mala m[6]\n    m[2] = 4\n    vitti s = m[2:5]\n    vitti t = s\n'
     '    likha(t[0])\n}\n', '', '4\n', 0),
    ('a raw buffer reassigned raw, and a number reassigned', 'mukhya() {\n    vitti p = nirmmita(16)\n'
     '    likh8(p, 3)\n    p = nirmmita(16)\n    likh8(p, 4)\n    likha(pad8(p))\n    vitti n = 1\n    n = n + 1\n'
     '    likha(n)\n}\n', '', '4\n2\n', 0),
    ('two prakriyas, one name, two kinds (each prakriya its own)', 'prakriya f() {\n    vitti a = nirmmita(8)\n'
     '    likh8(a, 5)\n    nivartanam pad8(a)\n}\nmukhya() {\n' + K + '    vitti a = k\n    likha(a[0])\n'
     '    likha(f())\n}\n', '', '41\n5\n', 0),
]


def main():
    checks = fails = 0
    pe = '--pe' in sys.argv

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    with tempfile.TemporaryDirectory() as d:
        p, exe = os.path.join(d, 'p.sm'), os.path.join(d, 'p.bin')
        for what, src, code in REFUSED:
            open(p, 'w').write(src)
            if os.path.exists(exe):
                os.remove(exe)
            c = subprocess.run([COMPILER, p, exe], capture_output=True, text=True, cwd=d)
            msg = c.stdout + c.stderr
            ok = c.returncode == 1 and not os.path.exists(exe) and (code is None and 'Sutram truti' in msg or code in msg)
            check(ok, f'refused, no output: {what} ({code or "an error"}){"" if ok else " -- got rc=%d %r" % (c.returncode, msg[:200])}')
        for what, src, stdin, want, wexit in RUNS:
            open(p, 'w').write(src)
            c = subprocess.run([COMPILER, p, exe], capture_output=True, text=True, cwd=d)
            if c.returncode:
                check(False, f'{what}: did not compile: {(c.stdout + c.stderr)[:200]}')
                continue
            r = subprocess.run([exe], input=stdin, capture_output=True, text=True, timeout=30)
            got = r.stdout + r.stderr
            check(got == want and r.returncode == wexit, f'runs (ELF): {what}: {got!r} exit {r.returncode}'
                  + ('' if got == want and r.returncode == wexit else f' (want {want!r} exit {wexit})'))
            if pe:
                if not os.path.exists(WINE):
                    print(f'NOT RUN  PE: {what}: no Wine here')
                    continue
                pexe = os.path.join(d, 'p.exe')
                c = subprocess.run([COMPILER, p, pexe], capture_output=True, text=True, cwd=d)
                r = subprocess.run([WINE, pexe], input=stdin, capture_output=True, timeout=120, cwd=d,
                                   env=dict(os.environ, WINEDEBUG='-all'))
                got = (r.stdout + r.stderr).decode('latin-1').replace('\r', '')
                okp = c.returncode == 0 and got == want and r.returncode == wexit
                # R155: on a failure, everything needed to tell Wine's noise from the program's: what was wanted, the
                # compile result, and stdout and stderr apart (R154 had one unexplained failure here).
                check(okp, f'runs (PE, Wine): {what}: {got!r} exit {r.returncode}' + ('' if okp else
                      f' (want {want!r} exit {wexit}; compile rc {c.returncode}; stdout {r.stdout[:300]!r}; stderr {r.stderr[:300]!r})'))
    print(f'r126 kinds: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
