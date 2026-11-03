# Sutram — ROUND-105: ATTACK THE ARENA. Your job this round is to break it.

**Base:** main at v290 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is

**Compiler v290 on main.** The outlives rule (a `kosh` cannot be kept in a `prakriya`), the `mala` refusal, and `parimana()` moving. Suite 287, guard 697 programs, gates 59 PASS / 1 FAIL (installer payload v243 vs v290).
**The block-arena is BUILT and on a review branch, not main: `claude/r108-arena-review`, commit `0e71e54`.** Claude finished it before my correction arrived, so it put it aside rather than merging.
**My arena design was wrong: ChatGPT R177 showed copying to a new slot IS relocation even when the arena does not move, so aliases break. An arena epoch alone fixes neither alias coherence nor lifetime safety.**
**Audit: v290 consistent across binary, source, changelog. 289 example FILES, 287 suite passes, 4 without expectation. Root down to 6 .md files. `Sutram-Setup.exe` is v290 with a matching SHA-256, but `bin/sutram.exe` and `win/sutram.exe` inside it are still v243.**

## This round you attack a design and a build, before either reaches main

**That is the arrangement we are testing.** **You have been the most accurate voice in this room: you corrected my count four times, my loop description twice, and found eight traps nobody else found.**

## WS1 - break Claude's build
**The branch is `claude/r108-arena-review`, commit `0e71e54`.** **Claude says it works.** **Find the program that breaks it.**

**Specifically:**
- **a `kosh` grown inside the arena, with an alias taken before growth - does the alias see the new data?**
- **a `kosh` that outlives its block - is it refused, and at what point?**
- **an arena exhausted mid-block - what happens?**
- **and `parimana()` - does it report something meaningful while the arena is in use?**

**Report the program, the output, and whether the output is wrong or merely unexpected.**

## WS2 - and attack ChatGPT's specification when it lands
**It is designing the arena this round.** **When its report is in the tree, read it and find the case it does not cover.**

**You do not need my permission to say a design is wrong.** **That is the assignment.**

## WS3 - and the census, ninth run
**Three counts, same method.** **And: has v290's outlives rule broken any example that used to work?** **Name any file where the answer changed.**
