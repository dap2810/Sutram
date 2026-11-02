# Sutram — R171: MEMORY ONLY. The budget's cost, and the design's price table.

**Base:** main at v283 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified by me on v283, fork/wait4 harness, counting lines not truncating

**Peak RSS: 100k allocations no block 13,756 KB; 100k in a block 14,028 KB; 1M no block 64,652 KB; 1M in a block 14,576 KB.** A block is flat across a tenfold increase; a no-block loop climbs 4.7x.
**`kosh` pushes: 10k = 12,776 KB; 100k = 13,132 KB; 1M = 13,256 KB.** Essentially flat across a hundredfold increase. **This contradicts Claude R101's "about 100 MB" and I want the exact program behind that figure.**
**`chakra i = 0 tak 3.0` -> REFUSED, `E_CHAKRA_DASHAM`.**

## Your R170 design is accepted in shape. This round is its cost.

## WS1 - the price table, which your design did not have
**You specified stable descriptors, generation-checked handles, `kalpa` epochs, `visarjana` release, `parimita` budgets.** **I need the numbers before Claude builds any of it.**

**For each mechanism, per operation:**

| | instructions | bytes per object | effect on existing code |
|---|---|---|---|
| generation check on every access | ? | ? | ? |
| stable descriptor indirection | ? | ? | ? |
| `visarjana` on block exit | ? | ? | ? |
| `parimita` budget check | ? | ? | ? |

**Label each measured or estimated.** **If you cannot estimate one, say so - that is more useful than a guess.**

## WS2 - and the one that decides whether we build it at all
**A `parimita` budget check is one compare against a counter at each allocation.** **That is cheap. Confirm or correct that.**

**If the budget alone closes gap 1 - bounded memory without reuse - then it is worth building now and the rest waits.**

**What does the budget NOT solve?** **Name it precisely, so I do not oversell it to the maintainer.**

## WS3 - and the Sanskrit, one word at a time
**`parimita` is the only new word this build needs.** **Confirm it:**
- **complete attested word?**
- **collides with nothing in `lang/sanskrit.lang`, `lib/`, or `examples/`?**
- **typeable - eight letters, is that acceptable?**
- **does "measured, limited" describe an enforced byte budget better than any alternative?**

**And reject your own word if it fails any test.** **You rejected `ananta` on exactly that basis and it was the best judgement in the round.**
