# Consolidated Windows handoffs for Sarvam

**Latest machine state: working v307, recovered from a deliberate interruption;
657/657 hashes and 322 checked suite cases pass. OOM and three slice failures remain.**
**Acronis also suspended the observed v307 upgrade.** Read the v307 handoff first.
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

The owner-supplied instructions, exact commands, raw logs, probes and screenshots
are linked within each evidence folder. Review-branch test scripts are named
above where main intentionally contains only the earlier verified reports/logs.
No email or external message delivery is implied: these handoffs are published
in the repository for Sarvam to read and acknowledge.

## Decisions still requested

- The earlier OOM candidate is incorporated in the tested v306/v307 builds. Investigate
  the expanded B3 448/480/512 MiB boundary and mandapa 64 MiB crash-after-message
  cases before treating the OOM behavior as closed.
- Retain the non-project-CWD library test with a complete compiler bundle.
- Preserve the now-verified v306 IDE refusal notice and previous-file Save
  protection; the isolated Save test left original examples unchanged.
- Preserve the v307 interrupted-install recovery pass and corrected DisplayVersion
  1.0.307. Address the three remaining slice escapes and log-reader fragility.
- Reconcile the handoff's A3 refusal expectation with the implementation's
  allowance for same-directory upgrades. Review the confirmed Acronis suspension
  and the recoverable-upgrade design. The runnable-wizard timeout remains unverified;
  no automatic action occurred while both processes were externally suspended.
- Distinguish this machine's working v307 installation from general v1.0 release
  acceptance. No product code was changed in this verification round.

Please acknowledge this consolidated index and the latest v307 evidence.
