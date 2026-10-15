# Sutram — `str_*` vs `strb_*`: the complete parity table

**Status:** the full cell-array vs byte-string surface as shipped
(WS1, R24). Every `str_*` beside its `strb_*` counterpart, with the
verdict for each row: `added` (this round or an earlier one),
`deliberately not`, or `cannot (compiler-side)`.

## The two representations

| | Cell array (`str_*`) | Byte string (`strb_*`) |
|---|---|---|
| Element | one qword cell per char code, `h[i]` (8-byte stride) | one byte per char, `char_at(s, i)` (1-byte stride) |
| Length | explicit `n` (source of truth) | explicit `n` (source of truth) |
| Output | `0` terminator cell at `out[n]` | `0` terminator byte at `out[n]` |

Do NOT mix them: `h[i]` on a byte string reads 8 bytes at once, and
`char_at` on a cell array reads one byte of a qword cell.

## The table

| # | Cell-array form (`lib/string.smlib`) | Byte form (`lib/strb.smlib`) | Verdict |
|---|---|---|---|
| 1 | `str_len(s)` — NUL-terminated | `strb_len(s)` — NUL-terminated | both exist; both scan to the terminator, neither is usable on a slice |
| 2 | `char_code_at(s, i)` — byte read | — | `deliberately not` — `char_at` IS the byte accessor |
| 3 | `is_digit_char(s, i)` | — | `deliberately not` — representation-independent (`char_at` reads bytes either way) |
| 4 | `is_upper_char(s, i)` | — | `deliberately not` — same |
| 5 | `is_lower_char(s, i)` | — | `deliberately not` — same |
| 6 | `is_letter_char(s, i)` | — | `deliberately not` — same |
| 7 | `is_space_char(s, i)` | — | `deliberately not` — same |
| 8 | `count_vowels(s)` — NUL-terminated | `strb_count_vowels(s, n)` — explicit | `added` (R20) — explicit form is correct on slices |
| 9 | `count_char(s, code)` — NUL-terminated | `strb_count_char(s, n, code)` — explicit | `added` (R20) |
| 10 | `find_char(s, code)` — NUL-terminated | `strb_find_char(s, n, code)` — explicit | `added` (R20) |
| 11 | `is_all_digits(s)` — NUL-terminated | `strb_is_all_digits(s, n)` — explicit | `added` (R20) |
| 12 | `upper_code(c)` — code → code | — | `deliberately not` — representation-independent |
| 13 | `lower_code(c)` — code → code | — | `deliberately not` — same |
| 14 | `str_equals(a, b)` — NUL-terminated | `strb_equals(a, an, b, bn)` — explicit | `added` (R20) |
| 15 | `str_find(hay, hn, needle, nn)` | `strb_find(hay, hn, needle, nn)` | both explicit (R9 / R10) |
| 16 | `str_contains(...)` | `strb_contains(...)` | both explicit (R9 / R10) |
| 17 | `str_replace(src, sn, find, fn, repl, out)` — `repl` 0-terminated | `strb_replace(src, sn, find, fn, repl, out)` — `repl` 0-terminated | `cannot (compiler-side)` — see repl rule below |
| 18 | `str_split(...)` | `strb_split(...)` | both explicit (R9 / R10) |
| 19 | `str_join(...)` | `strb_join(...)` | both explicit (R9 / R10) |
| 20 | `str_trim(...)` | `strb_trim(...)` | both explicit (R9 / R10); both strip ASCII space (32) only |
| 21 | `str_upper(...)` | `strb_upper(...)` | both explicit (R9 / R10) |
| 22 | `str_lower(...)` | `strb_lower(...)` | both explicit (R9 / R10) |
| 23 | `str_starts(...)` | `strb_starts(...)` | both explicit (R9 / R10) |
| 24 | `str_ends(...)` | `strb_ends(...)` | both explicit (R9 / R10) |
| 25 | `str_compare(...)` | `strb_compare(...)` | both explicit (R9 / R10) |
| 26 | `str_reverse(...)` | `strb_reverse(...)` | both explicit (R19 / R20); both safe in place |
| 27 | `str_count(...)` | `strb_count(...)` | both explicit (R19 / R20); both count non-overlapping occurrences |
| 28 | — | `strb_pack(cells, n, out)` | `deliberately not` — no cell-array analogue (identity) |
| 29 | — | `strb_unpack(bytes, n, out)` | `deliberately not` — same |
| 30 | — | `strb_dup(src, n, out)` | `deliberately not` — same; also the slice-as-repl workaround (below) |

## The three rules that stay open

**The repl rule — `cannot (compiler-side)`.** Both `*_replace` forms
take `repl` as a 0-terminated string (its length is derived), so `repl`
cannot be a slice. An explicit-length `repl` form would need 7
arguments, over the compiler's 6-argument cap. Workaround: `strb_dup`
the slice into a terminated buffer first, then pass it (proven by the
R23 `slices23` golden). Note the same rule means a `repl` containing an
interior NUL byte is truncated at that byte.

**The length-function rule.** `str_len` / `strb_len` / `vartani_len`
scan to the terminator: they cannot be used on slices at all. A slice
carries its length — that IS the length.

**The `(s, i)` predicate rule.** The char predicates take no length:
the caller must keep `i` in bounds; they read `char_at(s, i)`
unconditionally.

## Slice-boundary rules (summary)

A slice is a (pointer, length) pair into a larger buffer, with NO
terminator at the slice end. Every `strb_*` function takes an explicit
length and stops at it: `strb_find_char("hello world", 5, 'w')` is -1.
The NUL-terminated forms (`find_char`, `count_char`, `count_vowels`,
`is_all_digits`, `str_equals`) scan to the terminator, so they are
WRONG on slices — never pass a slice to them. The same rules are stated
in the `lib/strb.smlib` and `lib/string.smlib` headers (R23 WS4 audit).
One compiler-side finding from that audit: a string literal plus an
offset does NOT advance the pointer (`char_at("hello world" + 6, 0)`
is `'h'`), so slice pointers must come from variables.
