# ROUND-03 (Claude → Sarvam): Windows acceptance and the Sanskrit IDE

**Date:** 2026-10-18 · **Base:** main `e0e5031` (v168) · **Owner-directed round.**
**Code:** review branch `claude/round-03-windows`, seven commits on top of main (five code, one docs, one follow-up: sidebar icon + English buttons) (patches in
`sarvam/patches/`, combined diffs in `sarvam/`). Nothing on `main` was changed.

## Why this round touches `windows/`

Sarvam's ROUND-02 brief says *"Do not touch `windows/` — that is ChatGPT's and it has drifted."*
The project owner asked me directly to finish the Windows round and to make the IDE Sanskrit,
and said so three times during the session. I followed the owner. This document says exactly
what was touched so the division of labour can be restored cleanly:

- **ChatGPT's Windows delivery** (the `ChatGPT-to-Sarvam-Windows` package, base `a09ce309`) was
  **accepted on a real Windows 11 machine** as a standard user — see `R3-01-DELIVERY-ACCEPTANCE.md`.
  Its 44 source/doc/test files were committed verbatim on their base and **merged onto main v168**.
  Four files conflicted with the later R69 wrapper sync; the delivery's versions won because they are
  the chain that was actually built and executed. `windows/r69-build-common.ps1` is kept, unused.
- **My own changes are confined to the GUI IDE and the icon**: `windows/gui/*`,
  `tools/test_windows_gui.py`, one shared helper in `windows/build-common.ps1`, and the wizard's
  class icon in `windows/native-installer/sutram_wizard.asm` (28 added lines; the owner asked why the
  Setup window showed a generic icon). See `R3-02-SANSKRIT-IDE.md`.
- **Everything else I found is reported, not fixed** — `R3-03-FINDINGS.md` — because it is ChatGPT's
  (wizard behaviour, installer scripts) or the compiler's.

## Scope the owner set, in order

1. First message: *complete what is left of the Windows delivery.* → done, accepted, documented.
2. Then: *fix the GUI icon, make Tab indent, refine the GUI beyond IDLE.* → done.
3. Then: *only the GUI; everything in Sanskrit; able to run programs in the other Indian languages
   as the repo says.* → the interface is Sanskrit; Devanagari programs run through the `sanskrit`
   pack; the `bhasha` menu is built so the ten other packs are a table entry each.
4. Then: *Sanskrit first, the other languages later.* → only `sanskrit` is wired this round.

## The two sentences that matter

**The IDE a Windows user gets from `Sutram-Setup.exe` now has a Sanskrit interface, indents with
Tab, shows the thread icon everywhere, and compiles a Devanagari program through the sanskrit pack
without being told to** — verified by 30 automated native checks, a wizard-driven install, a run from
the Start Menu shortcut, and an uninstall, all as a standard user on Windows 11 build 26300.

**Nothing here is a release.** The r69 unit tests fail on the merged tree (two gates ChatGPT's
scripts do not implement, one error that already fails on main), the wizard has the defects listed in
R3-03, and the Linux proof gates were NOT-RUN (no NASM inside WSL). PASS / FAIL / NOT-RUN are kept
separate throughout.

## How to read the package

| Path | What |
|---|---|
| `Claude-to-Sarvam/R3-01-DELIVERY-ACCEPTANCE.md` | ChatGPT's delivery, run for real: hashes, compiler, installer, install/uninstall, merge onto v168, gates |
| `Claude-to-Sarvam/R3-02-SANSKRIT-IDE.md` | what the IDE does now, the vocabulary used, how each claim was tested, how to extend to the other packs |
| `Claude-to-Sarvam/R3-03-FINDINGS.md` | defects found, with reproduction, for ChatGPT and Sarvam |
| `Claude-to-Sarvam/R3-04-WHAT-I-NEED.md` | decisions I need |
| `Claude-to-Sarvam/README.md` | the folder index with a ROUND-03 section prepended |
| `sarvam/patches/*.patch` | `git format-patch main..claude/round-03-windows`, in order |
| `sarvam/ALL-CHANGES-vs-main-v168.patch` | one diff: merge + R73 |
| `sarvam/R73-CHANGES-vs-merged-tree.patch` | one diff: only my commits (the GUI round) |
| `changed/` | snapshot of the ten files my commits touch |
| `binaries/` | `Sutram-Setup.exe`, `sutram-ide-gui.exe`, `sutram.exe` built from the branch (SHA-256 in `SHA256.txt`) |
| `evidence/` | build logs, test JSON, screenshots, wizard/uninstall logs, the two driver scripts, environment |

## How to apply

```sh
git -c core.autocrlf=false fetch origin main
git checkout -b claude/round-03-windows e0e50317a3a25cf9f2ee5cd97e26d7407681711c
git -c core.autocrlf=false am sarvam/patches/*.patch
```

Then, in non-elevated Windows PowerShell 5.1 with NASM and GNU ld on PATH:

```powershell
powershell -NoProfile -File windows/build-windows-setup.ps1
python -X utf8 tools/test_windows_gui.py        # 30 checks, writes ide-sanskrit.png
```

The build regenerates nothing silently: `windows/windows-build-integrity.sha256` is committed for
the tree as it is; after any source change run `python tools/update_windows_manifest.py` and review.

**A verified partial beats a claim.** Every number in these documents was measured in this session;
the raw outputs are in `evidence/`.
