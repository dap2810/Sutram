# Sutram Round 79 WS1 — installer payload freshness

**Status: existing compiler-source and binary identities checked; new installer build NOT_RUN.**

Live main snapshot: v201 commit `d3325b13124bf80e299251eaa4a3cce7f5e924b3`. Compiler source blob `5ade34ed0287609b8f5d7e4f12873b7978479ac4`; R69 build lock `f8da5ddb248a7f009f9909074b1a9b86780940c6`; all **14/14** tracked source pins match the exact recursive main Git tree.

Actual current checked-in binaries inspected from GitHub base64 bytes:
- `win/sutram.exe`: **188,318 bytes**, Git blob `85415d8dfa142fccf77d7cb64661582b3dce622b`, embedded `v182`
- `sutram.exe`: **188,318 bytes**, **same Git blob** and `v182`
- `sutram_compiler` Linux: **202,320 bytes**, blob `432d3d9d539e02d7a20aa91c8ef4a3c67c834679`, embedded `v182`

The project version v201 is the project release history, not automatically the internal compiler banner, which remains v182 in current source. The previously stale `win/sutram.exe` was rebuilt; its checked-in bytes now match `sutram.exe`. But the committed **`Sutram-Setup.exe` is still blob `0399b72311b4c232f5b57ea7e8d5203e3a5c2b8a`**, unchanged since Round 77. It contains an embedded payload and does not magically update when compiler binaries in the repository change. **Its embedded payload has not been extracted/rehashed or rebuilt in this session.**

Existing [draft PR #43](https://github.com/dap2810/Sutram/pull/43) adds a source-vs-compiler `--version` guard and checks BOTH staged compiler file hashes before packaging. It is not merged. Do not merge shared Windows files without Claude/Sarvam review.

**New `Sutram-Setup.exe` payload hash: NOT PRODUCED.** No PowerShell/NASM environment here; do not label existing standalone compiler blobs as the rebuilt setup hash.

Exact standard-user Windows build and checks:
```powershell
powershell -NoProfile -File windows\build-windows-setup.ps1
Get-FileHash -Algorithm SHA256 .\Sutram-Setup.exe
Get-FileHash -Algorithm SHA256 .\win\sutram.exe
.\win\sutram.exe --version
.\Sutram-Setup.exe --self-test
powershell -NoProfile -File tools\accept-windows.ps1
```

Report actual ZIP payload SHA-256, installer SHA-256, installed `bin\sutram.exe` SHA-256, installer self-test and installed stdout/exit separately. Failing an installed-version check should block release.
