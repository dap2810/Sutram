# Sutram — ROUND-85: the alias is real, and now decide what to do about it

**Base:** main at v278 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour — each line run on v278, with the CASE it was tested in

**Diverges:** `kosh k[1]; kosh_push(k,41); vitti a = k; vitti obstacle = nirmmita(64); kosh_push(k,42); k[0]=99` -> **`a[0]=41, k[0]=99`**. The obstacle blocks in-place extension, so `k` relocates and `a` stays.
**Agrees:** the same WITHOUT the obstacle -> **`a[0]=999, k[0]=999`**. In-place extension succeeded, nothing moved.
**So divergence is conditional on RELOCATION, not on aliasing itself.** My earlier "they agree" test was the no-obstacle case and proved nothing about the class.

## Your R84 was right and my withdrawal was wrong

**You said two names DO diverge, and gave five cases of six across Linux ELF, PE under Wine and the guard-page build.** I reproduced it with ChatGPT's witness.

**And your recommendation - do not reopen the recycling bins - now rests on evidence rather than my mistaken premise.** I accept it.

## WS1 — decide: refuse, copy, or document

1. **Refuse `vitti a = k` when both are `kosh`** - a compile error naming the copy. How many programs in the tree does that break?
2. **Deep copy** - correct, expensive, surprising.
3. **Document it** - two names share one buffer; a relocating growth leaves the older name behind.

**If option 1 breaks zero programs, do it. If it breaks some, report the count and the programs and do nothing else this round.**

## WS2 — the fix I want priced, not built

**The divergence happens only because relocation is silent.** A forwarding pointer in the `kosh` header would let a stale handle follow the move.

**Price it: how many instructions on `k[0]`, and does it worsen the 11% generation-check cost?** Under three instructions and it may be cheaper than a language rule. **Do not build it.**

## WS3 — and one verification

**Run your five-of-six divergence cases against the guard-page build.** A stale handle reading a freed block faults; a stale handle reading a live block does not. **Say which these are.**
