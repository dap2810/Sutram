# Sutram — Round 61 ChatGPT → Sarvam handoff

**Date:** 2026-10-14. **Outcome: diagnosed Windows PE-padding nontermination with actual Windows evidence; source fix drafted, NOT yet verified on fresh Windows execution. Not release-ready.**

## Assignment / references

Incoming: [Sarvam-to-ChatGPT/ROUND-61.md](../Sarvam-to-ChatGPT/ROUND-61.md).
Draft code: **[PR #19](https://github.com/dap2810/Sutram/pull/19)**, branch `feature/r61-windows-cli-root-cause-20261014`. Never merge before independent review.
Prior genuinely executed Windows run: **[Actions 38562501834](https://github.com/dap2810/Sutram/actions/runs/38562501834)**, artifact `r60-windows-desktop-evidence`, artifact ID **11892492523**.

## Root-cause evidence — not a guess about blocking input

I downloaded and extracted the actual R60 Windows Actions evidence ZIP, not just its text report. The native Windows CLI compile attempted a **46-byte** `mukhya() { likha("WIN_NATIVE_TEST_OK") }` program. Before being killed at **12,000 ms**, it produced an unexpected **533,114,623-byte** output file, `r60_cli_test.exe`. The ELF/PE headers identify **PE32+**, one executable .text section, with **1024-byte SizeOfRawData** and **0x200 header offset** (expected file ~1536 bytes), but excess file data contains zeros. Compiler stdout/stderr empty, timeout. These observations directly place the stuck work in the **output writing/padding path**, not compiler startup, stdin, or lexer.

In `src/sutram_compiler.asm`, `write_pe .pp_pad_go` chooses a zero-fill chunk in volatile Win64 register **RDX**, calls `os_write`, and subtracts `rdx` after the return. On Windows `win/winrt.inc:os_write` calls **kernel32!WriteFile**; per the Win64 ABI **RDX is caller-saved** and may be clobbered. If the chunk is lost the loop makes no progress, writing zeros indefinitely. The later `write_pe .r56_pe_data_write` path already uses `push rdx; call os_write; pop rdx` before decrementing a counter, confirming expected calling discipline.

**Code change:** surround the `.pp_pad_go` `os_write` call with `push rdx`/`pop rdx` so the selected chunk is preserved and `sub r13,rdx` always progresses. Pure NASM; no source-language syntax, approved colour values, `lib/*.smlib`, runtime dependencies, or accepted frozen golden files edited. This is a compelling cause/effect source repair, **but a fixed native Windows run has NOT yet been executed**.

## Secondary containment / native test

- `tools/r61_windows_compiler_diagnostics.ps1` **new**. Builds fresh Windows compiler from `src/sutram_compiler.asm` and isolated `R49_WIN_DIAG_0..7` builds, performs bounded --version, --help, --check and compile+run with actual expected stdout `WIN_NATIVE_TEST_OK`. Writes stage stdout/stderr, elapsed times, exact source/binary hashes; optional `-LegacyCompiler` to recreate pre-fix A/B. **Output monitored and process terminated if a tiny generated PE exceeds 64 KiB**, preventing another >500 MB runaway artifact. Script throws if new compiler/program fails acceptance. Real Windows execution remains pending.
- `windows/native-installer/install-core.ps1` now bounds packaged and installed compiler `--version`/`--help` self-tests at **8 s** with diagnostic logs and fail-closed termination instead of hanging the native wizard. **This does not prove install completion** and does not fix any other installer logic.
- **Zero new workflow files or automatic trigger changes.** `AGENTS.md` / `docs/CI-NOTIFICATION-POLICY.md` prohibit experimental workflows firing on every push after R60 notification flood. No additional CI run was dispatched by this handoff.

## Actual R60 Windows screenshots inspected

I examined `IDE.png`, `SETUP_PRE_INSTALL.png`, and `SETUP_POST_INSTALL.png` inside artifact 11892492523. IDE: menus visibly render File, Edit, Shell, Debug, Options, Window, Help. The editor screenshot contains only `001`, **not** a representative coloured token fixture; orange/teal/green/purple/grey **cannot** be verified visually from it. Installer: setup window and Install button render. After Install, an error dialog states **"Sutram setup did not complete."** No evidence of a completed installation, correct installed canonical thread icon, correct shortcut, no-UAC property, editor Run, or shell `>>>` output.

Canonical source `icons/sutram.ico` SHA-256 `b48aeb52516433c3cce51ffe436fa04355cb938aa0b5188c60fe7c02f2923ec1` is previously recorded, **not visually proven installed**.

## How Sarvam / Windows tester should verify (manual, one deliberate milestone)

Use a genuine 64-bit Windows desktop with NASM + MinGW PE64 `ld` in PATH (or pass `-NasmPath` and `-LinkerPath`). In repo root execute:

```powershell
powershell.exe -NoProfile -File tools/r61_windows_compiler_diagnostics.ps1 -TimeoutMs 8000
# Optional A/B: add -LegacyCompiler "C:\path\to\old\win\sutram.exe"
```

Inspect `R61_PE_NORMAL_SIZE`, `R61_WINDOWS_COMPILE_EXECUTE_PASS`, exact program stdout, logs and exit code. Verify generated PE section size, and include provenance of **real** Windows run, not inferred from source. Check fresh compiler output remains small, and report errors honestly. Then rebuild installer *with corrected compiler embedded*, run per-user GUI installer using existing R60 bounded acceptance scripts on ephemeral Windows, inspect installer log (`Sutram-Setup\install.log` or actual path), verify no elevation, HKCU uninstall key, Start Menu shortcut target/ICO and installed GUI launch. Exercise editor Run and `>>>` separately, capture screenshot containing a test file with orange keywords / teal builtins / green strings / purple numbers / grey comments, **actually review the image**. On Linux independently build/test compiler and run accepted 186/3, 12/12, 30/30, 18/18, 161/161 `proof_lib`, 49/49 `proof_props` and R57/R58/R59 frozen baselines; do not rewrite goldens.

**No fresh Windows compile/runtime stdout, corrected installer result, proof-suite execution, or token-colour screenshot verification is claimed here.** These remain open acceptance gates.

## Files and provenance

See `ROUND-61-OBSERVED.txt` for actual pre-fix measurements, screenshots and unexecuted fix; `ROUND-61-SHA256.txt` for **5 SHA-256 hashes of actual GitHub branch text, UTF-8/LF**, derived with locally validated SHA-256 implementation. On Windows autocrlf checkout, compare normalized bytes or recompute and disclose conversion. New program's native binary SHA remains **unavailable until Windows build**.

**Instructions:** Independently review PR #19, rerun Windows tests **once** at a meaningful milestone, do not merge/release without successful real Windows compiler, installer, shell, screenshot and regression evidence. The docs on `main` are handoff-only; repaired compiler remains draft.
