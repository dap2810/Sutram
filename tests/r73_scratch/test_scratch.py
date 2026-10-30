#!/usr/bin/env python3
"""R73 (Steps 3 + 4): the mandapa block's scratch side, and the escape check.

    python3 -B tests/r73_scratch/test_scratch.py --compiler ./sutram_compiler

  * loop_with / loop_without: the same output; peak RSS with the block below 4 MB, without it above 32 MB
    (1,000,000 x 64 B). This is the measurement that says whether the block works;
  * jumps: agrim, krama and recursion rewind; flat memory over 1,000,000 agrim passes;
  * reuse_zeroed: reused scratch reads 0; nirmmita(0) is 0;
  * full: kshetra purnam, exit 1;
  * escape_*: refused with E_SCRATCH_ESCAPE, and the message carries the Sanket line naming the blind spots;
  * allowed_*: compiles and runs;
  * blind_call: compiles - a known blind spot, pinned here so a future check that catches it is noticed.
  * R74: ChatGPT R146's F1 (store calls in expressions), F2 (loop back edges), F3 (prasar rewinds:
    flat over 1,000,000 failures), F4 (negative sizes) - escape_f1_*, escape_f2_*, allowed_f*, prasar_rewind,
    negative_size.
Linux ELF only (PE output keeps the ordinary allocator; GUARD_PAGES builds turn the block off).
Last line: `r73 scratch: N checks, M failed`.
"""
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EXPECT = {
    'loop_with': '499999500000', 'loop_without': '499999500000',
    'jumps': '250000000000\n5\n5050', 'reuse_zeroed': '0\n11', 'allowed_nested': '7', 'blind_call': '1',
    # R74: ChatGPT R146's F1-F4, closed in v271
    'allowed_f1_numbers': '42 41', 'allowed_f2_numbers': '123', 'prasar_rewind': '3500000 500000',
    'negative_size': '0 0 0\n0 0\n123 456', 'allowed_global_number': '42',
}


def main():
    comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1]) if '--compiler' in sys.argv \
        else os.path.join(ROOT, 'sutram_compiler')
    work = tempfile.mkdtemp()
    checks = failed = 0

    def report(ok, text):
        nonlocal checks, failed
        checks += 1
        failed += not ok
        print(('PASS' if ok else 'FAIL') + '  ' + text)

    def build(name):
        out = os.path.join(work, name)
        c = subprocess.run([comp, os.path.join(HERE, name + '.sm'), out], cwd=ROOT, capture_output=True, text=True)
        return c, out

    def run(out):
        r = subprocess.run(['/usr/bin/time', '-f', '%M', out], capture_output=True, text=True, timeout=60)
        rss = int(r.stderr.strip().split('\n')[-1])
        lines = [l for l in r.stdout.split('\n') if l.strip()]
        return r.returncode, '\n'.join(lines), rss

    rss = {}
    for n in sorted(f[:-3] for f in os.listdir(HERE) if f.endswith('.sm')):
        c, out = build(n)
        if n.startswith('escape_'):
            msg = c.stdout + c.stderr
            report(c.returncode != 0 and 'E_SCRATCH_ESCAPE' in msg and 'Sanket' in msg,
                   f'{n}: refused with E_SCRATCH_ESCAPE and the blind-spot note')
            continue
        if c.returncode != 0:
            report(False, f'{n}: did not compile: {(c.stdout + c.stderr).strip()[-120:]}')
            continue
        code, text, r = run(out)
        rss[n] = r
        if n == 'full':
            report(code == 1 and 'kshetra purnam' in text, f'full: kshetra purnam, exit 1 (exit {code})')
            continue
        want = EXPECT.get(n)
        report(code == 0 and (want is None or text == want), f'{n}: output {text!r}' + (f', peak RSS {r} KB' if n in ('loop_with', 'loop_without', 'jumps', 'prasar_rewind') else ''))
    if 'loop_with' in rss and 'loop_without' in rss:
        report(rss['loop_with'] < 4096 and rss['loop_without'] > 32768,
               f"memory: 1,000,000 x 64 B, with the block {rss['loop_with']} KB, without it {rss['loop_without']} KB")
    if 'prasar_rewind' in rss:
        report(rss['prasar_rewind'] < 4096, f"memory: 1,000,000 prasar failures out of blocks, {rss['prasar_rewind']} KB")
    if 'jumps' in rss:
        report(rss['jumps'] < 4096, f"memory: 1,000,000 agrim passes through a block, {rss['jumps']} KB")
    print(f'r73 scratch: {checks} checks, {failed} failed')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
