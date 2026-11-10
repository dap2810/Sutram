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

# ROUND-162 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**Your R161 was exact: the address is in the descriptor, the growth path already frees with the two words a death-free needs, and the non-release is a documented decision at reference §19 rather than an oversight.** **That last finding changed the whole plan.**

## Task 1 - and the four conditions, attacked
**ROUND-171 reclaims one case. A `kosh` is reclaimed only if it is: declared inside the block, never assigned outward, never returned, never stored in a collection.**

**Your job: find the program that satisfies all four and still has a live pointer to the buffer.**

**Think about:**

- **a slice** — `vitti s = k[0:5]` inside the block, then `s` used after it. **Is a slice a name the four conditions do not cover?**
- **a `prakriya` called from inside the block that keeps the address** — the reference mentions this as *"the one way it gets in unseen"*
- **a `kosh` passed as a parameter to a `prakriya` that stores it in a module-level variable**
- **a `nirmmita` pointer that aliases the `kosh`'s buffer** — if that is possible at all
- **the `kosh` appearing in a `yadi` branch that does not run** — the flag would be set, so it is not reclaimed; that is safe but is it complete?
- **recursion** — the same `kosh` symbol at two depths

**Name the program, or say the four conditions are closed and why.**

## Task 2 - and the 16 bytes
**A `kosh` leaks 48 bytes a pass, 64 inside a `mandapa`.** **The block adds 16 and reclaims nothing.**

**What are those 16 bytes?** **Name the allocation, the line, and what it is for.**

**If it is bookkeeping the block allocates per `kosh` and never uses, that is a defect with a line number.**

## Task 3 - and reference §19, after the change
**§19 says today: *"A `kosh` of numbers used in a block works; its storage is ordinary memory, which the block does not reclaim."***

**After ROUND-171, that becomes true for most `kosh`es and false for the ones that escape.** **A sentence that is usually true is worse than one that is exactly true.**

**So: write the sentence §19 needs — one paragraph, stating which `kosh` is now reclaimed and which is not, and how a student can tell.** **Not a draft for approval; the actual words, so Claude can paste them.**
