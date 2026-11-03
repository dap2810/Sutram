# Sutram — ROUND-116: implement the 16 from ChatGPT's spec. One commit.

**Base:** main at v295 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v295

**`Sutram Error` -> `Sutram truti` in the compiler and all eleven packs (v294). 82 goldens updated; `pack messages` passes. The LINKER still says `Sutram Error` and that is deliberate - Claude caught its own overreach on the first gate run and put 16 test lines back.**
**`sankhya_bindu` is WITHDRAWN at v295 - Claude's own R113 integer-dot repair was also wrong and it says so.**
**The arena defect is named: `chain40_reuse.sm` - a block `kosh` passed out through 40 `prakriya`s, second block reuses the slot, program prints 99 (the other block's number), exit 0. Fixed on the branch at `3a6292e`. NOT merged.**
**`rachana` beside an operator refuses with `E_RACHANA_GANIT` (v293).** **A `dasham` into a `mala` converts on main - the raw-bits report was stale.**
**Suite 297, guard 707 programs 0 DIFFER, gates 60 PASS / 1 FAIL (installer payload v243).**

## The specification is written and it is 25,000 characters
**`ChatGPT-to-Sarvam/ROUND-189-SIXTEEN-CONTRACT-IMPLEMENTATION-SPEC.md`** - **16 rows, each with what to refuse on, the exact Sanskrit string, one-line or rewrite, compile-time or runtime.**

**The policy, accepted: mathematical library operations produce the documented result or signal failure through a declared channel. Ordinary runtime integer operators are unchanged.**

**Shared convention from the spec: `MIN = -9223372036854775808`, `MAX = 9223372036854775807`, validate BEFORE the operation can overflow. Do not use `abs(MIN)` to build a guard.**

## WS1 - build it, in the order the spec gives
**One commit. Every function that must refuse, refuses. Every function that is already correct, untouched.**

**If a row cannot be built as written, STOP and report it - do not improvise.** **You did that on the vocabulary round and it was right.**

## WS2 - and the goldens
**Each of the 16 needs a golden showing the refusal.** **And the guard: 707 programs, 0 DIFFER except where a refusal is now emitted.**

## WS3 - and one thing you should fix while you are in there
**`sankhya_bindu` is withdrawn but the spec may list it.** **If it does, skip it - it is already gone.**

## WS4 - and the arena stays unmerged
**Do not merge `claude/r108-arena-review` this round.** **This is 16 functions in one commit; adding an arena would make it impossible to bisect.**
