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

# ROUND-164 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

## WS1 - and this is urgent: the personal paths
**The repository is public and carries the owner's Windows username and drive layout in 361 files.**

**The replacement is mechanical and must preserve every claim:**

- **`C:\Users\<account>` and `C:\Users\<computer name>` -> `%USERPROFILE%`**
- **`<drive>:\<projects folder>\Sutram` -> `<repo>`**
- **exact OS build numbers -> "Windows 11 Home, November 2026"**

**The evidence keeps its meaning; only the identifier goes.** **`%USERPROFILE%\AppData\Local\Programs\Sutram\bin\sutram.exe` says exactly what the absolute path said.**

**Do it in `.md` and `.json` across the whole tree, and state the count of files changed.**

## WS2 - and a gate, so it cannot come back
**`R159 no personal paths`.** **Fail if any tracked file contains a home directory, a username, a drive letter outside the repo, or an absolute path to a build machine.**

**And make it fail on the tree before this commit, so we know it works.**

## WS3 - and the honest limits
**Say both of these in the report:**

**1. This cleans the current tree.** **A fresh clone of this commit is clean. `git log -p` still shows the old strings.**
**2. Only a history rewrite removes them from history, and that breaks every existing clone - including the owner's Windows clone.**

**Do not claim the exposure is gone.** **Say what is fixed and what is not.**

## WS4 - and the memory work, which continues
**a. The compiler overwriting its input - after Tuesday, not before.**
**b. The chapter's false sentence: "grows each time you add" -> "grows only when it is full".**
**c. And the sentence I measured: *"a block gives memory back when it ends - a loop inside a block does not."* The chapter must say it, or a student will wrap a loop in a block and watch memory grow.**
**d. And state the program behind 49,920 / 392 KB. My programs give 13,256 / 15,708 KB. A number in a book with no program behind it is a claim, not a measurement.**
**e. And `parimana()` counts capacity, not length. Say so.**
