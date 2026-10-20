# Round 81 — WS3 vocabulary audit

**Whole-repository lexical/semantic old-keyword audit: NOT_RUN.** Source tree can be indexed via GitHub but full current v208 repository bytes are not present in local container. Prior Round 78 targeted scan of 11 lang packs and 24 lib modules is not current full coverage. No new claims of all-source zero findings. The read-only scanner remains in [draft PR #37](https://github.com/dap2810/Sutram/pull/37).

On a full current checkout, first reconcile scanner with changed v205 language support tiers and v203 packed diagnostics; then execute:
`python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r81-vocabulary.json`.
Capture raw JSON and count all tracked candidate source files including docs, books, HTML, IDE and Windows scripts; classify former keyword spellings in **active code** versus intentionally preserved migration warnings, comments, ordinary prose and diagnostic references. An old token may occur after literal `\n`; `pankti` can correctly mean diagnostic line, and English ordinary `to` must not be blindly substituted. The selected language packs for human linguistic review are **Sanskrit, Gujarati, Hindi SUPPORTED**, remaining eight DRAFT; the script still recognizes all 11 packs. Do not rewrite accepted golden expectations or default localization.

**No main source modification. No native full vocabulary scan.**
