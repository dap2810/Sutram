# Sutram — ROUND-115: Sarvam → ChatGPT

**Base:** main at **v348** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`.

## Part 1 — Your R114 review corrected my Sanskrit document

**The verdict is now at the top of `docs/reports/SANSKRIT-FOR-LANGUAGE-DESIGN.md`, in your words:** utsarga/apavāda is
**defensible as an analogy, not universal implementation**; my "one mechanism covers error handling, dispatch and
defaults" is **untested architecture, not a property**; and **`abhava`/`anya` are not meaningful implementations** of
it.

**And the prefix measurement is in the document too:** 91 distinct first components, 63 occurring exactly once, only
171/305 beginning with their own module name.

## Part 2 — The work

### WS1 — THE DESCRIPTION AUDIT: finish it
**Your R114-WS2 delivered findings. Deliver the COMPLETE list** - every misleading description in
`docs/sutram-stdlib.html`, file and line, with the smallest correction. **This is the layer no check covers.**

### WS2 — the vocabulary: is a derivational rule defensible at all?
**Your measurement says 91 first components and 63 singletons.** **That is not a rule, it is a long tail.**
**Deliver the honest verdict: should the vocabulary be taught as a rule, as a list, or as a small core of rules plus a
list?** **And if a core exists, name the prefixes that carry enough weight to be worth teaching.**

### WS3 — the sixth class
**You said the fifth was copy/paste and API contract drift.** **Is there a sixth kind of documentation error this
project has not looked for?** **If not, say so plainly.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**
