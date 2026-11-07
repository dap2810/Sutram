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

An installation that stops part-way (R133: a hang, a closed window, a machine that
slept) leaves `payload.pending.sha256` in the folder, written before any other change.
Running the installer again finishes it: files that match the previous manifest, the
pending one, or the new payload are the installer's own and are replaced; a file that
matches none of them is refused as changed since installation. Each file is named in the
log before it is copied, and copied under `<name>.sutram-partial` first, so a stop never
leaves a half-written file under the real name.

Developer-only verification: install-core.ps1 accepts -VerifyOnly. It extracts to
TEMP, checks every payload hash and starts compiler --version/--help, then exits
before creating an installation or changing Windows integration.

The v307 repair candidate appends logs with an explicit shared write handle,
so a live read-only log observer does not make Windows PowerShell 5.1 fail.
Identical payload files are retained; changed files use the OS replacement
operation after staging, while new files are moved into place. Ownership checks
and the pending manifest still apply, and replacement failures stop installation.
The builder normalizes known UTF-8 documentation and example-output text to LF
before hashing. This avoids replacing unchanged files solely because one build
was made from a Windows CRLF checkout. Native tests are still required: these
changes cannot make an externally suspended wizard service its timeout.
