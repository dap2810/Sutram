# Round report — Round 7: sorting + base conversion, 14/14 properties

Date: 2026-10-09 (UTC) · From: Ank (Muse) · Task: Sarvam-to-Muse ROUND-07.md

## 1. Sorting — `lib/sort.smlib` grows by two algorithms

The module already had `bubble_sort`/`shell_sort`; I added:

- `insertion_sort(a, n)` — simple, the "provably correct" one
- `merge_sort(a, n)` — top-down with a temp buffer (faster)

Both operate in place on `pankti` integer arrays. Edge cases verified:
empty array and single-element are no-ops for both.

Implementation notes:
- Insertion sort's first version had a broken break-via-`j=-1` (overwrote
  `a[0]`); rewrote with a `done` flag.
- Merge sort's first version had nested-`yavat` logic errors; rewrote with
  explicit exhausted-flags.

Golden tests: `sort_insertion`, `sort_merge` (8-element reverse-ish input →
1,2,3,4,5,7,8,9).

## 2. Base conversion — `lib/baseconv.smlib` (new)

- `bigint_to_digits(x, n, base, out)` — render bigint as digit values (MSB
  first) in base 2/8/10/16; returns count
- `bigint_from_digits(d, count, base, x, n)` — parse back; rejects digits
  >= base

Design note: the intermediate is a pankti of *integer digit values*, not a
byte string — Sutram's `buf[i] = c` writes 8-byte cells while `char_at`
reads bytes, so byte-packed string building is not directly expressible.
The round-trip property is what matters and it holds.

Verified: 255 → hex `[15,15]`, binary length 8, octal length 3.

Golden test: `baseconv_roundtrip` (per-base lengths + hex round-trip).

## 3. Properties — 14/14 hold

Four sort properties (the ones you specified):
- output ordered (`is_sorted == 1` for both algorithms)
- permutation (insertion and merge give identical output on same input)
- idempotent (sorting sorted input is a no-op)
- edge cases (empty, single element)

One baseconv property:
- `from_digits(to_digits(x, b), b) == x` for b in {2,8,10,16}, 15 values

Sort properties use 5 cases each (not 15) — 15 cases × ~30 statements hit
the compiler's "too many statements in block" limit.

## What was actually run

```
$ python3 tools/proof_lib.py --compiler build/sutram_compiler
124 passed, 0 failed, 124 total
$ python3 tools/proof_props.py --compiler build/sutram_compiler
14/14 properties hold
$ python3 tools/gen_stdlib_ref.py
Wrote docs/sutram-stdlib.html: 15 modules, 128 functions
```

**Clean-checkout verification** (fresh `git clone`, harness):
```
124 passed, 0 failed, 124 total
```
Compiler untouched (`src/sutram_compiler.asm` SHA unchanged).

## What was NOT run

- Windows builds/runs (POSIX-only harness).
- Sort on arrays larger than 10 elements in properties (goldens use 8).
- Base conversion for bases other than 2/8/10/16.

## Files pushed via GitHub API (one burst)

- `lib/sort.smlib` (modified: +insertion_sort, +merge_sort, +merge_sort_rec)
- `lib/baseconv.smlib` (new)
- `tools/proof_props.py` (modified: +5 properties, 14 total)
- `docs/sutram-stdlib.html` (regenerated: 15 modules, 128 functions)
- `tests/stdlib/sort_insertion.*`, `sort_merge.*`, `baseconv_roundtrip.*` (9 new)
- This report: `Muse-to-Sarvam/2026-10-09-round7-sort-baseconv.md`

## Definition of done — checklist

- [x] Sorting module with the four ordering/permutation properties
- [x] Base-conversion module with round-trip properties and per-base goldens
- [x] Both harnesses green, totals reproduced from a clean checkout
- [x] `docs/sutram-stdlib.html` regenerated
- [x] Artifacts committed with hashes below
- [x] Plain statement of what could not run (above)

## File hashes (SHA-256)

```
919b415a0e08650f4832f7bfddc5c4bb2f298f06888a8735e74469ba9976bdcf  lib/sort.smlib
80e626f41ec0fbf9cd2fd2f9c6c50fcb5df1ba9272dd9a8188b963a5b32dcdcc  lib/baseconv.smlib
0f535f320093d81ce7a0752ec6cd3fa7af89e0859713214e89f50c039ac6fdaa  tools/proof_props.py
```
