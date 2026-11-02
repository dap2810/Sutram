# Sutram — ROUND-97: audit the five names, and the census number I still do not have

**Base:** main at v283 · **Deliver into:** `Muse-to-Sarvam/`

## Your R96 was delivered and read. This is the next round.

## Verified behaviour - run by me on v283, with a fork/wait4 harness

**Peak RSS: 100k allocations no block 13,756 KB; 100k in a block 14,028 KB; 1M no block 64,652 KB; 1M in a block 14,576 KB.** So a block is flat across a tenfold increase and a no-block loop climbs 4.7x.
**Claude R101 adds: the block holds `nirmmita` flat at 10 million, but NOT `kosh` - about 100 MB.**

## WS1 - the five names ChatGPT proposed, audited by you
**`kalpa` (epoch) · `visarjana` (release for reuse) · `parimita` (finite budget) · `ananta` (unbounded - it rejects this as a mode) · `kalpasmriti` (generation-bearing handle, a compound of kalpa + smriti).**

**For each, answer four things:**
1. **Is it a complete attested word, or a fragment?** (The project rule: `paripurna` to `purn` loses `pari`.)
2. **Does it collide with any existing keyword, library function, or `.sm` identifier?** Search the tree.
3. **Is it typeable and memorable for a student whose first language is not Sanskrit?** Count the letters and say plainly if it is too long.
4. **Does its literal meaning describe the thing, or is it an English concept wearing Sanskrit clothes?**

**And one more I want your view on: is `samskara` a better word than `kalpasmriti` for a generation-bearing handle?** `samskara` is the latent trace a thing carries from a previous state - which is what a generation IS. **If you think it is better, say so and argue it.**

## WS2 - and the census numbers I have asked for twice
**Three counts, from your method - script, then hand-read every candidate, then run the decisive cases:**
1. **How many programs in `examples/` and `lib/` allocate inside a loop?**
2. **How many grow a `kosh` more than 1,000 times?**
3. **How many allocate without a `mandapa` block at all?**

**If all three are near zero, the memory gaps are theoretical for our own code - exactly as the 3-1-0 alias census settled that question.** **That is the number that decides whether the `kosh` leak is urgent or documentary.**
