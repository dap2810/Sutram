# Sutram — ROUND-107: the memory design. Price this, then build what is safe.

**Base:** main at v288 · **Deliver into:** `Claude-to-Sarvam/`

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

## WS1 - the price, before any build
**Answer these four, with numbers:**
1. **Does drawing a `kosh` from the block's arena cost more or less than the current 64 MiB region allocation?** **Instructions, and whether it touches the slow path.**
2. **What does growth-with-waste cost in bytes for a `kosh` grown to 1,000 elements inside a block?** **The dead slots, summed.**
3. **Does the arena need to grow, or is a fixed size with a `parimita` refusal enough?**
4. **What breaks?** **Which of the 283 examples make a `kosh` inside a `mandapa` and use it after the block?**

**Muse is counting the same thing independently. If your number and its number differ, say so.**

## WS2 - and build only what is safe now
**Do not build the arena design this round.** **Build these two, which are safe and independent of it:**
- **The escape error.** **A `kosh` that tries to outlive its block refuses with a named Sanskrit error.** **Even under today's model this is right, and it becomes the enforcement point if the arena design lands.**
- **`parimana()`** - **one function returning bytes currently in use**, so a program and a test can both ask. **Right now neither can, which is why every memory measurement in this project needed a Python harness.**

**One commit, one guard run.**

## WS3 - and the decision you made in R106
**You decided the region stays for the program's life.** **State the reason in one paragraph.** **If it was cost, name the cost. If it was risk, name the risk.**

**The maintainer wants the memory system finished. I am not overruling you - I am asking for the argument so it can be weighed.**
