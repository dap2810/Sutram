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


def prop_string_find(compiler, rng):
    """str_find agrees with Python str.find on spread (incl absent)"""
    cases = []
    for _ in range(8):
        hn = rng.randint(1, 12)
        hay = "".join(chr(rng.randint(97, 99)) for _ in range(hn))
        # needle: sometimes present, sometimes absent
        if rng.random() < 0.5 and hn >= 2:
            start = rng.randint(0, hn - 1)
            nn = rng.randint(1, hn - start)
            needle = hay[start:start + nn]
        else:
            nn = rng.randint(1, 4)
            needle = "".join(chr(rng.randint(97, 99)) for _ in range(nn))
        cases.append((hay, needle, hay.find(needle)))
    lines = ["ayojan string", "mukhya() {",
             "    vitti hay = nirmmita(12*8)",
             "    vitti nd = nirmmita(6*8)"]
    for idx, (hay, needle, exp) in enumerate(cases):
        for j, ch in enumerate(hay):
            lines.append(f"    hay[{j}] = {ord(ch)}")
        for j, ch in enumerate(needle):
            lines.append(f"    nd[{j}] = {ord(ch)}")
        lines.append(f"    yadi (str_find(hay, {len(hay)}, nd, {len(needle)}) != {exp}) {{")
        lines.append(f'        likha("FAIL string_find\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "str_find", "\n".join(lines))
    return ok and out == "PASS", out


def prop_string_replace(compiler, rng):
    """str_replace matches Python str.replace; find returns -1 after"""
    cases = []
    for _ in range(6):
        src = "".join(chr(rng.randint(97, 99)) for _ in range(rng.randint(3, 10)))
        # pick a needle that occurs (or empty)
        if len(src) >= 2 and rng.random() < 0.7:
            i = rng.randint(0, len(src) - 2)
            needle = src[i:i + 2]
        else:
            needle = "zz"
        repl = "".join(chr(rng.randint(97, 99)) for _ in range(rng.randint(1, 3)))
        exp = src.replace(needle, repl)
        cases.append((src, needle, repl, exp))
    lines = ["ayojan string", "mukhya() {",
             "    vitti src = nirmmita(12*8)",
             "    vitti find = nirmmita(4*8)",
             "    vitti repl = nirmmita(5*8)",
             "    vitti out = nirmmita(30*8)"]
    for idx, (src, needle, repl, exp) in enumerate(cases):
        for j, ch in enumerate(src):
            lines.append(f"    src[{j}] = {ord(ch)}")
        for j, ch in enumerate(needle):
            lines.append(f"    find[{j}] = {ord(ch)}")
        for j, ch in enumerate(repl):
            lines.append(f"    repl[{j}] = {ord(ch)}")
        lines.append(f"    repl[{len(repl)}] = 0")
        lines.append(f"    vitti n{idx} = str_replace(src, {len(src)}, find, {len(needle)}, repl, out)")
        lines.append(f"    yadi (n{idx} != {len(exp)}) {{")
        lines.append(f'        likha("FAIL string_replace len\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        for j, ch in enumerate(exp):
            lines.append(f"    yadi (out[{j}] != {ord(ch)}) {{")
            lines.append(f'        likha("FAIL string_replace chars\\n")')
            lines.append(f"        pratiyati 1")
            lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "str_repl", "\n".join(lines))
    return ok and out == "PASS", out


def prop_string_split_join(compiler, rng):
    """str_join(str_split(s, sep), sep) == s (skip trailing-sep edge)"""
    cases = []
    for _ in range(6):
        # avoid trailing separator (documented edge: yields extra empty seg)
        s = "".join(chr(rng.randint(97, 99)) for _ in range(rng.randint(1, 10)))
        sep = chr(rng.randint(44, 45))  # ',' or '-'
        # ensure no trailing sep for the round-trip
        if s.endswith(sep):
            s = s[:-1] + "a"
        cases.append((s, sep))
    lines = ["ayojan string", "mukhya() {",
             "    vitti src = nirmmita(12*8)",
             "    vitti sep = nirmmita(2*8)",
             "    vitti parts = nirmmita(40*8)",
             "    vitti out = nirmmita(20*8)"]
    for idx, (s, sep) in enumerate(cases):
        for j, ch in enumerate(s):
            lines.append(f"    src[{j}] = {ord(ch)}")
        lines.append(f"    sep[0] = {ord(sep)}")
        lines.append(f"    vitti nc{idx} = str_split(src, {len(s)}, sep, 1, parts, 10)")
        lines.append(f"    vitti jn{idx} = str_join(parts, nc{idx}, sep, 1, out)")
        lines.append(f"    yadi (jn{idx} != {len(s)}) {{")
        lines.append(f'        likha("FAIL split_join len\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        for j, ch in enumerate(s):
            lines.append(f"    yadi (out[{j}] != {ord(ch)}) {{")
            lines.append(f'        likha("FAIL split_join chars\\n")')
            lines.append(f"        pratiyati 1")
            lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "split_join", "\n".join(lines))
    return ok and out == "PASS", out


def prop_string_trim_case(compiler, rng):
    """str_trim/str_upper/str_lower match Python strip/upper/lower.

    NOTE (R10): the per-character checks are done through a loop helper
    comparing against a literal, not unrolled yadi blocks — the string
    module grew (byte-string surface) and the unrolled form exceeded the
    compiler's fixed AST capacity. Same 8 inputs, same invariant.
    """
    cases = []
    for _ in range(8):
        # mix of spaces and letters
        s = "".join(rng.choice([" ", "a", "B", "c"]) for _ in range(rng.randint(1, 8)))
        cases.append(s)
    lines = ["ayojan string",
             "prakriya cells_match(cells, n, lit, ln) {",
             "    vitti i = 0",
             "    yadi (n != ln) { pratiyati 0 }",
             "    yavat (i < n) {",
             "        yadi (cells[i] != char_at(lit, i)) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "mukhya() {",
             "    vitti src = nirmmita(10*8)",
             "    vitti out = nirmmita(10*8)"]
    for idx, s in enumerate(cases):
        for j, ch in enumerate(s):
            lines.append(f"    src[{j}] = {ord(ch)}")
        exp_trim = s.strip(" ")
        exp_upper = s.upper()
        exp_lower = s.lower()
        lines.append(f"    vitti tn{idx} = str_trim(src, {len(s)}, out)")
        lines.append(f'    yadi (cells_match(out, tn{idx}, "{exp_trim}", {len(exp_trim)}) == 0) {{')
        lines.append(f'        likha("FAIL trim\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        lines.append(f"    str_upper(src, {len(s)}, out)")
        lines.append(f'    yadi (cells_match(out, {len(s)}, "{exp_upper}", {len(exp_upper)}) == 0) {{')
        lines.append(f'        likha("FAIL upper\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        lines.append(f"    str_lower(src, {len(s)}, out)")
        lines.append(f'    yadi (cells_match(out, {len(s)}, "{exp_lower}", {len(exp_lower)}) == 0) {{')
        lines.append(f'        likha("FAIL lower\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "trim_case", "\n".join(lines))
    return ok and out == "PASS", out


def prop_strb_find(compiler, rng):
    """strb_find agrees with Python str.find on byte strings incl literals"""
    cases = []
    for _ in range(8):
        hn = rng.randint(1, 12)
        hay = "".join(chr(rng.randint(97, 99)) for _ in range(hn))
        if rng.random() < 0.5 and hn >= 2:
            start = rng.randint(0, hn - 1)
            nn = rng.randint(1, hn - start)
            needle = hay[start:start + nn]
        else:
            nn = rng.randint(1, 4)
            needle = "".join(chr(rng.randint(97, 99)) for _ in range(nn))
        cases.append((hay, needle, hay.find(needle)))
    # one explicit literal case (a literal, not a hand-built buffer)
    cases.append(("literal probe", "probe", "literal probe".find("probe")))
    lines = ["ayojan strb", "mukhya() {"]
    for idx, (hay, needle, exp) in enumerate(cases):
        lines.append(f'    yadi (strb_find("{hay}", {len(hay)}, "{needle}", {len(needle)}) != {exp}) {{')
        lines.append(f'        likha("FAIL strb_find\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "strb_find", "\n".join(lines))
    return ok and out == "PASS", out


def prop_strb_replace(compiler, rng):
    """strb_replace matches Python str.replace; incl a literal-driven case"""
    cases = []
    for _ in range(6):
        src = "".join(chr(rng.randint(97, 99)) for _ in range(rng.randint(3, 10)))
        if len(src) >= 2 and rng.random() < 0.7:
            i = rng.randint(0, len(src) - 2)
            needle = src[i:i + 2]
        else:
            needle = "zz"
        repl = "".join(chr(rng.randint(97, 99)) for _ in range(rng.randint(1, 3)))
        exp = src.replace(needle, repl)
        cases.append((src, needle, repl, exp))
    # excluded edge: empty needle (strb_replace copies verbatim, Python
    # interleaves the replacement) — documented in the module header.
    cases.append(("foo bar foo", "foo", "baz", "baz bar baz"))
    lines = ["ayojan strb", "mukhya() {",
             "    vitti out = nirmmita(64)"]
    for idx, (src, needle, repl, exp) in enumerate(cases):
        lines.append(f'    vitti n{idx} = strb_replace("{src}", {len(src)}, "{needle}", {len(needle)}, "{repl}", out)')
        lines.append(f"    yadi (n{idx} != {len(exp)}) {{")
        lines.append(f'        likha("FAIL strb_replace len\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        for j, ch in enumerate(exp):
            lines.append(f"    yadi (char_at(out, {j}) != {ord(ch)}) {{")
            lines.append(f'        likha("FAIL strb_replace chars\\n")')
            lines.append(f"        pratiyati 1")
            lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "strb_repl", "\n".join(lines))
    return ok and out == "PASS", out


def prop_strb_split_join(compiler, rng):
    """strb_join(strb_split(s, sep), sep) == s (skip trailing-sep edge)"""
    cases = []
    for _ in range(6):
        s = "".join(chr(rng.randint(97, 99)) for _ in range(rng.randint(1, 10)))
        sep = chr(rng.randint(44, 45))  # ',' or '-'
        if s.endswith(sep):
            s = s[:-1] + "a"
        cases.append((s, sep))
    lines = ["ayojan strb", "mukhya() {",
             "    vitti parts = nirmmita(40*8)",
             "    vitti out = nirmmita(32)"]
    for idx, (s, sep) in enumerate(cases):
        lines.append(f'    vitti nc{idx} = strb_split("{s}", {len(s)}, "{sep}", 1, parts, 12)')
        lines.append(f'    vitti jn{idx} = strb_join(parts, nc{idx}, "{sep}", 1, out)')
        lines.append(f"    yadi (jn{idx} != {len(s)}) {{")
        lines.append(f'        likha("FAIL strb_split_join len\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        for j, ch in enumerate(s):
            lines.append(f"    yadi (char_at(out, {j}) != {ord(ch)}) {{")
            lines.append(f'        likha("FAIL strb_split_join chars\\n")')
            lines.append(f"        pratiyati 1")
            lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "strb_sj", "\n".join(lines))
    return ok and out == "PASS", out


def prop_strb_trim_case(compiler, rng):
    """strb_trim/strb_upper/strb_lower match Python (literal inputs).

    Loop-helper comparison (see prop_string_trim_case note): keeps the
    generated program under the compiler's fixed AST capacity.
    """
    cases = []
    for _ in range(8):
        s = "".join(rng.choice([" ", "a", "B", "c"]) for _ in range(rng.randint(1, 8)))
        cases.append(s)
    lines = ["ayojan strb",
             "prakriya bytes_match(buf, n, lit, ln) {",
             "    vitti i = 0",
             "    yadi (n != ln) { pratiyati 0 }",
             "    yavat (i < n) {",
             "        yadi (char_at(buf, i) != char_at(lit, i)) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "mukhya() {",
             "    vitti out = nirmmita(16)"]
    for idx, s in enumerate(cases):
        exp_trim = s.strip(" ")
        exp_upper = s.upper()
        exp_lower = s.lower()
        lines.append(f'    vitti tn{idx} = strb_trim("{s}", {len(s)}, out)')
        lines.append(f'    yadi (bytes_match(out, tn{idx}, "{exp_trim}", {len(exp_trim)}) == 0) {{')
        lines.append(f'        likha("FAIL strb_trim\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        lines.append(f'    strb_upper("{s}", {len(s)}, out)')
        lines.append(f'    yadi (bytes_match(out, {len(s)}, "{exp_upper}", {len(exp_upper)}) == 0) {{')
        lines.append(f'        likha("FAIL strb_upper\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
        lines.append(f'    strb_lower("{s}", {len(s)}, out)')
        lines.append(f'    yadi (bytes_match(out, {len(s)}, "{exp_lower}", {len(exp_lower)}) == 0) {{')
        lines.append(f'        likha("FAIL strb_lower\\n")')
        lines.append(f"        pratiyati 1")
        lines.append(f"    }}")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "strb_tc", "\n".join(lines))
    return ok and out == "PASS", out


def _fnv1a_py(s):
    h = 2166136261
    for b in s.encode():
        h = ((h ^ b) * 16777619) % 4294967296
    return h


def _distinct_keys(rng, n, lo=97, hi=99):
    keys = []
    while len(keys) < n:
        k = "".join(chr(rng.randint(lo, hi)) for _ in range(rng.randint(2, 5)))
        if k not in keys:
            keys.append(k)
    return keys


def prop_map_roundtrip(compiler, rng):
    """map_get returns what map_put stored, for a spread of distinct keys"""
    keys = _distinct_keys(rng, 8)
    vals = [rng.randint(1, 999) for _ in keys]
    lines = ["ayojan map", "mukhya() {",
             "    vitti m = map_init(16)"]
    for k, v in zip(keys, vals):
        lines.append(f'    map_put(m, 16, "{k}", {len(k)}, {v})')
    lines.append("    yadi (map_size(m) != 8) {")
    lines.append('        likha("FAIL map size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k, v in zip(keys, vals):
        lines.append(f'    yadi (map_get(m, 16, "{k}", {len(k)}) != {v}) {{')
        lines.append(f'        likha("FAIL map roundtrip\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "map_rt", "\n".join(lines))
    return ok and out == "PASS", out


def prop_map_update(compiler, rng):
    """putting the same key twice: size unchanged, second value wins"""
    keys = _distinct_keys(rng, 4)
    lines = ["ayojan map", "mukhya() {",
             "    vitti m = map_init(8)"]
    for k in keys:
        v1 = rng.randint(1, 500)
        v2 = rng.randint(501, 999)
        lines.append(f'    map_put(m, 8, "{k}", {len(k)}, {v1})')
        lines.append(f'    map_put(m, 8, "{k}", {len(k)}, {v2})')
        lines.append(f'    yadi (map_get(m, 8, "{k}", {len(k)}) != {v2}) {{')
        lines.append(f'        likha("FAIL map update\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    yadi (map_size(m) != 4) {")
    lines.append('        likha("FAIL map update size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "map_upd", "\n".join(lines))
    return ok and out == "PASS", out


def prop_map_delete(compiler, rng):
    """after remove: contains 0, size decreases, other keys unaffected"""
    keys = _distinct_keys(rng, 6)
    vals = [rng.randint(1, 999) for _ in keys]
    drop = (1, 4)
    lines = ["ayojan map", "mukhya() {",
             "    vitti m = map_init(16)"]
    for k, v in zip(keys, vals):
        lines.append(f'    map_put(m, 16, "{k}", {len(k)}, {v})')
    for d in drop:
        k = keys[d]
        lines.append(f'    yadi (map_remove(m, 16, "{k}", {len(k)}) != 1) {{')
        lines.append(f'        likha("FAIL map remove rc\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    for d in drop:
        k = keys[d]
        lines.append(f'    yadi (map_contains(m, 16, "{k}", {len(k)}) != 0) {{')
        lines.append(f'        likha("FAIL map remove contains\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    yadi (map_size(m) != 4) {")
    lines.append('        likha("FAIL map remove size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for i, (k, v) in enumerate(zip(keys, vals)):
        if i in drop:
            continue
        lines.append(f'    yadi (map_get(m, 16, "{k}", {len(k)}) != {v}) {{')
        lines.append(f'        likha("FAIL map remove survivor\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "map_del", "\n".join(lines))
    return ok and out == "PASS", out


def prop_map_collision(compiler, rng):
    """keys hashing to the same bucket are all still retrievable"""
    cands = []
    while len(cands) < 40:
        cands.append("".join(chr(rng.randint(97, 102))
                             for _ in range(rng.randint(2, 5))))
    buckets = {}
    for k in cands:
        buckets.setdefault(_fnv1a_py(k) % 8, []).append(k)
    triple = next(v[:3] for v in buckets.values() if len(v) >= 3)
    vals = [rng.randint(1, 999) for _ in triple]
    lines = ["ayojan map", "mukhya() {",
             "    vitti m = map_init(8)"]
    for k, v in zip(triple, vals):
        lines.append(f'    map_put(m, 8, "{k}", {len(k)}, {v})')
    for k, v in zip(triple, vals):
        lines.append(f'    yadi (map_get(m, 8, "{k}", {len(k)}) != {v}) {{')
        lines.append(f'        likha("FAIL map collision\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "map_col", "\n".join(lines))
    return ok and out == "PASS", out


def prop_map_keys_count(compiler, rng):
    """map_keys count == map_size, and the written bytes add up"""
    keys = _distinct_keys(rng, 5)
    vals = [rng.randint(1, 999) for _ in keys]
    total_len = sum(len(k) for k in keys)
    lines = ["ayojan map", "mukhya() {",
             "    vitti m = map_init(16)",
             "    vitti out = nirmmita(32*8)",
             "    vitti nk = 0",
             "    vitti rpos = 0",
             "    vitti total = 0",
             "    vitti t = 0",
             "    vitti sl = 0"]
    for k, v in zip(keys, vals):
        lines.append(f'    map_put(m, 16, "{k}", {len(k)}, {v})')
    lines.append("    nk = map_keys(m, out)")
    lines.append("    yadi (nk != 5) {")
    lines.append('        likha("FAIL map keys count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (nk != map_size(m)) {")
    lines.append('        likha("FAIL map keys vs size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yavat (t < nk) {")
    lines.append("        sl = out[rpos]")
    lines.append("        total = total + sl")
    lines.append("        rpos = rpos + 1 + sl")
    lines.append("        t = t + 1")
    lines.append("    }")
    lines.append(f"    yadi (total != {total_len}) {{")
    lines.append('        likha("FAIL map keys bytes\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "map_keys", "\n".join(lines))
    return ok and out == "PASS", out


def _tdiv(a, b):
    """Integer division truncated toward zero (matches Sutram /)."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def prop_strb_pack_unpack(compiler, rng):
    """strb_unpack(strb_pack(x)) == x and strb_pack(strb_unpack(b)) == b"""
    cases = []
    for _ in range(8):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 8)))
        cases.append(s)
    lines = ["ayojan strb",
             "prakriya cells_match(a, b, n) {",
             "    vitti i = 0",
             "    yavat (i < n) {",
             "        yadi (a[i] != b[i]) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "prakriya bytes_match(buf, n, lit, ln) {",
             "    vitti i = 0",
             "    yadi (n != ln) { pratiyati 0 }",
             "    yavat (i < n) {",
             "        yadi (char_at(buf, i) != char_at(lit, i)) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "mukhya() {",
             "    vitti cells = nirmmita(8*8)",
             "    vitti back = nirmmita(8*8)",
             "    vitti out = nirmmita(16)",
             "    vitti out2 = nirmmita(16)"]
    for s in cases:
        n = len(s)
        for i, ch in enumerate(s):
            lines.append(f"    cells[{i}] = {ord(ch)}")
        lines.append(f"    yadi (strb_pack(cells, {n}, out) != {n}) {{")
        lines.append('        likha("FAIL strb_pack len\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    strb_unpack(out, {n}, back)")
        lines.append(f"    yadi (cells_match(cells, back, {n}) == 0) {{")
        lines.append('        likha("FAIL strb_pack_unpack roundtrip\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f'    strb_unpack("{s}", {n}, back)')
        lines.append(f"    strb_pack(back, {n}, out2)")
        lines.append(f'    yadi (bytes_match(out2, {n}, "{s}", {n}) == 0) {{')
        lines.append('        likha("FAIL strb_unpack_pack roundtrip\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "strb_pu", "\n".join(lines))
    return ok and out == "PASS", out


def prop_strb_dup(compiler, rng):
    """strb_dup copies the source bytes exactly, including empty input"""
    cases = [""]
    for _ in range(8):
        cases.append("".join(rng.choice(["a", "b", "c", " "])
                             for _ in range(rng.randint(1, 8))))
    lines = ["ayojan strb",
             "prakriya bytes_match(buf, n, lit, ln) {",
             "    vitti i = 0",
             "    yadi (n != ln) { pratiyati 0 }",
             "    yavat (i < n) {",
             "        yadi (char_at(buf, i) != char_at(lit, i)) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "mukhya() {",
             "    vitti out = nirmmita(16)"]
    for s in cases:
        n = len(s)
        lines.append(f'    yadi (strb_dup("{s}", {n}, out) != {n}) {{')
        lines.append('        likha("FAIL strb_dup len\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f'    yadi (bytes_match(out, {n}, "{s}", {n}) == 0) {{')
        lines.append('        likha("FAIL strb_dup bytes\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "strb_dup", "\n".join(lines))
    return ok and out == "PASS", out


def prop_sankhyiki_purna(compiler, rng):
    """purna_* integer stats agree with Python (trunc division) on a
    spread of arrays including negatives, a single element, and empty."""
    cases = [[], [7], [1, 2, 3, 4, 5]]
    for _ in range(8):
        cases.append([rng.randint(-20, 20)
                      for _ in range(rng.randint(2, 6))])
    lines = ["ayojan sankhyiki",
             "prakriya check_purna_a(xs, n, esum, emean, emin) {",
             "    yadi (purna_yoga(xs, n) != esum) { pratiyati 1 }",
             "    yadi (purna_madhya(xs, n) != emean) { pratiyati 1 }",
             "    yadi (purna_laghutama(xs, n) != emin) { pratiyati 1 }",
             "    pratiyati 0",
             "}",
             "prakriya check_purna_b(xs, n, emax, erange, evar) {",
             "    yadi (purna_adhikatama(xs, n) != emax) { pratiyati 1 }",
             "    yadi (purna_vyapti(xs, n) != erange) { pratiyati 1 }",
             "    yadi (purna_prasaran(xs, n) != evar) { pratiyati 1 }",
             "    pratiyati 0",
             "}",
             "mukhya() {",
             "    pankti a[6]"]
    for vals in cases:
        n = len(vals)
        if n == 0:
            esum = emean = emin = emax = erange = evar = 0
        else:
            esum = sum(vals)
            emean = _tdiv(esum, n)
            emin = min(vals)
            emax = max(vals)
            erange = emax - emin
            evar = _tdiv(sum((v - emean) ** 2 for v in vals), n)
        for i, v in enumerate(vals):
            lines.append(f"    a[{i}] = {v}")
        lines.append(
            f"    yadi (check_purna_a(a, {n}, {esum}, {emean}, {emin}) != 0) {{")
        lines.append('        likha("FAIL purna_a\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(
            f"    yadi (check_purna_b(a, {n}, {emax}, {erange}, {evar}) != 0) {{")
        lines.append('        likha("FAIL purna_b\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "purna", "\n".join(lines))
    return ok and out == "PASS", out


def _emit_segments(lines, var, words):
    """Emit cell assignments building a length-prefixed segment array."""
    pos = 0
    for w in words:
        lines.append(f"    {var}[{pos}] = {len(w)}")
        for k, ch in enumerate(w):
            lines.append(f"    {var}[{pos + 1 + k}] = {ord(ch)}")
        pos += 1 + len(w)
    return pos


def _segs_equal_lines():
    return ["prakriya segs_equal(x, xn, y, yn) {",
            "    vitti px = 0",
            "    vitti py = 0",
            "    vitti i = 0",
            "    vitti lx = 0",
            "    vitti ly = 0",
            "    vitti k = 0",
            "    yadi (xn != yn) { pratiyati 0 }",
            "    yavat (i < xn) {",
            "        lx = x[px]",
            "        ly = y[py]",
            "        yadi (lx != ly) { pratiyati 0 }",
            "        k = 0",
            "        yavat (k < lx) {",
            "            yadi (x[px + 1 + k] != y[py + 1 + k]) { pratiyati 0 }",
            "            k = k + 1",
            "        }",
            "        px = px + 1 + lx",
            "        py = py + 1 + ly",
            "        i = i + 1",
            "    }",
            "    pratiyati 1",
            "}"]


def prop_set_add_contains_remove(compiler, rng):
    """set_add then set_contains is true; set_remove then false"""
    keys = _distinct_keys(rng, 6)
    drop = keys[:3]
    keep = keys[3:]
    lines = ["ayojan set", "mukhya() {",
             "    vitti s = set_init(16)"]
    for k in keys:
        lines.append(f'    set_add(s, 16, "{k}", {len(k)})')
    lines.append("    yadi (set_size(s) != 6) {")
    lines.append('        likha("FAIL set size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in keys:
        lines.append(f'    yadi (set_contains(s, 16, "{k}", {len(k)}) != 1) {{')
        lines.append('        likha("FAIL set contains after add\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    for k in drop:
        lines.append(f'    yadi (set_remove(s, 16, "{k}", {len(k)}) != 1) {{')
        lines.append('        likha("FAIL set remove rc\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f'    yadi (set_contains(s, 16, "{k}", {len(k)}) != 0) {{')
        lines.append('        likha("FAIL set contains after remove\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    yadi (set_size(s) != 3) {")
    lines.append('        likha("FAIL set size after remove\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in keep:
        lines.append(f'    yadi (set_contains(s, 16, "{k}", {len(k)}) != 1) {{')
        lines.append('        likha("FAIL set survivor\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "set_acr", "\n".join(lines))
    return ok and out == "PASS", out


def prop_set_idempotent(compiler, rng):
    """set_add twice does not change set_size"""
    keys = _distinct_keys(rng, 5)
    lines = ["ayojan set", "mukhya() {",
             "    vitti s = set_init(16)"]
    for k in keys:
        lines.append(f'    set_add(s, 16, "{k}", {len(k)})')
        lines.append(f'    set_add(s, 16, "{k}", {len(k)})')
    lines.append("    yadi (set_size(s) != 5) {")
    lines.append('        likha("FAIL set idempotent size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "set_idem", "\n".join(lines))
    return ok and out == "PASS", out


def prop_set_union_commutative(compiler, rng):
    """set_union is commutative in size and content (sorted compare)"""
    words = _distinct_keys(rng, 6)
    avals, bvals = words[:4], words[2:]
    exp = sorted(set(avals) | set(bvals))
    lines = ["ayojan set"] + _segs_equal_lines() + [
             "mukhya() {",
             "    vitti a = set_init(16)",
             "    vitti b = set_init(16)",
             "    vitti u1 = set_init(32)",
             "    vitti u2 = set_init(32)",
             "    vitti arr1 = nirmmita(64*8)",
             "    vitti arr2 = nirmmita(64*8)",
             "    vitti exp = nirmmita(64*8)",
             "    vitti n1 = 0",
             "    vitti n2 = 0"]
    for k in avals:
        lines.append(f'    set_add(a, 16, "{k}", {len(k)})')
    for k in bvals:
        lines.append(f'    set_add(b, 16, "{k}", {len(k)})')
    lines.append("    set_union(a, 16, b, 16, u1)")
    lines.append("    set_union(b, 16, a, 16, u2)")
    lines.append("    yadi (set_size(u1) != set_size(u2)) {")
    lines.append('        likha("FAIL set union size commutative\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    n1 = set_to_array(u1, 32, arr1)")
    lines.append("    n2 = set_to_array(u2, 32, arr2)")
    lines.append("    yadi (segs_equal(arr1, n1, arr2, n2) == 0) {")
    lines.append('        likha("FAIL set union content commutative\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    _emit_segments(lines, "exp", exp)
    lines.append(f"    yadi (segs_equal(arr1, n1, exp, {len(exp)}) == 0) {{")
    lines.append('        likha("FAIL set union content\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "set_union", "\n".join(lines))
    return ok and out == "PASS", out


def prop_set_intersect_self_empty(compiler, rng):
    """intersect with itself equals the set; with empty is empty"""
    keys = _distinct_keys(rng, 4)
    exp = sorted(keys)
    lines = ["ayojan set"] + _segs_equal_lines() + [
             "mukhya() {",
             "    vitti a = set_init(16)",
             "    vitti e = set_init(16)",
             "    vitti o1 = set_init(16)",
             "    vitti o2 = set_init(16)",
             "    vitti arr0 = nirmmita(64*8)",
             "    vitti arr1 = nirmmita(64*8)",
             "    vitti exp = nirmmita(64*8)",
             "    vitti n0 = 0",
             "    vitti n1 = 0"]
    for k in keys:
        lines.append(f'    set_add(a, 16, "{k}", {len(k)})')
    lines.append("    set_intersect(a, 16, a, 16, o1)")
    lines.append("    set_intersect(a, 16, e, 16, o2)")
    lines.append("    yadi (set_size(o2) != 0) {")
    lines.append('        likha("FAIL set intersect empty\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    n0 = set_to_array(a, 16, arr0)")
    lines.append("    n1 = set_to_array(o1, 16, arr1)")
    lines.append("    yadi (segs_equal(arr0, n0, arr1, n1) == 0) {")
    lines.append('        likha("FAIL set intersect self\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    _emit_segments(lines, "exp", exp)
    lines.append(f"    yadi (segs_equal(arr1, n1, exp, {len(exp)}) == 0) {{")
    lines.append('        likha("FAIL set intersect content\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "set_inter", "\n".join(lines))
    return ok and out == "PASS", out


def prop_set_difference(compiler, rng):
    """difference(a, b) contains nothing in b; equals Python expectation"""
    words = _distinct_keys(rng, 5)
    avals, bvals = words[:4], words[2:]
    exp = sorted(set(avals) - set(bvals))
    lines = ["ayojan set"] + _segs_equal_lines() + [
             "mukhya() {",
             "    vitti a = set_init(16)",
             "    vitti b = set_init(16)",
             "    vitti d = set_init(16)",
             "    vitti arr = nirmmita(64*8)",
             "    vitti exp = nirmmita(64*8)",
             "    vitti n = 0"]
    for k in avals:
        lines.append(f'    set_add(a, 16, "{k}", {len(k)})')
    for k in bvals:
        lines.append(f'    set_add(b, 16, "{k}", {len(k)})')
    lines.append("    set_difference(a, 16, b, 16, d)")
    lines.append("    n = set_to_array(d, 16, arr)")
    _emit_segments(lines, "exp", exp)
    lines.append(f"    yadi (segs_equal(arr, n, exp, {len(exp)}) == 0) {{")
    lines.append('        likha("FAIL set difference content\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in exp:
        lines.append(f'    yadi (set_contains(a, 16, "{k}", {len(k)}) != 1) {{')
        lines.append('        likha("FAIL set difference in a\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f'    yadi (set_contains(b, 16, "{k}", {len(k)}) != 0) {{')
        lines.append('        likha("FAIL set difference not in b\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "set_diff", "\n".join(lines))
    return ok and out == "PASS", out


def prop_set_subset(compiler, rng):
    """subset: reflexive, empty subset, both-directions-implies-equal"""
    words = _distinct_keys(rng, 4)
    avals, bvals, cvals = words[:2], words[:3], [words[0], words[3]]
    lines = ["ayojan set"] + _segs_equal_lines() + [
             "mukhya() {",
             "    vitti a = set_init(16)",
             "    vitti b = set_init(16)",
             "    vitti c = set_init(16)",
             "    vitti d = set_init(16)",
             "    vitti e = set_init(16)",
             "    vitti arr1 = nirmmita(64*8)",
             "    vitti arr2 = nirmmita(64*8)",
             "    vitti n1 = 0",
             "    vitti n2 = 0"]
    for k in avals:
        lines.append(f'    set_add(a, 16, "{k}", {len(k)})')
        lines.append(f'    set_add(d, 16, "{k}", {len(k)})')
    for k in bvals:
        lines.append(f'    set_add(b, 16, "{k}", {len(k)})')
    for k in cvals:
        lines.append(f'    set_add(c, 16, "{k}", {len(k)})')
    lines.append("    yadi (set_is_subset(a, 16, a, 16) != 1) {")
    lines.append('        likha("FAIL set subset reflexive\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (set_is_subset(a, 16, b, 16) != 1) {")
    lines.append('        likha("FAIL set subset a b\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (set_is_subset(b, 16, a, 16) != 0) {")
    lines.append('        likha("FAIL set subset b a\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (set_is_subset(e, 16, b, 16) != 1) {")
    lines.append('        likha("FAIL set subset empty\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (set_is_subset(c, 16, b, 16) != 0) {")
    lines.append('        likha("FAIL set subset c b\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (set_is_subset(a, 16, d, 16) != 1) {")
    lines.append('        likha("FAIL set subset a d\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (set_is_subset(d, 16, a, 16) != 1) {")
    lines.append('        likha("FAIL set subset d a\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    n1 = set_to_array(a, 16, arr1)")
    lines.append("    n2 = set_to_array(d, 16, arr2)")
    lines.append("    yadi (segs_equal(arr1, n1, arr2, n2) == 0) {")
    lines.append('        likha("FAIL set subset both ways equal\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "set_sub", "\n".join(lines))
    return ok and out == "PASS", out


def _fmt_half_away(x, places):
    """Python mirror of fmt_fixed: half away from zero, float arithmetic
    identical to the Sutram side (magnitude * 10**places + 0.5, floor)."""
    import math
    places = max(0, min(9, places))
    p10 = 10.0 ** places
    mag = abs(x)
    r = math.floor(mag * p10 + 0.5)
    ip, fp = divmod(r, 10 ** places)
    sign = "-" if x < 0 else ""
    if places == 0:
        return f"{sign}{ip}"
    return f"{sign}{ip}.{fp:0{places}d}"


def prop_fmt_int_base_roundtrip(compiler, rng):
    """fmt_int_base then parse == original, incl negatives and base 36;
    bad bases return 0"""
    vals = [0, 1, -1, 255, -255, 99999, -99999, rng.randint(-10 ** 6, 10 ** 6)]
    bases = [2, 8, 10, 16, 36]
    lines = ["ayojan fmt",
             "prakriya parse_base(buf, n, base) {",
             "    vitti i = 0",
             "    vitti neg = 0",
             "    vitti val = 0",
             "    vitti c = 0",
             "    vitti d = 0",
             "    yadi (n == 0) { pratiyati 0 }",
             "    yadi (char_at(buf, 0) == 45) { neg = 1 }",
             "    yadi (neg == 1) { i = 1 }",
             "    yavat (i < n) {",
             "        c = char_at(buf, i)",
             "        d = 0 - 1",
             "        yadi (c >= 48) {",
             "            yadi (c <= 57) { d = c - 48 }",
             "        }",
             "        yadi (c >= 97) {",
             "            yadi (c <= 122) { d = c - 87 }",
             "        }",
             "        yadi (c >= 65) {",
             "            yadi (c <= 90) { d = c - 55 }",
             "        }",
             "        val = val * base + d",
             "        i = i + 1",
             "    }",
             "    yadi (neg == 1) { val = 0 - val }",
             "    pratiyati val",
             "}",
             "mukhya() {",
             "    vitti out = nirmmita(128)"]
    for v in vals:
        for b in bases:
            lines.append(f"    yadi (parse_base(out, fmt_int_base({v}, {b}, out), {b}) != {v}) {{")
            lines.append('        likha("FAIL fmt base roundtrip\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
    # uppercase hex round-trips through the same parser (A-F handled)
    lines.append("    yadi (parse_base(out, fmt_int_flags(255, 16, 2, out), 16) != 255) {")
    lines.append('        likha("FAIL fmt hex upper roundtrip\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # prefixed form: skip the 0x and parse the rest
    lines.append("    vitti pn = fmt_int_pre(255, 16, 0, out)")
    lines.append("    yadi (parse_base(out + 2, pn - 2, 16) != 255) {")
    lines.append('        likha("FAIL fmt prefix skip\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # flags 3 = prefix + upper: skip 0x, parse "FF"
    lines.append("    vitti pn3 = fmt_int_flags(255, 16, 3, out)")
    lines.append("    yadi (parse_base(out + 2, pn3 - 2, 16) != 255) {")
    lines.append('        likha("FAIL fmt hex prefix roundtrip\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (fmt_int_base(255, 1, out) != 0) {")
    lines.append('        likha("FAIL fmt bad base low\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (fmt_int_base(255, 37, out) != 0) {")
    lines.append('        likha("FAIL fmt bad base high\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "fmt_base", "\n".join(lines))
    return ok and out == "PASS", out


def prop_fmt_pad_content(compiler, rng):
    """padding never changes the non-pad content; length == max(width, n)"""
    cases = []
    for _ in range(6):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(1, 5)))
        w = rng.randint(0, len(s) + 4)
        cases.append((s, w))
    lines = ["ayojan fmt",
             "prakriya bytes_match_at(buf, off, lit, ln) {",
             "    vitti i = 0",
             "    yavat (i < ln) {",
             "        yadi (char_at(buf, off + i) != char_at(lit, i)) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "prakriya all_fill(buf, n, byte) {",
             "    vitti i = 0",
             "    yavat (i < n) {",
             "        yadi (char_at(buf, i) != byte) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "mukhya() {",
             "    vitti out = nirmmita(64)"]
    for s, w in cases:
        n = len(s)
        exp_len = max(w, n)
        pad = w - n if w > n else 0
        left = pad // 2
        # pad_left: content at offset pad, fill before it
        lines.append(f'    yadi (fmt_pad_left("{s}", {n}, {w}, 42, out) != {exp_len}) {{')
        lines.append('        likha("FAIL fmt pad_left len\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f'    yadi (bytes_match_at(out, {pad}, "{s}", {n}) == 0) {{')
        lines.append('        likha("FAIL fmt pad_left content\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        if pad:
            lines.append(f'    yadi (all_fill(out, {pad}, 42) == 0) {{')
            lines.append('        likha("FAIL fmt pad_left fill\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
        # pad_right: content at 0, fill after it
        lines.append(f'    yadi (fmt_pad_right("{s}", {n}, {w}, 42, out) != {exp_len}) {{')
        lines.append('        likha("FAIL fmt pad_right len\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f'    yadi (bytes_match_at(out, 0, "{s}", {n}) == 0) {{')
        lines.append('        likha("FAIL fmt pad_right content\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        # pad_center: content at offset left
        lines.append(f'    yadi (fmt_pad_center("{s}", {n}, {w}, 42, out) != {exp_len}) {{')
        lines.append('        likha("FAIL fmt pad_center len\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f'    yadi (bytes_match_at(out, {left}, "{s}", {n}) == 0) {{')
        lines.append('        likha("FAIL fmt pad_center content\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "fmt_pad", "\n".join(lines))
    return ok and out == "PASS", out


def _fmt_group_py(digits, indian):
    """Python mirror of the grouping rules, digits only (no sign/dot)."""
    if len(digits) <= 3:
        return digits
    parts = []
    if indian:
        # rightmost group 3, then 2s
        rest = digits[:-3]
        parts.append(digits[-3:])
        while rest:
            parts.append(rest[-2:])
            rest = rest[:-2]
    else:
        rest = digits
        while len(rest) > 3:
            parts.append(rest[-3:])
            rest = rest[:-3]
        parts.append(rest)
    return ",".join(reversed(parts))


def prop_fmt_group_digits(compiler, rng):
    """grouping never alters the digits; strip commas == original;
    grouped output matches Python grouping"""
    cases = ["0", "12", "123", "1234", "12345", "123456", "1234567",
             "12345678", "-1234567", "1234567.89", "-12.5"]
    lines = ["ayojan fmt",
             "prakriya strip_commas(src, sn, out) {",
             "    vitti i = 0",
             "    vitti w = 0",
             "    yavat (i < sn) {",
             "        yadi (char_at(src, i) != 44) {",
             "            set_char(out, w, char_at(src, i))",
             "            w = w + 1",
             "        }",
             "        i = i + 1",
             "    }",
             "    set_char(out, w, 0)",
             "    pratiyati w",
             "}",
             "prakriya bytes_match(buf, n, lit, ln) {",
             "    vitti i = 0",
             "    yadi (n != ln) { pratiyati 0 }",
             "    yavat (i < n) {",
             "        yadi (char_at(buf, i) != char_at(lit, i)) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "mukhya() {",
             "    vitti out = nirmmita(64)",
             "    vitti stripped = nirmmita(64)"]
    for ci, s in enumerate(cases):
        n = len(s)
        sign = ""
        body = s
        if s[:1] in ("-", "+"):
            sign, body = s[0], s[1:]
        if "." in body:
            intpart, frac = body.split(".")
            exp_in = sign + _fmt_group_py(intpart, True) + "." + frac
            exp_intl = sign + _fmt_group_py(intpart, False) + "." + frac
        else:
            exp_in = sign + _fmt_group_py(body, True)
            exp_intl = sign + _fmt_group_py(body, False)
        for fi, (fn, exp) in enumerate((("fmt_group_indian", exp_in),
                                     ("fmt_group_intl", exp_intl))):
            lines.append(f'    vitti gn{ci}_{fi} = {fn}("{s}", {n}, out)')
            lines.append(f'    yadi (bytes_match(out, gn{ci}_{fi}, "{exp}", {len(exp)}) == 0) {{')
            lines.append('        likha("FAIL fmt group content\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
            lines.append(f"    vitti sn2_{ci}_{fi} = strip_commas(out, gn{ci}_{fi}, stripped)")
            lines.append(f'    yadi (bytes_match(stripped, sn2_{ci}_{fi}, "{s}", {n}) == 0) {{')
            lines.append('        likha("FAIL fmt group digits\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
    # fmt_group_int agrees with Python on plain integers
    for gi, v in enumerate([0, 999, 1234, -1234567, 1000000]):
        for indian in (0, 1):
            exp = ("-" if v < 0 else "") + _fmt_group_py(str(abs(v)), bool(indian))
            lines.append(f"    vitti gin{gi}_{indian} = fmt_group_int({v}, {indian}, out)")
            lines.append(f'    yadi (bytes_match(out, gin{gi}_{indian}, "{exp}", {len(exp)}) == 0) {{')
            lines.append('        likha("FAIL fmt group_int\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "fmt_grp", "\n".join(lines))
    return ok and out == "PASS", out


def prop_fmt_fixed(compiler, rng):
    """fmt_fixed matches Python half-away-from-zero formatting"""
    cases = [(0.0, 2), (1.5, 0), (2.5, 0), (-2.5, 0), (3.14159, 2),
             (-0.004, 2), (100.0, 3), (0.125, 2), (999.999, 2),
             (-0.5, 0), (7.25, 1), (-7.25, 1)]
    lines = ["ayojan fmt",
             "prakriya bytes_match(buf, n, lit, ln) {",
             "    vitti i = 0",
             "    yadi (n != ln) { pratiyati 0 }",
             "    yavat (i < n) {",
             "        yadi (char_at(buf, i) != char_at(lit, i)) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "mukhya() {",
             "    vitti out = nirmmita(64)"]
    for ci, (x, places) in enumerate(cases):
        exp = _fmt_half_away(x, places)
        lines.append(f"    vitti fn{ci} = fmt_fixed({x!r}, {places}, out)")
        lines.append(f'    yadi (bytes_match(out, fn{ci}, "{exp}", {len(exp)}) == 0) {{')
        lines.append('        likha("FAIL fmt_fixed\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        exp_s = "+" + exp if x >= 0 else exp
        lines.append(f"    vitti fs{ci} = fmt_fixed_signed({x!r}, {places}, out)")
        lines.append(f'    yadi (bytes_match(out, fs{ci}, "{exp_s}", {len(exp_s)}) == 0) {{')
        lines.append('        likha("FAIL fmt_fixed_signed\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "fmt_fixed", "\n".join(lines))
    return ok and out == "PASS", out


def prop_fmt_signed(compiler, rng):
    """fmt_signed / fmt_sign_char match Python sign + digits"""
    vals = [0, 1, -1, 42, -42, 99999, -99999]
    lines = ["ayojan fmt",
             "prakriya bytes_match(buf, n, lit, ln) {",
             "    vitti i = 0",
             "    yadi (n != ln) { pratiyati 0 }",
             "    yavat (i < n) {",
             "        yadi (char_at(buf, i) != char_at(lit, i)) { pratiyati 0 }",
             "        i = i + 1",
             "    }",
             "    pratiyati 1",
             "}",
             "mukhya() {",
             "    vitti out = nirmmita(64)"]
    for ci, v in enumerate(vals):
        exp = ("+" if v >= 0 else "-") + str(abs(v))
        exp_sp = (" " if v >= 0 else "-") + str(abs(v))
        lines.append(f"    vitti sn{ci} = fmt_signed({v}, out)")
        lines.append(f'    yadi (bytes_match(out, sn{ci}, "{exp}", {len(exp)}) == 0) {{')
        lines.append('        likha("FAIL fmt_signed\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    vitti sc{ci} = fmt_sign_char({v}, 32, out)")
        lines.append(f'    yadi (bytes_match(out, sc{ci}, "{exp_sp}", {len(exp_sp)}) == 0) {{')
        lines.append('        likha("FAIL fmt_sign_char\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "fmt_sign", "\n".join(lines))
    return ok and out == "PASS", out


def prop_list_push_get(compiler, rng):
    """push N values (past initial capacity), get(i) == pushed[i], len == N"""
    vals = [rng.randint(-100, 100) for _ in range(12)] + [0]
    lines = ["ayojan list",
             "mukhya() {",
             "    vitti l = list_init(2)"]
    for v in vals:
        lines.append(f"    yadi (list_push(l, {v}) != 1) {{")
        lines.append('        likha("FAIL list push\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append(f"    yadi (list_len(l) != {len(vals)}) {{")
    lines.append('        likha("FAIL list len\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for i, v in enumerate(vals):
        lines.append(f"    yadi (list_get(l, {i}) != {v}) {{")
        lines.append('        likha("FAIL list get\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "list_pg", "\n".join(lines))
    return ok and out == "PASS", out


def prop_list_stack_lifo(compiler, rng):
    """stack pops come back in reverse push order; peek is non-destructive;
    pop/peek on empty give ok 0"""
    vals = [rng.randint(-100, 100) for _ in range(8)]
    lines = ["ayojan list",
             "mukhya() {",
             "    vitti s = list_init(1)",
             "    vitti ok = nirmmita(8)"]
    for v in vals:
        lines.append(f"    yadi (stack_push(s, {v}) != 1) {{")
        lines.append('        likha("FAIL stack push\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append(f"    yadi (stack_peek(s, ok) != {vals[-1]}) {{")
    lines.append('        likha("FAIL stack peek value\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 1) {")
    lines.append('        likha("FAIL stack peek ok\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (list_len(s) != {len(vals)}) {{")
    lines.append('        likha("FAIL stack peek removed\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for i, v in enumerate(reversed(vals)):
        lines.append(f"    vitti p{i} = stack_pop(s, ok)")
        lines.append(f"    yadi (p{i} != {v}) {{")
        lines.append('        likha("FAIL stack LIFO\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append("    yadi (ok[0] != 1) {")
        lines.append('        likha("FAIL stack pop ok\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    yadi (stack_empty(s) != 1) {")
    lines.append('        likha("FAIL stack empty\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    vitti pe = stack_pop(s, ok)")
    lines.append("    yadi (ok[0] != 0) {")
    lines.append('        likha("FAIL stack pop empty ok\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    vitti pk = stack_peek(s, ok)")
    lines.append("    yadi (ok[0] != 0) {")
    lines.append('        likha("FAIL stack peek empty ok\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "list_st", "\n".join(lines))
    return ok and out == "PASS", out


def prop_list_queue_fifo(compiler, rng):
    """queue dequeues come back in enqueue order, across wrap-around and
    growth; peek is non-destructive; dequeue/peek on empty give ok 0"""
    from collections import deque
    # scenario 1: deterministic wrap + grow
    # scenario 2: randomized ops against a deque model
    lines = ["ayojan list",
             "mukhya() {",
             "    vitti q = queue_init(2)",
             "    vitti ok = nirmmita(8)"]
    lines.append("    yadi (queue_enqueue(q, 1) != 1) {")
    lines.append('        likha("FAIL queue enqueue\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (queue_enqueue(q, 2) != 1) {")
    lines.append('        likha("FAIL queue enqueue\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    vitti d0 = queue_dequeue(q, ok)")
    lines.append("    yadi (d0 != 1) {")
    lines.append('        likha("FAIL queue FIFO 1\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (queue_enqueue(q, 3) != 1) {")
    lines.append('        likha("FAIL queue enqueue wrap\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (queue_enqueue(q, 4) != 1) {")
    lines.append('        likha("FAIL queue enqueue grow\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (queue_peek(q, ok) != 2) {")
    lines.append('        likha("FAIL queue peek\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (queue_len(q) != 3) {")
    lines.append('        likha("FAIL queue peek removed\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for i, v in enumerate((2, 3, 4)):
        lines.append(f"    vitti d{i + 1} = queue_dequeue(q, ok)")
        lines.append(f"    yadi (d{i + 1} != {v}) {{")
        lines.append('        likha("FAIL queue FIFO 2\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    yadi (queue_empty(q) != 1) {")
    lines.append('        likha("FAIL queue empty\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    vitti de = queue_dequeue(q, ok)")
    lines.append("    yadi (ok[0] != 0) {")
    lines.append('        likha("FAIL queue dequeue empty ok\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    vitti pk = queue_peek(q, ok)")
    lines.append("    yadi (ok[0] != 0) {")
    lines.append('        likha("FAIL queue peek empty ok\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # scenario 2: randomized
    model = deque()
    lines.append("    vitti q2 = queue_init(3)")
    n_ops = 0
    for step in range(30):
        if not model or rng.random() < 0.55:
            v = rng.randint(-50, 50)
            model.append(v)
            lines.append(f"    yadi (queue_enqueue(q2, {v}) != 1) {{")
            lines.append('        likha("FAIL queue rand enqueue\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
        else:
            v = model.popleft()
            lines.append(f"    vitti r{n_ops} = queue_dequeue(q2, ok)")
            lines.append(f"    yadi (r{n_ops} != {v}) {{")
            lines.append('        likha("FAIL queue rand FIFO\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
            lines.append("    yadi (ok[0] != 1) {")
            lines.append('        likha("FAIL queue rand ok\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
            n_ops += 1
        lines.append(f"    yadi (queue_len(q2) != {len(model)}) {{")
        lines.append('        likha("FAIL queue rand len\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "list_qu", "\n".join(lines))
    return ok and out == "PASS", out


def prop_list_len_tracks(compiler, rng):
    """list_len tracks pushes, inserts, removes and clear exactly"""
    lines = ["ayojan list",
             "mukhya() {",
             "    vitti l = list_init(1)"]
    expected = 0

    def check_len():
        lines.append(f"    yadi (list_len(l) != {expected}) {{")
        lines.append('        likha("FAIL list len tracks\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")

    check_len()
    for v in (5, 6, 7):
        lines.append(f"    list_push(l, {v})")
        expected += 1
        check_len()
    lines.append("    list_insert_at(l, 1, 99)")
    expected += 1
    check_len()
    lines.append("    list_remove_at(l, 0)")
    expected -= 1
    check_len()
    lines.append("    list_remove_at(l, 2)")
    expected -= 1
    check_len()
    lines.append("    list_clear(l)")
    expected = 0
    check_len()
    lines.append("    list_push(l, 42)")
    expected = 1
    check_len()
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "list_len", "\n".join(lines))
    return ok and out == "PASS", out


def prop_list_insert_remove(compiler, rng):
    """insert/remove preserve the rest: full contents match a Python list;
    contains / index_of agree with Python"""
    model = []
    lines = ["ayojan list",
             "mukhya() {",
             "    vitti l = list_init(2)"]
    for step in range(20):
        r = rng.random()
        if not model or r < 0.5:
            v = rng.randint(0, 9)
            i = rng.randint(0, len(model))
            model.insert(i, v)
            lines.append(f"    yadi (list_insert_at(l, {i}, {v}) != 1) {{")
            lines.append('        likha("FAIL list insert\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
        else:
            i = rng.randrange(len(model))
            del model[i]
            lines.append(f"    yadi (list_remove_at(l, {i}) != 1) {{")
            lines.append('        likha("FAIL list remove\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
        lines.append(f"    yadi (list_len(l) != {len(model)}) {{")
        lines.append('        likha("FAIL list insert/remove len\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    for j, v in enumerate(model):
        lines.append(f"    yadi (list_get(l, {j}) != {v}) {{")
        lines.append('        likha("FAIL list insert/remove content\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    for v in range(12):
        want_c = 1 if v in model else 0
        want_i = model.index(v) if v in model else -1
        lines.append(f"    yadi (list_contains(l, {v}) != {want_c}) {{")
        lines.append('        likha("FAIL list contains\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (list_index_of(l, {v}) != {want_i}) {{")
        lines.append('        likha("FAIL list index_of\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "list_ir", "\n".join(lines))
    return ok and out == "PASS", out


def prop_map_keys_bytes_roundtrip(compiler, rng):
    """map_keys_bytes: every inserted key appears exactly once as a packed
    byte segment; count == map_size; total bytes add up; 33-byte keys
    truncate to 32; old cell-form map_keys agrees on the count"""
    fixed = ["a", "apple", "fig", "pear",
             "abcdefghijklmnopqrstuvwxyz123456",  # exactly 32
             "abcdefghijklmnopqrstuvwxyz1234567"]  # 33 -> truncates to 32
    rand_keys = ["".join(rng.choice("abcde") for _ in range(rng.randint(1, 8)))
                 for _ in range(rng.randint(0, 6))]
    all_keys = fixed + rand_keys
    # distinct keys after 32-byte truncation (re-put updates, no dup)
    seen = []
    for k in all_keys:
        t = k[:32]
        if t not in seen:
            seen.append(t)
    cap = 32
    lines = ["ayojan map",
             "ayojan strb",
             "prakriya seg_count(buf, nk, key, keyn) {",
             "    vitti pos = 0",
             "    vitti i = 0",
             "    vitti seglen = 0",
             "    vitti c = 0",
             "    yavat (i < nk) {",
             "        seglen = char_at(buf, pos)",
             "        yadi (seglen == keyn) {",
             "            yadi (strb_compare(buf + pos + 1, seglen, key, keyn) == 0) { c = c + 1 }",
             "        }",
             "        pos = pos + 1 + seglen",
             "        i = i + 1",
             "    }",
             "    pratiyati c",
             "}",
             "mukhya() {",
             f"    vitti m = map_init({cap})",
             f"    vitti tmp = nirmmita({cap} * 33 + 1)",
             f"    vitti cells = nirmmita(({cap} * 33 + 1) * 8)"]
    for k in all_keys:
        lines.append(f'    map_put(m, {cap}, "{k}", {len(k)}, 1)')
    lines.append("    vitti nk = map_keys_bytes(m, tmp)")
    lines.append(f"    yadi (nk != {len(seen)}) {{")
    lines.append('        likha("FAIL keys_bytes count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (nk != map_size(m)) {")
    lines.append('        likha("FAIL keys_bytes vs size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (map_keys(m, cells) != nk) {")
    lines.append('        likha("FAIL keys_bytes vs keys count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in seen:
        lines.append(f'    yadi (seg_count(tmp, nk, "{k}", {len(k)}) != 1) {{')
        lines.append('        likha("FAIL keys_bytes exactly once\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    total = sum(1 + len(k) for k in seen)
    lines.append("    vitti pos = 0")
    lines.append("    vitti i = 0")
    lines.append("    vitti tot = 0")
    lines.append("    yavat (i < nk) {")
    lines.append("        tot = tot + 1 + char_at(tmp, pos)")
    lines.append("        pos = pos + 1 + char_at(tmp, pos)")
    lines.append("        i = i + 1")
    lines.append("    }")
    lines.append(f"    yadi (tot != {total}) {{")
    lines.append('        likha("FAIL keys_bytes total bytes\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "keys_bytes", "\n".join(lines))
    return ok and out == "PASS", out


MIN64 = -(2 ** 63)
MAX64 = 2 ** 63 - 1


def _lit(v):
    if v == MIN64:
        return "(0 - 9223372036854775807) - 1"
    return str(v)


def _clamp(v):
    return max(MIN64, min(MAX64, v))


def _trunc_divmod(a, b):
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q, a - q * b


def prop_ganita_checked_add_sub(compiler, rng):
    """checked_add/sub ok flag + value agree with unbounded Python ints;
    ok 0 exactly on overflow, value 0 then"""
    cases = [(MAX64, 1), (MIN64, -1), (MAX64, -1), (MIN64, 1),
             (MAX64, MAX64), (MIN64, MIN64), (0, 0), (MAX64, 0),
             (MIN64, 0), (0, MIN64), (0, MAX64)]
    for _ in range(12):
        cases.append((rng.randint(-10 ** 6, 10 ** 6),
                      rng.randint(-10 ** 6, 10 ** 6)))
    for _ in range(6):
        cases.append((MAX64 - rng.randint(0, 100), rng.randint(0, 100)))
        cases.append((MIN64 + rng.randint(0, 100), -rng.randint(0, 100)))
    lines = ["ayojan ganita",
             "mukhya() {",
             "    vitti ok = nirmmita(8)"]
    for i, (a, b) in enumerate(cases):
        for op, fn, tag in (("+", "ganita_checked_add", "add"),
                            ("-", "ganita_checked_sub", "sub")):
            true = a + b if op == "+" else a - b
            want_ok = 1 if MIN64 <= true <= MAX64 else 0
            want_val = true if want_ok else 0
            lines.append(f"    vitti r{i}{tag} = {fn}({_lit(a)}, {_lit(b)}, ok)")
            lines.append(f"    yadi (ok[0] != {want_ok}) {{")
            lines.append(f'        likha("FAIL checked {op} ok\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
            lines.append(f"    yadi (r{i}{tag} != {_lit(want_val)}) {{")
            lines.append(f'        likha("FAIL checked {op} value\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gan_checked_as", "\n".join(lines))
    return ok and out == "PASS", out


def prop_ganita_checked_mul(compiler, rng):
    """checked_mul ok flag + value agree with unbounded Python ints"""
    cases = [(MAX64, 2), (MAX64, MAX64), (MIN64, -1), (MIN64, 2),
             (MIN64, -2), (MIN64, MIN64), (MAX64, -1), (0, MAX64),
             (1, MIN64), (-1, MIN64), (2 ** 32, 2 ** 32),
             (3037000500, 3037000500), (3037000499, 3037000499),
             (0, 0), (1, 1), (-1, -1)]
    for _ in range(12):
        cases.append((rng.randint(-10 ** 6, 10 ** 6),
                      rng.randint(-10 ** 6, 10 ** 6)))
    for _ in range(4):
        cases.append((rng.choice([2 ** rng.randint(1, 62),
                                  -(2 ** rng.randint(1, 62))]),
                      rng.randint(-1000, 1000)))
    lines = ["ayojan ganita",
             "mukhya() {",
             "    vitti ok = nirmmita(8)"]
    for i, (a, b) in enumerate(cases):
        true = a * b
        want_ok = 1 if MIN64 <= true <= MAX64 else 0
        want_val = true if want_ok else 0
        lines.append(f"    vitti m{i} = ganita_checked_mul({_lit(a)}, {_lit(b)}, ok)")
        lines.append(f"    yadi (ok[0] != {want_ok}) {{")
        lines.append('        likha("FAIL checked mul ok\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (m{i} != {_lit(want_val)}) {{")
        lines.append('        likha("FAIL checked mul value\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gan_checked_mul", "\n".join(lines))
    return ok and out == "PASS", out


def prop_ganita_checked_divmod(compiler, rng):
    """checked_div/mod agree with truncating Python division;
    ok 0 exactly on b == 0 or INT64_MIN / -1"""
    cases = [(MIN64, -1), (MIN64, 1), (MAX64, -1), (7, 0), (-7, 0),
             (0, 0), (-7, 2), (7, -2), (-7, -2), (7, 2), (0, 5),
             (5, 5), (MIN64, 2), (MAX64, 3)]
    for _ in range(12):
        cases.append((rng.randint(-10 ** 6, 10 ** 6),
                      rng.randint(-10, 10)))
    lines = ["ayojan ganita",
             "mukhya() {",
             "    vitti ok = nirmmita(8)"]
    for i, (a, b) in enumerate(cases):
        bad = b == 0 or (a == MIN64 and b == -1)
        if bad:
            want_ok, want_q, want_r = 0, 0, 0
        else:
            want_ok = 1
            want_q, want_r = _trunc_divmod(a, b)
        lines.append(f"    vitti q{i} = ganita_checked_div({_lit(a)}, {_lit(b)}, ok)")
        lines.append(f"    yadi (ok[0] != {want_ok}) {{")
        lines.append('        likha("FAIL checked div ok\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (q{i} != {_lit(want_q)}) {{")
        lines.append('        likha("FAIL checked div value\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    vitti r{i} = ganita_checked_mod({_lit(a)}, {_lit(b)}, ok)")
        lines.append(f"    yadi (ok[0] != {want_ok}) {{")
        lines.append('        likha("FAIL checked mod ok\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (r{i} != {_lit(want_r)}) {{")
        lines.append('        likha("FAIL checked mod value\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gan_checked_dm", "\n".join(lines))
    return ok and out == "PASS", out


def prop_ganita_sat(compiler, rng):
    """sat_add/sub/mul equal Python results clamped to [MIN64, MAX64]"""
    cases = [(MAX64, 1), (MIN64, -1), (MAX64, -1), (MIN64, 1),
             (MAX64, MAX64), (MIN64, MIN64), (MIN64, -2),
             (MIN64, 2), (0, 0), (2, 3)]
    for _ in range(10):
        cases.append((rng.randint(-10 ** 6, 10 ** 6),
                      rng.randint(-10 ** 6, 10 ** 6)))
    lines = ["ayojan ganita",
             "mukhya() {"]
    for i, (a, b) in enumerate(cases):
        for op, fn in (("+", "ganita_sat_add"),
                       ("-", "ganita_sat_sub"),
                       ("*", "ganita_sat_mul")):
            true = {"+": a + b, "-": a - b, "*": a * b}[op]
            lines.append(f"    yadi ({fn}({_lit(a)}, {_lit(b)}) != {_lit(_clamp(true))}) {{")
            lines.append(f'        likha("FAIL sat {op}\\n")')
            lines.append("        pratiyati 1")
            lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gan_sat", "\n".join(lines))
    return ok and out == "PASS", out


def prop_map_clear_reuse(compiler, rng):
    """map_clear: size 0, old keys gone, whole buffer zeroed
    (state/keylen/val/key bytes), reuse in place, clear twice no-op"""
    pool = ["aa", "ab", "ba", "bb", "abc", "bca", "cab", "a", "b", "c"]
    old = rng.sample(pool, 5)
    new = rng.sample([k for k in pool if k not in old], 3)
    old_vals = {k: rng.randint(-100, 100) for k in old}
    new_vals = {k: rng.randint(-100, 100) for k in new}

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    lines = ["ayojan map",
             "mukhya() {",
             "    vitti m = map_init(16)",
             "    vitti keys = nirmmita(600)",
             "    vitti i = 0"]
    for k in old:
        lines.append(f'    map_put(m, 16, "{k}", {len(k)}, {lit(old_vals[k])})')
    lines.append("    map_clear(m)")
    lines.append("    yadi (map_size(m) != 0) {")
    lines.append('        likha("FAIL clear size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in old:
        lines.append(f'    yadi (map_contains(m, 16, "{k}", {len(k)}) != 0) {{')
        lines.append('        likha("FAIL clear contains\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    yadi (map_keys_bytes(m, keys) != 0) {")
    lines.append('        likha("FAIL clear keys\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # white-box: the whole buffer is zeroed (state/keylen/val/key bytes)
    lines.append("    yavat (i < 16) {")
    lines.append("        yadi (m[2 + i] != 0) {")
    lines.append('            likha("FAIL clear state\\n")')
    lines.append("            pratiyati 1")
    lines.append("        }")
    lines.append("        yadi (m[2 + 16 + i] != 0) {")
    lines.append('            likha("FAIL clear keylen\\n")')
    lines.append("            pratiyati 1")
    lines.append("        }")
    lines.append("        yadi (m[2 + 32 + i] != 0) {")
    lines.append('            likha("FAIL clear val\\n")')
    lines.append("            pratiyati 1")
    lines.append("        }")
    lines.append("        i = i + 1")
    lines.append("    }")
    lines.append("    i = 0")
    lines.append("    yavat (i < 512) {")
    lines.append("        yadi (char_at(m, 400 + i) != 0) {")
    lines.append('            likha("FAIL clear keybytes\\n")')
    lines.append("            pratiyati 1")
    lines.append("        }")
    lines.append("        i = i + 1")
    lines.append("    }")
    # reuse in place: new keys land, old keys stay absent
    for k in new:
        lines.append(f'    map_put(m, 16, "{k}", {len(k)}, {lit(new_vals[k])})')
    lines.append(f"    yadi (map_size(m) != {len(new)}) {{")
    lines.append('        likha("FAIL reuse size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in new:
        lines.append(f'    yadi (map_get(m, 16, "{k}", {len(k)}) != {lit(new_vals[k])}) {{')
        lines.append('        likha("FAIL reuse get\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    for k in old:
        lines.append(f'    yadi (map_contains(m, 16, "{k}", {len(k)}) != 0) {{')
        lines.append('        likha("FAIL reuse old\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    # clear twice is a no-op; clearing an empty map too
    lines.append("    map_clear(m)")
    lines.append("    map_clear(m)")
    lines.append("    yadi (map_size(m) != 0) {")
    lines.append('        likha("FAIL clear twice\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "map_clear", "\n".join(lines))
    return ok and out == "PASS", out


def prop_containers_clear(compiler, rng):
    """set_clear/list_clear/queue_clear: emptied, storage zeroed,
    reuse after clear works"""
    pool = ["aa", "ab", "ba", "bb", "abc", "bca", "cab", "a", "b", "c"]
    elems = rng.sample(pool, 4)
    vals = [rng.randint(-100, 100) for _ in range(4)]
    qvals = [rng.randint(-100, 100) for _ in range(3)]

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    lines = ["ayojan set",
             "ayojan list",
             "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti i = 0",
             "    vitti s = set_init(8)"]
    for k in elems:
        lines.append(f'    set_add(s, 8, "{k}", {len(k)})')
    lines.append("    set_clear(s)")
    lines.append("    yadi (set_size(s) != 0) {")
    lines.append('        likha("FAIL set clear size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in elems:
        lines.append(f'    yadi (set_contains(s, 8, "{k}", {len(k)}) != 0) {{')
        lines.append('        likha("FAIL set clear contains\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append(f'    set_add(s, 8, "{elems[0]}", {len(elems[0])})')
    lines.append("    yadi (set_size(s) != 1) {")
    lines.append('        likha("FAIL set reuse\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # list: len 0, data cells zeroed, push-after works
    lines.append("    vitti l = list_init(4)")
    lines.append("    vitti ld = l[2]")
    for v in vals:
        lines.append(f"    list_push(l, {lit(v)})")
    lines.append("    list_clear(l)")
    lines.append("    yadi (list_len(l) != 0) {")
    lines.append('        likha("FAIL list clear len\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yavat (i < 4) {")
    lines.append("        yadi (ld[i] != 0) {")
    lines.append('            likha("FAIL list clear data\\n")')
    lines.append("            pratiyati 1")
    lines.append("        }")
    lines.append("        i = i + 1")
    lines.append("    }")
    lines.append(f"    list_push(l, {lit(vals[0])})")
    lines.append(f"    yadi (list_get(l, 0) != {lit(vals[0])}) {{")
    lines.append('        likha("FAIL list reuse\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # queue: len 0, dequeue ok 0, ring data zeroed, reuse works
    lines.append("    vitti q = queue_init(4)")
    lines.append("    vitti qd = q[2]")
    for v in qvals:
        lines.append(f"    queue_enqueue(q, {lit(v)})")
    lines.append("    queue_dequeue(q, ok)")
    lines.append("    queue_clear(q)")
    lines.append("    yadi (queue_len(q) != 0) {")
    lines.append('        likha("FAIL queue clear len\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (queue_dequeue(q, ok) != 0) {")
    lines.append('        likha("FAIL queue clear dequeue\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 0) {")
    lines.append('        likha("FAIL queue clear ok\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    i = 0")
    lines.append("    yavat (i < 4) {")
    lines.append("        yadi (qd[i] != 0) {")
    lines.append('            likha("FAIL queue clear data\\n")')
    lines.append("            pratiyati 1")
    lines.append("        }")
    lines.append("        i = i + 1")
    lines.append("    }")
    lines.append(f"    queue_enqueue(q, {lit(qvals[0])})")
    lines.append("    yadi (queue_dequeue(q, ok) != %s) {" % lit(qvals[0]))
    lines.append('        likha("FAIL queue reuse\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "containers_clear", "\n".join(lines))
    return ok and out == "PASS", out


def prop_gaps19(compiler, rng):
    """map_get_default / set_equals / strb_reverse / strb_count /
    ganita_checked_pow against Python"""
    pool = ["aa", "ab", "ba", "bb", "abc", "bca", "cab", "a", "b", "c"]
    present = rng.sample(pool, 4)
    absent = [k for k in pool if k not in present][:2]
    pvals = {k: rng.choice([-1, 0, rng.randint(-100, 100)]) for k in present}
    default = rng.choice([-1, 0, 99, rng.randint(-100, 100)])
    set_a = set(rng.sample(pool, rng.randint(0, 5)))
    set_b = set(rng.sample(pool, rng.randint(0, 5)))
    alpha = "abc"
    hay = "".join(rng.choice(alpha) for _ in range(rng.randint(0, 12)))
    needle = "".join(rng.choice(alpha) for _ in range(rng.randint(1, 3)))
    src = "".join(rng.choice(alpha) for _ in range(rng.randint(0, 8)))

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    # Python non-overlapping count
    cnt, pos = 0, 0
    while True:
        f = hay.find(needle, pos)
        if f < 0:
            break
        cnt += 1
        pos = f + len(needle)
    pow_cases = [(2, 10), (2, 63), (2, 62), (3, 40), (10, 18), (10, 19),
                 (-2, 3), (-2, 63), (-2, 64), (1, 1000), (0, 0), (0, 5),
                 (5, 0), (2, -1), (-1, 100), (-1, 101),
                 (rng.randint(-5, 5), rng.randint(0, 8))]
    lines = ["ayojan map",
             "ayojan set",
             "ayojan strb",
             "ayojan ganita",
             "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti m = map_init(16)"]
    for k in present:
        lines.append(f'    map_put(m, 16, "{k}", {len(k)}, {lit(pvals[k])})')
    for k in present:
        lines.append(f'    yadi (map_get_default(m, 16, "{k}", {len(k)}, {lit(default)}) != {lit(pvals[k])}) {{')
        lines.append('        likha("FAIL get_default present\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    for k in absent:
        lines.append(f'    yadi (map_get_default(m, 16, "{k}", {len(k)}, {lit(default)}) != {lit(default)}) {{')
        lines.append('        likha("FAIL get_default absent\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    # set_equals vs Python set equality
    lines.append("    vitti sa = set_init(8)")
    lines.append("    vitti sb = set_init(8)")
    for k in set_a:
        lines.append(f'    set_add(sa, 8, "{k}", {len(k)})')
    for k in set_b:
        lines.append(f'    set_add(sb, 8, "{k}", {len(k)})')
    want_eq = 1 if set_a == set_b else 0
    lines.append(f"    yadi (set_equals(sa, 8, sb, 8) != {want_eq}) {{")
    lines.append('        likha("FAIL set_equals\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # strb_reverse: reversed bytes + terminator
    lines.append("    vitti rout = nirmmita(32)")
    rev = src[::-1]
    lines.append(f'    yadi (strb_reverse("{src}", {len(src)}, rout) != {len(src)}) {{')
    lines.append('        likha("FAIL reverse ret\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for i, ch in enumerate(rev):
        lines.append(f"    yadi (char_at(rout, {i}) != {ord(ch)}) {{")
        lines.append('        likha("FAIL reverse bytes\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append(f"    yadi (char_at(rout, {len(src)}) != 0) {{")
    lines.append('        likha("FAIL reverse term\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # strb_count vs Python non-overlapping count
    lines.append(f'    yadi (strb_count("{hay}", {len(hay)}, "{needle}", {len(needle)}) != {cnt}) {{')
    lines.append('        likha("FAIL count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # ganita_checked_pow vs Python unbounded ints
    for a, e in pow_cases:
        if e < 0:
            want_ok, want_val = 0, 0
        else:
            true = a ** e
            want_ok = 1 if MIN64 <= true <= MAX64 else 0
            want_val = true if want_ok else 0
        lines.append(f"    yadi (ganita_checked_pow({lit(a)}, {lit(e)}, ok) != {lit(want_val)}) {{")
        lines.append('        likha("FAIL pow value\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (ok[0] != {want_ok}) {{")
        lines.append('        likha("FAIL pow ok\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gaps19", "\n".join(lines))
    return ok and out == "PASS", out


def prop_strb_cell_pairs(compiler, rng):
    """strb explicit-length forms + cell str_reverse/str_count vs Python"""
    alpha = "abcdeiouAEIOU019 "
    s = "".join(rng.choice(alpha) for _ in range(rng.randint(0, 12)))
    n = rng.randint(0, len(s)) if s else 0
    code = ord(rng.choice(alpha))
    t = "".join(rng.choice("abc") for _ in range(rng.randint(0, 8)))
    needle = "".join(rng.choice("abc") for _ in range(rng.randint(1, 3)))
    cells = [rng.randint(32, 122) for _ in range(rng.randint(0, 6))]
    ncells = [rng.randint(32, 122) for _ in range(rng.randint(1, 3))]

    def esc(x):
        return x.replace("\\", "\\\\").replace('"', '\\"')

    vowels = sum(1 for ch in s[:n] if ch in "aeiou")
    want_cc = s[:n].count(chr(code))
    want_fc = s[:n].find(chr(code))
    want_digits = 1 if n > 0 and s[:n].isdigit() else 0
    want_eq = 1 if s == t else 0
    # Python non-overlapping count over cell arrays
    cnt, pos = 0, 0
    while True:
        try:
            f = cells.index(ncells[0], pos)
        except ValueError:
            break
        if cells[f:f + len(ncells)] == ncells:
            cnt += 1
            pos = f + len(ncells)
        else:
            pos = f + 1
    lines = ["ayojan strb",
             "ayojan string",
             "mukhya() {",
             "    vitti out = nirmmita(64)",
             f'    vitti src = "{esc(s)}"',
             f'    vitti other = "{esc(t)}"',
             f"    vitti h = nirmmita({max(len(cells), 1)} * 8)",
             f"    vitti nd = nirmmita({len(ncells)} * 8)",
             "    vitti i = 0"]
    for i, c in enumerate(cells):
        lines.append(f"    h[{i}] = {c}")
    for i, c in enumerate(ncells):
        lines.append(f"    nd[{i}] = {c}")
    lines.append(f'    yadi (strb_count_vowels(src, {n}) != {vowels}) {{')
    lines.append('        likha("FAIL count_vowels\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f'    yadi (strb_count_char(src, {n}, {code}) != {want_cc}) {{')
    lines.append('        likha("FAIL count_char\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f'    yadi (strb_find_char(src, {n}, {code}) != {want_fc}) {{')
    lines.append('        likha("FAIL find_char\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f'    yadi (strb_is_all_digits(src, {n}) != {want_digits}) {{')
    lines.append('        likha("FAIL all_digits\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f'    yadi (strb_equals(src, {len(s)}, other, {len(t)}) != {want_eq}) {{')
    lines.append('        likha("FAIL strb_equals\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f'    yadi (str_reverse(h, {len(cells)}, out) != {len(cells)}) {{')
    lines.append('        likha("FAIL str_reverse ret\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for i, c in enumerate(cells[::-1]):
        lines.append(f"    yadi (out[{i}] != {c}) {{")
        lines.append('        likha("FAIL str_reverse cells\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append(f"    yadi (out[{len(cells)}] != 0) {{")
    lines.append('        likha("FAIL str_reverse term\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f'    yadi (str_count(h, {len(cells)}, nd, {len(ncells)}) != {cnt}) {{')
    lines.append('        likha("FAIL str_count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "strb_cell", "\n".join(lines))
    return ok and out == "PASS", out


def prop_containers_resize_swap(compiler, rng):
    """map_resize/set_resize/list_swap/list_reverse vs Python"""
    pool = ["aa", "ab", "ba", "bb", "abc", "bca", "cab", "a", "b", "c"]
    keys = rng.sample(pool, 5)
    vals = {k: rng.randint(-100, 100) for k in keys}
    skeys = rng.sample(pool, 4)
    lvals = [rng.randint(-100, 100) for _ in range(5)]
    i, j = rng.randint(0, 4), rng.randint(0, 4)

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    lines = ["ayojan map",
             "ayojan set",
             "ayojan list",
             "mukhya() {",
             "    vitti m = map_init(8)"]
    for k in keys:
        lines.append(f'    map_put(m, 8, "{k}", {len(k)}, {lit(vals[k])})')
    lines.append("    m = map_resize(m, 32)")
    lines.append("    yadi (m[0] != 32) {")
    lines.append('        likha("FAIL resize cap\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (map_size(m) != {len(keys)}) {{")
    lines.append('        likha("FAIL resize size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in keys:
        lines.append(f'    yadi (map_get(m, 32, "{k}", {len(k)}) != {lit(vals[k])}) {{')
        lines.append('        likha("FAIL resize get\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    yadi (map_resize(m, 1) != 0) {")
    lines.append('        likha("FAIL resize small\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (map_size(m) != {len(keys)}) {{")
    lines.append('        likha("FAIL resize small unchanged\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    vitti s = set_init(8)")
    for k in skeys:
        lines.append(f'    set_add(s, 8, "{k}", {len(k)})')
    lines.append("    s = set_resize(s, 32)")
    lines.append("    yadi (s[0] != 32) {")
    lines.append('        likha("FAIL set resize cap\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in skeys:
        lines.append(f'    yadi (set_contains(s, 32, "{k}", {len(k)}) != 1) {{')
        lines.append('        likha("FAIL set resize contains\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    vitti l = list_init(8)")
    for v in lvals:
        lines.append(f"    list_push(l, {lit(v)})")
    lines.append(f"    yadi (list_swap(l, {i}, {j}) != 1) {{")
    lines.append('        likha("FAIL swap ret\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    swapped = list(lvals)
    swapped[i], swapped[j] = swapped[j], swapped[i]
    for idx, v in enumerate(swapped):
        lines.append(f"    yadi (list_get(l, {idx}) != {lit(v)}) {{")
        lines.append('        likha("FAIL swap vals\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    yadi (list_swap(l, 0, 9) != 0) {")
    lines.append('        likha("FAIL swap oob\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (list_get(l, 0) != {lit(swapped[0])}) {{")
    lines.append('        likha("FAIL swap oob unchanged\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    list_reverse(l)")
    for idx, v in enumerate(swapped[::-1]):
        lines.append(f"    yadi (list_get(l, {idx}) != {lit(v)}) {{")
        lines.append('        likha("FAIL reverse\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "resize_swap", "\n".join(lines))
    return ok and out == "PASS", out


def prop_gaps20(compiler, rng):
    """ganita_checked_fact / ganita_sat_pow vs Python (incl. huge e
    for the saturating early-exit path)"""
    import math
    fact_cases = list(range(-2, 26)) + [rng.randint(0, 25)]
    pow_cases = [(2, 10), (2, 63), (2, 62), (3, 40), (3, 41),
                 (-2, 63), (-2, 64), (-2, 65), (-3, 41), (5, 0),
                 (0, 0), (0, 5), (1, 1000), (-1, 1001), (2, -1),
                 (2, 1000000), (-2, 1000000), (-2, 1000001),
                 (3, 100000), (-3, 100001),
                 (rng.randint(-5, 5), rng.randint(0, 10))]

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    lines = ["ayojan ganita",
             "mukhya() {",
             "    vitti ok = nirmmita(8)"]
    for n in fact_cases:
        if n < 0:
            want_ok, want_val = 0, 0
        else:
            true = math.factorial(n)
            want_ok = 1 if MIN64 <= true <= MAX64 else 0
            want_val = true if want_ok else 0
        lines.append(f"    yadi (ganita_checked_fact({lit(n)}, ok) != {lit(want_val)}) {{")
        lines.append('        likha("FAIL fact value\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (ok[0] != {want_ok}) {{")
        lines.append('        likha("FAIL fact ok\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    for a, e in pow_cases:
        if e < 0:
            want = 0
        else:
            want = _clamp(a ** e)
        lines.append(f"    yadi (ganita_sat_pow({lit(a)}, {lit(e)}) != {lit(want)}) {{")
        lines.append('        likha("FAIL sat_pow\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gaps20", "\n".join(lines))
    return ok and out == "PASS", out


def prop_containers21(compiler, rng):
    """list_sort/min/max/sum/count, queue_contains, map_values vs Python"""
    lvals = [rng.randint(-100, 100) for _ in range(rng.randint(0, 8))]
    qvals = [rng.randint(-100, 100) for _ in range(rng.randint(0, 5))]
    pool = ["aa", "ab", "ba", "bb", "abc", "bca", "cab", "a", "b", "c"]
    keys = rng.sample(pool, rng.randint(0, 5))
    mvals = {k: rng.randint(-100, 100) for k in keys}
    probe = rng.choice(qvals) if qvals and rng.random() < 0.7 else 999

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    lines = ["ayojan map",
             "ayojan list",
             "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti l = list_init(8)"]
    for v in lvals:
        lines.append(f"    list_push(l, {lit(v)})")
    want_min = min(lvals) if lvals else 0
    want_min_ok = 1 if lvals else 0
    want_max = max(lvals) if lvals else 0
    want_max_ok = 1 if lvals else 0
    lines.append(f"    yadi (list_min(l, ok) != {lit(want_min)}) {{")
    lines.append('        likha("FAIL list_min value\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (ok[0] != {want_min_ok}) {{")
    lines.append('        likha("FAIL list_min ok\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (list_max(l, ok) != {lit(want_max)}) {{")
    lines.append('        likha("FAIL list_max value\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (ok[0] != {want_max_ok}) {{")
    lines.append('        likha("FAIL list_max ok\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (list_sum(l) != {lit(sum(lvals))}) {{")
    lines.append('        likha("FAIL list_sum\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    probe_v = rng.choice(lvals) if lvals else 999
    lines.append(f"    yadi (list_count(l, {lit(probe_v)}) != {lvals.count(probe_v)}) {{")
    lines.append('        likha("FAIL list_count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    list_sort(l)")
    for idx, v in enumerate(sorted(lvals)):
        lines.append(f"    yadi (list_get(l, {idx}) != {lit(v)}) {{")
        lines.append('        likha("FAIL list_sort\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    # queue_contains: dequeue one first so the ring head has moved
    lines.append("    vitti q = queue_init(8)")
    for v in qvals:
        lines.append(f"    queue_enqueue(q, {lit(v)})")
    if qvals:
        lines.append("    queue_dequeue(q, ok)")
    remaining = qvals[1:] if qvals else []
    lines.append(f"    yadi (queue_contains(q, {lit(probe)}) != {1 if probe in remaining else 0}) {{")
    lines.append('        likha("FAIL queue_contains\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (queue_len(q) != %d) {" % len(remaining))
    lines.append('        likha("FAIL queue_contains len\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # map_values: count + order-independent sum (slot order is hash order)
    lines.append("    vitti m = map_init(8)")
    lines.append("    vitti vals = nirmmita(8 * 8)")
    lines.append("    vitti vsum = 0")
    lines.append("    vitti i = 0")
    for k in keys:
        lines.append(f'    map_put(m, 8, "{k}", {len(k)}, {lit(mvals[k])})')
    lines.append(f"    yadi (map_values(m, vals) != {len(keys)}) {{")
    lines.append('        likha("FAIL map_values count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yavat (i < {len(keys)}) {{")
    lines.append("        vsum = vsum + vals[i]")
    lines.append("        i = i + 1")
    lines.append("    }")
    lines.append(f"    yadi (vsum != {lit(sum(mvals.values()))}) {{")
    lines.append('        likha("FAIL map_values sum\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "containers21", "\n".join(lines))
    return ok and out == "PASS", out


def prop_gaps21(compiler, rng):
    """ganita_sat_fact vs clamped Python factorials (incl. huge n
    for the early-exit path)"""
    import math
    cases = list(range(-2, 26)) + [rng.randint(0, 30), 100, 100000]

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    lines = ["ayojan ganita",
             "mukhya() {"]
    for n in cases:
        if n < 0:
            want = 0
        else:
            want = _clamp(math.factorial(n))
        lines.append(f"    yadi (ganita_sat_fact({lit(n)}) != {lit(want)}) {{")
        lines.append('        likha("FAIL sat_fact\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gaps21", "\n".join(lines))
    return ok and out == "PASS", out


def prop_containers23(compiler, rng):
    """list_find/is_sorted/binary_search, queue_to_array vs Python"""
    lvals = [rng.randint(-50, 50) for _ in range(rng.randint(0, 9))]
    qvals = [rng.randint(-50, 50) for _ in range(rng.randint(0, 6))]

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    lines = ["ayojan list",
             "mukhya() {",
             "    vitti l = list_init(16)"]
    for v in lvals:
        lines.append(f"    list_push(l, {lit(v)})")
    probe = rng.choice(lvals) if lvals and rng.random() < 0.7 else 999
    want_find = lvals.index(probe) if probe in lvals else -1
    lines.append(f"    yadi (list_find(l, {lit(probe)}) != {want_find}) {{")
    lines.append('        likha("FAIL list_find\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    want_sorted = 1 if lvals == sorted(lvals) else 0
    lines.append(f"    yadi (list_is_sorted(l) != {want_sorted}) {{")
    lines.append('        likha("FAIL list_is_sorted pre\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    list_sort(l)")
    lines.append("    yadi (list_is_sorted(l) != 1) {")
    lines.append('        likha("FAIL list_is_sorted post\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    want_bs = sorted(lvals).index(probe) if probe in lvals else -1
    lines.append(f"    yadi (list_binary_search(l, {lit(probe)}) != {want_bs}) {{")
    lines.append('        likha("FAIL list_binary_search\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # queue_to_array: dequeue some first so the ring head has moved,
    # then compare the non-destructive read against Python order
    lines.append("    vitti q = queue_init(8)")
    lines.append("    vitti arr = nirmmita(8 * 8)")
    for v in qvals:
        lines.append(f"    queue_enqueue(q, {lit(v)})")
    ndq = rng.randint(0, len(qvals)) if qvals else 0
    for _ in range(ndq):
        lines.append("    queue_dequeue(q, nirmmita(8))")
    remaining = qvals[ndq:]
    lines.append(f"    yadi (queue_to_array(q, arr) != {len(remaining)}) {{")
    lines.append('        likha("FAIL queue_to_array count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for idx, v in enumerate(remaining):
        lines.append(f"    yadi (arr[{idx}] != {lit(v)}) {{")
        lines.append('        likha("FAIL queue_to_array order\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append(f"    yadi (queue_len(q) != {len(remaining)}) {{")
    lines.append('        likha("FAIL queue_to_array len\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "containers23", "\n".join(lines))
    return ok and out == "PASS", out


def prop_gaps23(compiler, rng):
    """map_merge / set_sym_diff vs Python (incl. a partial merge when
    the destination fills up)"""
    pool = ["aa", "ab", "ba", "bb", "abc", "bca", "cab", "a", "b", "c"]
    akeys = rng.sample(pool, rng.randint(0, 4))
    bkeys = rng.sample(pool, rng.randint(0, 4))
    avals = {k: rng.randint(-50, 50) for k in akeys}
    bvals = {k: rng.randint(-50, 50) for k in bkeys}

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    merged = dict(avals)
    merged.update(bvals)
    lines = ["ayojan map",
             "ayojan set",
             "mukhya() {",
             "    vitti a = map_init(8)",
             "    vitti b = map_init(8)",
             "    vitti dst = map_init(8)"]
    for k in akeys:
        lines.append(f'    map_put(a, 8, "{k}", {len(k)}, {lit(avals[k])})')
    for k in bkeys:
        lines.append(f'    map_put(b, 8, "{k}", {len(k)}, {lit(bvals[k])})')
    lines.append(f"    yadi (map_merge(dst, 8, a, 8) != {len(avals)}) {{")
    lines.append('        likha("FAIL map_merge count a\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (map_merge(dst, 8, b, 8) != {len(bvals)}) {{")
    lines.append('        likha("FAIL map_merge count b\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k, v in merged.items():
        lines.append(f'    yadi (map_get(dst, 8, "{k}", {len(k)}) != {lit(v)}) {{')
        lines.append('        likha("FAIL map_merge value\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    # partial merge: destination capacity 1 cannot hold all of b
    if bvals:
        lines.append("    vitti small = map_init(1)")
        lines.append("    yadi (map_merge(small, 1, b, 8) != 1) {")
        lines.append('        likha("FAIL map_merge partial\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append("    yadi (map_size(small) != 1) {")
        lines.append('        likha("FAIL map_merge partial size\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    # set symmetric difference
    s1 = set(akeys)
    s2 = set(bkeys)
    sym = s1 ^ s2
    lines.append("    vitti x = set_init(8)")
    lines.append("    vitti y = set_init(8)")
    lines.append("    vitti o = set_init(16)")
    for k in akeys:
        lines.append(f'    set_add(x, 8, "{k}", {len(k)})')
    for k in bkeys:
        lines.append(f'    set_add(y, 8, "{k}", {len(k)})')
    lines.append(f"    yadi (set_sym_diff(x, 8, y, 8, o) != {len(sym)}) {{")
    lines.append('        likha("FAIL set_sym_diff count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in sym:
        lines.append(f'    yadi (set_contains(o, 16, "{k}", {len(k)}) != 1) {{')
        lines.append('        likha("FAIL set_sym_diff member\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    for k in (s1 & s2):
        lines.append(f'    yadi (set_contains(o, 16, "{k}", {len(k)}) != 0) {{')
        lines.append('        likha("FAIL set_sym_diff excluded\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "gaps23", "\n".join(lines))
    return ok and out == "PASS", out


def prop_slices23(compiler, rng):
    """Explicit-length strb_* forms on random slices vs Python slices;
    the NUL-terminated forms see past the slice end (contrast)."""
    import string as _string
    alphabet = _string.ascii_lowercase + _string.digits + "   "
    full = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 20)))
    start = rng.randint(0, len(full)) if full else 0
    slen = rng.randint(0, len(full) - start) if full else 0
    sl = full[start:start + slen]
    code = rng.choice([ord("a"), ord(" "), ord("0"), ord("z")])

    def cstr(s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    lines = ["ayojan strb",
             "ayojan string",
             "mukhya() {",
             f"    vitti base = {cstr(full)}"]
    lines.append(f"    yadi (strb_find_char(base + {start}, {slen}, {code}) != {sl.find(chr(code))}) {{")
    lines.append('        likha("FAIL strb_find_char slice\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (strb_count_char(base + {start}, {slen}, {code}) != {sl.count(chr(code))}) {{")
    lines.append('        likha("FAIL strb_count_char slice\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    want_vowels = sum(1 for ch in sl if ch in "aeiou")
    lines.append(f"    yadi (strb_count_vowels(base + {start}, {slen}) != {want_vowels}) {{")
    lines.append('        likha("FAIL strb_count_vowels slice\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    want_digits = 1 if slen > 0 and all(ch.isdigit() for ch in sl) else 0
    lines.append(f"    yadi (strb_is_all_digits(base + {start}, {slen}) != {want_digits}) {{")
    lines.append('        likha("FAIL strb_is_all_digits slice\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    # slice repl workaround: dup the slice, use it as repl
    # ("ab" with "b" replaced by the slice = "a" + slice)
    lines.append("    vitti tmp = nirmmita(64)")
    lines.append("    vitti out = nirmmita(64)")
    lines.append(f"    strb_dup(base + {start}, {slen}, tmp)")
    want_repl = "a" + sl
    lines.append(f"    yadi (strb_replace(\"ab\", 2, \"b\", 1, tmp, out) != {len(want_repl)}) {{")
    lines.append('        likha("FAIL slice repl len\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (strb_equals(out, {len(want_repl)}, {cstr(want_repl)}, {len(want_repl)}) != 1) {{")
    lines.append('        likha("FAIL slice repl content\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "slices23", "\n".join(lines))
    return ok and out == "PASS", out


def prop_invariants24_containers(compiler, rng):
    """R23 cross-function invariants: binary_search agrees with find
    on a sorted list; queue_to_array does not mutate (same read twice,
    and dequeue afterwards still yields the first element)."""
    lvals = [rng.randint(-50, 50) for _ in range(rng.randint(0, 9))]
    qvals = [rng.randint(-50, 50) for _ in range(rng.randint(0, 6))]

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    lines = ["ayojan list",
             "mukhya() {",
             "    vitti l = list_init(16)",
             "    vitti ok = nirmmita(8)"]
    for v in lvals:
        lines.append(f"    list_push(l, {lit(v)})")
    lines.append("    list_sort(l)")
    for _ in range(3):
        probe = rng.choice(lvals) if lvals and rng.random() < 0.7 else 999
        lines.append(f"    yadi (list_binary_search(l, {lit(probe)}) != list_find(l, {lit(probe)})) {{")
        lines.append('        likha("FAIL binary_search != find\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    vitti q = queue_init(8)")
    lines.append("    vitti a1 = nirmmita(8 * 8)")
    lines.append("    vitti a2 = nirmmita(8 * 8)")
    for v in qvals:
        lines.append(f"    queue_enqueue(q, {lit(v)})")
    lines.append("    yadi (queue_to_array(q, a1) != queue_to_array(q, a2)) {")
    lines.append('        likha("FAIL to_array count\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    vitti i = 0")
    lines.append(f"    yavat (i < {len(qvals)}) {{")
    lines.append("        yadi (a1[i] != a2[i]) {")
    lines.append('            likha("FAIL to_array repeat\\n")')
    lines.append("            pratiyati 1")
    lines.append("        }")
    lines.append("        i = i + 1")
    lines.append("    }")
    if qvals:
        lines.append("    yadi (queue_dequeue(q, ok) != a1[0]) {")
        lines.append('        likha("FAIL to_array mutated\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (queue_len(q) != {len(qvals) - 1}) {{")
        lines.append('        likha("FAIL to_array len\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "invariants24_containers", "\n".join(lines))
    return ok and out == "PASS", out


def prop_invariants24_merge_symdiff(compiler, rng):
    """R23 cross-function invariants: map_merge is associative
    (src-wins), set_sym_diff is symmetric, sym_diff with itself is
    empty, sym_diff with empty is identity."""
    pool = ["aa", "ab", "ba", "bb", "abc", "bca", "cab", "a", "b", "c"]
    akeys = rng.sample(pool, rng.randint(0, 3))
    bkeys = rng.sample(pool, rng.randint(0, 3))
    ckeys = rng.sample(pool, rng.randint(0, 3))
    avals = {k: rng.randint(-50, 50) for k in akeys}
    bvals = {k: rng.randint(-50, 50) for k in bkeys}
    cvals = {k: rng.randint(-50, 50) for k in ckeys}

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    merged = dict(avals)
    merged.update(bvals)
    merged.update(cvals)
    lines = ["ayojan map",
             "ayojan set",
             "mukhya() {"]
    # three maps a, b, c; merge both associations and compare
    for name, vals in (("a", avals), ("b", bvals), ("c", cvals)):
        lines.append(f"    vitti {name} = map_init(8)")
        for k, v in vals.items():
            lines.append(f'    map_put({name}, 8, "{k}", {len(k)}, {lit(v)})')
    lines.append("    vitti m1 = map_init(16)")
    lines.append("    vitti m2 = map_init(16)")
    lines.append("    vitti tmp = map_init(16)")
    lines.append("    vitti tmp2 = map_init(16)")
    lines.append("    map_merge(tmp, 16, a, 8)")
    lines.append("    map_merge(tmp, 16, b, 8)")
    lines.append("    map_merge(m1, 16, tmp, 16)")
    lines.append("    map_merge(m1, 16, c, 8)")
    lines.append("    map_merge(tmp2, 16, b, 8)")
    lines.append("    map_merge(tmp2, 16, c, 8)")
    lines.append("    map_merge(m2, 16, a, 8)")
    lines.append("    map_merge(m2, 16, tmp2, 16)")
    lines.append(f"    yadi (map_size(m1) != {len(merged)}) {{")
    lines.append('        likha("FAIL merge assoc size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append("    yadi (map_size(m1) != map_size(m2)) {")
    lines.append('        likha("FAIL merge assoc size2\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k, v in merged.items():
        lines.append(f'    yadi (map_get(m1, 16, "{k}", {len(k)}) != map_get(m2, 16, "{k}", {len(k)})) {{')
        lines.append('        likha("FAIL merge assoc value\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f'    yadi (map_get(m1, 16, "{k}", {len(k)}) != {lit(v)}) {{')
        lines.append('        likha("FAIL merge src-wins\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    # symmetric difference: symmetric, self-empty, identity-with-empty
    for name, keys in (("x", akeys), ("y", bkeys)):
        lines.append(f"    vitti {name} = set_init(8)")
        for k in keys:
            lines.append(f'    set_add({name}, 8, "{k}", {len(k)})')
    lines.append("    vitti o1 = set_init(16)")
    lines.append("    vitti o2 = set_init(16)")
    lines.append("    vitti o3 = set_init(16)")
    lines.append("    vitti o4 = set_init(16)")
    lines.append("    vitti e = set_init(8)")
    lines.append("    set_sym_diff(x, 8, y, 8, o1)")
    lines.append("    set_sym_diff(y, 8, x, 8, o2)")
    lines.append("    set_sym_diff(x, 8, x, 8, o3)")
    lines.append("    set_sym_diff(x, 8, e, 8, o4)")
    lines.append("    yadi (set_size(o1) != set_size(o2)) {")
    lines.append('        likha("FAIL sym_diff symmetric size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    sym = set(akeys) ^ set(bkeys)
    for k in sym:
        lines.append(f'    yadi (set_contains(o2, 16, "{k}", {len(k)}) != 1) {{')
        lines.append('        likha("FAIL sym_diff symmetric member\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append("    yadi (set_size(o3) != 0) {")
    lines.append('        likha("FAIL sym_diff self\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    lines.append(f"    yadi (set_size(o4) != {len(set(akeys))}) {{")
    lines.append('        likha("FAIL sym_diff identity size\\n")')
    lines.append("        pratiyati 1")
    lines.append("    }")
    for k in akeys:
        lines.append(f'    yadi (set_contains(o4, 16, "{k}", {len(k)}) != 1) {{')
        lines.append('        likha("FAIL sym_diff identity member\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "invariants24_merge_symdiff", "\n".join(lines))
    return ok and out == "PASS", out


def prop_safety24(compiler, rng):
    """ganita_sat_div/sat_mod/checked_abs/sat_abs vs Python (incl.
    MIN/-1, division by zero, abs(MIN))."""
    import random as _random
    maxv = 2**63 - 1
    minv = -(2**63)
    pairs = []
    for _ in range(6):
        a = rng.choice([rng.randint(-100, 100), maxv, minv, 0, 1, -1])
        b = rng.choice([rng.randint(-10, 10), maxv, minv, 0, 1, -1])
        pairs.append((a, b))
    singles = [rng.randint(-100, 100) for _ in range(3)] + [maxv, minv, 0]

    def lit(v):
        return f"(0 - {-v})" if v < 0 else str(v)

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return q if (a < 0) == (b < 0) else -q

    lines = ["ayojan ganita",
             "mukhya() {",
             "    vitti ok = nirmmita(8)"]
    for a, b in pairs:
        if b == 0:
            want_div, want_mod = 0, 0
        elif a == minv and b == -1:
            want_div, want_mod = maxv, 0
        else:
            want_div = trunc_div(a, b)
            want_mod = a - trunc_div(a, b) * b
        lines.append(f"    yadi (ganita_sat_div({lit(a)}, {lit(b)}) != {lit(want_div)}) {{")
        lines.append('        likha("FAIL sat_div\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (ganita_sat_mod({lit(a)}, {lit(b)}) != {lit(want_mod)}) {{")
        lines.append('        likha("FAIL sat_mod\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    for a in singles:
        if a == minv:
            want_cabs, want_cok, want_sabs = 0, 0, maxv
        else:
            want_cabs, want_cok, want_sabs = abs(a), 1, abs(a)
        lines.append(f"    yadi (ganita_checked_abs({lit(a)}, ok) != {lit(want_cabs)}) {{")
        lines.append('        likha("FAIL checked_abs value\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (ok[0] != {want_cok}) {{")
        lines.append('        likha("FAIL checked_abs ok\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
        lines.append(f"    yadi (ganita_sat_abs({lit(a)}) != {lit(want_sabs)}) {{")
        lines.append('        likha("FAIL sat_abs\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "safety24", "\n".join(lines))
    return ok and out == "PASS", out


def prop_safety25(compiler, rng):
    """WS1+WS4: every ganita_checked_*/ganita_sat_* against an
    independent Python-oracle implementation of the contract, plus
    the R24 invariants: sat and checked agree on the success path,
    sat_abs/checked_abs agree for non-MIN, saturating never wraps."""
    import math
    maxv = 2**63 - 1
    minv = -(2**63)
    edges = [0, 1, -1, 2, -2, 3, -3, 5, -5, 7, -7, 100, -100,
             3037000499, 3037000500, -3037000500, maxv, minv,
             maxv - 1, minv + 1]

    def lit(v):
        return "maxv" if v == maxv else ("minv" if v == minv else
                                         (f"(0 - {-v})" if v < 0 else str(v)))

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return q if (a < 0) == (b < 0) else -q

    def trunc_mod(a, b):
        return a - trunc_div(a, b) * b

    def clamp(true):
        return maxv if true > maxv else (minv if true < minv else true)

    def overflows(true):
        return true > maxv or true < minv

    # The checks are split into four programs: one mukhya() block holds
    # at most a few hundred statements ("too many statements in block"
    # otherwise). Each part must print PASS.
    parts = {"a": [], "b": [], "c": [], "d": []}
    for p in parts.values():
        p += ["ayojan ganita",
              "mukhya() {",
              "    vitti ok = nirmmita(8)",
              "    vitti minv = (0 - 9223372036854775807) - 1",
              "    vitti maxv = 9223372036854775807"]

    def fail(lines, msg):
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")

    def check_checked(lines, fname, args, want_val, want_ok):
        argstr = ", ".join(lit(a) for a in args)
        lines.append(f"    yadi ({fname}({argstr}, ok) != {lit(want_val)}) {{")
        fail(lines, f"{fname} value")
        lines.append("    }")
        lines.append(f"    yadi (ok[0] != {want_ok}) {{")
        fail(lines, f"{fname} ok")
        lines.append("    }")

    def check_sat(lines, fname, args, want_val):
        argstr = ", ".join(lit(a) for a in args)
        lines.append(f"    yadi ({fname}({argstr}) != {lit(want_val)}) {{")
        fail(lines, f"{fname}")
        lines.append("    }")

    # --- part a: binary add/sub/mul
    la = parts["a"]
    pairs = [(rng.choice(edges), rng.choice(edges)) for _ in range(8)]
    pairs += [(maxv, 1), (minv, -1), (minv, 1), (maxv, -1),
              (3037000500, 3037000500), (3037000499, 3037000499),
              (-3037000500, 3037000500), (2**32, 2**32)]
    for a, b in pairs:
        for fname, op in (("ganita_checked_add", lambda a, b: a + b),
                          ("ganita_checked_sub", lambda a, b: a - b),
                          ("ganita_checked_mul", lambda a, b: a * b)):
            true = op(a, b)
            if overflows(true):
                check_checked(la, fname, (a, b), 0, 0)
            else:
                check_checked(la, fname, (a, b), true, 1)
        for fname, op in (("ganita_sat_add", lambda a, b: a + b),
                          ("ganita_sat_sub", lambda a, b: a - b),
                          ("ganita_sat_mul", lambda a, b: a * b)):
            check_sat(la, fname, (a, b), clamp(op(a, b)))
    # --- part b: div/mod + WS4 sat/checked agreement
    lb = parts["b"]
    for a, b in pairs:
        if b == 0 or (a == minv and b == -1):
            check_checked(lb, "ganita_checked_div", (a, b), 0, 0)
            check_checked(lb, "ganita_checked_mod", (a, b), 0, 0)
            check_sat(lb, "ganita_sat_div", (a, b), 0 if b == 0 else maxv)
            check_sat(lb, "ganita_sat_mod", (a, b), 0)
        else:
            check_checked(lb, "ganita_checked_div", (a, b), trunc_div(a, b), 1)
            check_checked(lb, "ganita_checked_mod", (a, b), trunc_mod(a, b), 1)
            check_sat(lb, "ganita_sat_div", (a, b), trunc_div(a, b))
            check_sat(lb, "ganita_sat_mod", (a, b), trunc_mod(a, b))
            lb.append(f"    yadi (ganita_sat_div({lit(a)}, {lit(b)}) != ganita_checked_div({lit(a)}, {lit(b)}, ok)) {{")
            fail(lb, "sat/checked div agree")
            lb.append("    }")
            lb.append(f"    yadi (ganita_sat_mod({lit(a)}, {lit(b)}) != ganita_checked_mod({lit(a)}, {lit(b)}, ok)) {{")
            fail(lb, "sat/checked mod agree")
            lb.append("    }")
    # --- part c: pow/fact
    lc = parts["c"]
    pow_cases = [(2, 62), (2, 63), (-2, 63), (-2, 64), (3, 40), (10, 18),
                 (10, 19), (0, 0), (0, 5), (5, 0), (-1, 100), (-1, 101),
                 (2, -1), (rng.choice(edges), rng.randint(0, 5))]
    for a, e in pow_cases:
        if e < 0:
            check_checked(lc, "ganita_checked_pow", (a, e), 0, 0)
            check_sat(lc, "ganita_sat_pow", (a, e), 0)
        else:
            true = a ** e
            if overflows(true):
                check_checked(lc, "ganita_checked_pow", (a, e), 0, 0)
            else:
                check_checked(lc, "ganita_checked_pow", (a, e), true, 1)
            check_sat(lc, "ganita_sat_pow", (a, e), clamp(true))
    for n in [-1, 0, 1, 5, 20, 21, 25]:
        true = math.factorial(n) if n >= 0 else None
        if n < 0 or overflows(true):
            check_checked(lc, "ganita_checked_fact", (n,), 0, 0)
        else:
            check_checked(lc, "ganita_checked_fact", (n,), true, 1)
        check_sat(lc, "ganita_sat_fact", (n,), 0 if n < 0 else clamp(true))
    # --- part d: abs + WS4 abs agreement + never-wrap
    ld = parts["d"]
    for a in [0, 1, -1, 5, -5, 100, -100, maxv, minv, minv + 1]:
        if a == minv:
            check_checked(ld, "ganita_checked_abs", (a,), 0, 0)
            check_sat(ld, "ganita_sat_abs", (a,), maxv)
        else:
            check_checked(ld, "ganita_checked_abs", (a,), abs(a), 1)
            check_sat(ld, "ganita_sat_abs", (a,), abs(a))
            ld.append(f"    yadi (ganita_sat_abs({lit(a)}) != ganita_checked_abs({lit(a)}, ok)) {{")
            fail(ld, "sat/checked abs agree")
            ld.append("    }")
    for expr, want in [("ganita_sat_add(maxv, 1)", "maxv"),
                       ("ganita_sat_sub(minv, 1)", "minv"),
                       ("ganita_sat_mul(maxv, 2)", "maxv"),
                       ("ganita_sat_mul(minv, 2)", "minv"),
                       ("ganita_sat_pow(2, 63)", "maxv")]:
        ld.append(f"    yadi ({expr} != {want}) {{")
        fail(ld, f"{expr} never wraps")
        ld.append("    }")
    for key, lines in parts.items():
        lines.append('    likha("PASS\\n")')
        lines.append("}")
        ok, out = run_sm(compiler, f"safety25{key}", "\n".join(lines))
        if not (ok and out == "PASS"):
            return False, out
    return True, "PASS"


def prop_safety26(compiler, rng):
    """WS1 (R26): checked/saturating INTERACTION — for every op, sat
    and checked agree on the success path, and on the failure path sat
    is the clamp (overflow) or 0 (invalid input); saturating never
    wraps for any input. Randomized battery (fixed seed), split into
    three programs to stay under the per-block statement limit."""
    import math
    maxv = 2**63 - 1
    minv = -(2**63)
    edges = [0, 1, -1, 2, -2, 5, -5, 100, -100, maxv, minv,
             maxv - 1, minv + 1, 3037000500, -3037000500]

    def lit(v):
        return "maxv" if v == maxv else ("minv" if v == minv else
                                         (f"(0 - {-v})" if v < 0 else str(v)))

    def trunc_div(a, b):
        q = abs(a) // abs(b)
        return q if (a < 0) == (b < 0) else -q

    def trunc_mod(a, b):
        return a - trunc_div(a, b) * b

    def clamp(true):
        return maxv if true > maxv else (minv if true < minv else true)

    def overflows(true):
        return true > maxv or true < minv

    parts = {"a1": [], "a2": [], "b": [], "c": []}
    # Unique variable names per call: re-declaring `vitti cv` in one
    # block is a compiler bug (later reads see the FIRST value).
    cnt = [0]

    def fresh():
        cnt[0] += 1
        return cnt[0]
    for p in parts.values():
        p += ["ayojan ganita",
              "mukhya() {",
              "    vitti ok = nirmmita(8)",
              "    vitti minv = (0 - 9223372036854775807) - 1",
              "    vitti maxv = 9223372036854775807"]

    def fail(lines, msg):
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")

    def agree_binop(lines, cf, sf, a, b, true, invalid):
        """checked cf vs saturating sf on (a,b): true = exact result,
        invalid = True if the input itself is invalid (div/mod by
        zero, MIN/-1 for div is overflow not invalid)."""
        n = fresh()
        lines.append(f"    vitti cv{n} = {cf}({lit(a)}, {lit(b)}, ok)")
        lines.append(f"    vitti cok{n} = ok[0]")
        lines.append(f"    vitti sv{n} = {sf}({lit(a)}, {lit(b)})")
        lines.append(f"    yadi (cok{n} == 1) {{")
        lines.append(f"        yadi (sv{n} != cv{n}) {{")
        fail(lines, f"{cf}/{sf} agree success")
        lines.append("        }")
        lines.append("    } anyatra {")
        if invalid:
            lines.append(f"        yadi (sv{n} != 0) {{")
            fail(lines, f"{cf}/{sf} invalid -> 0")
            lines.append("        }")
        else:
            lines.append(f"        yadi (sv{n} != {lit(clamp(true))}) {{")
            fail(lines, f"{cf}/{sf} overflow -> clamp")
            lines.append("        }")
        lines.append("    }")

    # --- parts a1/a2: add/sub/mul, then div/mod; random + edge pairs
    la1 = parts["a1"]
    la2 = parts["a2"]
    pairs = [(rng.choice(edges), rng.choice(edges)) for _ in range(6)]
    pairs += [(rng.randint(-10**12, 10**12), rng.randint(-10**12, 10**12))
              for _ in range(6)]
    pairs += [(maxv, 1), (minv, -1), (minv, 1), (maxv, -1),
              (3037000500, 3037000500), (2**32, 2**32), (5, 0), (0, 0)]
    for a, b in pairs:
        agree_binop(la1, "ganita_checked_add", "ganita_sat_add",
                    a, b, a + b, False)
        agree_binop(la1, "ganita_checked_sub", "ganita_sat_sub",
                    a, b, a - b, False)
        agree_binop(la1, "ganita_checked_mul", "ganita_sat_mul",
                    a, b, a * b, False)
    for a, b in pairs:
        if b == 0:
            agree_binop(la2, "ganita_checked_div", "ganita_sat_div",
                        a, b, 0, True)
            agree_binop(la2, "ganita_checked_mod", "ganita_sat_mod",
                        a, b, 0, True)
        elif a == minv and b == -1:
            # div: overflow -> MAX; mod: exact 0 (guarded, not overflow)
            la2.append("    vitti cvd = ganita_checked_div(minv, 0 - 1, ok)")
            la2.append("    yadi (ok[0] != 0) {")
            fail(la2, "checked_div MIN/-1 ok")
            la2.append("    }")
            la2.append("    yadi (ganita_sat_div(minv, 0 - 1) != maxv) {")
            fail(la2, "sat_div MIN/-1 clamp")
            la2.append("    }")
            la2.append("    vitti cvm = ganita_checked_mod(minv, 0 - 1, ok)")
            la2.append("    yadi (ok[0] != 0) {")
            fail(la2, "checked_mod MIN/-1 ok")
            la2.append("    }")
            la2.append("    yadi (ganita_sat_mod(minv, 0 - 1) != 0) {")
            fail(la2, "sat_mod MIN/-1 exact 0")
            la2.append("    }")
        else:
            agree_binop(la2, "ganita_checked_div", "ganita_sat_div",
                        a, b, trunc_div(a, b), False)
            agree_binop(la2, "ganita_checked_mod", "ganita_sat_mod",
                        a, b, trunc_mod(a, b), False)
    # --- part b: pow/fact
    lb = parts["b"]
    pow_cases = [(rng.choice(edges), rng.randint(0, 70)) for _ in range(6)]
    pow_cases += [(2, 62), (2, 63), (-2, 63), (-2, 64), (3, 40),
                  (10, 19), (0, 0), (2, -1), (-3, -2)]
    for a, e in pow_cases:
        n = fresh()
        lb.append(f"    vitti cv{n} = ganita_checked_pow({lit(a)}, {lit(e)}, ok)")
        lb.append(f"    vitti cok{n} = ok[0]")
        lb.append(f"    vitti sv{n} = ganita_sat_pow({lit(a)}, {lit(e)})")
        if e < 0:
            lb.append(f"    yadi (cok{n} != 0) {{")
            fail(lb, "checked_pow neg ok")
            lb.append("    }")
            lb.append(f"    yadi (sv{n} != 0) {{")
            fail(lb, "sat_pow neg -> 0")
            lb.append("    }")
        else:
            true = a ** e
            lb.append(f"    yadi (cok{n} == 1) {{")
            lb.append(f"        yadi (sv{n} != cv{n}) {{")
            fail(lb, "pow agree success")
            lb.append("        }")
            lb.append("    } anyatra {")
            lb.append(f"        yadi (sv{n} != {lit(clamp(true))}) {{")
            fail(lb, "pow overflow -> clamp")
            lb.append("        }")
            lb.append("    }")
    for n in [rng.randint(-2, 30) for _ in range(6)] + [-1, 0, 20, 21, 25]:
        n = fresh()
        lb.append(f"    vitti cv{n} = ganita_checked_fact({lit(n)}, ok)")
        lb.append(f"    vitti cok{n} = ok[0]")
        lb.append(f"    vitti sv{n} = ganita_sat_fact({lit(n)})")
        if n < 0:
            lb.append(f"    yadi (cok{n} != 0) {{")
            fail(lb, "checked_fact neg ok")
            lb.append("    }")
            lb.append(f"    yadi (sv{n} != 0) {{")
            fail(lb, "sat_fact neg -> 0")
            lb.append("    }")
        else:
            true = math.factorial(n)
            lb.append(f"    yadi (cok{n} == 1) {{")
            lb.append(f"        yadi (sv{n} != cv{n}) {{")
            fail(lb, "fact agree success")
            lb.append("        }")
            lb.append("    } anyatra {")
            lb.append(f"        yadi (sv{n} != {lit(clamp(true))}) {{")
            fail(lb, "fact overflow -> clamp")
            lb.append("        }")
            lb.append("    }")
    # --- part c: abs + never-wrap spot checks
    lc = parts["c"]
    for a in [rng.randint(-2**63, 2**63 - 1) for _ in range(8)] + [minv, maxv, 0]:
        n = fresh()
        lc.append(f"    vitti cv{n} = ganita_checked_abs({lit(a)}, ok)")
        lc.append(f"    vitti cok{n} = ok[0]")
        lc.append(f"    vitti sv{n} = ganita_sat_abs({lit(a)})")
        if a == minv:
            lc.append(f"    yadi (cok{n} != 0) {{")
            fail(lc, "checked_abs MIN ok")
            lc.append("    }")
            lc.append(f"    yadi (sv{n} != maxv) {{")
            fail(lc, "sat_abs MIN clamp")
            lc.append("    }")
        else:
            lc.append(f"    yadi (cok{n} != 1) {{")
            fail(lc, "checked_abs ok")
            lc.append("    }")
            lc.append(f"    yadi (sv{n} != cv{n}) {{")
            fail(lc, "abs agree success")
            lc.append("    }")
    for expr, want in [("ganita_sat_add(maxv, 1)", "maxv"),
                       ("ganita_sat_sub(minv, 1)", "minv"),
                       ("ganita_sat_mul(maxv, maxv)", "maxv"),
                       ("ganita_sat_mul(minv, minv)", "maxv"),
                       ("ganita_sat_pow(0 - 2, 65)", "minv"),
                       ("ganita_sat_fact(30)", "maxv")]:
        lc.append(f"    yadi ({expr} != {want}) {{")
        fail(lc, f"{expr} never wraps")
        lc.append("    }")
    for key, lines in parts.items():
        lines.append('    likha("PASS\\n")')
        lines.append("}")
        ok, out = run_sm(compiler, f"safety26{key}", "\n".join(lines))
        if not (ok and out == "PASS"):
            return False, out
    return True, "PASS"


def prop_breadth26(compiler, rng):
    """R26 WS4: math_rand determinism + known LCG values, math_clamp
    vs Python, str_to_float vs Python float() (relative 1e-9)."""
    import math as _math
    part1 = ["ayojan math", "ayojan strconv", "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti s1 = nirmmita(8)",
             "    vitti s2 = nirmmita(8)",
             "    s1[0] = 12345",
             "    s2[0] = 12345"]
    part2 = ["ayojan strconv", "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti buf = nirmmita(32 * 8)"]
    lines = part1

    def fail(msg):
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")

    # rand: same seed -> identical sequences; seed 0 -> first is the
    # LCG increment constant.
    for i in range(4):
        lines.append(f"    yadi (math_rand(s1) != math_rand(s2)) {{")
        fail("rand determinism")
        lines.append("    }")
    lines.append("    vitti s0 = nirmmita(8)")
    lines.append("    s0[0] = 0")
    lines.append("    yadi (math_rand(s0) != 1442695040888963407) {")
    fail("rand seed0")
    lines.append("    }")
    # clamp vs Python
    for v, lo, hi in [(5, 0, 10), (-5, 0, 10), (15, 0, 10), (0, 0, 10),
                      (10, 0, 10), (7, 7, 7), (-100, -10, -1)]:
        want = min(max(v, lo), hi)
        lines.append(f"    yadi (math_clamp({v}, {lo}, {hi}) != {want}) {{")
        fail("clamp")
        lines.append("    }")
    # float parse vs Python, tolerance 1e-9 relative
    lines.append("    vitti buf = nirmmita(32 * 8)")
    for ci, s in enumerate(["0", "1", "-1", "3.14159", "0.5", "2.5", "-0.02",
              "100000", "123456.789", "1e10", "1.5e-5", ".5", "12.",
              "-2e-2", "0.000001"]):
        want = float(s)
        for j, ch in enumerate(s):
            lines.append(f"    buf[{j}] = {ord(ch)}")
        lines.append(f"    vitti f{ci} = str_to_float(buf, {len(s)}, ok)")
        lines.append("    yadi (ok[0] != 1) {")
        fail(f"float ok {s}")
        lines.append("    }")
        if want == 0.0:
            lines.append(f"    yadi (f{ci} != 0.0) {{")
            fail(f"float zero {s}")
            lines.append("    }")
        else:
            wlit = repr(want) if "e" not in repr(want) else f"{want:.15f}"
            lines.append(f"    vitti want{ci} = {wlit}")
            lines.append(f"    vitti diff{ci} = f{ci} - want{ci}")
            lines.append(f"    yadi (diff{ci} < 0.0) {{ diff{ci} = 0.0 - diff{ci} }}")
            lines.append(f"    vitti lim{ci} = want{ci}")
            lines.append(f"    yadi (lim{ci} < 0.0) {{ lim{ci} = 0.0 - lim{ci} }}")
            lines.append(f"    lim{ci} = lim{ci} * 0.000000001")
            lines.append(f"    yadi (diff{ci} > lim{ci}) {{")
            fail(f"float value {s}")
            lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    lines = part2
    # invalid inputs -> ok 0
    for ii, s in enumerate(["", "1x", "1e", "1e+", ".", "e5", "1.2.3", "+1", " 1",
              "inf", "nan", "1e400"]):
        for j, ch in enumerate(s):
            lines.append(f"    buf[{j}] = {ord(ch)}")
        lines.append(f"    vitti f{ci} = str_to_float(buf, {len(s)}, ok)")
        lines.append("    yadi (ok[0] != 0) {")
        fail(f"float invalid {s or 'empty'}")
        lines.append("    }")
    # underflow -> 0.0, ok 1
    lines.append('    buf[0] = 49')
    lines.append('    buf[1] = 101')
    lines.append('    buf[2] = 45')
    lines.append('    buf[3] = 57')
    lines.append('    buf[4] = 57')
    lines.append('    buf[5] = 57')
    lines.append('    vitti fu = str_to_float(buf, 6, ok)')
    lines.append("    yadi (ok[0] != 1) {")
    fail("float underflow ok")
    lines.append("    }")
    lines.append("    yadi (fu != 0.0) {")
    fail("float underflow value")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    for key, prog in (("b26a", part1), ("b26b", part2)):
        ok, out = run_sm(compiler, key, "\n".join(prog))
        if not (ok and out == "PASS"):
            return False, out
    return True, "PASS"


def _base_repr(n, b):
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    if n == 0:
        return "0"
    out = ""
    while n > 0:
        out = digits[n % b] + out
        n //= b
    return out


def prop_min26(compiler, rng):
    """R26 WS3: INT64_MIN fixes — int_to_str(MIN), fmt_digits_base
    negatives, fmt_int_base/fmt_int_flags(MIN) vs Python."""
    lines = ["ayojan strconv", "ayojan fmt", "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti buf = nirmmita(32 * 8)",
             "    vitti out = nirmmita(80 * 8)",
             "    vitti minv = (0 - 9223372036854775807) - 1"]

    def fail(msg):
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")

    # int_to_str(MIN) == "-9223372036854775808", and round-trips
    lines.append("    vitti n0 = int_to_str(minv, buf)")
    lines.append("    yadi (n0 != 20) {")
    fail("int_to_str MIN len")
    lines.append("    }")
    for j, ch in enumerate("-9223372036854775808"):
        lines.append(f"    yadi (buf[{j}] != {ord(ch)}) {{")
        fail("int_to_str MIN chars")
        lines.append("    }")
    lines.append("    yadi (str_to_int(buf, n0, ok) != minv) {")
    fail("int_to_str MIN roundtrip")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 1) {")
    fail("int_to_str MIN roundtrip ok")
    lines.append("    }")
    # fmt_digits_base(-5) == "5"
    lines.append("    yadi (fmt_digits_base(0 - 5, 10, 0, out) != 1) {")
    fail("fmt_digits_base neg len")
    lines.append("    }")
    lines.append("    yadi (char_at(out, 0) != 53) {")
    fail("fmt_digits_base neg char")
    lines.append("    }")
    # fmt_int_base(MIN) vs Python in several bases
    for ci, b in enumerate([2, 8, 10, 16, 36]):
        want = "-" + _base_repr(2**63, b)
        lines.append(f"    vitti nb{ci} = fmt_int_base(minv, {b}, out)")
        lines.append(f"    yadi (nb{ci} != {len(want)}) {{")
        fail(f"fmt_int_base MIN base {b} len")
        lines.append("    }")
        for j, ch in enumerate(want):
            lines.append(f"    yadi (char_at(out, {j}) != {ord(ch)}) {{")
            fail(f"fmt_int_base MIN base {b} char {j}")
            lines.append("    }")
    # fmt_int_flags(MIN, 16, prefix) == "-0x8000000000000000"
    want = "-0x8000000000000000"
    lines.append("    vitti nf = fmt_int_flags(minv, 16, 1, out)")
    lines.append(f"    yadi (nf != {len(want)}) {{")
    fail("fmt_int_flags MIN len")
    lines.append("    }")
    for j, ch in enumerate(want):
        lines.append(f"    yadi (char_at(out, {j}) != {ord(ch)}) {{")
        fail("fmt_int_flags MIN chars")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "min26", "\n".join(lines))
    return ok and out == "PASS", out


def prop_safety27(compiler, rng):
    """R27 WS1: cross-module safety — strconv's overflow guards and
    ganita's checked forms agree on the same magnitudes: a string
    that parses (ok 1) names a value the checked ops accept; a string
    that overflows (ok 0, return 0) names a magnitude the checked ops
    reject (also return 0). Neither silently wraps."""
    # Two programs: the parse battery alone exceeds the per-block
    # statement limit.
    part1 = ["ayojan strconv", "ayojan ganita", "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti buf = nirmmita(32 * 8)",
             "    vitti maxv = 9223372036854775807",
             "    vitti minv = (0 - 9223372036854775807) - 1"]
    part3 = ["ayojan strconv", "ayojan ganita", "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti buf = nirmmita(32 * 8)",
             "    vitti maxv = 9223372036854775807",
             "    vitti minv = (0 - 9223372036854775807) - 1"]
    part2 = ["ayojan strconv", "ayojan ganita", "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti buf = nirmmita(32 * 8)",
             "    vitti maxv = 9223372036854775807",
             "    vitti minv = (0 - 9223372036854775807) - 1"]
    lines = part1

    def fail(msg):
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")

    def put_str(s):
        for j, ch in enumerate(s):
            lines.append(f"    buf[{j}] = {ord(ch)}")

    # --- fitting strings: parse ok, and checked ops accept the value
    for fi, (s, val) in enumerate([("0", 0), ("123", 123), ("-456", -456),
                   ("9223372036854775807", 2**63 - 1),
                   ("-9223372036854775808", -(2**63))]):
        put_str(s)
        lines.append(f"    vitti pvf{fi} = str_to_int(buf, {len(s)}, ok)")
        lines.append("    yadi (ok[0] != 1) {")
        fail(f"parse fits {s}")
        lines.append("    }")
        vname = "maxv" if val == 2**63 - 1 else ("minv" if val == -(2**63) else str(val))
        lines.append(f"    yadi (pvf{fi} != {vname}) {{")
        fail(f"parse value {s}")
        lines.append("    }")
        # checked ops accept the parsed value
        lines.append(f"    yadi (ganita_checked_add(pvf{fi}, 0, ok) != {vname}) {{")
        fail(f"checked_add accepts {s}")
        lines.append("    }")
        lines.append("    yadi (ok[0] != 1) {")
        fail(f"checked_add ok {s}")
        lines.append("    }")
        lines.append(f"    yadi (ganita_checked_mul(pvf{fi}, 1, ok) != {vname}) {{")
        fail(f"checked_mul accepts {s}")
        lines.append("    }")
        lines.append("    yadi (ok[0] != 1) {")
        fail(f"checked_mul ok {s}")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    lines = part2
    # --- overflowing strings: parse fails with 0, and the checked op
    # for the SAME magnitude also fails with 0 (neither wraps)
    over = [("9223372036854775808",
             "ganita_checked_add(maxv, 1, ok)"),
            ("-9223372036854775809",
             "ganita_checked_sub(minv, 1, ok)"),
            ("18446744073709551616",
             "ganita_checked_mul(4294967296, 4294967296, ok)"),
            ("18446744073709551615", None),
            ("99999999999999999999", None)]
    for oi, (s, gexpr) in enumerate(over):
        put_str(s)
        lines.append(f"    vitti pvo{oi} = str_to_int(buf, {len(s)}, ok)")
        lines.append("    yadi (ok[0] != 0) {")
        fail(f"parse rejects {s}")
        lines.append("    }")
        lines.append(f"    yadi (pvo{oi} != 0) {{")
        fail(f"parse returns 0 {s}")
        lines.append("    }")
        if gexpr:
            lines.append(f"    yadi ({gexpr} != 0) {{")
            fail(f"checked returns 0 {s}")
            lines.append("    }")
            lines.append("    yadi (ok[0] != 0) {")
            fail(f"checked rejects {s}")
            lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    lines = part3
    # --- hex: same boundary in base 16
    for hi, (s, ok_want) in enumerate([("ffffffffffffffff", 0),
                       ("10000000000000000", 0),
                       ("7fffffffffffffff", 1),
                       ("8000000000000000", 0)]):
        put_str(s)
        lines.append(f"    vitti pvh{hi} = str_to_int_base(buf, {len(s)}, 16, ok)")
        lines.append(f"    yadi (ok[0] != {ok_want}) {{")
        fail(f"hex parse {s}")
        lines.append("    }")
        if ok_want == 0:
            lines.append(f"    yadi (pvh{hi} != 0) {{")
            fail(f"hex returns 0 {s}")
            lines.append("    }")
    # hex 2^64 boundary vs ganita: checked_mul(2^32, 2^32) also fails
    lines.append("    yadi (ganita_checked_mul(4294967296, 4294967296, ok) != 0) {")
    fail("checked_mul 2^64 returns 0")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 0) {")
    fail("checked_mul 2^64 rejects")
    lines.append("    }")
    # --- roundtrip: int_to_str(v) parses back, and checked accepts v
    for ri, v in enumerate([0, 1, -1, 2**63 - 1, -(2**63)]):
        vname = "maxv" if v == 2**63 - 1 else ("minv" if v == -(2**63) else str(v))
        lines.append(f"    vitti rn{ri} = int_to_str({vname}, buf)")
        lines.append(f"    yadi (str_to_int(buf, rn{ri}, ok) != {vname}) {{")
        fail("roundtrip parse")
        lines.append("    }")
        lines.append("    yadi (ok[0] != 1) {")
        fail("roundtrip ok")
        lines.append("    }")
        lines.append(f"    yadi (ganita_checked_add({vname}, 0, ok) != {vname}) {{")
        fail("roundtrip checked")
        lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    for key, prog in (("safety27a", part1), ("safety27b", part2),
                      ("safety27c", part3)):
        ok, out = run_sm(compiler, key, "\n".join(prog))
        if not (ok and out == "PASS"):
            return False, out
    return True, "PASS"


def prop_bigint_divzero(compiler, rng):
    """R27 WS3: bigint_divmod and bigint_powmod by zero are defined
    (q=0, r=a; powmod unreduced) instead of hanging."""
    lines = ["ayojan bigint", "mukhya() {",
             "    vitti a = nirmmita(4 * 8)",
             "    vitti b = nirmmita(4 * 8)",
             "    vitti q = nirmmita(4 * 8)",
             "    vitti r = nirmmita(4 * 8)",
             "    bigint_from_int(10, a, 4)",
             "    bigint_from_int(0, b, 4)",
             "    bigint_divmod(a, b, q, r, 4)",
             "    yadi (bigint_to_int(q, 4) != 0) {",
             '        likha("FAIL divmod zero q\\n")',
             "        pratiyati 1",
             "    }",
             "    yadi (bigint_to_int(r, 4) != 10) {",
             '        likha("FAIL divmod zero r\\n")',
             "        pratiyati 1",
             "    }",
             "    bigint_from_int(2, a, 4)",
             "    bigint_powmod(a, 10, b, r, 4)",
             "    yadi (bigint_to_int(r, 4) != 1024) {",
             '        likha("FAIL powmod zero mod\\n")',
             "        pratiyati 1",
             "    }",
             '    likha("PASS\\n")',
             "}"]
    ok, out = run_sm(compiler, "bigint_divzero", "\n".join(lines))
    return ok and out == "PASS", out


def prop_ok_convention(compiler, rng):
    """R28 WS2: the ok convention — every ok-param container function
    sets ok on every path and returns a defined failure value (0)."""
    lines = ["ayojan list", "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti l = list_init(4)",
             "    vitti q = queue_init(4)"]

    def fail(msg):
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")

    # empty containers: return 0, ok 0
    for call in ["stack_pop(l, ok)", "stack_peek(l, ok)",
                 "queue_dequeue(q, ok)", "queue_peek(q, ok)",
                 "list_min(l, ok)", "list_max(l, ok)"]:
        lines.append(f"    yadi ({call} != 0) {{")
        fail(f"empty {call} returns 0")
        lines.append("    }")
        lines.append("    yadi (ok[0] != 0) {")
        fail(f"empty {call} ok 0")
        lines.append("    }")
    # non-empty: ok 1, correct value
    lines.append("    list_push(l, 7)")
    lines.append("    yadi (stack_pop(l, ok) != 7) {")
    fail("stack_pop value")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 1) {")
    fail("stack_pop ok 1")
    lines.append("    }")
    lines.append("    list_push(l, 7)")
    lines.append("    yadi (stack_peek(l, ok) != 7) {")
    fail("stack_peek value")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 1) {")
    fail("stack_peek ok 1")
    lines.append("    }")
    lines.append("    yadi (list_min(l, ok) != 7) {")
    fail("list_min value")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 1) {")
    fail("list_min ok 1")
    lines.append("    }")
    lines.append("    yadi (list_max(l, ok) != 7) {")
    fail("list_max value")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 1) {")
    fail("list_max ok 1")
    lines.append("    }")
    lines.append("    queue_enqueue(q, 9)")
    lines.append("    yadi (queue_peek(q, ok) != 9) {")
    fail("queue_peek value")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 1) {")
    fail("queue_peek ok 1")
    lines.append("    }")
    lines.append("    yadi (queue_dequeue(q, ok) != 9) {")
    fail("queue_dequeue value")
    lines.append("    }")
    lines.append("    yadi (ok[0] != 1) {")
    fail("queue_dequeue ok 1")
    lines.append("    }")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "ok_convention", "\n".join(lines))
    return ok and out == "PASS", out


def prop_numeric28(compiler, rng):
    """R28 WS3: the numeric contract — gcd/lcm sign and zero cases,
    math power/fact edges, wrapping abs, bit_count negatives,
    is_prime/sum_to edges, and the documented domain limits."""
    lines = ["ayojan math", "ayojan ganita", "ayojan fmt", "ayojan strconv",
             "ayojan num",
             "mukhya() {",
             "    vitti ok = nirmmita(8)",
             "    vitti buf = nirmmita(32 * 8)",
             "    vitti out = nirmmita(40 * 8)",
             "    vitti minv = (0 - 9223372036854775807) - 1"]

    def check(expr, want, msg):
        lines.append(f"    yadi (({expr}) != ({want})) {{")
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")

    # gcd is non-negative; gcd(0,0) = 0
    check("gcd(0 - 6, 4)", 2, "gcd neg first")
    check("gcd(6, 0 - 4)", 2, "gcd neg second")
    check("gcd(0 - 6, 0 - 4)", 2, "gcd both neg")
    check("gcd(0, 0)", 0, "gcd 0 0")
    check("gcd(0, 5)", 5, "gcd 0 5")
    # lcm is non-negative; lcm(0,0) = 0 (was SIGFPE)
    check("lcm(0, 0)", 0, "lcm 0 0")
    check("lcm(0, 5)", 0, "lcm 0 5")
    check("lcm(6, 4)", 12, "lcm 6 4")
    check("lcm(0 - 6, 4)", 12, "lcm neg")
    check("lcm(6, 0 - 4)", 12, "lcm neg2")
    # math power/fact edges: non-positive exponent/argument -> 1
    check("power(2, 0)", 1, "power 0")
    check("power(2, 0 - 1)", 1, "power neg")
    check("fact(0 - 3)", 1, "fact neg")
    check("fact(0)", 1, "fact 0")
    check("fact(20)", 2432902008176640000, "fact 20")
    check("power(2, 10)", 1024, "power 2 10")
    # plain abs wraps at MIN (checked form exists for the safe case)
    check("abs_val(minv)", "minv", "abs_val MIN wraps")
    check("ganita_abs(minv)", "minv", "ganita_abs MIN wraps")
    # bit_count: defined for n >= 0; negative returns 0
    check("bit_count(7)", 3, "bit_count 7")
    check("bit_count(0)", 0, "bit_count 0")
    check("bit_count(0 - 1)", 0, "bit_count neg")
    # is_prime / sum_to edges
    check("is_prime(0)", 0, "prime 0")
    check("is_prime(1)", 0, "prime 1")
    check("is_prime(2)", 1, "prime 2")
    check("is_prime(0 - 5)", 0, "prime neg")
    check("sum_to(0 - 3)", 0, "sum_to neg")
    check("sum_to(10)", 55, "sum_to 10")
    # ganita_isqrt(negative) = 0
    check("ganita_isqrt(0 - 1)", 0, "isqrt neg")
    check("ganita_isqrt(16)", 4, "isqrt 16")
    # ganita_isqrt(MAX) = 3037000499 (binary search; the old
    # (i+1)^2 loop hung here by overflow)
    check("ganita_isqrt(9223372036854775807)", 3037000499, "isqrt MAX")
    # is_prime: division bound (i*i overflowed near MAX)
    check("is_prime(97)", 1, "prime 97")
    check("is_prime(91)", 0, "prime 91")
    # is_perfect: division bound (d*d overflowed near MAX)
    check("is_perfect(28)", 1, "perfect 28")
    check("is_perfect(27)", 0, "perfect 27")
    check("is_perfect(6)", 1, "perfect 6")
    # collatz_steps: -1 means "does not reach 1" (x < 1, or the
    # 3x+1 step would overflow int64)
    check("collatz_steps(27)", 111, "collatz 27")
    check("collatz_steps(0)", "0 - 1", "collatz 0")
    check("collatz_steps(0 - 5)", "0 - 1", "collatz neg")
    check("collatz_steps(4611686018427387905)", "0 - 1",
          "collatz overflow")
    # fmt_digits_base rejects base < 2 or > 36 with 0, empty
    check("fmt_digits_base(123, 1, 0, out)", 0, "fmt base 1")
    check("fmt_digits_base(123, 37, 0, out)", 0, "fmt base 37")
    check("fmt_digits_base(255, 16, 0, out)", 2, "fmt base 16")
    # int_to_base_str requires n >= 0; negative gives 0 (empty)
    check("int_to_base_str(0 - 5, 10, buf)", 0, "int_to_base neg")
    check("int_to_base_str(255, 16, buf)", 2, "int_to_base 255")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "numeric28", "\n".join(lines))
    return ok and out == "PASS", out


def prop_result29(compiler, rng):
    """R29 WS3: the Result type — constructors, inspectors,
    value_or, the ok-convention bridge, and the checked
    producers (success, overflow, div/mod by zero, MIN/-1)."""
    lines = ["ayojan result",
             "mukhya() {",
             "    vitti r = nirmmita(2 * 8)",
             "    vitti ok = nirmmita(8)",
             "    vitti minv = (0 - 9223372036854775807) - 1"]

    def check(expr, want, msg):
        lines.append(f"    yadi (({expr}) != ({want})) {{")
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")

    # constructors + inspectors
    lines.append("    result_ok(r, 42)")
    check("result_is_ok(r)", 1, "ok is_ok")
    check("result_value(r)", 42, "ok value")
    check("result_value_or(r, 99)", 42, "ok value_or")
    lines.append("    result_err(r)")
    check("result_is_ok(r)", 0, "err is_ok")
    check("result_value(r)", 0, "err value")
    check("result_value_or(r, 99)", 99, "err value_or")
    # from_ok bridge: value passes through on success, 0 on failure
    lines.append("    ok[0] = 1")
    lines.append("    result_from_ok(r, 7, ok)")
    check("result_is_ok(r)", 1, "from_ok ok")
    check("result_value(r)", 7, "from_ok value")
    lines.append("    ok[0] = 0")
    lines.append("    result_from_ok(r, 7, ok)")
    check("result_is_ok(r)", 0, "from_ok fail")
    check("result_value(r)", 0, "from_ok fail value")
    # checked producers
    lines.append("    result_checked_add(r, 2, 3)")
    check("result_is_ok(r)", 1, "add ok")
    check("result_value(r)", 5, "add value")
    lines.append("    result_checked_add(r, 9223372036854775807, 1)")
    check("result_is_ok(r)", 0, "add overflow")
    check("result_value(r)", 0, "add overflow value")
    lines.append("    result_checked_sub(r, minv, 1)")
    check("result_is_ok(r)", 0, "sub overflow")
    lines.append("    result_checked_mul(r, 4294967296, 4294967296)")
    check("result_is_ok(r)", 0, "mul overflow")
    lines.append("    result_checked_mul(r, 6, 7)")
    check("result_is_ok(r)", 1, "mul ok")
    check("result_value(r)", 42, "mul value")
    lines.append("    result_checked_div(r, 7, 2)")
    check("result_is_ok(r)", 1, "div ok")
    check("result_value(r)", 3, "div value")
    lines.append("    result_checked_div(r, 1, 0)")
    check("result_is_ok(r)", 0, "div zero")
    lines.append("    result_checked_div(r, minv, 0 - 1)")
    check("result_is_ok(r)", 0, "div MIN -1")
    lines.append("    result_checked_mod(r, 7, 3)")
    check("result_is_ok(r)", 1, "mod ok")
    check("result_value(r)", 1, "mod value")
    lines.append("    result_checked_mod(r, 1, 0)")
    check("result_is_ok(r)", 0, "mod zero")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "result29", "\n".join(lines))
    return ok and out == "PASS", out


def prop_serial29(compiler, rng):
    """R29 WS5: serialisation — i64 roundtrips incl. MIN/MAX,
    length-prefixed bytes roundtrip, overrun -> -1, corrupt
    (negative) length -> -1, and len_bytes."""
    lines = ["ayojan serial",
             "mukhya() {",
             "    vitti buf = nirmmita(64 * 8)",
             "    vitti out = nirmmita(8)",
             "    vitti dst = nirmmita(16 * 8)",
             "    vitti n = nirmmita(8)",
             "    vitti minv = (0 - 9223372036854775807) - 1"]

    def check(expr, want, msg):
        lines.append(f"    yadi (({expr}) != ({want})) {{")
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")

    # i64 roundtrips
    for i, v in enumerate([0, 1, -1, 9223372036854775807,
                           "minv", -123456789012345]):
        lines.append(f"    serial_put_i64(buf, {i * 8}, 64, {v})")
    for i, v in enumerate([0, 1, -1, 9223372036854775807,
                           "minv", -123456789012345]):
        lines.append(f"    serial_get_i64(buf, {i * 8}, 64, out)")
        check("out[0]", v, f"i64 roundtrip {v}")
    # overrun -> -1, nothing written
    check("serial_put_i64(buf, 60, 64, 1)", "0 - 1", "put overrun")
    check("serial_get_i64(buf, 60, 64, out)", "0 - 1", "get overrun")
    check("serial_put_i64(buf, 0 - 1, 64, 1)", "0 - 1", "put neg pos")
    check("serial_len_bytes(5)", 13, "len_bytes")
    # bytes roundtrip
    lines.append("    vitti src = nirmmita(16 * 8)")
    lines.append("    set_char(src, 0, 104)")
    lines.append("    set_char(src, 1, 101)")
    lines.append("    set_char(src, 2, 108)")
    lines.append("    set_char(src, 3, 108)")
    lines.append("    set_char(src, 4, 111)")
    check("serial_put_bytes(buf, 0, 64, src, 5)", 13, "put_bytes")
    check("serial_get_bytes(buf, 0, 64, dst, n)", 13, "get_bytes")
    check("n[0]", 5, "get_bytes len")
    for i, c in enumerate([104, 101, 108, 108, 111]):
        check(f"char_at(dst, {i})", c, f"byte {i}")
    # empty payload
    check("serial_put_bytes(buf, 0, 64, src, 0)", 8, "put_bytes empty")
    check("serial_get_bytes(buf, 0, 64, dst, n)", 8, "get_bytes empty")
    check("n[0]", 0, "get_bytes empty len")
    # overrun and negative length
    check("serial_put_bytes(buf, 60, 64, src, 5)", "0 - 1",
          "put_bytes overrun")
    check("serial_put_bytes(buf, 0, 64, src, 0 - 1)", "0 - 1",
          "put_bytes neg len")
    lines.append("    serial_put_i64(buf, 0, 64, 0 - 1)")
    check("serial_get_bytes(buf, 0, 64, dst, n)", "0 - 1",
          "get_bytes neg len")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "serial29", "\n".join(lines))
    return ok and out == "PASS", out


def prop_numeric29(compiler, rng):
    """R29 WS4: pin the numeric contract gaps — ganita classical
    wrapping (kuttaka/samasa/brahmagupta), math plain wrapping
    (sq/square/cube/double/triple/inc/power/fact), num fib and
    reverse_num wrapping, fmt_fixed overflow -> 0, and the
    chakravala fixes (perfect square, small Pell solutions,
    MAX -> 0 instead of hanging)."""
    lines = ["ayojan math", "ayojan ganita", "ayojan fmt", "ayojan num",
             "mukhya() {",
             "    vitti out = nirmmita(8 * 8)",
             "    vitti buf = nirmmita(40 * 8)",
             "    vitti minv = (0 - 9223372036854775807) - 1"]

    def check(expr, want, msg):
        lines.append(f"    yadi (({expr}) != ({want})) {{")
        lines.append(f'        likha("FAIL {msg}\\n")')
        lines.append("        pratiyati 1")
        lines.append("    }")

    # kuttaka: intermediate q*s wraps; the wrapped result is pinned
    # against a Python wrapping simulation (exact result differs)
    check("kuttaka(0 - 7819279541048604735, "
          "0 - 2881118045913156764, 0 - 150)",
          2605677504891245458, "kuttaka wrap")
    # samasa: p*r overflows (2^80 wraps to 0)
    lines.append("    samasa(out, 1099511627776, 0, 1099511627776, 0, 0)")
    check("out[0]", 0, "samasa wrap 0")
    check("out[1]", 0, "samasa wrap 1")
    # brahmagupta_area: (a+b+c+d) overflows (2^64 wraps to 0)
    check("brahmagupta_area(4611686018427387904, "
          "4611686018427387904, 4611686018427387904, "
          "4611686018427387904)", 0, "brahmagupta wrap")
    # math plain wrapping
    check("sq(4294967296)", 0, "sq wrap")
    check("square(3037000500)", "0 - 9223372036709301616", "square wrap")
    check("cube(2097152)", "minv", "cube 2^63")
    check("cube(2097153)", "0 - 9223358842708951039", "cube wrap")
    check("double(9223372036854775807)", "0 - 2", "double wrap")
    check("triple(9223372036854775807)", 9223372036854775805,
          "triple wrap")
    check("inc(9223372036854775807)", "minv", "inc wrap")
    check("power(2, 63)", "minv", "power wrap")
    check("power(3, 40)", "0 - 6289078614652622815", "power 3 40 wrap")
    check("fact(21)", "0 - 4249290049419214848", "fact 21 wrap")
    check("fib(93)", "0 - 6246583658587674878", "fib 93 wrap")
    check("reverse_num(1234567890123456789)",
          "0 - 8570200862721897295", "reverse_num wrap")
    # fmt_fixed overflow -> 0 (empty); the largest fixed output is
    # 9223372036854774784 (2^63 - 1024), 19 chars
    check("fmt_fixed(1000000000000000000.0, 2, buf)", 0, "fmt_fixed ovf")
    check("fmt_fixed(0 - 1000000000000000000.0, 2, buf)", 0,
          "fmt_fixed neg ovf")
    check("fmt_fixed(9223372036854774784.0, 0, buf)", 19, "fmt_fixed max")
    for i, c in enumerate("9223372036854774784"):
        check(f"char_at(buf, {i})", ord(c), f"fmt_fixed max char {i}")
    # chakravala: perfect square -> trivial solution, return 1
    lines.append("    vitti r = chakravala(out, 4)")
    check("r", 1, "chakravala 4 ret")
    check("out[0]", 1, "chakravala 4 x")
    check("out[1]", 0, "chakravala 4 y")
    # small Pell solutions, verified by x^2 - n*y^2 = 1
    for n, x, y in [(2, 3, 2), (3, 2, 1), (5, 9, 4), (13, 649, 180),
                    (61, 1766319049, 226153980)]:
        lines.append(f"    r = chakravala(out, {n})")
        check("r", 1, f"chakravala {n} ret")
        check("out[0]", x, f"chakravala {n} x")
        check("out[1]", y, f"chakravala {n} y")
        check(f"out[0] * out[0] - {n} * out[1] * out[1]", 1,
              f"chakravala {n} Pell")
    # MAX: the minimal solution does not fit in int64 — return 0
    # (was an effective hang in the m-scan) instead of hanging
    lines.append("    r = chakravala(out, 9223372036854775807)")
    check("r", 0, "chakravala MAX ret")
    lines.append('    likha("PASS\\n")')
    lines.append("}")
    ok, out = run_sm(compiler, "numeric29", "\n".join(lines))
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
        ("string find vs python", prop_string_find),
        ("string replace", prop_string_replace),
        ("string split/join", prop_string_split_join),
        ("string trim/case", prop_string_trim_case),
        ("strb find vs python", prop_strb_find),
        ("strb replace", prop_strb_replace),
        ("strb split/join", prop_strb_split_join),
        ("strb trim/case", prop_strb_trim_case),
        ("map put/get roundtrip", prop_map_roundtrip),
        ("map update", prop_map_update),
        ("map delete", prop_map_delete),
        ("map collision survival", prop_map_collision),
        ("map keys count", prop_map_keys_count),
        ("strb pack/unpack roundtrip", prop_strb_pack_unpack),
        ("strb dup", prop_strb_dup),
        ("sankhyiki purna int stats", prop_sankhyiki_purna),
        ("set add/contains/remove", prop_set_add_contains_remove),
        ("set add idempotent", prop_set_idempotent),
        ("set union commutative", prop_set_union_commutative),
        ("set intersect self/empty", prop_set_intersect_self_empty),
        ("set difference", prop_set_difference),
        ("set subset", prop_set_subset),
        ("fmt int base roundtrip", prop_fmt_int_base_roundtrip),
        ("fmt pad content", prop_fmt_pad_content),
        ("fmt group digits", prop_fmt_group_digits),
        ("fmt fixed decimals", prop_fmt_fixed),
        ("fmt signed", prop_fmt_signed),
        ("list push/get", prop_list_push_get),
        ("list stack LIFO", prop_list_stack_lifo),
        ("list queue FIFO", prop_list_queue_fifo),
        ("list len tracks", prop_list_len_tracks),
        ("list insert/remove", prop_list_insert_remove),
        ("map keys_bytes roundtrip", prop_map_keys_bytes_roundtrip),
        ("ganita checked add/sub", prop_ganita_checked_add_sub),
        ("ganita checked mul", prop_ganita_checked_mul),
        ("ganita checked div/mod", prop_ganita_checked_divmod),
        ("ganita saturating", prop_ganita_sat),
        ("map_clear reuse", prop_map_clear_reuse),
        ("containers clear", prop_containers_clear),
        ("gaps19", prop_gaps19),
        ("strb cell pairs", prop_strb_cell_pairs),
        ("containers resize/swap", prop_containers_resize_swap),
        ("gaps20", prop_gaps20),
        ("containers21", prop_containers21),
        ("gaps21", prop_gaps21),
        ("containers23", prop_containers23),
        ("gaps23", prop_gaps23),
        ("slices23", prop_slices23),
        ("invariants24 containers", prop_invariants24_containers),
        ("invariants24 merge/symdiff", prop_invariants24_merge_symdiff),
        ("safety24", prop_safety24),
        ("safety25 oracle", prop_safety25),
        ("safety26 interaction", prop_safety26),
        ("breadth26", prop_breadth26),
        ("min26", prop_min26),
        ("safety27 cross-module", prop_safety27),
        ("bigint divzero", prop_bigint_divzero),
        ("result type", prop_result29),
        ("serialisation roundtrip", prop_serial29),
        ("numeric contract gaps pinned", prop_numeric29),
        ("ok convention", prop_ok_convention),
        ("numeric28", prop_numeric28),
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
