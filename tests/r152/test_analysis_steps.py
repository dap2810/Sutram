#!/usr/bin/env python3
"""R152: --analysis-steps=N, the expression check's budget for one compile - to ChatGPT R217's contract, case by case.

  syntax        one argv token, exactly "--analysis-steps=" and one or more ASCII decimal digits
  range         1 .. 2147483647; leading zeros are decimal ("=00064" is 64, and the messages say 64)
  accepted      =1, =00064, =200000, =2147483647
  rejected      empty, 0, -1, +1, 200k, 1e5, 0x100, 1_000, a fraction, leading/embedded/trailing whitespace,
                non-ASCII digits, trailing junk, 2147483648, a 20-digit value (checked before it can wrap),
                "--analysis-steps 200000" (the value in the next argument), a second occurrence (even the same
                value), "--analysis-stepsX"
  rejected how  exit 1, no output file, "[E_PARIKSHA_PADANI]"
  scope         the whole compile: every walk starts from N - statements, module initializers; any position
                among the arguments; with --check, --lang and --ffi ... --object too
  default       200000, and the usage text says so

Accepted values are tested by compiling one program; =1 is accepted and then the compile is refused by the
budget itself (one step cannot finish any check), which is what N = 1 means.
Last line: "r152 analysis steps: N checks, M failed".
"""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROG = 'vitti g = 2 + 3\nmukhya() {\n    likha(g + 1 + 2)\n}\n'
REJECT = ['--analysis-steps=', '--analysis-steps=0', '--analysis-steps=000', '--analysis-steps=-1',
          '--analysis-steps=+1', '--analysis-steps=200k', '--analysis-steps=1e5', '--analysis-steps=0x100',
          '--analysis-steps=1_000', '--analysis-steps=1.5', '--analysis-steps=1/2', '--analysis-steps= 5',
          '--analysis-steps=5 5', '--analysis-steps=5 ', '--analysis-steps=\t5', '--analysis-steps=٥',
          '--analysis-steps=१०', '--analysis-steps=５', '--analysis-steps=5x',
          '--analysis-steps=2147483648', '--analysis-steps=4294967297', '--analysis-steps=99999999999999999999',
          '--analysis-steps', '--analysis-stepsX', '--analysis-steps:5']


def main():
    comp = os.path.join(ROOT, 'sutram_compiler')
    if '--compiler' in sys.argv:
        comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    work = tempfile.mkdtemp(prefix='r152-')
    sm = os.path.join(work, 'p.sm')
    open(sm, 'w').write(PROG)
    out = os.path.join(work, 'p')

    def comp_(args):
        if os.path.exists(out):
            os.remove(out)
        r = subprocess.run([comp] + args, cwd=ROOT, capture_output=True, text=True, errors='replace', timeout=60)
        return r, r.stdout + r.stderr, os.path.exists(out)

    def runs():
        return subprocess.run([out], capture_output=True, text=True, timeout=10).stdout if os.path.exists(out) else None

    for v in ('=00064', '=200000', '=2147483647'):
        r, said, made = comp_(['--analysis-steps' + v, sm, out])
        check(r.returncode == 0 and made and runs() == '8\n', f'accepted: --analysis-steps{v} - compiles, prints {runs()!r}')
    r, said, made = comp_(['--analysis-steps=1', sm, out])
    check(r.returncode == 1 and not made and 'parikshanam 1 padeshu' in said and '[E_PARIKSHA_PADANI]' not in said,
          'accepted: --analysis-steps=1 - the flag is taken, and the compile is refused by a budget of 1 (E_VAKYA_SEEMA, "1")')
    r2 = subprocess.run([comp, '--analysis-steps=000001', sm, out], cwd=ROOT, capture_output=True, text=True)
    check('parikshanam 1 padeshu' in r2.stdout + r2.stderr, 'leading zeros are decimal and displayed normalised ("=000001" is named 1)')
    for a in REJECT:
        r, said, made = comp_([a, sm, out])
        check(r.returncode == 1 and not made and '[E_PARIKSHA_PADANI]' in said, f'rejected: {a!r} - exit {r.returncode}, '
              f'{"output written" if made else "no output"}, {"E_PARIKSHA_PADANI" if "[E_PARIKSHA_PADANI]" in said else said.strip()[:50]!r}')
    r, said, made = comp_(['--analysis-steps', '200000', sm, out])
    check(r.returncode == 1 and not made and '[E_PARIKSHA_PADANI]' in said, 'rejected: "--analysis-steps 200000" (the value is not in the token)')
    for pair in (['--analysis-steps=5000', '--analysis-steps=5000'], ['--analysis-steps=5000', '--analysis-steps=6000']):
        r, said, made = comp_(pair + [sm, out])
        check(r.returncode == 1 and not made and '[E_PARIKSHA_PADANI]' in said, f'rejected: a second occurrence {pair}')
    r, said, made = comp_([sm, out, '--analysis-steps=5000'])
    check(r.returncode == 0 and runs() == '8\n', 'any position: after the files')
    r, said, made = comp_([sm, out, '--analysis-steps=3'])
    check(r.returncode == 1 and not made and 'parikshanam 3 padeshu' in said, 'any position: after the files, and in force (3 steps refuse)')
    big = os.path.join(work, 'g.sm')
    open(big, 'w').write('vitti z = 2\nvitti g = ' + ' + '.join(['z'] * 40) + '\nmukhya() {\n    likha(g)\n}\n')
    r, said, made = comp_(['--analysis-steps=20', big, out])
    check(r.returncode == 1 and 'parikshanam 20 padeshu' in said and 'vaishvika' in said,
          'scope: a module-level initializer is checked with N too (refused at 20, named "mukhya athava vaishvika-arambhah")')
    r = subprocess.run([comp, '--check', '--analysis-steps=3', sm], cwd=ROOT, capture_output=True, text=True)
    check(r.returncode == 1 and 'parikshanam 3 padeshu' in r.stdout + r.stderr, 'with --check')
    r = subprocess.run([comp, '--analysis-steps=3', '--lang', 'sanskrit', sm, out], cwd=ROOT, capture_output=True, text=True)
    check(r.returncode == 1 and '[E_VAKYA_SEEMA]' in r.stdout + r.stderr, 'with --lang')
    ffi = subprocess.run([comp, '--analysis-steps=3', '--ffi', os.path.join(ROOT, 'tests', 'r33', 'kinds.sffi'), '--object',
                          sm, out + '.smo'], cwd=ROOT, capture_output=True, text=True)
    check(ffi.returncode == 1 and '[E_VAKYA_SEEMA]' in ffi.stdout + ffi.stderr, 'with --ffi ... --object')
    u = subprocess.run([comp], capture_output=True, text=True)
    check('--analysis-steps=N' in u.stdout + u.stderr and '(mula 200000)' in u.stdout + u.stderr,
          'the usage text names the flag and its effective default, 200000')
    print(f'r152 analysis steps: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
