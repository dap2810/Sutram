# Sutram — ROUND-68: fix `pad_vam`, then audit every library function for the same over-write

**Base:** main at v263 · **Deliver into:** `Claude-to-Sarvam/`

**Your R67 settled `217` and I accept the verdict: the example writes 16 bytes past a 4-cell block, the write happens on v261 too, and the old allocator only gave it somewhere harmless to land.** **Step 1 stands.** **And the leak bound is now a real number — thank you, that was the most useful thing in the round.**

## WS1 — ChatGPT found a SECOND bug, and it is in the library

**Its R139: *"The report-example diagnosis is substantially correct, but its proposed fix is incomplete. `pad_vam` writes `dst[w] = 0` after filling positions 0 to w-1."***

**If that is right, `pad_vam` writes cell `w` — one past its own stated width.** **So the example's `nirmmita(48)` fix would still over-write by one cell, and every other caller of `pad_vam` does too.**

**Verify it in `lib/vakyank.smlib:237` and its body.**
1. **Does `pad_vam` write cell `w`?** **Show the loop bounds.**
2. **If yes, is the contract wrong (it should say `width + 1`), or the body wrong (it should stop at `w - 1`)?** **Which is the fix — the code or the doc?**
3. **And: does the same off-by-one exist in any sibling function — `pad_dakshin`, or whatever else pads?**

**Fix whichever is wrong, and state which you chose and why.** **A function that writes past its stated width is a bug wherever it is called, and now that allocations are packed tightly, every caller is a live corruption instead of a harmless landing.**

## WS2 — the audit that matters more than the fix

**`217` was one program.** **The pattern is "allocate n, use more than n", and the tighter allocator turned every instance from harmless into corrupting.**

**Audit `lib/` for the pattern:**
- **every function with a documented "caller must allocate ≥ N" contract — does the body stay within N?**
- **every loop that writes `dst[i]` — is `i` bounded by the documented capacity?**
- **and every caller in `examples/` that passes a capacity smaller than the width it asks for**

**Give me the count and the names.** **If there are more, we fix them before Step 2, because Step 2 will pack even tighter.**

## WS3 — and the honest question
**If the audit finds several, the right response may be a guard rather than a set of fixes.** **`check_alloc_bounds.py` already exists and covers 26 computed allocations in `lib/`.**

**Would extending it to the padding family catch this class?** **If yes, price it.** **If no, say why.**

**Do NOT start Step 2 this round.** **The library has to be sound first.**
