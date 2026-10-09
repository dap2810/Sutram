#!/usr/bin/env python3
"""PERF-F1 native runtime benchmark. No compiler/runtime dependencies.

Runs a 5M-iteration binary64 accumulation with correctness checking, optional
one-core affinity, warm-ups, and the min/p10/median. Compare on SAME host,
same CPU/core and workload; never compare cross-host raw times as speedups.
"""
import os
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER = Path(os.environ.get("SUTRAM_COMPILER", ROOT / "sutram_compiler"))
SOURCE = ROOT / "benchmarks" / "float_accum_heavy.sm"
EXPECTED = "1250000.000000\n"


def main():
    with tempfile.TemporaryDirectory(prefix="sutram-float-hot-") as tmp:
        out = Path(tmp) / "float_hot.bin"
        subprocess.run([str(COMPILER), str(SOURCE), str(out)], check=True, capture_output=True)
        affinity = None
        if hasattr(os, "sched_getaffinity"):
            allowed = sorted(os.sched_getaffinity(0))
            if allowed:
                affinity = allowed[0]
        def run():
            if affinity is not None:
                def pin():
                    os.sched_setaffinity(0, {affinity})
                preexec = pin
            else:
                preexec = None
            t = time.perf_counter_ns()
            p = subprocess.run([str(out)], text=True, capture_output=True,
                               check=True, timeout=30, preexec_fn=preexec)
            elapsed = (time.perf_counter_ns() - t) / 1e6
            if p.stdout != EXPECTED:
                raise AssertionError(f"Output mismatch: {p.stdout!r} != {EXPECTED!r}")
            return elapsed
        for _ in range(2):
            run()
        data = sorted(run() for _ in range(9))
        idx = (len(data) - 1) * .1
        lo = int(idx); fraction = idx - lo
        p10 = data[lo] * (1-fraction) + data[min(lo+1,len(data)-1)] * fraction
        print(f"compiler={COMPILER}")
        print(f"affinity={affinity if affinity is not None else 'unavailable'}")
        print(f"min={data[0]:.3f}ms p10={p10:.3f}ms median={statistics.median(data):.3f}ms")
        print(f"spread={(data[-1]/data[0]-1)*100:.1f}% result=PASS")

if __name__ == "__main__":
    main()
