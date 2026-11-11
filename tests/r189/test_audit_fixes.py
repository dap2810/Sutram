#!/usr/bin/env python3
"""R189: the audit's fixes (ChatGPT R233) on the v325 tree, and the behaviours v325's reference now states.

Fixed in the library (each fails on v324):
  - brihat_ank_tak_laghu refuses a digit of -1 (it returned -1);
  - laghuttam_samapavartya (lcm) of a pair with 0 is 0, and of (MIN, MIN) is -1 (both stopped the program).
Pinned because the reference now states them (a later change must show up here, not in a student's program):
  - brihat_ank_se leaves x untouched for a bad base and clears it for a bad digit;
  - a chakra counts down only when both ends are written as numbers; with a variable end it runs no times;
  - purna_prasaran of [0, 0, 6000000000] is -1; ekanka_gan of a negative number is 0;
  - ganita_paripurna_bhaj / _shesh by zero and ganita_paripurna_kramgun(-1) are 0;
  - akshar gives bytes; anka_akshar keeps the low eight bits; akshar_guru is ASCII only;
  - an empty string held in a module-level vitti is true in yadi (a value not known to be a string);
  - a prakriya body without braces holds several statements (the reference's example prints 12);
  - the reference's madhya example returns the middle of three for all six orders.

Usage: python3 tests/r189/test_audit_fixes.py [--compiler PATH]
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
checks = fails = 0
M = '(0 - 9223372036854775807) - 1'

CASES = [
    ('brihat-negative-digit', 'brihat_ank_tak_laghu refuses a digit of -1',
     'yoj brihat\n\nmukhya() {\n    vitti a = nirmmita(16)\n    likh8(a, 0 - 1)\n    likha(brihat_ank_tak_laghu(a, 1))\n}\n',
     1, b'', 'E_MULYA_AYOGYA'),
    ('lcm-zero-and-min', 'lcm: (4,6) 12, (0,7) 0, (MIN,2) -1, (0,MIN) 0, (MIN,0) 0, (MIN,MIN) -1 - and no stop',
     'yoj ganit\n\nmukhya() {\n    vitti m = %s\n    likha(laghuttam_samapavartya(4, 6))\n    likha(laghuttam_samapavartya(0, 7))\n'
     '    likha(laghuttam_samapavartya(m, 2))\n    likha(laghuttam_samapavartya(0, m))\n    likha(laghuttam_samapavartya(m, 0))\n'
     '    likha(laghuttam_samapavartya(m, m))\n}\n' % M, 0, b'12\n0\n-1\n0\n0\n-1\n', None),
    ('ank-se-failures', 'brihat_ank_se: a bad base leaves x, a bad digit clears it',
     'yoj aadhar\n\nmukhya() {\n    mala d[2]\n    d[0] = 1\n    d[1] = 12\n    mala x[3]\n    x[0] = 7\n    x[1] = 7\n    x[2] = 7\n'
     '    vitti r = brihat_ank_se(d, 2, 1, x, 3)\n    likha(r, x[0], x[1], x[2])\n'
     '    r = brihat_ank_se(d, 2, 10, x, 3)\n    likha(r, x[0], x[1], x[2])\n}\n', 0, b'0777\n0000\n', None),
    ('chakra-written-ends-down', 'chakra j = 5 tak 1 counts down',
     'mukhya() {\n    chakra j = 5 tak 1 {\n        likha(j)\n    }\n}\n', 0, b'5\n4\n3\n2\n1\n', None),
    ('chakra-variable-end', 'chakra i = 5 tak e (e = 3) runs no times',
     'mukhya() {\n    vitti n = 0\n    vitti e = 3\n    chakra i = 5 tak e {\n        n = n + 1\n    }\n    likha(n)\n}\n',
     0, b'0\n', None),
    ('chakra-to-max', 'a chakra up to the largest vitti does not stop by itself (stopped here at 11 passes)',
     'mukhya() {\n    vitti n = 0\n    chakra i = 9223372036854775805 tak 9223372036854775807 {\n        n = n + 1\n'
     '        yadi (n > 10) { krama }\n    }\n    likha(n)\n}\n', 0, b'11\n', None),
    ('prasaran-deviation', 'purna_prasaran([0,0,6000000000]) is -1',
     'yoj sankhyiki\n\nmukhya() {\n    mala a[3]\n    a[0] = 0\n    a[1] = 0\n    a[2] = 6000000000\n    likha(purna_prasaran(a, 3))\n}\n',
     0, b'-1\n', None),
    ('ekanka-negative', 'ekanka_gan: 7 -> 3, -1 -> 0',
     'yoj ganit\n\nmukhya() {\n    likha(ekanka_gan(7))\n    likha(ekanka_gan(0 - 1))\n}\n', 0, b'3\n0\n', None),
    ('paripurna-zero', 'ganita_paripurna: MAX*2 saturates; /0, %0 and kramgun(-1) are 0',
     'yoj ganita\n\nmukhya() {\n    likha(ganita_paripurna_gun(9223372036854775807, 2))\n    likha(ganita_paripurna_bhaj(7, 0))\n'
     '    likha(ganita_paripurna_shesh(7, 0))\n    likha(ganita_paripurna_kramgun(0 - 1))\n}\n',
     0, b'9223372036854775807\n0\n0\n0\n', None),
    ('bytes', 'akshar gives bytes; anka_akshar(300) is ","; akshar_guru leaves 224',
     'mukhya() {\n    vitti a = "आ"\n    likha(akshar(a, 0), " ", akshar(a, 1), " ", akshar(a, 2))\n    shabda(anka_akshar(300))\n'
     '    likha(" ", vartani_aayam(anka_akshar(0)))\n    likha(akshar_guru(97), " ", akshar_guru(224))\n}\n',
     0, b'224 164 134\n, 0\n65 224\n', None),
    ('module-empty-string-true', 'an empty string in a module vitti is true in yadi',
     'vitti g = ""\n\nmukhya() {\n    yadi (g) { likha("true") }\n    anya { likha("false") }\n}\n', 0, b'true', None),
    ('braceless-prakriya', 'a prakriya without braces holds three statements (the reference example: 12)',
     'prakriya f(n)\n    vitti x = n + 1    # three statements, no braces\n    x = x * 2\n    nivartanam x\n\nmukhya()\n'
     '    likha(f(5))        # prints 12\n', 0, b'12\n', None),
]


def check(ok, name, what, detail=''):
    global checks, fails
    checks += 1
    print(('ok    ' if ok else 'FAIL  ') + '%-26s %s %s' % (name, what, '' if ok else detail))
    if not ok:
        fails += 1


def madhya_source():
    ref = open(os.path.join(ROOT, 'docs', 'LANGUAGE-REFERENCE.md'), encoding='utf-8').read()
    a = ref.index('prakriya madhya(a, b, c)')
    body = ref[a:ref.index('```', a)]
    calls = ', '.join('madhya(%s)' % ', '.join(p) for p in
                      (('1', '2', '3'), ('1', '3', '2'), ('2', '1', '3'), ('2', '3', '1'), ('3', '1', '2'), ('3', '2', '1')))
    return body + '\nmukhya() {\n    likha(%s)\n}\n' % calls


def main():
    comp = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    work = tempfile.mkdtemp(prefix='r189_')
    try:
        cases = CASES + [('reference-madhya', "the reference's madhya: the middle of three in all six orders",
                          madhya_source(), 0, b'222222\n', None)]
        for name, what, src, rc, out, code in cases:
            sm = os.path.join(work, name + '.sm')
            exe = os.path.join(work, name + '.bin')
            open(sm, 'w', encoding='utf-8').write(src)
            c = subprocess.run([comp, sm, exe], capture_output=True, cwd=ROOT)
            if not os.path.exists(exe):
                check(False, name, what, '- did not compile: ' + c.stdout.decode('utf-8', 'replace')[-200:])
                continue
            r = subprocess.run([exe], capture_output=True, timeout=60)
            if code:
                text = (r.stdout + r.stderr).decode('utf-8', 'replace')
                check(r.returncode == rc and code in text, name, what, '- exit %d, %r' % (r.returncode, text[:120]))
            else:
                check(r.returncode == rc and r.stdout == out, name, what, '- exit %d, got %r' % (r.returncode, r.stdout[:120]))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print('r189 audit fixes: %d checks, %d failed' % (checks, fails))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
