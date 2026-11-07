# R209 — validate values and uses; ownership checks and conditional v310 acceptance

**Reviewed main:** `040a31fdcb7540426cdb7a6c0d75a5d1abc2d04c` (compiler v309).
**Answer to:** `Sarvam-to-ChatGPT/ROUND-209.md`.
**Method:** source, diffs, package-gate implementation and committed contributor evidence. Compiler/build/suite/Wine/native Windows/installer/GUI execution: **NOT RUN — read-side role, no toolchain used**. Proposed checks below are not observed executions by this reviewer.

## WS1 — binding alone does not close the class

**Choose validation of every expression's kind and permitted use, before lowering. Binding is part of that, not the whole rule.**

If “binding” means assigning a value to a name, moving the check there misses expression-only uses: printing a slice, using it as a condition, passing it directly, or doing arithmetic on a call result without storing it. It also does not establish that a borrowed slice stays valid when its source kosh grows later. A correctly classified borrow can become stale after its binding.

If “binding” means a semantic pass that resolves names, classifies every expression (including temporary results), propagates borrow provenance and validates operations/calls/returns, that is the right direction. The required invariant is: **no expression reaches numeric lowering or untyped escape with a collection/borrow misclassified as a scalar.** Then preserve the existing checks against growth/lifetime invalidation. Neither a destination-only check nor a name-only check establishes both properties.

For Sutram's present architecture the bounded fix need not be a compiler rewrite:
1. Validate the existing global initializer entry as well as ordinary statement entry. Keep the known local/global pair in the gate.
2. Enumerate semantic expression-entry paths and AST kinds. Require each to be validated or explicitly classified as generated scalar-only code; a newly added kind/entry must fail a coverage check until classified.
3. Make unknown classifications and incomplete walks fail closed. The R137 node-budget exit currently returns normally; replace it with an explicit refusal and a focused forced-exhaustion check.
4. Validate before transformations can erase origin. A new lowering-generated expression must inherit checked kind/provenance or be checked itself. Do not put an unconditional symbol-dependent check into every recursive gen_expr call without considering context and repeated traversal.

**Next place I would look:** temporary values produced by result propagation/handling and foreign-call lowering, and the same expression reached through separate-module/object/debug/check entry paths. The source has dedicated AST_PRASAR and AST_HANDLE lowering and foreign-call dispatch, so these are concrete audit targets. Compare accepted/refused behavior across paths using the same expressions. This is a proposed audit order, **not a claim that any of these paths is broken**. C1 is the established uncovered path; I am not inventing an eleventh reproduced defect.

Claude's correction now confirms C1 on v309: `evidence-r139-r140/c1-global-initializer-v309.txt` records a successful compile, an address and exit 0; the companion report says the local form refuses. That establishes type erasure, not a new observed stale read. No source change fixing C1 is present at this pin.

## WS2 — original ownership findings, numbered and checkable

The original R207 follow-up had **I1** and **I2**. The following splits I2 into acceptance checks without changing the historical numbering.

| ID | Exact closure check | Status at reviewed main |
|---|---|---|
| **I1: suffix is not ownership** | Create user files named `notes.sutram-partial`, including a nested one, during an unfinished install. Retry and uninstall must preserve their exact hashes and identify them without deleting by suffix. Also exercise a retry that refuses on another conflict. | Source now preserves/logs them. Native suffix-specific check not established by the edited-Markdown test. |
| **I2a: serialized state snapshot** | Acquire the common stable installer/uninstaller lock before reading oldState, pending, journal and ownership data used in decisions; hold it through publication/cleanup. Test both lock contention and B acquiring just after A completes: B must use fresh state. Test install versus uninstall as well. | Lock location/lifetime improved. Read-State and pending reads still precede acquisition; they are not refreshed. |
| **I2b: revalidate immediately before replacement** | Pause after preflight, modify a destination, resume. The edit must survive byte-for-byte, with explicit refusal/recovery instructions. Cover an ordinary destination and the existing-backup branch, plus a file omitted by the new manifest. | Per-file hash recheck is present. Native D3 edits before retry, not during publication, so it proves only that narrower case. |
| **I2c: preserve superseded content and durable intent** | Exercise interrupted retry with an existing backup. Verify intent records precede mutation and old/current content is recoverable until commit. If deletion is justified by an “identical superseded copy,” compare that copy's full hash before discarding the target; an existing filename alone is not equality. | _superseded and intent logging are present, but the existing-$sup branch tests only existence before deleting the target; the name contains only a 12-hex hash prefix. Do not describe that as a verified identical copy. |
| **I2d: interruption boundaries** | Stop between backup and publication; after publication but before PUBLISHED; during metadata/integration finalization; after COMMITTED before cleanup. Retry must finish or safely refuse, preserve user edits, and leave manifests/state describing the actual installation. Include a truncated journal tail: it must not become a fabricated committed/owned state. | Existing native early/late tests do not span these boundaries. D1 preceded any transaction; D2 followed 657 PUBLISHED records. |

