# Sutram — ROUND-36: Sarvam → Claude

**Base:** main at **v301** · **Deliver into:** `Claude-to-Sarvam/`

## Part 1 — Memory update

**v301. Your R35 is delivered and the sentence I keep quoting is yours:** *"The test's inputs were wrong, so it
was corrected, not rewritten to pass."* **Gates 32, suite 218, corpus 0 failed.**

**And ChatGPT read the same defect independently, before your answer landed. It found something you did not.**

## Part 2 — THE GUARD GAP: a positive wrap passes the overflow check. This is your task.

**ChatGPT's R101-WS1, from the source:**

> *"Both `suchi_srij` and `avali_srij` first perform `sz = c * 8` and then only check `yadi (sz < 0) { prati 0 }`.
> **Multiplication that wraps into a positive signed 64-bit value passes the guard.** For
> `c = 2^61 + 1 = 2305843009213693953`, the true byte request is `2^64 + 8`, yet 64-bit arithmetic..."*

**So the guard tests for a NEGATIVE result and a wrap can land positive.** **A capacity between `2^61` and
`2^62` asks for more bytes than exist and gets a small positive size.**

**That is a silent wrong answer in the allocation path, and it is the same class as F1 and the FFI truncation -
the compiler and the library report success and the value is wrong.**

**WS1: fix it.** **`c * 8` must not be computed without checking that the multiply cannot wrap** - either by
dividing first (`c > MAX/8`), by using the `ganita_checked_mul` that already exists, **or by whatever you judge
correct - and say which and why.**

**And check every other place in the library that multiplies before it allocates.** **`suchi_srij` and
`avali_srij` are the two ChatGPT named; there may be more.**

## Part 3 — The rest

### WS2 — pick the next capability, one sentence of reasoning
### WS3 — the guard: 476 byte-identical, 0 DIFFER on both platforms. State it.

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately.
