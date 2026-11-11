# Sutram — ROUND-191: settle one contradiction, then finish the input story.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Two partners disagree and both cannot be right.** **That comes first, because a documentation fix that did not land is worse than one that was never attempted — the record says it is done.**

---

## 1. The contradiction, stated exactly

**Your R190-00 says:**

> *"Both books, which said the loop 'counts down automatically', now say what is true."*

**Muse's R172 says:**

> *"The v325 books' 'Descending Loops' section was not corrected — the English book still says the sentence at :400."*

**One of you is reading a different branch or a different file.** **Settle it.**

## WS1 - and this is the round: the check
**On the v326 tip:**

1. **Open the English book and go to line 400 — or wherever the descending-loop sentence is.** **Quote the sentence as it stands.**
2. **Open the Sanskrit book and find the same section.** **Quote it.**
3. **And the reference.** **Quote it.**
4. **Then say: does any of the three still claim a `chakra` counts down automatically?**

**If one does, it is still false and the fix did not land on that file.** **Fix it, and say which file was missed.**

**If none does, then Muse was reading v325 and the fix landed in v326 — say that plainly, with the commit that changed it.** **A disagreement resolved by a fact is not a failure; it is the method working.**

## WS2 - and then the input story, which the owner asked for
**You added a function to `vakyank` that takes a string.** **Good — and it is the piece that was missing.**

**So finish it:**

1. **What is it called, what does it take, what does it return, and what does it do on `hello`?** **A student typing a word where a number was expected is the case that matters.**
2. **Does it refuse, return 0, or return a success flag?** **If it returns 0 silently, it is the same defect class as the en dash and the `chakra`.**
3. **And the three lines the owner asked for:** **read a line, convert it, print it.** **Put them in the reference and in both books, in the chapter that teaches input.**
4. **And an example in `examples/`** — **a program that asks a question and prints the answer, using the new function.**
5. **And a test with a golden.**

**That is the Python `input()` capability, delivered without breaking `grahan`.**

## WS3 - and the one thing the warning does not cover
**Your R190 chose a compile-time warning for `chakra i = n tak 1`, and left `chakra i = 5 tak e` silent until the language has a word for counting down.**

**That is a defensible line, and it leaves a hole.** **So:**

1. **What would the word be?** **Not a design — a name, so the question is not open forever.** **The language has 33 keywords; a 34th for a descending loop is a real option.**
2. **And: does the warning fire for `chakra i = n tak 1` where `n` is a variable, or only where it is a literal?** **If only literals, the common case is uncaught.**
3. **And: is the warning in the compiler's message list, or is it a new mechanism?** **If it is new, is it in the 65 codes?**

**Answer, and put the descending-loop word in `docs/WHATS-LEFT.md` as an open design question rather than a hole.**

## WS4 - and nothing else
**Do not merge. Stage, report, hand back.**

**And report the guard: if this round changes only documents and adds one function, the DIFFER set should be exactly the programs that bring in `vakyank`, as it was in v326.**
