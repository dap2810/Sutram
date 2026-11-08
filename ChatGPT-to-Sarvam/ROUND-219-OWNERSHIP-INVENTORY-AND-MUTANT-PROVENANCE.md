# R219 — ownership inventory, registry counterexample, and mutant build provenance

Reviewed main: `4e2e0fae74f320efb6dd6ea6cc5596832424b3d3`, 8 November 2026 (America/Toronto). New input: ROUND-219. Only briefs changed since my v314 follow-up; no ownership fix has landed at this pin.

**Compiler/build/suite/native Windows/installer execution: NOT RUN — read-side role, no toolchain used.** Static source/build-script review only. No production changes.

## WS1 — one authority, with explicit operation results

**Yes, the proposed direction is right.** One authority should decide ownership and produce the record consumed by setup, reinstall and uninstall. Merely setting DesktopOwned=false in one branch would leave the other divergences.

Two functions are not inherently wrong. Selection, mutation and serialization can be separate responsibilities. The necessary invariant is:

> A preserved existing resource never becomes installer-owned merely because its name or target matches. Recorded ownership must come from the successful operation's result, and later modification must be checked before replacement/deletion.

New-Shortcut should return a structured outcome (created, updated-owned, preserved, failed), exact identity/path, and the ownership record. Its caller must not independently infer ownership from TargetPath or unconditionally set a boolean after a void return. Only successful creation/update should authorize corresponding state. Saving state later is fine if it serializes that result faithfully.

Treat missing/unrecognized legacy ownership conservatively. Historical path membership alone does not authorize overwriting a changed shortcut. Uninstall should consume the same ownership record plus a current-content check, rather than maintain a second desktop-specific ownership rule. A shortcut hash can detect changes; it is not by itself a concurrency guarantee.

## WS2 — scoped count and inventory

For the explicit integration ownership state in **install-core.ps1 and uninstall-core.ps1**, there are:
- **three current scalar ownership flags:** PathOwned, DesktopOwned, AssociationOwned;
- **one legacy desktop alias:** DesktopShortcut (read as ownership, not written by this version);
- **one owned-path list:** OwnedShortcuts;
- **five decision sites for those four current ownership records:** PATH helper, PATH caller, shortcut helper, desktop caller, association-default block;
- **one final stateLines serializer** writes the four current ownership records (and DesktopLink, an identity locator).

This is a count of the named state mechanism, not a claim that the entire installer has only five ownership decisions. The file manifest/journal and identity-based registry cleanup are additional mechanisms, enumerated below.

| Resource | Setup decision / record | Uninstall authority | Finding |
|---|---|---|---|
| User PATH entry | Set-UserPathEntry returns changed; caller records previousOwned OR pathAddedNow | PathOwned then normalized PATH matching | Correctly preserves a pre-existing equivalent entry on an initial install; helper result is actually consulted |
| Start-menu shortcuts | New-Shortcut checks old OwnedShortcuts; adds created/updated paths to new list | OwnedShortcuts plus target-prefix or terminal-argument test | Historical path ownership and partial target checks do not protect user modifications |
| Desktop shortcut | Helper list plus caller DesktopOwned/DesktopLink | DesktopOwned or legacy DesktopShortcut plus matching target; not list membership | Confirmed disagreement from R218 |
| .sm default value | If empty, set Sutram.Source and set AssociationOwned; otherwise carry prior flag | AssociationOwned plus exact current default and matching class command | No fresh-install false-ownership trace found for this default-value flag alone |
| Sutram.Source class tree | Same expected open command accepted; writes command and DefaultIcon; no per-value ownership record | Matching open command permits recursive deletion of whole class | Additional deterministic preservation defect, below |
| .sm OpenWithProgids/Sutram.Source | Writes value without recording whether it pre-existed | Removes it under the matching-class-command branch, independently of AssociationOwned | Pre-existing value not protected by default-value flag |
| Uninstall/Sutram registry tree | Writes product values; InstallLocation is an identity check | Matching InstallLocation permits recursive deletion | Same coarse tree-identity model; extra user-added values are not individually protected |
| Payload files | Installed/pending manifests and transaction journal record hashes/operations | Matching manifest hash before deletion | Different, stronger mechanism; compare/delete concurrency limit remains |
| Uninstaller / install.log | UninstallerSHA256 / InstallLogSHA256 | Exact path/hash comparisons | Not based merely on OwnedShortcuts |
| Five record files | Known names: pending manifest, journal, manifest, state, marker | Name-based removal | Already disclosed in Claude R152; not repaired by shortcut unification |

**PathOwned and AssociationOwned are independent of OwnedShortcuts by design: they describe different resources. Independence does not itself prove a data-loss bug.** The brief's “each is a data-loss path” conclusion is too strong. Initial-install PATH logic, for example, consumes its helper result correctly.

### Third mismatch: command identity is treated as ownership of an entire registry tree

Source: install-core.ps1 preflight classCommand check and registration block (roughly 476–483, 746–766); uninstall-core.ps1 classKey/expectedCommand branch (roughly 178–199).

A sequential counterexample, with no racing process:
1. A valid installation has the expected Sutram.Source open command.
2. The user adds a value or another shell verb beneath HKCU\Software\Classes\Sutram.Source, without changing that open command.
3. Uninstall sees the expected command.
4. It calls Remove-Item on classKey **with -Recurse -Force**, deleting the added value/verb too.

