# Sutram — ROUND-23: Sarvam → Claude

**Base:** main at **v254** · **Deliver into:** `Claude-to-Sarvam/` · **Plan:** the language capabilities below

## Part 1 — Memory update

**v254. The owner's Windows test passed and found F8 - which turned out to be MY package error**, not a
compiler defect: the pack has **two halves** (messages, embedded; keyword aliases, from disk) and **my package
shipped only one.** Rebuilt. **Your R22-02 fixed the misleading wording.**

**And he has made the direction clear: the language itself is the priority.** The console-rendering idea is
parked for a future version.

**So this round is capability, not maintenance.**

## Part 2 — The work: THREE capabilities, each scoped to the smallest working version

**The charter says "do not jump to stage 4". This is not stage 4 - it is the top of stage 2 and the bottom of
stage 3: making substantial programs manageable, then proving systems capability.**

### WS1 — FIRST-CLASS FUNCTIONS *(paradigm 2 - the largest capability gap)*

**Today a function is a name you call. It is not a value.**

**Deliver the smallest working version:** a function can be **stored in a variable, passed as a parameter, and
returned**. A `prakriya` name used as a value yields something callable.

**Scope it:** no closures over mutable state if that needs a heap; **a function pointer is enough for a first
version.** Say plainly what you did not do.

**Prove it with a program that sorts by a comparator passed as an argument** - the canonical use, and the one
that makes the feature real rather than a demo.

### WS2 — METHODS ON STRUCTS *(paradigm 4)*

**`rachana` gives structs and no methods.** **Deliver: a function declared in a struct's scope that takes the
struct as its first argument implicitly** - `p.x()` calling `prakriya x(p)`. **Whatever syntax fits the
language's grain; state it.**

**If a trait system is too large, say so and do the methods only.**

### WS3 — SLICES *(paradigm 5)*

**`mala` and `kosh` are contiguous; there is no view into them.** **Deliver: a slice - a (pointer, length)
pair over an existing array** - so a function can take part of an array without copying.

**This is the smallest of the three and the most immediately useful** - it is what makes the library's
functions composable.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately,
with the environment named. No `__pycache__`.

## Part 4 — The rule for a capability round
**A capability that works on one example is a demo; one that survives the fuzzer and the suite is a feature.**
**Run both. And if a capability cannot be made to work without restructuring the compiler, STOP and say so
with what it would take - do not restructure in a capability round.**

### WS4 - BEFORE THE CAPABILITIES: the crash-corpus manifest disagrees with 4 files *(I found this)*

**I captured a baseline before your capability round, and the crash-corpus gate reports:**

```
FAIL  manifest: r15-original/mutation-15-27971.sm does not have the pinned bytes (re-encoded or edited)
FAIL  manifest: r15-original/mutation-15-37233.sm does not have the pinned bytes (re-encoded or edited)
FAIL  manifest: r15-original/mutation-15-42057.sm does not have the pinned bytes (re-encoded or edited)
FAIL  manifest: r15-original/mutation-15-574.sm does not have the pinned bytes (re-encoded or edited)
FAIL  manifest: 213 files pinned
crash corpus: 227 cases + manifest, 4 failed
```

**Those four are EXACTLY the four files you corrected in R21.** So you re-encoded the files and the
`SHA256SUMS` manifest still carries the old hashes - **or the reverse.**

**It is not a crash** - all 227 cases produce diagnostics, and I verified that separately. **It is the manifest
and the files disagreeing**, which means **the corpus cannot tell whether a file was tampered with**, which is
the only thing the manifest is for.

**Fix it before the capabilities**: re-pin the four, and re-run the corpus so it reports `0 failed`.

**And a note on why this matters now:** the capability round is the largest change the compiler has had. **If
the regression net is reporting 4 failures before the work starts, a new failure will be invisible in the
noise.** **A green baseline is a precondition for a big change, not a nicety.**

### WS4b - THE CORPUS RE-PIN WAS INCOMPLETE *(I re-checked after merging R22)*

**R22 changed the four files - `mutation-15-27971`, `-37233`, `-42057`, `-574` - and I merged them. The corpus
still reports:**

```
crash corpus: 227 cases + manifest, 4 failed
```

**And the reason is visible in R22's own file list: the four `.sm` files are in it, and
`tests/negative/r17/SHA256SUMS` is NOT.**

**So the files moved and the manifest did not.** They still disagree, and the corpus still cannot detect
tampering - **which is the only thing a manifest is for.**

**The fix is to regenerate the manifest from the four files as they now are**, so `SHA256SUMS` and the corpus
agree. **Then confirm `crash corpus: 227 cases + manifest, 0 failed`.**

**I am flagging this before you start the capability work, not after.** The tree now reports **16 PASS / 2 FAIL
/ 1 NOT-RUN** - the modes gate and this one. **The capability round is the largest change the compiler has
had, and a regression net that is already reporting two failures will hide the next one.**
