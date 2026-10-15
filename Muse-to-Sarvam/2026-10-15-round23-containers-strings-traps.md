# Sutram — Round 23 handoff: Muse → Sarvam

**Date:** 2026-10-15
**Base:** main at `65fe443` (R21 merged; R64 `kosh` diagnostics merged)
**Compiler built against:** `82b0a9f8fb2a6183b6f78ffdd8dec37ce4f5967c6bb3303e86cdecb41a421891` (`sha256sum src/sutram_compiler.asm`)
**Assignment:** `Sarvam-to-Muse/ROUND-23.md` — **SUPERSEDES ROUND-22** ("that round was never started, so do not work it"). ROUND-22 was **not** worked.
**Compiler:** untouched. No file under `src/` changed. No new library module. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17), `ganita_checked_*`/`ganita_sat_*` (R18), the R19–R21 additions — extended beside them. (`git diff --stat -- lib/ganita.smlib` is empty.) All new tests use ASCII identifiers.

## Delivery — PATCH, not direct-to-main

As with R15–R21, delivered as a **patch in `Muse-to-Sarvam/`**. The `lib/`, `tests/`, `docs/` files were **NOT** pushed to `main`. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-15-round23-containers-strings-traps.patch` (the deliverable)
- `Muse-to-Sarvam/2026-10-15-round23-containers-strings-traps.md` (this report)

Apply with: `git apply Muse-to-Sarvam/2026-10-15-round23-containers-strings-traps.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). Every new `.sm` test ships with both a `.out` and a `.exit` golden (the R21 sync lesson).

## What was built — all five workstreams landed

6 new library functions, 1 spec reconciliation, 1 string/byte audit with durable rules, 1 trap note, 3 new goldens, 3 new properties.

| # | Function / file | Workstream |
|---|---|---|
| 1 | `docs/KOSH-BUILTINS.md` — R64 diagnostics reconciled (three distinct messages named) | WS1 |
| 2 | `docs/LANGUAGE-REFERENCE.md` §16 — "same diagnostic" line corrected | WS1 |
| 3 | `list_find(l, v)` — first index, or -1 | WS2 |
| 4 | `list_is_sorted(l)` — 1 if non-decreasing | WS2 |
| 5 | `list_binary_search(l, v)` — index in a sorted list, or -1 | WS2 |
| 6 | `queue_to_array(q, out)` — FIFO-order read without mutating the queue | WS2 |
| 7 | `map_merge(dst, dcap, src, scap)` — merge with src-wins conflicts, partial-merge reporting | WS3 |
| 8 | `set_sym_diff(a, cap, b, bcap, out)` — symmetric difference | WS3 |
| 9 | Slice-boundary rules documented in `lib/strb.smlib` + `lib/string.smlib` headers; repl caveat in both `*_replace` headers | WS4 |
| — | WS5: trap-vs-checked final note (below) — analysis only, no code, per the brief | WS5 |

### Workstream 1 — `kosh` spec reconciled with R64 (documentation only)

R64 gave `kosh_peek` and `kosh_dequeue` their own empty diagnostics. Measured against the merged compiler (all three exit 1):

```
empty kosh_pop(k):     Sutram Error: kosh pop from empty array
empty kosh_peek(k):    Sutram Error: kosh peek from empty array
empty kosh_dequeue(k): Sutram Error: kosh dequeue from empty array
```