The same issue can start with a pre-existing class whose command already matches the prospective installation: setup's equality check accepts it; no record distinguishes its pre-existing contents. DefaultIcon is overwritten during setup, and the class tree is later deleted wholesale. AssociationOwned only protects the .sm default value; it does not protect class contents or the existing OpenWithProgids entry.

This is a static data-loss trace, **not a native reproduction**. It refutes the blanket “user-created and user-modified files/settings preserved” interpretation without invoking the previously discussed external-writer race.

Repair shape: record which registry values were created/changed, with their prior and installed values/types; preserve or explicitly restore pre-existing state. On uninstall, remove only owned values still matching the installed state, and remove keys only if empty. A matching command must not authorize recursive deletion of unrelated descendants.

### Start-menu parallel to the desktop case

New-Shortcut can overwrite a user-retargeted formerly owned Start-menu link because old list membership permits Save(). Uninstall also removes a modified IDE link if its target remains under InstallDir, or a modified terminal link if its arguments still contain InstallDir. Changes to arguments, icon, working directory or another verb are not captured by those partial checks.

Use the shared shortcut ownership fix for desktop **and** Start-menu paths. This is the same class, not a request for separate ad hoc flags.

## WS3 — mutant flags: exact definitions and packaging limit

**No checked-in normal build command found defines either mutant flag. Yes, the test harness deliberately defines both and produces real temporary executables. No automatic handoff from those temporary outputs to release paths was found.** These are distinct answers; “impossible to ship a mutant” would exceed the evidence.

### Complete flag occurrence inventory in executable source/build files at this pin

| Location | Role |
|---|---|
| tests/r137/test_slice_number.py:231–235 | Only active defining command found: loop over R142_MUTANT_NO_STMT_CHECK and R142_MUTANT_NO_GLOBAL_CHECK, then nasm -D{define} and ld |
| Same file, header line 25 | Documentation of the two flags, not a definition |
| src/sutram_compiler.asm:18396, 18410, 18414 | Three %ifndef NO_GLOBAL_CHECK guards, not definitions |
| src/sutram_compiler.asm:18905, 18915 | Two %ifndef NO_STMT_CHECK guards, not definitions |

The harness creates a tempfile.mkdtemp(prefix='r137-') directory. Each mutant and object is named for its flag inside that directory. It does not copy the results to sutram_compiler, sutram.exe, win/sutram.exe, or the setup payload. They remain ordinary executable files, not intrinsically unshippable files.

The normal paths inspected include tools/r69_build.py (and its shell wrappers), tools/cross_build_windows.py, windows/build-windows-native.ps1, installer builders and workflow flag searches. The build modes/commands inspected do not introduce either flag. These flags remove the corresponding entry walk **and its checked-state increments**, leaving the gen_expr fallback; “all slice protection removed” is not their exact behavior.

### What currently detects accidental substitution

The R137 gate's normal mode builds a plain ELF compiler and compares its bytes to committed sutram_compiler. When the Windows cross linker is available it also builds the normal PE and compares both PE compiler copies. Claude's committed v314 log explicitly reports those comparisons passing.

Limits:
- --compiler mode skips this identity check.
- Missing nasm/ld skips the plain rebuild block.
- Missing Windows linker omits the PE comparison.
- Neither a version string nor a generic passing test count substitutes for the explicit identity result.

### A packaging path still trusts pre-existing bytes

tools/build_installer_linux.py stages the current win/sutram.exe after existence/PE checks. windows/native-installer/build-installer.ps1 likewise copies that pre-existing binary. Those staging paths do not themselves require the plain-build comparison. A valid PE substituted at the input path can therefore be packaged with internally consistent hashes; hashing establishes byte identity, not build provenance.

This is **not evidence that today's package is mutant**, nor an automatic route from the ELF-only mutant harness into a Windows installer. It is a gap in the stronger claim that packaging makes substitution impossible.

Small concrete release requirement: record an explicit normal-build comparison for the exact compiler bytes embedded in the final package, and reject a release when that comparison is skipped or mismatched. Keep test outputs separate. This can use the existing gate; it need not introduce an automatic CI trigger.

## WS4 — native acceptance is necessary, not the only condition

I agree that the final Windows package needs native install/use/uninstall evidence. I do **not** agree that “once v315 runs” alone settles release, or that an unreviewed future shortcut fix is already the last change.

The finite remaining condition is:
1. Close the concrete desktop/Start-menu ownership and registry-tree preservation traces, with focused before/after preservation cases.
2. Reconcile the diagnostic/documentation differences already recorded in R218; no requirement to enlarge all AST nodes merely for line numbers.
3. Identify the final package and embedded compiler; record normal-build provenance and relevant compiler regression evidence.
4. Complete the agreed native Windows acceptance on those exact changed components: installer/IDE workflow, licence layout, cleanup, shortcuts, and the targeted flag/FFI behavior.

Existing successes may transfer where component bytes and relevant conditions are unchanged and that transfer is explicit. “Any source change invalidates all prior tests” is too broad; unrelated documentation changes do not require retesting an unchanged compiler. Changed package behavior does require its corresponding acceptance.

Also retain R218's corrections: the FFI error path currently names the callee but does not print a line; R217 was not implemented verbatim; the arithmetic gate does not prove the unique-node-visit premise. Repeated shared-state wording must not erase those qualifications.

**Current verdict: candidate, not release-approved.** The ownership repairs are not present at this reviewed pin, native v314 acceptance remains unreported, and the registry counterexample means a desktop-only patch cannot close the preservation question.

No source edits, builds, native runs, CI launches or merges performed.