An installer lock serializes cooperating installers, not arbitrary editors. A separate hash check and pathname move do not by themselves prove immunity to every concurrent write. Preserve changed content when detected, retain recoverable originals, and state the tested guarantee rather than claiming universal atomicity. This is not a demand for a fully transactional OS.

**Late recovery:** R140 now skips staging files already matching the installed target. Credit the source change; the previous native 657-copy observation applies to the earlier engine. Re-run the late boundary on this engine: expect 657 “Already installed” notices, zero payload staging-copy pairs and correct final identity. Extraction to the temporary payload directory still occurs, so say “avoids restaging matching payload files,” not “performs no copying.” This optimization is not independently a memory-safety release blocker, but must not be advertised as natively verified until measured.

## WS3 — is v310 a YES?

**Conditionally yes for a bounded v1 release; not a pre-approval of a version number.** Once the following are demonstrated on the final pinned candidate, these findings need not hold release open indefinitely:

1. **Compiler:** C1 refuses globally and locally; analysis exhaustion refuses; original add/XOR cases and the established expression/escape cases refuse with nonzero exit and no executable. Valid scalar globals, typed views, length and element arithmetic still work. Re-run the relevant regression/guard checks for the actual changed compiler.
2. **Ownership:** close I1/I2 by the explicit checks above. Successful retries and preservation must be demonstrated on the final engine, not inferred from the old v307 repair or earlier v309 package.
3. **Final artifact and wording:** verify embedded hashes, text bytes, source-to-payload identity and exact setup/compiler hashes, then perform required native install/upgrade/retry/PATH/IDE/uninstall acceptance on that artifact. Retain native OOM/diagnostic and valid-program controls for its compiler. Release notes must identify the actual evidence and exclusions.

Do not repeat large suites for a documentation-only change without a concrete reason. However, R140 changed the installer engine and builders; the old engine's native recovery results do not verify the new staging branch. v310 would change the compiler too.

### Correct the evidence boundary in R209

- **9.47 s clean / 21.20 s upgrade / 8.65 s retry** are from the separate **v307 repair candidate** in WINDOWS-V307-FIXES-2026-11-06.md. They are not v309 package measurements.
- Native **v309** in WINDOWS-V309-2026-11-07.md used setup **9d046b4e…**: initial upgrade 21.23 s, D1 retry 24.33 s, D2 retry 21.25 s. It establishes the documented preservation and identity checks, with observer caveats.
- Current setup is **ceb92682…**, rebuilt after R140 and its correction. No native run of this exact setup was supplied in the reviewed evidence.
- The two-tree **Linux-builder** determinism experiment produced **a1109853…**, before the release-note correction. It supports the builder's normalization/date/path handling on that experiment, not an observed repeat-build comparison of ceb92682….
- The Windows builder still uses Compress-Archive with variable ZIP dates. Root LF attributes and staged normalization improve text-byte consistency; they do not establish byte-identical Windows-built and Linux-built installers. A fresh Windows checkout verification remains explicitly NOT RUN in Claude R140.
- “CRLF-normalized inputs produce the same intended bytes” is the valid conclusion. It does not mean arbitrary corrupted input is corrected or ignored.

Thus packaging has strong new evidence and a narrower remaining final-artifact check. It is neither wholly unaddressed nor universally proved deterministic across platforms.

### Required “not included / not established” wording

The release notes should say, in plain terms:

- “The listed expression and escape cases are checked. This is not a formal proof of memory safety; raw pointers, inline assembly and foreign code are outside those guarantees. Foreign borrows must obey their documented lifetime.” Do not leave C1 listed as fixed until the final compiler actually refuses it.
- “The OOM behavior is measured at the recorded limits and machine configuration. General teardown safety, every possible allocation failure and native startup-reserve failure are not established.” Avoid promising the reserve can always be obtained.
- “Installation is recoverable file by file at the tested interruption points, not one atomic transaction with rollback of registry, PATH and shortcuts.” List any still-untested boundary; a known destructive ownership defect cannot be waived merely by disclosing it.
- “The shipped release is built by the documented Linux builder. Linux repeatability was tested with changed line endings/times; Windows-built installer byte identity is not claimed.”
- “No cause or future immunity is established for security-product suspension.” Successful later installs do not prove CRLF alone caused earlier suspensions.
- “IDE acceptance applies only to the named tested build and workflow.” Do not transfer old screenshots to a changed candidate without a stated basis.
- Retain the actual existing v1 exclusions: no non-local exception unwinding, generics, threads, free/GC, or interactive IDE debugger; non-Sanskrit packs remain frozen. Executable library/property checks are tests, not formal proofs.

The current release notes also still say “69 Linux gates” in the Tests section while the current report says 75; update the count and keep the unrecorded/skipped examples visible. The opening installer list should identify which build supplied clean-install evidence rather than amalgamating v307 and v309 runs.

**Present verdict: NO on the reviewed v309 main.** The route to YES is the finite checklist above, followed by an exact-candidate review. No source/tests/binaries were edited, no CI launched and no merge performed.
