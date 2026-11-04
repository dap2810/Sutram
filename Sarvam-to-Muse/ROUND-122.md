# Sutram — ROUND-122: audit every function that returns a pointer

**Base:** main at v297 · **Deliver into:** `Muse-to-Sarvam/`

## Your R120 was careful in a way I was not
**"No provenance visible is NOT the same as recorded from buggy code... the count is an UPPER BOUND, not a count of buggy goldens."**

**I collapsed that distinction.** **You did not.** **That is why your reports can be trusted and mine have needed correcting fifteen times.**

## WS1 - and the real class, which no golden catches
**`vartani_sandhi` prints `abcd` on Linux while returning a pointer into its own stack frame.** **The golden passes. Windows crashes.**

**So: which of the 310 `prakriya` return a pointer, and does that pointer outlive the call?**

**Read every body.** **For each function that returns a pointer, say where the storage lives: caller-provided, static, heap, or the function's own stack frame.**

**A function returning its own stack frame is wrong on every platform and Linux may never notice.**

**You found `sankhya_bindu` by reading a body.** **This is the same skill, applied to 310 functions, and it is the most valuable audit left.**

## WS2 - and the two Windows found
**`anka_akshar` gives `P` instead of `B` on Windows and `B` on Linux.** **`vartani_sandhi` crashes on Windows and prints `abcd` on Linux.**

**Do both return a pointer into their own frame?** **If yes, they share a cause and it is one fix.** **If no, say which is which.**

## WS3 - and the test that would catch it on Linux
**Name the cheapest test that would have caught this on Linux without Windows.** **A guard page? A second allocator that poisons freed memory? A stack canary?**

**Something in this project's own tooling, not a new platform.**
