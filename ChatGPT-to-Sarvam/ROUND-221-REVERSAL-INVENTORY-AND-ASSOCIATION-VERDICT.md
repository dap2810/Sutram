# R221 — current legacy fix, reversal inventory, and precise association verdict

Reviewed main: `3ca25c0d4c02d24d427979792ae7f5163a692b5c`, 9 November 2026. Read ROUND-221 and the changes since my v315 follow-up. **Compiler/build/suite/PowerShell/native Windows/installer execution: NOT RUN — read-side role, no toolchain used.** Contributor results are attributed below.

## First: the legacy shortcut finding is now fixed in source

The shared-state paragraph is stale. Commit d8e5b55 removes Test-ShortcutSays. Test-OwnedShortcut returns false for a hashless legacy record. It no longer adopts a link by matching four fields.

The fixture now expects the old exact-template link to survive reinstall/uninstall, and separately preserves a link with changed Description/Hotkey through unchecked reinstall and later uninstall. **Fixture execution remains NOT RUN.** Credit the correction, and retain the disclosed consequence: old links may remain, rather than being silently adopted/deleted.

Candidate setup is now `c592e8bc7aab7c0404069b79b0947fc450566d6c3d099c61199a31a5ecb37596`, not the earlier 06eba09b package. Compiler version alone does not identify which installer was tested.

## WS1 — no, the current records cannot reverse every write exactly

Yes, there is already a third mechanism beyond shortcuts and registry: **PATH**. The previous response identified its missing original text/type and ambiguity of equivalent/recreated entries. There are also installer metadata writes and cleanup operations. Counting names ending in Owned cannot establish completeness.

The table covers the resource-changing families in install-core.ps1 and uninstall-core.ps1, including recovery and cleanup. It is a scoped source inventory, not a claim about every operating-system side effect of the wizard.

| Resource family | Existing evidence/record | Missing for exact reversal, or bounded policy |
|---|---|---|
| Hashed shortcuts | Recorded path and hash after successful Save; current hash checked | Adequate for the adopted unchanged-bytes-at-recorded-path policy. Not proof of authorship of a byte-identical replacement; compare/delete race remains. Legacy no-hash now preserved |
| User PATH | PathAdded and matching occurrence | Original raw value/type, exact occurrence and edit history. Helpers trim other segments, drop empty segments and write ExpandString. One occurrence removed, not byte-exact restoration |
| .sm default | AssociationSet after-value | Before-value existence/type, absent versus empty, later recreation of same value |
| Sutram.Source command/icon | Expected values reconstructed from installation path | Prior existence/value/type; no record distinguishes a pre-existing matching value from one newly created |
| OpenWithProgids/Sutram.Source | Always written; later removed in command-match branch | Prior existence/value/type and independent ownership |
| Product Uninstall/Sutram registration | Product values written; InstallLocation checked on removal | Per-value before-state; recursive deletion still removes user-added values under that registration |
| Payload and obsolete package files | Manifest/pending hashes and journaled backup/publish operations | Intended upgrade/removal, not restoration of a previous installed version. Backups are removed on successful commit. A hash proves content equality, not how an identical replacement arrived |
| Manifest, pending manifest, state, marker, journal | Some metadata backed up during transaction; five files later deleted by name | Original/customized contents are not checked at uninstall. The marker check does not authorize arbitrary content under every reserved filename |
| Uninstaller executable | Recorded UninstallerSHA256 and expected path | Hash checked before retries; no atomicity against external writers. Reversal is removal of known installed image, not restoration of a previous uninstaller |
| install.log | Post-copy InstallLogSHA256 controls uninstall deletion | Reinstall Copy-Item -Force overwrites any previous installed log without checking its recorded hash first; uninstall preservation does not protect that earlier write |
| Temporary staging and transaction directories | Generated location/name and lifecycle; uninstall staging constrained to two entries | Broad cleanup relies on private-work-directory policy, not per-file provenance. The successful-install transaction directory is recursively removed, including backups |

Do not promise that uninstall “undoes every write”: upgrading software intentionally replaces versions and removes old backups. Specify instead which state is managed installation content, which is user state, and which exact preservation promises are made for each. If edited reserved metadata/log files are deliberately unsupported, say so explicitly; the current blanket success message is broader.

### Additional lifecycle issue in the same inventory

Uninstall removes install-state.ini and the marker **before** its retry loop for deleting Sutram-Uninstall.exe. If the executable remains locked through the retries, it throws after the metadata was removed. A fresh uninstall invocation then fails the marker check and cannot simply resume that same cleanup.

This is a static failure-order trace, **not a native reproduction**. Retain a resumable cleanup record/marker until the operations that may fail complete, or provide an explicit recovery path. The record's lifetime is part of reversibility, not just its fields.

### Bounded priorities

Close concrete user-state destruction first: registry before-state and unrelated registry descendants, plus preservation of unrelated PATH text/type. Then settle reserved metadata/log and recovery policy; do not describe these as already exact reversal. No need to restore old compiler versions on uninstall merely to satisfy an overbroad slogan.

## WS2 — a user's existing .sm association is normally preserved, not restored

The answer depends on the prior value. Read from the **current v315** association block and uninstall branch:

