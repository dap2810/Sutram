# Sutram — R149: your safe/unsafe boundary is now the top risk. Design the marker.

**Base:** main at v273 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour, tested by me on v273 (not remembered)

**Refused:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · **and the laundering case `box[0] = nirmmita(64); outer = box[0]` — already closed.**
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused:** `nirmmita(-1)` literal and computed, with `E_NIRMMITA_RNA`.
**Still broken:** `nirmmita(10)` then `p[0..9]` — 80 bytes into 10. **Being fixed this round.**

## WS1 — your R148 answered my question, and I have accepted the design direction

**A generation-checked opaque handle, a hybrid of static classification and dynamic validation, and a qualified small feature rather than an unqualified large one.** **And your rejection of address-range checking — which Gemini reached independently, with the same reasoning about reuse.**

**Two parties, no contact, same conclusion.** **That settles it.**

## WS2 — and now the thing you named, which is now the top risk

**> "The single release risk I prioritize is an unenforced safe/unsafe boundary: ordinary unchecked raw memory can invalidate the assumptions of the checked part."**

**Design the boundary.** **Concretely:**
**1. What is the smallest marking that makes the boundary visible to a reader and to the compiler?** **A keyword, a naming convention, a warning, or something else.**
**2. Inside a `mandapa`, if a programmer calls a library function that allocates — does that break the block's assumption? Show the case.**
**3. Can a checked function receive a raw pointer from an unchecked caller and have its guarantee silently broken?**
**4. And: should the compiler REFUSE a call from a checked region into an unchecked function, or only warn?** **Refusing is safe and restricts; warning is honest and does not protect.** **Pick one and defend it.**

**This is worth more than the next three rounds of fixes.**

## WS3 — and the release question again, now that the count is corrected
**I told you there were 15 surviving mutants. Muse's audit says 2 — the Madhava sign error is a mutant, not a shipped bug, and the code matches Python's `math` to 6 decimals.** **I had been repeating a number I had not checked.**

**So: with 2 survivors rather than 15, and the memory model built, what does the v1.0 gate look like now?** **Give me the list of things that must be true, and say which are true today.**
