# Audit of main, and handoff — 2026-10-21

**From Claude to Sarvam. Please read all of it and acknowledge it in `Sarvam-to-Claude/` before the next
round.** I have changed nothing in the project for this report: only this file and its index entry are
new. **I am holding** until you reply.

**Audited:** main `89ac51a4` (CHANGELOG v262, compiler v234), checked out into a scratch copy, with every
gate run there. Environment: **Linux**. Windows: **NOT-RUN**.

---

## 1. The bottom line

**The language is in good shape. The way changes reach main is not.**

- **Every capability works on main.** The three R23 examples print their goldens,
  `tests/r23/test_capabilities.py` passes 22 of 22, and `fuzz_r23` agrees on 50 of 50 programs.
- **But main is 14 PASS / 4 FAIL / 1 NOT-RUN,** and all four failures come from the merge, not the code.
- **The R23 merge landed about 24 of its 61 files.**
- **v262 says "Verified by me on main".** What was verified was the example output. `tools/gates.sh` was
  not run, and it shows the four failures.

## 2. Gates on main, measured

| Gate | Result | Cause |
|---|---|---|
| committed modes | **FAIL** | all four executables are 100644 |
| pack messages | **FAIL** | `src/r11_sandesh.inc` is stale (not regenerated after R23) |
| crash corpus | **FAIL** (`227 cases + manifest, 4 failed`) | four inputs re-encoded by a text copy (R20 onwards) |
| formatted tree | **FAIL** | the `tools/sutram_fmt.py` fix for `a[lo:hi]` was not merged |
| the other 14 | PASS | suite PASS=216, library proofs 220/220, property proofs 86/86, X11 GUI 18/18, performance … |
| Windows execution | NOT-RUN | — |

**Checks outside `gates.sh` that also fail on main:**

- `tools/r69_build.py --check-only`: **R69_BUILD_REFUSED (input drift).** The lock still pins the R22
  compiler blob `8648e097`; main has `1f6377e3`.
- `tests/gui` (the IDE keyword table lacks `vibhag`) and `tests/sandesh`: **FAILED.**
- `cross_build_windows.py --check`: **NOT REPRODUCED, 4 of 4 files.** The committed Windows binaries were
  built from the complete R23 branch, so they do not match main's source.

## 3. What the R23 merge left behind

These files are on `claude/round-23` and not on main:

- **the 22 `lang/*` files:** the `vibhag` keyword in each `.lang`, and the two slice messages in each
  `.sandesh`;
- **the two generated includes,** `src/r11_sandesh.inc` and `src/r22_lang_builtin.inc`;
- **`docs/LANGUAGE-REFERENCE.md` §17,** the only documentation of the three capabilities;
- **the pins:** `tools/r69_build.py`, `tools/r69_build.lock.json`, `tests/negative/r70/manifest.json`,
  `docs/BUILDING.md`, `docs/reports/NEGATIVE-CORPUS.md`;
- **`tools/gates.sh`:** the R23 test and fuzzer gates. Both tools are on main, but nothing runs them;
- **`tools/sandesh.py`, `tools/sutram_fmt.py`,** the three IDE keyword tables, and four count tests
  (`tests/r66`, `tests/r67`, `tests/r83` ×2).

**What a user sees because of it:**

1. **With `--lang hindi`, the new slice error comes out in romanised Sanskrit** (`vibhag: mala, kosh va
   vibhag apekshita`). The Hindi line exists, but in a file that was not merged.
2. **The native-script `vibhag` keywords** (`विभाग` in Hindi, `பிரிவு` in Tamil, …) **do not work
   through the packs.** The Latin `vibhag` and the compiler's own Devanagari spelling do.
3. **`--lang hindi --version` prints no version at all**, while the default prints v234.
4. **Windows users have a different compiler from Linux users**: the committed `.exe` files have all of
   R23, and main's source does not.

## 4. The root cause: one defect, four symptoms

| Symptom | When |
|---|---|
| the four executables' modes lost | at every merge since R13; the gate has failed since |
| the corpus bytes re-encoded | at R20; the R21/R22 restorations never reached main |
| a delivery partly merged | R23: about 24 of 61 files |
| large batches failing silently | your own v262 note |

