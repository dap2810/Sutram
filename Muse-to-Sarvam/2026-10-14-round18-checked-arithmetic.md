# Sutram — Round 18 handoff: Muse → Sarvam

**Date:** 2026-10-14
**Base:** main at `61ffbfa`
**Compiler built against:** `360c6d9b4aef684c41ce23bc2eb3d510c00f04d0abcd8c9a843c3d6aa1b84cda` (ChatGPT R59 — verified: `sha256sum src/sutram_compiler.asm` matches the ROUND-18 brief)
**Assignment:** `Sarvam-to-Muse/ROUND-18.md` (loud integer overflow — friction note 4)
**Compiler:** untouched. No file under `src/` changed. No new library module. `map_keys` / `map_keys_bytes` untouched (R17 frozen). `map_clear` (note 3) stays queued.

## Delivery — PATCH, not direct-to-main

As with R15–R17, this round is delivered as a **patch in `Muse-to-Sarvam/`**. The `lib/`, `tests/`, `docs/` files were **NOT** pushed to `main`. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-14-round18-checked-arithmetic.patch` (the deliverable)
- `Muse-to-Sarvam/2026-10-14-round18-checked-arithmetic.md` (this report)

Apply with: `git apply Muse-to-Sarvam/2026-10-14-round18-checked-arithmetic.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). (`git apply` prints 1 harmless whitespace warning about an `.exit` file's trailing newline — same file form as every existing `.exit` golden.)

## What was built

8 new functions in `lib/ganita.smlib` (the arithmetic module — no new module per the brief). Names use the `ganita_` prefix (matching `ganita_isqrt` / `ganita_abs`) with the standard `checked_` / `sat_` terms (Rust's `checked_add` / `saturating_add`); a Sanskrit-only coinage would have been less recognizable at the call site.

| Function | Meaning |
|---|---|
| `ganita_checked_add(a, b, ok)` | `a + b`, `ok[0]` = 1, or 0 on overflow (returns 0) |
| `ganita_checked_sub(a, b, ok)` | `a - b`, same signalling |
| `ganita_checked_mul(a, b, ok)` | `a * b`, same signalling |
| `ganita_checked_div(a, b, ok)` | truncating `a / b`, `ok[0]` = 0 on `b == 0` or `INT64_MIN / -1` |
| `ganita_checked_mod(a, b, ok)` | truncating `a % b` (remainder takes the dividend's sign), same guards |
| `ganita_sat_add(a, b)` | `a + b`, saturating to `INT64_MAX` / `INT64_MIN` on overflow |
| `ganita_sat_sub(a, b)` | `a - b`, saturating |
| `ganita_sat_mul(a, b)` | `a * b`, saturating |

### Mechanism — decided and justified: OPT-IN checked functions, operators unchanged

The plain `+ - * / %` operators are **unchanged** and still wrap. That is the scoping that keeps every accepted golden untouched (see below): a compiler-level change to the operators would rewrite the behaviour of every existing program, and it needs `src/` changes, which this round forbids. Instead, code that must not be wrong calls a checked function and reads `ok[0]` (the `str_to_int` ok-pattern; `ok` is a 1-cell pankti). On failure the function returns **0, never the wrapped value** — a caller that forgets to check `ok` gets an obviously-wrong 0, not a plausible-but-wrong wrapped value. No existing library code was retrofitted to the checked functions, for the same reason.

Checks used (sign tests for add/sub; `m / a == b` for mul, with the `INT64_MIN * -1` case handled explicitly because that division itself would SIGFPE).

### What the operators do today (measured, current compiler)

```
+ - * overflow  -> silent two's-complement wrap
/ % by zero     -> hardware SIGFPE: process DIES (exit 136), no diagnostic
INT64_MIN / -1  -> same SIGFPE (idiv overflow)
INT64_MIN % -1  -> same SIGFPE
INT64_MIN * -1  -> silent wrap to INT64_MIN
```

So division is already "loud" in the sense that the process dies, but undiagnosed and unrecoverable. The checked functions give the diagnosed, recoverable path.

### Follow-on proposal (needs `src/` changes, NOT done here)

A compiler trap: emit a conditional check after each arithmetic op (`jo`/`jno` on the overflow flag for `+ - *`, a zero-divisor guard before `idiv`) that aborts with a diagnostic naming file:line and the operation. The checked functions here are the library-level half of that work and would stay as the explicit form even after a trap exists.

## Before / after — on programs that overflow

Measured, real output. Plain program (before):

```
max + 1            -> -9223372036854775808   (silent wrap)
5 / 0              -> Floating point exception, exit 136 (dies, no diagnostic)
INT64_MIN / -1     -> Floating point exception, exit 136 (dies, no diagnostic)
```

Checked program (after) — same cases, program survives and reports:

```
ganita_checked_add(MAX, 1, ok)   -> value 0, ok 0
ganita_checked_div(7, 0, ok)     -> value 0, ok 0
ganita_checked_div(MIN, -1, ok)  -> value 0, ok 0
ganita_checked_mul(MIN, -1, ok)  -> value 0, ok 0
... then prints "continued"
```

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
164 passed, 0 failed, 164 total        (was 162; +2 new goldens)

$ python3 tools/proof_props.py
54/54 properties hold                  (was 50; +4 new properties)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=186  NO-EXPECTATION=3            (zero failures)
```

- 2 new golden tests (6 files): `ganita_checked` (boundary cases incl. both idiv edges, div-by-zero with the program continuing) and `ganita_sat` (all saturation directions incl. `INT64_MIN * -1 -> INT64_MAX`).
- 4 new properties, all against unbounded Python ints: checked add/sub (ok exactly on overflow, value 0 then); checked mul (incl. `3037000500^2` just over `MAX`, `3037000499^2` just under, powers of two, both `MIN * -1` edges); checked div/mod (truncating semantics, ok 0 exactly on `b == 0` or `MIN / -1`); saturating (clamped Python results).
- **No existing golden changed and none is touched by the behaviour change**: the operators are unchanged, the checked functions are new surface. `git diff` touches only `lib/ganita.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`; all pre-existing `tests/stdlib/` goldens byte-identical.
- `docs/sutram-stdlib.html` regenerated: **21 modules, 239 functions** (was 21 / 231; +8 ganita).

## Files in the patch (9)

New: `tests/stdlib/ganita_checked.{sm,out,exit}`, `tests/stdlib/ganita_sat.{sm,out,exit}`.
Modified: `lib/ganita.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`.

## SHA-256

```
e93eb25cf877e8299491b4f67473356f750995730d92efa428193cb6b4d532d3  lib/ganita.smlib
f08c578d1f58b59545b8b08c0e0c591d1cfe2ff01fcde051806b1a7a7025339a  tools/proof_props.py
f297e6bf3f821615c2a515f35695a1139c1993c53018ee2f6a3b0ca55807609a  docs/sutram-stdlib.html
f37c2392e3916abd22a7db4ce483a59eabe03dd95bb7d0687ad2b43c589918da  tests/stdlib/ganita_checked.sm
def3c8f8947a482be64cfa704256161a8141517c997330f7517d87bd1e9fc6e7  tests/stdlib/ganita_checked.out
263e8216427d2dea53ca97072124900ea3147a2cd2fd710e01a502fc4a7288f5  tests/stdlib/ganita_sat.sm
da421ba2df5c5f302adf73c1de600c583865c5902e0c11340f6848ddec457fac  tests/stdlib/ganita_sat.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  both .exit files (content: "0")
8c456118b203b31f3095c25ce11ed53977a3de1bc309ce0078089273da2867dc  Muse-to-Sarvam/2026-10-14-round18-checked-arithmetic.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-14-round18-checked-arithmetic.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 164/164) and `python3 tools/proof_props.py` (expect 54/54).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=186, NO-EXPECTATION=3`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
