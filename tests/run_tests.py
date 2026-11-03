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


def ensure_executable(path):
    """R13: the committed sutram_compiler must be mode 100755. A checkout that lost the
    mode (a merge that uploads files one by one does that) used to stop the suite with
    PermissionError; say so, and set the bit on this working copy."""
    if os.path.isfile(path) and not os.access(path, os.X_OK):
        os.chmod(path, os.stat(path).st_mode | 0o111)
        print(f"NOTE: {os.path.relpath(path, ROOT)} was not executable; set +x on this copy. "
              "The committed mode should be 100755 (git update-index --chmod=+x).")


ensure_executable(COMPILER)
EXAMPLES = os.path.join(ROOT, "examples")
EXPECT = os.path.join(ROOT, "tests", "expect")
# R101: SUTRAM_TEST_TIMEOUT lets tools/guard_page.py give its build more time: with no arena, every
# nirmmita there is its own mmap and a block cannot rewind, so 268_r73_return_value (1,000,000 calls)
# takes about 5 s and 4 GB - exactly the old 5-second limit, which is why that gate failed now and then.
TIMEOUT = int(os.environ.get('SUTRAM_TEST_TIMEOUT', '5'))

# examples that need a language pack
LANG = {
    "37_native_gujarati": "gujarati",
    "38_native_hindi": "hindi",
    "39_native_tamil": "tamil",
    "218_sanskrit_devanagari": "sanskrit",
    "219_sanskrit_kosh_aliases": "sanskrit",
    "220_hindi_parse_error": "hindi",     # R2-WS1a: localized diagnostic bytes
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


def norm(s):
    """Make compiler output checkout-independent: the compiler echoes the
    source path it was given, so goldens would otherwise embed an absolute
    path and fail in any other checkout."""
    return s.replace(ROOT, "<ROOT>")


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
            open(exp_out, "w").write(norm(stdout))
            open(exp_exit, "w").write(str(code))
            return ("RECORDED", stdout, code, None)
        if not os.path.exists(exp_out) or not os.path.exists(exp_exit):
            return ("NO-EXPECTATION", stdout, code, None)
        want_out = open(exp_out).read()
        want_code = open(exp_exit).read().strip()
        if norm(stdout) == want_out and str(code) == want_code:
            return ("PASS", stdout, code, None)
        return ("FAIL", stdout, code, f"expected compile exit {want_code}, got {code}\n"
                                      f"--- expected compiler output ---\n{want_out}\n"
                                      f"--- actual compiler output ---\n{stdout}")
    if expect_compile_fail:
        return ("FAIL", c.stdout + c.stderr, c.returncode, "expected compilation to fail, but it succeeded")

    try:
        r = subprocess.run([out_bin], input=STDIN.get(name, ""), capture_output=True,
                           text=True, timeout=TIMEOUT)
        stdout, code, stderr = r.stdout, r.returncode, r.stderr
    except subprocess.TimeoutExpired:
        stdout, code, stderr = "", "TIMEOUT", ""

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
    # R116: a program that stops with a run-time diagnostic records it in <name>.err (stderr); when the
    # file exists it must match too. Without it stderr is not checked, as before.
    exp_err = os.path.join(EXPECT, name + ".err")
    if os.path.exists(exp_err) and stderr != open(exp_err).read():
        return ("FAIL", stdout, code, f"expected stderr\n{open(exp_err).read()}\n--- actual stderr ---\n{stderr}")
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
    # R101A: SUTRAM_TEST_SKIP names examples a special build cannot run as the shipped one does -
    # tools/guard_page.py's build has no kosh regions, so example 288 (two names stay one) differs there.
    skip = [n for n in os.environ.get('SUTRAM_TEST_SKIP', '').split(',') if n]
    names = [n for n in names if n not in skip]
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
    # R109 (WS3): the details first, the summary LAST - it used to be printed first, so the run ended
    # with a no-expectation program's raw output ("1 7 7 1"), which read as if it were the result.
    # A program's output is indented and labelled, never left bare; the gates read the last line only.
    for n, status, detail in failures:
        if status == "NO-EXPECTATION":
            lines = (detail or "").splitlines()
            print(f"--- {n}: NO-EXPECTATION - no golden, not counted as passing; "
                  f"its output ({len(lines)} line(s)) is not checked:")
            for l in lines[:5]:
                print(f"    | {l}")
            if len(lines) > 5:
                print(f"    | ... {len(lines) - 5} more")
        else:
            print(f"--- {n}: {status}")
            for l in (detail or "").splitlines():
                print(f"    | {l}")
    print()
    print("suite: " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items()))
          + f"  ({len(names)} run)")
    bad = counts.get("FAIL", 0) + counts.get("COMPILE-FAIL", 0) + counts.get("NO-EXPECTATION", 0)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
