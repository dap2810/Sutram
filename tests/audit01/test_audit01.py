#!/usr/bin/env python3
"""AUDIT-01 (the owner's audit, 10 November 2026): five defects found by 150 probes, closed in v322.

  1  A prakriya that ends without nivartanam returned whatever was last computed (f(5) gave 15). It returns 0.
  2  krama / agrim outside any loop compiled and did nothing. Refused: E_AVARTAN_VINA.
  3  mala m[n] with a negative or impossible n was SIGSEGV. A negative number written out is refused when
     compiled, anything else stops when run: E_MALA_PARIMAN.
  4  likha(m) on a mala printed its address. Refused: E_MALA_LIKHA.
  5  A kosh as a condition was always true. Refused: E_KOSH_SATYA (as a string is, E_VARTANI_SATYA).

Each case: the program, and either what it prints, or the error code it is refused with when compiled, or the
error code it stops with when run (exit 1 - not a signal).

Usage: python3 tests/audit01/test_audit01.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0


def M(body):
    return 'mukhya() {\n' + ''.join('    ' + l + '\n' for l in body.split(';') if l.strip()) + '}\n'


F = 'prakriya f(a) {\n'
# (name, what, source, ('prints', text) | ('refused', code) | ('stops', code))
CASES = [
    ('noret-value', 'a prakriya without nivartanam returns 0, not the last value computed',
     F + '    vitti b = a * 3\n}\nmukhya() {\n    likha(f(5), "\\n")\n}\n', ('prints', '0')),
    ('noret-statement', 'the same when its last statement is a likha',
     F + '    likha("in f\\n")\n}\nmukhya() {\n    vitti r = f(5)\n    likha(r, "\\n")\n}\n', ('prints', 'in f\n0')),
    ('noret-loop', 'the same when it ends with a loop',
     'prakriya f(n) {\n    vitti s = 0\n    chakra i = 1 tak n {\n        s = s + i\n    }\n}\nmukhya() {\n    likha(f(4), "\\n")\n}\n', ('prints', '0')),
    ('noret-some-paths', 'nivartanam on one path only: the other path returns 0',
     F + '    yadi (a > 0) {\n        nivartanam 7\n    }\n}\nmukhya() {\n    likha(f(1), " ", f(0), "\\n")\n}\n', ('prints', '7 0')),
    ('ret-as-before', 'a prakriya that ends with nivartanam is as before',
     F + '    nivartanam a * 3\n}\nmukhya() {\n    likha(f(5), "\\n")\n}\n', ('prints', '15')),
    ('krama-outside', 'krama as a statement of mukhya', M('krama;likha(1, "\\n")'), ('refused', 'E_AVARTAN_VINA')),
    ('agrim-outside', 'agrim as a statement of mukhya', M('agrim;likha(1, "\\n")'), ('refused', 'E_AVARTAN_VINA')),
    ('krama-under-yadi', 'krama under a yadi with no loop around it', M('vitti a = 1;yadi (a) {;krama;};likha(2, "\\n")'), ('refused', 'E_AVARTAN_VINA')),
    ('krama-in-callee', 'krama in a prakriya called from inside a loop: the loop is not its own',
     F + '    krama\n    nivartanam 7\n}\nmukhya() {\n    chakra i = 1 tak 2 {\n        likha(f(1), "\\n")\n    }\n}\n', ('refused', 'E_AVARTAN_VINA')),
    ('krama-in-chakra', 'krama inside a chakra is as before', M('chakra i = 1 tak 5 {;yadi (i == 3) {;krama;};likha(i);}'), ('prints', '1\n2')),
    ('agrim-in-yavat', 'agrim inside a yavat is as before', M('vitti i = 0;yavat (i < 3) {;i = i + 1;yadi (i == 2) {;agrim;};likha(i);}'), ('prints', '1\n3')),
    ('mala-negative-number', 'mala m[-3]', M('mala m[-3];likha(1, "\\n")'), ('refused', 'E_MALA_PARIMAN')),
    ('mala-negative-computed', 'a computed negative length', M('vitti n = 0 - 1;mala m[n];likha(1, "\\n")'), ('stops', 'E_MALA_PARIMAN')),
    ('mala-16-gb-computed', 'a computed length of 2,000,000,000 (16 GB)', M('vitti n = 2000000000;mala m[n];m[0] = 1;likha(m[0], "\\n")'), ('stops', 'E_MALA_PARIMAN')),
    ('mala-16-gb-number', 'mala m[2000000000]', M('mala m[2000000000];m[0] = 1;likha(m[0], "\\n")'), ('stops', 'E_MALA_PARIMAN')),
    ('mala-zero', 'mala m[0] is as before', M('mala m[0];likha(1, "\\n")'), ('prints', '1')),
    ('mala-computed-ok', 'a computed length that is fine', M('vitti n = 1000;mala m[n];m[n - 1] = 7;likha(m[n - 1], "\\n")'), ('prints', '7')),
    ('likha-mala', 'likha(m)', M('mala m[2];likha(m, "\\n")'), ('refused', 'E_MALA_LIKHA')),
    ('likha-mala-second', 'a mala as a later value of likha', M('mala m[2];likha("m = ", m, "\\n")'), ('refused', 'E_MALA_LIKHA')),
    ('likha-element', 'likha(m[0]) is as before', M('mala m[2];m[0] = 4;likha(m[0], "\\n")'), ('prints', '4')),
    ('kosh-condition', 'yadi (k)', M('kosh k[1];yadi (k) {;likha("yes\\n");}'), ('refused', 'E_KOSH_SATYA')),
    ('kosh-yavat', 'yavat (k)', M('kosh k[1];yavat (k) {;krama;}'), ('refused', 'E_KOSH_SATYA')),
    ('kosh-length-condition', 'yadi (kosh_gan(k) > 0) is as before', M('kosh k[1];yadi (kosh_gan(k) > 0) {;likha("yes\\n");} anya {;likha("empty\\n");}'), ('prints', 'empty')),
]


def check(ok, what):
    global checks, fails
    checks += 1
    print(('ok    ' if ok else 'FAIL  ') + what)
    fails += not ok


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors='replace', timeout=120)
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    compiler = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        compiler = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    d = tempfile.mkdtemp(prefix='a1_')
    try:
        for name, what, src, (kind, want) in CASES:
            open(os.path.join(d, name + '.sm'), 'w').write(src)
            rc, out = run([compiler, name + '.sm', name + '.bin'], d)
            made = os.path.exists(os.path.join(d, name + '.bin'))
            if kind == 'refused':
                check(rc == 1 and not made and f'[{want}]' in out.split('\n')[0], f'{name}: {what} - refused when compiled, {want}' + ('' if not made else '  (it compiled)'))
                continue
            if not made:
                check(False, f'{name}: {what} - does not compile: {out[:100]}')
                continue
            rc, out = run([os.path.join(d, name + '.bin')], d)
            if kind == 'stops':
                check(rc == 1 and f'[{want}]' in out, f'{name}: {what} - stops with {want}, exit 1 (got exit {rc})')
            else:
                check(rc == 0 and out == want, f'{name}: {what} - prints {want!r}' + ('' if out == want else f'  GOT {out[:80]!r}'))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'audit01 fixes: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
