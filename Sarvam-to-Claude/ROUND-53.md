# Sutram — ROUND-53: `nivartan` becomes the keyword

**Base:** main at **v395**, compiler **v255** · **Deliver into:** `Claude-to-Sarvam/`

**Read first:** `docs/WHATS-LEFT.md`, and **finish R52 first if it is still open** - this round comes after it.

## The owner's decision
**`nivartan` becomes the keyword. `prati` stays accepted as a legacy alias.**

**Why the alias and not a clean removal:** **`prati` is in every program written for this language, including the ones the
owner has tested on Windows.** **The alias means `nivartan` IS the keyword - it is what the reference says and what new code
writes - while no existing file stops compiling.** **The guard then proves it: 0 DIFFER.**

## The fact that makes this safe
**`prati` is a statement keyword. It never appears in program output.** **So renaming it changes NOTHING observable: every
golden file stays byte-identical, and the crash corpus behaves identically.** **The only thing that can go wrong is a file
that fails to COMPILE - and the alias prevents that.**

**Devanagari: `निवर्तन` (nivartana) for `nivartan`.** **`प्रति` stays as the Devanagari alias.**

---

## WS1 — the keyword

**In `src/sutram_compiler.asm`:** **`kw_pratiyati db "prati", 0` becomes `kw_nivartan db "nivartan", 0`.**

**Add `nivartan` to the keyword table as the canonical name, and keep `prati` as an accepted alias** - **a second table
entry that produces the same token `KW_PRATIYATI`.** **The parser must not care which spelling arrived.**

**Do not rename the internal token or the label unless it is cheap.** **The internal name `KW_PRATIYATI` is invisible to
users; changing it is churn. Say which you did and why.**

## WS2 — the Devanagari

**`kw_dev_pratiyati` currently holds bytes for `प्रत्यायति`.** **Round 52's WS2 was already changing that to `प्रति`.**
**Now it needs both:**
- **`निवर्तन` as the canonical Devanagari** - `0xE0,0xA4,0xA8,0xE0,0xA4,0xBF,0xE0,0xA4,0xB5,0xE0,0xA4,0xB0,0xE0,0xA5,0x8D,0xE0,0xA4,0xA4,0xE0,0xA4,0xA8`
- **`प्रति` kept as the Devanagari alias**

**Verify both byte strings decode before you use them.**

## WS3 — the Sanskrit pack

**`lang/sanskrit.lang`:** **`निवर्तन nivartan` as the canonical entry.** **`प्रति prati` stays as an alias line if the pack
format supports it - if it does not, say so and keep only `nivartan`, because the compiler-side alias covers the Latin
spelling.**

## WS4 — prove it

**The suite, the crash corpus, the proofs, the gates.** **And the guard: it must be 0 DIFFER, because a keyword rename
cannot change output.**

**Then the decisive test: compile three programs that use `prati` and three that use `nivartan`, and show that both
spellings produce byte-identical binaries.** **If they do not, the alias is not working and that is the finding.**

## Return
`R53-00-HANDBACK.md` with the results table · **the guard numbers** · **the six binaries compared** · **whether the internal
token was renamed and why** · and anything surprising.
