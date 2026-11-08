# Sutram — R213: you and Claude disagree on the budget. Here is the number.

**Base:** main at v312 · **Deliver into:** `ChatGPT-to-Sarvam/`

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

## WS1 - and the disagreement is resolvable with one measurement
**You say: *"Do not lower the release budget merely to make a suite hit it. That would create unnecessary refusals of legitimate large programs."***

**Claude lowered it from 200,000 to 65,536.**

**So the question is not principle, it is size: what is the largest statement a real program contains?**

**Claude is asked to measure the largest statement in the 331 examples and 310 library functions.** **If the largest real statement is 200 terms, 65,536 refuses nothing anyone writes. If it is 15,000, your objection stands.**

**Is there a rule of thumb you would use instead of a measurement?** **Something like "the budget should be at least 10x the largest observed, or it is a limit rather than a guard."**

**That rule would be useful beyond this project.**

## WS2 - and your evidence sentence, which I have adopted
**I have taken your wording for the release notes and I am asking Claude to write the v312 equivalent.**

**So: what does v312's evidence establish, and what does it not?** **Not the sentence - the list of what is untested, so the notes can name it.**

**Specifically: has anything verified the licence page renders Sanskrit correctly after the encoding fix?** **The acceptance run said every Sanskrit line showed as noise; the fix addresses the cause, but nobody has looked at the result.**

## WS3 - and the verdict, which now has one open question
**Your R211 NO had two reasons: the walk budget evidence, and the IDE/uninstall workflow.**

**Both are now addressed - the budget is measured at two scales, and the workflow ran with three findings that v312 fixes.**

**So: is v313 a YES once Windows runs v312's installer fixes?**

**And if the licence Sanskrit rendering is still unverified, does that alone block a release?** **It is the first thing a user sees.**
