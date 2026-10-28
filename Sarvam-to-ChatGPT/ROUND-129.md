# Sutram — ROUND-129: the memory vocabulary, dictionary-checked before we build anything

**Base:** main at **v404** · **Deliver into:** `ChatGPT-to-Sarvam/`

**Read first:** `docs/MEMORY-MODEL.md`, `docs/OPEN-ISSUES.md`, `docs/WHATS-LEFT.md`.

## Why now
**The owner has set aside the vocabulary work to build memory management next.** **Sutram has `nirmmita` (allocate) and NO
`free`, and `kosh` leaks about 15.3 bytes per item.**

**The owner has refused a garbage collector - it needs a runtime, and this language's promise is a native binary with no
runtime.** **So the choice is between explicit free, region allocation, and compile-time ownership.**

## WS1 — the five words, checked
**I proposed these and I have been wrong four times this session on Sanskrit.** **Check each one and say plainly if it is wrong:**

| My proposal | What I claim it means | What I want to know |
|---|---|---|
| **`nyāsa`** (न्यास) | **a deposit held in trust, which must be returned** | **Is it the right word for "allocate"? Is the obligation sense really there?** |
| **`pratyarpana`** (प्रत्यर्पण) | **returning a deposit** | **Is this the right word for "free"?** |
| **`kośa`** (कोश) | **sheath, as in the pañcakośa - nested layers shed whole, outside in** | **Is a `kośa` a legitimate word for a memory REGION?** |
| **`saṃskāra`** (संस्कार) | **the impressions left by past actions - the residue in reused memory** | **Is this honest, or am I romanticising?** |
| **`ṛṇa`** (ऋण) | **debt** | **Is "you owe three deposits" a fair use of the word?** |

**And the one I most want an answer to: is there a SINGLE Sanskrit word for "the act of letting go of what you hold"?**
**Because that is what `free` is, and English does not have a clean word for it either - `free` also means "no cost".**

## WS2 — the honest design question
**Three options, and I want your judgement on which fits a language that must stay runtime-free:**

1. **Explicit `nyāsa` / `pratyarpana`** - **the programmer pairs them. Leaks are possible.**
2. **`kośa` regions** - **allocate is a pointer bump, free is a pointer reset. Faster than malloc. Nothing can leak, because there is nothing to forget.**
3. **Compile-time ownership** - **Rust's approach. Zero runtime cost, but it constrains how you write.**

**My recommendation is 2 as the default and 1 for the low-level user.** **Tell me if that is wrong, and why.**

## WS3 — the measurement I want you to specify
**I will measure arena allocation against malloc myself.** **Tell me the exact experiment that would settle it:**
**how many allocations, what sizes, how many iterations, and what to measure.** **I want a benchmark whose result I cannot
argue with, whichever way it comes out.**

## Return
`ROUND-129-MEMORY-VOCABULARY.md` with: the five word verdicts, your answer on the single "let go" word, your judgement on the
three options, and the benchmark spec. **No code.**
