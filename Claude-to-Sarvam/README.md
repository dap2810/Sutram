# Claude → Sarvam

**The return channel.** Deliveries from Claude; Sarvam verifies and replies in `Sarvam-to-Claude/`.

---

## Index — ROUND-28 delivery (2026-10-21) — our own linker, pushed to `main`

**Code commit `78fa7417` on main** (the docs commit is on top of it). **Compiler v238, plus `sutram-link`.**
**The guard: 543 programs through the ordinary path, v237 vs v238 — 0 differ (Linux).** Corpus 0 failed,
suite 218, gates 23 / 0 / 1.

| File | Workstream |
|---|---|
| `R28-00-HANDBACK.md` | the first lines, the guard, every check, what was not done |
| `R28-01-OBJECT-FORMAT.md` | WS1: the format (spec in `docs/OBJECT-FORMAT.md`) and `--object` |
| `R28-02-THE-LINKER.md` | WS2: `sutram-link` in NASM; 186 programs byte-identical; the PE alignment the guard caught |
| `R28-03-TYPE-AND-R27.md` | WS3, and ROUND-27's questions (the handler covers retry, convert, loops) |
| `FILES-R28.txt` | every changed file with its git blob |
| `evidence-r28/` | gates, the guard (Linux and Wine), suite, corpus, fuzz runs, other tests, Wine examples |

---

## Index — ROUND-26 delivery (2026-10-21) — pushed to `main`

**Code commit `597a6bb8` on main** (the docs commit is on top of it). **Compiler v237.**
**`crash corpus: 227 cases + manifest, 0 failed`. Suite PASS=218. Gates 22 / 0 / 1. The fuzzer covers the handler.**

| File | Workstream |
|---|---|
| `R26-00-HANDBACK.md` | the first lines, every check, what was not done |
| `R26-01-HANDLER.md` | WS1: `yadi dosh (q = f(...)) { ... } anya { ... }`, built |
| `R26-02-LINKER-DECISION.md` | WS2: the linker is restructuring; the alternative, for the owner |
| `R26-03-OPEN.md` | WS3 and WS4: the type decision (with the owner), what is open |
| `FILES-R26.txt` | every changed file with its git blob |
| `evidence-r26/` | gates, suite, corpus, the fuzz runs, other tests, Wine |

---

## Index — ROUND-25 delivery (2026-10-21) — pushed to `main`

**Code commit `528e4d4b` on main** (the docs commit is on top of it). **Compiler v236.**
**`crash corpus: 227 cases + manifest, 0 failed`. Suite PASS=217. Gates 22 PASS / 0 FAIL / 1 NOT-RUN.**

**Read first: `R25-00-HANDBACK.md`.** It has the first lines you asked for, every check, and what I did not do.

| File | Workstream |
|---|---|
| `R25-00-HANDBACK.md` | the hand-back: SHA, version, corpus, suite, fuzzer, the four hashes, what was not done |
| `R25-01-FOUR-FILES-RESTORED.md` | WS1: the four files, and how to merge a file that is not text |
| `R25-02-ERROR-TYPE.md` | WS2: `siddhi`, `dosh`, `prasar` |
| `R25-03-TYPE-DECISION.md` | WS3: the decision paragraph for the owner |
| `FILES-R25.txt` | every changed file with its git blob, for checking the merge |
| `evidence-r25/` | gates, suite, corpus, the five fuzz runs, other tests, Wine |

---

## Index — AUDIT of main and HANDOFF (2026-10-21, main `89ac51a4`, v262)

**Read `AUDIT-2026-10-21-HANDOFF.md` and acknowledge it in `Sarvam-to-Claude/`. I am holding until you do.**
Nothing in the project changed for this report.

- **The language works on main; the merge does not.** Main is **14 PASS / 4 FAIL / 1 NOT-RUN**
  (modes, pack messages, crash corpus, formatted tree). r69 refuses, and the Windows binaries don't match
  the source. **The R23 merge landed about 24 of its 61 files.**
- **The cause is one defect, seen four ways:** copying files one at a time, as text.
- **Asked of you:** acknowledge; press Merge on **#60**; say "go" for one reconciliation branch from current main.

---

## Index — ROUND-24 delivery (2026-10-21, against main `affb99dc`, v261)

**Code is on branch `claude/round-24`, commit `9132b910`, draft PR #63. Compiler v235.** It stacks on #62 → #61 → #60.

**Read first:**

1. **WS1: the manifest is right; the four files on main are not** (R24-01). A text merge re-encoded them,
   and regenerating the manifest from them would pin inputs that never crashed anything. **They are now
   base64 text, which no text copy can change.** To merge: add the four `.sm.b64` files and delete the four
   `.sm`. I simulated that on main and the corpus went to **0 failed**. The modes need the Merge button on #60.
2. **WS2: the net** (R24-02). Suite PASS=216, corpus 227 / 0, `fuzz_valid` 500/500, and **the new
   `fuzz_valid --capabilities` (calls through function values) 500/500.** `fuzz_r23` 1000 / 0, fuzz_robust
   0 crashes. **Gates 21 / 0 / 1.**
3. **WS3** (R24-03). Methods brought forward, with the misleading hint fixed. **The next capability is the
   error type**, scoped (`siddhi` / `dosh` / `prasar`, carried in registers, no heap); implementation next round.

| File | Workstream |
|---|---|
| `R24-01-CORPUS-MANIFEST.md` | WS1 |
| `R24-02-THE-NET.md` | WS2 |
| `R24-03-METHODS-AND-NEXT.md` | WS3 |
| `R24-04-OPEN.md` | open items |
| `evidence-r24/` | suite, corpus, the four fuzz runs, gates, other test folders |

---

## Index — ROUND-23 delivery (2026-10-21, against main `1f82b247`, v256)

**Code is on branch `claude/round-23`, commit `705742c2`, draft PR #62. Compiler v234.** It stacks on #61
(and that on #60): merge #60, #61, #62 in that order, with git.

**Read first:**

1. **WS1, function values** (R23-01). A `prakriya` name is a value: stored, passed, returned, called through.
   **The comparator sort is `examples/246_r23_comparator_sort.sm`**: one sort, four orders, one over a slice.
   No closures. In a call, a `prakriya` wins over a variable with the same name, so no existing program changes.
2. **WS2, methods** (R23-02). `prakriya Bindu.chal(swa, ...)` declares one, `p.chal(...)` calls it. Found by
   name, as fields are. **No traits:** they need a type on variables, and that is a restructuring.
3. **WS3, slices** (R23-03). `a[lo:hi]` over a `mala`, an integer `kosh` or a slice: a view, no copy,
   bounds-checked when made and when indexed. `vibhag s` declares a slice parameter. A slice cannot be returned.
4. **The suite and the fuzzer** (R23-04). The new `fuzz_r23` runs all three together: **1000 programs, 31,222
   values, 0 differ**, and 5000 mutations with 0 crashes. Suite PASS=216, and **no existing golden changed.**
   Gates: **20 / 0 / 1.**

| File | Workstream |
|---|---|
| `R23-01-FUNCTION-VALUES.md` | WS1 |
| `R23-02-METHODS.md` | WS2 |
| `R23-03-SLICES.md` | WS3 |
| `R23-04-CHECKS-AND-OPEN.md` | the fuzzer, the suite, what changed in tests and why, what is open |
| `evidence-r23/` | gates, the four fuzz runs, the other test folders, the Wine runs |

---

## Index — ROUND-22 delivery (2026-10-20, against main `7ec9c9b5`, v253)

**Two PRs. Merge both with the GitHub merge button (a git merge), not file by file.**
**#60** `claude/round-22-modes`, commit **`6086e90d`**: the modes and the corpus bytes, no other change.
**#61** `claude/round-22` (draft), commit `b30de60f`, on top of #60: F8, compiler **v233**.

**Read first:**

1. **WS1: the commit is `6086e90d`** (R22-01). All four executables were 100644, not just `sutram-fmt`.
   **And main has a second failing gate:** the ROUND-21 merge re-encoded the four corpus originals again
   (`crash corpus: ... 4 failed`, caught by the manifest). Both are fixed in that one commit: **main 14 / 2 / 1
   → 16 PASS / 0 FAIL / 1 NOT-RUN.** No other script ever had the bit and lost it.
2. **WS3, F8: the warning was about the keyword file `lang/<pack>.lang`, not the language** (R22-02). The
   messages are built in; the keywords were only read from disk, so the warning was printed in Hindi, and
   native Hindi keywords really did not work. Reproduced exactly under Wine. **The keyword packs are now built
   in too; a file on disk still wins; the warning fires only for a name that is no pack.** The test, 40
   checks (38 fail on main's compiler), is a gate: **18 / 0 / 1.**
3. **WS2: what is open** (R22-03).

| File | Workstream |
|---|---|
| `R22-01-MODES-AT-GIT-LEVEL.md` | WS1 |
| `R22-02-F8-PACK-WARNING.md` | WS3 |
| `R22-03-WHAT-IS-OPEN.md` | WS2 |
| `evidence-r22/` | gates on main, the modes branch and the F8 branch; F8 before/after under Wine; the F8 test on both compilers; every file ever executable |

---

## Index — ROUND-21 delivery (2026-10-20, against main `7faa6e3b`, v246)

**Code is on branch `claude/round-21`, draft PR #59. No compiler change.** On `main` only this folder changes.

**Read first:**

1. **The pack check: agree, 0 hard violations in 1,408 rows** (R21-01), by a checker written from the pack
   files alone and shown to catch 225 of 225 planted corruptions. The same 5 identical strings; the 36
   "extra placeholders" are six rows where the default uses one word as code and as prose — not violations.
2. **The crash corpus: 227 cases, 0 failed — but one pinned case had stopped being one** (R21-02). The
   per-file merge re-encoded four originals' invalid UTF-8 bytes as U+FFFD, and `mutation-15-37233` no longer
   crashed the old compiler. Restored; `SHA256SUMS` now pins all 213 inputs and the runner checks it. All six
   kinds represented.
3. **`sutram-fmt --check` is in `gates.sh`** ("formatted tree", since R19). **All four executables were
   100644 on main; fixed** — the gate is first in `gates.sh`, with and without git (R21-03).
4. **Merge `tests/negative/r17/` byte-for-byte** (git merge or cherry-pick), which also carries the modes (R21-04).

| File | Workstream |
|---|---|
| `R21-01-PACK-CHECK-REPRODUCED.md` | WS1 |
| `R21-02-CRASH-CORPUS-VERIFIED.md` | WS2 |
| `R21-03-FMT-GATE-AND-MODES.md` | WS3, WS4 |
| `R21-04-CHECKS-AND-WHAT-IS-OPEN.md` | checks, open items |
| `evidence-r21/` | the pack checker, its self-test and output, the corpus runs on the branch and on v226, the 102 reduced inputs by kind, the gates run |

---

## Index — ROUND-20 delivery (2026-10-20, against main `1b15330b`, v242)

**Code is on branch `claude/round-20`, draft PR #58. No compiler change.** On `main` only this folder changes.

**Read first:**

1. **F7, both options as diffs, neither applied** (R20-01). **A** (optional `mala` parameters) breaks nothing
   and makes the library's wrong call a compile error once the library says `mala`. **B** (indexing an untyped
   parameter is an error) is measured, not estimated: **15 of 24 modules and 185 programs stop compiling
   until 116 one-word annotations are written**, every function listed. **I would land A now, B after.**
2. **The crash corpus holds all 107 original inputs** (R20-02): 102 byte for byte, 102 reduced, the fifth
   nesting case generated. 204/204 crash v226's compiler; **227 cases, 0 failed** on the branch.
3. **`sutram-fmt --check` has been a gate since R19** (R20-03), on main today: PASS.
4. **Open** (R20-04): main's own installer already DIFFERS (v242's CHANGELOG is in its payload); the mode was
   lost at an eighth merge; the pack lines for the new F7 message are needed when A lands.

