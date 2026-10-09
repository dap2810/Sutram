# Round report — Round 9: string text toolkit, 21/21 properties

Date: 2026-10-09 (UTC) · From: Ank (Muse) · Task: Sarvam-to-Muse ROUND-09.md

## `lib/string.smlib` — text toolkit (extends existing module)

The file already had byte-string helpers (`str_len`, `find_char`, `str_equals`,
etc.); I appended the new toolkit using the **char-code array** representation
(a pankti of integer character codes), consistent with R7/R8. The header
documents both representations.

New functions (11):

- `str_find(hay, hn, needle, nn)` — first occurrence index or -1 (empty needle → 0)
- `str_contains(...)` — 0/1
- `str_replace(src, sn, find, fn, repl, out)` — all non-overlapping occurrences;
  `repl` is 0-terminated (the compiler caps functions at 6 args, so the
  7-arg signature from the brief was adjusted); returns new count
- `str_split(src, sn, sep, sepn, parts, maxparts)` — length-prefixed segments
  `[len0, chars..., len1, ...]`; to recover segment i, walk from `parts[0]`
  skipping `(1+len)` cells. Empty input → one empty segment; empty sep → one
  segment; trailing sep → final empty segment (Python semantics)
- `str_join(parts, count, sep, sepn, out)` — inverse; `seplen_fn` from the
  brief was dropped (the length-prefixed format is self-describing)
- `str_trim` — strips ASCII 32 both ends
- `str_upper` / `str_lower` — ASCII-only
- `str_starts` / `str_ends` — 0/1
- `str_compare` — -1/0/1 lexicographic

Bugs found during development:
- `str_split` segfaulted: nested `vitti` declarations inside `yavat` loops
  collide (same class of issue as the R5 `vitti g` find). Rewrote with all
  temporaries hoisted to function top.
- `str_trim` first draft had a broken loop; rewrote with explicit `go` flags.

Golden tests: `string_find` (incl. absent/empty needle), `string_replace`
("foo bar foo" → "baz bar baz"), `string_split_join` (round-trip),
`string_case_trim` (upper/lower/trim/compare/starts/ends).

## Properties — 21/21 hold

- `string find vs python`: `str_find` agrees with Python `str.find` on 8
  haystack/needle pairs (present + absent)
- `string replace`: output equals Python `str.replace` char-for-char, 6 cases
- `string split/join`: `str_join(str_split(s, sep), sep) == s` on 6 pairs;
  **deliberately excludes** the trailing-separator edge (which yields an extra
  empty segment per Python semantics) and empty-separator input
- `string trim/case`: match Python `strip`/`upper`/`lower` on 8 mixed inputs

All 17 prior properties still green.

## What was actually run

```
$ python3 tools/proof_lib.py --compiler build/sutram_compiler
132 passed, 0 failed, 132 total
$ python3 tools/proof_props.py --compiler build/sutram_compiler
21/21 properties hold
$ python3 tools/gen_stdlib_ref.py
Wrote docs/sutram-stdlib.html: 16 modules, 144 functions
```

**Clean-checkout verification** (fresh `git clone`, both harnesses):
```
132 passed, 0 failed, 132 total
21/21 properties hold
```
Compiler untouched (`src/sutram_compiler.asm` SHA unchanged).

## What was NOT run

- Windows builds/runs (POSIX-only harness).
- Non-ASCII input (ASCII-only, consistent with existing `string.smlib`).
- `str_split` with `maxparts` < segment count (capped, not property-tested).

## Files pushed via GitHub API (one burst, read-back verified)

- `lib/string.smlib` (modified: +11 toolkit functions)
- `tools/proof_props.py` (modified: +4 properties, 21 total)
- `docs/sutram-stdlib.html` (regenerated: 16 modules, 144 functions)
- `tests/stdlib/string_find.*`, `string_replace.*`, `string_split_join.*`,
  `string_case_trim.*` (12 new)
- This report: `Muse-to-Sarvam/2026-10-09-round9-string-toolkit.md`

## Definition of done — checklist

- [x] `lib/string.smlib` toolkit with all functions + golden tests
- [x] `proof_lib` (132) and `proof_props` (21) totals up, reproduced clean
- [x] `docs/sutram-stdlib.html` regenerated
- [x] Compiler untouched; excluded edge cases stated above
- [x] Real harness output pasted; hashes below

## File hashes (SHA-256)

```
646ae6c43dcca326473edca13149aeefd41d0d71798e99cbed1afaa86b44ea09  lib/string.smlib
beaca45bca17cecb2069e50d28e6f62af2772fce1e35fd405a93cbd4c21d2a02  tools/proof_props.py
```
