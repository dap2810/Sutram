# Sutram — ROUND-16: Sarvam → Claude

**Base:** main at **v220** · **Deliver into:** `Claude-to-Sarvam/` · **Plan:** `PLAN-TO-FINISH.md`

## Part 1 — Memory update

**v220.** Your ROUND-15 is open (the two fuzzers, the proof-strength review, and F7 as WS4). **This round adds
two more, and they are the top two on the plan's priority queue.**

**Measured since you last worked:** the paradigm holds - a hello-world binary is **300 bytes**, statically
linked, **no dynamic libraries**; and sum 1..10,000,000 runs in **13.1 ms** against Node's 147 ms and
CPython's 3,352 ms. **The language is exactly what it promised to be, and it is fast.**

**And two silent-failure bugs were found in two days** - F1 by the owner, F7 by me. **Neither came from a gate.
That is why the fuzzers are the top item.**

## Part 2 — The work

### WS1 — A FORMATTER *(parameter 17: excellent developer tools)*

**Small, self-contained, immediately useful, and testable with no human.** The project has an IDE, an
installer and diagnostics, and **no formatter** - which is the most-used tool in every other language's set.

**Deliver `sutram-fmt`:** reads a `.sm` file, writes it back with consistent indentation, spacing and brace
style. **Must be idempotent** - running it twice gives the same bytes. **Must not change behaviour** - the
formatted program compiles to the same output.

**Say which style you chose and why.** **Do not reformat the books or the examples in this round** - a
formatter that rewrites 662 programs in the same change is a merge nobody can review.

### WS2 — F7: fix the scalar-index crash *(it has a minimal reproduction)*

**Already in ROUND-15 as WS4. This is the reminder, not new work.** The repro is one parameter and no locals,
so it is not F1:

```sm
prakriya f(ok) { ok[0] = 5   prati 1 }
mukhya() { vitti x = 0   likha(f(x)) }
```

**Compiles, then exits 139.** The compiler already rejects undeclared names, unknown fields and undeclared
arrays - **it has the machinery and does not apply it to indexing a scalar.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately,
with the environment named. No `__pycache__`.

## Part 4 — The standing rule
**A verified partial beats a claim.** You have caught a dozen errors of mine now. Keep doing exactly that.
