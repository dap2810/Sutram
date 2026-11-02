# Sutram — ROUND-103: count what breaks, and give me the count command

**Base:** main at v288 · **Deliver into:** `Muse-to-Sarvam/`

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

## WS1 - the number that decides whether this design is small or large
**How many of the 283 examples make a `kosh` inside a `mandapa` and use it after the block?**

**Not how many make one - how many USE IT AFTER.** **Those are the programs the design breaks.**

**If it is zero, this design changes nothing that exists and it is cheap. If it is more than a handful, it is a large change and I want the list.**

**Claude is counting the same thing independently. Two sources.**

## WS2 - and the cost of a `kosh` today
**Measure a program with 1, 10, 100 and 1,000 live `kosh` objects.** **Peak RSS and virtual size for each.**

**That answers the invisibility problem - 64 MiB reserved per collection is either harmless because it is virtual, or it is not. A number settles it.**

## WS3 - and the census, eighth run
**Three counts, same method.** **And: has any of the eight traps you found been fixed by v288?** **You said three were; confirm which three, and which five remain.**

## WS4 - and the count command, which I have now asked twice
**You have corrected my example count four times: 259, 274, 277, 283.** **Do not give me the number this time - give me the command or the file path that produces it.** **One line. I will run it myself.**
