# Sutram — ROUND-98: MEMORY ONLY. The allocation census, which is the number that decides urgency.

**Base:** main at v283 · **Deliver into:** `Muse-to-Sarvam/`

## Verified by me on v283, fork/wait4 harness, counting lines not truncating

**Peak RSS: 100k allocations no block 13,756 KB; 100k in a block 14,028 KB; 1M no block 64,652 KB; 1M in a block 14,576 KB.** A block is flat across a tenfold increase; a no-block loop climbs 4.7x.
**`kosh` pushes: 10k = 12,776 KB; 100k = 13,132 KB; 1M = 13,256 KB.** Essentially flat across a hundredfold increase. **This contradicts Claude R101's "about 100 MB" and I want the exact program behind that figure.**
**`chakra i = 0 tak 3.0` -> REFUSED, `E_CHAKRA_DASHAM`.**

## Nothing else this round. The three counts, and the vocabulary for one word.

## WS1 - the three allocation counts, which I have asked for twice
**Script the tree, read every candidate by hand, run the decisive cases - your method.**

1. **How many programs in `examples/` and `lib/` allocate inside a loop?**
2. **How many grow a `kosh` more than 1,000 times?**
3. **How many allocate without a `mandapa` block at all?**

**If all three are near zero, the memory gaps are theoretical for our own code - exactly as the 3-1-0 alias census settled that question.** **That is the number that decides whether the budget is urgent or documentary.**

## WS2 - and one word only: `parimita`
**ChatGPT proposes `parimita` - "measured, limited" - for a `mandapa` byte budget.**

**Four tests: complete word not fragment; no collision anywhere in the tree; typeable and memorable; and does its literal meaning describe an enforced budget rather than translate the English word "limit"?**

**Search the tree for collisions and give me the count of hits.** **Then say yes or no.**

## WS3 - and your `dasham -> mala` finding
**You reported it stores 0.** **I measured `4613937818241073152` for `3.0` - the IEEE bit pattern, not zero.**

**Which path did you test?** **Give me the program.** **Either your reading or mine is wrong, and the difference matters: "stores zero" and "stores the raw bits" are different bugs with different fixes.**

**Do not soften this. One of us is wrong and I would rather find out now.**
