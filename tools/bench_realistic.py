#!/usr/bin/env python3
"""End-to-end representative statistics + Madhava benchmark for Sutram.

Runs a real imported-library numerical program (not a tiny codegen kernel),
checks exact output, measures compiler and executable separately, and reports
min/p10/median. The timings are MACHINE-LOCAL; compare only interleaved A/B
on the SAME machine with identical binary/input and affinity.

Example: python3 tools/bench_realistic.py --runs 25 --warmup 5 --json
SUTRAM_COMPILER=/path/to/binary python3 tools/bench_realistic.py
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import tempfile
import time

from bench_stable import percentile, pin_one_cpu
from shape_profile import profile

ROOT = Path(__file__).resolve().parents[1]
COMPILER = Path(os.environ.get('SUTRAM_COMPILER', ROOT / 'sutram_compiler'))
SOURCE = ROOT / 'examples' / '126_numeric_pipeline.sm'
EXPECTED = '1100000.000000\n11.000000\n5.000000\n3.141593\n'
IMPORTS = [ROOT / 'lib' / 'sankhyiki.smlib', ROOT / 'lib' / 'madhava.smlib']


def measure_command(command: list[str], *, stdout: bool, timeout: int = 20) -> tuple[float, bytes]:
    start = time.perf_counter_ns()
    run = subprocess.run(command, stdout=subprocess.PIPE if stdout else subprocess.DEVNULL,
                         stderr=subprocess.PIPE, timeout=timeout, cwd=ROOT)
    elapsed = (time.perf_counter_ns() - start) / 1_000_000.0
    if run.returncode != 0:
        raise RuntimeError(f'command failed ({run.returncode}): {run.stderr.decode(errors="replace")}')
    return elapsed, run.stdout or b''


def metrics(samples: list[float]) -> dict:
    return {k: round(v, 6) for k, v in {
        'min_ms': min(samples), 'p10_ms': percentile(samples, 0.10),
        'median_ms': statistics.median(samples), 'max_ms': max(samples),
        'spread_pct': (max(samples) - min(samples)) / min(samples) * 100,
    }.items()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runs', type=int, default=25)
    ap.add_argument('--warmup', type=int, default=5)
    ap.add_argument('--compile-runs', type=int, default=5)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--compare-compiler', type=Path, help='Second Sutram compiler; compare byte-for-byte emitted native program')
    args = ap.parse_args()
    if args.runs < 3 or args.warmup < 0 or args.compile_runs < 2:
        ap.error('--runs must be >=3, --compile-runs >=2, --warmup >=0')
    if not COMPILER.is_file():
        ap.error(f'compiler not found: {COMPILER}')

    cpu = pin_one_cpu()
    with tempfile.TemporaryDirectory(prefix='sutram-realistic-') as temp:
        binary = Path(temp) / 'stat_madhava.bin'
        compile_samples = []
        # Each compile overwrites the same destination, producing the same native ELF.
        for _ in range(args.compile_runs):
            elapsed, _ = measure_command([str(COMPILER), str(SOURCE), str(binary)],
                                         stdout=False)
            compile_samples.append(elapsed)
        elapsed, output = measure_command([str(binary)], stdout=True)
        if output.decode('utf-8') != EXPECTED:
            raise RuntimeError(f'output mismatch: {output!r}; expected {EXPECTED!r}')
        for _ in range(args.warmup):
            measure_command([str(binary)], stdout=False)
        runtime_samples = [measure_command([str(binary)], stdout=False)[0]
                           for _ in range(args.runs)]
        binary_size = binary.stat().st_size
        comparison = None
        if args.compare_compiler is not None:
            if not args.compare_compiler.is_file():
                ap.error(f'comparison compiler not found: {args.compare_compiler}')
            other = Path(temp) / 'other-native.bin'
            measure_command([str(args.compare_compiler.resolve()), str(SOURCE), str(other)], stdout=False)
            _, other_output = measure_command([str(other)], stdout=True)
            if other_output.decode('utf-8') != EXPECTED:
                raise RuntimeError(f'comparison compiler output mismatch: {other_output!r}')
            left_data, right_data = binary.read_bytes(), other.read_bytes()
            comparison = {'compiler': str(args.compare_compiler.resolve()),
                          'current_sha256': hashlib.sha256(left_data).hexdigest(),
                          'comparison_sha256': hashlib.sha256(right_data).hexdigest(),
                          'byte_identical': left_data == right_data,
                          'note': 'Identical native binaries imply no code-generation effect for this workload; differing binaries need controlled A/B timing.'}
    source_shapes = profile([SOURCE] + IMPORTS)
    result = {'compiler': str(COMPILER), 'cpu_affinity': cpu,
              'program': str(SOURCE.relative_to(ROOT)),
              'modules': [str(p.relative_to(ROOT)) for p in IMPORTS],
              'compiled_binary_bytes': binary_size, 'expected_output': EXPECTED,
              'compile': metrics(compile_samples), 'run': metrics(runtime_samples),
              'warmup_runs': args.warmup, 'measured_runs': args.runs,
              'shape_census': source_shapes['totals'],
              'compiler_comparison': comparison,
              'scope_note': 'static program + 2 imported modules; excludes transitive imports'}
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f'Compiler: {COMPILER}')
        print(f"Realistic workload: {result['program']} + 2 library modules")
        print(f'Pinned CPU: {cpu if cpu is not None else "not available"}')
        print(f"Output verified: {EXPECTED.strip()!r}; binary {binary_size} bytes")
        print('                                   min ms    p10 ms   median ms  spread')
        for label in ('compile', 'run'):
            r = result[label]
            print(f"{label:32s} {r['min_ms']:8.3f} {r['p10_ms']:9.3f} {r['median_ms']:11.3f} {r['spread_pct']:7.2f}%")
        if comparison is not None:
            print(f"Compiler A/B generated code: {'IDENTICAL' if comparison['byte_identical'] else 'DIFFERENT'}")
            print(f"  current:    {comparison['current_sha256']}")
            print(f"  comparison: {comparison['comparison_sha256']}")
        print('Source census (static, not execution-weighted):')
        for name, value in sorted(source_shapes['totals'].items(), key=lambda x: -x[1])[:12]:
            print(f'  {name}: {value}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
