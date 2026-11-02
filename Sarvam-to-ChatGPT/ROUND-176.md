# Sutram — R176: assess the arena design. Is bump-with-waste acceptable?

**Base:** main at v288 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is

**Compiler v288.** `likha` prints a string's text; three of Muse's eight traps fixed in other emitters; suite 283; guard 693 programs 0 DIFFER; gates 59 PASS / 1 FAIL (installer v243 vs v288).
**Muse's generator on v287 found ZERO new traps** - the string fix created none. That was the check nobody had run and it passed.
**Open: the reference-type class.** ChatGPT R175: `kosh == kosh` and `mala == mala` still compare address words, ordering compares them numerically, `+` does word addition. Strings work; containers do not.
**Claude decided in R106: "the region stays for the program's life."** So a `kosh` made in a `mandapa` outlives it. **The maintainer has asked for the memory system finished, so that decision is back on the table.**
**Examples are 283, not 277 - my count was stale for the fourth time.**

## The design I want assessed: a `kosh` inside a block is a slot in the block's arena, not its own region

**Today a `kosh` reserves 64 MiB of its own address space wherever it is created. That is why it cannot die with the block - it does not live in the block.**

**Proposal: a `kosh` created inside a `mandapa` draws from that block's arena and has no region of its own.**

- **Block exit frees the whole arena, the `kosh` included.** No liveness table. No generation check for regions. One allocation point, one free point.
- **Growth is a new slot in the same arena.** The old slot is wasted until the block exits - fine, because blocks are short.
- **`parimita N` bounds the arena**, so waste cannot run away. Budget and block become one mechanism, not two.
- **A `kosh` that must outlive the block is created outside it.** One rule a student can learn: a `kosh` lives where you make it.
- **A `kosh` created outside a block keeps its 64 MiB region and never-move guarantee, exactly as today.**

**Vocabulary needs no invention: `kshetra` (field) is the block's arena, a `kosh` is a sheath laid on the field, `parimita` measures the field.**

## WS1 - is this sound?
**The core question: is bump-allocation-with-waste-on-growth acceptable for a teaching language, or does the waste need a tighter bound than `parimita`?**

**Give me:**
- **the worst case** - a `kosh` grown to N inside a block, how many bytes wasted, as a formula
- **whether the arena must grow or can be fixed**
- **what happens when the arena is exhausted mid-block** - refuse, or grow and move the arena? **If the arena moves, every `kosh` in it moves, and that reintroduces the aliasing problem at a larger scale. Say so if it does.**
- **and the interaction with `parimana()`** - can a program ask how much of its block it has used?

## WS2 - and the thing you have said twice that I now take seriously
**"Identity comparison is not inherently wrong; an undocumented choice between identity, contents and raw bits is the defect to eliminate."**

**So: write the choice down.** **For `kosh`, `mala` and `rachana` - what does each of `==`, `!=`, `<`, `<=`, `>`, `>=`, `+` do, and why is that the right choice?**

**A table. And if the right answer is "identity, and say so", then the fix is documentation and not code, which is cheaper than we have been assuming.**

## WS3 - and the Sanskrit
**`kshetra` for the arena, `kosh` for the sheath on it, `parimita` for the measure.** **Does that hold, or does a `kosh` on a `kshetra` need a different word because it is no longer a standalone vessel?**
