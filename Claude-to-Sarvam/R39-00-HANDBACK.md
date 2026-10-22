# R39-00 — Hand-back to Sarvam: the first lines

- **Pushed to `main`:** this hand-back's commit, on top of the following.
  - `034026b1` — the merge of `claude/round-38`.
  - `a292d997` — the numbers audit, the set-scratch fix and the bounds gate.
  - `5e155179` — the lower-bound check.

  Pushed with git, not file by file, and not `--force`.
- **Compiler on `main`: `Sutram 1.0 (v246) - sampurna sutra`** (R38, now merged).
- **Capability:** branch `claude/round-39`, at `13b3c07a`, is v247. It is not merged, because it changes the
  compiler (WS2).
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud), on `main` and on the branch.
- **Suite: `NO-EXPECTATION=4 PASS=218`, FAIL=0.** Linux x86-64 (cloud), on `main` and on the branch.
  - These are the same 4 programs as before: `215_r12_wordfreq`, `216_r12_expr`, `217_r12_report` and
    `219_sanskrit_kosh_aliases`.
  - The runner exits 1 because it counts NO-EXPECTATION as not passing.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud:**
  - `main`: **34 PASS / 0 FAIL / 1 NOT-RUN.**
  - `claude/round-39`: **35 / 0 / 1.** The extra gate is the new "R39 nirmmita_gun".
  - The NOT-RUN is "Windows execution".
- **The guard:**
  - **The merge, Linux:** 566 programs, **474 byte-identical, 92 refused identically, 0 DIFFER.**
  - **The merge, Wine:** 182 / 182 identical.
  - **The capability branch:** 567 programs, 475 / 92 / **0 DIFFER**, and Wine 182 / 182.

## ITEM 1 — the merge

**`claude/round-38` is merged** (`034026b1`, `--no-ff`, with git).

- File modes were checked: 9 files are 100755 before the merge and 9 after.
- The binaries came through intact: the merged `sutram_compiler` rebuilds byte for byte from the merged source.
- The guard numbers are in the first lines (`evidence-r39/guard-linux.txt`, `guard-wine.txt`).
- The library half of the change is `guard-library.txt`: **86 programs differ, and they are exactly the 86 that
  reach one of R38's 7 changed modules.**

**Does merging mine first make `claude/windows-ffi` harder? No.** I trial-merged it onto the merged `main` in a
throwaway worktree (`evidence-r39/windows-ffi-merge-order.txt`).

- **9 files conflict, and every one of them would conflict in either order.** Both branches bump the version,
  move the same pins and rebuild the same three binaries.
- **One source hunk needs thought:**
  - `windows-ffi` removed the `%ifndef WINDOWS` that guarded the `--ffi` block.
  - R38's `--fail-alloc` block sits inside that guard.
  - **The fix:** keep R38's block and close it with its own `%endif`.
- **Resolved that way, the trial merge holds up on Linux:**
  - it builds (as v247);
  - `test_fail_alloc` is 115 / 0, and `test_ffi` is 50 / 0;
  - the ordinary path is 0 DIFFER;
  - `win/sutram.exe` cross-builds.
- **When they merge, the version should be v248**, because the capability branch uses v247.

## ITEM 2 — the full test run, on the merged tree

Environment: **Linux x86-64, the cloud container**, for every line unless it says otherwise. Each tool's full
output is in `evidence-r39/`.

| Check | Result |
|---|---|
| `sh tools/gates.sh` | **PASS: 34 / 0 / 1.** The NOT-RUN is Windows execution |
| `tests/run_tests.py` | **AS EXPECTED: NO-EXPECTATION=4 PASS=218, 0 FAIL** |
| `crash_corpus.py` | **PASS:** 227 cases + manifest, 0 failed |
| `proof_lib.py`, unlimited and under `ulimit -v 4 GB` | **PASS:** 224 / 224 both. One new proof: R39's witness |
| `proof_props.py` | **PASS:** 86 / 86 |
| `check_layers.py` | **PASS:** 14 core, 9 alloc, 1 std |
| `check_alloc_bounds.py` | **PASS:** 26 computed allocations, 13 bounded, 13 exempt, 0 failed |
| unittest r66, r67, r68, r70 | **PASS:** 22, 17, 19 and 36 tests |
| r22, r23, r25, r28, r29, r30, r31, r34 (`test_ffi_v2`, `test_windows_fixes`) | **PASS:** each 0 failed |
| **unittest r69** | **FAIL: 2 failures, both in Windows-channel files I did not touch** (below) |
| `tests/r34/test_link_windows.py` | **NOT-RUN:** needs real Windows |
| **`tests/r35`** | **NOT-RUN: it does not exist on `main`.** It is on the unmerged `claude/windows-ffi` |

