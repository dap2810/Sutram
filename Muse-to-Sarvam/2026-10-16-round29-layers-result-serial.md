# Sutram — Round 29 handoff: Muse → Sarvam

**Date:** 2026-10-16
**Base:** `origin/main` at `827d134` (R27 + R28 merged — this patch
applies directly; no dependency on the R27/R28 patches).
**Library:** **23 modules / 297 functions** (was 21 / 281).
**Verified on a pristine checkout after applying the patch:**
`proof_lib` **187/187** · `proof_props` **79/79** ·
`check_layers` **14 core, 9 alloc, 0 std** · suite
**PASS=187, NO-EXPECTATION=4** · compiler untouched.
All 25 patched files compared byte-identical with the working tree.

**Counts:** +16 functions (11 `result` + 5 `serial`), +4 goldens,
+3 properties, +1 diagnostic tool. 0 functions removed or renamed.

## WS1 — the `0 std` result, resolved

Investigated, not relabelled. The answer is that `0 std` is
legitimate: **no lib module calls any OS-service builtin.**
`tools/check_layers.py` now enforces this — it fails if any module
calls `likha` / `likha_fmt` / `likh` (console output), `paadh`
(console input), `band` (file handles), or `netsock` /
`netbind` / `netlisten` / `netaccept` (sockets). Negative test:
a probe `likha` call in `math` fails the checker with
"marked core but calls OS builtin likha (belongs in std)".
`docs/LIBRARY-LAYERS.md` states the resolution explicitly,
including the judgment call that `nirmmita`'s `mmap` underpinning
is the allocator's implementation detail, not an OS service
(an `alloc` module needs *a* heap, not the OS).

## WS2 — the `kosh` growth leak: verified real, not fixable from the library

- **Inspection (read-only):** the `kosh_push` growth path in
  `src/sutram_compiler.asm` (`.ge_call_koshpush`) emits
  `emit_nirmmita_from_rax` (`mmap`) for the new buffer, copies
  the cells, stores the new pointer — and a grep of the whole
  compiler finds **no `munmap` / free emission anywhere**.
- **No free primitive exists in the language.** The `kosh` API
  has no free, and there is no general `munmap` builtin — so the
  library cannot reclaim the buffer even if it wanted to.
- **Measurement:** `tools/test_kosh_growth_leak.py` (new
  diagnostic, not a suite gate — RSS is machine-dependent)
  compiles a program pushing 8,000,000 items and measures the
  child's peak RSS. Slope is **~15.3 bytes/item** — peak heap
  is ~2× the live buffer, i.e. every superseded buffer is
  retained. A fixed compiler would show ~8.
- **Fix (compiler-side, `src/` work):** emit a `munmap` of the
  old buffer in the growth path after the copy. The test is
  expected to FAIL until that lands; it fails on this tree as
  designed. `docs/MEMORY-MODEL.md` §7 records the verification.

## WS3 — from convention to a real result type

`lib/result.smlib` (new, layer: core, 11 functions). A `Result`
is a 2-cell pankti `[ok, value]` supplied by the caller.
`result_ok` / `result_err` construct; `result_is_ok` /
`result_value` inspect; `result_value_or(r, def)` handles both
branches in one expression; `result_from_ok` bridges the `ok`
convention; `result_checked_add/sub/mul/div/mod` produce a
Result from the `ganita` checked forms (overflow, div/mod by
zero, `MIN / -1` → failure `[0, 0]`). The checked producers
pass `out` itself as the `ok` cell, so the module allocates
nothing and stays core. `docs/ERROR-CONVENTION.md` gains the
full table plus an honest "what it still cannot do" section:
no forced check, no propagation operator, no chaining (no
callbacks), no ownership.

## WS4 — the numeric contract, closed out (nearly)

Every gap from R28 is now pinned by `prop_numeric29` + golden
`numeric29`, except `sum_to` (below):

- **ganita classical wrapping:** `kuttaka` (wrapping input found
  by brute-force simulation; wrapping result `2605677504891245458`
  differs from the exact `1483584605987376058` — pinned against
  the wrapping simulation), `samasa` (2^80 → 0),
  `brahmagupta_area` (2^64 sum → 0).
