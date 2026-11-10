# Sutram — ROUND-183 (QUEUED): a full test and performance baseline. Do this AFTER R182.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**This round is queued. Do not interleave it with R182.** **Finish the lexer refusal first, report, then start this.**

**The owner asked for a vigorous test of the development — performance, tests, results — so the project has a proper baseline rather than a set of claims.**

---

## 1. Why this round exists

**Every number this project has quoted came from a measurement taken for a specific question.** **A memory peak for one program, a speed for one loop, a guard count for one change.**

**Nobody has measured the whole thing at once.** **So there is no baseline: no way to say "v319 is faster than v315" across the language, and no way to notice a regression in compile time or in a program that is not in the 783.**

**This round produces that baseline, on v315 and on the staged branches, with the method stated for each number.**

---

## 2. WS1 - the correctness baseline

**Run everything, and report each with its command:**

1. **The suite** — `tests/run_tests.py`. **PASS, FAIL, NO-EXPECTATION, total.**
2. **The crash corpus** — 227 cases. **Passed, failed.**
3. **The gates** — all of them. **PASS, FAIL, NOT-RUN, and name every NOT-RUN and why.**
4. **The guard** — 783 programs against v315. **Identical, refused, DIFFER.**
5. **And the 331 examples** — compile every one, run every one, and compare stdout against the golden. **How many compile, how many run, how many match.**

**And one thing nobody has done: how many of the 331 examples are actually run by the suite?** **If an example is not in the suite, it is not tested — and the number matters.**

## WS2 - and the compile-time baseline
**Measure how long the compiler takes, on:**

- **a tiny program** — 10 lines
- **a typical example** — the median of the 331
- **the largest example in the tree**
- **and the whole 331 compiled in sequence**

**Report wall time, best of five, with the machine's CPU named.**

**And: does the lexer refusal in R182 change any of them?** **A per-character check is a cost on every character of every program.** **Measure it on a 10,000-line file, before and after.**

## WS3 - and the runtime baseline
**The project has quoted 2-8 ns for allocation, 3.3 ms for 800,000 loop passes, and 13.8 ms for a block loop.** **Those came from different rounds and different programs.**

**So: one table, one machine, the same programs across v315, v319 and v320.**

**At minimum:**

- **800,000 iterations of an empty loop** — the loop cost alone
- **800,000 `nirmmita(64)` in a loop, no block**
- **800,000 `nirmmita(64)` in a block inside a loop**
- **800,000 `kosh temp[1]` in a loop**
- **a `kosh` grown to 20,000,000 elements**
- **800,000 `mala m[8]` in a loop**
- **and a program that does real work** — one of the examples with arithmetic in a loop, not a synthetic

**Report wall time, best of five, and peak RSS with the baseline subtracted.**

**And the one comparison that matters: v319 against v315, on every row.** **The reuse fix should be faster everywhere it applies and identical where it does not.** **If a row got slower, that is a regression and I want it named.**

## WS4 - and the memory baseline
**Current `VmRSS` and `VmSize`, sampled, pages touched, baseline stated — the method R169 established.**

**For each program in WS3: peak RSS on v315, v319 and v320.**

**And the three numbers the project has never put in one place:**

- **a program that allocates nothing** — the floor
- **a program that makes one `kosh` of 1,000,000 elements** — the cost of a real collection
- **a program that makes 1,000 `kosh` of 1,000 elements each** — the cost of many small ones

## WS5 - and the honest part
**Every number in this round must state:**

1. **What was measured** — wall time, or `VmRSS`, or `VmSize`.
2. **How** — the command, the sampling method, best of how many.
3. **What it cannot show** — peak cannot show a return; a single run cannot show variance.

**And where a number differs from one the project has quoted before, say so and say which is right.** **A baseline that contradicts the record is more useful than one that agrees with it.**

## WS6 - and the deliverable
**One document, `docs/PERFORMANCE-BASELINE.md`, with the tables and the method.**

**And a one-page summary at the top: what the language costs, in compile time, run time and memory, on this machine, on this date.**

**That page is what the owner will read. Make it readable without the rest.**
