# R54-00 — Hand-back to Sarvam: Muse's patches applied, and the limit they needed

- **Commit on `main`:** `caed891c965cf825001e274053b931614e835c43` (v257 → v258), then this hand-back's commit. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v258) - sampurna sutra`.**
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs: **226/226**.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 48 PASS / 0 FAIL / 1 NOT-RUN.**
  - The new gate is "R54 migration".
  - The NOT-RUN is Windows execution.
- **The guard, three ways, each on Linux ELF, Linux PE, and the Windows compiler under Wine** (577 programs each time):
  - **The compiler change alone (v257 → v258), on the tree before the patches: 486 byte-identical, 91 refused
    identically, 0 DIFFER.**
  - **The nivartanam patches alone (the ROUND-52 tree → the ROUND-52 + nivartanam tree, both v258): 486
    byte-identical, 91 refused identically, 0 DIFFER.**
  - **The compiler change on the patched tree: 485 byte-identical, 91 refused identically, 1 DIFFER.** The one is
    `tests/stdlib/r11_sets_lists`: v257 refuses it (over the limit) and v258 compiles it. That is the change.
- **Was R52 on main before I started? Two answers, because there are two R52s:**
  - **My ROUND-52 (the compiler: `likha` with up to six values, and the rest): yes,** since `50f2043`.
  - **Muse's `ROUND-52.patch` (the examples' print triples, and comments in lib/): NO.** It was not on main.
    **The nivartanam patches were made on top of it.**

## WS1 — the patches

**Without `ROUND-52.patch` first, 12 of the 24 lib files reject** (`evidence-r54/without-r52-first.txt`):
- part1: ank, chandas, ganit, ganita, khand, mala;
- part2: nighantu, phal, roop, sadhan, shreni, varna.

Those are exactly the 12 lib files `ROUND-52.patch` adds comments to. The examples patch applies either way.

**By your rule I stopped there and asked the owner. The answer was to apply all four, and raise the limit.**

**Applied with `git apply`, in this order, 0 rejected hunks, nothing edited by hand** (`evidence-r54/patches-applied.txt`):

| Patch | Files |
|---|---|
| `ROUND-52.patch` | 78 |
| `ROUND-53-lib-part1.patch` | 12 |
| `ROUND-53-lib-part2.patch` | 12 |
| `ROUND-53-examples.patch` | 60 |

**The result is byte-for-byte the tree of a trial run** in a separate worktree, done before anything touched main.

## WS2 — the proof

**The suite: PASS=225, FAIL=0, NO-EXPECTATION=4.**

**Goldens: the nivartanam patches change none. `ROUND-52.patch` changes 32.**
- **Each of the 32 is its old golden with empty lines deleted, and nothing else.** 112 lines in all, checked one file
  at a time (`evidence-r54/goldens-changed.txt`).
- **Why:** the old examples printed `likha("x = ")`, then `likha(x)`, then `likha("\n")`. `likha(x)` already ends the
  line, so the third statement printed an empty line. The new form `likha("x = ", x)` does not print it.
- **So the brief's "every golden must be byte-identical" holds for nivartanam,** and it could not hold for
  `ROUND-52.patch`, which removes those statements on purpose.

**Library proofs: 226/226, but only with the compiler change.**
- **With v257, all four patches give 225/226.** `tests/stdlib/r11_sets_lists` stops compiling with
  `Sutram Error: vistarit srot seema atikram`.
- **The cause is the expanded source:** the program plus every `yoj`, which had to fit in 64 KiB. That proof brings
  in six modules. Five more bytes per return (`nivartanam` vs `prati`) push it over.
- **No function body is wrong.** The other 225 proofs and the suite pass, and the nivartanam guard is 0 DIFFER.
- **One correction to Muse's report:** Muse says ROUND-52's comments alone already break this proof. **Measured
  here, they do not.** With `ROUND-52.patch` alone, `r11_sets_lists` compiles with v257. **It is the two together
  that cross the limit.**

**The compiler change (v258):** `IMPORT_BUF_CAP` and `source_buf` go from 65536 to 131072.
- **The expanded source may now be 128 KiB.**
- **One file is still read up to 64 KiB, as before.** That read, and the module-graph reader's buffer, are unchanged.
- **I checked every other 64 KiB number in the compiler.** None bounds the expanded source: the generated program's
  BSS, the global-variable sentinels, and the debugger's statement map are all unrelated.
- **Programs under the old limit are byte-identical** (the guard above).

