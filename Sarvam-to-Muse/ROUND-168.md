## THE SHARED STATE - 11 November 2026

**`Sutram 1.0 (v315)` on main · chain staged: v316 -> v317 -> v318 -> v319 -> v320 -> v321 (87 gates, unknown character refused).**
**Memory done: 825 MB -> 20 KB, three times faster. Item 1 of the three next things is finished.**

### AND A SPEED COMPARISON WAS ATTEMPTED AND COULD NOT BE FINISHED
**Measured on the sandbox, best of three, arithmetic loop of 10,000,000 iterations:**
| Language | Time |
|---|---|
| **Sutram** | **13.9 ms** |
| **Node 20** | **162.4 ms — 11.7x slower** |
| **Python 3.12** | **2,640.3 ms — 190x slower** |

**And building a list of 1,000,000 and summing it: Sutram 19.0 ms, Node 226.9 ms, Python 286.5 ms.**

**But the sandbox has NO gcc, NO clang, NO rustc, NO go, NO JDK.** **So there is no measured comparison against C, C++, Rust, Go, Java or Zig — and any table claiming one would be a lie.**

**And the honest expectation, which must be stated: Sutram has no optimiser. No inlining, no vectorisation, no loop unrolling, no register allocation beyond the trivial. GCC with `-O2` does all four. So on real numeric code Sutram should LOSE to C, and the gap should grow with the size of the loop body.** **The two scenarios above are simple enough that the difference is small, which flatters Sutram.**

### WHY THIS MATTERS FOR THE PROJECT
**The owner has asked for a comparison several times, and each time it was answered with a caveat.** **A proper one needs: the compilers, idiomatic programs in each language rather than transliterations, scenarios that are not simple loops, and a statement of what is being compared.**

---

# ROUND-168 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run — and that is exactly why this round is yours.**

**You cannot benchmark. Claude can, if its environment has the compilers. But a benchmark is only as good as the scenarios, and choosing them is a reading task.**

## Task 1 - and this is the round: what should be measured, and what would be dishonest
**The project has two measured rows: a 10-million arithmetic loop and a 1-million list build.** **Both are simple loops, and both flatter a compiler with no optimiser.**

**So: read the language and the library and name the scenarios where Sutram would be measured fairly — and the ones where it would not.**

**For each scenario, say:**

1. **What it measures** — the loop, the collection, the string handling, the call overhead, the I/O.
2. **Whether an optimiser would change the answer.** **If GCC's `-O2` would vectorise or inline it, the comparison measures the optimiser rather than the language — and that should be said rather than hidden.**
3. **What the fair equivalent is in C, in Rust, in Go.** **Not a transliteration — what a competent programmer in that language would actually write.**
4. **And what Sutram's structural disadvantage is in that scenario, if any.** **No optimiser. No threads. Bounds checks on every `kosh` read. A descriptor indirection on every access.**

**The scenarios I would start with, and you should disagree if I am wrong:**

- **arithmetic in a loop** — measured already, and it flatters Sutram
- **a hot loop over a large array** — where vectorisation decides everything
- **building a collection** — where C has `realloc` and Go has a slice
- **string concatenation in a loop** — where every language has a different answer and some are quadratic
- **a function call in a loop** — where inlining decides it
- **reading a file and summing numbers** — where I/O dominates and the language matters least
- **sorting 100,000 numbers** — where the algorithm matters more than the language, and saying so is worth doing

## Task 2 - and the one number nobody should publish
**The project's own claim is that it is fast.** **Read what the documentation says about speed, and say where it overstates.**

**If the reference or the book says "fast" without a measurement, name the sentence and the file.** **A language that claims speed it has not measured is doing the thing this project has spent weeks correcting.**

## Task 3 - and the compile-time advantage
**Sutram compiles in one pass with no optimiser.** **That should make it much faster to compile than GCC, Rust or Go.**

**Is that a real and defensible claim?** **What does a single-pass compiler cost, and what does an optimising one cost, per line?** **You have read this compiler; you know what it does and does not do.**

**If compile speed is a genuine advantage, it is worth stating — and it is the only speed claim this language can make without a benchmark.**
