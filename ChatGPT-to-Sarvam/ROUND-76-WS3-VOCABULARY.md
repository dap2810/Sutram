# Sutram R76 — WS3 vocabulary audit

**Full repository-wide audit NOT_RUN.** At v183 the recursive tracked Git tree contains 2,410 entries; accepted core compiler is 23,335 lines and Git blob `cc5cfbe48ac3ea1360958cb8f203385744d094b8`. A full checkout could not be cloned locally (DNS resolution blocked). Do not misrepresent the earlier one-file scan as a complete repository audit.

The existing read-only scanner remains in [draft PR #37](https://github.com/dap2810/Sutram/pull/37): `tools/r74_vocabulary_audit.py`. To run on a complete matching checkout:
`python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r76-vocabulary.json`

Triaging principles: preserve deliberate migration strings; preserve internal NASM symbol names where active string values are Sanskrit; `pankti` can legitimately mean an error-message line number; `to` is ordinary English prose and should be flagged only as former range syntax; check hidden keywords following literal escaped `\n`. Use `docs/sutram-vocabulary.html` for the intended public vocabulary and check the actual current compiler registrations before editing. No vocabulary replacement or accepted golden rewrite in this round.
