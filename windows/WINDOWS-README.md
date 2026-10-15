# Sutram for Windows — supported native route

The canonical installer and privilege policy is documented once in
[Windows installer security comparison](../docs/R65-LEGACY-NSIS-VS-NATIVE-INSTALLER.md).
That document identifies the shipping builder, output, per-user locations,
legacy NSIS behavior, and required real Windows acceptance.

For a source build, use the existing approved NASM/PE64 linker/MinGW toolchain
in a normal, non-elevated session. From the repository root:

```powershell
powershell.exe -NoProfile -File .\windows\build-windows-setup.ps1
```

The wrapper builds the compiler, builds the GUI with its linked cluster
counter, then calls `windows/native-installer/build-installer.ps1`.
Stop and report policy or build failures. Do not request elevation, bypass
execution policy, install WSL, or build the obsolete administrator NSIS path
as a workaround. End users of an accepted native package do not need the
compiler toolchain or WSL installed separately.

For GUI-only source builds use `windows/gui/build-gui.ps1`; its `-Run` switch
is opt-in. Format/link checks are not a Windows visual or install test.
