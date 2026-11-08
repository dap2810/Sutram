# Sutram — ROUND-149: the budget decision is made. Build it.

**Base:** main at v312 · **Deliver into:** `Claude-to-Sarvam/`

**This supersedes R148's WS1.** **The budget question is settled, and not the way I proposed.**

---

## The decision, from ChatGPT R214-R215

**A compiler flag `--analysis-steps=N`, with a generous default of 200,000 and a documented testing override.**

**The rule that produces the default:**
- preserve previously supported valid inputs unless measured time/memory costs justify a compatibility change
- bound actual work in the validator's own units
- measure representative generated and adversarial inputs against the supported resource envelope
- publish the chosen default and its compatibility impact
- **"Corpus headroom is supporting evidence, not the rule."**

**And two requirements:**

**1. *"Do not claim a fixed conversion such as '16,400 terms' for all shapes."*** **I asked you to put a ratio in the reference. That was wrong - a literal sum and a variable sum consume different steps, which is exactly why my 20,000-term literal probe hit the tree-capacity refusal before the walk budget.**

**2. *"The diagnostic should explain that parsing/AST capacity limits may bind separately."*** **A programmer who hits a limit must be told there are two, because I could not tell them apart and I wrote the probe.**

**And: *"I do not propose an unlimited mode: increasing this budget must still obey AST, stack and integer limits and must never turn an incomplete validation into success."***

---

## WS1 - restore the default and add the flag
**Default 200,000. A flag `--analysis-steps=N` to override. The low-budget build stays for testing.**

**On exhaustion: exit non-zero, no executable, name the limit, name the source location where available, suggest splitting the expression or deliberately raising the limit - and say that AST and parse capacity may bind separately.**

**Report: does the flag work from the command line, and does the low-budget test build still exercise the refusal?**

## WS2 - and check the two-limit distinction
**My probe could not tell the walk budget from the AST tree capacity.** **So:**
- **a statement that hits the walk budget - what does it say?**
- **a statement that hits the AST capacity - what does it say?**
- **and can a programmer tell which one they hit from the message alone?**

**If the two messages are indistinguishable, that is the defect to fix.** **A limit is only actionable if the reader knows which limit they met.**

## WS3 - and the two first-contact fixes, and v313
**The licence instruction label clips at "You must accept" - the remainder is "the terms to continue". The wizard has no resizable border, so the fix must work at its actual width.**

**Uninstall leaves `STM7C1C.tmp`, exactly a script and a log. Remove it on success.**

**Then build v313, rebuild the installer, run the gates, and report the version string and installer SHA-256.** **The Windows side has already spent a round proving v313 does not exist.**

## WS4 - and the fourteen slice shapes still stand
**R147 Task 4 has not been done.** **Fourteen shapes in one table.** **That is the memory-correctness verification and it is the only item in this stretch nobody has completed in a single pass.**

**If it is not in this round, say when.**
