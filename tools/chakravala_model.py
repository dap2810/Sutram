#!/usr/bin/env python3
"""Python model of the R29 chakravala candidate selection (R30 WS5).

Models lib/ganita.smlib chakravala's per-step candidate choice:
given (a, b, k) with a^2 - n*b^2 = k, pick m with (a + b*m) divisible
by |k| minimising |m^2 - n|. The code solves b*m = -a (shesh |k|) with
kuttaka, then compares the two candidates bracketing sqrt(n). A
candidate with m > isqrt(MAX) is SKIPPED, because m*m would overflow
int64 and |m^2 - n| cannot even be evaluated.

Usage:
    python3 tools/chakravala_model.py [n]
With no argument, analyses the documented R30 case
n = 9223372030926249006, where the below-sqrt candidate is valid but
suboptimal: the above-sqrt candidate is strictly better, but its
vargit overflows int64, so the code picks the worse one and the
iteration ultimately returns 0.

With an argument, prints the first-step candidate table for that n.
"""
import math
import sys

MAXV = 2**63 - 1
ISQ = math.isqrt(MAXV)  # 3037000499

# The documented R30 case (first step, n > MAX/2).
DOC_N = 9223372030926249006


def kuttaka(a, b, c):
    """One solution of a*x = c (shesh b); None if unsolvable."""
    g = math.mahattam(a, b)
    if c % g != 0:
        return None
    a1, b1, c1 = a // g, b // g, c // g
    inv = pow(a1, -1, b1)
    return (inv * c1) % b1


def first_step(n):
    """First chakravala step for n. Returns a dict, or None if n is
    a perfect vargit (trivial solution) or the step is impossible."""
    a = math.isqrt(n)
    b = 1
    k = a * a - n
    if k == 0:
        return None
    ak = abs(k)
    if a % math.mahattam(b, ak) != 0:
        return None
    m0 = kuttaka(b, ak, -a)
    varg = math.isqrt(n)
    d = varg - m0
    t = d // ak
    if d < 0 and d % ak != 0:
        t -= 1
    cands = []
    for _ in range(2):
        m = m0 + t * ak
        valid = (a + b * m) % ak == 0
        fits = m * m <= MAXV
        cands.append({
            "m": m,
            "valid": valid,
            "fits_int64": fits,
            "score": abs(m * m - n),
        })
        t += 1
    # Code rule: keep candidates with 0 <= m <= isqrt(MAX), pick min score.
    kept = [c for c in cands if 0 <= c["m"] <= ISQ]
    picked = min(kept, key=lambda c: c["score"]) if kept else None
    return {"a": a, "b": b, "k": k, "ak": ak, "varg": varg,
            "candidates": cands, "picked": picked}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else DOC_N
    print(f"n = {n}")
    print(f"MAX = {MAXV}, MAX/2 = {MAXV // 2}, n > MAX/2: {n > MAXV // 2}")
    print(f"isqrt(MAX) = {ISQ}")
    st = first_step(n)
    if st is None:
        print("perfect vargit or impossible first step")
        return 0
    print(f"first step: a = {st['a']}, b = {st['b']}, k = {st['k']}, "
          f"|k| = {st['ak']}, isqrt(n) = {st['varg']}")
    for c in st["candidates"]:
        tag = ""
        if st["picked"] is not None and c["m"] == st["picked"]["m"]:
            tag = "  <-- picked by the code"
        print(f"  m = {c['m']}: (a + b*m) % |k| == 0: {c['valid']}, "
              f"m*m <= MAX: {c['fits_int64']}, |m*m - n| = {c['score']}{tag}")
    lo, hi = st["candidates"]
    if (hi["score"] < lo["score"] and not hi["fits_int64"]
            and hi["m"] > ISQ and lo["m"] <= ISQ):
        print("LIMITATION DEMONSTRATED: the above-sqrt candidate is "
              "strictly better, but m > isqrt(MAX), so m*m overflows "
              "int64 and the code must pick the worse below-sqrt one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
