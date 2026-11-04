#!/usr/bin/env python3
"""R127: a kosh is a descriptor that never moves; growth moves its elements, and every name sees it.

v301 made each kosh a 64 MiB region and grew it in place, so a second name (vitti a = k) parted from k
past 8,388,603 numbers (at 4,194,305 pushes from one), and a program could hold about 15 koshes under a
1 GiB address limit. From v302 a kosh is a small descriptor in the arena; a kosh past 64 KiB of elements
gets a region (reserved, not committed) and grows in place inside it, moving to a larger one, through the
descriptor, when it outgrows it; the old region is given back.

Checks (ELF; with --pe and Wine 64 the run checks again as PE, NOT RUN without Wine):
  * two names stay one past 4,194,305 pushes and past a region move (9,000,000);
  * 1,000 koshes under a 300 MB address limit, 20,000 koshes (no region each);
  * pop / peek / dequeue / clear / a dasham kosh / a slice passed on / a kosh parameter, all through d;
  * no memory for a kosh, or for its growth: a message and exit 1, not SIGSEGV (--fail-alloc);
  * a slice of a kosh kept in a name is refused (E_KOSH_VIBHAG): the next growth would leave it behind;
  * a moved region is given back: 20,000,000 numbers peak under 200 MB (it holds 160 MB);
  * R128 (ChatGPT R203): an index or slice bound that grows or shrinks the kosh is read after it (F1); a
    capacity whose bytes would wrap stops (F2); parimana() counts a region kosh's bytes (F3).
Last line: "r127 descriptor: N checks, M failed".
"""
import os, resource, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPILER = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
    else os.path.join(ROOT, 'sutram_compiler')
WINE = '/usr/lib/wine/wine64'


def grow(n):
    return ('mukhya() {\n    kosh k[1]\n    vitti a = k\n    vitti z = nirmmita(8)\n'
            f'    chakra i = 1 tak {n} {{\n        kosh_kship(k, i)\n    }}\n    k[0] = 99\n'
            f'    likha(kosh_gan(a))\n    likha(a[0])\n    likha(a[{n} - 1])\n}}\n')


RUNS = [  # (what, program, compile flags, address limit in KB or 0, stdout, exit, also as PE)
    ('two names stay one past 4,194,305 pushes', grow(4194305), [], 0, '4194305\n99\n4194305\n', 0, True),
    ('two names stay one past a region move (9,000,000)', grow(9000000), [], 0, '9000000\n99\n9000000\n', 0, True),
    ('1,000 koshes under a 300 MB address limit', 'mukhya() {\n    vitti t = 0\n    chakra j = 1 tak 1000 {\n'
     '        kosh k[1]\n        kosh_kship(k, j)\n        kosh_kship(k, j)\n        t = t + kosh_gan(k)\n    }\n'
     '    likha(t)\n}\n', [], 300000, '2000\n', 0, False),
    ('20,000 koshes', 'mukhya() {\n    vitti t = 0\n    chakra j = 1 tak 20000 {\n        kosh k[4]\n'
     '        kosh_kship(k, j)\n        t = t + k[0]\n    }\n    likha(t)\n}\n', [], 0, '200010000\n', 0, True),
    ('pop, peek, dequeue, clear through the descriptor', 'mukhya() {\n    kosh k[1]\n    vitti z = nirmmita(8)\n'
     '    chakra i = 1 tak 20 {\n        kosh_kship(k, i)\n    }\n    vitti a = k\n    likha(kosh_hri(a))\n'
     '    likha(kosh_iksh(k))\n    likha(kosh_apanay(a))\n    likha(k[0])\n    likha(kosh_gan(k))\n'
     '    kosh_shodh(a)\n    likha(kosh_rikt(k))\n}\n', [], 0, '20\n19\n1\n2\n18\n1\n', 0, True),
    ('a dasham kosh, a slice passed on, a kosh parameter', 'prakriya yog(vibhag s) {\n    vitti t = 0\n'
     '    chakra i = 0 tak pankti_gan(s) - 1 {\n        t = t + s[i]\n    }\n    nivartanam t\n}\n'
     'prakriya pratham(kosh k) {\n    nivartanam k[0]\n}\nmukhya() {\n    kosh dasham d[0]\n'
     '    kosh_kship(d, 1.5)\n    kosh_kship(d, 2.5)\n    likha(d[1])\n    kosh k[1]\n    vitti z = nirmmita(8)\n'
     '    chakra i = 1 tak 10 {\n        kosh_kship(k, i)\n    }\n    likha(yog(k[2:5]))\n    likha(yog(k))\n'
     '    likha(pratham(k))\n}\n', [], 0, '2.500000\n12\n55\n1\n', 0, True),
    ('no memory to make a kosh: a message', 'mukhya() {\n    kosh k[1]\n    kosh_kship(k, 1)\n}\n',
     ['--fail-alloc', '1'], 0, 'Sutram truti: kosh rachayitum smritih na labdha\n', 1, False),
    ('no memory to grow a kosh: a message', 'mukhya() {\n    kosh k[1]\n    chakra i = 1 tak 10 {\n'
     '        kosh_kship(k, i)\n        vitti p = nirmmita(16)\n    }\n}\n', ['--fail-alloc', '3'], 0,
     'Sutram truti: kosh vardhayitum smritih na labdha - kosh yatha asit tatha eva\n', 1, False),
    # R128 (ChatGPT R203): the index or slice bounds may grow or shrink the kosh - read it after them
    ('an index that grows the kosh past a region move (R203 F1; v302 SIGSEGV)', 'mukhya() {\n    kosh k[1]\n'
     '    vitti z = nirmmita(8)\n    chakra i = 1 tak 8388608 {\n        kosh_kship(k, i)\n    }\n'
     '    likha(k[kosh_kship(k, 5) - 2])\n}\n', [], 0, '8388608\n', 0, False),
    ('k[i] = v where i grows the kosh (R203 F1)', 'mukhya() {\n    kosh k[1]\n    vitti z = nirmmita(8)\n'
     '    kosh_kship(k, 1)\n    k[kosh_kship(k, 2) - 1] = 9\n    likha(k[0])\n    likha(k[1])\n}\n', [], 0, '1\n9\n', 0, True),
    ('an index that shrinks the kosh is checked against the new length (R203 F1)', 'mukhya() {\n    kosh k[4]\n'
     '    kosh_kship(k, 1)\n    kosh_kship(k, 2)\n    likha(k[kosh_hri(k) - 1])\n}\n', [], 0,
     'Sutram truti: mala ank seema atikram\n', 1, False),
    ('a slice bound that grows the kosh (R203 F1)', 'prakriya pratham(vibhag s) {\n    nivartanam s[0]\n}\n'
     'mukhya() {\n    kosh k[1]\n    vitti z = nirmmita(8)\n    kosh_kship(k, 7)\n'
     '    likha(pratham(k[kosh_kship(k, 8) - 2:2]))\n}\n', [], 0, '7\n', 0, True),
    ('a capacity whose bytes would wrap is refused at run time (R203 F2; v302 overwrote memory)', 'mukhya() {\n'
     '    kosh k[2305843009213693952]\n    vitti p = nirmmita(16)\n    likh8(p, 77)\n    chakra i = 1 tak 8 {\n'
     '        kosh_kship(k, i)\n    }\n    likha(pad8(p))\n}\n', [], 0,
     'Sutram truti: kosh rachayitum smritih na labdha\n', 1, True),
    ('parimana() counts a region kosh (R203 F3; v302 counted the clobbered r11)', 'mukhya() {\n    kosh k[1]\n'
     '    vitti z = nirmmita(8)\n    chakra i = 1 tak 20000 {\n        kosh_kship(k, i)\n    }\n    likha(parimana())\n'
     '}\n', [], 0, '294976\n', 0, False),
]


