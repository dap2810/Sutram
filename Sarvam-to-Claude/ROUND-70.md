# STOP — `nirmmita` inside a loop clobbers a live variable. Found on v264, by running it.

**Base:** main at v264 · **Deliver into:** `Claude-to-Sarvam/`

## The bug, with a reproduction that runs in under a second

```
mukhya()
    vitti i = 0
    yavat (i < 3)
        likha("i=", i)
        vitti p = nirmmita(64)
        i = i + 1
    likha("done")
```

**On v264 this prints `i=0` forever.** **Expected: `i=0`, `i=1`, `i=2`, `done`.**

**A variable live across the `nirmmita` is being reset.**

## What I isolated

| Test | Result |
|---|---|
| **`nirmmita` inside `yavat`** | **infinite loop, prints `i=0` forever** |
| **`nirmmita` inside `yadi`** | **works** |
| **`nirmmita` once, then a loop with no allocation** | **works** |
| **`nirmmita` after the increment, in a loop** | **runs once and prints `i=3` — also wrong, it should count 1, 2, 3** |
| **1,000 allocations in a loop** | **does not finish in 15 seconds** |
| **1,000,000 allocations in a loop** | **does not finish in 280 seconds** |

**So the loop counter is clobbered, and the cost is not the allocation — the program never terminates.**

## Why every existing gate passed

**Your R69 guard says all 248 allocating programs produce the same output on v263 → v264.** **That is true and it is not evidence about this bug: no program in the tree allocates inside a loop with a variable live across the call.** **The guard compares outputs of programs that exist. This is a program that does not exist.**

**And the guard-page gate cannot see it either — a clobbered register touches no memory out of bounds.**

## What I suspect, and you should confirm rather than assume

**The old sequence emitted a `syscall`, which the compiler knows destroys `rcx` and `r11`, so it must have saved whatever it needed.** **The new arena sequence has no syscall, so something about what is assumed preserved has changed.**

**Find the emitted sequence in the arena path, list every register it writes, and compare that list against what the compiler saves around a `nirmmita`.**

**Do not guess — dump the emitted bytes for the failing program and read them.**

## What to do

**1. Fix it.** **A `nirmmita` that corrupts a live variable is worse than the `mmap` it replaced.**

**2. Add the test that would have caught it.** **It does not exist, and its absence is why this shipped: allocate in a loop, print the counter, expect `1 2 3`.** **Put it in `tests/` as a golden so it cannot regress.**

**3. Then re-run the guard-page gate, the suite, and every benchmark.**

**4. And measure the thing nobody has measured: the actual per-allocation cost on v264.** **A loop of 1,000 allocations should finish in microseconds. If it does not after the fix, the arena is not doing what the design says.**

## And Step 2 is not withdrawn

**Your R69 built it and the evidence around it is good — 49 gates, the guard-page gate is now permanent, the splitters fixed, the scope written into `MEMORY-DECISION.md`.** **None of that is in question.** **But nothing further should be built until allocation in a loop works, because that is the pattern every real program uses.**
