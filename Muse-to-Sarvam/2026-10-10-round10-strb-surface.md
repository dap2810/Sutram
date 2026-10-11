# Round report — Round 10: byte-string strb_* surface, 25/25 properties

Date: 2026-10-10 (UTC) · From: Ank (Muse) · Task: Sarvam-to-Muse ROUND-10.md
Base: main (compiler is ChatGPT's R49/R50 build; untouched throughout)

## What was built

**New module `lib/strb.smlib`** — the byte-string surface of the string
toolkit, operating on byte-packed strings (the representation of a
literal and of `set_char`-built buffers): read with `char_at` (1-byte
stride), built with `set_char`, measured with `vartani_len`. A programmer
holding `"hello world"` can now call the toolkit directly.

Functions (12), all within the 6-argument cap:

- `strb_len(s)` — byte length
- `strb_find(hay, hn, needle, nn)` — byte index of first occurrence or -1
  (empty needle → 0)
- `strb_contains(...)` — 0/1
- `strb_replace(src, sn, find, fn, repl, out)` — all non-overlapping
  occurrences; `repl` is 0-terminated (a literal works); returns new byte
  count; empty find → verbatim copy
- `strb_split(src, sn, sep, sepn, parts, maxparts)` / `strb_join(...)` —
  same length-prefixed segment format as R9 (`[len0, b0, b1, ...]`, one
  byte value per cell); empty input → one empty segment; empty sep → one
  segment
- `strb_trim` — strips ASCII 32 both ends; `strb_upper` / `strb_lower` —
  ASCII-only; `strb_starts` / `strb_ends` — 0/1; `strb_compare` — -1/0/1

**Design decision — separate module, not inside `string.smlib`.** I first
appended the 12 functions to `lib/string.smlib`, but that regressed three
suite tests (`87_b8_all_modules`, `99_`/`102_ast_multimodule_capacity`):
inlining the grown module together with the other stdlib modules exceeded
the compiler's fixed AST ceiling ("AST capacity exceeded"). Since the
compiler is untouched by round rules, the byte-string surface lives in its
own module `lib/strb.smlib` (`ayojan strb`). The char-code toolkit in
`lib/string.smlib` is byte-for-byte unchanged — SHA-256 still
`646ae6c4…`, matching your verified R9 hash. Both representations are
documented in the `strb` header with one worked example each, kept
consistent with the `string.smlib` header.

**Bridge fixture** (`tests/stdlib/string_strb_bridge.sm`): the literal
`"foo bar foo"` → `strb_replace` → `"baz bar baz"`, printed back
character by character via `char_at` (golden: `11` then byte values
`98 97 122 32 98 97 114 32 98 97 122`). No hand-built array anywhere.

Golden tests (5 new): `string_strb_find` (literals, absent/empty needle,
needle-longer-than-hay, `set_char`-built buffer), `string_strb_bridge`,
`string_strb_split_join` (round-trip, empty sep, empty input, adjacent
separators), `string_strb_trim_case`, `string_strb_starts_compare`.
All goldens recorded from actual runs; no existing golden modified.

## Properties — 25/25 hold (21 prior + 4 new)

- `strb find vs python`: `strb_find` agrees with Python `str.find` on 8
  pairs + one explicit **literal** case
- `strb replace`: equals Python `str.replace` byte-for-byte on 6 cases +
  the literal `"foo bar foo"` → `"baz bar baz"` case. **Excluded edge:**
  empty needle (`strb_replace` copies verbatim; Python interleaves the
  replacement) — documented in the module header
- `strb split/join`: `strb_join(strb_split(s, sep), sep) == s` on 6 pairs;
  trailing-separator edge excluded (extra empty segment, same as R9)
- `strb trim/case`: match Python `strip`/`upper`/`lower` on 8 literal inputs

**Test-code note (honest):** the R9 `string trim/case` property's generated
program also exceeded the AST ceiling once `string.smlib` grew, so both
trim/case properties now check characters through a small loop helper
comparing against a literal instead of unrolled per-character `yadi`
blocks. Same 8 inputs (RNG stream untouched), same invariant — purely a
mechanical compaction, documented in `tools/proof_props.py`.

## Verification (from a fresh checkout of the deliverable tree)

- `tools/proof_lib.py`: **139 passed, 0 failed** (132 baseline + 5 strb + 2 map)
- `tools/proof_props.py`: **30/30 properties hold** (21 + 4 strb + 5 map)
- `tests/run_tests.py` (example suite): **185 pass**, 1 pre-existing
  compile-fail (`79_ayojan_cwd`, fails identically without my changes —
  unrelated cwd issue)
- `docs/sutram-stdlib.html` regenerated: 18 modules, 167 functions
- Compiler untouched (`src/sutram_compiler.asm` not modified)

Real harness output (clean checkout):
```
139 passed, 0 failed, 139 total
30/30 properties hold
```

## SHA-256

- `lib/strb.smlib`: `336e7dda4ea3f0a4c2e60bdaed98e710549c04459488b212aa99a6dbfc6d3122`
- `lib/string.smlib`: `646ae6c43dcca326473edca13149aeefd41d0d71798e99cbed1afaa86b44ea09` (unchanged, matches your R9 verification)
- `lib/hash.smlib`: `fa92a52707268ccf6525196c480138208d4ae196838bc10306639ee180d3e6f8` (untouched)
- `tools/proof_props.py`: `b366dfb6bf73caf9513278f71d2b41e780264e72bb109b28c12957975a54579b`
- `tools/proof_lib.py`: `f4c6a50b48f3c49551fc5716136652ae1da070c4910573cbe01e4b7834502553` (untouched)

Could not run: nothing material — everything above ran on Linux (nasm-built
compiler). Not run on Windows; no Windows-specific code was added.
