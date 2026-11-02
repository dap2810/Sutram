#!/usr/bin/env python3
"""R101: the memory claims, measured by the kernel (tools/peak_rss.py: wait4 -> ru_maxrss).

  1. 1,000,000 x nirmmita(64) with a mandapa per pass: flat (under 1 MB of resident memory)
  2. the same without the block: every allocation stays (over 32 MB; 62 MB measured)
  3. 10,000,000 with the block: still flat - the claim "a block bounds memory" for nirmmita
  4. a kosh grown to 100,000 with an allocation between pushes (it moves at every doubling): the abandoned
     copies cost at most about one more kosh - under 3x the kosh that grows in place
  5. a kosh made in a mandapa 100,000 times: NOT reclaimed by the block (about 100 MB). This pins a known,
     documented gap: if it starts passing below 8 MB, the block reclaims kosh storage and the reference
     (section 19) must change with it.
Last line: "r101 memory: N checks, M failed".
"""
import os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMP = sys.argv[sys.argv.index('--compiler') + 1] if '--compiler' in sys.argv else os.path.join(ROOT, 'sutram_compiler')

LOOP = '''mukhya()
    vitti i = 0
    vitti s = 0
    yavat (i < {n})
{body}
    likha("s ", s)
'''
WITH = '''        mandapa
            vitti b = nirmmita(64)
            b[0] = i
            s = s + b[0]
        i = i + 1'''
WITHOUT = '''        vitti b = nirmmita(64)
        b[0] = i
        s = s + b[0]
        i = i + 1'''
KOSH = '''mukhya() {{
    kosh k[1]
    vitti i = 0
    yavat (i < 100000) {{
        kosh_push(k, i)
{obstacle}        i = i + 1
    }}
    likha("len ", kosh_len(k))
}}
'''
KOSH_IN_BLOCK = '''mukhya() {
    vitti i = 0
    vitti s = 0
    yavat (i < 100000) {
        mandapa {
            kosh k[1]
            vitti j = 0
            yavat (j < 100) {
                kosh_push(k, j)
                j = j + 1
            }
            s = s + k[99]
        }
        i = i + 1
    }
    likha("s ", s)
}
'''


def peak(work, name, src):
    p = os.path.join(work, name)
    open(p + '.sm', 'w').write(src)
    c = subprocess.run([COMP, p + '.sm', p], cwd=ROOT, capture_output=True, text=True)
    if c.returncode:
        return None, None
    out = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'peak_rss.py'), '--repeat', '2', p],
                         capture_output=True, text=True).stdout.split()
    return int(out[1]), int(out[3])


def main():
    checks = fails = 0
    with tempfile.TemporaryDirectory() as w:
        m = {}
        m['with_1m'] = peak(w, 'with_1m', LOOP.format(n=1000000, body=WITH))
        m['without_1m'] = peak(w, 'without_1m', LOOP.format(n=1000000, body=WITHOUT))
        m['with_10m'] = peak(w, 'with_10m', LOOP.format(n=10000000, body=WITH))
        m['kosh_in_place'] = peak(w, 'kosh_in_place', KOSH.format(obstacle=''))
        m['kosh_moving'] = peak(w, 'kosh_moving', KOSH.format(obstacle='        vitti o = nirmmita(8)\n'))
        m['kosh_in_block'] = peak(w, 'kosh_in_block', KOSH_IN_BLOCK)
        for k, (kb, code) in m.items():
            print(f'      {k}: peak {kb} KB, exit {code}')
        tests = [
            ('1,000,000 nirmmita(64) in a block: under 1 MB', m['with_1m'][0] < 1024),
            ('the same without the block: over 32 MB', m['without_1m'][0] > 32768),
            ('10,000,000 in a block: still under 1 MB (flat)', m['with_10m'][0] < 1024),
            ('a moving kosh of 100,000: under 3x the in-place one', m['kosh_moving'][0] < 3 * max(m['kosh_in_place'][0], 256)),
            ('a kosh made in a block 100,000 times is NOT reclaimed (the documented gap): over 8 MB', m['kosh_in_block'][0] > 8192),
        ]
        for text, ok in tests:
            checks += 1
            fails += not ok
            print(('PASS  ' if ok else 'FAIL  ') + text)
        if any(code != 0 for _, code in m.values()):
            fails += 1
            print('FAIL  a program did not exit 0')
    print(f'r101 memory: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
