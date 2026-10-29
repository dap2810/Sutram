# R58-00 — Hand-back to Sarvam: Patch A v2 applied; the vocabulary work is closed

- **Commit on `main`:** `9a73a04` (Patch A v2), then this hand-back's commit, which also adds `tools/guard_pair.py`.
  Pushed with git, not `--force`. **No compiler change this round.**
- **Compiler: `Sutram 1.0 (v261) - sampurna sutra`,** byte-identical to the R56 build.
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs: **226/226**.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 48 PASS / 0 FAIL / 1 NOT-RUN.**
  - The NOT-RUN is Windows execution.
- **The guard, the tree before the patch against the tree after it, the same v261 compiler: 577 programs, 486
  byte-identical, 91 refused identically, 0 DIFFER.**
  - It held on all three paths: Linux ELF, Linux PE, and the Windows compiler under Wine.
  - **36 programs changed their text, and all 36 compile to the same bytes.**

## WS1 — the patch

**Compared with v1 BEFORE applying, hunk by hunk:**
- The same 36 files and 43 hunks.
- **41 hunks are byte-identical to v1.**
- **Two differ, exactly the two you named, and only by the function names my R56 renames changed:**
  - `examples/126_numeric_pipeline.sm`, hunk 2: the context line `likha(bindu(u, v))` → `likha(bindu_gunan(u, v))`.
  - `examples/208_kalana.sm`, hunk 1: `pravan2(...)` → `dvitiya_pravan(...)` in its old and new line. Its variable
    rename, `xs` → `ank_suchi`, is unchanged.
- **So: no difference beyond the two hunks.**
- **The new name is `dvitiya_pravan`,** as the tree has it. The brief's `dvvitiya_pravan` is a typo, and Muse's patch
  uses the right name.

**Then `git apply --check`, which passed, and `git apply`.** 0 rejected hunks, nothing edited by hand.

## WS2 — the proof, and the golden check

**Every golden is byte-identical.** No file under `tests/expect/` changed, and the suite passes against the
unchanged goldens.

**I checked Muse's claim that label strings were left alone, not just trusted it**
(`evidence-r58/strings-and-comments-unchanged.txt`):
- **All 274 changed lines keep every string literal and every comment exactly.** Every file keeps its line count.
- **Two output strings still contain an old variable name, both in `examples/array_demo.sm`:** `"Array values:\n"`
  and `"  arr["`.
  - **That is the deliberate choice.** Renaming them would change what the program prints.

**The 12 names Patch A renamed** match Muse's list: `st`, `xs`, `values`, `sum`, `out`, `data`, `total`, `arr`,
`buf`, `util_chinha`, `flag`, `terms`.
- One is worth noting: **the `util_chinha` variables in the examples became `chinha`** (sign).
- That closes part of the old blind-rename damage I reported in R56.

## A tool that should have been in the tree: `tools/guard_pair.py`

**Every guard line in my hand-backs since R44 came from a script in my scratch space, not the repository.** For the
closing paragraph to tell a reader how to check, the check has to be something they can run.
- **`tools/guard_pair.py` is that script, documented:**
  `python3 tools/guard_pair.py OLD_TREE OLD_COMPILER NEW_TREE NEW_COMPILER OUT_DIR [--pe]`.
- **It gave the same verdict as the scratch guard for each of the 577 programs** (`evidence-r58/tools-guard_pair-linux-elf.txt`).
- **The control:** with a "compiler" that writes nothing, it reports 577 DIFFER and exits 1
  (`evidence-r58/tools-guard_pair-control-must-differ.txt`). **So 0 DIFFER is a measurement, not a tool that cannot
  fail.**
- It is a tool, not a gate. It needs two trees and two compilers, so it is run around a change, not on one tree.

## WS3 — the closing statement, for the project record

> **Sutram's vocabulary work (rounds R44–R58, October 2026) changed names and nothing else.**
>
> **What changed:**
> - **Keywords.** Sanskrit keywords in Devanagari compile without a flag (R50). The return keyword is
>   **`nivartanam` / निवर्तनम्** (R53). The library, the examples, the tests and the live documents now use it
>   (R54–R55). The exceptions are the tests that deliberately feed `prati` to prove the alias, and the pinned
>   negative corpus.
>   The Sanskrit pack's wrong Devanagari words were corrected (the owner's commits `e1fd04b` and `7fb43c6`).
> - **Library functions.** **20 of the 305 were renamed** because their names described a different operation
>   (R56). For example, `mahattam` → `mahattam_samapavartak` (GCD), `sadish_yoga` → `adish_gunan` (a dot product,
>   not a vector sum), and `dviguna` → `dwi_ghat` (2^n, not 2n). Earlier renames: `vartani_*` (R44) and the
>   `brihat` *laghu* pair (R47).
> - **Comments.** 33 surprising contracts are now stated in the comments above their functions (R57).
> - **Example variables.** The 12 English variable names that recur in the examples became Sanskrit (R58).
>
> **What did NOT change:**
> - **Every program compiles to the same machine code, byte for byte, before and after each step, on Linux and
>   Windows. No program's output changed for a rename.**
> - **`prati` / प्रति is still accepted as an alias** of the return keyword.
> - **The renamed library functions have no aliases.** A program that still calls an old name, such as `mahattam`,
>   is refused with *agyat prakriya*.
> - **The ten other language packs are frozen and untouched.**
> - **English remains in three places, by decision:**
>   - comments and output strings;
>   - 96 variable names used only once or twice (Muse's "Patch B", skipped as churn);
>   - dated history: the CHANGELOG and round reports.
>
> **To verify it yourself:**
> - Run `sh tools/gates.sh`, which builds the compiler itself. On Linux with a display it should print 48 PASS,
>   0 FAIL, 1 NOT-RUN, where the NOT-RUN is Windows execution. Without a display, the X11 GUI gate is NOT-RUN too.
> - For any step, check out the commit before it with `git worktree add`, and run
>   `python3 tools/guard_pair.py <old tree> <old compiler> . ./sutram_compiler out [--pe]`. Expect `0 DIFFER`.
> - `python3 -B tests/r53/test_nivartanam.py` shows the two return spellings give identical binaries.
> - `git grep -w mahattam -- lib examples` shows the old name is gone from the code.

## What I did NOT do, and why

- **Patch B:** skipped, as you said.
- **The two output strings in `array_demo.sm`:** left alone, as above.
- **No other change to Muse's patch.**
- **Not run:** real Windows (Wine only).
- **Not touched:**
  - `backups/`, `Windows-to-Sarvam/`, `lang/`, `lib/`, `tests/` and the compiler;
  - **the frozen packs.**
