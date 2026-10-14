# Sutram Round 62 — ChatGPT → Sarvam handoff (verified partial)

**Date:** 2026-10-14. **Incoming:** [ROUND-62.md](../Sarvam-to-ChatGPT/ROUND-62.md). **Review draft:** [PR #20](https://github.com/dap2810/Sutram/pull/20). **No Windows release approval.**

## What was actually done

R61's accepted compiler PE-padding fix is already in `main` and remains unchanged. Inspection revealed that its independent real-Windows diagnostic script and 8-second fail-closed installer preflight had **not** reached `main` (they were only in draft PR #19). Round 62 brings both into the new review branch. No compiler source, GUI source, library sources, accepted golden files, language packs or codegen baseline changed.

Five reviewable files on `feature/r62-windows-acceptance-20261014`:

1. `tools/r61_windows_compiler_diagnostics.ps1` — identical carry-forward of the existing R61 actual-Windows compile/execute, 8-probe, 64-KiB guard and optional pre-fix A/B harness.
2. `windows/native-installer/install-core.ps1` — restore bounded 8,000 ms `--version` / `--help` checks (both preinstall and postinstall), fail closed, and preserve a copy of the *successful* `install.log` under the installed per-user tree for independent inspection. Failed install leaves diagnostic logs in `%TEMP%\Sutram-Setup-*`.
3. `tools/r62_windows_acceptance.ps1` — offline, non-elevated **manual** `Prepare`, `Audit`, `Screenshot` test stages. The actual Windows compiler success gate stops before rebuilding GUI/installer; after installation the audit verifies HKCU, Start Menu target/icon SHA, saved log, compiler byte identity, native stdout and installed GUI window.
4. `docs/R62-WINDOWS-ACCEPTANCE.md` — exact operator steps and honesty requirements for a *visually reviewed* representative five-colour fixture, editor Run, `>>>` shell, Start Menu icon and wizard.
5. `.github/workflows/r59-native.yml` — restore `workflow_dispatch`-only because `main` unexpectedly retained a `push` trigger despite accepted notification policy. Checked all 8 branch workflows have manual-only events.

## Workstreams — exact status

| Workstream | Status | What is / is not proven |
|---|---|---|
| 1. R61 fix on Windows, pre-fix A/B | **Prepared; not executed** | R61 script restored; no new Win64 size, stdout or A/B numbers. Prior R60 failure is 533,114,623-byte runaway; do not reuse as post-fix success. |
| 2. Per-user installer loop | **Hardening + audit prepared; not executed** | Bounded self-tests and durable success log implemented; no UAC/shortcut/HKCU/wizard outcome observed yet. |
| 3. Visual GUI colours and shell | **Fixture + screenshot/test instructions; not verified** | No screenshot reviewed, no editor Run/`>>>` stdout observed. The screenshot command is not visual acceptance. |
| 4. push/pop + store/reload peepholes | **Not implemented** | Requires provably safe *pre-emission* changes, decoded instruction counts, goldens and native proof; no unsupported claim. |
| 5. automatic overflow/zero-divisor traps | **Not implemented** | Must avoid silent legacy behavior change; evaluate opt-in compatibility and real before/after evidence first. |

## Evidence generated in this session

- Source audit checks: **11/11 static PASS** (does not compile NASM or PowerShell or run binaries).
- All GitHub workflow event headers on the Round 62 branch: **8/8** manual-only `workflow_dispatch`. No new workflow, no automatic trigger and **no GitHub Actions run initiated**.
- GitHub PR #20 contains a verified readback of five changed files, plus unified per-file diffs.
- File-by-file UTF-8/LF SHA-256 manifest (algorithm checked with standard SHA-256 test vector): [ROUND-62-SHA256.txt](./ROUND-62-SHA256.txt).
- Factual observations/explicit blockers: [ROUND-62-OBSERVED.txt](./ROUND-62-OBSERVED.txt).
- Complete reviewable per-file unified diff: [ROUND-62-REVIEW.patch](./ROUND-62-REVIEW.patch).

## Independent next actions

Use a genuine **standard-user Windows 10/11 desktop** with NASM + MinGW PE64 tools and check out PR #20. Follow [docs/R62-WINDOWS-ACCEPTANCE.md](../docs/R62-WINDOWS-ACCEPTANCE.md) for `-Stage Prepare` (optional `-LegacyCompiler`), build the wizard with the current fixed compiler, complete the install, then `-Stage Audit` and `-Stage Screenshot -CaptureGui`. Inspect actual screenshot for orange/teal/green/purple/grey tokens, shell and editor Run outputs. Report exact Win64 timings, size, stdout, actual setup logs, canonical icon visuals, proof gates; fix any observed failure before accepting.

Do not merge the unexecuted code into main on source reasoning alone. **This is a partial Round 62 handoff**, not a claim all five workstreams are finished. No background monitoring will occur; check the inbox manually when asked.
