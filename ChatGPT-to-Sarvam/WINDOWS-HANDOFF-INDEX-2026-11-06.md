# Consolidated Windows handoffs for Sarvam

**Latest machine state (7 November): unchanged upstream v311, pinned checkout `2e8f2ea4`, reinstalled and natively verified.** All 657 payload hashes match; one canonical compiler; all 11 tracked acceptance-test process identities closed. Read the [v311 acceptance observations](WINDOWS-V311-ACCEPTANCE-2026-11-07.md) first. Default install, first Notepad/CLI program, four IDE checks and 322 native cases pass (19.048 s). Licence text rendering, brief owner-observed uninstall PowerShell visibility and an empty association key remain findings; strict no-residue uninstall is partial. This was the existing account with active state cleared, not a new OS/profile. No timeout fired because neither install stalled.

The [v310 round](WINDOWS-V310-2026-11-07.md) reproduced loss of controlled target bytes when an unequal backup occupied the expected prefix-name. v311 now refuses and preserves both copies in that same reproduction. Compiler controls, 322 native suite cases, concurrency/publication-edit/recovery checks and 40 upstream installer-fixture assertions pass on v311. Arbitrary-writer atomicity and full release acceptance remain unproven. Older v309 repair evidence/PR #68 stays separately pinned; compare remaining differences before any integration.

**Owner's standing Windows workflow: implement the fixes, verify them, then hand
off to Sarvam.** Keep source in review branches and publish the verified evidence
and instructions on main; do not stop at a diagnostic-only handoff when a fix is authorised. The later v310 brief expressly prohibited product edits for that verification round; the newly landed upstream v311 repair was then independently tested without local source changes.
Earlier reports remain dated evidence and should not be rewritten
as if their failures never occurred. This index collects all handoffs from this
Windows install/diagnostic/repair sequence, as requested by the owner.

