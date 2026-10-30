# Sutram — ROUND-75: prove the three gaps, and find the fourth

**Base:** main at v272 · **Deliver into:** `Muse-to-Sarvam/`

## The memory model is built; three gaps are known

**`nirmmita(-1)` compiles (I confirmed it). The store check may miss nested expressions. A `kosh` of scratch pointers is invisible.**

## WS1 — prove or disprove the nested-store gap
**ChatGPT reports that the store check only inspects root statements.** **Establish it:**

**1. `out = (m[0] = buf) + 1` — checked or not?**
**2. `yadi (m[0] = buf) > 0` — checked or not?**
**3. `likha(m[0] = buf)` — a store as an argument?**
**4. `m[0] = buf[0]` — a DATA copy, must be allowed**
**5. and the loop case: `k[i] = buf` where `i` is a variable**

**For each: caught or missed.** **And if missed, does the program compile and then corrupt memory at run time?**

## WS2 — and find the fourth gap
**Three are known. There is very likely a fourth.** **So: what else about `nirmmita` is not guarded?**

**Check the size domain specifically:**
- **`nirmmita(0)`** — zero bytes
- **`nirmmita(1)`** — one byte, then a 4-byte write
- **a size computed from a variable that is negative at run time**
- **a size that overflows when multiplied, `nirmmita(n * 1024 * 1024)`**

**For each: what happens?** **That is the fourth gap if there is one.**

## WS3 — and the check against the library
**The library has 305 functions, 371 write sites.** **How many of them would be refused if called inside a `mandapa`?** **Give the count.** **If the answer is "most of them", then the block cannot be used with the standard library and that is the most important fact about the feature.**
