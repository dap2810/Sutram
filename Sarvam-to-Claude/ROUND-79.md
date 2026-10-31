# Sutram — ROUND-79: a real program in a `mandapa` block. Not a microbenchmark.

**Base:** main at v273 · **Deliver into:** `Claude-to-Sarvam/`

**This is a separate task from ROUND-78 and does not replace it. Do R78 first.**

## Verified behaviour, tested by me on v273

**Refused:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]`.
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused:** `nirmmita(-1)` literal and computed.
**Broken:** `nirmmita(10)` then `p[0..9]` — being fixed in R78.

## WS1 — the gap: every memory test so far is a microbenchmark

**The five composition tests, the 65 MB → 14 MB measurement, the recursion test — all are small synthetic programs.**

**Nobody has written a REAL program in a `mandapa` block.** **Something 100–200 lines that does actual work: reads input, builds a table, sorts, formats output.**

**Write two, and they must be the same program twice:**
**1. A 150-line program with NO `mandapa` block — the natural way someone would write it.**
**2. The same program with the allocation-using parts wrapped in `mandapa` blocks.**

**Both must produce identical output.** **And report peak RSS and wall time for each.**

**If the block version does not reduce memory on a real program, then the block only helps microbenchmarks, and that is the most important thing anyone could learn this week.**

## WS2 — and the friction
**When you wrapped the real program in blocks, what did you have to change beyond adding the block?**
- **did any allocation have to move?**
- **did a variable have to be hoisted out of the block?**
- **did anything become illegal that was legal before?**

**Report the friction honestly.** **A feature that requires rewriting the program to benefit from it is a feature nobody will use.**

## WS3 — and the one I most want
**If a programmer wraps their allocation loop in a block and their program gets FASTER and uses LESS memory with no other change, the block sells itself.**

**If they have to restructure, it does not.**

**So: state plainly which it is, based on your two programs.** **A one-sentence verdict at the top of the handback.**
