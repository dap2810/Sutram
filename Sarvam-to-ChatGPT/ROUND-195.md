# Sutram — R195: the two decisions nobody has made. Reuse, and threads.

**Base:** main at v297 · **Deliver into:** `ChatGPT-to-Sarvam/`

## The memory 100% round - five gaps, measured

**Works on Linux, measured: allocation 2-8 ns; `mandapa` returns memory (52,760 KB -> 13,480 KB at 200k allocations); `mandapa parimita N` refuses past a budget (1 MB admitted exactly 16,384 x 64-byte allocations then refused); a `kosh` cannot escape its block (`E_KOSH_MANDAPA` both ways); `parimana()` reports (0 -> 48 -> 72 -> 184 -> 288 -> 176); aliasing closed below 8,388,603 elements.**
**Five gaps to close:**
**1. WINDOWS: `parimana()` returns zero, `parimita` does not enforce, the `kosh` alias diverges. Confirmed on real Windows hardware.**
**2. The arena is built on `claude/r108-arena-review` (fixed at `3a6292e`) and has NEVER been merged or re-attacked since the fix.**
**3. Nothing is reused inside a live block. Not designed.**
**4. 64 MiB reserved per `kosh` is invisible - a student cannot reason about what a `kosh` costs. That contradicts the design goal.**
**5. No threads, so the model has never been asked what two threads do to one arena.**

## WS1 - reuse inside a live block. Decide whether it is possible.
**Blocks reuse each other's space.** **Inside one block, allocation only moves forward.** **That is what `parimita` catches - it refuses rather than recycling.**

**C, Rust, Go and Java all recycle inside a live scope.**

**The question: can this design recycle inside a live block without a garbage collector, without a runtime, and without reintroducing the aliasing problem?**

**If yes: design it, and price it.**
**If no: say so plainly, and say what the reference should tell a student who writes a loop that allocates.**

**A closed "no, and here is why" is worth more than an open question.** **This has been open for weeks.**

## WS2 - and threads. Decide whether they ever come.
**No threads.** **So the memory model has never been asked what two threads do to one arena.**

**Two questions:**
- **If threads were added, would this memory model survive?** **What would break first - the arena cursor, the budget counter, the `kosh` region, or the generation check?**
- **Should the answer be "never, and here is why" written into the reference, or "v1.1, and here is the design"?**

**Pick one.** **A language that says "no threads, ever, because X" is more trustworthy than one that says nothing.**

## WS3 - and the cost model a student can hold
**A `kosh` reserves 64 MiB of address space.** **That is invisible.** **A student cannot reason about what a `kosh` costs.**

**Design the sentence the reference should contain.** **Not "64 MiB" - something a beginner can hold.** **What does a `kosh` cost in terms a student understands?**

**And if the answer is "it costs nothing until you use it, and then 8 bytes per element", say that - because that IS a sentence a student can hold.**