- **math plain wrapping:** `sq(2^32)=0`, `square(3037000500)`,
  `cube(2^21)=MIN`, `double(MAX)=-2`, `triple(MAX)`,
  `inc(MAX)=MIN`, `power(2,63)=MIN`, `power(3,40)`,
  `fact(21)` — all vs Python oracles.
- **num wrapping:** `fib(93)`, `reverse_num(1234567890123456789)`.
- **`fmt_fixed` overflow — was a SEGFAULT, now guarded.**
  `fmt_fixed(1e18, 2)` crashed (exit 139): the dasham→int
  conversion is indefinite past 2^63. Now returns `0`
  (empty) when `scaled >= 2^63`. Largest fixed output is
  `9223372036854774784` (2^63 − 1024), 19 chars, pinned
  including content. Note: written as `9223372036854775807.0`
  (MAX) because the literal `9223372036854775808.0`
  overflows the int64 part of the dasham parser — see the
  scientific-notation finding below.
- **`chakravala` — two defects fixed** (golden `chakravala29`
  + `prop_numeric29`): perfect-square input crashed
  (`chakravala(4)` → SIGFPE, division by `|k| = 0`) — now
  returns the trivial `(1, 0)` with return `1`; large `|k|`
  hung (the `m = 0, 1, 2, ...` scan needs `m ~ 2.9e9` for
  `n = MAX`) — now solves `b*m = -a (mod |k|)` with `kuttaka`
  and compares the two divisible candidates bracketing
  `sqrt(n)`. `chakravala(61)` still gives the minimal
  `(1766319049, 226153980)`. Return contract made explicit:
  `1` = solution in `out`, `0` = failure (`out` untouched)
  — overflow in the update step, no divisible `m`, or the
  1000-iteration guard. `chakravala(MAX)` returns `0`
  (its minimal solution does not fit in int64) instead of
  hanging. Approximation (documented): candidates with
  `m > isqrt(MAX)` are skipped — the below-`sqrt(n)`
  candidate is always exact, so one always exists; for
  `n > MAX/2` this can pick a suboptimal `m`, never a wrong
  one. The rewrite had to be compacted to fit the 64 KiB
  expanded-source cap (below).
- **Open gap (honest hole):** `sum_to` wrapping is defined
  but not pinned — pinning needs `n ≈ 4.3e9` iterations,
  impractical in a test.

**Compiler-side findings** (in `src/`, not fixable here,
recorded in `docs/NUMERIC-CONTRACT.md`):

1. **Scientific-notation literals are broken.**
   `dasham x = 1e18` parses as `1.0` (exponent dropped),
   and `fmt_fixed(1e18, ...)` with the literal inline in a
   call argument segfaults. Full decimal literals work.
2. **~29+ locals across nested blocks miscompile.** A
   function with ~29 locals in nested blocks segfaults at
   runtime even when the branch never executes (bisected:
   28 fine, 29 crashes in `chakravala`). The fix reuses
   dead variables (`g1`, `g2`, `gt`, `r`) in the nested
   branch instead of declaring fresh locals.
3. **64 KiB expanded-source cap.** The compiler caps total
   `ayojan`-expanded source at 65536 bytes
   (`IMPORT_BUF_CAP`). The `gaps19` property program
   (`map` + `set` + `strb` + `ganita`) sits ~130 bytes under
   it after compaction. Raising the cap is compiler-side work.

## WS5 — library breadth: binary serialisation

`lib/serial.smlib` (new, layer: core, 5 functions) — the one
new capability area, chosen as most useful and least covered.
Format: `i64` = 8 bytes little-endian two's-complement;
bytes = 8-byte LE length + payload. Every put/get takes
`(buf, pos, cap)` and returns the new cursor, or `-1` on
overrun / corrupt negative length (destination untouched).
`serial_len_bytes(n)` = `8 + n` for sizing. Deliberately not
here: floats (no bit-cast primitive), varints, schema/
versioning. `put_bytes`/`get_bytes` require non-overlapping
buffers (documented — the header is written before the
payload is copied). Pinned by `prop_serial29` + golden
`serial29` (roundtrips incl. `MIN`/`MAX`, overrun → `-1`,
corrupt length → `-1`).

