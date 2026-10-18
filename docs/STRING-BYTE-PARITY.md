# Sutram — `str_*` vs `strb_*`: the complete parity table

**Status:** the full cell-mala vs byte-varna surface as shipped
(WS1, R24). Every `str_*` beside its `strb_*` counterpart, with the
verdict for each row: `added` (this round or an earlier one),
`deliberately not`, or `cannot (compiler-side)`.

## The two representations

| | Cell mala (`str_*`) | Byte varna (`strb_*`) |
|---|---|---|
| Element | one qword cell per char code, `h[i]` (8-byte stride) | one byte per char, `akshar(s, i)` (1-byte stride) |
| Length | explicit `n` (source of truth) | explicit `n` (source of truth) |
| Output | `0` terminator cell at `out[n]` | `0` terminator byte at `out[n]` |

Do NOT mix them: `h[i]` on a byte varna reads 8 bytes at once, and
`akshar` on a cell mala reads one byte of a qword cell.

## The table

| # | Cell-mala form (`lib/varna.smlib`) | Byte form (`lib/khand.smlib`) | Verdict |
|---|---|---|---|
| 1 | `varna_maap(s)` — NUL-terminated | `khand_maap(s)` — NUL-terminated | both exist; both scan to the terminator, neither is usable on a slice |
| 2 | `akshar_sanket(s, i)` — byte read | — | `deliberately not` — `akshar` IS the byte accessor |
| 3 | `asti_ank_akshar(s, i)` | — | `deliberately not` — representation-independent (`akshar` reads bytes either way) |
| 4 | `asti_unnat_akshar(s, i)` | — | `deliberately not` — same |
| 5 | `asti_avanat_akshar(s, i)` | — | `deliberately not` — same |
| 6 | `asti_akshar_akshar(s, i)` | — | `deliberately not` — same |
| 7 | `asti_avakash_akshar(s, i)` | — | `deliberately not` — same |
| 8 | `gan_swar(s)` — NUL-terminated | `khand_gan_swar(s, n)` — explicit | `added` (R20) — explicit form is correct on slices |
| 9 | `gan_akshar(s, code)` — NUL-terminated | `khand_gan_akshar(s, n, code)` — explicit | `added` (R20) |
| 10 | `anwesh_akshar(s, code)` — NUL-terminated | `khand_anwesh_akshar(s, n, code)` — explicit | `added` (R20) |
| 11 | `asti_sarv_ank(s)` — NUL-terminated | `khand_asti_sarv_ank(s, n)` — explicit | `added` (R20) |
| 12 | `unnat_sanket(c)` — code → code | — | `deliberately not` — representation-independent |
| 13 | `avanat_sanket(c)` — code → code | — | `deliberately not` — same |
| 14 | `varna_sam(a, b)` — NUL-terminated | `khand_sam(a, an, b, bn)` — explicit | `added` (R20) |
| 15 | `varna_anwesh(hay, hn, needle, nn)` | `khand_anwesh(hay, hn, needle, nn)` | both explicit (R9 / R10) |
| 16 | `varna_antah(...)` | `khand_antah(...)` | both explicit (R9 / R10) |
| 17 | `varna_pratisthap(src, sn, find, fn, repl, out)` — `repl` 0-terminated | `khand_pratisthap(src, sn, find, fn, repl, out)` — `repl` 0-terminated | `cannot (compiler-side)` — see repl rule below |
| 18 | `varna_bhed(...)` | `khand_bhed(...)` | both explicit (R9 / R10) |
| 19 | `varna_yuj(...)` | `khand_yuj(...)` | both explicit (R9 / R10) |
| 20 | `varna_chhid(...)` | `khand_chhid(...)` | both explicit (R9 / R10); both strip ASCII space (32) only |
| 21 | `varna_unnat(...)` | `khand_unnat(...)` | both explicit (R9 / R10) |
| 22 | `varna_avanat(...)` | `khand_avanat(...)` | both explicit (R9 / R10) |
| 23 | `varna_aadi(...)` | `khand_aadi(...)` | both explicit (R9 / R10) |
| 24 | `varna_ant(...)` | `khand_ant(...)` | both explicit (R9 / R10) |
| 25 | `varna_tul(...)` | `khand_tul(...)` | both explicit (R9 / R10) |
| 26 | `varna_viparyay(...)` | `khand_viparyay(...)` | both explicit (R19 / R20); both safe in place |
| 27 | `varna_gan(...)` | `khand_gan(...)` | both explicit (R19 / R20); both count non-overlapping occurrences |
| 28 | — | `khand_bandh(cells, n, out)` | `deliberately not` — no cell-mala analogue (identity) |
| 29 | — | `khand_mukt(bytes, n, out)` | `deliberately not` — same |
| 30 | — | `khand_pratilip(src, n, out)` | `deliberately not` — same; also the slice-as-repl workaround (below) |

## The three rules that stay open

**The repl rule — `cannot (compiler-side)`.** Both `*_replace` forms
take `repl` as a 0-terminated varna (its length is derived), so `repl`
cannot be a slice. An explicit-length `repl` form would need 7
arguments, over the compiler's 6-argument cap. Workaround: `khand_pratilip`
the slice into a terminated buffer first, then pass it (proven by the
R23 `slices23` golden). Note the same rule means a `repl` containing an
interior NUL byte is truncated at that byte.

**The length-function rule.** `varna_maap` / `khand_maap` / `vartani_len`
scan to the terminator: they cannot be used on slices at all. A slice
carries its length — that IS the length.

**The `(s, i)` predicate rule.** The char predicates take no length:
the caller must keep `i` in bounds; they read `akshar(s, i)`
unconditionally.

## Slice-boundary rules (summary)

A slice is a (pointer, length) pair into a larger buffer, with NO
terminator at the slice end. Every `strb_*` function takes an explicit
length and stops at it: `khand_anwesh_akshar("hello world", 5, 'w')` is -1.
The NUL-terminated forms (`anwesh_akshar`, `gan_akshar`, `gan_swar`,
`asti_sarv_ank`, `varna_sam`) scan to the terminator, so they are
WRONG on slices — never pass a slice to them. The same rules are stated
in the `lib/khand.smlib` and `lib/varna.smlib` headers (R23 WS4 audit).
One compiler-side finding from that audit: a varna literal plus an
offset does NOT advance the pointer (`akshar("hello world" + 6, 0)`
is `'h'`), so slice pointers must come from variables.
