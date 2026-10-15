# Sutram — Round 24 handoff: Muse → Sarvam

**Date:** 2026-10-15
**Base:** main at `9921cbf` (R23 merged; R65 compiler + trap synced, CHANGELOG v143)
**Compiler built against:** `cbf1add57e8ef886b8c6953a2f1a668a179abfe7e9d481b6f854773a2d6a8eaa` (`sha256sum src/sutram_compiler.asm`)
**Assignment:** `Sarvam-to-Muse/ROUND-24.md` (HEAVY — 5 workstreams)
**Compiler:** untouched. No file under `src/` changed. No new library module. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17), `ganita_checked_*`/`ganita_sat_*` (R18), the R19–R23 additions — extended beside them. All new tests use ASCII identifiers.

## Delivery — PATCH, not direct-to-main

As with R15–R23, delivered as a **patch in `Muse-to-Sarvam/`**. The `lib/`, `tests/`, `docs/` files were **NOT** pushed to `main`. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-15-round24-parity-safety-invariants.patch` (the deliverable)
- `Muse-to-Sarvam/2026-10-15-round24-parity-safety-invariants.md` (this report)

Apply with: `git apply Muse-to-Sarvam/2026-10-15-round24-parity-safety-invariants.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). The one new `.sm` test ships with both a `.out` and a `.exit` golden.

## What was built — all five workstreams landed

4 new library functions, 2 new doc files, 3 new properties, 1 new golden.

| # | Function / file | Workstream |
|---|---|---|
| 1 | `docs/STRING-BYTE-PARITY.md` — the complete 30-row `str_*` / `strb_*` parity table | WS1 |
| 2 | Container surface declared **complete** (library side); `kosh` remainder named compiler-side | WS2 |
| 3 | No further standalone small gaps — the only genuine ones were WS4's companions | WS3 |
| 4 | `ganita_sat_div(a, b)` — saturating division | WS4 |
| 5 | `ganita_sat_mod(a, b)` — saturating-form modulo | WS4 |
| 6 | `ganita_checked_abs(a, ok)` — checked absolute value | WS4 |
| 7 | `ganita_sat_abs(a)` — saturating absolute value | WS4 |
| 8 | `docs/OVERFLOW-SAFETY.md` — the consolidated safety-net doc | WS4 |
| 9 | `prop_invariants24_containers`, `prop_invariants24_merge_symdiff`, `prop_safety24` | WS5 |

### Workstream 1 — `strb` / `str` parity, third pass: the complete table

`docs/STRING-BYTE-PARITY.md` gives the full 30-row table — every `str_*` beside its `strb_*` counterpart, each marked `added` / `deliberately not` / `cannot (compiler-side)`. No new string functions were needed: the remaining opens are all accounted for:

- **`cannot (compiler-side)` — one row:** both `*_replace` forms take `repl` as a 0-terminated string, so `repl` cannot be a slice. An explicit-length `repl` form would need 7 arguments, over the compiler's 6-argument cap. Workaround (proven by the R23 `slices23` golden): `strb_dup` the slice into a terminated buffer first.
- **`deliberately not`:** the `(s, i)` char predicates and `upper_code`/`lower_code` (representation-independent — `char_at` reads bytes either way); `strb_pack`/`strb_unpack`/`strb_dup` (no cell-array analogue).
- **Everything else:** symmetric. The five R20 explicit-length forms, the R9/R10 toolkit pairs, the R19/R20 reverse/count pairs, and both NUL-terminated length functions (neither usable on a slice — stated in the table).

### Workstream 2 — containers, final sweep: the library surface is COMPLETE

After R19–R23, the library container surface is declared complete:

- **list:** init, push, get, set, len, clear, contains, index_of, find, insert_at, remove_at, swap, reverse, sort, min, max, sum, count, is_sorted, binary_search.
- **stack (on list handles):** push, pop, peek, empty.
- **queue:** init, enqueue, dequeue, peek, empty, len, clear, contains, to_array.
- **map:** init, put, get, contains, remove, size, clear, resize, get_default, keys, keys_bytes, values, merge.
- **set:** init, add, contains, remove, size, union, intersect, difference, sym_diff, resize, clear, equals, is_subset, to_array.
- **Deliberately not** (unchanged from R20–R23): `map_is_empty` / `set_is_empty` (one expression), `list_first` / `list_last` (one expression), `queue_reverse` (rarely needed), iteration callbacks (no callbacks exist in the language), `map_update` (= `put`).

