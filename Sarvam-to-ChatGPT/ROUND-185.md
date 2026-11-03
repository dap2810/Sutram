# Sutram — R185: error handling, which this language does not have. Design the answer.

**Base:** main at v292 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v292

**22 builtins renamed as aliases, `asti`/`nasti` are `==`/`!=`. Suite 295, gates 60 PASS, guard 705 programs 0 DIFFER.**
**Memory: blocks return memory (measured 52,760 KB -> 13,480 KB at 200k allocations); `mandapa parimita N` refuses past a budget; the outlives rule refuses storing or returning a block `kosh`; `parimana()` reports (0 -> 48 -> 72 -> 184 -> 288 -> 176).**
**The block-arena is BUILT on `claude/r108-arena-review` (0e71e54), UNMERGED, and Claude R109 reports a SILENT WRONG ANSWER on it that nobody has diagnosed.**
**`dasham` into a `mala` element stores the raw IEEE bits: `3.0` becomes `4613937818241073152`. Found by Muse, confirmed by me, never assigned.**
**55 distinct error codes, no exception handling - a program cannot raise or recover from an error.**

## WS1 - 55 codes, no way to handle one
**The language has 55 distinct `E_` codes: syntax, type, runtime, memory, verification, module.** **Every one is in Sanskrit with a line number.**

**And a program cannot respond to any of them.** **There is no `try`, no `catch`, no `raise`.** **When something fails the program stops.**

**Design the answer. Three options, and pick one:**

- **No exception handling, by design.** **C does this.** **A program checks before acting.** **Then the reference must say so plainly and say what a program does instead.**
- **A minimal raise-and-handle: one construct, no hierarchy, no stack unwinding.** **What does it cost?**
- **Full exceptions.** **Say why this is wrong for a language with no runtime and no GC, if it is.**

**And the question underneath: which of the 55 codes can a program actually do something about?** **`E_SHUNYA_BHAJAN` is preventable by checking first.** **`E_NIRMMITA_SEEMA` is preventable.** **`E_PARSE` is not a runtime event at all.** **Sort the 55 by whether a running program could respond to them.**

**That sort is the real answer to whether this language needs exceptions.**

## WS2 - and `dasham` into a `mala`
**`dasham d = 3.0; mala m[4]; m[0] = d` stores the raw IEEE bits.** **What should it do?**

**`mala` is a cell array.** **A `dasham` is 8 bytes and a cell is 8 bytes, so the bits fit and nothing is lost - it is the READING back that is wrong.** **So: is this a store problem or a read problem, and what is the smallest correct answer?**

## WS3 - and the whole-tree English audit stands
**R184 is still open.** **This round is in addition to it, not instead of it.** **Do the audit first if you have to choose.**
