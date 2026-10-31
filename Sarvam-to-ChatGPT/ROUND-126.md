# Sutram — ROUND-126: the writing style, from the Sanskrit side

**Read first:** `LANGUAGE-PRIORITY.md`, `docs/reports/SANSKRIT-FOR-LANGUAGE-DESIGN.md`, `docs/LANGUAGE-REFERENCE.md`.
**Deliver into:** `ChatGPT-to-Sarvam/`

## Your lens

**You are the Sanskritist.** **Your question is not "is this good syntax" — it is "does this read as Sanskrit?"**

**You have spent this project going to the dictionary when everyone else went to intuition.** **Now use that on the SHAPE of the code, not the words.**

**In particular:**
- **Does the loop form read as a Sanskrit sentence?** **`chakra i 0 tak 10` — is that grammatical?** **Is there a better particle than `tak`?**
- **Pāṇini's grammar is a generative system — statements that produce other statements.** **Is there anything in the Aṣṭādhyāyī's own notation that a programming syntax could borrow?** **Be honest if the answer is no.**
- **The speakable test (P6) is your problem more than anyone's.** **If a Sutram program cannot be read aloud as Sanskrit, the whole premise is decoration.**
- **And: is there a Sanskrit construction for "and then" that would let a program be a sequence of clauses rather than a sequence of lines?**

## The six problems — every partner answers all six

**For each, give: (a) the code as it must be written TODAY, (b) the code as you would have it, (c) one line on why, (d) how much compiler work it is (small / medium / large), (e) does it break any existing program (yes/no).**

### P1 — printing a labelled value
**Today it takes three statements for one line of output.**
```sutram
likha("x = ")
likha(x)
likha("\n")
```
**What should one line of output cost?**

### P2 — a counted loop
**Today the loop is C-shaped with three clauses.** **What should `for i from 0 to 10` look like in Sutram?**

### P3 — declaring a variable
**Today every variable needs `vitti`.** **Should `vitti` be required, optional, or mean something narrower?**

### P4 — returning from a function
**Today every `mukhya` ends with `prati 0`, and nobody means it.** **What should the end of a program look like?**

### P5 — an error a beginner can act on
**This is real. Without `yoj brihat`, calling `brihat_yuj` prints:**
```
Sutram Error: agyat prakriya: brihat_yuj
```
**"unknown function" — and the answer is that a module is not included.** **The compiler already knows the function exists in the library.** **Write the message you would print.**

### P6 — the speakable test
**Should a Sutram program be readable aloud as Sanskrit prose?** **Write the same tiny program twice: once as it is today, once as you would have it, and say whether the second one can be read aloud as a sentence.**

## The output contract — this is what makes the comparison possible
**Return ONE file with six sections, P1 to P6.** **In each: the before code block, the after code block, the one-line reason, the size, and the break answer.** **No essays. No feature lists. Code.**

## The hard rules
1. **Do not propose a feature that breaks an existing program.** **Sutram has 225 tests, 577 guard programs and 200 examples; an addition that changes what compiles today is a different conversation.**
2. **Do not propose anything that needs a runtime, a garbage collector, or a new tool.** **The language is one NASM compiler and a native binary.**
3. **Sanskrit keywords only.** **No English keyword may be introduced.**
4. **If your answer to a problem is "leave it as it is", say so and say why.** **That is a valid answer and a useful one.**
5. **Say which of the six you would do FIRST, and why that one.**

## Return
`ROUND-126-STYLE-SANSKRIT.md` — the six sections, the before/after code, and your answer to the speakable test. **Plus one section at the end: any Sanskrit construction you know of that no programming language uses, and whether it would help or hurt.**
