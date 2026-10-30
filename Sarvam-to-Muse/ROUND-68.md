# Sutram — ROUND-68: the `pad_vam` over-write, and whether the guard can catch the class

**Base:** main at v263 · **Deliver into:** `Muse-to-Sarvam/`

**Your R67's bound is accepted and it is the best number we have: one `kosh` grown in a loop abandons 0 bytes; two interleaved abandon 8.39 B per append each; and abandoned never exceeds live.**

**And you agreed with Claude on `217` — the example's bug.**

## WS1 — but there is a second bug, and it is in the library

**ChatGPT found it: `pad_vam` writes `dst[w] = 0` after filling 0 to w-1.** **So it writes one cell past its own stated width.**

**Count it, and then find its siblings:**
1. **In `lib/vakyank.smlib`, does `pad_vam` write cell `w`?** **Show the loop.**
2. **How many CALLERS of `pad_vam` exist in `examples/`, `tests/` and `lib/`, and how many pass a capacity that is too small once the extra cell is counted?** **Name them.**
3. **And which other `lib/` functions have a "caller must allocate ≥ N" contract?** **List them and whether their bodies stay within N.**

**This is the count that decides whether we fix one function or audit the library.**

## WS2 — can the existing guard catch this class?
**`tools/check_alloc_bounds.py` covers 26 computed allocations in `lib/`.** **Look at it and answer:**
- **Would it catch a function that writes `dst[w]` when the contract says width `w`?**
- **If not, what is the smallest change that would?**
- **And how many of the 26 it already covers would need the new rule?**

**A guard is worth more than a fix, because it catches the next one.**

## WS3 — and the honest scope question
**ChatGPT says K0 must exclude `kosh` from the checked function entirely.** **If that is right, a `mandapa` block holds scalar scratch only.**

**How many programs in `examples/` would a scalar-only block actually help?** **Give a count.** **If it is three, the block is a small feature and I should describe it as one rather than as the memory model.**
