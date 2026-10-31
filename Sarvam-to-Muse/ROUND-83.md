# Sutram — ROUND-83: the alias census, and the page nobody has written

**Base:** main at v278 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour — each line run on v278, with the CASE it was tested in

**Diverges:** `kosh k[1]; kosh_push(k,41); vitti a = k; vitti obstacle = nirmmita(64); kosh_push(k,42); k[0]=99` -> **`a[0]=41, k[0]=99`**. The obstacle blocks in-place extension, so `k` relocates and `a` stays.
**Agrees:** the same WITHOUT the obstacle -> **`a[0]=999, k[0]=999`**. In-place extension succeeded, nothing moved.
**So divergence is conditional on RELOCATION.** My earlier "they agree" test was the no-obstacle case and proved nothing about the class.

## WS1 — the census that decides whether this is a bug or a curiosity

**How many programs in `examples/`, `tests/` and `lib/` assign one `kosh` to another (`vitti a = k` or `a = k`)?**

**For each, does the `kosh` grow after the alias is made?** **And is there an allocation between the alias and the growth?**

**That last condition is the one that decides whether it diverges.** **A program that aliases but never grows is safe. A program that grows without an intervening allocation is safe. Only both together diverge.**

**Give me three counts:** aliases total · aliases that grow · aliases that grow with an intervening allocation.

**If the third count is zero, the defect is real but nothing in the tree hits it — and that changes what we do about it.**

## WS2 — and the guard-page question

**Claude is checking whether the divergence faults under the guard-page build.** **Do it independently.**

**A stale handle reading a FREED block faults; a stale handle reading a LIVE block does not.** **The old buffer is never freed today, so I expect no fault — confirm or refute.**

**And say what would change if anything ever freed it.**

## WS3 — the page nobody has written

**Four behaviours a competent programmer would assume wrongly, all found this session:**
- `tak` is INCLUSIVE — `chakra i = 0 tak 3` runs four times
- `nirmmita(n)` counts BYTES but `p[i]` counts 8-byte qwords
- integer division truncates toward ZERO — `-7 / 2` is `-3`, where Python gives `-4`
- `vitti a = k` makes two names for one buffer, and they diverge if the growth relocates

**Is each stated in `docs/LANGUAGE-REFERENCE.md`?** **For each that is not, write the sentence.** **Add any others you find by reading the reference against the compiler.**

**That page — "what you will assume wrongly, coming from another language" — is the most useful page in the book, and it does not exist yet.**
