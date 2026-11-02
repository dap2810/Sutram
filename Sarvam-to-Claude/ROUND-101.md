# Sutram — ROUND-101: measure the memory claim, then build what the design says

**Base:** main at v283 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on v283, counting lines not truncating

**1M allocations, no block: 164 ms, exit 0, correct.** **1M allocations, in a block: 40 ms, exit 0, correct.** So a block is 4x faster at a million allocations, and neither crashes.
**I could NOT measure peak RSS.** `/proc` polling returns zero (the process finishes in under 200 ms); `ulimit -v` fails both versions so it does not discriminate. **The claim "a block bounds memory" has NO measurement behind it - only speed evidence.**
**`chakra i = 0 tak 3.0` -> REFUSED, `E_CHAKRA_DASHAM`.**
**`dasham avg = 15 / 4` -> `3.000000`** - integer division before the store, same as C.

## Your R100 verdict is accepted: NO, and the installer is the reason

**Two blockers, installer v243 first.** **I am not arguing with it.** **This round is memory, because that is the design work and it can proceed in parallel with the Windows build.**

## WS1 - the measurement I could not make
**I cannot read peak RSS.** `/proc` polling returns zero because the process finishes in under 200 ms; `ulimit -v` fails both versions so it discriminates nothing.

**Build the harness that does it: fork, `wait()`, read `ru_maxrss`.** **A small C or Python wrapper in `tools/`.**

**Then measure and report:**
- **1M allocations with a block - peak RSS**
- **1M allocations without a block - peak RSS**
- **10M allocations with a block - does it stay flat?**
- **A loop that grows a `kosh` 100,000 times - how much is abandoned?**

**Four numbers.** **The claim "a `mandapa` block bounds memory" currently has only speed evidence behind it, and this project has learned what unmeasured claims cost.**

## WS2 - and the growth leak, which is measured but unfixed
**A `kosh` that cannot extend in place copies and abandons the old buffer.** **Nothing frees it.**

**Two options:**
- **Extend in place always, by reserving slack on growth** - costs memory up front, removes the leak.
- **Free the old buffer when it is provably unreachable** - requires the aliasing fix first.

**Which is cheaper, and what does it cost per push?**

## WS3 - and the aliasing decision, which now gates reuse
**`vitti a = k` diverges on relocating growth. Documented, latent, 3 aliases in the tree, 0 hitting the condition.**

**A forwarding pointer costs 3 instructions and 8-16% per read - your R85 measurement.** **That was too much for v1.0.**

**But if reuse is impossible without it, the trade changes: 8-16% on reads, against bounded memory for long-running programs.**

**Price both, and say which you would ship.**
