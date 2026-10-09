#!/usr/bin/env python3
"""Measure Sutram's own speed so "faster" is a number, not a claim.

  python3 tools/bench.py              # compile time + run time for a set of programs
  python3 tools/bench.py --runs 20    # more run samples (default 10)
  python3 tools/bench.py --json       # machine-readable, for tracking across rounds

Two things are timed per program:
  compile  — how long sutram_compiler takes to emit the binary
  run      — how long the produced binary takes (median of N runs)

Deliberately excludes I/O-heavy programs, so the numbers reflect generated code,
not the terminal. Keep this file stable: it is the baseline we compare rounds against.
"""
import json, os, statistics, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER = os.environ.get("SUTRAM_COMPILER") or os.path.join(ROOT, "sutram_compiler")

# representative: arithmetic loop, recursion, nested loops, arrays, strings, branching
PROGRAMS = [
    "02_arith", "04_while", "11_forloop", "41_recursion", "45_shifts",
    "20_pankti_array", "14_strings", "22_precedence", "prime", "multable",
    "fizzbuzz", "strength_reduction",
]
# CPU-bound programs live in benchmarks/ — these are the ones whose RUN time
# actually reflects generated code rather than process startup.
CPU_PROGRAMS = ["loop_sum", "nested_loop", "fib_rec"]


def median_ms(fn, runs):
    samples = []
    for _ in range(runs):
        t = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t) * 1000.0)
    return statistics.median(samples)


def bench_one(name, runs):
    src = os.path.join(ROOT, "examples", name + ".sm")
    if not os.path.exists(src):
        src = os.path.join(ROOT, "benchmarks", name + ".sm")
    if not os.path.exists(src):
        return None
    out = f"/tmp/bench_{name}.bin"

    def compile_once():
        subprocess.run([COMPILER, src, out], capture_output=True, timeout=60)

    c_ms = median_ms(compile_once, max(3, runs // 3))
    if not os.path.exists(out):
        return None

    def run_once():
        subprocess.run([out], capture_output=True, timeout=60)

    r_ms = median_ms(run_once, runs)
    return c_ms, r_ms


def main():
    runs = 10
    if "--runs" in sys.argv:
        runs = int(sys.argv[sys.argv.index("--runs") + 1])
    as_json = "--json" in sys.argv

    rows = []
    print("# compile-heavy set (examples/)")
    for name in PROGRAMS:
        got = bench_one(name, runs)
        if got:
            rows.append((name, got[0], got[1]))

    if as_json:
        print(json.dumps({"runs": runs,
                          "programs": [{"name": n, "compile_ms": round(c, 2), "run_ms": round(r, 3)}
                                       for n, c, r in rows]}))
        return 0

    print(f"{'program':22s} {'compile ms':>10s} {'run ms':>9s}")
    print("-" * 44)
    for n, c, r in rows:
        print(f"{n:22s} {c:10.2f} {r:9.3f}")
    print("-" * 44)
    print("\n# CPU-bound set (benchmarks/) - run time here reflects generated code")
    print(f"{'program':22s} {'compile ms':>10s} {'run ms':>9s}")
    print("-" * 44)
    for name in CPU_PROGRAMS:
        got = bench_one(name, runs)
        if got:
            rows.append((name, got[0], got[1]))
            print(f"{name:22s} {got[0]:10.2f} {got[1]:9.3f}")
    print("-" * 44)
    if rows:
        print(f"{'TOTAL':22s} {sum(c for _, c, _ in rows):10.2f} {sum(r for _, _, r in rows):9.3f}")
        print(f"{'MEDIAN':22s} {statistics.median(c for _, c, _ in rows):10.2f} "
              f"{statistics.median(r for _, _, r in rows):9.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
