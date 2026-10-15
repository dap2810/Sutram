# Sutram installation routes — canonical source statement

This is the single maintained installation-route statement. It supersedes
installation claims in the earlier R65/R66/R67 comparison and old Windows
guides. Historical round reports remain historical evidence, not current setup
instructions. **A source build path is not proof that a shipped binary was
built from that source or accepted on the target OS.**

## OS and artifact route

| OS | Route represented by the reviewed source | Acceptance boundary |
|---|---|---|
| Windows x64 | Native per-user wizard built by `windows/native-installer/build-installer.ps1`; output `windows/native-installer/output/Sutram-Setup-0.1.0-native-x64.exe`. A published copy may be named `Sutram-Setup.exe`. A coherent portable directory is an alternative. | Requires real standard-user install/uninstall and GUI acceptance. No claim that a particular existing EXE is current or tested. |
| Linux x86-64 | Native ELF compiler built from the repository source; run it and the generated ELF directly. The Linux IDE is separate from the Windows GUI. | The root `install.sh` advertised by the old README was absent at this review's pinned root tree. No current Linux installer/package is certified here. Do not invent a download or invoke a missing script. |
| macOS / other targets | No verified native installer route established by this review. | Do not describe Windows PE or Linux ELF outputs as a macOS package. |

For the accepted compiler, use the repository root and its includes:

```sh
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/sutram.o
ld -o /tmp/sutram_compiler /tmp/sutram.o
```

Experimental R68 diagnostics require the separately checked entry described in
`R68-SOURCE-REVIEW.md`; that source-review entry is NOT a new public installer.
No toolchain is auto-downloaded by this document.

## Supported Windows scope versus legacy NSIS

The supported source path is **`windows/native-installer/`**, not the legacy
`windows/sutram-installer.nsi`. Its intended installation directory is
`%LOCALAPPDATA%\Programs\Sutram`. Uninstall metadata is under HKCU, optional PATH
integration is per-user, and shortcuts are current-user Start Menu/Desktop.
Do not request UAC, use Program Files as the default, write HKLM, or alter another
user's environment. Built-in Windows PowerShell is used by packaging scripts;
that is distinct from requiring an end-user development toolchain.

The legacy NSIS file requests `RequestExecutionLevel admin`, installs under
`$PROGRAMFILES64`, uses HKLM installation/uninstall entries, modifies system PATH
through `EnVar::SetHKLM`, and writes HKCR file associations. Its old payload and
finish-page text refer to a Linux/WSL compiler. That is a retained **legacy path**,
not the supported least-privilege route or a fallback when policy blocks setup.
Do not run it merely because an old guide recommends it.

## Current wrapper discrepancy

At pinned main `a700bfd21a6af1c6d5efc275df1963585615ef67`,
`windows/build-windows-setup.ps1` still has Git blob
`f51f3accf46eb59d6fe37a21dad7eea73ddd16a6`. It references the nonexistent
`windows-installer-native` name, includes explicit execution-policy bypass flags,
and prints an obsolete transitional-ELF message. R67 supplied a corrected wrapper
on its review branch, but that corrected file is NOT the one observed on this
pinned main. This documentation does not silently replace or execute it.

For an authorized developer build, use the actual GUI builder
`windows/gui/build-gui.ps1` and the actual `windows/native-installer/build-installer.ps1`
directly, from a verified checkout with required compiler/GUI/icon inputs. Do not
use the stale wrapper as an acceptance step. Before a release, reconcile the
wrapper to reviewed source and re-run the relevant release gates. The GUI builder
on this pinned main does reference the three R67 cluster objects.

## Security and verification

Use only verified artifacts in a writable current-user directory. When security
software or organization policy blocks execution, record the message and consult
the appropriate administrator; do not disable or bypass protection. A new unsigned
PE header or a hash check alone does not establish trust or GUI correctness.

Record source commit and binary hashes. Verify overlay/payload integrity, then
perform normal-user install, PATH/shortcut/uninstall checks and actual program
execution. For GUI opening/closing and the counter, use
`R68-WINDOWS-GUI-CHECKLIST.md`. No installer, registry mutation, elevation or
Windows GUI execution was performed during this documentation work.
