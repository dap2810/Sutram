# Sutram — Round 26 handoff: Muse → Sarvam

**Date:** 2026-10-16
**Base:** main at `a700bfd` (R25 merged; R67 compiler, CHANGELOG v146+)
**Compiler built against:** `7650d5db872aa217509f4d42c117f5e63e20b1c37eacc327d5883898b1e364d3` (`sha256sum src/sutram_compiler.asm`)
**Assignment:** `Sarvam-to-Muse/ROUND-26.md` (HEAVY — 4 workstreams)
**Compiler:** untouched. No file under `src/` changed. Frozen surfaces untouched. All new tests use ASCII identifiers.

## Delivery — PATCH, not direct-to-main

As with R15–R25, delivered as a **patch in `Muse-to-Sarvam/`**. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-16-round26-interaction-breadth-min.md` (this report)
- `Muse-to-Sarvam/2026-10-16-round26-interaction-breadth-min.patch` (the deliverable)

Apply with: `git apply Muse-to-Sarvam/2026-10-16-round26-interaction-breadth-min.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). Every new `.sm` test ships with both a `.out` and a `.exit` golden.

**Overlap note (per the R26 definition of done):** this patch touches `tools/proof_props.py`, which R25 also touched — the same file the R24 sync dropped. It applies cleanly to current main (which has the R25 version), and the report states the resulting property count (72) so a sync can check it directly.

## What was built — all four workstreams landed

3 new library functions, 3 bug fixes, 3 new goldens, 3 new properties, 1 new doc.

| # | Deliverable | Workstream |
|---|---|---|
| 1 | `prop_safety26` — checked/saturating interaction, randomized | WS1 |
| 2 | `docs/PROPERTY-NET.md` — what would have to break, per property | WS2 |
| 3 | `str_to_int` / `str_to_int_base` overflow guards (0 + `ok` 0 on overflow) | WS3 |
| 4 | `int_to_str(MIN)`, `fmt_digits_base` negatives, `fmt_int_base`/`fmt_int_flags` MIN fixes | WS3 |
| 5 | `math_rand`, `math_clamp`, `str_to_float` | WS4 |
| 6 | Goldens `breadth26`, `strconv_overflow`, `fmt_min`; properties `breadth26`, `min26` | WS3 + WS4 |

### Workstream 1 — the safety net, one level deeper (interaction)

**Finding: checked and saturating agree everywhere. No violations.**

`prop_safety26` states the interaction as cross-function agreement, not per-function oracle checks (those were R25):

- **Agreement on the success path:** for all 8 operations, where `checked_*` succeeds (`ok` 1), `sat_*` returns the identical value.
- **Agreement on the failure path:** where `checked_*` fails, `sat_*` is the clamp (overflow) or 0 (invalid input: div/mod by zero, negative pow/fact exponent). The `MIN/-1` split is asserted explicitly: `sat_div(MIN,-1)` is `MAX` (overflow), `sat_mod(MIN,-1)` is `0` (exact).
- **Never-wrap, randomized:** fresh random battery (fixed seed) — 20 add/sub/mul/div/mod pairs incl. `±10^12` randoms and edges, 15 pow cases, 11 fact cases, 11 abs cases — every saturating result equals the Python clamp, plus direct never-wrap spot checks (`sat_mul(MIN,MIN)` is `MAX`, `sat_pow(-2,65)` is `MIN`, `sat_fact(30)` is `MAX`).

Interaction results table:

| Operation | Success path | Overflow path | Invalid-input path |
|---|---|---|---|
| add/sub/mul | sat == checked | sat == clamp | — (no invalid input) |
| div | sat == checked | `MIN/-1` → sat `MAX` | div-by-zero → sat `0` |
| mod | sat == checked | — (remainder never overflows) | div-by-zero → sat `0`; `MIN/-1` → sat `0` exact |
| pow/fact | sat == checked | sat == clamp | negative exp/n → sat `0` |
| abs | sat == checked (non-`MIN`) | `MIN` → sat `MAX` | — |

### Workstream 2 — the property suite as a regression net

