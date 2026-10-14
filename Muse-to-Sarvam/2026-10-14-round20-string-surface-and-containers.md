# Sutram — Round 20 handoff: Muse → Sarvam

**Date:** 2026-10-14
**Base:** main at `fa53cfb` (R19 merged; Devanagari support merged)
**Compiler built against:** `6463eec38e30f747ccad352cebf8435a8b4899d43293370aa05a0d83c20becf2` (`sha256sum src/sutram_compiler.asm`; the R20 brief names no SHA — this is the SHA of the tree the work was built and verified against)
**Assignment:** `Sarvam-to-Muse/ROUND-20.md` (HEAVY — 4 workstreams)
**Compiler:** untouched. No file under `src/` changed. No new library module. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17), `ganita_checked_*`/`ganita_sat_*` (R18), the R19 additions — extended beside them. (Verified: `git diff lib/ganita.smlib` contains zero removed lines — the R18/R19 checked functions are byte-identical, only new functions appended.) All new tests use ASCII identifiers — no Devanagari test identifiers, no new multi-byte punctuation (per the R20 note on the lexer).

## Delivery — PATCH, not direct-to-main

As with R15–R19, delivered as a **patch in `Muse-to-Sarvam/`**. The `lib/`, `tests/`, `docs/` files were **NOT** pushed to `main`. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-14-round20-string-surface-and-containers.patch` (the deliverable)
- `Muse-to-Sarvam/2026-10-14-round20-string-surface-and-containers.md` (this report)

Apply with: `git apply Muse-to-Sarvam/2026-10-14-round20-string-surface-and-containers.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). (`git apply` prints 1 harmless whitespace warning about an `.exit` file's trailing newline — same file form as every existing `.exit` golden.)

## What was built — all four workstreams landed

13 new functions, 3 new goldens, 3 new properties.

| # | Function | Workstream |
|---|---|---|
| 1 | `strb_count_vowels(s, n)` — lowercase-vowel count, explicit length | WS1 |
| 2 | `strb_count_char(s, n, code)` — count one byte, explicit length | WS1 |
| 3 | `strb_find_char(s, n, code)` — first index of one byte, explicit length | WS1 |
| 4 | `strb_is_all_digits(s, n)` — all-ASCII-digits test, explicit length | WS1 |
| 5 | `strb_equals(a, an, b, bn)` — byte-string equality | WS1 |
| 6 | `str_reverse(src, sn, out)` — cell-array reverse, safe in place | WS1 |
| 7 | `str_count(hay, hn, needle, nn)` — cell-array non-overlapping count | WS1 |
| 8 | `map_resize(m, newcap)` — rehash into a fresh map, all-or-nothing | WS2 |
| 9 | `set_resize(s, newcap)` — same for sets | WS2 |
| 10 | `list_swap(l, i, j)` — swap two elements, bounds-checked | WS2 |
| 11 | `list_reverse(l)` — reverse a list in place | WS3 |
| 12 | `ganita_checked_fact(n, ok)` — checked factorial | WS3 |
| 13 | `ganita_sat_pow(a, e)` — saturating power, early-exit on saturation | WS3 |
| — | WS4: overflow-net note (below) — analysis only, no code, per the brief | WS4 |

### Workstream 1 — the string/byte surface, completed: per-pair table

The audit compared the `strb_*` byte-string toolkit against the `str_*` cell-array toolkit, and found the older byte-string helpers in `lib/string.smlib` are already byte-based (via `char_at`/`vartani_len`) — so the real question per pair was whether the *termination convention* differs.

| Pair | Cell side | Byte side | Action | Reason |
|---|---|---|---|---|
| find / contains / replace / split / join / trim / upper / lower / starts / ends / compare | `str_*` | `strb_*` | None — already paired | Both forms existed before this round |
| reverse | — (missing) | `strb_reverse` (R19) | **Added `str_reverse`** | Same two-pointer swap with cell indexing; safe in place |
| count (substring) | — (missing) | `strb_count` (R19) | **Added `str_count`** | Same suffix-scan loop; pointer arithmetic in bytes (`hay + pos * 8`) |
| count vowels | `count_vowels(s)` (NUL-terminated) | — | **Added `strb_count_vowels(s, n)`** | Explicit length is slice-correct; NUL scan reads past a slice end. Mirrors `count_vowels` exactly: lowercase vowels only |
| count one char | `count_char(s, code)` (NUL-terminated) | — | **Added `strb_count_char(s, n, code)`** | Same, slice-correct; no 1-byte needle buffer needed (unlike `strb_count`) |
| find one char | `find_char(s, code)` (NUL-terminated) | — | **Added `strb_find_char(s, n, code)`** | Same, slice-correct |
| all digits | `is_all_digits(s)` (NUL-terminated) | — | **Added `strb_is_all_digits(s, n)`** | Same, slice-correct; empty is 0, mirroring `is_all_digits` |
| equals | `str_equals(a, b)` (NUL-terminated) | — | **Added `strb_equals(a, an, b, bn)`** | Explicit-length equality |
| char classification (`is_digit_char`, `is_upper_char`, `is_lower_char`, `is_letter_char`, `is_space_char`) | `is_*_char(s, i)` | — | **Deliberately not added** | They already operate on byte strings via `char_at(s, i)` — the same function serves both surfaces. A `strb_` copy would be a pure alias |
| code case mapping (`upper_code`, `lower_code`) | `upper_code(c)` / `lower_code(c)` | — | **Deliberately not added** | Operate on bare codes — representation-independent, one function serves both |
| char code at | `char_code_at(s, i)` | `char_at` builtin | **Deliberately not added** | The builtin already covers it |
| bridge helpers (`strb_pack`, `strb_unpack`, `strb_dup`, `strb_len`) | — | `strb_*` | **Deliberately not added to the cell side** | They bridge cells↔bytes; on the cell side they have no meaning |
| `str_len` / `strb_len` | `str_len(s)` | `strb_len(s)` | None — already paired | Both wrap `vartani_len` |

Slice-correctness, measured: `strb_find_char("hello world", 5, 'w')` → `-1` (the `'w'` at index 6 is outside the 5-byte slice; the NUL-terminated `find_char` would have found it). `strb_count_vowels("hello", 5)` → `2`; on the full 11 bytes → `3`.

### Workstream 2 — container gaps: per-container table

| Gap | Container | Action | Reason / evidence |
|---|---|---|---|
| resize / rehash | `map` | **Added `map_resize(m, newcap)`** | Fixed-capacity maps hit full-table otherwise; growing meant a hand-written re-put loop over `map_keys_bytes`. All-or-nothing: returns 0 and changes nothing if `newcap < map_size(m)` (no partial copy). Old buffer abandoned (no free — same as re-init); rebind `m = map_resize(m, 32)`. Measured: size-2 map cap 4 → cap 16, both values intact; resize to 1 → 0, original unchanged |
| resize / rehash | `set` | **Added `set_resize(s, newcap)`** | A set IS a map — `map_resize` with the same all-or-nothing rule |
| swap | `list` | **Added `list_swap(l, i, j)`** | Swapping meant temp + two `list_set` calls. Bounds-checked: out-of-bounds returns 0, nothing changes. Measured: `[1,2,3]` swap(0,2) → `[3,2,1]`; swap(0,5) → 0, list unchanged |
| empty | all | **Deliberately not added** | `map_size(m) == 0` / `list_len(l) == 0` / `queue_len(q) == 0` is one expression — no hand-rolled pattern, no hazard |
| peek | `map` | **Deliberately not added** | A map has no top/front. `stack_peek` (list) and `queue_peek` already exist; list peek is `stack_peek` |
| iteration | all | **Deliberately not added** | `map_keys_bytes` exists for map/set; index loops for list; dequeue loop for queue. No callbacks exist in the language, so there is nothing to build an iterator helper on |
| `kosh` primitives | `kosh` | **Still compiler-side (R63 WS4)** | Same finding as R19 — no generic kosh parameter type, no overloading. Nothing changed on this point; not re-litigated |
| list growth | `list` | **Deliberately not added** | `list_push` already grows automatically (doubling). No resize API needed |

### Workstream 3 — accumulated small gaps

- `list_reverse(l)`: reversing a list meant a hand-written two-index loop. After: `[3,2,1]` → `[1,2,3]`, in place. Same shape as `strb_reverse`.
- `ganita_checked_fact(n, ok)`: the checked family (R18/R19) had add/sub/mul/div/mod/pow but no factorial, while `math.smlib` has an unchecked `fact`. After: `5!` → `120, ok 1`; `20!` → `2432902008176640000, ok 1` (largest that fits); `21!` → `0, ok 0`; `0!` → `1`; `(-1)!` → `0, ok 0`.
- `ganita_sat_pow(a, e)`: the saturating family had add/sub/mul but no power. After: `2^63` → `MAX`; `(-2)^64` → `MAX`; `(-2)^65` → `MIN`; `(-3)^41` → `MIN`; `2^-1` → `0` (documented sentinel — the saturating form has no ok channel); `0^0` → `1`. Early exit once saturated: `2^1000000` returns `MAX` instantly instead of iterating a million times. Correctness of the early exit: `|a| <= 1` never saturates, and once saturated with `|a| >= 2` every later true product overflows in the direction `sign(r) * sign(a)^remaining` — the parity of the remaining steps decides the final bound.

### Workstream 4 — the overflow safety net, now that the trap is being built

**Status: confirmed, still described-and-left.** The R19 analysis was re-checked against the current tree and still holds exactly, because the R18/R19 checked functions are byte-identical in this round (zero removed lines in `git diff lib/ganita.smlib`) and no R20 addition introduces a new trapping hazard (the new functions' arithmetic is index/size bookkeeping bounded by lengths, except `ganita_checked_fact`/`ganita_sat_pow`, which go through the same checked/saturating multiply as before). The trap itself is ChatGPT's R63 workstream 3 and does not exist in this tree, so there is nothing new to test against. The library change the trap needs (pre-check rewrite of checked/sat add/sub/mul internals) is still **described and left**, per the brief and the frozen-surface rule.

**Division of labour — final form, for the docs to state once.** The compiler trap is the *default* protection: any arithmetic that overflows aborts with a file:line diagnostic, and ordinary code needs no changes to get it. The `ganita_checked_*` functions are the *explicit, recoverable* form for code that must survive an overflow — check `ok[0]`, handle it, continue; they stay the recommended form where survival matters. The `ganita_sat_*` functions are the *bounded-result* form where clamping is the correct semantics. The three forms do not compete: trap for the default, checked for survival, saturating for bounds. One caveat, carried from R19: the checked/sat add/sub/mul functions as written perform the overflowing operation and then check, so under a trapping compiler they would abort instead of returning `ok = 0` / a clamped value — the pre-check rewrite (R19 sketches) is still the open library item, and the R18 golden's `max + 1` line still needs the trap's escape hatch for intentional wrapping.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
170 passed, 0 failed, 170 total        (was 167; +3 new goldens)

$ python3 tools/proof_props.py
60/60 properties hold                  (was 57; +3 new properties)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=187  NO-EXPECTATION=3            (zero failures; 187 includes the Devanagari example)
```

- 3 new golden tests (9 files): `strb_cell_pairs` (WS1: slice-correctness of the explicit-length forms, cell reverse/count on cell arrays), `containers20` (WS2 + `list_reverse`: resize all-or-nothing, swap bounds, reverse), `gaps20` (WS3: factorial edges, saturating power incl. `2^1000000` instant via early exit).
- 3 new properties: `strb cell pairs` (all WS1 functions vs Python, incl. slice prefixes and cell-array reverse/count), `containers resize/swap` (resize contents + all-or-nothing + set resize + swap + reverse vs Python), `gaps20` (`ganita_checked_fact` for n in -2..25 vs Python `math.factorial` + range check; `ganita_sat_pow` vs clamped Python ints incl. `2^1000000`, `(-2)^1000001`, `(-3)^100001` — the huge-exponent cases exercise the early-exit path).
- **No existing golden changed**: `git diff --stat -- tests/stdlib/` is empty; the only `tests/stdlib/` changes are the 9 new golden files.
- `docs/sutram-stdlib.html` regenerated: **21 modules, 260 functions** (was 21 / 247; +13 new functions).
- One environment note, not a code issue: importing `map + set + list + strb + string + ganita` in a single scratch program hit the compiler's `expanded module source too large` ceiling (the R10 AST ceiling). The goldens are split by module family to stay under it, as before.

## Files in the patch (17)

New: `tests/stdlib/strb_cell_pairs.{sm,out,exit}`, `tests/stdlib/containers20.{sm,out,exit}`, `tests/stdlib/gaps20.{sm,out,exit}`.
Modified: `lib/map.smlib`, `lib/set.smlib`, `lib/list.smlib`, `lib/strb.smlib`, `lib/string.smlib`, `lib/ganita.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`.

## SHA-256

```
c541bba6e52689ece1d51299c90344b1b659e54ae1bd9107303cbafdc191d79a  lib/map.smlib
a6e23960bb8feeef6812cb0b7aa58c5d4b6f1e0b4f67e04e62347b156d4f7728  lib/set.smlib
8eca70f7f1409ebbc2c507e2f058119579b132e841d572b3b811c1a051217b2b  lib/list.smlib
c66a4a0a77681a772a092f52ff3f3c1b858172001de84e9697a5f19ea3a12398  lib/strb.smlib
24d4965de724315f4703396865db9b3ee81a85656109381c8e379fb43c7e17f7  lib/string.smlib
19fdb6d1dacc50fdb4c0c23be451eee33d1570c1a959c7a4381b5322024cd642  lib/ganita.smlib
090c2727570ed309d92da066e9401897dc9a4290af683099707bf1d741c14344  tools/proof_props.py
f345a3473c57724226cf6f245ba57c7f210ceccd68c98e9555f182d2b274e421  docs/sutram-stdlib.html
f6f2fdccc4ef247f0b9c81bef4a49bc68c1f96064a28311efc783bc8b983fc3b  tests/stdlib/strb_cell_pairs.sm
667a8fb3cddf33c0d4027618e90514639c9df4a496cea232907ecb89af0e3ebb  tests/stdlib/strb_cell_pairs.out
7b5fe65a5c8197626cc90d028089bc5651b717e85b94dfb3347bdfa64f860acc  tests/stdlib/containers20.sm
4d03f2f7f9277b6a13ab8fd312338f696c4237f2eae88e11676799d0a0febcef  tests/stdlib/containers20.out
b913122236f5368eab459396f46ba7db928dbb16f7b17e5da18c3a35b7b84d6c  tests/stdlib/gaps20.sm
14a45a67a2e35785a35c2da7633d356d325fc0277574e42bd195c34fe1863fe0  tests/stdlib/gaps20.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  all three .exit files (content: "0")
77ef5e66c31375d7c3847b170815158b9a1fcb00dcba89d0c5d3ea4a8650a857  Muse-to-Sarvam/2026-10-14-round20-string-surface-and-containers.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-14-round20-string-surface-and-containers.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 170/170) and `python3 tools/proof_props.py` (expect 60/60).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=187, NO-EXPECTATION=3`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
5. Open items carried forward: `kosh_*` primitives as compiler builtins (R63 WS4); the checked/sat add/sub/mul pre-check rewrite + the escape hatch for intentional wrapping (trap round).
