#!/usr/bin/env python3
"""R63 native kosh A/B acceptance. Requires a built native Sutram compiler.

Run: python3 tools/r63_kosh_acceptance.py --compiler ./sutram_compiler
Optional: --before ./pre_r63_sutram_compiler
No implicit online operations or package installation; bounded processes only.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "r63_check"


def run(argv: list[str], timeout: float = 12.0) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout, check=False)


def compile_program(compiler: Path, src: Path, dest: Path) -> subprocess.CompletedProcess[bytes]:
    return run([str(compiler), str(src), str(dest)])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--before", default="")
    args = parser.parse_args()
    compiler = Path(args.compiler).resolve()
    before = Path(args.before).resolve() if args.before else None
    if not compiler.is_file():
        parser.error(f"compiler not found: {compiler}")
    if before and not before.is_file():
        parser.error(f"before compiler not found: {before}")

    passed = 0
    with tempfile.TemporaryDirectory(prefix="sutram-r63-") as temporary:
        folder = Path(temporary)
        for case in ("kosh_native_core", "kosh_native_float"):
            src = CASES / (case + ".sm")
            expect = (CASES / (case + ".out")).read_bytes()
            exe = folder / case
            compiled = compile_program(compiler, src, exe)
            assert compiled.returncode == 0 and exe.exists(), (
                f"{case} COMPILE_FAIL: {compiled.stdout!r} {compiled.stderr!r}"
            )
            completed = run([str(exe)])
            assert completed.returncode == 0, f"{case} native exit {completed.returncode}"
            assert completed.stdout == expect, (
                f"{case} stdout mismatch\nexpected={expect!r}\nobserved={completed.stdout!r}"
            )
            print(f"R63_NATIVE_STDOUT_PASS {case} exit=0 bytes={len(completed.stdout)}")
            passed += 1
            if before:
                oldexe = folder / (case + ".pre")
                old_compile = compile_program(before, src, oldexe)
                assert old_compile.returncode != 0, (
                    f"{case} unexpectedly compiled under old compiler: missing negative A/B evidence"
                )
                print(f"R63_BEFORE_REJECTED {case} compiler_exit={old_compile.returncode}")
                passed += 1
        for case in ("kosh_invalid_non_kosh", "kosh_invalid_arity"):
            src = CASES / (case + ".sm")
            compiled = compile_program(compiler, src, folder / case)
            assert compiled.returncode != 0, (
                f"{case} accepted incorrectly: {compiled.stdout!r} {compiled.stderr!r}"
            )
            print(f"R63_EXPECTED_COMPILE_ERROR_PASS {case} code={compiled.returncode}")
            passed += 1
        src = CASES / "kosh_peek_empty.sm"
        exe = folder / "kosh_peek_empty"
        compiled = compile_program(compiler, src, exe)
        assert compiled.returncode == 0 and exe.exists(), (
            f"peek empty compile failed unexpectedly: {compiled.stdout!r} {compiled.stderr!r}"
        )
        completed = run([str(exe)])
        assert completed.returncode != 0, "peeking empty kosh did not terminate with error"
        assert b"kosh pop from empty array" in completed.stdout, (
            f"missing inherited empty kosh diagnostic: {completed.stdout!r}"
        )
        print(f"R63_EMPTY_PEEK_TRAP_PASS runtime_exit={completed.returncode}")
        passed += 1
    print(f"R63_NATIVE_ACCEPTED {passed} gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
