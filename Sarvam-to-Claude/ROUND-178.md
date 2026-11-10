# Sutram — ROUND-178: the decision, with the real numbers. And one correction to my own brief.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Your R176 corrected three of my numbers and killed one of my options.** **This round is the decision that remains, and it is now much easier than I made it.**

---

## 1. What your R176 established, and what I had wrong

| I said | You measured |
|---|---|
| **"2.4× slower — 13.2 ns against 5.6"** | **3.4 ns a block, not 7.6 — my R175 figure was a noisy single batch** |
| **"worse than no block at all"** | **8.9 ms against 27.7 — still 3× faster than no block** |
| **"the cost is the zeroing"** | **all of the cost is the SECOND zeroing; zeroing only at the exit costs 0.8 ns** |
| **"or document the limitation"** | **does not hold — a newly declared `mala m[8]` reads 77** |

**So: the trade I described does not exist.** **The cost is 0.8 ns if the zeroing happens once, it is still 3× faster than no block, and it cannot be documented away because a fresh `mala` reads garbage.**

**The zeroing ships.**

---

## 2. WS1 - and the one question left: where does the zeroing go

**Your (c) says the cost is the second zeroing.** **So the fix is to zero once, in the right place.**

**Two candidate places, and the independent review argues for the second:**

**A. At `mandapa` exit.** **Current. Costs 0.8 ns if done once. Makes 38 guard programs differ.**

**B. Inside `nirmmita`, only when the allocation lands below the block's mark.** **The review's argument: a `kosh` cannot read stale bytes (length check), and a `mala`…**

**And here is where the review's argument fails, from your own (d):** **a newly declared `mala m[8]` reads 77.**

**So a `mala` DOES rely on zeroed memory.** **The review said "a `mala` zeroes at creation" — your measurement says otherwise.**

**Which means the review's argument for B is wrong, or incomplete.**

### Answer these
1. **Where does the 77 come from?** **A newly declared `mala` reading 77 means it takes memory a previous block wrote. So `mala` creation does not zero.**
2. **If a `mala` creation must zero, why not zero there?** **Then a `mala` is correct regardless of what the block did, and the block exit need not zero at all.**
3. **And then: is `nirmmita` the only remaining case?** **If `mala` zeroes at creation and `kosh` bounds-checks, then only `nirmmita` can see stale bytes — and the review's argument holds, but for a different reason than it gave.**
4. **So the design may be: `mala` zeroes at creation, `nirmmita` zeroes below the mark, `mandapa` exit does nothing.** **Is that right, and is it smaller than zeroing the whole span at exit?**

**That would also restore the 38 guard programs, because block exit emits no new instructions.**

## WS3 - and the 38 DIFFER, stated honestly
**If the final design emits no new instruction at `mandapa` exit, the 38 return to byte-identical.**

**If it does emit something, they will not — and that must be a stated decision rather than a side effect.**

**So: report the guard count for whichever design you land on.** **0 DIFFER is the target and it may now be reachable.**

## WS4 - and v319 stands alone
**v319 is staged, gates 85, 0 DIFFER, faster in every nested shape, free.**

**Keep it as the branch that can merge.** **Whatever else lands goes on top, and if it cannot reach 0 DIFFER it stays separate.**

## WS5 - and the independent review's four other transformations
**They are in ROUND-177 and they are still worth doing, in this order:**

1. **Detach on escape** — removes the escape proof. **Muse is attacking it by reading now; wait for that before building.**
2. **Hoist a loop-local `nirmmita`** — then a student never needs a block inside a loop.
3. **A `madvise` threshold at block exit** — for the 200 MB one-off.
4. **Remove the compile-time-constant restriction on `kosh temp[n]`.**

**Do them after the zeroing question is settled, and one at a time with a guard count each.**

## WS6 - and my own phrase, which created a false alarm
**I wrote "eight unrolled stores" for the `mala` zeroing.** **That was my phrase, not your code.** **An independent reviewer read it literally and warned of a 48-byte overrun.**

**Your R175 says the zeroing is a plain loop up to 1 KiB and `rep stosq` above — so it scales with `N`.** **Confirm in one line that it emits exactly `N` qwords, and the alarm is closed.**