## Files touched (25) — SHA-256

```
4734a3cf40b051c48158cecb1ace4bc912a70da743babee4418791b78b2821e6  docs/ERROR-CONVENTION.md
b6c69b54aa01ce2ad1581645f60662e52db0d56784bf4162891782757861df51  docs/LIBRARY-BOUNDARY.md
9ee0443a8f7bce14a035182da4610c82d049e2c041aa4fbd1a7fa52ec322d369  docs/LIBRARY-LAYERS.md
4631f82760cc87295d2ea1c25bdbbcb6a11403c0bbdf60e9e0ea8225f02642da  docs/MEMORY-MODEL.md
e89759dfcc4f9c18a38718d01261f7c681e31c818511417732ae1f95fb81e648  docs/NUMERIC-CONTRACT.md
905abfccd09f581f5f8d2260d4bd2b25838905cdf8273884bf8f19bfc7690fd0  docs/sutram-stdlib.html
37cd1f2e08004bc02a0da6f996bb8ecf12955ece2a35f8c0937288f1a4b58a03  lib/fmt.smlib
36a9b843f3cca2f88d84aabb3107e64512ac3732813806997fb7d3d4949d3764  lib/ganita.smlib
c3f8aaf68b7cdc7f5b7c0c816d29962218ece5d6621733cfb6ab2257415efc22  lib/result.smlib
911cb86598158d6a9c28393c0afc3d11d093667c4f1d257f45db3e16ce41aed7  lib/serial.smlib
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/chakravala29.exit
f818e8cd00822602d2fb8bf49fc8da1c4fa34d5c7af0dfd0af41f415d7b493b3  tests/stdlib/chakravala29.out
c7853587b867c39b554d3e5071437e3f0ec17974c25d6ac313d5bc8a55a0a179  tests/stdlib/chakravala29.sm
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/numeric29.exit
81ab6ecf8afb6711b2b50d9d306ed71b412e25127dc587f8c9710ba54a45dc35  tests/stdlib/numeric29.out
ecb6e92ad6859b42316e899182702cd250a04c6840fbfd8aa166899d8e438096  tests/stdlib/numeric29.sm
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/result29.exit
c2350ace8713a3a7d124cb34fdec1c2d8ece3b4619aab5a115c83eda085a9bf8  tests/stdlib/result29.out
0c68b212d2f8f06bee26e871951c049a9386e6865615065086283c013615a6bd  tests/stdlib/result29.sm
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  tests/stdlib/serial29.exit
66f0feb5e8efabaab12b82b88a8c6051dba9359ef693536ccbd4391664c719a5  tests/stdlib/serial29.out
c9b9b4dd1456494c53b0f7ed1f853e2d3e2f9245d6cc95dc99592c89b67a9fc6  tests/stdlib/serial29.sm
5243596cbb7dcc80da2581ef34ba6aad104c04f810dc6a987eb6bdb777d24661  tools/check_layers.py
7f038a22b64c45225bfdf8db2f0f2a2919871387e4c6b372eb3d934040b591b0  tools/proof_props.py
51ab68ae4431bce6a963c5106ca8cc0d44926dbdb7d091ad85dbc61de268c9c0  tools/test_kosh_growth_leak.py
```

Patch SHA-256:

```
8493f4207908cbb5b641ea140a0884f1c82c5c4bcb07432da2c3f4826df052b8  2026-10-16-round29-layers-result-serial.patch
```

**Apply order:** apply this patch to `origin/main` at `827d134`
(R27 + R28 already merged). No earlier patch needed.

**Not done / open:** `sum_to` wrap unpinned (impractical);
`kosh` leak fix, scientific-notation lexer, local-count
miscompilation, and the 64 KiB cap all need compiler-side
(`src/`) work. The leak diagnostic is expected to FAIL until
the compiler fix lands.
