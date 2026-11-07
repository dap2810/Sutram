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

The scripts require Windows PowerShell 5.1. They are unsigned. Since v306 (R130) the
wizard starts them with `-NoProfile -NonInteractive -ExecutionPolicy Bypass`, which sets
the policy for that one PowerShell process only: the machine's and user's settings are
not changed, and a Restricted or AllSigned local setting does not stop them. An execution
policy set by Group Policy (MachinePolicy or UserPolicy) takes precedence over the process
setting, so on a machine managed that way the scripts are still refused and the wizard
reports the failure. Signing the scripts is the remaining step for such machines.
End users need no NASM, linker or Python.

An installation is a journaled transaction (R134, after ChatGPT R207). A folder beside the
installation, on the same volume (`<folder>.sutram-transaction`), holds a journal that is
written through to disk before anything in the installation changes, the staged files (each
logged START and DONE, and checked by hash) and backups of the files it replaces. Files reach
the installation only by a rename, so none is ever half-written. Running the installer again
after a stop finishes the transaction from its journal. A file that is not what the installer
wrote is never replaced: such files are listed with a way out, and nothing changes. The
transaction folder is removed once the installation is complete; uninstall leaves an
unfinished one in place, because its backups may be the only copy of the previous installation.

Staging reuses a target only when its current SHA-256 matches the incoming payload.
A late retry after all files were published therefore logs `Already installed` for
every payload file and creates no staging copies. Publication rechecks each target;
if a reused file changed or disappeared, the run stops before moving it or its backup.
Payload extraction/hash verification still runs. User edits remain protected by the
ownership checks; an unchanged file does not need a replacement copy to finish metadata.

Both Windows and Linux builders normalize declared UTF-8 documentation/fixture text
to LF before hashing and use the same manifest path order/newlines. This also handles
older checkouts that still contain CRLF. Executables and icons are copied unchanged.

Developer-only verification: install-core.ps1 accepts -VerifyOnly. It extracts to
TEMP, checks every payload hash and starts compiler --version/--help, then exits
before creating an installation or changing Windows integration.
