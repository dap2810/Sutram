# Sutram — R190: the English audit and error handling, which you said were delivered

**Base:** main at v295 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v295

**`Sutram Error` -> `Sutram truti` in the compiler and all eleven packs (v294). 82 goldens updated; `pack messages` passes. The LINKER still says `Sutram Error` and that is deliberate - Claude caught its own overreach on the first gate run and put 16 test lines back.**
**`sankhya_bindu` is WITHDRAWN at v295 - Claude's own R113 integer-dot repair was also wrong and it says so.**
**The arena defect is named: `chain40_reuse.sm` - a block `kosh` passed out through 40 `prakriya`s, second block reuses the slot, program prints 99 (the other block's number), exit 0. Fixed on the branch at `3a6292e`. NOT merged.**
**`rachana` beside an operator refuses with `E_RACHANA_GANIT` (v293).** **A `dasham` into a `mala` converts on main - the raw-bits report was stale.**
**Suite 297, guard 707 programs 0 DIFFER, gates 60 PASS / 1 FAIL (installer payload v243).**

## Your R189 said R184 and R185 were delivered, not dropped
**I asked for links and completion limits and you gave them.** **Good - that is the answer I wanted.**

**This round is what comes after them.**

## WS1 - the remaining English, now that `truti` landed
**`Sutram Error` is `Sutram truti` everywhere except the LINKER, which Claude deliberately left alone.** **So one English word remains, in a smaller place.**

**Two questions:**
- **Should the linker say `Sutram truti` too?** **What would it cost - is it the same token in the same place, or a different mechanism?**
- **And after the 22 renames and `truti`, what English is left in the tree?** **Your R184 audit found the number. Give me the count now, post-`truti`, and the list.**

## WS2 - and the error-handling design, which I have not seen the answer to
**55 codes, no `try`/`catch`.** **I asked you to sort the 55 by whether a running program could respond to them.** **That sort is the answer to whether this language needs exceptions at all.**

**If it is in R185, point me at it. If it is not, write it now - it is reading work and it is the last unanswered design question in the project.**

## WS3 - and one thing you should know
**Muse found that Claude's `sankhya_bindu` repair changed the contract: three arguments with an explicit `n`, which trusts `n` and does not refuse unequal lengths - where your R186 specified two collections with an equal-length check.**

**Claude then withdrew it entirely.** **So the contract question is now moot for that function - but it is not moot in general.**

**Should every library function with a length or count parameter trust it, or verify it?** **That is a rule the whole library needs, and nobody has written it.**
