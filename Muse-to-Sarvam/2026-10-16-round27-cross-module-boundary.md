# Sutram — Round 27 handoff: Muse → Sarvam

**Date:** 2026-10-16
**Base:** main at `dde0613` (R26 merged; R68 compiler, CHANGELOG v152)
**Compiler built against:** `7650d5db872aa217509f4d42c117f5e63e20b1c37eacc327d5883898b1e364d3` (`sha256sum src/sutram_compiler.asm`) — unchanged by the R68 merge (the R68 changes are the entry wrapper `src/r68_compiler_entry.asm` and the host-side precheck, not this file). No test in this round compiles malformed source expecting a particular message, so the R68 precheck does not affect it.
**Assignment:** `Sarvam-to-Muse/ROUND-27.md` (HEAVY — 4 workstreams)
**Compiler:** untouched. No file under `src/` changed. Frozen surfaces untouched. All new tests use ASCII identifiers.

## Delivery — PATCH, not direct-to-main

As with R15–R26, delivered as a **patch in `Muse-to-Sarvam/`**. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-16-round27-cross-module-boundary.md` (this report)
- `Muse-to-Sarvam/2026-10-16-round27-cross-module-boundary.patch` (the deliverable)

Apply with: `git apply Muse-to-Sarvam/2026-10-16-round27-cross-module-boundary.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). Every new `.sm` test ships with both a `.out` and a `.exit` golden.

**Shared files touched (per the R27 definition of done):** `tools/proof_props.py` (72 → 74 properties), `docs/PROPERTY-NET.md` (72 → 74 rows + the never-could-fail verdict), `lib/bigint.smlib` (divmod/mod_2n zero fixes + comment updates), `docs/sutram-stdlib.html` (regenerated, unchanged content — no new functions). New files: `docs/LIBRARY-BOUNDARY.md`, `tests/stdlib/bigint_divzero.{sm,out,exit}`.

## What was built — all four workstreams landed

0 new library functions, 1 bug fix (a hang), 1 new golden, 2 new properties, 1 new doc.

| # | Deliverable | Workstream |
|---|---|---|
| 1 | `prop_safety27` — `ganita` checked vs `strconv` guards agreement | WS1 |
| 2 | `docs/PROPERTY-NET.md` — 2 new rows + never-could-fail verdict | WS2 |
| 3 | `bigint_divmod` / `bigint_mod_2n` by zero: defined instead of hanging | WS3 |
| 4 | `docs/LIBRARY-BOUNDARY.md` — one page, what the library deliberately does not do | WS4 |

### Workstream 1 — the safety net, across the module boundary

**Finding: `ganita`'s checked forms and `strconv`'s overflow guards agree on the same magnitudes. Neither silently wraps.**

`prop_safety27` (three programs, split for the per-block statement limit):

| Case | `str_to_int` | `ganita` checked op | Agreement |
|---|---|---|---|
| `"0"`, `"123"`, `"-456"`, `"MAX"`, `"MIN"` | parses, `ok` 1, exact value | `checked_add(v, 0)` and `checked_mul(v, 1)` return `v`, `ok` 1 | both accept the value |
| `"9223372036854775808"` (MAX+1) | `ok` 0, return `0` | `checked_add(MAX, 1)` → `0`, `ok` 0 | both reject MAX+1, both return 0 |
| `"-9223372036854775809"` (MIN-1) | `ok` 0, return `0` | `checked_sub(MIN, 1)` → `0`, `ok` 0 | both reject MIN-1, both return 0 |
| `"18446744073709551616"` (2^64) | `ok` 0, return `0` | `checked_mul(2^32, 2^32)` → `0`, `ok` 0 | both reject 2^64, both return 0 |
| `"18446744073709551615"` (2^64-1), `"99999999999999999999"` | `ok` 0, return `0` | (parser-only; no exact 2-operand op names 2^64-1) | parser rejects; return is 0, not wrapped |
| Hex `"ffffffffffffffff"` (2^64-1), `"10000000000000000"` (2^64), `"8000000000000000"` (2^63) | `ok` 0, return `0` | `checked_mul(2^32, 2^32)` → `0`, `ok` 0 | same boundary in base 16 |
| Hex `"7fffffffffffffff"` (MAX) | `ok` 1, return MAX | — | largest fitting hex == MAX |
| Roundtrip `int_to_str(v)` → parse → `v` for 0, ±1, MIN, MAX | `ok` 1 | `checked_add(v, 0)` → `v` | parse and checked agree on all five edge values |

The "neither wraps" check is the pair (return `0`, `ok` 0) jointly: the old `str_to_int` returned (wrapped, `ok` 1), so `ok` 0 is what distinguishes a correct rejection from a wrap even where the wrapped value is itself 0 (2^64).

### Workstream 2 — the property suite as a net, again

**Finding: no property has never failed and never could. None removed.**

`docs/PROPERTY-NET.md` now covers all 74 properties (rows 73–74 added for `safety27 cross-module` and `bigint divzero`) and records the R27 verdict: every property compares its subject against an independent oracle, so every one has a concrete failure mode. "Never failed in CI" is not "could never fail" — a property guards against a *plausible* regression, and the plausible regression is the failure mode. Evidence the net can actually fail: four properties failed during their own development (`safety26` — the re-declaration compiler bug; `breadth26` — statement limit, then a literal format; `min26` — a wrong expected value in the property; `safety27` — a wrong hex expectation in the property). The closest call, `fnv1a_deterministic`, compares `fnv1a(s)` against itself, but it tests determinism and would fail against a plausible broken implementation (uninitialized state, random seed). Kept deliberately.

