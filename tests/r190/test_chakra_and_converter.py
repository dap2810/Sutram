#!/usr/bin/env python3
"""R190: which way a chakra counts, the warning for the countdown shape, and vartani_tak_ank.

The rule (decided when the loop is compiled, unchanged by this round, pinned here):
  - both ends written as numbers and the start larger: it counts down - 5 tak 3 is 5 4 3, and so
    1 tak 0 is 1 0 and 0 tak -1 is 0 -1;
  - any variable or call at either end: it counts up, and runs no times when the start is past the end.
New in v326:
  - `chakra i = n tak 1` (a start that is not a number, an end that is) compiles to the same program and
    prints one `Sutram suchana: chakra 'i' ...` line on stderr; no other shape is warned about; not in a
    --lang run;
  - vartani_tak_ank(s, ok) (yoj vakyank) converts a string to its number and says whether it was one.

Usage: python3 tests/r190/test_chakra_and_converter.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0
WARN = b"Sutram suchana: chakra 'i' urdhvam eva ganayati"


def loop(decl, a, b, word='tak', tail=''):
    return ('mukhya() {\n%s    chakra i = %s %s %s%s {\n        likha(i)\n    }\n    likha("end")\n}\n'
            % (''.join('    %s\n' % d for d in decl), a, word, b, tail))

# (name, what, source, stdout, warned?)
LOOPS = [
    ('written-down', '5 tak 3 counts 5 4 3', loop([], '5', '3'), b'5\n4\n3\nend', False),
    ('written-1-0', '1 tak 0 runs twice: 1 0', loop([], '1', '0'), b'1\n0\nend', False),
    ('written-0-minus-1', '0 tak -1 runs 0 -1', loop([], '0', '-1'), b'0\n-1\nend', False),
    ('written-up', '3 tak 5 counts 3 4 5', loop([], '3', '5'), b'3\n4\n5\nend', False),
    ('both-variables-past', 'a = 5, b = 3: a tak b runs no times', loop(['vitti a = 5', 'vitti b = 3'], 'a', 'b'), b'end', False),
    ('both-variables-1-0', 'a = 1, b = 0: a tak b runs no times', loop(['vitti a = 1', 'vitti b = 0'], 'a', 'b'), b'end', False),
    ('both-variables-up', 'a = 3, b = 5: a tak b counts 3 4 5', loop(['vitti a = 3', 'vitti b = 5'], 'a', 'b'), b'3\n4\n5\nend', False),
    ('number-to-variable', '5 tak e (e = 3) runs no times - and cannot be warned about', loop(['vitti e = 3'], '5', 'e'), b'end', False),
    ('empty-range', '0 tak n - 1 (n = 0) runs no times', loop(['vitti n = 0'], '0', 'n - 1'), b'end', False),
    ('variable-to-number', 'n tak 1 (n = 3) runs no times - AND IS WARNED ABOUT', loop(['vitti n = 3'], 'n', '1'), b'end', True),
    ('expression-to-number', 'n - 1 tak 0 (n = 3) is warned about', loop(['vitti n = 3'], 'n - 1', '0'), b'end', True),
    ('variable-to-number-up', 'n tak 5 (n = 3) counts 3 4 5, and is warned about too (the shape, not the values)',
     loop(['vitti n = 3'], 'n', '5'), b'3\n4\n5\nend', True),
    ('arabhya-variable', '5 arabhya e paryantam (e = 3) runs no times: the same loop',
     loop(['vitti e = 3'], '5', 'e', 'arabhya', ' paryantam'), b'end', False),
    ('arabhya-written', '5 arabhya 3 paryantam counts 5 4 3', loop([], '5', '3', 'arabhya', ' paryantam'), b'5\n4\n3\nend', False),
    ('yavat-down', 'yavat counts down from a variable', 'mukhya() {\n    vitti e = 3\n    vitti i = 5\n    yavat (i >= e) {\n'
     '        likha(i)\n        i = i - 1\n    }\n    likha("end")\n}\n', b'5\n4\n3\nend', False),
]
CONV = '''yoj vakyank

mukhya() {
    mala ok[1]
    yavat (1) {
        vitti s = vartani_grahan()
        yadi (nivesha_anta()) { krama }
        vitti n = vartani_tak_ank(s, ok)
        likha(ok[0], " ", n)
    }
}
'''
CONV_IN = (b'42\n-17\n0\n9223372036854775807\n-9223372036854775808\n9223372036854775808\nabc\n5abc\n12 34\n 42\n+5\n-\n\n'
           b'0000000000000000000000000000042\n' + b'0' * 31 + b'7\n' + b'9' * 5000 + b'\n')
CONV_OUT = (b'1 42\n1 -17\n1 0\n1 9223372036854775807\n1 -9223372036854775808\n0 0\n0 0\n0 0\n0 0\n0 0\n0 0\n0 0\n0 0\n'
            b'1 42\n0 0\n0 0\n')
OLD = 'yoj vakyank\n\nmukhya() {\n    mala ok[1]\n    vitti n = varna_tak_ank("42", 2, ok)\n    likha(ok[0], " ", n)\n}\n'


def check(ok, name, what, detail=''):
    global checks, fails
    checks += 1
    print(('ok    ' if ok else 'FAIL  ') + '%-24s %s %s' % (name, what, '' if ok else detail))
    if not ok:
        fails += 1


def build(comp, work, name, src, extra=()):
    sm = os.path.join(work, name + '.sm')
    exe = os.path.join(work, name + '.bin')
    open(sm, 'w', encoding='utf-8').write(src)
    c = subprocess.run([comp] + list(extra) + [sm, exe], capture_output=True, cwd=ROOT)
    return (exe if os.path.exists(exe) else None), c


def main():
    comp = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    work = tempfile.mkdtemp(prefix='r190_')
    try:
        for name, what, src, out, warned in LOOPS:
            exe, c = build(comp, work, name, src)
            if not exe:
                check(False, name, what, '- did not compile: ' + c.stdout.decode('utf-8', 'replace')[-160:])
                continue
            r = subprocess.run([exe], capture_output=True, timeout=30)
            said = WARN in c.stderr
            check(r.returncode == 0 and r.stdout == out and said == warned and c.stderr.count(b'suchana') == (1 if warned else 0),
                  name, what, '- got %r, warned %s, stderr %r' % (r.stdout[:60], said, c.stderr[:80]))
        # the warning changes nothing in the program: the same source with the end in a variable is the same loop
        a, _ = build(comp, work, 'same-a', loop(['vitti n = 3', 'vitti one = 1'], 'n', '1'))
        b, _ = build(comp, work, 'same-b', loop(['vitti n = 3', 'vitti one = 1'], 'n', 'one'))
        ra = subprocess.run([a], capture_output=True, timeout=30).stdout
        rb = subprocess.run([b], capture_output=True, timeout=30).stdout
        check(ra == rb == b'end', 'warned-is-unchanged', 'the warned loop runs exactly as the unwarned one does', '- %r %r' % (ra, rb))
        exe, c = build(comp, work, 'conv', CONV)
        if not exe:
            check(False, 'converter', 'vartani_tak_ank compiles', c.stdout.decode('utf-8', 'replace')[-160:])
        else:
            r = subprocess.run([exe], input=CONV_IN, capture_output=True, timeout=30)
            check(r.returncode == 0 and r.stdout == CONV_OUT, 'converter', 'vartani_tak_ank: 6 numbers accepted (one of 31 characters), 10 non-numbers reported (32 and 5,000 characters too)',
                  '- got %r' % r.stdout[:200])
        exe, c = build(comp, work, 'old', OLD)
        r = subprocess.run([exe], capture_output=True, timeout=30) if exe else None
        check(bool(exe) and r.stdout == b'0 0\n', 'older-sibling', 'varna_tak_ank("42", 2, ok) is 0 with ok 0: it does not take a string',
              '- %r' % (r.stdout if r else c.stdout[-100:]))
        # R191: the program the reference teaches must itself report a word, not print 0 for it
        ref = open(os.path.join(ROOT, 'docs', 'LANGUAGE-REFERENCE.md'), encoding='utf-8').read()
        i = ref.index('- **From text to a number: `vartani_tak_ank(s, ok)`**')
        i = ref.index('```\n', i) + 4
        taught = '\n'.join(l[2:] if l.startswith('  ') else l for l in ref[i:ref.index('```', i)].split('\n'))
        exe, c = build(comp, work, 'taught', taught)
        got = ([subprocess.run([exe], input=x, capture_output=True, timeout=30).stdout for x in (b'42\n', b'hello\n')]
               if exe else ['did not compile: ' + c.stdout.decode('utf-8', 'replace')[-120:]])
        check(got == [b'84\n', b'sankhya na: hello'], 'taught-program',
              "the reference's own program prints 84 for 42 and reports hello", '- %r' % got)
        ex = os.path.join(ROOT, 'examples', '364_r190_vartani_tak_ank.sm')
        exe = os.path.join(work, 'ex.bin')
        subprocess.run([comp, ex, exe], capture_output=True, cwd=ROOT)
        got = ([subprocess.run([exe], input=i, capture_output=True, timeout=30).stdout for i in (b'21\n', b'abc\n')]
               if os.path.exists(exe) else ['did not compile'])
        check(got == [b'sankhya? dvigunam: 42\n', b"sankhya? 'abc' sankhya na\n"], 'example-364',
              'the example doubles 21 and reports abc', '- %r' % got)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print('r190 chakra and converter: %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