**Finding: all 72 properties are genuine, falsifiable tests. None removed.**

`docs/PROPERTY-NET.md` states, for each of the 72 properties (69 at round start + 3 new this round), in one line, what would have to break for it to fail. Method: every assertion was read; the four most suspicious properties (`fnv1a_deterministic`, `fnv1a_avalanche`, `map_collision`, `map_keys_count`) were read line by line. Two caveats recorded, neither vacuous:

- `hash fnv1a avalanche` checks five fixed pairs hash differently — a distinctness check, not a statistical avalanche measurement (a constant hash still fails it).
- `string split/join` and `strb split/join` skip the trailing-separator edge (documented in code: it yields an extra empty segment).

### Workstream 3 — accumulated small gaps: three real bugs, all with before/after

**1. `str_to_int` / `str_to_int_base` silently wrapped on overflow (fixed).** Both accumulated without any overflow check, so a too-large input returned a wrapped value with `ok[0] = 1` — the same failure mode the checked family exists to prevent. Before/after:

| Input | Before | After |
|---|---|---|
| `str_to_int("99999999999999999999")` | wrapped value, `ok` 1 | `0`, `ok` 0 |
| `str_to_int("9223372036854775808")` | wrapped value, `ok` 1 | `0`, `ok` 0 |
| `str_to_int("9223372036854775807")` | `MAX`, `ok` 1 | unchanged |
| `str_to_int("-9223372036854775808")` | `MIN`, `ok` 1 | unchanged (boundary is exact) |
| `str_to_int_base("fffffffffffffffff", 16)` | wrapped value, `ok` 1 | `0`, `ok` 0 |
| `str_to_int_base("7fffffffffffffff", 16)` | `MAX`, `ok` 1 | unchanged |

The guard is a pre-multiplication bound check (`val > MAX/base`, plus the exact-boundary digit check), so no overflow ever occurs in the check itself. No existing golden tested an overflowing input, so no golden changed.

**2. `int_to_str(MIN)` returned `"-"` (fixed).** `val = 0 - val` wraps MIN back to MIN, the digit loop never runs, and the output is just the minus sign. Before: `n = 1`, `"-"`. After: `n = 20`, `"-9223372036854775808"`. Fixed with a direct write of the MIN string.

**3. `fmt` MIN handling (fixed).** `fmt_digits_base`'s comment claimed "write |v|" but for any negative `v` it returned 0 (empty) — the digit loop never ran. `fmt_int_base(MIN, …)` returned 0; `fmt_int_flags(MIN, …)` returned 0; the fmt header documented MIN as "excluded". Before/after:

| Call | Before | After |
|---|---|---|
| `fmt_digits_base(-5, 10)` | `0`, empty | `1`, `"5"` |
| `fmt_int_base(MIN, 10)` | `0`, empty | `20`, `"-9223372036854775808"` |
| `fmt_int_base(MIN, 16)` | `0`, empty | `17`, `"-8000000000000000"` |
| `fmt_int_base(MIN, 2)` | `0`, empty | `65`, `"-"` + 64 binary digits |
| `fmt_int_flags(MIN, 16, prefix)` | `0`, empty | `19`, `"-0x8000000000000000"` |
| `fmt_digits(MIN)` | `0`, empty | `19`, `"9223372036854775808"` |

One fix in `fmt_digits_base` covers all of them: for MIN, split `|MIN| = 2^63` as `hi * b + lo` with `hi = -(MIN / b)`, `lo = -(MIN % b)` (both fit in int64), convert `hi`, append the `lo` digit; other negatives just negate. `fmt_digits` delegates the MIN case to `fmt_digits_base`. The header's MIN exclusion is removed and replaced with the handling note.

### Workstream 4 — library-breadth pass, honestly scoped

The ten most likely to be wanted next by someone writing a real program, with the three implemented first:

