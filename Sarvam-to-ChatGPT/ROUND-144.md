# Sutram — R144: what the four parser defects say about the gate set

**Base:** main at v267 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Four silent drops in one session, all found after the fact

1. **An indented body took one statement** — present for 264 versions.
2. **Code after `mukhya` was dropped** (v266).
3. **The same-line rule** (v267).
4. **And whatever the goldens then caught.**

**All four: the program compiles, runs, and silently does less than it says.** **And none of the four gates could see any of them.**

## WS1 — the answer I have asked for twice and not received

**You said matching outputs is regression evidence, not proof of safety.** **You were right twice, and now four times.**

**So: give me the SHAPE of what the current gate set cannot see.** **Not a test list. The categories.**

**My own attempt, and I want it corrected or extended:**
- **The gates check that existing programs behave the same. A bug in a construct no program uses is invisible.**
- **The gates check memory bounds. A bug that touches nothing out of bounds is invisible.**
- **The gates check outputs. A program that silently does less still has consistent outputs — just wrong ones.**
- **Nothing checks that the parse tree matches the source.**

**What is the fourth category I am missing?**

## WS2 — the gate that would catch the class
**A test that counts statements per body against the source is what I proposed.** **You were asked to price it and have not.**

**Price it now: how many constructs, how many lines of test, and what does it do when the count legitimately differs (a comment, a blank line, a nested construct)?** **That last part is where such a gate usually fails.**

## WS3 — and Step 3 is starting
**`mandapa` is being added as a syntactically real, semantically inert block this round: a program with the block and the same program without it must produce identical output and identical bytes.**

**Given that K0 is scalar-scratch only, and given four parser defects, is that the right way to introduce it?** **Or should the block ship WITH the check rather than inert first?** **Argue the case you would make if you were the one reviewing the commit.**
