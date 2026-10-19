import sys, pathlib
M = 2**64
def signed(x): x %= M; return x - M if x >= 2**63 else x
def tdiv(a, b): q = abs(a) // abs(b); return q if (a >= 0) == (b > 0) else -q
def tmod(a, b): return a - b * tdiv(a, b)
st = 99; out = []
def nxt():
    global st
    st = signed(st * 6364136223846793005 + 1442695040888963407)
    r = tmod(st, 1000003)
    return -r if r < 0 else r
def split(s, sep, maxp):
    if not s: return [[]]
    if not sep: return [s]
    S = ''.join(map(chr, s)).split(''.join(map(chr, sep)))
    return [list(map(ord, x)) for x in S][:maxp]
for step in range(300):
    r = nxt(); n = r % 10; kind = (r // 10) % 4; maxp = (r // 40) % 5
    s = []
    for i in range(n):
        ch = 97 + nxt() % 3
        s.append(44 if ch == 99 else ch)
    sep = {0: [44], 1: [97, 98], 2: [44, 44], 3: []}[kind]
    segs = split(s, sep, maxp)
    for _ in range(2):
        out.append(len(segs))
        for g in segs: out += [len(g), *g]
pathlib.Path(sys.argv[1]).write_text(''.join(f'{x}\n' for x in out))
