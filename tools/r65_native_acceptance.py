#!/usr/bin/env python3
"""R65 native acceptance for Sarvam. NEVER substitutes static checks for execution.
Build three compilers first:
  nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r65-default.o
  ld -o /tmp/r65-default /tmp/r65-default.o
  nasm -DSUTRAM_R65_PEEPHOLES=1 -f elf64 -I. src/sutram_compiler.asm -o /tmp/r65-opt.o
  ld -o /tmp/r65-opt /tmp/r65-opt.o
  nasm -DSUTRAM_R65_TRAP_INT=1 -f elf64 -I. src/sutram_compiler.asm -o /tmp/r65-trap.o
  ld -o /tmp/r65-trap /tmp/r65-trap.o

Run: python3 tools/r65_native_acceptance.py --default /tmp/r65-default --peephole /tmp/r65-opt --trap /tmp/r65-trap
Optional --reference accepted-parent-default-compiler for default-mode machine-code identity.
"""
from __future__ import annotations
import argparse
import pathlib
import re
import subprocess
import tempfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
F = ROOT / "tests" / "r65_check"
SRC_DEV = ROOT / "examples" / "219_sanskrit_kosh_aliases.sm"

def execute(cmd, timeout=12):
    return subprocess.run([str(x) for x in cmd], cwd=ROOT,
                          capture_output=True, timeout=timeout, check=False)

def build(compiler, src, exe, lang=None):
    cmd = [compiler, src, exe]
    if lang:
        cmd = [compiler, "--lang", lang, src, exe]
    result = execute(cmd)
    assert result.returncode == 0 and exe.is_file(), (
        f"COMPILE_FAIL {src} code={result.returncode} "
        f"out={result.stdout!r} err={result.stderr!r}")
    return exe

def check_output(compiler, src, expected, exe, lang=None):
    build(compiler, src, exe, lang=lang)
    result = execute([exe])
    assert result.returncode == 0 and result.stdout == expected, (
        f"NATIVE_OUTPUT_FAIL {src}: code={result.returncode} "
        f"expected={expected!r}, actual={result.stdout!r}, stderr={result.stderr!r}")
    print(f"R65_NATIVE_STDOUT_PASS {src.name} bytes={len(expected)}")
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--default", required=True)
    p.add_argument("--peephole", required=True)
    p.add_argument("--trap", required=True)
    p.add_argument("--reference", default="")
    a = p.parse_args()
    compilers = {k: pathlib.Path(getattr(a, k)).resolve()
                 for k in ("default", "peephole", "trap")}
    for name, path in compilers.items():
        assert path.is_file(), f"missing {name} compiler: {path}"
    with tempfile.TemporaryDirectory(prefix="sutram-r65-") as temp:
        work = pathlib.Path(temp)
        src = F / "peephole_scalar.sm"
        exp = (F / "peephole_scalar.out").read_bytes()
        oldbin = work / "default-peephole"
        optbin = work / "optimized-peephole"
        check_output(compilers["default"], src, exp, oldbin)
        check_output(compilers["peephole"], src, exp, optbin)
        assert oldbin.read_bytes() != optbin.read_bytes(), (
            "PEEPHOLE_NOT_TRIGGERED: output binaries identical")
        print(f"R65_PEEPHOLE_DIFFERENT_CODE_PASS before={oldbin.stat().st_size} "
              f"after={optbin.stat().st_size}")
        if a.reference:
            prev = pathlib.Path(a.reference).resolve()
            old = work / "pre-r65-default"
            cur = work / "r65-default"
            build(prev, F / "overflow_safe.sm", old)
            build(compilers["default"], F / "overflow_safe.sm", cur)
            assert old.read_bytes() == cur.read_bytes(), "DEFAULT_CODEGEN_REGRESSION"
            print(f"R65_DEFAULT_BINARY_IDENTITY_PASS bytes={cur.stat().st_size}")
        else:
            print("R65_DEFAULT_AB_NOT_RUN (supply --reference)")
        safe = F / "overflow_safe.sm"
        safe_exp = (F / "overflow_safe.out").read_bytes()
        check_output(compilers["default"], safe, safe_exp, work / "safe-default")
        check_output(compilers["trap"], safe, safe_exp, work / "safe-trap")
        errors = {"trap_add": "addition overflow",
                  "trap_sub": "subtraction overflow",
                  "trap_mul": "multiplication overflow",
                  "trap_div": "shunya se bhajan",
                  "trap_mod": "shunya se shesh"}
        for stem, description in errors.items():
            path = F / (stem + ".sm")
            exe = work / stem
            build(compilers["trap"], path, exe)
            result = execute([exe])
            assert result.returncode != 0, f"{stem} unexpectedly succeeded"
            output = result.stdout.decode("utf-8", errors="replace")
            # Exact diagnostic wording uses 'signed addition' etc.
            op_fragment = {
                "trap_add": "yog atipravah",
                "trap_sub": "nyun atipravah",
                "trap_mul": "gun atipravah",
                "trap_div": "shunya se bhajan",
                "trap_mod": "shunya se shesh",
            }[stem]
            assert ("E_INTEGER_TRAP" in output and op_fragment in output
                    and re.search(r":[1-9][0-9]*:", output)), (
                    f"{stem} missing source:line and operation: {output!r}")
            print(f"R65_TRAP_PASS {stem} exit={result.returncode} {output!r}")
        check_output(compilers["default"], SRC_DEV,
                     (F / "sanskrit_kosh_aliases.out").read_bytes(),
                     work / "sanskrit-kosh", lang="sanskrit")
    print("R65_NATIVE_ACCEPTANCE_PASS (only genuine run counts)")
if __name__ == "__main__":
    main()
