# R38-00 — Hand-back to Sarvam: the first lines

- **The code is on branch `claude/round-38`, commit `3d56ccd4`. It is not on `main`.** It changes the compiler,
  so it waits for review, as AGENTS.md asks. The branch is `main` at `6241c1ab`, plus that code commit, plus a
  merge of this delivery, so it merges into `main` cleanly. `main` gets only this hand-back, `evidence-r38/` and
  the README index. Pushed with git, not file by file, and not `--force`.
- **Compiler: `main` is still `Sutram 1.0 (v244)`. The branch is `v246`.** I skipped v245 because the unmerged
  Windows FFI build already uses it (`Windows-to-Sarvam/WIN-FFI-2026-10-21.md`).
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux, branch).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux, branch). No golden file changed.
- **Fuzzers (Linux, branch):**
  - `fuzz_r23`: 1000 programs, 35,919 values compared, 0 differ.
  - `fuzz_valid --capabilities`: 500 / 500 agree.
  - `fuzz_robust`: 5000 mutations, 0 crashes, 0 hangs.
- **Gates (`tools/gates.sh`, branch): 34 PASS / 0 FAIL / 1 NOT-RUN.** The NOT-RUN is Windows execution. There is
  one new gate, "R38 fail-alloc", so the count is one higher than R37.
- **Proofs:** library proofs 223 / 223, both with a 4 GB limit and unlimited. Property proofs 86 / 86.

## WS1 — my pick, and why

**I picked the capability: an allocation-failure switch.** The overflow class was closed in R37. What was left was
the code that runs when an allocation fails, and no one could run that code. So I built the way to run it, and
then I ran it.

**On the other two candidates:**

- **The type on variables is still the right next language decision.** It is still the owner's decision, so I
  have not started it.
- **Development is not done, so it is not time for performance.** These correctness items are open:
  - the `kosh` crash found today (below);
  - output-extent APIs (Muse and the owner);
  - printing a large dasham with `likha` (the owner);
  - the `yoj` scanner branch (the owner).

### The switch

```
sutram_compiler --fail-alloc N <in.sm> <out>
```

- **What it does.** It is the ordinary compile, except that the program's Nth allocation returns 0 without calling
  `mmap`. That covers every `nirmmita`, the ones inside libraries included, and `kosh` storage.
- **How it works.** The program keeps a counter inside its own code. Every allocation site decrements it, so only
  the Nth allocation fails. Source: `src/r38_fail_alloc.inc`. Documentation: `docs/FAIL-ALLOC.md`.
- **Without the flag, nothing changes.** On Linux, 566 programs were compiled by v244 and by v246: 474
  executables are byte-identical, 92 are refused identically, and 0 differ.
- **Linux only.** A `.exe` output is refused, and the Windows compiler does not have the flag.
- **It refuses bad input and writes no output file** in each case:
  - N = 0, a non-decimal N, or N of 10⁹ or more;
  - a missing argument or an extra one;
  - another mode after it (`--object`, `--check` and the others).
- **`SUTRAM_LANG` still works after the flag.** The two dropped arguments become empty entries, as with `--ffi`,
  so the environment is still found.

### What it found: every allocation failure in the library crashed

I called every library function that allocates, once for each allocation it makes:

- **Before: 37 fault points, all 37 SIGSEGV** (`evidence-r38/sweep-before.txt`).
- **After: 0** (`sweep-after.txt`).

Each function now returns its failure value, and leaves the caller's buffer as its contract says:

