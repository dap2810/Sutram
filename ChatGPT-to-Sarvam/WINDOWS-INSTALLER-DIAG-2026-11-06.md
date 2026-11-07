# Installer diagnostic: failed ownership check masks the earlier copy hang

**Not installed successfully.** Two native, non-elevated attempts using current
main's v305 installer (`99d26a89...`) refuse before copying:

```text
Upgrade would overwrite a user file; preserve it elsewhere first: C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram-link.exe
```

The PowerShell child exits by the ten-second observation on both attempts; it
is still absent at seventy seconds. Its live command line was captured early
on the retry. Enter/Y tests are **not applicable**, not passes: there is no
stuck child. The owner captured the explicit “Sutram setup did not complete”
dialog. The wizard's near-complete progress bar is not a success indication.

Before either attempt, the installed compiler already prints v305, but its hash
differs from the package. The installation has only 137 files. Of 657 current
payload entries, 525 are missing, 10 differ, and 122 match. The existing linker
matches the new package but not the old ownership manifest, triggering the
upgrade guard. Both diagnostic attempts leave installed files and registry/PATH
state unchanged. Uninstall registration is absent; an old uninstaller file exists.

PATH: no Sutram entry in machine scope; the canonical user entry is already at
position 20, unchanged. Source writes only HKCU; these failed attempts did not
reach the PATH update. No UAC prompt was observed. This is not fresh-install
acceptance or proof that the original copy hang is fixed.

[Full diagnosis/table/command line and screenshots](../Windows-to-Sarvam/win-installer-diag-2026-11-06/HANG.md)
· [Installed state](../Windows-to-Sarvam/win-installer-diag-2026-11-06/left-behind.md)
· [PATH before/after](../Windows-to-Sarvam/win-installer-diag-2026-11-06/path-scopes.json)
· [Exact commands](../Windows-to-Sarvam/win-installer-diag-2026-11-06/COMMANDS.md).

The original copy-stage stall remains unisolated because current ownership
metadata refuses retry earlier. Next reproduction needs a disposable clean
standard-user environment or explicitly approved recovery preserving the current
files. No ownership bypass, repair, uninstall, source changes, compiler probes,
or CI run was performed. Please acknowledge this diagnostic result; do not
interpret a working version command or a near-full progress bar as installation
completion.
