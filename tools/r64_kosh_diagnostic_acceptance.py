#!/usr/bin/env python3
"""R64 native kosh diagnostic acceptance: needs real NASM-built Sutram compiler.

Use:
    python3 tools/r64_kosh_diagnostic_acceptance.py --compiler ./sutram_compiler
Optional native byte-for-byte old/new default codegen comparison:
    --before /path/tak/pre-r64-compiler

No network, no compiler installation, bounded subprocess timeouts.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "tests" / "r64_check"


def execute(args: list[str], timeout: float = 12) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, timeout=timeout, check=False)


def compile_case(compiler: Path, src: Path, exe: Path) -> None:
    result = execute([str(compiler), str(src), str(exe)])
    assert result.returncode == 0 and exe.is_file(), (
        f"COMPILE FAIL {src.name}: exit={result.returncode} "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_error(compiler: Path, path: Path, stem: str, phrase: bytes) -> None:
    exe = path / stem
    compile_case(compiler, CASES / (stem + ".sm"), exe)
    result = execute([str(exe)])
    assert result.returncode != 0, f"{stem}: expected nonzero exit; got 0"
    assert phrase in result.stdout, f"{stem}: expected {phrase!r}, got {result.stdout!r}"
    all_messages = (
        b"kosh pop from empty array",
        b"kosh peek from empty array",
        b"kosh dequeue from empty array",
    )
    assert sum(msg in result.stdout for msg in all_messages) == 1, (
        f"{stem}: mixed or duplicated error messages: {result.stdout!r}"
    )
    print(f"R64_EMPTY_DIAGNOSTIC_PASS {stem} exit={result.returncode} "
          f"stdout={result.stdout!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--before", default="")
    args = parser.parse_args()
    compiler = Path(args.compiler).resolve()
    before = Path(args.before).resolve() if args.before else None
    if not compiler.is_file():
        parser.error(f"compiler missing: {compiler}")
    if before and not before.is_file():
        parser.error(f"before compiler missing: {before}")
    with tempfile.TemporaryDirectory(prefix="sutram-r64-") as tmp:
        path = Path(tmp)
        for stem, phrase in (
            ("kosh_pop_empty", b"kosh pop from empty array"),
            ("kosh_peek_empty", b"kosh peek from empty array"),
            ("kosh_dequeue_empty", b"kosh dequeue from empty array"),
        ):
            test_error(compiler, path, stem, phrase)
        for stem in ("kosh_nonempty", "default_compat"):
            exe = path / stem
            compile_case(compiler, CASES / (stem + ".sm"), exe)
            result = execute([str(exe)])
            expected = (CASES / (stem + ".out")).read_bytes()
            assert result.returncode == 0 and result.stdout == expected, (
                f"{stem}: exit={result.returncode}, "
                f"expected={expected!r} actual={result.stdout!r}")
            print(f"R64_EXACT_STDOUT_PASS {stem} bytes={len(expected)}")
        if before:
            oldexe = path / "old-default-compat"
            compile_case(before, CASES / "default_compat.sm", oldexe)
            newexe = path / "default_compat"
            assert oldexe.read_bytes() == newexe.read_bytes(), (
                "Default non-kosh codegen changed! Do NOT rewrite accepted goldens."
            )
            print(f"R64_DEFAULT_BINARY_IDENTICAL_PASS bytes={newexe.stat().st_size}")
        else:
            print("R64_AB_CODEGEN_NOT_RUN (pass --before tak compare)")
    print("R64_KOSH_DIAGNOSTICS_ACCEPTED (native evidence only when actually run)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
