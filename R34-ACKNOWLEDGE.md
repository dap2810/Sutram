# R34 — the Windows linker, the real-Windows fixes, the rebuilt installer: please acknowledge

**For Sarvam, ChatGPT, Muse and Claude.** Written 2026-10-21 by Claude, on the owner's real Windows 11 PC, at
the owner's request: *"make the linker for Windows and test it here; fix the project where it requires, but do
not change the fundamentals or the philosophy; run the GUI and every sample file one by one; rebuild
Sutram-Setup.exe; record it so Sarvam, Claude and ChatGPT know what has been done and what is left."*

**Where it is:** branch **`claude/windows-linker`** - code, binaries, installer, tests, evidence. **Not merged
into `main`** (`AGENTS.md`: unapproved code stays on a review branch until Sarvam accepts it). This file is on
both.

**Read, in this order:** `Claude-to-Sarvam/R34-00-HANDBACK.md` (the linker) · `R34-01-FIXES.md` (what the
real Windows run found and fixed) · `R34-02-INSTALLER.md` (the installer and acceptance) ·
`Windows-to-Sarvam/WIN-ACCEPT-2026-10-21.md` · `Claude-to-Sarvam/evidence-r34/` (every number).

## Status at a glance

| | |
|---|---|
| Compiler | **v243** (one pure-NASM source, as before). The ordinary path: **562 programs compile to the same bytes as v242, on Windows and on Linux** |
| Windows linker | **built**: `--object`/`--separate` on Windows, object format **version 2 (`SUTRAMO2`)**, `sutram-link.exe`; 1018 checks, 0 failed |
| IDE on Windows | **every sample, one by one: 210 match** (was 193); 0 hangs; status line in the pack's script; a data-loss defect fixed |
| Installer | **`Sutram-Setup.exe` rebuilt** (`285470a4…`): v243, the linker, the fixed IDE; leaves no install staging in `%TEMP%` |
| Windows acceptance | **PASS, 16 / 0 / 0, run exactly as documented**; the project's checker: **ACCEPTED** (one machine, one run - not a release) |
| Linux gates | `gates.sh` **28 PASS / 3 FAIL / 1 NOT-RUN**; the 3 FAILs are `main`'s own (below) |

## What did not change - the fundamentals

- One pure-NASM compiler source; native code; no runtime; no toolchain for the user.
- An ordinary program needs no linker - the linker is opt-in, as before.
- **No golden, no test expectation and no R70 fixture was changed** to make anything pass.
- Least privilege: nothing elevates, nothing writes HKLM, no new network access, no new workflow.

## Done

| Area | What | Proved by |
|---|---|---|
| **Windows linker** | Windows `--object`/`--separate` -> `SUTRAMO2` (version 2 of the format, as the R29-02 plan asked: same layout, the runtime calls and `vitti` are holes) -> `sutram-link` writes the PE field for field as the compiler does; `sutram-link.exe` is the same source built for Windows | `tests/r34/test_link_windows.py`: 182 examples byte-identical, 252 module programs behave the same; either host links either target to the same bytes (182 / 182 both ways) |
| **Compiler crash** | a Windows program with more than 256 runtime calls crashed the compiler (v242 too); fixed | `tests/r34/test_windows_fixes.py` - **a gate** (on Linux too) |
| **IDE: data loss** | a refused open, then Save, **overwrote the refused file with another file's text** (70,686 bytes -> 67) | `tools/ide_examples_windows.ps1`, on a throwaway copy: v290's IDE FAIL, R34's PASS |
| **IDE** | examples ask before dropping unsaved work; input programs end at end of input instead of hanging the IDE; programs with their own modules compile; the status line shows the pack's script, not `?` | the same tool: 193 -> 210 match, 0 hangs, 14 -> 0 `?` lines |
| **Installer** | rebuilt with v243 + linker + fixed IDE; **removes its install staging after success (R4-03 s3)** | acceptance `install-staging-removed` PASS |
| **Acceptance tooling** | `accept-windows.ps1` runs on PowerShell 5.1 as documented; checks the installed linker (`linker-installed`, required); `check_accept_windows_log.py` no longer crashes on Windows | 16 / 0 / 0; ACCEPTED |
| **Repository** | the FFI tests' `.o` files committed (four gates failed on every fresh clone); `.gitattributes` (a Windows CRLF checkout broke 94 hashes and the pin check); two GUI tests read UTF-8 | fresh clone: FFI gates PASS with no C compiler; 213 / 213 hashes; `SOURCE_PINS_CHECKED` |

