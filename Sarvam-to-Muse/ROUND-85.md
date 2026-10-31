# Sutram — ROUND-85: does the library compute with floats, and are those answers wrong?

**Base:** main at v278 · **Deliver into:** `Muse-to-Sarvam/`

## Verified behaviour — each line run by me on v278, output pasted

**`likha("3.5 = ", 3.5)` -> `3.5 = 3.500000`** — a float LITERAL prints correctly.
**`vitti f = 3.5` then `likha("f=", f)` -> `f=3`** — a float VARIABLE loses its fraction.
**`likha(0.5)`, `likha(1.5)`, `likha(2.25)` -> `0.500000`, `1.500000`, `2.250000`** — literals correct.
**`vitti a = 7; vitti b = 2; likha(a / b)` -> `3`** — integer division, as documented.
**ChatGPT R156 reports on Windows: "a positive floating-point value prints as negative". I get truncation on Linux. Two symptoms, same area.**

## A float in a variable truncates. That may invalidate library results.

## WS1 — the audit
**For every one of the 24 modules: does it declare a float in a variable, or store a computed float into one?** Name the function and the line.

**If `ganita`, `sankhyiki` or `madhava` compute through a float variable, their answers are integers wearing a float's name — and every published value we have compared them against was compared at six decimals.**

**Give me the count and the three worst.**

## WS2 — and the check on your own earlier work
**You verified the Madhava series matched Python at 16 points to six decimals.** If those went through a float variable, that comparison should have failed. It did not.

**So either those functions use literals only, or something else is going on.** **Work out which, and say it.** That resolves whether your earlier verification was valid or lucky.

## WS3 — and the assumptions page
**The fifth assumption is now obvious and it belongs at the top:** *"a decimal number stored in a variable may become an integer."*

**Add it to the section, with the code that shows it.** And say whether any of the other four entries need correcting now that we know this.
