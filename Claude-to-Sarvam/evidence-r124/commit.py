#!/usr/bin/env python3
"""R124: commit, as Wine shows it. Wine implements MEM_RESERVE as an inaccessible mapping (---p) and MEM_COMMIT
as a read-write one (rw-p), so the read-write private anonymous mappings of the program's process are what it
has committed - a proxy for Windows commit charge (native Windows not available here). Each program prints
'ready' and waits on grahan; this script then sums the mappings and lets it finish. The Wine process's own
baseline (a program that allocates nothing) is reported, and subtracted."""
import os, subprocess, sys, time, tempfile
G = '<scratch>'
comps = dict(a.split('=', 1) for a in sys.argv[1:])
env = dict(os.environ, WINEDEBUG='-all', WINEPREFIX=G + '/r41/wineprefix')
PROGS = [
    ('prints only', 'mukhya() {\n    likha("ready\\n")\n    vitti x = grahan()\n}\n'),
    ('one nirmmita(64)', 'mukhya() {\n    vitti b = nirmmita(64)\n    likha("ready\\n")\n    vitti x = grahan()\n}\n'),
    ('one kosh of 1', 'mukhya() {\n    kosh k[1]\n    kosh_kship(k, 1)\n    likha("ready\\n")\n    vitti x = grahan()\n}\n'),
    ('100 kosh of 1', 'mukhya() {\n    chakra i = 1 tak 100 {\n        kosh k[1]\n        kosh_kship(k, i)\n    }\n    likha("ready\\n")\n    vitti x = grahan()\n}\n'),
    ('nirmmita(100 MB), every page written', 'mukhya() {\n    vitti b = nirmmita(100000000)\n    vitti i = 0\n    yavat (i < 100000000) {\n        likh8(b + i, 1)\n        i = i + 4096\n    }\n    likha("ready\\n")\n    vitti x = grahan()\n}\n'),
]
def mapped(pid):
    rw = 0
    for l in open(f'/proc/{pid}/maps'):
        f = l.split()
        if len(f) == 5 and f[1] == 'rw-p':          # anonymous, private, read-write
            a, b = (int(x, 16) for x in f[0].split('-'))
            rw += b - a
    return rw
d = tempfile.mkdtemp(dir=G + '/r124')
print('# MB of read-write private anonymous mappings in the Wine process (= what Wine committed), at the program\'s end')
print(f"{'program':40s} " + ' '.join(f'{k:>12s}' for k in comps))
base = {}
for what, src in PROGS:
    p = os.path.join(d, 'p.sm'); open(p, 'w').write(src)
    row = []
    for tag, c in comps.items():
        exe = os.path.join(d, f'p_{tag}.exe')
        r = subprocess.run([c, p, exe], capture_output=True)
        if r.returncode: row.append('NO COMPILE'); continue
        pr = subprocess.Popen(['/usr/lib/wine/wine64', exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
        pr.stdout.readline()
        rw = mapped(pr.pid)
        pr.stdin.write(b'1\r\n'); pr.stdin.flush(); pr.wait(timeout=60)
        if what == 'prints only': base[tag] = rw
        row.append(f'{(rw - base[tag]) / 1e6:12.1f}')
    print(f'{what:40s} ' + ' '.join(row))
print('(each row less the "prints only" row of the same compiler; that row itself is the Wine process baseline:',
      ', '.join(f'{k} {v/1e6:.1f} MB' for k, v in base.items()) + ')')
