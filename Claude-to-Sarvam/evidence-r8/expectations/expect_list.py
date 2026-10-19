import sys, pathlib
from collections import deque
M = 2**64
def signed(x): x %= M; return x - M if x >= 2**63 else x
def tdiv(a, b): q = abs(a) // abs(b); return q if (a >= 0) == (b > 0) else -q
def tmod(a, b): return a - b * tdiv(a, b)
st = 7; out = []
def nxt():
    global st
    st = signed(st * 6364136223846793005 + 1442695040888963407)
    r = tmod(st, 1000003)
    return -r if r < 0 else r
L = []
for step in range(500):
    r = nxt(); op = r % 6; i = (r // 6) % (len(L) + 2) - 1
    if op <= 1: L.append(step); out.append(1)
    elif op == 2:
        if 0 <= i <= len(L): L.insert(i, step); out.append(1)
        else: out.append(0)
    elif op == 3:
        if 0 <= i < len(L): del L[i]; out.append(1)
        else: out.append(0)
    elif op == 4: out.append(L[i] if 0 <= i < len(L) else 0)
    else:
        j = (r // 7) % (len(L) + 1)
        if 0 <= i < len(L) and 0 <= j < len(L): L[i], L[j] = L[j], L[i]; out.append(1)
        else: out.append(0)
out += [len(L), *L]
Q = deque()
for step in range(500):
    r = nxt(); op = r % 5
    if op <= 1: Q.append(step); out.append(1)
    elif op == 2: out += [Q.popleft(), 1] if Q else [0, 0]
    elif op == 3: out += [Q[0], 1] if Q else [0, 0]
    else: out.append(int(step - 3 in Q))
out += [len(Q), len(Q), *Q]
pathlib.Path(sys.argv[1]).write_text(''.join(f'{x}\n' for x in out))
print('list len', len(L), 'queue len', len(Q))
