# Sutram — ROUND-109: build only what survives. And the installer payload.

**Base:** main at v290 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is

**Compiler v290 on main.** The outlives rule (a `kosh` cannot be kept in a `prakriya`), the `mala` refusal, and `parimana()` moving. Suite 287, guard 697 programs, gates 59 PASS / 1 FAIL (installer payload v243 vs v290).
**The block-arena is BUILT and on a review branch, not main: `claude/r108-arena-review`, commit `0e71e54`.** Claude finished it before my correction arrived, so it put it aside rather than merging.
**My arena design was wrong: ChatGPT R177 showed copying to a new slot IS relocation even when the arena does not move, so aliases break. An arena epoch alone fixes neither alias coherence nor lifetime safety.**
**Audit: v290 consistent across binary, source, changelog. 289 example FILES, 287 suite passes, 4 without expectation. Root down to 6 .md files. `Sutram-Setup.exe` is v290 with a matching SHA-256, but `bin/sutram.exe` and `win/sutram.exe` inside it are still v243.**

## Your R108 was the right call and I want it on the record
**"The correction arrived mid-build: the arena was finished and works, so it is on a review branch, not main."** **That is exactly what a build should do when its premise changes, and you still shipped the safe part.**

**And you reported the failing first gate run both times, and said what you should have done.** **Twice now. That is the discipline this project needs.**

## WS1 - do not merge the arena branch yet
**Muse is attacking it this round and ChatGPT is specifying the correct design.** **Wait for both.**

**When they return: merge only what survives, and if the branch is wrong in a way that cannot be fixed cheaply, say so and leave it unmerged.** **An unmerged branch is a better outcome than a wrong one on main.**

## WS2 - and the installer payload, which is now the only release blocker
**`Sutram-Setup.exe` at root is v290 and its SHA-256 matches.** **But `bin/sutram.exe` and `win/sutram.exe` INSIDE it are v243.** **The gate reports this as "installer version FAIL", which reads as "the installer is old" when the truth is "the installer is new and its payload is old".**

**Two things:**
1. **Make the gate say which it is.** **"payload v243, installer v290" is a different message from "installer v243".** **The current message sent me looking at the wrong file.**
2. **Write the exact command the maintainer runs on Windows to rebuild the payload, and the SHA-256 he should expect.**

## WS3 - and the test runner
**`python3 tests/run_tests.py` printed `1 7 7 1` and a NO-EXPECTATION line instead of a summary on my run.** **I could not read the result, so I did not quote a number.** **A test runner whose output cannot be read is one people stop trusting.** **Check it.**
