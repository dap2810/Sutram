import os, subprocess, sys, signal
sys.path.insert(0, os.path.dirname(__file__)); sys.dont_write_bytecode = True
from sweep_probes import PROBES, program
comp, work = sys.argv[1], sys.argv[2]
os.makedirs(work, exist_ok=True)
for name in PROBES:
    src = os.path.join(work, name + '.sm'); open(src, 'w').write(program(name))
    def run(n):
        exe = os.path.join(work, name)
        args = [comp, src, exe] if n == 0 else [comp, '--fail-alloc', str(n), src, exe]
        r = subprocess.run(args, capture_output=True, cwd=os.getcwd())
        if r.returncode or not os.path.exists(exe): return ('COMPILE', r.stdout[-300:])
        p = subprocess.run([exe], capture_output=True, timeout=20); os.remove(exe)
        st = f'SIG{signal.Signals(-p.returncode).name[3:]}' if p.returncode < 0 else f'rc{p.returncode}'
        return (st, p.stdout.decode('utf-8', 'replace').strip())
    plain = run(0)
    res = []
    for n in range(1, 40):
        r = run(n)
        res.append(r)
        if r == plain and n > PROBES[name][3]: break
    setup = PROBES[name][3]
    tgt = res[setup:-1]
    print(f'{name:22s} plain={plain[1]!r:12s} setup-allocs={setup} own-allocs={len(tgt)} ' +
          ' '.join(f'N{setup+1+k}:{s}:{o!r}' for k, (s, o) in enumerate(tgt)))