**r69 had 3 problems, and they were on `main` before the merge,** so the merge did not cause them.

- **I fixed one of them, which was mine.** The R19 reformat had changed `tests/r69/pairs/all_registers.sm` (it
  added spaces before `#`), so it no longer matched its pinned SHA-256.
  - I restored the reviewed bytes and listed the file in `tools/fmt-exclude.txt`.
  - **The pin did not change.**
- **The other two are the Windows channel's**, and I left them:
  - `windows/build-windows-native.ps1` no longer runs the E_UTF8 diagnostic check that R69 asserts.
  - `windows/build-windows-setup.ps1` no longer checks the staged payload's hash.
  - Both were dropped in the 2026-10-18 ROUND-03 Windows merge (`91aa7e5c`, `7bacd51f`).
  - Both are still absent on `claude/windows-ffi`. **The Windows channel should restore them, or retire the two
    tests.**

## ITEM 3 — the numbers audit

**`tools/doc_counts_gate.py` reported nothing,** both on `main` and on the merged tree. It checks only two
things:

- an `N/N` pair whose first number is higher than the number of gates;
- an `NNN pass` count.

So it let through these stale numbers. Each one I fixed is now the measured number.

| Document | Was | Measured |
|---|---|---|
| README | 195 examples (191 + 11); 303 functions; codegen 27/27 | 222 (209 numbered + 13), and 13 more in subfolders; 305; 12/12 |
| PROJECT-MASTER table | library proofs 217; 303 functions; 207 examples; source 545,722 B → binary 190,144 B; ~1,800 files | 224; 305; 222; 598,889 B → 424,568 B; ~3,800 files |
| PROJECT-MASTER table | — | added rows: gates 34 / 0 / 1, and crash corpus 227 |
| PROJECT-MASTER "expect" lines | codegen 27; proofs 183; properties 76; layers "12 core, 9 alloc" | 12; 224; 86; 14 core, 9 alloc, 1 std |
| PROJECT-OVERVIEW | ~15k lines; 303 functions; 202 examples; codegen 27/27; packs 30/30; IDE undo 27/27; X11 31 checks; SHA `6036dd1c…`; suite 227/270; 178 tests | ~24k; 305; 222; 12/12; 33/33; 12/12; 65; `51f8f6f1…` (v246); 218 pass + 4; 218 |
| PROJECT-OVERVIEW build commands | `nasm … src/sutram_compiler.asm` | `src/r68_compiler_entry.asm` (see below) |
| `sutram-project-status.html` | snapshot of 2026-10-16 (v173); 187 tests; 217 / 72 proofs; 21 modules and 281 functions; 202 examples; 22 doc pages; 16 GUI tests; 1,782 files; 180 / 72; r66–r68 "24 pass (15 skipped)"; sizes | 2026-10-22 (v310, compiler v246); 218; 224 / 86; 24 and 305; 222; 25; 18; ~3,800; 224 / 86; 58 pass, 0 skipped; 598,889 B → 424,568 B; IDE 38,160 B |
| `sutram-design-parameters.html` | 21 modules; 16 GUI tests; 281 functions; codegen 27/27; 180 / 72 proofs (twice) | 24; 18; 305; 12/12; 224 / 86 |
| `sutram-scorecard.html` "measured" parts | SHA `64ea028a`; suite 227/270; 303 functions; 202 examples; 22 doc pages; codegen 3/3; 14,986 lines and 359 KB; IDE 1,339 lines and 18 KB; "21 modules, 303 functions" | blob `7db83d38` (v246); 218 + 4; 305; 222; 25; 12/12; 24,325 and 599 KB; 1,708 and 25 KB; 24 and 305 |

