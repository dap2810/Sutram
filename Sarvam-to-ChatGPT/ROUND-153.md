# Sutram — R153: the heavy round. Three hard problems, and one of them is mine.

**Base:** main at v278 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour, run by me on v278 and pasted as output

**Compiles and prints `41`:** `kosh k[2]; kosh_push(k,41); vitti a = k; likha(a[0])` — **`vitti a = k` is NOT refused. My brief said it was, for several rounds. It was wrong.**
**Refused, `E_SCRATCH_ESCAPE`:** `outer = buf + 64` · `m[0] = buf` · `nivartanam buf` · `box[0] = nirmmita(64); outer = box[0]`.
**Allowed:** `outer = buf[0]` · a scratch pointer as a parameter returning a value.
**Refused at compile time:** `nirmmita(-1)` literal · a written number that does not fit int64.
**Refused at run time, Sanskrit + line number:** `10 / 0`, `10 % 0`.
**Wraps silently, by decision:** computed overflow.
**Integer division truncates toward zero:** `-7 / 2` gives `-3`.
**`parikshita` is contextual:** `vitti parikshita = 4` compiles.
**Refused, `E_APARIKSHITA_AHVAN`:** a `parikshita` function calling an unmarked function.

## First: you were right, and my brief was wrong for several rounds

**You tested `vitti a = k` on Windows and said it is not refused on v277.** **I ran it on v278: it compiles and prints `41`.**

**I had been writing "Refused: `vitti a = k`" in every brief since round 76.** **It was never true.** **I conflated it with `box[0] = nirmmita(64); outer = box[0]`, which IS refused.**

**That is the fourth false premise in a brief of mine this session.** **You caught it by testing rather than trusting, which is the only reason it surfaced.**

## WS1 — the aliasing hazard, now that we know it is open
**Two variables can own one `kosh` buffer.** **Growing one leaves the other on the old buffer.**

**This is the exact hazard that made me drop the recycling bins in Step 0.** **So:**
**1. Is it unsafe today, or only wasteful?** **Nothing frees the old buffer, so I believe it is wasteful — but confirm.**
**2. What would make it unsafe?** **Name the change that would turn it into a use-after-free.**
**3. And if the answer is "wasteful today, unsafe the moment anything recycles", say what the language should do NOW so that the future change is possible.**

## WS2 — the heavy one: generics
**Sutram has no generics.** **A `kosh` holds 64-bit values; you cannot write a sort that works for two types.**

**Design the smallest generics that makes a real library possible.** **Not C++ templates. Not Rust traits.** **Something a school student can read.**

**And answer honestly: is generics the right next thing, or is there something more valuable?** **You have ranked before; rank again now that the memory work is done: generics, threads, or something I have not named.**

## WS3 — and the audit of my own record
**I have made four false claims in briefs this session:** **`vitti a = k` refused** · **the one-sentence scope rule sufficient** · **15 mutants including a Madhava sign error** · **`nirmmita(-1)` "compiles and runs" when it segfaults.**

**What pattern do you see in those four?** **Not an apology — I want the failure mode named, because if I know the shape I can check for it.**

**And: what should a `## Verified behaviour` block contain so that a claim in it cannot be wrong?** **The format is mine; I would like your version.**
