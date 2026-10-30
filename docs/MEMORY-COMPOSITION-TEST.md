# The composition of the five memory steps — tested, all five pass

**Run by me, 30 October 2026, on the shipped v270 compiler.** **This is the test nobody had run: each step was verified alone, and the joins were not.**

---

## The five tests

| # | Composition | Expected | Got | |
|---|---|---|---|---|
| **1** | **a block inside a loop, writing into a `kosh` declared OUTSIDE** | `0 1 2` | **`0 1 2`** | **pass** |
| **2** | **a scratch pointer passed to a `prakriya` that returns a derived VALUE** | allowed, `42` | **`out=42`** | **pass** |
| **3** | **two sibling blocks in sequence** | `first=111 second=222` | **`first=111 second=222`** | **pass** |
| **4** | **a block allocating 64 MB, 1,000 times** | RSS stays at one block | **67,484 KB peak — one 64 MB block** | **pass** |
| **5** | **recursion 500 deep, a block in every frame** | `125250` | **`sum=125250`** | **pass** |

**Test 5's number is the check that matters: 0+1+2+...+500 = 125,250.** **Exact.** **So the per-frame mark holds under recursion — which was the specific thing I was worried about, because a mark that is not per-frame would corrupt the scratch cursor silently and the escape check would not see it.**

**Test 4's number is the other one: 64 MB is 65,536 KB, and peak RSS was 67,484 KB after 1,000 allocations of 64 MB each.** **So the block released every one of them — 64 GB of cumulative allocation, 64 MB of actual memory.**

---

## What this establishes

**The five steps compose.** **Persistent and scratch memory coexist in the same function; a block can write into an outer `kosh`; two blocks in sequence do not see each other; a scratch pointer can be used and its value returned; the scratch range is reused; and recursion keeps a separate mark per frame.**

**That was the last untested claim in the design.**

---

## And the honest limits, which the tests also showed

**Test 4 took 9.39 seconds for 1,000 iterations — 9.4 ms each.** **That is not the allocator; it is touching 64 MB of fresh pages once per block.** **The allocation is still 2–8 ns; the memory is the cost.** **A program that allocates a large block in a hot loop will be slow for the same reason it would be slow in C.**

**And the `kosh`-of-scratch-pointers hole is unchanged and untested by all five of these.** **None of my five tests put a scratch pointer into a container, because that is the escape the check cannot see.** **A test that passed it would prove nothing except that the hole exists.**

---

## One process note, in my own interest

**The sandbox was recycled between rounds and I had deleted my NASM copy cleaning up disk space, so I could not rebuild the compiler.** **I used the prebuilt `sutram_compiler` binary from the repo instead — which is the right artefact to test anyway, because it is the one that ships.**

**But it means these five results are on the binary in the tree, not on a rebuild of the source in the tree.** **If those ever diverge, these numbers describe the binary.** **Claude's rounds rebuild from source; mine did not, and that difference should be stated rather than glossed.**
