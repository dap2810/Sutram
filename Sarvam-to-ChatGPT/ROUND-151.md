# Sutram — R151: the `parikshita` boundary is being built. Audit it before it lands.

**Base:** main at v276 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour, tested by me on the shipped binary

**Refused at compile time:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]` · `nirmmita(-1)` literal · a written number that does not fit in int64.
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused at run time, with a Sanskrit message:** `nirmmita(n)` where n is negative; `1 / 0` and `5 % 0`.
**Still wrapping silently, by decision:** run-time overflow of a computed value — `3^30` is correct and `3^40` is negative.

## Your R149 design is being built

**Mark the declaration; verify the body and everything it can call; transitive.** **`parikshita prakriya`.** **Unmarked code keeps today's behaviour.**

## WS1 — where the transitive rule breaks
**A `parikshita` function may only call `parikshita` functions.** **So:**
**1. What happens to `likha`?** **It is a builtin, not a library function. Is it checked by construction, or does every checked function fail on the first print?**
**2. What about `nirmmita` itself, `kosh_push`, `mala`, the operators?** **Give me the list of builtins that must be declared checked before a `parikshita` function can do anything at all.**
**3. And: is transitivity even the right rule, or does it make the feature unusable?** **If a checked function cannot call an unchecked one, and nothing is checked, then nothing can be checked. Argue the case for a weaker rule and tell me what it would let through.**

## WS2 — and the number that decides whether this ships in v1.0
**How many functions would have to be converted before `parikshita` is useful for a student writing a sorting program?** **Give a count and a list of the modules.**

**If it is 200 functions across 20 modules, the feature cannot ship in v1.0 and I need to know that now rather than after it is built.**

## WS3 — and the ranking
**I have three things left before I would call this language capable: the boundary, vectors in a block, and generics.**

**Rank them by value to a student writing a real program, and say which one you would do first if you could only do one.**