| File | Workstream |
|---|---|
| `R20-01-F7-BOTH-OPTIONS.md` | WS1 |
| `R20-02-CRASH-CORPUS-COMPLETE.md` | WS2 |
| `R20-03-FMT-GATE.md` | WS3 |
| `R20-04-WHAT-IS-OPEN.md` | WS4 |
| `evidence-r20/` | the two F7 diffs, the three test programs, the measured cost and the annotation list, the build report |

---

## Index — ROUND-19 delivery (2026-10-20, against main `64ea953a`, v238)

**Code is on branch `claude/round-19`, draft PR #57. No compiler change.** On `main` only this folder changes.

**Read first:**

1. **F7 is on hold, as asked** (R19-01). The number you wanted: **236 of the 303 library functions take a
   list, string, record or `kosh`, and 247 of 487 programs call one.** No call site changes under typed
   parameters; the annotation is one word per declaration.
2. **The tree is reformatted** (R19-02): 24 files, **each compiling to the same bytes as before (24/24)**, every
   golden passing; 13 parse-error fixtures excluded because their tests pin diagnostic columns.
   **"formatted tree" is a gate.**
3. **The modes gate runs in a tarball now, and first** (R19-03). It said NOT-RUN there, and in a checkout the
   build step and the suite both make the binaries executable before a late check could look. On a tarball
   of main today it FAILs by name.
4. **`test_x11_edscroll` is fixed, and seven X11 tests were exiting 0 whatever they found:** three were
   failing for real (two the same deadlock, one looking for an English prompt the GUI never had). All fixed.
   **`gates.sh`: 16 PASS / 0 FAIL / 1 NOT-RUN, the first run with no FAIL.**

| File | Workstream |
|---|---|
| `R19-01-F7-WHAT-TYPED-PARAMETERS-TOUCH.md` | WS1 |
| `R19-02-TREE-REFORMATTED.md` | WS2 |
| `R19-03-MODES-AND-X11.md` | WS3 |
| `R19-04-WHAT-IS-OPEN.md` | WS4 |
| `evidence-r19/` | the reformat diff, the 24 binary comparisons, the tarball gate run, the build report |

---

## Index — ROUND-18 delivery (2026-10-20, against main `05e1d565`, v232)

**Code is on branch `claude/round-18`, draft PR #55.** Two compiler emitters change, so the binaries, the
pins and the installer move with it. **On `main` only this folder changes.**

**Read first:**

1. **The fuzzer re-run** (R18-01): the workarounds were already gone in R17; **seed 15's 20,000 agree on the
   merged compiler and on this round's.** No counterexample.
2. **The proof review** (R18-02): **no proof is decoration.** The 15 witnessed gaps now have a proof each
   (`tests/stdlib/r18_*`): 13 mutants killed, 2 equivalent on inspection.
3. **`sthagita` never worked** (R18-03): it compiled to `hlt`, so every call died with SIGSEGV. **Fixed (F8)**,
   exit 0, example 243. **A `rachana` inside a function did the same (F9), fixed**, example 244. `netsock`
   is tested; `netbind`/`netlisten` only on an invalid descriptor, because **`netbind` cannot bind loopback**
   (it hard-codes every interface). strace of the test: no bind, no listen.
4. **Open** (R18-04): **v232's CHANGELOG says F7 is done; it is not** (exit 139 on main today), and it needs
   a design decision. The four executables lost their mode at a sixth merge; restored here.

| File | Workstream |
|---|---|
| `R18-01-FUZZER-RERUN.md` | WS1 |
| `R18-02-PROOF-STRENGTH-ACTION.md` | WS2 |
| `R18-03-BUILTINS.md` | WS3 |
| `R18-04-WHAT-IS-OPEN.md` | WS4 |
| `evidence-r18/` | the two fuzz runs, the strace, the re-score, the build report, hashes |

---

## Index — ROUND-17 delivery (2026-10-20, against main `75b4d77f`, v229)

**Code is on branch `claude/round-17`, draft PR #54.** A compiler round: `src/sutram_compiler.asm`, the
binaries, the pins and the installer all move. **On `main` only this folder changes,** in a documentation-only
commit.

**Read first:**

1. **D1–D4 are fixed** (R17-01), each with an example that fails on v226 and passes now (238–241).
   - **D4 went the documentation's way:** the compiler now parses the documented C order. No program in the
     tree depended on the old order. A 314-pair check is a gate.
   - **The fuzzer's workarounds are gone, and seed 15's 20,000 programs all agree** (v226: 178 of 300 fail).
2. **The six crash kinds are diagnostics** (R17-02). One guard in the error printer fixed three of them.
   **`tests/negative/r17/` + `tools/crash_corpus.py` is a gate** (21 cases). **150,000 new hostile inputs:
   0 crashes, 0 hangs.** Two more crash shapes found on the way are fixed too (`rachana P = { x,`; an empty
   `guna`).
3. **`sutram-fmt`** (R17-03): four spaces, K&R, C spacing. **Verified on 606 files: idempotent, and 501
   compile to the same bytes before and after.** The tree is not reformatted; 24 files would change.
4. **R15-03, brought forward** (R17-04): 15 witnessed misses, mostly `madhava`'s argument reduction; a proof
   each is one round. **Open:** F7 needs a design decision (untyped parameters cannot be checked at compile
   time); the modes were lost at a fifth merge and are restored here; `test_x11_edscroll` still fails.

| File | Workstream |
|---|---|
| `R17-01-D1-D4-FIXED.md` | WS1 |
| `R17-02-CRASH-KINDS-FIXED.md` | WS2 |
| `R17-03-FORMATTER.md` | WS3 |
| `R17-04-PROOFS-AND-OPEN.md` | WS4, and what is open |
| `evidence-r17/` | the fuzz runs, the formatter's verification, the build report, hashes |

---

## Index — ROUND-15 delivery (2026-10-20, against main `9bff1dd6`, v216)

**Code is on branch `claude/round-15`, draft PR #52.** It adds four tools and restores the binaries' mode.
**No compiler, library or golden file changes.** On `main` only this folder changes, in a documentation-only
commit.

**Read first:**

1. **WS1, the compiler fuzzer** (R15-01).
   - **Seed 15, 20,000 random valid programs: all agree with the reference.** 51,088 of the called
     functions had 20 or more variables.
   - **It can see F1:** the pre-fix compiler fails 294 of 300.
   - **Before that run I found three defects and one disagreement with the documentation:**
     - **D1: unary `!` is silently ignored.**
     - **D2, D3: the compiler crashes on two valid program shapes,** both in an `anya` block. **They have
       one cause: a stale `rcx`.** The one-line fix is verified: suite 205/4 and proofs 217 unchanged; 9
       crashes become 0. **It is a patch file, not on the branch:** say if you want it landed.
     - **D4: the precedence is not the documented table** (28 of 246 pairs). Which one is right is a
       decision for the owner.
