# Sutram — R156: generics. The heavy round, and the one that decides whether this language is capable.

**Base:** main at v278 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour — each line run on v278, with the CASE it was tested in

**Diverges:** `kosh k[1]; kosh_push(k,41); vitti a = k; vitti obstacle = nirmmita(64); kosh_push(k,42); k[0]=99` -> `a[0]=41, k[0]=99`. The obstacle blocks in-place extension, so `k` relocates and `a` stays.
**Agrees:** the same WITHOUT the obstacle -> `a[0]=999, k[0]=999`. In-place extension succeeded, nothing moved.
**Census (Muse R83 and Claude R85, independently): 3 aliases total, 1 that grows, 0 that grow with an intervening allocation.**
**Claude R85: refusing `vitti a = k` breaks 3 programs. A forwarding pointer costs 3 instructions and 8-16% per read. The divergence cases are stale handles to LIVE blocks, so the guard page catches nothing.**

## Your R155 was right on all three, and your evidence standard is now adopted

**Ranking accepted: document first, refuse second, forwarding third.** **The census proved the first is enough: 3 - 1 - 0.**

**And your line — *"the measured v278 examples are not two logical owners of a common stable handle: they are raw data addresses"* — is the clearest statement of the defect anyone has made.** **That is the sentence the documentation will be built from.**

## WS1 — generics, in full

**Sutram has no generics.** A `kosh` holds 64-bit values; you cannot write a sort that works for two types.

**Design the smallest generics that makes a real library possible.** **Constraints that cannot move:**
- **no runtime, no type tags at run time, no GC**
- **one NASM file, 24,700 lines**
- **a school student must be able to read it**
- **Sanskrit keywords only**

**Deliver: the syntax, three lines of it in use, what it costs in compiler complexity, and what it explicitly does NOT do.**

**And say plainly whether it is worth doing at all in v1.0, or whether a `kosh` of 64-bit values plus manual discipline is the honest answer for a teaching language.**

## WS2 — and the question I have asked three times
**A sorting program a student would write: how many of the 306 library functions must become `parikshita` before that program can be fully checked?**

**A number, and the module names.** **If it is 200 across 20 modules, `parikshita` cannot ship in v1.0 as a guarantee and must ship as a tool for new code — and I need to say that in the reference.**

## WS3 — and the last thing: what is missing that I have not named
**Four things are done: memory, arithmetic, the boundary, kosh-in-a-block.** **The known gaps: alias documentation, generics, threads, Windows execution.**

**What is missing that is on neither list?** **One thing, and why it matters more than threads.**

**Then: if you could ship v1.0 next week, what would you cut, and what would you refuse to ship without?**
