#!/usr/bin/env python3
"""R134 (ChatGPT R207): one predicate decides every door a kosh - and a slice of one - may not pass.

Up to v307 each door (a cell or field store, a module vitti, an untyped or function-value parameter, a raw store,
a builtin's other argument, a phal result) asked r126_is_kosh_value, which knows the kosh kinds (2, 3, 6) and not a
slice (kind 1). So a slice of a kosh went into a cell, a global, another kosh or an untyped parameter, outlived the
elements it pointed at, and a write through it was lost (the five programs below printed 7 on v307). v308 routes
every door through r134_holds_kosh: a kosh, or a slice that may borrow one's elements (a slice of a kosh or of a
slice name / vibhag parameter, or such a name itself).

  1. source: `call r126_is_kosh_value` appears exactly once - inside r134_holds_kosh - so a new door that asks
     the old question fails this gate; each door check calls r134_holds_kosh;
  2. tests/r134/escape/e*.sm are refused (E_KOSH_VIBHAG); c*.sm compile and print 7, 99 and 5.

  python3 tests/r134/test_one_predicate.py [--compiler PATH]     (v307 fails 5 of the 8 programs)
Last line: "r134 one predicate: N checks, M failed".
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(ROOT, 'tests', 'r134', 'escape')
WANT = {'e1_cell': 'E_KOSH_VIBHAG', 'e2_keep': 'E_KOSH_VIBHAG', 'e3_global': 'E_KOSH_VIBHAG', 'e4_fwd': 'E_KOSH_VIBHAG',
        'e5_pushslice': 'E_KOSH_VIBHAG', 'c1_direct_read': '7\n', 'c2_direct_write': '99\n', 'c3_mala_cell': '5\n'}
DOORS = ['r126_check_assign', 'r126_check_builtin', 'r126_check_writemem', 'r126_check_untyped_arg', 'r126_check_return']


def body(src, label):
    i = src.find('\n' + label + ':')
    if i < 0:
        return ''
    m = re.search(r'\n[a-z_][a-z0-9_]*:', src[i + 1:])
    return src[i:i + 1 + (m.start() if m else len(src))]


def main():
    comp = os.path.join(ROOT, 'sutram_compiler')
    own = '--compiler' not in sys.argv
    if not own:
        comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    if own:
        src = open(os.path.join(ROOT, 'src', 'sutram_compiler.asm'), encoding='utf-8').read()
        code = re.sub(r';[^\n]*', '', src)
        n = code.count('call r126_is_kosh_value')
        check(n == 1 and 'call r126_is_kosh_value' in body(code, 'r134_holds_kosh'),
              f'only r134_holds_kosh asks r126_is_kosh_value ({n} call sites)')
        for d in DOORS:
            check('call r134_holds_kosh' in body(code, d), f'{d} asks r134_holds_kosh')
    work = tempfile.mkdtemp(prefix='r134-')
    for name, want in WANT.items():
        out = os.path.join(work, name)
        c = subprocess.run([comp, os.path.join(DIR, name + '.sm'), out], cwd=ROOT, capture_output=True, text=True)
        said = c.stdout + c.stderr
        if os.path.exists(out):
            try:
                r = subprocess.run([out], capture_output=True, text=True, timeout=30)
                got = r.stdout if r.returncode == 0 else f'{r.stdout!r} exit {r.returncode}'
            except subprocess.TimeoutExpired:
                got = 'TIMEOUT'
            ok, what = got == want, f'compiles and prints {got!r}'
        else:
            ok = want.startswith('E_') and f'[{want}]' in said
            what = 'refused: ' + (said.strip().split('\n')[0][:110] if said.strip() else '(no message)')
        check(ok, f'{name}: want {want!r}; {what}')
    print(f'r134 one predicate: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
