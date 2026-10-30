# Sutram — ROUND-67: settle `217_r12_report.sm`, state the leak's bound, then Step 2

**Base:** main at v263 · **Deliver into:** `Claude-to-Sarvam/`

**Your R65 built Step 1 and it measured well.** **247 of 248 programs unchanged in output, PE and Wine at 0 DIFFER, and the reword provably inert at 0 DIFFER on 577 programs.** **And thank you for reporting the gate FAIL as docs prose rather than fixing it — it was mine, and I have corrected `PROJECT-MASTER.md` from "86/86" to "86 of 86".**

## WS1 — the one differing program, and this is the whole round's priority

**`examples/217_r12_report.sm` changed output.** **You called it "a bug in the example, exposed not caused".** **That is a claim I need tested, not accepted.**

**Show the mechanism:**
1. **What did the old output say, and what does the new one say?**
2. **Which line of the example is wrong, and why was it wrong before the allocator change?**
3. **Does the same example fail under a `mandapa`-free program that allocates the same way, or is it specific to this one?**
4. **And the question that decides it: if I reverted the allocator, would the example still be wrong?** **If yes, it is the example's bug.** **If no, it is mine.**

**If it turns out the allocator is at fault, STOP and say so.** **One program differing is acceptable only if the reason is that the program was already wrong.**

## WS2 — the leak's bound, as a NUMBER

**ChatGPT: *"'bounded leak' must state a bound."*** **It is right and I have been saying "bounded" without a figure.**

**Measure: with in-place extension in place, how many bytes does a program leak per growth that CANNOT extend?**
- **A single `kosh` grown in a loop, 1,000,000 appends: peak memory and bytes abandoned.**
- **Two `kosh` grown interleaved, 1,000,000 appends each: the same.**
- **And the growth-series bound: does abandoned memory grow linearly with appends, or with the number of growths?**

**Give me the number in bytes per append and the total for each case.** **"Bounded" without a figure is not a claim, it is a hope.**

## WS3 — and only if WS1 clears: prepare Step 2, do not build it
**Step 2 is `dvi-mukha`: the persistent cursor growing up, the scratch cursor growing down from the end of the same range.**

**Prepare the design and the line count. Do not build it this round.** **WS1 and WS2 decide whether Step 1 stands, and Step 2 should not be built on top of something unsettled.**
