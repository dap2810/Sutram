# Sutram — ROUND-81: the library audit's table, and what it says about `parikshita`

**Base:** main at v276 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour, tested by me on the shipped binary

**Refused at compile time:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]` · `nirmmita(-1)` literal · a written number that does not fit in int64.
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused at run time, with a Sanskrit message:** `nirmmita(n)` where n is negative; `1 / 0` and `5 % 0`.
**Still wrapping silently, by decision:** run-time overflow of a computed value — `3^30` is correct and `3^40` is negative.

## Your R80 confirmed all three of my findings and added one I missed

**`5 % 0` also traps — I did not test that.** **Thank you for it.**

## WS1 — the table, summarised
**Your R80 deliverable is the overflow table. Give me its headline: how many library functions overflow on an ordinary input, and which are the worst three?**

**If the number is small, we fix them.** **If it is large, that is the argument for the boundary being mandatory rather than optional.**

## WS2 — and the question that decides the boundary's cost
**Claude is building `parikshita` — a checked function that may only call checked functions.**

**So: how many of the 305 library functions are simple enough to become `parikshita` without rewriting them?** **A function with a `kosh` in it cannot be, because the check cannot see through a container.**

**Give me the count.** **If it is 20 out of 305, the boundary is a feature for new code only and I should say so.**

## WS3 — and the overflow policy, tested
**The decision: literal overflow is a compile error, run-time overflow wraps silently and is documented.**

**So test the documentation's claim: write the sentence a student would read, then find the program where a student follows it and still gets a wrong answer.** **If such a program exists, the documentation is not enough and I need to know.**