**One build fact I fixed: PROJECT-OVERVIEW's build command built a different compiler.** It said
`nasm -f elf64 src/sutram_compiler.asm`. That assembles, but without the R68 diagnostics, so the binary is not
the shipped one; I checked this by building it. Both commands (Linux and Windows) now name
`src/r68_compiler_entry.asm`, as README and BUILDING already did.

**The gate is stronger now.** It checks every count that `gates.sh` states, wherever a document quotes it:

- codegen shapes;
- library proofs and property proofs;
- library modules and functions;
- GUI tests;
- crash-corpus cases.

It reports each mismatch as a NOTE. A quoted count that is history goes on a `HISTORY` list with its reason;
there is one so far, PROJECT-MASTER's account of the rename.

**Run over `main`'s old documents, the new gate reports 24 stale counts** (`doc_counts_gate-r39-on-old-docs.txt`).
On this tree it reports none.

**What the gate still does not catch:**

- the example count, the file count, the compiler's lines, bytes and SHA, the versions and dates;
- the keyword count. The tree has no single definition of a keyword: the scorecard says 32 in one place and 28
  in another, and the Sanskrit pack maps 52 distinct words. I left those numbers alone;
- any document other than these six (`docs/*.md`, the books, ROADMAP);
- **prose that is false without containing a number.**

**Prose that is false now: ChatGPT's R105 WS2 already lists it**, so I am not filing it again. I confirm it by
measurement, and I did not edit it:

- "no separate compilation" (R29 built it);
- "no first-class functions" (R23);
- "there is no FFI" (R32 to R34);
- "Windows never executed";
- the `mala` / `io` / `net` "comment-only files": `mala` is a working module, and `io` and `net` do not exist.

**The scorecard's percentages are judgements, not measurements,** and I did not change them.

## ITEM 4 — clean up

- **The tree is clean.** It has no tracked `__pycache__`, `*.pyc`, `*.bak`, `*.orig`, `*.rej` or `*.tmp` files,
  and no stray `.o`, `.bin`, `.smo` or `.obj` at the root. Each run's caches and the `build/` and
  `fuzz-robust-out/` directories were deleted after it.
  - The tracked `.o` files in `tests/r32`, `tests/r33` and `tests/r34` are test inputs, so they stay.
  - The tracked zip under `ChatGPT-to-Sarvam/` is ChatGPT's, and I did not touch it.
- **`backups/` is untouched,** as `backups/README.md` asks.
- **The `compiler/` folder should go.**
  - It holds 11 files: R30–R40-era design notes, two patches, two manifests, and a 384 KB `.asm.txt` snapshot.
  - No tool, test or build step reads it. I searched every `.py`, `.sh`, `.asm`, `.inc` and `.ps1` file.
  - **Its name misleads:** the compiler is in `src/`.
  - Git history and `backups/` both keep it.
  - I did not delete it: that is the owner's call, and it is one `git rm -r compiler`.

## ITEM 5 — the Windows channel's r18 answer

**It was acted on, in R35** (`46540309`).

- The defect it named (`tests/stdlib/r18_srij_overflow_guard`) was fixed after the Windows delivery's base:
  `1e8dc661` is an ancestor of `46540309`, so the Windows run did not have the fix.
- R35 replaced the 24 GB input, whose result depended on the machine, with values that give 0 on every machine.
- The test's own comment says so. "Nobody has reacted" is not right.

**Its real point was that a golden file can encode the machine's memory policy.** I tested that in both
directions on the merged tree (`evidence-r39/r18-memory-policy.txt`):

- **A machine that refuses large allocations.** I ran the library proofs under `ulimit -v` at 256 MB, 512 MB,
  1 GB, 2 GB, 4 GB and unlimited. All 224 pass at every limit.
- **A machine that grants them, as the owner's 48 GB WSL and real Windows did.** I built a scratch compiler,
  never committed, whose allocations pass `MAP_NORESERVE`. Here it gets 24 GB and 100 TB granted, where the
  ordinary compiler gets 0.
  - Library proofs: 224 / 224.
  - Property proofs: 86 / 86.
  - Suite: 218 / 4.
  - `test_fail_alloc`: 115 / 0.
  - The four memory-sensitive tests each match their golden.
- **So no golden in the tree depends on memory policy any more.**

**The Windows branch's other numbers:**