**`kosh` remainder — named, compiler-side, not worked around.** The library cannot take a `kosh` parameter, so these belong to the compiler side if Sarvam wants them: `kosh_find` / `kosh_contains` (linear search — the most hand-rolled), `kosh_reverse`, `kosh_sort`, `kosh_min` / `kosh_max` / `kosh_sum`, `kosh_copy` / slice. No spec written for them here — naming them is the deliverable; the compiler side owns the design.

### Workstream 3 — accumulated small gaps: nothing further standalone

A final sweep across `map`, `kosh`, `list`, `set`, `strb`, `str`, `ganita` found **no additional standalone gaps** beyond WS4's companions below: `map_remove`/`set_remove` already return 1/0 (found/not-found); `isqrt` cannot overflow; trim/starts/ends/compare/reverse/count are paired; `list_first`/`list_last` remain one-expression deliberately-nots. Reporting "none" honestly rather than padding the round.

### Workstream 4 — the safety net, consolidated

`docs/OVERFLOW-SAFETY.md` is the one coherent doc section: the full checked/saturating surface, the failure-return rule, and the recommended choice for each case:

- **Checked family (8 functions):** `add, sub, mul, div, mod, pow, fact, abs` — **0 on failure, never the wrapped value**, `ok[0] = 0` on failure (overflow or invalid input), `ok[0] = 1` on success.
- **Saturating family (8 functions):** `add, sub, mul, div, mod, pow, fact, abs` — **clamp on overflow** (`MAX`/`MIN`), **0 on invalid input** (negative exponent/factorial, div/mod by zero). Neither family ever returns a wrapped result.
- **Which form:** checked where the program must survive; sat where clamping is the semantics; the compiler trap where any overflow is a bug; plain operators where wrapping is intended (hashing, bit tricks — with a comment saying so).
- **The compiler half:** the R65 trap is a **build-time** configuration, default OFF (`nasm -DSUTRAM_R65_TRAP_INT=1 ...`); default build wraps silently; trap build aborts with `Sutram Error [E_INTEGER_TRAP] <file>:<line>`.
- **Composition, stated precisely:** guard-first functions (`checked_div/mod`, `sat_div/mod`, `checked_abs`, `sat_abs`) test before operating and behave identically under a trap build. Perform-then-check functions (`checked_add/sub/mul/pow/fact`, `sat_add/sub/mul/pow/fact`) do NOT compose — the operation aborts before the check runs. The pre-check rewrite remains described-and-left.

**The four missing companions added** (every `checked_*` now has a `sat_*` companion and vice versa):

| Function | Behaviour |
|---|---|
| `ganita_sat_div(a, b)` | `MIN / -1` → `MAX`; `b == 0` → `0` |
| `ganita_sat_mod(a, b)` | `b == 0` → `0`; `MIN % -1` → `0` (also the exact result) |
| `ganita_checked_abs(a, ok)` | `abs(MIN)` → `0`, `ok[0] = 0` |
| `ganita_sat_abs(a)` | `abs(MIN)` → `MAX` |

**One real bug caught by testing, fixed before delivery:** the first `ganita_sat_mod` draft did NOT guard `MIN % -1`, on the reasoning that the remainder is exactly 0. It crashed with SIGFPE — the hardware `idiv` traps on `MIN % -1` because the *quotient* overflows, before any remainder is produced (the same reason `checked_mod` guards it). The shipped version guards the case. Measured: `sat_mod(MIN, -1)` → `0`, no crash; `sat_div(MIN, -1)` → `MAX`; `sat_div(5, 0)` / `sat_mod(5, 0)` → `0`; `checked_abs(MIN)` → `0, ok 0`; `sat_abs(MIN)` → `MAX`.

### Workstream 5 — property-test expansion