| # | Candidate | Verdict |
|---|---|---|
| 1 | `math_rand` — PRNG | **IMPLEMENTED** (below) |
| 2 | `str_to_float` — parse a decimal float | **IMPLEMENTED** (below) |
| 3 | `math_clamp` — clamp to `[lo, hi]` | **IMPLEMENTED** (below) |
| 4 | `map_keys_sorted` — map keys in sorted order | SKIPPED: `map` module — the `map+set+list` combination sits ~43 bytes under the 64 KiB expanded-source ceiling; any `map` addition breaks it. Needs the compiler-side ceiling raise first. |
| 5 | String sort (`list_sort_ptrs`) — sort byte-string pointers | SKIPPED: `list`/`sort` modules — same ceiling. |
| 6 | `strb_trim_all` — strip all ASCII whitespace, not just space | SKIPPED: `strb` module — same ceiling (strb is imported by map/set). |
| 7 | `list_shuffle` | SKIPPED: `list` module — same ceiling, plus needs the RNG (now available). |
| 8 | `list_map` / `list_filter` (higher-order) | SKIPPED: CANNOT — the language has no callbacks/closures; compiler-side. |
| 9 | `strb_to_hex` — byte-string hex encoding | SKIPPED: `strb` module — same ceiling. |
| 10 | `file read_lines` — line iteration | SKIPPED: deliberately not — fileio was deleted in R1 (builtins are the API). |

**Implemented:**

- `math_rand(state)` — Knuth MMIX LCG (`state = state * 6364136223846793005 + 1442695040888963407`, wrapping). `state` is a 1-cell seed array, updated in place, new state returned. Any seed works, including 0 (first output from seed 0 is the increment `1442695040888963407`, verified against Python). Deterministic: same seed, same sequence (verified: two state arrays, seed 1, identical first three values `7806831264735756412, -9049835345590740197, -6486624265480721906`). The language has no entropy source, so the caller owns the seed. Full 64-bit state returned (may be negative).
- `math_clamp(v, lo, hi)` — `lo` if `v < lo`, `hi` if `v > hi`, else `v`. Requires `lo <= hi` (if `lo > hi`, returns `lo` — the first branch wins, documented).
- `str_to_float(buf, n, ok)` — parses `[-] digits [. digits] [(e|E) [-] digits]`; at least one digit in the integer or fraction part. Same conventions as `str_to_int`: no whitespace, no `+`, no `inf`/`nan` → `ok` 0. Malformed input or overflow (`|value| > ~1.8e308`) → `ok` 0, return `0.0`. Extreme underflow → `0.0` with `ok` 1 (as `strtod`). Mantissa accumulated in int64 (18 significant digits); further digits only move the decimal exponent. Verified against Python `float()` within 1e-9 relative (property) and by golden (`"3.14159"`, `"-2e-2"` → `-0.02`, `".5"` → `0.5`, `"1e5"`, `"1e400"` → `ok` 0, `"1e-999"` → `0.0` `ok` 1, `"1x"`/`"1e"`/`"."`/`"e5"`/`"1.2.3"`/`"+1"`/`" 1"`/`"inf"` → `ok` 0).

All three live in ceiling-safe modules (`math`, `strconv`) — neither is in the `map+set+list` import closure, so the ceiling is unaffected.

## A compiler bug found mid-round (not fixed — `src/` is off-limits)

**Re-declaring a variable in one function silently reads the wrong value.** Minimal repro:

```
vitti cv = ganita_checked_mul(2, 3, ok)   # cv = 6
likha(cv)                                  # prints 6
vitti cv = ganita_checked_mul(7, 8, ok)   # cv = 56
likha(cv)                                  # prints 6, NOT 56
```

The second declaration's reads resolve to the first declaration's slot. Worse, in `str_to_float` a re-declared `vitti k` in two branches corrupted `exp10` on repeat calls (second call to `str_to_float` returned `0.2` for `"2e-2"` instead of `0.02`). The library now contains **zero** duplicate `vitti <name>` declarations in any one function (verified by scan across `lib/`), and the new property generators use unique names per call. Carried forward as a compiler-side issue: re-declaration should either be an error or work — silent wrong values are the worst option. (My own mid-round false alarms — the safety26 failure and two str_to_float failures — both traced to this bug or to hand-typed digit strings in test programs, not to library defects; the digit strings in the shipped goldens are machine-generated and verified against Python.)

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
180 passed, 0 failed, 180 total        (was 177; +3 new goldens)

