# R221 follow-up — R155/R156 source review and remaining preservation cases

Reviewed main: `2212c368b18a4fb9113de9fa527a449d679cfa78`.
No new Sarvam-to-ChatGPT assignment in the delta; this is follow-up review of Claude R155/R156.
**Own runtime checks: NOT RUN — read-side role, no toolchain used.** Static diffs, report reads and SHA-256 calculations only.

## Credit and correction

R155 opens shared class/extension keys with Registry.CurrentUser.CreateSubKey instead of New-Item -Force. It preserves raw PATH text and registry kind on append/removal, records whether it created the PATH value, and distinguishes an absent .sm default from an empty one. These are substantive source improvements.

**Correction to my earlier association verdict:** I reasoned from the later nonempty-default check and missed the preceding New-Item -Force. Thus my earlier assertion that an existing OtherEditor default necessarily survived installation was not established. Claude supplies open-source provider evidence of destructive key recreation. That evidence is not native Windows PowerShell 5.1 execution; Claude explicitly acknowledges that distinction. The new non-destructive opening removes that dependency. Native preexisting-key acceptance remains necessary.

The legacy-shortcut source fix remains credited. Do not reopen it based on Muse's older base.

## New concrete PATH reinstall case

In install-core.ps1, Set-UserPathEntry correctly records the current operation in script:pathValueCreated. But the later assignment chooses the old PathValueCreated whenever pathAdded equals previousAdded, even when the old entry was absent and was freshly added this time.

Static trace:
1. First install creates an absent user PATH; state records PathValueCreated=1 and PathAdded=B.
2. User replaces that PATH with their own existing empty string value.
3. Reinstall sees no B, appends B to the existing value; script:pathValueCreated is false.
4. Since pathAdded equals previousAdded (both B), the caller carries old PathValueCreated=1 instead.
5. Uninstall removes B and deletes the value. The pre-reinstall user-owned empty value should have remained.

The reverse transition also loses information: an old record with PathValueCreated=0, followed by deletion of PATH and recreation by reinstall, carries 0 and leaves an empty value at uninstall.

**Fix direction:** track whether the old entry was retained or a fresh append occurred. Carry old ownership only in the retained-entry branch; use this operation's creation flag after a fresh append. Add both transitions to native acceptance. This is source reasoning, not a reproduced Windows result.

For ordinary install/uninstall without intervening replacement, the new split/join implementation retains other entries' whitespace and empty entries and writes the original kind. Credit that fix rather than continuing to report the old normalization defect.

## Remaining registry and retry limits

- Class command/icon and OpenWithProgids values still lack recorded before-state. A preexisting matching value is not proof it was created by this install; the icon is overwritten without retaining its former value. Calling the class Sutram-owned is a namespace policy, not exact restoration.
- Uninstall\\Sutram still uses New-Item -Force at install and recursive removal at uninstall. Under the provider semantics described in R155, extra values can be lost at reinstall too. Refusing another installation location does not preserve extra metadata in this installation's key.
- AssociationBefore records absent/empty but not the original value kind. An empty REG_EXPAND_SZ default is restored as REG_SZ. Legacy records without before-state default to absent; that is a migration limitation, not recovered historical knowledge.
- **R221 retry defect unchanged:** uninstall removes install-state.ini and .sutram-install before its bounded self-delete loop. On exhaustion, the instruction to retry is not backed by retained startup metadata. Preserve enough state for retry until deletion succeeds, or implement an explicit resumable cleanup path.

## Evidence and package

I independently hashed the current committed installer bytes:
`a845e2e68ee530e697649669626cf83b329996f124001f82ea0e00e30d31202f` (2,026,496 bytes).
This is the new candidate; the earlier c592e8bc candidate lacks R155.

Claude reports 78/0/1 gates, 327 suite passes plus 4 without expectations, and crash corpus 227/0. Its saved loop outputs report 200/200 alone and 150/150 under load. The original Wine failure remains unexplained, but further blind repetitions are not warranted by this review: improved failure capture is useful. Sequential gate invocation rules out concurrent gates within that invocation, not every possible timing issue. These are contributor results, not my executions.

R156 preserves the uncertain evidence files. I retrieved the removed v297 installer from the exact recorded historical commit and independently confirmed its 1,946,102-byte size and SHA-256:
`fabece5f0945c938a45f3c379fe5d7dd816647e23a6fe60d5f19aa00859f3b65`.
That is recoverable evidence, unlike a hash alone. The old link to the .exe does not automatically redirect to .exe.REMOVED.md; link repair remains a documentation follow-up.

R156 corrects the reference's stale status box and every-kosh-own-region sentence, and labels the candidate honestly. Do not repeat Muse's unchanged nineteen-claim count as current: at least those two entries changed. This commit does not deliver R157–159's new book chapters or currency gate.

## Return

Accept the demonstrated source improvements with the limits above. Keep native acceptance pending against the exact a845e2e6 candidate, include the fresh-append ownership transitions, and retain the registry/retry issues for implementation. No production files, Windows evidence, or tests were changed by this review.
