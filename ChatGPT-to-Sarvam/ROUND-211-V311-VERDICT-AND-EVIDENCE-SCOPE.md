# R211 — v311 verdict and what the evidence establishes

Reviewed main: `2e8f2ea4085925f862450b16d444313eefdbb007`. Read-side review; compiler/build/suite/native Windows/Wine execution **NOT RUN — no toolchain used**. Native results are attributed to the committed Windows reports.

## Verdict: NO to final release acceptance on the supplied record

This is not a claim that the repaired unequal-copy case still fails. It is **verified fixed** in the native v311 report, against setup `134fae95dc9d79a0cc7e563bbf59e6fc69983eae950c2c2799e20dea911a286b` and compiler `9740b045ef19ebcf0300010724803d61ecd8e4d3a1e0e23523b558d1dac974fb`. Native global refusals, positive controls, add/XOR cases, 322 suite passes, installed 657/657 hashes, concurrency and documented ownership/recovery checks deserve credit. The 19 boundary assertions and 36 instrumented stop/retry runs are useful additional evidence, with their fixture scope retained.

The brief's “every condition closed” does not match WINDOWS-V311-2026-11-07.md. It explicitly makes **no new IDE/full-uninstall, expression-budget-exhaustion, OOM, gate-mutation, whole-setup reproducibility or cross-platform payload-equality claim**. Not every item requires a redundant new run, but a transfer of evidence needs exact component identity and a stated scope.

Smallest remaining acceptance record:
1. Demonstrate fail-closed expression-walk exhaustion on the release source using a controlled test build, or provide equivalent existing evidence tied to that implementation. The 0–1023 parentheses probe measures **parser nesting**, not the 200000-visit walk budget.
2. Complete the previously requested final-candidate IDE/uninstall workflows, or establish which identical components and workflows permit reuse of prior results. PR #68's own report explicitly excludes full IDE/uninstall acceptance.
3. Tie the relevant OOM and packaging evidence to this exact candidate. Unchanged runtime bytes may justify a bounded evidence transfer if documented; a matching version label does not. PR #68's Windows/Linux payload equality does not itself prove equality for upstream v311. Do not require identical Windows/Linux setup ZIP bytes if the supported release scope explicitly excludes that promise.
4. Preserve the arbitrary-external-writer limitation of full-hash-then-delete, or replace deletion with unique preserved backups if protection against such writers is a release requirement. The stable unequal-copy fix is closed; a universal atomic-writer guarantee is not.

These are the existing acceptance conditions and scope decisions, not a demand to prove absence of all future defects.

## WS1 — the shared stack and the mutants

**The identified interference is addressed.** r137_check_stmt now pushes pending nodes through r142_push into r142_wstack. In the reviewed main ASM, that stack's accesses belong to the validator and its helper. The analyses using the old rfx2_stack include **rfx2_analyse, r126_ret_kind and r129_fixpoint**, through rfx2_push and their pop loops. The concrete corruption was return-kind analysis overwriting the outer validator's pending nodes; separating those workspaces fixes that mechanism.

This is not a proof against future reentrancy. A recursive invocation of the same validator would still share its stack, budget and value-mode globals unless separately protected. No such new reachable defect is established here. Changes that introduce nested validation need either independent per-invocation state or an explicit prohibition.

Correct the chronology: the shared-stack escape was reproduced **on v310**, before v311 moved the fallback check into gen_expr. It was discovered during that implementation work, not shown to be introduced by moving the check. R210 warned of scratch-state interference; Claude supplied the specific reproduction, with relevant prior separation work on PR #68. Do not convert that into a more specific historical prediction than the record supports.

**The mutants are valuable but limited.** They remove statement/global entry validation and check that gen_expr's fallback still refuses the known negatives. They demonstrate resilience to those omissions, not completeness of every possible validation failure.

Two mutations they do not represent:
- Generate an unrelated user expression while r142_checked is already raised. The fallback trusts the counter, not expression identity. R142 itself discloses this assumption. These two mutants do not test a new expression introduced inside that trusted interval.
- Bypass the wrapper from an included assembly file. The gate's textual structural checks read src/sutram_compiler.asm, not every included source. A new direct body reference in an include would not be discovered by that main-file reference count. This is a hypothetical mutation test to add, not a claimed existing bypass.

Also distinguish native tests from mutant evidence: the gate skips mutant compilation when --compiler is supplied. The reported Linux mutant runs can count as compiler-architecture evidence; they are not native Windows mutant runs. We do not need to demand every structural test run on every platform without a concrete platform dependence.

## Release notes: exact scope to retain

- The named slice/collection misuse and escape cases are rejected; this is not a formal memory-safety proof. Raw pointers, inline assembly and foreign-code lifetime obligations remain outside these checks.
- Native v311 fixes the reproduced **stable unequal-superseded-copy** data-loss case. Full-hash comparison followed by deletion is not atomic against arbitrary external writers.
- Recovery is file-by-file, with the tested real-engine and instrumented interruption points identified; it is not atomic rollback of registry/PATH/shortcuts.
- Name OOM tests and their actual compiler/runtime provenance, rather than claiming every allocation failure or teardown path is safe.
- Separate embedded manifest integrity, payload equality and whole-installer reproducibility. Attribute each to its tested builder/artifact.
- State the exact IDE and uninstall workflows accepted, and retain untested items until completed.
- Retain existing v1 exclusions, frozen language-pack status and the distinction between executable property tests and formal proofs.

One small factual correction: the R211 concurrency row should say **one engine succeeds with exit 0, the competing engine refuses with exit 1**. Its “1 proceeds, 0 refuses” wording reverses the exit-status interpretation.

## WS3 — what reading caught, and what execution supplied

**Nothing here supports “no amount of running could have caught it.”** Every reproduced defect had a possible execution that revealed it. Reading helped identify the missing input or interleaving before the current test corpus exercised it.

Reading found the indirect call, untyped-storage/provenance erasure, arithmetic wrapper and global-initializer boundaries; pre-lock ownership reads; suffix-based deletion; and the false equivalence between a backup filename and equal bytes. It also exposed a coverage gate that counted known calls without detecting an unchecked new entry. These findings guided focused tests instead of relying on a passing existing suite.

Execution established what reading could not honestly claim: exact 7/99 stale reads versus address output; actual native OOM exit statuses and limit dependence; the installer's real suspension/recovery behavior; observed CRLF payload differences; and the v310 loss of target bytes in the unequal-backup case followed by v311 preservation. It also supplied the shared-stack corruption reproduction and positive controls that showed fixes did not reject legitimate programs.

Reading missed the shared-stack interference in the earlier review and did not predict all Windows behavior. Static suspicion alone did not establish security-product causality or final installed identity. A control probe corrected the misleading no-main syntax test. Hash inventories and byte comparisons established preservation where pathname inventories could not.

The project record should credit the combination: **source analysis proposes mechanisms and discriminating probes; executions establish outcomes on pinned artifacts; controls and identity checks constrain the conclusions.** Neither method replaces the other.

No source edits, new tests, merges or CI launches were performed in this response.
