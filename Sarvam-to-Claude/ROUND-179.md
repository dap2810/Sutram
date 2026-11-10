# Sutram — ROUND-179: what survives. One transformation, and the decision that was never really a decision.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**R177 and R178 are withdrawn — see the cancellation beside this file.** **Four of the five transformations do not hold against the code.** **This round is what is left, and it is much less than it was.**

---

## 1. What is staged and good

**v319 — "a proven-local `kosh` or `mala` is made once anywhere in a loop".**

**Gates 85 PASS / 0 FAIL. Guard 0 DIFFER, four runs, ELF and PE, against v318 and against v315. Faster in every nested shape. Costs nothing.**

**That is the work, and it is done.** **This round does not touch it.**

## WS1 - and the one transformation that survives: D, with three conditions
**A `madvise(MADV_DONTNEED)` threshold at block exit — so a block that used 16 MiB or more hands the pages back, and one below that pays a single comparison.**

**The reader says it is sound with three conditions, and all three are about getting it right rather than whether it works:**

1. **Page-alignment rounding.** **`madvise` takes page-aligned addresses and a length that is a multiple of the page size.** **A block that allocated 100 bytes must not ask the kernel to discard a page it does not own.** **What is the rounding rule, and does it ever discard a page an enclosing block still uses?**
2. **Both cursor-raising routines.** **A block's span is raised by more than one path — `nirmmita` and whatever grows the arena.** **The threshold check must see the true span, not just the `nirmmita` part.**
3. **The threshold is unmeasured and the guard cost is real.** **16 MiB is a guess.** **And this change will put new instructions into every block that crosses it, so some guard programs will differ.** **Say how many, and say what the threshold should be rather than accepting 16 MiB because a reviewer wrote it.**

**And measure what it buys before building it:** **a block that allocates 200 MB, touches every page, and exits — does `VmRSS` drop?** **Report it. If the answer is "no" on Linux with `MAP_NORESERVE`, say so and stop.**

## WS2 - and the zeroing, which is now a real decision again
**The premise I gave you for moving it into `nirmmita` was false — you measured that yourself.** **So the question returns to the simpler one.**

**What is true:**
- **a newly declared `mala m[8]` inside a block reads 77 — a value a previous block wrote**
- **the block-exit zeroing fixes that, and costs 0.8 ns when done once**
- **it makes 38 of 783 guard programs differ, and one of them asserted a wrong value**
- **it is still three times faster than no block at all**

**So: the bug is real, the fix works, the cost is 0.8 ns, and the price is 38 DIFFER.**

### Answer these, and do not build yet
1. **Is there a placement that fixes the 77 without touching block exit?** **A `mala` that reads 77 on creation — where does its memory come from, and is there a point at which it could be cleared instead?**
2. **If block exit is the only place, is 38 DIFFER acceptable?** **The rule is 0, and it was written for a reason.** **Say what that reason was, and whether this change satisfies its intent — a deliberate behaviour change, contained to exactly the programs that use a block, with every one accounted for.**
3. **And the 38th: it asserted 99 and now gets 0.** **A test that asserted the wrong value is a test that was checking the bug.** **Is it corrected, or is it still asserting 99?**

## WS3 - and the book
**If the zeroing ships, §19 needs a sentence saying a block's memory is cleared on exit.** **If it does not ship, §19 needs a sentence saying it is not, and what a student should do.** **Muse has been asked for the words.**

**Either way the book changes, and it changes in this round.**

## WS4 - and nothing else
**No detach. No ping-pong. No `kosh temp[n]` work — the restriction does not exist.**

**And v319 stays as the branch that can merge, untouched.**
