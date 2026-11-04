# How this project found its defects: reading and testing catch different things

**Written in R129 (4 November 2026, v305) for the record, so that a future reader knows how the release
candidate was checked, and does not mistake one method for enough.**

**The fact:** between v297 and v305 the project found its memory and tracking defects in four different ways.
Each way found defects the others had missed. No single way was enough.

## The record, v297 to v305

| found by | how | what | missed by |
|---|---|---|---|
| **a second platform** (Windows rounds 1-2, native) | running the same 305 examples on Windows | `anka_akshar` returned memory it did not own (`P` for `B`); `vartani_sandhi` wrote into a read-only literal (access violation) | **every Linux test**: on Linux both happened to produce the right bytes by luck; R121 then proved both wrong on Linux too |
| **testing while reading** (Claude, R125) | checking a claim about the compiler by writing programs against its source | three tracking defects: two SIGSEGVs and a silent read past a `kosh`'s length (v300) | the suite and 62 gates, all green |
| **an independent attack** (Muse R127, without reading Claude's report) | deriving attacks from the description of the table, then running them | eight instances, including the global door - a `kosh` in a module `vitti`, silently 0 | Claude's R125, which found three |
| **reading alone** (ChatGPT R203, no toolchain) | reading the descriptor's generated code | three v302 defects: an index with a call read stale elements (SIGSEGV), a capacity wrapped into a 32-byte allocation (silent overwrite), `parimana()` read a clobbered register | **Claude's 15-check gate, Muse R129's attack (no crash found), and the owner's own four checks** - all passed v302 |
| **reading again** (ChatGPT R204, on v303) | reading v303's fix | S1: a slice passed beside an argument that grows the `kosh` (v303 SIGSEGV, reproduced in R129); S2: `k[lo:]` kept the old end | **v303's own fix**, which covered indexes and explicit bounds but not this. S1 had just been closed by v304's slice rule, built for another reason; S2 was fixed in v305 |

## What each method is good at

- **Testing** (the suite, the gates, the guard, the fuzz-like attacks) finds what a program does on inputs someone
  thought to write. It is exact about those inputs and blind to the rest.
  - Muse R129 attacked v302 carefully and found nothing, because no probe put a call inside an index, a
    capacity near 2^61, or `parimana()` next to a region.
  - **A passing test says that case works, not that the code is right.**
- **Reading** finds the cases nobody wrote. R203 saw:
  - that the length was loaded before the index was evaluated;
  - that `(cap + 4) * 8` had no check;
  - that a value was read from a register a `syscall` overwrites.
  - **But reading is unconfirmed until something runs.** R203 was explicitly NOT RUN. Each finding became a fact
    only when a program reproduced it on v302 (R128).
- **A second platform** finds what one platform's accidents hide. Linux's memory layout made two wrong builtins
  look right.
- **Independence matters.** Muse found five instances Claude had not, partly because it had not read Claude's
  conclusion. A reviewer handed the answer tends to confirm it.

## What the project does because of this

- **Every reading finding is reproduced before it is fixed, and becomes a gate check that fails on the old
  compiler.**
  - `R127 descriptor`: v302 fails the six R203 checks.
  - `R126 kinds`: v300 fails 28 of 40.
  - Muse's eight are goldens, `examples/351`-`359`.
- **Every fix is guarded:** every program compiled before and after, the bytes compared, and every difference run
  on both platforms.
- **No round declares "no known defect".** A round says which methods were applied, and to what. The release notes
  (`docs/RELEASE-NOTES.md`) list the limitations that remain.

**And it kept happening:** the round that fixed R203's three let one through that R204 found by reading the fix.
That is the pattern, not an exception - **a fix is new code, and gets read and attacked like any other.**

**The lesson in one line: test what you thought of, read for what you did not, and run the reading - neither alone
was enough here.**
