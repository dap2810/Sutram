#!/usr/bin/env python3
"""R44 native acceptance candidates. No output goldens are manufactured here.

Run ONLY after assembling the modified handwritten NASM compiler:
  nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r44.o
  ld -o sutram_compiler /tmp/r44.o
  python3 tools/r44_pending_acceptance.py

A passing candidate is not a replacement for tests/run_tests.py.
"""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "r44_pending"
COMPILER = ROOT / "sutram_compiler"

CASES_SPEC = {
    "01_undefined_export": ("E_EXPORT_UNDEFINED", ("missing", "calc.smlib:2")),
    "02_exported_constant": ("OK", ("64",)),
    "03_unknown_qualified": ("E_EXPORT_UNDEFINED", ("missing", "main.sm:3")),
    "04_private_constant": ("E_MODULE_NOT_EXPORTED", ("SECRET", "main.sm:3")),
    "05_private_function": ("E_MODULE_NOT_EXPORTED", ("helper", "main.sm:3")),
    "06_public_function": ("OK", ("11",)),
    "07_legacy_import": ("OK", ("42",)),
}

def run_one(name, expected_kind, needles, binpath):
    entry = CASES / name / "main.sm"
    result = subprocess.run(
        [str(COMPILER), str(entry), str(binpath)],
        cwd=ROOT, capture_output=True, text=True, timeout=30
    )
    raw = result.stdout + result.stderr
    # Goldens are recorded from an actual GitHub Actions native run
    # (2026-10-09, run 37945627640). Normalize only checkout-directory prefixes,
    # preserving source-relative paths, line numbers, code and punctuation.
    expected_file = CASES / name / "recorded.out"
    expected_code = int((CASES / name / "recorded.exit").read_text().strip())
    expected_stdout = expected_file.read_text()
    assert expected_stdout, f"{name}: recorded.out must not be empty"
    if expected_kind != "OK":
        actual = raw.replace(str(ROOT) + "/", "")
        ok = (result.returncode == expected_code and actual == expected_stdout
              and expected_kind in actual and all(t in actual for t in needles))
        print(f"{'PASS' if ok else 'FAIL'} {name}: compile rc={result.returncode} {actual!r}")
        if not ok:
            print(f"  REAL GOLDEN: rc={expected_code} {expected_stdout!r}")
        return ok
    if result.returncode:
        print(f"FAIL {name}: compiler rc={result.returncode} {raw!r}")
        return False
    program = subprocess.run([str(binpath)], cwd=ROOT,
                             capture_output=True, text=True, timeout=10)
    actual = program.stdout
    ok = (program.returncode == expected_code and actual == expected_stdout
          and actual.strip() == needles[0])
    print(f"{'PASS' if ok else 'FAIL'} {name}: run rc={program.returncode} {actual!r}")
    if not ok:
        print(f"  REAL GOLDEN: rc={expected_code} {expected_stdout!r}")
    return ok

def main():
    if not COMPILER.is_file():
        print("NO NATIVE COMPILER: assemble current src/sutram_compiler.asm first")
        return 2
    passed = 0
    with TemporaryDirectory(prefix="sutram-r44-") as temp:
        for name, (kind, needles) in CASES_SPEC.items():
            if run_one(name, kind, needles, Path(temp) / f"{name}.bin"):
                passed += 1
    print(f"R44 native candidates: {passed}/{len(CASES_SPEC)}")
    return 0 if passed == len(CASES_SPEC) else 1

if __name__ == "__main__":
    sys.exit(main())
