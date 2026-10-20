# Round 81 — WS1 installer payload (owner-visible, first)

**Actual rebuilt Sutram-Setup.exe and payload SHA-256: NOT_PRODUCED / NOT_RUN.** This host has neither NASM nor PowerShell. Direct GitHub clone still cannot resolve github.com; no native Windows build/installation was executed. Do not present the current committed installer (unchanged old blob) as rebuilt.

## Current-source facts actually verified

At initial snapshot main v207 commit `465c202f4455468c326cd3c0ad45dad98a584cf4`: all **15/15** source pins in `tools/r69_build.lock.json` matched actual Git blobs, including `src/r11_sandesh.inc`. A later snapshot v208 `4b7d53122898a26733e3b67f521ad450545c5468` also matched **15/15**. Current accepted compiler source `src/sutram_compiler.asm` blob `8625095aa53027bbaf4eef29e7afe76e525d1008` still declares `msg_version db "Sutram 1.0 (v182)..."`, while `docs/CHANGELOG.md` top declares **v208**. Build-input identity is not user-visible release version consistency.

## Substantive R81 development

Extended existing [draft PR #47](https://github.com/dap2810/Sutram/pull/47) on `review/r80-source-bound-installer-20261020`:
- `tools/r81_version_gate.py` — **read-only, fail-closed packaging preflight** verifying exactly one canonical assembler `msg_version` and equality with first `## vNNN` changelog release heading. Rejects missing/ambiguous versions, detects symlink input, emits structured PASS/FAIL JSON with source SHA-256 and no false native-execution claim; no download, privilege, compiler rebuild or golden rewrite.
- `tests/r81/test_version_gate.py` — 11 tests: current-match, v182→v207 mismatch, older release, missing changelog/banner, duplicate declaration, comment/non-banner exclusion, real temporary fixture files and hashes, symlink refusal, and **installer invokes gate BEFORE compile**.
- `windows/native-installer/build-installer.ps1` — invokes preflight before `r69_build.py`. The previous Round 80 builder still builds fresh canonical compiler, verifies actual embedded ZIP/hash, links/self-tests candidate before replacing old setup.

**Executed locally:** Round 80 artifact/source-order suite **29/29 PASS** and R81 suite **11/11 PASS** (40 total). An initial pre-existing R80 test rejected the term `msg_version` in a newly added comment; the comment was corrected to `assembly banner` and **both full suites reran green**. No R80 verification logic relaxed or test disabled. GitHub readback blobs match exact locally tested bytes:
- `tools/r81_version_gate.py` Git blob `9f064f8ff41d64485235e7e379b3e28ac2dca27d`, SHA-256 `13ef3e910ba698e671de8394da142279afad3c6d5e745fdd95ddcfcd370faa82`.
- `tests/r81/test_version_gate.py` blob `bd60cd5850af68673c0bbd78de69a6f35810ed11`, SHA-256 `a0c674f8e1d5d502a8d9f25e1726596cad109986a26e8d35cbe9424a55535230`.
- `windows/native-installer/build-installer.ps1` blob `be1193627c4897e0593561125653d44a95f2faaa`, SHA-256 `30efe197ea490692581878e23991b8f8f5f6a8ea72f57950e37536c368b81ec6`.

## Raw current-banner reproduction — NOT a full local repo
The latest two version declarations were inspected through GitHub at v208, then reproduced in local **two-line test snippets** (not full source/changelog). Command:
`python3 tools/r81_version_gate.py --repo current_snapshot --report evidence/current-snapshot-reproduction.json`
Exit **2**, actual stdout:
```json
{
  "project_version": "v208",
  "compiler_banner_version": "v182",
  "status": "FAIL",
  "reason": "STALE COMPILER VERSION: do not package an installer until the accepted NASM source is rebuilt, reviewed and re-pinned",
  "compiler_source_sha256": "9065e2c896d36f28bd73f74b82af3759baa92b8bc5f6bd49ed407101cef7a845",
  "changelog_sha256": "878b03b7e1e3b6bd87587a0afef3e86d069ddfa7908b446aa98760786de74181",
  "gate": "source_release_banner_only",
  "native_binary_executed": false
}
```
The two SHA-256 values above are of **local reduced snippets**, NOT the current GitHub files.

## Important current Sarvam policy collision

In v208 Sarvam **independently added `tools/version_gate.py` to `gates.sh`**, with a **NOTE rather than a FAIL** when the source banner lags the changelog by more than five versions. This is an intentional general-development policy: compiler source versions may lag development commits without blocking every gate. The R81 guard deliberately imposes the **stricter policy only at installer packaging/release time**, since the installed banner is the first owner-visible line. **Sarvam/Claude must explicitly review and accept/reject that stricter policy before merge.** Do not override the general gate or auto-bump the compiler source/lock. No compiler edits were made.

## Required native acceptance
On a reviewed branch checkout containing PR #47:
```powershell
python -m unittest discover -s tests/r80 -p 'test_*.py' -v
python -m unittest discover -s tests/r81 -p 'test_*.py' -v
python tools/r81_version_gate.py --repo .
powershell -NoProfile -File windows\build-windows-setup.ps1
Get-FileHash -Algorithm SHA256 .\Sutram-Setup.exe
.\Sutram-Setup.exe --self-test
powershell -NoProfile -File tools\accept-windows.ps1
```
Current version gate should **refuse** until Claude's approved compiler banner/source lock change (and Sarvam policy approval), after which repeat from clean checkout, preserve actual `Sutram-Setup.evidence.json` and record newly built payload/compiler/setup SHA-256 and installed `--version` stdout. No elevated builds, no automatic tool installation, no hidden golden rewrite.

**STATUS:** source identity 15/15 PASS; local verifier/preflight fixture tests 40/40 PASS; current version drift confirmed by remote source; actual compiler assembly, new setup and Windows lifecycle **NOT_RUN**.
