# R207 — slice provenance, minimum release conditions, and interrupted-install recovery

Reviewed main `5bd58aee7acfe7e7e527fc1ed057211007338bc6` (v306). Product code is unchanged from the R205–206 review; the intervening changes are handoffs, evidence and a report correction. Read-side only. Compilation, native execution, Wine, installer and GUI checks: **NOT RUN — no toolchain used**. Proposed probes below are not reproduced results.

## Correction to the installer record

Accept the R207 correction. The original copy stall and the subsequent ownership refusal are separate events. Claude R132 reconstructs 131 matching v303 payload files, five previous installation-state files and an empty `docs/rounds/PROJECT-OVERVIEW.md` from the recorded snapshot. The original log reached copying; the later refusal occurred before copying. The later refusal does not explain away the original stall.

My R205–206 statement that the latest diagnostic measured an ownership refusal remains narrowly accurate, but must not be read as denying the earlier stall. The reported file-132 reconstruction is Claude's analysis, not a native observation made in this round. The cause of the original block remains unknown. Logging every 100 completed copies cannot identify an in-progress copy; log a start and finish for each file.

## WS1 — a third path, and where the rule belongs

A third path to investigate is **erasing a slice into untyped storage or an untyped function parameter/result**, not another spelling of a function-value call.

Source evidence in `src/sutram_compiler.asm`:
- `r126_check_assign .cell` rejects `r126_is_kosh_value`, which recognizes kinds 2, 3 and 6. A slice is kind 1.
- `r127_check_slice_value` rejects a direct kosh slice in named declarations/assignments, but is not applied by that cell-store branch.
- `r126_check_untyped_arg` similarly rejects kosh values, not kind-1 slices.
- `r23_check_return` recognizes syntactic slices and locally tracked slice variables; an untyped parameter does not retain that classification.

A minimal **unrun** cell-storage candidate is:

```sutram
mukhya() {
    kosh k[1]
    kosh_kship(k, 7)
    vitti obstacle = nirmmita(16)
    mala box[1]
    box[0] = k[0:1]
    kosh_kship(k, 8)
    vitti descriptor = box[0]
    vitti old_data = descriptor[0]
    old_data[0] = 99
    likha(k[0])
}
```

Source prediction: the cell store accepts the slice descriptor, growth moves the elements, and the raw write changes the abandoned buffer, leaving `k[0]` at 7. This deliberately exposes the raw representation: it is evidence of an unchecked **escape boundary**, not a claim that raw-pointer indexing is promised safe. The smallest conservative closure is refusal at `box[0] = k[0:1]`. Also test an untyped identity function `prakriya keep(x) { nivartanam x }` receiving that slice: the parameter/result path can erase its kind without an indirect call. Validate these candidates before claiming observed behavior.

**Creating the slice is where provenance must originate; creation alone is not enough to enforce its lifetime.** A slice valid when created can become invalid during another argument, a later statement, or a nested callee. Moving the existing check to `r23_gen_slice` without retaining context/provenance does not solve that.

Two sound approaches:
1. For the smallest conservative v1 rule, mark kosh-derived slices and allow only checked, nonescaping uses with no invalidating growth across the complete borrow interval. Reject erasure into cells, fields, globals, untyped parameters/results and unresolved calls unless safety is established. Preserve provenance through aliases, subslices and forwarded `vibhag` parameters. Unknown callee effects are not proof of no growth.
2. A larger representation change could retain descriptor identity/offset/extent and validate or pin the borrow dynamically. This needs explicit shrink semantics and is not required merely to release v1.

Enforcement therefore belongs at **creation plus every escape/invalidation boundary**, with one shared policy, rather than a growing list of callee spellings. Rejecting every kosh slice at creation would be safe but removes an existing feature; that is a separate language decision. No need for that blanket removal if the supported safe subset can be enforced.

## WS2 — the smallest checkable YES conditions

The verdict remains NO on unchanged v306. These are five finite acceptance conditions, not a request to fix every possible defect:

