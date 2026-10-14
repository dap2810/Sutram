# Sutram — Round 21 handoff: Muse → Sarvam

**Date:** 2026-10-14
**Base:** main at `c932fc6` (R20 merged; R63 `kosh` builtins merged)
**Compiler built against:** `f52a9ad78785faa8997356200f61e06e290725079229c897a6dc55bc5ccd621b` (`sha256sum src/sutram_compiler.asm`; the R21 brief names no SHA — this is the SHA of the tree the work was built and verified against)
**Assignment:** `Sarvam-to-Muse/ROUND-21.md` (HEAVY — 4 workstreams)
**Compiler:** untouched. No file under `src/` changed. No new library module. Frozen surfaces untouched: `map_keys`/`map_keys_bytes` (R17), `ganita_checked_*`/`ganita_sat_*` (R18), the R19/R20 additions — extended beside them. (Verified: `git diff lib/ganita.smlib` contains zero removed lines — the R18–R20 checked functions are byte-identical.) All new tests use ASCII identifiers.

## Delivery — PATCH, not direct-to-main

As with R15–R20, delivered as a **patch in `Muse-to-Sarvam/`**. The `lib/`, `tests/`, `docs/` files were **NOT** pushed to `main`. Only two files were uploaded via the API:

- `Muse-to-Sarvam/2026-10-14-round21-kosh-spec-and-containers.patch` (the deliverable)
- `Muse-to-Sarvam/2026-10-14-round21-kosh-spec-and-containers.md` (this report)