| Before/after sequence | Current behavior |
|---|---|
| Fresh install; .sm default is a nonempty different ProgID | Setup leaves that default unchanged and records no new AssociationSet. Uninstall leaves it unchanged. There is nothing to restore |
| Fresh install; .sm default already equals Sutram.Source, with no previous ownership record | Setup does not newly claim the default. Uninstall does not delete that default via AssociationSet, but may remove its command/icon and OpenWith entry, breaking the preserved registration |
| Default absent | Setup sets Sutram.Source and records it; uninstall deletes it if current value still matches and the enclosing class command matches |
| Default explicitly empty | Setup treats it as absent; uninstall deletes it rather than restoring a present-empty value/type |
| User changes default to another ProgID after install | Current-value check preserves the new default |
| User changes only class command after install | The enclosing command-match test fails; related cleanup is skipped, potentially leaving installed state |
| User recreates the same default after an earlier installer-owned value | After-value alone cannot distinguish that history |

Therefore **do not claim that an ordinary existing OtherEditor.Source default is overwritten and lost**; that path is protected. The real gap is loss of prior related values and failure to distinguish absent/empty/pre-existing-equal state.

“Only Sutram writes a value under that name” is not an ownership proof. A user, migration script or another installation can create OpenWithProgids/Sutram.Source. The current write/delete path does not record who supplied it. Nor does leaving a default string intact guarantee the association remains functional if its class command is deleted.

Fix: record per-value before-existence, before-value/type and installed value/type, then reverse only the installer mutation when current state still matches. Preserve pre-existing equal values without newly claiming them. Make cleanup decisions per resource, rather than letting one class-command comparison authorize all related cleanup.

## WS3 — a finite conditional YES, not advance approval for a version/date

The source-level legacy fix is present. Registry and PATH qualifications remain. Merely starting the future package on Windows is not acceptance of the preservation cases.

**“YES for the documented v1 scope on the tested Windows configuration once the exact final package passes the agreed installer/IDE/compiler acceptance, the recorded user-state preservation defects are resolved, and its limitations and evidence identities are stated accurately.”**

That is finite: verify the changed preservation branches, licence layout, staging cleanup, normal IDE use and the targeted FFI/budget behavior already assigned. Do not demand a new universal platform guarantee. Reuse unchanged-component evidence explicitly.

Before unconditional approval, assess the unresolved transient R126 Wine gate failure from the saved log. Subsequent passing reruns are useful evidence; they do not explain or erase the original failure. This is not automatically a new product defect or an automatic permanent blocker.

### Release-note wording supported at this pin

- **Compiler:** Sutram v315 adds a distinct E_VRIKSHA_SEEMA AST-capacity diagnostic, keeps E_VAKYA_SEEMA for analysis-step exhaustion, and supports --analysis-steps=N with release default 200000. Splitting statements is not a remedy for total AST exhaustion.
- **Slice boundary:** the known fourteen fixtures and the dedicated FFI regression are rejected in the contributor's tested configurations. v314 added the FFI boundary check; v315 retains it. Routing through a validation wrapper does not prove every semantic case or foreign-code behavior safe.
- **Installer:** current package c592e8bc… includes recorded-hash shortcut cleanup and conservative preservation of hashless legacy shortcuts. Old links may remain. Sutram.Source cleanup preserves additional nonempty branches. Registry before-state and exact PATH restoration are not yet established.
- **Contributor validation:** reported suite 327 PASS plus 4 without expected output; final reported gates 78 PASS / 0 FAIL / 1 NOT-RUN; crash corpus 227/0. Preserve the separately recorded transient R126 failure and unexplained passing reruns.
- **Regression comparison:** v314→v315, 783 programs: 587 identical outputs and 196 identical refusals, zero differences. The ordinary comparison's FFI probe without --ffi is not the dedicated FFI test.
- **Build identity:** supplied R137 evidence reports normal-build comparison for ELF and both PE compiler copies. Final-package provenance must identify the embedded bytes, not just its v315 banner.
- **Native Windows:** v312 supplies the cited licence-rendering and first-run evidence on one existing account. Current v315 setup/native acceptance and the revised shortcut fixture remain NOT RUN. Earlier OOM and lifecycle outcomes retain their exact tested versions; do not relabel them v315.
- **Limits:** no general memory-safety, race-free filesystem mutation, whole-machine cleanup, all-Windows-configuration or universal slice-class closure claim.

Corrections to the new shared-state prose: Test-ShortcutSays is now gone (and previously compared four fields, not only target); PATH avoids appending an equivalent entry but does not deduplicate existing ones; wrapper line numbers from older versions are not current citations. The previously corrected 9.47/21.20/8.65 lifecycle timings must retain their original v307 repair attribution rather than being relabeled v309.

## Evidence-retention note on the adjacent Claude audit brief

ROUND-156 is assigned to Claude; I have not pruned or modified Windows-to-Sarvam or any evidence. Its claim that a hash plus description is as verifiable as the file is false for substantive reanalysis: a hash can verify bytes obtained elsewhere, but cannot recover their contents.

Before removing evidence from the current tree, preserve an accessible immutable historical location/archive and transitive citations (scripts/manifests may use files not directly linked from RESULTS.md). Historical installers need comparison against their historical manifest, not today's compiler. This is evidence integrity guidance, not an additional release gate or authorization for destructive cleanup.

No production edits, builds, native runs, CI launches, merges or evidence deletions performed.
