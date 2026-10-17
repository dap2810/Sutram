#!/usr/bin/env python3
"""Measure the kosh growth-avoidance pattern (R30 WS2).

The compiler-side leak (R29): kosh_push growth allocates a new buffer,
copies, and never releases the old one. The language has no free
primitive, so repeated growth retains every superseded buffer.

Two patterns, same work (R rounds x N pushes, same values):

  A. fresh + grow (leaky): each round declares a fresh `kosh v[4]`
     and pushes N items. Growth doubles from 4 to N, retaining ~2x
     the final buffer per round — O(R x N) retained.
  B. reserve + reuse (harm reduction): ONE `kosh v[N]` declared up
     front with the full capacity, each round fills it to N and
     `kosh_clear`s it. No growth ever happens, so no superseded
     buffer exists — O(N) retained, one allocation.

This is harm reduction, NOT a fix: pattern B still retains its one
allocation for the process lifetime (there is no free), and the
growth path still leaks for any kosh that does grow. What it buys
is a cap: retention stops growing with the number of rounds.

This is a diagnostic, not a suite gate: RSS is machine-dependent,
so it lives here rather than in tools/proof_lib.py.

Usage: python3 tools/kosh_reuse_measure.py
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER = os.path.join(REPO, "build", "sutram_compiler")
ROUNDS = 50
N = 100_000


def child_rss(path):
    pid = os.fork()
    if pid == 0:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        os.execv(path, [path])
        os._exit(127)
    _, status, ru = os.wait4(pid, 0)
    assert status == 0, f"child exit status {status}"
    return ru.ru_maxrss  # KiB on Linux


def measure(name, src):
    sm = f"/tmp/kosh_reuse_{name}.sm"
    binary = sm + ".bin"
    open(sm, "w").write(src)
    r = subprocess.run([COMPILER, sm, binary], capture_output=True, text=True)
    assert "OK" in r.stdout, f"compile failed: {r.stdout}"
    rss = child_rss(binary) / 1024.0  # MB
    os.remove(sm)
    os.remove(binary)
    return rss


def pattern_fresh_grow():
    # Fresh kosh per round, grown from cap 4 to N.
    return ("mukhya() {\n"
            "    vitti round = 0\n"
            "    vitti total = 0\n"
            "    yavat (round < %d) {\n"
            "        kosh v[4]\n"
            "        vitti i = 0\n"
            "        yavat (i < %d) {\n"
            "            kosh_push(v, i)\n"
            "            i = i + 1\n"
            "        }\n"
            "        total = total + kosh_len(v)\n"
            "        kosh_clear(v)\n"
            "        round = round + 1\n"
            "    }\n"
            "    likha(total)\n"
            '    likha("\\n")\n'
            "}\n" % (ROUNDS, N))


def pattern_reserve_reuse():
    # One kosh, capacity reserved up front, cleared and reused.
    return ("mukhya() {\n"
            "    kosh v[%d]\n"
            "    vitti round = 0\n"
            "    vitti total = 0\n"
            "    yavat (round < %d) {\n"
            "        vitti i = 0\n"
            "        yavat (i < %d) {\n"
            "            kosh_push(v, i)\n"
            "            i = i + 1\n"
            "        }\n"
            "        total = total + kosh_len(v)\n"
            "        kosh_clear(v)\n"
            "        round = round + 1\n"
            "    }\n"
            "    likha(total)\n"
            '    likha("\\n")\n'
            "}\n" % (N, ROUNDS, N))


def main():
    base = measure("base", "mukhya() {\n    likha(0)\n    likha(\"\\n\")\n}\n")
    fresh = measure("fresh", pattern_fresh_grow())
    reuse = measure("reuse", pattern_reserve_reuse())
    print(f"baseline peak RSS: {base:.1f} MB")
    print(f"A. fresh + grow:   {fresh:.1f} MB "
          f"(+{fresh - base:.1f} MB over baseline)")
    print(f"B. reserve + reuse: {reuse:.1f} MB "
          f"(+{reuse - base:.1f} MB over baseline)")
    print(f"work: {ROUNDS} rounds x {N} pushes "
          f"({ROUNDS * N} pushes each)")
    if fresh - base > 2 * max(reuse - base, 1.0):
        print("RESULT: reserve + reuse retains far less than fresh + grow")
        return 0
    print("RESULT: no clear difference (unexpected — re-run on this machine)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
