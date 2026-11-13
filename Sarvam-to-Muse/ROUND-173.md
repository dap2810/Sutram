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

# ROUND-173 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.**

**Eleven branches are about to merge as one.** **Each has been checked against the branch beneath it, and every one reads 0 DIFFER against its parent.**

**But nobody has read the eleven together as one change.** **That is this round, and it is the last chance to catch something before it lands.**

## Task 1 - and this is the round: the whole chain, read as one diff
**Read `git diff v315..v326` on `src/` and `lib/` and answer:**

1. **Is there any place where two of the eleven changes interact?** **A guard that v321 added and v325 changed. A hoist that v319 widened and v320's clearing touches. A function v323 added and v325 fixed.**
2. **Is there any place where the ORDER matters** — **where merging them in a different order would produce a different compiler?**
3. **And the one I would check first: does v320's block-exit clearing interact with v319's hoist?** **A hoisted `kosh` lives in a slot the loop owns; a block's exit clears a range of the arena. If a hoisted allocation sits inside a range a block clears, the clearing would zero memory the loop still owns.**
4. **And: does anything in the chain assume the arena layout that v320 changed?**

**Name anything that reads wrong when the eleven are taken together, even if each was right alone.**

## Task 2 - and the guard's blind spot
**The guard compares 788 programs. 0 DIFFER across the chain, except the accounted-for sets.**

**So: what kind of defect would the guard not catch?**

**Not a general answer — the specific shapes. A change that alters behaviour only for a program shape that is not among the 788. A change that is correct for every program that compiles but wrong for one that is refused. A change that alters only the timing.**

**Name the shapes, and say which of the eleven changes could hide in one.**

## Task 3 - and the eleven descriptions
**Each branch has a one-line description in the release lines.** **Read the eleven and say whether each description is accurate** — **a description that overstates is a claim nobody checks, and this project has spent weeks correcting those.**

## Task 4 - and what a student gets
**Not the compiler. The student.**

**Eleven changes have landed. What can a student do today that they could not do on v315?** **Name it in their terms, not in the compiler's.**

**And: is anything in the eleven something a student would never notice, and was it worth the risk?**
