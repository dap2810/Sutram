# Sutram Round 79 WS5 — ensure all supported Indic-script fonts are usable

## Source implementation completed on isolated draft PR #43
Upgraded `windows/native-installer/install-core.ps1` from a weak installed-family-only `Check-R77IndicFont` to `Check-R79IndicFonts`, called **exactly once after payload verification**, also in verify-only mode (without displaying its modal warning there). Uses an installed-font-family lookup and Windows GDI `CreateCompatibleDC / CreateFontW / GetGlyphIndicesW` with the **GGI_MARK_NONEXISTING_GLYPHS** flag to test an actual representative consonant for each script in each available candidate face. The check reports per-script family chosen or missing and prints a summary.

**All eleven Sutram language packs map to nine unique writing scripts:**
- Devanagari U+0915 — Sanskrit, Hindi, Marathi
- Gujarati U+0A95 — Gujarati
- Bengali U+0995 — Bengali
- Gurmukhi U+0A15 — Punjabi
- Odia U+0B15 — Odia
- Tamil U+0B95 — Tamil
- Telugu U+0C15 — Telugu
- Kannada U+0C95 — Kannada
- Malayalam U+0D15 — Malayalam

Candidates prioritize machine's **Nirmala UI** family and check conventional installed legacy faces (Mangal, Shruti, Vrinda, Raavi, Kalinga, Latha, Gautami, Tunga and Kartika) and installed Noto alternatives where present. A family listed as installed does not automatically count as covering a script: glyph probe must succeed.

When coverage is missing, logs one line per script and one summary and shows **one actionable warning** to use Windows Settings > Time & language > Language & region > Add a language and install the matching Windows language/font feature. When glyph probing itself fails, logs and warns as *UNKNOWN*, never silently marks all scripts PASS. No fonts are bundled, copied, downloaded or installed, and no HKLM/admin changes occur. We deliberately **do not attempt privileged/online optional feature installation**, because these would violate the current round's no new network / least privilege requirements; Windows' own Settings is the safe user route. Thus the output fulfills Sarvam's expressly allowed “check and prompt; cannot bundle” alternative, **not automatic installation**.

## Test evidence and limitations
Read back modified GitHub branch source, Git blob `0423632794d1c6f816cc219accfcd2429e897f4d` and new `tests/r79/test_font_coverage_contract.py` Git blob `33d81b52e2887157a187d4cc84f1702f5debe489`. Executed **14/14 structural contract assertions** directly against returned current branch contents: all nine scripts, eleven distinct packs, exact representative codepoints, GDI glyph probe, one install-time call, missing/unknown warning and summary, no font distribution/download/elevation, existing rollback retained, and test file present.

**Native Windows PowerShell parse, GDI font probe execution, missing-font warning UX, Windows installation/retry/uninstall: NOT_RUN** (this host has no Windows PowerShell). Added 10 Python `unittest` source-contract test cases for Sarvam to run from a full checkout; **the exact Python file was uploaded but not executed locally**. Static checks do not establish full shaping coverage; one representative consonant only proves that one glyph is present, not every grapheme. Windows verification must enumerate/log results on an actual machine.

Native developer commands in PR #43 checkout:
`python3 -m unittest discover -s tests/r79 -p 'test_*.py' -v`
`powershell -NoProfile -File windows\build-windows-setup.ps1`
`powershell -NoProfile -File tools\accept-windows.ps1`

Request Windows owner test on standard-user Windows 10/11 with Nirmala UI present and a controlled missing/disabled font setup. Check one warning, all nine named scripts in log, no unexpected network/admin/font copies, and successful setup including rollback. Claude owns IDE font choice; no IDE code changed.

**Do not merge PR #43 until Claude/Sarvam reviews concurrency/rollback effects and native Windows evidence.**
