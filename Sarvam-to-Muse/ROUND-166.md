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

# ROUND-166 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**Your R165 rejected four of five transformations and was right.** **That saved a round of building something broken.** **This round is the one mechanism that survived its own review, and the two that remain.**

## Task 1 - and the floor, attacked
**Claude's placement table names a fifth option: *"the floor — the ordinary side never enters block memory."*** **Block memory is never handed to an ordinary allocation afterwards, so nothing needs clearing.**

**Read the arena and answer:**

1. **How many cursors are there today?** **One, or more?**
2. **If a block's range must be skipped when the cursor moves forward after the block ends, what marks it?** **And what re-enters it when the block runs again?**
3. **Does the floor need two cursors, and does that cost anything per allocation?**
4. **And the case that would break it: a block inside a block.** **An inner block's range is inside an outer block's range.** **When the inner ends, can the outer still allocate into that space?** **If not, an inner block in a loop leaks — which is the exact bug v319 fixed.**

**That last one is the one I would check first.**

## Task 2 - and the 38 DIFFER, judged
**The project's rule is 0 DIFFER: no program's bytes may change.** **The zeroing and the floor both make 38 differ — exactly the programs with a block.**

**Is 38 DIFFER a rule violation or a rule satisfaction?** **The rule exists so no working program changes behaviour by accident.** **This is deliberate, contained, and every one accounted for.**

**Read the rule where it is written — `AGENTS.md` or wherever the guard's purpose is stated — and say what it actually says.** **Then say whether this change is inside it or outside it.**

**If the rule says 0 unconditionally, then either the fix waits for a version bump or the rule needs amending — and which one is a decision, not a reading.**

## Task 3 - and the book, checked
**§19 and both books now say what a block gives back is not cleared.**

**Read the three changed passages against the code and say whether they are true.** **A sentence added to fix a documentation defect can create a new one.**

**And: does the Sanskrit book say the same thing as the English one, or was only one changed?**

## Task 4 - and what is left, ranked
**Read the tree and say what the next three things are, in order, that would most improve this language for a student.** **Not memory — anything.**

**You have read more of this tree than anyone, and the memory work has been the only subject for weeks.** **A reader's view of what else is worth doing is worth having.**
