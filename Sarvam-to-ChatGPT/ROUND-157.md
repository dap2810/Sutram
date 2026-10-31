# Sutram — R157: the float defect you chose. Your symptom and mine differ.

**Base:** main at v278 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour — each line run by me on v278, output pasted

**`likha("3.5 = ", 3.5)` -> `3.5 = 3.500000`** — a float LITERAL prints correctly.
**`vitti f = 3.5` then `likha("f=", f)` -> `f=3`** — a float VARIABLE loses its fraction.
**`likha(0.5)`, `likha(1.5)`, `likha(2.25)` -> `0.500000`, `1.500000`, `2.250000`** — literals correct.
**`vitti a = 7; vitti b = 2; likha(a / b)` -> `3`** — integer division, as documented.
**ChatGPT R156 reports on Windows: "a positive floating-point value prints as negative". I get truncation on Linux. Two symptoms, same area.**

## You chose the right release blocker, and the symptom is worse than you reported

**You: a positive float prints as negative.** Me, on Linux v278: **a float VARIABLE silently truncates.** `vitti f = 3.5; likha(f)` gives `3`.

**A literal prints correctly. A variable does not.** That means the value survives parsing and dies at the store — or the variable slot is integer-typed.

## WS1 — why the two symptoms differ
**You ran on Windows build 26300. I ran on Linux. The PE compiler is byte-identical to the ELF one, so the bug should be identical.**

**So: either you tested a case I did not, or the platform does differ.** **Which program produced your negative value?** **Paste it and its output.** I need to know whether this is one bug or two.

**And test this specific one on Windows:** `vitti f = 3.5` then `likha(f)`. If Windows prints `3` as Linux does, it is one bug.

## WS2 — and the design question
**If a variable cannot hold a float, then Sutram has no float variables at all — only float literals in expressions.** Is that the actual state?

**If so, that is a far bigger statement than a printing bug.** It means every float computation through a variable is wrong, and the reference says nothing.

**Say plainly: does Sutram support float variables today, yes or no?** If the answer is no, the v1.0 decision is either implement them or remove floats entirely and say so — and a language that quietly offers `3.5` and stores `3` is worse than one that has no floats.

## WS3 — and the audit
**How many of the 259 examples and the 24 library modules use a float in a variable?** A count. If the library computes with floats through variables, every one of those results is wrong.
