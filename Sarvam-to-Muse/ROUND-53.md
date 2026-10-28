# Sutram — ROUND-53 (corrected): migrate to `nirvatanam` — BUT DO NOT START YET

**Base:** main at **v395** · **Deliver into:** `Muse-to-Sarvam/`
**Supersedes the earlier ROUND-53.** **Read this one; the word changed.**

## GATE - read this first
**The owner's word is `nirvatanam` (निर्वतनम्).** **ChatGPT is being asked to confirm the spelling in ROUND-128 before this
migration runs.**

**So: do WS1 now, and WAIT for ChatGPT's answer before WS2 and WS3.**
**If ChatGPT says the spelling is wrong, the migration is one word different and it is cheaper to find out now than after
1,400 sites move.**

## Why this is safe when it does run
**`prati` is a statement keyword and never appears in program output.** **So every golden must stay BYTE-IDENTICAL.**

---

## WS1 — count it, now
**Count every `prati` in the tree:** `lib/`, `examples/`, `tests/`, `docs/`. **Numbers by directory.** **That is the change
surface and it is the first thing to report.** **Do this before the gate opens.**

## WS2 — migrate `lib/` (after the gate)
**Every `prakriya` ending in `prati x` becomes `nirvatanam x`.** **Library proofs must still pass 226/226.**

## WS3 — migrate `examples/` (after the gate)
**Every `prati` becomes `nirvatanam`.** **Compile, run, compare against the UNCHANGED golden.** **A golden that differs means
the rename broke something - revert that file and list it.**

## WS4 — the honest check
**After migration, does any file still use `prati`?** **List it and say why.** **Re-run the WS1 counts and give before and
after.**

## Return
`ROUND-53-NIVATANAM.md` with the counts · every file changed · any file reverted with the reason · the library proof result ·
the suite result. **And say explicitly whether you waited for the gate.**
