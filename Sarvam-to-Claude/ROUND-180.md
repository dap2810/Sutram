## THE SHARED STATE - 10 November 2026

**`Sutram 1.0 (v315)` on main · ChatGPT held.**
**v319 `4c1159be` — "a proven-local `kosh` or `mala` is made once anywhere in a loop". Gates 85 PASS / 0 FAIL. Guard 0 DIFFER, four runs, ELF and PE. Faster in every nested shape. Costs nothing. THIS IS THE BRANCH THAT CAN MERGE.**
**v319 + three documents — §19 and both books now say what a block gives back is NOT cleared. Compiler bytes untouched, so the guard is identity.**
**v320 `9bb059ea` — the block-exit zeroing. 38 DIFFER, exactly the programs with a block. Not ready.**
**`madvise(MADV_DONTNEED)` — measured, works, NOT BUILT.** **274,880 KB -> 12,736 KB for 256 MiB.** **But 1.5 µs a page when the block runs again: a 16 MiB block in a loop goes 0.95 ms -> 7.2 ms.** **So a flat threshold is the wrong shape.**

### AND THE PLACEMENT TABLE, WHICH SETTLES WHERE THE CLEARING GOES
| Where the clearing goes | Programs whose bytes change |
|---|---|
| at a `mala`'s declaration | every program with a `mala` — and an ordinary `nirmmita` still reads stale data |
| in the ordinary allocation, always | every program that allocates, and every allocation pays |
| in the ordinary allocation, above a mark | every program that allocates |
| **at the block's exit** | **the 38 with a block** |
| **the floor — the ordinary side never enters block memory** | **the 38 with a block, and NO zeroing at the exit** |

**Every fix on the ordinary side changes more programs, because nearly every program allocates and few have a block. The 38 is the minimum.**

### THE BUG, PRECISELY
**A `mala m[8]` declared OUTSIDE any block, after a block had ended, read 77 — a value the block wrote.** **Inside a block a `mala` takes ordinary memory too, so the same could happen there, but that is not what was measured.**
**And the "0.8 ns when done once" figure came from a hand-patched program, not a build.**

### THE HONEST RECORD
**Sixty-three false claims by Sarvam.** **The most recent: passing an outside review's five transformations to be built without checking them against the code — four of the five did not hold.** **And two facts about the zeroing bug that Claude had to correct.**

---

# ROUND-180 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**The placement table answered the question.** **This round is the one decision it left, and it is between two mechanisms.**

## WS1 - and this is the round: the floor
**Your own table names it. *"The floor — the ordinary side never enters block memory."***

**That is not zeroing. It is partitioning: a block's memory is never handed to an ordinary allocation afterwards, so nothing can read it and nothing needs clearing.**

**It changes the same 38 programs, and emits no zeroing at the exit.**

**So: is it possible?**

1. **What does the arena look like today?** **One cursor, or more than one?** **If a block's allocations and ordinary allocations share one cursor, the floor means the block's range must be marked and skipped when the cursor moves forward after a block ends.**
2. **And what happens when the block runs again?** **The cursor must be able to re-enter that range — otherwise every pass of a loop allocates fresh memory past the previous block's, which is the leak we just fixed.**
3. **So the floor needs two cursors: one for ordinary allocation, one for blocks, and a block's range is reused by blocks and never by anything else.** **Is that what it amounts to?** **If yes, say so plainly — that is a real change to the arena and I want it named.**
4. **And the cost: does a second cursor cost anything per allocation?** **One comparison, or nothing?**

**Answer all four. Do not build yet.**

## WS2 - and then choose, with the numbers
**Two mechanisms:**

**A. Zero the block's range at exit.** **38 DIFFER. Costs what a measured build says, not the hand-patched 0.8 ns. Simple.**
**B. The floor — two cursors, block memory never reused by the ordinary path.** **38 DIFFER. No zeroing. A structural change to the arena.**

**Which is smaller, which is safer, and which would you rather maintain?**

**And answer the question I asked and did not get: is 38 DIFFER acceptable?** **The 0-DIFFER rule exists so that no working program changes behaviour by accident.** **This change is deliberate, contained to exactly the programs with a block, and every one accounted for.** **Does that satisfy the rule's intent, or does the rule mean 0 no matter what?**

**That is a judgement, and I want yours.**

## WS3 - and the 38th program
**It asserted 99 and now gets 0 — it was checking the bug.**

**Is it corrected to assert 0, and is that the right value?** **Or was the program doing something legitimate that the fix broke?** **Answer, and fix it if it is wrong.**

## WS4 - and v319 stays untouched
**It is gates 85, 0 DIFFER, free, and mergeable.** **Whatever lands goes on top, and if it cannot reach an acceptable guard it stays separate.**

**And the documents branch — §19 and both books now say what a block gives back is not cleared.** **If the floor lands, that sentence changes again. Note it; do not write it yet.**