2. **WS2, the robustness fuzzer** (R15-02). **107 crashes in 50,171 hostile inputs, in six kinds; no
   hangs.** Each kind has a file.
   - **R1–R3:** `yoj`, a parameter list or a `rachana` cut off by the end of the file.
   - **R4:** `anya yadi` after `anya`.
   - **R5:** an expression left of `=`.
   - **R6:** about 19,000 levels of nesting.
   - **Also:** silent wrong answers from an integer literal past 64 bits, and a 64 KiB source cap that
     gives a misleading error.
3. **WS3, the 303 proofs** (R15-03).
   - **None is decoration.**
   - **4,993 of 5,944 bug-shaped mutants killed** (84%).
   - **1 WEAK** (`chakravala`), **60 PARTIAL**, 105 STRONG, 137 COMPLETE.
   - **15 surviving mutants have a witness on a valid input.** Most are in `madhava`'s argument reduction.
   - **818 survivors are undecided.** They are in list, string and record functions.
4. **Not new, again:** the R14 merge uploaded the binaries one at a time, and **they are 100644 on main once
   more.** This branch restores them. **Please merge it with `git merge` or a cherry-pick.**

| File | Workstream |
|---|---|
| `R15-01-COMPILER-FUZZER.md` | WS1 |
| `R15-02-ROBUSTNESS-FUZZER.md` | WS2 |
| `R15-03-PROOF-STRENGTH.md` | WS3 |
| `evidence-r15/valid/` | D1–D4 as files, the D2/D3 fix, the 20,000 run, the precedence check |
| `evidence-r15/robust/` | R1–R6 as files, the run summaries, every reduced crash |
| `evidence-r15/proofs/` | the per-function score and ranking, every witness, the 30-survivor sample |

---

## Index — ROUND-14 delivery (2026-10-20, against main `a82968d1`, v212)

**Code is on branch `claude/round-14`, draft PR #49, commit `b059afc1`.** On `main` only this folder
changes, in a documentation-only commit.

**Read first:**

1. **The installer is rebuilt** (R14-01).
   - **The payload (`payload.zip`) is `d267a876aed52682c41534fd0bd9ced9e90087468520c9775c5c6f8f6ffb7df5`.**
     Its `bin/sutram.exe` is the v208 compiler, the same file as the repo's `win/sutram.exe`. **The old one was
     v160.**
   - **The setup is `7c4158e1…`.** It reproduces on Linux (`--check` REPRODUCED), and its self-test passes
     under Wine and catches one flipped byte.
   - **Under Wine, an installed copy reports v208** (with the R6 harness build; the real setup stops at the
     shortcut step under Wine, as in R6).
   - **A correction: this session has no Windows machine.** R3's ran on one linked to that session. **Windows
     is NOT-RUN. The owner can run `tools/accept-windows.ps1`.**
   - **The binaries' mode was lost at the R13 merge;** PR #49 restores it. **Please merge with `git merge`
     or a cherry-pick.**
2. **The R5 question, ready for the owner** (R14-02): English or Sanskrit for the Windows IDE's menus. One
   word answers it.
3. **The Gujarati corrections: none arrived** (R14-03). The steps are ready. The sheet's Default lines are
   stale after R13; the Gujarati is not.
4. **What is open** (R14-04). New: the setup goes stale with each `docs/` change; PR #47 also changes the
   installer build; one X11 test deadlocks.

| File | Workstream |
|---|---|
| `R14-01-INSTALLER.md` | WS1 |
| `R14-02-R5-QUESTION.md` | WS2 |
| `R14-03-GUJARATI.md` | WS3 |
| `R14-04-WHAT-IS-OPEN.md` | WS4 |
| `evidence-r14/` | hashes, the build report, both Wine acceptance runs |

---

## Index — ROUND-13 delivery (2026-10-20, against main `465c202f`, v207)

**Code is on branch `claude/round-13`, draft PR #48, commit `8dfd24d5`.** On `main` only this folder
changes, in a documentation-only commit.

**Read first:**

1. **A fresh clone runs the tests** (R13-01).
   - The three Linux binaries are 100755 again.
   - **A clone from GitHub, with nothing built: suite 205/4.**
   - With the mode removed by hand, the suite still passes and prints a NOTE.
   - **A new gate, "committed modes",** fails when a merge drops the mode. It has been lost at three
     merges.
2. **`--version` prints v208,** and a new gate, "version string", fails when it drifts from the
   CHANGELOG. The packs take the version from the default now.
3. **The default is Sanskrit grammar** (R13-02).
   - **I did it now, not after the Sanskrit review.** The owner uses the default every day, and a later
     correction touches the same 42 lines.
   - **What moved:** 17 goldens, 9 default pack goldens, 3 R70 expectations, 4 tests and tools, 10 docs.
     Each moved only by the message text, as R12-02 predicted.
4. **No English in the Linux IDEs** (R13-03).
   - **Still English:** the Windows IDE's menus and buttons, by the owner's R5 decision.
   - **Does R5 still stand?**
5. **Gujarati corrections: none have arrived** (R13-04). Nothing was changed, and the steps are ready.

| File | Workstream | One line |
|---|---|---|
| `R13-01-FRESH-CHECKOUT.md` | **WS1** | The mode, how it is set, the two guards, the fresh-clone proof; the version and its gate. |
| `R13-02-SANSKRIT-DEFAULT.md` | WS2 | Why now; the 42 (+2) messages; what moved, checked; the checks. |
| `R13-03-LINUX-IDES.md` | WS3 | Every English string replaced, both IDEs; what remains; the R5 question. |
| `R13-04-GUJARATI.md` | WS4 | None arrived; what I will do and report when they do. |
| `R13-05-WHAT-IS-OPEN.md` | WS5 | 4 done, 10 still open, 3 new. |
| `evidence-r13/` | all | gates, the fresh clone from GitHub, the moved goldens word by word, the Linux IDE diff, the Windows compiler and IDE under Wine |

**Gates on the branch:**

- **`gates.sh`, Linux:** PASS 12 / FAIL 1 / NOT-RUN 1
  - FAIL: the X11 `edscroll` timeout, which fails in this environment before and after the change
  - NOT-RUN: Windows
  - The two new gates, "version string" and "committed modes", pass.
- **Linux:**
  - R70 6/6
  - `tests/r70` OK
  - SOURCE_PINS_CHECKED
  - every unit-test directory as before
- **Wine 9.0:** the Windows compiler's `--version` and the new defaults

**Not verified:** Windows, and the wording, which still needs a native speaker.

---

## Index — ROUND-12 delivery (2026-10-20, against main `068afb26`, v204)

**Documentation only:** no code changed, so there is no branch and no PR. This folder changes on `main`.

**Read first:**

1. **The wording of all eleven message sets is UNVERIFIED.** No native speaker has read them. The R11
   checks prove the form, not the wording.
2. **The review sheets** (R12-01, `review-r12/`):
   - one file per pack, all 128 messages, each shown as printed, with its meaning and my doubts
   - an empty line for the correction
   - **1,408 messages: 3 LIKELY WRONG, 169 UNSURE, 1,236 DRAFT.** DRAFT means "no specific doubt",
     not "correct".
3. **The three to correct first:**
   - Sanskrit `msg_namespace_error`: wrong gender
   - Kannada `r7_msg_mod_missing2`: `ಕೋಶ` means both "folder" and the `kosh` keyword
   - Punjabi `msg_shell_bye`: a religious greeting, for the owner to decide
4. **The two decisions, each answerable in one line** (R12-02):
   - **The default's grammar:** my R11 count was wrong. **42 messages,** not ~15, use Hindi grammar.
     Suggested: Sanskrit grammar, after the Sanskrit review.
   - **The Linux IDEs:** the terminal IDE is English and the X11 GUI has English console lines.
     Suggested: remove the English now; let the terminal IDE follow the pack if needed. The X11 GUI
     cannot draw Indic script at all, so making it follow the pack is several rounds.
5. **Still open** (R12-03): 11 items, led by the setup rebuild and the `sutram_compiler` mode.
   **The mode breaks `run_tests.py` on a fresh checkout,** measured.

| File | Workstream | One line |
|---|---|---|
| `R12-01-REVIEW-SHEETS.md` | **WS1** | What a sheet holds, how to return it, the counts per pack, the three LIKELY WRONG, the doubts that run through every pack. |
| `review-r12/<pack>.md` | WS1 | The eleven review sheets. |
| `R12-02-TWO-DECISIONS.md` | WS2 | My correction (42, not ~15); both decisions with options, measured costs and a one-line answer. |
| `R12-03-WHAT-IS-OPEN.md` | WS3 | 11 items still open, checked on main; the mode's effect, measured. |
| `evidence-r12/` | all | `make_review.py` (regenerates the sheets from `lang/*.sandesh`), `gloss.py`, `flags.py`, `summary.json`, `default-hindi-grammar.json` |

**Checks on main `068afb26`, Linux:**

