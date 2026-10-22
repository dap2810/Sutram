"""R39 WS3: provenance mutations through main's (R38) gate, this round's gate, and the R103 allowlist."""
import os, shutil, subprocess, sys, tempfile
REPO, OLDGATE, OLDLIB = sys.argv[1], sys.argv[2], sys.argv[3]
MUT = [
 ('P0 no mutation', None, None, None, 'safe'),
 ('P1 mala_nava\'s bound raised past the safe value (c > 2^61)', 'mala.smlib',
  '    yadi (c > 1152921504606846975) { prati 0 }\n', '    yadi (c > 2305843009213693952) { prati 0 }\n', 'unsafe: c * 8 wraps under the bound'),
 ('P2 mala_nava doubles c after its bound', 'mala.smlib',
  '    sz = c * 8\n', '    c = c * 2\n    sz = c * 8\n', 'unsafe: the bound no longer covers c'),
 ('P3 a new allocation in an exempt prakriya (rakh_bhed)', 'sangrah.smlib',
  'prakriya rakh_bhed(a, cap, b, bcap, out) {\n    vitti ocap = out[0]\n',
  'prakriya rakh_bhed(a, cap, b, bcap, out) {\n    vitti ocap = out[0]\n    vitti extra = nirmmita(bcap * 64)\n', 'unsafe: bcap is the caller\'s, unbounded'),
 ('P4 R104\'s case: sz = c * 8 with no check, nirmmita(sz)', 'mala.smlib',
  '    yadi (c > 1152921504606846975) { prati 0 }\n    sz = c * 8\n', '    sz = c * 8\n', 'unsafe'),
 ('P5 the multiply moved into the caller: mala_nava calls a helper with c * 8', 'mala.smlib',
  'prakriya mala_nava(n) {', 'prakriya mala_raw(sz) {\n    prati nirmmita(sz)\n}\n\nprakriya mala_nava2(n) {\n    prati mala_raw(n * 8)\n}\n\nprakriya mala_nava(n) {', 'unsafe: n * 8 wraps; no nirmmita sees it'),
 ('P6 mala_nava loses its c < 0 check (the R37 defect: -2^61 + 1 cells is 8 bytes)', 'mala.smlib',
  '    yadi (c < 0) { prati 0 }   # R37: -2^61 + 1 wrapped to 8\n', '', 'unsafe: a negative count wraps positive'),
 ('P7 mala_nava\'s bound only on one branch (yadi (n == 7) { yadi (c > K) ... })', 'mala.smlib',
  '    yadi (c > 1152921504606846975) { prati 0 }\n', '    yadi (n == 7) {\n        yadi (c > 1152921504606846975) { prati 0 }\n    }\n', 'unsafe for n != 7'),
]
def run(libsrc, gate, mut):
    name, f, old, new, truth = mut
    t = tempfile.mkdtemp()
    shutil.copytree(libsrc, os.path.join(t, 'lib'))
    os.makedirs(os.path.join(t, 'tools'))
    if f:
        p = os.path.join(t, 'lib', f); s = open(p).read(); assert s.count(old) == 1, name
        open(p, 'w').write(s.replace(old, new))
    if gate == 'R103':
        r = subprocess.run([sys.executable, '-B', os.path.join(REPO, 'ChatGPT-to-Sarvam/ROUND-103-CHECK-ALLOC-SIZES.py'), os.path.join(t, 'lib')], capture_output=True, text=True)
    else:
        shutil.copy(gate, os.path.join(t, 'tools/check_alloc_bounds.py'))
        r = subprocess.run([sys.executable, '-B', os.path.join(t, 'tools/check_alloc_bounds.py')], capture_output=True, text=True)
    shutil.rmtree(t)
    return 'PASS' if r.returncode == 0 else 'FAIL'

print('Each checker runs on the library of its own round, with the same mutation applied:')
print('  R38 gate (main before R39) and the R103 allowlist on the R38 library; the R39 gate on the R39 library.')
for mut in MUT:
    a = run(OLDLIB, OLDGATE, mut)
    b = run(os.path.join(REPO, 'lib'), os.path.join(REPO, 'tools/check_alloc_bounds.py'), mut)
    c = run(OLDLIB, 'R103', mut)
    print(f'{mut[0]}\n    truth: {mut[4]}\n    R38 gate: {a}   R39 gate: {b}   R103 allowlist: {c}')
