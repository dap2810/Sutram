# Windows v309 verification — 7 November 2026

**v309 is installed and working at the canonical path.** Arithmetic, the requested OOM cases and the native suite pass. Payload determinism remains unresolved; late recovery completes but repeats all staging copies. Independent Sarvam acceptance is pending.

| Task | Result | Evidence |
| --- | --- | --- |
| A arithmetic | 7/7; six refusals, valid length prints 2 | [ARITHMETIC.md](ARITHMETIC.md) |
| B OOM | 32/32; exit 1, exact 32-byte diagnostic, no FD | [OOM.md](OOM.md) |
| C checkout/package hashes | FAIL: 2/3 differ by CRLF; embedded integrity 657/657 | [PAYLOAD.md](PAYLOAD.md) |
| D recovery | Early/late retries finish; edit preserved; late retry restages 657 files | [RECOVERY.md](RECOVERY.md) |
| E fresh-shell identity | Only canonical v309, registry 1.0.309, 657/657 installed hashes | [handoff-identity.json](handoff-identity.json) |
| E native suite | 322 PASS; 3 NO_EXPECTATION; 6 deliberate skips; 0 FAIL / COMPILE_FAIL / TIMEOUT | [native-cases.json](native-cases.json) |

Tested repository commit: `7c92bc02ff6f81b4903a20c14712ad3fd566b0c4`.
Compiler SHA-256: `05b23d56d40aaa4b71c6d67d13996d75da6e4d2e2b2ac47fbf4960a1a52fb481`.
Setup SHA-256: `9d046b4e1b3d95222523e78304e48cb5bc10a69f951b33822a2673f0dc3bb533`.

The original fresh-shell check found an older installed candidate and stopped, as requested. The owner's subsequent `start working on it` authorised the v309 installation. The original installation was preserved before upgrade; v309 was backed up before interruption tests. [Original inventory](backup-before-v309.json), [working v309 inventory](backup-working-v309.json).

No compiler, library, example, golden, installer, release binary or workflow was modified. This publication contains only reports, test probes/helpers and recorded evidence. No full CI was launched. No release, IDE or general memory-safety acceptance is claimed. The two helper errors are disclosed in RECOVERY.md.

[Exact commands and evidence interpretation](COMMANDS.md). [Owner's brief](OWNER-INSTRUCTIONS.md). [Sarvam handoff](../../ChatGPT-to-Sarvam/WINDOWS-V309-2026-11-07.md).
