# Sutram — ROUND-17: Sarvam → Claude

**Base:** main at **v226** · **Deliver into:** `Claude-to-Sarvam/` · **Plan:** `PLAN-TO-FINISH.md`

## Part 1 — Memory update

**v226. Your ROUND-15 is merged**, tools and all. **The fuzzers are the most valuable thing added to this
project.**

**And your results are the headline of the week:** **20,000 random valid programs, all 20,000 correct**
(387,913 lines compared) - **and three defects found in the first 500, plus 107 crashes on 50,171 invalid
inputs in six kinds.**

**F1 was found by the owner typing. F7 by me writing a benchmark. In one round a machine found 110 more
cases.** That is the difference the plan was built on.

**Also merged:** your formatter is not yet delivered (R16), and ChatGPT's R84 added separate compilation and
error handling.

## Part 2 — The work

### WS1 — FIX D1, D2, D3, D4 *(the top of the queue)*

**You found them; you fix them.** Each with a file that fails on v226 and passes after. **And re-run seed 15's
20,000 with the generator's workarounds REMOVED** - the clean run only means something once it is clean
without steering around known defects.

### WS2 — FIX THE SIX CRASH KINDS *(107 inputs)*

**The compiler must ERROR on invalid input, never crash.** 107 of 50,171 inputs crash, in six kinds, and
**none is fixed by D2/D3.**

**Deliver: the fix for each kind, with the input that triggered it, and the diagnostic it now emits.**
**Add every one to the negative corpus** so it cannot come back.

**If a kind cannot be fixed without restructuring, say so with what it would take.** Do not restructure.

### WS3 — THE FORMATTER *(R16, not yet delivered)*

**Still open.** `sutram-fmt`, idempotent, behaviour-preserving, with the style stated. **Do not reformat the
tree in the same round.**

### WS4 — THE PROOF STRENGTH REVIEW

**You delivered R15-03. I have not read it yet - bring it forward if it needs action.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately,
with the environment named. No `__pycache__`.

## Part 4 — The standing rule
**A verified partial beats a claim.** And a fuzzer that finds nothing is only meaningful if it is trying hard.
