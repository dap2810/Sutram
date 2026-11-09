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

# ROUND-160 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

## WS1 - and this is the round: the nineteen
**Muse says nineteen claims in the reference are still wrong at v315, and it lists them in ROUND-152 and ROUND-153.**

**Fix all nineteen.** **Not by softening the wording - by making the reference say what the code does, or changing the code to do what the reference says, and saying which you chose for each.**

**Where a claim is about behaviour a student relies on, prefer changing the code.** **A reference that describes a better language than the one you have is a specification, not a lie - but only if someone builds it.**

**And the twentieth: Muse says one is "not locatable verbatim".** **Find it or say it was a misreading.**

## WS2 - and then the gate, which would have caught this
**R158's five checks catch a missing version number.** **They do not catch nineteen false paragraphs.**

**So: what check would have?** **One idea: every claim in the reference that names an E-code, a flag, a function or a limit must be extracted and matched against the source.** **Muse did that by hand and found twenty.**

**Can it be a gate?** **If yes, build it.** **If not, say why - and say what the closest checkable approximation is.**

## WS3 - and the books
**R157: the memory chapter in English and Sanskrit, seven topics, and every example compiled.**

**Is it written?** **If not, say when.**

## WS4 - and your footprint
**Your channel is 17 MB.** **Of that, what is evidence a `RESULTS.md` cites, and what is a snapshot nobody reads?**

**Apply the rule you applied to the Windows folders: keep what is cited, replace the rest with a hash and a line.**

**Report the before and after for your own folder.**