def main():
    checks = fails = 0
    pe = '--pe' in sys.argv

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    def limit(kb):
        return (lambda: resource.setrlimit(resource.RLIMIT_AS, (kb * 1024, kb * 1024))) if kb else None

    with tempfile.TemporaryDirectory() as d:
        p, exe = os.path.join(d, 'p.sm'), os.path.join(d, 'p.bin')
        for what, src, flags, kb, want, wexit, as_pe in RUNS:
            open(p, 'w').write(src)
            c = subprocess.run([COMPILER] + flags + [p, exe], capture_output=True, text=True, cwd=d)
            if c.returncode:
                check(False, f'{what}: did not compile: {(c.stdout + c.stderr)[:200]}')
                continue
            r = subprocess.run([exe], capture_output=True, text=True, timeout=120, preexec_fn=limit(kb))
            got = r.stdout + r.stderr
            check(got == want and r.returncode == wexit, f'{what} (ELF): {got!r} exit {r.returncode}'
                  + ('' if got == want and r.returncode == wexit else f' (want {want!r} exit {wexit})'))
            if pe and as_pe:
                if not os.path.exists(WINE):
                    print(f'NOT RUN  {what} (PE): no Wine here')
                    continue
                pexe = os.path.join(d, 'p.exe')
                c = subprocess.run([COMPILER] + flags + [p, pexe], capture_output=True, text=True, cwd=d)
                r = subprocess.run([WINE, pexe], capture_output=True, timeout=300, cwd=d,
                                   env=dict(os.environ, WINEDEBUG='-all'))
                got = (r.stdout + r.stderr).decode('latin-1').replace('\r', '')
                check(c.returncode == 0 and got == want and r.returncode == wexit,
                      f'{what} (PE, Wine): {got!r} exit {r.returncode}')
        # a slice of a kosh kept in a name
        open(p, 'w').write('mukhya() {\n    kosh k[2]\n    kosh_kship(k, 1)\n    vitti s = k[0:1]\n    likha(s[0])\n}\n')
        if os.path.exists(exe):
            os.remove(exe)
        c = subprocess.run([COMPILER, p, exe], capture_output=True, text=True, cwd=d)
        check(c.returncode == 1 and 'E_KOSH_VIBHAG' in c.stdout + c.stderr and not os.path.exists(exe),
              'a slice of a kosh kept in a name is refused (E_KOSH_VIBHAG), no output')
        # a moved region is given back
        open(p, 'w').write(grow(20000000))
        subprocess.run([COMPILER, p, exe], capture_output=True, cwd=d)
        r = subprocess.run(['/usr/bin/time', '-f', '%M', exe], capture_output=True, text=True, timeout=120)
        try:
            kb = int(r.stderr.strip().split('\n')[-1])
        except ValueError:
            kb = -1
        check(r.stdout == '20000000\n99\n20000000\n' and 0 < kb < 200000,
              f'20,000,000 numbers: peak {kb // 1024} MB (under 200: the 64 MiB region it left is given back)')
    print(f'r127 descriptor: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
