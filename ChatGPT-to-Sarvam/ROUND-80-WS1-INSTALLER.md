# ROUND-80 WS1 — installer payload

Date: 2026-10-20. Reviewed main v204 snapshot `068afb2673bd48885ec71279ac1ca7342d8d082f`. Review: draft PR #47, branch `review/r80-source-bound-installer-20261020`.

## Delivered source fix

The current main installer builder copies the existing `win/sutram.exe` into its payload. The earlier PR #43 guard uses version text, which cannot establish exact build identity when different compilers share the same banner. R80 replaces that dependency with a new canonical build and byte-level verification.

`windows/native-installer/build-installer.ps1` now:
1. Requires existing developer Python, NASM and GNU ld; refuses an elevated build; downloads nothing.
2. Runs the existing `tools/r69_build.py --target windows` into a fresh private work directory, preserving its source-pin/include checks and raw build JSON. It does not substitute a different compiler frontend.
3. Packages those freshly built compiler bytes as both `bin/sutram.exe` and `win/sutram.exe`. It runs the compiler version command and known hello program without matching translated diagnostic prose.
4. Runs `tools/r80_payload_verify.py` against the current source lock, canonical build report, compiler, ZIP manifest and both payload compiler copies.
5. Builds an installer candidate rather than immediately overwriting the published setup. After the candidate self-test, the verifier resolves actual PE/COFF `blob_payload`, `blob_payload_end` and `hash_payload` symbols to check the embedded ZIP and hash constant. An appended new ZIP next to an old embedded ZIP does not count.
6. Replaces the published executable only after those checks and retains its previous version in the work directory. Reports payload/compiler/setup SHA-256 in `Sutram-Setup.evidence.json` and prints them separately.

The verifier is read-only. It checks complete manifest membership, every file hash, duplicate/case-colliding/unsafe paths, symlinks, file-directory conflicts, and archive expansion limits. Source and compiler identities are checked again before returning. This is artifact consistency under a trusted local build, not a signed attestation or defense against a malicious toolchain. It requires an unstripped PE candidate; missing symbol proof fails closed.

The inspected R11 lock contains **15 pins**, including `src/r11_sandesh.inc`, not the former 14. The verifier derives the set from the lock rather than hardcoding a count. No production lock was changed, and no full current-repository source-pin execution is claimed here.

## Actually executed

Command from `/mnt/data/sutram_r80`:

```text
python -m unittest discover -s tests/r80 -p 'test_*.py' -v
```

Final output: `Ran 29 tests in 0.083s`, `OK`, exit 0, zero skips. Breakdown: 26 artifact tests, including a genuinely GNU-binutils-linked PE fixture, and three builder source-order tests. The exact four uploaded code/test files match locally tested bytes by Git blob SHA. Full test names and assembler/linker output are in ROUND-80-OBSERVED.txt.

The test PEs contain fixture payloads, not Sutram compilers. No test executable was presented as an actual rebuilt Sutram installer.

## Native build not completed

**Actual current Sutram-Setup.exe rebuild: NOT_RUN. Actual new installer payload SHA-256: NOT PRODUCED.** NASM and PowerShell are absent in this Linux execution environment; GitHub clone/download routes tested here failed. The committed setup still resolves to blob `0399b72311b4c232f5b57ea7e8d5203e3a5c2b8a`; its bytes were not unpacked locally.

On a complete PR #47 checkout in a standard-user Windows shell, with existing developer tools:

```text
python -m unittest discover -s tests/r80 -p 'test_*.py' -v
powershell -NoProfile -File windows\build-windows-setup.ps1
```

Do not bypass preflight or source-lock refusals. Review `Sutram-Setup.evidence.json` and the retained `build/windows/setup-*/compiler-build.json`, then run owner-approved install/upgrade/uninstall acceptance. Confirm both installed compiler copies match the reported hash and pack diagnostics work. Compiler/hello/setup smoke tests are not full lifecycle acceptance.

This draft changes only the builder, new verifier, tests and documentation. It supersedes the version-banner-only packaging portion of PR #43, not its separate install-core/rollback/font work. Keep PR #47 draft until native Windows execution and independent review.