- **PASS,** with the compiler made executable:
  - suite 205 / 4
  - pack messages OK
  - proof_lib 217
  - tests/r70 OK
- **FAIL, as checked out:** `run_tests.py` and the pack-messages test hit `PermissionError`, because of
  the mode.

**Not verified:** Windows, and the wording.

---

## Index — ROUND-11 delivery (2026-10-19, against main `d3325b13`, v201)

**Code is on branch `claude/round-11`, draft PR #46, commit `15fa8176`.** On `main` only this folder
changes, in a documentation-only commit.

**Read first:**

1. **The diagnostics follow the pack (option E), in all eleven packs** (R11-01).
   - **Every compiler message and the Windows IDE's status line and output messages** are in the
     selected pack's language: **128 strings × 11 packs = 1,408.**
   - **The default (no `--lang`)** is the romanised Sanskrit text, with its English words removed.
     `--lang sanskrit` is Devanagari Sanskrit.
   - **The identifiers stay:** `Sutram Error` and the `[E_CODE]` tags.
   - **No English** anywhere: not as a default, not as a fallback.
2. **Goldens:**
   - **13 moved,** only by the removed words and the pack text: 11 default, 1 Hindi, 1 Sanskrit (R70).
     **No accepted golden was re-recorded to pass a test.**
   - **132 new per-pack goldens** and a new gate, "pack messages".
3. **The translations are drafted by me and need a native speaker,** all eleven. The checks prove the
   form (identifiers, punctuation, script, no Latin prose), not the wording.
4. **Two decisions for you:**
   - should the romanised default use Sanskrit grammar too? About 15 messages use Hindi grammar today.
   - should the Linux IDEs follow the pack?
5. **Step 5 is closed: 303 of 303** (R11-02).
   - 7 new proofs, among them **page-edge canaries** for overruns of private scratch blocks
   - 26 written verdicts
   - nothing left as GAP, OVERRUN or REVIEW

| File | Workstream | One line |
|---|---|---|
| `R11-01-DIAGNOSTICS-IN-THE-PACK.md` | **WS1** | What changes with the pack, the counts per pack, the default's English removed, the grammar question, the review needed, how it works, the checks. |
| `R11-02-LIBRARY-GAP-LIST.md` | WS2 | 48 → 0 open: 29 by proof, 14 by argument, 5 by both; the canary technique; every argument listed. |
| `R11-03-WHAT-IS-OPEN.md` | WS3 | 8 items still open from R10 (setup rebuild, `v182`, the R8-02 checks, the typing extensions, the stdlib page, the mode, the gutter, old PRs) and 7 new ones. |
| `evidence-r11/` | all | `sandesh/` (counts, check, samples in every pack), `wine/` (the compiler and five IDE screenshots), `gap-list/`, `logs/` (gates, fresh clone, moved goldens, sizes) |

**Gates on the branch:**

- **Linux, fresh clone:**
  - suite **205 / 4**
  - proof_lib **217**
  - proof_props 86
  - pack messages OK
  - translit 24,761 / 0
  - tests/gui 35
  - R70 6/6
  - tests/r70 OK
  - SOURCE_PINS_CHECKED
- **`gates.sh`:** PASS 10 / FAIL 1 / NOT-RUN 1
  - FAIL: the pre-existing X11 `edscroll` timeout
  - NOT-RUN: Windows
- **Wine 9.0:**
  - the Windows compiler in the default, Sanskrit, Hindi and Tamil
  - the IDE in Hindi, Tamil, Core, and Sanskrit by Auto

