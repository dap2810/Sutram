## THE SHARED STATE - 10 November 2026, Tuesday. WINDOWS TESTING DAY.

**`Sutram 1.0 (v315)` on main · gates 80 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `6f9cdbda02164cb521aa853ea920f60dd77d871eb2e70b32da3130b1ebb05018`.**
**v316 is STAGED on branch `r163-output-collision` at `315660ec`, not merged: it refuses `sutram hello.sm hello.sm` and changes nothing else (guard: 783 programs, ELF and PE both 587 identical / 196 refused identically / 0 DIFFER).**

**FIRM STANDING INSTRUCTION: never write the owner's system details into this repository.** **No home directory, no username, no drive letter or absolute path outside the repo, no machine name, no OS build number, no hardware detail, no IP or MAC address, no screenshot filename that encodes a path.** **Write `%USERPROFILE%`, `<repo>`, `%TEMP%`, "Windows 11 Home, November 2026".** **A path is evidence; a username is not.**

### The privacy work is done, and it took two attempts
**Claude normalised 806 files, then found that the gate it reported as passing could not read 21 UTF-16 files or a WSL kernel version - 36 files still carried system details.** **The hardened gate found them.**
**Now: `R159 no personal paths` - 10,844 of 10,844 tracked files inspected, 0.**
**I verified the tree myself: 0 home directories, 0 usernames, 84 MB (down from 110 MB).**
**And the honest limit, which must stay stated: this cleans the tree. `git log -p` still shows the old strings. Only a history rewrite removes them and it would break the owner's Windows clone.**

### The chapter and the memory document
**The book's chapter 19 now says what a block gives back, three ways, each measured on v315 first: `nirmmita` written in it, yes; a `kosh` made in it, no; a `mala` made in it, never - and returning that `mala` is not refused.** **`agrim` is among the ways a block ends, and a budget counts rounded-up bytes.**

**And `docs/MEMORY-MODEL.md`: of 49 claims checked, 39 hold, 3 wrong, 4 imprecise, 2 stale, 1 unverifiable.** **The three wrong ones are all in the status box the document calls "the current model":**
- **`mandapa` "gives back what it allocated", unqualified - a `kosh` and a `mala` are both allocated in a block's text and neither is given back**
- **the descriptor is listed with THREE fields and no size - and a reader counting them gets 24 bytes by arithmetic. That is where my wrong number came from. The code has four fields, 32 bytes, or 56 with R82.**
- **the slice-walk attributed to the wrong version**

### The seven manifests are a liability, not a record
**None was regenerated and nothing reads any of them.** **Of 3,089 recorded entries: 2,817 match, 215 mismatch, 57 missing.** **The 215 are exactly accounted for - 210 changed by the normalisation, 5 by build-number redactions.** **The 57 missing are all screenshots.**

### The design decisions
**Scope rewind: rejected - needs an owner-aware design with generational handles, prototyped separately.** **`nirmmita`: checked buffers for teaching, raw pointers explicitly advanced.** **`vibhakti`: deferred to v1.1 - "named-argument readability, not a new ownership proof".** **Compiler self-overwrite: a file-identity class, ten ways, staged.**

### The honest record
**Forty-six false claims by Sarvam.** **The most recent: a file count of 361 when it was 526; a repo-path count of 276 when it was 272; a brief that carried the username it forbade; and a block measurement that measured the shell's environment rather than the program.**

---

# ROUND-167 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

## WS1 - and today is the day v316 can land
**The condition was: do not ship code changed since the last native run.** **v316 is staged and tested.**

**So: is it safe to merge today?** **Answer with what the owner must run to accept it, in order, as a checklist he can tick.**

**Not a narrative. A list: command, expected output, and what it proves.**

**And if you would rather wait for a native run of v315 first, say so - that is a legitimate answer and it costs one day.**

## WS2 - and the memory model document
**Muse checked 49 claims: 39 hold, 3 wrong, 4 imprecise, 2 stale, 1 unverifiable.**

**Fix all ten.** **And the three in the status box matter most, because that is the part a reader trusts:**
- **`mandapa` gives back what it allocated - unqualified. Three kinds are allocated in a block's text and only one is given back.**
- **the descriptor with three fields and no size - which is where 24 bytes came from. Give the four fields, 32 bytes, and 56 with R82.**
- **the slice-walk attributed to the wrong version.**

**And add the check to `R158 doc currency`: a field list with no size is a size nobody wrote and everybody computes.**

## WS3 - and the seven manifests
**Nothing reads them. 3,089 entries, 215 no longer match, 57 point at files that do not exist.**

**Two options: make a gate read them, or remove them and say what replaced them.**

**Which is right?** **A manifest that nothing verifies is a claim that nothing checks - and this project has spent two weeks learning what that costs.**

**If you keep them, regenerate and gate them.** **If you remove them, say what now proves what they claimed to prove.**

## WS4 - and the lock
**ChatGPT said A is only partially addressed: an empty unrelated file is still deleted, and there is a path replacement window between reading the stale lock and acting on it.**

**Fix both.** **And its design question is open with it, not with you - so wait for its answer if you can.**

## WS5 - and your footprint
**84 MB now, down from 110.** **What is left in your own channel that is a byte-identical copy or an uncited snapshot?** **The same rule you applied to the Windows folder.**
