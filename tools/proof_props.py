#!/usr/bin/env python3
"""Sutram library property tests — invariants over deterministic inputs.

Unlike proof_lib.py (fixed golden outputs), this checks PROPERTIES:
invariants that must hold for many inputs. Uses a fixed seed so runs are
deterministic. Fails on the first counterexample, printing the input.

Each property generates a .sm program that checks the invariant over N
cases and prints PASS or FAIL with the counterexample. This script compiles,
runs, and reports.

Usage: python3 tools/proof_props.py [--compiler PATH]
Exit code: 0 if all properties hold, 1 otherwise.
"""

import os
import random
import subprocess
import sys
import shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDDIR = os.path.join(REPO, "build")
COMPILER_SRC = os.path.join(REPO, "src", "sutram_compiler.asm")
SEED = 20261009
N_CASES = 15


def build_compiler(compiler=None):
    if compiler:
        return compiler
    out = os.path.join(BUILDDIR, "sutram_compiler")
    if os.path.exists(out):
        return out
    # Build it (same logic as proof_lib.py)
    obj = os.path.join(BUILDDIR, "sutram.o")
    os.makedirs(BUILDDIR, exist_ok=True)
    nasm = shutil.which("nasm") or os.path.expanduser(
        "~/workspace/build-tools/nasm-inst/bin/nasm")
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