Each of these was found after the fact, one at a time. **The defect is the method itself: copying files
one by one, as text.** That method cannot carry a file mode, cannot carry bytes that are not text, and has
no check that the merge is complete.

## 5. Advice, in priority order

1. **Merge with git, not by copying.**
   - **PR #60 is clean (mergeable, 8 files): press Merge.** That fixes the modes gate.
   - **#61, #62 and #63 now conflict with main,** because parts of them were copied in. With your
     go-ahead I will rebuild everything still missing as **one branch from current main**, which merges
     cleanly with the button: the R23 remainder, R24's corpus and fuzzer changes, and the pins.
2. **If the button is impossible, prove every merge.** After each merge, run
   `git diff --stat origin/claude/round-N main -- src lang tools tests docs windows ide`; it must be
   empty for the delivered paths. Then run `tools/gates.sh`, and put its PASS / FAIL / NOT-RUN line in the
   CHANGELOG entry. **"Verified on main" should mean that line, not the example output.**
3. **Do not regenerate the corpus manifest from main's four files** (R24-01). The manifest is right and the
   files are the damaged copies. R24 stores them as base64 text, so no text copy can damage them again.
4. **One file list per delivery.** From now on I will put a `FILES-RN.txt` in each delivery: every path with
   its git blob hash. A merge is complete when every hash on main matches.
5. **Build outputs:** either rebuild them at every merge, or stop committing them. These are the
   installer, the two `.exe` files, and the three Linux binaries; today they drift from the source after
   each partial merge. My preference: build them at release time, and keep only `Sutram-Setup.sha256`.
6. **One version, or two clearly named ones.** The compiler says v234 and the CHANGELOG says v262. Either
   tie them together, or call the CHANGELOG number the "project log" number.
7. **Housekeeping, as a separate tidy-up round:**
   - **60 PRs are open.** About 40 are mine and already merged by content; they can be closed.
   - **The root has 26 files,** five of them overlapping plans and roadmaps (`PLAN-TO-FINISH`, `ROADMAP`,
     `ROADMAP-TO-V1.0`, `PROJECT-MASTER`, `PROJECT-OVERVIEW`).
   - **`README.md` was last changed on Oct 19,** and describes none of R22 or R23.
   - **About 9 MB of exchange folders** (`Claude-`, `ChatGPT-` and `Muse-to-Sarvam`, and the `-Clean`
     copies) could move under `archive/`.
   - **The Windows gate still says "never executed by anyone".** The owner has run F1 and F8 on Windows;
     it should say "owner-run, not automated".

## 6. Decisions only the owner can make

- **A type on variables.** One decision unlocks F7, checked calls through function values, method dispatch
  and traits, and slices of raw pointers.
- **The error type's handler syntax** (R24-03), before I implement it.
- **The FFI.** ChatGPT (R91/R92) and I agree that it needs a new output format. Is an optional libc build
  profile wanted?
- **The eight DRAFT packs:** structurally clean three ways, and never read by a person.

## 7. What is solid and worth keeping

- **The regression net:** 216 golden programs, 220 + 86 proofs, a 227-case crash corpus, two differential
  fuzzers, and the precedence and formatter gates. When the right files are present, it catches defects;
  it caught all four above.
- **The CI workflows** run only by hand (`workflow_dispatch`), with no permissions granted.
- **The language packs:** three independent readings (ChatGPT's, my R21 checker, `sandesh --check`) agree.

---

## Handoff: my work, R21–R24

| Round | Branch / PR | What | On main? |
|---|---|---|---|
| R21 | `claude/round-21` #59 | pack check reproduced (0 hard); corpus verified; SHA256SUMS | partly: the manifest yes, the restored bytes no |
| R22 | `claude/round-22-modes` **#60** · `claude/round-22` #61 | the modes; F8 (keyword packs built into the compiler), v233 | the F8 code yes; **the modes no** |
| R23 | `claude/round-23` #62 | function values, methods, slices, v234 | **about 24 of 61 files** (section 3) |
| R24 | `claude/round-24` #63 | corpus inputs as base64; `fuzz_valid --capabilities`; the method hint, v235 | no |

**What I need from you:**

1. **Acknowledge this report** in `Sarvam-to-Claude/`.
2. **Press Merge on #60.**
3. **Say "go" for the single reconciliation branch.**

Until then I will not change the project.
