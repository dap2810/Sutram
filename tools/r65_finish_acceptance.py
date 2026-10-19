#!/usr/bin/env python3
"""Native finishing gates for Sarvam's staged R65 compiler. Never builds or installs.

Supply separately built --default, --peephole, --trap compilers. Optional
--combined and --reference cover both flags and prior-default byte identity.
A signal/timeout is a failure, not a successfully caught arithmetic error.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

POSITIVE = {
    "statement_and_expression_args": ('''prakriya identity(x) { prati x }
prakriya show(x) { likha(x) prati x }
prakriya pair(a,b) { likha(a + b) prati a + b }
mukhya() {
    show(identity(7))
    pair(identity(3), identity(4))
    likha(identity(identity(9)))
}
''', b"7\n7\n9\n"),
    "safe_constants_and_strings": ('''sutra c = 2 * 3
mukhya() { likha(c) likha("a" + "b") }
''', b"6\nab"),
    "ordinary_arithmetic": ('''mukhya() {
    vitti a = 9
    vitti b = 3
    likha(a + b) likha(a - b) likha(a * b)
    likha(a / b) likha(a % b)
}
''', b"12\n6\n27\n3\n0\n"),
}
TRAPS = {
    "add_line4": ('''mukhya() {
    vitti a = 9223372036854775807
    vitti b = 1
    likha(a + b)
}
''', 4, "yog atipravah"),
    "multiline_line6": ('''mukhya() {
    vitti a = 9223372036854775807
    vitti b = 1
    likha(
        a
        + b)
}
''', 6, "yog atipravah"),
    "div_zero_line4": ('''mukhya() {
    vitti a = 7
    vitti b = 0
    likha(a / b)
}
''', 4, "shunya se bhajan"),
    "div_min_line4": ('''mukhya() {
    vitti a = -9223372036854775807
    a = a - 1
    likha(a / -1)
}
''', 4, "bhajan atipravah"),
    "mod_min_line4": ('''mukhya() {
    vitti a = -9223372036854775807
    a = a - 1
    likha(a % -1)
}
''', 4, "shesh atipravah"),
}


def run(argv: list[str | Path]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([str(x) for x in argv], cwd=ROOT, capture_output=True,
                          timeout=12, check=False)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def compile_program(compiler: Path, source: Path, output: Path) -> None:
    result = run([compiler, source, output])
    require(result.returncode == 0 and output.is_file(),
            f"compile {source.name}: exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("default", "peephole", "trap"):
        parser.add_argument("--" + key, required=True, type=Path)
    for key in ("combined", "reference"):
        parser.add_argument("--" + key, type=Path)
    args = parser.parse_args()
    modes = {key: getattr(args, key).resolve() for key in
             ("default", "peephole", "trap", "combined") if getattr(args, key)}
    reference = args.reference.resolve() if args.reference else None
    for path in list(modes.values()) + ([reference] if reference else []):
        require(path.is_file(), f"compiler is missing: {path}")
    observations = []
    with tempfile.TemporaryDirectory(prefix="sutram-r65-finish-") as tmp:
        work = Path(tmp)
        for name, (program, expected) in POSITIVE.items():
            src = work / (name + ".sm")
            src.write_text(program, encoding="utf-8")
            for mode, compiler in modes.items():
                exe = work / (name + "-" + mode)
                compile_program(compiler, src, exe)
                result = run([exe])
                require(result.returncode == 0 and result.stdout == expected,
                        f"positive {mode}/{name}: exit={result.returncode}, stdout={result.stdout!r}, expected={expected!r}")
                observations.append({"gate": name, "mode": mode, "exit": 0,
                                     "stdout_hex": result.stdout.hex()})
            if reference:
                prior = work / (name + "-reference")
                compile_program(reference, src, prior)
                current = work / (name + "-default")
                require(prior.read_bytes() == current.read_bytes(), f"default binary changed: {name}")
                observations.append({"gate": name + "_default_binary_identity", "bytes": current.stat().st_size})
        for name, (program, line, phrase) in TRAPS.items():
            src = work / (name + ".sm")
            src.write_text(program, encoding="utf-8")
            for mode in ("trap", "combined"):
                if mode not in modes:
                    continue
                exe = work / (name + "-" + mode)
                compile_program(modes[mode], src, exe)
                result = run([exe])
                text = result.stdout.decode("utf-8", errors="strict")
                require(result.returncode == 1, f"{name}: expected explicit exit 1, got {result.returncode}; {text!r}")
                require("E_INTEGER_TRAP" in text and phrase in text and
                        str(src) + f":{line}:" in text,
                        f"{mode}/{name}: incorrect full filename/operator line/operation: {text!r}")
                observations.append({"gate": name, "mode": mode, "exit": 1, "stdout": text})
        # Exact UTF-8 path, longer than the old 95-byte truncation and rel8 limit.
        folder = work / ("long-path-" * 10) / ("unicode-" * 7 + "संस्कृत")
        folder.mkdir(parents=True)
        src = folder / "overflow.sm"
        program, line, phrase = TRAPS["add_line4"]
        src.write_text(program, encoding="utf-8")
        exe = work / "long-path-trap"
        compile_program(modes["trap"], src, exe)
        result = run([exe])
        text = result.stdout.decode("utf-8", errors="strict")
        require(result.returncode == 1 and str(src) + f":{line}:" in text and phrase in text,
                f"long-path diagnostic failure: exit={result.returncode}, output={text!r}")
        observations.append({"gate": "long_utf8_filename", "stdout": text, "exit": 1})
    print(json.dumps({"status": "R65_FINISH_NATIVE_PASS", "observations": observations,
                      "prior_default_comparison": "RUN" if reference else "NOT_RUN"},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