| Order | Handoff | Evidence / code | Status to retain |
| --- | --- | --- | --- |
| 1 | [v303 stopped verification](WINDOWS-V303-2026-11-06-STOPPED.md) | [Full report](../Windows-to-Sarvam/win-v303-2026-11-06/RESULTS.md); scripts on `codex/windows-v303-2026-11-06` | Older installation shadowed PATH; installer completion unproven; tests stopped as instructed. |
| 2 | [v305 direct execution](WINDOWS-V305-2026-11-06-DIRECT-RESULTS.md) | [Full report](../Windows-to-Sarvam/win-v305-2026-11-06/RESULTS.md); probes/scripts on `codex/windows-v305-2026-11-06` | Native OOM crash, partial direct-layout suite failure, and IDE load-refusal behavior measured. |
| 3 | [Lazy-commit OOM candidate](WINDOWS-COMMIT-OOM-2026-11-06.md) | [Draft PR #66](https://github.com/dap2810/Sutram/pull/66); [fixed review evidence](https://github.com/dap2810/Sutram/blob/3426712b2726247a8661cf6bd5049bbd2512d5d2/Windows-to-Sarvam/win-commit-oom-2026-11-06/RESULTS.md) | Eight targeted checks and 322 native suite passes; Linux parity; acceptance/repinning pending. Not installed. |
| 4 | [v305 boundary/IDE/harness diagnostics](WINDOWS-DIAG-V305-2026-11-06.md) | [OOM](../Windows-to-Sarvam/win-diag-v305-2026-11-06/OOM.md), [IDE](../Windows-to-Sarvam/win-diag-v305-2026-11-06/IDE.md), [harness](../Windows-to-Sarvam/win-diag-v305-2026-11-06/HARNESS.md) | B3 fails at 640 MiB/succeeds at 768 MiB; failure shared beyond kosh; Run clears compile/runtime errors; complete library layout fixes unrelated-CWD test. |
| 5 | [Installer diagnostic](WINDOWS-INSTALLER-DIAG-2026-11-06.md) | [Logs, argv and owner error screenshot](../Windows-to-Sarvam/win-installer-diag-2026-11-06/HANG.md) | Two retries refused old ownership metadata before copy. No stuck child; incomplete state was not accepted. |
| 6 | **[Installation repair](WINDOWS-REPAIR-2026-11-06.md)** | **[Verified results and screenshots](../Windows-to-Sarvam/win-repair-2026-11-06/RESULTS.md)** | **Original files preserved; current installer completed; all 657 package hashes match; installed CLI/desktop IDE work.** |
| 7 | **[v306 native verification](WINDOWS-V306-2026-11-06.md)** | **[Full results](../Windows-to-Sarvam/win-v306-2026-11-06/RESULTS.md), [OOM reproductions](../Windows-to-Sarvam/win-v306-2026-11-06/OOM.md), [installation](../Windows-to-Sarvam/win-v306-2026-11-06/INSTALL.md), [IDE](../Windows-to-Sarvam/win-v306-2026-11-06/IDE.md)** | **Clean install, new-shell identity, IDE safeguard and 322 checked suite cases pass. B3 512 MiB and mandapa 64 MiB still crash after printing the refusal, 6/6 each. Automatic installer timeout not verified because the owner ended the stalled upgrade.** |
| 8 | **[v306 follow-up](WINDOWS-V306-FOLLOWUP-2026-11-06.md)** | **[OOM boundary](../Windows-to-Sarvam/win-v306-followup-2026-11-06/OOM.md), [upgrade/security/timer evidence](../Windows-to-Sarvam/win-v306-followup-2026-11-06/UPGRADE.md)** | **Acronis explicitly suspended both upgrade processes in this and the prior round. No timeout action through 937.88 s under external suspension; working backup restored. B3 crashes at 448 MiB (2/3), 480/512 (3/3 each); 544–640 pass. Mandapa crashes 10/10; all messages complete.** |
| 9 | **[v307 native verification](WINDOWS-V307-2026-11-06.md)** | **[OOM](../Windows-to-Sarvam/win-v307-2026-11-06/OOM.md), [upgrade/recovery/security](../Windows-to-Sarvam/win-v307-2026-11-06/UPGRADE.md), [slice probes](../Windows-to-Sarvam/win-v307-2026-11-06/SLICE.md), [commands/limitations](../Windows-to-Sarvam/win-v307-2026-11-06/COMMANDS.md)** | **18/32 OOM runs crash despite complete stderr; three slice escapes fail while function-value refusals pass. Upgrade suspended by Acronis through 936.39 s. Final interrupted-install recovery passes in 16.57 s; working v307 remains, all test processes closed. PowerShell live-log-reader interference independently reproduced and disclosed.** |
| 10 | **[Implemented repair and pinned v308 comparison](WINDOWS-V307-FIXES-2026-11-06.md)** | **[Draft PR #67](https://github.com/dap2810/Sutram/pull/67), [full evidence](../Windows-to-Sarvam/win-v307-fixes-2026-11-06/RESULTS.md)** | **Installed repair: upgrade 21.20 s, clean 9.47 s, recovery 8.65 s; 657/657 hashes, 36+8 OOM checks, 20 slice checks, 322 native suite passes. Corrected 153 CRLF-only package differences. Separate upstream v308 OOM 36/36 pass; arithmetic S4 failure confirmed. PR conflicts with concurrent v308 changes; independent port/review required.** |
| 11 | **[v309 native verification](WINDOWS-V309-2026-11-07.md)** | **[Full results](../Windows-to-Sarvam/win-v309-2026-11-07/RESULTS.md), [commands/probes](../Windows-to-Sarvam/win-v309-2026-11-07/COMMANDS.md)** | **Canonical v309 installed; 657/657 hashes; 7 arithmetic, 32 OOM and 322 native suite passes. README/reference checkout CRLF mismatch remains. Early/late retries complete; late retry restages 657 files. Edited file preserved by refusal. Two helper errors disclosed; all owned processes closed.** |
| 12 | **[v309 remaining issues fixed](WINDOWS-V309-FIXES-2026-11-07.md)** | **[Draft PR #68](https://github.com/dap2810/Sutram/pull/68), [verified evidence](../Windows-to-Sarvam/win-v309-fixes-2026-11-07/RESULTS.md)** | **Fixed candidate installed. 657 files plus manifest match across native Windows/Linux builds; late retry 657 reused / 0 staged. Upgrade/early/late retries Finish; edited bytes preserved. 14 behavioral + 40 existing installer checks pass; both installed compiler layouts run; all 18 owned processes closed. Full corrected wizard screenshot retained.** |
| 13 | **[Final v309 fixes and native verification](WINDOWS-V309-FINAL-FIXES-2026-11-07.md)** | **[PR #68 at 664ff188](https://github.com/dap2810/Sutram/pull/68), [final evidence](../Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/RESULTS.md)** | **Final candidate installed. C1/I2 reproduced/fixed; 42/59/21 compiler checks pass on Windows and Linux; 322 native cases, 7 arithmetic, 32 OOM, 44 installer gate checks, 14 reuse checks and 7 lock checks pass. IDE Run/Save/refusal verified. Payload parity and early/late/edited recovery pass; all 21 owned processes closed. Observer failures retained.** |
| 14 | **[Final integration with current main](WINDOWS-V309-FINAL-FIXES-2026-11-07.md)** | **[PR #68 at 7ab8c439](https://github.com/dap2810/Sutram/pull/68), [integration evidence](../Windows-to-Sarvam/win-v309-integrated-2026-11-07/RESULTS.md)** | **Concurrent R140 changes retained and conflicts resolved. Compiler/engine/wizard/IDE source and payload binaries unchanged from 664ff188; four docs updated. Rebuilt package installed in 22.67 s; 657/657 hashes and Linux parity; 14/7 fixtures and 16/29 gates pass again; both new processes closed.** |
| 15 | **[v310 native verification](WINDOWS-V310-2026-11-07.md)** | **[Full evidence](../Windows-to-Sarvam/win-v310-2026-11-07/RESULTS.md)** | **322 suite passes; globals/arithmetic/nesting/concurrency/publication-edit controls pass. C4 unequal superseded backup loses controlled target bytes before cleanup; ordinary recovery succeeds. No product edits.** |
| 16 | **[v311 upstream repair verified](WINDOWS-V311-2026-11-07.md)** | **[Full evidence](../Windows-to-Sarvam/win-v311-2026-11-07/RESULTS.md)** | **Same C4 reproduction now refuses and preserves both copies. 322 native suite passes; 19/14/7 installer-fixture assertions; real concurrency/edit/recovery passes; 657/657 installed hashes; all 12 full-install processes closed. No release acceptance.** |
| 17 | **[v311 acceptance observations](WINDOWS-V311-ACCEPTANCE-2026-11-07.md)** | **[Full result table](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/RESULTS.md), [install/uninstall](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/FRESH-INSTALL.md), [IDE](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/IDE.md), [suite/time](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/SUITE.md)** | **Default install 27.171 s, first Notepad/CLI program, reinstall 40.188 s, four IDE checks and 322 native cases pass. Owner uninstall: no error, brief PowerShell window; empty registry key remains. Licence presentation defect observed. 657/657 final hashes; no spontaneous stall; no product edits or release verdict.** |

The owner-supplied instructions, exact commands, raw logs, probes and screenshots
are linked within each evidence folder. Review-branch test scripts are named
above where main intentionally contains only the earlier verified reports/logs.
No email or external message delivery is implied: these handoffs are published
in the repository for Sarvam to read and acknowledge.

## Decisions still requested

- Acknowledge the v311 acceptance observations and review licence UTF-8/line-break rendering, transient uninstall PowerShell visibility and empty association-key cleanup. The acceptance brief prohibited product edits; these are remaining findings, not claimed repairs. Retain the existing-account scope and unexercised timeout.

- Acknowledge the new v310 reproduction and independent v311 repair verification. Retain the remaining full-hash-then-delete writer-race limitation and A2 class-inference correction. The final installed candidate is v311, not PR #68.

- Acknowledge and independently review PR #68 at 7ab8c439: payload determinism,
  repeated staging, global initializer validation and ownership snapshot ordering
  are implemented and verified. Rebuild and update
  release artefacts/pins only after acceptance. The installed candidate is identified
  by exact hashes in the latest fix handoff.
- Compare the repair's self-termination OOM path with v308's reserve-based path:
  both now have the same 36/36 native boundary/control evidence. Exact original
  fault location and reserve-allocation-failure behavior remain unproven.
- Retain the non-project-CWD library test with a complete compiler bundle.
- Preserve the now-verified v306 IDE refusal notice and previous-file Save
  protection; the isolated Save test left original examples unchanged.
- v309 now passes the requested arithmetic-wrapper refusals and valid length
  control. Review the broader compatibility and deterministic LF packaging work
  from PR #67 independently; the seven v309 cases are not a general borrow checker.
- Reconcile the handoff's A3 refusal expectation with the implementation's
  allowance for same-directory upgrades. Review the confirmed Acronis suspension
  and the recoverable-upgrade design. The runnable-wizard timeout remains unverified;
  no automatic action occurred while both processes were externally suspended.
- Distinguish the historical v307 repair/v308 comparison from the historical
  upstream v309 verification. Reconcile the historical
  [pinned v308 static review](ROUND-207-V308-STATIC-REVIEW-FOLLOWUP.md) with v309's
  changes and native evidence; neither this index nor the tests grant release acceptance.

Please acknowledge this consolidated index, the new v311 acceptance observations and the prior v310/v311 evidence sets; retain PR #67 and the earlier reports as dated comparison material.
