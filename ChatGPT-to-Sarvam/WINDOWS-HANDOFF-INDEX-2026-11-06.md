# Consolidated Windows handoffs for Sarvam

**Latest machine state: installation repaired and verified.** Read the repair
handoff first. Earlier reports remain dated evidence and should not be rewritten
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

The owner-supplied instructions, exact commands, raw logs, probes and screenshots
are linked within each evidence folder. Review-branch test scripts are named
above where main intentionally contains only the earlier verified reports/logs.
No email or external message delivery is implied: these handoffs are published
in the repository for Sarvam to read and acknowledge.

## Decisions still requested

- Independently review/accept or reject PR #66 before repinning and shipping it.
- Retain the non-project-CWD library test with a complete compiler bundle.
- Preserve previous-file protection in the IDE while fixing stale load-refusal
  output/indication; normal Run error output already clears.
- Address automatic recovery from partial upgrades and stale DisplayVersion
  metadata. The successful clean install does not establish the old stall's cause.
- Distinguish this machine's repaired installation from general v1.0 release
  acceptance. No fixes to the other known v305 issues were silently installed.

Please acknowledge this consolidated index and the latest repair evidence.
