# Sutram — R150: your boundary design, audited. And the arithmetic that lies.

**Base:** main at v275 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour, tested by me on the shipped binary

**Refused:** `outer = buf + 64`, `m[0] = buf`, `nivartanam buf`, `box[0] = nirmmita(64); outer = box[0]`.
**Allowed:** `outer = buf[0]`, a scratch pointer as a parameter returning a value.
**Refused:** `nirmmita(-1)` literal and computed.
**Fixed at v274:** `nirmmita(10)` then `p[0..9]` now stops at `p[1]`.
**Still broken, and I confirmed it:**
- **`9223372036854775807 + 1` -> `-9223372036854775808`** (silent)
- **`4000000000 * 4000000000` -> `-2446744073709551616`** (silent)
- **`1 / 0` -> SIGFPE, exit 136, no message**

## WS1 — your `parikshita` design, audited
**Mark the declaration; verify the body and everything it can call; transitive.**

**Answer these:**
**1. Is transitivity achievable at acceptable cost?** **A checked function that calls an unchecked one must be rejected — so how much of the 24-module library has to be converted before `parikshita` is usable at all?** **Give a number.**
**2. What happens to a checked function that calls `kosh_push`?** **The library is unchecked today.**
**3. Is `parikshita` the right word?** **It means "examined, tested". If you had to name it in Sanskrit for a student, would you choose that, and is there a better one?**

## WS2 — and the arithmetic, which is now a bigger problem than the boundary
**A language aimed at school students silently returns a negative square.** **I rank that above the boundary: the boundary is a subtle safety property, and this is a student getting wrong answers in their homework.**

**So:**
**1. Division by zero — one compare.** **Agreed it should be an error. What is the Sanskrit sentence?**
**2. Overflow of literal arithmetic — computable at compile time.** **Is that worth it, or does it create a false sense that overflow is caught generally?**
**3. Run-time overflow checking — what does it cost, and is it ever worth it in a language with no runtime?**
**4. Or: is C-like wraparound simply the right answer, documented, and students are taught to use wider types?**

**Pick one and defend it.** **I would rather have a documented C-like answer than a half-check.**

## WS3 — and the v1.0 gate, now that the memory work is done
**Give me the list of things that must be true for v1.0, and say which are true today.** **That list is what I will hold the release to.**
