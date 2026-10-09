#!/usr/bin/env python3
"""Sutram golden-file test harness.

For every examples/*.sm it compiles, runs, and compares stdout + exit code
against recorded expectations in tests/expect/<name>.out and .exit.

  python3 tests/run_tests.py            run the suite
  python3 tests/run_tests.py --record   (re)record expectations
  python3 tests/run_tests.py --list     list the tests
  python3 tests/run_tests.py NAME...    run only the named tests

Examples that need language packs or stdin are declared below.
"""
import os, subprocess, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPILER = os.environ.get("SUTRAM_COMPILER") or os.path.join(ROOT, "sutram_compiler")
EXAMPLES = os.path.join(ROOT, "examples")
EXPECT = os.path.join(ROOT, "tests", "expect")
TIMEOUT = 5

# examples that need a language pack
LANG = {
    "37_native_gujarati": "gujarati",
    "38_native_hindi": "hindi",
    "39_native_tamil": "tamil",
}
# examples that read from stdin (fed exactly this)
STDIN = {
    "23_grahan_input": "5\n",
    "24_guess_game": "7\n",
    "26_calculator": "20\n4\n",
    "number_game": "3\n",
    "46_language_reference": "7\n",
    "59_windows_grahan_runtime": "42\n",
}
# examples whose exit code is intentionally non-zero
EXIT_OVERRIDE = {
    "29_nishkriya": 42,   # nishkriya() inline asm exits 42 on purpose
}

# examples that must compile from a non-project working directory
CWD = {
    "79_ayojan_cwd": "/tmp",
}


def tests():
    return sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(EXAMPLES, "*.sm")))


def run_one(name, record=False):
    src = os.path.join(EXAMPLES, name + ".sm")
    out_bin = f"/tmp/sutram_test_{name}.bin"
    cmd = [COMPILER]
    if name in LANG:
        cmd += ["--lang", LANG[name]]
    cmd += [src, out_bin]

    c = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                       cwd=CWD.get(name, ROOT))
    compile_fail_marker = os.path.join(EXPECT, name + ".compile_fail")
    expect_compile_fail = os.path.exists(compile_fail_marker)
    if c.returncode != 0:
        if not expect_compile_fail:
            return ("COMPILE-FAIL", c.stdout + c.stderr, c.returncode, None)
        stdout, code = c.stdout + c.stderr, c.returncode
        exp_out = os.path.join(EXPECT, name + ".out")
        exp_exit = os.path.join(EXPECT, name + ".exit")
        if record:
            os.makedirs(EXPECT, exist_ok=True)
            open(exp_out, "w").write(stdout)
            open(exp_exit, "w").write(str(code))
            return ("RECORDED", stdout, code, None)
        if not os.path.exists(exp_out) or not os.path.exists(exp_exit):
            return ("NO-EXPECTATION", stdout, code, None)
        want_out = open(exp_out).read()
        want_code = open(exp_exit).read().strip()
        if stdout == want_out and str(code) == want_code:
            return ("PASS", stdout, code, None)
        return ("FAIL", stdout, code, f"expected compile exit {want_code}, got {code}\n"
                                      f"--- expected compiler output ---\n{want_out}\n"
                                      f"--- actual compiler output ---\n{stdout}")
    if expect_compile_fail:
        return ("FAIL", c.stdout + c.stderr, c.returncode, "expected compilation to fail, but it succeeded")

    try:
        r = subprocess.run([out_bin], input=STDIN.get(name, ""), capture_output=True,
                           text=True, timeout=TIMEOUT)
        stdout, code = r.stdout, r.returncode
    except subprocess.TimeoutExpired:
        stdout, code = "", "TIMEOUT"

    exp_out = os.path.join(EXPECT, name + ".out")
    exp_exit = os.path.join(EXPECT, name + ".exit")

    if record:
        os.makedirs(EXPECT, exist_ok=True)
        open(exp_out, "w").write(stdout)
        open(exp_exit, "w").write(str(code))
        return ("RECORDED", stdout, code, None)

    if not os.path.exists(exp_out) or not os.path.exists(exp_exit):
        return ("NO-EXPECTATION", stdout, code, None)
    want_out = open(exp_out).read()
    want_code = open(exp_exit).read().strip()
    if stdout == want_out and str(code) == want_code:
        return ("PASS", stdout, code, None)
    return ("FAIL", stdout, code, f"expected exit {want_code}, got {code}\n"
                                  f"--- expected stdout ---\n{want_out}\n"
                                  f"--- actual stdout ---\n{stdout}")


def main():
    args = sys.argv[1:]
    record = "--record" in args
    args = [a for a in args if not a.startswith("--")]
    names = args or tests()
    if "--list" in sys.argv:
        print("\n".join(names)); return 0

    counts = {}
    failures = []
    for n in names:
        status, out, code, detail = run_one(n, record)
        counts[status] = counts.get(status, 0) + 1
        mark = {"PASS": ".", "RECORDED": "r", "FAIL": "F",
                "COMPILE-FAIL": "C", "NO-EXPECTATION": "?", "TIMEOUT": "T"}.get(status, "?")
        sys.stdout.write(mark); sys.stdout.flush()
        if status in ("FAIL", "COMPILE-FAIL", "NO-EXPECTATION"):
            failures.append((n, status, detail or out))
    print()
    print("  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    for n, status, detail in failures:
        print(f"\n--- {n}: {status}\n{detail}")
    bad = counts.get("FAIL", 0) + counts.get("COMPILE-FAIL", 0) + counts.get("NO-EXPECTATION", 0)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
