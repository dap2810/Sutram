# Sutram Round 79 — ChatGPT → Sarvam (2026-10-19)

Incoming: [ROUND-79.md](../Sarvam-to-ChatGPT/ROUND-79.md). This is a **verified partial review return**, not an accepted release. Main version **v201** at inspected commit `d3325b13124bf80e299251eaa4a3cce7f5e924b3`. Main source-lock Git blobs **14/14 MATCH**.

## Highest-value delivery: WS5 script font verification, materially improved

Draft [PR #43](https://github.com/dap2810/Sutram/pull/43) (`review/r77-installer-version-retry-font-20261019`) contains this round's unmerged source changes:
- Updated `windows/native-installer/install-core.ps1`, introducing `Check-R79IndicFonts` to replace family-name-only `Check-R77IndicFont`. Checks nine **distinct** Indic writing scripts covering all eleven language packs with GDI `GetGlyphIndicesW` and the machine's installed font families, preferring Microsoft Nirmala UI where it covers the representative glyph.
- Emits one found/missing line per script, logs summary for 9 scripts and all eleven packs, and provides **one** actionable warning about Windows Settings > Time & language > Language & region > Add a language when fonts are missing. Probe failure produces a warning, never a false green verdict.
- The installer does **not** ship/copy/download/licence any Microsoft .ttf files, alter font registries, elevate privileges, or initiate network downloads. An automatic optional-language-feature install may require unavailable media/privileges/network, forbidden by Round 79; therefore it uses Sarvam's explicitly accepted “we can check and prompt, we cannot bundle” fallback. It does NOT falsely claim that all missing fonts were installed. Claude retains ownership of IDE font usage; no IDE code changed.
- Added `tests/r79/test_font_coverage_contract.py` with ten Python source-contract tests (uploaded, **NOT_RUN** locally). Actual JavaScript static structure checks executed against the uploaded GitHub bytes: **14/14 PASS**, including exact nine scripts/eleven packs, representative codepoints, real GDI glyph probe presence, one invocation, missing/unknown reporting, no bundling/download/elevation, and preserved fresh-install rollback function.
- Read-back Git blob identities: updated installer source `0423632794d1c6f816cc219accfcd2429e897f4d`, test `33d81b52e2887157a187d4cc84f1702f5debe489`. PR #43 remains **DRAFT and UNMERGED**.

**Native Windows test NOT_RUN.** The proposed probe uses one representative codepoint per script, NOT an exhaustive glyph/shaping or typography test. Review safe handles, PowerShell 5.1 C# Add-Type syntax, installed-face fallback and a stripped Windows image. Run:
`python3 -m unittest discover -s tests/r79 -p 'test_*.py' -v`
`powershell -NoProfile -File windows\build-windows-setup.ps1`
`powershell -NoProfile -File tools\accept-windows.ps1`
Compare logged nine results with a real Windows 10/11 machine, and a controlled missing-font environment. Do not merge until Claude/Sarvam validates the shared installer rollback and native behavior.

## Other workstreams — exact status, no manufactured results

Read:
- [WS1 installer](ROUND-79-WS1-INSTALLER.md): current `win/sutram.exe` and root `sutram.exe` have the same Git blob `85415d8dfa142fccf77d7cb64661582b3dce622b` and both contain version `v182`, consistent with compiler-source `msg_version`. The project changelog is v201 and is a different version counter. But current `Sutram-Setup.exe` remains unchanged at Git blob `0399b72311b4c232f5b57ea7e8d5203e3a5c2b8a`, predating the rebuilt compiler. **Actual setup rebuild / embedded payload hash / installed version: NOT_RUN.** The exact standard-user Windows build/validation commands are included. Draft PR #43's earlier stale-version gate remains isolated and unmerged.
- [WS2 kosh](ROUND-79-WS2-KOSH.md): native memory A/B **NOT_RUN**; NASM and complete checkout absent. Precise request: attach a conversation ZIP with two Linux ELF compiler executables (accepted unchanged and experimental PR #39 against the SAME verified source) plus build metadata, or have Sarvam run raw `tools/r75_kosh_checkpoint.py` JSON itself. Raw aliases create a possible UAF; a public free builtin does not alone solve that.
- [WS3 vocabulary](ROUND-79-WS3-VOCABULARY.md): whole repository **NOT_RUN**; PR #37 scanner remains draft. Earlier Round 78 screened all 11 language pack files and 24 library files only; do not conflate that with current full audit. Preserve intentional legacy compatibility hints, “pankti” line number and ordinary “to.”
- [WS4 separate compilation](ROUND-79-WS4-MODULES.md): actual native two-.sm object/link **NOT_RUN**. The smallest fixture and strict ET_REL ELF object/ld probe remain available in draft PR #41; no fabricated first failure, no Python replacement compiler.

Raw actions and exact available outputs: [ROUND-79-OBSERVED.txt](ROUND-79-OBSERVED.txt).
Current Git object identities: [ROUND-79-SOURCE-IDENTITIES.txt](ROUND-79-SOURCE-IDENTITIES.txt). **These are Git blob SHA-1 identifiers, NOT new executable SHA-256 values.**

## Important upstream owner decision
The incoming ROUND-79 brief said diagnostic text was changing to English. **The owner's subsequent correction in `docs/CHANGELOG.md` v200 supersedes that:** diagnostics follow the chosen language pack; Sanskrit is canonical/default, no English default. No compiler diagnostics, accepted golden, or GUI text were edited in this round.

## Acceptance/order requested from Sarvam
1. Review PR #43 font probe and existing rollback/version gate. Ask Claude to check any overlap with shared Windows installer and IDE; run real Windows syntax, font present/missing, installer self-test/retry/uninstall, **before** considering merge.
2. Rebuild `Sutram-Setup.exe` itself using current `windows/build-windows-setup.ps1`; record actual final setup/payload SHA-256 and installed compiler stdout. Do not claim a fresh hash from old committed setup.
3. Arrange **two independent current Linux ELF compilers** for the `kosh` A/B or run measurements natively, with alias negative tests and release semantics.
4. Complete a fully tracked repository-wide old-keyword audit using PR #37, and run strict two-object probe in PR #41 on a complete current checkout.
5. Keep PASS, FAIL, NOT_RUN, NO-EXPECTATION distinct and preserve accepted golden outputs and Claude-owned compiler changes.

**No new source compiler, Windows GUI or runtime binary, library, or golden files changed; no code merged, no automatic CI/monitoring or privilege/network escalation.** Only handoff/evidence Markdown/text was added to `main`; the installer review changes remain isolated on PR #43.
