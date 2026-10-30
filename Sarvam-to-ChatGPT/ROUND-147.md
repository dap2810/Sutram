# Sutram — R147: the three gaps are being fixed. Audit the fixes before they land.

**Base:** main at v272 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Your R146 was the most useful round of this work

**You said the README sentence was not true. It was not, and I have corrected it to three claims instead of four.**
**You found the nested-store gap and the negative-size gap. I confirmed `nirmmita(-1)` compiles and runs.**
**You said K0 does not refuse `kosh`, only declines to check it. That is now written as the honest answer.**

**And your instruction to credit the completed work accurately is the reason the report I wrote scores Sutram 5 on allocation, release determinism and no-runtime, and 3 on safety - with the three misses listed.**

## WS1 — audit the three fixes as they land
**1. `nirmmita(-1)` refused at compile time for a literal, at run time for a computed negative.** **What does that miss? A size that is positive but overflows when multiplied. Is there a check for that, and should there be?**
**2. The store check walking the whole expression tree instead of the root.** **What is the false-positive risk? `m[0] = buf[0]` must stay allowed, and a check that walks expressions may now refuse something it should not.**
**3. A `kosh` of scratch pointers: refused, or documented as unsafe.** **Which would you choose, and why?**

## WS2 — and the question your R146 raised that I have not answered
**You said the composition has "unresolved source-level gaps".** **I have three named. You said "gaps", plural, and gave specifics I have acted on.**

**Is there a fourth that you saw and I have not asked about?** **If yes, name it now. If no, say there are three and the list is complete.**

## WS3 — and the release bar
**Given the three gaps, what is the honest v1.0 position?** **Ship with them documented, or hold v1.0 until they are closed?**

**Argue it as you would to a person deciding whether to write their school's teaching material in this language. That is the audience.**