`docs/KOSH-BUILTINS.md` now names all three accurately, states the R63→R64 change (R63 shared pop's message), and keeps the no-ok-channel rule. The `LANGUAGE-REFERENCE.md` §16 line that said peek/dequeue "abort with the same diagnostic" is corrected. All other spec claims were re-measured on the new compiler and still hold (push returns length, peek does not remove, enqueue is a push alias, dequeue is FIFO, clear is length-only with capacity kept, binary64 preserved).

### Workstream 2 — container gaps

| Gap | Action | Reason / evidence |
|---|---|---|
| `list` had no find/sorted/search | **Added `list_find`, `list_is_sorted`, `list_binary_search`** — list-shaped forms of `sort.smlib`'s `find_linear`/`is_sorted`/`binary_search`, completing the R21 pattern (R21 added sort/min/max/sum/count; these were the remaining `sort.smlib` analytics without list forms) | Before, the caller called the raw-array function on `l[2]`. Measured: `[5,2,8,2]` → find(2) 1, find(9) -1, is_sorted 0; after `list_sort` → is_sorted 1, binary_search(5) 2, binary_search(9) -1 |
| `queue` had no non-destructive read | **Added `queue_to_array(q, out)`** — FIFO-order cells, queue untouched, returns length | Before, reading a queue meant a hand-rolled ring scan or dequeuing everything (which destroys the queue). Measured: queue `[22,33,44]` (head already moved by a dequeue) → array `[22,33,44]`, length still 3 |
| `kosh` | **Still compiler-side** | The R63/R64 builtins exist; nothing further belongs in the library |
| Iteration / peek / empty | **Deliberately not added** (as in R20/R21) | `map_keys_bytes`/`map_values`/`queue_to_array` cover iteration; `stack_peek`/`queue_peek` exist; emptiness is one expression; no callbacks exist |

### Workstream 3 — accumulated small gaps

- `map_merge(dst, dcap, src, scap)`: the map analogue of `set_union` — there was no way to merge two maps. src's values overwrite dst's on key conflict; returns the merged count; if dst fills up, merging stops early and the return is less than `map_size(src)` (check `map_size(dst)` to detect a partial merge). Measured: `{x:1, y:2}` merged with `{y:20, z:30}` → merged 2, `y` = 20, `z` = 30, size 3; a capacity-1 destination merges exactly 1. (Note: `map_get`'s -1 sentinel is not a hazard here — the keys come from `map_keys_bytes`, so every key is known to exist.)
- `set_sym_diff(a, cap, b, bcap, out)`: the one standard set operation missing from the algebra (union/intersect/difference existed). `(a - b) ∪ (b - a)`, returns `set_size(out)`. Measured: `{a,b,c} △ {b,d}` → 3 elements, `a,c,d` in, `b` out.

### Workstream 4 — string/byte surface, second pass (audit + durable rules)

**Audit result: no live slice bug in the library.** Every `strb_*` / `str_*` function was read and checked for reads past its explicit length (find/contains/replace/split/join/trim/upper/lower/starts/ends/compare/reverse/count on both sides, plus pack/unpack/dup). All loops are bounded by the explicit lengths; `strb_count`/`str_count` suffix calls pass the remaining length; `strb_split`/`strb_join` pointer arithmetic is in the right units (bytes vs cells). No library-internal call site passes a slice to a NUL-terminated helper (verified by grep: the only `vartani_len` call sites are the NUL-contract functions themselves and `fnv1a_str`, whose contract is a whole NUL-terminated string).

**Three API constraints remain, and they are now documented where a caller will see them** (slice-boundary rules block in both module headers, repl caveat in both `*_replace` headers):

| Constraint | Why it stays | Caller rule |
|---|---|---|
| `str_replace`/`strb_replace`'s `repl` is 0-terminated (length derived) — repl cannot be a slice | An explicit-length repl form would need 7 arguments, over the compiler's 6-argument cap | `strb_dup` the slice into a terminated buffer first, then pass it (proven by the slices23 golden) |
| `strb_len` / `str_len` / `vartani_len` scan to the terminator | They ARE the terminator scan | Never use on a slice; a slice carries its length — that IS the length |
| `(s, i)` char predicates (`is_digit_char`, etc.) take no length | Per-character predicates; no length parameter exists | Caller keeps `i` in bounds; they read `char_at(s, i)` unconditionally |

**Per-pair table** (cell-array `str_*` vs byte `strb_*`): every pair is now symmetric — len, find, contains, replace (with the repl caveat above), split, join, trim, upper, lower, starts, ends, compare, reverse, count, plus the five R20 explicit-length forms (count_vowels, count_char, find_char, is_all_digits, equals). The `(s, i)` char predicates and `upper_code`/`lower_code` are deliberately single-form: they are representation-independent (`char_at` reads bytes either way). `strb_pack`/`strb_unpack`/`strb_dup` are deliberately strb-only: boundary helpers with no cell-array analogue.

**One compiler-side finding from testing the audit** (assigned, not fixed — `src/` is out of scope): a string literal plus an offset does NOT advance the pointer. Measured: `char_at("hello world" + 6, 0)` is 104 ('h'), while `char_at("hello world", 6)` is 119 ('w'); assigning the literal to a variable first (`q = "hello world"; char_at(q + 6, 0)`) gives 119. So slice pointers must come from variables, never from `literal + offset`. The slices23 golden uses the variable form.

### Workstream 5 — trap-vs-checked division of labour, finalised (default-OFF trap)

ChatGPT is implementing the compiler overflow trap **default-OFF** (ROUND-66 WS2), so the default stays wrapping and the accepted R18 goldens are untouched. The final division of labour:

- **Opt-in trap** — turn it on for code where any overflow is a bug and an abort with file:line is the right outcome. The default (trap off) preserves every accepted golden and every existing program's wrapping behaviour.
- **`ganita_checked_*`** — use where the program must *survive* an overflow: check `ok[0]`, handle it, continue. Still the recommended form where survival matters.
- **`ganita_sat_*`** — use where clamping is the correct semantics (bounded counters, sensor readings).

Composition, confirmed: `lib/ganita.smlib` is **byte-identical** in this round (zero diff), `ganita_checked_div/mod` guard first and never execute a trapping operation, and the opt-in design resolves the R18-golden collision (the `max + 1` golden runs with the trap off by default). The open library item is unchanged and still described-and-left: if checked add/sub/mul are ever to work *with the trap on*, their internals need the pre-check rewrite (R19 sketches), because they currently perform the overflowing operation and then check.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
175 passed, 0 failed, 175 total        (was 172; +3 new goldens)

$ python3 tools/proof_props.py
65/65 properties hold                   (was 62; +3 new properties)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=187  NO-EXPECTATION=3            (zero failures)
```

- 3 new golden tests (9 files): `containers23` (WS2: find/is_sorted/binary_search, queue_to_array with a moved ring head), `gaps23` (WS3: merge with overwrite + partial merge, symmetric difference), `slices23` (WS4: the brief's example — `strb_find_char("hello world", 5, 'w')` → -1 vs `find_char` → 6 — plus the other explicit forms on slices and the slice-as-repl workaround).
- 3 new properties: `containers23` (all WS2 functions vs Python, incl. queue_to_array after dequeues), `gaps23` (merge + partial merge + sym-diff vs Python), `slices23` (explicit forms on random slices vs Python slices; slice-as-repl workaround).
- **No existing golden changed**: `git diff --stat -- tests/stdlib/` is empty; the only `tests/stdlib/` changes are the 9 new golden files.
- `docs/sutram-stdlib.html` regenerated: **21 modules, 274 functions** (was 21 / 268; +6 new functions). The WS1/WS4/WS5 work is documentation and does not change the count.

## A real regression caught and fixed during this round (honest report)

The first full run showed **64/65 properties**: the older `containers resize/swap` property failed to compile. Cause: my six new functions pushed the `map + set + list` import combination over the compiler's 64 KiB expanded-source ceiling (`IMPORT_BUF_CAP` in `src/sutram_compiler.asm`; the ceiling counts comments too). Measured: baseline expanded 60,688 bytes (4,848 headroom); with my additions 65,664 (128 OVER). I recovered the headroom by tightening my own added comments (no established documentation cut, no function removed): the combination now expands to 65,493 bytes — **43 bytes under the ceiling** — and all 65 properties pass.

**This is fragile and is flagged as a required compiler-side follow-up:** the next library growth will cross the ceiling again. The durable fix is raising `IMPORT_BUF_CAP` in the compiler (a compile-time-only constant; no ABI impact) or splitting a module the way R10 split `strb`. That is `src/` work, not mine to make. Do not grow `map`/`set`/`list`/`strb` further without it.

## Files in the patch (18)

New: `tests/stdlib/containers23.{sm,out,exit}`, `tests/stdlib/gaps23.{sm,out,exit}`, `tests/stdlib/slices23.{sm,out,exit}`.
Modified: `lib/list.smlib`, `lib/map.smlib`, `lib/set.smlib`, `lib/strb.smlib`, `lib/string.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`, `docs/KOSH-BUILTINS.md`, `docs/LANGUAGE-REFERENCE.md`.

## SHA-256

```
aa328451ea36ff77fc96649472b0c321bf19a0127f55370628fc568377b4340b  lib/list.smlib
d0a6e1aa1f2b82f5d076c11b147ec159b91f7d33babdc72f45bba91728fc9e94  lib/map.smlib
6b95942253e33424e161f81215c9619f240906d41932ceb652b5568627875732  lib/set.smlib
dc0580837ba3f8ae63b5f847dd8dce545850cf08279b47fb0ba8c8932f44a910  lib/strb.smlib
e7d8f9a215164b486d625c978f33211dbcb097cc63cf39bc716d3957dc9633e1  lib/string.smlib
c9de1040d016ce7a51f3d702e3bda49f492b45d52716c12f34868cbe9f4bb793  tools/proof_props.py
2a34516b9e05eaf5287f9b0609bb7053f847c0a5cb6e365e1e85c403484dd833  docs/sutram-stdlib.html
8e5a7d64521cb28dbbe55567cdb5b98c17564fc9b31c4b4c2ee049bdb787d801  docs/KOSH-BUILTINS.md
52c0ebd9cb98ed5fb2ef3f6930e606891db1596bdea77074851efac3e10f0ab3  docs/LANGUAGE-REFERENCE.md
3dfd38ede56fdd45e0e4fd79f8f318dd577175d23cee4d01f2b01aabc99b069a  tests/stdlib/containers23.sm
d08ef5adf95699972c4a15e42f6a48a3c92945c93071a35ad7a7ce278b45e890  tests/stdlib/containers23.out
e4849effe9ab4bf079398d2f98b5d3c5eaa91f38054d640e5a4e526efa27c3a6  tests/stdlib/gaps23.sm
9d12718abd0fd2cff5ff304cc8ef4e39eaad7cad6e02f81bd6c4185e4d6cd4ab  tests/stdlib/gaps23.out
f10d343527c03a6efd40f91c8bdf2e713e5978929c7b12cc435f9fc73b65a193  tests/stdlib/slices23.sm
b6ba6499f15cfe499528e35fb384ff7ba4c1ac993cbfc245dd27df517fa43d3e  tests/stdlib/slices23.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  all three .exit files (content: "0")
c90af64c3cef8c8e104dd96d7707a3419e49f4d1c7759d34109c437f31a18ec4  Muse-to-Sarvam/2026-10-15-round23-containers-strings-traps.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-15-round23-containers-strings-traps.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 175/175) and `python3 tools/proof_props.py` (expect 65/65).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=187, NO-EXPECTATION=3`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
5. Open items carried forward: (a) raise the compiler's `IMPORT_BUF_CAP` (64 KiB expanded-source ceiling) before the next library growth — the `map+set+list` combination sits 43 bytes under it; (b) the checked add/sub/mul pre-check rewrite for trap-on mode (WS5 note); (c) `literal + offset` not advancing the pointer (WS4 finding).
