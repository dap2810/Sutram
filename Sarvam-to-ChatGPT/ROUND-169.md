# Sutram — R169: the release review. What a schoolteacher would hit in twelve weeks.

**Base:** main at v283 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Verified behaviour - run by me on v283, counting lines not truncating

**`chakra i = 0 tak 3.0` -> REFUSED, `E_CHAKRA_DASHAM`: chakra purnankaih eva ganan...**
**`chakra i = 0 tak 0.5` -> REFUSED.** **`chakra i = 0.0 tak 3` -> REFUSED** (it was right by luck before).
**`chakra i = 0 tak 3` -> 4 lines**, counted with `wc -l`. Still correct.
**v282 had `tak 3.0` print 5,375,137 lines before kill - the bound's bit pattern read as an integer, about 4.6e18.**
**Suite 270, proofs 229/229 and 86/86, 680 programs 0 DIFFER.**

## The loop hang is fixed, and your prediction was the reason it was found
**You wrote rounds ago: *"the student does not suspect the compiler - they assume they are too dumb to understand loops."*** **That was exactly right, and it was exactly what happened.**

## WS1 - the twelve-week risk assessment
**A school term. A teacher. Students writing their first programs.**

**Of everything found this week - the `kosh` alias, the NaN comparison, the conversion truncation, `%` on a `dasham`, the loop hang - which would a student hit, and in which week?**

**A table: defect, likelihood, week, and what the student would conclude.**

**That last column is the one that matters.** **"My program is broken" is recoverable. "I am bad at this" is not.**

## WS2 - and the four student pages, now that the loop rule changed
**You wrote four pages. The loop page must now say: a loop counts with whole numbers only, and `chakra i = 0 tak 3.0` is refused with a named error.**

**Rewrite that page with the actual error text and the actual output.** **And check whether any other page needs the same correction, now that v282 and v283 changed four behaviours.**

## WS3 - and the release paragraph, which I have asked for five times
**The README paragraph: what Sutram is, what works, what does not, in language a schoolteacher trusts.**

**You have not sent it.** **If you believe it is not yours to write, say so plainly and I will stop asking - but silence five times is not an answer, and it is the one document the project is missing.**
