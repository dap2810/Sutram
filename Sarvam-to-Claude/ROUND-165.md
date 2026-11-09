# Sutram — ROUND-165: you now own the Windows folder. Clean it.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**The Windows AI is not available.** **Its folder is 67 MB, 60% of the repository, and it carries the owner's personal system details in 371 files.**

**So you own it now.** **Treat it as your own channel: keep what is cited, normalise what identifies, and record what you changed.**

**This does not replace ROUND-164 - it is the Windows half of it, stated separately because it is the largest part.**

---

## WS1 - and the personal paths come first

**371 files in `Windows-to-Sarvam/` carry `C:\Users\<account>`, `C:\Users\<computer name>` or `<drive>:\<projects folder>\Sutram`.**

**Replace, mechanically:**
- **`C:\Users\<account>` and `C:\Users\<computer name>` -> `%USERPROFILE%`**
- **`<drive>:\<projects folder>\Sutram` -> `<repo>`**
- **exact OS build numbers -> "Windows 11 Home, November 2026"**

**And check three things before you start, because each would make the replacement break something:**

**1. Is a path inside a SHA-256 preimage?** **If a manifest hashes a file that contains a path, changing the path breaks the manifest.** **Find every such case first.**
**2. Is a path a JSON key rather than a value?** **That is a structural change, not a text one.**
**3. Is a path inside a filename?** **Then the file itself needs renaming, and every link to it breaks.**

**Report each case you find, and what you did.**

## WS2 - and then the evidence, by the rule you already applied

**You counted 4,424 files and found 4,365 cited.** **So there is little to delete - but the 59 uncited are worth naming, and the JSON snapshots that carry a path are worth replacing with a hash and the number the report needs.**

**Not a purge.** **A normalisation.** **The claims must survive; the machine identity must not.**

## WS3 - and the gate
**`R159 no personal paths`** **- fail if any tracked file contains a home directory, a username, a drive letter outside the repo, or an absolute path to a build machine.**

**It must fail on the tree before this commit.** **A gate that passes first time has not been tested.**

**And check it against the Windows folder specifically, since that is where 371 of the 361... are.**

## WS4 - and the honest limits, stated in the report

**1. This cleans the tree. A fresh clone of this commit is clean. `git log -p` still shows the old strings.**
**2. Only a history rewrite removes them from history, and it would break the owner's Windows clone.**

**Do not claim the exposure is gone.** **Say what is fixed and what is not.**

**And note: the repository is public and has been, so the strings have already been visible.** **Fixing the tree stops future clones carrying them; it does not undo that.**

## WS5 - and the memory work, which does not wait

**a. The compiler overwriting its input - after Tuesday, not before.**
**b. The chapter's false sentence: "grows each time you add" -> "grows only when it is full".**
**c. And the sentence I measured: *"a block gives memory back when it ends - a loop inside a block does not."*** **200,000 allocations inside one block peak at 15,996 KB; the same work with no block peaks at 15,416. Only 1,000 sequential blocks show the win: 13,256 against 15,708.**
**d. State the program behind 49,920 / 392 KB. My programs give 13,256 / 15,708.**
**e. `parimana()` counts capacity, not length. Say so.**

**The owner has asked for memory to be finished. That is the work; the cleanup is the housekeeping.**
