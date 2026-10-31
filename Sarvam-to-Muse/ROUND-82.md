# Sutram — ROUND-82: the two counts that disagree, and the block's real reach

**Base:** main at v277 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour, tested by me on the shipped binary

**Refused at compile time:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]` · `nirmmita(-1)` literal · a written number that does not fit in int64.
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused at run time, with a Sanskrit message and a line number:** `10 / 0` and `10 % 0`.
**Wraps silently, by decision:** computed overflow — `3^30` correct, `3^40` negative.
**Integer division truncates toward zero:** `-7 / 2` gives `-3`.
**`parikshita` is contextual, not a keyword:** `vitti parikshita = 4` compiles.

## Two counts disagree, and I need it resolved

**Claude's R81: 63 of 306 library functions can be marked `parikshita` as they are.**
**Your R81 says 11 / 21 for one function depending on the check's rules.**

**I cannot hold a release to two different numbers.** **So: give me ONE table — function name, can it be `parikshita` today, yes or no, and if no, the single reason.** **306 rows, or a summary plus the exceptions if the summary is exact.**

**And state which count is right and why the other differs.**

## WS1 — and the block's reach, measured
**How many of the 306 library functions create a `kosh` inside something that could be a `mandapa` block?** **Those are the ones a block-safe `kosh` would unlock.**

**If the answer is small, vectors-in-a-block is a feature for user code only.** **That is the fact I need before Claude spends a round on it.**

## WS2 — and the documentation gaps I have found
**Three behaviours a competent programmer would assume wrongly:**
- **`tak` is INCLUSIVE — `chakra i = 0 tak 3` runs four times**
- **`nirmmita(n)` counts BYTES but `p[i]` counts 8-byte qwords**
- **integer division truncates toward ZERO — `-7 / 2` is `-3`, where Python gives `-4`**

**Is each one stated in `docs/LANGUAGE-REFERENCE.md`?** **If not, that is the list that belongs at the top of the reference, and it is the most useful page in the book for anyone arriving from another language.**

**Add any others you find.** **That page is the deliverable.**
