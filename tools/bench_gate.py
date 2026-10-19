#!/usr/bin/env python3
"""tools/bench_gate.py — the performance gate.

The project's rule is "performance measured, not assumed". Until now there was no gate
that measured anything: `benchmarks/` held eleven programs and `tools/bench.py` existed,
but nothing in `tools/gates.sh` ran them.

This gate COMPILES and RUNS every benchmark, repeats each one, and reports the median
wall time. It records numbers; it does not invent a threshold.

A threshold would be dishonest here. A pass/fail line on a wall-clock measurement depends
on the machine, the load and the governor, so a fixed number would either be trivially
true on a fast box or a permanent false alarm on a slow one. So the gate fails only when
a benchmark cannot be built or run, and prints the numbers for the record — which is what
"measured, not assumed" actually requires.

Usage:
    python3 tools/bench_gate.py --compiler ./sutram_compiler [--repeat 5] [--json out.json]
"""

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def find_benchmarks(root):
    d = os.path.join(root, "benchmarks")
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".sm"))


def run_one(compiler, src, repeat):
    """Compile and run one benchmark. Returns (ok, median_ms, detail)."""
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "bench.bin")
        r = subprocess.run([compiler, src, out], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(out):
            return False, None, (r.stdout or r.stderr).strip().split("\n")[0][:70]
        os.chmod(out, 0o755)
        times = []
        for _ in range(repeat):
            t0 = time.perf_counter()
            p = subprocess.run([out], capture_output=True)
            times.append((time.perf_counter() - t0) * 1000.0)
            if p.returncode not in (0,):
                # a benchmark may legitimately exit non-zero; only a signal is fatal
                if p.returncode < 0:
                    return False, None, f"killed by signal {-p.returncode}"
        return True, statistics.median(times), f"min {min(times):.2f} / max {max(times):.2f} ms"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compiler", default=os.path.join(ROOT, "sutram_compiler"))
    ap.add_argument("--repeat", type=int, default=5)
    ap.add_argument("--json")
    a = ap.parse_args()

    if not os.path.exists(a.compiler):
        print(f"  compiler not found: {a.compiler}")
        return 2

    benches = find_benchmarks(ROOT)
    if not benches:
        print("  no benchmarks found in benchmarks/")
        return 2

    print(f"  machine: {platform.machine()} · {platform.system()} · "
          f"{os.cpu_count()} cpus · repeat {a.repeat}")
    results = []
    ok_n = bad_n = 0
    for src in benches:
        name = os.path.basename(src)
        ok, med, detail = run_one(a.compiler, src, a.repeat)
        if ok:
            ok_n += 1
            print(f"  {name:28s} {med:9.2f} ms   ({detail})")
        else:
            bad_n += 1
            print(f"  {name:28s} FAILED      {detail}")
        results.append({"benchmark": name, "ok": ok, "median_ms": med, "detail": detail})

    print()
    print(f"  {ok_n} ran, {bad_n} failed")
    print("  These are wall-clock numbers on THIS machine. They are recorded, not asserted —")
    print("  a threshold would be true on one box and a false alarm on another.")
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"machine": platform.machine(), "system": platform.system(),
                       "cpus": os.cpu_count(), "repeat": a.repeat, "results": results}, f, indent=2)
        print(f"  wrote {a.json}")
    return 0 if bad_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
