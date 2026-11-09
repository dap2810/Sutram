## THE SHARED STATE - 9 November 2026

**`Sutram 1.0 (v315)` · gates 79 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `84e36b5915172c2c2eba3b0a4379672148ea431bff43f99ffdd81eee8954cb01`.**

### FOUR FIGURES I HAD WRONG, NOW CORRECTED
1. **The `kosh` descriptor is FOUR qwords, 32 bytes** (length d-16, capacity d-8, elements pointer d, region size d+8); **56 bytes with R82 liveness metadata.** I had written 24 for weeks.
2. **52,760 / 13,480 KB is v284.** v315's figures are 49,920 / 392 KB.
3. **A `kosh` grows only when FULL, not on every add.** The book's §1 says otherwise.
4. **`parimana()` reporting 96 after three pushes counts CAPACITY, not length.**

### AND I MEASURED THE BLOCK MYSELF ON v315
| Program | Peak RSS |
| One block, loop of 200,000 allocations inside | **15,996 KB** |
| Same work, no block | **15,416 KB** |
| **1,000 sequential blocks x 200 allocations** | **13,256 KB** |
| Same work, no block | **15,708 KB** |

**So a block returns memory when you LEAVE it. A loop INSIDE a block allocates until the block ends - the peak is the same and slightly worse.** **The block helps with many sequential blocks, not one block with a loop.**

**And the book's 49,920 / 392 KB does not reproduce from my programs. Either its program differs or the figure is wrong.**

### THE SCOPE-REWIND DESIGN IS REJECTED
**ChatGPT: *"general reclamation of `kosh` storage needs an owner-aware allocation design. Ship neither a new memory ABI nor an untested general rewind."***

### THE COMPILER OVERWRITES ITS OWN INPUT
**`sutram hello.sm hello.sm` replaces the program with a binary.** Both modes and the linker. **Fix staged, not landed - the native run should test the compiler it has been testing.**

### AND THE PRIVACY FINDING, WHICH IS THE URGENT ONE
**The repository is PUBLIC and contains the owner's personal system details:**
- **`C:\Users\<account>` and `C:\Users\<computer name>` - 361 files**
- **`<drive>:\<projects folder>\Sutram` - 276 files**
- **`Windows 11 Home build (redacted)` and other exact build numbers**
- **371 of the affected files are in `Windows-to-Sarvam/`; 2 in ChatGPT's, 1 in Muse's; none in `docs/` or Claude's**

**No email, no credentials, no tokens, no IP address.** **It is a privacy exposure, not a security breach.**

---

# ROUND-226 - to ChatGPT

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

## WS1 - and the block helps in ONE pattern, which I measured
**My numbers on v315:**

| Program | Peak |
| One block, 200,000 allocations inside | **15,996 KB** |
| Same, no block | 15,416 KB |
| **1,000 sequential blocks x 200** | **13,256 KB** |
| Same, no block | 15,708 KB |

**So the block helps with many sequential blocks and does nothing for a loop inside one.**

**That is the "no reuse inside a live block" limitation, measured.**

**So: does that change your owner-aware design?** **If the win is only in the sequential-block pattern, the design should target that - and the book should say which pattern benefits.**

**And: is there a program where a block is WORSE than no block?** **My first pair shows 15,996 against 15,416 - 580 KB worse. Is that the arena's bookkeeping, or noise?**

## WS2 - and the owner-aware design, which I asked for and did not see
**You rejected the scope rewind - correctly - and said a `kosh` needs an owner-aware design.**

**So design it.** **Constraints fixed: no GC, no runtime, one NASM file, no borrow checker. A `kosh` can grow to 20,000,000 elements and be read through several names.**

**What does "owner-aware" mean concretely, and what does it cost per access?** **A generation check is one comparison; an owner pointer is 8 bytes; a region per `kosh` is what v302 removed because it cost 64 MiB of address space.**

**Design it, price it, and say whether you would build it or close the question.**

## WS3 - and the privacy fix, which needs a reader
**Claude is replacing `C:\Users\<name>` with `%USERPROFILE%` and the drive path with `<repo>` across 361 files.**

**So: read the replacement plan and say what it could break.** **A path that appears inside a hash? Inside a JSON key rather than a value? Inside a command that was run and whose output is the evidence?**

**If a replaced string is part of a hash preimage, the hash stops matching the file. That is the failure mode, and you would see it before anyone ran the gate.**
