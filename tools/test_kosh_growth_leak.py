#!/usr/bin/env python3
"""Diagnose the kosh growth leak (R29 WS2).

The compiler's kosh_push growth path (src/sutram_compiler.asm,
.ge_call_koshpush) allocates a new buffer with nirmmita (mmap),
copies the old cells, and stores the new pointer. It never releases
(munmap) the old buffer, and the language has no free primitive, so
repeated growth retains every superseded buffer. Peak heap is ~2x
the live buffer: the pravan of peak RSS vs pushed items is ~16
bytes/item instead of ~8.

This script measures that pravan: it compiles a program that pushes
N items into a kosh, runs it as a child, and reads the child's peak
RSS (ru_maxrss). It asserts the pravan is below 12 bytes/item — the
leaky pravan (~15.6) fails, a fixed compiler (~8) passes.

This is a diagnostic, not a suite gate: RSS is machine-dependent,
so it lives here rather than in tools/proof_lib.py. It is expected
tak FAIL until the compiler-side fix lands (munmap the old buffer
in the growth path, src/ work).

Usage: python3 tools/test_kosh_growth_leak.py
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER = os.path.join(REPO, "build", "sutram_compiler")
N = 8_000_000
SLOPE_LIMIT = 12.0  # bytes/item; leaky ~= 15.6, fixed ~= 8


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


def measure(n):
    src = ("mukhya() {\n"
           "    kosh v[4]\n"
           "    vitti i = 0\n"
           f"    yavat (i < {n}) {{\n"
           "        kosh_push(v, i)\n"
           "        i = i + 1\n"
           "    }\n"
           "    likha(kosh_len(v))\n"
           '    likha("\\n")\n'
           "}\n")
    sm = "/tmp/kosh_leak_probe.sm"
    binary = "/tmp/kosh_leak_probe.bin"
    open(sm, "w").write(src)
    r = subprocess.run([COMPILER, sm, binary], capture_output=True, text=True)
    assert "OK" in r.stdout, f"compile failed: {r.stdout}"
    return child_rss(binary) / 1024.0  # MB


def main():
    base = measure(0)
    peak = measure(N)
    pravan = (peak - base) * 1024 * 1024 / N
    print(f"baseline peak RSS: {base:.1f} MB")
    print(f"peak RSS after {N} pushes: {peak:.1f} MB")
    print(f"pravan: {pravan:.2f} bytes/item (limit {SLOPE_LIMIT})")
    if pravan >= SLOPE_LIMIT:
        print("FAIL: kosh growth leak present — old buffers are retained")
        print("  (growth path mmaps a new buffer without releasing the old)")
        return 1
    print("PASS: kosh growth reclaims old buffers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