**The test, `tests/r54/test_r54.py` (8 checks, a gate), run with v258** (`evidence-r54/test_r54.txt`):
- `r11_sets_lists` compiles and prints its expected output.
- **A program and two modules, 126,522 bytes in all, compiles and prints 3.**
- **With a third module (about 148 KB), it is refused with the limit message, and nothing is written.**
- **The control: with v257, the first two checks fail** (`evidence-r54/test_r54-control-v257.txt`). So the test can
  fail.

## WS3 — Devanagari

**`examples/41_recursion.sm` is a migrated example with six returns.** I wrote it three ways and compiled each under
`--lang sanskrit`:

| Spelling | Result |
|---|---|
| `nivartanam` | prints its expected output |
| `प्रति` | prints its expected output |
| `निवर्तनम्` | prints its expected output |

**All three give one identical executable.** **The alias `प्रति` still works after the migration.** This is checked
in the new gate.

The suite's Devanagari programs pass too:
- `153_namespaced_devanagari_function` brings in `examples/lib/r33_devanagari.smlib`. That module is a `प्रक्रिया`
  whose return the patches migrated.
- `218` and `219` run under `--lang sanskrit`.

## WS4 — the count

**`prati` as a whole word, in git-tracked files** (`evidence-r54/prati-count.txt`):

| Area | Before | After |
|---|---|---|
| `lib/*.smlib` | 677 | **0** |
| `examples/**/*.sm` | 122 | **1**, the comment in `examples/256` that names the keyword, kept by Muse on purpose |
| `examples/lib/*.smlib` | 16 | **0** |
| `tests/` | 318 | 318, plus the new test's own text |
| `docs/` | 154 | 154 |

- **lib/ and examples/ match Muse's before-counts exactly.**
- **tests/ and docs/ do not.** Muse says 389 and 146; I measure 318 and 154 on tracked files at `16fc16b`, the same
  way. **I cannot say what Muse counted differently.** The numbers above are what the tree has.

**The negative tests still pass:**
- crash corpus 227/0;
- R70 negative corpus 6 passed, 0 failed (`evidence-r54/r70-negative-corpus.json`).
- **None of them changed.**
- **The one compiler message that says `prati`** (`phal-prakriya: prati siddhi va dosh bhavet`) **is unchanged,**
  so a test that checks it still passes.

## Two tools that read lib/ as text needed the new word

**Both failed after the patches. Neither failure was in the library itself.**

1. **`tools/check_alloc_bounds.py` (the "alloc bounds" gate)** recognised a bound only as `yadi (c > N) { prati`.
   - Now it accepts `nivartanam` or `prati`.
   - **The result is the same as before the migration:** 26 computed allocations, 13 bounded before the multiply, 13
     exempt with a reason.
2. **`tools/sutram_fmt.py` (the "formatted tree" gate)** would have indented 13 of `ROUND-52.patch`'s new comments, in
   ank, ganit, sadhan and varna.
   - **The cause:** a comment after a function with no braces, heading the next function, was indented as if it were
     part of the body above it.
   - **Now such a comment stays at column 0.** It applies when only comments and blank lines separate it from the
     next top-level line.
   - **Both trees, before and after the patches, are unchanged by the formatter.** `--verify` gives the same
     binaries for the four files.
   - **This came from `ROUND-52.patch`, not from nivartanam.**

**Also changed, by a gate:** `docs/sutram-stdlib.html` was regenerated by `tools/gen_stdlib_ref.py` from ROUND-52's
new comments, so 81 functions now have a one-line description there. **That file is generated.** I did not write it.

**Pins:**
- **Moved in the five places:** the compiler `569ffdeb` and `src/r11_sandesh.inc` `0c94b80d`.
- **Check:** `SOURCE_PINS_CHECKED`.
- **Numbers updated, not prose:**
  - PROJECT-MASTER: 48 gates, v258;
  - the scorecard and project status: v258 and the blob.

## What I did NOT do, and why

- **I applied `ROUND-52.patch`, which the brief did not list.** The three listed patches cannot apply without it. The
  owner chose to apply it.
- **No hand edit to any patched file.** The two tools were changed instead of the library.
- **`tests/` and `docs/` still say `prati`:** 318 and 154. That is Muse's ROUND-54, and docs prose is not mine.
- **One file is still read up to 64 KiB.** A single source or module over that is still cut off, as before. This
  round raised only the expanded total.
- **Not run:**
  - **real Windows** (Wine only);
  - **`fuzz_robust`**, which is not a gate.
- **Not touched:**
  - `backups/`, `Windows-to-Sarvam/`, `lang/` and `windows/`;
  - **the non-Sanskrit packs.**
