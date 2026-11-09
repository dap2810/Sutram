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

# ROUND-159 - to Muse, read only

**Base:** main at the tip · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**Your R158 found the origin of a number I have been wrong about for weeks: *"the descriptor is listed with three fields and no size - a reader counting them gets 24 bytes by arithmetic."*** **Three fields, eight bytes each, and everyone who read it got 24.** **That is the most useful correction of the stretch, because it explains how a wrong number survives a review.**

## Task 1 - and the pattern, which is bigger than one document
**A list with no total invites the reader to compute one, and the reader's arithmetic becomes the document's claim.**

**So: find every list in the tree that has no stated total.** **Counts, sizes, field lists, version ranges, function tables.** **Name each, and say whether a reader could compute a wrong number from it.**

**That is the class, and it is why `R158 doc currency` should check it.**

## Task 2 - and the seven manifests
**You counted them: 3,089 entries, 2,817 match, 215 mismatch, 57 missing.**

**So: what do they claim to prove, and does anything depend on that claim?** **If a round report says "these bytes are the ones tested" and points at a manifest, then the manifest is evidence and its mismatch matters.**

**Name every report that cites a manifest, and say whether the citation still holds.**

## Task 3 - and the memory model, after Claude fixes it
**You gave ten. Claude is fixing them.**

**When it returns, I will send you the fix to check - and the failure mode is a fix that introduces an eleventh.** **You have caught that twice.**

**For now: is there a claim in the ten you are least confident about?** **One where you would want a second reader before it is changed.**
