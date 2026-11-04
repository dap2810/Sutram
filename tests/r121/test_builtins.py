#!/usr/bin/env python3
"""R121: the two builtins Windows exposed, fixed - checked on Linux ELF (run) and PE (compiled; run under Wine
when /usr/lib/wine/wine64 is present, else that half is NOT RUN and said so).

  * anka_akshar(code) is a new one-character string that outlives the call: printed at once, kept across a
    prakriya call, two kept at the same time, and 200,000 calls in a loop (up to v297 each call left the
    stack 8 bytes lower and the character below the stack pointer);
  * vartani_sandhi(dst, src) appends into a writable dst and returns it (R54's raw test: "YES" + "!" -> 4);
  * a literal destination is refused when compiled (E_VARTANI_STHIRA, at the literal, no output written);
  * a literal reached through a variable stops the program at run time (E_VARTANI_STHIRA on stderr, exit 1)
    instead of writing into the program's code.
Last line: "r121 builtins: N checks, M failed".
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPILER = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
    else os.path.join(ROOT, 'sutram_compiler')
WINE = '/usr/lib/wine/wine64'

CASES = [  # (name, program, stdout, exit)
    ('anka_akshar printed at once', 'mukhya() {\n    shabda(anka_akshar(66))\n    likha("\\n")\n}\n', 'B\n', 0),
    ('anka_akshar kept across a prakriya call',
     'prakriya f(x) {\n    vitti a = x * 3\n    nivartanam a + 1\n}\nmukhya() {\n    vitti c = anka_akshar(66)\n'
     '    vitti d = anka_akshar(67)\n    vitti y = f(5)\n    shabda(c)\n    shabda(d)\n    likha("\\n")\n    likha(y)\n}\n',
     'BC\n16\n', 0),
    ('anka_akshar 200,001 times in a loop (tak is inclusive), the last kept: 200000 % 26 = 8, so I',
     'mukhya() {\n    vitti c = 0\n    chakra i = 0 tak 200000 {\n        c = anka_akshar(65 + i % 26)\n    }\n'
     '    shabda(c)\n    likha("\\n")\n}\n', 'I\n', 0),
    ('vartani_sandhi into a writable buffer, returned',
     'mukhya() {\n    vitti b = nirmmita(16)\n    vartani_pratilip(b, "ab")\n    vitti s = vartani_sandhi(b, "cd")\n'
     '    shabda(s)\n    likha("\\n")\n    shabda(b)\n    likha("\\n")\n}\n', 'abcd\nabcd\n', 0),
    ('vartani_sandhi in place, as R54 tests it ("YES" + "!" is 4 long)',
     'mukhya() {\n    vitti b = nirmmita(64)\n    vartani_pratilip(b + 8, "YES")\n    vartani_sandhi(b + 8, "!")\n'
     '    likha(vartani_aayam(b + 8))\n}\n', '4\n', 0),
    ('vartani_sandhi on a literal through a variable stops at run time',
     'mukhya() {\n    vitti s = "ab"\n    vitti t = vartani_sandhi(s, "cd")\n    shabda(t)\n    likha("never\\n")\n}\n',
     '', 1),
]
REFUSED = 'mukhya() {\n    vitti s = vartani_sandhi("ab", "cd")\n    shabda(s)\n}\n'


def main():
    checks = fails = 0
    notrun = []

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    wine = os.path.exists(WINE)
    env = dict(os.environ, WINEDEBUG='-all')
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
                if ext == 'exe' and not wine:
                    notrun.append(what)
                    continue
                cmd = [out] if ext == 'bin' else [WINE, out]
                r = subprocess.run(cmd, capture_output=True, timeout=120, env=env)
                so = r.stdout.decode('latin-1').replace('\r', '')
                se = r.stderr.decode('latin-1')
                ok = so == want and r.returncode == code and (code == 0 or '[E_VARTANI_STHIRA]' in se)
                check(ok, f'{what} ({ext}{", Wine" if ext == "exe" else ""}): stdout {so!r} exit {r.returncode} '
                          f'(want {want!r} exit {code})')
        open(p, 'w').write(REFUSED)
        for ext in ('bin', 'exe'):
            out = os.path.join(d, 'r.' + ext)
            c = subprocess.run([COMPILER, p, out], capture_output=True, text=True)
            msg = c.stdout + c.stderr
            ok = c.returncode == 1 and '[E_VARTANI_STHIRA]' in msg and 'p.sm:2:30' in msg and not os.path.exists(out)
            check(ok, f'vartani_sandhi("ab", ...) refused when compiled ({ext}): exit {c.returncode}, '
                      f'at 2:30 {"p.sm:2:30" in msg}, no output {not os.path.exists(out)}')
    if notrun:
        print(f'NOT RUN  {len(notrun)} PE runs (no Wine here)')
    print(f'r121 builtins: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
