# Native Windows installer review build

Build from project root with `powershell -NoProfile -File windows/build-windows-setup.ps1`.
NASM and GNU ld with PE support are developer prerequisites. No tool is installed automatically.
The active launcher is `sutram_wizard.asm`, linked with kernel32 and bcrypt system import libraries.
The legacy C launcher, `sutram_setup.asm`, and NSIS recipe are not used.

The wrapper checks the repo-relative source manifest, builds the R68 compiler and
R67 GUI entrypoints, stages an explicit payload, and embeds the ZIP, two PowerShell
scripts and license with SHA-256 values. `Sutram-Setup.exe --self-test` verifies
those parts without extraction or installation. Hashes detect corruption, not publisher authenticity.

Payload layout: bin/sutram.exe, win/sutram.exe, sutram-ide-gui.exe, assets/sutram.ico,
LICENSE.txt, README.md, lang/, lib/, examples/, docs/. Both compiler directories
also contain lang/ and lib/ so command-line compilation works from another directory.
The GUI expects win/sutram.exe relative to its executable directory.

The guided NASM wizard targets the current user's Programs directory. The scripts
manage user PATH, HKCU registration, .sm association and user shortcuts. Existing
.sm defaults are preserved. Ownership records and content hashes protect user
files during upgrades/uninstall. Install and uninstall integration are still
unverified; see the delivery REPORT and TEST-PLAN before accepting a release.

The scripts require Windows PowerShell 5.1 and obey the current execution policy.
Unsigned scripts will be blocked on Restricted/AllSigned configurations. This is
an unresolved release blocker for the zero-configuration promise. Do not change
security policy to run this review build. End users need no NASM, linker or Python.

Developer-only verification: install-core.ps1 accepts -VerifyOnly. It extracts to
TEMP, checks every payload hash and starts compiler --version/--help, then exits
before creating an installation or changing Windows integration.