1. **Slice closure:** reproduce/refute R206 S3 and the above escape candidates on the pinned compiler; accepted hazardous cases become controlled refusals or correct views. Cover the small stale write and large region release, indirect/untyped/storage routes, and safe direct read/write controls. A named restriction must survive provenance forwarding.
2. **Windows setup and OOM:** check failed exception-handler registration; injected NULL must stop cleanly before lazy memory is used. Preserve the failed-commit, success, invalid-stderr and unrelated-fault controls. Run the native cases against the actual replacement binaries.
3. **Recoverable interrupted installation:** a forcibly interrupted install can be completed on retry; a modified or unrelated user file is preserved. Verify interruption during a file write and around manifest/state publication, for both a fresh install and an upgrade. Each copy logs its start before writing.
4. **Exact candidate acceptance:** build/package once fixes are accepted; verify pins, payload hashes and required project gates. Native Windows must accept that exact package's wizard, repaired-v305 upgrade, clean installation, duplicate-install refusal, PATH, IDE refused-load behavior and uninstall. Prior candidate evidence remains credited but cannot substitute for changed paths.
5. **Truthful release description:** incorporate the exclusions already supplied in R205–206; correct the hang history, recovery behavior, policy behavior and OOM scope. State any remaining Wine observation honestly. No claim of general raw-pointer safety, formal proof, universal OOM recovery or mixed-version object compatibility.

The unexplained historical hang need not force an endless investigation if the replacement candidate has bounded failure, useful diagnostics, successful native copying and demonstrated recovery. Do not claim its root cause was fixed. General ownership tracking of all foreign reservations, GC, threads, generics and broader fuzz infrastructure are not additional release gates here.

## WS3 — complete a known partial transaction; preserve ambiguity

**Recommended default:** recognize an incomplete installation, explain it, and offer to finish it using a verified package. Offer a preservation/recovery option when state is ambiguous. Never label every mismatching product-named file disposable.

Claude's proposed pending manifest is useful but insufficient by itself:
- An intact file matching either the previous or pending payload hash is recognized product content.
- A half-written file matches neither. The proposed two-hash check still cannot classify the empty 132nd file.
- A marker for the whole directory does not prove every file in it belongs to the installer. Someone may add or edit files after the interruption.

### Minimal transaction layout and ordering

Use a private transaction directory **beside the target on the same volume**, e.g. `<parent>/Sutram-install-<transaction-id>/`, bound to the canonical installation path. Store a versioned journal, verified incoming manifest/package identity, previous manifest/state and recovery copies there. Reject reparse/path traversal inconsistencies and serialize installers for this target.

1. Verify the package, target and existing ownership first. Create and durably publish the transaction journal **before deleting, truncating or replacing any target file**. Record transaction ID, canonical target, old/new manifest identities and phase.
2. Stage each incoming file under the transaction directory. Log `START <relative path>` before copying. Copy to a unique temporary file, close/flush it, and verify its full expected hash. Then log completion. Never stream directly into an existing destination.
3. Before publishing each destination, journal whether it was absent or its verified prior hash and recovery location. Preserve prior content before replacement. Publish the verified staged file using an appropriate same-volume replacement operation. Record completion after publication. A crash between publication and its journal update is reconciled using the expected old/new hashes.
4. On restart, inspect actual files against the journal and both manifests. Already-new files can be skipped; unchanged old files can be safely replaced after preservation; incomplete **transaction-owned temporary files** can be recopied. A destination that matches neither hash is ambiguous: preserve it and surface the conflict rather than overwrite it.
5. Verify all final payload files and required integration steps. Publish the final manifest and install state consistently, then mark the transaction committed. Clear the active pending marker only after that commit state is durable. Cleanup is idempotent: a crash during cleanup must not turn a committed installation into a new partial install. Retain the recovery log/backups according to the stated retention choice.

A compact `payload.pending.sha256` in the target can point to this transaction, but it must be written before destructive mutation and removed only after successful commit. It is a journal hint, not blanket permission to replace files. Do not delete the only recovery copy merely because the new payload copied successfully; PATH/registration/finalization may still fail.

### The already-existing unjournaled v303 partial install

A new journal cannot retrospectively establish who wrote an unknown mismatching file. Matching known payload hashes can classify intact files; an empty file alone cannot establish ownership. Preserve the old tree in a named recovery folder before authorized replacement, as the owner's successful repair did. Present the target, recovery location and conflict list. Refusal with only a folder path is not an adequate default user experience; offer a concrete preservation-and-repair route.

The recovery guarantee should be interruption/retry safety and preservation of ambiguous content, not an unsupported promise of a completely atomic transaction across files, registry, shortcuts and PATH. Those steps need separate journal records and idempotent completion/compensation.

### Required recovery evidence

Interrupt during staging, after verified-file publication but before its journal update, and around final manifest/state commit. Retry must complete without user-file loss. Include one deliberately edited installed file and one unrelated user file as preservation controls. Record exact package hashes and filesystem/integration state before and after. Native execution of these scenarios: **NOT RUN — no toolchain used**.

This round supplies design and acceptance criteria only; Claude/Muse retain reproduction and implementation ownership.
