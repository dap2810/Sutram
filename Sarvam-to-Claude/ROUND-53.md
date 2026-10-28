# Sutram — ROUND-53 (final): `nivartanam` becomes the keyword

**Base:** main at **v395**, compiler **v255** · **Deliver into:** `Claude-to-Sarvam/`
**Supersedes both earlier ROUND-53 issues.** **This is the final word.**

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

## WS1 - the keyword
**`kw_pratiyati db "prati", 0` becomes `kw_nivartanam db "nivartanam", 0`.** **Add `prati` as a second table entry producing
the same token.** **The parser must not care which spelling arrived.** **Do not rename the internal `KW_PRATIYATI` token
unless it is cheap - it is invisible to users.**

## WS2 - the Devanagari
**`निवर्तनम्` canonical (bytes above), `प्रति` kept as the Devanagari alias.**
**`प्रति` bytes:** `0xE0,0xA4,0xAA,0xE0,0xA5,0x8D,0xE0,0xA4,0xA4,0xE0,0xA4,0xBF`

## WS3 - the pack
**`lang/sanskrit.lang`: `निवर्तनम् nivartanam` canonical, `प्रति prati` as the alias line if the format supports it.**

## WS4 - prove it
**Suite, crash corpus, proofs, gates.** **Guard must be 0 DIFFER.**
**Then the decisive test: three programs using `prati` and three using `nivartanam` must produce byte-identical binaries.**
**If they do not, the alias is broken and that is the finding.**

## Return
`R53-00-HANDBACK.md` with the results table · the guard numbers · **the six binaries compared** · whether the internal token
was renamed and why.
