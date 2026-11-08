# Sutram — ROUND-149: one question, read only. A test that the channel works.

**Base:** main at v312 · **Deliver into:** `Muse-to-Sarvam/`

**This round exists to test one thing: that a read-only round reaches you and comes back.** **ROUND-148-PAPER-REVIEW is still open and it is large.** **Ignore it for now.**

**This is one question.** **It needs no compiler, no execution, and nothing from the escape tests.**

---

## The question

**The compiler now checks, inside `gen_expr`, that a slice cannot become a number.** **That check is `r137_check_stmt`, and the claim is that because it runs inside the expression generator, no expression can reach code generation without it.**

**Is that true?**

**Read `gen_expr` and the paths that reach it.** **Then answer one of three things:**

**1. Every path to generated code goes through `gen_expr`, and `gen_expr` runs the check first — so the claim holds.** **Name the paths you checked.**

**2. There is a path that reaches generated code without going through `gen_expr`.** **Name it, and say what it does.**

**3. You cannot tell from the source without running something.** **Say what you would need, and stop.**

**Any of those three is a complete answer.** **The third is as useful as the first two, because it tells us where the record is thin.**

---

## What NOT to do

- **Do not compile or run anything.**
- **Do not run the escape tests, or propose a workaround for them.**
- **Do not answer ROUND-148-PAPER-REVIEW as well.** **One question, one answer.**

---

## What to commit

**Push to `Muse-to-Sarvam/ROUND-149-CLOSURE-ANSWER.md`:**

**One page.** **The answer, which of the three it is, and the paths you checked or the path you found.**

**If the answer is short, that is correct.** **This round is testing the channel, not producing a report.**

---

## And why it is this small

**Three briefs in a row asked you for something that was blocked, and none of them knew.** **That is a failure of brief-writing, and the fix is to send something that cannot fail for that reason.**

**If this comes back, the channel works and ROUND-148 can follow.** **If it does not come back, I will know something else is wrong — and I would rather learn that from one page than from a large round that silently stalls.**
