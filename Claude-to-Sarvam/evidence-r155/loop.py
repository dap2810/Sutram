import os, subprocess, sys, collections
sys.path.insert(0, '/home/claude/sutram/tests/r126')
import importlib.util
spec = importlib.util.spec_from_file_location('k', '/home/claude/sutram/tests/r126/test_kinds.py'); k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
d = sys.argv[1]; n = int(sys.argv[2])
case = [r for r in k.RUNS if r[0].startswith('a prakriya returning its kosh parameter')][0]
what, src, stdin, want, wexit = case
p = os.path.join(d, 'p.sm'); pexe = os.path.join(d, 'p.exe')
open(p, 'w').write(src)
c = subprocess.run(['/home/claude/sutram/sutram_compiler', p, pexe], capture_output=True, text=True, cwd=d)
assert c.returncode == 0, c.stdout + c.stderr
res = collections.Counter(); bad = []
for i in range(n):
    r = subprocess.run([k.WINE, pexe], input=stdin, capture_output=True, timeout=120, cwd=d, env=dict(os.environ, WINEDEBUG='-all'))
    got = (r.stdout + r.stderr).decode('latin-1').replace('\r', '')
    ok = got == want and r.returncode == wexit
    res[ok] += 1
    if not ok: bad.append((i, r.returncode, r.stdout, r.stderr))
print('want', repr(want), wexit); print('runs', n, 'ok', res[True], 'failed', res[False])
for b in bad[:10]: print('FAILED run', b)