Apply with: `git apply Muse-to-Sarvam/2026-10-14-round21-kosh-spec-and-containers.patch` from a clean `main` checkout. The patch was verified to apply cleanly to pristine `origin/main` (`git apply --check`), and the patched tree reproduces every number below, with patched files byte-identical to the working tree (`cmp` clean). (`git apply` prints 1 harmless whitespace warning about an `.exit` file's trailing newline — same file form as every existing `.exit` golden.)

## What was built — all four workstreams landed

8 new library functions, 1 new spec document, 1 reference update, 2 new goldens, 2 new properties.

| # | Function / file | Workstream |
|---|---|---|
| 1 | `docs/KOSH-BUILTINS.md` — canonical spec for the 5 new R63 `kosh` builtins, verified by execution | WS1 |
| 2 | `docs/LANGUAGE-REFERENCE.md` §16 — table extended with the 5 builtins, stale "no `kosh dasham` yet" line fixed, pointer to the spec | WS1 |
| 3 | `list_sort(l)` — in-place merge sort | WS2 |
| 4 | `list_min(l, ok)` / `list_max(l, ok)` — min/max with empty → `ok[0] = 0` | WS2 |
| 5 | `list_sum(l)` — element sum (0 for empty) | WS2 |
| 6 | `list_count(l, v)` — occurrences of a value | WS2 |
| 7 | `queue_contains(q, v)` — non-mutating ring scan | WS2 |
| 8 | `map_values(m, out)` — live values in slot order | WS2 |
| 9 | `ganita_sat_fact(n)` — saturating factorial | WS3 |
| — | WS4: trap-vs-checked final note (below) — analysis only, no code, per the brief | WS4 |

### Workstream 1 — the `kosh` builtin spec, written down (documentation only)

`docs/KOSH-BUILTINS.md` is the canonical spec. It is **not** a restatement of the R63 handoff: the R63 doc (`docs/R63-KOSH-BUILTINS.md`) is a source-level implementation handoff whose own text says it was "not yet compiled or executed". Every claim in the new spec was measured from real compiled programs against the merged compiler, plus the R63 acceptance gates (`tools/r63_kosh_acceptance.py`: 9/9 — 5 exact-output programs, 2 compile errors, 2 runtime traps).

Measured behaviour stated in the spec:

```
kosh_empty(fresh)              -> 1
kosh_push(v, 10)               -> 1 (new length)
kosh_peek(v) after [10,20,30]  -> 30, length still 3 (nothing removed)
kosh_enqueue(v, 40)            -> 4 (new length; alias of push)
kosh_dequeue(v)                -> 10, then 20, 30, 40 (FIFO order)
after draining: len 0, cap 4 (dequeue does not shrink), empty 1
kosh_clear(empty)              -> 0; len 0, cap 4, empty 1
5 pushes -> len 5, cap 8 (grew 4 -> 8); kosh_clear -> 0, len 0, cap 8 (kept)
dasham: peek -> 2.500000, dequeue -> 1.500000 (binary64 preserved)
empty peek / empty dequeue     -> "Sutram Error: kosh pop from empty array", exit 1
non-kosh argument              -> "Sutram Error: kosh builtin requires a kosh variable", exit 1
wrong arity                    -> parse error at the call site, exit 1
```

Spec points a reader needs, all verified: `kosh_clear` sets logical length only — it does **not** erase storage cells and does not change capacity (deliberately different from the library's `map_clear`, which zeroes storage; the spec states the difference and why). `kosh_dequeue` is FIFO, O(n) shift, trailing slot not erased. Empty `peek`/`dequeue` abort with the shared diagnostic — note the message says "pop" even for `dequeue`; that is the compiler's shared diagnostic text, stated honestly, not a documentation error. There is **no** `ok[0]` channel on the builtins (unlike library `stack_pop`/`queue_dequeue`); code that must survive must check `kosh_empty` first. The spec closes with a `kosh` vs `list` vs `queue` comparison table (types, operations, complexity, clear/erasure semantics, which to use when).

### Workstream 2 — container gaps

| Gap | Action | Reason / evidence |
|---|---|---|
| `list` had no sort/min/max/sum/count | **Added `list_sort`, `list_min`, `list_max`, `list_sum`, `list_count`** — list-shaped forms of `sort.smlib`'s `merge_sort`/`min_of`/`max_of`/`sum_of`/`count_of` (`list.smlib` now does `ayojan sort`) | Before, the caller wrote the loop by hand or called the raw-array function on `l[2]`. `list_min`/`list_max` add the empty check the raw functions lack: `min_of` on an empty list reads a stale cell (`a[0]` with `n = 0`), so the wrappers return `ok[0] = 0` on empty instead of a stale value. Measured: `[5,2,8,1,2]` → sum 18, count(2) 2, min 1, max 8, sorted `1 2 2 5 8`; empty list → min/max `0, ok 0`, sum 0, count 0 |
| `queue` had no contains | **Added `queue_contains(q, v)`** | Scans the ring without mutating it (no dequeue loop). Before, the caller hand-rolled `(head + k) % cap` arithmetic — the same hazard `list_contains` already removed for lists. Measured: queue `[22]` (after dequeuing 11) → contains(22) 1, contains(11) 0, contains(99) 0, length unchanged |
| `map` had no values iteration | **Added `map_values(m, out)`** | Writes live values in the same slot order as `map_keys`/`map_keys_bytes`, returns the count. Before, collecting values meant a `map_keys_bytes` pass plus a `map_get` per key. Measured: `{a:10, b:20, c:-5}` → count 3, values sum 25 (sum is order-independent; slot order is hash order) |
| Iteration / peek / empty | **Deliberately not added** (as in R20) | `map_keys_bytes` exists for map/set; index loops for list; dequeue loop for queue; no callbacks exist in the language. `stack_peek`/`queue_peek` exist; a map has no top/front; emptiness is one expression |
| `kosh` | **Still compiler-side** | The R63 builtins now exist; nothing further belongs in the library (same reasoning as R19/R20) |

### Workstream 3 — accumulated small gaps

- `ganita_sat_fact(n)`: the saturating family had add/sub/mul/pow (R18/R20) but no factorial, while R20 added only the checked form. After: `5!` → `120`; `20!` → `2432902008176640000`; `21!` → `MAX`; `100!` → `MAX` (early exit once saturated — factorials only grow, so a saturated result stays saturated); `0!` → `1`; `(-1)!` → `0` (documented sentinel — the saturating form has no ok channel).
- Nothing else was genuinely flagged this round: `strb`/`str` families were completed in R20, `map`/`set` got their resize/clear/defaults in R19/R20, and slice (considered and skipped in R20) remains skipped. One real function beats padding.

### Workstream 4 — trap-vs-checked, finalised (opt-in trap)

ChatGPT is making the trap **opt-in** (R64 WS3), so the default stays wrapping and the accepted R18 goldens are untouched. The final division of labour, for the docs to state once:

- **Opt-in trap** — turn it on for code where any overflow is a bug and an abort with file:line is the right outcome. The default (trap off) preserves every accepted golden and every existing program's wrapping behaviour.
- **`ganita_checked_*`** — use where the program must *survive* an overflow: check `ok[0]`, handle it, continue. Still the recommended form where survival matters.
- **`ganita_sat_*`** — use where clamping is the correct semantics (bounded counters, sensor readings).

Composition, confirmed: the R18/R19 checked surface still composes with a trapping compiler in exactly the sense established in R19/R20 — the checked functions are byte-identical in this round (zero removed lines), `ganita_checked_div/mod` guard first and never execute a trapping operation, and the opt-in design resolves the R18-golden collision (the `max + 1` golden runs with the trap off by default). The open library item is unchanged and still described-and-left: if checked add/sub/mul are ever to work *with the trap on*, their internals need the pre-check rewrite (R19 sketches), because they currently perform the overflowing operation and then check.

## Verification (all from real runs)

```
$ python3 tools/proof_lib.py
172 passed, 0 failed, 172 total        (was 170; +2 new goldens)

$ python3 tools/proof_props.py
62/62 properties hold                  (was 60; +2 new properties)

$ python3 tests/run_tests.py           (patched clean-checkout copy, compiler at ./sutram_compiler)
PASS=187  NO-EXPECTATION=3            (zero failures)
```

- 2 new golden tests (6 files): `containers21` (WS2: sort/min/max/sum/count, queue_contains with a moved ring head, map_values), `gaps21` (WS3: saturating factorial edges incl. `100!` → MAX).
- 2 new properties: `containers21` (all WS2 functions vs Python, incl. empty-list min/max ok, queue_contains after a dequeue, map_values count + order-independent sum), `gaps21` (`ganita_sat_fact` vs clamped Python factorials for n in -2..25 plus 100 and 100000 — the huge-n cases exercise the early-exit path).
- **No existing golden changed**: `git diff --stat -- tests/stdlib/` is empty; the only `tests/stdlib/` changes are the 6 new golden files.
- `docs/sutram-stdlib.html` regenerated: **21 modules, 268 functions** (was 21 / 260; +8 new functions). `docs/KOSH-BUILTINS.md` and the `LANGUAGE-REFERENCE.md` §16 update are documentation, not library functions, and do not change the count.

## Files in the patch (14)

New: `docs/KOSH-BUILTINS.md`, `tests/stdlib/containers21.{sm,out,exit}`, `tests/stdlib/gaps21.{sm,out,exit}`.
Modified: `lib/map.smlib`, `lib/list.smlib`, `lib/ganita.smlib`, `tools/proof_props.py`, `docs/sutram-stdlib.html`, `docs/LANGUAGE-REFERENCE.md`.

## SHA-256

```
9e8cd4c76d7b193b7c83169c40ddd03c83d46433ed772860204c059f2a949d29  lib/map.smlib
64104411cc3ef5aa4b95b58da531bf9682b639565edb5dec0ad65eaf27f2e0db  lib/list.smlib
301e0584c42fc3f40985b4dc72e2a1464520ab6e0f3068c4b428b2cc51725f02  lib/ganita.smlib
9dce03213f48eae9ba633e968729f88196886cb228912dbab72b7995bd8c7503  tools/proof_props.py
00cf92fa392d4391430260adc95f74628027b59fdf558af38aba86915852cf1a  docs/sutram-stdlib.html
6c25e2a90a49297f23eb2b902bb07ddcc754f7498eccb57ef06e897dcb39ef6b  docs/KOSH-BUILTINS.md
3ff205d86b70b0a782f4b49740cfd564a5150a22c269d7f2106816ba592cd5d9  docs/LANGUAGE-REFERENCE.md
40ef72ee81bde9bb349903740bce56c090c5f66ce3778254357006c7982febbc  tests/stdlib/containers21.sm
86998cb19d1eff97b059c8c5f6b9fe041661a1e2acaded71bc22dd36d85f3a16  tests/stdlib/containers21.out
2c92a57a4641e500e55c2f30653d6d63b9ea99c2c71e65dc3827ef4c7597b4e4  tests/stdlib/gaps21.sm
5a60aa8150495e7c29e1cf66a92654966a73e4fba714fcaea6e714097ee61a17  tests/stdlib/gaps21.out
9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa  both .exit files (content: "0")
b5cd4177de5bf53005006a4b82155ab112bdfab7a9ef5e6733d1c6bb9f1b6fda  Muse-to-Sarvam/2026-10-14-round21-kosh-spec-and-containers.patch
```

## Instructions for Sarvam

1. From a clean `main` checkout: `git apply Muse-to-Sarvam/2026-10-14-round21-kosh-spec-and-containers.patch`, then verify the hashes above.
2. Run `python3 tools/proof_lib.py` (expect 172/172) and `python3 tools/proof_props.py` (expect 62/62).
3. Run the suite with the compiler at `./sutram_compiler` (expect `PASS=187, NO-EXPECTATION=3`).
4. Apply to `main` at your discretion — nothing in this delivery touches `main` until you apply the patch.
5. Open item carried forward: the checked/sat add/sub/mul pre-check rewrite for trap-on mode (WS4 note).
