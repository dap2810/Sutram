# R123-00 — PR #65's memory work is merged (v299), ported onto v298, not merged whole. Verified: on Windows `parimana()` reports real bytes, `mandapa parimita` refuses, the `kosh` alias gives `a[0]=99 k[0]=99`. Linux: suite 315, ELF guard 0 DIFFER. The branch could not go in as it stood - it still carries Round 3's `vartani_sandhi`, which v298 replaced - and its own note says so. The price is Windows commit: 1 GiB for the first allocation and 64 MiB a `kosh`. My numbers for WS2/WS3 are below.

- **Commit on `main`:** **`c86e343`** - the merge in one commit (on top of your R123 files and R121's Wine line, `33cab2d`). PR #65 itself is left open: what it adds beyond this is Round 3's builtins, which main does not take.
- **Compiler: `Sutram 1.0 (v299) - sampurna sutra`** (was v298). Linux x86-64 cloud; PE run under Wine 64.
- **`crash corpus: 227 cases + manifest, 0 failed`.** **Suite: `suite: NO-EXPECTATION=4  PASS=315  (319 run)`**, FAIL=0 - no golden changed.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 64 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, payload v243, as before; NOT-RUN: Windows execution) - 66 gates now, with **`R123 PE memory` (9 checks, 0 failed)**.
- **The guard, main v298 (`33cab2d`) → v299, 725 programs** (`evidence-r123/guard.txt`):
  - **Linux ELF: 582 byte-identical, 143 refused identically, 0 DIFFER, 0 new.** The merge changes no Linux program by a byte.
  - **Linux PE: 255 byte-identical, 143 refused identically, 327 DIFFER, 0 new** - every program that allocates now uses the arena on Windows. **Run old and new under Wine: 317 print the same and exit the same; 10 change, and every one now does what Linux does:**
    - **examples 288, 303, 317, 318: now print their Linux golden** (the four Windows gaps);
    - **six tests without a golden** (`tests/r73_scratch/blind_kosh_via_call`, `full`, `negative_runtime`; `tests/r74_compose/c3_siblings`, `c4_too_big`; `tests/r79_real/report_blocks`): **now print exactly what the Linux ELF build prints.** On v298 four of them ran on where Linux stops (a block's field or budget), and `c3_siblings` was killed (exit -9).
  - **The Windows compiler under Wine: the same 327, and its 1164 outputs are byte-identical to the Linux compiler's PE outputs.** Its log shows 328: `07_module`'s old compile timed out under Wine while I was running the PE binaries alongside. Rerun alone, it is identical, in 0.8 s.

## WS1 - verified, then merged - but not the branch as it stood

**PR #65 (`codex/windows-round4-2026-11-03`, `029c06d`) is based on v297, before main's v298.** It carries two things:

1. **Round 3's builtins** - `vartani_sandhi` returning a new string, `anka_akshar` allocating - and its `E_WINDOWS_SMRITI` refusals.
2. **Round 4's change:** `r65_active` no longer excludes PE, which turns the shared arena and the `kosh` regions on for Windows; Round 3's refusals are removed again.

**Merging the branch whole would have reverted v298's `vartani_sandhi`** (in place, a literal refused). **Its own `INTEGRATION.md` (`029c06d`) says the same:** *"Do not merge the entire branch over v298 ... retain v298's builtin semantics, independently port the Round 4 `r65_active` PE enablement and Windows harness corrections."* **That is what I did, in one commit:**

- **`src/r65_arena.inc`:** `r65_active` is 1 for ELF and PE (not the `GUARD_PAGES` build) - Round 4's change, byte for byte. Plus comments, in it and in `src/sutram_compiler.asm`.
- **`tools/test_windows_native.py`:** Round 4's two harness fixes - example 220 gets `--lang hindi`, example 29 (a raw Linux exit syscall) is skipped and says why.
- **The reference, `MEMORY-MODEL.md` and the three status boxes:** Windows now has the memory model; its cost is stated.
- **`tests/r123/test_pe_memory.py`, gate `R123 PE memory`.** The branch's `tests/windows_round3/test_contract.py` is **not** taken: it asserts Round 3's semantics (`vartani_sandhi("ab", "cd")` joined), which v298 refuses. Its parts that hold on v298 are in the new gate or in `R121 builtins`.

**Your four checks** (PE run under Wine 64; `evidence-r123/probes.txt`):

| check | v298 | v299 |
|---|---|---|
| **`parimana()` returns real bytes on Windows?** (example 317) | `0 0 0 0 0` | **`0 64 1072 64 8272`** - the Linux golden byte for byte |
| example 318 (one number, moving) | all 0 | **`0 48 72 184 288 176`** - the Linux golden |
| **`mandapa parimita` enforces?** (example 303) | prints the sum, exit 0 | **`E_PARIMITA ... (parimitih 1048576 baait)`**, exit 1 - the golden |
| a budget that fits (example 304) | runs | runs - the golden |
| **the `kosh` alias** (example 288) | `a[0]=41 k[0]=99` | **`a[0]=99 k[0]=99` / `a[0]=7 k[0]=7`** - the golden |
| **Linux: suite 315, guard 0 DIFFER?** | | **315; ELF 0 DIFFER** |

The gate checks the same four on ELF and PE with values worked out from the reference, not recorded. **v298 fails it on 3 of 9** (the three PE gaps); **v299 passes 9 of 9.**

**What I could not verify:** native Windows. Wine runs the PE output on a Linux kernel and does not charge Windows commit (it maps lazily). So **the Windows agent's own measurements are the only evidence for the commit cost** (Round 4's `MEMORY.md`: 475,136 bytes for an empty program; 1,076,314,112 with the arena; 67,715,072 for one `kosh`), and for the 312/0 native suite.

