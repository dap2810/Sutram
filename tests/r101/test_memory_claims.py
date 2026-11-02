#!/usr/bin/env python3
"""R101: the memory claims, measured by the kernel (tools/peak_rss.py: wait4 -> ru_maxrss).

  1. 1,000,000 x nirmmita(64) with a mandapa per pass: flat (under 1 MB of resident memory)
  2. the same without the block: every allocation stays (over 32 MB; 62 MB measured)
  3. 10,000,000 with the block: still flat - the claim "a block bounds memory" for nirmmita
  4. a kosh grown to 100,000 with an allocation between pushes: up to v283 it moved at every doubling and
     the abandoned copies cost about one more kosh (1.8 MB against 0.8 MB). R101A (v284): a kosh has a
     region of its own and grows in place, so it costs the same as one that grows alone (within 1.25x)
  5. a kosh made in a mandapa 100,000 times: NOT reclaimed by the block (about 100 MB). This pins a known,
     documented gap: if it starts passing below 8 MB, the block reclaims kosh storage and the reference
     (section 19) must change with it. (R101A: 400 MB, one page per kosh at least.)
  6. R101A: a kosh past its region (9,000,000 pushes; the region holds 8,388,603) moves once and keeps
     every value - the sum is exact.
  7. R103 (v285): 1,000,000 x nirmmita(64) in ONE block with `mandapa parimita 1048576` refuses (E_PARIMITA,
     exit 1) at the 16,385th, and its peak stays under 2 MB: the budget refuses rather than grows.
  8. R103: the same budget on a block entered once per pass runs to the end, flat (under 1 MB).
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
        big = os.path.join(w, 'kosh_past_region')
        open(big + '.sm', 'w').write('''mukhya() {
    kosh k[1]
    vitti i = 0
    yavat (i < 9000000) {
        kosh_push(k, i)
        i = i + 1
    }
    vitti s = 0
    i = 0
    yavat (i < kosh_len(k)) {
        s = s + k[i]
        i = i + 1
    }
    likha("s ", s, " len ", kosh_len(k))
}
''')
        refuse_src = open(os.path.join(ROOT, 'examples', '303_r103_parimita_refuses.sm')).read()
        m_refuse = peak(w, 'budget_refuses', refuse_src)
        rp = os.path.join(w, 'budget_refuses')
        r = subprocess.run([rp], capture_output=True, text=True)
        refuse_msg = (r.stdout + r.stderr).strip()
        print(f'      budget_refuses: peak {m_refuse[0]} KB, exit {m_refuse[1]}, {refuse_msg[:60]!r}')
        m['budget_within'] = peak(w, 'budget_within', LOOP.format(n=1000000, body=WITH.replace(
            '        mandapa', '        mandapa parimita 1048576')))
        subprocess.run([COMP, big + '.sm', big], cwd=ROOT, capture_output=True)
        past = subprocess.run([big], capture_output=True, text=True).stdout.strip()
        print(f'      kosh_past_region: {past!r}')
        for k, (kb, code) in m.items():
            print(f'      {k}: peak {kb} KB, exit {code}')
        tests = [
            ('1,000,000 nirmmita(64) in a block: under 1 MB', m['with_1m'][0] < 1024),
            ('the same without the block: over 32 MB', m['without_1m'][0] > 32768),
            ('10,000,000 in a block: still under 1 MB (flat)', m['with_10m'][0] < 1024),
            ('a kosh of 100,000 grown past an allocation costs what one grown alone does (within 1.25x; R101A)',
             m['kosh_moving'][0] <= 1.25 * max(m['kosh_in_place'][0], 256)),
            ('a kosh made in a block 100,000 times is NOT reclaimed (the documented gap): over 8 MB', m['kosh_in_block'][0] > 8192),
            ('a kosh past its region keeps every value (9,000,000 pushes; R101A)',
             past == f's {sum(range(9000000))} len 9000000'),
            ('a 1 MB budget refuses 1,000,000 x 64 bytes (E_PARIMITA, exit 1) with a peak under 2 MB (R103)',
             m_refuse[1] == 1 and 'E_PARIMITA' in refuse_msg and m_refuse[0] is not None and m_refuse[0] < 2048),
            ('the same budget, one block per pass, runs to the end under 1 MB (R103)', m['budget_within'][0] < 1024),
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
