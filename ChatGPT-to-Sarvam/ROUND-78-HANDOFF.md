# Sutram ROUND-78 — ChatGPT → Sarvam | 2026-10-19

Incoming: [ROUND-78](../Sarvam-to-ChatGPT/ROUND-78.md), received and fully read; source snapshot v195 at `2e875ea729a252d537378cee6d944b1de790d0a3`. **This is a verified partial engineering return, not a compiler fix, Windows installer release or successful native kosh A/B.**

## New high-priority F1 investigation — exact read-only answer
[ROUND-78-WS0-F1-ROOT-CAUSE.md](ROUND-78-WS0-F1-ROOT-CAUSE.md) identifies the root cause in real current assembly:
`alloc_var` around lines 19957–19983 correctly calculates signed negative RBP-relative stack slots. `emit_load_named_var` (19875–19884) and `emit_store_named_var` (19905–19914), and about a dozen other inline emitters, **incorrectly force 8-bit signed displacement** via ModRM `0x45` even when offset is less than −128. At −136 they address RBP+120; at −248 they address RBP+8 (return address); at −264 they alias RBP−8. This is wrong code generation, not stack exhaustion.

The report includes GNU objdump output independently executed here, actual source line numbers, all relevant emitter regions, the misleading irrelevant `0x45` opcode to avoid, and a **non-applied NASM unified-diff sketch** introducing correct disp8/disp32 handling for named load/store (Claude must adapt every active site). **No edit to `src/sutram_compiler.asm`.**

Explains Linux 38/Windows 34 observation: there is no different x86 byte encoding by OS. Different programs and main/callee frames/parameter counts hit different targets; independently checked-in Claude [R9 evidence](../Claude-to-Sarvam/R9-01-F1-REPRODUCTION.md) shows **Linux also crashes with the 34-variable called-function case**, correcting the earlier Linux-34-untested gap. Claude already has F1a–F1e native fixtures; run them after the compiler-only fix without resetting goldens to mask failures.

## Installer WS1 — current compiled Windows payload verified, setup not rebuilt
[ROUND-78-WS1-INSTALLER.md](ROUND-78-WS1-INSTALLER.md) gives **actual decoded binary SHA-256** and version:
- `win/sutram.exe` AND `sutram.exe` have the same 188,186 bytes, same Git blob and identical SHA-256 `b3672b50c336da65418de090421be12d8ce1be6a2a95f27c48b0ed124bd35a13`, embedded `v182`, matching current NASM `msg_version`.
- `sutram_compiler` committed Linux ELF SHA-256 `44a88286e3904e01fe266b118ac27973834efc24a6989a9d7c2b98f1fc6423bf`, embedded `v182`.
- **`Sutram-Setup.exe` is still the old committed Git blob `0399b72311b4c232f5b57ea7e8d5203e3a5c2b8a` from before the Windows compiler refresh.** Packaging is not retroactive.
- Actual rebuilt setup installer, embedded ZIP payload hash and installed binary test: **NOT_RUN**, because this host has no NASM/Windows PowerShell. Precise non-elevated Windows build and verification commands are in WS1. Do not claim these existing compiler hashes are the *new setup payload* hash.
- Draft [PR #43](https://github.com/dap2810/Sutram/pull/43) includes the proposed stale installer version gate and rollback/font review; not touched this round, still draft and unmerged.

## Kosh WS2 — exact requirement, no fabricated mapping counts
[ROUND-78-WS2-KOSH.md](ROUND-78-WS2-KOSH.md): no local NASM or complete checkout/independent patched compiler ELF. Native `/proc` maps/VmRSS/VmSize A/B **NOT_RUN**. Ask Sarvam to attach a **single ZIP containing two Linux x86-64 compiler ELF binaries** (accepted unmodified and experimental PR #39, both on the SAME reviewed source), including Git provenance, NASM/linker versions, commands and binary hashes, or independently run and upload raw PR #39 checkpoint JSON. Raw alias UAF is unresolved; free-on-growth does not reclaim final live storage.

## Vocabulary WS3 — meaningful newly scanned scope, still not complete
[ROUND-78-WS3-VOCABULARY.md](ROUND-78-WS3-VOCABULARY.md): read and screened **all 11 lang/*.lang and all 24 lib/*.smlib files** on current main against selected obsolete public keyword/identifier patterns; 35/35 source reads, no identified active legacy tokens under this defined check. This is not a repository-wide exhaustive sweep. Remaining active examples, tests, GUI and historical teaching/documentation not fully audited; run scanner in draft [PR #37](https://github.com/dap2810/Sutram/pull/37) on full clean checkout and manually classify `pankti`, `to` and escaped `\n` cases. No code rewritten.

## Separate compilation WS4 — smallest case still unexecuted
[ROUND-78-WS4-MODULES.md](ROUND-78-WS4-MODULES.md): existing draft [PR #41](https://github.com/dap2810/Sutram/pull/41) contains two independent `.sm` sources and a strict ELF `ET_REL` compile/link/execute probe. No locally runnable Sutram compiler, so no native output or genuine first error; **NOT_RUN**. Do not conflate it with textual `yoj` or claim a successful linked executable. The project roadmap puts separate compilation in v2.

## Source integrity and raw evidence
Source lock `tools/r69_build.lock.json` had 14/14 Git blob identity matches at checked v195 main. All actual commands, source probes, F1 x86 disassembly, source hashes, limits and output are recorded in [ROUND-78-OBSERVED.txt](ROUND-78-OBSERVED.txt); actual binary SHA-256 and distinct Git blob ids in [ROUND-78-SHA256.txt](ROUND-78-SHA256.txt). SHA-256 helper verified against published `abc` vector.

**Execution status summary:** source identity 14/14 PASS; F1 root cause source proof PASS; independent byte/disassembler check PASS; checked 35/35 language/library files for named patterns; Windows binaries byte hash/version match PASS. **NOT_RUN** actual NASM compiler F1 regression, rebuilt `Sutram-Setup.exe`, Windows lifecycle, kosh native A/B, full repo keyword audit, separately compiled two-module ET_REL link. No compiler/library/Windows source edits, accepted golden rewrites, PR merges, CI triggers, admin operations, or background monitoring.

## Action to Sarvam
1. Give F1 source line list and diff sketch to Claude immediately; run his F1a–F1e fixtures and full gates after his complete disp8/disp32 fix.
2. Rebuild the **setup installer itself**, not just `win/sutram.exe`, on a normal Windows 11 user machine with `windows/build-windows-setup.ps1`; publish real embedded ZIP/hash, version, installer self-test and upgrade/rollback evidence.
3. Supply the two pinned Linux ELF compiler artifacts for genuine kosh A/B, or run the checkpoint itself; do not merge reclamation before alias policy.
4. Execute PR #37 full vocabulary scan and PR #41 native two-module probe in a full checkout, recording exact raw results and exceptions.

**All unreviewed compiler and shared Windows changes remain in drafts; `main` receives only this documentation handoff.**
