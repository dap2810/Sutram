# Sutram — R146: the memory model is built and measured. Audit it as a whole.

**Base:** main at v270 · **Deliver into:** `ChatGPT-to-Sarvam/`

## What now exists, all verified by me

| | |
|---|---|
| **allocation** | **2-8 ns** (was ~62,500 ns) |
| **`mandapa` block** | **releases memory - 65,216 KB down to 14,464 KB over 1,000,000 allocations** |
| **`outer = buf + 64`** | **refused** |
| **`m[0] = buf`** | **refused** |
| **copying the data out** | **allowed** |
| **the error message** | **`E_SCRATCH_ESCAPE: asthayi smriti bahir na gacchati` - in Sanskrit** |

**Five steps designed over many rounds, all five now built and measured.** **This is the first round where I can say that.**

## WS1 — audit it as a whole, and find what the composition breaks
**Every step was tested alone.** **You are the one who has consistently found what a design misses when it is composed.**

**So: given the five pieces as they now exist, what breaks when they are used together?** **Specifically:**
- **a block inside a loop that grows an outer `kosh`**
- **a `prakriya` taking a scratch pointer and returning a derived value**
- **deep recursion with a block in each frame**
- **a block that exhausts the scratch range**

**Name the composition that fails.** **If none fails, say that too - but only if you have looked.**

## WS2 — and the claim I can now make, checked
**I want to write in the README: "Sutram's memory is released by scope, checked at compile time, with no garbage collector and no runtime."**

**Is that sentence true of the compiler as it now exists?** **If any part of it is not, say which word is wrong.** **That sentence will be read by people deciding whether to use this language, and I would rather correct it now than defend it later.**

## WS3 — and the honest limit, in the place a programmer will read it
**A `kosh` of scratch pointers is not seen by the check.** **Where should that be said?** **The reference entry, the error message, or both?** **Give me the sentence, and I will put it where you say.**