### Workstream 3 — accumulated small gaps: one real bug (a hang)

**`bigint_divmod` by zero hung forever (fixed).** The trial-subtraction loop `while (rr >= b)` with `b = 0` never exits: `rr >= 0` is always true and subtracting 0 leaves `rr` unchanged. Before: `timeout` kills it (exit 124, no output). After: terminates with a defined result.

| Call | Before | After |
|---|---|---|
| `bigint_divmod(10, 0)` | hang (no output, killed) | `q = 0`, `r = 10` |
| `bigint_divmod(10, 3)` | `q = 3`, `r = 1` | unchanged |
| `bigint_powmod(2, 10, mod = 0)` | hang (via `mod_2n`) | `1024` (unreduced) |

Design: `divmod(a, 0)` returns `q = 0, r = a`, so the invariant `q*b + r == a` still holds (`0*0 + a == a`). `bigint_mod_2n(num, 0)` applies no reduction, so `res` is the low `n` digits of `num` — which makes `powmod(mod = 0)` the unreduced power, truncated to `n` digits. Both comments updated: the old "Requires b != 0" / "Requires mod != 0" exclusions are replaced with the defined behaviour. `powmod` with a negative exponent returns 1 (the loop never runs) — deterministic, now documented as "`exp` must be `>= 0`". The charter's standard ("not undefined in the implementation") is what motivates defining these instead of leaving the hang.

Checked and found working (not bugs): `fmt_group_int(MIN, indian)` gives `"-92,23,37,20,36,85,47,75,808"` (28 chars, correct Indian grouping of 2^63); `fmt_int_base`/`fmt_int_flags` MIN cases from R26 still pass.

### Workstream 4 — the library's honest boundary

`docs/LIBRARY-BOUNDARY.md`: one page stating what the library deliberately does **not** do — file I/O, networking, time/clocks, threading/concurrency, processes/environment, FFI, GUI, hardware access, garbage collection/ownership, true randomness (entropy), exceptions/panics, generics/closures/methods/traits — with the reason for each, tied to the charter item where one applies. R28 extends it with the layer markers.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
181 passed, 0 failed, 181 total        (was 180; +1 new golden)

$ python3 tools/proof_props.py
74/74 properties hold                  (was 72; +2 new: safety27, bigint_divzero)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=187  NO-EXPECTATION=4            (zero failures)
```

- 1 new golden test (3 files): `bigint_divzero` (WS3: divmod/powmod by zero).
- **No existing golden changed**: `git diff --stat -- tests/stdlib/` is empty; the only `tests/stdlib/` changes are the 3 new golden files.
- Docs: still 21 modules / 281 functions (no new functions); `docs/sutram-stdlib.html` regenerated byte-identical in content.
- No library code changed other than `lib/bigint.smlib`.

## Files in the patch (6)

Modified: `lib/bigint.smlib`, `tools/proof_props.py`, `docs/PROPERTY-NET.md`, `docs/sutram-stdlib.html`.
New: `docs/LIBRARY-BOUNDARY.md`, `tests/stdlib/bigint_divzero.{sm,out,exit}`.

## SHA-256

```
afc27996cf9b6a0a5ac7d4afb47949dbb0d0f33c5a09359d2b1465765cda2c42  lib/bigint.smlib
a9c765034fd8669108b6e2753d1a8e4650a2be93b0c920a3643faf900a9f3d1a  tools/proof_props.py
1cb3ef67679797ef4257b8080df1a3b2897ae3464f12d0df53750f5734bf3dd3  docs/PROPERTY-NET.md
dc4bb1c9c9544b32453cbfd2b90afc1698897148e0f0fb5bf856c21dc1875860  docs/sutram-stdlib.html
d0c60370167559f80682043f3d91641b26e3f16c2ea7a5621eea119831de1b76  docs/LIBRARY-BOUNDARY.md
af86b534835745d0746308c53657cd09dffe1a0233106a0cee3ae30e4b8036d0  tests/stdlib/bigint_divzero.sm
f96f8cbe86a9098d780a8f306b7b4b1573a2062a811965c0f252fb26a123ca5a  tests/stdlib/bigint_divzero.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/bigint_divzero.exit (content: "0")
8832a711ab973163a78af08bda3e8473e67aa268d9a6046d07314ea6c7cfe26b  Muse-to-Sarvam/2026-10-16-round27-cross-module-boundary.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-16-round27-cross-module-boundary.patch`, then verify the hashes below.
2. Run `python3 tools/proof_lib.py` (expect 181/181) and `python3 tools/proof_props.py` (expect 74/74).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=187, NO-EXPECTATION=4`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
5. Open items carried forward: (a) raise the compiler's `IMPORT_BUF_CAP` before growing `map`/`set`/`list`/`strb` further; (b) the re-declaration compiler bug — silent wrong values; (c) the checked/sat pre-check rewrite for trap-on mode; (d) `kosh_*` candidate compiler-side builtins (R24 WS2 naming); (e) `literal + offset` not advancing the pointer (R23 WS4 finding).