$ python3 tools/proof_props.py
72/72 properties hold                  (was 69; +3 new: safety26, breadth26, min26)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=187  NO-EXPECTATION=4            (zero failures)
```

- 3 new golden tests (9 files): `breadth26` (WS4), `strconv_overflow` (WS3: parse overflow + `int_to_str`), `fmt_min` (WS3: MIN formatting).
- **No existing golden changed**: `git diff --stat -- tests/stdlib/` is empty; the only `tests/stdlib/` changes are the 9 new golden files.
- Docs: 21 modules / **281 functions** (was 278; +3), `docs/sutram-stdlib.html` regenerated; `docs/PROPERTY-NET.md` is new.
- No library code changed other than the above; the `map+set+list` ceiling is unaffected (no change to `map`, `set`, `list`, `sort`, `strb`, `hash`).

## Files in the patch (16)

Modified: `lib/math.smlib`, `lib/strconv.smlib`, `lib/fmt.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`.
New: `docs/PROPERTY-NET.md`, `tests/stdlib/breadth26.{sm,out,exit}`, `tests/stdlib/strconv_overflow.{sm,out,exit}`, `tests/stdlib/fmt_min.{sm,out,exit}`.

## SHA-256

```
3f3bf1becf3245746b680b9e54b204f15ab42ab7cf90ce8b1a96ca0ea63881aa  lib/math.smlib
e3cf03efa53b277a7db656c573c1f1e3a2752745c3df861f87f577f01b4a04b2  lib/strconv.smlib
d5fcfc368bbd91e8274522787c8002166dd8f4060ade99cdb522c06597c29041  lib/fmt.smlib
57c61485c41107c6a8379648c5d10e0013b77ddd55f24f49a95baa211c962465  tools/proof_props.py
2d8861f9375b538bca43c2c326ae257c36367c21a69198315577007d8815d7bd  docs/PROPERTY-NET.md
94bbbe8365e1aa71049bf31b91a4a73ae636001c42dcd02ba9e682828dcadf5b  docs/sutram-stdlib.html
9318174eb7bf3480addf755b291e623a1a274a6d3b51a00c9d03e35bdccd1d4c  tests/stdlib/breadth26.sm
9a8c3811154ababade3549f01d6a4f4f0d10c7df94bc80430b631a29a40a2c51  tests/stdlib/breadth26.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/breadth26.exit (content: "0")
c5fc19bbb2306f819e8c4585c1e00bde87858be1e4f998ed08155d113fde88b6  tests/stdlib/strconv_overflow.sm
2fee335634afc05b0ee0583f2f835607fa279af1f34fee1197e8397fcfdcb1d9  tests/stdlib/strconv_overflow.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/strconv_overflow.exit (content: "0")
9ed1f3d2e1dbff48aab93b4463152695a2ee733d5773839c38635c5df2d56503  tests/stdlib/fmt_min.sm
9d4a0d0b2b1372b2ba0ea4846aa22cf9dc284df9936ceea0be702319b27c2ff3  tests/stdlib/fmt_min.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/fmt_min.exit (content: "0")
c3d50933633183f4e77a039f29810dfa1329e148e8ef26a3c3bd0a9653401b10  Muse-to-Sarvam/2026-10-16-round26-interaction-breadth-min.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-16-round26-interaction-breadth-min.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 180/180) and `python3 tools/proof_props.py` (expect 72/72).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=187, NO-EXPECTATION=4`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
5. Open items carried forward: (a) raise the compiler's `IMPORT_BUF_CAP` before growing `map`/`set`/`list`/`strb` further — it now blocks five genuinely-wanted functions (WS4 table); (b) the re-declaration compiler bug above — silent wrong values; (c) the checked/sat pre-check rewrite for trap-on mode; (d) `kosh_*` candidate compiler-side builtins (R24 WS2 naming); (e) `literal + offset` not advancing the pointer (R23 WS4 finding).