def run_sm(compiler, name, code):
    """Write, compile, run a .sm program. Returns (ok, stdout)."""
    sm_path = os.path.join("/tmp", f"prop_{name}.sm")
    bin_path = sm_path + ".bin"
    with open(sm_path, "w") as f:
        f.write(code)
    r = subprocess.run([compiler, sm_path, bin_path],
                       capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        return False, f"compile failed: {r.stderr.strip()}"
    r = subprocess.run([bin_path], capture_output=True, text=True,
                       cwd=REPO, timeout=30)
    try:
        os.remove(bin_path)
        os.remove(sm_path)
    except OSError:
        pass
    if r.returncode != 0:
        return False, f"runtime exit {r.returncode}: {r.stderr.strip()}"
    return True, r.stdout.strip()


def prop_bigint_add_sub(compiler, rng):
    """add(a,b) then sub(result,a) == b"""
    cases = []
    for _ in range(N_CASES):
        a = rng.randint(0, 999999)
        b = rng.randint(0, 999999)
        cases.append((a, b))
    lines = ["ayojan bigint", "mukhya() {",
             "    vitti a = nirmmita(8*8)", "    vitti b = nirmmita(8*8)",
             "    vitti r = nirmmita(8*8)", "    vitti s = nirmmita(8*8)"]
    for a, b in cases:
        lines.append(f"    bigint_from_int({a}, a, 8)")
        lines.append(f"    bigint_from_int({b}, b, 8)")
        lines.append(f"    bigint_add(a, b, r, 8)")
        lines.append(f"    bigint_sub(r, a, s, 8)")
        lines.append(f"    yadi (bigint_cmp(s, b, 8) != 0) {{")
        lines.append(f'        likha("FAIL add_sub {a} {b}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "add_sub", "\n".join(lines))
    return ok and out == "PASS", out


def prop_bigint_mul_distrib(compiler, rng):
    """mul distributes over add: a*(b+c) == a*b + a*c"""
    cases = []
    for _ in range(N_CASES):
        a = rng.randint(0, 999)
        b = rng.randint(0, 999)
        c = rng.randint(0, 999)
        cases.append((a, b, c))
    lines = ["ayojan bigint", "mukhya() {",
             "    vitti a = nirmmita(8*8)", "    vitti b = nirmmita(8*8)",
             "    vitti c = nirmmita(8*8)", "    vitti bc = nirmmita(8*8)",
             "    vitti lhs = nirmmita(16*8)", "    vitti ab = nirmmita(16*8)",
             "    vitti ac = nirmmita(16*8)", "    vitti rhs = nirmmita(16*8)"]
    for a, b, c in cases:
        lines.append(f"    bigint_from_int({a}, a, 8)")
        lines.append(f"    bigint_from_int({b}, b, 8)")
        lines.append(f"    bigint_from_int({c}, c, 8)")
        lines.append(f"    bigint_add(b, c, bc, 8)")
        lines.append(f"    bigint_mul(a, bc, lhs, 8)")
        lines.append(f"    bigint_mul(a, b, ab, 8)")
        lines.append(f"    bigint_mul(a, c, ac, 8)")
        # rhs = ab + ac (16-digit add)
        lines.append(f"    bigint_add(ab, ac, rhs, 16)")
        lines.append(f"    yadi (bigint_cmp(lhs, rhs, 16) != 0) {{")
        lines.append(f'        likha("FAIL distrib {a} {b} {c}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "distrib", "\n".join(lines))
    return ok and out == "PASS", out


def prop_bigint_roundtrip(compiler, rng):
    """from_int(to_int(x)) == x"""
    cases = [rng.randint(0, 99999999) for _ in range(N_CASES)]
    lines = ["ayojan bigint", "mukhya() {",
             "    vitti a = nirmmita(8*8)"]
    for x in cases:
        lines.append(f"    bigint_from_int({x}, a, 8)")
        lines.append(f"    yadi (bigint_to_int(a, 8) != {x}) {{")
        lines.append(f'        likha("FAIL roundtrip {x}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "roundtrip", "\n".join(lines))
    return ok and out == "PASS", out


def prop_bigint_divmod(compiler, rng):
    """q*b + r == a and r < b"""
    cases = []
    for _ in range(N_CASES):
        a = rng.randint(0, 999999)
        b = rng.randint(1, 9999)
        cases.append((a, b))
    lines = ["ayojan bigint", "mukhya() {",
             "    vitti a = nirmmita(8*8)", "    vitti b = nirmmita(8*8)",
             "    vitti q = nirmmita(8*8)", "    vitti r = nirmmita(8*8)",
             "    vitti qb = nirmmita(16*8)", "    vitti chk = nirmmita(16*8)"]
    for a, b in cases:
        lines.append(f"    bigint_from_int({a}, a, 8)")
        lines.append(f"    bigint_from_int({b}, b, 8)")
        lines.append(f"    bigint_divmod(a, b, q, r, 8)")
        lines.append(f"    bigint_mul(q, b, qb, 8)")
        lines.append(f"    bigint_add(qb, r, chk, 16)")
        lines.append(f"    yadi (bigint_cmp(chk, a, 16) != 0) {{")
        lines.append(f'        likha("FAIL divmod_reconstruct {a} {b}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        lines.append(f"    yadi (bigint_cmp(r, b, 8) >= 0) {{")
        lines.append(f'        likha("FAIL divmod_remainder {a} {b}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "divmod", "\n".join(lines))
    return ok and out == "PASS", out


def prop_math_gcd(compiler, rng):
    """gcd(a,b) divides both a and b"""
    cases = []
    for _ in range(N_CASES):
        a = rng.randint(1, 9999)
        b = rng.randint(1, 9999)
        cases.append((a, b))
    lines = ["ayojan math", "mukhya() {"]
    # NOTE: use unique var names per case — redeclaring `vitti g` in the same
    # block does not reassign (compiler limitation, found by this property).
    for idx, (a, b) in enumerate(cases):
        lines.append(f"    vitti g{idx} = gcd({a}, {b})")
        lines.append(f"    yadi ({a} % g{idx} != 0) {{")
        lines.append(f'        likha("FAIL gcd_divides {a} {b}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        lines.append(f"    yadi ({b} % g{idx} != 0) {{")
        lines.append(f'        likha("FAIL gcd_divides {a} {b}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gcd", "\n".join(lines))
    return ok and out == "PASS", out


def prop_math_gcd_lcm(compiler, rng):
    """gcd(a,b) * lcm(a,b) == a * b"""
    cases = []
    for _ in range(N_CASES):
        a = rng.randint(1, 999)
        b = rng.randint(1, 999)
        cases.append((a, b))
    lines = ["ayojan math", "mukhya() {"]
    for a, b in cases:
        lines.append(f"    yadi (gcd({a},{b}) * lcm({a},{b}) != {a}*{b}) {{")
        lines.append(f'        likha("FAIL gcd_lcm {a} {b}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gcd_lcm", "\n".join(lines))
    return ok and out == "PASS", out


def prop_hash_fnv1a_deterministic(compiler, rng):
    """fnv1a(s) == fnv1a(s) — deterministic for same input"""
    cases = []
    for _ in range(N_CASES):
        # random lowercase string, length 1..10
        n = rng.randint(1, 10)
        s = "".join(chr(rng.randint(97, 122)) for _ in range(n))
        cases.append(s)
    lines = ["ayojan hash", "mukhya() {"]
    for idx, s in enumerate(cases):
        # escape for Sutram string literal
        lines.append(f'    vitti s{idx} = "{s}"')
        lines.append(f"    vitti h{idx}a = fnv1a_str(s{idx})")
        lines.append(f"    vitti h{idx}b = fnv1a_str(s{idx})")
        lines.append(f"    yadi (h{idx}a != h{idx}b) {{")
        lines.append(f'        likha("FAIL fnv1a_deterministic {s}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "fnv1a_det", "\n".join(lines))
    return ok and out == "PASS", out


def prop_hash_fnv1a_empty(compiler, rng):
    """fnv1a('') == 2166136261 (offset basis)"""
    lines = ["ayojan hash", "mukhya() {",
             '    vitti e = ""',
             "    yadi (fnv1a_str(e) != 2166136261) {",
             '        likha("FAIL fnv1a_empty\\n")',
             "        pratiyati 1",
             "    }",
             '    likha("PASS\\n")',
             "}"]
    ok, out = run_sm(compiler, "fnv1a_empty", "\n".join(lines))
    return ok and out == "PASS", out


def prop_hash_fnv1a_avalanche(compiler, rng):
    """Different strings hash differently (for these test cases)"""
    # fixed pairs known to differ
    pairs = [("hello", "hellp"), ("abc", "abd"), ("test", "Test"),
             ("", "a"), ("xyz", "xy")]
    lines = ["ayojan hash", "mukhya() {"]
    for idx, (s1, s2) in enumerate(pairs):
        lines.append(f'    vitti a{idx} = "{s1}"')
        lines.append(f'    vitti b{idx} = "{s2}"')
        lines.append(f"    yadi (fnv1a_str(a{idx}) == fnv1a_str(b{idx})) {{")
        lines.append(f'        likha("FAIL fnv1a_avalanche {s1} {s2}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "fnv1a_aval", "\n".join(lines))
    return ok and out == "PASS", out


def prop_sort_ordered(compiler, rng):
    """insertion_sort and merge_sort output is ordered (is_sorted==1)"""
    # fewer cases: each case emits many statements (block size limit)
    lines = ["ayojan sort", "mukhya() {",
             "    vitti a = nirmmita(10*8)",
             "    vitti b = nirmmita(10*8)"]
    for idx in range(5):
        vals = [rng.randint(0, 99) for _ in range(10)]
        for j, v in enumerate(vals):
            lines.append(f"    a[{j}] = {v}")
            lines.append(f"    b[{j}] = {v}")
        lines.append(f"    insertion_sort(a, 10)")
        lines.append(f"    yadi (is_sorted(a, 10) != 1) {{")
        lines.append(f'        likha("FAIL sort_ordered insertion\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        lines.append(f"    merge_sort(b, 10)")
        lines.append(f"    yadi (is_sorted(b, 10) != 1) {{")
        lines.append(f'        likha("FAIL sort_ordered merge\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "sort_ord", "\n".join(lines))
    return ok and out == "PASS", out


def prop_sort_permutation(compiler, rng):
    """insertion_sort and merge_sort give identical output (same multiset)"""
    lines = ["ayojan sort", "mukhya() {",
             "    vitti a = nirmmita(10*8)",
             "    vitti b = nirmmita(10*8)"]
    for idx in range(5):
        vals = [rng.randint(0, 99) for _ in range(10)]
        for j, v in enumerate(vals):
            lines.append(f"    a[{j}] = {v}")
            lines.append(f"    b[{j}] = {v}")
        lines.append(f"    insertion_sort(a, 10)")
        lines.append(f"    merge_sort(b, 10)")
        lines.append(f"    vitti k{idx} = 0")
        lines.append(f"    yavat (k{idx} < 10) {{")
        lines.append(f"        yadi (a[k{idx}] != b[k{idx}]) {{")
        lines.append(f'            likha("FAIL sort_permutation\\n")')
        lines.append(f"            pratiyati 1")
        lines.append(f"        }}")
        lines.append(f"        k{idx} = k{idx} + 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "sort_perm", "\n".join(lines))
    return ok and out == "PASS", out


def prop_sort_idempotent(compiler, rng):
    """sorting an already-sorted array is a no-op"""
    lines = ["ayojan sort", "mukhya() {",
             "    vitti a = nirmmita(10*8)"]
    for idx in range(5):
        vals = sorted(rng.randint(0, 99) for _ in range(10))
        for j, v in enumerate(vals):
            lines.append(f"    a[{j}] = {v}")
        lines.append(f"    insertion_sort(a, 10)")
        for j, v in enumerate(vals):
            lines.append(f"    yadi (a[{j}] != {v}) {{")
            lines.append(f'        likha("FAIL sort_idempotent\\n")')
            lines.append(f"        pratiyati 1")
            lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "sort_idem", "\n".join(lines))
    return ok and out == "PASS", out


def prop_sort_edges(compiler, rng):
    """empty and single-element arrays are handled"""
    lines = ["ayojan sort", "mukhya() {",
             "    vitti e = nirmmita(1*8)",
             "    insertion_sort(e, 0)",
             "    merge_sort(e, 0)",
             "    vitti s = nirmmita(1*8)",
             "    s[0] = 42",
             "    insertion_sort(s, 1)",
             "    yadi (s[0] != 42) {",
             '        likha("FAIL sort_edges single insertion\\n")',
             "        pratiyati 1",
             "    }",
             "    s[0] = 42",
             "    merge_sort(s, 1)",
             "    yadi (s[0] != 42) {",
             '        likha("FAIL sort_edges single merge\\n")',
             "        pratiyati 1",
             "    }",
             '    likha("PASS\\n")',
             "}"]
    ok, out = run_sm(compiler, "sort_edge", "\n".join(lines))
    return ok and out == "PASS", out


def prop_baseconv_roundtrip(compiler, rng):
    """from_digits(to_digits(x, b), b) == x for b in {2,8,10,16}"""
    lines = ["ayojan bigint", "ayojan baseconv", "mukhya() {",
             "    vitti x = nirmmita(8*8)",
             "    vitti digits = nirmmita(70*8)",
             "    vitti y = nirmmita(8*8)"]
    for idx in range(N_CASES):
        val = rng.randint(0, 999999)
        for b in (2, 8, 10, 16):
            lines.append(f"    bigint_from_int({val}, x, 8)")
            lines.append(f"    vitti len{idx}_{b} = bigint_to_digits(x, 8, {b}, digits)")
            lines.append(f"    bigint_from_digits(digits, len{idx}_{b}, {b}, y, 8)")
            lines.append(f"    yadi (bigint_cmp(x, y, 8) != 0) {{")
            lines.append(f'        likha("FAIL baseconv_roundtrip {val} base {b}\\n")')
            lines.append(f"        pratiyati 1")
            lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "baseconv_rt", "\n".join(lines))
    return ok and out == "PASS", out


def prop_strconv_roundtrip(compiler, rng):
    """str_to_int(int_to_str(n)) == n for spread incl 0, negatives, large"""
    vals = [0, 1, 0 - 1, 42, 0 - 987, 12345, 999999, 2147483647]
    for _ in range(7):
        vals.append(rng.randint(-999999, 999999))
    lines = ["ayojan strconv", "mukhya() {",
             "    vitti buf = nirmmita(30*8)",
             "    vitti ok = nirmmita(1*8)"]
    for idx, v in enumerate(vals):
        lines.append(f"    vitti len{idx} = int_to_str({v}, buf)")
        lines.append(f"    vitti back{idx} = str_to_int(buf, len{idx}, ok)")
        lines.append(f"    yadi (back{idx} != {v}) {{")
        lines.append(f'        likha("FAIL strconv_roundtrip {v}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        lines.append(f"    yadi (ok[0] != 1) {{")
        lines.append(f'        likha("FAIL strconv_roundtrip ok {v}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "strconv_rt", "\n".join(lines))
    return ok and out == "PASS", out


def prop_strconv_base_roundtrip(compiler, rng):
    """per-base round-trip through the string path: base 2/8/10/16"""
    vals = [0, 1, 255, 1024, 999999]
    for _ in range(5):
        vals.append(rng.randint(0, 999999))
    lines = ["ayojan strconv", "mukhya() {",
             "    vitti buf = nirmmita(70*8)",
             "    vitti ok = nirmmita(1*8)"]
    for idx, v in enumerate(vals):
        for b in (2, 8, 10, 16):
            lines.append(f"    vitti l{idx}_{b} = int_to_base_str({v}, {b}, buf)")
            lines.append(f"    vitti r{idx}_{b} = str_to_int_base(buf, l{idx}_{b}, {b}, ok)")
            lines.append(f"    yadi (r{idx}_{b} != {v}) {{")
            lines.append(f'        likha("FAIL strconv_base {v} base {b}\\n")')
            lines.append(f"        pratiyati 1")
            lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "strconv_base", "\n".join(lines))
    return ok and out == "PASS", out


def prop_strconv_pad_left(compiler, rng):
    """pad_left width invariant: result length == max(count, width),
    original digits preserved at the right, fill on the left"""
    lines = ["ayojan strconv", "mukhya() {",
             "    vitti buf = nirmmita(12*8)"]
    for idx in range(8):
        v = rng.randint(0, 9999)
        width = rng.randint(1, 10)
        # render v, then pad
        lines.append(f"    vitti c{idx} = int_to_str({v}, buf)")
        lines.append(f"    vitti w{idx} = pad_left(buf, c{idx}, {width}, 48)")
        # expected length
        # (compute in python for the check)
        s = str(v)
        exp_len = max(len(s), width)
        lines.append(f"    yadi (w{idx} != {exp_len}) {{")
        lines.append(f'        likha("FAIL pad_left len {v} w{width}\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        # check the rightmost len(s) chars are the digits of v
        for j, ch in enumerate(s):
            pos = exp_len - len(s) + j
            lines.append(f"    yadi (buf[{pos}] != {ord(ch)}) {{")
            lines.append(f'        likha("FAIL pad_left digits {v} w{width}\\n")')
            lines.append(f"        pratiyati 1")
            lines.append(f"    }}")
        # check fill chars on the left
        for j in range(exp_len - len(s)):
            lines.append(f"    yadi (buf[{j}] != 48) {{")
            lines.append(f'        likha("FAIL pad_left fill {v} w{width}\\n")')
            lines.append(f"        pratiyati 1")
            lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "pad_left", "\n".join(lines))
    return ok and out == "PASS", out


def main():
    compiler = None
    for i, a in enumerate(sys.argv):
        if a == "--compiler" and i + 1 < len(sys.argv):
            compiler = sys.argv[i + 1]
    if not compiler:
        compiler = build_compiler()

    rng = random.Random(SEED)
    props = [
        ("bigint add/sub inverse", prop_bigint_add_sub),
        ("bigint mul distributes over add", prop_bigint_mul_distrib),
        ("bigint from_int/to_int roundtrip", prop_bigint_roundtrip),
        ("bigint divmod reconstruct", prop_bigint_divmod),
        ("math gcd divides", prop_math_gcd),
        ("math gcd*lcm == a*b", prop_math_gcd_lcm),
        ("hash fnv1a deterministic", prop_hash_fnv1a_deterministic),
        ("hash fnv1a empty == basis", prop_hash_fnv1a_empty),
        ("hash fnv1a avalanche", prop_hash_fnv1a_avalanche),
        ("sort output ordered", prop_sort_ordered),
        ("sort permutation", prop_sort_permutation),
        ("sort idempotent", prop_sort_idempotent),
        ("sort edge cases", prop_sort_edges),
        ("baseconv roundtrip", prop_baseconv_roundtrip),
        ("strconv roundtrip", prop_strconv_roundtrip),
        ("strconv base roundtrip", prop_strconv_base_roundtrip),
        ("strconv pad_left", prop_strconv_pad_left),
    ]

    failed = []
    for name, fn in props:
        ok, out = fn(compiler, rng)
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {name}")
        if not ok:
            print(f"  {out}")
            failed.append(name)

    print(f"\n{len(props)-len(failed)}/{len(props)} properties hold")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
