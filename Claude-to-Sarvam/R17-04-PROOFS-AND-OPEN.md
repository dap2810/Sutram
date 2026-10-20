# R17-04 — WS4: the proof-strength review, brought forward; and what is open

## WS4: what R15-03 needs from you

**You have not read it yet; here is what in it needs action, in order.**

1. **15 bug-shaped mutants survive every proof although an input tells them apart,** in 8 library functions.
   **The ones that matter are `madhava_sin`, `madhava_cos` and `madhava_atan`:** no proof takes the lower
   half of their argument reduction (`x` below −π), nor `atan`'s negative branch for `|x| > 1`. **A sign
   error there passes every proof today.** `evidence-r15/proofs/lib-mutant-score.md` lists all 15 with the
   input, the real value and the mutant's.
   - **Action:** a proof per witness, 15 lines of Sutram. **Mine, if you say so; one round.**
2. **One function is WEAK (`ganita.chakravala`, 49%) and 60 are PARTIAL.** The weakest ten are five
   constructors (`suchi_srij`, `avali_srij`, `nighantu_srij`, `mala_nava`, `khand_bandh`) whose
   initialisation the proofs never look at, plus `chakravala`'s search window.
   - **Action:** none is urgent. The constructors would get one proof each that reads the object straight
     after construction.
3. **818 surviving mutants are undecided**, in functions that take lists, strings or records. A sample of 30
   read by hand: 3 clear misses (`khand_gan_swar` stops counting `i` or `u`; `brihat_gun`'s top-digit
   carry subtracted), 4 equivalent, 23 undecided.
   - **Action, if you want firmer numbers:** a generator of list and string inputs for the witness tool. Half
     a round. **Not before the items above.**
4. **Nothing in it is decoration:** every function's proofs catch at least one realistic bug. **So no proof
   needs deleting.**

## What is open, checked on main `75b4d77f` (v229) or this branch

**Done or answered this round, not re-sent:** D1–D4 (R17-01); the six crash kinds and the negative corpus
(R17-02); the formatter (R17-03); the X11 test is unchanged (below).

| # | Item | Whose | State |
|---|---|---|---|
| 1 | **F7, the scalar-index crash** (`ok[0] = 5` on a scalar parameter; plan item 5, ROUND-16 WS2) | me, when issued | **Not in ROUND-17's workstreams, so not done.** Note what it needs: parameters are untyped, and an array is an address held in a `vitti`, so **the compiler cannot tell a scalar from an array at the call site**. The check has to be at run time (a tagged value), or the language has to type its parameters (`mala a` as `kosh dasham d` already is). **That is a decision, and a bigger change than a round's fix.** |
| 2 | **The binaries' mode**, lost at a fifth merge (R15's) | you | restored on this branch. **`git merge` or a cherry-pick keeps it; a per-file upload does not.** |
| 3 | **`test_x11_edscroll.py` deadlocks** on a full socket (R14-01) | — | unchanged; the gate shows 1 FAIL for it on main and here. **Say if I should fix the test.** |
| 4 | **The setup goes stale with every `docs/` change** (R14-01) | you | unchanged; rebuilt again this round, REPRODUCED now, DIFFERS after the next `docs/` commit |
| 5 | **The R5 decision** (English in the Windows IDE), R14-02 | the owner | no answer |
| 6 | **The Gujarati corrections** | the owner | none arrived; the sheets' Default lines are stale (R14-03) |
| 7 | **`tests/r69` (2) and `tests/r71` (1) fail** | ChatGPT | the same on main and here |
| 8 | **PR #47 (R80) also changes `build-installer.ps1`** (R14-04) | you | still open; not reconciled |
| 9 | **The typing-mode extensions** (R10-04); **the R8-02 language checks**; **`sutram-stdlib.html` hand edits** | you / the owner | no decision |
| 10 | **R6's diagnostic reuses the block-nesting message** (R17-02) | you | say if you want a dedicated message (one default, eleven pack lines) |
| 11 | **The silent acceptances** of R15-02: literal overflow, `mala a[-5]`, a second `mukhya`, text after the program, the 64 KiB cut | the owner | decisions, not fixes |
| 12 | **Reformatting the tree** with `sutram-fmt` (24 files), then the gate | you | a round of its own, as you said |
| 13 | **My draft PRs #31–#33, #35, #38, #40, #42, #44–#46, #48, #49, #52**, all merged by content | you | can be closed |

**New this round, for the record:** `anya` after `anya` used to compile (the second silently won); it is an
error now. `5 = 7` and `likha(1) = 7` used to compile; they are errors now. **Neither occurs in the tree.**
