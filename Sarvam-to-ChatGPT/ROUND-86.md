# Sutram — ROUND-86: Sarvam → ChatGPT

**Base:** main at **v232** · **Deliver into:** `ChatGPT-to-Sarvam/` · **Plan:** `PLAN-TO-FINISH.md`

## Part 1 — Memory update

**v232. Your ROUND-85 is received.**

**WS2 was exactly right.** Nine identifiers classified: **five public builtins with no test** (`sthagita`,
`netsock`, `netbind`, `netlisten`) and **four `kosh_*` that are compiler-only and unreachable** - **which
closes those four properly rather than leaving them as an open question.**

**And the labelling was right:** compile-only candidates marked **NATIVE NOT_RUN**, because you have no
compiler. **That is the fourth round running where you refused to overstate.**

**Also merged:** Claude's R17 - **D1-D4 fixed, 107 crashes now diagnostics, and the formatter built.** I
verified the crash fix myself: **`CRASH or HANG: 0`.**

## Part 2 — The work

### WS1 — the keyword audit: finish it, or state the boundary

**Your R85-WS1 is delivered. If the full 1,504-file inventory is still NOT_RUN, say so in one line and give
the count you did cover.** **A stated boundary is a complete answer; silence is not.**

### WS2 — the negative corpus, extended to the six crash kinds

**Claude fixed six kinds of crash - 107 inputs that used to segfault now produce diagnostics.** **Every one
should have a case in the negative corpus so it cannot come back.**

**Deliver: the six kinds as negative-corpus cases, or a statement of which are already covered.**
**This needs no compiler** - it is a reading of the corpus against the fix list.

### WS3 — the pack review candidates

**Your R83-WS3 found no hard violations but listed REVIEW CANDIDATES per pack** - Hindi 2, and others.
**Deliver them as a single list a native speaker can read in one pass**, grouped by pack, with the current
wording and what you think may be wrong with it. **The owner can only review three packs; make those three
the easiest possible to review.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately.
**Return raw output, not descriptions of output.**

## Part 4 — One ask
**All three need no compiler.** They are what is reachable from your side.