| Functions | Then | Now |
|---|---|---|
| set operations: `rakh_samroop_diff`, `rakh_sangam`, `rakh_sampat`, `rakh_bhed`, `rakh_asti_upasamuh`, `rakh_tak_mala` | SIGSEGV | **`-1`**, `out` unchanged |
| `rakh_sam` | SIGSEGV | passes on the `-1` (it treated any value that was not 0 as "subset") |
| `nighantu_mil` | SIGSEGV | **`-1`**, `dst` unchanged |
| `brihat_shesh`, `brihat_ghatmod` | SIGSEGV, 7 fault points in one `ghatmod` call | **`-1`**, `res` unchanged. `ghatmod` now allocates its scratch once (`brihat_shesh_tr`) instead of once per loop step, so it has 3 fault points |
| `brihat_ank_tak` | SIGSEGV | **`-1`**, `out` unchanged |
| `mil_shreni` | SIGSEGV | **`-1`**, the array unchanged |
| the `roop` formatters (6) and the `vakyank` renderers (2) | SIGSEGV | **`0`, with only the terminator written.** This is the convention they already use for refusing a bad base. A valid number always has at least one digit, so 0 cannot be mistaken for a result |
| controls: `suchi`, `avali`, `nighantu_srij`, `nighantu_vardh`, `mala_nava` | already `0` | unchanged |

The failure value is `-1` wherever the result is a count, because a count is never negative. Where a size can
legitimately be 0, the zero-size case behaves exactly as before. For example, `mil_shreni(a, 0)` is still a no-op:
`nirmmita(0)` returns 0 and is not treated as a failure.

**`tests/r38/test_fail_alloc.py` is a gate: 115 checks over 43 fault points.**

- It checks each fault point's result and the state of the caller's buffer after it.
- It also checks that each function makes exactly the listed number of allocations: one more N must give the
  ordinary result. So a new unchecked allocation is a fault point this test does not expect, and the test fails.
- **Against `main`'s library it gives 34 failures.**

**Source size.** The new checks pushed two property-proof programs over the 64 KiB source limit (`gaps19`,
`containers resize/vinimay`). I shortened history-only comments in `sangrah` and `nighantu`: notes like "Before
R17 this used…", which git still holds. Both modules are now smaller than on `main`, and both properties pass. The
largest flattened program that grew is 55,431 bytes (`evidence-r38/source-headroom.txt`).

**Still open, and I did not fix it: `kosh` storage crashes when its allocation fails** (`kosh-under-fault.txt`).
That code is the compiler's own, not the library's. The fix adds a check to every `kosh` allocation, so it changes
the ordinary compile's bytes. That breaks the rule "the ordinary path is unchanged", so I stopped there. **The
decision it needs: may every `kosh` allocation get a check that stops the program with a message?** The cost is a
few bytes per `kosh` site.

## WS2 — is ChatGPT's allowlist complete?

**It is complete for today's library.** Run over the branch's `lib/`, it finds 36 calls and 0 findings. The extra
call is `brihat_ghatmod`'s single scratch allocation, which uses a spelling (`c * 8`) the list already accepts.

**It is also both stricter and looser than the truth.** I ran the same library mutations through both checkers
(`evidence-r38/ws2-checker-mutations.txt`):

| Mutation | Truth | R103 allowlist | alloc-bounds gate |
|---|---|---|---|
| M1 `mala_nava` loses its bound | unsafe | **PASS** (looser) | FAIL |
| M2 a new `mala` function allocates `sz = n * 16` | unsafe | **PASS** (looser) | FAIL |
| M3 `c * 8` respaced as `c*8` | safe | **FAIL** (stricter) | PASS |
| M4 a new constant `nirmmita(64)` | safe | **FAIL** (stricter) | PASS |
| M5 `nirmmita(3 * 8)` split over two lines | safe, but unreadable | FAIL | FAIL (R38) |
| M6 `ncap * 8 + 8`, with `ncap` bounded | safe | **FAIL** (stricter) | PASS |

- **It is looser** because it matches spellings, not where a value came from. ChatGPT's own R104 named this, and
  v308 records it.
- **It is stricter** because it rejects any new spelling, however safe. The "formatted tree" gate (`tools/sutram_fmt.py --check` over `lib/*.smlib`) keeps the library's
  spacing canonical, which is why M3 does not happen today.

**The same test found a gap in my own R37 gate.** A computed `nirmmita(` split over two lines was skipped, not
checked: `main`'s gate counted 25 allocations instead of 26 and passed. The gate now refuses any call it cannot
read whole on one line (M5).

**My recommendation:**

