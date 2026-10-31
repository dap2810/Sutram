# Sutram — ROUND-80: arithmetic that lies — overflow and division by zero

**Base:** main at v275 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour, tested by me on the shipped binary

**All of your R77/R78/R79 claims hold as reported.** **And your R79 is the strongest result of this work: a real 185-line program, 185 MB → 110 MB with blocks around the allocating functions, 7 MB with library temporaries in blocks, and ~5% faster.** **My own 200,000-iteration test found 27,620 KB → 11,772 KB.** **Two independent measurements, same verdict.**

## WS1 — what I found while doing the real-program test

**The program's total overflowed.** **So I tested the arithmetic directly:**

| Program | Result |
|---|---|
| **`9223372036854775807 + 1`** | **`-9223372036854775808`** — silent wraparound |
| **`4000000000 * 4000000000`** | **`-2446744073709551616`** — silent wraparound (real answer is 16,000,000,000,000,000,000) |
| **`1 / 0`** | **SIGFPE, exit 136 — a crash with no message** |

**So Sutram has no overflow story and no divide-by-zero story.**

**For a language aimed at school students, this is worse than it looks.** **A student squaring large numbers gets a negative answer and no explanation.** **They will conclude they do not understand arithmetic — which is exactly the failure Gemini named about the parser, in a different place.**

## WS2 — the fixes, in order of value per line

**1. Division by zero: one compare, and it is cheap.** **`Sutram Error: shunye vibhajanam na sambhavati`.** **Do this one first — it is a crash today, and a crash is the worst outcome in a language whose errors are meant to be readable.**

**2. Overflow of literal arithmetic, at compile time.** **`4000000000 * 4000000000` is computable by the compiler.** **If the constant result does not fit in int64, refuse it at compile time.** **Zero run-time cost, and it catches the textbook case.**

**3. Run-time overflow checking: measure it before deciding.** **`jo` (overflow flag) after an add, or `imul` with a check, costs a branch per operation.** **Run the existing benchmarks with it on and tell me the percentage.** **If it is more than 10%, do not ship it — document C-like wraparound instead.**

**And whatever the answer, write the behaviour into `docs/LANGUAGE-REFERENCE.md` in one sentence a student reads.** **Silence is the only unacceptable option.**

## WS3 — and check the library for the same class
**Do any of the 24 library modules compute something that overflows for ordinary inputs?** **`ganita`'s factorial, `sankhyiki`'s sums, `madhava`'s series terms.** **If a student calls a library function with a plausible number and gets a negative result, that is our bug, not theirs.**
