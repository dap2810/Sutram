# Independent expectations for the R8 proofs: computed here from the contracts, not from the compiler.
import math
MAX = 2**63 - 1; MIN = -2**63
def L(*v): return ''.join(f'{x}\n' for x in v)
def isprime(n): return n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))
def kuttaka(a, b, c):
    # least x in [0, b) with a*x = c (mod b)
    return next(x for x in range(b) if (a * x - c) % b == 0)
def fibm(n): # 0,1,1,2,3
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
up = lambda c: c - 32 if 97 <= c <= 122 else c
lo = lambda c: c + 32 if 65 <= c <= 90 else c
E = {}
E['r8_number_edges'] = L(math.factorial(2), math.factorial(3),
    *[int(isprime(n)) for n in (4, 9, 25, 49, 2, 3, 5)],
    *[math.isqrt(n) for n in (2, 3, 4, 8, 9)],
    kuttaka(7, 2, 12), kuttaka(3, 7, 0), kuttaka(3, 7, 1),
    *[fibm(n) for n in (0, 1, 2, 3)],
    *[len(str(abs(n))) for n in (9, 10, 100, -10)],
    0, 1,
    *[up(c) for c in (96, 97, 122, 123)], *[lo(c) for c in (64, 65, 90, 91)])
a = [5, 3, 9]
E['r8_array_guard'] = L(min(a), 0, -1, max(a), sum(a), 0, 0, 0)
s = [96, 97, 122, 123, 64, 65, 90, 91]
x, y = [97, 98, 88], [97, 98, 89]
def aadi(s, sn, p, pn): return int(0 <= pn <= sn and s[:pn] == p[:pn])
def ant(s, sn, p, pn): return int(0 <= pn <= sn and s[sn - pn:sn] == p[:pn])
def tul(a, an, b, bn):
    A, B = a[:an], b[:bn]; return (A > B) - (A < B)
E['r8_text_edges'] = L(8, *map(up, s), 8, *map(lo, s),
    aadi(x, 3, y, 2), aadi(x, 2, y, 2), aadi(x, 3, y, 0), aadi(x, 2, y, 3),
    ant(x, 2, y, 2), ant(x, 3, x, 3), ant(x, 3, y, 0), ant(x, 2, x, 3),
    tul(x, 2, y, 2), tul(x, 3, y, 3), tul(x, 2, y, 3))
# list [10,20,30,40]; remove index 3 -> [10,20,30]; then index 3 is out of bounds everywhere
E['r8_list_edges'] = L(1, 3, 0, 0, 0, 0, 0, 3, 10, 30, 1, 5)
fits = lambda v: MIN <= v <= MAX
E['r8_result_flags'] = L(1, 0, 1, 0, 1, int(fits(MAX + 1)), 1, 2 - 3, int(fits(MIN - 1)),
    1, int(fits(MAX * 2)), 1, 0, 1, 0)
def tobase(n, b): 
    d = '0123456789abcdefghijklmnopqrstuvwxyz'; r = ''
    while n: r = d[n % b] + r; n //= b
    return r or '0'
E['r8_base_digits'] = L(len(tobase(10, 16)), ord(tobase(10, 16)[0]), len(tobase(9, 16)), ord(tobase(9, 16)[0]),
    len(tobase(35, 36)), ord(tobase(35, 36)[0]), 0,
    10, 1, 15, 10, 1, 15, 1, 0, 0, 0, 0, 7, 1,
    MAX, 1, 0, 0)
import sys, pathlib
for k, v in E.items():
    pathlib.Path(sys.argv[1], k + '.expect').write_text(v)
print('\n'.join(E))

def pell(n):
    a0 = math.isqrt(n); m, d, a = 0, 1, a0
    p0, p1, q0, q1 = 1, a0, 0, 1
    while p1 * p1 - n * q1 * q1 != 1:
        m = d * a - m; d = (n - m * m) // d; a = (a0 + m) // d
        p0, p1 = p1, a * p1 + p0; q0, q1 = q1, a * q1 + q0
    return p1, q1
rows = []
for n in range(2, 100):
    if math.isqrt(n) ** 2 == n: continue
    x, y = pell(n)
    rows += [n, 1, x, y] if x <= MAX else [n, 0, 0, 0]
E2 = {'r8_chakravala_sweep': L(*rows), 'r8_map_edges': L(1, 7, 0, 1, 1, 2, 97, 98, 77)}
for k, v in E2.items():
    pathlib.Path(sys.argv[1], k + '.expect').write_text(v)
