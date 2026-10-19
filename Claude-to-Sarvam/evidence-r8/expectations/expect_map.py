import sys, pathlib
M = 2**64
def signed(x): x %= M; return x - M if x >= 2**63 else x
def tdiv(a, b): q = abs(a) // abs(b); return q if (a >= 0) == (b > 0) else -q
def tmod(a, b): return a - b * tdiv(a, b)
st = 20261019; d = {}; out = []
for step in range(600):
    st = signed(st * 6364136223846793005 + 1442695040888963407)
    r = tmod(st, 1000003)
    if r < 0: r = -r
    k = r % 12; op = (r // 12) % 3
    if op == 0:
        if k in d or len(d) < 7: d[k] = step; out.append(1)
        else: out.append(0)
    elif op == 1: out.append(1 if d.pop(k, None) is not None else 0)
    else: out.append(d.get(k, -1))
out.append(len(d))
pathlib.Path(sys.argv[1]).write_text(''.join(f'{x}\n' for x in out))
from collections import Counter
print(Counter((o) for o in out[:-1] if o in (0, 1)), 'full-rejections:', sum(1 for i,o in enumerate(out[:-1]) if o == 0))
