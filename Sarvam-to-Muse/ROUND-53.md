# Sutram — ROUND-53 (final): migrate to `nivartanam` - GATE OPEN, GO

**Base:** main at **v395** · **Deliver into:** `Muse-to-Sarvam/`
**Supersedes both earlier ROUND-53 issues.** **This is the final word, and nothing is waiting.**

## THE WORD IS FINAL: `nivartanam` (निवर्तनम्)

**The owner has confirmed it.** **`निवर्तनम्` = `0xE0,0xA4,0xA8,0xE0,0xA4,0xBF,0xE0,0xA4,0xB5,0xE0,0xA4,0xB0,0xE0,0xA5,0x8D,0xE0,0xA4,0xA4,0xE0,0xA4,0xA8,0xE0,0xA4,0xAE,0xE0,0xA5,0x8D` - 27 bytes.** **Decode it and confirm it prints before using it.**

**Meaning: returning, turning back - `ni` + `vṛt`.** **This is the genuine noun for "return", and it is the word I believed
was right, so the owner and I now agree.**

**`prati` stays accepted as a legacy alias so no existing program stops compiling.**

## Why this is safe
**`prati` is a statement keyword and never appears in program output.** **So renaming it changes NOTHING observable: every
golden stays byte-identical, the crash corpus behaves identically, and the guard reads 0 DIFFER.** **The only failure mode is
a file that does not COMPILE, and the alias removes it.**

**THE GATE IS OPEN.** **The owner confirmed the word, so nothing waits on a spelling answer any more.**

---

## WS1 - count it
**Count every `prati` in the tree:** `lib/`, `examples/`, `tests/`, `docs/`. **Numbers by directory.** **Report that first.**

## WS2 - migrate `lib/`
**Every `prakriya` ending in `prati x` becomes `nivartanam x`.** **Library proofs must still pass 226/226.**
**If any fails, that body changed in a way it should not have - revert and list it.**

## WS3 - migrate `examples/`
**Every `prati` becomes `nivartanam`.** **Compile, run, compare against the UNCHANGED golden - it must be byte-identical,
because `prati` never prints.** **A golden that differs means the rename broke something: revert that file and list it.**

## WS4 - the honest check
**After migration, does any file still use `prati`?** **List it and say why.** **Re-run the WS1 counts and give before and
after.**

## Return
`ROUND-53-NIVARTANAM.md` with the counts · every file changed · any file reverted with the reason · the library proof result ·
the suite result.
