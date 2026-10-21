# R80: source-bound installer packaging

This review branch addresses ROUND-80 WS1. It does not implement a compiler, modify diagnostics, install fonts, or change installation/rollback behavior.

## Build change

`windows/native-installer/build-installer.ps1` now requires developer Python as well as existing NASM/GNU ld. It calls the existing canonical `tools/r69_build.py` in Windows/default mode to build a fresh compiler and source-identity JSON into a private work directory. It packages that compiler twice, not the possibly stale checked-in `win/sutram.exe`. It runs compiler/hello smoke checks without matching localized diagnostic wording.

The new `tools/r80_payload_verify.py` compares all current lock inputs with the canonical build report and compiler bytes. It verifies the ZIP's complete manifest and both compiler copies; rejects unsafe paths, case collisions, symlinks, excessive expansion and unmanifested content; then uses actual PE/COFF `blob_payload`, `blob_payload_end` and `hash_payload` symbols to check the final embedded ZIP and hash constant. An appended decoy ZIP does not count. An unstripped PE candidate is required; missing symbols fail closed.

The candidate installer is linked and self-tested before replacing `Sutram-Setup.exe`. An existing setup is retained as `previous-setup.exe` under the work directory. Compiler, ZIP payload, manifest, setup, and source-lock hashes are recorded in `Sutram-Setup.evidence.json`; individual raw compiler build commands remain in the work directory. This is artifact consistency under a trusted local build, not a cryptographic build attestation or a malicious-compiler defense.

## Commands

From a complete checkout of this branch, with existing developer tools:

```text
python -m unittest discover -s tests/r80 -p 'test_*.py' -v
powershell -NoProfile -File windows\build-windows-setup.ps1
```

Do not bypass a source-lock/preflight refusal. Review the relevant source change first. Python is developer-only and is not bundled into the installer. No tools or fonts are downloaded automatically.

After a real Windows build, review `Sutram-Setup.evidence.json`, then perform owner-approved install/upgrade/uninstall acceptance. Compiler hello and setup self-tests are not that acceptance.

## Evidence and limits

Round-80 local run: 29 tests passed, comprising 26 artifact tests (including an actual GNU-binutils-linked AMD64 PE fixture) and three builder source-order tests. No test was skipped. These are not tests of the actual Sutram installer or of PowerShell execution. Native NASM build, PowerShell execution, the current full installer, Windows lifecycle, kosh A/B, whole-repository audit, and true two-Sutram-module linking were NOT_RUN in this session.

Keep this PR draft pending Windows validation. Its builder change supersedes the version-banner-only portion of PR #43; it intentionally does not copy PR #43's separate installation/font changes or modify any accepted compiler source, lock, library or golden.
