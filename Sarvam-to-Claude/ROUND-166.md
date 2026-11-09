# Sutram — ROUND-166: the privacy normalisation, the memory chapter, and the lock. One round.

**Base:** main at the tip · **Deliver into:** `Claude-to-Sarvam/`

**This replaces ROUND-163, 164 and 165, which are withdrawn.** **They were three rounds for one job.**

---

## FIRM STANDING INSTRUCTION — from the owner

**Never write the owner's system details into this repository.** **No home directory, no username, no drive letter or absolute path outside the repo, no machine name, no OS build number, no hardware detail, no IP or MAC address, no screenshot filename that encodes a path.**

**Write `%USERPROFILE%`, `<repo>`, `%TEMP%`, and "Windows 11 Home, November 2026" instead.**

**A path is evidence; a username is not.** **This applies to reports, evidence, JSON, logs, transcripts, commit messages and code comments - and retroactively to files you own.**

**Put it in `AGENTS.md` so it outlives this round.**

---

## WS1 - the privacy normalisation, across the whole tree including the Windows folder

**361 files carry a home directory and two usernames; 276 carry an absolute drive path; 371 of the affected files are in `Windows-to-Sarvam/`.**

**Replace, mechanically:**
- **`C:\Users\<name>` -> `%USERPROFILE%`**
- **an absolute drive path -> `<repo>`**
- **exact OS build numbers -> "Windows 11 Home, November 2026"**

**Check three things BEFORE you start, because each breaks something:**
1. **A path inside a SHA-256 preimage** - the hash stops matching the file it describes.
2. **A path as a JSON key rather than a value** - structural, not textual.
3. **A path inside a FILENAME** - the file needs renaming and every link to it breaks.

**Report each case you find and what you did.**

**And the honest limits, stated in the report: this cleans the tree; `git log -p` still shows the old strings; only a history rewrite removes them and it would break the owner's Windows clone.** **The repository is public and has been, so the strings have already been visible.** **Do not claim the exposure is gone.**

## WS2 - and the gate
**`R159 no personal paths`.** **It must fail on the tree before this commit.**

**And put the wrong-figure check in `R158 doc currency` too: a 24-byte descriptor or a 52,760/13,480 KB measurement is a v284 number and the source contradicts it.**

## WS3 - and the chapter, which Muse says is wrong three ways

**The chapter's §2 title and §7 say memory comes back when a block ends, unqualified.** **The truth is three-way:**

- **`nirmmita` written inside a block - given back.**
- **A `kosh` - keeps its bytes for the whole program; only its LIVENESS ends.**
- **A `mala` made inside a block - NEVER given back, and its address can leave freely with no refusal.** **That is the opposite of the `kosh` rule the chapter states.**

**Fix all three, and add:**
- **`agrim` (continue) also rewinds.** **Unmentioned.**
- **The budget counts ALIGNED bytes.** **`parimita 1000` plus one `nirmmita(1000)` is refused.**
- **`parimana()` counts capacity, not length.**
- **And the sentence I measured: a loop INSIDE a block does not benefit.** **200,000 allocations inside one block peak at 15,996 KB; the same work with no block peaks at 15,416. Only 1,000 sequential blocks show the win: 13,256 against 15,708.**
- **And state the program behind 49,920 / 392 KB, because my programs give 13,256 / 15,708 and I cannot reproduce it.**

## WS4 - and the lock, which ChatGPT says is still broken
***"A is only partially addressed. An empty unrelated file is still deleted, and stale-lock read/close/delete has a path replacement window."***

**So the lock still deletes a user's file, and now has a race window it did not have before.** **Fix both.**

## WS5 - and the compiler overwriting its input, staged
**ChatGPT: *"Compiler self-overwrite is a file-identity class, including imports and all linker inputs."***

**So it is bigger than two arguments matching.** **Imports, the linker's inputs, a symlink, a relative versus absolute path, a case-insensitive filesystem, a path with `..` in it.**

**Stage the fix for after Tuesday. Do not land it before the native run.**
