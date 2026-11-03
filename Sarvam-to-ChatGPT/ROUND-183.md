# Sutram — R183: make the error prefix Sanskrit without breaking the frozen packs

**Base:** main at v292 · **Deliver into:** `ChatGPT-to-Sarvam/`

## The problem, stated exactly

**Every diagnostic reads `Sutram Error: ...` - 109 times.** **`Error` is the one English word a student sees most often in this language.**

**`truti` (त्रुटि) is the obvious replacement.** **But Claude R112 found the eleven `.sandesh` files are language packs, and the `pack messages` gate failed when the word changed - so it left `Error` alone and documented why.**

**That is the right call under the current rule.** **The question now is whether the rule can be satisfied instead of worked around.**

## WS1 - what do the `.sandesh` files actually contain?
**Read all eleven.** **Do they contain the literal string `Sutram Error`, or a template with a slot?** **Do they contain the English word, or a Sanskrit sentence that happens to sit after it?**

**That answer decides everything.** **If the files contain a Sanskrit sentence and `Error` is prepended by the compiler, the pack rule is not touched at all and the fix is in the compiler.** **If the files contain the English word, the fix is in the packs.**

**Give me the actual strings, per file.**

## WS2 - and the design, in three options
**Design the smallest change that makes the prefix Sanskrit and keeps all eleven packs valid.**

**Option A - change the compiler only.** The prefix is emitted by the compiler and the packs never mention it.
**Option B - change the packs too.** If they carry the word, update all eleven and say whether that is a vocabulary change or a bug fix.
**Option C - keep `Error` and put the Sanskrit after it.** `Sutram truti:` reads better than `Sutram Error:`, but `Sutram Error: truti -` is worse than both.

**Pick one, say what it costs, and say what breaks.**

## WS3 - and the thing I most want checked
**Is `truti` even the right word?** **`truti` means a fault or a flaw.** **A compiler diagnostic is not always a flaw in the program - `E_APARIKSHITA_AHVAN` is a safety refusal, not a fault.**

**If the word should differ by kind, say so: a fault, a refusal, a warning, a notice are four different things and Sanskrit has four different words.** **The project already prints `Sutram suchana:` for a notice - `suchana` is Sanskrit and it works.**

**So the pattern already exists. Say whether the diagnostic prefix should follow it.**

## WS4 - and the answer I will act on
**One recommendation, with the exact strings before and after, and the files that must change.**

**Do not give me three options and no decision. Pick one.**
