# Round 78 WS3 — repository vocabulary: targeted active-source scan

**New direct-source checks performed against live v195 main:** enumerated `lang/*.lang` (11 files) and `lib/*.smlib` (24 files) using the recursive Git tree, fetched **all 35 files** through connected GitHub, and screened active language-pack canonical keys or code tokens against obsolete names including `punaravartana, pratiyati, ayojan, nishkriya, nishedha, srijana, char_at, char_code, set_char, array, string, sort, list, map, set`. Found **0 candidate obsolete public-key registrations in 11 packs and 0 active code-token candidates in 24 libraries**. Quote strings and single-line comments were masked for libraries; this is a lexical screening, not a full parser, and multi-line comment handling/semantics were not comprehensively validated.

This is an actual new source scan with 35/35 fetches and no read failures, **but the whole repository audit remains NOT_RUN**. Hundreds of examples/tests and the GUI, teaching docs and historical compatibility data have not been exhaustively classified in this session. The compiler also contains intentionally old internal symbol identifiers and migration literals; in error diagnostics `pankti` correctly means “line,” and ordinary English `to` in prose is not syntax.

The review-branch scanner in [draft PR #37](https://github.com/dap2810/Sutram/pull/37), `tools/r74_vocabulary_audit.py`, remains the recommended fully local path. On a current clean checkout run:
`python3 tools/r74_vocabulary_audit.py --repo . --output /tmp/r78-vocabulary.json`
Review all candidates against `docs/sutram-vocabulary.html` and current compiler registrations, and include exact path/line counts; ensure escaped literal `\n` sequences cannot hide old tokens. Do not rewrite accepted migration strings or golden outputs.

**Status:** targeted active-source screening PASS (35/35 reads, 0 shortlisted old names); **repository-wide exhaustive audit NOT_RUN**. No source edits.
