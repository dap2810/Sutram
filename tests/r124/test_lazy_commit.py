#!/usr/bin/env python3
"""R124: Windows commits what a program touches, not what it reserves.

The PE runtime now reserves an mmap with MAP_NORESERVE (the arena, each kosh region) and a vectored exception
handler commits 64 KiB at a time where the program first touches it; ReadFile / WriteFile buffers are touched
first. Checked with the PE program run under Wine 64 (NOT RUN, and said, without it):

  * correctness: a 100 MB nirmmita written page by page and summed back; a kosh of 200,000 numbers grown from 1;
    1000 blocks each with a kosh; a file written, then read into a fresh, untouched nirmmita buffer;
  * commit: Wine maps MEM_RESERVE inaccessible and MEM_COMMIT read-write, so the read-write private anonymous
    mappings of the process are what it committed. One nirmmita(64) must commit under 1 MB (it was 1 GiB);
    100 koshes under 16 MB (they were 6.7 GB); a 100 MB buffer touched on every page about 100 MB.
Last line: "r124 lazy commit: N checks, M failed".
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPILER = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
    else os.path.join(ROOT, 'sutram_compiler')
WINE = '/usr/lib/wine/wine64'

RUNS = [  # (what, program, stdout)
    ('a 100 MB nirmmita written on every page and summed back',
     'mukhya() {\n    vitti b = nirmmita(100000000)\n    vitti i = 0\n    yavat (i < 100000000) {\n'
     '        likh8(b + i, 3)\n        i = i + 4096\n    }\n    vitti s = 0\n    i = 0\n'
     '    yavat (i < 100000000) {\n        s = s + pad8(b + i)\n        i = i + 4096\n    }\n    likha(s)\n}\n',
     '73245\n'),
    ('a kosh grown from 1 to 200,000 numbers',
     'mukhya() {\n    kosh k[1]\n    chakra i = 1 tak 200000 {\n        kosh_kship(k, i)\n    }\n'
     '    likha(kosh_gan(k))\n    likha(k[199999])\n}\n', '200000\n200000\n'),
    ('1000 blocks, each with a kosh of 100',
     'mukhya() {\n    vitti t = 0\n    chakra j = 1 tak 1000 {\n        mandapa {\n            kosh k[1]\n'
     '            chakra i = 1 tak 100 {\n                kosh_kship(k, i)\n            }\n'
     '            t = t + kosh_gan(k)\n        }\n    }\n    likha(t)\n}\n', '100000\n'),
    ('a file written, then read into a fresh, untouched buffer',
     'yoj patra\nmukhya() {\n    likha(patra_likh_sarv("r124.txt", "pustakam\\n", 9))\n'
     '    vitti b = nirmmita(200000)\n    vitti n = patra_path_sarv("r124.txt", b + 100000, 64)\n'
     '    likha(n)\n    dvaram_likha(1, b + 100000, n)\n}\n', '9\n9\npustakam\n'),
]
COMMIT = [  # (what, program, the most it may commit in MB, the least)
    ('one nirmmita(64)', 'mukhya() {\n    vitti b = nirmmita(64)\n    likha("ready\\n")\n    vitti x = grahan()\n}\n', 1, 0),
    ('100 koshes of 1', 'mukhya() {\n    chakra i = 1 tak 100 {\n        kosh k[1]\n        kosh_kship(k, i)\n    }\n'
     '    likha("ready\\n")\n    vitti x = grahan()\n}\n', 16, 0),
    ('a 100 MB nirmmita, every page written',
     'mukhya() {\n    vitti b = nirmmita(100000000)\n    vitti i = 0\n    yavat (i < 100000000) {\n'
     '        likh8(b + i, 1)\n        i = i + 4096\n    }\n    likha("ready\\n")\n    vitti x = grahan()\n}\n', 110, 95),
]
BASE = 'mukhya() {\n    likha("ready\\n")\n    vitti x = grahan()\n}\n'


def rw_mb(pid):
    t = 0
    for l in open(f'/proc/{pid}/maps'):
        f = l.split()
        if len(f) == 5 and f[1] == 'rw-p':
            a, b = (int(x, 16) for x in f[0].split('-'))
            t += b - a
    return t / 1e6


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    if not os.path.exists(WINE):
        print('NOT RUN  no Wine here: the PE runs and the commit checks need it')
        print('r124 lazy commit: 0 checks, 0 failed')
        return 0
    env = dict(os.environ, WINEDEBUG='-all')
    with tempfile.TemporaryDirectory() as d:
        p, exe = os.path.join(d, 'p.sm'), os.path.join(d, 'p.exe')
        for what, src, want in RUNS:
            open(p, 'w').write(src)
            c = subprocess.run([COMPILER, p, exe], capture_output=True, text=True)
            if c.returncode:
                check(False, f'{what}: did not compile: {(c.stdout + c.stderr)[:160]}')
                continue
            r = subprocess.run([WINE, exe], capture_output=True, timeout=300, env=env, cwd=d)
            so = r.stdout.decode('latin-1').replace('\r', '')
            check(so == want and r.returncode == 0, f'{what} (PE, Wine): {so!r} exit {r.returncode} (want {want!r})')

        def committed(src):
            open(p, 'w').write(src)
            c = subprocess.run([COMPILER, p, exe], capture_output=True)
            if c.returncode:
                return None
            pr = subprocess.Popen([WINE, exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env, cwd=d)
            pr.stdout.readline()
            mb = rw_mb(pr.pid)
            pr.stdin.write(b'1\r\n')
            pr.stdin.flush()
            pr.wait(timeout=60)
            return mb
        base = committed(BASE)
        for what, src, most, least in COMMIT:
            mb = committed(src)
            got = None if mb is None or base is None else mb - base
            check(got is not None and least <= got <= most,
                  f'{what}: commits {got if got is None else round(got, 1)} MB (allowed {least}-{most})')
    print(f'r124 lazy commit: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
