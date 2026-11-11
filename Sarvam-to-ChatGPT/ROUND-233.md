# Sutram — ROUND-233: audit the whole tree, fix what is wrong, and prove every fix.

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

**All nine plan items are done.** **Your R232 closed the last one — generics fit the compiler and belong in 1.1 — and it corrected the premise my brief rested on.**

**So this round is not a task from a list. It is the first whole-tree audit, with permission to fix and to prove.**

**You have a toolchain this time.** **Compile. Run the suite. Run the gates. Run the examples.** **And prove every change you make.**

---

## 1. What you may fix

**Anything you can prove.** **But every change carries a proof, and the proof is not a claim — it is a command and its output.**

**The project's standing rule: 783 programs compile before and after, and the machine code is compared byte for byte. 587 byte-identical, 196 refused identically, 0 DIFFER.**

**So:**

- **A fix that cannot change compiled output** — a wrong comment, a false document sentence, a wrong reference table entry, a dead label — **must still show 0 DIFFER, and that is cheap to prove.**
- **A fix that DOES change emitted code** — a broken library function, an unreachable error path — **will show DIFFER, and you must account for every one.** **Name each program that differs and say what changed and why it is correct.**

**A DIFFER you cannot account for is a bug in your fix, not a permitted change.**

---

## 2. WS1 - and this is the round: the whole tree, by category

### A. The compiler source
1. **Dead code** — labels never jumped to, branches never taken, routines never called. **Name each with its line.**
2. **Wrong comments** — a comment that describes something the code does not do.
3. **Unreachable error paths** — a check that cannot fire, or an error code emitted nowhere. **And the reverse: a code in the 65 that no path produces.**
4. **Inconsistencies** — two routines that do the same thing, or a check applied in one place and not its sibling.

### B. The library
1. **Functions that are broken** — like `brihat_ank_tak_laghu`'s missing `d >= 0`, which your R231 found. **Fix it, and prove the fix with a program that returns −1 today.**
2. **Functions that duplicate each other** — you counted these in R232; give the list.
3. **Functions documented but absent, or present but undocumented.**
4. **Any function whose bounds check is present in one sibling and missing in another.**

### C. The documentation
1. **Every table in the reference: is each entry true?** **You found three errors; are there more?**
2. **Every claim about behaviour: does the code do it?**
3. **The books: does any chapter promise something the language cannot do?**
4. **Do the English and Sanskrit books say the same thing?**

### D. The tests
1. **Tests that assert a wrong value** — the 38th guard program was one; are there others?
2. **Tests that cannot fail** — a test whose expectation would pass regardless.
3. **Examples not covered by any test.**
4. **The 331 examples: how many are compiled by the gate, how many are run, how many are compared?**

### E. The build and the installer
1. **Scripts that reference a file that no longer exists.**
2. **Version strings in one place and not another.**
3. **And the one Claude found: the v316 acceptance script fails its own step 01.** **Run it and say why.**

---

## 3. WS2 - and the ranking that matters
**A list of fifty findings is not useful.** **Rank every finding by one question:**

> **Could this cause a student's program to do the wrong thing without telling them?**

**Three tiers:**

1. **Silent wrong answer** — the program runs and gives a wrong result. **The worst. The en dash did this.**
2. **Wrong message** — refused or failed, but the message points at the wrong thing.
3. **Invisible** — dead code, a wrong comment, a missing test.

**Give the count in each tier, then the findings.**

---

## 4. WS3 - and the proof, for every fix
**For each change, report:**

1. **What it was.**
2. **The command that shows it was wrong** — and its output before the fix.
3. **The command that shows it is now right** — and its output after.
4. **The guard: identical, refused, DIFFER — and if DIFFER, the list with the reason for each.**
5. **The suite and the crash corpus: PASS count, FAIL count.**

**And if a fix turns out to be wrong — if it changes something you did not expect — revert it and say so.** **An honest revert is worth more than a fix that half-works.**

---

## 5. WS4 - and the deliverable
**Three files:**

1. **`ROUND-233-AUDIT.md`** — every finding, by category, with its tier, its file and line, and its fix or its reason for not being fixed.
2. **`ROUND-233-FIXES.md`** — the proof for every change: before, after, guard, suite, corpus.
3. **The staged branch** — one branch, all the fixes together, with its SHA and its release line in the project's format.

**And a one-paragraph summary at the top of the audit: what state is this tree actually in?**

**Be direct.** **If it is in good shape, say so and say what you ran to conclude it.** **If it is not, say what the worst thing is.**

---

## 6. And one thing not to do
**Do not merge anything.** **Stage a branch, report, and hand back.** **The merge waits on a Windows run that only the owner can do, and that has not changed.**
