# Sutram — ROUND-57: the last two pieces, and they close the vocabulary work

**Base:** main at **v410**, compiler **v261** · **Deliver into:** `Claude-to-Sarvam/`

## What is left, and it is only two things
**The 20 library names are renamed (v261, guard 0 DIFFER nine times).** **`nivartanam` is everywhere.** **The pack is fixed.**

**Two artefacts remain unapplied:**

1. **`Muse-to-Sarvam/ROUND-56-patchA.patch`** - **the 12 variable names declared 3+ times.** **Muse's own words: "Apply this alone and the suite still passes. This is the recommended patch."**
2. **`ChatGPT-to-Sarvam/ROUND-130-COMMENTS.md`** - **33 comment lines as a TSV.** **A comment cannot break a program.**

**And one thing I am deliberately NOT applying: `ROUND-56-patchB.patch`** - **the 96 names declared 1-2 times.**
**Muse called it "the churn set".** **Renaming a variable used twice has no reader benefit and produces a 40 KB diff.** **Skipped.**

---

## WS1 - Patch A
**Apply `ROUND-56-patchA.patch` with `git apply`. If it rejects, STOP and report which hunk.**
**Then: suite PASS=225, proofs 226/226, guard 0 DIFFER** - **a variable name never prints, so any differ is a bug.**
**And answer Muse's own question: after this, does a beginner reading `examples/01_hello.sm` still meet an English word?** **If yes, name the file.**

## WS2 - the 33 comments
**ChatGPT's TSV has `file | function | comment_line`.** **Its application rule is the one to follow:**
> *"Insert its proposed `#` comment immediately above the declaration ONLY after checking whether Muse already added an equivalent comment. Prefer replacing/reconciling duplicate existing contract comments rather than stacking inaccurate prose."*

**So: for each of the 33, check whether a comment already exists above that `prakriya`.** **If one exists, reconcile - do not stack two.**
**Say how many you inserted, how many you reconciled, and how many already had an adequate comment.**

**Then the suite again.** **A comment cannot change a binary, so the guard must still read 0 DIFFER - that is the proof the comments did not break a parse.**

## WS3 - the two I could not settle
**`sadish_yoga` computes a dot product.** **ChatGPT's R130 was asked whether any reading makes that correct.** **Read its verdict and, if the rename stands, say so plainly in the changelog entry you propose.**

## Return
`R57-00-HANDBACK.md` with: the patch result · the suite, proofs and guard · **the Muse question answered with a file name or "no"** · **the comment counts (inserted / reconciled / already adequate)** · and anything surprising.
