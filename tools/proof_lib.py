#!/usr/bin/env python3
"""Sutram standard-library proof harness.

Compiles and runs every test in tests/stdlib/, comparing stdout and exit
code against golden .out / .exit files. Goldens are recorded from actual
runs -- never hand-written or predicted.

Usage: python3 tools/proof_lib.py [--record] [--compiler PATH]
  --record    (re)generate goldens from actual runs instead of checking
  --compiler  path to sutram_compiler binary (default: build it)

Exit code: 0 if all tests pass, 1 otherwise.
Failure output names the module, function, expected value and actual value.
"""

import os
import subprocess
import sys
import shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTDIR = os.path.join(REPO, "tests", "stdlib")
BUILDDIR = os.path.join(REPO, "build")
COMPILER_SRC = os.path.join(REPO, "src", "sutram_compiler.asm")


def build_compiler():
    """Build sutram_compiler with nasm if missing or stale. Returns path."""
    out = os.path.join(BUILDDIR, "sutram_compiler")
    obj = os.path.join(BUILDDIR, "sutram.o")
    src_mtime = os.path.getmtime(COMPILER_SRC)
    if os.path.exists(out) and os.path.getmtime(out) >= src_mtime:
        return out
    os.makedirs(BUILDDIR, exist_ok=True)
    nasm = shutil.which("nasm")
    if not nasm:
        # try the local build-tools copy
        cand = os.path.expanduser("~/workspace/build-tools/nasm-inst/bin/nasm")
        if os.path.exists(cand):
            nasm = cand
    if not nasm:
        sys.exit("FAIL: nasm not found; cannot build the compiler")
    # win/rtblob.inc is a release artifact; provide an empty stub for the
    # Linux build if it is absent (the ELF path never uses it).
    win_inc = os.path.join(REPO, "win", "rtblob.inc")
    stub_created = False
    if not os.path.exists(win_inc):
        os.makedirs(os.path.join(REPO, "win"), exist_ok=True)
        with open(win_inc, "w") as f:
            f.write("; test-only stub\nRT_BLOB_LEN equ 0\nRT_BUF_CAP equ 0\n"
                    "RT_NAMES_CAP equ 0\nRT_SYSCALL_OFF equ 0\nrt_blob: db 0\n")
        stub_created = True
    try:
        r = subprocess.run([nasm, "-f", "elf64", COMPILER_SRC, "-o", obj],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"FAIL: nasm failed:\n{r.stderr}")
        r = subprocess.run(["ld", "-o", out, obj],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"FAIL: ld failed:\n{r.stderr}")
    finally:
        if stub_created:
            os.remove(win_inc)
            try:
                os.rmdir(os.path.join(REPO, "win"))
            except OSError:
                pass
    return out


def run_test(compiler, sm_path):
    """Compile and run one .sm test. Returns (ok, stdout, exitcode, err)."""
    bin_path = sm_path + ".bin"
    r = subprocess.run([compiler, sm_path, bin_path],
                       capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        return False, "", r.returncode, f"compile failed: {r.stderr.strip()}"
    # lib/ resolution: run with cwd=REPO so ayojan finds lib/
    r = subprocess.run([bin_path], capture_output=True, text=True, cwd=REPO,
                       timeout=10)
    try:
        os.remove(bin_path)
    except OSError:
        pass
    return True, r.stdout, r.returncode, r.stderr


def main():
    record = "--record" in sys.argv
    compiler = None
    for i, a in enumerate(sys.argv):
        if a == "--compiler" and i + 1 < len(sys.argv):
            compiler = sys.argv[i + 1]
    if not compiler:
        compiler = build_compiler()

    if not os.path.isdir(TESTDIR):
        sys.exit(f"FAIL: test directory missing: {TESTDIR}")

    tests = sorted(f for f in os.listdir(TESTDIR) if f.endswith(".sm"))
    if not tests:
        sys.exit("FAIL: no tests found in tests/stdlib/")

    passed, failed = 0, []
    for t in tests:
        name = t[:-3]  # module_function
        sm = os.path.join(TESTDIR, t)
        out_golden = os.path.join(TESTDIR, name + ".out")
        exit_golden = os.path.join(TESTDIR, name + ".exit")

        ok, stdout, exitcode, err = run_test(compiler, sm)
        if not ok:
            failed.append(f"{name}: {err}")
            continue

        if record:
            with open(out_golden, "w") as f:
                f.write(stdout)
            with open(exit_golden, "w") as f:
                f.write(str(exitcode) + "\n")
            passed += 1
            continue

        # check mode
        problems = []
        if os.path.exists(out_golden):
            with open(out_golden) as f:
                expected_out = f.read()
            if stdout != expected_out:
                problems.append(
                    f"stdout mismatch:\n  expected: {expected_out!r}\n"
                    f"  actual:   {stdout!r}")
        else:
            problems.append("missing golden .out (run with --record)")

        if os.path.exists(exit_golden):
            with open(exit_golden) as f:
                expected_exit = int(f.read().strip())
            if exitcode != expected_exit:
                problems.append(
                    f"exit code mismatch: expected {expected_exit}, "
                    f"actual {exitcode}")
        else:
            problems.append("missing golden .exit (run with --record)")

        if problems:
            # name the module/function from the test name
            failed.append(f"{name}:\n  " + "\n  ".join(problems))
        else:
            passed += 1

    print(f"\n{passed} passed, {len(failed)} failed, {len(tests)} total")
    for f in failed:
        print(f"FAIL {f}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