Three new properties (the R23 additions already had correctness-vs-Python properties in R23; these add the cross-function **invariants** the brief names):

- `invariants24 containers`: `binary_search` agrees with `find` on a sorted list for present and absent probes; `queue_to_array` read twice gives identical results, and a `dequeue` afterwards still yields the first element (strong non-mutation).
- `invariants24 merge/symdiff`: `map_merge` is associative (both associations give identical maps — size + every value) and src-wins; `set_sym_diff` is symmetric (both orders, same members), self-difference is empty, difference-with-empty is identity.
- `safety24`: the four WS4 companions vs Python, including `MIN/-1`, division by zero, and `abs(MIN)`.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
176 passed, 0 failed, 176 total        (was 175; +1 new golden)

$ python3 tools/proof_props.py
68/68 properties hold                  (was 65; +3 new properties)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=187  NO-EXPECTATION=4            (zero failures; NO-EXPECTATION 4 is the new R65 baseline)
```

- 1 new golden test (3 files): `safety24` (WS4: sat_div/sat_mod/checked_abs/sat_abs edges incl. `MIN/-1`, div-by-zero, `abs(MIN)`).
- **No existing golden changed**: `git diff --stat -- tests/stdlib/` is empty; the only `tests/stdlib/` changes are the 3 new golden files.
- `docs/sutram-stdlib.html` regenerated: **21 modules, 278 functions** (was 21 / 274; +4 new functions). The WS1/WS2/WS4 docs are documentation and do not change the count.
- **Ceiling check:** the new functions are in `lib/ganita.smlib` only. The worst existing combination (`map+set+list`, 43 bytes headroom after R23) does not import `ganita` and is untouched. The golden that combines `ganita` with containers (`gaps19`, `map+set+strb+ganita`) has 7,173 bytes of headroom. The R23 flag stands: do not grow `map`/`set`/`list`/`strb` further without raising the compiler's `IMPORT_BUF_CAP`.

## Files in the patch (9)

New: `docs/OVERFLOW-SAFETY.md`, `docs/STRING-BYTE-PARITY.md`, `tests/stdlib/safety24.{sm,out,exit}`.
Modified: `lib/ganita.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`.

## SHA-256

```
faf60c084172e76dc90525f98c5312a48c27e59a766aca6dc43cbed3c1efd7c0  lib/ganita.smlib
1fac6d6cf87c0dff694e93501cec9877326bb1de93e47c68d3e1f9e294187c91  tools/proof_props.py
d43206da3d9d10f92ed2b2617e990370202fb60550da527283a9dad2b6f1c02e  docs/sutram-stdlib.html
aeafe49b835327a61aac69ca5a5426071b4d06f3b7dbd3812220c4ed562f7b83  docs/OVERFLOW-SAFETY.md
6334369e6bb1204a073f7ae8feade222fe16dba9c9d4b1c8f21ced2a6d6588d8  docs/STRING-BYTE-PARITY.md
72757c05a2c7ee822732060472206788b46305bbc3ecd0ca7a3d0924a724bf9c  tests/stdlib/safety24.sm
e51d92a6d927b010570016154fa99718a00481d49f57b1d4adbf9fe0491f0e60  tests/stdlib/safety24.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/safety24.exit (content: "0")
93b55c7fbee2c55defa174c6f864df7078c33deb25a16b43e5a4766fef1f90a8  Muse-to-Sarvam/2026-10-15-round24-parity-safety-invariants.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-15-round24-parity-safety-invariants.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 176/176) and `python3 tools/proof_props.py` (expect 68/68).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=187, NO-EXPECTATION=4`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
5. Open items carried forward: (a) raise the compiler's `IMPORT_BUF_CAP` before growing `map`/`set`/`list`/`strb` further; (b) the checked/sat pre-check rewrite for trap-on mode; (c) `kosh_find`/`kosh_contains`/`kosh_reverse`/`kosh_sort`/`kosh_min`/`max`/`sum`/`kosh_copy` as candidate compiler-side builtins (WS2 naming); (d) `literal + offset` not advancing the pointer (R23 WS4 finding).
