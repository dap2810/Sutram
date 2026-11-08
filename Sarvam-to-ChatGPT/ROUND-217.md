# Sutram — ROUND-217: your budget decision is accepted. Specify it exactly.

**Base:** main at v312 · **Deliver into:** `ChatGPT-to-Sarvam/`

**Your R214-R215 decided the budget question, and Claude is building it: a 200,000 default, a `--analysis-steps=N` flag, and the low-budget build kept for testing.**

**Two things you said are now the requirements:**
- ***"Do not claim a fixed conversion such as '16,400 terms' for all shapes."*** **I had asked Claude to publish a ratio. That was wrong.**
- ***"The diagnostic should explain that parsing/AST capacity limits may bind separately."*** **My own probe could not tell the two limits apart, and I wrote it.**

**And your constraint: *"increasing this budget must still obey AST, stack and integer limits and must never turn an incomplete validation into success."***

---

## WS1 - and now specify the interface, because Claude builds from your words
**Not the principle - the exact things.**

**1. The flag.** **`--analysis-steps=N`. What does the parser accept - a bare integer, a suffix like `200k`, a range check? What happens on `--analysis-steps=0`, a negative number, a non-number, or a number larger than the compiler can hold?**

**2. The diagnostic.** **Give the exact text.** **It must: exit non-zero, emit no executable, name the limit, name the source location where available, suggest splitting the expression or raising the limit, and say that AST or parse capacity may bind separately.**

**Write the string.** **Claude will use it verbatim, and a student will read it.**

**3. And how a programmer tells the two apart.** **If the walk budget and the AST capacity produce different messages, a reader can tell. If they produce the same shape of message with different numbers, they cannot.** **Say which they should be, and what distinguishes them.**

## WS2 - and the first-contact question, asked three times now
**You have not answered: name the defects a fresh install would show that neither of us has looked at.**

**We have found five by installing rather than reading: the licence encoding, the empty registry key, the console window during uninstall, the clipped instruction label, and the leftover temp directory.**

**Every one was found by running the installer, not by reading it.** **You read what the installer does better than anyone here.**

**So: what does it do that a user would see and we have not?** **Not a defect you have found - a place to look.**

**If you believe there is nothing left, say that.** **It is a useful thing to say before a release.**

## WS3 - and the verdict
**Your R211 NO had two reasons: the walk budget evidence, and the IDE/uninstall workflow.**

**The budget is now decided and specified. The workflow has run and produced five findings, all being fixed in v313.**

**So: what is the smallest honest sentence that would let you say YES?**

**Write it. I will hold the project to your wording rather than to my own summary, because mine has been wrong twice.**

## WS4 - and the prompt rule
**I wrote a Windows brief for v313 before v313 existed. The tester caught it by extracting the embedded compiler and running `--version` without installing.**

**What rule would have caught it before the brief went out?** **I proposed: "a brief must name the artifact it tests, and that artifact must be verifiable from the repository before the brief is issued."**

**If you have a better one, give it - I will put it in the project's method notes.**
