#!/usr/bin/env python3
"""R133: a kosh slice given to a function value beside an argument with a call in it is refused (ChatGPT R205-206 S3).

v304 refused a kosh-made slice beside an argument that could grow the kosh first - for a direct call. Through a
function value (vitti f = badal; f(k[0:1], kosh_kship(k, 8))) the check never ran: v306 compiled it, captured the
slice, grew k, and the callee wrote into the abandoned buffer (prints 0 and 7) or read a released 64 MiB region
(SIGSEGV). The programs are tests/r133/indirect/*.sm; each is compiled, and run when it compiles:

  refused (E_KOSH_VIBHAG): s3small, s3big, st1 (statement form), ind_fv_arg (growth inside another call),
                           alias_sl (slice of an alias), and the direct controls s3small_direct, s3big_direct, ind_wrap;
  ind_k (a whole kosh to a function value, beside a slice of it): E_KOSH_DVARA up to v307; from v308 the slice,
                           the first argument, is refused first (E_KOSH_VIBHAG);
  safe1 (a slice to a function value with nothing beside it): compiled and wrote through up to v307; from v308
  (R134, one predicate) refused - a function value's parameters are untyped, and an untyped parameter can keep a
  slice past its kosh's growth (tests/r134/escape/e2_keep.sm).

  python3 tests/r133/test_indirect_slice.py [--compiler PATH]     (v306 fails 6 of the 10; v307 fails 1, safe1)
Last line: "r133 indirect slice: N checks, M failed".
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(ROOT, 'tests', 'r133', 'indirect')
WANT = {
    's3small': 'E_KOSH_VIBHAG', 's3big': 'E_KOSH_VIBHAG', 'st1': 'E_KOSH_VIBHAG', 'ind_fv_arg': 'E_KOSH_VIBHAG',
    'alias_sl': 'E_KOSH_VIBHAG', 's3small_direct': 'E_KOSH_VIBHAG', 's3big_direct': 'E_KOSH_VIBHAG',
    'ind_wrap': 'E_KOSH_VIBHAG', 'ind_k': 'E_KOSH_VIBHAG', 'safe1': 'E_KOSH_VIBHAG',
}


def main():
    comp = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    checks = fails = 0
    work = tempfile.mkdtemp(prefix='r133-')
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
            ok = got == want
            what = f'compiles and prints {got!r}'
        else:
            ok = want.startswith('E_') and f'[{want}]' in said
            what = 'refused: ' + (said.strip().split('\n')[0][:110] if said.strip() else '(no message)')
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + f'{name}: want {want!r}; {what}')
    print(f'r133 indirect slice: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
