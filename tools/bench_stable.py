#!/usr/bin/env python3
"""Lower-noise Sutram generated-code benchmark.

This complements, rather than replaces, tools/bench.py. It uses longer-running
CPU-bound programs, compiles each program once, discards warm-ups, pins the
process (and inherited children) to one allowed CPU when the OS permits it, and
reports minimum/p10/median so scheduler noise is visible instead of hidden.

Examples:
  python3 tools/bench_stable.py
  python3 tools/bench_stable.py --runs 25 --warmup 5
  python3 tools/bench_stable.py --json

SUTRAM_COMPILER may point at a specific compiler binary for A/B runs.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
COMPILER = Path(os.environ.get("SUTRAM_COMPILER", ROOT / "sutram_compiler"))
PROGRAMS = ("loop_sum_heavy", "nested_loop_heavy", "fib_rec_heavy")


def pin_one_cpu() -> int | None:
    """Pin this process to one CPU; child processes inherit affinity on Linux."""
    if not hasattr(os, "sched_getaffinity") or not hasattr(os, "sched_setaffinity"):
        return None
    try:
        allowed = sorted(os.sched_getaffinity(0))
        if not allowed:
            return None
        cpu = allowed[0]
        os.sched_setaffinity(0, {cpu})
        return cpu
    except (OSError, PermissionError):
        return None


def percentile(samples: list[float], q: float) -> float:
    if not samples:
        return math.nan
    xs = sorted(samples)
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def compile_program(name: str) -> Path:
    src = ROOT / "benchmarks" / f"{name}.sm"
    out = Path("/tmp") / f"bench_stable_{name}.bin"
    cp = subprocess.run([str(COMPILER), str(src), str(out)],
                        capture_output=True, text=True, timeout=60)
    if cp.returncode != 0:
        raise RuntimeError(f"compile failed for {name}:\n{cp.stdout}{cp.stderr}")
    return out


def time_binary(path: Path, warmup: int, runs: int) -> list[float]:
    def once() -> float:
        t0 = time.perf_counter_ns()
        rp = subprocess.run([str(path)], stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, timeout=120)
        dt = (time.perf_counter_ns() - t0) / 1_000_000.0
        if rp.returncode != 0:
            raise RuntimeError(f"{path.name} exited {rp.returncode}: {rp.stderr.decode(errors='replace')}")
        return dt

    for _ in range(warmup):
        once()
    return [once() for _ in range(runs)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=25)
    ap.add_argument("--warmup", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    ns = ap.parse_args()
    if ns.runs < 3 or ns.warmup < 0:
        ap.error("--runs must be >=3 and --warmup must be >=0")

    cpu = pin_one_cpu()
    rows = []
    for name in PROGRAMS:
        binary = compile_program(name)
        samples = time_binary(binary, ns.warmup, ns.runs)
        rows.append({
            "name": name,
            "min_ms": min(samples),
            "p10_ms": percentile(samples, 0.10),
            "median_ms": statistics.median(samples),
            "max_ms": max(samples),
            "spread_pct": ((max(samples) - min(samples)) / min(samples) * 100.0),
            "samples_ms": samples,
        })

    if ns.json:
        print(json.dumps({"compiler": str(COMPILER), "cpu": cpu,
                          "runs": ns.runs, "warmup": ns.warmup,
                          "programs": rows}, indent=2))
        return 0

    print(f"compiler: {COMPILER}")
    print(f"cpu affinity: {cpu if cpu is not None else 'not pinned'}")
    print(f"warmup={ns.warmup} measured_runs={ns.runs}")
    print(f"{'program':22s} {'min ms':>10s} {'p10 ms':>10s} {'median ms':>11s} {'max ms':>10s} {'spread':>9s}")
    print("-" * 78)
    for r in rows:
        print(f"{r['name']:22s} {r['min_ms']:10.3f} {r['p10_ms']:10.3f} "
              f"{r['median_ms']:11.3f} {r['max_ms']:10.3f} {r['spread_pct']:8.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
