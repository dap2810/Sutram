# Sutram — ROUND-233: audit the whole tree. Fix what is trivial. Report what is not.

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

**All nine plan items are done.** **Your R232 closed the last one — generics fit the compiler and belong in 1.1, not 1.0 — and it corrected the premise my brief rested on.**

**So this round is not a task from a list. It is the first time anyone has asked for a whole-tree audit with permission to fix.**

---

## 1. What you may fix, and what you may not

**You are read-side. You cannot compile, cannot run the suite, and cannot run the gates.** **So a patch you write is untested, and an untested patch applied to a compiler that 783 programs depend on is a risk.**

**So:**

**You MAY produce patches for changes that cannot change compiled output.** **That means:**

- **a comment that is wrong**
- **a document sentence that is false**
- **a reference table entry that names the wrong function or the wrong width**
- **a dead label, an unreachable branch, a variable assigned and never read**
- **a library function that is present but never called, or called but absent**

**You MAY NOT produce patches for anything that changes emitted code.** **That means:**

- **any instruction sequence in `src/` that the emitter runs**
- **any library function's behaviour**
- **any error message the compiler prints**

**Those go in the report as findings for Claude, who can test them.**

**And say for every patch: "this cannot change compiled output because …"** **If you cannot complete that sentence, it is not a trivial patch.**

---

## 2. WS1 - and this is the round: the whole tree, by category

**Not every file — every category. Audit and report:**

### A. The compiler source
1. **Dead code** — labels never jumped to, branches never taken, routines never called. **Name each with its line.**
2. **Wrong comments** — a comment that describes something the code does not do. **This project has already found several.**
3. **Unreachable error paths** — a check that cannot fire, or an error code that is emitted nowhere. **And the reverse: a code in the 65 that no code path produces.**
4. **Inconsistencies** — two routines that do the same thing, or a check applied in one place and not its sibling.

### B. The library
1. **Functions that are broken** — like `brihat_ank_tak_laghu`'s missing `d >= 0`, which your R231 found.
2. **Functions that duplicate each other** — you counted these in R232; give the list.
3. **Functions documented but absent, or present but undocumented.**
4. **And: any function whose bounds check is present in one sibling and missing in another.**

### C. The documentation
1. **Every table in the reference: is each entry true?** **You found three errors; are there more?**
2. **Every claim about behaviour: does the code do it?**
3. **The books: does any chapter promise something the language cannot do?**
4. **And: do the English and Sanskrit books say the same thing?**

### D. The tests
1. **Tests that assert a wrong value** — the 38th guard program was one; are there others?
2. **Tests that cannot fail** — a test whose expectation would pass regardless.
3. **Examples not covered by any test.**
4. **And: the 331 examples — how many are compiled by the gate, how many are run, how many are compared?**

### E. The build and the installer
1. **Scripts that reference a file that no longer exists.**
2. **Version strings in one place and not another.**
3. **And the one Claude found: the v316 acceptance script fails its own step 01.** **Read that script and say why.**

---

## 3. WS2 - and the ranking that matters
**A list of fifty findings is not useful.** **So rank every finding by one question:**

> **Could this cause a student's program to do the wrong thing without telling them?**

**Three tiers:**

1. **Silent wrong answer** — the program runs and gives a wrong result. **The worst. The en dash did this.**
2. **Wrong message** — the program is refused or fails, but the message points at the wrong thing.
3. **Invisible** — dead code, a wrong comment, a missing test. **Nothing a user sees.**

**Give the count in each tier, then the findings.**

---

## 4. WS3 - and the deliverable
**Three files:**

1. **`ROUND-233-AUDIT.md`** — every finding, by category, with its tier and its file and line.
2. **`ROUND-233-TRIVIAL.patch`** — the patches you are confident cannot change compiled output, each with the sentence that says why.
3. **`ROUND-233-FOR-CLAUDE.md`** — the findings that need a compiler and a test, in the order they should be fixed, with what each would need to prove it.

**And a one-paragraph summary at the top of the audit: what state is this tree actually in?**

**Be direct.** **If it is in good shape, say so and say what you checked to conclude it.** **If it is not, say what the worst thing is.**
