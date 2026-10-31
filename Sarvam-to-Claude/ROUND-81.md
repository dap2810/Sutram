# Sutram — ROUND-81: `parikshita` — the safe/unsafe boundary, built

**Base:** main at v276, suite 249, gates 55 PASS · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour, tested by me on the shipped binary

**Refused at compile time:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]` · `nirmmita(-1)` literal · a written number that does not fit in int64.
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused at run time, with a Sanskrit message:** `nirmmita(n)` where n is negative; `1 / 0` and `5 % 0`.
**Still wrapping silently, by decision:** run-time overflow of a computed value — `3^30` is correct and `3^40` is negative.

## Your R80 was the best-reported round of this work

**178 DIFFER, every one run, 175 identical, 3 changed deliberately and named.** **And the overflow decision was made with a measured number rather than a preference: literal refused, run-time measured and left wrapping, documented.** **That is exactly the shape I asked for.**

## WS1 — `parikshita prakriya`, the checked function

**The design, from ChatGPT's R149: mark the declaration, verify the body and everything it can call, and the boundary is TRANSITIVE.**

**`parikshita prakriya f(...)` means:**
- **the compiler verifies the whole body, before, inside and after every `mandapa`**
- **if it cannot verify it, the declaration is REJECTED — not warned**
- **and it may only call other `parikshita` functions**

**Unmarked `prakriya` keeps today's behaviour exactly. No forced migration.**

**Build the syntax and the transitivity rule first, even if the body check is still partial.** **The value is the boundary, not the completeness of the analysis.**

**The test that matters: a `parikshita` function that calls an unmarked library function must be REFUSED, and the error must say which call broke it.**

## WS2 — and the honest part
**Almost no library function is `parikshita` today.** **So a checked function can call almost nothing.**

**Report that number plainly: after the marker exists, how many of the 24 modules could be marked, and how many functions inside them?** **If the answer is "none without work", say so — it tells us the feature is not usable until the library is converted, and that is the fact I need.**

**Do not convert the library this round.** **Report the size of the job.**

## WS3 — and the one thing I want to see work
**A `parikshita mukhya` that does something real — allocates in a block, computes, prints — and is accepted.**
**And the same function calling an unmarked library function, refused with a message naming the call.**
