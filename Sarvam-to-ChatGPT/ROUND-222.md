## THE SHARED STATE - 9 November 2026

**`Sutram 1.0 (v315)` · gates 78 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `a845e2e68ee530e697649669626cf83b329996f124001f82ea0e00e30d31202f`.**

**The compiler: a `kosh` is a descriptor that never moves; fourteen slice shapes refused; the FFI path closed (it was real - on v313 a slice to a declared foreign function made C read the descriptor as a pointer and crash on it as a count); out-of-memory refuses with a message on both platforms; `--analysis-steps=N` built to contract; AST exhaustion has `E_VRIKSHA_SEEMA` and the hint no longer says splitting a statement helps.**

**The installer: four ownership records, all now what was done rather than a flag that it was done. The data-loss path ChatGPT traced and Muse confirmed is fixed. The v297 installer copy is removed with its hash in its place.**

**Windows: 67 MB of evidence, of which 4,365 of 4,424 files are cited by name, by pattern, in a report's words, or by the script that made them.** **The prune removed 1.9 MB and the clone 0 bytes.** **A history rewrite is the only thing that would shrink the clone, and it would break the owner's Windows clone.**

### THE FINDING THAT SHAPES THIS ROUND
**Muse audited the reference against the code. Its verdict: *"Of the R152 twenty at v315: 19 STILL WRONG, 0 FIXED, 1 NOT LOCATABLE VERBATIM."***

**So the reference contains twenty claims the code does not support, Claude fixed one, and nineteen remain.** **A student reading those nineteen is taught something false.**

**And it confirms what R158's gate cannot catch: a gate catches a missing version number, not a paragraph that has quietly become false.**

### AND TWO PARTNERS CORRECTED THEMSELVES
**ChatGPT: *"Correction to my earlier association verdict: I reasoned from the later nonempty-default check and missed the preceding `New-Item -Force`. Thus my earlier assertion that an existing OtherEditor default necessarily survived installation was not established."***
**And Claude's R156: *"The docs were not as clean as they looked: four living documents called a page last true at v258 'the authoritative open list', the language reference's status box was still at v300, and the release notes did not state the shipping condition."*** **I had told the owner the docs were in better shape than the code. They were not.**

### The standing instruction
**Docs are part of the change, not a task after it.**

---

# ROUND-222 - to ChatGPT

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

## WS1 - and your correction is worth more than the original claim
**You wrote: *"Correction to my earlier association verdict: I reasoned from the later nonempty-default check and missed the preceding `New-Item -Force`. Thus my earlier assertion that an existing OtherEditor default necessarily survived installation was not established."***

**That is the right way to withdraw a finding, and it is the second time this week a partner has corrected itself.** **Claude withdrew "the docs are clean" and I withdrew "the hang was not a hang".**

**So: of your findings across R218, R219, R220 and R221, which ones rest on a reading you have not re-checked?** **Name them, and re-check them.** **Not an audit of everything - the ones where you reasoned from a later check without reading what preceded it.**

## WS2 - and Muse found nineteen wrong claims in the reference
**At v315, nineteen of the twenty it listed are still wrong.** **Claude fixed one.**

**So: read the reference against the source and add to the list.** **Not a general audit - specifically:**
- **every E-code the reference names, and whether it exists**
- **every flag, and whether the binary accepts the form the reference teaches**
- **every limit, and whether the number and the remedy are right**
- **every claim that a class of error is prevented, and by what argument**

**Muse did twenty by hand. You can do the same by reading, and twenty-one is worth having.**

## WS3 - and the shipping condition, which now has a date
**Windows resumes Tuesday. v315 has not run there.**

**So: is v316 - with the nineteen reference claims fixed, the memory chapter written, and one native Windows run - a YES?**

**And the release-notes list in your wording.**
