#!/usr/bin/env python3
"""R72 (Step 3, first half), revised in R73: the mandapa block.

    python3 -B tests/r72_mandapa/test_mandapa.py --compiler ./sutram_compiler

  * every X_with.sm / X_without.sm pair prints the same output and exits the same way. In R72 (v268) the two
    compiled to the same bytes - the block was inert. From R73 (v269) a block's nirmmita takes the scratch
    side and the block rewinds it, so the bytes differ by design; the OUTPUT may not;
  * escape_*.sm are refused with E_SCRATCH_ESCAPE: nivartanam inside a mandapa may not return a block
    allocated inside it;
  * allowed_*.sm compile and run: returning a block allocated OUTSIDE the mandapa, or a value read from
    scratch, is fine.
Last line: `r72 mandapa: N checks, M failed`.
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    comp = sys.argv[sys.argv.index('--compiler') + 1] if '--compiler' in sys.argv else os.path.join(ROOT, 'sutram_compiler')
    comp = os.path.abspath(comp)
    work = tempfile.mkdtemp()
    checks = failed = 0

    def build(name):
        out = os.path.join(work, name + '.bin')
        c = subprocess.run([comp, os.path.join(HERE, name + '.sm'), out], cwd=ROOT, capture_output=True, text=True)
        return c, out

    names = sorted(f[:-3] for f in os.listdir(HERE) if f.endswith('.sm'))
    for n in names:
        if n.endswith('_with'):
            base = n[:-5]
            a, ab = build(n)
            b, bb = build(base + '_without')
            checks += 1
            ok = a.returncode == 0 and b.returncode == 0
            if ok:
                ra = subprocess.run([ab], capture_output=True, text=True, timeout=20)
                rb = subprocess.run([bb], capture_output=True, text=True, timeout=20)
                ok = (ra.returncode, ra.stdout) == (rb.returncode, rb.stdout)
                detail = ra.stdout.strip()
            else:
                detail = (a.stdout + a.stderr + b.stdout + b.stderr).strip()[-160:]
            print(('PASS' if ok else 'FAIL') + f'  {base}: with and without the block, same output ({detail})')
            failed += not ok
        elif n.startswith('escape_'):
            c, _ = build(n)
            checks += 1
            ok = c.returncode != 0 and 'E_SCRATCH_ESCAPE' in c.stdout + c.stderr
            print(('PASS' if ok else 'FAIL') + f'  {n}: refused with E_SCRATCH_ESCAPE')
            failed += not ok
        elif n.startswith('allowed_'):
            c, out = build(n)
            checks += 1
            ok = c.returncode == 0
            if ok:
                r = subprocess.run([out], capture_output=True, text=True, timeout=20)
                ok = r.returncode == 0
            print(('PASS' if ok else 'FAIL') + f'  {n}: compiles and runs')
            failed += not ok
    print(f'r72 mandapa: {checks} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
