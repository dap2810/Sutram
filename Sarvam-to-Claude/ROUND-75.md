# Sutram — ROUND-75: the three gaps, in priority order

**Base:** main at v272 · **Deliver into:** `Claude-to-Sarvam/`

## Where the memory work stands, measured

**Allocation 2-8 ns. A block releases memory - 65,216 KB down to 14,464 KB over 1,000,000 allocations. Five composition tests pass, including recursion 500 deep with an exact sum and 1,000 blocks of 64 MB at one block of RSS.**

**And three gaps, in the order I would fix them.**

## WS1 — `nirmmita(-1)` compiles and runs. I confirmed it.

```
mukhya()
    mandapa
        vitti p = nirmmita(-1)
        likha("got it")
```
**Prints `got it`.** **A negative size is accepted and the scratch cursor is moved backwards.**

**What does `nirmmita(-1)` actually DO to the cursor?** **Dump the emitted code and read it.** **If the cursor goes backwards, the next allocation in the block overlaps the previous one — a silent aliasing bug that the check cannot see.**

**Fix it: refuse a negative size at compile time where the size is a literal, and refuse a computed negative at run time with a Sanskrit error.** **Both, because a literal is the easy case and a computed one is the real one.**

## WS2 — the store check only inspects root statements
**ChatGPT found it; my test was inconclusive.** **So establish it first: does a store nested inside an expression get checked?**

**If it does not, that is a hole, because `out = (m[0] = buf) + 1` is one line of ordinary code.**

**Fix: walk the whole expression tree, not just the root.** **And add the golden that would have caught it.**

## WS3 — and the one that cannot be fixed, only stated
**A scratch pointer inside a `kosh` is invisible.** **ChatGPT has said so four times.**

**Do not attempt to fix it.** **Instead, make it impossible to do by accident if you can, and if you cannot, make the documentation unmissable:**
- **if a `kosh` of scratch pointers can be refused cheaply, refuse it**
- **if not, say in `docs/LANGUAGE-REFERENCE.md`, in the `mandapa` entry, in one sentence a beginner reads: a `kosh` created inside a block cannot be relied on to hold a pointer created in that block**

**And in the changelog, name it as a known limit rather than leaving it to be discovered.**

## WS4 — and the sentence I got wrong
**I proposed: "Sutram's memory is released by scope, checked at compile time, with no garbage collector and no runtime."** **ChatGPT: not true without qualification.**

**Corrected: "Sutram releases memory when a block ends, refuses the common escapes at compile time, and has no garbage collector and no runtime."**

**Put that sentence, and only that sentence, in `README.md`.** **And put the three known gaps under it, in plain words.** **A README that lists its own limits is worth more than one that does not.**
