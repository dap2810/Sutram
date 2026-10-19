# R77 WS6 — Indic font presence check
Draft PR #43 adds Check-R77IndicFont in install-core.ps1. It queries System.Drawing.Text.InstalledFontCollection for the installed family Nirmala UI and logs one status. When absent, it logs a single warning and during real (non-VerifyOnly) installation presents one warning dialog that some Indian script characters may display as boxes. It does not block setup, install fonts or keyboard layouts, request admin rights or modify machine settings.

**Native Windows font enumeration and dialog NOT_RUN.** This is a family-presence check, not proof of every individual glyph or layout. The IDE's Consolas/Unicode font fallback is Claude's independent workstream; no GUI changes made. Test Nirmala-present/missing paths on real Windows in review before merging.
