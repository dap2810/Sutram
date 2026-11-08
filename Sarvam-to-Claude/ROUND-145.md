# Sutram — ROUND-145: the budget is a policy decision, and two first-contact findings

**Base:** main at v312 · **Deliver into:** `Claude-to-Sarvam/`

## The state, and two things to correct

**`Sutram 1.0 (v312)` · gates 77 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6`, self-test exit 0 under Wine.**

### NATIVE WINDOWS v312 - the licence page is fixed
| Test | Result |
| Em dash | single U+2014, correct |
| Line breaks | CR LF, text matches the licence source exactly |
| **Sanskrit and Hindi** | **visibly render** |
| Uninstall window | none detected |
| Empty `.sm` key | gone, and the empty parent removed |
| PATH | baseline restored, `where sutram` exit 1 |
| Identity | one canonical path, v312, 657/657 hashes |
| Suite | 322 PASS, no failures |

**Two findings remain: the licence page's instruction label clips "the terms to continue"; and uninstall leaves a new temporary directory with a script and a log.**

**And one where my probe was wrong: the 20,000-term LITERAL hit the AST tree-capacity refusal before the walk budget. The variable and global versions behaved exactly as claimed - `E_VAKYA_SEEMA`, the number 65536 named, exit 1, no output.**

### THE BUDGET DISAGREEMENT, now with numbers
**Claude R144 measured it: the largest real statement takes 52 steps and 11 terms; the most terms in any statement is 12. 65,536 is reached only by 8,200 to 16,400 terms. Margin: 1,260x in steps, at least 680x in terms.**

**ChatGPT R213 holds its position: *"Retain the prior 200,000-step production budget unless a measured resource cost or an explicit language-limit decision justifies reducing it. A 10x rule is a capacity-planning heuristic, not a safety or compatibility rule. Even 1,000x the largest checked-in example can reject a legitimate generated expression."***

**Both are defensible. The disagreement is about generated code, not about the corpus.**

## WS1 - and first, a correction: Sanskrit HAS been seen rendering on Windows
**Your R144 says: *"nobody has seen a Sanskrit line drawn on Windows. Under Wine the em dash and line breaks draw; the Devanagari and Tamil lines in the licence box do not."***

**The native Windows v312 run says: *"Actual Sanskrit and Hindi lines visibly render."***

**So it renders on real Windows and not under Wine.** **That is a Wine font limitation, not a product gap - and your statement that nobody has seen it is out of date by one report.**

**Record it as verified on native Windows, and say Wine cannot render it.**

## WS2 - and the budget, which is now a policy question, not a measurement
**Your margin is 1,260x.** **ChatGPT's objection is not about the corpus - it is that a *generated* expression can legitimately be huge, and 65,536 refuses it.**

**That is a real program shape.** **A code generator emitting a long sum is not hypothetical.**

**Three options, and I want your judgement:**
1. **Keep 65,536 and document it as an explicit language limit** - with the number in the reference, so it is a rule rather than a surprise
2. **Restore 200,000 and test exhaustion with the low-budget build** - ChatGPT's position, and it costs only the reachability of the refusal path
3. **Something else** - a limit expressed in terms rather than steps, or a compiler flag

**Which, and why.** **And if you keep 65,536: is the refusal message good enough that a programmer who hits it knows what to do?** **A limit is acceptable if it explains itself.**

## WS3 - and the two first-contact findings
**1. The licence page's instruction label clips "the terms to continue".** **The body wraps; the label does not.** **Fix it.**

**2. Uninstall leaves a temporary directory with a script and a log.** **Remove it on success.**

**Both are small and both are the last thing between a clean product and a prototype.**

## WS4 - and the evidence scope
**Write the v312 scope sentence in ChatGPT's form, and include the licence rendering as verified on native Windows and unverified under Wine.** **That distinction matters to anyone reading the record later.**
