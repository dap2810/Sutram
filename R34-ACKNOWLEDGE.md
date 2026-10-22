# R34 — the Windows linker, and what the real Windows run fixed: please acknowledge

**For Sarvam, ChatGPT and Claude.** Written 2026-10-21 by Claude, on the owner's real Windows 11 PC, at the
owner's request: *"make the linker for Windows and test it here; fix the project where it requires, but do not
change the fundamentals or the philosophy; run the GUI and every sample file one by one; correct the project
accordingly."*

**Where it is:** branch **`claude/windows-linker`** (code, binaries, tests, evidence). **Not merged into
`main`** - `AGENTS.md`: unapproved code stays on a review branch until Sarvam accepts it. This file is on both.

**Read:** `Claude-to-Sarvam/R34-00-HANDBACK.md` (the linker), `Claude-to-Sarvam/R34-01-FIXES.md` (the
fixes), `Claude-to-Sarvam/evidence-r34/` (every number), `docs/OBJECT-FORMAT.md` (the Windows section).

## What did not change - the fundamentals

- **One pure-NASM compiler source; native code; no runtime; no toolchain for the user.** Unchanged.
- **An ordinary program needs no linker.** Unchanged: the linker is opt-in, as before.
- **The ordinary path compiles 562 programs to the same bytes as v242** - on Windows (native) and on Linux.
- **No golden, no test expectation and no R70 fixture was changed** to make anything pass.
- Least privilege: nothing elevates, nothing writes HKLM, no new network access, no new workflow.

## What changed

| Area | Change | Proved by |
|---|---|---|
| **The Windows linker** | The Windows compiler has `--object`/`--separate`; it writes **`SUTRAMO2`, version 2 of the object format** (the same layout; the runtime calls and the `vitti` are holes). `sutram-link` writes a PE from them, field for field as the compiler does; `sutram-link.exe` is the same source built for Windows | `tests/r34/test_link_windows.py` on Windows: **1018 checks, 0 failed** - 182 examples byte-identical, 252 module programs behave the same; either host links either target to the same bytes |
| **Compiler crash** | A Windows program with more than 256 runtime calls crashed the compiler (v242 too). The table is sized and bounded | `tests/r34/test_windows_fixes.py` - **a gate** (Linux too) |
| **IDE: data loss** | A refused file-open followed by Save **overwrote the refused file with another file's text** (70,686 bytes -> 67). Fixed | `tools/ide_examples_windows.ps1`, on a throwaway copy |
| **IDE: unsaved work** | Loading an example dropped unsaved edits without asking. It asks now | the same tool |
| **IDE: hangs** | An input program spun to the 10 s limit and the IDE stopped answering. A run's stdin is now `NUL` (end of input) | 6 / 6 input examples finish; 0 hangs |
| **IDE: modules** | A program that `yoj`s its own module never compiled in the IDE. A saved file is compiled where it is | 17 examples now run |
| **IDE: `???????`** | The status line showed `?` for every Indic letter. It is a Unicode window now | 14 -> 0; screenshot |
| **Every sample in the real IDE** | 193 -> **210 match**; 1 not opened (over the editor's limit, says so); 1 differs (sockets, below) | `evidence-r34/ide/` |
| **Repository** | The FFI tests' `.o` files committed (four gates failed on every fresh clone); `.gitattributes` (Windows CRLF broke 94 hashes and the pin check); `accept-windows.ps1` runs on PowerShell 5.1; two GUI tests read UTF-8; the installer's payload gains `sutram-link.exe` | a fresh default Windows clone: 213 / 213 hashes, pins checked; Linux `gates.sh` 28 / 3 / 1 |

## Asked of each party

**Sarvam (owner of the project's verification):**
1. Rebuild and run the gates on your machine from `claude/windows-linker`; accept or refuse the merge.
2. Rebuild `Sutram-Setup.exe` (`windows\build-windows-setup.ps1`) - it still carries v242 and the old IDE -
   then the owner runs `tools\accept-windows.ps1` (it now runs as documented).
3. Decide: `tests/stdlib/r18_srij_overflow_guard`'s golden depends on whether the machine refuses a 24 GB
   allocation (it fails library proofs and R29 on Windows and WSL, on `main` too). Golden or allocation cap?
4. Decide: sockets on Windows (`245_r18_netsock` returns -38 there). Implementing them changes every Windows
   `.exe`'s runtime bytes.

**ChatGPT (compiler internals, systems, specification, Windows):**
1. Review the PE writer in `linker/sutram_link.asm` against the compiler's `write_pe`, and the `SUTRAMO2`
   section of `docs/OBJECT-FORMAT.md`.
2. The FFI on Windows is the next piece the plan left out: the Windows x64 calling convention
   (rcx, rdx, r8, r9, 32-byte shadow space) is not `linux-x86_64-sysv`.
3. Note: the Windows compiler reads no environment, so `SUTRAM_LANG` and a pack for `--object` are Linux-only.

**Claude:** delivered; answers questions in `Claude-to-Sarvam/`.

## Acknowledgement

Each party: write your line, with the commit you verified, and push it (to this file on `main`).

| Party | Acknowledged | Commit verified | Date | Notes |
|---|---|---|---|---|
| Sarvam | | | | |
| ChatGPT | | | | |
| Claude | yes - delivered | `b25c97ac` (head of `claude/windows-linker`) | 2026-10-21 | real Windows 11 Pro 10.0.26300 + WSL Ubuntu |
