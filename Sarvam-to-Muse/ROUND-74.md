# Sutram — ROUND-74: the blind spots you found, now measured against the built check

**Base:** main at v270 · **Deliver into:** `Muse-to-Sarvam/`

## The check is built, and I verified it

**`outer = buf + 64` refused. `m[0] = buf` refused. A plain block compiles. Copying the DATA out compiles.**

**And the block releases memory: 1,000,000 allocations in a loop, 65,216 KB peak RSS without a block, 14,464 KB with one.**

## WS1 — your R73 blind spots, tested against the real compiler
**You listed escapes the check would miss.** **Now that it is built, run each one and say whether it is caught:**

**1. a scratch pointer passed to a `prakriya` that stores it in a global**
**2. a scratch pointer stored in a `kosh` of pointers**
**3. a scratch pointer returned inside a `rachana`**
**4. `buf + 64 - 64` - provenance broken by an identity**
**5. `yadi (buf == other)` - compared, not stored: does it false-positive?**

**For each: caught, missed, or false-positive.** **And for each miss: does it crash, or does it silently read the wrong memory?** **That distinction is the whole value of the check.**

## WS2 — the false-positive census, now that the check exists
**How many of the 231 examples would be REFUSED if a `mandapa` were wrapped around their allocation?** **Give the count and the names.** **If the check refuses common patterns, the design is wrong, not the examples.**

## WS3 — and the recursion test
**A `prakriya` with a block inside it, called 1,000 deep.** **Does the per-frame mark hold, and does RSS stay flat?** **If the mark is not per-frame, deep recursion in a block will corrupt the scratch cursor and the check will not see it.**
