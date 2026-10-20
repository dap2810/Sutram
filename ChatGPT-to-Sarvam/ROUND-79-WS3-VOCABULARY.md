# Sutram Round 79 WS3 — vocabulary audit

**Status: full repository-wide audit NOT_RUN.** The complete clean checkout is not accessible in this execution host. The existing draft [PR #37](https://github.com/dap2810/Sutram/pull/37) has a read-only tracked-file candidate scanner in `tools/r74_vocabulary_audit.py` with escaped-literal-newline tests.

Previous Round 78 specifically fetched and screened all 11 `lang/*.lang` and all 24 `lib/*.smlib` against selected older keyword spellings; no active matches under that scope. That does **not** prove the remaining examples, tests, NASM/IDE/Windows source, documentation or teaching HTML are free of old keywords. No comprehensive new sweep was executed this round, and no coverage number was fabricated.

Required full checkout command:
`python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r79-vocabulary.json`
Return raw path/line findings and counts, classify active incorrect tokens vs intentional migration diagnostics/internal labels/historical prose, and run full native regressions after accepted changes. Preserve `pankti` when it correctly denotes line, `to` when ordinary English prose, and obsolete old-keyword hints that are intentionally used for migration errors. Inspect strings after literal `\n` escapes.

**Important upstream correction:** Round 79's text described diagnostics moving to English, but the later owner-approved `docs/CHANGELOG.md` v200 explicitly reverses that. Diagnostics must follow the selected Indian-language pack, with Sanskrit as default. This round changes no diagnostic text or goldens.
