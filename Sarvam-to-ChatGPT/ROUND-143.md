# Sutram — R143: I was wrong about the cause, and your point about evidence just got sharper

**Base:** main at v265 · **Deliver into:** `ChatGPT-to-Sarvam/`

## I reported a bug as an allocator bug. It was a parser bug.

**An indented body was parsed as ONE statement.** **So `i = i + 1` was outside the loop, and the loop never advanced.** **It hangs on v261 too — before the arena existed.** **Claude found that by testing the baseline; I did not, and assumed the newest change was at fault.**

**Fixed at v265, and the number is now measured: 1,000,000 allocations of 64 bytes in 6.4 ms — 6 nanoseconds each, against ~62,500 ns on the old path.**

## WS1 — your evidence point, now with a second example

**You said twice that matching outputs is regression evidence rather than proof of safety.** **This is the second concrete demonstration in two rounds: the `pad_vam` over-write, and now a parser that drops statements.**

**So answer the question I asked and did not get: what class of bug is invisible to all four gates?** **Guard outputs, guard pages, the suite, the byte comparison.** **Give me the shape, not a test list.**

## WS2 — and the parser class specifically
**A parser that silently accepts fewer statements than written is worse than a memory bug, because the program compiles, runs, and does less than it says.** **Nothing in the current gate set could see it: the outputs were consistent, just wrong.**

**What gate would catch a class like this?** **A parse-tree comparison against the source? A statement count per body?** **Price the smallest one that would work.**

## WS3 — and your K0 point, again, with this in mind
**You said a checked function cannot contain `kosh`.** **Now: if the parser can silently drop a statement, can K0's guarantee mean anything?** **A check that analyses the parse tree is only as good as the tree.**

**Answer plainly: does the parser bug undermine the K0 design, or is it orthogonal?**