- Its "31 PASS / 3 FAIL" under WSL is measured on its base, `1e8dc661`.
- Two of the three FAILs are the r18 test, which R35 fixed. The third is X11, which needs a display.
- Once the branch is on today's `main`, the first two should pass.

## ITEM 6 — the guard

- **This round: 566 programs, 474 byte-identical, 92 refused identically, 0 DIFFER on Linux; and 182 / 182
  identical under Wine (not Windows).**
- **I cannot state "476".** That is the Windows session's count over its own 564 programs, two of them
  `tests/r35` programs that are not on `main`.
- **This round's library change:**
  - 71 programs differ, and they are exactly the 71 that reach one of the 5 modules it changed
    (`guard-library-r39.txt`).
  - Wine: all 64 `tests/stdlib` programs that reach those modules match their golden files.
- **A correction to R38's evidence.** R38's `library-guard.txt` said both trees were "compiled by the same v246
  compiler".
  - In fact each tree used its own compiler, v244 against v246.
  - The conclusion still holds, because v244 and v246 give the same bytes for every program. The label was
    wrong.
  - This round's label is correct.

## ITEM 7 / WS2 — the capability, and whether development is done

**My pick:** two checkers keep chasing a wrap that exists only because the library multiplies before it
allocates. So the capability is an allocation that does the multiply itself, and checks it.

### `nirmmita_gun(count, size)`, on branch `claude/round-39` (v247)

**It gives 0, instead of a small wrong allocation, when:**

- `count < 0`;
- `size <= 0`;
- `count × size` passes 2⁶³ − 1.

Otherwise it is `nirmmita(count × size)`.

**How it works:** the multiply is in the emitted code (`imul`, then `jo`), next to the allocation. So a wrapped
size never reaches `mmap`, whatever the caller passed. Source: `src/r39_nirmgun.inc`. Documentation:
`docs/NIRMMITA-GUN.md`.

**Test: `tests/r39/test_nirmgun.py`, a gate, 10 checks.** It covers:

- each refusal, including 2⁶¹ + 1 cells, which a plain multiply wraps to 8 bytes, and MAX × MAX;
- nested use and use as a statement;
- `--fail-alloc`;
- arity: one or three arguments are refused with no output, as for every builtin;
- a PE build.

**Results:**

- A program that does not use it compiles to the same bytes (567 programs, 0 DIFFER).
- A PE program compiled by the Windows compiler gives the same values. That ran under Wine, not real Windows.
- The fuzzers on v247 (Linux cloud) found nothing:
  - `fuzz_r23`: 1000 programs, 35,741 values compared, 0 differ.
  - `fuzz_valid`: 500 / 500 agree.
  - `fuzz_robust`: 5000 mutations, 0 crashes, 0 hangs.

**The library does not use it yet.** Moving the 26 computed sites onto it changes those programs' bytes, so it
is a separate step, for after review.

### Is the development phase complete? No.

These correctness items are open, each with its owner:

1. **The compiler's own `kosh` storage crashes when an allocation fails** (R38). The fix changes the ordinary
   compile's output, so it needs a decision.
2. **Printing a large dasham with `likha` is inexact** (the owner).
3. **The output-extent APIs** (Muse and the owner).
4. **The two lost Windows build checks** (above; the Windows channel).
5. **The `yoj` scanner branch** (the owner).
6. **The type on variables** (the owner). It also unblocks the one provenance question no source checker can
   answer: how large is the buffer a caller passes?

The performance phase should start when 1 to 4 are closed.

## WS3 — does `tools/check_alloc_bounds.py` have R104's weakness?

**Partly, before this round. It now closes every case I could construct, except one, which is stated below.**

R38's gate already followed a size through the variables a product was assigned to, so R104's own case
(`sz = c * 8` with no bound) failed it. But **six other routes to an unsafe size passed it.** I ran the same
seven mutations through each checker, each on its own round's library (`evidence-r39/ws3-provenance-mutations.txt`):

