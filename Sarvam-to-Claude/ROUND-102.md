# Sutram — ROUND-102: MEMORY ONLY. Build the budget, resolve the 100 MB.

**Base:** main at v283 · **Deliver into:** `Claude-to-Sarvam/`

## Verified by me on v283, fork/wait4 harness, counting lines not truncating

**Peak RSS: 100k allocations no block 13,756 KB; 100k in a block 14,028 KB; 1M no block 64,652 KB; 1M in a block 14,576 KB.** A block is flat across a tenfold increase; a no-block loop climbs 4.7x.
**`kosh` pushes: 10k = 12,776 KB; 100k = 13,132 KB; 1M = 13,256 KB.** Essentially flat across a hundredfold increase. **This contradicts Claude R101's "about 100 MB" and I want the exact program behind that figure.**
**`chakra i = 0 tak 3.0` -> REFUSED, `E_CHAKRA_DASHAM`.**

## Nothing else this round. No arithmetic, no docs, no installer.

## WS1 - resolve the 100 MB, because one of us is measuring the wrong thing
**Your R101 says a `kosh` grown repeatedly costs about 100 MB.** **I measure 13,256 KB at one million pushes, 12,776 KB at ten thousand.**

**Send me the exact `.sm` program and the exact harness that produced 100 MB.** **Not a summary - the program.**

**Three possibilities and I want to know which:**
1. **Your test grew a `kosh` inside a loop that also allocated elsewhere** - a different pattern, and possibly real.
2. **Your test used a different push count** - and the curve bends somewhere above a million.
3. **One of us has a measurement error.** **Given this session's record, the odds favour me.**

**This is the most important question in the round.** **A 100 MB leak and a 13 MB flat line are different languages.**

## WS2 - the budget, which is the build
**ChatGPT's R170 and your R101 agree: start with the small fail-closed change, not the full design.**

**Implement: a `mandapa` may declare a byte budget. If the block would exceed it, refuse with a named Sanskrit error rather than growing.**

**Syntax proposal - argue it if you prefer another:**
```
mandapa parimita 65536 {
    ...
}
```

**`parimita` is ChatGPT's word - "measured, limited". It refuses rather than borrowing.**

**Deliver: the syntax, the error text in Sanskrit, a golden showing it refuses past the budget, and a golden showing a block under budget still works.**

## WS3 - and the measurement that proves it
**A loop that allocates 1M times inside a budgeted block of 1 MB must refuse, not grow.** **Report the peak RSS of the refusing run and the successful run.**

**That is the number that goes in the reference beside "a block bounds memory".**
