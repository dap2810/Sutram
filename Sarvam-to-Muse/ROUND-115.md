# Sutram — ROUND-115: verify the 16 after Claude builds them, and the withdrawal

**Base:** main at v295 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v295

**`Sutram Error` -> `Sutram truti` in the compiler and all eleven packs (v294). 82 goldens updated; `pack messages` passes. The LINKER still says `Sutram Error` and that is deliberate - Claude caught its own overreach on the first gate run and put 16 test lines back.**
**`sankhya_bindu` is WITHDRAWN at v295 - Claude's own R113 integer-dot repair was also wrong and it says so.**
**The arena defect is named: `chain40_reuse.sm` - a block `kosh` passed out through 40 `prakriya`s, second block reuses the slot, program prints 99 (the other block's number), exit 0. Fixed on the branch at `3a6292e`. NOT merged.**
**`rachana` beside an operator refuses with `E_RACHANA_GANIT` (v293).** **A `dasham` into a `mala` converts on main - the raw-bits report was stale.**
**Suite 297, guard 707 programs 0 DIFFER, gates 60 PASS / 1 FAIL (installer payload v243).**

## WS1 - `sankhya_bindu` is withdrawn. Verify the withdrawal works.
**Claude withdrew it at v295.** **ChatGPT designed the tombstone: a reserved name that refuses at compile time with a specific diagnostic.**

**Test:**
- **`sankhya_bindu(a, b)` - does it refuse, and with what message?**
- **`sankhya_dot(a, b)` - the old alias. Does it also refuse?**
- **Is the name still RESERVED, so a user cannot declare a `prakriya` with that name?**
- **And does the reference say why?**

**A withdrawal that leaves the name callable is not a withdrawal. Test that it is gone.**

## WS2 - and the 16, after Claude builds them
**Claude is implementing ChatGPT's spec this round.** **When it lands, verify each of the 16 the way you found them: run the probe, read the body, and say whether the refusal is correct and the message is right.**

**And the question only you ask: does the refusal fire on the RIGHT cases and not on legitimate ones?** **A `dvardh` that refuses at MAX is right. A `vardh` that refuses at MAX-1 is wrong.**

## WS3 - and the segfault you mentioned
**Your R114 said "the segfault moved (not gone)."** **Name where it is now.** **A segfault that moved is a segfault that is still there.**
