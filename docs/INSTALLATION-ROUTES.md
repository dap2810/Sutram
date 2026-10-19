# Installation routes and release-acceptance boundary

This is the current installation entrypoint. Historical release notes and
round reports describe their own snapshots; they do not certify a newly built
installer. The clean-project review examined source metadata and selected
files at `0482bf6a979fcd1a8e1a6f55412d0cc25bb7cf1f` on 2026-10-15.

## Windows

The intended supported route is a native, per-user Windows package: program
files under `%LOCALAPPDATA%\Programs\Sutram`, current-user PATH and shortcuts,
and HKCU uninstall registration. No administrator prompt, HKLM change, system
PATH change or security-policy bypass is permitted. This is a release contract;
no installer was executed during this clean-source review.

For an independently accepted portable package, run `sutram.exe` directly from
a user-owned folder and keep its supporting files together. A portable package
does not need PATH registration. The source checkout and a packaged distribution
are different layouts; a script mentioned in old distribution notes is not
necessarily a root-level patra in this repository.

### Source routes that must not be confused

- `windows/native-installer/` contains the native launcher/installer sources and
  `install-core.ps1` / `uninstall-core.ps1`. The reviewed installation core uses
  `Set-UserPathEntry` and the current-user registry. The actual launcher, payload,
  entrypoint, privilege behavior and uninstall safety still need package-level
  verification on Windows.
- `windows/sutram-installer.nsi` is a legacy NSIS/WSL-era route. It explicitly
  requests administrator execution, uses Program Files and HKLM, and describes
  a WSL shell. It is incompatible with the present least-privilege/native-Windows
  contract. Do not select it to obtain a nominally successful build.
- `windows/BUILD-WINDOWS-SETUP.cmd` now invokes the coordinated NASM build chain.
  Preflight validates the repo-relative manifest and refuses missing, modified,
  duplicate or unmanifested inputs. The compiler and GUI use their R68/R67 entrypoints.
- `windows/windows-build-integrity.sha256` covers current build and payload inputs.
  Review source changes before explicitly regenerating it with
  `python tools/update_windows_manifest.py`; never auto-refresh it during a build.

The Windows delivery includes real compiler/GUI logs and an embedded-payload
installer self-test. Full install/uninstall integration remains unverified.
PowerShell policies that block unsigned scripts remain a release blocker for
zero-configuration installation. Use the delivery test plan on an isolated Windows
account or VM; do not weaken security settings.

## Linux

The checkout supplies the pure-NASM compiler and Linux IDE sources, but no
root-level `install.sh` or `books/` directory. Run a source build from repository
root, preserving the reviewed include files:

```sh
nasm -f elf64 -I. src/sutram_compiler.asm -o sutram.o
ld -o sutram_compiler sutram.o
./sutram_compiler examples/01_hello.sm hello.bin
./hello.bin
```

These are maintainer build commands, not commands executed by the clean review:
NASM was unavailable in that environment. A packaged installer may only be
claimed when the specific archive and installation behavior have been verified.
No Linux installer was produced by this audit. macOS packaging is not validated.

## Books and counts

The six language-edition books are `docs/sutram-book-english.html`,
`docs/sutram-book-hindi.html`, `docs/sutram-book-sanskrit.html`,
`docs/sutram-book-tamil.html`, `docs/sutram-book-telugu.html`, and
`docs/sutram-book-gujarati.html`. They are not in a root `books/` folder.

The example inventory is distinct from the executable regression count, and a
case with no accepted expectation is not a passing case. Current introductory
guides avoid duplicating an unverified package example count. Keep historical
CHANGELOG figures intact. Report fresh gate totals alongside the exact source
commit and commands rather than changing a number to make a check agree.

## Windows acceptance still required

Record the exact source commit, package SHA-256, OS build, normal-user account
status and command/log evidence. Verify compiler startup, generated PE execution,
IDE open/edit/save/run/close/reopen, native-script rendering and caret behavior,
installation/PATH/shortcuts, cancelled installation, and uninstallation without
removing user files or unrelated PATH entries. An MZ header, successful link, or
resource self-test alone does not establish any of these user-visible results.

Keep operating-system protections enabled. Investigate antivirus/policy blocks
with the maintainer; neither an unsigned executable nor a matching checksum is
by itself evidence that running it is safe.
