# Sutram — ROUND-192: the four frozen books, and `avaroha` as a named question.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Your R191 settled the contradiction and then found a fault in its own example.** **That is the third time this week a partner has caught its own error first, and it is worth more than a clean round.**

**Two things are left from it, and both are small.**

---

## 1. The four frozen books

**Your R191: *"the four frozen books still say 'counts down automatically'."***

**Those are the paused language editions — Hindi, Telugu, Tamil, Gujarati.** **They carry the same false sentence the English and Sanskrit books had until v326.**

**A paused book that says something false is worse than a paused book that says nothing**, because it will be resumed by someone who trusts it.

**So:**

1. **Name the four files and the sentence in each.** **Quote it.**
2. **Fix the sentence in all four.** **The corrected English sentence is the source; translate it as literally as the language allows.**
3. **And say whether each of the four is otherwise current** — **does it have the memory chapter?** **Does it mention reading a line?** **If not, say so plainly rather than fixing one sentence and leaving the rest stale.**

**A paused book is not a licence to leave it wrong. It is a reason to mark it paused.**

**So also: is there a marker in each of the four saying it is paused?** **If not, add one at the top, naming the version it was frozen at.** **A reader opening the Gujarati book should know it is not current.**

## WS1 - and `avaroha` as a named question, not a hole
**You named the word. So put it in `docs/WHATS-LEFT.md` as an open design question, with everything a decision would need:**

1. **What `avaroha` would mean** — a loop that counts down, or a modifier on `chakra`, or something else.
2. **What it would cost** — a 34th keyword, a parser branch, and what happens to `chakra i = 5 tak 3` when the word exists.
3. **Why it was not done now** — your R190 reasoning, in one sentence.
4. **And what a student does today** — **the workaround, written as three lines they can copy.** **Because a hole with a workaround is a gap; a hole without one is a trap.**

**That last part is the one that matters. If the language cannot count down, say how a student counts down.**

## WS2 - and the input story, checked end to end
**You fixed the three lines and put them in the gate.** **So now check the whole path as a student would walk it:**

1. **Open the book at the chapter that teaches input.**
2. **Follow it literally: install, write the program, run it, type `hello` where a number is expected.**
3. **What happens?** **A refusal, a named error, or a wrong answer?**
4. **And type `42` — does it print 42?**

**Report what a student would actually see at each step.** **Not what the code does — what the book tells them to do and what they get.**

**If there is any step where the book says one thing and the language does another, that is the last Tier 1 finding and it should be fixed here.**

## WS3 - and the guard
**Documents only, so it should read 0 DIFFER against the v326 tip.**

**Report it.**

## WS4 - and the honest summary
**In one paragraph, for the owner: what is the state of this tree now?**

**Not the findings — the state.** **Is it ready to merge when the Windows run passes, or is something still open that he should know about before he runs it?**

**Be direct. If it is ready, say so. If it is not, name the one thing.**
