#!/usr/bin/env python3
"""R123: the Windows memory model, merged from the Windows round 4 branch (PR #65): on PE as on ELF, nirmmita
uses the arena, a mandapa gives its memory back, `mandapa parimita N` refuses past its budget, parimana()
reports the bytes held, and a kosh has a region and never moves (so a second name stays right).

Each case is compiled for ELF and PE by the compiler given; the ELF binary is run, and the PE one under Wine 64
when /usr/lib/wine/wine64 exists (else that half is NOT RUN, and said). Both must print the same, and that must be
the expected text below - the Linux values the reference documents (section 19), worked out, not recorded.
Also: ELF output of a program without a kosh or nirmmita is unchanged by the merge (it never was PE-dependent),
and --fail-alloc's anka_akshar failure still stops with E_VARTANI_SMRITI (the branch's test, for v298's builtin).
Last line: "r123 pe memory: N checks, M failed".
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPILER = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
    else os.path.join(ROOT, 'sutram_compiler')
WINE = '/usr/lib/wine/wine64'

CASES = [  # (what, program, stdout, exit)
    ('parimana counts nirmmita, a block and a kosh',
     'mukhya() {\n    likha(parimana())\n    vitti a = nirmmita(64)\n    likha(parimana())\n    mandapa {\n'
     '        vitti b = nirmmita(1000)\n        likha(parimana())\n    }\n    likha(parimana())\n}\n',
     '0\n64\n1072\n64\n', 0),
    ('mandapa parimita refuses past its budget',
     'mukhya() {\n    mandapa parimita 100 {\n        vitti a = nirmmita(64)\n        likha("one fits\\n")\n'
     '        vitti b = nirmmita(64)\n        likha("not reached\\n")\n    }\n}\n',
     'one fits\nSutram truti [E_PARIMITA]: pankti 2 - mandape parimitat adhikam nirmmitam na sambhavati (parimitih 100 baait)\n', 1),
    ('a budget that fits is not refused',
     'mukhya() {\n    mandapa parimita 1000 {\n        vitti a = nirmmita(64)\n        vitti b = nirmmita(64)\n'
     '        likha("both fit\\n")\n    }\n}\n', 'both fit\n', 0),
    ('a second name for a growing kosh stays right (it never moves)',
     'mukhya() {\n    kosh k[1]\n    kosh_kship(k, 41)\n    vitti a = k\n    vitti x = nirmmita(16)\n'
     '    kosh_kship(k, 42)\n    a[0] = 99\n    likha(k[0])\n    likha(kosh_gan(a))\n}\n', '99\n2\n', 0),
]


def main():
    checks = fails = 0
    notrun = 0
    env = dict(os.environ, WINEDEBUG='-all')

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'p.sm')
        for what, src, want, code in CASES:
            open(p, 'w').write(src)
            for ext in ('bin', 'exe'):
                out = os.path.join(d, 'p.' + ext)
                c = subprocess.run([COMPILER, p, out], capture_output=True, text=True)
                if c.returncode:
                    check(False, f'{what} ({ext}): did not compile: {(c.stdout + c.stderr)[:160]}')
                    continue
                if ext == 'exe' and not os.path.exists(WINE):
                    notrun += 1
                    continue
                r = subprocess.run([out] if ext == 'bin' else [WINE, out], capture_output=True, timeout=120, env=env)
                so = r.stdout.decode('latin-1').replace('\r', '')
                ok = so == want and r.returncode == code
                check(ok, f'{what} ({ext}{", Wine" if ext == "exe" else ""}): {so!r} exit {r.returncode} (want {want!r} exit {code})')
        open(p, 'w').write('mukhya() {\n    shabda(anka_akshar(66))\n}\n')
        out = os.path.join(d, 'f.bin')
        c = subprocess.run([COMPILER, '--fail-alloc', '1', p, out], capture_output=True, text=True)
        r = subprocess.run([out], capture_output=True) if c.returncode == 0 else None
        check(r is not None and r.returncode == 1 and b'E_VARTANI_SMRITI' in r.stdout + r.stderr,
              f'--fail-alloc 1: anka_akshar stops with E_VARTANI_SMRITI (exit {r.returncode if r else "-"})')
    if notrun:
        print(f'NOT RUN  {notrun} PE runs (no Wine here)')
    print(f'r123 pe memory: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