**One more thing the merge does not fix, now reachable on Windows too:** a `kosh` region whose allocation is refused crashes the program instead of failing cleanly (R122 found it on Linux under `ulimit -v`: the 16th `kosh` under 1 GiB). **On Windows the refusal comes from commit, not address space,** so the wall is where the machine's free commit runs out. I checked the tree: **every one of the 582 compiled programs runs the same under a 2 GiB address limit**, so no program in the tree comes near it - but a student's loop of a few hundred `kosh`es would.

## WS2 - 1 GiB of commit, priced

**First, two constants, not one:**

- **The arena is `R65_ARENA`, 1 GiB** - every `nirmmita` and `mandapa` block.
- **A `kosh` region is `R101A_REGION`, 64 MiB** - one per `kosh`.
- **The 8,388,603 cap is per `kosh`** (numbers in one `kosh` before it moves), **not a count of koshes.** The count is bounded by address space on Linux, and on Windows by commit.

**What a Windows program commits today (v299) = 1 GiB if it allocates anything + 64 MiB for each `kosh`.** A program that only prints commits nothing extra (the arena is created at the first allocation). **The trade, with 4 GiB of free commit as the example machine:**

| arena | region | a program with one allocation | per `kosh` | koshes in 4 GiB of commit | the most one `mandapa` can hold | a `kosh` never moves up to |
|---|---|---:|---:|---:|---:|---:|
| **1 GiB (today)** | **64 MiB** | **1 GiB** | 64 MiB | **48** | 1 GiB | 8,388,603 |
| 1 GiB | 1 MiB | 1 GiB | 1 MiB | 3,072 | 1 GiB | 131,067 |
| 64 MiB | 64 MiB | 64 MiB | 64 MiB | 63 | **64 MiB** | 8,388,603 |
| **64 MiB** | **1 MiB** | **64 MiB** | **1 MiB** | **4,032** | **64 MiB** | **131,067** |
| any - **commit only what is touched** | | **the pages used** | **4 KB + 8 B a number** | **as on Linux** | unchanged | unchanged |

(Koshes = (4096 − arena) / region, in MiB. Computed, not measured. A smaller arena costs blocks: R103 measured a block of 1,000,000 64-byte `nirmmita`, 64 MB, which a 64 MiB arena would refuse with `kshetra purnam`.)

**Is 1 GiB acceptable for a teaching language? No.** On your 4 GB machine a program that makes one string commits a quarter of the machine before it does anything, and two such programs at once may not start. **The fix is the last row: commit on demand.**

- **What it needs:** reserve the arena and each region (`MEM_RESERVE`), and commit pages as the arena's bump pointer or a `kosh`'s capacity passes them (`MEM_COMMIT`).
- **That is PE-only emitted code:** a compare and, rarely, a `VirtualAlloc` call at those two places. The runtime's `mmap` adapter has to learn `MAP_NORESERVE`.
- **About two days with its gate.** It changes every allocating PE program's bytes again, and no ELF byte.
- **If v1.0 cannot wait for it, the interim is the fourth row, PE only:** 64 MiB of commit for the arena, 1 MiB a `kosh`. It costs Windows two limits Linux does not have, both stated: a block holds at most 64 MiB, and a `kosh` past 131,067 numbers moves again.

**Not changed, as you said.**

## WS3 - the 16-`kosh` ceiling, and the right number

**On Linux the ceiling is not 16. It is about two million** (128 TiB of address space / 64 MiB). **16 is what a 1 GiB `ulimit -v` leaves, and the number is not the problem - the crash is.** A refused region writes through the error value instead of failing.

**My answer, and why:**

- **Linux: keep 64 MiB, and fix the failure.** Address space is the cheap resource there; never-move up to 8.4 million numbers is the property that makes a second name safe. When a region is refused, either fall back to the old moving path (only that `kosh` loses never-move, and it works) or stop with a message (`Sutram truti: ...`, exit 1). **About half a day, both platforms; it changes every `kosh` program's bytes.**
- **Windows: 64 MiB only with commit on demand** (WS2's last row). **Until then, 1 MiB** - the never-move limit drops to 131,067 numbers, and 64× more koshes fit.
- **The general rule:** the reservation should be sized to the never-move guarantee you want to state, and *what* it reserves must be address space, not memory. On Linux it already is; on Windows it is not yet.

## Not done, and why

- **Commit on demand, the region-failure fallback, a smaller PE region:** priced, not built, as WS2 says.
- **The branch's Round 3 `vartani_sandhi` and its contract test:** not taken - v298's semantics stand (R121).
- **Native Windows:** NOT RUN (no Windows host). PE checked under Wine, which does not charge commit.
- **Not touched:** `backups/`, `Windows-to-Sarvam/` (read only), the packs, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`; the PR #65 branch itself.
