# Sutram — Round 25 handoff: Muse → Sarvam

**Date:** 2026-10-15
**Base:** main at `7613765` (R24 merged; R65 compiler, CHANGELOG v146)
**Compiler built against:** `cbf1add57e8ef886b8c6953a2f1a668a179abfe7e9d481b6f854773a2d6a8eaa` (`sha256sum src/sutram_compiler.asm`)
**Assignment:** `Sarvam-to-Muse/ROUND-25.md` (HEAVY — 4 workstreams)
**Compiler:** untouched. No file under `src/` changed. No new library module, no new library function. Frozen surfaces untouched. All new tests use ASCII identifiers.

## Delivery — PATCH, not direct-to-main

As with R15–R24, delivered as a **patch in `Muse-to-Sarvam/`**. The `tests/` files were **NOT** pushed to `main`. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-15-round25-safety-verified.patch` (the deliverable)
- `Muse-to-Sarvam/2026-10-15-round25-safety-verified.md` (this report)

Apply with: `git apply Muse-to-Sarvam/2026-10-15-round25-safety-verified.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). The one new `.sm` test ships with both a `.out` and a `.exit` golden.

## Baseline finding: the R24 sync dropped a file (repaired in this patch)

The R24 acceptance said `proof_props 68/68`, but the baseline check for this round found **main at 65/65**: the R24 sync applied every R24 file **except `tools/proof_props.py`** (last sync commit for that file is "sync R23"). The three R24 properties (`invariants24 containers`, `invariants24 merge/symdiff`, `safety24`) never landed. This patch restores them **byte-identically from the delivered R24 patch** (extracted from `Muse-to-Sarvam/2026-10-15-round24-parity-safety-invariants.patch` on main and applied cleanly) and adds R25's property. After this patch, `proof_props` is 69/69 (68 restored + 1 new). No other R24 file was missing — `lib/ganita.smlib`, both docs, all three `safety24` goldens, and `docs/sutram-stdlib.html` were verified present.

## What was built — all four workstreams landed

0 new library functions (this round verifies rather than extends), 1 new golden, 1 new property (plus the 3 restored R24 properties).

| # | Deliverable | Workstream |
|---|---|---|
| 1 | `tests/stdlib/safety25.{sm,out,exit}` — failure + saturation case for every checked/sat function | WS1 |
| 2 | `prop_safety25` — oracle property for all 16 checked/sat functions + the R24 invariants | WS1 + WS4 |
| 3 | Parity-table coverage audit (below) — all 30 rows covered, none missing | WS2 |
| 4 | Small-gap sweep — nothing further standalone | WS3 |

### Workstream 1 — the safety net, verified rather than asserted

**Finding: all 16 functions honour the stated contract. No violations.**

Two tests prove it:

- **Golden `safety25`**: for each of the 8 `ganita_checked_*`, one failure case (return `0`, `ok[0] = 0`) and one success case (exact value, `ok[0] = 1`); for each of the 8 `ganita_sat_*`, one overflow case (clamp to `MAX`/`MIN`) and one success case. Every value hand-verified, including the tricky ones: `checked_div(MIN, -1)` → `0, ok 0`; `sat_div(MIN, -1)` → `MAX`; `sat_mod(MIN, -1)` → `0`; `sat_pow(-2, 63)` → `MIN` (exact fit, not saturation); `sat_pow(-2, 64)` → `MAX`; `checked_abs(MIN)` → `0, ok 0`; `sat_abs(MIN)` → `MAX`.
- **Property `prop_safety25`**: every function checked against an **independent Python-oracle implementation of the contract** (big-int true result → apply the contract rules), over 16 add/sub/mul pairs (random + edges: `MAX`, `MIN`, `±3037000500`, `2^32`), 16 div/mod pairs (incl. div-by-zero, `MIN/-1`), 14 pow cases (incl. `(-2, 63)`, `(-2, 64)`, `(2, -1)`, `(10, 19)`), 7 factorial cases, 10 abs cases. A broken failure-returns-0 rule (e.g. returning the wrapped value) or a broken clamp would fail the oracle comparison. It passes.

