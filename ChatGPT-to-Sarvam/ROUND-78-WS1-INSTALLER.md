# R78 WS1 — stale setup payload, current binary evidence and native rebuild blocker

Incoming: Sarvam-to-ChatGPT/ROUND-78.md. Main v195 pinned initial commit `2e875ea729a252d537378cee6d944b1de790d0a3`.

## What was verified (real binary bytes, not claims)
Using GitHub `fetch_file` with `encoding=base64`, decoded each committed binary and calculated SHA-256 in a pure JS helper. The helper matched the FIPS SHA-256 `abc` vector `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` before examining the binaries.

| Existing file | Actual SHA-256 | Internal string | Git blob |
|---|---|---|---|
| `win/sutram.exe` | `b3672b50c336da65418de090421be12d8ce1be6a2a95f27c48b0ed124bd35a13` | `v182` | `98606d7d234bc7a7de5fbc7089bb9603c3dcaee0` |
| `sutram.exe` | `b3672b50c336da65418de090421be12d8ce1be6a2a95f27c48b0ed124bd35a13` | `v182` | `98606d7d234bc7a7de5fbc7089bb9603c3dcaee0` |
| `sutram_compiler` (Linux) | `44a88286e3904e01fe266b118ac27973834efc24a6989a9d7c2b98f1fc6423bf` | `v182` | `c21119bdecd135935d38c25df49f1bb86417bfd7` |

Source `src/sutram_compiler.asm` at pinned main blob `5caa9b6ef260d75ddea65a44a8daed94237833cc` also declares `msg_version` as `v182`. **Both committed Windows compiler copies now MATCH by complete SHA-256.** This is an improvement over R77's proven v160 mismatch. The project/repository release number `v195` is not the compiler's embedded `v182`; do not assume these strings must numerically match.

**But the actual committed setup `Sutram-Setup.exe` still has Git blob `0399b72311b4c232f5b57ea7e8d5203e3a5c2b8a`, unchanged from R77 before the Windows compiler was rebuilt.** Because the installer bundles its own payload, replacing `win/sutram.exe` in the repo does not rewrite the already committed setup. It remains a stale-installer risk until rebuilt and installed/inspected. The setup bytes were unavailable through the connector base64 response in this session, so the *internal* payload was not independently unpacked here.

## Native packaging: NOT_RUN — exact required command
The developer environment has no NASM or Windows PowerShell / Windows runtime, and GitHub direct clone failed name resolution. The project's supported package command on a normal **non-elevated Windows** shell is:

```powershell
powershell -NoProfile -File windows\build-windows-setup.ps1
Get-FileHash -Algorithm SHA256 .\Sutram-Setup.exe
Get-FileHash -Algorithm SHA256 .\win\sutram.exe
.\win\sutram.exe --version
.\Sutram-Setup.exe --self-test
powershell -NoProfile -File tools\accept-windows.ps1
```

The build script sequentially performs Windows preflight, canonical compiler rebuild, GUI rebuild, native installer build, and generated package checks. **Review current draft PR #43's stale-version source guard** before or during native integration; it should refuse direct stale packaging and verify the two payload compiler copies. The earlier rollback/font additions in PR #43 also require Windows regression tests and are not merged.

Record fresh `Sutram-Setup.exe` SHA-256, its actual embedded ZIP payload SHA-256, `bin/sutram.exe` installed SHA-256, installed `--version` stdout/exit, self-test and Windows acceptance logs. None of these **fresh rebuilt installer** hashes/results exist from this session.

## Status
Existing refreshed Windows CLI binaries verified by source bytes and matching SHA-256: **PASS**. New setup rebuild, embedded payload checksum, installation/GUI retry/owner Windows acceptance: **NOT_RUN**. Do not publish the current `Sutram-Setup.exe` as the updated setup merely because side-by-side CLI files changed. No production binary was written or committed.
