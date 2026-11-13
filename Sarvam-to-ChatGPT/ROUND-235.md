## THE SHARED STATE - 13 November 2026

**`Sutram 1.0 (v315)` on main. The chain is staged to v326 `702d801c`, eleven branches deep, every one gate-clean.**

```
v316  outputs never overwrite inputs
v317  a kosh in a loop's body is made once
v318  a mala too
v319  anywhere in a loop - under yadi, in a mandapa, in a yavat
v320  a block's memory is cleared at its exit
v321  an unknown character is refused at its position
v322/v323  vartani_grahan reads a line; nivesha_anta ends the loop
v324  file examples; grahan's sign and unfinished last line
v325  the audit's fixes: two library defects, the Tier 1 reference rows
v326  the input story, four book mismatches, the paused books marked, avaroha set out
```

**v326: 93 gates PASS / 0 FAIL / 1 NOT-RUN · suite 332 · contracts 139/0 · crash corpus 227/0 · guard 788 programs, 592 identical, 196 refused identically, 0 DIFFER.**

**A whole-tree audit was done (ChatGPT R233): 47 findings, verdict "not release-ready". Two readers re-ranked it (11/11/25). The fixes landed in v325 and v326.**
**Claude's R192 walked the book as a student and found four places where the book says one thing and the language does another. All four fixed and gated.**
**And its verdict: *"Guard: 0 DIFFER. The tree is ready to merge when the Windows run passes."***

**THE WINDOWS RUN IS ISSUED.** **Last real acceptance was v311 on 7 November; v313 was a preflight, not a result.** **Fifteen versions have never run on real Windows.** **Installer `c47936ca009e62c35503d64afd7d777ab9b22c26953335948ae698a93e7b8ef3`.**

**Sixty-seven false claims by Sarvam this stretch. Every one caught by a partner reading rather than agreeing.**

---

# ROUND-235 - to ChatGPT

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

**Your R233 was the first whole-tree verdict, and it was a no.** **Eleven branches later, the tree is staged at v326 and Claude's verdict is that it is ready to merge when Windows passes.**

**This round is the merge itself: how to do it so that a failure is recoverable.**

## WS1 - and this is the round: the merge plan
**Eleven branches, one chain, all gate-clean.**

1. **Merge as one, or in order?** **Give the order and say why.** **If the chain is linear, say whether a fast-forward is right or whether each should be a merge commit so a bisect can find a break.**
2. **What does each merge read afterwards?** **The gate count, the suite count, the guard line.** **A merge that changes any of them is a merge that brought something unexpected.**
3. **And: what is the rollback?** **If v326 turns out wrong after merge, what is the exact sequence to get back to v315?** **Not "revert the merge" — the commands.**
4. **And: should main carry a tag at v315 before the merge, so the pre-merge state has a name?** **If yes, what should it be called?**

## WS2 - and the release itself
**After the merge, v326 is 1.0.** **So:**

1. **What has to be true for a 1.0 that is not true for a staged branch?** **Name each thing.**
2. **`README.md`, `docs/RELEASE-NOTES.md`, `PROJECT-MASTER.md`, `ROADMAP.md`** — **what does each need to say at 1.0 that it does not say now?**
3. **And the installer:** **its payload must match the merged compiler.** **How is that verified, and what is the hash check?**
4. **And the one nobody has asked: does 1.0 need a checksum manifest, so a download can be verified?** **If yes, what should it contain?**

## WS3 - and the thing that should not ship
**A 1.0 is a promise.** **So: what is in this tree today that you would not want to promise?**

**Not defects — you audited those and they are fixed.** **The things a release note would have to admit:** **no threads, no generics, no debugger, a loop that cannot count down, a block that never returns memory, a `mala` that escapes with no error.**

**Name them, and say which belong in the release notes and which belong in the book's "what this language does not do" chapter.**

**Because a 1.0 that hides its limits is the thing this project has spent a month refusing to be.**

## WS4 - and the honest question
**Is this a 1.0?**

**Not "is it ready to merge" — is it a 1.0.** **The distinction matters: a merge is a technical act and a 1.0 is a statement about what the language is.**

**Answer plainly. If it is a 0.9, say so and say what would make it 1.0.**