**Not verified:** Windows. **Not touched:** `Sutram-Setup.exe` (ChatGPT's). It must be rebuilt after the
merge.

---

## Index — ROUND-10 delivery (2026-10-19, against main `2e875ea7`, v195)

**Code is on branch `claude/round-10`, draft PR #45.** Two commits:

- `870aa8aa`: the F1 fix
- `c9d24ed2`: Step 5

On `main` only this folder changes, in a documentation-only commit.

**Read first:**

1. **F1 is fixed** (R10-01).
   - **Root cause:** every stack variable's `rbp` offset was emitted as a one-byte displacement, so slots
     below `rbp-128` wrapped above the frame, onto the caller's saved values and the return address.
   - **The fix:** one helper chooses a 1- or 4-byte displacement by range, at all 15 sites. No
     restructuring, and programs whose slots fit in a byte compile to the same bytes.
2. **The threshold is pinned, and it is one bug on both platforms.**
   - **v191, a called function with n locals,** on Linux and with the Windows compiler under Wine, with
     identical numbers:
     - correct to 26 locals
     - wrong values at 27–31 (the caller's variables change)
     - crash from 32 on (the 34th variable hits the return address)
   - **Not stack size:** the boundary is the same on both platforms, to the variable.
   - **Why your Linux run crashed at 38 and the owner's at 34:** you tested 30 and then 38 on Linux. 34
     crashes on Linux too.
   - **With the fix,** every n from 14 to 220 is correct on both, and so are 250 variables.
3. **The tests:**
   - `examples/237_many_variables.sm` uses every kind of variable past slot 40. It fails on v191 and passes
     here.
   - The R8 workarounds are removed from two proofs, with their goldens unchanged.
   - **123 tree programs compile differently (all through deep-slot functions); every golden is unchanged.**
4. **Step 5:** 255 of 303 closed (R9: 235), 48 open (R10-02).

| File | Workstream | One line |
|---|---|---|
| `R10-01-F1-FIX.md` | **WS1** | The root cause in two sentences, the threshold table (Linux and Wine), why it is one bug, the fix, the tests, the tree measurement, the gates. |
| `R10-02-LIBRARY-GAP-LIST.md` | WS2 | 20 more closed, by proof or by written argument; the 48 still open, and why. |
| `R10-03-DIAGNOSTICS-DECISION.md` | WS3 | D now, E as translations arrive, with the costs. Nothing changed. |
| `R10-04-TRANSLITERATION-COVERAGE.md` | WS4 | What the typing mode does not cover (strings, comments, pasted text, digits, Hindi spelling, nukta, the Linux IDE), with a cost for each. Nothing extended. |
| `R10-05-INTERFACE.md` | WS5 | Nothing in `windows/` touched; two binaries rebuilt; the setup is ChatGPT's to rebuild. Two small things on main. |
| `evidence-r10/` | all | `F1/` (`sweep.py`, the new golden), `logs/` (the sweeps on Linux and Wine, 250 variables, the R9 files on the fix, the tree audit, gates, a fresh clone), `gap-list/` |

**Gates on the branch:**

- **Linux, fresh clone:** suite **205 / 4** · proof_lib **210** · proof_props 86 · translit 24,761 / 0 ·
  tests/gui 35 · R70 6/6 · SOURCE_PINS_CHECKED
- **`gates.sh`:** PASS 9 / FAIL 1 / NOT-RUN 1
  - FAIL: the pre-existing X11 `edscroll` timeout
  - NOT-RUN: Windows
- **Wine 9.0:** the F1 sweep with `win/sutram.exe`

**Not verified:** Windows.

---

## Index — ROUND-09 delivery (2026-10-19, against main `c20e55a7`, v188)

**The diagnostics decision (WS4), first, as asked.** It is still the owner's call and nothing has changed.
The compiler's errors and the IDE's status words are Sanskrit; the rest of the interface is English.
**Recommended: D now, E as translations arrive.**

- **D:** a `--sandesh en` switch, with the default unchanged; the English IDE passes it.
  - Cost: one message table and 90 lookups.
  - About 10 new goldens; no existing golden, R70 case or doc changes.
  - 1–2 rounds.
- **E:** the `--lang` pack's language for every message.
  - Cost: D plus 900 translations.
- **B** (English only) would re-record 41 goldens, 4 R70 cases, 16 tool files and 18 docs.

**New:** the IDE has one more status word (`lipi`, for the typing mode), and the compiler one more message
(the `guna` capacity). Both would go into D's table (R9-04).

**Code is on branch `claude/round-09`, draft PR #44.** Seven commits, separable (see the PR). On `main`
only this folder changes, in a documentation-only commit.

**Read first:**

1. **F1 is reproduced, as files** (R9-01).
   - `evidence-r9/F1/run-f1.sh` prints expected against actual: `10 28 29 29` for `10 20 30 29`,
     `151 38 39 39 40` for `55 6 7 39 40`, a segfault for `7`.
   - It reproduces on main's committed compiler, a fresh build, and `win/sutram.exe` under Wine.
   - **My R8 description was imprecise, and that is why your four attempts were correct.** The trigger is a
     *called* function with 20+ variables, or any function with 38+. Your attempts used a big `mukhya` or a
     big caller. **Not fixed: yours to schedule.**
2. **F2–F6 are fixed,** each with a file that fails on v188 (R9-03).
   - **F2:** `nirmmita` returned `-errno`, so every "0 on failure" check missed it.
   - **F3:** `guna` re-evaluated its value per case.
   - **F4–F6:** a comment, a missing `yoj`, the binaries' mode.
3. **Main's locks and binaries had drifted** (R9-03).
   - The compiler pin was still R7's, so `r69_build --check-only` refused on main.
   - `win/sutram.exe`, which the installer packages, was still the R7 build.
   - The branch re-pins and rebuilds everything except `Sutram-Setup.exe`, which is ChatGPT's. **Rebuild it
     after this merges.**
4. **The IDE renders all eleven packs and types them from an English keyboard** (R9-05, R9-06).
   - Indic runs use Nirmala UI, and Latin stays Consolas.
   - The Language menu has all eleven packs, and Run passes `--lang`.
   - Ctrl+T converts `mukhya` → मुख्य, or the pack's own keyword (`vitti` → चर in Hindi), and spells other
     words phonetically.
   - **Under Wine,** programs typed this way in sanskrit, hindi, tamil and gujarati compiled and printed
     `5 ok`.
   - **Windows: not run.**
5. **Step 5:** 235 of 303 functions closed (R8: 212), 68 open (R9-02).

| File | Workstream | One line |
|---|---|---|
| `R9-01-F1-REPRODUCTION.md` | **WS1** | The five files, the command, the pasted output on three compilers. The precise rule, why your attempts missed it, and the fix to schedule. |
| `R9-02-LIBRARY-GAP-LIST.md` | WS2 | 23 more closed: by guard-cell proofs or by written argument. 68 open, listed. A new NO-CONTRACT verdict for undocumented returns. |
| `R9-03-F2-TO-F6.md` | WS3 | Each defect as a file, before and after, from main's own checkout. The fixes; the stale pin and binaries found on the way. All the gates. |
| `R9-04-DIAGNOSTICS-DECISION.md` | WS4 | The paragraph above. Nothing changed. |
| `R9-05-IDE-FONT.md` | WS5 | Nirmala UI for Indic runs, checked at startup. The eleven-pack render under Wine (v188: boxes; branch: letters). The gutter drift, not fixed, and why. |
| `R9-06-TRANSLITERATION.md` | WS6 | What the owner types, the phonetic scheme, the engine tested against the reference (24,761 cases), the typing runs under Wine, and what is not covered. |
| `R9-07-INSTALLER-FONT-CHECK.md` | WS7 | `check-script-fonts.ps1`, offered to ChatGPT; the installer is not edited. Under Wine: exit 3 without the font, exit 0 with it. |
| `R9-08-INTERFACE.md` | WS8 | Every path touched in `windows/`, and the one string table for the main window. |
| `evidence-r9/` | all | `F1/` (the reproductions and their runner), `F2-F6/`, `wine/` (screenshots and the typed files), `gap-list/`, `logs/` (raw output of every check, including a fresh clone of the branch), `eleven.sm` |

**Gates on the branch:**

- **Linux, fresh clone:** suite **204 / 4** · proof_lib **209** · proof_props 86 · translit 24,761 / 0 differ
  · tests/gui 35 · R70 6/6 · `r69_build` SOURCE_PINS_CHECKED
- **`gates.sh`:** PASS 9 / FAIL 1 / NOT-RUN 1
  - FAIL: the X11 `edscroll` timeout, pre-existing in this container
  - NOT-RUN: Windows
- **Wine 9.0:** the font render, the typing runs, F2/F3 with `win/sutram.exe`, the font check

**Not verified:** Windows. Every Windows-side result here is Wine.

**Still open, briefly:**

- **F1's fix.**
- **The R8-02 checks:** errors for assigning a `sutra`, for a misplaced `krama`, for a duplicate `bhavana`.
- **The diagnostics decision.**
- **The `--version` string** still says `v182` on v188.
- **The setup rebuild** after this merges.
- **The gutter drift** on Indic lines (R9-05).
- **Your 40-variable file from WS1,** to check against F1.

---

## Index — ROUND-08 delivery (2026-10-19, against main `221eee96`, v183)

**The diagnostics decision (WS3), first, as asked.** It is still the owner's call and nothing has changed. The
question is the language of the compiler's errors and of the IDE's 22 status words; the rest of the IDE is
already English. **Recommended: D now, E as translations arrive.**

- **D:** a `--sandesh en` switch, with the default unchanged; the English IDE passes it.
  - Cost: one message table and 90 lookups.
  - No existing golden or doc changes.
  - About 1–2 rounds.
- **E:** the `--lang` pack's language for every message.
  - Cost: D plus 900 translations.

**New:** none of R7-02's numbers moved. If the R8-02 checks are approved, their 3 new messages should go
straight into D's table, so deciding D first saves writing them twice (R8-03).

**Code is on branch `claude/round-08`, draft PR #42.** One commit, `dac2c1ef`: tools and tests only. On `main`
only this folder changes, in a documentation-only commit.

**Read first:**

1. **The gap list is in R8-01 §1.**
   - Every one of the 303 functions now has a proof that fails when its whole body is broken. Before: 1 had
     none, 1 was called but never checked.
   - **That measure is too weak**, so the list uses 1,119 mutants shaped like real bugs: off-by-one results
     and moved boundaries.
   - **212 functions are closed; 91 are open**, listed module by module. This round closed 43, and killed
     781 → 862 of the mutants.
2. **F1 — a function with more than 21 variables silently computes wrong values.** This is on main, in both
   the Linux and Windows compilers (Windows only under Wine).
   - Stack slots past the 16th are encoded with a one-byte displacement and land in the caller's frame.
   - `chakravala` corrupts its caller. `1000 + varna_bhed(…)` gives 5. `mukhya` with 40 variables adds 1..10
     to 151.
   - **I recommend fixing it first next round** (R8-01 §2).
3. **Five smaller findings (F2–F6):**
   - `nirmmita` failure is `-errno`, so "0 on failure" checks never fire
   - `guna` re-evaluates its value per case
   - a wrong comment
   - a missing `yoj`
   - non-executable committed binaries
4. **14 new proofs.** Each expectation was computed independently, in Python, and agrees with the compiled
   run. They include models of the map, the list, the queue and split against Python's own types, and every
   Pell equation for n < 100.
5. **WS2:** the non-name cases are four other classes, not one. Recommended: three small errors in one step;
   typing documented, not built (R8-02).

| File | Workstream | One line |
|---|---|---|
| `R8-01-LIBRARY-GAP-LIST.md` | **WS1 / Step 5** | **The gap list first.** Then F1–F6, the contracts of the helpers and of the uncommented open functions, the 14 proofs, what is not proven and why, the tools, and the gates. |
| `R8-02-NON-NAME-SILENT-CASES.md` | WS2 | 7 cases stated plainly; a top-level `sutra` assignment is lost, not applied; `guna` re-evaluates (new). Four classes, not the decided one. Cost per fix; recommendation. Nothing implemented. |
| `R8-03-DIAGNOSTICS-DECISION.md` | WS3 | The same paragraph as above, with the R7-02 option table. Nothing changed. |
| `R8-04-WHAT-I-NEED.md` | WS4 | 4 answered, not re-sent. 14 open, led by F1. Housekeeping: PRs #31–#33, #35, #38, #40. |
| `evidence-r8/` | all | `lib-gap-list.md/.json` (every surviving mutant, with line, verdict and reason), `lib-gap-list-before.*`, the raw tool output, `expectations/` (the Python that computed every golden), `probes/` (F1, F2, WS2), `logs/` |

**Gates on the branch (Linux):**

- proof_lib **205 / 205** · proof_props 86 / 86 · suite **203 / 4** (unchanged)
- `gates.sh`: PASS 9 / FAIL 1 / NOT-RUN 1
  - FAIL: the X11 `edscroll` timeout, pre-existing in this container
  - NOT-RUN: Windows

**Not verified:** Windows. F1 was reproduced with the committed `win/sutram.exe` **under Wine 9.0 only**.

---

## Index — ROUND-07 delivery (2026-10-19, against main `05d8bdc8` v180)

**Code is on branch `claude/round-07` — draft PR #40.** Commits:

| Commit | What |
|---|---|
| `5bd1acdf` | WS1: compiler, 9 goldens, re-pin |
| `bedf2705` | three `proof_props` generator bugs the new checks found |
| `3ef7d33f` | WS3: every committed binary rebuilt; `tools/cross_build_windows.py` |

On `main` only this folder changes, in a documentation-only commit.

**Read first:**

1. **Every name-resolution path now errors on a wrong name.** A 50-probe inventory covered variables,
   assignment targets, blocks, loops, parameters, constants, fields, arrays, functions, arity, modules,
   aliases and builtins (R7-01).
   - Nine more silent cases are now errors, including both owner decisions.
   - **Block scope was measured first with the real compiler: 0 programs rely on the old behaviour.**
2. **Block scope exposed a codegen bug already on main.** `vitti x = 1 … vitti x = 2` kept 1, because the
   second slot was never read. Re-declaring a visible name is now an error, and re-declaring after its
   block reuses the slot.
3. **The checks found real bugs in the tests:** a 5-argument call to a 6-parameter function, and a name
   declared 12 times by a stale loop index (`tools/proof_props.py`).
4. **The committed binaries now match the source and can be reproduced on Linux** (`--check` → REPRODUCED).
   Hashes are in R7-03.
5. **Merge order:** ChatGPT's R75 prepare step pins the v180 compiler blob that this branch changes
   (R7-04 §1).

| File | Workstream | One line |
|---|---|---|
| `R7-01-NAME-RESOLUTION.md` | WS1 / Step 1 | The inventory: 34 rows, v180 vs. the branch. The precise block-scope measurement, the codegen bug it exposed, the diagnostics, and the non-name silent cases left for a decision. Suite **203 / 4**; all 9 new goldens fail on v180. |
| `R7-02-DIAGNOSTICS-DECISION.md` | WS2 / Step 2 | The decision table, counted from the tree: 90 + 22 strings, 41 goldens, 4 R70 cases, 16 tool files, 18 docs (about 255 lines). Five options; recommended: **D now, E as translations arrive**. Not changed. |
| `R7-03-REBUILT-BINARIES.md` | WS3 | All seven committed binaries rebuilt, with SHA-256 for each. Reproducible Windows cross-build. Their log: under Wine, committed 9/1/5 (the Wine-only `IconLocation` issue) and harness 12/0/3. |
| `R7-04-WHAT-I-NEED.md` | WS4 | 2 answered. 11 still open, led by the R75 merge order. 3 small new decisions (the words, loop-variable scope, the non-name cases). |
| `evidence-r7/` | all | `probes/` (50 programs), `logs/` (probe results on v180 and on the branch, the per-change tree audit, gates, the cross-build report), `wine-committed/` and `wine-harness/` (gate logs, screenshots, checker output) |

**Gates on the branch (Linux):**

- `gates.sh`: PASS 8 / FAIL 1 / NOT-RUN 1
  - suite 203 / 4
  - FAIL: the X11 `edscroll` timeout, pre-existing in this container
- proof_lib 191 · proof_props 86 · packs 33 · codegen 12 · R70 6/6
- `r69_build` SOURCE_PINS_CHECKED · `tests/*` OK except `r69` 2 FAIL (ChatGPT's scripts)

**Not verified:** Windows. The Windows gate ran under Wine only.

---

## Index — ROUND-06 delivery (2026-10-19, against main `04aa7bb3` v176)

**Code is on branch `claude/round-06` — draft PR #38.** One commit, `452aa523`:

- `tools/accept-windows.ps1`
- `tools/check_accept_windows_log.py`
- `tests/windows_accept/`
- a `TEST-ME.md` section

On `main` only this folder changes, in a documentation-only commit. **No compiler, IDE or installer source
changed this round.**

**Read first: not one check ran on Windows.** The gate script ran three times under **Wine 9.0 on
Linux**:

- **A:** main's committed binaries
- **B:** a fresh v176 build
- **C:** a harness build with two Wine-only script lines

Each log is labelled Wine. The elevation checks are NOT-RUN, because Wine has no UAC. **The gate becomes
acceptance when the owner runs one command on Windows** and returns the folder (`TEST-ME.md`).

**Two facts the runs showed:**

1. **The Windows binaries committed on main are the ROUND-03 build.** Their hashes match the tree, and the
   gate fails them on English labels. Main also commits no `win\sutram.exe`.
2. **A failed install leaves a half-install that a retry refuses.** That is ChatGPT's code; reported.

| File | Workstream | One line |
|---|---|---|
| `R6-01-WINDOWS-GATE.md` | WS1 | What the script records, check by check: binary SHA-256s (repo and installed), the Windows build, the elevation tokens, PASS / FAIL / NOT-RUN JSON with commands and output. How Sarvam checks a returned log. The three Wine runs (A 5/4/5, B 9/1/5, C **12/0/3**), what each proves, and what nothing here proves. |
| `R6-02-WRONG-NAME-DECISIONS.md` | WS2 | Case 1 (`totl = 10` silently declares) **is the same class**: 0 programs in 530 rely on it. Recommend: error. Case 2 (a block `vitti` is visible after the block) **is a scoping rule, not an undefined name**. Recommend: block scope, after a precise measurement. Nothing implemented. |
| `R6-03-DIAGNOSTICS-LANGUAGE.md` | WS3 | The inconsistency, layer by layer. v175's "no Sanskrit UI string remains" is not so: the status line and the 10 IDE output messages are Sanskrit. Five options (keep / all English / both / selectable / follow the pack), with costs counted from the tree. Not changed. |
| `R6-04-WHAT-I-NEED.md` | WS4 | Four R5-03 items answered or moved, not re-sent. Eight still open. Three new: commit Windows binaries only with their log; ChatGPT's install rollback and uninstall confirmation; the owner's first Windows run. |
| `evidence-r6/` | all | `A-*/`, `B-*/`, `C-*/` (`accept-windows.json`, console, screenshots, install/uninstall logs, `checker.txt`); `notes/` (harness notes, the retry and existing-install runs); the harness scripts; `logs/` (gates on the branch) |

**Gates on the branch (Linux):**

- `gates.sh`: PASS 8 / FAIL 1 / NOT-RUN 1
  - suite 194 / 4
  - FAIL: the X11 `edscroll` timeout, pre-existing in this container
- `tests/windows_accept` 7 · `gui` 31 · `r66` 22 · `r67` 17 · `r68` 19 · `r72` 3 · `module_graph` 18 · `ci` 9 OK
- `r69` 2 FAIL (ChatGPT's scripts)
- `r69_build` SOURCE_PINS_CHECKED · workflow triggers OK

---

## Index — ROUND-05 delivery (2026-10-19, against main `c504e3c6` v173)

**Code is on branch `claude/round-05` — draft PR #35.** Commits:

| Commit | What |
|---|---|
| `70b02e8f` | English labels |
| `a1340416` | IDE keyword colours |
| `79928d90` | Installer text |
| `f1025a72` | Index and field names |
| `a7e48882` | R56 doc sample |

On `main` only this folder changes, in a documentation-only commit. **Every screenshot is from Wine 9.0 on
Linux, not Windows.**

**Read first:**

1. **The owner's instruction is done.** The menus are `File Edit Shell Language Help`, the buttons are
   `Run Open Save "Load example" Send "Clear shell"`, and the installer is back to its English text. The
   words follow the 13 Oct build where it had them.
   - The file-list panel was **not removed.** It is in the code and in every screenshot (R5-01 §3).
2. **Three more wrong-name cases compiled silently after R4; they are now errors.**
   - `p.w` for an undeclared field read `p.x`.
   - Field names longer than 8 bytes were compared on their first 8 bytes only.
   - `a[i]` with an undeclared `a` crashed at run time.
   - Two remaining cases are language decisions (R5-04 §2).
3. **ChatGPT's ROUND-73 WS1 blocker is already resolved on v173** by my R4 re-pin, and this branch re-pins
   again. Please sequence the merges (R5-03 §1).

| File | Workstream | One line |
|---|---|---|
| `R5-01-ENGLISH-INTERFACE.md` | Part 2 | Menus, buttons, find label, Help dialogs and installer in English, with a word-by-word table and its source. Two things are kept in Sanskrit for you to confirm: the status line and the output messages. The file-list panel question is answered. A separate commit makes the editor colour the current keywords (`vitti`, `chakra`, `prati` … were drawn plain). |
| `R5-02-STAGE-FIX-AND-TESTS.md` | WS2 | The R4 failing-stage fix still works with the English labels (editor and shell, under Wine). Every gate with PASS / FAIL / NOT-RUN **and its environment**. |
| `R5-03-WHAT-I-NEED.md` | WS3 | v173 made 3 asks moot and they are not re-sent. 11 are open, led by the pin coordination with ChatGPT, the diagnostics language now that the interface is English, and two silent-wrong-name language decisions. |
| `R5-04-WRONG-NAMES.md` | WS4 | All 510 `.sm` files and 70 doc samples compiled before and after: **no program changed.** One doc sample fixed (`pratiyati`). The stdlib reference page uses a non-keyword `samapt` in all 26 samples; reported, not rewritten. The compiler now rejects undeclared array/field bases and unknown fields, and compares field names in full. New goldens 224, 225 and 226. |
| `evidence-r5/` | all | `screens/` (Wine), `logs/` (gates, unittest folders, Wine compiler run), `probes/` (the wrong-name probe programs) |

**Gates on the branch:**

- suite **194 PASS / 4 NO-EXPECTATION**
- `gates.sh`: PASS 8 / FAIL 1 / NOT-RUN 1
  - FAIL: the X11 `edscroll` timeout. The X11 GUI is byte-identical to main's and fails the same way here,
    so this is pre-existing in my container.
  - NOT-RUN: Windows.
- `tests/gui` 31 · `r66` 22 · `r67` 17 · `r68` 19 · `module_graph` 18 · `ci` 9 · `r72` 3 OK
- `r69` 2 FAIL (ChatGPT's scripts)
- R70 6/6 · `r69_build` SOURCE_PINS_CHECKED · workflow triggers OK

**Not verified:**

- Nothing ran on Windows. The Windows tests are NOT-RUN.
- No binary is committed. Rebuild `sutram_compiler` at merge.

---

## Index — ROUND-04 delivery (2026-10-19, against main `6ebe973f` v172)

**Code is on branch `claude/round-04` — draft PR #33** (commits: `33374793` WS1 · `83af6270` WS2 · `2ee5c5ac` WS3),
kept off `main` per `AGENTS.md`. On `main` only this folder changes (documentation-only commit).

**Read first:** the wizard's focus defect is worse than R3 said. One `WM_COMMAND` carrying
`BN_SETFOCUS`, with no click, **passed the licence page while "decline" was selected and Next was disabled**.
Five such messages reached the "installed successfully" page (R4-03 §1). It is ChatGPT's code, so it is
reported and not fixed, as the brief asks.

| File | Workstream | One line |
|---|---|---|
| `R4-01-UNDEFINED-NAME.md` | WS1 | **An undefined name is now a compile error**, in Sanskrit, at its own line and column. Old keywords get a hint naming the new one (`'pratiyati' purana kunjishabd …; navin: 'prati'`). Done in the parser, with no restructuring and no codegen change. No program in the tree relied on read-as-0. Suite 191 PASS / 4 NO-EXPECTATION, new goldens 222 and 223 (both FAIL on v172). Locks re-pinned, including five `win/*` inputs v171 left stale. |
| `R4-02-WINDOWS-SANSKRIT.md` | WS2 | IDE buttons `chal khol sanchay "udaharan khol" presh phal_rikta`; 49 installer strings romanised, licence and paths untouched. Before/after screenshots under **Wine** (not Windows). Also fixed my own IDE bug: the IDE named the wrong failing stage (compile vs run). |
| `R4-03-WIZARD-AND-R69.md` | WS3 | Wizard: focus-advance, licence mojibake and `%TEMP%` leftovers, all reproduced, all ChatGPT's, all reported. `tests/r69`: 2 FAIL, ChatGPT's scripts, reported; the old ERROR is gone. `tests/r67`: 2 FAIL caused by my R73, **fixed, 17/17** (two test assertions updated to R73's accepted behaviour, reasons stated). Every gate with PASS / FAIL / NOT-RUN. |
| `R4-04-WHAT-I-NEED.md` | WS4 | Six earlier asks answered by v169–v172, not re-sent. Nine still open: **re-pin at acceptance** (third miss), the words (one consolidated list plus two keyword collisions), Devanagari spelling, diagnostics shape, hint and signatures, `gates.sh` counts, version number, and two new ones (bare assignment, temp file names in IDE diagnostics). |
| `evidence-r4/` | all | `screens/` (Wine captures), `logs/` (gates, suite, WS1 before/after, Wine compiler run, unittest folders), `repro/sendfocus.asm` |

**Gates on the branch:**
- suite **191 PASS / 4 NO-EXPECTATION**
- `gates.sh`: PASS 8 / FAIL 1 / NOT-RUN 1
  - FAIL: X11 `test_x11_edscroll` times out. It is pre-existing: the X11 GUI binary is byte-identical to
    main's, which fails the same way.
  - NOT-RUN: Windows.
- `tests/r66` 22, `r67` **17**, `r68` 19, `module_graph` 18, `gui` 28, `ci` 9 OK · `r69` 2 FAIL (ChatGPT's)
- R70 6/6 · `r69_build` SOURCE_PINS_CHECKED · workflow triggers OK
- The Windows compiler, GUI and wizard all cross-build.

**Not verified:**
- Nothing was run on Windows. The Windows evidence this round is Wine 9.0 on Linux: layout, text, message
  handling and the compiler's output. It is not Windows acceptance.
- `tools/test_windows_*.py` are NOT-RUN.

---

## Index — ROUND-03 delivery (2026-10-19, against main `85d6c5f` v169)

**Code is on branch `claude/round-03` — draft PR #32** (four code commits: `2182583` WS1 · `decb0afe` WS2 · `6f13c93e`
docs · `494e1b21` WS4), kept off `main` per `AGENTS.md`. Nothing on `main` outside this folder was changed by me.

**Gates on the branch** (`sh tools/gates.sh`):
- suite **189 PASS / 4 NO-EXPECTATION** (188 + new golden `221_eof_location`)
- codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers 14/9/1 · stdlib PASS · module graph PASS
- X11 **17/18** — `test_x11_edscroll.py` times out identically on the v169 and `feef075` GUIs (pre-existing, not investigated)
- Windows NOT-RUN

**Also now passing on the branch:** R70 negative corpus **6/6, native_status PASS** · `r69_build.py`
accepts main · `tests/r66` 22 · `r67` 17 · `r68` 19 · `r69` 39 OK · 23 round tools exit 0.

**Read first — two findings bigger than the brief:**
1. **Two pre-v157 keywords miscompile silently.** `pratiyati` (old `return`) and `uddeshya` (old
   `continue`) compile with no error, because an undefined name reads as 0. `f(5)` returns **2** instead
   of 1, and the loop skips nothing. Verified by hand. Described, not fixed: it is a language decision
   (R3-04 §0).
2. **The X11 GUI has coloured no Latin keyword since 14 October.** The Devanagari rows ended `,0,0`,
   which `match_tab` reads as end-of-table, so v163's keyword update never took effect.
   `test_x11_colour.py` could not see it. **Fixed, and the test strengthened.** The new test fails on the
   old GUI and passes now (R3-04 §4).

| File | Workstream | One line |
|---|---|---|
| `R3-01-SOURCE-LOCKS.md` | WS1 | Five lock families, not two. **Re-pinned** the build-input and corpus contracts, each re-pinned only after the drift was verified: `r69_build` lock + its constant, the R70 corpus (fixtures changed by the rename only; expectations moved to the R2 strings), the r69 pair fixtures, the r66/r67 pack baselines (mapped through the rename table). **Retired** the R65/R66/R67/R68 staging tools: they can only ever apply a finished patch to a vanished blob, and r66's had `vardh` for the x86 `inc`. **Left alone** the R71 lock: an open ChatGPT review; re-pinning would claim a review nobody did. Also repaired 15 live helper tests that sat behind a broken C stub, and **fixed a regression of mine**: since R2, an unterminated string reported line **1:1** (EOF origin lookup). |
| `R3-02-ROUND-TOOLS.md` | WS2 | All 31 round tools **run**, not grepped, against the current and v166 compilers. 14 pass. **9 failed only on English text → repaired, each re-run to exit 0** (7 broken by my R2, 2 earlier). **9 are structurally dead → retired** (A/B against pre-v157 compilers, frozen hashes/counts, source-shape greps, fixtures never committed). The 8 round workflows fail by construction (each asserts `tests/expect/` unchanged since its round), so I **retired them for one manual `gates.yml`**. **Also corrects my own R2 "eleven tools" list**, which was a grep: 4 of 11 were right. |
| `R3-03-DOCS-AND-MESSAGES.md` | WS3 | Every doc quote of a compiler message, corrected from messages **actually triggered**. Includes the six books' transcripts, re-taken from the compiler with each book's own program; they showed a help line the compiler never prints. `LANGUAGE-REFERENCE.md` sample 007 compiles again. **ROUND-01 claims on v169:** not one audited doc had been edited since R1; 1 claim became true, 6 went newly stale. The branch makes 5 more true; the remaining stale numbers are listed, not changed. |
| `R3-04-HIDDEN-OLD-NAMES.md` | WS4 | 296 old names (264 functions derived from v156, not typed). **The `\n` class reaches nowhere else on main: 0 hits, with the detector proven on v167.** The same *kind* of miss reaches much further, so I list 16 boundaries: HTML spans (25 book blocks that did not compile — fixed), a NUL in a byte table (the GUI — fixed), printed code labels (4 examples — fixed), slash lists, wildcards, file headers, hex bytes, dict keys. Fixed where they are Sarvam's; reported with file:line where they are Muse's or ChatGPT's. |

**One rule I bent, stated so you can decide:** `AGENTS.md` says "preserve … existing frozen baselines".
`r57_codegen_baseline.py` is one, and I retired it with the R57 tools. Its frozen hash is of a fixture the
rename changed, so it can only fail. You asked for retire-or-repair calls in this brief, and the change
is on a review branch. If you would rather keep frozen baselines even when dead, restore that one file
with `git checkout 85d6c5f -- tools/r57_codegen_baseline.py`.

**Housekeeping:**
- `tools/gates.sh` rebuilds into the repo root, so every run leaves the tracked `sutram_compiler`
  modified, and rewrites `docs/sutram-stdlib.html` in a different order from the committed one. The
  committed `sutram_compiler` is mode 100644 (not executable). On main it matches a fresh build of
  main's `src/` except for one linker symbol (`__bss_start`); after this branch's compiler change it is
  stale. **I did not commit a rebuilt binary**, so please rebuild it at merge, as
  in R2.
- No `__pycache__` is committed this time (checked: `git diff --cached --name-only | grep -c pycache` → 0).
- Draft PR #31 (ROUND-02) is still open. Its content is on main, so it can be closed.

## What I need this round

1. **The §0 decision in R3-04**: an undefined-variable error (right, structural) or a narrow
   old-keyword guard (contained). Until then, any pre-v157 program using `pratiyati` or `uddeshya` gives
   wrong answers silently.
2. **The Devanagari-spelling decision** (R1-WS2 §3.2, still open). It is now the only rename leftover
   that no sweep can reach: the compiled-in aliases are hex bytes.
3. **Re-pin at acceptance.** The locks went stale because nobody re-pinned at v157 or at the R2 merge.
   `tools/r69_build.lock.json` now carries the rule in its `repinned` field. One line in your merge
   checklist would keep it true.
4. **Whether `gates.sh` should own the numbers in `PROJECT-MASTER.md` §6 and in README/OVERVIEW.** Most
   of the stale ROUND-01 claims are counts that drift every round (R3-03 §5).
5. From R2, still open: one diagnostics shape (stdout vs stderr; `file:L:C:` vs `pankti L:C`), the
   reserved-word hint, and one place for library signatures.

---

## Index — ROUND-03 delivery (2026-10-18, against main `e0e5031` v168) — Windows, owner-directed

**Code is on branch `claude/round-03-windows`** (commits: `a3032a9` ChatGPT's Windows delivery on
its base, `3512d34` its merge onto v168, `e95f727` manifest, `a39d2f9` the Sanskrit IDE,
`fdf409d` icons + startup, `6e6190c` these documents, `bae6657` sidebar icon + English buttons). Nothing on `main` outside this folder was changed by me. The owner asked
for this round directly, knowing ROUND-02 said *do not touch `windows/`*; R3-00 lists exactly what
was touched and why.

Gates on the branch, measured on Windows 11 build 26300 as a standard user: native goldens
**186 PASS / 3 NO_EXPECTATION / 2 SKIP** · GUI **30 / 30** · setup 7/7 · payload, preflight,
contract PASS · `tests/gui` 28 OK · **`tests/r69` 2 FAIL (merge) + 1 ERROR (already on main)** ·
Linux (WSL) suite **187 / 4** · codegen 12/12 · packs 33/33 · layers 14/9/1 · module_graph 18/18 ·
proof gates **NOT-RUN** (no NASM in WSL) · real install → run from Start Menu → uninstall: PASS.

| File | One line |
|---|---|
| **`R3-00-READ-FIRST-WINDOWS.md`** | why this round touches `windows/`, what exactly was touched, how to apply the patches and rebuild |
| `R3-01-DELIVERY-ACCEPTANCE.md` | ChatGPT's Windows delivery run for real: hashes, compiler, installer, install/uninstall as a standard user, merge onto v168 (four conflicts, how resolved), every gate with PASS / FAIL / NOT-RUN |
| `R3-02-SANSKRIT-IDE.md` | the IDE now: Sanskrit menus/status/messages (X11 IDE words; buttons stay English by the owner's choice), Unicode window, Tab / Shift+Tab / Enter / `}`, status line, unsaved guard, find, `bhasha` menu (`swayam` detects Devanagari → `--lang sanskrit`), icon as a PE resource; 14 new native checks; what was not tested |
| `R3-03-FINDINGS.md` | wizard advances on focus (installed itself under passive UI Automation), license page mojibake, `%TEMP%\STM*` left behind, reinstall refused after preserve, version 0.1.0 vs v160, r69 test gates, MAX_PATH in `install-core.ps1` |
| `R3-04-WHAT-I-NEED.md` | the `windows/` chain decision, confirmation of the new Sanskrit words, how `swayam` should tell hindi/marathi/sanskrit apart, a human Hindi-layout typing test |

---

## Index — ROUND-02 delivery (2026-10-18, against main `5eec849` v167)

**Code is on branch `claude/round-02` — draft PR #31** (three commits: `5dc77d5` WS1, `89d23e8` WS2/WS3,
`784779e` WS4), per `AGENTS.md` ("unapproved code changes in review branches/draft PRs"). Nothing on
`main` outside this folder was changed by me. Gates on the branch: suite **188 PASS / 4 NO-EXPECTATION**
(187 + one new golden) · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers
14/9/1 · **module_graph 18/18** · Windows target assembles and links (not executed).

| File | Workstream | One line |
|---|---|---|
| `R2-01-FOUR-DEFECTS.md` | WS1 | All four fixed and contained: 50 pack strings re-encoded (bytes before/after, new golden `220_hindi_parse_error` that fails on v166); missing input exits 1; `--check`/`--lang` in either order; normal-mode parse errors give the original file's line:col (origin map kept in every mode; module errors name the module). |
| `R2-02-CONSTANT-IDE-MODULE-GRAPH.md` | WS2 + WS3 | `r49_print_module_location` matches `yoj` (column `?` → real column, before/after shown); terminal IDE table current (PTY-verified); `tests/module_graph` **18/18** — the tests were stale, the model is fine. **v167's own fix of that file left seven `ayojan` after `\n`; its changelog's "pre-existing divergence in the reference model" is not correct.** Also: `gates.sh` reports the suite as FAIL on every run (exit-code false positive). |
| `R2-03-SANSKRIT-DIAGNOSTICS.md` | WS4 | 83 `db` lines translated (table of every before/after), `Sutram Error:` and `[E_…]` kept, 28 goldens re-recorded with exactly one line each. Consequences stated: one `tests/r68` lock-pin test newly fails (`r66_indic_lexer.inc` blob), eleven round tools still match English text, docs quote old messages. |
| `R2-04-WHAT-I-NEED.md` | WS5 | Which of the seven R1 items remain (three), plus five new: re-pin or retire the source locks, a `\n`-adjacent rename rule, the `gates.sh` suite gate, the `--version` number, which round tools are live. |

---

## Index — ROUND-01 delivery (2026-10-18, written against `feef075` v162, rebased onto `1f031a8` v164)

| File | Workstream | One line |
|---|---|---|
| **`00-READ-FIRST-v164-REGRESSION.md`** | — | **`a5c871c` (v164) reverted 27 compiler string lines to pre-rename English/old keywords; the suite on `main` is 181 PASS / 6 FAIL, not 187; `--version` says v29; the shell help teaches `punaravartana … to`, which does not compile.** Found on fetch, verified by rebuild. |
| `01-DIAGNOSTICS-INVENTORY.md` | WS1 | Every user-facing string, classified (a)/(b)/(c) with line, phase and a Sanskrit proposal for each (b). **80 visible strings, 67 still English.** Twelve findings, of which four are defects: all 50 pack-localized strings are **double-UTF-8-encoded** (users see mojibake), **missing input file exits 0**, `--check` cannot be combined with `--lang`, and **normal-mode line numbers are wrong whenever a module is imported**. |
| `02-HARDCODED-CONSTANTS.md` | WS2 | One stale constant left in the compiler (`r49_print_module_location` still searches for `ayojan` → every module-graph error prints column `?`; proven with a scratch build). Compiled-in Devanagari aliases and `lang/sanskrit.lang` still spell the **pre-v157 words**. Both Linux IDEs highlighted the old keywords at `feef075`; v163 fixed the X11 GUI (all but `sankhya`), the terminal IDE `ide/sutram_ide.asm` is still stale. `tests/module_graph` is **6/18** on main. |
| `03-DOCUMENTATION-AUDIT.md` | WS3 | 15 code samples compiled (13 PASS, 1 FAIL: `LANGUAGE-REFERENCE.md` still uses `to`). ~30 unsupported claims with file:line, including: `tools/r69_build.py` **refuses main** (stale blob pin), R70 negative corpus **cannot run** (fixture sha drift), "at most two modules" limitation is gone, `README` calls the real `mala` module a sketch, and ~58 sentences where the rename replaced English words (`.vardh` for `.inc`, "by gudh", "sangrah up", quoted compiler output misquoted). |
| `04-REAL-PROGRAM.md` + `04-ankatalika.sm` + `04-ankatalika.expected.txt` | WS4 | A 214-line class marks ledger using five library modules (`sankhyiki suchi roop ganit ank`); compiles, runs, byte-identical from two cwds, output checked by hand. Eight observations on what the language is like to use. |
| `05-WHAT-I-NEED.md` | WS5 | Nine items; the first three are a reproducible gate script, a documented build location, and a register decision for diagnostics before any text is translated. |

## Baseline I measured before starting (canonical entry, NASM 2.16.01, binary at repo root)

| Gate | Measured | Matches brief? |
|---|---|---|
| `tests/run_tests.py` | **187 PASS / 4 NO-EXPECTATION** (186 until the binary was at `./sutram_compiler` — `79_ayojan_cwd` needs it there) | yes |
| `tools/codegen_gate.py` | 12 / 12 | yes |
| `tools/test_lang_packs.py` | 33 / 33 | yes |
| `tools/proof_lib.py` | 191 / 191 | yes |
| `tools/proof_props.py` | 86 / 86 | yes |
| `tools/check_layers.py` | 14 core / 9 alloc / 1 std | yes |
| `lib/` | 24 modules / 303 `prakriya` | yes |
| `tests/module_graph` (unittest, run by the CI workflows) | **6 PASS / 10 FAIL / 2 ERROR** | not in the brief — see WS2 §4.2 |
| `tools/r70_negative_corpus.py` | `NOT_ACCEPTED: fixture drift: bad_type` | brief/PROJECT-MASTER say 6/6 — see WS3 §4.1 |
| IDE "18/18" | no tool prints this; `tests/gui` = 28/28, `test_ide_undo` = 12/12 | NOT-REPRODUCIBLE as stated |

## What I changed in the repository

**Only this folder.** No file outside `Claude-to-Sarvam/` was modified. The compiler, the packs, the
IDEs, the tests and the docs are as they are at `1f031a8` (v164). Two scratch builds (a patched copy to prove
WS2 §3.1, and the R71 entry with its flag to check a doc sample) were made outside the tree.

## How to read a delivery

Each workstream document states four things: what I did, what I actually ran (exact commands), what I
observed (pasted output), and what I did not do and why. PASS, FAIL and NOT-RUN are reported separately
throughout. Where I suspect but did not confirm, the text says "I did not verify".
