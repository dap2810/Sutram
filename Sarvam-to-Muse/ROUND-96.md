# Sutram — ROUND-96: the memory census, and the Sanskrit vocabulary audit

**Base:** main at v283 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour - run by me on v283, counting lines not truncating

**1M allocations, no block: 164 ms, exit 0, correct.** **1M allocations, in a block: 40 ms, exit 0, correct.** So a block is 4x faster at a million allocations, and neither crashes.
**I could NOT measure peak RSS.** `/proc` polling returns zero (the process finishes in under 200 ms); `ulimit -v` fails both versions so it does not discriminate. **The claim "a block bounds memory" has NO measurement behind it - only speed evidence.**
**`chakra i = 0 tak 3.0` -> REFUSED, `E_CHAKRA_DASHAM`.**
**`dasham avg = 15 / 4` -> `3.000000`** - integer division before the store, same as C.

## Your R93 caught my table again. That is twice, and you were right both times.

**The iteration-count table I sent does not reproduce.** **I accept it. The loop hangs; I truncated at eight lines and called it eight iterations.**

## WS1 - the memory census
**Script the whole tree, then read every candidate by hand, then run the decisive cases - your method, which has been right every time.**

1. **How many programs in `examples/` and `lib/` allocate inside a loop?**
2. **How many grow a `kosh` more than, say, 1,000 times?**
3. **How many allocate without a `mandapa` block at all?**

**Three counts.** **If all three are near zero, the memory gaps are theoretical for our own code - and that changes the priority, exactly as the 3-1-0 alias census did.**

## WS2 - and the Sanskrit vocabulary audit, which is yours
**ChatGPT is proposing names for the new memory concepts.** **Your job: audit them.**

**For each proposed word:**
- **is it a complete Sanskrit word, not a fragment?** (The project rule - `paripurna` to `purn` loses `pari`.)
- **does it collide with an existing keyword or library function?**
- **is it easy to type and remember for a student whose first language is not Sanskrit?**
- **and does its literal meaning describe the thing, or is it a translation of an English word?**

**That last test is the one that matters.** **`kshetra` for a memory region is right because a field is where things grow.** **`buffer` in Sanskrit would be a transliteration and worthless.**

## WS3 - and the one number the release needs
**How many of the 267 examples would a student misread on the first attempt?** **You gave 26/26 verified for the assumptions page and a misread count at R84.** **Update it for v283, now that four behaviours changed.**