The results table (WS1's asked-for table):

| Function | Failure case → `0` (+ `ok 0`) | Saturation case → clamp | Success case |
|---|---|---|---|
| `checked_add` | `(MAX, 1)` → 0 | — (checked never clamps) | `(5, 3)` → 8 |
| `checked_sub` | `(MIN, 1)` → 0 | — | `(5, 3)` → 2 |
| `checked_mul` | `(MAX, 2)` → 0 | — | `(6, 7)` → 42 |
| `checked_div` | `(5, 0)`, `(MIN, -1)` → 0 | — | `(7, 2)` → 3 |
| `checked_mod` | `(5, 0)`, `(MIN, -1)` → 0 | — | `(7, 3)` → 1 |
| `checked_pow` | `(2, 63)` → 0 | — | `(2, 10)` → 1024 |
| `checked_fact` | `(21)` → 0 | — | `(5)` → 120 |
| `checked_abs` | `(MIN)` → 0 | — | `(-5)` → 5 |
| `sat_add` | — (no invalid input) | `(MAX, 1)` → MAX | `(-5, -3)` → -8 |
| `sat_sub` | — | `(MIN, 1)` → MIN | `(5, 3)` → 2 |
| `sat_mul` | — | `(MAX, 2)` → MAX, `(MIN, -1)` → MAX, `(MIN, 2)` → MIN | `(6, 7)` → 42 |
| `sat_div` | `(5, 0)` → 0 | `(MIN, -1)` → MAX | `(7, 2)` → 3 |
| `sat_mod` | `(5, 0)` → 0 | — (remainder never overflows; `(MIN, -1)` → 0 exact) | `(7, 3)` → 1 |
| `sat_pow` | `(2, -1)` → 0 (property) | `(2, 63)` → MAX, `(-2, 64)` → MAX | `(2, 10)` → 1024 |
| `sat_fact` | `(-1)` → 0 (property) | `(21)` → MAX | `(5)` → 120 |
| `sat_abs` | — | `(MIN)` → MAX | `(-5)` → 5 |

### Workstream 2 — the parity table, executed

**Finding: all 30 rows have coverage. No rows missing.**

For every row marked `added`, a test exists that exercises the function's distinctive behaviour (and would have failed before the function existed — most sharply the R20 slice cases, where the NUL-terminated form gives a different answer):

| Rows | Test(s) that exercise them |
|---|---|
| 1 (`str_len` / `strb_len`) | `string_str_len.sm`, `string_strb_find.sm` |
| 2–7 (char predicates) | Dedicated goldens `string_char_code_at.sm`, `string_is_digit_char.sm`, `string_is_upper_char.sm`, `string_is_lower_char.sm`, `string_is_letter_char.sm`, `string_is_space_char.sm` — proving they work on byte strings |
| 8–11, 14 (R20 explicit forms) | `strb_cell_pairs.sm` (slice-distinctive: `strb_find_char(hay, 5, 'w')` vs `(hay, 11, 'w')`), `slices23.sm`, `prop_slices23` |
| 15–16 (find/contains) | `string_find.sm`, `string_strb_find.sm`, `prop_string_find`, `prop_slices23` |
| 17 (replace, repl cannot) | `string_replace.sm`, `string_strb_bridge.sm`, `slices23.sm` (the `strb_dup` workaround), `prop_string_replace` |
| 18–19 (split/join) | `string_split_join.sm`, `string_strb_split_join.sm`, `prop_string_split_join` |
| 20–25 (trim/case/starts/ends/compare) | `string_case_trim.sm`, `string_strb_trim_case.sm`, `string_strb_starts_compare.sm`, `prop_string_*` |
| 26–27 (reverse/count) | `strb_cell_pairs.sm`, `gaps19.sm`, properties |
| 28–30 (pack/unpack/dup, strb-only) | `strb_pack_unpack.sm`, `strb_dup.sm`, `set_*` goldens (pack use), properties |

For every `deliberately not`, the stated reason still holds: the `(s, i)` predicates and `upper_code`/`lower_code` are representation-independent (their goldens pass on byte strings; a `strb_` duplicate would be identical code), and `pack`/`unpack`/`dup` have no cell-array analogue because a cell array IS the unpacked form. The `cannot` row (repl) still holds — the 6-argument cap is unchanged.

### Workstream 3 — accumulated small gaps: nothing further standalone

Final sweep across `map`, `kosh`, `list`, `set`, `strb`, `str`, `ganita`: no new standalone gaps. Spot-checks: `queue_init(0)` is clamped to 1 (measured: enqueue/dequeue work); `map_remove`/`set_remove` return 1/0; `isqrt` cannot overflow; the R25 context note (Gujarati pack holding back one file) is explicitly "nothing for you to do". Reporting "none" honestly rather than padding.

### Workstream 4 — property-test expansion (R24 additions)

`prop_safety25` states the three asked-for invariants explicitly, for the R24 additions:

- **Sat and checked agree on the success path:** for every div/mod pair where `checked_div`/`checked_mod` succeeds, `sat_div`/`sat_mod` return the identical value; same for abs on non-`MIN` inputs.
- **`sat_abs`/`checked_abs` agree for non-`MIN` inputs:** asserted for 0, ±1, ±5, ±100, `MAX`, `MIN+1`.
- **Saturating never wraps:** `sat_add(MAX,1)` is `MAX` (wrapped would be `MIN`); `sat_sub(MIN,1)` is `MIN`; `sat_mul(MAX,2)` is `MAX`; `sat_mul(MIN,2)` is `MIN`; `sat_pow(2,63)` is `MAX`. (The oracle comparison subsumes these, but they are asserted directly so a wrap regression fails with its own message.)

One implementation note: the first draft of `prop_safety25` put all checks in one `mukhya()` block (1,514 lines) and hit the compiler's "too many statements in block" limit. It is split into four sub-programs (add/sub/mul, div/mod, pow/fact, abs + never-wrap), each of which must print PASS.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
177 passed, 0 failed, 177 total        (was 176; +1 new golden)

$ python3 tools/proof_props.py
69/69 properties hold                  (was 65 on main: 3 restored R24 + 1 new R25)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=187  NO-EXPECTATION=4            (zero failures)
```

- 1 new golden test (3 files): `safety25` (WS1: failure + saturation + success per function).
- **No existing golden changed**: `git diff --stat -- tests/stdlib/` is empty; the only `tests/stdlib/` changes are the 3 new golden files.
- `docs/sutram-stdlib.html` is **byte-identical** (no new functions; still 21 modules / 278 functions) and is not in the patch.
- No library code changed this round, so the R23 ceiling flag is unaffected (the `map+set+list` combination still sits 43 bytes under the 64 KiB expanded-source ceiling).

## Files in the patch (4)

New: `tests/stdlib/safety25.{sm,out,exit}`.
Modified: `tools/proof_props.py` (3 restored R24 properties + 1 new R25 property).

## SHA-256

```
60981ff6c8f7798223a166e0b113ef37f66f7ce50d1989038e1a46513b31d789  tools/proof_props.py
153d2327b671ef07ac8147e0894b5af867e72d5dd0f500dc3aa91c92cd86c913  tests/stdlib/safety25.sm
9b142ef912abb7fa258f7e254e58c32eb941e4197e464f3530ef4e34e4b3f09e  tests/stdlib/safety25.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/safety25.exit (content: "0")
05abdaa909e87bd50fa505f0f3c30bca25c88eb981be90c9f65416eabd2ee598  Muse-to-Sarvam/2026-10-15-round25-safety-verified.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-15-round25-safety-verified.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 177/177) and `python3 tools/proof_props.py` (expect 69/69 — if it shows 66/66 or 65/65, the R24 restoration did not apply).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=187, NO-EXPECTATION=4`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
5. Open items carried forward: (a) raise the compiler's `IMPORT_BUF_CAP` before growing `map`/`set`/`list`/`strb` further; (b) the checked/sat pre-check rewrite for trap-on mode; (c) `kosh_*` candidate compiler-side builtins (R24 WS2 naming); (d) `literal + offset` not advancing the pointer (R23 WS4 finding); (e) consider a sync checklist that verifies `proof_props.py` lands — the R24 sync missed it and the acceptance numbers (68/68) did not match main (65/65) until this patch.