## Needs work - Sarvam

1. **Accept or refuse `claude/windows-linker`.** Rebuild and run the gates on your machine; merge if they hold.
   Record v243 in `CHANGELOG.md` and update `PROJECT-MASTER.md` section 9 ("Windows ... not a release",
   "Gate 6 is begun, not passed") with what is now measured.
2. **Regenerate `windows/windows-build-integrity.sha256`** - it is stale **on `main` too**:
   `preflight-windows.ps1` refuses (*"Source integrity mismatch: docs/BUILDING.md"*), so the documented full
   chain `windows\build-windows-setup.ps1` cannot run today. The installer here was built with
   `build-installer.ps1` directly, as R33 did. It is the build's trust root, so it is yours to re-sign.
3. **Decide - sockets on Windows.** `245_r18_netsock` returns -38 there (the runtime has no sockets).
   Adding them changes every Windows `.exe`'s runtime bytes.
4. **Decide - `29_nishkriya`** exits through a raw Linux `syscall`; on Windows it exits 0, not 42. Mark it
   Linux-only, or give it a Windows form.

## Needs work - ChatGPT (compiler internals, systems, specification, Windows)

1. **Review** the PE writer in `linker/sutram_link.asm` against the compiler's `write_pe`, and the `SUTRAMO2`
   section of `docs/OBJECT-FORMAT.md`.
2. **The FFI on Windows** - the next piece the plan left out. The Windows x64 convention (rcx, rdx, r8, r9,
   32-byte shadow space, xmm0-3 by position) is not `linux-x86_64-sysv`; the sidecar names the ABI, so a
   `windows-x86_64-msabi` line is the natural place; and a COFF reader in place of `sutram-elf2smo`.
3. **The Windows compiler reads no environment** (`env_get_value` walks the Linux stack layout), so
   `SUTRAM_LANG` does nothing on Windows and an `--object` for another pack is impossible there.

## Needs work - Muse (standard library, proofs)

1. **`tests/stdlib/r18_srij_overflow_guard`'s golden depends on the machine.** `suchi_srij(3037000499)` asks
   for 24 GB; its byte size does not wrap, so the documented guard does not apply, and `0` comes out only
   where the allocation is refused. Windows and WSL grant it, so **library proofs and R29 fail there** (on
   `main` too). Change the golden, or cap the allocation - a library decision.

## For information only

- **The IDE's editor holds 65,534 bytes**; a bigger program cannot be opened in it (it now says so and keeps
  the previous file's name). `105_block_nesting_capacity` (70,686 bytes) is the one example affected.
- **The IDE gives a run no input** - a clean end of input now, no longer a hang. An input box is a feature.
- **The IDE binary and the installer were linked by MSYS2 ld 2.47** on this PC; the same sources do not give
  the same bytes across different `ld` versions, so the IDE is proved by behaviour. The compiler and linker
  binaries rebuild byte for byte (NASM 3.01 + GNU ld 2.42) - `evidence-r34/reproducible-build.txt`.
- **The uninstall folder** (`%TEMP%\STM*.tmp` with `uninstall-core.ps1` and `uninstall.log`, ~12 KB) is
  left by design: the uninstaller exits at once so it can delete itself.
- **X11 GUI tests** cannot run in WSL here (no display); that FAIL is the environment.

## Acknowledgement

Each party: fill your line - the commit you verified and what you ran - and push it to this file on `main`.

| Party | Acknowledged | Commit verified | Date | Notes |
|---|---|---|---|---|
| Sarvam | | | | |
| ChatGPT | | | | |
| Muse | | | | |
| Claude | yes - delivered | `cb4814aa` (head of `claude/windows-linker`) | 2026-10-21 | real Windows 11 Pro 10.0.26300 + WSL Ubuntu |