| Mutation (each unsafe) | R38 gate | R39 gate | R103 allowlist |
|---|---|---|---|
| P1: the bound raised past the safe value (`c > 2⁶¹` before `c * 8`) | PASS | **FAIL** | PASS |
| P2: `c` doubled after its bound | PASS | **FAIL** | PASS |
| P3: a new allocation in an exempt prakriya | PASS | **FAIL** | FAIL |
| P4: R104's `sz = c * 8` with no check | FAIL | **FAIL** | PASS |
| P5: the multiply moved into a caller, `helper(n * 8)` → `nirmmita(sz)` | PASS | **FAIL** | PASS |
| P6: the `c < 0` check removed (R37's −2⁶¹ + 1 cells is 8 bytes) | PASS | **FAIL** | PASS |
| P7: the bound only on one branch | PASS | **FAIL** | PASS |
| P0: no mutation (safe) | PASS | PASS | PASS |

**What changed in the gate:**

- **An exemption names its expression.** A new allocation in an exempt prakriya is no longer exempt (P3).
- **The bound's value must be small enough.** With every bounded count at its bound, the size must still fit in
  2⁶³ − 1 (P1).
- **A bounded count assigned again after its bound is no longer bounded** (P2).
- **A bounded plain count needs a check below as well,** such as `c < 0` or `c < 1`. A container's field, such
  as `X[1]`, is exempt from that, because its constructor sets it (P6).
- **A bound counts only while its block is open** (P7).
- **Every size that is not a constant is checked:** a product, a parameter, or a function's result (P5).

**It also found a real defect, and ChatGPT's R105 WS1 found the same one independently.** The set operations and
`nighantu_mil` sized their scratch from the **caller's** `cap` argument, which nothing checks. The R37 exemption
reason, "a set is a map: cap ≤ the bound", was mine, and it was wrong: `cap` is the caller's claim, not `a[0]`.

- **What it did:** `rakh_tak_mala(s, 1, out)` on a set of 200 32-byte elements allocated 34 bytes and wrote
  6,600 into it, over the previous allocation. `rakh_sangam` then returned 6437991695636517851, read from
  memory that had been overwritten.
- **The fix:** they now size from the set itself (`a[0]`, `s[0]`, `src[0]`), which `nighantu_srij` bounds. The
  witness is `tests/stdlib/r39_scratch_from_set` (a new golden; no existing one changed).
- **The caller-trusted counts are bounded now too.** `brihat_shesh`, `brihat_ghatmod`, `brihat_ank_tak` and
  `mil_shreni` bound their counts instead of being exempt.
- **Every remaining exemption is a container's own capacity.**

**What the gate still cannot prove:**

- **the true value of a count a caller passes.** No source checker can know a raw buffer's real extent; that
  needs the type on variables or run-time bounds;
- a `#` inside a string literal;
- anything a one-line regular expression misreads.

It is a structured approximation, not a proof. `nirmmita_gun` removes the need for it at any call that uses it.

**On the R103 allowlist:** the 12 new set spellings (`a[0] * 33 + 1` and the others) fail it. That is the
"stricter" behaviour R38 measured. They need ChatGPT's review; the file is ChatGPT's, so I did not edit it. Its
pattern also does not see `nirmmita_gun(`.

## What I did NOT do, and why

- **I did not merge `claude/round-39`.** It changes the compiler, so it waits for review.
- **I did not merge, rebase or edit `claude/windows-ffi`, `windows/` or `Windows-to-Sarvam/`.** Those are the
  Windows channel's. That includes the two r69 failures in `windows/`.
- **I did not change any prose.** I changed numbers, and one build command that built the wrong compiler. The
  scorecard's percentages are judgements, so I left them.
- **I did not delete `compiler/`.** That is the owner's call.
- **I did not touch `backups/`.**
- **I did not edit ChatGPT's R103 allowlist,** even though 12 new library spellings fail it.
- **I did not fix the `kosh` crash, or move the library onto `nirmmita_gun`.** Both change ordinary output.
- **I did not run anything on real Windows.** Every Windows check above ran under Wine and is labelled so.
- **I did not change any existing golden, and I did not edit `docs/CHANGELOG.md`.**
- **I did not commit `docs/sutram-stdlib.html`.** The gates regenerate it, and I restored it after each run.
- **No network access beyond git, no credentials, no `__pycache__`, no `.pyc`.**

## Files

`evidence-r39/SUMMARY.txt` indexes the folder. The capability branch's own runs are in
`evidence-r39/branch-round-39/`: gates, guard, Wine, fuzzers, corpus and suite.
