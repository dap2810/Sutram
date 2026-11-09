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
- **`C:\Users\dmech` and `C:\Users\Dhruv` - 361 files**
- **`E:\Github_Projects\Sutram` - 276 files**
- **`Windows 11 Home build 26300` and other exact build numbers**
- **371 of the affected files are in `Windows-to-Sarvam/`; 2 in ChatGPT's, 1 in Muse's; none in `docs/` or Claude's**

**No email, no credentials, no tokens, no IP address.** **It is a privacy exposure, not a security breach.**

---

# ROUND-157 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

## Task 1 - and the privacy fix is the urgent one
**The repository is public and carries the owner's Windows username and drive path in 361 files.**

**Claude is replacing `C:\Users\<name>` with `%USERPROFILE%` and `E:\Github_Projects\Sutram` with `<repo>`.**

**So: read the tree and find every place that replacement would break something.**

**Specifically:**
- **a path inside a SHA-256 preimage** - the hash would stop matching the file it describes
- **a path used as a JSON key rather than a value** - a structural change, not a text one
- **a path inside a command whose output is the evidence** - the command becomes unreproducible
- **a path inside a URL or a link** - the link breaks
- **a path that appears in a filename** - the file itself would need renaming

**That last one is the one I would miss.** **Name every file whose NAME contains a personal path.**

## Task 2 - and the memory chapter, continued
**You checked the claims the brief named.** **Now the rest.**

**And the one I measured: a loop INSIDE a block does not benefit - 15,996 KB against 15,416 without a block; only 1,000 sequential blocks show the win, 13,256 against 15,708.**

**Does the chapter say which pattern benefits?** **If not, a student will wrap a loop in a block and watch memory grow.**

## Task 3 - and the wrong figures
**The tree may still carry a 24-byte descriptor or the v284 measurement.** **Name every file and line that does.**

**Claude needs the list, and `R158 doc currency` should hold it afterwards.**
