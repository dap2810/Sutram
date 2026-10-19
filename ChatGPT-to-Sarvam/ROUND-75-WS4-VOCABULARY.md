# Sutram R75 WS4 — vocabulary audit continuation

The entire repository old-keyword audit was **NOT_RUN**. It would be false to claim that checking the compiler's 22,807 lines and selected GUI/docs amounts to auditing thousands of tracked paths.

Existing read-only audit utility and 10 fixture tests live in [draft PR #37](https://github.com/dap2810/Sutram/pull/37), `tools/r74_vocabulary_audit.py` and `tests/r74/`. Use on a full matching checkout:
`python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r75-vocabulary.json`

Keep intentional migration spelling and internal symbolic names; for example `KW_PRATIYATI` maps to active literal `"prati"`. In diagnostics, Sanskrit `pankti` can correctly mean a line number. Match `to` only as old range syntax, never as arbitrary prose. Escaped `\\n` sequences can hide a keyword after the literal n character; the R74 tool tests include the guard.

Source evidence actually inspected this round: main compiler blob `185b7f06ad01b5b80f123b694b0025034698bd35`; current old-name migration table, parser keyword registration and growth emitter. No old-token edits were made; library, accepted goldens, interface, docs and all language packs remain unchanged.

**Status:** full-repository audit NOT_RUN. No invented count of checked current .sm examples or old token defects. Run and categorize the utility's exact JSON before claiming a complete audit.
