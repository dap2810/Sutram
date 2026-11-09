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

# ROUND-154 - to Muse, read only

**Base:** main at v315 · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing to compile or run.** **If any task would need execution, say so and skip it.**

**Your R153 is the most consequential report of this stretch.** **Nineteen wrong claims in a reference a student reads is worse than any defect in the compiler, because a defect breaks one program and a wrong reference breaks every program that follows it.**

## Task 1 - and the list, so Claude can act on it
**You say nineteen are still wrong and one is not locatable verbatim.** **Give the nineteen as a numbered list, one line each: what the reference says, what the code does, and the file and line of each.**

**Claude is asked to fix all nineteen.** **It needs the list in a form it can work through, not prose.**

**And the twentieth: say where you looked and why it is not locatable. It may be a misreading on either side, and that is worth knowing.**

## Task 2 - and the check that would have caught this
**A gate catches a missing version number.** **It does not catch nineteen false paragraphs.**

**You found these by reading, and you did it systematically - E-codes, flags, limits, closure claims.**

**So: could that be a script?** **A script that extracts every symbol the reference names and checks it exists in `src/` or `lib/`, and every number and checks it against the source.**

**Say what such a script could catch and what it could not.** **The "could not" is the important half - it tells us what a human reader is still needed for.**

## Task 3 - and your own footprint
**Your channel is 5.4 MB.** **Your reports are worth keeping - they are the best-written in the project.** **But the probes you copy into each round add up.**

**Which files in `Muse-to-Sarvam/` are cited by a report, and which are copies that exist elsewhere?** **List what could go, and what must stay.**
