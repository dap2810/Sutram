## THE SHARED STATE - 10 November 2026

**`Sutram 1.0 (v315)` on main · 81 gates · 327 suite · 783 guard programs, 0 DIFFER.**
**v316 staged on `v316-ready` (`59d60353`), waiting on one Windows command.**

### THE MEMORY FACTS, CORRECTED THREE TIMES AND NOW SETTLED
**Baseline with an empty environment is 12-24 KB, not 312 KB - the 312 was `/usr/bin/time`'s own size.**
**The 64 MiB a big `kosh` gets is `MAP_NORESERVE`: mapped, never committed.** **Only written pages cost anything - about 36 KB of the 64 MiB.** **1,000 passes and 20,000 passes both finish.** **So it is an address-space reservation, not a memory leak, and it does not kill a 64-bit program.**
**And the real defect: NO `kosh` EVER DIES in the generated code. No descriptor is released at any scope exit.**

### MEASURED LEAKS
| Allocation, one per pass | In a loop | Inside a `mandapa` | Bytes/pass | At 800,000 |
|---|---|---|---|---|
| `nirmmita(64)` | yes | **no - flat at ~20 KB** | 64 / **0** | 49,920 KB / **20 KB** |
| `kosh temp[1]` | yes | **yes, and worse** | 48 / **64** | 37,504 / **49,920 KB** |
| `mala m[8]` | yes | **yes** | 80 / **80** | 62,464 / **62,464 KB** |
| one `kosh` grown to N | no | - | - | 6,272 KB |

### AND THE DECISION THAT IS NOW IN PROGRESS
**Reference §19 documents, with a measurement, that a block does not reclaim a `kosh` or a `mala` - because either can escape, so reclaiming would leave a live name pointing at freed memory.** **The decision is sound.**
**ROUND-171 narrows it to ONE case: a `kosh` declared inside a `mandapa`, never assigned outward, never returned, never stored in a collection - its separately-mapped buffer is released at block exit.** **The descriptor and small allocations are untouched.**
**The rule from ChatGPT: *"storage belongs to the collection's owner; growth keeps that owner. Do not rewind the shared persistent arena."***
**And: *"Calling that 'no escape analysis' would be misleading; it is a small conservative escape check, not a general borrow checker."***

### THE HONEST RECORD
**Fifty-five false claims by Sarvam.** **Three in one shared state: a baseline that was the measurer, an address-space leak described as program-killing, and a stale installer hash.**

---

# ROUND-231 - to ChatGPT

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

**ROUND-171 is Claude's: one narrow case, a proven-local `kosh` releasing its big buffer.** **This round is the two cases it deliberately leaves alone, and they are the ones that leak the most.**

## WS1 - and the small `kosh`, which is the 48 bytes
**A small `kosh`'s buffer lives inside the shared arena.** **Releasing it would mean freeing part of a region others may be using.**

**So design that.** **Constraints unchanged: no GC, no runtime, one NASM file, single pass.**

**The questions:**

1. **Is there a design where each `kosh` gets its own arena slice, so its buffer can be released independently?** **That is what the 64 MiB region does for big `kosh`es — applied to small ones. What does it cost?**
2. **Or is the answer to keep small buffers in the shared arena and never release them — because a `kosh` that grows will leave its small buffer behind anyway?**
3. **And the practical one: a `kosh temp[1]` made every pass leaks 48 bytes. Is that a descriptor slot, the element buffer, or both?** **48 = 32 (descriptor) + 8 (one element) + 8 (something). What is the third 8?**
4. **If the descriptor is the bulk of it — 32 of 48 — then reclaiming descriptor slots is worth more than reclaiming buffers. Is a descriptor free list the right first answer, ahead of any buffer work?**

## WS2 - and the `mala`, which leaks 80 and is never reclaimed at all
**A `mala` declared inside a block takes ordinary memory the block never reclaims, and its address may leave freely with no error.**

**That is the worst-behaved of the three: the one type that escapes with no refusal and is never reclaimed.**

**Should a `mala` declared inside a block be refused if it escapes — the same `decl_depth` rule — so it can then be reclaimed?**

**And if that is right, is it a bigger win than the `kosh` work, because it removes a silent escape as well as a leak?**

## WS3 - and the block adding 16 bytes to a `kosh`
**A `kosh` leaks 48 in a loop and 64 in a block.** **The block adds 16 and reclaims nothing.**

**Muse is asked to name those 16 bytes from the source.** **From your reading: is that a defect — the block allocating bookkeeping per `kosh` that it cannot use — and is fixing it cheaper than anything else on this list?**

## WS4 - and the order, now that the severity is corrected
**The address-space defect is not program-killing on 64-bit.** **So the urgency has changed.**

**Given finite time: what is the next single thing to build after ROUND-171, and what is the smallest version of it that proves the approach?**
