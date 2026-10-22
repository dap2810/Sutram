"""WS2: the same library mutations through both checkers. Each mutation is applied to a copy of lib/."""
import os, shutil, subprocess, sys, tempfile
REPO = sys.argv[1]
MUT = [
 ('M0 none (today\'s library)', None, None, None, 'both pass'),
 ('M1 mala_nava loses its bound (sz = c * 8 unchecked)', 'mala.smlib',
  '    yadi (c > 1152921504606846975) { prati 0 }\n', '', 'unsafe: must FAIL'),
 ('M2 a new function in mala allocates an unbounded product through sz', 'mala.smlib',
  'prakriya mala_nava(n) {', 'prakriya mala_dvi(n) {\n    vitti sz = n * 16\n    prati nirmmita(sz)\n}\n\nprakriya mala_nava(n) {', 'unsafe: must FAIL'),
 ('M3 aadhar respaces c * 8 as c*8 (same code)', 'aadhar.smlib',
  '    vitti w = nirmmita(c * 8)\n', '    vitti w = nirmmita(c*8)\n', 'safe: should PASS'),
 ('M4 a new constant scratch nirmmita(64) in shreni', 'shreni.smlib',
  '    vitti tmp = nirmmita(n * 8)\n', '    vitti pad = nirmmita(64)\n    vitti tmp = nirmmita(n * 8)\n', 'safe: should PASS'),
 ('M5 suchi_srij splits nirmmita(3 * 8) over two lines', 'suchi.smlib',
  '    l = nirmmita(3 * 8)\n', '    l = nirmmita(\n        3 * 8)\n', 'safe, unreadable: a refusal is the honest answer'),
 ('M6 a bounded new formula: suchi_vardh allocates ncap * 8 + 8', 'suchi.smlib',
  '    ncap = lst[1] * 2\n    nd = nirmmita(ncap * 8)\n', '    ncap = lst[1] * 2\n    nd = nirmmita(ncap * 8 + 8)\n', 'safe (ncap is bounded): should PASS'),
]
for name, f, old, new, truth in MUT:
    t = tempfile.mkdtemp()
    shutil.copytree(os.path.join(REPO, 'lib'), os.path.join(t, 'lib'))
    os.makedirs(os.path.join(t, 'tools'))
    shutil.copy(os.path.join(REPO, 'tools/check_alloc_bounds.py'), os.path.join(t, 'tools'))
    if f:
        p = os.path.join(t, 'lib', f); s = open(p).read(); assert s.count(old) == 1, name
        open(p, 'w').write(s.replace(old, new))
    a = subprocess.run([sys.executable, '-B', os.path.join(REPO, 'ChatGPT-to-Sarvam/ROUND-103-CHECK-ALLOC-SIZES.py'),
                        os.path.join(t, 'lib')], capture_output=True, text=True)
    b = subprocess.run([sys.executable, '-B', os.path.join(t, 'tools/check_alloc_bounds.py')], capture_output=True, text=True)
    ra = 'PASS' if a.returncode == 0 else 'FAIL'
    rb = 'PASS' if b.returncode == 0 else 'FAIL'
    print(f'{name}\n    truth: {truth}\n    R103 allowlist: {ra}   alloc-bounds gate: {rb}')
    shutil.rmtree(t)