- Keep `tools/check_alloc_bounds.py` as the gate. It checks where a size comes from, through the variables a
  product was assigned to.
- Keep the allowlist as a review aid. A FAIL from it means "a person should look", not "this is wrong".

## WS3 — the guard

**I cannot state "476 byte-identical, 0 DIFFER".** That count is the Windows session's, over its own set of
programs. Mine, by platform:

- **The compiler, Linux.** v244 against v246, every `examples/`, `examples/*/`, `tests/stdlib/` and `tests/r*/`
  program: 566 programs, 474 byte-identical, 92 refused identically, **0 differ**
  (`ordinary-path-linux.txt`).
- **The compiler, Wine (not Windows).** v244 `win/sutram.exe` against v246, every `examples/*.sm`: 182 identical,
  40 give no output under both, **0 differ** (`ordinary-path-wine.txt`).
- **Real Windows: NOT-RUN.**
- **The library, Linux.** The same v246 compiler over `main`'s library and the branch's library:
  - 566 programs: 388 byte-identical, 92 refused identically, 86 differ (`library-guard.txt`).
  - **The 86 are exactly the programs that reach one of the 7 changed modules through `yoj`.** None reaches no
    changed module, and none reaches one but stays identical (`library-guard-who.txt`, by
    `sutram_build.module_graph`).
  - The 28 programs whose module graph cannot be computed are all identical.
- **The library, Wine (not Windows).** All 77 `tests/stdlib` programs that reach a changed module were compiled
  by v246 `win/sutram.exe` and match their golden files (`wine-stdlib.txt`).

## What I did NOT do, and why

- **I did not merge to `main`.** The compiler changed, and AGENTS.md says unapproved code changes stay in review
  branches.
- **I did not fix the `kosh` crash on allocation failure.** The fix changes the ordinary compile's bytes, so it is
  a decision for the owner (WS1).
- **I did not rebuild `sutram-ide-gui.exe` or `Sutram-Setup.exe`.** They are the owner's builds, accepted on real
  Windows. They still carry v243. `win/sutram.exe` (= `sutram.exe`) was cross-built in the cloud with
  `tools/cross_build_windows.py`, the same way as in R34. That is not the owner's toolchain.
- **I did not run anything on real Windows.** The Windows checks above ran under Wine, and they are labelled so.
- **I did not start the type on variables.** It is the owner's decision.
- **I did not change any golden file, or `docs/CHANGELOG.md`.**
- **I did not commit `docs/sutram-stdlib.html`.** The gate regenerates it, and I restored it after the run.
- **No network access beyond git, no credentials, no `__pycache__`, no `.pyc`.**

## Files

| File | What |
|---|---|
| `evidence-r38/compiler-version.txt` | the version and SHA-256 of both compilers (Linux, and the Windows cross-build) |
| `evidence-r38/sweep-before.txt`, `sweep-after.txt`, `sweep.py`, `sweep_probes.py` | every allocating function, at every allocation it makes, on `main`'s library and on the branch's |
| `evidence-r38/test_fail_alloc.txt` | the new gate's result |
| `evidence-r38/kosh-under-fault.txt` | the open `kosh` crash |
| `evidence-r38/ws2-checker-mutations.txt`, `ws2_mutate.py` | the two checkers against the same mutations, and the gap this found in my R37 gate |
| `evidence-r38/r103-allowlist-on-r38-lib.txt`, `alloc-bounds.txt` | both checkers on the branch's library |
| `evidence-r38/ordinary-path-linux.txt`, `ordinary-path-wine.txt` | the compiler guard |
| `evidence-r38/library-guard.txt`, `library-guard-who.txt` | the library guard, and which programs differ and why |
| `evidence-r38/source-headroom.txt` | the largest flattened programs before and after |
| `evidence-r38/wine-stdlib.txt` | the changed modules' tests under Wine |
| `evidence-r38/gates.txt`, `suite.txt`, `crash-corpus.txt`, `proof_lib-*.txt`, `proof_props.txt`, `fuzz_*.txt`, `other-tests.txt` | the rest |
