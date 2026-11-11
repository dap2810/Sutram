#!/usr/bin/env python3
"""R186: grahan() reads the sign and no longer loses an unfinished last line; a file is read by its
path (yoj patra, patra_path_sarv) and line by line as the program's input.

grahan() - each case: bytes fed, exact bytes printed (golden).
  - '-5' gives -5 and '+5' gives 5 (v323 gave 5 and 5): a '-' or '+' before the first digit is the sign;
  - '42' with no newline, then the end: 42 (v323 gave -1 - the number was lost);
  - end of input with nothing read: -1, and nivesha_anta() is 1 - so a typed -1 is told from the end;
  - kept as before and stated: '5abc' gives 5, '12 34' gives 1234, an empty line gives 0, 'abc' gives 0,
    and a number past the largest vitti wraps (reported in R186-00, not changed).
Files:
  - examples 362 (sums the numbers of examples/data/r186_sankhya.txt: 42) and 363 (counts its lines: 3);
  - vartani_grahan() returns an unfinished last line whole (the sibling of the grahan bug: it never had it).

Usage: python3 tests/r186/test_grahan_and_files.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0

ONE = 'mukhya() {\n    vitti a = grahan()\n    likha(a)\n}\n'
TWO = 'mukhya() {\n    vitti a = grahan()\n    vitti b = grahan()\n    likha(a, " ", b)\n}\n'
ENDS = '''mukhya() {
    vitti n = 0
    vitti s = 0
    yavat (1) {
        vitti a = grahan()
        yadi (nivesha_anta()) { krama }
        n = n + 1
        s = s + a
    }
    likha(n, " ", s)
}
'''
LINES = '''mukhya() {
    yavat (1) {
        vitti s = vartani_grahan()
        yadi (nivesha_anta()) { krama }
        likha("[", s, "]\\n")
    }
}
'''
RUNS = [
    ('minus', 'a minus sign is read', ONE, b'-5\n', b'-5\n'),
    ('plus', 'a plus sign is read', ONE, b'+5\n', b'5\n'),
    ('sign-after-letter', 'a sign before the first digit counts, letters before it do not', ONE, b'a-5\n', b'-5\n'),
    ('last-sign-wins', 'of two signs before the digits, the last one wins', ONE, b'+-5\n', b'-5\n'),
    ('sign-after-digit', 'after the first digit a sign is passed over (as before)', ONE, b'12-34\n', b'1234\n'),
    ('smallest', 'the smallest vitti reads exactly', ONE, b'-9223372036854775808\n', b'-9223372036854775808\n'),
    ('largest', 'the largest vitti reads exactly', ONE, b'9223372036854775807\n', b'9223372036854775807\n'),
    ('unfinished-last', 'a last number with no newline is returned, not lost', ONE, b'42', b'42\n'),
    ('unfinished-negative', 'and with its sign', ONE, b'-42', b'-42\n'),
    ('then-the-end', 'after an unfinished last number the next read is the end', TWO, b'42', b'42 -1\n'),
    ('two-lines', 'two numbers, the second unfinished', TWO, b'-7\n42', b'-7 42\n'),
    ('nothing', 'no input at all: -1', ONE, b'', b'-1\n'),
    ('typed-minus-one', 'a typed -1 is a number; nivesha_anta() ends the loop only at the end', ENDS, b'-1\n5\n-4',
     b'3 0\n'),
    ('loop-no-input', 'the same loop on no input runs zero times', ENDS, b'', b'0 0\n'),
    ('empty-lines', 'empty lines are 0, not the end', ENDS, b'\n\n', b'2 0\n'),
    ('kept-trailing-letters', 'kept: 5abc is 5', ONE, b'5abc\n', b'5\n'),
    ('kept-space', 'kept: 12 34 is 1234', ONE, b'12 34\n', b'1234\n'),
    ('kept-empty', 'kept: an empty line is 0', ONE, b'\n', b'0\n'),
    ('kept-letters', 'kept: abc is 0', ONE, b'abc\n', b'0\n'),
    ('kept-wrap', 'kept (reported, not changed): past the largest vitti it wraps', ONE, b'9223372036854775808\n',
     b'-9223372036854775808\n'),
    ('vartani-unfinished', 'vartani_grahan returns an unfinished last line whole', LINES, b'one\nlast', b'[one]\n[last]\n'),
]


def check(ok, name, what, detail=''):
    global checks, fails
    checks += 1
    if ok:
        print('ok    %-22s %s' % (name, what))
    else:
        fails += 1
        print('FAIL  %-22s %s %s' % (name, what, detail))


def build(comp, src, work, name):
    sm = os.path.join(work, name + '.sm')
    out = os.path.join(work, name + '.bin')
    if src.endswith('.sm') and os.path.exists(os.path.join(ROOT, src)):
        sm = os.path.join(ROOT, src)
    else:
        open(sm, 'w', encoding='utf-8').write(src)
    c = subprocess.run([comp, sm, out], capture_output=True, cwd=ROOT)
    return out if os.path.exists(out) else None, c.stdout.decode('utf-8', 'replace')


def main():
    comp = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    work = tempfile.mkdtemp(prefix='r186_')
    try:
        for name, what, src, feed, want in RUNS:
            exe, msg = build(comp, src, work, name)
            if not exe:
                check(False, name, what, '- did not compile: ' + msg[-200:])
                continue
            try:
                r = subprocess.run([exe], input=feed, capture_output=True, timeout=60)
            except subprocess.TimeoutExpired:
                check(False, name, what, '- did not end in 60 s')
                continue
            check(r.returncode == 0 and r.stdout == want, name, what, '- exit %d, got %r' % (r.returncode, r.stdout[:80]))
        fixture = open(os.path.join(ROOT, 'examples', 'data', 'r186_sankhya.txt'), 'rb').read()
        for name, what, src, feed, want in [
                ('file-sum', 'example 362 sums the fixture by its path: 42',
                 'examples/362_r186_patra_sankhya_yoga.sm', b'', b'yogah: 42\n'),
                ('file-lines', 'example 363 counts the fixture given as input: 3',
                 'examples/363_r186_pankti_ganana_patra.sm', fixture, b'panktayah: 3\n')]:
            exe, msg = build(comp, src, work, name)
            if not exe:
                check(False, name, what, '- did not compile: ' + msg[-200:])
                continue
            r = subprocess.run([exe], input=feed, capture_output=True, timeout=60, cwd=ROOT)
            check(r.returncode == 0 and r.stdout == want, name, what, '- exit %d, got %r' % (r.returncode, r.stdout[:80]))
        exe, msg = build(comp, 'examples/362_r186_patra_sankhya_yoga.sm', work, 'file-missing')
        r = subprocess.run([exe], capture_output=True, timeout=60, cwd=work)  # the relative path is not there
        check(r.stdout == b'patra na labdham\n', 'file-missing', 'a file that is not there: the program says so',
              '- got %r' % r.stdout[:80])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print('r186 grahan and files: %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
