# Round report — Guided Split wizard installer (`sutram_wizard.asm`)

Date: 2026-10-09 (UTC) · From: Ank (Muse) · Task: user picked the "Guided Split"
layout and asked to start building the setup GUI in that style.

## What was built

New file `windows/native-installer/sutram_wizard.asm` (2640 lines, pure NASM
x86-64 Win32, no CRT, no import libraries):

- Guided Split layout: left sidebar painted in `WM_PAINT` (teal panel, thread
  icon drawn with GDI, सूत्रम् dominant, the Sutram word in the ten
  language-pack scripts smaller beneath it), wizard pages on the right,
  Back / Next / Cancel navigation.
- Pages: Welcome → License (real `LICENSE.txt`, accept-gated Next) →
  Install location (edit + `SHBrowseForFolderW` Browse…) → Components
  (user PATH checkbox default-on, desktop shortcut default-off) →
  Ready (generated summary) → Installing (progress bar, worker thread via
  `CreateThread`, staged `PostMessageW` progress) → Finish (optional
  "Launch Sutram Terminal", which starts `cmd.exe /K` with the install
  `bin` on PATH, mirroring `install-core.ps1`'s terminal shortcut).
- Install engine adapted from `sutram_setup.asm`'s `do_install` (same
  `%TEMP%\Sutram-Setup` staging, same `install-core.ps1` flags); the
  `-AddPath` / `-DesktopShortcut` switches are now driven by the checkboxes
  instead of always-on. `--uninstall` behaves like `sutram_setup.asm`.
  Everything stays per-user, unelevated. No-interactive-desktop fallback
  (single Yes/No dialog) preserved.
- `windows/native-installer/README.md` gained a "Guided Split wizard"
  section documenting the file, its build, and its status.

## What was actually run (commands and real output)

NASM 2.16.03 was built from source (apt was unusable in this environment):

    $HOME/workspace/build-tools/nasm-inst/bin/nasm -v
    NASM version 2.16.03 compiled on Oct  8 2026

Assembly (run from a staging dir holding the `incbin` inputs; `payload.zip`
was a 1024-byte zeroed placeholder — see "not verified"):

    nasm -f win64 windows/native-installer/sutram_wizard.asm -o /tmp/wiz.obj
    → no errors, no warnings; /tmp/wiz.obj 63735 bytes

Link:

    ld -mi386pep --subsystem windows --entry=_start -o Sutram-Setup-Wizard.exe /tmp/wiz.obj
    → no warnings; PE32+ executable (GUI) x86-64, 5 sections, 60612 bytes

Entry-point check: `_start` is a global symbol at `.text`+0x22d5 and the
PE `AddressOfEntryPoint` RVA is 0x32d5 (0x22d5 + `.text` RVA 0x1000) — they
match, and disassembly at `_start` shows the expected prologue.

Bugs found and fixed during this round (all in the new file, none shipped):

1. `win_resolve`'s `.found` block had a duplicated `add r13, rbx` — would
   have corrupted the export-ordinal lookup and broken ALL runtime API
   resolution. Fixed to the single add used by `sutram_setup.asm`.
2. `win_kernel32` (PEB walk) was referenced but never defined — copied from
   `sutram_setup.asm`.
3. `load_one` used `PTR rcx, [rbp-8]` (macro expects a symbol) — changed to
   `mov rcx, [rbp-8]`.
4. `global _start` was missing — the linker's entry default would have been
   wrong.
5. 56 `p_*` API slots were never declared in `.bss` — added.
6. Terminal launch command embedded `\"` escapes NASM rejects — rebuilt the
   command line at runtime from quote-free pieces plus the existing `quote`
   label.

## What was NOT run / not verified

- The executable was **not run on Windows**. There is no Windows machine or
  emulator here. The wizard pages, sidebar painting, Browse dialog, worker
  thread, progress bar, and the full install flow are **unverified** and must
  be exercised on real Windows 10/11 before release.
- `payload.zip` does not exist in the repo (release artifact); the link test
  used a dummy. The real release build must `incbin` the genuine payload,
  scripts, and `LICENSE.txt` from the repo root.
- Sidebar transliterations of "Sutram" (Bengali, Kannada, Malayalam, Odia,
  Punjabi, Tamil, Telugu, Marathi, Hindi) are best-effort and marked
  `VERIFY` in the source — confirm with native speakers. Gujarati uses the
  owner-supplied form સુત્રમ verbatim.

## File hashes (SHA-256)

    897e7ed8ea825f4d01c2138ef3b9c9f852f7dbdf39775cbcab52579245d6bd97  windows/native-installer/sutram_wizard.asm (new)
    945263a8e314ba7d89f5e3798ffa8121ce1be71b7ead1e09cb65ca1857bc105f  windows/native-installer/README.md (modified)

## Diff

`windows/native-installer/README.md`:

```diff
--- a/windows/native-installer/README.md
+++ b/windows/native-installer/README.md
@@ -1,3 +1,36 @@
 # Sutram Native Windows Installer
+
+## Guided Split wizard (`sutram_wizard.asm`)
+
+`sutram_wizard.asm` is a pure-NASM x86-64 Win32 wizard GUI for the installer,
+built in the "Guided Split" layout: a branded left sidebar (project thread
+icon, सूत्रम् dominant, the Sutram word in the ten language-pack scripts
+beneath it) and wizard pages on the right with Back / Next / Cancel.
+
+Pages: Welcome → License → Install location (with Browse…) → Components
+(user PATH, desktop shortcut) → Ready (summary) → Installing (progress bar
+driven by a worker thread) → Finish (optional "Launch Sutram Terminal").
+
+It resolves every Win32 entry point at runtime via the PEB-walk mechanism
+from `sutram_setup.asm` (no import libraries), reuses that file's install
+engine (payload extraction + `install-core.ps1`), and stays per-user and
+unelevated. If no interactive desktop is available it falls back to a single
+confirmation dialog, like `sutram_setup.asm`.
+
+Build (from the repository root):
+
+    nasm -f win64 windows/native-installer/sutram_wizard.asm -o wiz.obj
+    ld -mi386pep --subsystem windows --entry=_start -o Sutram-Setup-Wizard.exe wiz.obj
+
+Requires `payload.zip`, `install-core.ps1`, `uninstall-core.ps1` and
+`LICENSE.txt` in the working directory at assembly time (pulled in with
+`incbin`). `--uninstall` is supported the same way as `sutram_setup.asm`.
+
+Status: assembles and links to a PE32+ GUI executable with NASM 2.16.03
+(zero warnings). Not yet executed on a real Windows machine — the wizard
+pages, sidebar painting and install flow must be verified on Windows
+before release. The sidebar transliterations of "Sutram" are best-effort
+and must be confirmed by native speakers (marked VERIFY in the source).
+
+---
+
+## Original notes
```

`sutram_wizard.asm` is a new 2640-line file (no diff against a previous
version; SHA-256 above).

## Proposed next task

Run `Sutram-Setup-Wizard.exe` (built with the genuine `payload.zip`) on a
real Windows 10/11 machine, walk all seven pages, and report back any visual
or behavioural defects — especially sidebar text rendering (Indic scripts),
the Browse dialog, and the install/finish flow.
