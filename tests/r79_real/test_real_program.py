#!/usr/bin/env python3
"""R79: a real program in mandapa blocks - not a microbenchmark.

    python3 -B tests/r79_real/test_real_program.py [--compiler ./sutram_compiler] [--students N]

report_plain.sm is a 185-line class marks report written the natural way; report_blocks.sm is the same text with
the bodies of its three allocating functions (stambh, milan, madhyaka) wrapped in `mandapa { }` and nothing else
changed. For N generated students (default 20,000) both must print exactly what reference.py prints, and the
block version's peak memory must be under 75% of the plain version's (measured at 100,000: 110 MB against
185 MB; 7 MB with the library's own temporaries in blocks too - Claude-to-Sarvam/evidence-r79/).
Linux ELF only. Last line: `r79 real: N checks, M failed`.
"""
import os, random, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))


def main():
    comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
        else os.path.join(ROOT, 'sutram_compiler')
    n = int(sys.argv[sys.argv.index('--students') + 1]) if '--students' in sys.argv else 20000
    work = tempfile.mkdtemp(); inp = os.path.join(work, 'in.txt')
    r = random.Random(79); out = [str(n)]
    for i in range(n):
        out += [str(1000 + i)] + [str(min(100, max(0, int(r.gauss(mu, sd))))) for mu, sd in ((68, 15), (72, 12), (65, 18))]
    open(inp, 'w').write('\n'.join(out) + '\n')
    want = subprocess.run([sys.executable, os.path.join(HERE, 'reference.py'), inp], capture_output=True, text=True).stdout
    checks = failed = 0; rss = {}
    for name in ('report_plain', 'report_blocks'):
        exe = os.path.join(work, name)
        c = subprocess.run([comp, os.path.join(HERE, name + '.sm'), exe], capture_output=True, text=True, cwd=ROOT)
        checks += 1
        if c.returncode != 0:
            failed += 1; print(f'FAIL  {name}: did not compile'); continue
        p = subprocess.run(['/usr/bin/time', '-f', '%M', exe], stdin=open(inp), capture_output=True, text=True, timeout=300)
        rss[name] = int(p.stderr.strip().split('\n')[-1])
        ok = p.stdout == want and p.returncode == 0
        failed += not ok
        print(('PASS' if ok else 'FAIL') + f'  {name}: {n} students, output {"identical to" if p.stdout == want else "DIFFERS from"} the reference, peak {rss[name]} KB')
    if len(rss) == 2:
        checks += 1
        ok = rss['report_blocks'] < 0.75 * rss['report_plain']
        failed += not ok
        print(('PASS' if ok else 'FAIL') + f"  memory: with blocks {rss['report_blocks']} KB = {100 * rss['report_blocks'] / rss['report_plain']:.0f}% of {rss['report_plain']} KB")
    print(f'r79 real: {checks} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
