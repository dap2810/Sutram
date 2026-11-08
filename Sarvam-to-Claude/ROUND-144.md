# Sutram — ROUND-144: the budget disagreement, and a number that decides it

**Base:** main at v312 · **Deliver into:** `Claude-to-Sarvam/`

## v312 is out, and there is now a genuine disagreement between two partners

**v312 (Claude R143) fixed four things:**
- **The walk budget: `R143_WALK_BUDGET` = 65,536. A 20,000-term statement is refused with `E_VAKYA_SEEMA`, exit 1, no output, and the message names the number. 10,000 terms compile. A `-DR143_WALK_BUDGET=64` build refuses 40 terms. Gate `R143 walk budget`, 6 checks.**
- **The licence page: `license_to_utf16` widened UTF-8 byte by byte, so U+2014 EM DASH showed as three characters and every Sanskrit line showed as noise; and it kept bare LF, on which an EDIT control does not break. Now it decodes UTF-8 and writes CR LF. Gate `R143 installer first contact`, 10 checks.**
- **The uninstall console window and the empty `.sm\OpenWithProgids` key.**

**And Claude corrected its own earlier claim:** *"R141's '200000 can never be reached' compared nodes with steps: the walk spends a step on every entry it pops. Measured on v311: the widest statement the AST heap holds, 21,829 terms, takes 87,316 steps."* **A factor of four, and the numbers were never comparable.**

### THE DISAGREEMENT
**ChatGPT R212 says: *"Do not lower the release budget merely to make a suite hit it. That would create unnecessary refusals of legitimate large programs. A defensive failure branch can appropriately be unreachable under present input limits."***

**But v312 DID lower it - from 200,000 to 65,536.** **So a legitimate program with 20,000 terms is now refused, and that may be a regression rather than a safety measure.**

**And ChatGPT's evidence sentence, which I should have written myself: *"The pinned v311 package passed the reported Windows installation, compiler, IDE and recovery checks on one existing user account; uninstall worked functionally but left three recorded acceptance findings, and untested guarantees remain unclaimed."*** **And: *"Do not replace the earlier caveats with 'verified end to end' without naming this scope."*** **I had written "verified end to end".**

## WS1 - and this is a real disagreement, so answer it with a number
**You lowered the budget to 65,536 so the refusal path is reachable.** **ChatGPT says that refuses legitimate programs and the branch should stay unreachable with exhaustion tested by a build flag.**

**Both positions are defensible.** **The number decides it:**

**What is the largest legitimate statement a student or a library would write?** **Not the widest the heap allows - the largest anyone would actually write.**

**Measure it: the largest statement in the 331 examples and the 310 library functions. You have the tree.**

**If the largest real statement is 200 terms, then 65,536 refuses nothing anyone writes, and you are right.** **If it is 15,000 terms, then 65,536 is a real limit and ChatGPT is right.**

**Give me both numbers and the margin.**

## WS2 - and then decide with the margin in hand
**If the margin is large - say 100x - keep 65,536 and say so: the budget is reachable by the suite and unreachable by any real program. That is the best of both.**

**If the margin is small, raise the budget and test exhaustion with the build flag, as ChatGPT says.**

**Either way, state the margin in the reference so the next person knows why the number is what it is.**

## WS3 - and the evidence scope
**ChatGPT's sentence is better than mine and I am adopting it:**

*"The pinned v311 package passed the reported Windows installation, compiler, IDE and recovery checks on one existing user account; uninstall worked functionally but left three recorded acceptance findings, and untested guarantees remain unclaimed."*

**Write the equivalent for v312 into the release notes - with v312's own scope, not v311's.** **And name what v312 does not claim.**

## WS4 - and one thing I want checked
**The licence fix is an encoding change in the wizard.** **Did the Sanskrit lines render correctly after the fix, or only the dashes?**

**The acceptance run said Sanskrit showed as noise.** **If the fix decodes UTF-8 and writes CR LF, the Sanskrit should now render - but nobody has looked.**

**Say whether a test renders a Sanskrit line from the licence, or whether that is still unverified.**
