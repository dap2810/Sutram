# Sutram — ROUND-128 (final): `nivartanam` - document it

**Base:** main at **v395** · **Deliver into:** `ChatGPT-to-Sarvam/`
**Supersedes both earlier ROUND-128 issues.** **This is the final word.**

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

## WS1 - the reference entry
**Rewrite the `prati` entry in `docs/LANGUAGE-REFERENCE.md` as `nivartanam`.** **Include the Devanagari, the meaning
(returning, turning back - `ni` + `vṛt`), the alias note, one runnable example with its exact output, and the honest line:
this is an improvement in precision - `prati` was a prefix, `nivartanam` is the noun.**

## WS2 - every document showing `prati`
**List them with exact replacement lines in the `path | mode | anchor_exact | insert_exact_line` shape.**
**Historical changelog entries stay as they are - a record of what was true then is still true.** **Mark them
KEEP_HISTORICAL.**

## WS3 - and the one question still worth asking
**`prati` was 5 letters; `nivartanam` is 10.** **It appears in every function ever written in this language.**
**The owner has decided and the migration is running - do NOT reopen the choice.**
**But for the record: is there a shorter genuine Sanskrit noun for "return" that is not a fragment?** **If there is, name it
once and I will note it for a future version. If `nivartanam` is the best available, say so.**

## Return
`ROUND-128-NIVARTANAM-DOCS.md` with the reference entry · the exact-insertion list · the KEEP_HISTORICAL list · and your
answer to WS3.
